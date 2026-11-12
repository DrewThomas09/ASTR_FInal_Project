"""Synthetic engineering tests only, not observed ground eclipses."""
import numpy as np
import pandas as pd
import pytest

from exofop_two_ground_NEBS_original_AIJ_fixed_window_depth import (
    original_ephemeris_window,depth_from_true_original_aperture,
    source_aij_timeseries_bytes,PRE_COMMITTED_OTHER_APERTURES
)

def report():
    return "Predicted ingress time: 1.0212\nPredicted egress time: 1.1277\n"


def ground_times():
    return np.arange(2460006.970,2460007.144,.001)


def test_absolute_ingress_recovered_by_nearest_integer_day_from_timestamps_not_flux():
    timing=original_ephemeris_window(report(),ground_times())
    assert timing["prescribed_full_BJD_TDB_ingress"]==pytest.approx(2460007.0212)
    assert timing["prescribed_full_BJD_TDB_egress"]==pytest.approx(2460007.1277)
    assert timing["no_photometry_shift_or_fitted_transit_epoch"] is True


def test_original_Eclipse_depth_detects_true_fixed_window_and_ordinary_pre_post():
    t=ground_times()
    y=np.ones(len(t))
    y[(t>=2460007.0212)&(t<=2460007.1277)]-=.035
    res=depth_from_true_original_aperture(t,y,2460007.0212,2460007.1277,boot=800,seed=123)
    assert res["status"]=="measured_original_ground_AIJ_aperture"
    assert res["measured_depth_ppt"]==pytest.approx(35)
    assert res["descriptive_fixed_four_cadence_block_bootstrap_95pct_ppt"][0]>32


def test_no_assumed_depth_if_no_valid_prepost_original_observations():
    t=np.arange(2459405.72,2459405.831,.002)
    y=np.ones(len(t))
    res=depth_from_true_original_aperture(t,y,2459405.7654,2459405.8325,boot=100)
    assert res["status"]=="not_evaluable_original_ground_time_or_aperture_cadence"
    assert res["measured_depth_ppt"] is None


def test_wrong_report_geometry_or_missing_sky_time_fail_closed():
    with pytest.raises(ValueError,match="no unique prescribed"):
        original_ephemeris_window("Predicted ingress time: 1.0212",ground_times())
    with pytest.raises(ValueError,match="not observed"):
        original_ephemeris_window("Predicted ingress time: 1.7\nPredicted egress time: 1.8",ground_times())


def test_real_AIJ_aperture_requires_original_BJD_and_all_precommitted_controls():
    cols=["BJD_TDB","rel_flux_T1","rel_flux_T6"]+[f"rel_flux_{k}" for k in PRE_COMMITTED_OTHER_APERTURES]
    df=pd.DataFrame([{c:2460007+i*.001 if c=="BJD_TDB" else .9 for c in cols} for i in range(50)])
    b=df.to_csv(index=False,sep="\t").encode()
    x=source_aij_timeseries_bytes(b,"T6")
    assert len(x)==50
    assert "rel_flux_T6" in x
    df=df.drop(columns="rel_flux_T4")
    with pytest.raises(ValueError,match="lacks source aperture"):
        source_aij_timeseries_bytes(df.to_csv(index=False,sep="\t").encode(),"T6")
