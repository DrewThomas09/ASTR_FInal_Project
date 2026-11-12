"""Synthetic original file metadata and text parser regression fixtures."""
import pytest
from exofop_original_23_ground_NEBcheck_text_files import (
    SELECTION, chosen_original_file_entries,inspect_original_text
)


def fake_inventory():
    hosts=[]
    for tic,ids in SELECTION.items():
        hosts.append({"TIC_ID":tic,"named_neighbor_candidate_TIC_ID":23456789,
         "original_user_file_evidence_queue":[{
            "original_exofop_file_ID":fid,
            "original_file_name":f"TIC{tic}_file{fid}_measurements_NEB-table.txt",
            "original_observer_supplied_description":"Original observer ground-based results",
            "original_observer_name":"Photometry observer"}
            for fid in ids]})
    return {"all_hosts_with_full_file_and_tseries_evidence":hosts}


def test_exact_frozen_five_hosts_and_23_source_file_ids():
    entries=chosen_original_file_entries(fake_inventory())
    assert len(entries)==23
    assert len({x["host_TIC_ID"] for x in entries})==5
    assert len({x["original_file_ID"] for x in entries})==23


def test_missing_original_selected_file_is_not_substituted():
    d=fake_inventory()
    d["all_hosts_with_full_file_and_tseries_evidence"][0]["original_user_file_evidence_queue"].pop()
    with pytest.raises(ValueError,match="not found"):
        chosen_original_file_entries(d)


def test_original_note_mentions_neighbor_without_automatically_verifying_eclipse():
    t=("NEBcheck original observation\n"
       "TIC 23456789 is not the eclipsing neighbor; aperture T2 flat\n"
       "Eclipse candidate other TIC 55555555\n").encode()
    report=inspect_original_text(t,23456789)
    assert report["number_of_lines_mentioning_canonical_neighbor_TIC"]==1
    assert report["ground_based_neighbor_eclipse_independently_verified"] is False
    assert report["original_file_line_count"]==3


def test_error_html_and_binary_files_fail_as_original_photometry_text():
    with pytest.raises(ValueError,match="HTML"):
        inspect_original_text(b"<!DOCTYPE html><html>Missing data</html>",23456789)
    with pytest.raises(ValueError,match="binary"):
        inspect_original_text(b"SIMPLE\x00\x01\x02",23456789)
