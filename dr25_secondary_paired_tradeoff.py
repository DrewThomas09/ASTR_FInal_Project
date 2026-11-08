"""Read-only supplemental host-aware audit of original DR25 heldout predictions.

No model fitting, no threshold tuning, and no new labels. This script can
only analyze the hash-verified first split from GitHub Actions run 42513638366.
The forest vs SNR balanced-accuracy contrast was the predeclared primary;
forest vs logistic and class-specific rates are EXPLORATORY supplementary
comparisons with NASA's historical Robovetter labels.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

from dr25_paired_statistical_validation import host_method_swap_permutation

EXPECTED_SOURCE_SHA256 = "3682e0be30506ddcfe4bbb0c683ed6884454c5e5fbf8d946922fb48248712663"
METHODS = ("SNR_only","logistic_4feature","random_forest")


def load_verified_predictions(path):
    b=Path(path).read_bytes()
    actual=hashlib.sha256(b).hexdigest()
    if actual!=EXPECTED_SOURCE_SHA256:
        raise ValueError("Original first-split NASA KOI predictions changed; abort")
    df=pd.read_csv(path)
    if (len(df)!=1619 or df.kepid.nunique()!=1385 or
        df.historical_nasa_candidate_label.sum()!=851):
        raise ValueError("Not the original 1619-row star-grouped NASA test")
    for method in METHODS:
        if not np.isin(df[f"prediction_{method}"],[0,1]).all():
            raise ValueError("Invalid binary prediction")
    return df


def star_bootstrap_class_tradeoffs(df,reps=2000,seed=2026110805):
    """Paired within host star, report both class recall and FPR deltas."""
    y=df.historical_nasa_candidate_label.to_numpy(dtype=int)
    stars,inverse=np.unique(df.kepid,return_inverse=True)
    n=len(stars)
    p=y==1;z=~p
    denom_p=np.bincount(inverse,weights=p,minlength=n)
    denom_n=np.bincount(inverse,weights=z,minlength=n)
    comparisons=[("random_forest","logistic_4feature"),
                 ("random_forest","SNR_only")]
    raw={}
    for a,b in comparisons:
        d=(df[f"prediction_{a}"].to_numpy(dtype=int) -
           df[f"prediction_{b}"].to_numpy(dtype=int))
        raw[(a,b)] = (
            np.bincount(inverse,weights=p*d,minlength=n),
            np.bincount(inverse,weights=z*d,minlength=n))
    rng=np.random.default_rng(seed)
    out={f"{a}_minus_{b}":{"candidate_recall":[],"false_positive_rate":[],
                            "balanced_accuracy":[]} for a,b in comparisons}
    for _ in range(reps):
        w=np.bincount(rng.integers(0,n,n),minlength=n)
        n_p=float(w@denom_p);n_n=float(w@denom_n)
        if n_p==0 or n_n==0: continue
        for pair,(pos,neg) in raw.items():
            rp=float(w@pos/n_p)
            fp=float(w@neg/n_n)
            entry=out[f"{pair[0]}_minus_{pair[1]}"]
            entry["candidate_recall"].append(rp)
            entry["false_positive_rate"].append(fp)
            entry["balanced_accuracy"].append(.5*(rp-fp))
    result={}
    for label,metrics in out.items():
        result[label]={}
        for name,data in metrics.items():
            if len(data)<reps*.95:raise ValueError("Too few valid star draws")
            result[label][name]={
                "bootstrap_ci95":[float(v) for v in np.quantile(data,[.025,.975])],
                "bootstrap_median":float(np.median(data)),
                "draws":len(data)}
    return {"independent_host_blocks":n, "reps":reps,"seed":seed,
            "methods":result,
            "limitation":"Retrospective, conditional on previously explored NASA labels and original fitted model scores."}


def exact_paired_count(df,first,second,subset=None):
    if subset is not None:
        df=df.loc[subset]
    y=df.historical_nasa_candidate_label.to_numpy(dtype=int)
    a=df[f"prediction_{first}"].to_numpy(dtype=int)
    b=df[f"prediction_{second}"].to_numpy(dtype=int)
    return {"n":len(df),"n_hosts":int(df.kepid.nunique()),
            "a_correct_b_wrong":int(np.sum((a==y)&(b!=y))),
            "b_correct_a_wrong":int(np.sum((b==y)&(a!=y))),
            "candidate_false_dismissals_a":int(np.sum((y==1)&(a==0))),
            "candidate_false_dismissals_b":int(np.sum((y==1)&(b==0))),
            "historical_false_positive_acceptances_a":int(np.sum((y==0)&(a==1))),
            "historical_false_positive_acceptances_b":int(np.sum((y==0)&(b==1)))}


def main(source,out):
    df=load_verified_predictions(source)
    permutation=host_method_swap_permutation(
        df,permutations=20000,seed=2026110806,
        method="random_forest",baseline="logistic_4feature")
    bootstrap=star_bootstrap_class_tradeoffs(df)
    long=df.koi_period>=100
    info={
        "source":"Original already archived first-split 1619 Kepler KOI historical vetter labels",
        "original_predictions_sha256":EXPECTED_SOURCE_SHA256,
        "forest_vs_logistic_exploratory_host_permutation":permutation,
        "class_specific_paired_host_bootstrap":bootstrap,
        "first_split_paired_counts":{
            "all_kois":exact_paired_count(df,"random_forest","logistic_4feature"),
            "period_at_least_100days":exact_paired_count(
                df,"random_forest","logistic_4feature",subset=long)},
        "context":"No refitting, no adjusted threshold, no independent planet confirmation; p-values assess archived automatic-label agreement only.",
        "limits":[
            "This is a secondary contrast checked after reviewing the original results; not a new predeclared primary confirmation.",
            "Host permutation relies on conditional exchangeability of the paired methods by Kepler source star.",
            "Forest has lower historical candidate recall despite fewer false positive labels accepted.",
            "Long-period subgroup was exposed in earlier exploratory output; no subgroup statistical claim is confirmatory."
        ]}
    folder=Path(out)
    folder.mkdir(parents=True,exist_ok=True)
    (folder/"supplementary_paired_clustering.json").write_text(json.dumps(info,indent=2)+"\n")
    print(json.dumps(info,indent=2),flush=True)
    return info


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--csv",required=True)
    ap.add_argument("--out",default="results/dr25_paired_supplemental")
    a=ap.parse_args()
    main(a.csv,a.out)
