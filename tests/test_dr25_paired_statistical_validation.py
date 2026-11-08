"""Deterministic nonastronomical engineering checks for host-paired DR25 inference."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import balanced_accuracy_score

from dr25_paired_statistical_validation import (
    read_frozen_protocol, verify_source, host_method_swap_permutation,
    host_cluster_bootstrap, cluster_aggregates, naive_exact_mcnemar,
    subgroup_table, forest_model, logistic_model
)


def toy_predictions():
    # Multiple KOIs from the same star are different rows, not separate hosts.
    host=np.repeat(np.arange(100, 112),4)
    y=np.tile([1,1,0,0],12)
    snr=np.tile([0,1,1,0],12)
    # Forest is deliberately better (both errors and improvement), so
    # sign-flip test is deterministic and scientifically interpretable.
    forest=np.tile([1,1,0,0],12)
    forest[[2,14,25,34]]=1-forest[[2,14,25,34]]
    logistic=np.tile([1,0,0,0],12)
    x=pd.DataFrame({
        "kepid":host, "koi_period":np.tile([3.,40.,7.,200.],12),
        "koi_model_snr":np.tile([6.,10.,14.,33.],12),
        "historical_nasa_candidate_label":y,
        "prediction_SNR_only":snr,
        "prediction_random_forest":forest,
        "prediction_logistic_4feature":logistic
    })
    for name in ["SNR_only","random_forest","logistic_4feature"]:
        x[f"score_{name}"]=.1 + .8*x[f"prediction_{name}"]
    return x


def test_frozen_model_primary_and_source_are_fixed():
    p=read_frozen_protocol()
    assert p["source"]["cohort_expected_rows_after_filter"]==8054
    assert p["heldout"]["primary_split_seed"]==12600
    assert len(p["heldout"]["additional_split_seeds"])==9
    assert p["decision"]["validation_recall_target"]==.9


def test_sha256_of_wrong_csv_fails_before_any_model_training(tmp_path):
    file=tmp_path/"changed.csv"
    file.write_text("kepid,koi_pdisposition\n1,CANDIDATE\n")
    with pytest.raises(ValueError,match="SHA256"):
        verify_source(file,read_frozen_protocol())


def test_delta_equals_sklearn_balanced_accuracy_difference():
    table=toy_predictions()
    hosts,inverse,weights=cluster_aggregates(table)
    assert len(hosts)==12
    y=table.historical_nasa_candidate_label
    expected=(balanced_accuracy_score(y,table.prediction_random_forest) -
              balanced_accuracy_score(y,table.prediction_SNR_only))
    assert weights.sum()==pytest.approx(expected)


def test_host_signflip_is_reproducible_and_not_row_permutation():
    table=toy_predictions()
    a=host_method_swap_permutation(table,permutations=400,seed=456)
    b=host_method_swap_permutation(table,permutations=400,seed=456)
    assert a==b
    assert a["n_independent_host_blocks"]==12
    assert 0 < a["two_sided_host_method_swap_permutation_p"] <= 1


def test_null_predictions_have_permutation_p_of_one():
    t=toy_predictions()
    t["prediction_random_forest"]=t["prediction_SNR_only"]
    report=host_method_swap_permutation(t,permutations=200,seed=77)
    assert report["observed_balanced_accuracy_difference"]==pytest.approx(0)
    assert report["two_sided_host_method_swap_permutation_p"]==1


def test_grouped_bootstrap_intervals_are_reproducible_and_nonempty():
    t=toy_predictions()
    a=host_cluster_bootstrap(t,reps=60,seed=15)
    b=host_cluster_bootstrap(t,reps=60,seed=15)
    assert a==b
    assert a["host_count"]==12
    for key,val in a["confidence_intervals"].items():
        assert val["completed_draws"]==60
        assert val["CI_95"][0]<=val["CI_95"][1]


def test_exact_mcnemar_detects_paired_nonzero_disagreements():
    t=toy_predictions()
    value=naive_exact_mcnemar(t)
    assert (value["a_correct_b_wrong"] +
            value["a_wrong_b_correct"]==value["n_discordant_KOIs"])
    assert 0<value["exact_two_sided_naive_mcnemar_p"]<=1
    assert "clustered" in value["warning"].lower()


def test_all_missing_subgroup_is_preserved():
    t=toy_predictions()
    t.loc[t.index[:5],"koi_model_snr"]=np.nan
    out=subgroup_table(t)
    row=out[(out.variable=="snr")&(out.range=="missing")].iloc[0]
    assert row.n_signals==5
    assert row.n_hosts>=1


def test_secondary_logistic_is_full_four_feature_model():
    model=logistic_model(12600)
    assert model.steps[-1][0]=="logisticregression"
    assert model.steps[0][0]=="simpleimputer"
    assert len(model.steps)==3


def test_primary_forest_architecture_is_unchanged():
    model=forest_model(12600)
    rf=model.steps[-1][1]
    assert rf.n_estimators==120
    assert rf.max_depth==9
    assert rf.min_samples_leaf==3
