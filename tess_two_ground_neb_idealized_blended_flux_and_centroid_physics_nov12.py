"""Post-hoc TESS flux-dilution and CCD centroid-vector physics consistency test.

Inputs are immutable authentic original ExoFOP observer notes and ground
time-series, original separate neighbor TIC T-band magnitudes/astrometry,
original NASA/TESS SPOC first-sector PDCSAP flux and target-pixel WCS, and
source-preserved physical direction controls.

Not an independent *prediction* because the TESS events and source observations
were already examined; not true NASA TPF aperture throughput, PRF
difference-image localization, a new planet, or model accuracy.
"""
import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path

import numpy as np

CASES={
  382437043:{"TOI":"1223.01","external_neighbor_TIC":382437045,"source_note_ID":906274},
  264303333:{"TOI":"2250.01","external_neighbor_TIC":1884344804,"source_note_ID":222162}
}
TIC_MAG_COLUMN="TESS Mag"


def positive_float(value):
    try:
        x=float(value)
        return x if np.isfinite(x) and x>0 else None
    except (TypeError,ValueError):return None


def original_ground_observer_dT_from_source(note_data,host):
    items=[x for x in note_data["original_observer_source_file_details"]
           if int(x["host_TIC_ID"])==host and int(x["original_file_ID"])==CASES[host]["source_note_ID"]]
    if len(items)!=1 or items[0]["source_download_status"]!="success":
        raise ValueError("Original ground observer source note missing")
    note=items[0]
    raw_lines=note["original_source_text_evidence"]["original_excerpt_first_nonblank_lines"]
    text="\n".join(raw_lines)
    # Evidence is actual observer quoted note, not independently measured photometry.
    matches=re.findall(r"(?:ΔT|dT)\s*=\s*([0-9]+(?:\.[0-9]+)?)",text,flags=re.I)
    if len(matches)!=1:
        raise ValueError("Original ExoFOP observer note did not give one unambiguous relative TESS magnitude")
    delta=float(matches[0])
    if not 0<delta<20:raise ValueError("Original quoted T-band contrast impossible")
    return {
        "relative_TESS_magnitude_original_observer_note":delta,
        "original_ExoFOP_observer_source_file_ID":note["original_file_ID"],
        "original_observer_uploaded_note_SHA256":note["original_uploaded_file_source_SHA256"],
        "quoted_note_short_excerpt":next(
            (line[:390] for line in raw_lines if "TIC" in line and re.search(r"(?:ΔT|dT)\s*=",line,re.I)),
            ""),
        "relative_TESS_magnitude_directly_independently_measured_by_this_project":False
    }


def independent_catalog_neighbor_tmag(blob,host,neighbor):
    text=blob.decode("utf-8-sig")
    reader=csv.DictReader(io.StringIO(text))
    if not {"TIC ID","TESS Mag","Separation (arcsec)","RA","Dec"}.issubset(reader.fieldnames or []):
        raise ValueError("Original separately archived neighbor astrometry lacks its magnitude")
    matching=[x for x in reader if str(x["TIC ID"]).strip()==str(neighbor)]
    if len(matching)!=1:
        raise ValueError("Original independent ExoFOP neighbor TIC absent or not unique")
    row=matching[0]
    mag=positive_float(row["TESS Mag"])
    sep=positive_float(row["Separation (arcsec)"])
    if mag is None or sep is None:
        raise ValueError("Original neighbor astrometry source magnitude or separation invalid")
    return {"external_neighbor_TESS_Mag":mag,
            "external_neighbor_sky_separation_arcsec":sep,
            "external_neighbor_catalog_SHA256":hashlib.sha256(blob).hexdigest(),
            "neighbor_original_RA":row["RA"],"neighbor_original_Dec":row["Dec"]}


def original_exofop_target_tmag(catalog_blob,host,toi):
    source=csv.DictReader(io.StringIO(catalog_blob.decode("utf-8-sig")))
    cols=set(source.fieldnames or [])
    possible=[x for x in ("TESS Mag","TESS Mag.","Tmag","T Mag") if x in cols]
    if not possible:
        return None,"Original ExoFOP TOI source catalog has no host TESS-magnitude field"
    hits=[r for r in source if str(r.get("TIC ID","")).strip()==str(host)
          and str(r.get("TOI","")).strip()==str(toi)]
    if len(hits)!=1:
        return None,"Original ExoFOP catalog host TOI record unavailable or duplicated"
    value=positive_float(hits[0][possible[0]])
    return value,("Original independent ExoFOP TIC/TOI TESS magnitude" if
                  value is not None else "Original ExoFOP host magnitude missing")


