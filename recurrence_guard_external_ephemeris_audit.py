"""Post-outcome external *stellar* eclipse ephemeris comparison.

Inputs are the ORIGINAL archived warnings from the frozen 13-star Kepler Q6
experiment, with SHA-256 verification. Published Kepler-35 and Kepler-1647
eclipse ephemerides are used ONLY AFTER the detector has already run.
This is physically meaningful corroboration, but NOT an independent test of
the recurrence method, because the two cases were inspected after selection.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
import numpy as np

from real_spsd_external_cohort import load_frozen_star
from kepler_preprocessing import normalize_flux

EXPECTED_WARNING_CSV_SHA = "85a6000382a2911a072d637611e9eb85c38be5a56c5b3f423b94151c3e9d532f"
BKJD_REFERENCE_BJD = 2454833.0

PUBLICATION = {
    9837578: {
        "name":"Kepler-35",
        "binary_period_days":20.733748565,
        "primary_eclipse_epoch_bjd":2454965.847,
        "secondary_phase_from_primary":None,
        "reference":"NASA Exoplanet Archive, Q1-Q17 DR25 KOI-2937.01 binary-like false positive; Welsh et al. (2012)",
        "source_url":"https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-35",
        "file_sha256":"c401d42c2939a9a218582268cd050a09d976b2404256eeaf177ff39b3555e2d2"
    },
    5473556: {
        "name":"Kepler-1647",
        "binary_period_days":11.258825027,
        "primary_eclipse_epoch_bjd":2454967.738,
        "secondary_phase_from_primary":0.5526,
        "reference":"NASA Exoplanet Archive Q1-Q17 DR25 KOI-2939.01; secondary eclipse phase offset reported by Kostov et al. (2016)",
        "source_url":"https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-1647",
        "file_sha256":"7e1d100455f556d427a64f8a6a5cd2f6da200ef73eb5dab7fabad1008c1890e3"
    }
}


def nearest_published_eclipse(time_bkjd, reference):
    p=float(reference["binary_period_days"])
    zero=float(reference["primary_eclipse_epoch_bjd"])-BKJD_REFERENCE_BJD
    candidates=[]
    types=[("primary",0.)]
    if reference["secondary_phase_from_primary"] is not None:
        types.append(("secondary",float(reference["secondary_phase_from_primary"])))
    for kind, phase in types:
        ref=zero+phase*p
        orbit=round((time_bkjd-ref)/p)
        eclipse=ref+orbit*p
        candidates.append({
            "eclipse_type":kind, "published_eclipse_phase":phase,
            "expected_eclipse_bkjd":float(eclipse),
            "residual_days":float(time_bkjd-eclipse),
            "residual_hours":float((time_bkjd-eclipse)*24.),
            "published_stellar_period_days":p,
            "cycle":int(orbit)
        })
    return min(candidates,key=lambda e:abs(e["residual_days"]))


def load_protected_rows(csv_path):
    data=Path(csv_path).read_bytes()
    digest=hashlib.sha256(data).hexdigest()
    if digest!=EXPECTED_WARNING_CSV_SHA:
        raise ValueError("Warning CSV is not the unmodified frozen 13-star output")
    entries=list(csv.DictReader(data.decode("utf-8").splitlines()))
    # No test hypothesis is selected by this function; all protected events
    # from the observational output must be retained, including extra ones.
    retained=[r for r in entries if str(r["protected_as_periodic"]).lower()=="true"]
    if not retained:
        raise ValueError("Original protected-warning file unexpectedly contains no protected events")
    if any(int(r["kic"]) not in PUBLICATION for r in retained):
        raise ValueError("Additional protected events lack a published independent timing model: do not silently omit")
    return retained


def evaluate_timings(rows):
    out=[]
    for r in rows:
        kic=int(r["kic"])
        w=float(r["warning_time_bkjd"])
        reference=PUBLICATION[kic]
        info=nearest_published_eclipse(w,reference)
        out.append({
            "kic":kic,"name":reference["name"],"product":r["product"],
            "warning_time_bkjd":w, "recovered_period_without_published_input":float(r["recovered_period_days"]),
            "supporting_other_cycles":int(r["supporting_other_cycles"]),
            "n_other_cycles_examined":int(r["other_cycles_with_valid_windows"]),
            "original_step_depth_fraction":float(r["jump_fraction"]),
            "n_original_instrument_quality_SPSD_match":r["archival_spsd_event_near_warning"],
            "ephemeris_publication":reference["reference"],
            **info
        })
    return sorted(out,key=lambda d:d["kic"])


def plot_actual_flux(rows, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(len(rows),1,figsize=(10,4*len(rows)),squeeze=False)
    for i,item in enumerate(rows):
        ax=axs[i,0]
        kic=int(item["kic"])
        t,sap,pdc,quality,extra=load_frozen_star(kic,6,500)
        if extra["source"]["sha256"]!=PUBLICATION[kic]["file_sha256"]:
            raise ValueError(f"NASA FITS checksum changed for KIC {kic}")
        s=normalize_flux(sap);d=normalize_flux(pdc)
        center=float(item["expected_eclipse_bkjd"])
        warning=float(item["warning_time_bkjd"])
        near=np.abs(t-center)<.5
        ax.scatter(t[near]-center,s[near],s=16,label="Original SAP",alpha=.8)
        ax.scatter(t[near]-center,d[near],s=16,label="NASA PDC-corrected PDCSAP",alpha=.8)
        ax.axvline(0,color="black",ls="--",label="Published stellar eclipse center")
        ax.axvline(warning-center,color="tab:red",ls=":",label="Frozen algorithm warning onset")
        ax.set(xlabel="Time from published binary eclipse center (days)",
               ylabel="Locally normalized brightness",
               title=f"{item['name']}: protected {item['product']} warning; eclipse offset {item['residual_hours']:.2f} h")
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out/"two_protected_real_eclipse_source_windows.png",dpi=175)
    plt.close(fig)


def run(warnings,out):
    protected=load_protected_rows(warnings)
    timings=evaluate_timings(protected)
    folder=Path(out);folder.mkdir(parents=True,exist_ok=True)
    with (folder/"protected_warnings_vs_published_stellar_eclipses.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(timings[0]))
        writer.writeheader();writer.writerows(timings)
    plot_actual_flux(timings,folder)
    report={
        "scope":"Post-hoc observational ephemeris corroboration for previously selected protected warnings; not independent validation",
        "n_original_protected_warning_rows":len(timings),
        "archived_original_warning_csv_sha256":EXPECTED_WARNING_CSV_SHA,
        "eclipse_timing_comparisons":timings,
        "limits":[
            "Candidate system choice and source cases were known before this comparison and may bias physical interpretation.",
            "Planet orbital periods are not the published binary eclipse periods used here.",
            "Close eclipse timing and real flux morphology support stellar association, but are not proof that all warnings are astrophysical.",
            "This visualization does not estimate instrument sensitivity, astrophysical false-alarm rates, or new planet discovery."
        ]}
    (folder/"published_ephemeris_posthoc_summary.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2),flush=True)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--warnings",required=True)
    p.add_argument("--out",default="results/recurrence_ephemeris_check")
    a=p.parse_args()
    run(a.warnings,a.out)
