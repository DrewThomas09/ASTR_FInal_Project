"""Exploratory, POST-HOC ephemeris audit of warnings in Kepler-47 Q6.

This is NOT part of the prospectively frozen SPSD detection evaluation.
It uses only the archived candidate-warning times from GitHub Actions
42510882421, with independently published stellar-binary eclipses.

Citation: Orosz et al. (2019), AJ, DOI 10.3847/1538-3881/ab0ca0.
Published primary/secondary eclipse ephemerides (BJD); converts BKJD by
subtracting 2454833.0. Attribution of each warning to an eclipse is unproven.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

KEPLER47 = 10020423
SOURCE_ARTIFACT_RUN = 42510882421
EXPECTED_WARNINGS_SHA256 = "1be4b1c9e28f31ad506cfed191c7818a9aa8d1627a269a87d89de3c6bc0a0b99"
BKJD_REFERENCE_BJD = 2454833.0
EPHEMERIDES = {
    "primary": {"period_days":7.44837568,"epoch_bjd":2454963.246137},
    "secondary":{"period_days":7.44837596,"epoch_bjd":2454959.427964},
}
EXPLORATORY_WINDOWS_DAYS = (.1, .3)


def nearest_published_eclipse(time_bkjd):
    """Return nearest predicted primary or secondary eclipse and residual."""
    t = float(time_bkjd)
    possible = []
    for name, spec in EPHEMERIDES.items():
        base = spec["epoch_bjd"] - BKJD_REFERENCE_BJD
        period = spec["period_days"]
        cycle = round((t - base) / period)
        expected = base + cycle * period
        residual = t - expected
        possible.append({
            "eclipse_type":name,"published_eclipse_cycle":int(cycle),
            "expected_eclipse_bkjd":expected,
            "residual_days":residual,
            "absolute_residual_days":abs(residual)})
    return min(possible,key=lambda x:x["absolute_residual_days"])


def load_original_warnings(path):
    data = Path(path).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_WARNINGS_SHA256:
        raise ValueError("Original November 8 warnings changed: SHA-256 mismatch")
    return list(csv.DictReader(data.decode("utf-8").splitlines()))


def analyze_original_warnings(rows):
    """Deduplicate same-time SAP/PDC warnings to independent ONSET timestamps."""
    times = {}
    for row in rows:
        if int(row["kic"]) != KEPLER47:
            continue
        product=row["product"]
        if product not in ("SAP","PDCSAP"):
            raise ValueError("Unrecognized Kepler photometric product")
        stamp=float(row["warning_time_bkjd"])
        # Both products share exact Kepler TIME sampling; numerical rounding
        # only coalesces the same cadence, not neighboring physical eclipses.
        key=round(stamp,7)
        times.setdefault(key,{"time_bkjd":stamp,"products":set()})
        times[key]["products"].add(product)
    table=[]
    for record in sorted(times.values(),key=lambda d:d["time_bkjd"]):
        item=nearest_published_eclipse(record["time_bkjd"])
        table.append({
            "kic":KEPLER47,"warning_time_bkjd":record["time_bkjd"],
            "seen_in_SAP":"SAP" in record["products"],
            "seen_in_PDCSAP":"PDCSAP" in record["products"],
            **item,
            "within_0p1_day":item["absolute_residual_days"] <= .1,
            "within_0p3_day":item["absolute_residual_days"] <= .3})
    return table



def circular_phase_shift_sensitivity(table, windows=EXPLORATORY_WINDOWS_DAYS,
                                    n_offsets=20000):
    """Descriptive *post-hoc* phase-offset check, NOT a confirmatory p-value.

    Preserve all seven observed warning spacings; move their entire sequence
    together through one fixed published binary orbital cycle.  The phase grid
    is deterministic and equally spaced, without random sampling or tuning.
    This controls for warning clustering but not for post-outcome system choice
    or the choice of matching windows.  Treat as an exploratory diagnostic.
    """
    if n_offsets != 20000 or tuple(windows) != (.1, .3):
        raise ValueError("The documented exploratory sensitivity grid changed")
    if not table:
        return {"n_warning_epochs":0, "phase_shift_grid_size":n_offsets,
                "fractions_ge_observed":{}}
    times=[float(r["warning_time_bkjd"]) for r in table]
    binary_period=EPHEMERIDES["primary"]["period_days"]
    original_distances=[
        nearest_published_eclipse(time)["absolute_residual_days"] for time in times]
    summary={}
    for window in windows:
        observed=sum(d<=window for d in original_distances)
        exceed=0
        for index in range(n_offsets):
            shift=binary_period*index/n_offsets
            count=sum(nearest_published_eclipse(time+shift)
                      ["absolute_residual_days"]<=window for time in times)
            exceed+=int(count>=observed)
        summary[f"{window:.1f}_days"]={
            "observed_close_warnings":int(observed),
            "joint_shifts_with_at_least_observed":int(exceed),
            "fraction_of_joint_shifts_at_least_as_aligned":float(exceed/n_offsets)}
    return {"n_warning_epochs":len(times),
            "phase_shift_grid_size":n_offsets,
            "grid_span_days":binary_period,
            "fractions_ge_observed":summary,
            "inference_warning":"Exploratory conditional phase-shift sensitivity only: the binary system and windows were chosen after observing the warnings; NOT an independent astronomical hypothesis test."}


def report(table):
    n=len(table)
    return {
        "scope":"Exploratory post-hoc eclipse-phase comparison after frozen instrument-defect cohort",
        "original_run_id":SOURCE_ARTIFACT_RUN,
        "original_input_sha256":EXPECTED_WARNINGS_SHA256,
        "kic":KEPLER47,
        "n_distinct_warning_epochs":n,
        "n_within_0p1_day_of_published_stellar_eclipse":sum(x["within_0p1_day"] for x in table),
        "n_within_0p3_day_of_published_stellar_eclipse":sum(x["within_0p3_day"] for x in table),
        "n_warnings_in_both_products":sum(x["seen_in_SAP"] and x["seen_in_PDCSAP"] for x in table),
        "n_sap_distinct_epochs":sum(x["seen_in_SAP"] for x in table),
        "n_pdcsap_distinct_epochs":sum(x["seen_in_PDCSAP"] for x in table),
        "source_ephemeris":"Orosz et al. 2019, DOI 10.3847/1538-3881/ab0ca0",
        "exploratory_joint_phase_shift_sensitivity":circular_phase_shift_sensitivity(table),
        "limitations":[
            "Star and hypothesis were identified after inspecting the 12-source cohort. Results are post-hoc, not independent or a prespecified significance test.",
            "An epoch near a published eclipse suggests astrophysical contamination; it does not prove a specific predicted warning is caused by an eclipse.",
            "SAP and PDCSAP warnings at the same cadence are not independent. Seven distinct epochs, not twelve separate events.",
            "The two eclipse timing windows are exploratory and chosen after initial case review, not calibrated detection thresholds.",
            "No instrument ground truth or real mission-wide false-alarm probability is established. No exoplanet discovery is claimed."
        ]
    }


def audit(csv_path, out):
    rows=load_original_warnings(csv_path)
    table=analyze_original_warnings(rows)
    summary=report(table)
    if len(table)!=7:
        raise ValueError("Original Kepler-47 candidate-warning count differs from archived run")
    folder=Path(out);folder.mkdir(parents=True,exist_ok=True)
    (folder/"kepler47_ephemeris_audit.json").write_text(json.dumps(summary,indent=2)+"\n")
    with (folder/"kepler47_warning_ephemeris_matches.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(table[0]))
        writer.writeheader();writer.writerows(table)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(9,4))
        x=[r["warning_time_bkjd"] for r in table]
        residual=[r["residual_days"]*24 for r in table]
        ax.scatter(x,residual,s=60)
        ax.axhline(0,linestyle="--",linewidth=1,label="Predicted binary eclipse")
        ax.axhspan(-2.4,2.4,alpha=.08,label="Post-hoc 0.1-day window")
        for row in table:
            ax.annotate(row["eclipse_type"][0].upper(),
                        (row["warning_time_bkjd"],24*row["residual_days"]),
                        xytext=(4,4),textcoords="offset points",fontsize=8)
        ax.set(xlabel="Unflagged warning time (BKJD)",
               ylabel="Warning minus nearest predicted eclipse (hours)",
               title="Kepler-47: local-step warnings versus published stellar eclipses")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(folder/"kepler47_warning_eclipse_alignment.png",dpi=160)
        plt.close(fig)
    except ImportError:
        pass
    print(json.dumps(summary,indent=2),flush=True)
    return summary


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--warnings",required=True)
    parser.add_argument("--out",default="results/kepler47_eclipse_audit")
    a=parser.parse_args()
    audit(a.warnings,a.out)
