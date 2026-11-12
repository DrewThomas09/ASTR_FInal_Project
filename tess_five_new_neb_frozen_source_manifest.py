"""Freeze five new ExoFOP named-neighbor TICs BEFORE opening TESS centroid data.

All selection uses immutable historical ExoFOP notes, external neighbor
catalogs and MAST LC/TP product availability only. A TIC mentioned in a
note is NOT independently confirmed eclipsing-source truth.
"""
import argparse
import hashlib
import json
from pathlib import Path

SEED="ASTR_NEB_FIVE_NEW_SPOC_FIRST_SECTOR_PRE_CENTROID_20261112"
PREVIOUS_PRIOR={82302240,54364414}


def freeze(source_screen,nearby_review):
    if hashlib.sha256(json.dumps(source_screen,indent=2,default=str).encode()).hexdigest()=="":
        raise AssertionError("unreachable")
    new=nearby_review["not_yet_truth_validated_single_named_neighbor_source_candidates"]
    if len(new)!=5 or source_screen["source_leads_with_original_SPOC_2min_LC_and_TP"]!=10:
        raise ValueError("Expected original source-only cohort 5 of 10")
    bytic={int(s["TIC_ID"]):s for s in
           source_screen["source_available_only_NEED_manual_external_ground_based_evidence"]}
    selected=[]
    for cand in new:
        tic=int(cand["TIC_ID"])
        if tic not in bytic or tic in PREVIOUS_PRIOR:
            raise ValueError("New TIC replaced with previously inspected source")
        src=bytic[tic]
        names={int(x) for x in cand["independent_nearby_catalog_matched_unique_other_TICs"]}
        if len(names)!=1 or cand["pointing_corrected_centroid_seen"] is not False:
            raise ValueError("Ambiguous external neighbor or prior centroid exposure")
        neighbor=next(iter(names))
        astrometry=[x["nearby_catalog_match"] for x in cand.get("note_mentioned_other_TICs",[])
                    if int(x["mentioned_TIC_ID"])==neighbor and x["nearby_catalog_match"]]
        if len(astrometry)==0:
            raise ValueError("Missing original independent nearby catalog geometry")
        primary=astrometry[0]
        if any(abs(float(y["original_catalog_separation_arcsec"])-
                   float(primary["original_catalog_separation_arcsec"]))>.01
               for y in astrometry):
            raise ValueError("Conflicting original neighbor astrometry")
        sectors=sorted(set(int(s) for s in src["genuine_2min_SPOC_LC_TP_sectors"]))
        if not sectors:
            raise ValueError("No verified original 2-minute SPOC data")
        sector=sectors[0] # Frozen BEFORE reading any new TESS centroid vectors.
        raw_products=src["matching_original_SPOC_products"]
        pair={}
        for kind in ("LC","TP"):
            hits=[p for p in raw_products if p["product_group"]==kind and
                  int(p["sector"])==sector and int(p["TIC_ID"])==tic and
                  f"{tic:016d}" in p["productFilename"]]
            if len(hits)!=1:
                raise ValueError("Original source sector has missing or duplicate LC/TP product")
            pair[kind]=hits[0]
        selected.append({
            "TIC_ID":tic,"TOI":cand["TOI"],
            "original_neb_named_neighbor_TIC_not_physical_truth":neighbor,
            "original_nearby_catalog_RA_deg":float(primary["original_catalog_neighbor_RA_deg"]),
            "original_nearby_catalog_Dec_deg":float(primary["original_catalog_neighbor_DEC_deg"]),
            "original_nearby_catalog_separation_arcsec":float(primary["original_catalog_separation_arcsec"]),
            "original_nearby_catalog_position_angle_deg":float(primary["original_catalog_position_angle_deg"]),
            "selected_first_original_SPOC_2min_sector":sector,
            "selection_rule":"lowest integer SPOC sector with exactly paired original LC/TP, before observing centroid",
            "original_MAST_products":pair,
            "original_ExoFOP_period_days":float(src["original_exofop_period_days"]),
            "original_ExoFOP_epoch_BTJD":float(src["original_exofop_epoch_BTJD"]),
            "original_ExoFOP_duration_days":float(src["original_exofop_duration_days"]),
            "source_selection_sha256_prior_centroid":src["deterministic_sha256_precentroid_order"],
            "ground_based_eclipse_in_named_neighbor_independently_verified":False,
            "moment_centroid_vectors_extracted":False
        })
    selected=sorted(selected,key=lambda x:x["source_selection_sha256_prior_centroid"])
    if len({x["TIC_ID"] for x in selected})!=5:
        raise ValueError("Must be exactly five distinct host stars")
    return selected


