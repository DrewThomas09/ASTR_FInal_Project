"""Synthetic baseline controls, NOT original ground astronomical measurements."""
import numpy as np
import pytest
from exofop_two_original_ground_neb_baseline_robustness import one_aperture_robustness


def times():
    return np.arange(2459405.70,2459405.89,.002)


def test_three_baselines_identify_fixed_strong_eclipse_without_retiming():
    t=times()
    y=1.0+.1*(t-np.median(t))
    mask=(t>=2459405.7654)&(t<=2459405.8325)
    y[mask]-=.15
    z=one_aperture_robustness(t,y,2459405.7654,2459405.8325)
    assert z["status"]=="actual_original_ground_timeseries_reanalyzed"
    assert z["all_three_fixed_baseline_methods_show_positive_dip"]
    assert 145<z["robust_theil_sen_outside_only_detrended_depth_ppt"]<155


def test_no_false_robust_positive_if_only_baseline_drift():
    t=times()
    y=1.0+2*(t-2459405.70)
    z=one_aperture_robustness(t,y,2459405.7654,2459405.8325)
    assert abs(z["robust_theil_sen_outside_only_detrended_depth_ppt"])<1e-6
    assert z["all_three_fixed_baseline_methods_show_positive_dip"] is False


def test_original_missing_cadence_prepost_no_unsupported_result():
    t=np.arange(2459405.70,2459405.831,.002)
    y=np.ones(len(t))
    z=one_aperture_robustness(t,y,2459405.7654,2459405.8325)
    assert z["status"]=="not_evaluable_original_ground_flux_coverage"
