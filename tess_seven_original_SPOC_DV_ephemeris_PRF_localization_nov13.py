"""Compare authentic NASA SPOC DV fitted PRF transit source sky coordinates with
original, independently ground-aperture-WCS matched NEB TICs, and report the
five independently catalog-confirmed planet host controls.

Seven host TICs, original first TESS sectors, TOI ephemerides, source
identities and original SPOC DVR XML URIs were frozen or separately archived
before this experiment. Official reported TCEs MUST independently match the
published TOI period and transit epoch (phase) before any centroid conclusion.

The official NASA DV differenceImageCentroid is a PRF model fit to a
difference image, not our naive positive-only TPF pixel-image centroid.
The former can still be inaccurate at low SNR or under blends: source-closest
is descriptive, not a validated source classification. Individual SPOC
sectors and multisection robust centroids are kept STRICTLY separate.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

from astropy import units as u
from astropy.coordinates import SkyCoord
import numpy as np
import requests
import xml.etree.ElementTree as ET

from tess_seven_official_SPOC_original_DVR_XML_structure_inspection_nov13 import (
    fetch_original_DV_XML,local,choose_original_source_DV_XML
)
from tess_seven_original_SPOC_official_DV_product_discovery_nov13 import (
    TWO_OFFTARGET,FIVE_PLANETS
)

P_MAX_RELATIVE_DIFFERENCE=.01
EPOCH_MAX_FRACTION_OF_PERIOD=.05
EPOCH_MAX_DURATION_FACTOR=2.
SKY_TARGET_CONSISTENCY_ARCSEC=8.


def safe_float(value):
    try:
        z=float(value)
        return z if math.isfinite(z) else None
    except (ValueError,TypeError):
        return None


def child(element,tag):
    if element is None:return None
    return next((x for x in element if local(x.tag)==tag),None)


def descendants(element,tag):
    if element is None:return []
    return [x for x in element.iter() if local(x.tag)==tag]


def value_record(node,child_tag):
    element=child(node,child_tag)
    if element is None:return {"value":None,"uncertainty":None,"raw_attributes":None}
    return {"value":safe_float(element.attrib.get("value")),
            "uncertainty":safe_float(element.attrib.get("uncertainty")),
            "raw_attributes":dict(element.attrib)}


def quantity_bundle(element,tags):
    return {k:value_record(element,k) for k in tags}


def correct_TCE_period_and_epoch(candidate,original_period,original_epoch,original_duration):
    if candidate is None:
        return {"match":False,"reason":"no_original_SPOC_TCE_planetCandidate"}
    p=safe_float(candidate.attrib.get("orbitalPeriodInDays"))
    e=safe_float(candidate.attrib.get("epochTjd"))
    if p is None or e is None or p<=0:
        return {"match":False,"reason":"original_SPOC_TCE_period_or_epoch_missing",
                "TCE_period_days":p,"TCE_epoch_TJD":e}
    frac=abs(p/original_period-1)
    # TESS TJD and TESS BTJD both use the same nominal offset 2457000 d
    # (barycentric distinction should be considered at sub-minute precision).
    diff=abs((e-original_epoch+.5*original_period)%original_period-.5*original_period)
    threshold=max(EPOCH_MAX_DURATION_FACTOR*original_duration,
                  EPOCH_MAX_FRACTION_OF_PERIOD*original_period)
    passperiod=frac<=P_MAX_RELATIVE_DIFFERENCE
    passphase=diff<=threshold
    return {
        "match":bool(passperiod and passphase),
        "TCE_period_days":p,
        "TCE_epoch_TJD":e,
        "original_ExoFOP_period_days":float(original_period),
        "original_ExoFOP_epoch_BTJD":float(original_epoch),
        "original_ExoFOP_duration_days":float(original_duration),
        "relative_period_difference":float(frac),
        "original_orbit_folded_epoch_residual_days":float(diff),
        "predeclared_epoch_residual_tolerance_days":float(threshold),
        "period_pass":bool(passperiod),
        "epoch_pass":bool(passphase),
        "reason":("period_and_epoch_both_match" if passperiod and passphase
                  else "original_DV_TCE_not_consistent_with_frozen_TOI_period_and_epoch")
    }


def coord_from_xml(node):
    ra=value_record(node,"raDegrees")
    dec=value_record(node,"decDegrees")
    if ra["value"] is None or dec["value"] is None:
        return None
    if not (0<=ra["value"]<360 and -90<=dec["value"]<=90):
        return None
    return SkyCoord(ra["value"]*u.deg,dec["value"]*u.deg,frame="icrs")


def sky_arcsec(a,b):
    return float(a.separation(b).arcsec) if a is not None and b is not None else None


def extract_first_sector_dv_PRF(difference,first_sector,host_sky,neighbor_sky):
    """Preserve all per-sector PRF difference-image results, even bad ones."""
    row={
       "original_DV_sector":safe_float(difference.attrib.get("sector")),
       "original_DV_numberOfTransits":safe_float(difference.attrib.get("numberOfTransits")),
       "original_DV_targetTableId":difference.attrib.get("targetTableId"),
       "original_DV_overlappedTransits":difference.attrib.get("overlappedTransits"),
       "original_DV_intransit_cadences":safe_float(difference.attrib.get("numberOfCadencesInTransit")),
       "original_DV_outoftransit_cadences":safe_float(difference.attrib.get("numberOfCadencesOutOfTransit")),
       "original_DV_sector_equal_to_previously_frozen_first_SPOC_sector":str(
           difference.attrib.get("sector"))==str(first_sector),
    }
    target=child(difference,"ticReferenceCentroid")
    background=child(difference,"controlImageCentroid")
    signal=child(difference,"differenceImageCentroid")
    row["original_TIC_reference_fit"] = quantity_bundle(target,(
        "raDegrees","decDegrees","row","column"))
    row["original_OUT_OF_TRANSIT_PRF_fit"]=quantity_bundle(background,(
        "raDegrees","decDegrees","row","column"))
    row["original_DIFFERENCE_IMAGE_PRF_fit"]=quantity_bundle(signal,(
        "raDegrees","decDegrees","row","column"))
    offsets=child(difference,"ticCentroidOffsets")
    row["original_official_SPOC_DV_TIC_reference_offsets"]=quantity_bundle(
        offsets,("raOffset","decOffset","skyOffset","rowOffset","columnOffset"))
    offsets2=child(difference,"controlCentroidOffsets")
    row["original_official_SPOC_DV_OUT_OF_TRANSIT_offsets"]=quantity_bundle(
        offsets2,("raOffset","decOffset","skyOffset","rowOffset","columnOffset"))
    tic_pos=coord_from_xml(target)
    signal_pos=coord_from_xml(signal)
    out_pos=coord_from_xml(background)
    row["original_DV_catalog_TIC_reference_to_original_external_NASA_host_arcsec"]=sky_arcsec(
        tic_pos,host_sky)
    row["original_mission_PRF_source_to_DV_TIC_reference_arcsec"]=sky_arcsec(
        signal_pos,tic_pos)
    row["original_mission_PRF_source_to_DV_OOT_image_arcsec"]=sky_arcsec(
        signal_pos,out_pos)
    row["original_mission_PRF_source_to_original_external_host_arcsec"]=sky_arcsec(
        signal_pos,host_sky)
    row["original_mission_PRF_source_to_original_ground_reported_neighbor_arcsec"]=(
        sky_arcsec(signal_pos,neighbor_sky) if neighbor_sky is not None else None)
    chi=row["original_mission_PRF_source_to_original_ground_reported_neighbor_arcsec"]
    th=row["original_mission_PRF_source_to_original_external_host_arcsec"]
    row["official_PRF_fit_closer_to_original_ground_NEb_than_original_host"]=(
        bool(chi<th) if chi is not None and th is not None else None)
    sig=(value_record(signal,"raDegrees")["uncertainty"],
         value_record(signal,"decDegrees")["uncertainty"])
    row["original_PRF_ra_dec_uncertainties_valid"] =bool(
        all(x is not None and x>=0 for x in sig))
    row["original_first_sector_DV_position_quality_guard_passed"]=bool(
        row["original_DV_sector_equal_to_previously_frozen_first_SPOC_sector"]
        and row["original_PRF_ra_dec_uncertainties_valid"]
        and signal_pos is not None
        and tic_pos is not None
        and row["original_DV_catalog_TIC_reference_to_original_external_NASA_host_arcsec"] is not None
        and row["original_DV_catalog_TIC_reference_to_original_external_NASA_host_arcsec"]<=SKY_TARGET_CONSISTENCY_ARCSEC
    )
    return row


def source_DV_TCEs(root,source,ground=None):
    source_period=float(source["original_ExoFOP_period_days"])
    source_epoch=float(source["original_ExoFOP_epoch_BTJD"])
    source_duration=float(source["original_ExoFOP_duration_days"])
    tic=int(source["TIC_ID"]);toi=source["TOI"]
    if ground:
        near=SkyCoord(float(ground["original_nearby_catalog_RA_deg"])*u.deg,
                       float(ground["original_nearby_catalog_Dec_deg"])*u.deg)
        # Target from original mission DV own catalog reference sky position,
        # plus independent original ground original TPF sky after WCS.
        host=SkyCoord(float(ground["original_primary_NASA_ra"])*u.deg,
                      float(ground["original_primary_NASA_dec"])*u.deg)
    else:
        near=None
        host=SkyCoord(float(source["original_NASA_host_catalog_RA_deg"])*u.deg,
                      float(source["original_NASA_host_catalog_Dec_deg"])*u.deg)
    planet_nodes=[r for r in root.iter() if local(r.tag)=="planetResults"]
    tces=[]
    for pp in planet_nodes:
        cand=child(pp,"planetCandidate")
        match=correct_TCE_period_and_epoch(
            cand,source_period,source_epoch,source_duration)
        label=pp.attrib.get("toiId")
        explicit_TOI=label and label.strip().removeprefix("TOI-")
        match["official_original_XML_TOI_label"]=label
        match["source_original_ExoFOP_TOI"]=toi
        match["official_explicit_TOI_ID_compatible"]=(
             (explicit_TOI==toi) if label else None)
        # If official older XML explicit label conflicts, do not silently
        # accept even if period aliases; require consistent independent label.
        eligible=bool(match["match"] and
              match["official_explicit_TOI_ID_compatible"] is not False)
        event={
            "original_DV_planetNumber":pp.attrib.get("planetNumber"),
            "original_DV_toiId":label,
            "original_DV_toiCorrelation":pp.attrib.get("toiCorrelation"),
            "all_original_TCE_timing_compatibility_checks":match,
            "NASA_DV_TCE_unique_candidate_eligibility_prior_to_examining_PRF":eligible,
            "original_DV_TCE_suspectedEB_flag":cand.attrib.get("suspectedEclipsingBinary") if cand is not None else None,
            "original_DV_TCE_observedTransitCount":cand.attrib.get("observedTransitCount") if cand is not None else None,
        }
        # Always report original sectors and positions to audit wrong TCE,
        # but draw no matched source interpretation for unmatched TCEs.
        difs=descendants(pp,"differenceImageResults")
        event["original_DV_all_sector_diff_image_fit_results"]=[
            extract_first_sector_dv_PRF(r,int(source["source_frozen_first_SPOC_2min_sector"]),host,near)
            for r in difs]
        first=[r for r in event["original_DV_all_sector_diff_image_fit_results"]
               if r["original_DV_sector_equal_to_previously_frozen_first_SPOC_sector"]]
        event["original_DV_first_sector_fit_count"]=len(first)
        event["original_DV_first_sector_fit_records_all"]=first
        if eligible and len(first)==1:
            this=first[0]
            event["original_DV_FIRST_SECTOR_PRF_TOI_match_and_source_QC_status"]=(
                "same_ephemeris_SPOC_TCE_and_original_first_sector_PRF_quality_passed" if this[
                    "original_first_sector_DV_position_quality_guard_passed"]
                else "same_ephemeris_TCE_but_PRF_position_quality_guard_failed")
        elif eligible and len(first)==0:
            event["original_DV_FIRST_SECTOR_PRF_TOI_match_and_source_QC_status"]=(
                "same_ephemeris_TCE_but_original_frozen_sector_DV_image_missing")
        elif eligible:
            event["original_DV_FIRST_SECTOR_PRF_TOI_match_and_source_QC_status"]=(
                "same_ephemeris_TCE_but_multiple_first_sector_PRF_table_records_no_selection")
        else:
            event["original_DV_FIRST_SECTOR_PRF_TOI_match_and_source_QC_status"]=(
                "not_original_TOI_TCE_ephemeris_match_do_not_interpret_PRF")
        tces.append(event)
    eligible=[x for x in tces if x[
        "NASA_DV_TCE_unique_candidate_eligibility_prior_to_examining_PRF"]]
    return {
        "official_DV_total_original_TCEs":len(tces),
        "original_TCEs_meeting_TESS_TOI_period_and_epoch_and_ID_rules":len(eligible),
        "official_original_NASA_SPOC_TCE_and_sector_PRF_diagnostics_all":tces,
        "only_one_TOI_compatible_TCE":len(eligible)==1,
        "same_ephemeris_first_sector_localization_status":(
            eligible[0]["original_DV_FIRST_SECTOR_PRF_TOI_match_and_source_QC_status"]
            if len(eligible)==1 else
            "no_unambiguous_original_TOI_corresponding_TCE"),
        "no_arbitrary_TCE_or_sector_PRF_optimization":True,
    }


def run(DV_source_json,nebs_frozen_json,planets_frozen_json,prior_ground_TESS_source_json,out):
    source_path=Path(DV_source_json)
    original_bytes=source_path.read_bytes()
    old=json.loads(original_bytes)
    records=old["exact_all_seven_selected_original_NASA_DV_source_and_unmatched_TCE_structure"]
    if len(records)!=7 or not old["not_a_TCE_source_location_validation_yet"]:
        raise ValueError("Wrong source-hashed original NASA DV XML structure inventory")
    nep=json.loads(Path(nebs_frozen_json).read_text())
    pp=json.loads(Path(planets_frozen_json).read_text())
    ground={int(x["TIC_ID"]):x for x in nep["source_records"]}
    planets={int(x["TIC_ID"]):x for x in pp["source_records"]}
    historical_TESS_bytes=Path(prior_ground_TESS_source_json).read_bytes()
    historical_TESS=json.loads(historical_TESS_bytes)
    if historical_TESS.get("exact_new_host_star_count_attempted")!=5:
        raise ValueError("Original ground-host TESS first-sector source record absent")
    historical={int(x["TIC_ID"]):x for x in historical_TESS["all_original_source_results"]}
    if (set(TWO_OFFTARGET)-set(ground) or set(FIVE_PLANETS)-set(planets) or
        set(TWO_OFFTARGET)-set(historical)):
        raise ValueError("Original source manifests no longer contain prior fixed host TICs")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for item in sorted(records,key=lambda x:x["host_TIC_ID"]):
        tic=int(item["host_TIC_ID"])
        source=(ground if tic in ground else planets)[tic]
        original_first_sector=int(source["selected_first_original_SPOC_2min_sector"])
        response={
            "original_source_host_TIC":tic,
            "original_public_ExoFOP_TOI":item["TOI"],
            "source_group":item["original_external_source_group"],
            "source_original_SPOC_2min_first_sector":original_first_sector,
            "original_public_ExoFOP_epoch_BTJD":source["original_ExoFOP_epoch_BTJD"],
            "original_public_ExoFOP_period_days":source["original_ExoFOP_period_days"],
            "original_public_ExoFOP_duration_days":source["original_ExoFOP_duration_days"],
            "ground_truth_source_localization_NOT_established_by_this_test":True
        }
        expected=item.get("real_downloaded_original_NASA_DV_XML_SHA_and_source")
        if not expected:
            response["source_status"]="source_only_previous_NASA_original_DV_XML_missing"
            rows.append(response)
            continue
        try:
            root,now=fetch_original_DV_XML(expected["source_MAST_uri"])
            if (now["original_source_SHA256"]!=expected["original_source_SHA256"]
                or now["original_XML_bytes"]!=expected["original_XML_bytes"]):
                raise ValueError("Original independent NASA SPOC report bytes changed; source SHAs do not match")
            if tic in ground:
                source=dict(source)
                original_TESS_host=historical[tic]
                fixed_sector=int(source["selected_first_original_SPOC_2min_sector"])
                if (int(original_TESS_host["original_SPOC_sector"])!=fixed_sector or
                    original_TESS_host.get("source_processing_status")!="processed"):
                    raise ValueError("Original independently archived TESS target header not same frozen first sector")
                original_header=original_TESS_host["original_SPOC_TPF_WCS_header"]
                source["original_primary_NASA_ra"]=float(
                    original_header["original_TPF_header_target_RA_deg"])
                source["original_primary_NASA_dec"]=float(
                    original_header["original_TPF_header_target_Dec_deg"])
                response["host_TIC_sky_position_source"]=(
                    "previously independently archived original SPOC TPF first-sector target header "
                    "from same original ground-host TESS data, NOT current DV XML")
                response["independent_original_TESS_TPF_target_header_sky_RA_deg"]=source[
                    "original_primary_NASA_ra"]
                response["independent_original_TESS_TPF_target_header_sky_Dec_deg"]=source[
                    "original_primary_NASA_dec"]
            x=source_DV_TCEs(root,{
                **source,"source_frozen_first_SPOC_2min_sector":original_first_sector
            },ground=source if tic in ground else None)
            response.update(
                original_report_file_SHA256=now["original_source_SHA256"],
                original_DV_XML_used_source=now["source_MAST_uri"],
                official_DV_report_start_sector=item[
                    "deterministically_chosen_smallest_range_original_DV_XML_product"][
                        "filename_DV_start_sector"],
                official_DV_report_end_sector=item[
                    "deterministically_chosen_smallest_range_original_DV_XML_product"][
                        "filename_DV_end_sector"],
                exact_original_SPOC_TCE_and_PRF_results=x,
                source_status="processed_original_NASA_DV_XML")
        except (ValueError,KeyError,requests.RequestException,ET.ParseError) as e:
            response["source_status"]="original_NASA_DV_XML_source_or_ephemeris_error"
            response["source_error"]=str(e)[:480]
        print("OFFICIAL_ORIGINAL_MISSION_DV_TCE_PRF_SKY_SOURCE",json.dumps({
            "TIC":tic,"TOI":response["original_public_ExoFOP_TOI"],
            "status":response["source_status"],
            "error":response.get("source_error"),
            "original_period":response["original_public_ExoFOP_period_days"],
            "original_epoch":response["original_public_ExoFOP_epoch_BTJD"],
            "official_DV_start_end_sectors":[response.get("official_DV_report_start_sector"),
                                             response.get("official_DV_report_end_sector")],
            "source_all_TCE_and_PRF":response.get("exact_original_SPOC_TCE_and_PRF_results")
        }),flush=True)
        rows.append(response)
    valid=[r for r in rows if r["source_status"]=="processed_original_NASA_DV_XML"
           and r["exact_original_SPOC_TCE_and_PRF_results"]["only_one_TOI_compatible_TCE"]]
    two=[r for r in valid if r["original_source_host_TIC"] in TWO_OFFTARGET]
    report={
        "research_question":"Do the unchanged, authenticated original NASA mission SPOC DV TCEs match the same published ExoFOP TOI periods/epochs, and do NASA PRF-fitted difference-image sky positions in the original frozen source sector fall nearer the independently ground-aperture sky-identified off-target TIC versus the primary host?",
        "original_prior_DV_XML_all_seven_source_SHA256":hashlib.sha256(original_bytes).hexdigest(),
        "prior_independent_ground_source_TESS_TPF_header_source_SHA256":hashlib.sha256(historical_TESS_bytes).hexdigest(),
        "source_fixed_before_centroid_observation":True,
        "original_sources_attempted":len(rows),
        "original_independently_ExoFOP_TOI_ephemeris_matched_official_TCE_host_count":len(valid),
        "matched_two_ground_supported_source_hosts":len(two),
        "all_original_NASA_DV_host_TCE_and_per_sector_PRF_source_records":rows,
        "diagnostic_only_not_new_ground_truth":True,
        "NASA_ExoMiner_model_weights_or_scores_changed":False,
        "cautions":[
            "SPOC DV xml planetResults TCEs are independently matched to ExoFOP original TOI by original period <=1% mismatch, modulo-period epoch residual <=max(2 original transit durations,5% of original period), and exact TOI label if present; older DV XML can lack published TOI IDs.",
            "DV ephemeris TJD uses nominal JD-2457000 day count; ExoFOP epoch BTJD is likewise nominal BJD-2457000, but the different time convention must be explicitly considered for fine transit timing.",
            "When no unique ephemeris-compatible TCE exists, do not treat the first report TCE as that TOI or infer absence of a real eclipse.",
            "A multisection DV report's robust centroid offsets use all included sectors; only per-differenceImageResults entries with the actual frozen first original SPOC sector are comparable to our original single-sector TPF image.",
            "Official SPOC PRF sky position can still have large uncertainties and invalid quality due to faint binary eclipses, systematics, blending, multiple neighbors and TCE aliases.",
            "Ground candidate neighbor sky was independently projected from real ground aperture FITS WCS to a TIC, but this is previously inspected case selection, NOT new blinded validation; the ground source itself may have multiple/background components.",
            "For ground NEB hosts, host target sky coordinates are independently recovered from the prior source-sha-locked original SPOC first-sector TPF header, not from the official DVR itself; historic target proper motion and reference-frame differences remain possible.",
            "Mission fitted PRF source position differs from our simple positive-only pixel centroid and difference image; disagreement does not prove the TESS official source is the planet host or invalidate independently ground-sky matched eclipse.",
            "This is not a NASA ExoMiner++ network classification accuracy audit and it did not change official pretrained scores or any source labels."
        ]
    }
    (out/"seven_original_SPOC_NASA_DV_TCE_ephemeris_matched_firstsector_PRF_source_sky_comparison.json").write_text(
        json.dumps(report,indent=2,default=str)+"\n")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--official-seven-original-DV-XML-structure",required=True)
    p.add_argument("--original-five-NEB-frozen",required=True)
    p.add_argument("--original-five-known-planets-frozen",required=True)
    p.add_argument("--original-five-ground-TESS-source-results",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.official_seven_original_DV_XML_structure,
        a.original_five_NEB_frozen,a.original_five_known_planets_frozen,
        a.original_five_ground_TESS_source_results,a.out)
