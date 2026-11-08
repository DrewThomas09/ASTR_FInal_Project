"""Offline controls for new event recovery/alias diagnostics.

These are controlled synthetic transit/step fixtures, NOT NASA model scores.
"""
import numpy as np
import pytest

from kepler_event_shape_diagnostics import (
    event_shape_measurements, summarize_shape_events, summarize_one
)


def make_series(period=4.45,duration=.16,epoch=1.7,total_days=94,
                depth=.008,step=None,alternating=False):
    t=np.arange(0,total_days,.02043)
    f=1+np.random.default_rng(219).normal(0,.00008,len(t))
    orbit=np.rint((t-epoch)/period).astype(int)
    phase=(t-epoch+.5*period)%period-.5*period
    if step is None:
        transit=np.abs(phase)<duration/2
        if alternating:
            f[transit&(orbit%2==0)]-=depth
            f[transit&(orbit%2!=0)]-=2.8*depth
        else:
            f[transit]-=depth
    else:
        f[t>=epoch]-=step
    return t,f,period,epoch,duration


def test_transit_recovers_to_roughly_same_baseline():
    arr=make_series()
    result,rows=summarize_one(*arr)
    assert result["usable_event_count"]>=15
    assert result["median_signed_local_depth_fraction"]>.006
    assert result["median_abs_persistent_step_fraction"]<.0003
    assert result["median_persistent_step_over_depth_plus_noise"]<.10
    assert 0<=result["positive_depth_event_fraction"]<=1


def test_a_persistent_detector_step_is_not_identical_to_a_transit():
    t,f,p,e,d=make_series(step=.009)
    # A single actual step may produce a positive near-midpoint local depth
    # but post-event baseline never recovers to the pre-step level.
    records=event_shape_measurements(t,f,p,e,d)
    step_record=min(records,key=lambda x:abs(x["predicted_epoch_bkjd"]-e))
    assert step_record["absolute_post_pre_step_fraction"]>.007
    assert step_record["persistent_step_over_depth_plus_noise"]>.55
    assert step_record["n_before"]>=6 and step_record["n_after"]>=6


def test_binary_like_alternating_eclipse_depth_is_detected_by_events():
    data=make_series(alternating=True)
    result,events=summarize_one(*data)
    assert result["usable_event_count"]>=16
    assert result["odd_event_count"]>=7
    assert result["even_event_count"]>=7
    assert result["median_odd_even_depth_difference_fraction"]>.010
    low,high=result["odd_even_descriptive_bootstrap_95pct_interval"]
    assert low>0
    assert result["odd_even_descriptive_separates_zero"] is True


def test_simulated_equal_transit_depth_does_not_forge_systematic_odd_even_gain():
    result,_=summarize_one(*make_series())
    assert abs(result["median_odd_even_depth_difference_fraction"])<.001
    assert result["odd_even_descriptive_separates_zero"] is False


def test_requires_cadences_on_both_sides_no_interpolation():
    t,f,p,e,d=make_series(total_days=40)
    original=event_shape_measurements(t,f,p,e,d)
    center=e+2*p
    # Destroy the entire after-event baseline window for one predicted orbit.
    keep=~((t>=center+1.49*d)&(t<=center+3.51*d))
    shortened=event_shape_measurements(t[keep],f[keep],p,e,d)
    assert len(shortened)==len(original)-1
    assert all(abs(x["predicted_epoch_bkjd"]-center)>.1 for x in shortened)


def test_missing_usable_event_does_not_generate_fake_zero_depth():
    t=np.arange(0,30,.02043)
    f=np.ones_like(t)
    p=4.5;e=1.;d=.15
    # Remove all predicted transit windows, preserving rest of flux.
    phase=(t-e+p/2)%p-p/2
    mask=np.abs(phase)>d
    rows=event_shape_measurements(t[mask],f[mask],p,e,d)
    assert rows==[]
    report=summarize_shape_events(rows)
    assert report["usable_event_count"]==0
    assert report["median_signed_local_depth_fraction"] is None
    assert report["odd_even_descriptive_bootstrap_95pct_interval"] is None


def test_fewer_than_three_events_per_parity_reports_inconclusive():
    res,events=summarize_one(*make_series(total_days=23))
    assert 0<len(events)<8
    assert res["median_odd_even_depth_difference_fraction"] is None
    assert res["odd_even_descriptive_separates_zero"] is None


def test_input_arrays_never_mutated_or_retimed():
    t,f,p,e,d=make_series()
    expected=f.copy()
    ecopy=t.copy()
    summarize_one(t,f,p,e,d)
    assert np.array_equal(f,expected)
    assert np.array_equal(t,ecopy)


def test_physically_invalid_ephemeris_is_rejected():
    t,f,p,e,d=make_series()
    with pytest.raises(ValueError):
        event_shape_measurements(t,f,-p,e,d)
    with pytest.raises(ValueError):
        event_shape_measurements(t[::-1],f[::-1],p,e,d)


def test_short_series_rejected_not_mislabeled():
    t,f,p,e,d=make_series()
    with pytest.raises(ValueError):
        summarize_one(t[:100],f[:100],p,e,d)
