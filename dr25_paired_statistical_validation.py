"""Host-aware paired statistical validation of NASA historical Kepler DR25 labels.

This is a REANALYSIS of already-explored DR25 KOIs and a previously explored
initial star split. A low p-value can show reproducible label-agreement
differences versus simple baselines; it does NOT show a new exoplanet, actual
planet classification accuracy, or a truly untouched confirmatory experiment.

The primary split/metric, validation thresholds, extra splits, and tests
were frozen in DR25_STATISTICAL_VALIDATION_FROZEN_2026_11_08.json before this
additional training run. AI-assisted code: verify independently.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

from ml_screening import (
    load_data, split_by_star, cutoff, metrics, FEATURES
)

PROTOCOL = "DR25_STATISTICAL_VALIDATION_FROZEN_2026_11_08.json"


def read_frozen_protocol(path=PROTOCOL):
    p = json.loads(Path(path).read_text())
    if p["heldout"]["primary_split_seed"] != 12600:
        raise ValueError("Primary star split changed")
    if p["heldout"]["additional_split_seeds"] != list(range(12601, 12610)):
        raise ValueError("Additional star split list changed")
    if p["decision"]["validation_recall_target"] != .9:
        raise ValueError("Validation candidate recall target changed")
    if p["statistical_tests"]["primary_permutations"] != 20000:
        raise ValueError("Primary permutation count changed")
    if p["statistical_tests"]["paired_host_bootstrap_reps"] != 2000:
        raise ValueError("Cluster bootstrap size changed")
    if list(p["features"]) != list(FEATURES):
        raise ValueError("Source feature list changed")
    return p


def verify_source(path, cfg):
    data = Path(path).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    expected = cfg["source"]["expected_original_csv_sha256"]
    if digest != expected:
        raise ValueError(
            f"The raw NASA DR25 CSV does not match the original frozen source. "
            f"Expected SHA256 {expected}; received {digest}. "
            "Do NOT silently substitute changed data."
        )
    return {"sha256": digest, "bytes": len(data), "path": str(path)}


def forest_model(seed):
    return make_pipeline(SimpleImputer(strategy="median"),
                         RandomForestClassifier(
                             n_estimators=120, max_depth=9, min_samples_leaf=3,
                             random_state=int(seed), n_jobs=-1))


def logistic_model(seed):
    return make_pipeline(SimpleImputer(strategy="median"),
                         StandardScaler(),
                         LogisticRegression(
                             max_iter=2000, solver="lbfgs", C=1.0,
                             class_weight=None, random_state=int(seed)))


def evaluate_one_split(df, seed, cfg, save_primary=False):
    train, valid, test = split_by_star(df, seed=int(seed))
    labels = df.label.to_numpy(dtype=np.int64)
    groups = df.kepid.to_numpy()
    features = np.log1p(df[list(FEATURES)].clip(lower=0).astype(float))
    train_stars = set(groups[train])
    valid_stars = set(groups[valid])
    test_stars = set(groups[test])
    if any((train_stars & valid_stars, train_stars & test_stars,
            valid_stars & test_stars)):
        raise AssertionError("Train/validation/test host-star contamination")
    median_snr = float(np.nanmedian(features.iloc[train].koi_model_snr))
    if not np.isfinite(median_snr):
        raise ValueError("Training SNR median absent")
    forest = forest_model(seed)
    logistic = logistic_model(seed)
    forest.fit(features.iloc[train], labels[train])
    logistic.fit(features.iloc[train], labels[train])

    def snr_scores(rows):
        return features.iloc[rows].koi_model_snr.fillna(median_snr).to_numpy(dtype=float)

    val_score = {
        "SNR_only":snr_scores(valid),
        "random_forest":forest.predict_proba(features.iloc[valid])[:, 1],
        "logistic_4feature":logistic.predict_proba(features.iloc[valid])[:, 1]}
    test_score = {
        "SNR_only":snr_scores(test),
        "random_forest":forest.predict_proba(features.iloc[test])[:, 1],
        "logistic_4feature":logistic.predict_proba(features.iloc[test])[:, 1]}
    decision = {}
    for name in val_score:
        threshold = cutoff(val_score[name], labels[valid],
                           cfg["decision"]["validation_recall_target"])
        predictions = test_score[name] >= threshold
        val_pred = val_score[name] >= threshold
        m = metrics(labels[test], predictions)
        m.update({
            "balanced_accuracy":float(balanced_accuracy_score(labels[test], predictions)),
            "roc_auc":float(roc_auc_score(labels[test], test_score[name])),
            "validation_candidate_recall":float(np.mean(val_pred[labels[valid] == 1])),
            "threshold_from_validation_only":float(threshold)
        })
        decision[name] = {"metrics": m, "pred":predictions,
                          "scores":test_score[name]}
    details = {
        "seed":int(seed), "train_n":len(train), "validation_n":len(valid),
        "test_n":len(test), "train_hosts":len(train_stars),
        "validation_hosts":len(valid_stars), "test_hosts":len(test_stars),
        "test_candidates":int(labels[test].sum()),
        "test_false_positives":int((labels[test] == 0).sum()),
        "models":{name:value["metrics"] for name,value in decision.items()},
        "difference_random_forest_minus_snr_balanced_accuracy":float(
            decision["random_forest"]["metrics"]["balanced_accuracy"] -
            decision["SNR_only"]["metrics"]["balanced_accuracy"]),
        "difference_random_forest_minus_logistic_balanced_accuracy":float(
            decision["random_forest"]["metrics"]["balanced_accuracy"] -
            decision["logistic_4feature"]["metrics"]["balanced_accuracy"]),
        "difference_random_forest_minus_snr_roc_auc":float(
            decision["random_forest"]["metrics"]["roc_auc"] -
            decision["SNR_only"]["metrics"]["roc_auc"])
    }
    if not save_primary:
        return details, None
    hold = df.iloc[test][["kepid", "kepoi_name", "koi_period",
                          "koi_duration", "koi_depth", "koi_model_snr"]].copy()
    hold["historical_nasa_candidate_label"] = labels[test]
    for name,item in decision.items():
        hold[f"score_{name}"] = item["scores"]
        hold[f"validation_threshold_{name}"] = item["metrics"]["threshold_from_validation_only"]
        hold[f"prediction_{name}"] = item["pred"].astype(np.int8)
    return details, hold.reset_index(drop=True)


def cluster_aggregates(test, method="random_forest", baseline="SNR_only"):
    y = test["historical_nasa_candidate_label"].to_numpy(dtype=np.int8)
    a = test[f"prediction_{method}"].to_numpy(dtype=bool)
    b = test[f"prediction_{baseline}"].to_numpy(dtype=bool)
    stars, inverse = np.unique(test.kepid.to_numpy(), return_inverse=True)
    pos = (y == 1)
    neg = ~pos
    if pos.sum()==0 or neg.sum()==0:
        raise ValueError("Both historical NASA label classes required")
    d = a.astype(int) == y
    e = b.astype(int) == y
    # Positive and negative classes carry equal total weight for BA.
    row_weight = np.where(pos, .5/pos.sum(), .5/neg.sum())
    per_host_ba_delta = np.bincount(inverse,
                          weights=row_weight*(d.astype(float)-e.astype(float)),
                          minlength=len(stars))
    return stars, inverse, per_host_ba_delta


def host_method_swap_permutation(test, permutations=20000, seed=2026110801,
                                 method="random_forest", baseline="SNR_only"):
    """Cluster-level pair swap: one sign for all signals of each host star.

    Balanced accuracy weights each historical label class equally. Under the
    null that the two methods are exchangeable as paired host blocks, flip
    signs of each full host contribution. This is a conditional permutation
    test, not a new-data causal or astrophysical claim.
    """
    stars, inverse, contribution = cluster_aggregates(
        test, method, baseline)
    observed = float(contribution.sum())
    rng = np.random.default_rng(seed)
    exceed = 0
    remaining = int(permutations)
    while remaining > 0:
        batch = min(384, remaining)
        swap = rng.integers(0, 2, size=(batch, len(stars)), dtype=np.int8)
        signs = (2*swap.astype(np.float64) - 1.)
        statistics = signs @ contribution
        exceed += int(np.count_nonzero(
            np.abs(statistics) >= abs(observed)-1e-12))
        remaining -= batch
    return {
        "observed_balanced_accuracy_difference":observed,
        "two_sided_host_method_swap_permutation_p":float((1+exceed)/(1+permutations)),
        "n_independent_host_blocks":len(stars), "permutations":int(permutations),
        "seed":int(seed), "extreme_permutations":int(exceed),
        "test_null":"Paired method exchangeability at the whole-star level",
        "limitation":"Retrospective dataset previously studied; the star-level exchangeability null is a modeling assumption, not proof of physical planet truth."
    }


def host_cluster_bootstrap(test, reps=2000, seed=2026110802):
    """Paired host bootstrap: retains every KOI of each resampled source star.

    BA is recomputed with class denominators for each bootstrap sample.
    ROC AUC comparisons use the same host resample and the same NASA label.
    These are conditional CIs for fixed trained models on heldout host stars.
    """
    from sklearn.metrics import roc_auc_score
    y = test["historical_nasa_candidate_label"].to_numpy(dtype=np.int8)
    scores = {n:test[f"score_{n}"].to_numpy(dtype=float)
              for n in ("random_forest", "SNR_only", "logistic_4feature")}
    pred = {n:test[f"prediction_{n}"].to_numpy(dtype=bool)
            for n in scores}
    hosts,inverse=np.unique(test.kepid.to_numpy(),return_inverse=True)
    n=len(hosts)
    pos=(y==1);neg=(y==0)
    n_pos=np.bincount(inverse,weights=pos,minlength=n)
    n_neg=np.bincount(inverse,weights=neg,minlength=n)
    success={
        method:(
            np.bincount(inverse,weights=pos & (pred[method]==1),minlength=n),
            np.bincount(inverse,weights=neg & (pred[method]==0),minlength=n))
        for method in scores}
    rng=np.random.default_rng(seed)
    deltas={"forest_minus_snr_BA":[], "forest_minus_logistic_BA":[],
            "forest_minus_snr_AUC":[], "forest_minus_logistic_AUC":[]}
    for _ in range(int(reps)):
        picked = rng.integers(0,n,n)
        w = np.bincount(picked,minlength=n)
        a_pos=float(w @ n_pos); a_neg=float(w @ n_neg)
        if a_pos<1 or a_neg<1:
            continue
        def ba(method):
            tp,tn=success[method]
            return .5*(float(w@tp)/a_pos+float(w@tn)/a_neg)
        deltas["forest_minus_snr_BA"].append(ba("random_forest")-ba("SNR_only"))
        deltas["forest_minus_logistic_BA"].append(ba("random_forest")-ba("logistic_4feature"))
        sample_weight=w[inverse]
        try:
            forest_auc=roc_auc_score(y,scores["random_forest"],sample_weight=sample_weight)
            snr_auc=roc_auc_score(y,scores["SNR_only"],sample_weight=sample_weight)
            logistic_auc=roc_auc_score(y,scores["logistic_4feature"],sample_weight=sample_weight)
        except ValueError:
            # Some pathological resamples could have only one class.
            continue
        deltas["forest_minus_snr_AUC"].append(float(forest_auc-snr_auc))
        deltas["forest_minus_logistic_AUC"].append(float(forest_auc-logistic_auc))
    summary={}
    for key,values in deltas.items():
        if len(values) < int(reps)*.95:
            raise ValueError("Too many unclassifiable bootstrap draws")
        summary[key]={
            "CI_95":[float(v) for v in np.quantile(values,[.025,.975])],
            "median_bootstrap_delta":float(np.median(values)),
            "completed_draws":len(values)
        }
    return {
        "host_count":n, "bootstrap_reps_requested":int(reps),
        "seed":int(seed),
        "confidence_intervals":summary,
        "note":"Percentile cluster bootstrap conditional on fitted scores and chosen host split; repeated KOIs from each host move together."
    }


def naive_exact_mcnemar(test, a="random_forest", b="SNR_only"):
    """Supplement only: KOIs may share a host; not the primary inference."""
    y=test["historical_nasa_candidate_label"].to_numpy(dtype=np.int8)
    x=test[f"prediction_{a}"].to_numpy(dtype=int)==y
    z=test[f"prediction_{b}"].to_numpy(dtype=int)==y
    a_only=int(np.sum(x & ~z))
    b_only=int(np.sum(~x & z))
    disagreement=a_only+b_only
    p=binomtest(a_only, n=disagreement, p=.5).pvalue if disagreement else 1.
    return {
        "a_correct_b_wrong":a_only,
        "a_wrong_b_correct":b_only,
        "n_discordant_KOIs":disagreement,
        "exact_two_sided_naive_mcnemar_p":float(p),
        "warning":"KOIs within a host are clustered; report host-level swap test as primary."
    }


def subgroup_table(test):
    """Show error trades with true denominators, including missing values."""
    data=test.copy()
    masks={}
    period=pd.to_numeric(data.koi_period,errors="coerce")
    snr=pd.to_numeric(data.koi_model_snr,errors="coerce")
    for name,series,cuts in [
        ("period",period,(10.,100.)),
        ("snr",snr,(10.,30.))]:
        a,b=cuts
        masks[(name,"<lower")]=series<a
        masks[(name,"middle")]=(series>=a)&(series<b)
        masks[(name,">=upper")]=series>=b
        masks[(name,"missing")]=series.isna()
    output=[]
    for (variable,binname),which in masks.items():
        selected=data.loc[which]
        if selected.empty:
            output.append({"variable":variable,"range":binname,
                           "n_signals":0})
            continue
        y=selected["historical_nasa_candidate_label"].to_numpy(dtype=int)
        row={"variable":variable,"range":binname,"n_signals":len(selected),
             "n_hosts":int(selected.kepid.nunique()),
             "n_candidate_labels":int(y.sum()),
             "n_false_positive_labels":int((y==0).sum())}
        for name in ("random_forest","SNR_only","logistic_4feature"):
            predicted=selected[f"prediction_{name}"].to_numpy(dtype=int)
            row[f"accuracy_{name}"]=float(np.mean(predicted==y))
            row[f"candidate_recall_{name}"]=(float(np.mean(predicted[y==1]))
                if np.any(y==1) else None)
            row[f"false_positive_rate_{name}"]=(float(np.mean(predicted[y==0]))
                if np.any(y==0) else None)
        output.append(row)
    return pd.DataFrame(output)


def run(input_csv, output="results/dr25_inference",
        protocol=PROTOCOL):
    cfg=read_frozen_protocol(protocol)
    source=verify_source(input_csv,cfg)
    df=load_data(input_csv,download=False)
    if len(df)!=int(cfg["source"]["cohort_expected_rows_after_filter"]):
        raise ValueError("NASA post-filter source count differs from frozen expectation")
    if df.kepid.nunique()!=6923:
        raise ValueError("Unique stellar host count inconsistent with archive")
    folder=Path(output);folder.mkdir(parents=True,exist_ok=True)
    (folder/"frozen_protocol.json").write_bytes(Path(protocol).read_bytes())

    seeds=[cfg["heldout"]["primary_split_seed"]] + cfg["heldout"]["additional_split_seeds"]
    across=[]
    primary=None
    for i,seed in enumerate(seeds):
        print(f"Host-grouped NASA DR25 split {i+1}/{len(seeds)} (seed={seed})",flush=True)
        row,heldout=evaluate_one_split(df,seed,cfg,save_primary=(i==0))
        across.append(row)
        if heldout is not None:
            primary=heldout
    if primary is None:
        raise ValueError("Primary holdout output absent")
    primary.to_csv(folder/"primary_heldout_paired_predictions.csv",index=False)
    comparisons=[]
    for row in across:
        comparison={"seed":row["seed"],"n_test":row["test_n"],
                    "n_test_hosts":row["test_hosts"],
                    "balanced_accuracy_forest_minus_snr":row[
                        "difference_random_forest_minus_snr_balanced_accuracy"],
                    "balanced_accuracy_forest_minus_logistic":row[
                        "difference_random_forest_minus_logistic_balanced_accuracy"]}
        for method, m in row["models"].items():
            for key in ("accuracy","balanced_accuracy","roc_auc","recall",
                        "false_positive_rate","false_negative","false_positive",
                        "true_positive","true_negative","validation_candidate_recall"):
                comparison[f"{method}_{key}"]=m[key]
        comparisons.append(comparison)
    pd.DataFrame(comparisons).to_csv(folder/"ten_grouped_star_split_metrics.csv",index=False)
    subgroups=subgroup_table(primary)
    subgroups.to_csv(folder/"primary_subgroups_including_missing.csv",index=False)
    primary_report=across[0]
    perm=host_method_swap_permutation(
        primary, cfg["statistical_tests"]["primary_permutations"],
        cfg["statistical_tests"]["primary_permutation_seed"])
    boot=host_cluster_bootstrap(
        primary,cfg["statistical_tests"]["paired_host_bootstrap_reps"],
        cfg["statistical_tests"]["paired_host_bootstrap_seed"])
    mcnemar=naive_exact_mcnemar(primary)
    ranges={}
    for comparison in ("difference_random_forest_minus_snr_balanced_accuracy",
                       "difference_random_forest_minus_logistic_balanced_accuracy",
                       "difference_random_forest_minus_snr_roc_auc"):
        values=np.array([x[comparison] for x in across],dtype=float)
        ranges[comparison]={
            "n_splits":len(values), "median":float(np.median(values)),
            "minimum":float(values.min()),"maximum":float(values.max()),
            "positive_splits":int(np.sum(values>0)),
            "negative_splits":int(np.sum(values<0)),
            "note":"Source stars overlap between repeated splits; not independent trials and no pooled p-value."}
    report={
        "title":"NASA historical DR25 classification label agreement: fair paired host-aware statistical test",
        "scientific_claim":"Historical NASA Robovetter CANDIDATE versus FALSE POSITIVE label agreement, NOT confirmed actual planets or real survey sensitivity",
        "source":source,"n_rows":len(df),"n_stars":int(df.kepid.nunique()),
        "primary_split":primary_report,
        "primary_paired_host_method_swap_test":perm,
        "primary_paired_host_bootstrap":boot,
        "naive_row_level_exact_mcnemar_supplement":mcnemar,
        "other_split_sensitivity_not_independent":ranges,
        "all_split_metadata":across,
        "statistical_caveats":[
            "The original 12600 star split and labels were previously inspected. Even the prespecified primary metric for this extension is a retrospective test, not newly untouched independent confirmation.",
            "Validation thresholds target 90% candidate recall; test recall can differ between models, so this is not equal heldout recall comparison.",
            "Historical NASA pipeline labels were derived using additional measurements; four derived features may themselves reflect NASA selection mechanisms.",
            "Star-bootstrap and conditional host permutation account for same-host KOI clustering but not mission selection or imperfect physical labels.",
            "Repeated group splits test sensitivity to test-star composition; overlapping test stars prohibit pooling nominal p values.",
            "Statistical significance in historical label agreement does not establish superior real planet detection, physical transit confirmation, or improvement over full NASA Robovetter.",
            "ROC AUC is secondary and threshold-free; score calibration to astrophysical probabilities not established.",
            "The separate natural-SPSD and recurrence-guard experiments involve different tasks; never combine their outcomes or denominators with these KOI classification tests."
        ],
        "ai_disclosure":"Model/data audit, statistical code and narrative drafted with GPT-6. Independently review all source and statistical assumptions."
    }
    (folder/"inference_summary.json").write_text(json.dumps(report,indent=2)+"\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(10,5))
    data=pd.DataFrame(comparisons)
    x=np.arange(len(data))
    ax.plot(x,data["SNR_only_balanced_accuracy"],"o-",label="SNR-only",
            alpha=.85)
    ax.plot(x,data["random_forest_balanced_accuracy"],"o-",label="Four-feature random forest")
    ax.plot(x,data["logistic_4feature_balanced_accuracy"],"o-",label="Four-feature logistic")
    ax.set(xticks=x,xticklabels=data["seed"].astype(str).tolist(),
           xlabel="Host-group split seed (test hosts overlap across seeds)",
           ylabel="Held-out balanced accuracy against historical labels",
           title="Ten different host-group splits, validation-selected thresholds")
    ax.legend()
    fig.tight_layout()
    fig.savefig(folder/"ten_star_split_balanced_accuracy.png",dpi=175)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4.5))
    methods=["SNR_only","logistic_4feature","random_forest"]
    names=["SNR threshold","Logistic, 4 features","Random forest, 4 features"]
    values=[primary_report["models"][k]["balanced_accuracy"] for k in methods]
    ax.barh(names,values)
    ax.set(xlim=(0,1),xlabel="Balanced accuracy on primary held-out stars",
           title="Historical NASA candidate-vs-false-positive labels")
    for i,v in enumerate(values):
        ax.text(v+.008,i,f"{100*v:.2f}%",va="center")
    fig.tight_layout()
    fig.savefig(folder/"primary_balanced_accuracy.png",dpi=175)
    plt.close(fig)
    print(json.dumps({
        "primary_test_n":primary_report["test_n"],
        "primary_test_hosts":primary_report["test_hosts"],
        "primary_balanced_accuracy":{
            name:x["balanced_accuracy"] for name,x in primary_report["models"].items()},
        "primary_permutation_p":perm["two_sided_host_method_swap_permutation_p"],
        "primary_ci":boot["confidence_intervals"]["forest_minus_snr_BA"],
        "other_split_summary":ranges
    },indent=2),flush=True)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--csv",default="data/kepler_dr25.csv")
    p.add_argument("--out",default="results/dr25_inference")
    p.add_argument("--protocol",default=PROTOCOL)
    a=p.parse_args()
    run(a.csv,a.out,a.protocol)
