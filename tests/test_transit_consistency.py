"""Offline physical sanity tests for individual transit consistency."""
import numpy as np
from transit_consistency import individual_transit_checks


def _observations(seed=1,kind="planet"):
    rng=np.random.default_rng(seed)
    t=np.arange(0,46,.025)
    f=1+rng.normal(0,.0005,len(t))
    period=4.2
    epoch=1.1
    duration=.15
    phase=(t-epoch+period/2)%period-period/2
    if kind=="planet":
        f[np.abs(phase)<duration/2]-=.006
    if kind=="single":
        f[np.abs(t-epoch)<duration/2]-=.006
    if kind=="alternating":
        number=np.floor((t-epoch+period/2)/period).astype(int)
        on=np.abs(phase)<duration/2
        f[on&(number%2==0)]-=.006
        f[on&(number%2==1)]-=.002
    return t,f,period,epoch,duration


def test_consistent_planet_has_many_contributing_events():
    result,_=individual_transit_checks(*_observations(kind="planet"))
    assert result["n_observable_events"]>=8
    assert result["positive_depth_fraction"]>=.9
    assert result["dominance"]<.4


def test_single_dip_has_dominance_warning():
    result,_=individual_transit_checks(*_observations(kind="single"))
    assert result["dominance"]>.6
    assert "one event dominates" in result["warning"]


def test_odd_even_depths_are_measurable():
    result,_=individual_transit_checks(*_observations(kind="alternating"))
    assert abs(result["odd_even_depth_difference_ppm"])>2000


def test_invalid_ephemeris_is_rejected():
    try:
        individual_transit_checks(*_observations(kind="planet")[:2],period=-3,epoch=1,duration=.1)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid period should be rejected")
