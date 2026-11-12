"""Offline engineering tests; synthetic ExoFOP source notes are NOT real stars."""
import csv
import io
import json
import pytest

from tess_neb_new_host_precentroid_original_spoc_coverage import (
    prospective_source_screen_leads,SEED,PREVIOUSLY_INSPECTED_NEB_TICS
)


def originals(tmp_path):
    catalog=tmp_path/"official_catalog.csv"
    ioout=io.StringIO()
    w=csv.writer(ioout)
    w.writerow(["TIC ID","TOI","Period (days)","Epoch (BJD)",
                "Duration (hours)","TFOPWG Disposition"])
    w.writerows([
        [11111111,"100.01",2.5,2459000.,3.0,"FP"],
        [22222222,"200.01",3.2,2459010.,2.5,"FP"],
        [82302240,"4255.01",2.5,2459010.,3.0,"FP"],
    ])
    catalog.write_text(ioout.getvalue())
    notes=tmp_path/"original_notes.json"
    notes.write_text(json.dumps({"source_rows":[
        {"TIC_ID":11111111,"TOI":"100.01","note_request_result":"fetched",
         "public_notes":[{"explicit_photometric_disposition_tokens":["NEB"],
                          "note":"Phot Disp: NEB near TIC 76543210"}]},
        {"TIC_ID":22222222,"TOI":"200.01","note_request_result":"fetched",
         "public_notes":[{"explicit_photometric_disposition_tokens":[],
                          "note":"NEBs ruled out by observation"}]},
        {"TIC_ID":82302240,"TOI":"4255.01","note_request_result":"fetched",
         "public_notes":[{"explicit_photometric_disposition_tokens":["NEB"],
                          "note":"Phot Disp: NEB TIC 82302236"}]},
    ]}))
    return notes,catalog


def test_only_explicit_NEBS_not_negated_keyword_and_excludes_prior_case(tmp_path):
    notes,catalog=originals(tmp_path)
    candidates,counts,h=prospective_source_screen_leads(notes,catalog,set())
    assert counts["has_explicit_NEB_disposition_note"]==2
    assert counts["prior_source_or_case_exclusions"]==1
    assert len(candidates)==1
    assert candidates[0]["TIC_ID"]==11111111
    assert candidates[0]["potential_other_TICs_mentioned_in_note_NOT_verified"]==["76543210"]
    assert candidates[0]["original_TESS_centroids_inspected"] is False
    assert candidates[0]["reported_onsky_neighbor_truth_verified"] is False
    assert candidates[0]["original_exofop_period_days"]==pytest.approx(2.5)


def test_inspected_host_is_removed_even_when_labeled_NEBS(tmp_path):
    notes,catalog=originals(tmp_path)
    result,counts,_=prospective_source_screen_leads(notes,catalog,{11111111})
    assert result==[]
    assert counts["prior_source_or_case_exclusions"]==2


def test_missing_original_photometry_times_cannot_fill_with_guesses(tmp_path):
    notes,catalog=originals(tmp_path)
    catalog.write_text(catalog.read_text().replace("2459000.0","0"))
    result,counts,_=prospective_source_screen_leads(notes,catalog,set())
    assert len(result)==0
    assert counts["no_matching_original_catalog_ephemeris"]==1


def test_duplicate_original_TOI_catalog_fails(tmp_path):
    notes,catalog=originals(tmp_path)
    lines=catalog.read_text().splitlines()
    catalog.write_text("\n".join(lines+[lines[1]])+"\n")
    with pytest.raises(ValueError,match="Repeated original ExoFOP"):
        prospective_source_screen_leads(notes,catalog,set())
