"""Source-grounded Kepler photometry and conservative near-gap experiment.

The experiment is motivated by Hatzes (2020), Oshagh (2018) and Robnik et
al. (2026). This is NOT Robnik's artifact-template bank, nor a calibrated
Kepler Robovetter or a claim of exoplanet discovery.

The raw PDCSAP transit injection is done BEFORE fixed median normalization.
Both methods are applied to precisely the same injected input.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np


def load_raw_kepler_quarter(kic: int, quarter: int):
    """Read quality-filtered *unflattened* PDCSAP flux, with MAST source hash.

    Reuses the existing bounded MAST fetch and cache. Source metadata already
    includes the raw FITS checksum; nothing here changes the official file.
    """
    from astropy.io import fits
    from real_kepler_lightcurve import fetch_kepler_quarter

    _, _, source = fetch_kepler_quarter(f"KIC {int(kic)}", int(quarter))
    file_path = Path("data/kepler_fits") / source["file"]
    if not file_path.exists():
        raise FileNotFoundError(f"Expected cached original FITS at {file_path}")
    with fits.open(file_path, memmap=False) as hdus:
        t = np.asarray(hdus[1].data["TIME"], dtype=float)
        f = np.asarray(hdus[1].data["PDCSAP_FLUX"], dtype=float)
        flags = np.asarray(hdus[1].data["SAP_QUALITY"], dtype=np.int64)
    good = np.isfinite(t) & np.isfinite(f) & (f > 0) & (flags == 0)
    time, raw = t[good], f[good]
    if len(time) < 500:
        raise ValueError("Too few quality-filtered raw observations")
    if np.any(np.diff(time) <= 0):
        raise ValueError("Nonmonotonic or repeated timestamps require review")
    return time, raw, source


def normalize_flux(raw, median_window=301):
    """The exact baseline median filter used by the existing Kepler demo."""
    from scipy.ndimage import median_filter
    x = np.asarray(raw, dtype=float)
    if x.ndim != 1 or len(x) < 500 or not np.all(np.isfinite(x)) or np.any(x <= 0):
        raise ValueError("Need >=500 valid positive raw brightness measurements")
    if median_window <= 1 or median_window % 2 != 1:
        raise ValueError("Detrending window must be an odd integer >1")
    trend = np.maximum(median_filter(x, size=int(median_window), mode="nearest"),
                       1e-12)
    out = x / trend
    out = out / np.median(out)
    if not np.all(np.isfinite(out)):
        raise ValueError("Failed to normalize brightness observations")
    return out


def gap_edge_mask(time, gap_days=0.5, edge_days=0.2, minimum_remaining=500):
    """Mask only a fixed distance around edges of gaps exceeding gap_days.

    This does not identify physical detector defects; it is a conservative,
    intentionally minimal gap-neighborhood policy fixed before heldout tests.
    """
    t = np.asarray(time, dtype=float)
    if t.ndim != 1 or len(t) < 2 or not np.all(np.isfinite(t)):
        raise ValueError("Need valid finite observation times")
    if np.any(np.diff(t) <= 0):
        raise ValueError("Times must be strictly ascending")
    if gap_days <= 0 or edge_days < 0:
        raise ValueError("Gap and edge widths must be nonnegative, gap positive")
    keep = np.ones(len(t), dtype=bool)
    gap_ids = np.flatnonzero(np.diff(t) > gap_days)
    for i in gap_ids:
        keep &= ~((t >= t[i] - edge_days) & (t <= t[i]))
        keep &= ~((t >= t[i + 1]) & (t <= t[i + 1] + edge_days))
    if int(keep.sum()) < minimum_remaining:
        raise ValueError("Predeclared mask leaves too few observations")
    return keep, {
        "n_long_gaps": int(len(gap_ids)),
        "n_masked": int((~keep).sum()),
        "n_retained": int(keep.sum()),
        "mask_fraction": float((~keep).mean()),
    }


def injection_model(time, period_days, epoch_days, depth_ppm, duration_days):
    """Deterministic injected box decrement; no fitted or known planet needed."""
    t = np.asarray(time, dtype=float)
    if not (period_days > 0 and 0 < duration_days < period_days / 3):
        raise ValueError("Invalid injected orbital period/duration")
    if not (0 < depth_ppm < 1e6):
        raise ValueError("Invalid injected depth")
    phase = (t - epoch_days + period_days / 2) % period_days - period_days / 2
    return np.abs(phase) < duration_days / 2


def inject_before_detrending(time, raw, period_days, epoch_days, depth_ppm,
                             duration_days):
    """Multiplicative flux-level transit injection into raw PDCSAP observations."""
    y = np.asarray(raw, dtype=float).copy()
    inside = injection_model(time, period_days, epoch_days, depth_ppm,
                             duration_days)
    if not np.any(inside):
        raise ValueError("Injection has no sampled transit cadences")
    y[inside] *= (1 - depth_ppm / 1e6)
    return y, inside


def proxy_inverted_rolled_flux(normalized_flux, seed):
    """Nonplanet 'proxy' based on inverted, rolled observed light curve.

    This operation is NOT a physically unbiased Kepler false-alarm generator:
    real instrumental artifacts, existing planets, and gap alignment can change.
    """
    x = np.asarray(normalized_flux, dtype=float)
    if x.ndim != 1 or len(x) < 500:
        raise ValueError("Need a full light curve for a proxy null")
    rng = np.random.default_rng(seed)
    shift = int(rng.integers(1, len(x)))
    return 1 - np.roll(x - 1, shift), shift


def injected_signal_retention(baseline_uninjected, baseline_injected,
                               inside, mask):
    """Fraction of added photometric depth remaining on unmasked cadences.

    Only compare differential injected-versus-uninjected brightness under the
    SAME normalization. This is a conservative diagnostic not physical depth
    inference under realistic limb darkening.
    """
    a = np.asarray(baseline_uninjected)
    b = np.asarray(baseline_injected)
    inside = np.asarray(inside, bool)
    keep = np.asarray(mask, bool)
    if a.shape != b.shape or a.shape != inside.shape or a.shape != keep.shape:
        raise ValueError("Injection retention shapes disagree")
    effect = np.maximum(a - b, 0)
    total = float(effect[inside].sum())
    if total <= 0:
        return None
    return float(effect[inside & keep].sum() / total)
