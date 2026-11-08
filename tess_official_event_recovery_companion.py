"""Attach an independent *descriptive* recovery diagnostic to official NASA TESS inference.

NASA ExoMiner++ v2.4.0 already performs its own vetted model diagnostics.
This script never modifies its neural model, TFRecords, predictions, or threshold.
Its additional event measurements are an exploratory physics companion for
the same original MAST TESS SPOC PDCSAP light-curve FITS.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from kepler_event_shape_diagnostics import (
    event_shape_measurements,summarize_shape_events
)


def read_official_predictions(path):
    """NASA model CSV includes commented version/provenance header."""
    p=Path(path)
    head=p.read_text(encoding="utf-8")[:9000]
    if "# Task: planet-validation" not in head:
        raise ValueError("Wrong NASA ExoMiner inference task")
    if "# ExoMiner Model: single" not in head:
        raise ValueError("Expected official pretrained single-model pilot")
    rows=pd.read_csv(p,comment="#")
    needed={"uid","target_id","sector_run","tce_period","tce_duration",
            "tce_time0bk","score","prediction"}
    if not needed.issubset(rows.columns):
        raise ValueError("Missing published NASA inference columns")
    if len(rows)==0 or rows.score.isna().any() or not rows.score.between(0,1).all():
        raise ValueError("No valid official NASA output scores")
    return rows,head


def load_original_tess_fits(path,tic,sector):
    from astropy.io import fits
    raw=Path(path).read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    with fits.open(path,memmap=False) as hdus:
        header=hdus[0].header
        if int(header.get("TICID",-1))!=int(tic):
            raise ValueError("Official light-curve FITS TIC ID differs from model result")
        if int(header.get("SECTOR",-1))!=int(sector):
            raise ValueError("Official FITS sector differs from scored DV sector")
        table=hdus[1].data
        time=np.asarray(table["TIME"],dtype=float)
        flux=np.asarray(table["PDCSAP_FLUX"],dtype=float)
        quality=np.asarray(table["QUALITY"],dtype=np.int64)
    good=np.isfinite(time)&np.isfinite(flux)&(flux>0)&(quality==0)
    t=time[good]
    f=flux[good]
    if len(t)<500 or np.any(np.diff(t)<=0):
        raise ValueError("Insufficient quality-zero original SPOC TESS cadences")
    # Preserve original telescope flux, only divide by a global median
    # for numerical scaling; no smoothing, resampling, artificial transit.
    f=f/np.median(f)
    return t,f,{
        "source_fits_filename":Path(path).name,
        "original_FITS_sha256":digest,
        "original_quality_zero_cadences":int(len(t)),
        "original_time_unit":"BTJD (BJD - 2457000), as documented by TESS SPOC",
        "source_processing":"Original NASA SPOC PDCSAP_FLUX, QUALITY==0, division by global flux median; no detrending; local pre/post sidebands in the additional analysis only."
    }


def find_matching_lc_fits(directory,tic,sector):
    """Never choose an unrelated sector or target by filename alone."""
    from astropy.io import fits
    base=Path(directory)
    matched=[]
    for path in base.rglob("*.fits"):
        if not path.name.lower().endswith("_lc.fits"):
            continue
        try:
            h=fits.getheader(path,0)
            if int(h.get("TICID",-1))==int(tic) and int(h.get("SECTOR",-1))==int(sector):
                matched.append(path)
        except Exception:
            continue
    if not matched:
        raise FileNotFoundError("No original TESS SPOC light curve FITS with matching TIC and sector found under NASA pipeline outputs")
    # An unambiguous source is required; no arbitrary selection of multiple
    # versions based on desired inference score or measured recovery.
    if len(matched)!=1:
        raise RuntimeError("Multiple different fitting original TESS light curves, resolve provenance before comparison")
    return matched[0]


def run_companion(nasa_predictions,original_fits_dir,out_dir):
    nasa,header=read_official_predictions(nasa_predictions)
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    records=[]
    for _,row in nasa.iterrows():
        sector_str=str(row["sector_run"])
        if "-" in sector_str:
            # Multi-sector source may need multiple files and epoch correction.
            raise ValueError("This first companion pilot supports single-sector SPOC data only")
        tic=int(row["target_id"])
        sector=int(sector_str)
        file=find_matching_lc_fits(original_fits_dir,tic,sector)
        t,f,source=load_original_tess_fits(file,tic,sector)
        duration_days=float(row["tce_duration"])/24.0
        events=event_shape_measurements(
            t,f,float(row["tce_period"]),float(row["tce_time0bk"]),duration_days)
        measures=summarize_shape_events(events)
        base=str(row["uid"]).replace("/","_")
        pd.DataFrame(events).to_csv(out/f"{base}_actual_original_TESS_event_shape.csv",index=False)
        records.append({
            "official_NASA_TCE_uid":str(row["uid"]),
            "TIC_ID":tic,"sector":sector,
            "NASA_official_pretrained_exominer_score_unmodified":float(row["score"]),
            "NASA_official_pretrained_model_label_unmodified":str(row["prediction"]),
            "NASA_original_TCE_period_days":float(row["tce_period"]),
            "NASA_original_TCE_duration_hours":float(row["tce_duration"]),
            "NASA_original_TCE_epoch_BTJD":float(row["tce_time0bk"]),
            "MAST_original_lightcurve":source,
            "additional_physical_event_morphology_only":measures,
            "event_row_file":f"{base}_actual_original_TESS_event_shape.csv"
        })
    result={
        "source":"Official NASA ExoMiner++ inference AND its original public MAST SPOC photometry",
        "n_official_TCEs":len(nasa),
        "n_additional_descriptive_event_series":len(records),
        "official_nasa_model_version_header":header.splitlines()[:12],
        "no_modified_NASA_scores":True,
        "no_new_planets_or_physical_validation":True,
        "no_model_gain_or_holdout_CI_claim":True,
        "events":records,
        "limitation":"Recovery is measured at the original NASA TCE period/epoch as a separately coded companion; official NASA already uses light-curve and artifact diagnostics. This is not a trained modification of ExoMiner++."
    }
    (out/"tess_official_inference_plus_unchanged_score_event_recovery.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({
        "n_official_TCEs":len(nasa),
        "results":[{"uid":r["official_NASA_TCE_uid"],
                    "official_nasa_score":r["NASA_official_pretrained_exominer_score_unmodified"],
                    "official_nasa_label":r["NASA_official_pretrained_model_label_unmodified"],
                    "usable_original_event_windows":r["additional_physical_event_morphology_only"]["usable_event_count"],
                    "median_local_depth":r["additional_physical_event_morphology_only"]["median_signed_local_depth_fraction"],
                    "median_step_over_depth_plus_noise":r["additional_physical_event_morphology_only"]["median_persistent_step_over_depth_plus_noise"]}
                   for r in records],
        "important":"NO official ExoMiner model change or independently validated planet."
    },indent=2),flush=True)
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--predictions",required=True)
    p.add_argument("--original-fits-root",required=True)
    p.add_argument("--out",default="results/nasa_exominer_official_pilot/physical_recovery_companion")
    a=p.parse_args()
    run_companion(a.predictions,a.original_fits_root,a.out)
