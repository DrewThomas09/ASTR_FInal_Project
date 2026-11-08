"""Exploratory Kepler-47 light-curve visualization against published stellar eclipses.

This is a POST-HOC physical illustration. Kepler-47 was selected only after
the 12-star instrument cohort exposed its warning concentration. The detector
and warning timestamps are immutable archival outputs; no tuning or inference
of a new planet is attempted. Source Kepler FITS hash is fixed to original run.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from kepler47_eclipse_warning_check import (
    KEPLER47, EPHEMERIDES, BKJD_REFERENCE_BJD,
    load_original_warnings, analyze_original_warnings, nearest_published_eclipse
)

EXPECTED_KEPLER47_Q6_FITS_SHA256 = (
    "3ab0b21547c32cce04b474ecfd210b894632552121d70d9821fbb677997d332c"
)


def phase_primary(time):
    """Dimensionless stellar binary orbital phase, primary eclipse at 0."""
    values=np.asarray(time,dtype=float)
    p=EPHEMERIDES["primary"]["period_days"]
    ref=EPHEMERIDES["primary"]["epoch_bjd"]-BKJD_REFERENCE_BJD
    return np.mod((values-ref)/p,1.0)


def secondary_phase():
    """Secondary eclipse is not forced to exactly 0.5 in an eccentric binary."""
    secondary=EPHEMERIDES["secondary"]["epoch_bjd"]-BKJD_REFERENCE_BJD
    return float(phase_primary(secondary))


def load_original_kepler47():
    from astropy.io import fits
    from real_kepler_lightcurve import fetch_kepler_quarter
    from real_spsd_external_cohort import common_flux_rows
    _,_,source=fetch_kepler_quarter("KIC 10020423",6)
    if source["sha256"] != EXPECTED_KEPLER47_Q6_FITS_SHA256:
        raise ValueError("Original Kepler-47 FITS checksum changed")
    path=Path("data/kepler_fits")/source["file"]
    with fits.open(path,memmap=False) as hdus:
        tab=hdus[1].data
        t=np.asarray(tab["TIME"],float)
        sap=np.asarray(tab["SAP_FLUX"],float)
        pdc=np.asarray(tab["PDCSAP_FLUX"],float)
        quality=np.asarray(tab["SAP_QUALITY"],np.int64)
    t,sap,pdc,quality,invalid=common_flux_rows(t,sap,pdc,quality,500)
    from kepler_preprocessing import normalize_flux
    return t,normalize_flux(sap),normalize_flux(pdc),quality,invalid,source


def summarize_flux_at_archived_warnings(t,sap,pdc,warning_table):
    rows=[]
    for record in warning_table:
        nearest_index=int(np.argmin(np.abs(t-float(record["warning_time_bkjd"]))))
        time=float(t[nearest_index])
        if abs(time-float(record["warning_time_bkjd"]))>1e-5:
            raise ValueError("Warning time does not exactly match Kepler cadence")
        rows.append({
            **record, "binary_phase":float(phase_primary(time)),
            "observed_time_bkjd":time,
            "normalized_sap_at_warning":float(sap[nearest_index]),
            "normalized_pdcsap_at_warning":float(pdc[nearest_index])})
    return rows


def render(t,sap,pdc,warning_table,out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    phase=phase_primary(t)
    sec=secondary_phase()
    fig,axes=plt.subplots(2,1,figsize=(11,8),sharex=True)
    for ax,data,name,indicator in [
        (axes[0],sap,"Original SAP light curve", "seen_in_SAP"),
        (axes[1],pdc,"NASA PDCSAP light curve", "seen_in_PDCSAP")]:
        ax.scatter(phase,data,s=3,alpha=.4,label="Original observed Kepler cadences")
        ax.axvline(0.,color="tab:red",ls="--",lw=1.2,label="Published primary eclipse")
        ax.axvline(sec,color="tab:orange",ls="--",lw=1.2,
                   label="Published secondary eclipse")
        ax.axvline(1.,color="tab:red",ls="--",lw=1.2)
        # These are original warning timestamps; not fitted to this image.
        wphase=[float(phase_primary(r["warning_time_bkjd"]))
                for r in warning_table if r[indicator]]
        ax.scatter(wphase,[1.015]*len(wphase),color="black",s=35,marker="v",
                   label="Preexisting step warnings (phase shown at top)")
        ax.set(ylabel="301-cadence median-normalized flux",
               title=name)
        ax.legend(loc="lower center",fontsize=7,ncol=2)
        ax.set_ylim(np.nanpercentile(data,.5)-.005,1.035)
    axes[-1].set(xlabel="Binary orbital phase (primary eclipse = 0)",
                 xlim=(0,1))
    fig.suptitle("Kepler-47 Q6: real SAP vs PDCSAP folded at published STELLAR binary period")
    fig.tight_layout()
    fig.savefig(out/"kepler47_original_sap_pdc_binary_phase.png",dpi=175)
    plt.close(fig)

    # Select first three warnings by chronological order, not strength or score.
    first=warning_table[:3]
    fig,axs=plt.subplots(len(first),1,figsize=(10,9),sharex=False)
    for ax,row in zip(np.atleast_1d(axs),first):
        e=nearest_published_eclipse(row["warning_time_bkjd"])
        center=e["expected_eclipse_bkjd"]
        view=np.abs(t-center)<.5
        ax.scatter(t[view]-center,sap[view],s=13,marker=".",label="Original SAP")
        ax.scatter(t[view]-center,pdc[view],s=13,marker=".",label="Corrected PDCSAP")
        ax.axvline(0,ls="--",color="gray",label="Published eclipse center")
        ax.axvline(row["warning_time_bkjd"]-center,
                   ls=":",color="black",label="Preexisting step warning")
        ax.set(ylabel="Normalized flux",xlabel="Time relative to published stellar eclipse (days)",
               title=f"Warning at BKJD {row['warning_time_bkjd']:.3f}; closest {e['eclipse_type']} eclipse")
        ax.legend(fontsize=7,ncol=2)
    fig.tight_layout()
    fig.savefig(out/"kepler47_first_three_warning_lightcurve_windows.png",dpi=175)
    plt.close(fig)


def main(warnings_file,out):
    warnings=load_original_warnings(warnings_file)
    table=analyze_original_warnings(warnings)
    if len(table)!=7: raise ValueError("Original seven warning epochs changed")
    t,sap,pdc,quality,invalid,source=load_original_kepler47()
    rows=summarize_flux_at_archived_warnings(t,sap,pdc,table)
    output=Path(out);output.mkdir(parents=True,exist_ok=True)
    if len(t)!=4272: raise ValueError("Joint valid source cadence count differs from frozen run")
    summary={
        "study":"Kepler-47 known binary: POST-HOC physical light curve visualization",
        "kic":KEPLER47,"quarter":6,"n_valid_joint_cadences":len(t),
        "n_removed_nonjoint_valid_cadences":invalid,
        "fits_file":source["file"],"fits_sha256":source["sha256"],
        "published_binary_period_days":EPHEMERIDES["primary"]["period_days"],
        "published_secondary_eclipse_phase":secondary_phase(),
        "n_original_unique_warning_times":len(rows),
        "n_archived_spsd_bit_1024_cadences":int(np.sum((quality & 1024)!=0)),
        "interpretation":"A visual, post-hoc physical crosscheck only. Period and ephemerides were published independently. The star was picked AFTER warning output and cannot yield independent detection performance.",
        "literature":"Orosz et al. 2019 doi:10.3847/1538-3881/ab0ca0"}
    with (output/"warning_times_with_photometry.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        writer.writeheader();writer.writerows(rows)
    (output/"posthoc_flux_figure_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    render(t,sap,pdc,rows,output)
    print(json.dumps(summary,indent=2),flush=True)
    return summary


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--warnings",required=True)
    parser.add_argument("--out",default="results/kepler47_phase_fold")
    a=parser.parse_args()
    main(a.warnings,a.out)
