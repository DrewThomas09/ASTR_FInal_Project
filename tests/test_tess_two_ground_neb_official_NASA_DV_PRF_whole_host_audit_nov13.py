"""Synthetic repeated NASA DV mission reduction host-level accounting test.

Does NOT provide independent off-target neighbor eclipse ground truth.
"""
import pytest
from tess_two_ground_neb_official_NASA_DV_PRF_whole_host_audit_nov13 import (
    summarize_official_source,HOSTS,EXPECTED_DV_ORIGINAL_RUNS_PER_HOST
)


def fake_host(host=382437043,invalid_first=True):
    toi=HOSTS[host]
    sector=1 if host==382437043 else 14
    records=[]
    for n,end in enumerate((13,36,39,65,69,96)):
        valid=not(invalid_first and n==0)
        q={
          "original_DV_XML_product":{
              "TIC_ID":host,"original_DV_search_start_sector":sector,
              "original_DV_search_end_sector":end,
              "product_filename":f"tess-XXXX-s{sector:04d}-s{end:04d}-{host:016d}.xml"},
          "original_DV_XML_source_processing_status":"processed_original",
          "original_DV_XML_source_provenance":{"original_source_SHA256":"a"*64},
          "original_DV_ephemeris_matched_TCE_count_before_centroid":1,
          "original_DV_frozen_sector_PRF_differences_for_only_ephemeris_matched_TCEs":[{
              "original_DV_original_TOI_ephemeris_match":{
                  "original_NASA_DV_candidate_period_days":1.5,
                  "DV_to_original_TOI_wrapped_phase_difference_days":.001},
              "original_DV_first_frozen_sector_difference_image_result_rows":[{
                  "original_DV_image_sector":sector,
                  "original_DV_image_quality_metric":{"valid":valid,"attempted":True,
                      "value":"0.85" if valid else "0.0"},
                  "original_DV_first_sector_PRF_physically_interpretable":valid,
                  "original_NASA_DV_PRF_to_primary_host_arcsec":3.,
                  "original_NASA_DV_PRF_to_ground_observed_neighbor_arcsec":20.,
                  "original_NASA_DV_PRF_source_target_to_neighbor_separation_arcsec":24.5,
                  "original_DV_PRF_sky_centroid_angular_uncertainty_RA_Dec_degrees_not_correlated":{"RA":.002,"Dec":.001}
              }]
          }]
        }
        records.append(q)
    return {"TIC_ID":host,"TOI":toi,"original_frozen_TESS_SPOC_sector":sector,
            "source_archive_records_all_no_selection_on_offset":records}


def test_earliest_source_run_remains_PRIMARY_even_if_invalid():
    s=summarize_official_source(fake_host())
    assert s["n_original_NASA_SPOC_DV_search_runs_all"]==6
    assert s["n_original_official_valid_PRF_results"]==5
    assert s["n_original_official_invalid_PRF_results"]==1
    assert s["number_of_independent_astrophysical_host_star_units"]==1
    assert s["primary_PRESELECTED_earliest_DV_search_run_even_if_invalid"][
        "n_valid_official_FIRST_SECTOR_difference_image_centroids"]==0
    assert s["n_valid_PRF_nominally_closer_to_primary"]==5
    assert s["n_valid_PRF_nominally_closer_to_ground_observed_neighbor"]==0


def test_repeated_campaigns_not_six_independent_sources_and_no_biased_replacement():
    source=fake_host(host=264303333,invalid_first=False)
    s=summarize_official_source(source)
    assert s["n_original_official_valid_PRF_results"]==6
    assert s["number_of_independent_astrophysical_host_star_units"]==1
    assert EXPECTED_DV_ORIGINAL_RUNS_PER_HOST==6
    wrong=fake_host()
    wrong["source_archive_records_all_no_selection_on_offset"][0][
        "original_DV_XML_product"]["TIC_ID"]=264303333
    with pytest.raises(ValueError,match="wrong host TIC"):
        summarize_official_source(wrong)
    reordered=fake_host()
    reordered["source_archive_records_all_no_selection_on_offset"].reverse()
    with pytest.raises(ValueError,match="run order"):
        summarize_official_source(reordered)


def test_not_silently_count_missing_tce_as_valid_prf():
    source=fake_host()
    first=source["source_archive_records_all_no_selection_on_offset"][0]
    first["original_DV_ephemeris_matched_TCE_count_before_centroid"]=0
    first["original_DV_frozen_sector_PRF_differences_for_only_ephemeris_matched_TCEs"]=[]
    result=summarize_official_source(source)
    assert result["n_original_NASA_DV_runs_with_matching_TCE_period_phase"]==5
    assert result["n_original_official_invalid_PRF_results"]==1
