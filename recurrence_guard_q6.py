"""Frozen, exploratory Kepler Q6 periodic-eclipse-preservation safeguard.

The rule uses only time and normalized original flux to classify a *warning*
from the existing, unchanged local-step detector. Catalog classifications,
published binary periods and SPSD quality flags NEVER enter the guard.
Reported Kepler binary/planet source labels and quality annotations are used
only after all detector computations, for descriptive observational scoring.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from blind_transit_benchmark import robust_sigma
from kepler_preprocessing import normalize_flux
from localized_discontinuity import localized_downward_step_mask
from real_spsd_external_cohort import (
    load_frozen_star, cluster_archival_events, unique_match)

MANIFEST = "RECURRENCE_GUARD_Q6_FROZEN_2026_11_08.json"
OLD_SETTINGS = "LOCALIZED_STEP_STUDY_FROZEN_2026_11_07.json"


def load_protocol(path=MANIFEST):
    cfg = json.loads(Path(path).read_text())
    names = [int(s["kic"]) for s in cfg["sources"]]
    if cfg["quarter"] != 6 or len(names) != 13 or len(set(names)) != 13:
        raise ValueError("Prospective source list is not the 13-star Q6 cohort")
    if any(k in names for k in [7461601, 10020423, 6762829]):
        raise ValueError("Known development or previously studied stars may not enter holdout")
    counts = [sum(s["role"] == typ for s in cfg["sources"])
              for typ in ("published_eclipsing_binary",
                          "published_transiting_planet_host")]
    if counts != [8, 5]:
        raise ValueError("Frozen source strata modified")
    return cfg


def validate_guard_config(settings):
    c = settings
    fields = (
        "period_search_min_days", "period_search_max_days",
        "period_grid_step_days", "minimum_other_cycles_with_valid_windows",
        "minimum_other_cycles_showing_a_dip", "minimum_repetition_fraction",
        "absolute_event_depth_floor", "sigma_depth_multiplier",
        "minimum_samples_per_window", "maximum_local_gap_days")
    if any(field not in c for field in fields):
        raise ValueError("Guard protocol has missing fields")
    if (float(c["period_search_min_days"]) != 2.5 or
        float(c["period_search_max_days"]) != 22.0 or
        float(c["period_grid_step_days"]) != .02 or
        int(c["minimum_other_cycles_with_valid_windows"]) != 3 or
        int(c["minimum_other_cycles_showing_a_dip"]) != 3 or
        float(c["minimum_repetition_fraction"]) != .75 or
        float(c["absolute_event_depth_floor"]) != .0025 or
        float(c["sigma_depth_multiplier"]) != 4 or
        int(c["minimum_samples_per_window"]) != 4 or
        float(c["maximum_local_gap_days"]) != .16 or
        tuple(c["trough_window_days"]) != (-.10, .16) or
        tuple(c["baseline_left_days"]) != (-.54, -.27) or
        tuple(c["baseline_right_days"]) != (.29, .56)):
        raise ValueError("Numerical parameters differ from pre-run frozen manifest")


def local_dip_depth(t, flux, center, guard):
    """A self-contained, locally recovering short dip near a trial time.

    Return None when any of three windows lacks sample coverage or straddles
    a gap. The lower of two nearby baselines guards against real long steps.
    This measurement NEVER receives source labels or orbital truth.
    """
    n = int(guard["minimum_samples_per_window"])
    gap = float(guard["maximum_local_gap_days"])
    def take(bounds):
        left = int(np.searchsorted(t, center + float(bounds[0]), "left"))
        right = int(np.searchsorted(t, center + float(bounds[1]), "right"))
        times = t[left:right]
        if len(times) < n or np.any(np.diff(times) > gap):
            return None
        return flux[left:right]

    prev = take(guard["baseline_left_days"])
    dip = take(guard["trough_window_days"])
    after = take(guard["baseline_right_days"])
    if prev is None or dip is None or after is None:
        return None
    base = min(float(np.median(prev)), float(np.median(after)))
    trough = float(np.quantile(dip, .20))
    return float(base - trough)


def candidate_periodic_context(time, flux, onset, guard):
    """Scan a frozen period grid for repeated locally *recovered* dips.

    To prevent a local one-off permanent step being called an eclipse, at
    least three OTHER cycles must contain self-contained local troughs
    returning to both left and right baselines. Repeated samples on one
    star are not independent population trials.
    """
    validate_guard_config(guard)
    t = np.asarray(time, dtype=float)
    f = np.asarray(flux, dtype=float)
    if (t.ndim != 1 or t.shape != f.shape or len(t) < 500 or
        not np.all(np.isfinite(t)) or not np.all(np.isfinite(f)) or
        np.any(np.diff(t) <= 0) or np.any(f <= 0)):
        raise ValueError("Need 500+ strictly ascending observations and positive finite flux")
    if not np.isfinite(onset):
        raise ValueError("Candidate onset must be finite")
    scatter = max(float(robust_sigma(f)), 1e-10)
    threshold = max(float(guard["absolute_event_depth_floor"]),
                    float(guard["sigma_depth_multiplier"]) * scatter)
    anchor_depth = local_dip_depth(t, f, float(onset), guard)
    basic = {
        "protected_as_periodic": False,
        "candidate_depth_fraction": anchor_depth,
        "dip_threshold_fraction": threshold,
        "recovered_period_days": None,
        "supporting_other_cycles": 0,
        "other_cycles_with_valid_windows": 0,
        "recurrence_fraction": None,
        "interpretation": "Conservative repeat-dip heuristic, not planet/binary classification"
    }
    if anchor_depth is None or anchor_depth < threshold:
        return basic
    minimum_other = int(guard["minimum_other_cycles_with_valid_windows"])
    minimum_hits = int(guard["minimum_other_cycles_showing_a_dip"])
    fraction = float(guard["minimum_repetition_fraction"])
    best = None
    start = float(guard["period_search_min_days"])
    final = float(guard["period_search_max_days"])
    step = float(guard["period_grid_step_days"])
    for p in np.arange(start, final + step / 2, step):
        lo = int(np.ceil((t[0] + .60 - onset) / p))
        hi = int(np.floor((t[-1] - .60 - onset) / p))
        cycles = [k for k in range(lo, hi + 1) if k != 0]
        if len(cycles) < minimum_other:
            continue
        valid = 0
        hits = 0
        for k in cycles:
            d = local_dip_depth(t, f, float(onset + k * p), guard)
            if d is not None:
                valid += 1
                hits += int(d >= threshold)
        if valid < minimum_other or hits < minimum_hits:
            continue
        rate = hits / valid
        if rate < fraction:
            continue
        # Prefer more corroborated cycles, then a higher fraction,
        # then shorter trial period. No published period is supplied.
        rank = (hits, rate, -p)
        if best is None or rank > best[0]:
            best = (rank, float(p), int(hits), int(valid), float(rate))
    if best is not None:
        _, period, hits, valid, rate = best
        basic.update({
            "protected_as_periodic": True,
            "recovered_period_days": period,
            "supporting_other_cycles": hits,
            "other_cycles_with_valid_windows": valid,
            "recurrence_fraction": rate
        })
    return basic


def run_original_and_guarded(t, flux, step_settings, guard_settings):
    """No extra detector warnings are made: only veto destructive *masking*."""
    orig_keep, diagnostic = localized_downward_step_mask(t, flux, step_settings)
    saved = np.ones(len(t), dtype=bool)
    diagnostics = []
    mask_half_width = float(step_settings["step_mask_half_width_days"])
    for index, warning in enumerate(diagnostic["detected_events"]):
        onset = float(warning["time_bkjd"])
        context = candidate_periodic_context(t, flux, onset, guard_settings)
        if not context["protected_as_periodic"]:
            saved &= np.abs(t - onset) > mask_half_width
        diagnostics.append({
            "warning_index":index, "warning_time_bkjd":onset,
            "jump_fraction":warning["jump_fraction"],
            **context
        })
    if not np.all(saved[orig_keep]):
        raise AssertionError("Protected-data safeguard must not delete baseline-retained cadences")
    if diagnostic["n_persistent_step_events"] != len(diagnostics):
        raise AssertionError("Baseline warning accounting changed")
    return orig_keep, saved, diagnostics


def evaluate_target(source, quarter, old_settings, guard_settings):
    """Open official original FITS, preserving all original sample flags."""
    from real_spsd_external_cohort import load_frozen_star
    kic = int(source["kic"])
    t, sap, pdc, flags, extra = load_frozen_star(kic, quarter, 500)
    unflagged_count = int(np.sum((flags & 1024) != 0))
    spsd_events = cluster_archival_events(t, flags)
    outcomes = []
    warnings = []
    for product, raw in [("SAP", sap), ("PDCSAP", pdc)]:
        normalized = normalize_flux(raw)
        orig_mask, guarded_mask, diagnostics = run_original_and_guarded(
            t, normalized, old_settings, guard_settings)
        baseline_epochs = [d["warning_time_bkjd"] for d in diagnostics]
        matched, missed = unique_match(spsd_events, baseline_epochs)
        spsd_warning_ids = {p["warning_index"] for p in matched.values()}
        for warning in diagnostics:
            # Published class, binary period and archived quality flags are
            # added AFTER all recurrent-context classification.
            idx = warning["warning_index"]
            predicted = warning["recovered_period_days"]
            published = source.get("published_binary_period_days")
            period_error = None
            alias = None
            if predicted is not None and published is not None:
                candidates = [(.5, "half"), (1., "exact"), (2., "double")]
                ratio, name = min(candidates, key=lambda v:
                                  abs(predicted / (published * v[0]) - 1))
                period_error = float(abs(predicted / (published * ratio) - 1))
                alias = name if period_error <= .05 else "unmatched"
            warnings.append({
                "kic":kic, "source_name":source["name"],
                "literature_role":source["role"], "product":product,
                "archival_spsd_event_near_warning":idx in spsd_warning_ids,
                "published_binary_period_days":published,
                "period_match_to_published_or_simple_alias":alias,
                "period_relative_error_to_closest_alias":period_error,
                **warning
            })
        outcomes.append({
            "kic":kic, "source_name":source["name"], "literature_role":source["role"],
            "quarter":quarter, "product":product, "status":"analyzed",
            "original_fits_file":extra["source"]["file"],
            "original_fits_sha256":extra["source"]["sha256"],
            "n_aligned_original_cadences":int(len(t)),
            "n_original_spsd_bit1024_cadences":extra["n_original_spsd_flagged_cadences"],
            "n_spsd_bit1024_cadences_joint_valid":unflagged_count,
            "n_spsd_archival_event_clusters":len(spsd_events),
            "n_original_step_warnings":len(diagnostics),
            "n_warnings_protected_as_periodic":sum(
                int(d["protected_as_periodic"]) for d in diagnostics),
            "n_still_masked_step_warnings":sum(
                int(not d["protected_as_periodic"]) for d in diagnostics),
            "n_original_cadences_masked":int((~orig_mask).sum()),
            "n_guarded_cadences_masked":int((~guarded_mask).sum()),
            "n_cadences_spared":int((~orig_mask & guarded_mask).sum()),
            "n_archival_spsd_events_matched_original_warnings":len(matched),
            "n_archival_spsd_events_with_protected_warning":sum(
                int(p["warning_index"] in spsd_warning_ids and
                    diagnostics[p["warning_index"]]["protected_as_periodic"])
                for p in matched.values()),
            "n_unmatched_original_warnings_not_verified_fp":len(missed)
        })
    return outcomes, warnings


def results_summary(targets, warnings, config):
    counted = [r for r in targets if r["status"] == "analyzed"]
    available = sorted({r["kic"] for r in counted})
    missing = sorted({r["kic"] for r in targets
                      if r["status"] != "analyzed"})
    role_summary = []
    if counted:
        for (role, product), group in pd.DataFrame(counted).groupby(
                ["literature_role", "product"]):
            role_summary.append({
                "literature_role":role,"product":product,
                "n_analyzed_stars":int(group.kic.nunique()),
                "n_original_warnings":int(group.n_original_step_warnings.sum()),
                "n_guarded_warnings_protected":int(group.n_warnings_protected_as_periodic.sum()),
                "n_cadences_spared":int(group.n_cadences_spared.sum())
            })
    return {
        "scope":"Preselected external Q6 cohort: unchanged step mask vs recurrence-preserving safeguard",
        "n_planned_stars":len(config["sources"]),
        "n_analyzed_stars":len(available),
        "n_missing_stars":len(missing),
        "missing_kics":missing,
        "n_method_level_observational_rows":len(counted),
        "n_original_step_warning_rows":len(warnings),
        "n_periodic_protected_warning_rows":sum(
            int(w["protected_as_periodic"]) for w in warnings),
        "n_archival_spsd_events_in_observed_stars":
            int(sum(r["n_spsd_archival_event_clusters"]
                    for r in counted if r["product"]=="SAP")),
        "n_archival_spsd_events_protected_by_guard":
            int(sum(r["n_archival_spsd_events_with_protected_warning"]
                    for r in counted)),
        "by_literature_role_and_photometry":role_summary,
        "limitations":[
            "This is a purposively chosen tiny group, not a representative Kepler survey population.",
            "Repetition safeguard labels protective masking decisions, not confirmed astrophysical source of warnings.",
            "A host is not guaranteed to be clean of other types of events merely because it is a documented planet host.",
            "Archived instrument SPSD marker is incomplete; unmatched warnings are not verified false positives.",
            "A period-grid search across many periods can find accidental alignments; no mission false-alarm calibration.",
            "Many long binary periods cannot show four events in one Q6 quarter, so the guard can be insensitive by design.",
            "No new exoplanets; no claim of increased BLS transit recovery or survey-level reliability."
        ]
    }


def experiment(manifest=MANIFEST, output="results/recurrence_guard_q6"):
    cfg=load_protocol(manifest)
    guard=cfg["recurrence_guard"]
    validate_guard_config(guard)
    old=json.loads(Path(OLD_SETTINGS).read_text())["preprocessing"]
    out=Path(output)
    out.mkdir(parents=True,exist_ok=True)
    (out/"frozen_manifest.json").write_bytes(Path(manifest).read_bytes())
    cohort=[]
    warnings=[]
    for src in cfg["sources"]:
        kic=int(src["kic"])
        print(f"Prospective source {src['name']} KIC {kic}",flush=True)
        try:
            source_rows, warning_rows=evaluate_target(src,cfg["quarter"],old,guard)
            cohort.extend(source_rows)
            warnings.extend(warning_rows)
            print("  ",[(r["product"],r["n_original_step_warnings"],
                           r["n_warnings_protected_as_periodic"])
                          for r in source_rows],flush=True)
        except Exception as exc:
            cohort.append({
                "kic":kic,"source_name":src["name"],"literature_role":src["role"],
                "quarter":cfg["quarter"],"status":"source_or_analysis_error",
                "exception_class":type(exc).__name__,
                "error":str(exc)[:340]
            })
            print(f"  UNAVAILABLE/ERROR {type(exc).__name__}: {str(exc)[:250]}",flush=True)
    summary=results_summary(cohort,warnings,cfg)
    pd.DataFrame(cohort).to_csv(out/"all_planned_sources.csv",index=False)
    warning_cols=[
        "kic","source_name","literature_role","product",
        "archival_spsd_event_near_warning","published_binary_period_days",
        "period_match_to_published_or_simple_alias","period_relative_error_to_closest_alias",
        "warning_index","warning_time_bkjd","jump_fraction",
        "protected_as_periodic","candidate_depth_fraction","dip_threshold_fraction",
        "recovered_period_days","supporting_other_cycles",
        "other_cycles_with_valid_windows","recurrence_fraction","interpretation"
    ]
    pd.DataFrame(warnings,columns=warning_cols).to_csv(
        out/"all_warnings_periodicity_decisions.csv",index=False)
    (out/"summary_and_caveats.json").write_text(json.dumps(summary,indent=2)+"\n")
    if summary["n_analyzed_stars"] > 0:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        source_rows=[r for r in cohort if r.get("status")=="analyzed"]
        df=pd.DataFrame(source_rows)
        fig,axs=plt.subplots(2,1,figsize=(12,8),sharex=True)
        for ax,product in zip(axs,("SAP","PDCSAP")):
            rows=df[df["product"]==product].sort_values("kic")
            x=np.arange(len(rows))
            ax.bar(x,rows["n_original_step_warnings"],label="Old step warnings")
            ax.bar(x,rows["n_warnings_protected_as_periodic"],
                   label="Protected as periodic",alpha=.75)
            ax.set(ylabel="Warning count",
                   title=f"{product}: observed warnings vs recurrence-protected candidates")
            ax.set_xticks(x,rows["kic"].astype(str))
            ax.tick_params(axis="x",rotation=60)
            ax.legend()
        axs[-1].set(xlabel="Preselected KIC target")
        fig.tight_layout()
        fig.savefig(out/"recurrence_guard_per_star.png",dpi=170)
        plt.close(fig)
    print(json.dumps(summary,indent=2),flush=True)
    return summary


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",default=MANIFEST)
    p.add_argument("--out",default="results/recurrence_guard_q6")
    a=p.parse_args()
    experiment(a.manifest,a.out)
