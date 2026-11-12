"""Synthetic source-control tests; never treated as actual astrophysical data."""
import numpy as np
import pandas as pd
import pytest
from tess_toi4255_source_pinned_quarter_phase_controls import (
    PHASE_OFFSETS,bootstrap_paired_event_angles,strict_original_event_values
)

def fixture_events():
    return pd.DataFrame([
        {"orbit_index":i,"original_ephemeris_predicted_center_BTJD":3010.+i*2.5,
         "raw_signed_x_CCD_pixels":-.01,
         "raw_signed_y_CCD_pixels":.012+(.001 if i%2 else 0),
         "pointing_subtracted_signed_x_CCD_pixels":-.01,
         "pointing_subtracted_signed_y_CCD_pixels":.0005+(.0002 if i%2 else 0),
         "original_PDCSAP_local_flux_depth":.01}
        for i in range(7)
    ])

def test_same_external_neighbor_away_alignment_resampling_is_paired():
    df=fixture_events()
    r=bootstrap_paired_event_angles(df,[1.,0.],seed=23,draws=1500)
    assert r["n_original_event_units_within_same_star"]==7
    assert r["observed_raw_minus_corrected_angle_deg"]>20
    assert r["finite_paired_bootstrap_draws"]==1500
    assert r["exploratory_fraction_resampled_samples_with_angle_improvement"]>.95

def test_frozen_exact_source_event_orbit_and_original_flux_reproduce():
    df=fixture_events()
    assert strict_original_event_values(df,df.copy())
    wrong=df.copy()
    wrong.loc[0,"raw_signed_x_CCD_pixels"]+=.05
    with pytest.raises(ValueError,match="source event values changed"):
        strict_original_event_values(df,wrong)
    wrong=df.copy()
    wrong.loc[0,"orbit_index"]+=100
    with pytest.raises(ValueError,match="identities changed"):
        strict_original_event_values(df,wrong)

def test_never_allow_posthoc_tuned_phase_offsets_or_one_event_bootstrap():
    assert PHASE_OFFSETS==(-.25,.25)
    with pytest.raises(ValueError,match="Insufficient actual finite"):
        bootstrap_paired_event_angles(fixture_events().iloc[:2],[1.,0.])
