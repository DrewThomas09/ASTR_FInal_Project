"""Offline checks of matched-star/threshold logic for the new BLS ablation."""
import pandas as pd
import pytest
from preprocessing_ablation import wilson_interval,calibrate_thresholds,summaries


def toy_plan():
    return {
       "decision":{"target_calibration_proxy_flag_fraction":.1},
       "null_proxy":{"warning":"Constructed proxy; not real FAP"}}


def test_thresholds_are_fit_per_method_on_calibration_controls_only():
    rows=[]
    for method,offset in [("standard_bls",0),
                          ("gap_edge_mask_bls",100)]:
        for i in range(20):
            rows.append({"kic":1,"method":method,"status":"success",
                         "split":"calibration","peak_score":offset+i})
    df=pd.DataFrame(rows)
    out=calibrate_thresholds(df,toy_plan())
    assert out["standard_bls"]["threshold"]==18
    assert out["gap_edge_mask_bls"]["threshold"]==118
    assert out["standard_bls"]["n_calibration_hosts"]==1
    assert out["gap_edge_mask_bls"]["n_control"]==20


def test_too_few_controls_fails_before_test_looks_at_data():
    df=pd.DataFrame([{"method":"standard_bls","status":"success",
                      "peak_score":i,"kic":1} for i in range(5)])
    with pytest.raises(RuntimeError):
        calibrate_thresholds(df,toy_plan())


def test_paired_improvement_and_losses_both_counted():
    rows=[
      {"case":"a","method":"standard_bls","status":"success",
       "depth_ppm":400,"recovered":True,
       "injected_differential_flux_retention":1.0,
       "n_injected_points_masked":0},
      {"case":"a","method":"gap_edge_mask_bls","status":"success",
       "depth_ppm":400,"recovered":False,
       "injected_differential_flux_retention":.7,
       "n_injected_points_masked":2},
      {"case":"b","method":"standard_bls","status":"success",
       "depth_ppm":400,"recovered":False,
       "injected_differential_flux_retention":1.0,
       "n_injected_points_masked":0},
      {"case":"b","method":"gap_edge_mask_bls","status":"success",
       "depth_ppm":400,"recovered":True,
       "injected_differential_flux_retention":1.0,
       "n_injected_points_masked":0}]
    nulls=pd.DataFrame([
       {"method":"standard_bls","status":"success","peak_score":1},
       {"method":"gap_edge_mask_bls","status":"success","peak_score":2}])
    thr={"standard_bls":{"threshold":1.5},
         "gap_edge_mask_bls":{"threshold":1.5}}
    out=summaries(pd.DataFrame(rows),nulls,toy_plan(),thr,[])
    assert out["paired_outcomes"]["n_paired"]==2
    assert out["paired_outcomes"]["baseline_only"]==1
    assert out["paired_outcomes"]["gap_mask_only"]==1
    assert out["null_flags_by_method"][0]["n_proxy"]==1


def test_wilson_intervals_bounded():
    assert wilson_interval(0,0) is None
    assert wilson_interval(0,10)[0]==0
    assert wilson_interval(10,10)[1]==1
