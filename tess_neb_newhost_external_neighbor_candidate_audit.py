"""Centroid-BLIND ExoFOP named-neighbor catalog verification for 10 new hosts.

Inputs: frozen original ExoFOP note snapshot AND prior genuine MAST
SPOC-2-minute availability snapshot. Do NOT treat a note mention as
independent ground-truth eclipse source; no photometry/centroids are read.
"""
import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path

import requests
from astropy import units as u
from astropy.coordinates import SkyCoord

NEIGHBOR_URL="https://exofop.ipac.caltech.edu/tess/download_nearbytarget.php?id={}&output=csv"
TIC_PATTERN=re.compile(r"\bTIC\s*[:#-]?\s*(\d{6,11})\b",re.I)


def read_neighbor_astrometry(blob,exclude_tic):
    reader=csv.DictReader(io.StringIO(blob.decode("utf-8-sig")))
    mandatory={"TIC ID","RA","Dec","Separation (arcsec)",
               "Position Angle (deg E. of N.)"}
    if not mandatory.issubset(reader.fieldnames or []):
        raise ValueError("External original astrometry missing required identifying columns")
    rows={}
    for row in reader:
        try:
            other=int(row["TIC ID"])
            if other==exclude_tic:continue
            ra=str(row["RA"]).strip();dec=str(row["Dec"]).strip()
            sky=SkyCoord(ra=ra,dec=dec,
                         unit=(u.hourangle,u.deg) if (":" in ra or "h" in ra.lower()) else (u.deg,u.deg))
            sep=float(row["Separation (arcsec)"])
            pa=float(row["Position Angle (deg E. of N.)"])
        except (ValueError,TypeError):
            continue
        if not (0<sep<=120 and 0<=pa<360):
            continue
        if other in rows:
            raise ValueError("Duplicate independent nearby TIC in astrometry source")
        rows[other]={
            "neighbor_TIC_ID":other,
            "original_catalog_neighbor_RA_deg":float(sky.ra.deg),
            "original_catalog_neighbor_DEC_deg":float(sky.dec.deg),
            "original_catalog_separation_arcsec":sep,
            "original_catalog_position_angle_deg":pa,
        }
    return rows


def candidate_note_matches(original_note_rows,host_tic,nearby):
    selected=[r for r in original_note_rows if int(r.get("TIC_ID",-1))==host_tic]
    if len(selected)!=1:
        raise ValueError("Original source note is absent or duplicated for host "+str(host_tic))
    row=selected[0]
    matching=[n for n in row.get("public_notes",[])
             if "NEB" in n.get("explicit_photometric_disposition_tokens",[])]
    if not matching:
        raise ValueError("Source note lacks original explicit NEB designation")
    mentions=[]
    for n in matching:
        text=str(n.get("note",""))
        for m in TIC_PATTERN.finditer(text):
            other=int(m.group(1))
            if other==host_tic:continue
            left=max(0,m.start()-160);right=min(len(text),m.end()+160)
            excerpt=text[left:right]
            mentions.append({
                "mentioned_TIC_ID":other,
                "in_external_nearby_star_catalog":other in nearby,
                "nearby_catalog_match":nearby.get(other),
                "raw_note_context_excerpt":excerpt,
                "source_note_lastmod":n.get("last_modified_as_reported"),
                "source_note_id":n.get("note_id_as_reported")
            })
    return matching,mentions


