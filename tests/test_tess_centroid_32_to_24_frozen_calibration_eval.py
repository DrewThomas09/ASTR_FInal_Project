"""Offline tests for strictly frozen development-learned source centroid review."""
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pandas as pd
import pytest
from tess_centroid_32_to_24_frozen_calibration_eval import (
    axis_interval_nonzero,parse_interval,score_one,checked_original_development_centroids
)


def fake_row(depth=.004,x="[0.002,0.006]",y="[-0.003,0.002]",n=5,score=.9):
    return SimpleNamespace(
        corrected_centroid_source_event_count=n,
        corrected_median_event_local_centroid_vector_pixels=depth,
        corrected_bootstrap_95pct_x_interval=x,
        corrected_bootstrap_95pct_y_interval=y,
        original_2026_NASA_score_unchanged=score
    )


def test_original_development_threshold_is_frozen_before_holdout():
    meta=json.loads(Path("TESS_32_TO_24_CENTROID_POSITIVE_REFERENCE_GATE_FROZEN_2026_11_08.json").read_text())
    assert meta["n_eligible_positive_development_stars"]==13
    assert meta["frozen_resulting_centroid_threshold_pixels"]==.0016012455384686
    assert meta["quantile_method"]=="higher"
    assert meta["source_development_csv_expected_SHA256"]=="84367f439fb58164a28768fd838288d205c6bdd4375c68b6f5e647580c471ea5"


def test_real_development_source_digest_required(tmp_path):
    p=tmp_path/"fake32.csv"
    p.write_text("uid,label,x\nfake,planet,.1\n")
    manifest=json.loads(Path("TESS_32_TO_24_CENTROID_POSITIVE_REFERENCE_GATE_FROZEN_2026_11_08.json").read_text())
    with pytest.raises(ValueError,match="differs from frozen"):
        checked_original_development_centroids(p,manifest)


def test_signed_centroid_bootstrap_interval_controls_manual_review():
    assert axis_interval_nonzero("[.001,.004]","[-.002,.005]") is True
    assert axis_interval_nonzero("[-.001,.004]","[-.002,.005]") is False
    assert axis_interval_nonzero("null","[-.002,.005]") is None


def test_calibrated_fixed_gate_flags_large_coherent_shift_in_NASA_candidate():
    a=score_one(fake_row(),.0016012455384686)
    assert a["eligible"] is True
    assert a["centroid_warning"] is True
    assert a["NASA_candidate_AND_centroid_warning"] is True


def test_same_shift_not_a_NASA_candidate_warning_if_original_score_low():
    a=score_one(fake_row(score=.2),.0016012455384686)
    assert a["centroid_warning"] is True
    assert a["NASA_candidate_AND_centroid_warning"] is False


def test_same_small_shift_does_not_trigger_original_0p05px_gate():
    a=score_one(fake_row(),.05)
    assert a["eligible"] is True
    assert a["centroid_warning"] is False


def test_source_with_two_original_events_is_indeterminate_not_zero_shift():
    a=score_one(fake_row(n=2),.0016012455384686)
    assert a["eligible"] is False
    assert a["centroid_warning"] is None


def test_bootstrap_CI_crossing_zero_does_not_trigger_review():
    a=score_one(fake_row(x="[-.002,.003]",y="[-.003,.003]"),.0016012455384686)
    assert a["eligible"] is True
    assert a["centroid_warning"] is False


def test_bad_original_interval_rejected_instead_of_forging_measurements():
    with pytest.raises(ValueError,match="not two values"):
        parse_interval("[.002]")
    with pytest.raises(ValueError,match="Malformed"):
        parse_interval("not data")
