"""Synthetic official mission multi-sector PRF source diagnostics: no external TESS values."""
import pytest
from tess_two_offtarget_NASA_SPOC_DV_PRF_sector_discordance_nov13 import (
    physical_fit_quality,source_all_sector_audit,TWO_GROUND,KNOWN_CONTROLS
)


def sector(sec,host,near,valid=True):
    return {
      "original_DV_sector":sec,
      "original_DV_numberOfTransits":3,
      "original_DV_catalog_TIC_reference_to_original_external_NASA_host_arcsec":.2,
      "original_PRF_ra_dec_uncertainties_valid":valid,
      "original_mission_PRF_source_to_original_external_host_arcsec":host if valid else None,
      "original_mission_PRF_source_to_original_ground_reported_neighbor_arcsec":near if valid else None,
      "original_official_SPOC_DV_TIC_reference_offsets":{
         "skyOffset":{"value":3.,"uncertainty":.3 if valid else -1.}},
      "original_official_SPOC_DV_OUT_OF_TRANSIT_offsets":{"skyOffset":{"value":2.}},
      "original_DIFFERENCE_IMAGE_PRF_fit":{
         "raDegrees":{"value":100.,"uncertainty":.001}},
    }


def sample(valid_neb=True):
    return {
      "original_source_host_TIC":382437043 if valid_neb else 36352297,
      "original_public_ExoFOP_TOI":"1223.01" if valid_neb else "547.01",
      "source_group":"prior_ground_aperture_sky_supported_neighbor_eclipse",
      "source_original_SPOC_2min_first_sector":1,
      "original_report_file_SHA256":"a"*64,
      "official_DV_report_start_sector":1,
      "official_DV_report_end_sector":5,
      "exact_original_SPOC_TCE_and_PRF_results":{
        "only_one_TOI_compatible_TCE":True,
        "official_original_NASA_SPOC_TCE_and_sector_PRF_diagnostics_all":[{
          "NASA_DV_TCE_unique_candidate_eligibility_prior_to_examining_PRF":True,
          "original_DV_all_sector_diff_image_fit_results":[
              sector(1,3,20),sector(2,21,1),sector(3,None,None,False),
              sector(4,8,9),sector(5,6,7)]
        }]
      }
    }


def test_all_original_sectors_kept_and_first_sector_not_replaced_by_more_favorable():
    r=source_all_sector_audit(sample(),True)
    assert r["original_DV_sectors_record_count_all_including_no_or_invalid_PRF"]==5
    assert r["original_first_sector_PRF_source_label"]=="closer_to_target_host"
    assert r["number_DV_sectors_with_usable_PRF_source_fit"]==4
    assert r["original_DV_sectors_with_valid_fits_closer_to_ground_neighbor"]==1
    assert r["original_DV_sectors_with_valid_fits_closer_to_primary"]==3
    assert r["original_DV_sectors_with_invalid_PRF_or_source_QC"]==1
    assert r["predeclared_one_source_first_sector_preserved_separately"]


def test_source_sentinel_invalid_uncertainty_not_mistaken_for_a_genuine_position():
    z=sector(1,2,5,False)
    assert not physical_fit_quality(z,True)
    z=sector(1,2,5)
    assert physical_fit_quality(z,True)
    z["original_DV_catalog_TIC_reference_to_original_external_NASA_host_arcsec"]=20
    assert not physical_fit_quality(z,True)


def test_missing_original_TCE_does_not_become_false_positive_or_source_nearest():
    s=sample()
    s["exact_original_SPOC_TCE_and_PRF_results"]["only_one_TOI_compatible_TCE"]=False
    r=source_all_sector_audit(s,True)
    assert r["status"]=="no_unique_original_TOI_ephemeris_matched_official_TCE"
    assert r["all_original_DV_sectors"]==[]


def test_all_confirmed_planet_hosts_kept_without_inventing_a_neighbor():
    s=sample(False)
    z=source_all_sector_audit(s,False)
    assert z["number_DV_sectors_with_usable_PRF_source_fit"]==4
    assert z["first_sector_PRF_separation_from_confirmed_planet_host_arcsec"]==3
    assert set(TWO_GROUND)=={382437043,264303333}
    assert set(KNOWN_CONTROLS)=={36352297,134537478,232038798,452808876,455135327}
