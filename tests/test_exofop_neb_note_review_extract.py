"""Synthetic tests for source-note excerpts; no astrophysical truth claim."""
import pytest
from exofop_neb_note_review_extract import extract_review_notes

def source():
    return {"source_rows":[
        {"TIC_ID":123456,"TOI":"100.01","note_request_result":"fetched",
         "physical_source_truth_verified":False,
         "observed_source_note_url":"https://exofop.ipac.caltech.edu/tess/download_obsnotes.php?tid=123456",
         "public_notes":[
            {"explicit_photometric_disposition_tokens":["NEB"],
             "note":"Phot Disp: NEB, possible TIC 654321 at 4.2 arcsec; needs confirmation.",
             "last_modified_as_reported":"2026-01-01","note_id_as_reported":"1"},
            {"explicit_photometric_disposition_tokens":[],
             "note":"Earlier observer ruled out an NEB",
             "last_modified_as_reported":"2025-01-01","note_id_as_reported":"2"}
         ]}
    ]}

def test_only_explicitly_reported_notes_queued_not_keyword_only():
    notes=extract_review_notes(source())
    assert len(notes)==1
    n=notes[0]
    assert n["TIC_ID"]==123456
    assert "654321" in n["possible_TIC_numbers_in_note_not_yet_verified"]
    assert n["offtarget_physical_source_localized"] is False
    assert n["on_target_physical_source_localized"] is False
    assert n["astrometry_verified"] is False

def test_falsely_verified_source_flag_cannot_pass():
    bad=source()
    bad["source_rows"][0]["physical_source_truth_verified"]=True
    with pytest.raises(ValueError,match="falsely upgrades"):
        extract_review_notes(bad)

def test_missing_original_note_collection_fails():
    with pytest.raises(ValueError,match="Missing original"):
        extract_review_notes({"other":"thing"})
