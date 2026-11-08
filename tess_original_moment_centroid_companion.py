"""TESS SPOC *event-local centroid* physics check beside REAL NASA ExoMiner.

This module never trains, recalibrates, replaces, or changes the official NASA
ExoMiner++ v2.4.0 neural model. Its inputs are original TESS 2-minute SPOC
light-curve FITS MOM_CENTR1/2 and POS_CORR1/2 fields, plus the NASA pipeline's
original TCE period/epoch/duration and score.

New experimental check: is the star's measured centroid temporarily different
during an event compared with locally adjacent pre/post observations?
A local shift by itself cannot verify the source of an eclipse or planet.
NASA already uses pixel/centroid diagnostics; NO novelty or improvement claim
can follow from reconstructing this baseline.

All 32 host stars came from two prior inspected source cohorts, not a fresh
independent 2026 model holdout. The .05 pixel warning threshold and minimum
event counts were frozen before running this new centroid code on them.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from tess_official_event_recovery_companion import (
    read_official_predictions,find_matching_lc_fits
)
from tess_exominer_cross_version_ephemeris_audit import (
    classify_period_ratio,verify_public_2025
)

SOURCE_EXPERIMENT_ID="TESS_FIXED_32_STAR_LOCAL_CENTROID_AND_ALIAS_COMPANION_20261108"


def verify_frozen_manifest(path):
    spec=json.loads(Path(path).read_text())
    if spec.get("experiment_id")!=SOURCE_EXPERIMENT_ID:
        raise ValueError("Wrong frozen centroid evaluation version")
    entries=spec["source_records"]
    if len(entries)!=32 or len({int(s["tic_id"]) for s in entries})!=32:
        raise ValueError("Frozen cohort must contain exactly 32 unique TIC hosts")
    if {x["source_cohort"] for x in entries}!={
        "prior_16star_class_balanced","prior_16star_old_score_error_enriched"}:
        raise ValueError("Source cohort labels changed")
    for source in entries:
        tic=int(source["tic_id"])
        a,b=source["sector_run"].split("-")
        if a!=b or source["uid"]!=f"{tic}-1-S{a}":
            raise ValueError("TIC/source UID ephemeris mismatched")
    return spec


def load_tess_centroid_columns(path,tic,sector):
    """Read REAL original FITS, with missing POS_CORR never replaced by zeros.

    The reference original SPOC light curve uses MOM_CENTR1/2 as flux-weighted
    CCD centroid; POS_CORR1/2 are common-mode pointing corrections in pixels.
    Subtracting POS_CORR is a *proposed companion diagnostic*, not identical
    to the official NASA difference-image centroid algorithm.
    """
    from astropy.io import fits
    file=Path(path)
    digest=hashlib.sha256()
    with file.open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""):
            digest.update(block)
    with fits.open(file,memmap=False) as hdus:
        hdr=hdus[0].header
        if int(hdr.get("TICID",-1))!=int(tic):
            raise ValueError("Original MAST light curve target TIC differs")
        if int(hdr.get("SECTOR",-1))!=int(sector):
            raise ValueError("Original MAST light curve sector differs")
        data=hdus[1].data
        cols=set(data.names)
        required={"TIME","PDCSAP_FLUX","QUALITY",
                  "MOM_CENTR1","MOM_CENTR2"}
        if not required.issubset(cols):
            raise ValueError("Original SPOC FITS lacks mandatory moment centroid columns: "+str(sorted(required-cols)))
        t=np.asarray(data["TIME"],dtype=float)
        flux=np.asarray(data["PDCSAP_FLUX"],dtype=float)
        quality=np.asarray(data["QUALITY"],dtype=np.int64)
        x=np.asarray(data["MOM_CENTR1"],dtype=float)
        y=np.asarray(data["MOM_CENTR2"],dtype=float)
        if {"POS_CORR1","POS_CORR2"}.issubset(cols):
            posx=np.asarray(data["POS_CORR1"],dtype=float)
            posy=np.asarray(data["POS_CORR2"],dtype=float)
            has_poscorr=True
        else:
            posx=np.full_like(x,np.nan)
            posy=np.full_like(y,np.nan)
            has_poscorr=False
    primary_mask=np.isfinite(t)&np.isfinite(flux)&(flux>0)&(quality==0)
    if int(primary_mask.sum())<500:
        raise ValueError("Too few original quality-zero photometric measurements")
    table=pd.DataFrame({
        "time_BTJD":t[primary_mask],
        "relative_PDCSAP_flux":flux[primary_mask]/
            float(np.median(flux[primary_mask])),
        "raw_moment_CCD_x_pixels":x[primary_mask],
        "raw_moment_CCD_y_pixels":y[primary_mask],
        "pointing_correction_x_pixels":posx[primary_mask],
        "pointing_correction_y_pixels":posy[primary_mask]
    })
    table["corrected_moment_x_pixels"]=(
        table["raw_moment_CCD_x_pixels"]-table["pointing_correction_x_pixels"])
    table["corrected_moment_y_pixels"]=(
        table["raw_moment_CCD_y_pixels"]-table["pointing_correction_y_pixels"])
    if not np.all(np.diff(table.time_BTJD.to_numpy())>0):
        raise ValueError("Original TESS time series is not strictly increasing")
    raw=np.isfinite(table[["raw_moment_CCD_x_pixels","raw_moment_CCD_y_pixels"]]).all(axis=1)
    corrected=np.isfinite(table[["corrected_moment_x_pixels","corrected_moment_y_pixels"]]).all(axis=1)
    metadata={
        "source_FITS_filename":file.name,
        "source_original_FITS_sha256":digest.hexdigest(),
        "original_total_FITS_rows":len(t),
        "original_quality_zero_flux_rows":len(table),
        "original_finite_RAW_two_dimensional_centroid_rows":int(raw.sum()),
        "original_finite_CORRECTED_two_dimensional_centroid_rows":int(corrected.sum()),
        "original_POS_CORR_columns_present":bool(has_poscorr),
        "instrument_position_units":"CCD detector pixels; approximate TESS plate scale 21 arcsec/pixel",
        "centroid_kind":"Original SPOC flux-weighted MOM_CENTR1/2, with experimental common-motion subtraction from POS_CORR1/2",
        "method_warning":"This MOM_CENTR - POS_CORR time-local metric is not identical to the image-difference/centroid model inputs used by ExoMiner."
    }
    return table,metadata


def event_centroid_shifts(frame,period,epoch,duration_days,mode="corrected",
                          min_inside=3,min_side=6):
    """Paired in-event versus locally flanking source centroid displacement.

    Median in-window minus average of medians in pre/post windows on same
    original CCD time series. Cannot invent missing cadences, phase-fold data,
    or fill NaN corrected centroids from a default 0 pointing correction.
    """
    if not all(np.isfinite(z) for z in (period,epoch,duration_days)):
        raise ValueError("Period, epoch and duration must be finite")
    if period<=0 or duration_days<=0 or duration_days>=.3*period:
        raise ValueError("Invalid transiting event window geometry")
    if mode not in ("raw","corrected"):
        raise ValueError("Centroid mode is raw or corrected")
    inn=1.5*duration_days
    out=min(3.5*duration_days,.44*period)
    if out<=inn:
        raise ValueError("No flanking event windows")
    for key in ["time_BTJD","relative_PDCSAP_flux"]:
        if key not in frame:
            raise ValueError("Missing physical time or flux field")
    xcol=("corrected_moment_x_pixels" if mode=="corrected" else "raw_moment_CCD_x_pixels")
    ycol=("corrected_moment_y_pixels" if mode=="corrected" else "raw_moment_CCD_y_pixels")
    if not {xcol,ycol}.issubset(frame.columns):
        raise ValueError("Original SPOC centroid fields unavailable")
    t=frame["time_BTJD"].to_numpy(dtype=float)
    x=frame[xcol].to_numpy(dtype=float)
    y=frame[ycol].to_numpy(dtype=float)
    flux=frame["relative_PDCSAP_flux"].to_numpy(dtype=float)
    if len(t)<20 or not np.all(np.diff(t)>0):
        raise ValueError("Original SPOC source timestamps must increase")
    finite=np.isfinite(x)&np.isfinite(y)&np.isfinite(flux)&np.isfinite(t)
    start=int(np.ceil((t[0]+out-epoch)/period))
    end=int(np.floor((t[-1]-out-epoch)/period))
    result=[]
    for k in range(start,end+1):
        c=float(epoch+k*period)
        dt=t-c
        ingress=(dt>=-out)&(dt<=-inn)&finite
        egress=(dt>=inn)&(dt<=out)&finite
        active=(np.abs(dt)<=.5*duration_days)&finite
        nc=int(active.sum());nb=int(ingress.sum());na=int(egress.sum())
        if nc<min_inside or nb<min_side or na<min_side:
            continue
        pre=np.array([np.median(x[ingress]),np.median(y[ingress])])
        after=np.array([np.median(x[egress]),np.median(y[egress])])
        inside=np.array([np.median(x[active]),np.median(y[active])])
        baseline=(pre+after)/2.0
        delta=inside-baseline
        norm=float(np.hypot(*delta))
        local_before_after=float(np.hypot(*(after-pre)))
        noise=np.concatenate([
            np.column_stack((x[ingress],y[ingress])),
            np.column_stack((x[egress],y[egress]))
        ])
        # Component robust scatter NOT the uncertainty of a transit centroid.
        scatter=np.median(np.abs(noise-np.median(noise,axis=0)),axis=0)*1.4826
        result.append({
            "orbit_index":int(k),
            "parity":"odd" if k%2 else "even",
            "predicted_NASA_TCE_center_BTJD":c,
            "event_model_period_days":float(period),
            "event_model_duration_days":float(duration_days),
            "n_cadences_pre":nb,
            "n_cadences_inside":nc,
            "n_cadences_post":na,
            "pre_CCD_x":float(pre[0]),"pre_CCD_y":float(pre[1]),
            "inside_CCD_x":float(inside[0]),"inside_CCD_y":float(inside[1]),
            "post_CCD_x":float(after[0]),"post_CCD_y":float(after[1]),
            "local_in_minus_flanking_x_pixels":float(delta[0]),
            "local_in_minus_flanking_y_pixels":float(delta[1]),
            "local_in_minus_flanking_vector_norm_pixels":norm,
            "local_pre_post_vector_norm_pixels":local_before_after,
            "local_centroid_MAD_x_pixels":float(scatter[0]),
            "local_centroid_MAD_y_pixels":float(scatter[1]),
            "local_relative_flux_depth":
                float((np.median(flux[ingress])+np.median(flux[egress]))/2-
                      np.median(flux[active]))
        })
    return result


def centroid_event_summary(events,minimum_events=3,bootstraps=500,seed=2026110811):
    if len(events)==0:
        return {
            "usable_original_source_events":0,
            "median_signed_x_pixels":None,"median_signed_y_pixels":None,
            "median_vector_shift_pixels":None,
            "median_magnitude_of_individual_event_shifts_pixels":None,
            "median_signed_x_bootstrap_95pct":None,
            "median_signed_y_bootstrap_95pct":None,
            "one_axis_descriptive_interval_excludes_zero":None,
            "scope":"Inconclusive, no qualifying original observed event windows"
        }
    x=np.array([e["local_in_minus_flanking_x_pixels"] for e in events],dtype=float)
    y=np.array([e["local_in_minus_flanking_y_pixels"] for e in events],dtype=float)
    mx=float(np.median(x));my=float(np.median(y))
    outcome={
        "usable_original_source_events":len(events),
        "median_signed_x_pixels":mx,
        "median_signed_y_pixels":my,
        "median_vector_shift_pixels":float(np.hypot(mx,my)),
        "median_magnitude_of_individual_event_shifts_pixels":
            float(np.median(np.hypot(x,y))),
        "median_signed_x_bootstrap_95pct":None,
        "median_signed_y_bootstrap_95pct":None,
        "one_axis_descriptive_interval_excludes_zero":None,
        "scope":"Descriptive event-centered original SPOC MOM_CENTR - POS_CORR sidecar; not independent transit-host localization or model improvement"
    }
    if len(events)>=minimum_events:
        rng=np.random.default_rng(seed)
        draws=rng.integers(0,len(events),size=(bootstraps,len(events)))
        medx=np.median(x[draws],axis=1)
        medy=np.median(y[draws],axis=1)
        lowx,highx=(float(v) for v in np.quantile(medx,[.025,.975]))
        lowy,highy=(float(v) for v in np.quantile(medy,[.025,.975]))
        outcome.update({
            "median_signed_x_bootstrap_95pct":[lowx,highx],
            "median_signed_y_bootstrap_95pct":[lowy,highy],
            "one_axis_descriptive_interval_excludes_zero":bool(
                (lowx>0 or highx<0) or (lowy>0 or highy<0)),
            "interval_warning":"Bootstrap event units are drawn within one star; interval is descriptive, not a calibrated pixel-level/mission source-localization test."
        })
    return outcome


def fixed_centroid_manual_review_flag(summary,settings):
    if (summary["usable_original_source_events"]<
            settings["min_individual_events"] or
        summary["one_axis_descriptive_interval_excludes_zero"] is None):
        return None
    return bool(
        summary["median_vector_shift_pixels"]>=settings["median_2d_shift_at_least_pixels"]
        and summary["one_axis_descriptive_interval_excludes_zero"]
    )


def run(cohort,original_2025_csv,official_predicted_2026_csv,nasa_fits_directory,out_dir):
    config=verify_frozen_manifest(cohort)
    original_md5=verify_public_2025(original_2025_csv)
    old=pd.read_csv(original_2025_csv)
    if old.uid.duplicated().any():
        raise ValueError("Original NASA 2025 source has repeated TCE UIDs")
    old=old.set_index("uid",drop=False)
    nasa,header=read_official_predictions(official_predicted_2026_csv)
    if nasa.uid.duplicated().any():
        raise ValueError("Original NASA 2026 model output has duplicated UIDs")
    nasa=nasa.set_index("uid",drop=False)
    settings=config["fixed_experimental_flag_NOT_VALIDATED_FOR_SCIENCE"]
    e=config["event_definitions"]
    nrep=config["fixed_event_uncertainty"]["repetitions"]
    seed=config["fixed_event_uncertainty"]["seed"]
    folder=Path(out_dir);folder.mkdir(parents=True,exist_ok=True)
    outcomes=[]
    for r in config["source_records"]:
        uid=r["uid"];tic=int(r["tic_id"]);sec=int(r["sector_run"].split("-")[0])
        if uid not in old:
            raise ValueError("Missing original frozen public 2025 TCE UID")
        oldrow=old.loc[uid]
        if int(oldrow.target_id)!=tic or str(oldrow.label)!=str(r["published_2025_label"]):
            raise ValueError("Original 2025 label/identity inconsistent with original frozen cohort")
        row={
            "source_cohort":r["source_cohort"],"uid":uid,
            "TIC_ID":tic,"sector":sec,
            "original_2025_historical_label":str(oldrow.label),
            "original_2025_score":float(oldrow.score),
            "original_2025_period_days":float(oldrow.tce_period),
            "NASA_2026_exact_UID_scored":uid in nasa.index,
            "NASA_2026_original_score_unmodified":None,
            "NASA_2026_original_prediction_unmodified":None,
            "NASA_2026_period_days":None,
            "fitted_period_identity_category":"no_exact_UID",
            "source_FITS_sha256":None,
            "source_status":"nasa_source_not_found",
            "original_quality_zero_flux_cadences":None,
            "corrected_centroid_finite_cadences":None,
            "raw_centroid_finite_cadences":None,
            "corrected_usable_event_count":None,
            "corrected_median_vector_shift_pixels":None,
            "corrected_median_local_event_depth_fraction":None,
            "corrected_descriptive_interval_nonzero":None,
            "raw_usable_event_count":None,
            "raw_median_vector_shift_pixels":None,
            "experimental_centroid_manual_review_flag":None,
            "original_source_error":None
        }
        if uid not in nasa.index:
            outcomes.append(row)
            continue
        n=nasa.loc[uid]
        newperiod=float(n.tce_period)
        row.update({
            "NASA_2026_original_score_unmodified":float(n.score),
            "NASA_2026_original_prediction_unmodified":str(n.prediction),
            "NASA_2026_period_days":newperiod,
            "fitted_period_identity_category":
                classify_period_ratio(newperiod,float(oldrow.tce_period)),
            "source_status":"nasa_scored_original_FITS_not_yet_loaded"
        })
        try:
            fits=find_matching_lc_fits(nasa_fits_directory,tic,sec)
            frame,provenance=load_tess_centroid_columns(fits,tic,sec)
            corrected_events=event_centroid_shifts(
                frame,newperiod,float(n.tce_time0bk),float(n.tce_duration)/24.,
                mode="corrected",min_inside=e["minimum_real_measurements_during"],
                min_side=e["minimum_real_measurements_each_pre_and_post"])
            raw_events=event_centroid_shifts(
                frame,newperiod,float(n.tce_time0bk),float(n.tce_duration)/24.,
                mode="raw",min_inside=e["minimum_real_measurements_during"],
                min_side=e["minimum_real_measurements_each_pre_and_post"])
            corr=centroid_event_summary(
                corrected_events,minimum_events=settings["min_individual_events"],
                bootstraps=nrep,seed=seed)
            raw=centroid_event_summary(
                raw_events,minimum_events=settings["min_individual_events"],
                bootstraps=nrep,seed=seed)
            check=fixed_centroid_manual_review_flag(corr,settings)
            pd.DataFrame(corrected_events).to_csv(
                folder/f"{uid}_observed_corrected_original_TESS_centroid_events.csv",index=False)
            pd.DataFrame(raw_events).to_csv(
                folder/f"{uid}_observed_RAW_original_TESS_centroid_events.csv",index=False)
            row.update({
                "source_status":"original_SPOC_FITS_centroid_measured",
                "source_FITS_sha256":provenance["source_original_FITS_sha256"],
                "source_FITS_name":provenance["source_FITS_filename"],
                "original_quality_zero_flux_cadences":provenance["original_quality_zero_flux_rows"],
                "corrected_centroid_finite_cadences":provenance["original_finite_CORRECTED_two_dimensional_centroid_rows"],
                "raw_centroid_finite_cadences":provenance["original_finite_RAW_two_dimensional_centroid_rows"],
                "corrected_usable_event_count":corr["usable_original_source_events"],
                "corrected_median_vector_shift_pixels":corr["median_vector_shift_pixels"],
                "corrected_median_shift_x_pixels":corr["median_signed_x_pixels"],
                "corrected_median_shift_y_pixels":corr["median_signed_y_pixels"],
                "corrected_x_interval_95pct":json.dumps(corr["median_signed_x_bootstrap_95pct"]),
                "corrected_y_interval_95pct":json.dumps(corr["median_signed_y_bootstrap_95pct"]),
                "corrected_descriptive_interval_nonzero":corr["one_axis_descriptive_interval_excludes_zero"],
                "raw_usable_event_count":raw["usable_original_source_events"],
                "raw_median_vector_shift_pixels":raw["median_vector_shift_pixels"],
                "experimental_centroid_manual_review_flag":check,
                "corrected_median_local_event_depth_fraction":(
                    float(np.median([a["local_relative_flux_depth"] for a in corrected_events]))
                    if corrected_events else None)
            })
        except Exception as exc:
            row["source_status"]="original_centroid_source_or_analysis_failed"
            row["original_source_error"]=f"{type(exc).__name__}: {str(exc)[:350]}"
        outcomes.append(row)
    if len(outcomes)!=32:
        raise AssertionError("Frozen denominator violated")
    out=pd.DataFrame(outcomes)
    out.to_csv(folder/"all_32_original_TESS_stars_unchanged_NASA_scores_and_centroid_windows.csv",index=False)
    measured=out[out.source_status=="original_SPOC_FITS_centroid_measured"]
    eligible=measured.loc[measured.experimental_centroid_manual_review_flag.notna()]
    flagged=eligible[eligible.experimental_centroid_manual_review_flag==True]
    unflagged=eligible[eligible.experimental_centroid_manual_review_flag==False]
    categories={}
    for label in sorted(out.original_2025_historical_label.unique()):
        rows=out[out.original_2025_historical_label==label]
        categories[label]={
            "n_original_requested":len(rows),
            "n_source_measured":int((rows.source_status=="original_SPOC_FITS_centroid_measured").sum()),
            "n_centroid_flag_evaluable":int(rows.experimental_centroid_manual_review_flag.notna().sum()),
            "n_flagged_FOR_MANUAL_REVIEW_only":int((rows.experimental_centroid_manual_review_flag==True).sum())
        }
    # Descriptive hypothetical conservative veto, NOT implemented in NASA:
    # candidates scoring >=.5 with a flagged displacement get a separate
    # manual-review label. Never silently override their official predictions.
    official_pc=(out.NASA_2026_original_score_unmodified>=.5)
    hypothetical_review=official_pc&(out.experimental_centroid_manual_review_flag==True)
    original_planet_like=out.original_2025_historical_label.isin(["KP","CP"])
    summary={
        "protocol":config["experiment_id"],
        "historical_source_original_2025_MD5":original_md5,
        "total_frozen_source_stars":32,
        "n_original_2026_model_scores_matched":int(out.NASA_2026_exact_UID_scored.sum()),
        "n_source_FITS_with_primary_plus_raw_centroid_measured":len(measured),
        "n_source_moments_flag_evaluable_min3_independent_events":len(eligible),
        "n_source_flagged_manual_review":len(flagged),
        "n_source_not_flagged_manual_review":len(unflagged),
        "n_source_insufficient_centroid_events_or_missing_fields":int(len(out)-len(eligible)),
        "n_2026_NASA_original_planet_candidate_signals_flagged_for_additional_review":int(hypothetical_review.sum()),
        "among_these_review_flags_historical_2025_positive_KP_CP":int((hypothetical_review&original_planet_like).sum()),
        "among_these_review_flags_historical_2025_negative_other":int((hypothetical_review&~original_planet_like).sum()),
        "by_2025_historical_label":categories,
        "period_identity_categories_all32":{str(k):int(v) for k,v in out.fitted_period_identity_category.value_counts().items()},
        "scientific_interpretation":[
            "This is a descriptive, reused previously scrutinized source cohort. It cannot establish a novel or statistically significant improvement in NASA's ExoMiner++ network.",
            "The .05px and three-event fixed gate is a suggested manual-review flag, not a calibrated false alarm or a hard veto and its output is never fed into the NASA model.",
            "NASA already uses centroid and difference-image diagnostics; moment-centroid + POS_CORR is not an original replacement, simply a separately interpretable source check.",
            "A centroid difference can also result from data issues or binary/multiple source geometries; even a coherent shift is not ground-truth source attribution.",
            "The original 2026 trained network may have seen these historical 2025 TCE stars; source labels from 2025 may evolve and some TCE UIDs have ephemeris aliases across versions.",
            "Use same-source time and FITS digest provenance, model version and all thirty-two initial IDs; no post-hoc missing example deletion."
        ]
    }
    (folder/"original_32source_centroid_companion_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,5))
    for label in sorted(out.original_2025_historical_label.unique()):
        group=measured[measured.original_2025_historical_label==label]
        group=group[group.corrected_median_vector_shift_pixels.notna()]
        if len(group):
            ax.scatter(group.NASA_2026_original_score_unmodified,
                       group.corrected_median_vector_shift_pixels,
                       label=label,alpha=.83,s=50)
    ax.axhline(settings["median_2d_shift_at_least_pixels"],ls="--",lw=1,color="black",label="Uncalibrated fixed manual-review shift gate")
    ax.axvline(.5,ls=":",lw=1,color="gray",label="NASA score 0.5")
    ax.set(xlabel="Unmodified official NASA v2.4.0 ExoMiner++ score",
           ylabel="Local moment-centroid shift (CCD pixels)",
           title="Real TESS source centroid shifts beside unchanged NASA scores")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(folder/"real_TESS_32star_local_centroid_shift_vs_original_NASA_score.png",dpi=170)
    plt.close(fig)
    print(json.dumps({
        "total_original_stars":32,
        "official_NASA_2026_scores_matched":summary["n_original_2026_model_scores_matched"],
        "source_FITS_centroid_measured":len(measured),
        "centroid_flag_evaluable":len(eligible),
        "fixed_centroid_warning_count":len(flagged),
        "NASA_planet_scored_and_manual_review_warning":int(hypothetical_review.sum()),
        "historical_label_positive_inside_NASA_PC_and_review_warning":int((hypothetical_review&original_planet_like).sum()),
        "historical_label_negative_inside_NASA_PC_and_review_warning":int((hypothetical_review&~original_planet_like).sum()),
        "ephemeris_identities":summary["period_identity_categories_all32"],
        "caveat":"Previously inspected reuse; manual-review gate, not a better NASA neural classifier or independent planet detection"
    },indent=2),flush=True)
    return summary


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--frozen",default="TESS_32STAR_CENTROID_ALIAS_COMPANION_FROZEN_2026_11_08.json")
    p.add_argument("--original-2025",required=True)
    p.add_argument("--official-nasa-2026",required=True)
    p.add_argument("--source-fits-root",required=True)
    p.add_argument("--out",default="results/tess32_original_centroid_diagnostics")
    a=p.parse_args()
    run(a.frozen,a.original_2025,a.official_nasa_2026,a.source_fits_root,a.out)
