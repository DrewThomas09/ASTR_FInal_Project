"""Real NASA SPOC Data Validation XML PRF source-location benchmark, without selecting on centroid.

Twelve source-only discovered original official MAST SPOC DVR XML files (six
per one of two preselected real ground NEB host TICs) are downloaded with SHA.
First and only match original NASA DV TCE period/phase to unchanged ExoFOP
TOI period/epoch; only *then* read official mission-quality difference-image
PRF centroid and its uncertainty/quality flags for the source-frozen first
sector. Preserve ALL runs, TCEs, missing/invalid matches and quality reasons.

This is NOT an independent ground-image source-truth classification or
train-independent ExoMiner validation. A NASA DV result may be absent if the
source signal never passed the transit-search TCE requirements.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import requests
from astropy import units as u
from astropy.coordinates import SkyCoord
from scipy.stats import binomtest

from tess_toi4255_original_spoc_neb_vector_case import MAST_FILE_ENDPOINT

HOSTS={382437043:"1223.01",264303333:"2250.01"}
MAX_XML_BYTES=12_000_000
MAX_XML_PER_SOURCE=20
PERIOD_MATCH_FRACTION=0.01
PHASE_MATCH_DURATIONS=3.0
PHASE_MATCH_LIMIT_IN_ORBIT_FRACTION=0.15
DV_VALID_MIN=0.0
EXPECTED_VETTED_XML_COUNTS={382437043:6,264303333:6}


def tagname(x):
    return str(x.tag).rsplit("}",1)[-1]


def childs_named(x,name):
    return [a for a in x.iter() if tagname(a)==name]


def strict_scalar(x,name):
    hits=childs_named(x,name)
    if len(hits)!=1:
        return None
    try:
        z=float(hits[0].attrib["value"])
        return float(z) if math.isfinite(z) else None
    except (ValueError,KeyError,TypeError):
        return None


def original_nasa_dv_source_xml(blob,tic):
    if len(blob)>MAX_XML_BYTES or len(blob)<80:
        raise ValueError("Unreasonable official NASA TESS DV XML original byte length")
    if b"<!DOCTYPE" in blob.upper() or b"<!ENTITY" in blob.upper():
        raise ValueError("Original mission DV XML has embedded declaration or entity")
    root=ET.fromstring(blob)
    if tagname(root)!="dvTargetResults" or int(root.get("ticId","-1"))!=int(tic):
        raise ValueError("Not original exact requested NASA DV TIC source root")
    planet_results=[z for z in root if tagname(z)=="planetResults"]
    rows=[]
    for item in planet_results:
        n=item.attrib.get("planetNumber")
        try:pnum=int(n)
        except (ValueError,TypeError):pnum=None
        candidate=childs_named(item,"planetCandidate")
        if len(candidate)!=1:
            rows.append({"original_NASA_DV_planet_number":pnum,
                "status":"no_unique_original_planetCandidate_ephemeris",
                "planet_result_direct_child_tags":[tagname(z) for z in list(item)][:25]})
            continue
        c=candidate[0]
        period=strict_scalar(c,"orbitalPeriod")
        epoch=strict_scalar(c,"transitEpoch")
        rows.append({
            "original_NASA_DV_planet_number":pnum,
            "status":"original_catalog_TCE_only_no_centroid_read",
            "original_NASA_DV_candidate_period_days":period,
            "original_NASA_DV_candidate_epoch_BTJD":epoch,
            "original_planetCandidate_direct_child_names":[tagname(z) for z in list(c)][:22],
            "original_planetResults_direct_child_names":[tagname(z) for z in list(item)][:30],
        })
    declared=int(root.attrib.get("planetCandidateCount","-1"))
    return root,rows,{
        "original_DV_root_ticId":int(root.attrib["ticId"]),
        "original_DV_root_declared_planetCandidateCount":declared,
        "original_DV_root_sectorsObserved_string":root.attrib.get("sectorsObserved"),
        "original_DV_actual_planetResults_count":len(planet_results),
    }


def wrapped_phase_separation_days(reference_epoch,comparison_epoch,p):
    if not all(math.isfinite(v) for v in (reference_epoch,comparison_epoch,p)) or p<=0:
        raise ValueError("Invalid authentic DV/ExoFOP ephemeris")
    return float(abs((comparison_epoch-reference_epoch+.5*p)%p-.5*p))


def source_tce_match(candidate,original_period,original_epoch,original_duration):
    p=candidate.get("original_NASA_DV_candidate_period_days")
    epoch=candidate.get("original_NASA_DV_candidate_epoch_BTJD")
    r={"has_original_NASA_DV_period_and_epoch":False,
       "matches_published_original_TOI_period_and_phase_before_any_centroid_read":False}
    if p is None or epoch is None or p<=0 or original_period<=0:
        return r
    phase=wrapped_phase_separation_days(original_epoch,epoch,original_period)
    rel=abs(float(p)/float(original_period)-1)
    threshold=min(PHASE_MATCH_LIMIT_IN_ORBIT_FRACTION*original_period,
                  PHASE_MATCH_DURATIONS*original_duration)
    r.update({
        "has_original_NASA_DV_period_and_epoch":True,
        "DV_to_original_TOI_period_fractional_difference":rel,
        "DV_to_original_TOI_wrapped_phase_difference_days":phase,
        "predeclared_photometric_phase_match_threshold_days":threshold,
        "matches_published_original_TOI_period_and_phase_before_any_centroid_read":bool(
            rel<=PERIOD_MATCH_FRACTION and phase<=threshold)
    })
    return r


def metric_element(x,key):
    hits=childs_named(x,key)
    if len(hits)!=1:
        return {"value":None,"uncertainty":None,"valid":False,
                "reason":"missing_or_multiple_original_metric_elements"}
    item=hits[0]
    try:
        v=float(item.attrib["value"])
        uncertainty=float(item.attrib["uncertainty"])
    except (ValueError,TypeError,KeyError):
        return {"value":None,"uncertainty":None,"valid":False,
                "reason":"original_metric_missing_value_or_uncertainty"}
    ok=math.isfinite(v) and math.isfinite(uncertainty) and uncertainty>=DV_VALID_MIN
    return {"value":v if math.isfinite(v) else None,
            "uncertainty":uncertainty if math.isfinite(uncertainty) else None,
            "valid":bool(ok),
            "reason":"original_uncertainty_nonnegative" if ok else
                     "original_uncertainty_invalid_or_nan"}


def position_centroid_group(item,name):
    groups=childs_named(item,name)
    if len(groups)!=1:
        return {"valid_RA_Dec":False,"reason":"missing_or_multiple_"+name}
    sky=groups[0]
    ra=metric_element(sky,"raDegrees")
    dec=metric_element(sky,"decDegrees")
    valid=ra["valid"] and dec["valid"]
    if valid:
        valid=0<=ra["value"]<360 and -90<=dec["value"]<=90
    return {"original_RA_degrees":ra,"original_Dec_degrees":dec,
            "valid_RA_Dec":bool(valid),
            "reason":"valid_original_position_and_uncertainties" if valid
                     else "missing_or_invalid_original_sky_position"}


def original_dv_match_centroids(planet_result,first_sector,host_sky,neighbor_sky):
    """Never call on period/phase-unmatched candidate."""
    results=childs_named(planet_result,"differenceImageResults")
    rows=[]
    for entry in results:
        try:sector=int(entry.attrib["sector"])
        except (ValueError,KeyError):
            sector=None
        if sector!=first_sector:
            continue
        q=childs_named(entry,"qualityMetric")
        quality={"attempted":None,"valid":None,"value":None}
        if len(q)==1:
            quality={
                "attempted":str(q[0].attrib.get("attempted","")).lower()=="true",
                "valid":str(q[0].attrib.get("valid","")).lower()=="true",
                "value":q[0].attrib.get("value")
            }
        official=position_centroid_group(entry,"differenceImageCentroid")
        reference=position_centroid_group(entry,"ticReferenceCentroid")
        control=position_centroid_group(entry,"controlImageCentroid")
        row={
          "original_DV_image_sector":sector,
          "original_DV_image_quality_metric":quality,
          "original_DV_PRF_difference_image_centroid":official,
          "original_DV_PRF_control_out_of_transit_centroid":control,
          "original_DV_TIC_reference_centroid":reference,
          "original_DV_first_sector_PRF_physically_interpretable":False
        }
        if (quality["attempted"] is True and quality["valid"] is True and
              official["valid_RA_Dec"]):
            a=SkyCoord(ra=official["original_RA_degrees"]["value"]*u.deg,
                       dec=official["original_Dec_degrees"]["value"]*u.deg)
            h=SkyCoord(*host_sky,unit=u.deg)
            n=SkyCoord(*neighbor_sky,unit=u.deg)
            dh=float(a.separation(h).arcsec)
            dn=float(a.separation(n).arcsec)
            row.update({
                "original_NASA_DV_PRF_to_primary_host_arcsec":dh,
                "original_NASA_DV_PRF_to_ground_observed_neighbor_arcsec":dn,
                "original_NASA_DV_PRF_nominally_closer_to_externally_ground_reported_neighbor":bool(dn<dh),
                "original_NASA_DV_PRF_source_target_to_neighbor_separation_arcsec":float(h.separation(n).arcsec),
                "original_DV_first_sector_PRF_physically_interpretable":True,
                "original_DV_PRF_sky_centroid_angular_uncertainty_RA_Dec_degrees_not_correlated":{
                    "RA":official["original_RA_degrees"]["uncertainty"],
                    "Dec":official["original_Dec_degrees"]["uncertainty"]}
            })
        rows.append(row)
    return {
        "original_DV_first_frozen_sector_difference_image_result_rows":rows,
        "n_original_DV_differences_with_first_sector":len(rows),
        "n_valid_original_NASA_DV_PRF_first_sector_centroids":sum(
            r["original_DV_first_sector_PRF_physically_interpretable"] for r in rows)
    }


def download_xml_source(uri,original_filename,dest):
    if not uri.startswith("mast:TESS/product/") or not uri.endswith("_dvr.xml") or ".." in uri:
        raise ValueError("Attempted non-official NASA DV XML or malicious path")
    dest=Path(dest)
    dest.parent.mkdir(parents=True,exist_ok=True)
    h=hashlib.sha256()
    total=0
    with requests.get(MAST_FILE_ENDPOINT,params={"uri":uri},stream=True,timeout=(35,165)) as req:
        req.raise_for_status()
        with dest.open("wb") as file:
            for chunk in req.iter_content(chunk_size=1_048_576):
                if not chunk:continue
                total+=len(chunk)
                if total>MAX_XML_BYTES:
                    dest.unlink(missing_ok=True)
                    raise ValueError("Official NASA DV XML source too large")
                h.update(chunk)
                file.write(chunk)
    original=dest.read_bytes()
    if b"<?xml" not in original[:128] or b"<" not in original[:128]:
        raise ValueError("MAST original source is not valid XML")
    return original,{
        "original_NASA_DV_MAST_download_URI":uri,
        "original_NASA_DV_filename":original_filename,
        "original_source_byte_count":total,
        "original_source_SHA256":h.hexdigest(),
    }


def run(source_inventory,original_frozen,out,working):
    sr=Path(source_inventory).read_bytes()
    locked=json.loads(sr)
    fr=Path(original_frozen).read_bytes()
    frozen=json.loads(fr)
    if not locked.get("original_source_DISCOVERY_only_no_DV_files_downloaded") or \
       locked.get("exact_previously_ground_corroborrated_host_TICs_attempted")!=2:
        raise ValueError("No original external source-only MAST DV freeze")
    frows={int(x["TIC_ID"]):x for x in frozen["source_records"]}
    pre={int(x["TIC_ID"]):x for x in locked["source_results_all_no_selection_on_centroid_outcomes"]}
    if set(pre)!=set(HOSTS) or not set(HOSTS).issubset(frows):
        raise ValueError("Ground source host TICs changed between original discovery and DV XML")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    working=Path(working);working.mkdir(parents=True,exist_ok=True)
    records=[]
    for tic,toi in HOSTS.items():
        entry=pre[tic];src=frows[tic]
        first=int(entry["original_source_frozen_SPOC_first_sector"])
        if (toi!=entry["TOI"] or src["TOI"]!=toi or
            int(src["selected_first_original_SPOC_2min_sector"])!=first):
            raise ValueError("Original prior first sector or TOI was replaced")
        candidates=entry["original_DV_frozen_first_sector_search_covering_XML_products"]
        if len(candidates)>MAX_XML_PER_SOURCE:
            raise ValueError("Unexpected source original NASA DV XML product overflow")
        if len({c["original_MAST_product_URI"] for c in candidates})!=len(candidates):
            raise ValueError("Original source repeated a NASA DV XML product")
        star={
          "TIC_ID":tic,"TOI":toi,
          "original_frozen_TESS_SPOC_sector":first,
          "original_external_ground_neighbor_TIC":int(src["original_neb_named_neighbor_TIC_not_physical_truth"]),
          "original_ExoFOP_published_P_days":entry["original_ExoFOP_period_days"],
          "original_ExoFOP_published_epoch_BTJD":entry["original_ExoFOP_epoch_BTJD"],
          "original_ExoFOP_published_duration_days":entry["original_ExoFOP_duration_days"],
          "exact_all_original_MAST_DV_XML_source_count":len(candidates),
          "source_archive_records_all_no_selection_on_offset":[],
        }
        if not candidates:
            star["official_NASA_SPOC_DV_TCE_status"]="no_original_source_frozen_sector_DV_XML"
        # Primary catalog target position is independently known from original
        # exact TESS FITS first-sector header. Use original near-TIC catalog
        # position and its catalog separation + PA to geometrically derive
        # primary sky, but preferentially verify official XML ticReference
        # centroid matches the ground WCS target in stage 2. Do not conjure a
        # sky origin from RA/Dec of a different source.
        for i,product in enumerate(candidates):
            r={
                "original_DV_XML_product":product,
                "original_DV_XML_source_processing_status":"not_attempted",
                "original_DV_TCE_candidates_not_filtered_by_centroid":[],
                "original_DV_frozen_sector_PRF_differences_for_only_ephemeris_matched_TCEs":[],
            }
            try:
                # Stable i from sorted frozen product list; no science outcome
                # used to pick source URI or order.
                path=working/str(tic)/(str(i)+"_"+product["product_filename"])
                data,prov=download_xml_source(
                    product["original_MAST_product_URI"],
                    product["product_filename"],path)
                root,all_planets,head=original_nasa_dv_source_xml(data,tic)
                r["original_DV_XML_source_provenance"]=prov
                r["original_DV_run_root_metadata"]=head
                p_by_num={int(q.attrib["planetNumber"]):q for q in root
                           if tagname(q)=="planetResults" and "planetNumber" in q.attrib}
                if len(p_by_num)!=head["original_DV_actual_planetResults_count"]:
                    raise ValueError("NASA DV original duplicated/invalid TCE candidate number")
                for p in all_planets:
                    ans=source_tce_match(
                        p,float(entry["original_ExoFOP_period_days"]),
                        float(entry["original_ExoFOP_epoch_BTJD"]),
                        float(entry["original_ExoFOP_duration_days"]))
                    record={**p,**ans}
                    r["original_DV_TCE_candidates_not_filtered_by_centroid"].append(record)
                matches=[p for p in r["original_DV_TCE_candidates_not_filtered_by_centroid"]
                    if p["matches_published_original_TOI_period_and_phase_before_any_centroid_read"]]
                if len(matches)==1:
                    pnum=matches[0]["original_NASA_DV_planet_number"]
                    if pnum not in p_by_num:
                        raise ValueError("Matched authentic NASA planet result not uniquely identified")
                    # Ground physical neighbor reference is original independent
                    # catalog RA/Dec. Primary reference is official DV TIC
                    # catalog centroid in each original first-sector DI row.
                    neighbor_sky=(
                        float(src["original_nearby_catalog_RA_deg"]),
                        float(src["original_nearby_catalog_Dec_deg"]))
                    # The first-sector catalog position stored in the genuine
                    # NASA XML is the primary coordinate; do not invent it.
                    obj=p_by_num[pnum]
                    diff_results=childs_named(obj,"differenceImageResults")
                    first_results=[]
                    for x in diff_results:
                        try:
                            if int(x.attrib.get("sector","-1"))==first:
                                first_results.append(x)
                        except (TypeError,ValueError):
                            continue
                    host_sky=None
                    for x in first_results:
                        reference=position_centroid_group(x,"ticReferenceCentroid")
                        if reference["valid_RA_Dec"]:
                            host_sky=(reference["original_RA_degrees"]["value"],
                                      reference["original_Dec_degrees"]["value"])
                            break
                    if host_sky is None:
                        r["original_DV_frozen_sector_localization_status"]="no_valid_first_sector_catalog_target_position"
                    else:
                        r["original_DV_frozen_sector_localization_status"]="original_DV_TCE_period_phase_match_and_official_sky_reference"
                        output=original_dv_match_centroids(obj,first,host_sky,neighbor_sky)
                        r["original_DV_frozen_sector_PRF_differences_for_only_ephemeris_matched_TCEs"].append({
                            "original_DV_TCE_planet_number":pnum,
                            "original_DV_original_TOI_ephemeris_match":matches[0],
                            "original_DV_first_sector_host_sky_from_DV_TIC_reference_degrees":list(host_sky),
                            "original_neighbor_sky_original_exofop_catalog_degrees":list(neighbor_sky),
                            **output
                        })
                elif len(matches)==0:
                    r["original_DV_frozen_sector_localization_status"]="no_original_DV_TCE_matches_exact_TOI_period_and_phase"
                else:
                    r["original_DV_frozen_sector_localization_status"]="multiple_ephemeris_matches_ambiguous_refuse_selection"
                r["original_DV_ephemeris_matched_TCE_count_before_centroid"]=len(matches)
                r["original_DV_XML_source_processing_status"]="processed_original"
            except (ValueError,KeyError,OSError,ET.ParseError,requests.RequestException) as err:
                r["original_DV_XML_source_processing_status"]="not_evaluable"
                r["original_DV_XML_source_error"]=str(err)[:430]
            print("ORIGINAL_OFFICIAL_NASA_DV_TCE_SOURCE",json.dumps({
                "host":tic,"TOI":toi,"run":product["product_filename"],
                "status":r["original_DV_XML_source_processing_status"],
                "matched_original_TOI_TCEs":r.get("original_DV_ephemeris_matched_TCE_count_before_centroid"),
                "first_sector_prf":r["original_DV_frozen_sector_PRF_differences_for_only_ephemeris_matched_TCEs"],
                "no_source_status":r.get("original_DV_frozen_sector_localization_status"),
                "error":r.get("original_DV_XML_source_error")
            }),flush=True)
            star["source_archive_records_all_no_selection_on_offset"].append(r)
        records.append(star)
    summary={
        "experiment":"Original NASA TESS SPOC official Data Validation XML PRF difference-image centroid benchmark against ground-WCS corroborated neighbor TICs, period and phase match first, centroid values only for unique TCE matches",
        "original_source_only_DV_discovery_SHA256":hashlib.sha256(sr).hexdigest(),
        "original_precentroid_ground_source_lock_SHA256":hashlib.sha256(fr).hexdigest(),
        "exact_physical_ground_NEBS_attempted":len(records),
        "authentic_original_SPOC_DV_XML_products_queried":sum(
            x["exact_all_original_MAST_DV_XML_source_count"] for x in records),
        "original_SPOC_DV_XML_sources_successfully_parsed":sum(
            x["original_DV_XML_source_processing_status"]=="processed_original"
            for r in records for x in r["source_archive_records_all_no_selection_on_offset"]),
        "unique_original_MAST_DV_runs_matching_TOI_period_and_phase":sum(
            x.get("original_DV_ephemeris_matched_TCE_count_before_centroid",0)==1
            for r in records for x in r["source_archive_records_all_no_selection_on_offset"]),
        "valid_original_NASA_first_sector_PRF_centroid_comparisons":sum(
            o["n_valid_original_NASA_DV_PRF_first_sector_centroids"]
            for r in records for x in r["source_archive_records_all_no_selection_on_offset"]
            for o in x["original_DV_frozen_sector_PRF_differences_for_only_ephemeris_matched_TCEs"]),
        "all_original_host_source_DV_XML_TCE_and_PRF_results":records,
        "physics_limits":[
          "Official NASA DV product XML containing target TIC does not imply the specific ExoFOP TOI was a detected TCE. Matching prior original published period and phase happens before any PRF sky source metrics are read.",
          "There can be six nested campaign spans of the same original star; they are repeated NASA pipeline reprocessings, not six independent stars or holdout labels.",
          "A DV PRF centroid with uncertainty=-1 or invalid difference-image quality flag is explicitly excluded from physical interpretation, not filled by an alternative metric.",
          "The official PRF source position is compared to the original NASA XML primary TIC catalog sky coordinates and separately frozen ExoFOP neighboring star sky position; no WCS angle is tuned to agreement.",
          "Official NASA DV difference images are mission-produced by SPOC from its transit search, whereas our simple TPF positive-only image method is not equivalent.",
          "Ground-photometry aperture sky association is observer-reduced original source, but neither independent raw image ground photometry nor new planet classification accuracy remeasured here.",
          "A result from one or two retrospectively chosen ground NEB examples is not generalized classification or NASA ExoMiner++ improvement.",
          "No neural weights, official NASA classifier scores, planet labels or source selection made based on newly seen PRF centroid distances."
        ]
    }
    (out/"two_ground_NEBS_official_NASA_DV_XML_original_PRF_centroid_source_comparison.json").write_text(
        json.dumps(summary,indent=2,default=str)+"\n")
    return summary


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-DV-source-inventory",required=True)
    p.add_argument("--frozen-five-source-manifest",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--working",required=True)
    a=p.parse_args()
    run(a.original_DV_source_inventory,a.frozen_five_source_manifest,a.out,a.working)
