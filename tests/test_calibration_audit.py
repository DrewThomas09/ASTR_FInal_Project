"""Offline tests of held-out DR25 score calibration bookkeeping."""
import numpy as np
import pandas as pd
import pytest
from calibration_audit import calibration_bins, run


def test_perfect_binary_score_has_zero_brier_and_ece():
    scores=[0.,0.,1.,1.]
    labels=[0,0,1,1]
    bins,metrics=calibration_bins(scores,labels)
    assert metrics["brier_score_against_vetter_labels"]==0
    assert metrics["expected_calibration_error_against_vetter_labels"]==0
    assert bins["n"].sum()==4


def test_constant_score_brier_matches_direct_calculation():
    x=np.full(100,.5)
    y=np.array([0]*60+[1]*40)
    bins,metrics=calibration_bins(x,y)
    assert np.isclose(metrics["brier_score_against_vetter_labels"],.25)
    assert np.isclose(metrics["expected_calibration_error_against_vetter_labels"],.10)
    assert bins["n"].sum()==len(x)


def test_calibration_does_not_mutate_predictions(tmp_path):
    df=pd.DataFrame({"model_score":[.1,.9,.4,.7],
                     "label":[0,1,0,1],"kepid":[1,2,3,4]})
    infile=tmp_path/"holdout.csv"; df.to_csv(infile,index=False)
    before=infile.read_bytes()
    result=run(infile,tmp_path/"out")
    assert result["n"]==4
    assert infile.read_bytes()==before
    assert (tmp_path/"out"/"calibration_curve.png").exists()
    assert (tmp_path/"out"/"calibration_bins.csv").exists()


def test_invalid_scores_raise():
    with pytest.raises(ValueError):
        calibration_bins([.1,1.2],[0,1])
    with pytest.raises(ValueError):
        calibration_bins([.1,float("nan")],[0,1])
