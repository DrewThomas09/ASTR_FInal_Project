"""Synthetic input and host-level statistical controls, not TESS observations."""
import pytest
from tess_five_new_neb_original_source_centroid_experiment import (
    check_source_manifest,source_direction_summary,CONTROLS
)

def manifest():
    return {
        "experiment_id":"ASTR_FIVE_NEW_NEB_SPOC_SOURCE_BLIND_WCS_EVAL_20261112",
        "source_manifest_frozen_prior_to_five_star_TESS_centroid_analysis":True,
        "source_records":[{
            "TIC_ID":10000000+i,
            "moment_centroid_vectors_extracted":False,
            "ground_based_eclipse_in_named_neighbor_independently_verified":False}
            for i in range(5)]
    }

def test_no_substitute_unfrozen_or_duplicate_star():
    assert len(check_source_manifest(manifest()))==5
    bad=manifest()
    bad["source_records"][0]["TIC_ID"]=bad["source_records"][1]["TIC_ID"]
    with pytest.raises(ValueError,match="precisely five fixed"):
        check_source_manifest(bad)
    bad=manifest()
    bad["source_manifest_frozen_prior_to_five_star_TESS_centroid_analysis"]=False
    with pytest.raises(ValueError,match="not frozen"):
        check_source_manifest(bad)

def test_source_identity_never_prior_centroid_exposed_or_falsely_verified():
    bad=manifest()
    bad["source_records"][0]["moment_centroid_vectors_extracted"]=True
    with pytest.raises(ValueError,match="falsely"):
        check_source_manifest(bad)

def test_star_is_independent_unit_not_number_of_source_event_windows():
    rows=[{"corrected_alignment_gain_degrees":x} for x in (10.,-2.,5.)]
    s=source_direction_summary(rows)
    assert s["n_new_host_stars_with_evaluable_direction"]==3
    assert s["n_new_hosts_corrected_angle_lower"]==2
    assert s["n_new_hosts_corrected_angle_higher"]==1
    assert s["median_new_host_angular_improvement_deg"]==pytest.approx(5.)
    assert s["exploratory_20000_whole_host_bootstrap_95pct_median_angle_improvement_deg"] is not None

def test_prespecified_quarter_phase_controls_and_absent_sources_are_not_fake_signals():
    assert CONTROLS==(-.25,.25)
    assert source_direction_summary([])["n_new_host_stars_with_evaluable_direction"]==0
    assert source_direction_summary([{"corrected_alignment_gain_degrees":5.}])[
        "exploratory_20000_whole_host_bootstrap_95pct_median_angle_improvement_deg"] is None
