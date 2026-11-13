"""Synthetic blended-flux physics tests, not observed ground/TESS astronomy."""
import csv
import io
import pytest

from tess_two_ground_neb_idealized_blended_flux_and_centroid_physics_nov12 import (
    CASES,naive_two_star_blend,
    independent_catalog_neighbor_tmag,original_exofop_target_tmag,
    original_ground_observer_dT_from_source
)


def test_two_star_exact_flux_fraction_and_away_direction():
    z=naive_two_star_blend(.25,5.,[1.0,0.])
    # Delta T=5 -> flux ratio .01; neighbor loses exactly 25% flux.
    assert z["external_approx_neighbor_over_primary_TESS_flux_ratio"]==pytest.approx(.01)
    assert z["idealized_original_full_aperture_TESS_diluted_depth_ppm"]==pytest.approx(
        1e6*.25*.01/1.01)
    assert z["idealized_two_star_centroid_away_vector_CCD_pixels"][0]<0
    assert z["idealized_two_star_centroid_signed_away_shift_pixels"]>0
    with pytest.raises(ValueError,match="physically valid"):
        naive_two_star_blend(1.5,5.,[1.0,0.])
    with pytest.raises(ValueError,match="physically valid"):
        naive_two_star_blend(.25,5.,[0.,0.])


def test_source_note_delta_t_is_not_invented_or_assumed_ground_truth():
    source={
        "original_observer_source_file_details":[{
            "host_TIC_ID":382437043,
            "original_file_ID":906274,
            "source_download_status":"success",
            "original_uploaded_file_source_SHA256":"a"*64,
            "original_source_text_evidence":{
                "original_excerpt_first_nonblank_lines":[
                    "LCO ground report on target",
                    "Nearby T6 (TIC 382437045 - ΔT = 5.3, r=24.6 arcsec E)",
                    "Other apertures not cleared"
                ]
            }
        }]
    }
    r=original_ground_observer_dT_from_source(source,382437043)
    assert r["relative_TESS_magnitude_original_observer_note"]==pytest.approx(5.3)
    assert r["relative_TESS_magnitude_directly_independently_measured_by_this_project"] is False
    assert r["original_ExoFOP_observer_source_file_ID"]==906274
    source["original_observer_source_file_details"][0]["original_source_text_evidence"][
        "original_excerpt_first_nonblank_lines"]=["No magnitude quoted"]
    with pytest.raises(ValueError,match="unambiguous"):
        original_ground_observer_dT_from_source(source,382437043)


def test_original_neighbor_Tmag_separate_from_host_and_source_mag():
    raw=("TIC ID,TESS Mag,Separation (arcsec),RA,Dec\n"
         "382437045,14.6152,24.49,07:48:55.1,-63:43:05.41\n").encode()
    a=independent_catalog_neighbor_tmag(raw,382437043,382437045)
    assert a["external_neighbor_TESS_Mag"]==pytest.approx(14.6152)
    assert a["external_neighbor_sky_separation_arcsec"]==pytest.approx(24.49)
    with pytest.raises(ValueError,match="absent"):
        independent_catalog_neighbor_tmag(raw,382437043,999999)


def test_original_exofop_target_tmag_is_used_only_if_exact_same_tic_toi():
    raw=("TIC ID,TOI,TESS Mag,TFOPWG Disposition\n"
         "382437043,1223.01,9.3152,FP\n").encode()
    v,status=original_exofop_target_tmag(raw,382437043,"1223.01")
    assert v==pytest.approx(9.3152)
    assert "Original independent" in status
    assert original_exofop_target_tmag(raw,382437043,"1223.02")[0] is None
    assert set(CASES)=={382437043,264303333}
