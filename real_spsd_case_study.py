"""A known REAL Kepler Sudden Pixel Sensitivity Dropout (SPSD) case study.

KIC 7461601 Q6 is demonstrated in the official STScI/Mast tutorial; quality
1152 combines cosmic ray in optimal aperture and sudden sensitivity dropout.

This is intentionally a known-positive *illustrative* case, not independent
detection/vetting performance. Quality flag is used ONLY after time-series
processing and to annotate the plot, never to supply the detector's epoch.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from real_kepler_lightcurve import fetch_kepler_quarter
from kepler_preprocessing import normalize_flux
from localized_discontinuity import localized_downward_step_mask


def marked_spsd_cadences(time, quality):
    """Return independently archived time labels; does not involve the fit."""
    t=np.asarray(time,float)
    q=np.asarray(quality,np.int64)
    if t.shape!=q.shape:
        raise ValueError("Misaligned time and quality arrays")
    finite=np.isfinite(t)
    flags=((q & 1024)!=0)&finite
    combined=(q==1152)&finite
    return {"spsd_bit_times":t[flags],"flag_1152_times":t[combined]}


def select_published_example(flags,nominal_time=547.):
    """Select already-published quality-flag reference, not the algorithm output."""
    x=np.asarray(flags["flag_1152_times"],float)
    if not len(x):
        x=np.asarray(flags["spsd_bit_times"],float)
    if not len(x):
        return None
    return float(x[np.argmin(abs(x-nominal_time))])


def case_study(output="results/real_spsd_case"):
    frozen=json.loads(Path("KNOWN_SPSD_REAL_STAR_FROZEN.json").read_text())
    kic=frozen["target"]["kic"];quarter=frozen["target"]["quarter"]
    _,_,source=fetch_kepler_quarter(f"KIC {kic}",quarter)
    from astropy.io import fits
    raw_path=Path("data/kepler_fits")/source["file"]
    if source["file"]!=frozen["expected_source"]:
        raise ValueError("Fetched source differs from predeclared natural SPSD example")
    with fits.open(raw_path,memmap=False) as h:
        t=np.asarray(h[1].data["TIME"],float)
        sap=np.asarray(h[1].data["SAP_FLUX"],float)
        pdc=np.asarray(h[1].data["PDCSAP_FLUX"],float)
        quality=np.asarray(h[1].data["SAP_QUALITY"],np.int64)
    valid=np.isfinite(t)&np.isfinite(sap)&np.isfinite(pdc)&(sap>0)&(pdc>0)
    t,sap,pdc,quality=t[valid],sap[valid],pdc[valid],quality[valid]
    labels=marked_spsd_cadences(t,quality)
    marked=select_published_example(labels)
    # Include flagged rows to visualize and investigate the known defect.
    # This differs from our standard planet-recovery input quality policy.
    raw_flat=normalize_flux(sap)
    pdc_flat=normalize_flux(pdc)
    settings=json.loads(Path("LOCALIZED_STEP_STUDY_FROZEN_2026_11_07.json").read_text())["preprocessing"]
    sap_keep,sap_diag=localized_downward_step_mask(t,raw_flat,settings)
    pdc_keep,pdc_diag=localized_downward_step_mask(t,pdc_flat,settings)
    tol=float(settings["step_mask_half_width_days"])
    def near_reference(report):
        if marked is None:return None
        return bool(any(abs(e["time_bkjd"]-marked)<tol for e in report["detected_events"]))
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    summary={
      "scope":"ONE previously documented real Kepler SPSD; NOT independent detector accuracy",
      "target":kic,"quarter":quarter,
      "precommitted_source":source["file"],"original_fits_sha256":source["sha256"],
      "original_FITS_cadences":len(t),
      "n_quality_flag_1152":int(len(labels["flag_1152_times"])),
      "n_spsd_bit_flagged":int(len(labels["spsd_bit_times"])),
      "chosen_reference_event_bkjd":marked,
      "sap_original_quality_flags_included_for_illustration":True,
      "sap_detected_onsets":sap_diag["detected_events"],
      "pdc_detected_onsets":pdc_diag["detected_events"],
      "sap_detected_near_known_spsd":near_reference(sap_diag),
      "pdc_detected_near_known_spsd":near_reference(pdc_diag),
      "difference_in_interpretation":"SAP is uncorrected aperture photometry, PDCSAP includes Kepler pipeline corrections. A difference in step detection on a labeled event is illustrative, not proof of general detector performance.",
      "source_note":frozen["target"]["reference"]}
    (out/"real_spsd_case_summary.json").write_text(json.dumps(summary,indent=2))
    if marked is None: 
        print(json.dumps(summary,indent=2),flush=True)
        return summary
    fig,axes=plt.subplots(2,1,figsize=(10,7),sharex=True)
    view=(t>=marked-2.5)&(t<=marked+2.5)
    for ax,y,name,diag in zip(axes,(raw_flat,pdc_flat),
                             ("Original Kepler SAP_FLUX","PDC-corrected PDCSAP_FLUX"),
                             (sap_diag,pdc_diag)):
        ax.scatter(t[view],y[view],s=8,color="black")
        ax.axvline(marked,color="firebrick",ls="--",label="Archived SPSD quality flag")
        for e in diag["detected_events"]:
            if abs(e["time_bkjd"]-marked)<=2.5:
                ax.axvline(e["time_bkjd"],color="royalblue",alpha=.8,
                           label="Our local step warning")
        ax.set(ylabel="Locally normalized flux",title=name)
        ax.legend(loc="best",fontsize=8)
    axes[-1].set(xlabel="Time (BKJD)",xlim=(marked-2.5,marked+2.5))
    fig.suptitle("KIC 7461601 Q6: published instrumental defect (case study only)")
    fig.tight_layout()
    fig.savefig(out/"known_kepler_spsd_sap_vs_pdc.png",dpi=160)
    plt.close(fig)
    print(json.dumps(summary,indent=2),flush=True)
    return summary


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default="results/real_spsd_case")
    args=parser.parse_args()
    case_study(args.out)
