"""Summarize original ExoFOP observing-note review candidates without truth guessing.

Consumes an archived immutable original-source retrieval artifact, rather than
redownloading the source catalog and silently changing cohort membership.
"""
import argparse
import json
import re
from pathlib import Path

SEP = re.compile(
    r"(?<![0-9])([0-9]+(?:\.[0-9]+)?)\s*(?:\"|''|arcsec(?:onds)?|as)\b?", re.I
)
TIC = re.compile(r"\bTIC\s*[:#-]?\s*([0-9]{6,11})\b",re.I)


def extract_review_notes(payload, max_excerpt=550):
    if not isinstance(payload,dict) or "source_rows" not in payload:
        raise ValueError("Missing original source-reviewed ExoFOP note array")
    output=[]
    for row in payload["source_rows"]:
        if row.get("note_request_result") != "fetched":
            continue
        if row.get("physical_source_truth_verified") is not False:
            raise ValueError("Input falsely upgrades source truth")
        for note in row.get("public_notes",[]):
            tokens=note.get("explicit_photometric_disposition_tokens",[])
            if not tokens or not any(t in ("NEB","PNEB","EB","BEB","SEB") for t in tokens):
                continue
            original = note.get("note","")
            output.append({
                "TIC_ID": row["TIC_ID"],"TOI":row["TOI"],
                "explicit_reported_photometric_dispositions":tokens,
                "note_lastmod":note.get("last_modified_as_reported",""),
                "note_id":note.get("note_id_as_reported",""),
                "source_url":row["observed_source_note_url"],
                "quoted_note_excerpt_for_review_only":original[:max_excerpt],
                "possible_TIC_numbers_in_note_not_yet_verified":sorted(set(TIC.findall(original))),
                "possible_angular_separations_unverified":SEP.findall(original)[:12],
                "offtarget_physical_source_localized":False,
                "on_target_physical_source_localized":False,
                "followup_original_lightcurve_verified":False,
                "astrometry_verified":False,
            })
    return sorted(output,key=lambda x:(x["TIC_ID"],x["note_lastmod"],x["note_id"]),reverse=False)


def run(source,out):
    payload=json.loads(Path(source).read_text(encoding="utf-8"))
    notes=extract_review_notes(payload)
    targets=sorted(set(n["TIC_ID"] for n in notes))
    result={
        "purpose":"Read-only candidate triage to prioritize inspecting original published NEB/EB observing evidence",
        "note_excerpt_count":len(notes),
        "distinct_source_hosts_with_explicit_photometric_disposition_tokens":len(targets),
        "original_candidate_source":str(source),
        "review_notes":notes,
        "claims_not_supported":[
            "A label token inside notes cannot certify the physical source, sky position or transit period.",
            "The possible TIC IDs and angular distances are unverified snippets and may refer to ruled-out neighbors.",
            "No truth-labeled holdout sample or model-accuracy evaluation has been established."
        ],
    }
    folder=Path(out);folder.mkdir(parents=True,exist_ok=True)
    (folder/"NEB_EB_public_note_excerpt_review_queue.json").write_text(
        json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "distinct_source_hosts_with_explicit_note_dispositions":len(targets),
        "source_note_excerpts_for_review":len(notes),
        "examples_at_most_5":[
            {"tic":n["TIC_ID"],"toi":n["TOI"],"tokens":n["explicit_reported_photometric_dispositions"],
             "lastmod":n["note_lastmod"],"excerpt":n["quoted_note_excerpt_for_review_only"][:400]}
            for n in notes[:5]
        ],
        "verified_offtarget_source_truth":0
    },indent=2),flush=True)
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.source,a.out)
