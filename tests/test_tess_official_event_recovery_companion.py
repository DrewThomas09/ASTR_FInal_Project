"""Synthetic provenance test of the NASA TESS extra postprocessor.

Real NASA case must still run in the separate Actions workflow.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from astropy.io import fits

from tess_official_event_recovery_companion import (
    read_official_predictions,load_original_tess_fits,find_matching_lc_fits,
    run_companion
)


def make_fits(path,tic=167526485,sector=6):
    t=np.arange(1460.,1487.,.02043,dtype=float)
    flux=1+np.random.default_rng(41).normal(0,.00012,len(t))
    p=5.01159; epoch=1469.68127; dur=6.96083/24
    phase=(t-epoch+.5*p)%p-.5*p
    flux[np.abs(phase)<dur/2]-=.01086
    columns=[
        fits.Column(name="TIME",format="D",array=t),
        fits.Column(name="PDCSAP_FLUX",format="D",array=flux*100000),
        fits.Column(name="QUALITY",format="K",array=np.zeros(len(t),dtype=np.int64))
    ]
    hdul=fits.HDUList([fits.PrimaryHDU(),fits.BinTableHDU.from_columns(columns)])
    hdul[0].header["TICID"]=tic
    hdul[0].header["SECTOR"]=sector
    hdul.writeto(path,overwrite=True)
    return path


def make_nasa_csv(path):
    path.write_text(
        "# Version Number: 2.4.0\n"
        "# Task: planet-validation\n"
        "# ExoMiner Model: single\n"
        "uid,target_id,sector_run,tce_period,tce_duration,tce_time0bk,score,prediction\n"
        "167526485-1-S6,167526485,6,5.01159,6.96083,1469.68127,.0203,NOT_PC\n"
    )
    return path


def test_recovery_companion_creates_event_analysis_without_editing_nasa_score(tmp_path):
    original=tmp_path/"tess_sample_lc.fits"
    make_fits(original)
    predictions=make_nasa_csv(tmp_path/"pred.csv")
    original_bytes=predictions.read_bytes()
    report=run_companion(predictions,tmp_path,tmp_path/"derived")
    assert report["n_official_TCEs"]==1
    rec=report["events"][0]
    assert rec["NASA_official_pretrained_exominer_score_unmodified"]==.0203
    assert rec["NASA_official_pretrained_model_label_unmodified"]=="NOT_PC"
    assert rec["additional_physical_event_morphology_only"]["usable_event_count"]>=3
    assert rec["additional_physical_event_morphology_only"]["median_signed_local_depth_fraction"]>.008
    assert predictions.read_bytes()==original_bytes
    assert (tmp_path/"derived"/rec["event_row_file"]).is_file()


def test_model_csv_must_be_official_planet_validation(tmp_path):
    p=make_nasa_csv(tmp_path/"nasa.csv")
    s=p.read_text().replace("planet-validation","phot-vetting")
    p.write_text(s)
    with pytest.raises(ValueError,match="Wrong NASA ExoMiner inference task"):
        read_official_predictions(p)


def test_source_FITS_with_wrong_target_or_sector_is_rejected(tmp_path):
    p=make_fits(tmp_path/"actual_lc.fits",tic=167526485,sector=6)
    with pytest.raises(ValueError,match="TIC ID differs"):
        load_original_tess_fits(p,167526486,6)
    with pytest.raises(ValueError,match="sector differs"):
        load_original_tess_fits(p,167526485,7)


def test_cannot_manually_choose_multiple_fits_to_affect_score(tmp_path):
    make_fits(tmp_path/"a_lc.fits")
    make_fits(tmp_path/"b_lc.fits")
    with pytest.raises(RuntimeError,match="Multiple different"):
        find_matching_lc_fits(tmp_path,167526485,6)


def test_preserves_real_quality_flags(tmp_path):
    p=make_fits(tmp_path/"tess_test_lc.fits")
    with fits.open(p,mode="update") as h:
        h[1].data["QUALITY"][3]=16
        h.flush()
    t,f,meta=load_original_tess_fits(p,167526485,6)
    assert meta["original_quality_zero_cadences"]==1321
    assert np.all(f>0)
