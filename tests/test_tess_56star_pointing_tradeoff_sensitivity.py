"""Synthetic unit tests only, not independent exoplanet ground truth."""
import numpy as np
import pandas as pd
import pytest

from tess_56star_pointing_tradeoff_sensitivity_nov12 import analyze_event_pairs


def synthetic_pairs():
    # Four independent source stars; each has two repeated orbit windows.
    # Deliberately cover all four possible joint-direction quadrants.
    rows = []
    cases = [
        ("100-1-S6", "prior_32", 100, .004, .002, .002, .001),
        ("101-1-S6", "prior_32", 101, .004, .002, .001, .002),
        ("102-1-S6", "additional_24", 102, .004, .006, .002, .001),
        ("103-1-S6", "additional_24", 103, .004, .006, .001, .002),
    ]
    for uid, cohort, tic, raw_p, corrected_p, raw_e, corrected_e in cases:
        for orbit in (1, 2):
            rows.append(dict(
                uid=uid, cohort=cohort, TIC_ID=tic, orbit_index=orbit,
                prepost_raw_pixels=raw_p, prepost_corrected_pixels=corrected_p,
                event_raw_pixels=raw_e, event_corrected_pixels=corrected_e,
            ))
    return pd.DataFrame(rows)


def test_tradeoff_quadrants_are_star_level_not_event_level():
    sources, result = analyze_event_pairs(synthetic_pairs(), require_frozen=False)
    assert len(sources) == 4
    assert result["n_observed_source_event_windows"] == 8
    assert result["pointing_proxy_reduced_stars"] == 2
    assert result["event_shift_reduced_stars"] == 2
    c = result["joint_star_outcome_counts"]
    assert c["both_pointing_proxy_and_event_shift_reduced"] == 1
    assert c["pointing_proxy_reduced_event_shift_not_reduced"] == 1
    assert c["pointing_proxy_not_reduced_event_shift_reduced"] == 1
    assert c["neither_reduced"] == 1
    assert result["leave_one_STAR_out_sensitivity"]["number_of_recomputations"] == 4


def test_repeated_orbits_of_one_source_cannot_count_as_new_stars():
    _, result = analyze_event_pairs(synthetic_pairs(), require_frozen=False)
    assert result["n_star_units"] == 4
    assert all(x["n_stars"] == 2 for x in result["cohort_sensitivity"].values())


def test_duplicate_source_orbit_rejected():
    d = synthetic_pairs()
    with pytest.raises(ValueError, match="Repeated source/orbit"):
        analyze_event_pairs(pd.concat([d, d.iloc[[0]]]), require_frozen=False)


def test_nonfinite_original_measurement_rejected():
    d = synthetic_pairs()
    d.loc[0, "event_corrected_pixels"] = np.nan
    with pytest.raises(ValueError, match="Invalid measured original event"):
        analyze_event_pairs(d, require_frozen=False)


def test_source_identity_changes_rejected():
    d = synthetic_pairs()
    d.loc[0, "cohort"] = "additional_24"
    with pytest.raises(ValueError, match="Source UID switched"):
        analyze_event_pairs(d, require_frozen=False)


def test_frozen_real_source_counts_required_in_production():
    with pytest.raises(ValueError, match="Expected 248 original events"):
        analyze_event_pairs(synthetic_pairs(), require_frozen=True)


def test_missing_measurement_column_rejected():
    with pytest.raises(ValueError, match="Missing original event columns"):
        analyze_event_pairs(synthetic_pairs().drop(columns="prepost_corrected_pixels"), require_frozen=False)
