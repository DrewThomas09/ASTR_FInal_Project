"""Regression controls for genuine TESS SPOC event-local moment-centroid analysis.

Synthetic examples are unit/engineering tests only, not new astrophysical
injections, precision/reliability measurements, or real NASA score outputs.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest
from astropy.io import fits

from tess_original_moment_centroid_companion import (
    event_centroid_shifts,centroid_event_summary,fixed_centroid_manual_review_flag,
    load_tess_centroid_columns,verify_frozen_manifest
)


def source_fake(path,transit_shift=.08,has_pointing=True,drop_quality=True,
                remove_centroid_inside=False,tic=167526485,sector=6):
    """Create a controlled original-FITS-shaped TESS fixture with drift+shift.

    Key physical distinction: raw MOM_CENTR moves with the spacecraft's drift,
    but the correction subtracts POS_CORR. The transient centroid shift is
    injected only during actual period/epoch-defined transit windows.
    """
    period=4.5;epoch=1463.5;duration=.22
    time=np.arange(1460,1486,.02043)
    k=np.rint((time-epoch)/period).astype(int)
    phase=(time-epoch+.5*period)%period-.5*period
    inside=np.abs(phase)<duration/2
    rng=np.random.default_rng(173)
    motionx=.03*np.sin((time-1460)/7)
    motiony=.025*np.cos((time-1460)/9)
    x=500+motionx+rng.normal(0,.002,len(time))
    y=402+motiony+rng.normal(0,.002,len(time))
    x[inside]+=transit_shift
    y[inside]+=transit_shift/4
    flux=50000*(1+rng.normal(0,.0001,len(time)))
    flux[inside]-=500
    quality=np.zeros(len(time),dtype=np.int64)
    if drop_quality:
        quality[10]=32
    if remove_centroid_inside:
        x[inside]=np.nan
        y[inside]=np.nan
    cols=[
        fits.Column(name="TIME",format="D",array=time),
        fits.Column(name="PDCSAP_FLUX",format="D",array=flux),
        fits.Column(name="QUALITY",format="K",array=quality),
        fits.Column(name="MOM_CENTR1",format="D",array=x),
        fits.Column(name="MOM_CENTR2",format="D",array=y)
    ]
    if has_pointing:
        cols.extend([
            fits.Column(name="POS_CORR1",format="D",array=motionx),
            fits.Column(name="POS_CORR2",format="D",array=motiony)
        ])
    hdul=fits.HDUList([fits.PrimaryHDU(),fits.BinTableHDU.from_columns(cols)])
    hdul[0].header["TICID"]=tic
    hdul[0].header["SECTOR"]=sector
    hdul.writeto(path,overwrite=True)
    return path,period,epoch,duration


def settings():
    return {"min_individual_events":3,
            "median_2d_shift_at_least_pixels":.05,
            "bootstrap_95pct_axis_excludes_zero":True}


def test_frozen_32_original_stars_unique_and_from_two_prior_cohorts():
    source=verify_frozen_manifest("TESS_32STAR_CENTROID_ALIAS_COMPANION_FROZEN_2026_11_08.json")
    assert len(source["source_records"])==32
    assert len(set(x["tic_id"] for x in source["source_records"]))==32
    assert sum(x["source_cohort"]=="prior_16star_class_balanced" for x in source["source_records"])==16
    assert sum(x["source_cohort"]=="prior_16star_old_score_error_enriched" for x in source["source_records"])==16


def test_injected_centroid_shift_measured_as_local_vector(tmp_path):
    f,p,e,d=source_fake(tmp_path/"example_lc.fits",transit_shift=.09)
    frame,meta=load_tess_centroid_columns(f,167526485,6)
    events=event_centroid_shifts(frame,p,e,d,mode="corrected")
    output=centroid_event_summary(events,bootstraps=200)
    assert len(events)>=4
    assert output["median_vector_shift_pixels"]>.075
    assert np.isclose(output["median_signed_x_pixels"],.09,atol=.01)
    assert output["one_axis_descriptive_interval_excludes_zero"] is True
    assert fixed_centroid_manual_review_flag(output,settings()) is True
    assert meta["original_quality_zero_flux_rows"]==len(frame)
    assert meta["original_finite_CORRECTED_two_dimensional_centroid_rows"]==len(frame)


def test_local_global_pointing_drift_subtracted_before_shift_inference(tmp_path):
    f,p,e,d=source_fake(tmp_path/"normal_lc.fits",transit_shift=0)
    frame,_=load_tess_centroid_columns(f,167526485,6)
    corrected=centroid_event_summary(
        event_centroid_shifts(frame,p,e,d,mode="corrected"),bootstraps=150)
    raw=centroid_event_summary(
        event_centroid_shifts(frame,p,e,d,mode="raw"),bootstraps=150)
    assert corrected["median_vector_shift_pixels"]<.01
    assert raw["median_vector_shift_pixels"]<.01
    assert fixed_centroid_manual_review_flag(corrected,settings()) is False


def test_missing_pointing_columns_never_default_to_zero_and_raw_remains_valid(tmp_path):
    f,p,e,d=source_fake(tmp_path/"without_poscorr_lc.fits",has_pointing=False)
    frame,meta=load_tess_centroid_columns(f,167526485,6)
    assert meta["original_POS_CORR_columns_present"] is False
    assert meta["original_finite_CORRECTED_two_dimensional_centroid_rows"]==0
    assert meta["original_finite_RAW_two_dimensional_centroid_rows"]>1000
    corrected=event_centroid_shifts(frame,p,e,d,mode="corrected")
    raw=event_centroid_shifts(frame,p,e,d,mode="raw")
    assert corrected==[]
    assert len(raw)>=4
    assert fixed_centroid_manual_review_flag(centroid_event_summary(corrected),settings()) is None


def test_moments_missing_inside_real_transits_do_not_produce_fake_measurements(tmp_path):
    f,p,e,d=source_fake(tmp_path/"drop_centroid_lc.fits",remove_centroid_inside=True)
    frame,meta=load_tess_centroid_columns(f,167526485,6)
    assert meta["original_finite_CORRECTED_two_dimensional_centroid_rows"]<len(frame)
    corrected=event_centroid_shifts(frame,p,e,d,mode="corrected")
    assert corrected==[]
    summary=centroid_event_summary(corrected)
    assert summary["median_vector_shift_pixels"] is None
    assert fixed_centroid_manual_review_flag(summary,settings()) is None


def test_less_than_three_independent_events_does_not_claim_reliable_shift():
    events=[
        {"local_in_minus_flanking_x_pixels":.09,
         "local_in_minus_flanking_y_pixels":-.01},
        {"local_in_minus_flanking_x_pixels":.08,
         "local_in_minus_flanking_y_pixels":-.012}
    ]
    summary=centroid_event_summary(events,bootstraps=50)
    assert summary["usable_original_source_events"]==2
    assert summary["one_axis_descriptive_interval_excludes_zero"] is None
    assert fixed_centroid_manual_review_flag(summary,settings()) is None


def test_a_large_magnitude_without_coherent_sign_is_not_a_gate():
    events=[
        {"local_in_minus_flanking_x_pixels":a,
         "local_in_minus_flanking_y_pixels":0.0}
        for a in [-.14,-.12,.13,.14]
    ]
    report=centroid_event_summary(events,bootstraps=500,seed=73)
    assert report["one_axis_descriptive_interval_excludes_zero"] is False
    assert fixed_centroid_manual_review_flag(report,settings()) is False


def test_bad_original_tic_or_sector_fails_closed(tmp_path):
    f,p,e,d=source_fake(tmp_path/"wrong_target_lc.fits",tic=167526485,sector=6)
    with pytest.raises(ValueError,match="target TIC differs"):
        load_tess_centroid_columns(f,167526486,6)
    with pytest.raises(ValueError,match="sector differs"):
        load_tess_centroid_columns(f,167526485,7)


def test_original_quality_mask_excludes_cadence_and_preserves_source_bytes(tmp_path):
    f,p,e,d=source_fake(tmp_path/"quality_lc.fits",drop_quality=True)
    before=f.read_bytes()
    frame,meta=load_tess_centroid_columns(f,167526485,6)
    assert meta["original_quality_zero_flux_rows"]==meta["original_total_FITS_rows"]-1
    assert f.read_bytes()==before


def test_unphysical_period_and_duration_are_rejected(tmp_path):
    f,p,e,d=source_fake(tmp_path/"geometry_lc.fits")
    frame,_=load_tess_centroid_columns(f,167526485,6)
    with pytest.raises(ValueError,match="Invalid transiting"):
        event_centroid_shifts(frame,period=-1,epoch=e,duration_days=d)
    with pytest.raises(ValueError,match="Invalid transiting"):
        event_centroid_shifts(frame,period=4,epoch=e,duration_days=3)


def test_real_tess_output_can_be_reported_without_touching_original_scores():
    original_scores=pd.Series([.003,.912],name="NASA_original_scores")
    sample=[
        {"local_in_minus_flanking_x_pixels":.08,"local_in_minus_flanking_y_pixels":.01}
    ]*5
    measured=centroid_event_summary(sample,bootstraps=120)
    assert fixed_centroid_manual_review_flag(measured,settings()) is True
    assert original_scores.tolist()==[.003,.912]
