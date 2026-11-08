"""Pure offline checks for supplemental archived DR25 class-tradeoff inference."""
import numpy as np
import pandas as pd
import pytest
from dr25_secondary_paired_tradeoff import (
    star_bootstrap_class_tradeoffs, exact_paired_count,
    load_verified_predictions
)


def toy():
    return pd.DataFrame({
        "kepid":np.repeat(np.arange(12),4),
        "koi_period":np.tile([2.,20.,100.,300.],12),
        "historical_nasa_candidate_label":np.tile([1,1,0,0],12),
        "prediction_SNR_only":np.tile([1,1,1,0],12),
        "prediction_logistic_4feature":np.tile([1,0,0,0],12),
        "prediction_random_forest":np.tile([1,1,0,0],12)
    })


def test_paired_methods_source_is_cryptographically_locked(tmp_path):
    f=tmp_path/"fake.csv"
    toy().to_csv(f,index=False)
    with pytest.raises(ValueError,match="changed"):
        load_verified_predictions(f)


def test_class_rate_forest_minus_logistic_only_improves_candidate_recall():
    df=toy()
    result=star_bootstrap_class_tradeoffs(df,reps=75,seed=14)
    x=result["methods"]["random_forest_minus_logistic_4feature"]
    assert x["candidate_recall"]["bootstrap_median"]==pytest.approx(.5)
    assert x["false_positive_rate"]["bootstrap_median"]==pytest.approx(0.)
    assert x["balanced_accuracy"]["bootstrap_median"]==pytest.approx(.25)


def test_bootstrap_entire_star_is_reproducible():
    df=toy()
    a=star_bootstrap_class_tradeoffs(df,reps=90,seed=11)
    b=star_bootstrap_class_tradeoffs(df,reps=90,seed=11)
    assert a==b
    assert a["independent_host_blocks"]==12


def test_false_dismissal_and_fp_counts_have_correct_denominators():
    df=toy()
    out=exact_paired_count(df,"random_forest","SNR_only")
    assert out["n"]==48
    assert out["n_hosts"]==12
    assert out["candidate_false_dismissals_a"]==0
    assert out["candidate_false_dismissals_b"]==0
    assert out["historical_false_positive_acceptances_a"]==0
    assert out["historical_false_positive_acceptances_b"]==12


def test_long_period_subset_is_applied_without_moving_other_rows():
    df=toy()
    mask=df.koi_period>=100
    result=exact_paired_count(df,"random_forest","logistic_4feature",mask)
    assert result["n"]==24
    assert result["n_hosts"]==12
