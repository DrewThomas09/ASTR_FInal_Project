"""Synthetic, offline regression tests for held-out audit and fixed review budgets.

These tests do not estimate Kepler model accuracy.
"""
import numpy as np
import pandas as pd
from ml_uncertainty_triage import experiment


def constructed_catalog(nstars=210):
    rng=np.random.default_rng(92026)
    rows=[]
    for star in range(nstars):
        repeats=2 if star%7==0 else 1
        for i in range(repeats):
            candidate=int(rng.random()<.48)
            rows.append({"kepid":100000+star,
                "kepoi_name":f"SYN{star:04d}.{i}",
                "koi_pdisposition":"CANDIDATE" if candidate else "FALSE POSITIVE",
                "label":candidate,
                "koi_period":float(rng.uniform(1,220)),
                "koi_duration":float(rng.uniform(1,15)),
                "koi_depth":float(rng.uniform(60,6000)),
                "koi_model_snr":float(rng.uniform(4,55))})
    return pd.DataFrame(rows)


def test_validation_only_model_selection_and_saved_holdout(tmp_path):
    result=experiment(constructed_catalog(),str(tmp_path),seed=13)
    assert result["chosen_disagreement_weight"] in (.01,.02,.04,.08,.16)
    assert len(result["validation_weight_trials"])==5
    assert (tmp_path/"holdout_predictions.csv").exists()
    assert (tmp_path/"equal_budget_comparison.csv").exists()
    assert (tmp_path/"equal_budget_tradeoff.png").exists()
    predictions=pd.read_csv(tmp_path/"holdout_predictions.csv")
    comparison=pd.read_csv(tmp_path/"equal_budget_comparison.csv")
    assert len(predictions)==result["test_n"]
    assert predictions["kepid"].nunique()>=50
    assert "review_margin_30pct" in predictions
    assert "review_disagreement_30pct" in predictions
    assert predictions["review_margin_30pct"].sum()==predictions["review_disagreement_30pct"].sum()
    for budget,group in comparison.groupby("budget"):
        assert group["review_n"].nunique()==1
        assert set(group["method"])=={"random_review","margin_only","margin_plus_disagreement"}
    assert 0<=result["equal_budget"]["paired_error_difference_at_30pct"]["reps"]


def test_identical_binary_predictions_preserved(tmp_path):
    report=experiment(constructed_catalog(180),str(tmp_path),seed=123)
    assert report["equal_budget"]["same_classification_predictions"] is True
    p=pd.read_csv(tmp_path/"holdout_predictions.csv")
    assert p["predicted_candidate"].isin([0,1]).all()
