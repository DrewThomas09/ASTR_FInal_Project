"""Create a scientific provenance manifest for a local NASA Kepler DR25 CSV.

This script does not train a model. It validates the required schema, records
the file hash, and reports label counts and missing measurements.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json
import numpy as np
import pandas as pd

SOURCE_TABLE="q1_q17_dr25_koi"
REQUIRED=("kepid","kepoi_name","koi_pdisposition",
          "koi_period","koi_duration","koi_depth","koi_model_snr")
FEATURES=REQUIRED[3:]
DISPOSITIONS=("CANDIDATE","FALSE POSITIVE")


def make_manifest(csv_path):
    path=Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    hasher=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024*1024), b""):
            hasher.update(chunk)
    data=pd.read_csv(path,comment="#")
    missing=set(REQUIRED)-set(data.columns)
    if missing:
        raise ValueError("Missing expected NASA columns: "+repr(sorted(missing)))
    retained=data.loc[data["koi_pdisposition"].isin(DISPOSITIONS)].copy()
    retained=retained.dropna(subset=["kepid","kepoi_name"]).drop_duplicates("kepoi_name")
    if len(retained)<500 or retained.koi_pdisposition.nunique()!=2:
        raise ValueError("Unexpected NASA data: incomplete or missing labels")
    numeric={}
    for col in FEATURES:
        values=pd.to_numeric(retained[col],errors="coerce")
        values=values.where(np.isfinite(values)&(values>=0))
        numeric[col]={"missing_count":int(values.isna().sum()),
                      "missing_fraction":float(values.isna().mean()),
                      "median":float(values.median()) if values.notna().any() else None}
    return {
        "source":"NASA Exoplanet Archive Kepler DR25 KOI catalog",
        "table":SOURCE_TABLE,
        "query_columns":list(REQUIRED),
        "generated_utc":datetime.now(timezone.utc).isoformat(),
        "csv_file_name":path.name,
        "csv_size_bytes":path.stat().st_size,
        "csv_sha256":hasher.hexdigest(),
        "rows_in_file":int(len(data)),
        "rows_after_labeled_deduplication":int(len(retained)),
        "distinct_host_stars":int(retained.kepid.nunique()),
        "disposition_counts":{k:int((retained.koi_pdisposition==k).sum()) for k in DISPOSITIONS},
        "measurements":numeric,
        "label_warning":"koi_pdisposition is an historical automatic vetter classification, not independently confirmed planet truth",
        "selection_warning":"Kepler Objects of Interest (KOI) are a preselected subset of all transit-like threshold crossings",
        "metadata_warning":"Store exact NASA TAP query URL separately; no alternate data versions should be silently substituted",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",default="data/kepler_dr25.csv")
    p.add_argument("--out",default="results/ml/data_manifest.json")
    args=p.parse_args()
    manifest=make_manifest(args.csv)
    dst=Path(args.out)
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({k:manifest[k] for k in ("csv_sha256","rows_in_file",
       "rows_after_labeled_deduplication","distinct_host_stars",
       "disposition_counts")},indent=2))


if __name__=="__main__":
    main()
