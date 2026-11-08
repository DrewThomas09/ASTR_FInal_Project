"""Prospectively frozen observational audit: archived SPSD flags, SAP vs PDCSAP.

Important: no injected artificial planet and no new exoplanet claim.  Kepler's
quality bit 1024 is an independent *archival instrument label* for evaluating
our unchanged local step detector after the detector has processed the flux.
Warnings unmatched to that label are NOT verified false positives.

The cohort and tolerance parameters were committed before this script's first
real Kepler observational evaluation on November 8, 2026.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

MANIFEST = "REAL_SPSD_EXTERNAL_COHORT_FROZEN_2026_11_08.json"
FROZEN_STEP_SETTINGS = "LOCALIZED_STEP_STUDY_FROZEN_2026_11_07.json"


def cohort_manifest(path=MANIFEST):
    data = json.loads(Path(path).read_text())
    targets = data["targets"]
    ids = [int(t["kic"]) for t in targets]
    if data["quarter"] != 6 or len(ids) != 12 or len(set(ids)) != 12:
        raise ValueError("Prospective 12-source Quarter 6 cohort changed")
    if 7461601 in ids:
        raise ValueError("Previously studied known positive must be excluded")
    conf = data["processing"]
    if (conf["quality_spsd_bit"] != 1024 or
            conf["warning_to_event_match_tolerance_days"] != .22 or
            conf["event_merge_width_days"] != .45 or
            conf["minimum_joint_valid_cadences"] != 500):
        raise ValueError("Predeclared primary analysis rules have changed")
    return data


def common_flux_rows(time, sap, pdc, quality, min_cadences=500):
    """Keep flagged original measurements; align both flux products identically."""
    t = np.asarray(time, dtype=float)
    a = np.asarray(sap, dtype=float)
    b = np.asarray(pdc, dtype=float)
    q = np.asarray(quality, dtype=np.int64)
    if any(arr.shape != t.shape for arr in [a, b, q]) or t.ndim != 1:
        raise ValueError("FITS arrays are not aligned vectors")
    valid = np.isfinite(t) & np.isfinite(a) & np.isfinite(b) & (a > 0) & (b > 0)
    if valid.sum() < min_cadences:
        raise ValueError("Insufficient simultaneous SAP and PDCSAP cadences")
    selected = [v[valid] for v in (t, a, b, q)]
    if np.any(np.diff(selected[0]) <= 0):
        raise ValueError("Duplicate or unordered times")
    return (*selected, int((~valid).sum()))


def cluster_archival_events(time, quality, bit=1024, merge_days=.45):
    """Cluster adjacent marked cadences, counting every underlying flag."""
    t = np.asarray(time, dtype=float)
    q = np.asarray(quality, dtype=np.int64)
    if t.ndim != 1 or q.shape != t.shape or not np.all(np.isfinite(t)):
        raise ValueError("Invalid time-quality arrays")
    if np.any(np.diff(t) <= 0):
        raise ValueError("Times must be strictly increasing")
    if bit != 1024 or merge_days != .45:
        raise ValueError("Frozen event-label policy has changed")
    labels = t[(q & bit) != 0]
    if len(labels) == 0:
        return []
    groups = [[float(labels[0])]]
    for stamp in labels[1:]:
        if float(stamp) - groups[-1][-1] <= merge_days:
            groups[-1].append(float(stamp))
        else:
            groups.append([float(stamp)])
    return [{"event_id":i, "archived_time_bkjd":g[0],
             "last_marked_time_bkjd":g[-1],
             "marked_cadences":len(g)} for i, g in enumerate(groups)]


def unique_match(events, warning_times, tolerance=.22):
    """One-to-one closest archival-epoch matching with no reused warning."""
    if tolerance != .22:
        raise ValueError("Frozen matching tolerance changed")
    warnings = [float(x) for x in warning_times]
    choices = []
    for i, event in enumerate(events):
        for j, predicted in enumerate(warnings):
            dt = float(predicted - event["archived_time_bkjd"])
            if abs(dt) <= tolerance:
                choices.append((abs(dt), i, j, dt))
    choices.sort()
    matched_events, matched_warnings = {}, set()
    for _, i, j, dt in choices:
        if i not in matched_events and j not in matched_warnings:
            matched_events[i] = {"warning_index":j, "lag_days":dt,
                                 "warning_time_bkjd":warnings[j]}
            matched_warnings.add(j)
    return matched_events, sorted(set(range(len(warnings))) - matched_warnings)


def paired_event_rows(kic, events, sap_warnings, pdc_warnings, tolerance=.22):
    sap_matches, sap_unused = unique_match(events, sap_warnings, tolerance)
    pdc_matches, pdc_unused = unique_match(events, pdc_warnings, tolerance)
    rows = []
    for i, e in enumerate(events):
        a, b = sap_matches.get(i), pdc_matches.get(i)
        rows.append({
            "kic":int(kic), "event_index":int(e["event_id"]),
            "archived_time_bkjd":e["archived_time_bkjd"],
            "marked_cadences":int(e["marked_cadences"]),
            "sap_match":a is not None, "pdc_match":b is not None,
            "sap_warning_time_bkjd":a["warning_time_bkjd"] if a else None,
            "pdc_warning_time_bkjd":b["warning_time_bkjd"] if b else None,
            "sap_lag_days":a["lag_days"] if a else None,
            "pdc_lag_days":b["lag_days"] if b else None,
        })
    return rows, sap_unused, pdc_unused


def load_frozen_star(kic, quarter, minimum):
    """Fetch official source, then reopen ORIGINAL FITS rather than filtered return."""
    from astropy.io import fits
    from real_kepler_lightcurve import fetch_kepler_quarter
    _, _, source = fetch_kepler_quarter(f"KIC {kic}", quarter)
    location = Path("data/kepler_fits") / source["file"]
    with fits.open(location, memmap=False) as h:
        table = h[1].data
        t = np.asarray(table["TIME"], dtype=float)
        a = np.asarray(table["SAP_FLUX"], dtype=float)
        b = np.asarray(table["PDCSAP_FLUX"], dtype=float)
        quality = np.asarray(table["SAP_QUALITY"], dtype=np.int64)
    n_original_flags = int(np.count_nonzero((quality & 1024) != 0))
    t, a, b, q, n_invalid = common_flux_rows(t, a, b, quality, minimum)
    return (t, a, b, q,
            {"n_original_spsd_flagged_cadences":n_original_flags,
             "n_joint_invalid_removed":n_invalid, "source":source})


def analyze_star(kic, manifest, settings):
    """Detector receives only normalized time/flux, never quality labels."""
    from kepler_preprocessing import normalize_flux
    from localized_discontinuity import localized_downward_step_mask

    t, sap, pdc, q, extras = load_frozen_star(
        kic, manifest["quarter"],
        manifest["processing"]["minimum_joint_valid_cadences"])
    sap_normalized = normalize_flux(sap)
    pdc_normalized = normalize_flux(pdc)
    sap_keep, sap_diagnostics = localized_downward_step_mask(
        t, sap_normalized, settings)
    pdc_keep, pdc_diagnostics = localized_downward_step_mask(
        t, pdc_normalized, settings)
    # Only AFTER searching both flux products, read archival quality labels.
    events = cluster_archival_events(
        t, q, manifest["processing"]["quality_spsd_bit"],
        manifest["processing"]["event_merge_width_days"])
    sap_warnings = [e["time_bkjd"] for e in sap_diagnostics["detected_events"]]
    pdc_warnings = [e["time_bkjd"] for e in pdc_diagnostics["detected_events"]]
    event_rows, sap_unused, pdc_unused = paired_event_rows(
        kic, events, sap_warnings, pdc_warnings,
        manifest["processing"]["warning_to_event_match_tolerance_days"])
    summary = {
        "kic":int(kic), "quarter":manifest["quarter"],
        "status":"analyzed", "n_joint_valid_cadences":int(len(t)),
        "n_joint_invalid_removed":extras["n_joint_invalid_removed"],
        "n_original_spsd_flagged_cadences":extras["n_original_spsd_flagged_cadences"],
        "n_joint_spsd_flagged_cadences":int(np.count_nonzero((q & 1024) != 0)),
        "n_archived_event_clusters":int(len(events)),
        "n_sap_warnings":len(sap_warnings),
        "n_pdc_warnings":len(pdc_warnings),
        "n_sap_warning_match":int(sum(r["sap_match"] for r in event_rows)),
        "n_pdc_warning_match":int(sum(r["pdc_match"] for r in event_rows)),
        "n_sap_unmatched_warnings":len(sap_unused),
        "n_pdc_unmatched_warnings":len(pdc_unused),
        "n_sap_cadences_masked":int((~sap_keep).sum()),
        "n_pdc_cadences_masked":int((~pdc_keep).sum()),
        "original_FITS_sha256":extras["source"]["sha256"],
        "original_FITS_filename":extras["source"]["file"],
        "source_archive_url":extras["source"]["url"],
    }
    warning_rows = [
        {"kic":int(kic), "product":product, "warning_time_bkjd":float(times[j]),
         "archival_spsd_match":False, "classification":"unmatched archival label; NOT verified false positive"}
        for product, times, unused in [
            ("SAP", sap_warnings, sap_unused), ("PDCSAP", pdc_warnings, pdc_unused)]
        for j in unused]
    payload = {
        "time":t, "sap":sap_normalized, "pdc":pdc_normalized,
        "events":events, "sap_warnings":sap_warnings, "pdc_warnings":pdc_warnings}
    return summary, event_rows, warning_rows, payload


def summarize(star_rows, event_rows, warning_rows):
    available = [r for r in star_rows if r["status"]=="analyzed"]
    flags = list(event_rows)
    category = {
        "both":sum(bool(r["sap_match"] and r["pdc_match"]) for r in flags),
        "sap_only":sum(bool(r["sap_match"] and not r["pdc_match"]) for r in flags),
        "pdc_only":sum(bool(r["pdc_match"] and not r["sap_match"]) for r in flags),
        "neither":sum(bool(not r["sap_match"] and not r["pdc_match"]) for r in flags)}
    assert sum(category.values()) == len(flags)
    return {
        "design":"Frozen 12-KIC exploratory SAP-versus-PDCSAP observational audit",
        "n_planned_stars":len(star_rows),
        "n_analyzed_stars":len(available),
        "n_unavailable_stars":len(star_rows)-len(available),
        "n_stars_with_evaluable_archived_spsd":sum(r["n_archived_event_clusters"]>0 for r in available),
        "n_archived_spsd_event_clusters":len(flags),
        "archival_event_detection":category,
        "n_sap_warnings":sum(r["n_sap_warnings"] for r in available),
        "n_pdc_warnings":sum(r["n_pdc_warnings"] for r in available),
        "n_sap_unmatched_warnings":sum(r["n_sap_unmatched_warnings"] for r in available),
        "n_pdc_unmatched_warnings":sum(r["n_pdc_unmatched_warnings"] for r in available),
        "n_unmatched_warning_rows":len(warning_rows),
        "inference":"Descriptive event-label comparison only; NASA's 1024 quality bit is not exhaustive physical ground truth, and selected Kepler hosts do not represent mission-wide stellar populations.",
        "no_new_exoplanet_discovery":True}


def draw_figures(out, stars, selected_example):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    available = [r for r in stars if r["status"]=="analyzed"]
    if available:
        fig, ax=plt.subplots(figsize=(11,4))
        x=np.arange(len(available))
        ax.bar(x-.24,[r["n_archived_event_clusters"] for r in available],
               width=.24,label="Archived SPSD event clusters")
        ax.bar(x,[r["n_sap_warning_match"] for r in available],
               width=.24,label="SAP step warnings matched")
        ax.bar(x+.24,[r["n_pdc_warning_match"] for r in available],
               width=.24,label="PDCSAP step warnings matched")
        ax.set(xticks=x,xticklabels=[str(r["kic"]) for r in available],
               xlabel="Kepler KIC ID",ylabel="Count (events / matched events)",
               title="Prospectively fixed Q6 sources: archival SPSD labels vs warnings")
        ax.tick_params(axis="x",rotation=60)
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(out/"real_spsd_events_by_star.png",dpi=160)
        plt.close(fig)
    if selected_example is not None:
        kic, payload=selected_example
        events=payload["events"]
        if events:
            center=events[0]["archived_time_bkjd"]
            view=np.abs(payload["time"]-center)<=2.5
            fig, axs=plt.subplots(2,1,figsize=(10,7),sharex=True)
            for ax,flux,warnings,title in zip(
                    axs,(payload["sap"],payload["pdc"]),
                    (payload["sap_warnings"],payload["pdc_warnings"]),
                    ("SAP (raw aperture product)","PDCSAP (NASA PDC-corrected)")):
                ax.scatter(payload["time"][view],flux[view],s=7)
                ax.axvline(center,linestyle="--",label="Archival SPSD bit 1024")
                for w in warnings:
                    if abs(w-center)<=2.5:
                        ax.axvline(w,linestyle=":",label="Blind local-step warning")
                ax.set(ylabel="Normalized flux",title=title)
                ax.legend(fontsize=8,loc="best")
            axs[-1].set(xlabel="Time (BKJD)",xlim=(center-2.5,center+2.5))
            fig.suptitle(f"First archived SPSD event by fixed KIC order: {kic}")
            fig.tight_layout()
            fig.savefig(out/"first_archived_spsd_event_sap_vs_pdc.png",dpi=160)
            plt.close(fig)


def experiment(manifest=MANIFEST, out="results/real_spsd_external_cohort"):
    config=cohort_manifest(manifest)
    settings=json.loads(Path(FROZEN_STEP_SETTINGS).read_text())["preprocessing"]
    dest=Path(out)
    dest.mkdir(parents=True,exist_ok=True)
    (dest/"frozen_design.json").write_bytes(Path(manifest).read_bytes())
    stars=[];events=[];warnings=[];example=None
    # Iterate exactly precommitted target order; no substitutions or early stops.
    for obj in config["targets"]:
        kic=int(obj["kic"])
        print(f"Frozen target KIC {kic}, Quarter {config['quarter']}",flush=True)
        try:
            row,ev,unmatched,payload=analyze_star(kic,config,settings)
            stars.append(row);events.extend(ev);warnings.extend(unmatched)
            # Illustration chosen by original archived labels, not detector output.
            if payload["events"] and (example is None or kic<example[0]):
                example=(kic,payload)
            print(f"  archive={row['n_archived_event_clusters']} SAP={row['n_sap_warning_match']} PDC={row['n_pdc_warning_match']}",flush=True)
        except Exception as exc:
            stars.append({"kic":kic,"quarter":config["quarter"],
                "status":"source_or_analysis_error","error_type":type(exc).__name__,
                "error":str(exc)[:350]})
            print(f"  FAILED {type(exc).__name__}: {str(exc)[:300]}",flush=True)
    summary=summarize(stars,events,warnings)
    pd.DataFrame(stars).to_csv(dest/"all_planned_targets.csv",index=False)
    pd.DataFrame(events,columns=[
        "kic","event_index","archived_time_bkjd","marked_cadences",
        "sap_match","pdc_match","sap_warning_time_bkjd",
        "pdc_warning_time_bkjd","sap_lag_days","pdc_lag_days"
    ]).to_csv(dest/"paired_archival_events.csv",index=False)
    pd.DataFrame(warnings,columns=[
        "kic","product","warning_time_bkjd","archival_spsd_match",
        "classification"]).to_csv(dest/"unmatched_warnings_not_confirmed_false_alarms.csv",index=False)
    (dest/"summary_and_limits.json").write_text(json.dumps(summary,indent=2)+"\n")
    draw_figures(dest,stars,example)
    print(json.dumps(summary,indent=2),flush=True)
    return summary


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",default=MANIFEST)
    p.add_argument("--out",default="results/real_spsd_external_cohort")
    args=p.parse_args()
    experiment(args.manifest,args.out)