def naive_two_star_blend(genuine_ground_intrinsic_depth_frac,delta_t_mag,target_to_neighbor_CCD):
    """Idealized full-capture, same-band target+neighbor only, no background."""
    delta=float(genuine_ground_intrinsic_depth_frac)
    mag=float(delta_t_mag)
    d=np.asarray(target_to_neighbor_CCD,dtype=float)
    if not (0<delta<1) or not (0<mag<20) or d.shape!=(2,) or not np.isfinite(d).all() or np.linalg.norm(d)<=0:
        raise ValueError("No physically valid original source dilution inputs")
    ratio=10**(-.4*mag)
    # Exact blend depth and exact two-source centroid shift from out-of-event
    # to in-event moments when only the secondary source dims.
    depth=delta*ratio/(1+ratio)
    coeff=delta*ratio/((1+ratio)*(1+(1-delta)*ratio))
    vec=(-coeff*d).tolist()
    return {
        "external_approx_neighbor_over_primary_TESS_flux_ratio":ratio,
        "idealized_original_full_aperture_TESS_diluted_depth_fraction":depth,
        "idealized_original_full_aperture_TESS_diluted_depth_ppm":depth*1e6,
        "idealized_two_star_centroid_away_vector_CCD_pixels":vec,
        "idealized_two_star_centroid_signed_away_shift_pixels":float(coeff*np.linalg.norm(d)),
        "naive_flux_completeness_and_bandpass_assumptions":
          "Exactly one fully captured target and one fully captured eclipsing neighbor, original Tmag ratio, same ground/TESS eclipse depth and no other stars",
        "original_crowded_scene_or_SPOC_aperture_fraction_unknown":True
    }


