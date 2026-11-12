"""Synthetic parser tests; file metadata is NOT an eclipse detection."""
import pytest
from exofop_five_frozen_hosts_original_ground_evidence_inventory import (
    original_csv_rows,evidence_queue
)

def file_csv():
    return ("Type,File Name,File ID,TIC,TOI,Date,User,Group,Tag,Description\n"
      "Time Series,TIC12345678_ground_neb.csv,123,12345678,100.01,2025-01-01,Researcher,TFOP,one,Photometry of neighbor TIC 22222222\n"
      "Imaging,TIC12345678_plot.pdf,124,12345678,100.01,2025-01-01,Researcher,TFOP,two,Possible NEB plot\n"
      "Unknown,other.zip,125,12345678,100.01,2025-01-01,Researcher,TFOP,three,Archive\n").encode()

def test_filelist_original_columns_preserved_with_honest_possible_source_categories():
    rows,fields=original_csv_rows(file_csv(),["file","tic"])
    assert len(rows)==3
    candidates=evidence_queue(rows,fields,12345678,22222222)
    assert [x["original_exofop_file_ID"] for x in candidates]==[123,124,125]
    assert candidates[0]["evidence_category_for_review_NOT_verified"]=="candidate_numeric_ground_photometry"
    assert candidates[0]["mentions_reported_neighbor_in_file_metadata"] is True
    assert candidates[1]["evidence_category_for_review_NOT_verified"]=="candidate_ground_source_plot"
    assert all(x["actual_eclipse_in_specific_neighbor_verified"] is False for x in candidates)

def test_missing_actual_original_source_or_error_page_fails_loudly():
    with pytest.raises(ValueError,match="HTML/error"):
        original_csv_rows(b"<html>not a source</html>",["file"])
    with pytest.raises(ValueError,match="expected field"):
        original_csv_rows(b"something_else,other\\n1,2",["file","tic"])

def test_no_upload_does_not_mean_no_ground_followup():
    rows,fields=original_csv_rows(b"Type,File Name,File ID,TIC,TOI,Date,User,Group,Tag,Description\\n",["file"])
    assert evidence_queue(rows,fields,12345678,22222222)==[]
