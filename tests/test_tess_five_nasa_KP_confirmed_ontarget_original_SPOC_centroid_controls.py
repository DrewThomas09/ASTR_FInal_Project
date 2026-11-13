"""Synthetic scientific calculator checks; these are not observed TESS planet scores."""
import numpy as np
import pytest
from tess_five_nasa_KP_confirmed_ontarget_original_SPOC_centroid_controls import (
    verify_original_catalogue_frozen_controls, source_metric,
    source_with_fixed_controls, whole_host_descriptive_statistics,CONTROLS
)


def freeze():
    return {
      "experiment_id":"ASTR_NASA_AND_EXOFOP_KP_CONFIRMED_TRANSITING_ON_TARGET_CONTROL_SPOC_SOURCE_FROZEN_NOV12",
      "source_manifest_frozen_before_any_control_TESS_centroid_measurements":True,
      "original_TESS_centroids_viewed":0,
      "source_records":[{
          "TIC_ID":123456780+i,
          "original_ExoFOP_TFOPWG_Disposition":"KP",
          "NASA_archive_confirmed_transit_and_ExoFOP_KP_agree":True,
          "MOM_CENTR_or_POS_CORR_not_queried":True,
          "no_mission_classifier_score_inspected":True,
          "independently_verified_on_target_ground_lightcurve_source":False,
          "original_ExoFOP_period_days":3.
      } for i in range(5)]
    }


def row(raw,adjusted,depth=.02):
    return {
      "original_PDCSAP_local_flux_depth":depth,
      "raw_signed_x_CCD_pixels":raw,
      "raw_signed_y_CCD_pixels":0,
      "pointing_subtracted_signed_x_CCD_pixels":adjusted,
      "pointing_subtracted_signed_y_CCD_pixels":0,
      "original_raw_local_prepost_movement_pixels":.005,
      "pointing_subtracted_local_prepost_movement_pixels":.004,
    }


def test_frozen_source_MUST_be_unique_unseen_and_NASA_KP_double_confirmed():
    assert len(verify_original_catalogue_frozen_controls(freeze()))==5
    s=freeze()
    s["source_records"][3]["TIC_ID"]=s["source_records"][4]["TIC_ID"]
    with pytest.raises(ValueError,match="Five distinct"):
        verify_original_catalogue_frozen_controls(s)
    s=freeze()
    s["source_records"][1]["MOM_CENTR_or_POS_CORR_not_queried"]=False
    with pytest.raises(ValueError,match="centroid"):
        verify_original_catalogue_frozen_controls(s)
    s=freeze()
    s["source_records"][1]["independently_verified_on_target_ground_lightcurve_source"]=True
    with pytest.raises(ValueError,match="falsely"):
        verify_original_catalogue_frozen_controls(s)


def test_actual_original_same_event_raw_corrected_centroid_norms_and_signed_vectors():
    s=source_metric([row(.010,.006),row(.020,.008),row(.030,.010)])
    assert s["complete_same_observed_original_event_windows"]==3
    assert s["raw_median_event_centroid_norm_pixels"]==pytest.approx(.020)
    assert s["pointing_subtracted_median_event_centroid_norm_pixels"]==pytest.approx(.008)
    assert s["reduction_in_median_true_event_vector_norm_pixels"]==pytest.approx(.012)
    assert s["reduction_in_median_original_pre_post_drift_pixels"]==pytest.approx(.001)
    assert s["photometry_supported_positive_local_PDCSAP_dips"]==3


def test_fixed_phase_controls_are_included_without_optimizing_phase_or_aperture():
    actual=[row(.02,.01) for _ in range(4)]
    controls=[[row(.004,.005,depth=0) for _ in range(4)] for _ in CONTROLS]
    s=source_with_fixed_controls(actual,controls)
    assert s["minimum_three_real_events_AND_three_each_fixed_phase_control_windows"]
    assert s["raw_true_minus_quarter_control_centroid_norm_pixels"]==pytest.approx(.016)
    assert s["pointing_subtracted_true_minus_quarter_control_centroid_norm_pixels"]==pytest.approx(.005)
    assert s["raw_minus_corrected_change_in_event_excess_over_control_pixels"]==pytest.approx(.011)
    assert [r["shift_fraction_of_original_orbital_period"] for r in s["original_shifted_phase_control_results"]]==[-.25,.25]
    short=source_with_fixed_controls(actual,[[row(.004,.005) for _ in range(2)],controls[1]])
    assert short["minimum_three_real_events_AND_three_each_fixed_phase_control_windows"] is False
    assert short["raw_minus_corrected_change_in_event_excess_over_control_pixels"] is None


def test_whole_host_statistical_unit_not_pseudoreplicated_multiple_transits():
    actual=[row(.02,.01) for _ in range(14)]
    controls=[[row(.004,.005) for _ in range(14)] for _ in CONTROLS]
    s=source_with_fixed_controls(actual,controls)
    rows=[{"source_processing_status":"processed","actual_science":s} for i in range(5)]
    stats=whole_host_descriptive_statistics(rows)
    assert stats["independent_eligible_confirmed_planet_host_TICs"]==5
    assert stats["local_drift_raw_minus_adjusted"]["n_reduced"]==5
    assert stats["true_event_norm_raw_minus_adjusted"]["n_reduced"]==5
    assert stats["true_minus_null_excess_raw_minus_adjusted"]["median_original_source_host_delta_pixels"]==pytest.approx(.011)
    assert stats["all_five_preserved"] is True