def run(original_neb_source_screen,original_observing_notes,out):
    scan=json.loads(Path(original_neb_source_screen).read_text())
    notes=json.loads(Path(original_observing_notes).read_text())
    viable=scan.get("source_available_only_NEED_manual_external_ground_based_evidence",[])
    if len(viable)!=10:
        raise ValueError("Original frozen candidate source availability changed from 10 hosts")
    target_tics=[int(x["TIC_ID"]) for x in viable]
    if len(set(target_tics))!=10 or {54364414,82302240}&set(target_tics):
        raise ValueError("Unexpected duplicate/prior-inspected host in new-source screen")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for source in viable:
        tic=int(source["TIC_ID"])
        item={
            "TIC_ID":tic,
            "TOI":source["TOI"],
            "SPOC_original_TESS_2min_available_sectors":source["genuine_2min_SPOC_LC_TP_sectors"],
            "period_days_original_ExoFOP":source["original_exofop_period_days"],
            "epoch_BTJD_original_ExoFOP":source["original_exofop_epoch_BTJD"],
            "duration_days_original_ExoFOP":source["original_exofop_duration_days"],
            "pointing_corrected_centroid_seen":False,
            "NASA_ExoMiner_predictions_seen":False,
            "independent_ground_based_eclipse_photometry_verified":False,
            "neighbor_physical_eclipse_identity_verified":False,
        }
        try:
            url=NEIGHBOR_URL.format(tic)
            response=requests.get(url,timeout=45,
                                  headers={"User-Agent":"Astronomy-Student-Source-Only-NEB-Verifier/1.0"})
            response.raise_for_status()
            raw=response.content
            nearby=read_neighbor_astrometry(raw,tic)
            matched,mentions=candidate_note_matches(notes["source_rows"],tic,nearby)
            item.update(
                original_external_neighbor_catalog_url=url,
                original_external_neighbor_catalog_SHA256=hashlib.sha256(raw).hexdigest(),
                number_explicit_NEB_source_notes=len(matched),
                note_mentioned_other_TICs=mentions,
                independent_nearby_catalog_matched_unique_other_TICs=sorted(set(
                    x["mentioned_TIC_ID"] for x in mentions
                    if x["in_external_nearby_star_catalog"])),
                number_distinct_named_nearby_TICs=len(set(
                    x["mentioned_TIC_ID"] for x in mentions
                    if x["in_external_nearby_star_catalog"])),
                source_verification_status="fetched_and_queued_for_original_ground_lightcurve_review"
            )
            (out/f"original_ExoFOP_TIC_{tic}_nearby_astrometry.csv").write_bytes(raw)
        except (requests.RequestException,ValueError,KeyError) as exc:
            item.update(source_verification_status="source_error",
                        source_verification_error=str(exc)[:300],
                        independent_nearby_catalog_matched_unique_other_TICs=[],
                        number_distinct_named_nearby_TICs=0)
        print("NEW_SOURCE_NEIGHBOR_CHECK",json.dumps({
            "TIC":tic,"TOI":source["TOI"],
            "status":item["source_verification_status"],
            "named_neighbor_in_catalog":item["independent_nearby_catalog_matched_unique_other_TICs"]}),flush=True)
        rows.append(item)
    unambiguous=[
        x for x in rows if x["source_verification_status"]==
            "fetched_and_queued_for_original_ground_lightcurve_review" and
            x["number_distinct_named_nearby_TICs"]==1
    ]
    report={
        "purpose":"Ten new original-TESS-SPOC-available ExoFOP NEB-report hosts, external named-neighbor candidates WITHOUT viewing source centroids",
        "original_source_screen_json_SHA256":hashlib.sha256(Path(original_neb_source_screen).read_bytes()).hexdigest(),
        "original_followup_notes_snapshot_SHA256":hashlib.sha256(Path(original_observing_notes).read_bytes()).hexdigest(),
        "source_host_count":len(rows),
        "n_sources_with_unique_catalog_neighbor_named_in_explicit_NEB_note":len(unambiguous),
        "not_yet_truth_validated_single_named_neighbor_source_candidates":unambiguous,
        "all_ten_sources_including_ambiguous_and_missing":rows,
        "scope_limits":[
            "SPOC 2-min source availability is verified from MAST products, but no true source light curves downloaded here.",
            "A note's occurrence of neighbor TIC may refer to a ruled-out object; even one matched TIC is only a source-verification lead.",
            "A separate human review must validate exact ground-observed eclipse, on/off-target source identity and crossmatch before designating verified NEB labels.",
            "No original TESS moment centroids, WCS direction outcomes, ExoMiner network weights or prediction scores have been examined for these ten hosts.",
            "This cohort is selected from already inspected follow-up notes and cannot be called independent of NASA 2026 training or a fully blind mission sample."
        ]
    }
    (out/"ten_new_SPOC_host_original_ExoFOP_named_neighbor_candidate_audit.json").write_text(
        json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("SUMMARY",json.dumps({
        "distinct_new_host_TICs":len(rows),
        "with_one_catalog_matched_neighbor_TIC_from_explicit_NEB_note":len(unambiguous),
        "missing_or_ambiguous":len(rows)-len(unambiguous),
        "centroid_data_inspected":0,
        "physically_verified_ground_NEBS":0
    }),flush=True)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-screen",required=True)
    p.add_argument("--original-notes",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.source_screen,a.original_notes,a.out)
