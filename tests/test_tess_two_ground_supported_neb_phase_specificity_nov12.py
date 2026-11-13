"""Synthetic source geometry tests only, not real TESS astrophysical detections."""
import pytest
from tess_two_ground_supported_neb_phase_specificity_nov12 import (
    GROUND_AUDITED_HOSTS,vector_projection_away,original_source_projected_phases
)


def sample_tess(ntrue=4,ncontrol=4):
    def summary(n,raw_x,corrected_x):
        return {
            "usable_paired_original_events":n,
            "n_observed_events_with_positive_PDCSAP_depth":n,
            "median_PDCSAP_local_depth":.02,
            "raw_median_signed_vector_pixels":[raw_x,0],
            "pointing_subtracted_median_signed_vector_pixels":[corrected_x,0],
            "raw_median_vector_amplitude_pixels":abs(raw_x),
            "pointing_subtracted_median_vector_amplitude_pixels":abs(corrected_x),
            "raw_median_vector_angular_difference_away_neighbor_deg":0.,
            "pointing_subtracted_median_vector_angular_difference_away_neighbor_deg":0.
        }
    return {
        "original_external_neighbor_in_TESS_WCS":{
           "catalog_sky_geometry_consistent_with_TPF_target_position":True,
           "target_to_neighbor_CCD_pixel_vector":[1.,0.]
        },
        "true_original_event_results":summary(ntrue,-.03,-.015),
        "same_original_source_quarter_phase_controls":[{
            "phase_offset_from_original_ephemeris_in_P":phase,
            "control_source_results":summary(ncontrol,-.01,-.01)
        } for phase in (-.25,.25)]
    }


def test_physics_away_from_dimming_neighbor_sign():
    assert vector_projection_away([-.03,0],[1,0])==pytest.approx(.03)
    assert vector_projection_away([+.03,0],[1,0])==pytest.approx(-.03)
    with pytest.raises(ValueError,match="No physical"):
        vector_projection_away([1,0],[0,0])


def test_preselected_phase_specific_difference_and_original_event_count():
    r=original_source_projected_phases(sample_tess())
    assert r["original_observed_true_complete_windows"]==4
    assert r["minimum_three_true_and_each_fixed_phase_control_for_source_level_summary"]
    assert r["raw_true_minus_pooled_phase_control_signed_away_excess_pixels"]==pytest.approx(.02)
    assert r["pointing_subtracted_true_minus_pooled_phase_control_signed_away_excess_pixels"]==pytest.approx(.005)
    assert r["pointing_correction_gain_in_true_phase_specific_signed_away_projection_pixels"]==pytest.approx(-.015)


def test_original_two_event_neb_stays_descriptive_ineligible():
    r=original_source_projected_phases(sample_tess(ntrue=2))
    assert not r["minimum_three_true_and_each_fixed_phase_control_for_source_level_summary"]
    assert r["original_observed_true_complete_windows"]==2
    assert r["raw_true_minus_pooled_phase_control_signed_away_excess_pixels"]==pytest.approx(.02)


def test_no_best_phase_selection_or_source_substitution():
    d=sample_tess()
    d["same_original_source_quarter_phase_controls"][0][
       "phase_offset_from_original_ephemeris_in_P"]=-.1
    with pytest.raises(ValueError,match="exact frozen"):
        original_source_projected_phases(d)
    assert GROUND_AUDITED_HOSTS=={382437043:382437045,264303333:1884344804}
