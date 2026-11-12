"""Synthetic source identity tests, not physically verified NEBs."""
import pytest
from tess_neb_newhost_external_neighbor_candidate_audit import (
    read_neighbor_astrometry,candidate_note_matches
)

def neighbors():
    return (
        "TIC ID,TOI,RA,Dec,Separation (arcsec),Position Angle (deg E. of N.)\n"
        "12345678,100.01,08:17:24.6,-35:15:12.1,5.1,31.21\n"
        "12345679,100.01,08:17:24.7,-35:15:12.2,1200,10.00\n"
    ).encode()

def notes():
    return [{"TIC_ID":98765432,"TOI":"100.01","public_notes":[
        {"explicit_photometric_disposition_tokens":["NEB"],
         "note":"Phot Disp: NEB, TIC 12345678 is the suspected eclipsing neighbor",
         "last_modified_as_reported":"2025-01-01","note_id_as_reported":"1"},
        {"explicit_photometric_disposition_tokens":[],
         "note":"We ruled out TIC 12345677 and all NEBs",
         "last_modified_as_reported":"2024-01-01","note_id_as_reported":"2"}
    ]}]

def test_original_named_neighbor_has_real_tic_separation_and_RA_HMS():
    d=read_neighbor_astrometry(neighbors(),98765432)
    assert sorted(d)==[12345678]
    assert d[12345678]["original_catalog_separation_arcsec"]==pytest.approx(5.1)
    assert d[12345678]["original_catalog_neighbor_RA_deg"]==pytest.approx(124.3525)

def test_only_explicit_neb_note_contributes_other_TIC_match():
    d=read_neighbor_astrometry(neighbors(),98765432)
    nebs,m=candidate_note_matches(notes(),98765432,d)
    assert len(nebs)==1
    assert len(m)==1
    assert m[0]["mentioned_TIC_ID"]==12345678
    assert m[0]["in_external_nearby_star_catalog"]
    assert "suspected" in m[0]["raw_note_context_excerpt"]

def test_missing_original_neb_disposition_or_wrong_host_rejected():
    d=read_neighbor_astrometry(neighbors(),98765432)
    with pytest.raises(ValueError,match="absent or duplicated"):
        candidate_note_matches(notes(),99999999,d)
    with pytest.raises(ValueError,match="lacks original explicit NEB"):
        candidate_note_matches([{"TIC_ID":98765432,"public_notes":[
            {"explicit_photometric_disposition_tokens":[],
             "note":"All nearby NEBs ruled out"}]}],98765432,d)
