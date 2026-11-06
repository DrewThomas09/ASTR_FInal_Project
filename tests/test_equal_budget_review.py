"""Fair-review evaluation sanity tests. No real NASA result is implied."""
import numpy as np
from ml_uncertainty_triage import (
    fixed_budget_mask, per_100_input_metrics, paired_budget_ci,
    fair_review_budget_comparison)


def test_fixed_budget_has_exact_count_without_labels():
    score=np.array([.2,1.,.8,.1,.4,1.1,2.,3.,0.])
    mask=fixed_budget_mask(score,1/3)
    assert int(mask.sum())==3
    assert list(np.flatnonzero(mask))==[5,6,7]


def test_reviewed_case_does_not_become_an_automatic_success():
    y=[1,1,0,0]
    predicted=[0,1,1,0]
    reviewed=[True,False,False,False]
    result=per_100_input_metrics(y,predicted,reviewed)
    assert result["review_n"]==1
    assert result["wrong_auto"]==1
    assert result["candidate_false_dismissals_auto"]==0
    assert result["false_positive_auto_per_100_input"]==25.


def test_host_star_bootstrap_sign_on_known_example():
    n=100
    stars=np.arange(n)
    y=np.array([0,1]*50)
    pred=np.ones(n,dtype=bool)
    # A: review correct predictions; B: review wrong predictions.
    a=np.array([False,True]*50)
    b=np.array([True,False]*50)
    result=paired_budget_ci(stars,y,pred,a,b,reps=100)
    assert result["difference_B_minus_A_per_100"]<0
    assert result["ci95"][1]<0


def test_equal_review_budget_for_all_three_strategies():
    n=120
    rng=np.random.default_rng(14)
    y=rng.integers(0,2,n)
    pred=np.arange(n)%2==0
    margin=rng.uniform(.01,.4,n)
    std=rng.uniform(.005,.12,n)
    stable=margin/(.04+std)
    table,paired,masks=fair_review_budget_comparison(
        y,pred,np.arange(n),margin,stable,
        budgets=(.1,.2,.3,.4),seed=12)
    assert len(table)==12
    for budget,group in table.groupby("budget"):
        assert group["review_n"].nunique()==1
        assert group["method"].nunique()==3
    assert paired["ci95"] is not None
    assert all(mask.sum()==36 for mask in masks.values())


def test_fixed_budget_rejects_nonfinite_scores():
    try:
        fixed_budget_mask([.2,float("nan")],.5)
    except ValueError:
        pass
    else:
        raise AssertionError("NaN must not silently influence review ranking")
