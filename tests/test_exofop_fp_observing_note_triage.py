"""Synthetic text parsing tests; never convert note keywords into physical source truth."""
import pytest
from exofop_fp_observing_note_triage import parse_observing_notes_csv, classify_note_screen

def test_explicit_ground_based_neb_disposition_is_still_review_only():
    blob=b'ID,TIC ID,Username,Groupname,TAG ID,Lastmod,notes\n1,100,observer,tfopwg,1,2025-01-02,"Phot Disp: NEB; evidence to be inspected"\n'
    notes=parse_observing_notes_csv(blob)
    status=classify_note_screen(notes)
    assert notes[0]["explicit_photometric_disposition_tokens"]==["NEB"]
    assert status["human_followup_priority"]=="review_explicit_NEB_note"
    assert status["physical_source_truth_verified"] is False
    assert status["actual_offtarget_neighbor_coordinates_verified"] is False

def test_negated_neb_keyword_is_not_verification():
    blob=b'ID,TIC ID,Username,Groupname,TAG ID,Lastmod,notes\n1,100,observer,tfopwg,1,2025-01-02,"Nearby NEBs ruled out by two observers"\n'
    notes=parse_observing_notes_csv(blob)
    status=classify_note_screen(notes)
    assert status["human_followup_priority"]=="review_NEB_keyword_only"
    assert status["physical_source_truth_verified"] is False

def test_explicit_eb_does_not_become_onsource_truth():
    blob=b'ID,TIC ID,Username,Groupname,TAG ID,Lastmod,notes\n1,100,observer,tfopwg,1,2025-01-02,"Phot Disp: EB"\n'
    status=classify_note_screen(parse_observing_notes_csv(blob))
    assert status["human_followup_priority"]=="review_explicit_EB_note"
    assert status["physical_source_truth_verified"] is False

def test_missing_note_field_fails_loudly():
    with pytest.raises(ValueError,match="text field"):
        parse_observing_notes_csv(b'ID,TIC ID\n1,100\n')

def test_empty_note_table_is_not_evidence():
    notes=parse_observing_notes_csv(b'ID,TIC ID,Username,notes\n')
    status=classify_note_screen(notes)
    assert status["public_note_rows"]==0
    assert status["human_followup_priority"]=="no_obvious_NEB_keyword"
