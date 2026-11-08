"""Score-blind cohort rules, original model score immutability, missing-star accounting."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from tess_exominer_16star_cohort_audit import (
    source_manifest, analyze_sources
)


def seeded_frozen_meta():
    labels=["KP","CP","EB","NTP"]
    records=[]
    for c,lab in enumerate(labels):
        for q in range(4):
            tic=100000000+100*c+q
            sector=3+(q%3)
            records.append({
                "uid":f"{tic}-1-S{sector}","tic_id":tic,
                "sector_run":f"{sector}-{sector}",
                "published_2025_label":lab,
                "published_2025_fold":q%10,
                "MES_band":"7-20" if q<2 else "20-80",
                "period_days_from_published_catalog":4.5,
                "signal_multiple_event_statistic":10. if q<2 else 30.
            })
    return {"experiment_id":"EXOMINER_16_HOST_SCORE_BLIND_FEASIBILITY_20261108",
            "source_records":records}


def make_meta(tmp_path):
    p=tmp_path/"cohort.json"
    p.write_text(json.dumps(seeded_frozen_meta()))
    return p


def make_nasa_csv(path,metarows,keep=2):
    rows=[]
    for row in metarows[:keep]:
        sector=row["sector_run"].split("-")[0]
        rows.append({
            "uid":row["uid"],"target_id":row["tic_id"],
            "sector_run":int(sector),"score":0.45,
            "prediction":"NOT_PC","tce_period":4.5,
            "tce_duration":3.,"tce_time0bk":1470.
        })
    p=path/"original_nasa.csv"
    with p.open("w") as handle:
        handle.write("# Version Number: 2.4.0\n# Task: planet-validation\n# ExoMiner Model: single\n")
        pd.DataFrame(rows).to_csv(handle,index=False)
    return p


def test_frozen_cohort_requires_four_per_label_and_two_per_MES(tmp_path):
    p=make_meta(tmp_path)
    spec=source_manifest(p)
    assert len(spec["source_records"])==16
    assert len(set(x["tic_id"] for x in spec["source_records"]))==16


def test_frozen_protocol_rejects_fabricated_sector_and_duplicate_star(tmp_path):
    m=seeded_frozen_meta()
    m["source_records"][1]["tic_id"]=m["source_records"][0]["tic_id"]
    f=tmp_path/"bad.json";f.write_text(json.dumps(m))
    with pytest.raises(ValueError,match="different stars"):
        source_manifest(f)
    m=seeded_frozen_meta()
    m["source_records"][0]["sector_run"]="5-9"
    f.write_text(json.dumps(m))
    with pytest.raises(ValueError,match="single-sector"):
        source_manifest(f)


def test_every_unavailable_nasa_source_is_kept_in_denominator(tmp_path):
    spec=seeded_frozen_meta()
    mf=make_meta(tmp_path)
    csv=make_nasa_csv(tmp_path,spec["source_records"],keep=2)
    original=csv.read_bytes()
    out=tmp_path/"output"
    report=analyze_sources(mf,csv,tmp_path,out)
    assert report["n_prespecified_unique_TIC_stars"]==16
    assert report["n_exact_requested_2025_TCE_UIDs_scored_by_2026_NASA"]==2
    assert report["n_exact_requested_2025_TCE_UIDs_missing"]==14
    assert report["n_orig_MAST_TESS_FITS_sidecar_analyzed"]==0
    assert csv.read_bytes()==original
    df=pd.read_csv(out/"all_16_frozen_stars_including_failed_sources.csv")
    assert len(df)==16
    assert df.NASA_2026_exact_UID_found.sum()==2
    assert all(df.NASA_2026_official_planet_score.dropna()==0.45)
    assert all(df.loc[2:,"same_TESS_FITS_sidecar_status"]=="not_attempted")


def test_identical_official_UID_cannot_be_counted_twice(tmp_path):
    meta=seeded_frozen_meta(); mf=make_meta(tmp_path)
    csv=make_nasa_csv(tmp_path,meta["source_records"],keep=2)
    with csv.open("a") as f:
        f.write(csv.read_text().splitlines()[-1]+"\n")
    with pytest.raises(ValueError,match="identical TCE UID"):
        analyze_sources(mf,csv,tmp_path,tmp_path/"out")


def test_missing_nasa_pretrained_header_not_accepted(tmp_path):
    meta=seeded_frozen_meta(); mf=make_meta(tmp_path)
    csv=make_nasa_csv(tmp_path,meta["source_records"],keep=2)
    csv.write_text(csv.read_text().replace("planet-validation","phot-vetting"))
    with pytest.raises(ValueError,match="Wrong NASA ExoMiner inference task"):
        analyze_sources(mf,csv,tmp_path,tmp_path/"out")


def test_report_has_no_fake_statistical_confidence_or_discovery_claim(tmp_path):
    meta=seeded_frozen_meta(); mf=make_meta(tmp_path)
    csv=make_nasa_csv(tmp_path,meta["source_records"],keep=2)
    report=analyze_sources(mf,csv,tmp_path,tmp_path/"out")
    assert report["NASA_original_model_unmodified"] is True
    assert "not an independent model holdout" in report["statistics"].lower()
    assert len(report["descriptive_2025_label_vs_2026_output_at_0_5"])==4
