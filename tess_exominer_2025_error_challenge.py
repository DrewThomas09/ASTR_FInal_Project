"""Historical ExoMiner++ 2025 error-case stress test with actual 2026 NASA neural scores.

This sample was deliberately ENRICHED for cases the 2025 model misclassified.
It is not unbiased performance, and the 2026 model may have trained on them.
Models and TCE IDs must be matched exactly; missing cases never disappear.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from tess_official_event_recovery_companion import (
    read_official_predictions,find_matching_lc_fits,load_original_tess_fits
)
from kepler_event_shape_diagnostics import event_shape_measurements,summarize_shape_events


def load_manifest(path):
    x=json.loads(Path(path).read_text())
    if x.get("experiment_id")!="EXOMINER_2025_MISTAKES_VS_2026_PRETRAINED_CHALLENGE_20261108":
        raise ValueError("Unexpected historical-error challenge experiment")
    r=x["source_records"]
    if len(r)!=16 or len({int(q["tic_id"]) for q in r})!=16 or len({q["uid"] for q in r})!=16:
        raise ValueError("Challenge must contain 16 unique original TESS stars/event UIDs")
    for tag in ("2025_missed_historical_planet","2025_accepted_historical_nonplanet"):
        if sum(q["published_2025_error_kind"]==tag for q in r)!=8:
            raise ValueError("Challenge wrong number of each 2025 mistake type")
    for q in r:
        sector=q["sector_run"].split("-")
        if (len(sector)!=2 or sector[0]!=sector[1] or
            q["uid"]!=f"{q['tic_id']}-1-S{sector[0]}"):
            raise ValueError("Incorrect frozen NASA source sector UID")
    return x


def source_2025_rows(original_csv,manifest):
    digest=hashlib.md5()
    size=0
    with Path(original_csv).open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):
            size+=len(b);digest.update(b)
    if size!=8944735 or digest.hexdigest()!=manifest["source_exact_MD5"]:
        raise ValueError("Not the exact released NASA 2025 catalog")
    original=pd.read_csv(original_csv)
    if original.uid.duplicated().any():
        raise ValueError("Duplicate original 2025 TCE UID")
    by_uid=original.set_index("uid")
    for q in manifest["source_records"]:
        if q["uid"] not in by_uid.index:
            raise ValueError("Frozen 2025 source UID missing from original source")
        reference=by_uid.loc[q["uid"]]
        if int(reference["target_id"])!=int(q["tic_id"]) or reference["label"]!=q["published_2025_label"]:
            raise ValueError("Original NASA label/source differs from prespecified cohort")
        positive=reference["label"] in ("KP","CP")
        score=float(reference["score"])
        historical_kind="2025_missed_historical_planet" if positive and score<.5 else (
            "2025_accepted_historical_nonplanet" if not positive and score>=.5 else "not_a_historical_error")
        if q["published_2025_error_kind"]!=historical_kind:
            raise ValueError("Frozen historical error class is not actually an original mistake")
    return by_uid


def evaluate(frozen,source_2025,predictions_2026,source_root,out):
    spec=load_manifest(frozen)
    old=source_2025_rows(source_2025,spec)
    new,header=read_official_predictions(predictions_2026)
    if new.uid.duplicated().any():
        raise ValueError("2026 pretrained model returned repeated exact UIDs")
    new=new.set_index("uid")
    output=Path(out);output.mkdir(parents=True,exist_ok=True)
    rows=[]
    for s in spec["source_records"]:
        uid=s["uid"]
        o=old.loc[uid]
        tic=int(s["tic_id"]);sector=int(s["sector_run"].split("-")[0])
        positive=o["label"] in ("KP","CP")
        oldscore=float(o["score"])
        row={
            "uid":uid,"tic_id":tic,"sector":sector,
            "original_2025_historical_label":s["published_2025_label"],
            "preselected_2025_error_kind":s["published_2025_error_kind"],
            "original_2025_out_of_fold_score":oldscore,
            "original_2025_wrong_decision_against_2025_label":True,
            "NASA_2026_same_exact_UID_scored":uid in new.index,
            "NASA_2026_original_score_unmodified":None,
            "NASA_2026_original_model_label":None,
            "2026_agrees_with_2025_label":None,
            "2025_error_resolved_on_historical_label_by_2026":None,
            "same_TESS_original_FITS_sidecar_status":"not_attempted",
            "same_TESS_original_FITS_sha256":None,
            "original_TESS_observed_event_windows":None,
            "original_TESS_median_event_depth":None,
            "original_TESS_median_post_pre_step_ratio":None,
            "error":None
        }
        if uid not in new.index:
            rows.append(row)
            continue
        c=new.loc[uid]
        updated=float(c["score"])
        correct=(updated>=.5)==positive
        row.update({
            "NASA_2026_original_score_unmodified":updated,
            "NASA_2026_original_model_label":str(c["prediction"]),
            "2026_agrees_with_2025_label":bool(correct),
            "2025_error_resolved_on_historical_label_by_2026":bool(correct),
            "same_TESS_original_FITS_sidecar_status":"attempted"
        })
        try:
            loc=find_matching_lc_fits(source_root,tic,sector)
            t,f,src=load_original_tess_fits(loc,tic,sector)
            events=event_shape_measurements(t,f,float(c["tce_period"]),
                                            float(c["tce_time0bk"]),
                                            float(c["tce_duration"])/24)
            shape=summarize_shape_events(events)
            pd.DataFrame(events).to_csv(output/f"{uid}_observed_original_TESS_events.csv",index=False)
            row.update({
                "same_TESS_original_FITS_sidecar_status":"analyzed",
                "same_TESS_original_FITS_sha256":src["original_FITS_sha256"],
                "original_TESS_observed_event_windows":shape["usable_event_count"],
                "original_TESS_median_event_depth":shape["median_signed_local_depth_fraction"],
                "original_TESS_median_post_pre_step_ratio":shape["median_persistent_step_over_depth_plus_noise"]
            })
        except Exception as exc:
            row.update({
                "same_TESS_original_FITS_sidecar_status":"failed",
                "error":f"{type(exc).__name__}: {str(exc)[:250]}"
            })
        rows.append(row)
    df=pd.DataFrame(rows)
    df.to_csv(output/"all_16_prespecified_2025_model_errors_and_actual_2026_outcomes.csv",index=False)
    grouped={}
    for kind in ("2025_missed_historical_planet","2025_accepted_historical_nonplanet"):
        sub=df[df.preselected_2025_error_kind==kind]
        good=sub[sub.NASA_2026_same_exact_UID_scored]
        grouped[kind]={
            "original_requested":len(sub),
            "exact_UID_scored_2026":len(good),
            "still_not_resolved":int((good["2025_error_resolved_on_historical_label_by_2026"]==False).sum()),
            "resolved_against_original_2025_label":int((good["2025_error_resolved_on_historical_label_by_2026"]==True).sum()),
            "not_scored":len(sub)-len(good),
            "original_FITS_sidecars":int((sub["same_TESS_original_FITS_sidecar_status"]=="analyzed").sum())
        }
    full={
        "experiment_id":spec["experiment_id"],
        "selection":"Source stars intentionally selected due to 2025 published-model mistakes; no 2026 output used in selecting original cohort.",
        "original_label_reference":"Published TESS SPOC 2-minute S1-S67 2025 ExoMiner++ catalog DOI 10.5281/zenodo.15466293, official MD5 verified",
        "actual_2026_model_inference":"Authentic official NASA v2.4.0 single planet-validation pretrained model, not edited",
        "n_preselected_historical_2025_source_errors":16,
        "n_exact_2025_UIDs_scored_by_NASA_2026":int(df.NASA_2026_same_exact_UID_scored.sum()),
        "n_additional_DV_TCEs_in_2026_model_output_not_preselected":len(new)-int(df.NASA_2026_same_exact_UID_scored.sum()),
        "n_same_original_TESS_FITS_analyzed":int((df.same_TESS_original_FITS_sidecar_status=="analyzed").sum()),
        "by_2025_model_error_type":grouped,
        "n_original_2025_historical_mistakes_resolved_in_2026":int(
            (df["2025_error_resolved_on_historical_label_by_2026"]==True).sum()),
        "n_original_2025_historical_mistakes_persist_in_2026":int(
            (df["2025_error_resolved_on_historical_label_by_2026"]==False).sum()),
        "n_original_2025_error_sources_unscored":int((~df.NASA_2026_same_exact_UID_scored).sum()),
        "caveats":[
            "Purposefully enriched with prior 2025 model errors. Not an unbiased accuracy, reliability or detection-performance estimate.",
            "2026 model training source exclusions are unknown: resolved historical errors do not prove new-star generalization.",
            "2025 published labels might include class taxonomy differences or subsequent astrophysical updates; score-based resolution is not independent planet confirmation.",
            "Full 2025 and 2026 CNN model versions differ; the cause of changed decisions is unknown without controlled ablations.",
            "Missing source UIDs are included in 16-case denominator; do not silently discard hard-case failures.",
            "This original-TESS morphology sidecar does not change or improve NASA's neural scores."
        ]
    }
    (output/"historical_error_challenge_complete_summary.json").write_text(json.dumps(full,indent=2)+"\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    mask=df.NASA_2026_same_exact_UID_scored
    plot=df.loc[mask]
    fig,ax=plt.subplots(figsize=(7,6))
    for kind,label in (("2025_missed_historical_planet","Historical planet 2025 missed"),
                       ("2025_accepted_historical_nonplanet","Historical nonplanet 2025 accepted")):
        p=plot[plot.preselected_2025_error_kind==kind]
        if len(p):
            ax.scatter(p.original_2025_out_of_fold_score,
                       p.NASA_2026_original_score_unmodified,
                       s=60,alpha=.85,label=label)
    ax.axhline(.5,ls="--",color="black",lw=1)
    ax.axvline(.5,ls="--",color="black",lw=1)
    ax.plot([0,1],[0,1],ls=":",color="grey",lw=1)
    ax.set(xlim=(-.025,1.025),ylim=(-.025,1.025),
           xlabel="Official ExoMiner++ 2025 released CV planet score",
           ylabel="Official ExoMiner v2.4.0 2026 actual pretrained score",
           title="Prior 2025 misclassifications: paired 2025 vs 2026 original scores")
    ax.legend(fontsize=8,loc="best")
    fig.tight_layout()
    fig.savefig(output/"paired_original_2025_error_cases_vs_2026_NASA_model.png",dpi=150)
    plt.close(fig)
    print(json.dumps({
        "n_source":16,
        "matched":full["n_exact_2025_UIDs_scored_by_NASA_2026"],
        "same_original_source_measured":full["n_same_original_TESS_FITS_analyzed"],
        "resolved":full["n_original_2025_historical_mistakes_resolved_in_2026"],
        "persisted":full["n_original_2025_historical_mistakes_persist_in_2026"],
        "unscored":full["n_original_2025_error_sources_unscored"],
        "group":grouped,
        "warning":"Retrospective old-model-error stress test, NOT unbiased or training-excluded planet discovery."
    },indent=2),flush=True)
    return full


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",default="TESS_16STAR_2025_ERRORS_VS_2026_FROZEN_2026_11_08.json")
    p.add_argument("--historical-catalog",required=True)
    p.add_argument("--nasa-predictions",required=True)
    p.add_argument("--nasa-source-root",required=True)
    p.add_argument("--out",default="results/tess_original_hardcase_challenge")
    a=p.parse_args()
    evaluate(a.manifest,a.historical_catalog,a.nasa_predictions,a.nasa_source_root,a.out)
