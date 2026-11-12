"""Synthetic engineering regression tests for TESS original 56-star event pairing.

These are NOT astrophysical validation data and do NOT claim a new planet.
"""
import numpy as np
import pandas as pd
import pytest
from pathlib import Path
from tess_56star_paired_pointing_motion_robustness_nov12 import read_original_events,SOURCES

def make_fake_original_pairing(tmp_path):
    records={}
    for cohort,relative,cor_suffix,raw_suffix,nstar in SOURCES:
        folder=tmp_path/relative
        folder.mkdir(parents=True,exist_ok=True)
        excess=18 if nstar==32 else 6
        for i in range(nstar):
            uid=f"{int(100000000 if nstar==32 else 200000000)+i}-1-S6"
            n=5 if i<excess else 4
            rows=[]
            for event in range(n):
                rows.append({
                  "orbit_index":event,
                  "predicted_NASA_TCE_center_BTJD":1500.+event*2,
                  "local_pre_post_vector_norm_pixels":.004+i*.00001,
                  "local_in_minus_flanking_vector_norm_pixels":.001+i*.000001})
            cor=pd.DataFrame(rows)
            raw=cor.copy()
            cor["local_pre_post_vector_norm_pixels"]*=.65
            cor["local_in_minus_flanking_vector_norm_pixels"]*=.85
            cp=folder/(uid+cor_suffix);rp=folder/(uid+raw_suffix)
            cor.to_csv(cp,index=False);raw.to_csv(rp,index=False)
            records[uid]=(cp,rp)
    return records

def test_all_56_fake_source_orbit_pairs_well_accounted(tmp_path):
    make_fake_original_pairing(tmp_path)
    result=read_original_events(tmp_path)
    assert len(result)==248
    assert result.uid.nunique()==56
    assert not result.duplicated(["uid","orbit_index"]).any()
    assert (result.prepost_raw_pixels>result.prepost_corrected_pixels).all()

def test_source_raw_counterpart_missing_not_silently_counted_negative(tmp_path):
    src=make_fake_original_pairing(tmp_path)
    next(iter(src.values()))[1].unlink()
    with pytest.raises(ValueError,match="Missing matching original raw"):
        read_original_events(tmp_path)

def test_mismatched_nasa_transit_epochs_rejected(tmp_path):
    src=make_fake_original_pairing(tmp_path)
    raw=next(iter(src.values()))[1]
    df=pd.read_csv(raw)
    df.loc[0,"predicted_NASA_TCE_center_BTJD"]+=.12
    df.to_csv(raw,index=False)
    with pytest.raises(ValueError,match="original same-source orbit alignment"):
        read_original_events(tmp_path)

def test_nonfinite_centroid_input_cannot_be_imputed_with_zero(tmp_path):
    src=make_fake_original_pairing(tmp_path)
    raw=next(iter(src.values()))[1]
    df=pd.read_csv(raw)
    df.loc[0,"local_pre_post_vector_norm_pixels"]=np.nan
    df.to_csv(raw,index=False)
    with pytest.raises(ValueError,match="Invalid measured"):
        read_original_events(tmp_path)

def test_duplicate_same_source_orbit_must_fail(tmp_path):
    src=make_fake_original_pairing(tmp_path)
    raw=next(iter(src.values()))[1]
    df=pd.read_csv(raw)
    df.loc[1,"orbit_index"]=df.loc[0,"orbit_index"]
    df.loc[1,"predicted_NASA_TCE_center_BTJD"]=df.loc[0,"predicted_NASA_TCE_center_BTJD"]
    df.to_csv(raw,index=False)
    with pytest.raises(ValueError,match="Duplicate original orbit"):
        read_original_events(tmp_path)
