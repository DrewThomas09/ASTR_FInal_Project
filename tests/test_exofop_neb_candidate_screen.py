"""Offline synthetic tests of public ExoFOP screening only, not astronomy evidence."""
import csv
import io
import json
from pathlib import Path

import pytest

from exofop_neb_candidate_screen import (
    REQUIRED_COLUMNS, SEED, candidate_rows, excluded_tics, run
)


def csv_sample():
    names=list(REQUIRED_COLUMNS)+["TESS Disposition", "Sectors"]
    records=[
       ["101","10.01","NEB","2459000","3.0","2.0","4","FP","6"],
       ["102","11.01","EB","2459001","5.0","2.5","3","FP","7"],
       ["103","12.01","PNEB","2459002","2.0","2.5","4","FP","8"],
       ["104","13.01","NEB","2459003","4.0","2.0","0","FP","6"],
       ["105","14.01","NEB","2459004","-3","2.0","2","FP","7"],
       ["101","10.02","NEB","2459000","3.0","2.0","4","FP","6"],
       ["106","15.01","NEB","2459005","3.0","2.0","4","FP","8"],
    ]
    s=io.StringIO()
    w=csv.writer(s)
    w.writerow(names)
    w.writerows(records)
    return s.getvalue().encode("utf-8")


def test_only_neb_eb_screened_and_prior_tic_excluded():
    candidates, totals=candidate_rows(csv_sample(),{106})
    assert [x["TOI"] for x in candidates["EB"]]==["11.01"]
    # Multiple TOIs from the same host appear once in deterministic host preview.
    assert len(candidates["NEB"])==1
    assert candidates["NEB"][0]["TIC_ID"]==101
    assert totals["NEB_already_inspected_TIC"]==1
    assert totals["NEB_no_referenced_timeseries"]==1
    assert totals["NEB_no_usable_ephemeris"]==1
    assert candidates["NEB"][0]["truth_localization_verified"] is False
    assert candidates["NEB"][0]["moment_centroid_evaluated"] is False


def test_deterministic_hash_order_independent_of_catalog_order():
    a,_=candidate_rows(csv_sample(),set())
    lines=csv_sample().decode().splitlines()
    b,_=candidate_rows(("\n".join([lines[0]]+list(reversed(lines[1:])))+"\n").encode(),set())
    assert [x["TIC_ID"] for x in a["NEB"]]==[x["TIC_ID"] for x in b["NEB"]]
    assert [x["deterministic_selection_sha256"] for x in a["EB"]]==[
        x["deterministic_selection_sha256"] for x in b["EB"]]


def test_no_truth_or_on_target_inference_from_generic_eb():
    d,_=candidate_rows(csv_sample(),set())
    eb=d["EB"][0]
    assert "not confirmed on-target source" in eb["candidate_evidence_status"]
    assert eb["original_TESS_SPOC_2min_FITS_verified"] is False


def test_missing_required_catalog_fields_fail_loudly():
    with pytest.raises(ValueError, match="fields missing"):
        candidate_rows(b"TOI,TIC ID\n10.01,101\n",set())


def test_missing_previous_source_manifest_fails_loudly(tmp_path):
    with pytest.raises(FileNotFoundError):
        excluded_tics(tmp_path)


def test_offline_catalog_source_snapshot_and_zero_truth_verification(tmp_path,monkeypatch):
    import exofop_neb_candidate_screen as mod
    src=tmp_path/"public.csv"
    src.write_bytes(csv_sample())
    monkeypatch.setattr(mod, "excluded_tics", lambda root: {106})
    report=run(tmp_path,tmp_path/"output",src)
    assert report["eligible_catalog_NEBS_new_distinct_TICs"]==2
    assert report["eligible_catalog_EBS_new_distinct_TICs"]==1
    assert len(report["preview_first_12_hash_ordered_each_not_selected_or_validated"]["NEB"])==2
    assert (tmp_path/"output/original_exofop_toi_catalog_snapshot.csv").read_bytes()==csv_sample()
    assert "not an independent truth-verified" in report["strict_research_boundary"][0]
