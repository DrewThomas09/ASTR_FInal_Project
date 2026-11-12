"""Prospective *screening only* for externally vetted TESS NEB sources.

Original ExoFOP TFOPWG dispositions identify follow-up candidates.
NEB does not itself supply an identified neighbor's sky coordinates,
and EB is NOT automatically a truth-localized on-target eclipsing binary.
No TESS centroid values, NASA model scores or model predictions are read.
"""
import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OFFICIAL_CSV_URL = "https://exofop.ipac.caltech.edu/tess/json/tois.csv"
SEED = "ASTR_OFFTARGET_TRUTH_20261112"
PREVIOUS = (
    "TESS_32STAR_CENTROID_ALIAS_COMPANION_FROZEN_2026_11_08.json",
    "TESS_NEW_24STAR_CENTROID_RULE_HOLDOUT_FROZEN_2026_11_08.json",
)
EXTRA_EXPOSED_TICS = {167526485}
WANTED = {"NEB", "EB", "FP"}
REQUIRED_COLUMNS = (
    "TIC ID", "TOI", "TFOPWG Disposition", "Epoch (BJD)",
    "Period (days)", "Duration (hours)", "Time Series Observations",
)


def excluded_tics(repo_root):
    root = Path(repo_root)
    old = set(EXTRA_EXPOSED_TICS)
    counts = {}
    for filename in PREVIOUS:
        d = json.loads((root / filename).read_text(encoding="utf-8"))
        tics = {int(row["tic_id"]) for row in d["source_records"]}
        old |= tics
        counts[filename] = len(tics)
    if counts[PREVIOUS[0]] != 32 or counts[PREVIOUS[1]] != 24:
        raise ValueError("Historical original-source cohort was altered")
    if len(old) != 57:
        raise ValueError("Previously inspected source exclusion changed")
    return old


def strictly_positive_float(value):
    try:
        f = float(str(value).strip())
        return f if 0 < f < float("inf") else None
    except (TypeError, ValueError):
        return None


def candidate_rows(raw_bytes, previous):
    decoded = raw_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))
    if reader.fieldnames is None or not set(REQUIRED_COLUMNS).issubset(reader.fieldnames):
        raise ValueError("Original ExoFOP TOI catalog fields missing")
    counts = Counter()
    all_candidates = []
    seen_tois = set()
    for row in reader:
        counts["all_exofop_rows"] += 1
        classification = str(row["TFOPWG Disposition"]).strip().upper()
        counts["disposition_" + (classification or "empty")] += 1
        if classification not in WANTED:
            continue
        counts[classification + "_catalog_status"] += 1
        toi = str(row["TOI"]).strip()
        try:
            tic = int(str(row["TIC ID"]).strip())
        except (TypeError, ValueError):
            counts[classification + "_invalid_TIC"] += 1
            continue
        if not toi or (tic, toi) in seen_tois:
            counts[classification + "_duplicate_or_missing_TOI"] += 1
            continue
        seen_tois.add((tic, toi))
        if tic in previous:
            counts[classification + "_already_inspected_TIC"] += 1
            continue
        nseries = strictly_positive_float(row["Time Series Observations"])
        if nseries is None:
            counts[classification + "_no_referenced_timeseries"] += 1
            continue
        period = strictly_positive_float(row["Period (days)"])
        epoch = strictly_positive_float(row["Epoch (BJD)"])
        duration = strictly_positive_float(row["Duration (hours)"])
        if period is None or epoch is None or duration is None or duration >= 7.2*period:
            counts[classification + "_no_usable_ephemeris"] += 1
            continue
        digest = hashlib.sha256(
            (SEED + "|" + str(tic) + "|" + toi).encode("utf-8")
        ).hexdigest()
        all_candidates.append({
            "TIC_ID": tic,
            "TOI": toi,
            "catalog_TFOPWG_disposition": classification,
            "catalog_TESS_disposition": str(row.get("TESS Disposition", "")).strip(),
            "published_epoch_BJD": epoch,
            "published_period_days": period,
            "published_duration_hours": duration,
            "catalog_timeseries_observation_count": int(nseries),
            "reported_TESS_sectors_unverified": str(row.get("Sectors", "")).strip(),
            "exofop_target_url": "https://exofop.ipac.caltech.edu/tess/target.php?id=" + str(tic),
            "exofop_time_series_url": "https://exofop.ipac.caltech.edu/tess/download_tseries.php?output=csv&target=" + str(tic),
            "exofop_nearby_astrometry_url": "https://exofop.ipac.caltech.edu/tess/download_nearbytarget.php?id=" + str(tic) + "&output=csv",
            "deterministic_selection_sha256": digest,
            "candidate_evidence_status": (
                "NEB catalog status; neighbor identity/coordinates and direct original follow-up must be independently checked"
                if classification=="NEB" else
                "EB catalog status only; not confirmed on-target source without independently located eclipses"
                if classification=="EB" else
                "FP is a broad catalog label, NOT a verified nearby or on-target eclipsing binary; inspect ground-based follow-up notes"
            ),
            "truth_localization_verified": False,
            "original_TESS_SPOC_2min_FITS_verified": False,
            "moment_centroid_evaluated": False,
        })
    counts["screened_plausible_rows_with_epoch_and_tseries"] = len(all_candidates)
    # Prevent a star with multiple TOIs from filling multiple candidate slots.
    grouped = {}
    for row in sorted(all_candidates, key=lambda x:x["deterministic_selection_sha256"]):
        grouped.setdefault(row["catalog_TFOPWG_disposition"], {})
        grouped[row["catalog_TFOPWG_disposition"]].setdefault(row["TIC_ID"], row)
    ordered = {}
    for disposition in sorted(WANTED):
        ordered[disposition] = sorted(
            grouped.get(disposition, {}).values(),
            key=lambda row: row["deterministic_selection_sha256"]
        )
    return ordered, counts


