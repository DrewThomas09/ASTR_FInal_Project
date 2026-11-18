#!/usr/bin/env python3
"""Frozen single-star Kepler-69 b Q8 -> Q9 transit-window forecast.

Read only Q8 flux to train period, epoch, duration, then open Q9 original
quality-filtered PDCSAP flux. A positive Q9 test means repeating brightness
dips, NOT a new exoplanet detection or confirmation.

FROZEN PROTOCOL: NOV18_Q8_TO_Q9_FORECAST_PROTOCOL_FROZEN.json
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from blind_transit_benchmark import bls_peak
from real_kepler_lightcurve import fetch_kepler_quarter
from q6_to_q7_blind_ephemeris_validation import phase_shift_null

FROZEN_PATH = Path("NOV18_Q8_TO_Q9_FORECAST_PROTOCOL_FROZEN.json")
REFERENCE_PERIOD = 13.7223682  # POST-ANALYSIS comparison only.


def validate_protocol(cfg):
    if (
        cfg["planned_target"]["kic"] != 8692861
        or cfg["training_quarter"] != 8
        or cfg["heldout_quarter"] != 9
        or cfg["q9_long_cadence_suffix"] != "2011177032512"
    ):
        raise ValueError("Preselected target or quarter changed")
    a = cfg["fixed_bls_search"]
    b = cfg["heldout_check"]
    expected_search = {
        "period_min_days": 1.5, "period_max_days": 20.0,
        "frequency_factor": 5.0, "duration_grid_days": [.09, .15, .24],
        "objective": "snr"
    }
    expected_check = {
        "baseline_inner_duration_multipliers": 1.5,
        "baseline_outer_duration_multipliers": 3.5,
        "minimum_in_transit_cadences_per_event": 3,
        "minimum_baseline_cadences_per_event": 6,
        "minimum_usable_events": 2,
        "positive_event_fraction_at_least": 0.6,
        "phase_shift_control_count": 1000,
        "phase_shift_control_seed": 2026110817,
        "empirical_fraction_at_most": 0.01
    }
    if a != expected_search or b != expected_check:
        raise ValueError("Frozen evaluation thresholds were modified")


def predicted_count_between(tmin, tmax, epoch, period):
    start = int(np.ceil((tmin - epoch) / period))
    end = int(np.floor((tmax - epoch) / period))
    return max(0, end - start + 1)


def run(outdir="results/q8_to_q9_kepler69b"):
    cfg = json.loads(FROZEN_PATH.read_text())
    validate_protocol(cfg)
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    (out / FROZEN_PATH.name).write_bytes(FROZEN_PATH.read_bytes())

    kic = cfg["planned_target"]["kic"]
    search = cfg["fixed_bls_search"]
    print("Opening ORIGINAL Q8 training brightness data", flush=True)
    t8, f8, source8 = fetch_kepler_quarter(f"KIC {kic}", 8)
    peak = bls_peak(
        t8, f8,
        bounds=(search["period_min_days"], search["period_max_days"]),
        frequency_factor=search["frequency_factor"]
    )
    # The fitted epoch, duration, and period are fixed before any Q9 flux is read.
    period = float(peak["period_days"])
    epoch = float(peak["transit_time_days"])
    duration = float(peak["duration_days"])
    print(
        "FROZEN Q8 FIT:",
        json.dumps({"period_days": period, "epoch_bkjd": epoch,
                    "duration_days": duration, "score": peak["score"]}),
        flush=True
    )
    if not (1.5 <= period <= 20 and 0 < duration < period / 3):
        raise ValueError("Unphysical Q8 best fit")

    print("Now opening ORIGINAL Q9 held-out brightness data", flush=True)
    t9, f9, source9 = fetch_kepler_quarter(f"KIC {kic}", 9)

    settings = cfg["heldout_check"]
    q7_style = {
        "baseline_inner_window_duration_multipliers": settings["baseline_inner_duration_multipliers"],
        "baseline_outer_window_duration_multipliers": settings["baseline_outer_duration_multipliers"],
        "min_in_transit_cadences_per_event": settings["minimum_in_transit_cadences_per_event"],
        "min_baseline_cadences_per_event": settings["minimum_baseline_cadences_per_event"],
        "min_expected_transit_events_in_Q7": settings["minimum_usable_events"],
        "phase_null_random_seed": settings["phase_shift_control_seed"],
        "phase_null_shift_count": settings["phase_shift_control_count"],
        "positive_event_depth_fraction_at_least": settings["positive_event_fraction_at_least"]
    }
    measures, events, nulls = phase_shift_null(
        t9, f9, period, epoch, duration, q7_style, kic
    )
    # This is only a within-star phase comparison; it is not a calibrated
    # telescope-wide false-alarm rate or proof of a planetary origin.
    fraction = measures["relative_phase_shift_fraction"]
    pass_test = bool(
        len(events) >= settings["minimum_usable_events"]
        and fraction is not None
        and fraction <= settings["empirical_fraction_at_most"]
        and measures["positive_event_fraction"] >= settings["positive_event_fraction_at_least"]
    )
    if pass_test != bool(measures["predictive_evidence"]):
        raise AssertionError("Held-out rule implementation disagrees with predeclared check")

    total_centers = predicted_count_between(
        float(np.min(t9)), float(np.max(t9)), epoch, period
    )
    report = {
        "study": "Kepler-69b Q8-only BLS predicts original untouched Q9 brightness",
        "scope": "Single known Kepler planet host; cannot infer survey performance or planet identity",
        "source_q8": source8,
        "source_q9": source9,
        "train_q8_fixed": peak,
        "post_hoc_reference_period_days": REFERENCE_PERIOD,
        "post_hoc_period_difference_minutes_per_orbit": abs(period-REFERENCE_PERIOD)*1440,
        "matches_prior_q8_report_period_to_0p02_days": abs(period-13.7133429855) <= .02,
        "q9_predicted_centers_within_observing_time_span": total_centers,
        "q9_usable_predicted_event_windows": len(events),
        "q9_unusable_predicted_centers": max(0, total_centers-len(events)),
        "q9_positive_event_windows": sum(bool(e["positive_local_depth"]) for e in events),
        "q9_mean_local_depth_ppm": measures["mean_predicted_event_depth"]*1e6
             if measures["mean_predicted_event_depth"] is not None else None,
        "q9_positive_event_fraction": measures["positive_event_fraction"],
        "q9_phase_control_trials": measures["phase_shift_null_trials"],
        "q9_phase_fraction": fraction,
        "q9_frozen_rule_pass": pass_test,
        "limitations": [
            "Q9 cannot be fitted or phase-shifted to rescue a negative result",
            "Q8 fit was developed on a previously studied known planet, so this is not blind discovery",
            "Even repeatable predicted dips do not identify whether the physical cause is a planet",
            "One star does not measure general success rate",
            "Phase-shift controls are internal comparators, not a mission-wide false alarm rate",
            "Period fit may shift with a different Astropy version; note reproducibility check"
        ]
    }
    (out / "summary.json").write_text(json.dumps(report, indent=2, default=float)+"\n")
    pd.DataFrame(events).to_csv(out / "q9_predicted_event_windows.csv", index=False)
    pd.DataFrame(nulls).to_csv(out / "q9_phase_shift_comparisons.csv", index=False)

    fig, ax = plt.subplots(2, 1, figsize=(8.5, 5.5), sharex=True)
    for axis, time, flux, label in (
        (ax[0], t8, f8, "Training: Quarter 8"),
        (ax[1], t9, f9, "Untouched test: Quarter 9"),
    ):
        phase = (time - epoch + period/2) % period - period/2
        axis.plot(phase, flux, ".", markersize=1.5, alpha=.5, color="black")
        axis.axvline(0, color="tab:red", linestyle="--", linewidth=1)
        axis.set(xlim=(-.7, .7), ylabel="Relative brightness", title=label)
        axis.tick_params(labelsize=8)
    ax[1].set_xlabel("Days relative to Quarter-8 predicted mid-transit")
    fig.suptitle("Kepler-69 b: one frozen clock tested on later NASA measurements")
    fig.tight_layout()
    fig.savefig(out / "kepler69b_q8_q9_frozen_phase.png", dpi=170)
    plt.close(fig)

    print("FROZEN_Q8_TO_Q9_RESULT_JSON_START", flush=True)
    print(json.dumps(report, indent=2), flush=True)
    print("FROZEN_Q8_TO_Q9_RESULT_JSON_END", flush=True)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/q8_to_q9_kepler69b")
    args = parser.parse_args()
    run(args.out)
