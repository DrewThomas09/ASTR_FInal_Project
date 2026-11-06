"""Offline tests for the new blind simulator and uncertainty-aware triage."""
import numpy as np
import pandas as pd
import pytest
from blind_transit_benchmark import (
    simulate, robust_sigma, threshold_from_controls, summarize_trials)
from ml_uncertainty_triage import (
    select_review_cutoff, triage_evaluation,
    star_bootstrap_difference, experiment)


def test_blind_simulation_has_random_period_and_negative_controls():
    periods=[]
    for seed in [12,13,14,15,16]:
        t,f,truth=simulate(seed,kind="planet")
        periods.append(truth["injected_period_days"])
        assert len(t)==len(f) and len(t)>1000
        assert 2.1<=truth["injected_period_days"]<=9.8
    assert len(set(periods))==len(periods)
    for kind in ("white_noise","red_noise","single_dip","binary_like"):
        _,_,truth=simulate(33,kind=kind)
        assert truth["injected_period_days"] is None


def test_blind_simulation_is_reproducible():
    t,f,truth=simulate(22,depth_ppm=4000)
    t2,f2,truth2=simulate(22,depth_ppm=4000)
    assert np.array_equal(t,t2) and np.array_equal(f,f2)
    assert truth==truth2


def test_noise_estimate_and_null_threshold():
    _,f,_=simulate(12,kind="white_noise")
    assert 0.0006<robust_sigma(f)<0.0015
    threshold=threshold_from_controls(np.arange(1,11),.2)
    assert 8<=threshold<=10


def test_control_summary_does_not_count_fake_planets_as_recovered():
    df=pd.DataFrame({
        "group":["planet_500ppm","planet_500ppm","red_noise"],
        "flagged":[True,False,True],"recovered":[True,False,False]})
    summary=summarize_trials(df)
    assert summary.loc[summary.group=="planet_500ppm","recovery_fraction"].iloc[0]==.5


def test_triage_accounts_for_abstention_and_hidden_misses():
    report=triage_evaluation([0,1,1,0],[1,0,1,0],[False,True,False,False])
    assert report["review_n"]==1
    assert report["auto_wrong_count"]==1
    assert report["false_dismissals_auto"]==0
    assert report["underlying_binary"]["false_negative"]==1


def test_validation_review_quantile():
    v=np.arange(100,dtype=float)
    cutoff=select_review_cutoff(v,.3)
    assert sum(v<cutoff)/100<.31


def test_paired_bootstrap():
    stars=np.arange(100)
    y=np.array([0,1]*50)
    pred=np.array([1,1]*50)
    a=np.array([True,False]*50)
    b=np.array([False,True]*50)
    result=star_bootstrap_difference(stars,y,pred,a,b,reps=80)
    assert result["ci95"] is not None


def synthetic_catalog(nstars=200):
    rng=np.random.default_rng(100)
    rows=[]
    for s in range(nstars):
        for j in range(2 if s%10==0 else 1):
            label=int(rng.random()>.5)
            rows.append({
                "kepid":100000+s, "kepoi_name":f"K.{s}.{j}",
                "koi_pdisposition":"CANDIDATE" if label else "FALSE POSITIVE",
                "label":label, "koi_period":float(rng.uniform(1,150)),
                "koi_duration":float(rng.uniform(1,15)),
                "koi_depth":float(rng.uniform(100,4000)),
                "koi_model_snr":float(rng.uniform(3,25)),
            })
    return pd.DataFrame(rows)


def test_synthetic_triage_end_to_end(tmp_path):
    report=experiment(synthetic_catalog(),tmp_path,seed=12600)
    assert (tmp_path/"triage_tradeoff.png").exists()
    assert (tmp_path/"subgroups.csv").exists()
    assert report["methods"]["margin_only"]["n"]==report["test_n"]
    assert report["methods"]["margin_plus_disagreement"]["n"]==report["test_n"]


def test_astropy_blind_bls_smoke_if_installed():
    pytest.importorskip("astropy")
    from blind_transit_benchmark import bls_peak
    t,f,_=simulate(20,kind="planet",depth_ppm=4000)
    peak=bls_peak(t,f)
    assert 1.5<=peak["period_days"]<=12.0
    assert np.isfinite(peak["score"])
