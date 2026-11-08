"""Reproduce the frozen 24-star TESS holdout without reading ANY model scores.

The source was preselected independently of its 2026 ExoMiner++ model output,
and by excluding the 32 sources previously used to develop the centroid
review rule. It is *not* necessarily excluded from NASA's own training.

Input must be exactly the original NASA 2025 labeled TCE Zenodo CSV, checked
against MD5. pandas.read_csv(usecols=...) makes it impossible for this routine
to access the 'score' field when selecting source IDs.
"""
from __future__ import annotations
import hashlib
import json
import re
import argparse
from pathlib import Path
import pandas as pd
from tess_exominer_cross_version_ephemeris_audit import verify_public_2025


SEED="ASTR_CENTROID_24STAR_HOLDOUT_20261108"
COLUMN_WHITELIST=[
    "uid","target_id","label","fold","tce_period","tce_duration",
    "tce_max_mult_ev"
]


def reselect_new_24_sources(original_2025_csv,
                            prior_32_manifest="TESS_32STAR_CENTROID_ALIAS_COMPANION_FROZEN_2026_11_08.json"):
    verify_public_2025(original_2025_csv)
    from tess_original_moment_centroid_companion import verify_frozen_manifest
    earlier=verify_frozen_manifest(prior_32_manifest)
    excluded={int(s["tic_id"]) for s in earlier["source_records"]}|{167526485}
    df=pd.read_csv(original_2025_csv,usecols=COLUMN_WHITELIST)
    if "score" in df.columns:
        raise AssertionError("Never select on NASA released score")
    filtered=df[
        (df.tce_period>=2)&(df.tce_period<=10)&
        (df.tce_duration>=.05)&(df.tce_duration<=.4)&
        (~df.target_id.isin(excluded))
    ].copy()
    filtered["sector"]=pd.to_numeric(
        filtered.uid.astype(str).str.extract(r"\-1\-S(\d+)$")[0],
        errors="coerce")
    filtered=filtered[filtered.sector.between(3,12)]
    filtered["stable_order"]=filtered.uid.map(lambda s:
        hashlib.sha256((SEED+"|"+str(s)).encode("utf-8")).hexdigest())
    chosen=[]
    used=set(excluded)
    for label in ("KP","CP","EB","NTP"):
        for band,lower,upper in (("7-20",7,20),("20-80",20,80)):
            portion=filtered[
                (filtered.label==label)&
                (filtered.tce_max_mult_ev>=lower)&
                (filtered.tce_max_mult_ev<upper)
            ].sort_values("stable_order")
            count=0
            for row in portion.itertuples(index=False):
                tic=int(row.target_id)
                if tic in used:
                    continue
                used.add(tic)
                chosen.append({
                    "uid":str(row.uid),"tic_id":tic,
                    "sector_run":f"{int(row.sector)}-{int(row.sector)}",
                    "original_2025_historical_label":label,
                    "MES_band":band,
                    "old_2025_period_days_display_only":round(float(row.tce_period),7),
                    "old_2025_duration_days_display_only":round(float(row.tce_duration),7),
                    "old_2025_multiple_event_statistic_display_only":round(float(row.tce_max_mult_ev),7)
                })
                count+=1
                if count==3:break
            if count!=3:
                raise ValueError(f"Insufficient distinct original TESS hosts for {label} {band}")
    if len(chosen)!=24 or len({s["tic_id"] for s in chosen})!=24:
        raise AssertionError("Frozen score-blind selection must contain 24 distinct hosts")
    return chosen


def verify_locked_24_selection(original_2025,holdout_manifest):
    reproducible=reselect_new_24_sources(original_2025)
    frozen=json.loads(Path(holdout_manifest).read_text())["source_records"]
    if len(frozen)!=24 or reproducible!=frozen:
        raise ValueError("Actual original NASA score-blind source selection does not exactly reproduce prior-to-model frozen TICs")
    return {
        "cohort_id":"TESS_NEW_TO_STUDENT_24_STAR_FIXED_CENTROID_GATE_HOLDOUT_20261108",
        "source_md5_checked":True,
        "score_column_ever_read":False,
        "all_original_24_TCE_UIDs_match":True,
        "new_to_previous_32_sources":True,
        "source_TIC_count":24
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--catalog",required=True)
    p.add_argument("--manifest",default="TESS_NEW_24STAR_CENTROID_RULE_HOLDOUT_FROZEN_2026_11_08.json")
    a=p.parse_args()
    print(json.dumps(verify_locked_24_selection(a.catalog,a.manifest),indent=2))
