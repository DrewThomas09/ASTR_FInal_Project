"""Independent real Kepler light-curve check + injection into observed stellar variability.

NO NEW PLANET DISCOVERY IS CLAIMED. Uses NASA MAST public Kepler FITS via Lightkurve.
Published reference period of Kepler-69b is used ONLY after blind period fitting.
Additional control star may contain unrecognized signals; an un-injected control is
NOT proof of a planet-free star.
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
from transit_consistency import individual_transit_checks

KNOWN_REFERENCE_PERIOD_DAYS = 13.721772
KNOWN_SYSTEM = "Kepler-69"
KNOWN_QUARTER = 8
CONTROL_SYSTEM = "KIC 2436365"
CONTROL_QUARTER = 2
INJECTION_PERIOD_RANGE_DAYS = (2.1, 9.8)


def fetch_kepler_quarter(target, quarter):
    """Public MAST archive; downloads one default-quality-masked Kepler quarter."""
    import lightkurve as lk
    found = lk.search_lightcurve(target, author="Kepler",
                                 cadence="long", quarter=quarter)
    if len(found) < 1:
        raise RuntimeError("MAST returned no Kepler light curves for target/quarter")
    curve = found.download(quality_bitmask="default")
    if curve is None:
        raise RuntimeError("MAST download returned no light curve")
    clean = curve.remove_nans().normalize()
    # 301 long-cadence samples ~= six days; suppress slow trends.
    # This processing is fixed for both the target example and injection test.
    flat = clean.flatten(window_length=301, break_tolerance=5)
    t = np.asarray(flat.time.value, dtype=float)
    f = np.asarray(flat.flux.value, dtype=float)
    valid = np.isfinite(t) & np.isfinite(f)
    t, f = t[valid], f[valid]
    if len(t) < 500:
        raise RuntimeError("Insufficient valid time series after masking and flattening")
    return t, f, {
        "target": str(target), "requested_quarter": int(quarter),
        "cadences_after_quality_mask": int(len(t)),
        "time_start_bkjd": float(t.min()),
        "time_end_bkjd": float(t.max()),
        "source": "public NASA MAST Kepler PDC-SAP, default quality masking",
        "processing": "remove_nans, normalize, flatten(301 samples)",
    }


def insert_known_transit(t, f, period, epoch, depth_ppm, duration_days):
    """Inject a known, box-shaped transit AFTER fixed detrending."""
    if period <= 0 or depth_ppm < 0 or not 0 < duration_days < period / 3:
        raise ValueError("Unphysical injection parameters")
    t, f = np.asarray(t, float), np.asarray(f, float)
    if t.shape != f.shape:
        raise ValueError("Time and flux must have matching shapes")
    phi = (t - epoch + period / 2) % period - period / 2
    injected = f.copy()
    inside = np.abs(phi) < duration_days / 2
    injected[inside] -= depth_ppm / 1_000_000
    return injected, inside


def known_planet_example(output):
    t, f, source = fetch_kepler_quarter(KNOWN_SYSTEM, KNOWN_QUARTER)
    # The search does NOT receive the published 13.72-day reference period.
    found = bls_peak(t, f, bounds=(5., 18.))
    diagnostics, event_table = individual_transit_checks(
        t, f, found["period_days"],
        found["transit_time_days"], found["duration_days"])
    difference = abs(found["period_days"] - KNOWN_REFERENCE_PERIOD_DAYS)
    result = {
        "dataset": source,
        "method": "Astropy BLS with 5–18 day period grid",
        "period_range_predeclared_days": [5., 18.],
        "published_period_days": KNOWN_REFERENCE_PERIOD_DAYS,
        "period_absolute_error_days": float(difference),
        "period_relative_error_pct": float(100 * difference / KNOWN_REFERENCE_PERIOD_DAYS),
        "fitted_bls": found,
        "per_event_diagnostics": diagnostics,
        "limitation": "Single published planet and one quarter are not survey-wide proof of detection accuracy",
    }
    out = Path(output); out.mkdir(parents=True, exist_ok=True)
    (out/"kepler69b_known_system.json").write_text(json.dumps(result, indent=2))
    event_table.to_csv(out/"kepler69b_event_diagnostics.csv", index=False)
    period = found["period_days"]; center = found["transit_time_days"]
    phase = (t - center + period / 2) % period - period / 2
    fig, axes = plt.subplots(2, 1, figsize=(9, 6))
    axes[0].plot(t, f, "k.", ms=1)
    axes[0].set(xlabel="Time (BKJD)", ylabel="Normalized flux",
                title="Kepler-69: one real quarter (quality-masked, flattened)")
    axes[1].plot(phase, f, "k.", ms=1)
    axes[1].set(xlabel="Folded phase (days)", ylabel="Normalized flux",
                title=f"Blind BLS fitted period: {period:.4f} days")
    axes[1].set_xlim(-.65, .65)
    fig.tight_layout()
    fig.savefig(out/"kepler69b_folded.png", dpi=160)
    plt.close(fig)
    return result


def inject_into_real_noise(output, trials=3, seed=12600):
    """Known synthetic transits overlaid on ACTUAL Kepler stellar light curve.

    Never interpret the unmodified star as verified planet-free.
    """
    if trials < 1:
        raise ValueError("Require at least one realization")
    t, f, source = fetch_kepler_quarter(CONTROL_SYSTEM, CONTROL_QUARTER)
    rng = np.random.default_rng(seed)
    records = []
    for depth in [500., 1500., 4000.]:
        for i in range(trials):
            period = float(rng.uniform(*INJECTION_PERIOD_RANGE_DAYS))
            epoch = float(t.min() + rng.uniform(0, period))
            duration = float(rng.uniform(.11, .19))
            test_flux, in_transit = insert_known_transit(
                t, f, period, epoch, depth, duration)
            peak = bls_peak(t, test_flux, bounds=(1.5, 12.))
            exact = bool(abs(peak["period_days"]-period)/period < .02)
            records.append({
                "source":"REAL Kepler flux + SYNTHETIC injected planet",
                "target":CONTROL_SYSTEM, "quarter":CONTROL_QUARTER,
                "depth_ppm":depth, "trial":i, "period_injected_days":period,
                "period_recovered_days":peak["period_days"],
                "period_recovered_within_2_percent":exact,
                "injected_points":int(in_transit.sum()),
                "peak_score_uncalibrated":peak["score"],
            })
    out = Path(output);out.mkdir(parents=True,exist_ok=True)
    df = pd.DataFrame(records)
    df.to_csv(out/"real_noise_injection_trials.csv",index=False)
    summary = df.groupby("depth_ppm",as_index=False).agg(
        n=("period_recovered_within_2_percent","size"),
        n_recovered=("period_recovered_within_2_percent","sum"))
    summary["recovery_fraction"] = summary.n_recovered/summary.n
    summary.to_csv(out/"real_noise_injection_summary.csv",index=False)
    fig, ax = plt.subplots(figsize=(7,3.8))
    ax.bar(summary.depth_ppm.astype(str),summary.recovery_fraction)
    ax.set(xlabel="Synthetic injected transit depth (ppm)",
           ylabel="Correct period recovery fraction",
           ylim=(0,1.05),
           title="Known injections in real Kepler stellar variability")
    fig.tight_layout()
    fig.savefig(out/"real_noise_injection.png",dpi=160)
    plt.close(fig)
    return {
        "data":source,
        "injection_count":int(len(df)),
        "results":json.loads(summary.to_json(orient="records")),
        "limitation":"Real observed noise, simulated box transits; baseline star not proven planet-free",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results/real_kepler")
    parser.add_argument("--trials", type=int, default=3)
    a = parser.parse_args()
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    known=known_planet_example(out)
    injected=inject_into_real_noise(out,trials=a.trials)
    report={"known_planet":known,"injection_into_real_noise":injected,
            "study_scope":"Feasibility demonstration, not NASA mission completeness"}
    (out/"real_kepler_summary.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