def run(source_screen,neighbor_review,out):
    raw1=Path(source_screen).read_bytes()
    raw2=Path(neighbor_review).read_bytes()
    a=json.loads(raw1);b=json.loads(raw2)
    expected=b.get("original_source_screen_json_SHA256")
    if expected!=hashlib.sha256(raw1).hexdigest():
        raise ValueError("The new-neighbor audit does not correspond to original 10-host source manifest")
    entries=freeze(a,b)
    report={
        "experiment_id":"ASTR_FIVE_NEW_NEB_SPOC_SOURCE_BLIND_WCS_EVAL_20261112",
        "source_manifest_frozen_prior_to_five_star_TESS_centroid_analysis":True,
        "original_source_only_10host_SHA256":hashlib.sha256(raw1).hexdigest(),
        "original_external_note_astrometry_10host_SHA256":hashlib.sha256(raw2).hexdigest(),
        "selection_SEED":SEED,
        "fixed_new_source_host_count":5,
        "source_records":entries,
        "evaluation_preplanned":[
            "Keep exact five TICs including any absent or non-photometric source events; no replacement or selection on detector outcomes.",
            "Select first authentic original SPOC LC/TP sector per host by integer sector order, not by transit or centroid magnitude.",
            "Use original ExoFOP TOI period, epoch and duration unchanged for quality-zero complete event windows.",
            "Compare original raw and experimental MOM_CENTR-POS_CORR in-event x/y vectors in sector-specific source TPF WCS.",
            "Predicted physical direction for simple off-target fade is away from cataloged neighbor; no optimizing angle or sign.",
            "Only source hosts with >=3 exact real observed complete paired events and external source WCS consistency get a descriptive angular comparison.",
            "Report all five denominators and QC missingness, as well as raw-vs-corrected angles, independent at HOST not event level.",
            "Preserve input original MAST source-file SHA256, all original event counts and any negative physical outcomes.",
        ],
        "limitations":[
            "Source-selected from already-reviewed public ExoFOP follow-up notes, not independent of NASA model training.",
            "One named neighbor TIC in a NEB-tagged note and independent nearby astrometry is NOT independent ground-based eclipse photometry confirmation.",
            "No control on-target cohort currently selected; five-star exploratory directional assessment is NOT NASA planet-vetting accuracy.",
            "Source-note false or mixed identifiers must be reported, not silently excluded based on centroid results.",
        ]
    }
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    dst=out/"FROZEN_FIVE_NEW_NEB_SPOC_PRE_CENTROID_SOURCE_MANIFEST.json"
    dst.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({
        "n_new_source_hosts":len(entries),
        "TIC_sector_neighbor":[[s["TIC_ID"],s["selected_first_original_SPOC_2min_sector"],
                                s["original_neb_named_neighbor_TIC_not_physical_truth"]]
                               for s in entries],
        "input_manifest_sha256":hashlib.sha256(raw1).hexdigest(),
        "external_source_evidence_sha256":hashlib.sha256(raw2).hexdigest(),
        "source_manifest_SHA256":hashlib.sha256(dst.read_bytes()).hexdigest(),
        "centroids_inspected":0,
        "physically_independent_NEBS_verified":0
    },indent=2),flush=True)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-screen",required=True)
    p.add_argument("--neighbor-review",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.source_screen,a.neighbor_review,a.out)
