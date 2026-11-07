"""Physical sanity checks for eclipsing-binary warning logic.

This is not a completeness or false-positive calibration study.
"""
import numpy as np
from binary_eclipse_diagnostics import estimate_binary_indicators


def fixture(mode="planet", seed=7):
    rng=np.random.default_rng(seed)
    t=np.arange(0,56,.025)
    f=1+rng.normal(0,.00022,len(t))
    p=4.
    epoch=.9
    duration=.175
    phase=(t-epoch+p/2)%p-p/2
    k=np.round((t-epoch)/p).astype(int)
    near=np.abs(phase)<duration/2
    if mode=="planet":
        f[near]-=.004
    elif mode=="alternating":
        f[near&(k%2==0)]-=.006
        f[near&(k%2==1)]-=.002
    elif mode=="secondary":
        f[near]-=.006
        opposite=(t-(epoch+p/2)+p/2)%p-p/2
        f[np.abs(opposite)<duration/2]-=.0025
    return t,f,p,epoch,duration


def test_equal_repeating_dips_do_not_trigger_binary_warning():
    d=estimate_binary_indicators(*fixture("planet"))
    assert d["n_events"]>=9
    assert d["odd_even_warning"] is False
    assert d["secondary_warning"] is False
    assert d["binary_review_warning"] is False


def test_alternating_unequal_dips_trigger_odd_even_warning():
    d=estimate_binary_indicators(*fixture("alternating"))
    assert d["odd_even_depth_ratio"]>.35
    assert d["odd_even_statistic"]>3
    assert d["odd_even_warning"] is True


def test_separate_secondary_eclipse_triggers_warning():
    d=estimate_binary_indicators(*fixture("secondary"))
    assert d["secondary_snr"]>5
    assert d["secondary_warning"] is True


def test_not_a_planet_probability():
    d=estimate_binary_indicators(*fixture("planet"))
    assert "not proof" in d["scientific_caveat"].lower()
