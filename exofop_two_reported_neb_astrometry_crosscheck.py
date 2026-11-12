"""Two post-hoc externally reported ExoFOP NEB case studies.

Crosscheck nearby-TIC astrometry against original, immutable public follow-up
notes. No TESS centroid processing or ExoMiner classification occurs here.
These cases were inspected post hoc and cannot be an independent holdout.
"""
import argparse,csv,hashlib,io,json,re
from pathlib import Path
import requests

CASES=[
 {"toi":"2041.01","target_tic":54364414,"neighbor_tic":54364420,
  "reported_neighbor_separation_arcsec":23.4,
  "primary_followup_source":"Original ExoFOP note explicitly says ground-based on-neighbor event and NEB disposition"},
 {"toi":"4255.01","target_tic":82302240,"neighbor_tic":82302236,
  "reported_neighbor_separation_arcsec":5.0,
  "primary_followup_source":"Original ExoFOP note explicitly says on-neighbor eclipse and NEB disposition"},
]
API="https://exofop.ipac.caltech.edu/tess/download_nearbytarget.php?id={}&output=csv"


def normalized_field(row,words):
    for key,val in row.items():
        k=(key or "").lower().strip()
        if all(w in k for w in words):
            return val
    return None


def parse_neighbor_sep(raw, neighbor_tic):
    try:
        contents=raw.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise ValueError("Original nearby-target table invalid UTF-8") from e
    reader=csv.DictReader(io.StringIO(contents))
    if not reader.fieldnames:
        raise ValueError("Original nearby-target CSV has no field header")
    header=list(reader.fieldnames)
    if not any("tic" in h.lower() and "id" in h.lower() for h in header):
        raise ValueError("Nearby-target table lacks TIC ID field")
    if not any("separation" in h.lower() for h in header):
        raise ValueError("Nearby-target table lacks angular separation")
    hits=[]
    for row in reader:
        tid=normalized_field(row,("tic","id"))
        sep=normalized_field(row,("separation",))
        try:
            if int(str(tid).strip())!=int(neighbor_tic):
                continue
            sep=float(str(sep).strip())
        except (ValueError,TypeError):
            continue
        if not 0<sep<36000:
            continue
        pa=normalized_field(row,("position","angle"))
        hits.append({"catalog_neighbor_tic":neighbor_tic,
                     "catalog_angular_separation_arcsec":sep,
                     "catalog_position_angle_E_of_N_degrees":pa})
    return hits


def note_source(record, notes):
    matching=[]
    for row in notes:
        if int(row["TIC_ID"])!=record["target_tic"]:
            continue
        for n in row.get("public_notes",[]):
            text=str(n.get("note") or "")
            # An explicit physical SG1 photometric disposition + named
            # neighbor in the *same original note* is required.
            has_explicit_neb="NEB" in n.get("explicit_photometric_disposition_tokens",[])
            names_neighbor=bool(re.search(r"\bTIC\s*"+str(record["neighbor_tic"])+r"\b",text,re.I))
            if has_explicit_neb and names_neighbor:
                matching.append(n)
    return matching


def run(original_notes_json,out):
    original_path=Path(original_notes_json)
    raw_notes=original_path.read_bytes()
    payload=json.loads(raw_notes)
    notes=payload["source_rows"]
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    findings=[]
    for case in CASES:
        rec=dict(case)
        rec["original_30_target_note_snapshot_sha256"]=hashlib.sha256(raw_notes).hexdigest()
        noted=note_source(rec,notes)
        rec["source_note_explicit_NEBS_and_neighbor_identity_matches"]=len(noted)
        rec["most_recent_matched_note_lastmod"]=max(
            (n.get("last_modified_as_reported","") for n in noted),default=None)
        rec["source_reported_NEBS_with_identified_neighbor"]=len(noted)>0
        rec["position_verified_by_original_catalog"]=False
        rec["full_independent_physical_source_truth"]=False
        rec["same_event_TESS_2min_FITS_verified"]=False
        rec["Original_DV_difference_image_centroid_verified"]=False
        url=API.format(case["target_tic"])
        rec["official_nearby_source_url"]=url
        try:
            response=requests.get(url,timeout=45,
                headers={"User-Agent":"Astronomy-Student-Source-Astrometry-Review/1.0"})
            response.raise_for_status()
            raw=response.content
            rec["original_nearby_catalog_SHA256"]=hashlib.sha256(raw).hexdigest()
            (out/("TIC_"+str(case["target_tic"])+"_original_nearby_targets.csv")).write_bytes(raw)
            hits=parse_neighbor_sep(raw,case["neighbor_tic"])
            rec["original_nearby_catalog_matching_rows"]=hits
            rec["original_nearby_catalog_match_count"]=len(hits)
            rec["separation_within_2_arcsec_of_reported_note"]=any(
                abs(x["catalog_angular_separation_arcsec"] -
                    case["reported_neighbor_separation_arcsec"])<=2 for x in hits)
            rec["position_verified_by_original_catalog"]=(
                rec["separation_within_2_arcsec_of_reported_note"] and len(hits)==1)
            rec["retrieval_status"]="success"
        except (ValueError,requests.RequestException) as e:
            rec["retrieval_status"]="error"
            rec["retrieval_error"]=str(e)[:220]
            rec["position_verified_by_original_catalog"]=False
        findings.append(rec)
    summary={
       "purpose":"Two exploratory observed-neighbor crosschecks after examining frozen ExoFOP notes; NOT blind validation",
       "n_posthoc_NEB_candidate_targets":len(CASES),
       "n_sources_with_explicit_original_NEBS_and_neighbor_note":sum(x["source_reported_NEBS_with_identified_neighbor"] for x in findings),
       "n_source_neighbor_separation_matches":sum(x["position_verified_by_original_catalog"] for x in findings),
       "source_original_notes_SHA256":hashlib.sha256(raw_notes).hexdigest(),
       "cases":findings,
       "not_established":[
          "Ground-based original photometry plotted independently by this script",
          "Unchanged NASA original TESS SPOC event ephemerides and original source FITS verified for either case",
          "Valid TESS aperture WCS direction versus external off-target neighbor direction",
          "Whether the experimental pointing subtraction improved genuine physical localization",
          "NASA ExoMiner++ planet classifier accuracy on held-out stars"
       ],
    }
    (out/"Two_Original_ExoFOP_reported_NEB_nearby_source_crosschecks.json").write_text(
        json.dumps(summary,indent=2)+"\n")
    print(json.dumps({
        "n_posthoc_cases":len(CASES),
        "original_ground_note_neighbor_matches":summary["n_sources_with_explicit_original_NEBS_and_neighbor_note"],
        "original_catalog_astrometric_separation_matches":summary["n_source_neighbor_separation_matches"],
        "per_case":[{k:r.get(k) for k in ("toi","target_tic","neighbor_tic","retrieval_status",
           "position_verified_by_original_catalog","original_nearby_catalog_matching_rows")} for r in findings],
        "astrophysical_truth_ground_followup_plots_and_TESS_centroid_comparison_not_yet_validated":True
    },indent=2),flush=True)
    return summary


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-notes",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.original_notes,a.out)
