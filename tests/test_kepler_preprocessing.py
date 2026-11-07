"""Offline invariants for artifact-neighborhood BLS test.

These are engineering checks; they do not establish an astronomical
completeness gain or a statistically calibrated true false-alarm rate.
"""
import numpy as np
import pytest

from kepler_preprocessing import (
    gap_edge_mask, injection_model, inject_before_detrending,
    normalize_flux, proxy_inverted_rolled_flux, injected_signal_retention,
)


def test_no_gaps_mask_is_identity():
    t = np.arange(0, 40, .02)
    keep, report = gap_edge_mask(t)
    assert keep.all()
    assert report["n_long_gaps"] == 0
    assert report["n_masked"] == 0


def test_gap_only_masks_cadences_close_to_its_edges():
    t = np.r_[np.arange(0, 10, .02), np.arange(11, 21, .02)]
    keep, report = gap_edge_mask(t)
    assert report["n_long_gaps"] == 1
    assert report["n_masked"] > 0
    assert keep[t < 9].all()
    assert keep[t > 12].all()
    assert not keep[np.argmin(np.abs(t-9.98))]
    assert not keep[np.argmin(np.abs(t-11.0))]


def test_invalid_unsorted_times_rejected():
    with pytest.raises(ValueError,match="ascending"):
        gap_edge_mask([0, 2, 1],minimum_remaining=2)


def test_gap_mask_does_not_use_planet_truth():
    t = np.r_[np.arange(0, 5, .02),np.arange(6, 11, .02)]
    original, _ = gap_edge_mask(t, minimum_remaining=400)
    copy, _ = gap_edge_mask(t.copy(), minimum_remaining=400)
    assert np.array_equal(original,copy)


def test_injection_is_before_detrending_and_signal_kept_when_no_gaps():
    t = np.arange(0, 30, .02043)
    raw = np.full(len(t), 25000.)
    injection, inside = inject_before_detrending(
        t,raw,period_days=4.,epoch_days=.5,depth_ppm=1000,
        duration_days=.16)
    assert np.all(injection[~inside] == raw[~inside])
    assert np.all(injection[inside] == raw[inside] * .999)
    uninj_norm = normalize_flux(raw)
    inj_norm = normalize_flux(injection)
    mask,_ = gap_edge_mask(t)
    assert injected_signal_retention(uninj_norm,inj_norm,inside,mask)==pytest.approx(1.0)


def test_injected_signal_removed_near_gap_is_accounted_for():
    t = np.r_[np.arange(0, 5, .02),np.arange(6, 11, .02)]
    base = np.full(len(t),1000.)
    injected,inside = inject_before_detrending(
        t,base,period_days=2.,epoch_days=4.95,
        depth_ppm=1200.,duration_days=.18)
    keep, _ = gap_edge_mask(t, minimum_remaining=400)
    loss = injected_signal_retention(normalize_flux(base),
                                     normalize_flux(injected),inside,keep)
    assert 0 <= loss < 1


def test_inverted_rolled_null_is_reproducible_and_not_identical():
    t = np.arange(600)
    x = 1 + .001 * np.sin(t/13)
    null1,shift1 = proxy_inverted_rolled_flux(x,43)
    null2,shift2 = proxy_inverted_rolled_flux(x,43)
    assert shift1==shift2
    assert np.allclose(null1,null2)
    assert not np.allclose(null1,x)
    assert np.isclose(np.median(null1),1.0,atol=.0003)


def test_unphysical_injection_is_rejected():
    t=np.arange(500)*.02
    with pytest.raises(ValueError):
        injection_model(t,4.,1.,500.,3.)
