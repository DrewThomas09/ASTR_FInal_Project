"""Synthetic engineering tests; these are NOT simulated exoplanet discoveries."""
import numpy as np
import pandas as pd
import pytest
from tess_56star_signed_event_coherence_nov12 import (
    directional_concentration, analyze_signed_events
)


def fake_signed_events():
    rows=[]
    for uid, cohort, tic, raw, adjusted in [
        ("100-1-S6","prior_32",100,[(1,0),(-1,0),(1,0)],[(1,0),(1,0),(1,0)]),
        ("101-1-S6","additional_24",101,[(1,0),(1,0),(1,0)],[(1,0),(-1,0),(1,0)]),
        ("102-1-S6","prior_32",102,[(2,0),(1,0),(1,0)],[(1,0),(1,0),(1,0)]),
        ("103-1-S6","additional_24",103,[(0,0),(0,0)],[(0,0),(0,0)]),
    ]:
        for index,(v,w) in enumerate(zip(raw,adjusted)):
            rows.append(dict(uid=uid,cohort=cohort,TIC_ID=tic,orbit_index=index,
                predicted_NASA_TCE_center_BTJD=1500+index*2.,
                event_x_raw_pixels=v[0],event_y_raw_pixels=v[1],
                event_x_corrected_pixels=w[0],event_y_corrected_pixels=w[1]))
    return pd.DataFrame(rows)


def test_directional_concentration_perfect_alignment():
    assert directional_concentration([(1.,0.),(2.,0.),(3.,0.)]) == pytest.approx(1.0)


def test_directional_concentration_balanced_cancellation():
    assert directional_concentration([(1.,0.),(-1.,0.)]) == pytest.approx(0.0)


def test_directional_concentration_zero_denominator_is_missing():
    assert directional_concentration([(0.,0.),(0.,0.),(0.,0.)]) is None


def test_coherence_preserves_independence_and_valid_direction_changes():
    stars, eligible, result = analyze_signed_events(fake_signed_events(),require_frozen=False)
    assert result["source_stars"] == 4
    assert result["original_source_event_windows"] == 11
    assert result["sources_at_least_three_events"] == 3
    assert result["sources_with_valid_nonzero_signed_vectors"] == 3
    assert result["directional_concentration_increased_stars"] == 1
    assert result["directional_concentration_decreased_stars"] == 1
    assert result["directional_concentration_tied_stars"] == 1
    assert eligible.set_index("uid").loc["100-1-S6","raw_direction_concentration"] == pytest.approx(1/3.)
    assert eligible.set_index("uid").loc["100-1-S6","corrected_direction_concentration"] == pytest.approx(1.0)
    assert result["concentration_change_by_source_cohort"]["prior_32"]["n_eligible_valid"] == 2


def test_duplicate_orbit_rejected_as_pseudoreplication():
    a=fake_signed_events()
    with pytest.raises(ValueError,match="identity missing or duplicated"):
        analyze_signed_events(pd.concat([a,a.iloc[[0]]]),require_frozen=False)


def test_nonfinite_signed_vector_rejected_not_imputed():
    a=fake_signed_events()
    a.loc[0,"event_y_raw_pixels"]=np.nan
    with pytest.raises(ValueError,match="Nonfinite"):
        analyze_signed_events(a,require_frozen=False)


def test_source_uid_switching_target_rejected():
    a=fake_signed_events()
    a.loc[0,"TIC_ID"]=99999
    with pytest.raises(ValueError,match="Source UID changed"):
        analyze_signed_events(a,require_frozen=False)


def test_required_frozen_original_sample_cannot_be_replaced_with_synthetic():
    with pytest.raises(ValueError,match="Original source total"):
        analyze_signed_events(fake_signed_events(),require_frozen=True)


def test_vector_input_shape_rejected():
    with pytest.raises(ValueError,match="Invalid physical signed-vector"):
        directional_concentration([1,2,3])
