"""Small score audit checks (no original model training, no label claims)."""
import hashlib
import json
import pytest
import pandas as pd
from exominer_released_score_audit import (
    threshold_metrics, verify_catalog, pinned_sources,
    check_labeled_table
)


def test_metric_denominators_and_binary_types():
    report=threshold_metrics([True,True,False,False],[.9,.1,.8,.2],.5)
    assert report["true_positive_TCE_rows"]==1
    assert report["false_positive_TCE_rows"]==1
    assert report["false_negative_TCE_rows"]==1
    assert report["true_negative_TCE_rows"]==1
    assert report["catalog_planet_recall"]==.5
    assert report["catalog_planet_precision"]==.5


def test_source_digest_must_match_original(tmp_path):
    f=tmp_path/"test.csv"
    f.write_bytes(b"uid,label,score\n1,KP,.9\n")
    valid={"bytes":len(f.read_bytes()),
           "md5":hashlib.md5(f.read_bytes()).hexdigest()}
    assert verify_catalog(f,valid)["size_bytes"]==len(f.read_bytes())
    f.write_bytes(f.read_bytes()+b"\n")
    with pytest.raises(ValueError,match="source hash/size mismatch"):
        verify_catalog(f,valid)


def test_manifest_requires_public_2025_zenodo_source(tmp_path):
    good={"dataset_version_specific_doi":"10.5281/zenodo.15466293",
          "pinned_catalog_files":[
            {"role":"historically_labeled_TCEs","key":"labeled.csv"},
            {"role":"unlabeled_TCEs_with_published_scores","key":"unknown.csv"}
          ]}
    a=tmp_path/"a.json"
    a.write_text(json.dumps(good))
    assert len(pinned_sources(a))==2
    good["dataset_version_specific_doi"]="10.5281/zenodo.99999"
    a.write_text(json.dumps(good))
    with pytest.raises(ValueError,match="not frozen"):
        pinned_sources(a)


def test_labeled_table_rejects_incomplete_or_untrusted_rows():
    frame=pd.DataFrame({"uid":["1"],"target_id":[1],
                        "label":["KP"],"score":[.8],"fold":[3]})
    with pytest.raises(ValueError,match="essential"):
        check_labeled_table(frame)
