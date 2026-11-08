"""Frozen 24 previously unexamined source-selection and no-threshold-retuning tests."""
import json
from pathlib import Path
import pytest
from tess_centroid_24star_locked_holdout import fixed_24_manifest


FROZEN="TESS_NEW_24STAR_CENTROID_RULE_HOLDOUT_FROZEN_2026_11_08.json"
PRIOR="TESS_32STAR_CENTROID_ALIAS_COMPANION_FROZEN_2026_11_08.json"


def test_24_new_sources_stay_different_from_all_32_prior_development_hosts():
    m,rule=fixed_24_manifest(FROZEN,PRIOR)
    selected={int(x["tic_id"]) for x in m["source_records"]}
    prior={int(x["tic_id"]) for x in rule["source_records"]}
    assert len(selected)==24 and not selected&prior
    assert 167526485 not in selected


def test_selection_is_stratified_three_per_class_and_MES_band():
    m,_=fixed_24_manifest(FROZEN,PRIOR)
    for lab in ("KP","CP","EB","NTP"):
        subset=[r for r in m["source_records"] if r["original_2025_historical_label"]==lab]
        assert len(subset)==6
        assert sum(x["MES_band"]=="7-20" for x in subset)==3
        assert sum(x["MES_band"]=="20-80" for x in subset)==3


def test_precommitted_centroid_rule_threshold_unchanged():
    m,rule=fixed_24_manifest(FROZEN,PRIOR)
    assert m["unchanged_rule_reference"]==PRIOR
    settings=rule["fixed_experimental_flag_NOT_VALIDATED_FOR_SCIENCE"]
    assert settings["median_2d_shift_at_least_pixels"]==.05
    assert settings["min_individual_events"]==3
    assert rule["fixed_event_uncertainty"]["repetitions"]==500
    assert rule["fixed_event_uncertainty"]["seed"]==2026110811


def test_frozen_24_manifest_rejects_overlap_with_prior_tic(tmp_path):
    m=json.loads(Path(FROZEN).read_text())
    prior=json.loads(Path(PRIOR).read_text())
    m["source_records"][0]["tic_id"]=prior["source_records"][0]["tic_id"]
    p=tmp_path/"overlap.json";p.write_text(json.dumps(m))
    with pytest.raises(ValueError,match="overlaps the 32"):
        fixed_24_manifest(p,PRIOR)


def test_frozen_24_manifest_omits_2025_and_2026_classifier_scores():
    m=json.loads(Path(FROZEN).read_text())
    for r in m["source_records"]:
        assert "score" not in r
        assert set(r)>= {"uid","tic_id","sector_run","original_2025_historical_label"}
        assert 2<=r["old_2025_period_days_display_only"]<=10