def run(tess_path,ground_flux_path,ground_sky_path,ground_notes_path,
        external_neighbor_dir,original_catalog_path,phase_result_path,
        ground_robust_path,out):
    raw_inputs={
        "original_TESS":Path(tess_path).read_bytes(),
        "original_ground_AIJ_results":Path(ground_flux_path).read_bytes(),
        "original_ground_plate_WCS":Path(ground_sky_path).read_bytes(),
        "original_observer_notes":Path(ground_notes_path).read_bytes(),
        "original_TOI_catalog":Path(original_catalog_path).read_bytes(),
        "original_TESS_quarter_phase_physics":Path(phase_result_path).read_bytes(),
        "original_ground_baseline_robust":Path(ground_robust_path).read_bytes(),
    }
    sources={k:json.loads(v) for k,v in raw_inputs.items()
             if k!="original_TOI_catalog"}
    tess=sources["original_TESS"]
    phot=sources["original_ground_AIJ_results"]
    sk=sources["original_ground_plate_WCS"]
    phase=sources["original_TESS_quarter_phase_physics"]
    robust=sources["original_ground_baseline_robust"]
    notes=sources["original_observer_notes"]
    if tess["exact_new_host_star_count_attempted"]!=5:
        raise ValueError("Not the prior full source-frozen TESS host experiment")
    orig_tess={int(x["TIC_ID"]):x for x in tess["all_original_source_results"]}
    orig_phot={int(x["TIC_ID"]):x for x in phot["original_reported_cases"]}
    orig_sky={int(x["host_TIC_ID"]):x for x in sk["original_sky_source_records"]}
    orig_phase={int(x["TIC_ID"]):x for x in phase["original_two_ground_source_records"]}
    orig_robust={int(x["TIC_ID"]):x for x in robust["all_original_same_file_same_window_results"]}
    records=[]
    for host,c in CASES.items():
        if not all(host in x for x in (orig_tess,orig_phot,orig_sky,orig_phase,orig_robust)):
            raise ValueError("One original ground-supported source TIC missing; no substitution")
        t=orig_tess[host];g=orig_phot[host];s=orig_sky[host];ph=orig_phase[host];r=orig_robust[host]
        if int(t["external_note_named_neighbor_candidate_TIC"])!=c["external_neighbor_TIC"] or int(
          s["original_external_neighbor_candidate_TIC_ID"])!=c["external_neighbor_TIC"]:
            raise ValueError("Different physical TESS source neighbor versus ground WCS")
        if not s["original_ground_target_T1_matches_TESS_target_within_fixed_8arcsec"] or not s[
            "original_ground_reported_neighbor_aperture_matches_external_TIC_within_fixed_5arcsec"]:
            raise ValueError("Original external ground WCS source TIC physical position no longer corroborated")
        note=original_ground_observer_dT_from_source(notes,host)
        astpath=Path(external_neighbor_dir)/f"original_ExoFOP_TIC_{host}_nearby_astrometry.csv"
        original_neighbor_bytes=astpath.read_bytes()
        catalog=independent_catalog_neighbor_tmag(
            original_neighbor_bytes,host,c["external_neighbor_TIC"])
        target_tmag,original_tmag_qual=original_exofop_target_tmag(
            raw_inputs["original_TOI_catalog"],host,c["TOI"])
        observer_dT=note["relative_TESS_magnitude_original_observer_note"]
        external_dT=(catalog["external_neighbor_TESS_Mag"]-target_tmag
                     if target_tmag is not None else None)
        # If original source catalog has a Tmag that conflicts with observer note,
        # retain the evidence and both predictions rather than optimize a match.
        default_dT=external_dT if external_dT is not None and 0<external_dT<20 else observer_dT
        original_ground=g["reported_neighbor_aperture_result"]
        if original_ground["status"]!="measured_original_ground_AIJ_aperture":
            raise ValueError("Original genuine ground flux could not be measured")
        measured=float(original_ground["measured_depth_ppt"])/1000
        direction=t["original_external_neighbor_in_TESS_WCS"]
        if direction["catalog_sky_geometry_consistent_with_TPF_target_position"] is not True:
            raise ValueError("Original TESS source sky geometry failed its original catalog guard")
        d=direction["target_to_neighbor_CCD_pixel_vector"]
        estimate=naive_two_star_blend(measured,default_dT,d)
        bounds=original_ground["descriptive_fixed_four_cadence_block_bootstrap_95pct_ppt"]
        pred_ci=[naive_two_star_blend(float(q)/1000,default_dT,d)[
           "idealized_original_full_aperture_TESS_diluted_depth_ppm"]
           for q in bounds]
        ground_robust=r["reported_neighbor_results"]
        pred_three={}
        for name,key in (
            ("pre_only","pre_only_baseline_depth_ppt"),
            ("post_only","post_only_baseline_depth_ppt"),
            ("outside_only_Theil_Sen","robust_theil_sen_outside_only_detrended_depth_ppt")
        ):
            val=float(ground_robust[key])
            pred_three[name]=naive_two_star_blend(val/1000,default_dT,d)[
                "idealized_original_full_aperture_TESS_diluted_depth_ppm"]
        measured_tess=float(t["true_original_event_results"]["median_PDCSAP_local_depth"])*1e6
        n_tess=int(t["true_original_event_results"]["usable_paired_original_events"])
        original_vector_ph=ph["original_TESS_direct_same_event_and_quarter_phase_comparison"]
        record={
            "TIC_ID":host,"TOI":c["TOI"],"original_neighbor_TIC":c["external_neighbor_TIC"],
            "original_TESS_sector":t["original_SPOC_sector"],
            "original_real_TESS_completed_source_event_count":n_tess,
            "original_real_TESS_source_event_positive_dips":t["true_original_event_results"][
                "n_observed_events_with_positive_PDCSAP_depth"],
            "original_MAST_source_TESS_PDCSAP_flux_median_dip_ppm":measured_tess,
            "original_observer_relative_magnitude_evidence":note,
            "original_independent_ExoFOP_neighbor_star_catalog":catalog,
            "original_ExoFOP_TIC_host_TESS_mag":target_tmag,
            "original_TIC_catalog_host_Tmag_lookup_status":original_tmag_qual,
            "derived_independent_catalog_neighbor_minus_target_dT":external_dT,
            "observer_note_dT_minus_catalog_dT":(
                observer_dT-external_dT if external_dT is not None else None),
            "original_deltaT_used_for_idealized_physical_model":default_dT,
            "deltaT_provenance_selected_without_optimizing_against_TESS_flux":
                "independent_exact TIC+TOI original ExoFOP TESS magnitudes" if
                external_dT is not None and 0<external_dT<20 else
                "original observer note dT because target catalog magnitude missing",
            "idealized_ground_to_TESS_physical_blend_prediction":estimate,
            "predicted_TESS_blend_dip_descriptive_ground_flux_interval_ppm":pred_ci,
            "predicted_TESS_diluted_depth_by_three_ground_baseline_methods_ppm":pred_three,
            "original_TESS_minus_naive_two_star_predicted_flux_depth_ppm":
                measured_tess-estimate["idealized_original_full_aperture_TESS_diluted_depth_ppm"],
            "original_TESS_to_naive_two_star_predicted_flux_depth_ratio":(
                measured_tess/estimate["idealized_original_full_aperture_TESS_diluted_depth_ppm"]),
            "actual_TESS_ground_source_physical_away_projection":original_vector_ph[
                "true_signal"],
            "actual_TESS_phase_specific_away_direction_gain_pixels":original_vector_ph[
                "pointing_correction_gain_in_true_phase_specific_signed_away_projection_pixels"],
            "original_three_complete_TESS_real_and_each_control_eligible":original_vector_ph[
                "minimum_three_true_and_each_fixed_phase_control_for_source_level_summary"],
            "original_ground_aperture_to_catalog_source_offset_arcsec":s[
                "original_ground_reported_neighbor_aperture_sky_offset_arcsec"],
            "source_mode":"POSTHOC physical order-of-magnitude/source consistency, NOT blind prediction or PRF/exoplanet classifier validation",
        }
        print("ORIGINAL_GROUND_TESS_DILUTION",json.dumps({
            "host":host,"TOI":c["TOI"],"N_TESS":n_tess,
            "neighbor_TIC":c["external_neighbor_TIC"],
            "dT_note":observer_dT,"dT_catalog":external_dT,
            "measured_ground_intrinsic_candidate_ppt":original_ground["measured_depth_ppt"],
            "naive_predicted_blended_TESS_ppm":estimate["idealized_original_full_aperture_TESS_diluted_depth_ppm"],
            "genuine_original_TESS_PDCSAP_median_ppm":measured_tess,
            "predicted_interval_ground_flux_conditional_ppm":pred_ci,
            "predicted_raw_ground_robustness_ppm":pred_three,
            "naive_physical_centroid_signed_away_CCD_pixels":estimate[
                "idealized_two_star_centroid_signed_away_shift_pixels"],
            "TESS_true_signed_away_raw_CCD_pixels":original_vector_ph[
                "true_signal"]["raw_centroid_signed_away_projection_pixels"],
            "TESS_true_signed_away_corrected_CCD_pixels":original_vector_ph[
                "true_signal"]["pointing_subtracted_centroid_signed_away_projection_pixels"],
            "phase_specific_raw_minus_corrected_physical_gain_CCD_pixels":record[
                "actual_TESS_phase_specific_away_direction_gain_pixels"]
        }),flush=True)
        records.append(record)
    result={
        "scientific_question":"Can independently measured original ground eclipsing-neighbor aperture depths and actual original TESS catalog flux contrasts explain the original SPOC median transit brightness and signed CCD moment-centroid vector, within a deliberately idealized two-star full-inclusion model?",
        "n_previously_ground_sky_supported_NEBS":len(records),
        "n_three_real_TESS_events_eligible":sum(
            r["original_three_complete_TESS_real_and_each_control_eligible"] for r in records),
        "all_posthoc_two_source_physical_predictions":records,
        "source_original_input_SHA256":{k:hashlib.sha256(v).hexdigest()
                                         for k,v in raw_inputs.items()},
        "status_of_validated_NASA_ExoMiner_planet_classification_gain":"NOT TESTED",
        "limitations":[
            "Predictions are POST-HOC physical consistency checks after examining source-selected ground notes and TESS observed events; not a pre-registered blind model benchmark.",
            "Original ground zs-band relative aperture depth is a proxy, not known to equal TESS-band intrinsic eclipse depth.",
            "Idealized flux equation assumes exactly two fully included sources and zero other flux/background; the genuine TESS SPOC photometric aperture may not include every neighbor pixel or may include extra neighbors, and PDCSAP calibrated flux can differ from raw SAP.",
            "Original TESS source-matched sky vector from sector-specific FITS WCS predicts two-star moment centroid, not NASA mission PRF difference-image true source classification.",
            "Nominal deltaT from external catalog or public observer note is not a measured high-precision model input; original ground bootstrap variation ignores flux-contrast and TESS calibration uncertainty.",
            "All two source host TICs previously examined, one with only two original TESS event windows; no generalizable direction/localization accuracy can be measured.",
            "The true identified ground source aperture position and time-series stem from the observer-reduced original files; no new fully independent raw-CCD re-reduction.",
            "No original NASA ExoMiner++ neural weights, official model outputs, mission difference-image products or source labels have been changed."
        ]
    }
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/"original_two_ground_supported_NEBS_TESS_flux_dilution_and_centroid_physics_POSTHOC.json").write_text(
        json.dumps(result,indent=2)+"\n")
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-five-TESS",required=True)
    p.add_argument("--original-ground-flux",required=True)
    p.add_argument("--original-ground-sky",required=True)
    p.add_argument("--original-note-audit",required=True)
    p.add_argument("--original-neighbor-catalogs",required=True)
    p.add_argument("--original-exofop-catalog",required=True)
    p.add_argument("--original-quarter-phase-results",required=True)
    p.add_argument("--original-ground-robustness",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.original_five_TESS,a.original_ground_flux,a.original_ground_sky,
        a.original_note_audit,a.original_neighbor_catalogs,
        a.original_exofop_catalog,a.original_quarter_phase_results,
        a.original_ground_robustness,a.out)
