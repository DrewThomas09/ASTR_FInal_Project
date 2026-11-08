"""Offline safety tests for actual published ExoMiner++ score postprocessing.

These fixtures test software properties, not astrophysical performance.
"""
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import average_precision_score
from exominer_published_score_postprocessor import (
    design, fit_frozen_folds, metric
)


def make_table():
    rng=np.random.default_rng(415)
    n=100
    ids=np.arange(n)
    y=(ids%3==0)
    return pd.DataFrame({
        "uid":[f"{x}-1-S6" for x in ids],
        "target_id":ids+100000,
        "fold":ids%10,
        "label":np.where(y,"KP","EB"),
        "score":np.where(y,.77,.26)+rng.normal(0,.035,n),
        "tce_period":np.full(n,3.2),
        "tce_duration":np.full(n,.13),
        "tce_max_mult_ev":np.where(y,23.,9.),
        "ruwe":np.where(ids%5==0,np.nan,1.12),
    })


def settings():
    return {"model":{"C":.3,"max_iter":2000,"solver":"lbfgs"}}


def test_score_only_model_never_uses_label():
    df=make_table()
    original=df.score.copy()
    matrix=design(df,enhanced=False)
    assert matrix.shape==(100,1)
    shuffled=df.copy()
    shuffled.label=shuffled.label.iloc[::-1].to_numpy()
    assert np.allclose(design(shuffled,enhanced=False),matrix)
    assert np.array_equal(df.score,original)


def test_extra_features_have_frozen_shape_and_missing_gaia_is_not_zero_truth():
    df=make_table()
    x=design(df,enhanced=True)
    assert x.shape==(100,6)
    assert np.isnan(x[0,4])
    assert np.isclose(x[0,-1],np.log1p(.13/3.2))
    assert np.isclose(x[1,3],np.log1p(9.))


def test_ten_folds_predict_every_star_without_training_on_own_star():
    df=make_table()
    prediction,folds=fit_frozen_folds(df,settings(),enhanced=False)
    assert len(folds)==10
    assert all(r["train_star_count"]==90 for r in folds)
    assert all(r["test_star_count"]==10 for r in folds)
    assert np.isfinite(prediction).all()
    assert ((prediction>=0)&(prediction<=1)).all()


def test_extra_model_also_predicts_and_missing_values_are_imputed_train_only():
    df=make_table()
    prediction,logs=fit_frozen_folds(df,settings(),enhanced=True)
    assert len(logs)==10
    assert all(r["number_model_features"]==6 for r in logs)
    assert all(r["training_only_median_imputer_and_scaler"] for r in logs)
    assert np.isfinite(prediction).all()


def test_cannot_let_one_star_cross_original_published_folds():
    df=make_table()
    df.loc[1,"target_id"]=df.loc[0,"target_id"]  # indices 0 and 1 belong to DIFFERENT original folds
    with pytest.raises(AssertionError,match="TIC collision"):
        fit_frozen_folds(df,settings(),enhanced=True)


def test_binary_scores_and_result_threshold_are_correct():
    result=metric([1,1,0,0],[.9,.1,.8,.2])
    assert result["tp"]==result["fp"]==result["fn"]==result["tn"]==1
    assert result["precision_at_0_5"]==.5
    assert result["recall_at_0_5"]==.5
    assert result["average_precision"]==average_precision_score([1,1,0,0],[.9,.1,.8,.2])


def test_nonphysical_negative_orbit_rejected():
    df=make_table()
    df.loc[0,"tce_period"]=-1
    with pytest.raises(ValueError,match="invalid original NASA physical scalar"):
        design(df,enhanced=True)
