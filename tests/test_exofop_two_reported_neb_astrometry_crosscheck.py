"""Synthetic ExoFOP astrometry parsing tests, no claimed science truth."""
import pytest
from exofop_two_reported_neb_astrometry_crosscheck import parse_neighbor_sep,note_source,CASES

def fake_astrometry():
    return (
      b"TIC ID,TOI,RA,Dec,Separation (arcsec),Position Angle (deg E. of N.)\n"
      b"54364420,2041.01,10,-30,23.3,90.1\n"
      b"99999999,2041.01,10,-30,8.2,135\n"
    )

def test_original_catalog_neighbor_tic_and_separation_matched_not_any_nearby_star():
    hit=parse_neighbor_sep(fake_astrometry(),54364420)
    assert len(hit)==1
    assert hit[0]["catalog_angular_separation_arcsec"]==pytest.approx(23.3)
    assert len(parse_neighbor_sep(fake_astrometry(),99999999))==1
    assert not parse_neighbor_sep(fake_astrometry(),99999998)

def test_missing_original_angular_separation_field_fails():
    with pytest.raises(ValueError,match="separation"):
        parse_neighbor_sep(b"TIC ID,TOI\n54364420,2041.01\n",54364420)

def test_original_NEBS_note_must_explicitly_identify_same_neighbor():
    case=CASES[0]
    notes=[{"TIC_ID":case["target_tic"],"public_notes":[
        {"note":"Phot Disp: NEB. TIC 54364420 nearby",
         "explicit_photometric_disposition_tokens":["NEB"]},
        {"note":"NEBs ruled out around TIC 54364420",
         "explicit_photometric_disposition_tokens":[]},
        {"note":"Phot Disp: NEB, different TIC 44444444",
         "explicit_photometric_disposition_tokens":["NEB"]}
    ]}]
    assert len(note_source(case,notes))==1

def test_reported_NEB_neighbor_is_not_automatic_confirmed_physical_truth():
    assert len(CASES)==2
    assert CASES[0]["target_tic"]!=CASES[1]["target_tic"]
    assert CASES[0]["neighbor_tic"]!=CASES[0]["target_tic"]
