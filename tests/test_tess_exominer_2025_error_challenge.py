"""Synthetic safety checks for historical 2025 ExoMiner mistakes versus actual 2026 score comparisons."""
import json
from pathlib import Path

import pandas as pd
import pytest

import tess_exominer_2025_error_challenge as challenge


FROZEN="TESS_16STAR_2025_ERRORS_VS_2026_FROZEN_2026_11_08.json"


def make_manifest(tmp_path):
    official=json.loads(Path(FROZEN).read_text())
    p=tmp_path/"challenge.json"
    p.write_text(json.dumps(official))
    return p


def original_source_stub(manifest):
    return pd.DataFrame([
        {
            "uid":r["uid"],"target_id":r["tic_id"],
            "label":r["published_2025_label"],
            "score":r["published_2025_score_display_rounded"]
        } for r in manifest["source_records"]
    ]).set_index("uid")


def predictions_stub(tmp_path,manifest,n=2):
    rows=[]
    for r in manifest["source_records"][:n]:
        # Originally missed historical planets now scored above .5 in 2026.
        # A real inference must supply this; fixtures only exercise accounting.
        rows.append({
            "uid":r["uid"],"target_id":r["tic_id"],
            "sector_run":int(r["sector_run"].split("-")[0]),
            "score":.79,"prediction":"PC",
            "tce_period":4.5,"tce_duration":3.,"tce_time0bk":1460.
        })
    path=tmp_path/"mock_original_nasa.csv"
    with path.open("w") as h:
        h.write("# Version Number: 2.4.0\n# Task: planet-validation\n# ExoMiner Model: single\n")
        pd.DataFrame(rows).to_csv(h,index=False)
    return path


def test_original_frozen_2025_hard_cases_are_sixteen_distinct_tics():
    m=challenge.load_manifest(FROZEN)
    assert len(m["source_records"])==16
    assert all(r["uid"].endswith("S"+r["sector_run"].split("-")[0]) for r in m["source_records"])


def test_original_selection_scores_are_purposefully_misclassified_by_2025():
    m=challenge.load_manifest(FROZEN)
    for r in m["source_records"]:
        old=r["published_2025_score_display_rounded"]
        if r["published_2025_error_kind"]=="2025_missed_historical_planet":
            assert old<.5 and r["published_2025_label"] in ("KP","CP")
        else:
            assert old>=.5 and r["published_2025_label"] not in ("KP","CP")


def test_duplicate_historical_source_id_rejected(tmp_path):
    p=make_manifest(tmp_path)
    contents=json.loads(p.read_text())
    contents["source_records"][0]["tic_id"]=contents["source_records"][1]["tic_id"]
    p.write_text(json.dumps(contents))
    with pytest.raises(ValueError,match="unique original TESS stars"):
        challenge.load_manifest(p)


def test_missing_original_source_is_never_silently_removed(tmp_path,monkeypatch):
    path=make_manifest(tmp_path)
    data=challenge.load_manifest(path)
    old=original_source_stub(data)
    monkeypatch.setattr(challenge,"source_2025_rows",lambda *_:old)
    predicted=predictions_stub(tmp_path,data,n=2)
    before=predicted.read_bytes()
    result=challenge.evaluate(path,"ignored_original_source.csv",predicted,tmp_path,tmp_path/"out")
    assert result["n_preselected_historical_2025_source_errors"]==16
    assert result["n_exact_2025_UIDs_scored_by_NASA_2026"]==2
    assert result["n_original_2025_historical_mistakes_resolved_in_2026"]==2
    assert result["n_original_2025_error_sources_unscored"]==14
    assert predicted.read_bytes()==before
    recorded=pd.read_csv(tmp_path/"out"/"all_16_prespecified_2025_model_errors_and_actual_2026_outcomes.csv")
    assert len(recorded)==16


def test_wrong_published_source_hash_rejected(tmp_path):
    f=tmp_path/"wrong.csv"
    f.write_text("uid,score\nA,.7\n")
    with pytest.raises(ValueError,match="exact released"):
        challenge.source_2025_rows(f,challenge.load_manifest(FROZEN))


def test_historical_score_and_label_are_immutable_within_model_comparison(tmp_path,monkeypatch):
    p=make_manifest(tmp_path)
    m=challenge.load_manifest(p)
    rows=original_source_stub(m)
    monkeypatch.setattr(challenge,"source_2025_rows",lambda *_:rows)
    pred=predictions_stub(tmp_path,m,n=2)
    result=challenge.evaluate(p,"source2015.csv",pred,tmp_path,tmp_path/"out2")
    df=pd.read_csv(tmp_path/"out2"/"all_16_prespecified_2025_model_errors_and_actual_2026_outcomes.csv")
    assert df.iloc[0]["original_2025_out_of_fold_score"]==m["source_records"][0]["published_2025_score_display_rounded"]
    assert result["n_original_2025_historical_mistakes_persist_in_2026"]==0
