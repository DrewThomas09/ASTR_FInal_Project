"""Centroid-BLIND official MAST SPOC availability for ExoFOP NEB report leads.

This is a SOURCE / PRODUCT availability screen only, NOT an exoplanet
classification or independent ground-based-neighbor truth validation.
Candidates are preselected from a dated original ExoFOP observing-note
snapshot WITHOUT accessing any original TESS centroid measurements.
"""
import argparse
import csv
import hashlib
import io
import json
import re
from datetime import datetime,timezone
from pathlib import Path

from tess_two_neb_original_mast_discovery import (
    tablerows,filter_original_products,compatible_target
)
from exofop_neb_candidate_screen import excluded_tics

# These two prior note-inspected NEB targets cannot count as new sources.
PREVIOUSLY_INSPECTED_NEB_TICS={54364414,82302240}
SEED="ASTR_NEBS_ALL_NOTES_PRECENTROID_SOURCE_COHORT_20261112"


def prospective_source_screen_leads(note_json,exofop_catalog,old):
    source=json.loads(Path(note_json).read_text(encoding="utf-8"))
    raw=Path(exofop_catalog).read_bytes()
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    original_catalog={}
    for r in rows:
        try:
            k=(int(r["TIC ID"]),str(r["TOI"]).strip())
        except (TypeError,ValueError,KeyError):
            continue
        if k in original_catalog:
            raise ValueError("Repeated original ExoFOP TOI source identity")
        original_catalog[k]=r
    candidates={}
    counts={"original_public_targets_with_followup_notes":len(source.get("source_rows",[])),
            "has_explicit_NEB_disposition_note":0,
            "prior_source_or_case_exclusions":0,
            "no_matching_original_catalog_ephemeris":0}
    for r in source.get("source_rows",[]):
        if r.get("note_request_result")!="fetched":
            continue
        matching=[n for n in r.get("public_notes",[]) if
                  "NEB" in n.get("explicit_photometric_disposition_tokens",[])]
        if not matching:
            continue
        counts["has_explicit_NEB_disposition_note"]+=1
        tic=int(r["TIC_ID"]);toi=str(r["TOI"])
        if tic in old|PREVIOUSLY_INSPECTED_NEB_TICS:
            counts["prior_source_or_case_exclusions"]+=1
            continue
        entry=original_catalog.get((tic,toi))
        if not entry:
            counts["no_matching_original_catalog_ephemeris"]+=1
            continue
        try:
            p=float(entry["Period (days)"])
            epoch=float(entry["Epoch (BJD)"])
            d=float(entry["Duration (hours)"])/24
            if not (0<p<3653 and 2457000<epoch<2600000 and 0<d<.3*p):
                raise ValueError()
        except (KeyError,TypeError,ValueError):
            counts["no_matching_original_catalog_ephemeris"]+=1
            continue
        ids=sorted(set(y for n in matching for y in
                       re.findall(r"\bTIC\s*[:#-]?\s*(\d{6,11})\b",
                                  str(n.get("note","")),flags=re.I)
                       if int(y)!=tic))
        hashkey=hashlib.sha256((SEED+"|"+str(tic)+"|"+toi).encode()).hexdigest()
        candidates[tic]={
            "TIC_ID":tic,"TOI":toi,"original_public_TFOPWG_label":entry.get("TFOPWG Disposition"),
            "original_exofop_period_days":p,
            "original_exofop_epoch_BTJD":epoch-2457000,
            "original_exofop_duration_days":d,
            "note_explicit_NEB_disposition_count":len(matching),
            "potential_other_TICs_mentioned_in_note_NOT_verified":ids,
            "exofop_target_URL":"https://exofop.ipac.caltech.edu/tess/target.php?id="+str(tic),
            "deterministic_sha256_precentroid_order":hashkey,
            "reported_onsky_neighbor_truth_verified":False,
            "original_SPOC_2min_lightcurves_downloaded":False,
            "original_TESS_centroids_inspected":False,
        }
    result=sorted(candidates.values(),key=lambda x:x["deterministic_sha256_precentroid_order"])
    counts["distinct_new_source_leads_before_TESS_centroid_look"]=len(result)
    return result,counts,hashlib.sha256(raw).hexdigest()


