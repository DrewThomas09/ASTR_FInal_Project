"""Genuine original SPOC 2-minute MOM_CENTR on independently confirmed planet hosts.

Five host TIC, first SPOC sector, primary TOI ephemerides and original
MAST product URIs were frozen using NASA Archive+ExoFOP KP source documents
before looking at these stars' TESS moment-centroid outcomes.

This is a *catalogued confirmed transiting planet* negative/control cohort,
not a ground-imaged truth-localized control, not NASA-ExoMiner-training-
independent, and not a claim of exoplanet-vetting classification accuracy.

Original source-invariant metrics predeclared without looking at outcomes:
- median raw vs pointing-subtracted in-event vector norm
- median raw vs pointing-subtracted adjacent pre/post local drift norm
- same metrics in fixed +/−0.25 orbit phase pseudo-event windows
- source-level event-minus-shifted-control excess, n>=3 event/control windows
- complete original source (including missing or non-evaluable) reporting
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from astropy.coordinates import SkyCoord
from astropy import units as u
from scipy.stats import binomtest

from tess_original_moment_centroid_companion import load_tess_centroid_columns
from tess_toi4255_original_spoc_neb_vector_case import (
    download_original_mast,sky_wcs_from_tpf,paired_original_events
)

EXPERIMENT="ASTR_NASA_AND_EXOFOP_KP_CONFIRMED_TRANSITING_ON_TARGET_CONTROL_SPOC_SOURCE_FROZEN_NOV12"
N_FROZEN=5
CONTROLS=(-.25,.25)
B=20000
RNG_SEED=2026111207
MAX_ARCHIVE_TARGET_SEPARATION_ARCSEC=10.0


def verify_original_catalogue_frozen_controls(frozen):
    if frozen.get("experiment_id")!=EXPERIMENT:
        raise ValueError("Wrong pre-centroid on-target NASA/ExoFOP source lock")
    if frozen.get("source_manifest_frozen_before_any_control_TESS_centroid_measurements") is not True:
        raise ValueError("No authentic prior original control source freeze")
    if int(frozen.get("original_TESS_centroids_viewed",-1))!=0:
        raise ValueError("Source selected with pre-inspected original TESS centroids")
    records=frozen.get("source_records",[])
    if len(records)!=N_FROZEN or len({int(x["TIC_ID"]) for x in records})!=N_FROZEN:
        raise ValueError("Five distinct frozen confirmed planet hosts required; no replacement allowed")
    for x in records:
        if x.get("MOM_CENTR_or_POS_CORR_not_queried") is not True or x.get("no_mission_classifier_score_inspected") is not True:
            raise ValueError("Original source may be centroid- or classifier-outcome exposed")
        if x["original_ExoFOP_TFOPWG_Disposition"]!="KP":
            raise ValueError("Ground control without original ExoFOP known planet status")
        if x["NASA_archive_confirmed_transit_and_ExoFOP_KP_agree"] is not True or x.get(
            "independently_verified_on_target_ground_lightcurve_source") is not False:
            raise ValueError("Unverified off-source control falsely asserted as independent ground-labeled")
        if float(x["original_ExoFOP_period_days"])>6:
            raise ValueError("Original preselected period outside predeclared screen")
    return records


def source_metric(pairs):
    if not pairs:
        return {
            "complete_same_observed_original_event_windows":0,
            "photometry_supported_positive_local_PDCSAP_dips":0,
            "median_original_PDCSAP_local_depth":None
        }
    result={
        "complete_same_observed_original_event_windows":len(pairs),
        "photometry_supported_positive_local_PDCSAP_dips":sum(
           float(x["original_PDCSAP_local_flux_depth"])>0 for x in pairs),
        "median_original_PDCSAP_local_depth":float(np.median([
            float(x["original_PDCSAP_local_flux_depth"]) for x in pairs]))
    }
    for mode in ("raw","pointing_subtracted"):
        vx=np.asarray([r[mode+"_signed_x_CCD_pixels"] for r in pairs],dtype=float)
        vy=np.asarray([r[mode+"_signed_y_CCD_pixels"] for r in pairs],dtype=float)
        amp=np.hypot(vx,vy)
        if not np.isfinite(amp).all():
            raise ValueError("Original source event centroid vector is nonfinite")
        result[mode+"_median_event_centroid_norm_pixels"]=float(np.median(amp))
        result[mode+"_coherent_signed_event_vector_norm_pixels"]=float(
            np.hypot(np.median(vx),np.median(vy)))
    result["raw_median_pre_post_local_drift_pixels"]=float(np.median([
        x["original_raw_local_prepost_movement_pixels"] for x in pairs]))
    result["corrected_median_pre_post_local_drift_pixels"]=float(np.median([
        x["pointing_subtracted_local_prepost_movement_pixels"] for x in pairs]))
    result["reduction_in_median_original_pre_post_drift_pixels"]=(
        result["raw_median_pre_post_local_drift_pixels"]-
        result["corrected_median_pre_post_local_drift_pixels"])
    result["reduction_in_median_true_event_vector_norm_pixels"]=(
        result["raw_median_event_centroid_norm_pixels"]-
        result["pointing_subtracted_median_event_centroid_norm_pixels"])
    return result


def source_with_fixed_controls(events,controls):
    result={"actual_source_true_event":source_metric(events),
            "original_shifted_phase_control_results":[]}
    pooled=[]
    for fraction,pairs in zip(CONTROLS,controls):
        result["original_shifted_phase_control_results"].append({
            "shift_fraction_of_original_orbital_period":fraction,
            "original_source_phase_control":source_metric(pairs)
        })
        pooled+=pairs
    result["pooled_source_fixed_quarter_phase_pseudoevent_controls"]=source_metric(pooled)
    valid=(len(events)>=3 and all(len(z)>=3 for z in controls))
    result["minimum_three_real_events_AND_three_each_fixed_phase_control_windows"]=valid
    if valid:
        actual=result["actual_source_true_event"]
        control=result["pooled_source_fixed_quarter_phase_pseudoevent_controls"]
        for mode in ("raw","pointing_subtracted"):
            e=actual[mode+"_median_event_centroid_norm_pixels"]
            q=control[mode+"_median_event_centroid_norm_pixels"]
            result[mode+"_true_minus_quarter_control_centroid_norm_pixels"]=e-q
            result[mode+"_true_to_quarter_control_centroid_norm_ratio"]=e/q if q>0 else None
        result["raw_minus_corrected_change_in_event_excess_over_control_pixels"]=(
            result["raw_true_minus_quarter_control_centroid_norm_pixels"]-
            result["pointing_subtracted_true_minus_quarter_control_centroid_norm_pixels"])
    else:
        for mode in ("raw","pointing_subtracted"):
            result[mode+"_true_minus_quarter_control_centroid_norm_pixels"]=None
            result[mode+"_true_to_quarter_control_centroid_norm_ratio"]=None
        result["raw_minus_corrected_change_in_event_excess_over_control_pixels"]=None
    return result


def whole_host_descriptive_statistics(host_records):
    eligible=[x for x in host_records if
              x["source_processing_status"]=="processed" and
              x["actual_science"]["minimum_three_real_events_AND_three_each_fixed_phase_control_windows"]]
    n=len(eligible)
    result={"independent_eligible_confirmed_planet_host_TICs":n,
        "five_host_units_attempted":len(host_records),
        "all_five_preserved":len(host_records)==5}
    if n==0:return result
    for name,key in (
        ("local_drift_raw_minus_adjusted",
         ("actual_science","actual_source_true_event","reduction_in_median_original_pre_post_drift_pixels")),
        ("true_event_norm_raw_minus_adjusted",
         ("actual_science","actual_source_true_event","reduction_in_median_true_event_vector_norm_pixels")),
        ("true_minus_null_excess_raw_minus_adjusted",
         ("actual_science","raw_minus_corrected_change_in_event_excess_over_control_pixels"))):
        values=np.asarray([float(r[key[0]][key[1]][key[2]]) if len(key)==3
           else float(r[key[0]][key[1]]) for r in eligible],dtype=float)
        ups=int((values>0).sum());downs=int((values<0).sum())
        s={"median_original_source_host_delta_pixels":float(np.median(values)),
           "n_reduced":ups,"n_increased":downs,
           "exact_two_sided_host_sign_test_p_descriptive":float(
               binomtest(ups,ups+downs).pvalue) if ups+downs else None}
        if n>=2:
            rng=np.random.default_rng(RNG_SEED)
            samples=values[rng.integers(0,n,size=(B,n))]
            s["bootstrap_20000_resampled_host_median_95pct_pixels"]=np.quantile(
                np.median(samples,axis=1),[.025,.975]).tolist()
        else:
            s["bootstrap_20000_resampled_host_median_95pct_pixels"]=None
        result[name]=s
    return result


def run(frozen_path,out,working):
    path=Path(frozen_path)
    original=path.read_bytes()
    spec=json.loads(original)
    hosts=verify_original_catalogue_frozen_controls(spec)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    working=Path(working);working.mkdir(parents=True,exist_ok=True)
    rows=[]
    for h in hosts:
        tic=int(h["TIC_ID"])
        sector=int(h["selected_first_original_SPOC_2min_sector"])
        entry={
            "TIC_ID":tic,"TOI":h["TOI"],
            "original_NASA_archived_confirmed_planet":h["NASA_confirmed_host_alias"],
            "original_SPOC_sector_frozen_before_centroid":sector,
            "NASA_confirmed_planet_host_but_on_target_ground_image_not_independently_verified":True,
            "original_NASA_source_predicted_period_days":h["NASA_confirmed_transiting_planet_catalog_period_days"],
            "original_ExoFOP_period_days":h["original_ExoFOP_period_days"],
            "original_ExoFOP_epoch_BTJD":h["original_ExoFOP_epoch_BTJD"],
            "original_ExoFOP_duration_days":h["original_ExoFOP_duration_days"],
            "no_later_sector_or_target_substitution":True,
        }
        try:
            files={}
            for group in ("LC","TP"):
                p=h["original_MAST_products"][group]
                if int(p["TIC_ID"])!=tic or int(p["sector"])!=sector or p["product_group"]!=group:
                    raise ValueError("Original independent confirmed planet source SPOC product mismatch")
                file=working/str(tic)/p["productFilename"]
                entry["original_MAST_"+group+"_provenance"]=download_original_mast(
                    p["MAST_original_dataURI"],file)
                files[group]=file
            frame,metadata=load_tess_centroid_columns(files["LC"],tic,sector)
            entry["original_TESS_SPOC_LC_header_data_source"]=metadata
            _,sky,wcs_info=sky_wcs_from_tpf(files["TP"],tic,sector)
            entry["original_TESS_SPOC_TPF_WCS_header"]=wcs_info
            catalog=SkyCoord(float(h["NASA_confirmed_host_catalog_RA_deg"])*u.deg,
                            float(h["NASA_confirmed_host_catalog_Dec_deg"])*u.deg)
            sep=float(sky.separation(catalog).arcsec)
            entry["original_independent_NASA_archive_host_vs_MAST_SPOC_header_sep_arcsec"]=sep
            if sep>MAX_ARCHIVE_TARGET_SEPARATION_ARCSEC:
                raise ValueError("Independent NASA confirmed planet host coordinates mismatch original SPOC target")
            P=float(h["original_ExoFOP_period_days"])
            E=float(h["original_ExoFOP_epoch_BTJD"])
            D=float(h["original_ExoFOP_duration_days"])
            true,account=paired_original_events(frame,P,E,D,None)
            entry["original_real_event_counts"]=account
            if true:
                pd.DataFrame(true).to_csv(out/f"TIC{tic}_S{sector}_NASA_archive_confirmed_transit_actual_SPOC_centroid.csv",index=False)
            pseudos=[]
            for frac in CONTROLS:
                other,check=paired_original_events(frame,P,E+frac*P,D,None)
                pseudos.append(other)
                entry["original_quarter_phase_control_counts_"+str(frac)]=check
                if other:
                    pd.DataFrame(other).to_csv(out/f"TIC{tic}_S{sector}_quarter_phase_{frac:+.2f}_actual_source_controls.csv",index=False)
            entry["actual_science"]=source_with_fixed_controls(true,pseudos)
            entry["source_processing_status"]="processed"
        except (ValueError,KeyError,OSError,requests.RequestException) as err:
            entry["source_processing_status"]="not_evaluable"
            entry["source_error"]=str(err)[:420]
            entry["actual_science"]={"minimum_three_real_events_AND_three_each_fixed_phase_control_windows":False}
        print("CONFIRMED_PLANET_ON_TARGET_SOURCE",json.dumps({
            "TIC_ID":tic,"TOI":entry["TOI"],"NASA_planet":entry["original_NASA_archived_confirmed_planet"],
            "frozen_sector":sector,"status":entry["source_processing_status"],
            "error":entry.get("source_error"),
            "actual_event_counts":entry.get("original_real_event_counts"),
            "science":entry["actual_science"],
            "separation_arcsec":entry.get("original_independent_NASA_archive_host_vs_MAST_SPOC_header_sep_arcsec")
        }),flush=True)
        rows.append(entry)
    stats=whole_host_descriptive_statistics(rows)
    report={
        "purpose":"Five new source-frozen independently NASA-confirmed and ExoFOP-KP catalog-concordant transiting planet hosts: original SPOC raw-versus-pointing-subtracted centroids and fixed quarter-phase controls, NOT truth-localized ground sources or NASA ExoMiner classification benchmark",
        "original_frozen_precentroid_source_manifest_SHA256":hashlib.sha256(original).hexdigest(),
        "exact_five_catalogue_confirmed_host_stars_attempted":len(rows),
        "all_host_source_results":rows,
        "source_level_original_outcome_descriptive_statistics":stats,
        "original_NASA_ExoMiner_model_scores_or_weights_changed":False,
        "source_level_cautions":[
            "Original NASA Archive confirmed transiting planetary systems and ExoFOP known planet status corroborate existence but not individually independent high-resolution original ground source locality or absence of blended sources.",
            "A transit ON the target may move a flux-weighted centroid toward other non-eclipsing blended stars; a physically confirmed planet should not simply be assumed to produce exactly zero CCD centroid shift.",
            "The two quarter-period phase controls are fixed pseudo-event windows: real other planets, stellar variability or instrumental noise can occur there, so controls are not independent astrophysical null truth.",
            "Even a lower event centroid norm is not necessarily improved planet/false-positive discrimination; it might suppress real astrophysical shift.",
            "Only host TIC, not number of transit windows or repeated planetary periods, is independent inference unit.",
            "All five original source stars, first actual SPOC two-minute product sectors, original public TOI event times, original archive position mismatches, missing signals and processing errors are preserved.",
            "NASA 2026 pretrained ExoMiner++ model network scores, mission difference-image centroid products, PRF and weights are unmodified."
        ],
    }
    (out/"five_new_NASA_confirmed_on_target_source_original_TESS_raw_corrected_event_and_phase_control_results.json").write_text(
        json.dumps(report,indent=2,default=str)+"\n")
    plotted=[r for r in rows if r["source_processing_status"]=="processed" and
             r["actual_science"]["minimum_three_real_events_AND_three_each_fixed_phase_control_windows"]]
    if plotted:
        names=[f"TOI {r['TOI']}" for r in plotted]
        raw=[r["actual_science"]["actual_source_true_event"]["raw_median_event_centroid_norm_pixels"] for r in plotted]
        adj=[r["actual_science"]["actual_source_true_event"]["pointing_subtracted_median_event_centroid_norm_pixels"] for r in plotted]
        plotx=np.arange(len(plotted))
        fig,ax=plt.subplots(figsize=(9,5))
        ax.bar(plotx-.2,raw,.4,label="Original MOM_CENTR raw")
        ax.bar(plotx+.2,adj,.4,label="Experimental MOM_CENTR − POS_CORR")
        ax.set(xticks=plotx,xticklabels=names,
               ylabel="Median actual original in-transit centroid-vector norm, TESS pixels",
               title="Five previously centroid-unseen confirmed-planet hosts; original TESS event shift")
        ax.legend(frameon=False,fontsize=9)
        fig.text(.5,.02,"Confirmed planetary host is not independently sky-truth-labeled; no exoplanet classifier accuracy claim",
                 ha="center",fontsize=8)
        fig.tight_layout(rect=[0,.04,1,1])
        fig.savefig(out/"original_NASA_KP_five_host_event_centroid_norm_comparison.png",dpi=180)
        plt.close(fig)
    print("CONFIRMED_PLANET_CONTROL_SOURCE_RESULT",json.dumps({
        "original_star_units_attempted":len(rows),
        "processed":sum(r["source_processing_status"]=="processed" for r in rows),
        "eligible_three_true_and_each_control_events":stats["independent_eligible_confirmed_planet_host_TICs"],
        "star_level_summary":stats,
        "model_classifier_accuracy_verified":False
    }),flush=True)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-frozen-before-centroids",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--working",required=True)
    a=p.parse_args()
    run(a.source_frozen_before_centroids,a.out,a.working)
