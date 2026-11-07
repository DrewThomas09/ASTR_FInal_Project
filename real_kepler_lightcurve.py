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

KNOWN_REFERENCE_PERIOD_DAYS = 13.7223682
KNOWN_SYSTEM = "KIC 8692861"
KNOWN_QUARTER = 8
CONTROL_SYSTEM = "KIC 2436365"
CONTROL_QUARTER = 2
INJECTION_PERIOD_RANGE_DAYS = (2.1, 9.8)


def fetch_kepler_quarter(target, quarter):
    """Download the known, archived quarterly FITS directly, without a MAST search.

    MAST archive files follow https://archive.stsci.edu/pub/kepler/lightcurves/.
    Files can also be supplied manually in data/kepler_fits to avoid network requests.
    """
    import hashlib
    import time
    import requests
    from astropy.io import fits
    from scipy.ndimage import median_filter

    numbers = "".join(ch for ch in str(target) if ch.isdigit())
    if not numbers:
        raise ValueError("Kepler target must contain a numeric KIC ID")
    starid = f"{int(numbers):09d}"
    qstamp = {2: "2009259160929", 8: "2011073133259"}.get(quarter)
    if qstamp is None:
        raise ValueError("Quarter not in deliberately small predeclared sample")
    filename = f"kplr{starid}-{qstamp}_llc.fits"
    url = (
        f"https://archive.stsci.edu/pub/kepler/lightcurves/"
        f"{starid[:4]}/{starid}/{filename}"
    )
    cache = Path("data/kepler_fits") / filename
    cache.parent.mkdir(parents=True, exist_ok=True)
    if not cache.is_file():
        part = cache.with_suffix(".part")
        start_time = time.monotonic()
        try:
            with requests.get(url, stream=True, timeout=(12, 20),
                              headers={"User-Agent": "ASTR12600-kepler-study/1.0"}) as response:
                response.raise_for_status()
                size = 0
                with part.open("wb") as handle:
                    for chunk in response.iter_content(chunk_size=262144):
                        if not chunk:
                            continue
                        size += len(chunk)
                        if size > 30_000_000 or time.monotonic()-start_time > 75:
                            raise TimeoutError("Archived FITS exceeds 30MB or 75s cap")
                        handle.write(chunk)
            part.replace(cache)
        finally:
            if part.exists():
                part.unlink()
    raw = cache.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    with fits.open(cache, memmap=False) as hdus:
        quarter_in_file = hdus[0].header.get("QUARTER")
        if quarter_in_file is not None and int(quarter_in_file) != int(quarter):
            raise ValueError(f"Archived file is quarter {quarter_in_file}, expected {quarter}")
        table = hdus[1].data
        t = np.asarray(table["TIME"], dtype=float)
        f = np.asarray(table["PDCSAP_FLUX"], dtype=float)
        quality = np.asarray(table["SAP_QUALITY"], dtype=np.int64)
    good = np.isfinite(t) & np.isfinite(f) & (f > 0) & (quality == 0)
    t, f = t[good], f[good]
    if len(t) < 500:
        raise RuntimeError("Too few quality-filtered Kepler observations")
    # A fixed 301-cadence running median suppresses slow variability; it can
    # weaken long or unusual genuine transits, which we must acknowledge.
    trend = median_filter(f, size=301, mode="nearest")
    trend = np.maximum(trend, 1e-12)
    f = (f / trend)
    f = f / np.median(f)
    return t, f, {
        "target": str(target),
        "kic_id": starid,
        "requested_quarter": int(quarter),
        "cadences_after_quality_mask": int(len(t)),
        "time_start_bkjd": float(t.min()),
        "time_end_bkjd": float(t.max()),
        "source": "MAST Kepler PDC-SAP long-cadence FITS (direct public archive)",
        "file": filename, "url": url, "sha256": digest,
        "processing": "SAP_QUALITY==0; PDC_SAP flux; 301-cadence median normalization",
        "processing_caveat": "Trend removal can modify transit depth; injection occurs after detrending",
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
    found = bls_peak(t, f, bounds=(1.5, 20.))
    diagnostics, event_table = individual_transit_checks(
        t, f, found["period_days"],
        found["transit_time_days"], found["duration_days"])
    difference = abs(found["period_days"] - KNOWN_REFERENCE_PERIOD_DAYS)
    result = {
        "dataset": source,
        "method": "Astropy BLS with 1.5–20 day period grid",
        "period_range_predeclared_days": [1.5, 20.],
        "published_period_days": KNOWN_REFERENCE_PERIOD_DAYS,
        "period_reference": "NASA Exoplanet Archive DR25 Q1–Q17 KOI: Kepler-69 b",
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