def original_mast_coverage(tic):
    """Require original TESS SPOC target-name match, not nearby aperture source."""
    from astroquery.mast import Observations
    table=Observations.query_criteria(obs_collection="TESS",target_name=str(tic))
    obs=tablerows(table)
    strict=[r for r in obs if compatible_target(r.get("target_name"),tic)
            and str(r.get("provenance_name","")).upper()=="SPOC"]
    if len(strict)>160:
        raise ValueError("Unexpected original SPOC observation source abundance")
    if strict:
        ids={int(r["obsid"]) for r in strict}
        indexed=table[[int(q["obsid"]) in ids for q in obs]]
        products=tablerows(Observations.get_product_list(indexed))
    else:
        products=[]
    exact=filter_original_products(strict,products,tic)
    available=sorted(set(p["sector"] for p in exact if
        {"LC","TP"}.issubset({q["product_group"] for q in exact if q["sector"]==p["sector"]})))
    return len(obs),len(strict),exact,available


def run(original_notes,original_catalog,out,repo_root):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    old=excluded_tics(repo_root)
    candidates,counts,original_catalog_hash=prospective_source_screen_leads(
        original_notes,original_catalog,old)
    if not candidates:
        raise ValueError("No preserved NEB note candidates to screen")
    results=[]
    for c in candidates:
        r=dict(c)
        try:
            obs_count,original_count,products,sectors=original_mast_coverage(c["TIC_ID"])
            r.update(MAST_observation_row_count=obs_count,
                     exact_TIC_original_SPOC_observation_rows=original_count,
                     genuine_2min_SPOC_LC_TP_sectors=sectors,
                     matching_original_SPOC_products=products,
                     MAST_discovery_status="success")
        except Exception as e:
            r.update(MAST_discovery_status="error",MAST_error=str(e)[:250],
                     genuine_2min_SPOC_LC_TP_sectors=[],
                     matching_original_SPOC_products=[])
        print("NEB_SOURCE_AVAILABILITY",json.dumps({
            "TIC":c["TIC_ID"],"TOI":c["TOI"],
            "status":r["MAST_discovery_status"],
            "sectors":r["genuine_2min_SPOC_LC_TP_sectors"],
            "error":r.get("MAST_error")}),flush=True)
        results.append(r)
    available=[x for x in results if x["genuine_2min_SPOC_LC_TP_sectors"]]
    report={
        "screened_UTC":datetime.now(timezone.utc).isoformat(),
        "source_selection_before_new_TESS_centroid_inspection":True,
        "source_selection_basis":"Fixed original 30 ExoFOP broad-FP follow-up source notes, exact positive photometric NEB token, original TOI ephemerides; excludes 56 inspected TESS TIC plus prior pilot and two post-hoc source case TICs",
        "original_catalog_SHA256":original_catalog_hash,
        "original_notes_SHA256":hashlib.sha256(Path(original_notes).read_bytes()).hexdigest(),
        "original_56_plus_pilot_exclusions":len(old),
        "additional_two_reported_case_exclusions":sorted(PREVIOUSLY_INSPECTED_NEB_TICS),
        "source_counts":counts,
        "source_leads_with_original_SPOC_2min_LC_and_TP":len(available),
        "source_leads_with_no_original_SPOC_product_or_lookup_failed":len(results)-len(available),
        "candidate_list_all_not_reselected":results,
        "source_available_only_NEED_manual_external_ground_based_evidence":available,
        "interpretation":[
            "These are distinct candidate HOST TICs, not independently verified physical NEB labels or confirmed ground-based off-target positions.",
            "Public note's explicit NEB token is a retrospective research lead, not verified true source identity or ground-based photometry.",
            "No TESS moment centroid measured or viewed, no ExoMiner classifier weights/scores read or altered.",
            "True prospective evaluation would require freezing individually verified neighbor positions and same-event original SPOC source coverage before inspecting centroid outcomes.",
            "No missing SPOC two-minute source is substituted with TESS-SPOC FFI cadence products."
        ]
    }
    (out/"new_neb_ground_report_leads_MAST_2min_precentroid_coverage.json").write_text(
        json.dumps(report,indent=2,default=str)+"\n")
    print("SUMMARY",json.dumps({
        "note_research_hosts":counts["has_explicit_NEB_disposition_note"],
        "distinct_new_host_TICs":len(results),
        "original_SPOC_LC_TP_available_distinct_hosts":len(available),
        "source_TICs":[x["TIC_ID"] for x in available],
        "centroid_outcomes_inspected":0,
        "independent_ground_based_source_truth_verified":0
    }),flush=True)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-notes",required=True)
    p.add_argument("--original-catalog",required=True)
    p.add_argument("--repo-root",default=".")
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.original_notes,a.original_catalog,a.out,a.repo_root)
