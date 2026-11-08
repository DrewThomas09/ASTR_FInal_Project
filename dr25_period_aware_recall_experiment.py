"""Frozen validation-only period-aware DR25 forest screening policy.

This is a development analysis after the original DR25 split had shown poor
long-period candidate recall. It does not change the RF model, features,
NASA labels, or scores. It changes only the validation-derived classification
cutoff per period bin. Better recall can worsen false-positive screening.

Use precommitted host-grouped seeds 14000-14009, report ALL split outcomes,
and avoid any claim of independent exoplanet confirmation or survey accuracy.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score

from ml_screening import load_data, split_by_star, cutoff, metrics, FEATURES
from dr25_paired_statistical_validation import (
    forest_model, verify_source, host_method_swap_permutation
)

PROTOCOL = "PERIOD_AWARE_DR25_VALIDATION_FROZEN_2026_11_08.json"
PERIOD_BINS=("short","medium","long","missing")


def load_protocol(path=PROTOCOL):
    p=json.loads(Path(path).read_text())
    if p["new_group_split_seeds"]!=list(range(14000,14010)):
        raise ValueError("Frozen group holdout seed list changed")
    if p["source"]["expected_labeled_rows"]!=8054:
        raise ValueError("Unexpected source population")
    if p["new_method"]["per_bin_goal_historical_candidate_recall_on_validation"]!=.9:
        raise ValueError("Frozen target changed")
    if p["new_method"]["minimum_positive_validation_examples_to_use_bin_threshold"]!=30:
        raise ValueError("Frozen fallback changed")
    bins=p["new_method"]["bins"]
    if [(b["name"],b["lower_inclusive"],b["upper_exclusive"]) for b in bins]!=[
        ("short",0,10),("medium",10,100),("long",100,None)]:
        raise ValueError("Frozen period bins changed")
    return p


def period_labels(periods):
    """Exactly one of three astrophysical period categories or 'missing'."""
    p=np.asarray(periods,dtype=float)
    if p.ndim!=1:
        raise ValueError("1D period array required")
    labels=np.full(p.shape,"missing",dtype=object)
    ok=np.isfinite(p)&(p>=0)
    labels[ok&(p<10)]="short"
    labels[ok&(p>=10)&(p<100)]="medium"
    labels[ok&(p>=100)]="long"
    return labels


def validation_only_thresholds(validation_scores,validation_labels,
                               validation_periods,protocol):
    """Never inspect any heldout label for threshold or fallback selection."""
    scores=np.asarray(validation_scores,dtype=float)
    y=np.asarray(validation_labels,dtype=np.int8)
    bins=period_labels(validation_periods)
    if scores.shape!=y.shape or y.shape!=bins.shape:
        raise ValueError("Validation scores, truth and orbital periods disagree")
    if not np.all(np.isfinite(scores)):
        raise ValueError("Nonfinite validation model scores")
    if not np.isin(y,[0,1]).all():
        raise ValueError("Invalid NASA historical binary labels")
    desired=float(protocol["new_method"]["per_bin_goal_historical_candidate_recall_on_validation"])
    min_positive=int(protocol["new_method"]["minimum_positive_validation_examples_to_use_bin_threshold"])
    global_cutoff=cutoff(scores,y,desired)
    selected={}
    for name in PERIOD_BINS:
        portion=bins==name
        positive_n=int(np.sum(y[portion]==1))
        sample_n=int(portion.sum())
        if name!="missing" and positive_n>=min_positive:
            cut=float(cutoff(scores[portion],y[portion],desired))
            fallback=False
        else:
            cut=float(global_cutoff)
            fallback=True
        selected[name]={
            "validation_signals":sample_n,
            "validation_historical_candidate_labels":positive_n,
            "cutoff":cut,
            "used_fallback_global_cutoff":fallback
        }
    return {"global_validation_cutoff":float(global_cutoff),
            "period_bin_cutoffs":selected,
            "validation_target_historical_candidate_recall":desired}


def binary_decisions(test_scores, test_periods, threshold):
    """Flux source periods, not labels, route test rows into validation cutoffs."""
    scores=np.asarray(test_scores,dtype=float)
    bins=period_labels(test_periods)
    if scores.shape!=bins.shape or not np.all(np.isfinite(scores)):
        raise ValueError("Score/period shape mismatch or nonfinite scores")
    global_pred=scores>=threshold["global_validation_cutoff"]
    per=np.zeros(len(scores),dtype=bool)
    for name in PERIOD_BINS:
        chosen=bins==name
        per[chosen]=scores[chosen]>=threshold["period_bin_cutoffs"][name]["cutoff"]
    return global_pred,per,bins


def measure_classification(y,pred):
    y=np.asarray(y,dtype=int)
    pred=np.asarray(pred,dtype=bool)
    if not len(y) or len(y)!=len(pred):
        return {"n":int(len(y)),"balanced_accuracy":None,
                "candidate_recall":None,"false_positive_rate":None,
                "overall_accuracy":None,"n_candidate_labels":int(np.sum(y==1)),
                "n_false_positive_labels":int(np.sum(y==0))}
    pos=(y==1);neg=(y==0)
    rec=float(pred[pos].mean()) if pos.any() else None
    fpr=float(pred[neg].mean()) if neg.any() else None
    ba=float((rec + (1-fpr))/2) if rec is not None and fpr is not None else None
    return {"n":int(len(y)),"n_candidate_labels":int(pos.sum()),
            "n_false_positive_labels":int(neg.sum()),
            "balanced_accuracy":ba,
            "candidate_recall":rec,
            "false_positive_rate":fpr,
            "overall_accuracy":float(np.mean(pred==y)),
            "false_candidate_dismissals":int(np.sum(pos&~pred)),
            "false_positive_labels_flagged_as_candidate":int(np.sum(neg&pred))}


def evaluate_split(df,seed,protocol,write_predictions=False):
    train,validation,test=split_by_star(df,seed=seed)
    labels=df.label.to_numpy(dtype=int)
    x=np.log1p(df[list(FEATURES)].clip(lower=0).astype(float))
    stars=df.kepid.to_numpy()
    for a,b in [(train,validation),(train,test),(validation,test)]:
        if set(stars[a])&set(stars[b]):
            raise AssertionError("Same host in train/test, test/valid, or train/valid")
    model=forest_model(seed)
    model.fit(x.iloc[train],labels[train])
    val=model.predict_proba(x.iloc[validation])[:,1]
    scores=model.predict_proba(x.iloc[test])[:,1]
    thresholds=validation_only_thresholds(
        val,labels[validation],df.iloc[validation].koi_period,protocol)
    glob,period,bins=binary_decisions(
        scores,df.iloc[test].koi_period,thresholds)
    y=labels[test]
    evaluated={}
    for name,where in [("overall",np.ones(len(test),dtype=bool)),
                       ("short",bins=="short"),("medium",bins=="medium"),
                       ("long",bins=="long"),("missing",bins=="missing")]:
        g=measure_classification(y[where],glob[where])
        a=measure_classification(y[where],period[where])
        evaluated[name]={"original_global_forest":g,
                         "validation_period_bin_forest":a,
                         "balanced_accuracy_difference":(
                             a["balanced_accuracy"]-g["balanced_accuracy"]
                             if a["balanced_accuracy"] is not None and
                             g["balanced_accuracy"] is not None else None),
                         "candidate_recall_difference":(
                             a["candidate_recall"]-g["candidate_recall"]
                             if a["candidate_recall"] is not None and
                             g["candidate_recall"] is not None else None),
                         "false_positive_rate_difference":(
                             a["false_positive_rate"]-g["false_positive_rate"]
                             if a["false_positive_rate"] is not None and
                             g["false_positive_rate"] is not None else None)}
    row={"seed":int(seed),"n_train":len(train),
         "n_valid":len(validation),"n_test":len(test),
         "n_test_hosts":int(len(set(stars[test]))),
         "validation_selected_cutoffs":thresholds,
         "holdout_comparisons":evaluated}
    if not write_predictions:
        return row,None
    table=df.iloc[test][["kepid","kepoi_name","koi_period",
                         "koi_duration","koi_depth","koi_model_snr"]].copy()
    table["historical_nasa_candidate_label"]=y
    table["score_same_random_forest"]=scores
    table["period_bin"]=bins
    table["prediction_global"]=glob.astype(np.int8)
    table["prediction_period_aware"]=period.astype(np.int8)
    # These threshold values are derived from validation labels ONLY.
    table["global_validation_cutoff"]=thresholds["global_validation_cutoff"]
    table["period_bin_validation_cutoff"]=[
        thresholds["period_bin_cutoffs"][b]["cutoff"] for b in bins]
    return row,table.reset_index(drop=True)


def cluster_bootstrap_tradeoff(test,reps=2000,seed=2026110804):
    """Conditional paired bootstrap of BA, candidate recall and false alarm.

    Group whole source stars. No heldout threshold selection; the already-
    frozen predictions are resampled in matched host blocks.
    """
    data=test.copy()
    y=data["historical_nasa_candidate_label"].to_numpy(dtype=np.int8)
    old=data["prediction_global"].to_numpy(dtype=bool)
    new=data["prediction_period_aware"].to_numpy(dtype=bool)
    stars,inverse=np.unique(data.kepid,return_inverse=True)
    n=len(stars)
    p=y==1;neg=~p
    counts_pos=np.bincount(inverse,weights=p,minlength=n)
    counts_neg=np.bincount(inverse,weights=neg,minlength=n)
    dif_tp=np.bincount(inverse,weights=p*(new.astype(int)-old.astype(int)),minlength=n)
    dif_fp=np.bincount(inverse,weights=neg*(new.astype(int)-old.astype(int)),minlength=n)
    rng=np.random.default_rng(seed)
    deltas={"balanced_accuracy":[], "candidate_recall":[],
            "false_positive_rate":[]}
    for _ in range(reps):
        w=np.bincount(rng.integers(0,n,n),minlength=n)
        a=float(w@counts_pos);b=float(w@counts_neg)
        if a<1 or b<1:
            continue
        recall_d=float(w@dif_tp/a)
        fpr_d=float(w@dif_fp/b)
        deltas["candidate_recall"].append(recall_d)
        deltas["false_positive_rate"].append(fpr_d)
        deltas["balanced_accuracy"].append(.5*(recall_d-fpr_d))
    out={}
    for name,arr in deltas.items():
        if len(arr)<reps*.95:
            raise ValueError("Too many bootstrap draws without both label groups")
        out[name]={"CI95":[float(v) for v in np.quantile(arr,[.025,.975])],
                   "median":float(np.median(arr)),"draws":len(arr)}
    return {"n_independent_hosts":n,"bootstrap_reps":reps,
            "seed":seed,"difference_new_minus_global":out,
            "caveat":"Conditional star-block bootstrap on historical labels; not an independent physical planet completeness estimate."}


def run(csv,output="results/period_aware_dr25",protocol_path=PROTOCOL):
    protocol=load_protocol(protocol_path)
    expected=protocol["source"]["expected_sha256"]
    status=verify_source(csv,{"source":{"expected_original_csv_sha256":expected}})
    df=load_data(csv,False)
    if len(df)!=protocol["source"]["expected_labeled_rows"]:
        raise ValueError("Changed DR25 cohort labels")
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    (output/"frozen_protocol.json").write_bytes(Path(protocol_path).read_bytes())
    seeds=protocol["new_group_split_seeds"]
    trials=[]
    primary=None
    for i,seed in enumerate(seeds):
        print(f"New grouped-by-star period policy: split {i+1}/{len(seeds)}, seed={seed}",flush=True)
        result,raw=evaluate_split(df,seed,protocol,write_predictions=(i==0))
        trials.append(result)
        if raw is not None:primary=raw
    if primary is None:raise RuntimeError("First predeclared split not saved")
    primary.to_csv(output/"first_new_split_paired_predictions.csv",index=False)
    wide=[]
    for r in trials:
        row={"seed":r["seed"],"test_n":r["n_test"],
             "test_hosts":r["n_test_hosts"]}
        for name,metrics in r["holdout_comparisons"].items():
            for measure in ["balanced_accuracy_difference",
                            "candidate_recall_difference",
                            "false_positive_rate_difference"]:
                row[f"{name}_{measure}"]=metrics[measure]
            for method in ["original_global_forest",
                           "validation_period_bin_forest"]:
                for meas in ("n_candidate_labels",
                             "n_false_positive_labels",
                             "balanced_accuracy","candidate_recall",
                             "false_positive_rate"):
                    row[f"{name}_{method}_{meas}"]=metrics[method].get(meas)
        wide.append(row)
    pd.DataFrame(wide).to_csv(output/"ten_new_host_split_tradeoffs.csv",index=False)
    selected=primary[primary.period_bin=="long"].copy()
    if len(selected)<60 or selected.historical_nasa_candidate_label.nunique()!=2:
        raise ValueError("Insufficient frozen long-period holdout for meaningful primary contrast")
    # The generic inference method accepts arbitrary prediction column names.
    perm=host_method_swap_permutation(
        selected,permutations=protocol["stats"]["two_sided_host_method_swap_permutations"],
        seed=protocol["stats"]["permutation_seed"],
        method="period_aware",baseline="global")
    interval=cluster_bootstrap_tradeoff(
        selected,reps=protocol["stats"]["paired_star_bootstrap_repetitions"],
        seed=protocol["stats"]["bootstrap_seed"])
    all_interval=cluster_bootstrap_tradeoff(
        primary,reps=protocol["stats"]["paired_star_bootstrap_repetitions"],
        seed=protocol["stats"]["bootstrap_seed"]+1)
    allmetrics=trials[0]["holdout_comparisons"]
    aggregate={}
    for group in ("long","overall"):
        key=f"{group}_balanced_accuracy_difference"
        differences=[r[key] for r in wide if r[key] is not None]
        aggregate[group]={
            "balanced_accuracy_new_minus_old_median":float(np.median(differences)),
            "minimum":float(min(differences)),"maximum":float(max(differences)),
            "n_positive":int(sum(z>0 for z in differences)),
            "n_negative":int(sum(z<0 for z in differences)),
            "n_zero":int(sum(z==0 for z in differences)),
            "warning":"Group split holdouts overlap; not independent binomial trials."}
    report={
        "analysis":"NASA historical KOI label screening: period-bin threshold versus original global forest decision threshold",
        "underlying_classifier_scores_identical":True,
        "source":status,"source_rows":len(df),
        "selected_primary_seed":seeds[0],
        "primary_per_bin_metrics":allmetrics,
        "primary_paired_host_permutation_long_period_BA":perm,
        "primary_star_cluster_bootstrap_long_period":interval,
        "primary_star_cluster_bootstrap_overall":all_interval,
        "ten_split_sensitivity":aggregate,
        "each_split":trials,
        "limits":[
            "Period-aware policy was designed after observing long-period failures in an earlier star split; this is exploratory iterative development, not untouched confirmatory proof.",
            "Both strategies are identical random-forest predicted SCORES with distinct validation-derived operating thresholds. ROC AUC is exactly the same and cannot improve.",
            "A recall increase necessarily comes with a possibility of more false-positive candidate classifications. Balanced accuracy is the prespecified long-period summary endpoint.",
            "NASA prior Robovetter decisions are not physically verified planet truth; no new planet or survey completeness result.",
            "Repeated 10 star splits overlap and must not have their p-values pooled.",
            "A low host-level p value compares decisions conditional on scores; it does not establish causal model or astrophysical superiority."
        ]}
    (output/"period_policy_statistical_results.json").write_text(json.dumps(report,indent=2)+"\n")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    methods=("original_global_forest","validation_period_bin_forest")
    labels=("Global threshold","Period-bin threshold")
    for ax,stat,title in [
        (axes[0],"candidate_recall","Historical candidate-label recall"),
        (axes[1],"false_positive_rate","Historical false-positive labels accepted")]:
        parts=[allmetrics["long"][m][stat] for m in methods]
        ax.bar(labels,parts)
        ax.set(ylim=(0,1),ylabel=title,
               title="Long-period KOIs (>=100 d)")
        for i,v in enumerate(parts):
            ax.text(i,v+.015,f"{100*v:.1f}%",ha="center")
        ax.tick_params(axis="x",rotation=12)
    fig.suptitle("Same four-feature random forest; validation-only thresholds")
    fig.tight_layout()
    fig.savefig(output/"long_period_recall_false_alarm_tradeoff.png",dpi=170)
    plt.close(fig)
    print(json.dumps({
        "first_seed":seeds[0],
        "long_period_metrics":allmetrics["long"],
        "all_period_metrics":allmetrics["overall"],
        "long_period_host_swap_p":perm["two_sided_host_method_swap_permutation_p"],
        "long_period_cluster_CI":interval["difference_new_minus_global"]["balanced_accuracy"],
        "across_splits":aggregate
    },indent=2),flush=True)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--csv",default="data/kepler_dr25.csv")
    p.add_argument("--out",default="results/period_aware_dr25")
    p.add_argument("--protocol",default=PROTOCOL)
    a=p.parse_args()
    run(a.csv,a.out,a.protocol)
