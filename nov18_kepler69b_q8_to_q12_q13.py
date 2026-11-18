#!/usr/bin/env python3
"""Frozen Q8-only forecast evaluation in even later NASA Kepler quarters."""
import json
from pathlib import Path

import pandas as pd
import numpy as np

from blind_transit_benchmark import bls_peak
from real_kepler_lightcurve import fetch_kepler_quarter
from q6_to_q7_blind_ephemeris_validation import phase_shift_null
from nov18_kepler69b_q8_to_q9 import validate_protocol, predicted_count_between

def run():
    plan_file=Path("NOV18_Q8_TO_Q12_Q13_FROZEN.json")
    plan=json.loads(plan_file.read_text())
    q9_file=Path("NOV18_Q8_TO_Q9_FORECAST_PROTOCOL_FROZEN.json")
    cfg=json.loads(q9_file.read_text())
    validate_protocol(cfg)
    if plan["kic"]!=8692861 or plan["fit_quarter"]!=8 or plan["test_quarters"]!=[
        {"quarter":12,"suffix":"2012088054726"},
        {"quarter":13,"suffix":"2012179063303"}]:
        raise ValueError("Frozen future-quarter sample changed")
    out=Path("results/q8_to_q12_q13_kepler69b");out.mkdir(parents=True,exist_ok=True)
    (out/plan_file.name).write_bytes(plan_file.read_bytes())
    (out/q9_file.name).write_bytes(q9_file.read_bytes())
    t8,f8,s8=fetch_kepler_quarter("KIC 8692861",8)
    v=cfg["fixed_bls_search"]
    fit=bls_peak(t8,f8,bounds=(v["period_min_days"],v["period_max_days"]),
                 frequency_factor=v["frequency_factor"])
    print("Q8 FROZEN TRAINING: "+json.dumps(fit),flush=True)
    if abs(fit["period_days"]-plan["prior_Q8_period_days"])>.02:
        raise RuntimeError("Previous fixed Q8 model not reproduced")
    c=cfg["heldout_check"]
    settings={
        "baseline_inner_window_duration_multipliers":c["baseline_inner_duration_multipliers"],
        "baseline_outer_window_duration_multipliers":c["baseline_outer_duration_multipliers"],
        "min_in_transit_cadences_per_event":c["minimum_in_transit_cadences_per_event"],
        "min_baseline_cadences_per_event":c["minimum_baseline_cadences_per_event"],
        "min_expected_transit_events_in_Q7":c["minimum_usable_events"],
        "phase_null_random_seed":plan["phase_control_seed"],
        "phase_null_shift_count":c["phase_shift_control_count"],
        "positive_event_depth_fraction_at_least":c["positive_event_fraction_at_least"]
    }
    rows=[]; all_events=[]
    for test in plan["test_quarters"]:
        q=test["quarter"]
        row={"quarter":q,"status":"unavailable"}
        try:
            time,flux,info=fetch_kepler_quarter("KIC 8692861",q)
            measures,events,null=phase_shift_null(
                time,flux,fit["period_days"],fit["transit_time_days"],
                fit["duration_days"],settings,8692861 + q*100000)
            frac=measures["relative_phase_shift_fraction"]
            passed=bool(len(events)>=c["minimum_usable_events"] and
                frac is not None and frac<=c["empirical_fraction_at_most"] and
                measures["positive_event_fraction"]>=c["positive_event_fraction_at_least"])
            assert passed == bool(measures["predictive_evidence"])
            centers=predicted_count_between(float(time.min()),float(time.max()),
                                            fit["transit_time_days"],fit["period_days"])
            row.update({
                "status":"analyzed_original_NASA_FITS",
                "sha256":info["sha256"], "file":info["file"],
                "n_original_quality_filtered_cadences":len(time),
                "time_start_bkjd":float(time.min()),"time_end_bkjd":float(time.max()),
                "predicted_centers_in_quarter":centers,
                "usable_windows":len(events),
                "unusable_windows":max(0,centers-len(events)),
                "positive_windows":sum(int(e["positive_local_depth"]) for e in events),
                "mean_local_depth_ppm":measures["mean_predicted_event_depth"]*1e6
                    if measures["mean_predicted_event_depth"] is not None else None,
                "positive_window_fraction":measures["positive_event_fraction"],
                "alternative_phases":measures["phase_shift_null_trials"],
                "within_star_phase_fraction":frac,
                "passes_frozen_rule":passed
            })
            all_events.extend([{"quarter":q,**e} for e in events])
        except Exception as e:
            row["error"]=f"{type(e).__name__}: {str(e)[:220]}"
        rows.append(row)
        print("Q"+str(q)+" "+json.dumps(row),flush=True)
    report={
        "frozen_Q8_model":fit, "Q8_source_sha256":s8["sha256"],
        "predeclared_later_quarter_results":rows,
        "limits":"One known Kepler planet host; no re-fitting in Q12/Q13; within-star phase fractions are not mission-wide false alarm rates; negative results are retained"
    }
    (out/"summary.json").write_text(json.dumps(report,indent=2)+"\n")
    pd.DataFrame(rows).to_csv(out/"all_predeclared_Q12_Q13_results.csv",index=False)
    pd.DataFrame(all_events).to_csv(out/"individual_event_windows.csv",index=False)
    print("FROZEN_Q12_Q13_JSON_START")
    print(json.dumps(report,indent=2))
    print("FROZEN_Q12_Q13_JSON_END")
    return report

if __name__=="__main__":
    run()
