#!/usr/bin/env python3
"""Test the unchanged original Q8 transit clock on Q10 and Q11 NASA data."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

from blind_transit_benchmark import bls_peak
from real_kepler_lightcurve import fetch_kepler_quarter
from q6_to_q7_blind_ephemeris_validation import phase_shift_null
from nov18_kepler69b_q8_to_q9 import validate_protocol, predicted_count_between

PLAN = Path("NOV18_Q8_TO_Q10_Q11_LONGER_FORECAST_FROZEN.json")
EARLIER = Path("NOV18_Q8_TO_Q9_FORECAST_PROTOCOL_FROZEN.json")
REFERENCE_PERIOD = 13.7223682


def run(outdir="results/q8_to_q10_q11_kepler69b"):
    plan = json.loads(PLAN.read_text())
    q9cfg = json.loads(EARLIER.read_text())
    validate_protocol(q9cfg)
    if (plan["preselected_target_kic"] != 8692861 or
        plan["training_quarter"] != 8 or
        plan["phase_control_seed_base"] != 2026110817 or
        plan["phase_control_star_key_formula"] != "8692861 + quarter*100000" or
        plan["test_quarters"] != [
            {"quarter":10,"official_filename_suffix":"2011271113734"},
            {"quarter":11,"official_filename_suffix":"2012004120508"}]):
        raise ValueError("Later-quarter target, periods, or controls changed")
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    (out / PLAN.name).write_bytes(PLAN.read_bytes())
    (out / EARLIER.name).write_bytes(EARLIER.read_bytes())
    print("Train on original Q8 alone; later observations NOT read yet", flush=True)
    t8, f8, meta8 = fetch_kepler_quarter("KIC 8692861", 8)
    search = q9cfg["fixed_bls_search"]
    fit = bls_peak(t8, f8, bounds=(search["period_min_days"],
                                   search["period_max_days"]),
                   frequency_factor=search["frequency_factor"])
    if abs(fit["period_days"]-13.7133429855)>0.02:
        raise RuntimeError("Q8 model not consistent with prior locked analysis")
    print("Original frozen Q8 period/epoch/duration:", json.dumps(fit), flush=True)
    settings = q9cfg["heldout_check"]
    fixed = {
        "baseline_inner_window_duration_multipliers": settings["baseline_inner_duration_multipliers"],
        "baseline_outer_window_duration_multipliers": settings["baseline_outer_duration_multipliers"],
        "min_in_transit_cadences_per_event": settings["minimum_in_transit_cadences_per_event"],
        "min_baseline_cadences_per_event": settings["minimum_baseline_cadences_per_event"],
        "min_expected_transit_events_in_Q7": settings["minimum_usable_events"],
        "phase_null_random_seed": plan["phase_control_seed_base"],
        "phase_null_shift_count": settings["phase_shift_control_count"],
        "positive_event_depth_fraction_at_least": settings["positive_event_fraction_at_least"]
    }
    rows = []
    all_events = []
    all_null = []
    for planned in plan["test_quarters"]:
        q = planned["quarter"]
        print("Opening held-out NASA Kepler Q"+str(q), flush=True)
        row={"quarter":q, "status":"unavailable_or_error"}
        try:
            times, flux, meta = fetch_kepler_quarter("KIC 8692861", q)
            measurements, events, nulls = phase_shift_null(
                times, flux, fit["period_days"], fit["transit_time_days"],
                fit["duration_days"], fixed, 8692861 + q*100000
            )
            relative = measurements["relative_phase_shift_fraction"]
            score = bool(len(events)>=settings["minimum_usable_events"]
                         and relative is not None
                         and relative <= settings["empirical_fraction_at_most"]
                         and measurements["positive_event_fraction"] >=
                             settings["positive_event_fraction_at_least"])
            if score != bool(measurements["predictive_evidence"]):
                raise AssertionError("Held-out rule evaluation differs from existing version")
            centers = predicted_count_between(float(times.min()),float(times.max()),
                                               fit["transit_time_days"],fit["period_days"])
            row.update({
                "status": "analyzed_original_NASA_FITS",
                "n_quality_filtered_cadences": int(len(times)),
                "data_start_bkjd": float(times.min()),
                "data_end_bkjd": float(times.max()),
                "file": meta["file"], "sha256": meta["sha256"],
                "predicted_centers_in_time_span": centers,
                "usable_event_windows": int(len(events)),
                "unusable_center_windows": max(0,int(centers)-len(events)),
                "positive_depth_windows": int(sum(e["positive_local_depth"] for e in events)),
                "mean_depth_ppm": (measurements["mean_predicted_event_depth"]*1e6
                                   if measurements["mean_predicted_event_depth"] is not None else None),
                "positive_depth_fraction": measurements["positive_event_fraction"],
                "within_star_alternative_phase_count": int(measurements["phase_shift_null_trials"]),
                "within_star_phase_fraction": relative,
                "passed_frozen_rule": score
            })
            for e in events:
                all_events.append({"quarter":q, **e})
            for e in nulls:
                all_null.append({"quarter":q, **e})
            print("Q"+str(q)+" outcome: "+json.dumps(row), flush=True)
        except Exception as error:
            row["error_class"]=type(error).__name__
            row["error"]=str(error)[:250]
            print("Q"+str(q)+" unavailable/error: "+str(error)[:200], flush=True)
        rows.append(row)
    result={
        "study":"Same Q8 model, predictions carried unchanged into Q10 and Q11",
        "q8_reference_source_sha256":meta8["sha256"],
        "q8_fixed_model":fit,
        "later_quarters":rows,
        "limitations":"One previously known planet host; repeating dips are not independently confirmed planets. Phase fractions are within-star comparisons, not mission false alarm probabilities. Both quarters were selected before inspecting either quarter's brightness.",
    }
    (out/"summary.json").write_text(json.dumps(result,indent=2)+"\n")
    pd.DataFrame(rows).to_csv(out/"q10_q11_all_results.csv",index=False)
    pd.DataFrame(all_events).to_csv(out/"q10_q11_events.csv",index=False)
    pd.DataFrame(all_null).to_csv(out/"q10_q11_phase_controls.csv",index=False)
    print("FROZEN_Q8_Q10_Q11_SUMMARY_START",flush=True)
    print(json.dumps(result, indent=2),flush=True)
    print("FROZEN_Q8_Q10_Q11_SUMMARY_END",flush=True)
    return result

if __name__=="__main__":
    run()