def run(repo_root, output_dir, input_csv=None):
    import requests
    root = Path(repo_root)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    previous = excluded_tics(root)
    if input_csv:
        raw = Path(input_csv).read_bytes()
        acquisition = "explicit local ExoFOP snapshot (must be separately sourced)"
    else:
        response = requests.get(
            OFFICIAL_CSV_URL, timeout=120,
            headers={"User-Agent":"University-Astronomy-Research-Reproducible-Source-Screen/1.0"}
        )
        response.raise_for_status()
        raw = response.content
        acquisition = OFFICIAL_CSV_URL
    if len(raw) < 100:
        raise ValueError("Original ExoFOP TOI table unexpectedly empty")
    snapshot_hash = hashlib.sha256(raw).hexdigest()
    (out/"original_exofop_toi_catalog_snapshot.csv").write_bytes(raw)
    ordered, counts = candidate_rows(raw, previous)
    for group in sorted(WANTED):
        rows = ordered.get(group, [])
        name = {"NEB":"NEB_nearby_binary_NEEDS_source_verification",
                "EB":"EB_control_NEEDS_onsource_proof",
                "FP":"FP_broad_false_positive_category_NEEDS_subtype_evidence"}[group]
        with (out/(name+".csv")).open("w",newline="",encoding="utf-8") as handle:
            fields = list(rows[0]) if rows else [
                "TIC_ID","TOI","catalog_TFOPWG_disposition","candidate_evidence_status"
            ]
            writer=csv.DictWriter(handle,fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    selected = {group:ordered[group][:12] for group in sorted(WANTED)}
    report = {
        "screened_at_utc": datetime.now(timezone.utc).isoformat(),
        "official_source": acquisition,
        "original_raw_csv_sha256": snapshot_hash,
        "original_raw_csv_size_bytes": len(raw),
        "exclusion_56_prior_stars_plus_pilot": len(previous),
        "screen_counts": dict(counts),
        "eligible_catalog_NEBS_new_distinct_TICs": len(ordered["NEB"]),
        "eligible_catalog_EBS_new_distinct_TICs": len(ordered["EB"]),
        "broad_FP_status_followup_review_distinct_TICs": len(ordered["FP"]),
        "preview_first_12_hash_ordered_each_not_selected_or_validated": selected,
        "strict_research_boundary": [
            "This is an external ExoFOP disposition-and-ephemeris screening, not an independent truth-verified localization study.",
            "The public ExoFOP TOI catalog has broad FP/PC dispositions rather than NEB/EB subtypes; do not call zero NEB/EB subtype rows zero real eclipsing binaries.",
            "NEB status (when available) is a lead for identifying an off-target eclipsing star; must inspect ground-based follow-up for which neighbor and sky coordinates.",
            "EB status is not proof that the TESS target is the eclipsing source; must verify directly before making on-target control labels.",
            "The TOI tables and timing may have changed after original TESS sectors; compare to exact 2-minute SPOC source light curves and event ephemerides later.",
            "Do not mix this new potential cohort with the original 56 TESS sources, or treat multiple TOIs around one TIC as independent stars.",
            "No original NASA ExoMiner model scores, moment-centroid values, or event classifier labels were consulted for sample screening.",
            "No candidate selection or science inference may be announced until individual evidence inspection and an explicit frozen manifest."
        ]
    }
    (out/"ExoFOP_external_NEBS_and_EBS_screening_summary.json").write_text(
        json.dumps(report, indent=2)+"\n",encoding="utf-8"
    )
    print(json.dumps({
        "source_sha256": snapshot_hash,
        "screen_counts": dict(counts),
        "distinct_catalog_NEB_potential_targets":len(ordered["NEB"]),
        "distinct_catalog_EB_potential_targets":len(ordered["EB"]),
        "broad_FP_status_followup_review_distinct_TICs":len(ordered["FP"]),
        "first_12_NEB_TOI_only_preliminary": [x["TOI"] for x in selected["NEB"]],
        "first_12_EB_TOI_only_preliminary": [x["TOI"] for x in selected["EB"]],
        "first_12_FP_TOI_only_preliminary": [x["TOI"] for x in selected["FP"]],
        "ground_truth_confirmed":0,
        "centroid_measurements_performed":0
    },indent=2),flush=True)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",default=".")
    p.add_argument("--out",required=True)
    p.add_argument("--input-csv")
    a=p.parse_args()
    run(a.repo_root,a.out,a.input_csv)
