"""Evaluate the PREVIOUSLY FROZEN centroid warning on 24 DIFFERENT TESS stars.

No source was used to design/adjust the .05px, 3-event, source bootstrap
gate. The 24 are new TO THIS PROJECT (not necessarily independent of NASA's
original v2.4.0 neural training), preselected with original 2025 labels and
MES but WITHOUT reading original 2025 or current NASA 2026 model scores.

This is exploratory external-to-development verification of a sidecar flag,
NOT a validated novel exoplanet classifier or new physical planet proof.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

from tess_exominer_cross_version_ephemeris_audit import (
    classify_period_ratio,verify_public_2025
)
from tess_official_event_recovery_companion import (
    find_matching_lc_fits,read_official_predictions
)
from tess_original_moment_centroid_companion import (
    verify_frozen_manifest,load_tess_centroid_columns,
    event_centroid_shifts,centroid_event_summary,fixed_centroid_manual_review_flag
)


def fixed_24_manifest(path,original_32_gate_protocol):
    meta=json.loads(Path(path).read_text())
    if meta.get("experiment_id")!="TESS_NEW_TO_STUDENT_24_STAR_FIXED_CENTROID_GATE_HOLDOUT_20261108":
        raise ValueError("Wrong before-centroid-data holdout")
    rec=meta["source_records"]
    if len(rec)!=24 or len({int(i["tic_id"]) for i in rec})!=24:
        raise ValueError("Must retain exactly 24 distinct unseen-to-this-project stars")
    for label in ("KP","CP","EB","NTP"):
        group=[x for x in rec if x["original_2025_historical_label"]==label]
        if len(group)!=6 or sum(x["MES_band"]=="7-20" for x in group)!=3 or sum(
                x["MES_band"]=="20-80" for x in group)!=3:
            raise ValueError("Original label-MES balance changed")
    rule=verify_frozen_manifest(original_32_gate_protocol)
    old={int(r["tic_id"]) for r in rule["source_records"]}
    hold={int(r["tic_id"]) for r in rec}
    if old & hold or 167526485 in hold:
        raise ValueError("Sample overlaps the 32 previous model-development stars or NASA tutorial")
    if meta.get("unchanged_rule_reference")!="TESS_32STAR_CENTROID_ALIAS_COMPANION_FROZEN_2026_11_08.json":
        raise ValueError("Centroid rule no longer points to original prior freeze")
    for r in rec:
        sec=r["sector_run"].split("-")
        if (len(sec)!=2 or sec[0]!=sec[1] or
            r["uid"]!=f"{r['tic_id']}-1-S{sec[0]}"):
            raise ValueError("Frozen original event number or sector mismatch")
    return meta,rule


def run(original_manifest,old_gate_manifest,official_2025,unchanged_nasa_2026,
        tess_fits_dir,outdir):
    spec,gate=fixed_24_manifest(original_manifest,old_gate_manifest)
    orig_hash=verify_public_2025(official_2025)
    origin=pd.read_csv(official_2025)
    if origin.uid.duplicated().any():
        raise ValueError("Original NASA 2025 public TCE UID is not unique")
    origin=origin.set_index("uid")
    nasa,_=read_official_predictions(unchanged_nasa_2026)
    if nasa.uid.duplicated().any():
        raise ValueError("Actual 2026 ExoMiner source UID duplicate")
    nasa=nasa.set_index("uid")
    settings=gate["fixed_experimental_flag_NOT_VALIDATED_FOR_SCIENCE"]
    geom=gate["event_definitions"]
    boot=gate["fixed_event_uncertainty"]
    dest=Path(outdir);dest.mkdir(parents=True,exist_ok=True)
    results=[]
    for source in spec["source_records"]:
        uid=source["uid"];tic=int(source["tic_id"])
        sector=int(source["sector_run"].split("-")[0])
        if uid not in origin.index:
            raise ValueError("A prespecified original 2025 TCE source is missing")
        o=origin.loc[uid]
        if (int(o.target_id)!=tic or
            str(o.label)!=source["original_2025_historical_label"]):
            raise ValueError("Original 2025 source label/TIC identity corrupted")
        row={
            "uid":uid,"TIC_ID":tic,"sector":sector,
            "published_2025_label":str(o.label),
            "source_original_2025_period_days":float(o.tce_period),
            "original_2026_model_has_exact_TCE_UID":uid in nasa.index,
            "original_2026_NASA_score_unchanged":None,
            "original_2026_NASA_disposition_unchanged":None,
            "original_2026_fitted_period_days":None,
            "source_ephemeris_identity":"not_scored",
            "source_FITS_sha256":None,
            "source_original_status":"not_scored",
            "corrected_centroid_source_event_count":None,
            "corrected_median_event_local_centroid_vector_pixels":None,
            "corrected_bootstrap_95pct_x_interval":None,
            "corrected_bootstrap_95pct_y_interval":None,
            "raw_centroid_source_event_count":None,
            "raw_median_event_local_centroid_vector_pixels":None,
            "original_total_quality_zero_cadences":None,
            "original_finite_poscorr_corrected_centroids":None,
            "frozen_fixed_centroid_manual_review_flag":None,
            "error_message":None
        }
        if uid not in nasa.index:
            results.append(row)
            continue
        n=nasa.loc[uid]
        period=float(n.tce_period)
        row.update({
            "original_2026_NASA_score_unchanged":float(n.score),
            "original_2026_NASA_disposition_unchanged":str(n.prediction),
            "original_2026_fitted_period_days":period,
            "source_ephemeris_identity":classify_period_ratio(period,float(o.tce_period)),
            "source_original_status":"NASA_scored_source_FITS_unavailable"
        })
        try:
            path=find_matching_lc_fits(tess_fits_dir,tic,sector)
            frame,sha=load_tess_centroid_columns(path,tic,sector)
            kw={"min_inside":geom["minimum_real_measurements_during"],
                "min_side":geom["minimum_real_measurements_each_pre_and_post"]}
            corrected=event_centroid_shifts(
                frame,period,float(n.tce_time0bk),float(n.tce_duration)/24.,
                mode="corrected",**kw)
            raw=event_centroid_shifts(
                frame,period,float(n.tce_time0bk),float(n.tce_duration)/24.,
                mode="raw",**kw)
            sc=centroid_event_summary(
                corrected,minimum_events=settings["min_individual_events"],
                bootstraps=boot["repetitions"],seed=boot["seed"])
            sr=centroid_event_summary(
                raw,minimum_events=settings["min_individual_events"],
                bootstraps=boot["repetitions"],seed=boot["seed"])
            warning=fixed_centroid_manual_review_flag(sc,settings)
            pd.DataFrame(corrected).to_csv(dest/f"{uid}_new_holdout_observed_corrected_event_centroids.csv",index=False)
            pd.DataFrame(raw).to_csv(dest/f"{uid}_new_holdout_observed_raw_event_centroids.csv",index=False)
            row.update({
                "source_FITS_sha256":sha["source_original_FITS_sha256"],
                "source_original_status":"NASA_original_FITS_centroid_measured",
                "corrected_centroid_source_event_count":sc["usable_original_source_events"],
                "corrected_median_event_local_centroid_vector_pixels":sc["median_vector_shift_pixels"],
                "corrected_bootstrap_95pct_x_interval":json.dumps(sc["median_signed_x_bootstrap_95pct"]),
                "corrected_bootstrap_95pct_y_interval":json.dumps(sc["median_signed_y_bootstrap_95pct"]),
                "raw_centroid_source_event_count":sr["usable_original_source_events"],
                "raw_median_event_local_centroid_vector_pixels":sr["median_vector_shift_pixels"],
                "original_total_quality_zero_cadences":sha["original_quality_zero_flux_rows"],
                "original_finite_poscorr_corrected_centroids":sha["original_finite_CORRECTED_two_dimensional_centroid_rows"],
                "frozen_fixed_centroid_manual_review_flag":warning
            })
        except Exception as ex:
            row["source_original_status"]="NASA_original_FITS_centroid_processing_failed"
            row["error_message"]=f"{type(ex).__name__}: {str(ex)[:300]}"
        results.append(row)
    if len(results)!=24:
        raise AssertionError("Loss of prespecified source hosts")
    frame=pd.DataFrame(results)
    frame.to_csv(dest/"all_24_UNSEEN_TO_OUR_CENTROID_RULE_source_TICs_with_NASA_original_scores.csv",index=False)
    primary=frame[frame.source_original_status=="NASA_original_FITS_centroid_measured"]
    eligible=primary[primary.frozen_fixed_centroid_manual_review_flag.notna()]
    review=eligible[eligible.frozen_fixed_centroid_manual_review_flag==True]
    labelstat={}
    for label in ("KP","CP","EB","NTP"):
        group=frame[frame.published_2025_label==label]
        labelstat[label]={
            "original_frozen_sources":len(group),
            "scored_by_original_NASA_2026":int(group.original_2026_model_has_exact_TCE_UID.sum()),
            "actual_original_centroid_sources":int((group.source_original_status=="NASA_original_FITS_centroid_measured").sum()),
            "event_count_sufficient_for_fixed_warning":int(group.frozen_fixed_centroid_manual_review_flag.notna().sum()),
            "manual_review_warning_count":int((group.frozen_fixed_centroid_manual_review_flag==True).sum())
        }
    nasa_pc=frame.original_2026_NASA_score_unchanged>=.5
    candidate_warn=nasa_pc&(frame.frozen_fixed_centroid_manual_review_flag==True)
    historical_positive=frame.published_2025_label.isin(["KP","CP"])
    summary={
        "experiment":spec["experiment_id"],
        "prior_to_new_centroid_measurement_source_manifest":original_manifest,
        "preexisting_rule_and_32star_development_sources":old_gate_manifest,
        "canonical_original_2025_Zenodo_MD5":orig_hash,
        "total_new_stars_to_student":24,
        "n_exact_original_NASA_pretrained_2026_TCEs_scored":int(frame.original_2026_model_has_exact_TCE_UID.sum()),
        "n_original_TESS_FITS_centroid_measured":len(primary),
        "n_at_least_3_corrected_centroid_events_evaluable":len(eligible),
        "n_fixed_review_warnings_on_all_historical_classes":len(review),
        "n_fixed_review_warnings_among_NASA_original_planet_score_ge_half":int(candidate_warn.sum()),
        "n_NASA_planet_candidate_review_warnings_on_historical_KP_CP_sources":int((candidate_warn&historical_positive).sum()),
        "n_NASA_planet_candidate_review_warnings_on_historical_EB_NTP_sources":int((candidate_warn&~historical_positive).sum()),
        "source_period_identity_counts":{str(k):int(v) for k,v in frame.source_ephemeris_identity.value_counts().items()},
        "by_published_2025_historical_class":labelstat,
        "limitations":[
            "This is held out from our earlier student development stars, not certified absent from NASA's original training stars.",
            "Sources were selected using public 2025 labels and multiple-event statistics, not a representative TESS survey sample.",
            "The original .05-pixel review flag remains fixed and is not calibrated by these results; do not select new thresholds after inspecting it.",
            "A manual-review warning is not a validated false-positive veto; all NASA original scores remain entirely unmodified.",
            "NASA already includes centroid and difference-image branches; no novel model improvement is claimed.",
            "Missing original astrometric fields and short-event series are counted explicitly; no zero-imputation or silent deletions.",
            "Retrospective KP/CP/EB/NTP class labels and matching period/UID do not guarantee independent physical planet validation."
        ]
    }
    (dest/"24star_heldout_centroid_rule_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(7.5,5))
    for label in ("KP","CP","EB","NTP"):
        group=primary[primary.published_2025_label==label]
        sub=group[group.corrected_median_event_local_centroid_vector_pixels.notna()]
        if len(sub):
            ax.scatter(sub.original_2026_NASA_score_unchanged,
                       sub.corrected_median_event_local_centroid_vector_pixels,
                       label=label,s=55,alpha=.8)
    ax.axhline(settings["median_2d_shift_at_least_pixels"],ls="--",color="black",lw=1)
    ax.axvline(.5,ls=":",color="gray",lw=1)
    ax.set(xlabel="Official original NASA ExoMiner++ v2.4.0 score",
           ylabel="New-to-student source local 2D centroid displacement (pixels)",
           title="Frozen centroid rule on 24 additional TESS stars, no retraining")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(dest/"centroid_24star_new_to_student_score_blind_source_plot.png",dpi=160)
    plt.close(fig)
    print(json.dumps({
        "n_new_to_student":24,
        "NASA_scores":summary["n_exact_original_NASA_pretrained_2026_TCEs_scored"],
        "original_centroid_sources":len(primary),
        "fixed_rule_evaluable":len(eligible),
        "original_rule_warning_count":len(review),
        "NASA_scores_ge_half_and_review":int(candidate_warn.sum()),
        "warned_original_KP_CP":int((candidate_warn&historical_positive).sum()),
        "warned_original_EB_NTP":int((candidate_warn&~historical_positive).sum()),
        "source_identity":summary["source_period_identity_counts"],
        "scope":"Precommitted to new-to-our-project stars only, not independently NASA-training-held-out; NO neural modification or confirmed new planets."
    },indent=2),flush=True)
    return summary


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--frozen",default="TESS_NEW_24STAR_CENTROID_RULE_HOLDOUT_FROZEN_2026_11_08.json")
    a.add_argument("--previous-gate",default="TESS_32STAR_CENTROID_ALIAS_COMPANION_FROZEN_2026_11_08.json")
    a.add_argument("--original-2025",required=True)
    a.add_argument("--official-nasa-2026",required=True)
    a.add_argument("--source-fits-root",required=True)
    a.add_argument("--out",default="results/tess24_new_to_student_centroid_rule")
    v=a.parse_args()
    run(v.frozen,v.previous_gate,v.original_2025,v.official_nasa_2026,v.source_fits_root,v.out)
