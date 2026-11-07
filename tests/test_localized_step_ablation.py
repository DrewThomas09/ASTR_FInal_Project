"""Offline bookkeeping tests for the fresh, frozen step-mask ablation."""
import json
from pathlib import Path

import pandas as pd
from localized_step_ablation import (
    METHODS,calibrate,make_summary,source_accountability,wilson)


def plan():
    return json.loads(Path("LOCALIZED_STEP_STUDY_FROZEN_2026_11_07.json").read_text())


def test_all_three_methods_have_independent_calibration_thresholds():
    data=[]
    for k,method in enumerate(METHODS):
        for i in range(20):
            data.append({"method":method,"status":"success",
                         "score":100*k+i,"kic":6541920 if i%2 else 10593626})
    results=calibrate(pd.DataFrame(data),plan())
    assert set(results)==set(METHODS)
    assert [results[m]["score_threshold"] for m in METHODS]==[18,118,218]
    assert all(results[m]["n_calibration_stars"]==2 for m in METHODS)


def test_preserve_inaccessible_stars_in_source_denominator():
    sources=source_accountability([
        {"role":"heldout","kic":123,"quarter":8,"status":"source_error",
         "error_type":"HTTPError","error_message":"404"},
        {"role":"heldout","kic":456,"quarter":8,
         "t":list(range(700)),
         "source":{"sha256":"abc","file":"f.fits"},
         "gap_summary":{"n_masked":14}}])
    assert len(sources)==2
    assert sources[0]["status"]=="source_error"
    assert sources[1]["status"]=="analyzed"


def test_untouched_paired_comparison_counts_both_improvements_and_losses():
    rows=[]
    for case,base,step,gap in [("a",True,False,False),
                               ("b",False,True,False),
                               ("c",True,True,True)]:
        for method,recovered in zip(METHODS,(base,gap,step)):
            rows.append({
                "status":"success","case":case,"kic":1,
                "condition":"synthetic_spsd_like_step",
                "depth_ppm":400,"method":method,
                "recovered":recovered,
                "n_true_transit_cadences_masked":1 if method==METHODS[2] else 0,
                "signal_retention_fraction":.90 if method==METHODS[2] else 1.,
                "n_step_detections":1})
    calibration=pd.DataFrame([{"status":"success","method":m,"score":10.,"kic":1}
                               for m in METHODS])
    nulls=pd.DataFrame([{"status":"success","method":m,
                         "condition":"synthetic_spsd_like_step",
                         "score":1.,"kic":1} for m in METHODS])
    thresholds={m:{"score_threshold":5.} for m in METHODS}
    report=make_summary(
        sources=[{"role":"heldout","status":"analyzed","kic":1}],
        calibration=calibration,thresholds=thresholds,nulls=nulls,
        trials=pd.DataFrame(rows),config=plan())
    assert report["paired_results"][0]["n_paired"]==3
    assert report["paired_results"][0]["baseline_only"]==1
    assert report["paired_results"][0]["localized_only"]==1
    assert report["paired_results"][0]["both"]==1
    summary=[r for r in report["per_condition_results"]
             if r["method"]=="localized_step_mask"][0]
    assert summary["n_real_transit_cadences_deleted"]==3


def test_wilson_with_small_n_is_not_confident():
    assert wilson(0,0) is None
    assert wilson(0,4)[1]>.4
    assert wilson(4,4)[0]<.6
