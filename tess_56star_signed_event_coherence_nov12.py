"""Signed-event direction consistency for original TESS SPOC centroid windows.

The directional-concentration metric checks repeatability of measured in-event
moment-centroid displacement vectors. It is NOT off-target source localization
ground truth, a NASA ExoMiner feature, or evidence of improved classification.
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import binomtest

from tess_56star_paired_pointing_motion_robustness_nov12 import (
    D32, D24, HASH32, HASH24, SOURCES, read_original_events
)

KEYS = ["uid", "cohort", "TIC_ID", "orbit_index", "predicted_NASA_TCE_center_BTJD"]
VECTOR_KEYS = ["event_x_raw_pixels", "event_y_raw_pixels",
               "event_x_corrected_pixels", "event_y_corrected_pixels"]


def load_source_signed_vectors(root):
    root = Path(root)
    original = {
        D32: root / "prior32/centroid_physics_analysis" / D32,
        D24: root / "new24/24star_original_TESS_centroid_analysis" / D24,
    }
    for name, expected in ((D32, HASH32), (D24, HASH24)):
        if hashlib.sha256(original[name].read_bytes()).hexdigest() != expected:
            raise ValueError("Original NASA source file SHA256 mismatch: " + name)
    original_events = read_original_events(root)
    rows = []
    for cohort, relative, corrected_suffix, raw_suffix, nstar in SOURCES:
        folder = root / relative
        csvs = sorted(folder.glob("*" + corrected_suffix))
        if len(csvs) != nstar:
            raise ValueError("Original source counts changed: " + cohort)
        for cp in csvs:
            uid = cp.name[:-len(corrected_suffix)]
            rp = folder / (uid + raw_suffix)
            if not rp.is_file():
                raise ValueError("Missing original RAW signed centroid source: " + uid)
            corrected = pd.read_csv(cp)
            raw = pd.read_csv(rp)
            keys = ["orbit_index", "predicted_NASA_TCE_center_BTJD"]
            needed = keys + ["local_in_minus_flanking_x_pixels",
                             "local_in_minus_flanking_y_pixels",
                             "local_in_minus_flanking_vector_norm_pixels"]
            if not set(needed).issubset(corrected.columns) or not set(needed).issubset(raw.columns):
                raise ValueError("Original signed event fields not available for " + uid)
            if corrected.duplicated(keys).any() or raw.duplicated(keys).any():
                raise ValueError("Duplicate original signed event key")
            d = corrected[needed].merge(
                raw[needed], on=keys, how="outer", indicator=True,
                validate="one_to_one", suffixes=("_corrected", "_raw")
            )
            if (len(d) != len(corrected) or len(d) != len(raw) or
                    not d["_merge"].eq("both").all()):
                raise ValueError("Raw/corrected signed event keys are mismatched for " + uid)
            for r in d.itertuples(index=False):
                row = {
                    "uid": uid, "cohort": cohort,
                    "TIC_ID": int(uid.split("-")[0]),
                    "orbit_index": int(r.orbit_index),
                    "predicted_NASA_TCE_center_BTJD": float(r.predicted_NASA_TCE_center_BTJD),
                }
                for mode in ("raw", "corrected"):
                    x = float(getattr(r, "local_in_minus_flanking_x_pixels_" + mode))
                    y = float(getattr(r, "local_in_minus_flanking_y_pixels_" + mode))
                    norm = float(getattr(r, "local_in_minus_flanking_vector_norm_pixels_" + mode))
                    if not np.isfinite([x, y, norm]).all() or norm < 0:
                        raise ValueError("Invalid original signed centroid source measurement")
                    if not np.isclose(np.hypot(x, y), norm, atol=1e-9, rtol=1e-8):
                        raise ValueError("Signed vector does not reproduce original reported norm")
                    row["event_x_" + mode + "_pixels"] = x
                    row["event_y_" + mode + "_pixels"] = y
                rows.append(row)
    signed = pd.DataFrame(rows)
    if len(signed) != 248 or signed.uid.nunique() != 56 or signed.duplicated(KEYS).any():
        raise ValueError("Original frozen signed-event sample is not 56 TICs / 248 events")
    merged = original_events.merge(
        signed, on=KEYS, validate="one_to_one", indicator=True, how="outer"
    )
    if (len(merged) != 248 or not merged["_merge"].eq("both").all()):
        raise ValueError("Signed vectors do not match the frozen 248 source event identities")
    for mode in ("raw", "corrected"):
        norms = np.hypot(merged["event_x_" + mode + "_pixels"],
                         merged["event_y_" + mode + "_pixels"])
        if not np.allclose(norms, merged["event_" + mode + "_pixels"],
                           atol=1e-9, rtol=1e-8):
            raise ValueError("Signed and previously independently paired original source norms differ")
    return merged.drop(columns="_merge")


def directional_concentration(vectors):
    """R=norm(sum(vector_i))/sum(norm(vector_i)), in [0,1].

    Unlike normalized unit vectors, this uses original vector magnitudes.
    A consistent systematic drift can also yield R=1; not source truth.
    """
    v = np.asarray(vectors, dtype=float)
    if v.ndim != 2 or v.shape[1] != 2 or len(v) == 0 or not np.isfinite(v).all():
        raise ValueError("Invalid physical signed-vector event array")
    amplitude = np.linalg.norm(v, axis=1)
    total = float(amplitude.sum())
    if total == 0:
        return None
    return float(np.clip(np.linalg.norm(v.sum(axis=0)) / total, 0, 1))


def analyze_signed_events(events, require_frozen=True):
    required = set(KEYS + VECTOR_KEYS)
    if not required.issubset(events.columns):
        raise ValueError("Missing signed source-event columns: " + str(sorted(required - set(events.columns))))
    e = events.copy()
    if len(e) == 0 or e[KEYS].isna().any().any() or e.duplicated(["uid", "orbit_index"]).any():
        raise ValueError("Source event identity missing or duplicated")
    if e.groupby("uid")[["TIC_ID", "cohort"]].nunique().gt(1).any().any():
        raise ValueError("Source UID changed cohort or TIC identity")
    for col in VECTOR_KEYS:
        a = pd.to_numeric(e[col], errors="coerce").to_numpy(dtype=float)
        if not np.isfinite(a).all():
            raise ValueError("Nonfinite original signed in-event measurement")
        e[col] = a
    if require_frozen:
        counts = e.groupby("cohort").uid.nunique().to_dict()
        if len(e) != 248 or e.uid.nunique() != 56 or counts != {
            "prior_32": 32, "additional_24": 24
        }:
            raise ValueError("Original source total and cohort counts changed")
    records = []
    for (uid, cohort, tic), g in e.groupby(["uid", "cohort", "TIC_ID"], sort=True):
        record = dict(uid=uid, cohort=cohort, TIC_ID=int(tic), n_events=len(g))
        for mode in ("raw", "corrected"):
            vectors = g[["event_x_" + mode + "_pixels",
                         "event_y_" + mode + "_pixels"]].to_numpy(dtype=float)
            record[mode + "_direction_concentration"] = directional_concentration(vectors)
            record[mode + "_median_event_shift_pixels"] = float(
                np.median(np.linalg.norm(vectors, axis=1))
            )
            record[mode + "_mean_signed_vector_norm_pixels"] = float(
                np.linalg.norm(vectors.mean(axis=0))
            )
        records.append(record)
    stars = pd.DataFrame(records)
    eligible = stars[stars.n_events >= 3].copy()
    # Strictly descriptive: stars with zero vector sums/zero denominator are not
    # silently counted as improved, and are tracked rather than imputed.
    valid = eligible[
        eligible.raw_direction_concentration.notna() &
        eligible.corrected_direction_concentration.notna()
    ].copy()
    valid["concentration_gain"] = (
        valid.corrected_direction_concentration -
        valid.raw_direction_concentration
    )
    valid["event_shift_median_reduction"] = (
        valid.raw_median_event_shift_pixels -
        valid.corrected_median_event_shift_pixels
    )
    gain = valid.concentration_gain.to_numpy(dtype=float)
    pos, neg, ties = int((gain > 1e-12).sum()), int((gain < -1e-12).sum()), int((np.abs(gain) <= 1e-12).sum())
    if len(valid):
        rng = np.random.default_rng(2026111213)
        draw = rng.integers(0, len(valid), size=(20000, len(valid)))
        ci = np.quantile(np.median(gain[draw], axis=1), [.025, .975]).tolist()
    else:
        ci = None
    cohorts = {}
    for cohort, g in valid.groupby("cohort"):
        z = g.concentration_gain.to_numpy(dtype=float)
        cohorts[cohort] = dict(n_eligible_valid=len(g),
            coherence_increased=int((z > 1e-12).sum()),
            coherence_decreased=int((z < -1e-12).sum()),
            coherence_ties=int((np.abs(z) <= 1e-12).sum()),
            median_paired_coherence_change=float(np.median(z)))
    summary = dict(
        question="Exploratory within-source repeatability of signed in-event moment centroid shift; NOT off-target eclipse ground truth",
        source_stars=int(len(stars)), original_source_event_windows=int(len(e)),
        sources_at_least_three_events=int(len(eligible)),
        sources_with_valid_nonzero_signed_vectors=int(len(valid)),
        source_with_zero_denominator=int(len(eligible)-len(valid)),
        direction_concentration_definition="norm(sum signed in-event vectors)/sum individual vector magnitudes, same original event orbits, [0,1]",
        directional_concentration_increased_stars=pos,
        directional_concentration_decreased_stars=neg,
        directional_concentration_tied_stars=ties,
        median_paired_coherence_change=float(np.median(gain)) if len(valid) else None,
        exploratory_20000_whole_star_bootstrap_95pct_median_change=ci,
        exploratory_source_level_two_sided_exact_sign_p=(
            float(binomtest(pos, pos + neg).pvalue) if pos + neg else None
        ),
        both_coherence_increased_and_event_magnitude_reduced=int(
            ((valid.concentration_gain > 1e-12) & (valid.event_shift_median_reduction > 0)).sum()
        ),
        concentration_change_by_source_cohort=cohorts,
        controls=[
            "Same genuine NASA original TCE and SPOC FITS source windows for raw and corrected vectors.",
            "56 independent star units; repeated event windows never treated as independent stars.",
            "At least three observed source events for source repeatability; ineligible source count explicit.",
            "Source file SHA256 pins, original event identity, signed-norm preservation, and exact 248-event match required.",
            "No new off-target eclipse truth labels or sky-position truth were obtained.",
            "Nonzero consistency can arise from coherent pointing/systematic artifacts; high R is not proof of astrophysical source.",
            "This is post-hoc on already inspected sources; exploratory p/CI are not a confirmatory model-gain claim.",
            "No change to ExoMiner model weights, scores, or official difference-image centroid diagnostic."
        ])
    return stars, valid, summary


def run(root, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    observed = load_source_signed_vectors(root)
    stars, valid, summary = analyze_signed_events(observed, require_frozen=True)
    observed.to_csv(out / "248_original_event_signed_centroid_vectors.csv", index=False)
    stars.to_csv(out / "56star_source_signed_event_coherence_all.csv", index=False)
    valid.to_csv(out / "eligible_original_source_signed_event_coherence.csv", index=False)
    (out / "TESS_56star_signed_centroid_coherence_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n")
    plt.rcParams.update({"font.family":"serif", "font.size":10})
    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    for cohort, g in valid.groupby("cohort"):
        ax.scatter(g.raw_direction_concentration,
                   g.corrected_direction_concentration,
                   marker="s" if cohort=="additional_24" else "o",
                   label="Additional 24" if cohort=="additional_24" else "Earlier 32",
                   s=36, alpha=.8)
    ax.plot([0,1],[0,1], color="grey", lw=1, linestyle="--")
    ax.set(xlim=(0,1.02), ylim=(0,1.02),
        xlabel="Original raw repeated-event direction concentration",
        ylabel="After exploratory pointing subtraction",
        title="TESS same-star event-vector repeatability")
    ax.legend(frameon=False)
    fig.text(.5,.015,"Not off-target eclipse truth or NASA classification accuracy", ha="center",fontsize=8)
    fig.tight_layout(rect=[0,.04,1,1])
    fig.savefig(out / "56star_original_signed_event_coherence.png",dpi=185)
    plt.close(fig)
    print(json.dumps(summary,indent=2),flush=True)
    return summary


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-root",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.source_root,a.out)
