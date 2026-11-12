"""Follow-up *triage* of public ExoFOP observing notes for broad FP TOIs.

The full TOI catalog publishes broad TFOPWG FP, not a verified NEB/EB subtype.
A note mentioning NEB/EB is a REVIEW CANDIDATE, never independently
validated source positions or an ExoMiner science-accuracy label.
"""
import argparse
import csv
import hashlib
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path

DISP_RE = re.compile(
    r"\b(?:phot(?:ometric)?\.?\s*disp(?:osition)?|sg1\s*disp(?:osition)?)"
    r"\s*[:=]\s*(PNEB|NEB|BEB|SEB|EB|NPC|VPC|PC|CPC|FA)\b",
    flags=re.I,
)
NEB_TEXT = re.compile(r"\bNEBS?\b|nearby eclipsing binar", flags=re.I)


def parse_observing_notes_csv(blob):
    s=blob.decode("utf-8-sig",errors="replace")
    reader=csv.DictReader(io.StringIO(s))
    if not reader.fieldnames:
        raise ValueError("No ExoFOP observing notes table header")
    cols={c.lower().strip():c for c in reader.fieldnames}
    field=next((cols[k] for k in ("notes","note","obs notes") if k in cols),None)
    if field is None:
        raise ValueError("No explicit observing-note text field; do not guess")
    out=[]
    for row in reader:
        note=str(row.get(field) or "").strip()
        if not note:
            continue
        matches=DISP_RE.findall(note)
        out.append({
            "note":note,
            "explicit_photometric_disposition_tokens":[x.upper() for x in matches],
            "mentions_NEB_or_nearby_eclipsing_binary":bool(NEB_TEXT.search(note)),
            "last_modified_as_reported":str(row.get(cols.get("lastmod",""),"")).strip(),
            "note_id_as_reported":str(row.get(cols.get("id",""),"")).strip(),
        })
    return out


def classify_note_screen(notes):
    # Source-localization never inferred from note text, even when an
    # explicit SG1 disposition token is available.
    all_tokens=[k for r in notes for k in r["explicit_photometric_disposition_tokens"]]
    potential_neb=sum(k in ("NEB","PNEB") for k in all_tokens)
    potential_eb=sum(k in ("EB","BEB","SEB") for k in all_tokens)
    has_neb_text=any(r["mentions_NEB_or_nearby_eclipsing_binary"] for r in notes)
    return {
        "public_note_rows":len(notes),
        "explicit_NEB_or_possible_NEB_disposition_mentions":potential_neb,
        "explicit_EB_BEB_SEB_disposition_mentions":potential_eb,
        "notes_with_any_NEB_text":sum(r["mentions_NEB_or_nearby_eclipsing_binary"] for r in notes),
        "human_followup_priority":(
            "review_explicit_NEB_note" if potential_neb else
            "review_explicit_EB_note" if potential_eb else
            "review_NEB_keyword_only" if has_neb_text else
            "no_obvious_NEB_keyword"
        ),
        "physical_source_truth_verified":False,
        "actual_offtarget_neighbor_coordinates_verified":False,
        "NASA_exominer_classification_evaluated":False,
    }


def screen(fp_csv, out, max_sources=30, timeout=25):
    import requests
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    csv_bytes=Path(fp_csv).read_bytes()
    rows=list(csv.DictReader(io.StringIO(csv_bytes.decode("utf-8-sig"))))
    if rows and not {"TIC_ID","TOI","catalog_TFOPWG_disposition",
                     "deterministic_selection_sha256"}.issubset(rows[0]):
        raise ValueError("Incorrect FP source-candidate manifest")
    if any(str(x["catalog_TFOPWG_disposition"]).strip().upper()!="FP" for x in rows):
        raise ValueError("Input contains non-FP source rows")
    if max_sources<=0 or max_sources>100:
        raise ValueError("Bound source note requests to <=100")
    ordered=sorted(rows,key=lambda x:x["deterministic_selection_sha256"])
    checked=[]
    for item in ordered[:max_sources]:
        tic=int(item["TIC_ID"])
        uri=f"https://exofop.ipac.caltech.edu/tess/download_obsnotes.php?tid={tic}"
        entry=dict(
            TIC_ID=tic,TOI=item["TOI"],source_exofop_TFOPWG_status="FP",
            original_toi_csv_sha256=hashlib.sha256(csv_bytes).hexdigest(),
            observed_source_note_url=uri,
            screening_selection_sha256=item["deterministic_selection_sha256"],
            note_request_result="not_fetched",notes_sha256=None,
            public_notes=[],
        )
        try:
            response=requests.get(uri,timeout=timeout,
                    headers={"User-Agent":"University-Astronomy-Research-Source-Review/1.0"})
            response.raise_for_status()
            notes=parse_observing_notes_csv(response.content)
            entry.update(
                note_request_result="fetched",
                notes_sha256=hashlib.sha256(response.content).hexdigest(),
                public_notes=notes,
                **classify_note_screen(notes)
            )
        except (requests.RequestException,ValueError,UnicodeError) as exc:
            entry.update(
                note_request_result="error",
                note_request_error=str(exc)[:180],
                physical_source_truth_verified=False,
                actual_offtarget_neighbor_coordinates_verified=False,
                NASA_exominer_classification_evaluated=False,
            )
        checked.append(entry)
        print("SCREENED TIC",tic,entry["note_request_result"],
              entry.get("human_followup_priority","cannot_parse_notes"),flush=True)
    result={
        "source":"Original public ExoFOP FP catalog snapshot + official per-target public observing notes",
        "screened_at_utc":datetime.now(timezone.utc).isoformat(),
        "original_full_FP_candidate_csv_sha256":hashlib.sha256(csv_bytes).hexdigest(),
        "total_broad_FP_candidates_in_list":len(rows),
        "number_requested_for_public_note_screen":len(checked),
        "number_public_notes_fetched":sum(x["note_request_result"]=="fetched" for x in checked),
        "number_note_fetch_or_parse_errors":sum(x["note_request_result"]=="error" for x in checked),
        "source_rows":checked,
        "cautions":[
            "The ExoFOP catalog's public TFOPWG disposition only broadly labels FP, not separately NEB or EB.",
            "A textual observing note can mention an NEB it explicitly ruled out; automatic keyword hits are review cues only.",
            "Contradictory or updated observing notes require human interpretation of the latest on-target/off-target conclusions.",
            "No source is a truth-verified NEB without independent observed eclipsing neighbor identity and sky coordinates.",
            "No new TESS moment-centroid measurements, ExoMiner model scores, or classifier outcomes were examined.",
            "The first fixed hash-sorted FP subset is not an independently physically validated or representative TESS sample."
        ]
    }
    (out/"first_public_FP_observing_note_triage.json").write_text(
        json.dumps(result,indent=2)+"\n",encoding="utf-8"
    )
    print(json.dumps({
        "public_source_note_requests":len(checked),
        "fetched":result["number_public_notes_fetched"],
        "errors":result["number_note_fetch_or_parse_errors"],
        "explicit_NEB_or_PNEB_note_candidates":sum(x.get("explicit_NEB_or_possible_NEB_disposition_mentions",0)>0 for x in checked),
        "explicit_EB_or_BEB_note_candidates":sum(x.get("explicit_EB_BEB_SEB_disposition_mentions",0)>0 for x in checked),
        "human_review_only":True,
        "verified_independent_source_truth":0
    },indent=2),flush=True)
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--fp-csv",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--max-sources",type=int,default=30)
    a=p.parse_args()
    screen(a.fp_csv,a.out,a.max_sources)
