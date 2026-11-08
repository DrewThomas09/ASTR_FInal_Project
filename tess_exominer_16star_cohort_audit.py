"""Source-preserving 16-star official NASA TESS model cohort audit.

The cohort was frozen from published 2025 *labels and signal metadata only*
before checking NASA 2026 scores on these stars. The 2026 model may have been
trained on some or all source observations: THIS IS NOT AN INDEPENDENT HOLDOUT.
We report every requested star, including sources not retrievable from MAST.

This script does not train, alter, recalibrate or improve ExoMiner++.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

from tess_official_event_recovery_companion import (
    read_official_predictions, find_matching_lc_fits, load_original_tess_fits
)
from kepler_event_shape_diagnostics import event_shape_measurements, summarize_shape_events


EXPECTED_LABELS=("KP","CP","EB","NTP")


def source_manifest(path):
    meta=json.loads(Path(path).read_text())
    if meta.get("experiment_id")!="EXOMINER_16_HOST_SCORE_BLIND_FEASIBILITY_20261108":
        raise ValueError("Wrong frozen 16-star cohort")
    data=meta["source_records"]
    if len(data)!=16 or len({int(row["tic_id"]) for row in data})!=16:
        raise ValueError("Cohort must contain exactly sixteen different stars")
    if set(row["published_2025_label"] for row in data)!=set(EXPECTED_LABELS):
        raise ValueError("Historical class strata changed")
    for label in EXPECTED_LABELS:
        sub=[row for row in data if row["published_2025_label"]==label]
        if len(sub)!=4 or sum(r["MES_band"]=="7-20" for r in sub)!=2 or sum(
                r["MES_band"]=="20-80" for r in sub)!=2:
            raise ValueError("Wrong frozen class/signal-strength strata")
    for record in data:
        tic=int(record["tic_id"])
        start,end=record["sector_run"].split("-")
        if not (start==end and 3<=int(start)<=12):
            raise ValueError("Only original single-sector 3..12 TESS sources")
        if record["uid"]!=f"{tic}-1-S{int(start)}":
            raise ValueError("Incorrect frozen canonical UID")
    return meta


def analyze_sources(manifest_path,predictions_csv,source_root,out_dir):
    manifest=source_manifest(manifest_path)
    nasa,header=read_official_predictions(predictions_csv)
    if nasa.uid.duplicated().any():
        raise ValueError("NASA returned multiple predictions with an identical TCE UID")
    idx=nasa.set_index("uid")
    output=Path(out_dir);output.mkdir(parents=True,exist_ok=True)
    observations=[]
    matched=0
    companion_ok=0
    for row in manifest["source_records"]:
        ident=row["uid"]
        tic=int(row["tic_id"])
        sector=int(row["sector_run"].split("-")[0])
        rec={
            "uid":ident,"TIC_ID":tic,"sector":sector,
            "published_2025_label":row["published_2025_label"],
            "published_2025_fold":row["published_2025_fold"],
            "MES_band_preselected":row["MES_band"],
            "source_2025_published_period_days":row["period_days_from_published_catalog"],
            "NASA_2026_exact_UID_found":False,
            "NASA_2026_official_planet_score":None,
            "NASA_2026_official_prediction":None,
            "official_pretrained_source_status":"not_scored_exact_original_TCE_UID",
            "same_TESS_FITS_sidecar_status":"not_attempted",
            "observed_original_FITS_sha256":None,
            "sidecar_usable_observed_event_count":None,
            "sidecar_median_original_local_depth_fraction":None,
            "sidecar_median_post_pre_step_over_depth_plus_noise":None,
            "sidecar_odd_even_median_depth_difference_fraction":None,
            "sidecar_odd_even_event_bootstrap_95pct":None,
            "error_message":None
        }
        if ident not in idx.index:
            observations.append(rec)
            continue
        match=idx.loc[ident]
        matched+=1
        rec.update({
            "NASA_2026_exact_UID_found":True,
            "NASA_2026_official_planet_score":float(match["score"]),
            "NASA_2026_official_prediction":str(match["prediction"]),
            "NASA_2026_official_TCE_period_days":float(match["tce_period"]),
            "NASA_2026_official_TCE_duration_hours":float(match["tce_duration"]),
            "official_pretrained_source_status":"successfully_scored",
            "same_TESS_FITS_sidecar_status":"attempting"
        })
        try:
            fitsfile=find_matching_lc_fits(source_root,tic,sector)
            time,flux,src=load_original_tess_fits(fitsfile,tic,sector)
            duration=float(match["tce_duration"])/24
            events=event_shape_measurements(
                time,flux,float(match["tce_period"]),
                float(match["tce_time0bk"]),duration)
            diagnostics=summarize_shape_events(events)
            # Existence of input FITS and no valid sideband events is NOT
            # converted into a fabricated depth=0 observation.
            pd.DataFrame(events).to_csv(output/f"{ident}_individual_source_events.csv",index=False)
            rec.update({
                "same_TESS_FITS_sidecar_status":"observations_evaluated",
                "observed_original_FITS_sha256":src["original_FITS_sha256"],
                "quality_zero_original_cadences":src["original_quality_zero_cadences"],
                "sidecar_usable_observed_event_count":diagnostics["usable_event_count"],
                "sidecar_median_original_local_depth_fraction":
                    diagnostics["median_signed_local_depth_fraction"],
                "sidecar_median_post_pre_step_over_depth_plus_noise":
                    diagnostics["median_persistent_step_over_depth_plus_noise"],
                "sidecar_odd_even_median_depth_difference_fraction":
                    diagnostics["median_odd_even_depth_difference_fraction"],
                "sidecar_odd_even_event_bootstrap_95pct":
                    diagnostics["odd_even_descriptive_bootstrap_95pct_interval"]
            })
            companion_ok+=1
        except Exception as ex:
            rec["same_TESS_FITS_sidecar_status"]="source_or_analysis_error"
            rec["error_message"]=f"{type(ex).__name__}: {str(ex)[:300]}"
        observations.append(rec)
    if len(observations)!=16:
        raise AssertionError("Could not account for all prespecified source stars")
    records=pd.DataFrame(observations)
    records.to_csv(output/"all_16_frozen_stars_including_failed_sources.csv",index=False)
    official=nasa[["uid","target_id","sector_run","score","prediction",
                   "tce_period","tce_duration","tce_time0bk"]].copy()
    official.to_csv(output/"original_NASA_all_scored_TCEs_no_model_perturbation.csv",index=False)
    groups={}
    for label in EXPECTED_LABELS:
        chunk=records[records.published_2025_label==label]
        valid=chunk[chunk.NASA_2026_exact_UID_found]
        groups[label]={
            "n_requested_stars":len(chunk),
            "n_exact_uid_scored":len(valid),
            "n_tess_original_sidecar_analyzed":int(
                (chunk.same_TESS_FITS_sidecar_status=="observations_evaluated").sum()),
            "n_score_at_least_0_5":int((valid.NASA_2026_official_planet_score>=.5).sum()),
            "original_pretrained_score_mean_on_scored":(
                float(valid.NASA_2026_official_planet_score.mean()) if len(valid) else None),
            "warning":"2025 historically labeled source selection, not independent 2026 training-excluded truth"
        }
    # Descriptive confusion ONLY for exact matched TCE UIDs. No CI at n<=16.
    where=records.NASA_2026_exact_UID_found
    matched_df=records.loc[where].copy()
    positive=matched_df.published_2025_label.isin(("KP","CP"))
    predicted=(matched_df.NASA_2026_official_planet_score>=.5)
    counts={
        "TP_2025_KP_or_CP_with_2026_score_ge_0_5":int((positive&predicted).sum()),
        "FN_2025_KP_or_CP_with_2026_score_lt_0_5":int((positive&~predicted).sum()),
        "FP_2025_EB_or_NTP_with_2026_score_ge_0_5":int((~positive&predicted).sum()),
        "TN_2025_EB_or_NTP_with_2026_score_lt_0_5":int((~positive&~predicted).sum()),
    }
    report={
        "source_manifest":manifest["experiment_id"],
        "original_2025_label_catalog_DOI":"10.5281/zenodo.15466293",
        "NASA_model_task":"planet-validation",
        "NASA_original_model_unmodified":True,
        "NASA_original_model_header":header.splitlines()[:15],
        "n_prespecified_unique_TIC_stars":16,
        "n_NASA_original_scores_all_TCEs_from_these_TICs":len(nasa),
        "n_exact_requested_2025_TCE_UIDs_scored_by_2026_NASA":matched,
        "n_exact_requested_2025_TCE_UIDs_missing":16-matched,
        "n_orig_MAST_TESS_FITS_sidecar_analyzed":companion_ok,
        "per_original_2025_label":groups,
        "descriptive_2025_label_vs_2026_output_at_0_5":counts,
        "statistics":"Not an independent model holdout, no p-value or inferential 95% CI; source sample is only 16 preselected original 2025 labeled stars",
        "crucial_limitations":[
            "This is a source feasibility and descriptive model-behavior study, not a credible population reliability test.",
            "2026 NASA pretrained model may have seen these 2025 sources or close analogs during training; only a documented exclusion establishes an independent model holdout.",
            "Historical KP/CP/EB/NTP labels and NASA 2026 PC decision do not have identical definitions or a consistent prospectively calibrated false-alarm denominator.",
            "All requested stars are retained in the accounting even if NASA SPOC source data or the companion diagnostic is unavailable.",
            "Do not report a specific system as a confirmed planet based only on model confidence or recovery to baseline.",
            "No new model was fitted, pretrained NASA score recalibrated, or NASA architecture modified during this comparison."
        ]
    }
    (output/"complete_16star_descriptive_study.json").write_text(json.dumps(report,indent=2)+"\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,5))
    for label in EXPECTED_LABELS:
        scores=records.loc[
            (records.published_2025_label==label)&(records.NASA_2026_exact_UID_found),
            "NASA_2026_official_planet_score"].to_numpy(dtype=float)
        if len(scores):
            ax.scatter([label]*len(scores),scores,s=45,label=label,alpha=.82)
    ax.axhline(.5,color="black",ls="--",lw=1,label="NASA reference cutoff 0.5")
    ax.set(title="Real NASA v2.4.0 pretrained scores on the 16 original source TCEs",
           ylabel="Original unmodified model planet-validation score",ylim=(-.025,1.025))
    ax.legend(loc="best",fontsize=8)
    fig.tight_layout()
    fig.savefig(output/"original_NASA_scores_by_previously_published_TESS_label.png",dpi=150)
    plt.close(fig)
    print(json.dumps({
        "cohort":report["source_manifest"],
        "requested":16,
        "matched_exact_uid":matched,
        "same_original_FITS_sidecar_analyzed":companion_ok,
        "by_2025_historical_label":groups,
        "historical_descriptive_confusion":counts,
        "warning":"No new exoplanet, no unmodified CNN gain and no untouched evaluation holdout."
    },indent=2),flush=True)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--cohort",default="TESS_16STAR_OFFICIAL_EXOMINER_COHORT_FROZEN_2026_11_08.json")
    p.add_argument("--predictions",required=True)
    p.add_argument("--nasa-output-root",required=True)
    p.add_argument("--out",default="results/tess_official_16star_descriptive_audit")
    a=p.parse_args()
    analyze_sources(a.cohort,a.predictions,a.nasa_output_root,a.out)
