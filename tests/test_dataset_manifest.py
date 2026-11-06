"""Offline checks for NASA CSV fingerprint and label-provenance bookkeeping."""
import hashlib
import pandas as pd
import pytest
from dataset_manifest import make_manifest


def write_fake_catalog(path,n=540):
    rows=[]
    for i in range(n):
        rows.append({
          "kepid":80000+i//2,
          "kepoi_name":f"FAKE.{i:05d}",
          "koi_pdisposition":"CANDIDATE" if i%2 else "FALSE POSITIVE",
          "koi_period":i%12+1.0,
          "koi_duration":3.5,
          "koi_depth":1500.0,
          "koi_model_snr":15.0 if i%6 else None})
    pd.DataFrame(rows).to_csv(path,index=False)


def test_manifest_checksum_counts_and_missingness(tmp_path):
    csv=tmp_path/"fake.csv"
    write_fake_catalog(csv)
    result=make_manifest(csv)
    assert result["csv_sha256"]==hashlib.sha256(csv.read_bytes()).hexdigest()
    assert result["rows_after_labeled_deduplication"]==540
    assert result["distinct_host_stars"]==270
    assert result["disposition_counts"]=={"CANDIDATE":270,"FALSE POSITIVE":270}
    assert result["measurements"]["koi_model_snr"]["missing_count"]>0
    assert "not independently confirmed" in result["label_warning"]


def test_manifest_rejects_incomplete_schema(tmp_path):
    csv=tmp_path/"invalid.csv"
    pd.DataFrame({"kepid":[1],"koi_pdisposition":["CANDIDATE"]}).to_csv(csv,index=False)
    with pytest.raises(ValueError):
        make_manifest(csv)


def test_manifest_rejects_tiny_sample(tmp_path):
    csv=tmp_path/"small.csv"
    write_fake_catalog(csv,n=12)
    with pytest.raises(ValueError):
        make_manifest(csv)
