"""Post-hoc version-aware TESS TCE identity audit for published 2025 vs NASA 2026 outputs.

Scientific purpose: CHECK whether the older and newer catalog rows describe
the same fitted astrophysical signal before interpreting "resolved" old
classification errors. This analysis is exploratory AFTER seeing the 2026
scores; it cannot be reported as a preregistered accuracy test.

Critical schema difference: original 2025 ExoMiner++ tce_duration is DAYS;
the 2026 operational NASA pipeline CSV tce_duration is HOURS.
A common UID is NOT sufficient for same-event identity across versions.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd


def classify_period_ratio(new_period,old_period,tolerance=.01):
    """Strict, version-aware period identity audit; aliases remain ambiguous."""
    if not (np.isfinite(new_period) and np.isfinite(old_period) and new_period>0 and old_period>0):
        return "invalid_ephemeris"
    ratio=float(new_period/old_period)
    if abs(ratio-1)<=tolerance:
        return "period_consistent_within_one_percent"
    if abs(ratio-2)<=2*tolerance:
        return "new_period_double_alias"
    if abs(ratio-.5)<=.5*tolerance:
        return "new_period_half_alias"
    return "different_fitted_period"


def verify_public_2025(path):
    digest=hashlib.md5()
    n=0
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            n+=len(b);digest.update(b)
    if n!=8944735 or digest.hexdigest()!="c79f3651d556e71f7878a46f960d09b4":
        raise ValueError("Only original pinned public NASA 2025 TESS labeled CSV accepted")
    return digest.hexdigest()


def run(a_csv,b_csv,manifest_path,out_dir):
    src=verify_public_2025(a_csv)
    spec=json.loads(Path(manifest_path).read_text())
    if spec.get("experiment_id")!="EXOMINER_2025_MISTAKES_VS_2026_PRETRAINED_CHALLENGE_20261108":
        raise ValueError("Original frozen 16-star selected cohort missing")
    old=pd.read_csv(a_csv).set_index("uid",drop=False)
    new=pd.read_csv(b_csv,comment="#").set_index("uid",drop=False)
    if old.index.has_duplicates or new.index.has_duplicates:
        raise ValueError("Source TCE UID duplicates; version identity ambiguous")
    obs=[]
    for target in spec["source_records"]:
        uid=target["uid"]
        if uid not in old.index:
            raise ValueError(f"Frozen UID missing from original 2025 source: {uid}")
        o=old.loc[uid]
        record={
            "requested_old_TCE_UID":uid,
            "old_label":str(o.label),
            "old_2025_score":float(o.score),
            "old_2025_period_days":float(o.tce_period),
            "old_2025_epoch_BTJD":float(o.tce_time0bk),
            "old_2025_duration_HOURS_converted_from_DAYS":float(o.tce_duration*24.),
            "new_exact_UID_present":uid in new.index,
            "new_exact_UID_score":None,
            "new_exact_UID_period_days":None,
            "new_exact_UID_epoch_BTJD":None,
            "new_exact_UID_duration_HOURS":None,
            "new_over_old_period_ratio":None,
            "new_over_old_duration_ratio_after_UNIT_conversion":None,
            "epoch_abs_delta_days_same_UID":None,
            "period_identity_category":"source_not_scored",
            "alternate_2026_UID_with_matching_old_period":None,
            "alternate_2026_period_ratio":None,
            "alternate_2026_epoch_abs_delta_days":None,
            "same_UID_historical_label_agreement_at_0_5":None,
            "flag_model_score_is_not_necessarily_same_signal":True
        }
        if uid not in new.index:
            obs.append(record)
            continue
        n=new.loc[uid]
        p=float(n.tce_period)
        r=classify_period_ratio(p,float(o.tce_period))
        # NOTE: no assumption about target astrophysical planet truth, even
        # when period and epoch are consistent. Signals can be blended.
        label_positive=bool(o.label in ("KP","CP"))
        record.update({
            "new_exact_UID_score":float(n.score),
            "new_exact_UID_period_days":p,
            "new_exact_UID_epoch_BTJD":float(n.tce_time0bk),
            "new_exact_UID_duration_HOURS":float(n.tce_duration),
            "new_over_old_period_ratio":float(p/o.tce_period),
            "new_over_old_duration_ratio_after_UNIT_conversion":
                float(n.tce_duration/(o.tce_duration*24.)),
            "epoch_abs_delta_days_same_UID":
                float(abs(n.tce_time0bk-o.tce_time0bk)),
            "period_identity_category":r,
            "same_UID_historical_label_agreement_at_0_5":
                bool((n.score>=.5)==label_positive),
            "flag_model_score_is_not_necessarily_same_signal":
                (r!="period_consistent_within_one_percent")
        })
        # Check if older event period/epoch is now carried by ANOTHER TCE of
        # this SAME STAR and SECTOR, not an arbitrary TCE with similar P.
        # The printed UID alone can retain its name but swap the signal.
        others=new.loc[(new.target_id==int(o.target_id)) &
                       (new.sector_run==n.sector_run) &
                       (new.uid!=uid)]
        candidate=[]
        for _,v in others.iterrows():
            ratio=float(v.tce_period/o.tce_period)
            if classify_period_ratio(float(v.tce_period),float(o.tce_period))=="period_consistent_within_one_percent":
                candidate.append((abs(float(v.tce_time0bk-o.tce_time0bk)),
                                  str(v.uid),ratio))
        candidate.sort()
        if candidate:
            elapsed,other,ratio=candidate[0]
            record.update({
                "alternate_2026_UID_with_matching_old_period":other,
                "alternate_2026_period_ratio":ratio,
                "alternate_2026_epoch_abs_delta_days":float(elapsed)
            })
        obs.append(record)
    if len(obs)!=16:
        raise AssertionError("Missing original frozen cohort sources")
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    df=pd.DataFrame(obs)
    df.to_csv(out/"all_16_hardcase_2025_vs_2026_ephemeris_and_duration_UNIT_audit.csv",index=False)
    freq={str(k):int(v) for k,v in df.period_identity_category.value_counts().items()}
    consistent=df[df.period_identity_category=="period_consistent_within_one_percent"]
    stable_comparison={
        "period_consistent_source_UID_count":len(consistent),
        "historical_errors_NOW_agree_with_2025_label_in_consistent_source_set":
            int((consistent.same_UID_historical_label_agreement_at_0_5==True).sum()),
        "historical_errors_STILL_disagree_in_consistent_source_set":
            int((consistent.same_UID_historical_label_agreement_at_0_5==False).sum()),
        "important":"Period consistency + catalog agreement is not independent physical exoplanet validation"
    }
    summary={
        "scope":"POST-HOC cross-version TCE ephemeris identity QA of previously reported hard-case scores; not a new physical planet accuracy claim",
        "original_source_verified_MD5":src,
        "original_frozen_error_cohort_UID_count":16,
        "number_2026_raw_exact_UIDs_available":int(df.new_exact_UID_present.sum()),
        "period_identity_counts":freq,
        "number_same_UID_period_INCONSISTENT_or_aliased":int(
            (df.period_identity_category!="period_consistent_within_one_percent").sum()),
        "retrospective_2025_label_agreement_among_period_consistent":stable_comparison,
        "different_TCE_UID_candidates_matching_old_signal_period":[
            {"old_uid":str(row.requested_old_TCE_UID),
             "new_uid":str(row.alternate_2026_UID_with_matching_old_period),
             "new_to_old_period_ratio":float(row.alternate_2026_period_ratio),
             "epoch_diff_days":float(row.alternate_2026_epoch_abs_delta_days)}
            for row in df.itertuples()
            if pd.notna(row.alternate_2026_UID_with_matching_old_period)
        ],
        "units_must_not_be_mixed":{
            "old_2025_tce_duration_units":"days",
            "new_2026_tce_duration_units":"hours",
            "conversion_rule":"old days * 24 = new comparable hours"
        },
        "limitations":[
            "The UID scheme alone does not establish the identity of astrophysical signals across NASA model processing versions.",
            "A factor-of-two period change may be an ephemeris alias rather than an entirely distinct physical signal; cannot simply call it correct or incorrect.",
            "A changed UID number with near-identical P and epoch is a candidate matching signal, not proof of matching planet truth.",
            "All 16 frozen sources remain visible; grouping by period is a post-hoc methodological QA and not pruning original denominators to inflate accuracy.",
            "Comparison to historic KP/CP or nonplanet labels is not independent follow-up and current 2026 model training overlap remains unknown."
        ]
    }
    (out/"cross_version_signal_identity_qualification.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2),flush=True)
    return summary


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-2025-catalog",required=True)
    p.add_argument("--original-2026-model-results",required=True)
    p.add_argument("--frozen-cohort",default="TESS_16STAR_2025_ERRORS_VS_2026_FROZEN_2026_11_08.json")
    p.add_argument("--out",default="results/cross_version_ephemeris_identity")
    a=p.parse_args()
    run(a.original_2025_catalog,a.original_2026_model_results,a.frozen_cohort,a.out)
