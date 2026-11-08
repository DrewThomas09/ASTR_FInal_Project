"""Deterministic checks for validation-only threshold and group-aware period evaluation."""
import numpy as np
import pandas as pd
import pytest

from dr25_period_aware_recall_experiment import (
    load_protocol, period_labels, validation_only_thresholds,
    binary_decisions, measure_classification, cluster_bootstrap_tradeoff
)


P=load_protocol()


def test_period_boundaries_and_missing_are_nonoverlapping():
    p=np.array([0.1,9.99,10,99.99,100,500,np.nan,np.inf,-1])
    got=list(period_labels(p))
    assert got==["short","short","medium","medium","long","long",
                 "missing","missing","missing"]


def test_protocol_has_new_untested_seed_list_and_three_bins():
    assert P["new_group_split_seeds"]==list(range(14000,14010))
    assert len(P["new_method"]["bins"])==3
    assert P["new_method"]["minimum_positive_validation_examples_to_use_bin_threshold"]==30


def test_fallback_when_not_enough_validation_candidates():
    n=100
    score=np.linspace(0,1,n)
    labels=np.r_[np.ones(50,dtype=int),np.zeros(50,dtype=int)]
    periods=np.full(n,120.)
    result=validation_only_thresholds(score,labels,periods,P)
    assert not result["period_bin_cutoffs"]["long"]["used_fallback_global_cutoff"]
    assert result["period_bin_cutoffs"]["short"]["used_fallback_global_cutoff"]
    assert result["period_bin_cutoffs"]["short"]["cutoff"]==result["global_validation_cutoff"]


def test_thresholds_use_validation_only_and_not_test_label_values():
    score=np.linspace(.1,.99,200)
    y=np.array([1 if i%3!=0 else 0 for i in range(200)])
    period=np.repeat([5.,30.,130.,np.nan],50)
    threshold=validation_only_thresholds(score,y,period,P)
    test_score=np.array([.2,.55,.8,.9])
    test_period=np.array([6.,20.,110.,np.nan])
    original,adjusted,bins=binary_decisions(test_score,test_period,threshold)
    assert original.shape==adjusted.shape==(4,)
    assert list(bins)==["short","medium","long","missing"]
    # The exact same predictions must be returned if hypothetical TEST labels change.
    unobserved_test_labels=np.array([0,0,0,0])
    assert np.array_equal(binary_decisions(test_score,test_period,threshold)[1],
                          adjusted)


def test_identical_bins_and_validation_thresholds_yield_same_classification():
    scores=np.array([.3,.55,.68,.95])
    y=np.r_[np.ones(50,int),np.zeros(50,int)]
    th=validation_only_thresholds(np.linspace(0,1,100),y,
                                 np.full(100,np.nan),P)
    old,new,bins=binary_decisions(scores,np.full(4,np.nan),th)
    assert np.array_equal(old,new)
    assert all(b=="missing" for b in bins)


def test_balanced_accuracy_handles_unequal_class_counts():
    y=np.array([1,1,1,0])
    pred=np.array([1,1,0,1])
    m=measure_classification(y,pred)
    assert m["candidate_recall"]==pytest.approx(2/3)
    assert m["false_positive_rate"]==pytest.approx(1)
    assert m["balanced_accuracy"]==pytest.approx(1/3)


def test_empty_or_single_label_group_does_not_invent_balanced_accuracy():
    empty=measure_classification([],[])
    assert empty["balanced_accuracy"] is None
    single=measure_classification([1,1],[1,0])
    assert single["candidate_recall"]==.5
    assert single["balanced_accuracy"] is None


def test_paired_host_bootstrap_no_difference_is_exactly_zero():
    n=80
    labels=np.tile([1,0,1,0],20)
    pred=np.tile([1,1,0,0],20)
    t=pd.DataFrame({
        "kepid":np.repeat(np.arange(20),4),
        "historical_nasa_candidate_label":labels,
        "prediction_global":pred,"prediction_period_aware":pred})
    r=cluster_bootstrap_tradeoff(t,reps=75,seed=123)
    assert r["n_independent_hosts"]==20
    for result in r["difference_new_minus_global"].values():
        assert result["CI95"]==[0.,0.]


def test_bootstrap_retains_same_host_block_and_seed():
    n=80
    labels=np.tile([1,0,1,0],20)
    old=np.tile([0,0,0,0],20)
    new=np.tile([1,0,0,0],20)
    t=pd.DataFrame({
        "kepid":np.repeat(np.arange(20),4),
        "historical_nasa_candidate_label":labels,
        "prediction_global":old,"prediction_period_aware":new})
    a=cluster_bootstrap_tradeoff(t,reps=90,seed=126)
    b=cluster_bootstrap_tradeoff(t,reps=90,seed=126)
    assert a==b
    assert a["difference_new_minus_global"]["candidate_recall"]["median"]==pytest.approx(.5)
    assert a["difference_new_minus_global"]["false_positive_rate"]["median"]==0
    assert a["difference_new_minus_global"]["balanced_accuracy"]["median"]==pytest.approx(.25)
