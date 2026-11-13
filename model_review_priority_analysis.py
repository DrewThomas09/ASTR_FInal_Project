"""Supplement: review-priority analysis of NASA historical DR25 labels.
Accepts the archived original *held-out predictions CSV*. Does not refit a model,
claim independent planet identifications, or assume human review is correct.

Usage: python model_review_priority_analysis.py path/to/primary_heldout_paired_predictions.csv
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, balanced_accuracy_score

MODELS = [
    ("SNR-only", "SNR_only"),
    ("4-feature logistic", "logistic_4feature"),
    ("4-feature random forest", "random_forest"),
]

def main(csv_path: Path):
    df = pd.read_csv(csv_path)
    required = {"kepid", "koi_period", "historical_nasa_candidate_label",
                "prediction_random_forest", "score_random_forest",
                "validation_threshold_random_forest"}
    for _, key in MODELS:
        required.update({"prediction_" + key, "score_" + key})
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing archived columns: {sorted(missing)}")
    y = df["historical_nasa_candidate_label"].to_numpy(dtype=int)
    n = len(y)
    if n != 1619 or df.kepid.nunique() != 1385:
        raise ValueError("This audit is tied to the original 1,619-row, 1,385-star split.")
    print("MODEL / ACCURACY / CANDIDATE RECALL / FPR / AUROC / AP")
    for name, key in MODELS:
        p = df["prediction_" + key].to_numpy(dtype=int)
        s = df["score_" + key].to_numpy(float)
        positives, negatives = y == 1, y == 0
        print(name, round(np.mean(p==y), 4),
              round(np.mean(p[positives]), 4), round(np.mean(p[negatives]), 4),
              round(roc_auc_score(y,s), 4), round(average_precision_score(y,s),4))
    long_period = df.koi_period.to_numpy(float) >= 100
    print("\nPERIOD >=100 d (exploratory; historical labels)")
    print("N=", int(long_period.sum()), "candidate-labels=", int(np.sum(y[long_period] == 1)))
    for name,key in MODELS:
        p=df["prediction_"+key].to_numpy(dtype=int)
        ym=y[long_period]; pm=p[long_period]
        print(name, "candidate retained",int(np.sum((ym==1)&(pm==1))),
              "historical FP accepted",int(np.sum((ym==0)&(pm==1))))
    pred = df.prediction_random_forest.to_numpy(dtype=int)
    score = df.score_random_forest.to_numpy(float)
    threshold = float(df.validation_threshold_random_forest.iloc[0])
    if not np.allclose(df.validation_threshold_random_forest, threshold):
        raise AssertionError("Unexpected change to original validation threshold")
    order = np.argsort(np.abs(score-threshold),kind="stable")
    errors = (pred != y)
    print("\nREVIEW QUEUE: lowest decision margin first; no actual review performed")
    print("reviewed  disagreements_flagged  wrong_unreviewed  random_expected_unreviewed")
    for share in (0, .1, .2, .3, .4, .5, .6):
        budget=round(share*n)
        flagged=int(errors[order[:budget]].sum())
        remaining=int(errors.sum()-flagged)
        random_expected=errors.sum()*(1-budget/n)
        print(budget,flagged,remaining,round(random_expected,2))
    print("\nThis is a retrospective diagnostic on already-used test labels.")
if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("predictions_csv",type=Path)
    main(p.parse_args().predictions_csv)
