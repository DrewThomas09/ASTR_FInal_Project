"""Apply precommitted development-calibrated centroid warning on 24 new TESS stars.

The original fixed >=.05px warning tested on 32 previously scrutinized stars
fired on zero sources. AFTER seeing those 32 and BEFORE inspecting the 24
additional-star results, the author froze a separate *development-learned*
threshold: the 95th percentile using method='higher' of thirteen eligible
historical KP/CP centroid magnitudes, 0.0016012455384686 px.

This is ONLY a manual-review sidecar; it does NOT change NASA ExoMiner scores.
Nor does the 24-source study independently evaluate NASA's neural training.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd


def checked_original_development_centroids(path,protocol):
    sha=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if sha!=protocol["source_development_csv_expected_SHA256"]:
        raise ValueError("32-development source magnitude table differs from frozen source hash")
    df=pd.read_csv(path)
    if len(df)!=32 or df.TIC_ID.nunique()!=32 or df.uid.duplicated().any():
        raise ValueError("Original fixed 32-star source inventory mismatch")
    n=df[
        df.original_2025_historical_label.isin(["KP","CP"])&
        (df.corrected_usable_event_count>=3)&
        df.corrected_median_vector_shift_pixels.notna()
    ]
    value=float(np.quantile(
        n.corrected_median_vector_shift_pixels.to_numpy(dtype=float),
        protocol["calibration_quantile"],method=protocol["quantile_method"]))
    if len(n)!=protocol["n_eligible_positive_development_stars"] or not np.isclose(
            value,protocol["frozen_resulting_centroid_threshold_pixels"],
            rtol=1e-10,atol=0):
        raise ValueError("Precommitted development-only threshold not reproducible")
    return value,n


def parse_interval(src):
    if isinstance(src,(float,np.floating)) and np.isnan(src):
        return None
    if src is None:
        return None
    if isinstance(src,str):
        try:
            o=json.loads(src)
        except json.JSONDecodeError:
            raise ValueError("Malformed original bootstrap axis interval")
    else:
        o=src
    if o is None:
        return None
    if not isinstance(o,list) or len(o)!=2:
        raise ValueError("Original bootstrap axis interval not two values")
    lo,hi=(float(i) for i in o)
    if not all(np.isfinite(z) for z in (lo,hi)) or lo>hi:
        raise ValueError("Invalid bootstrap interval")
    return lo,hi


def axis_interval_nonzero(x,y):
    a,b=parse_interval(x),parse_interval(y)
    if a is None or b is None:
        return None
    return bool(a[0]>0 or a[1]<0 or b[0]>0 or b[1]<0)


def score_one(observation,threshold):
    cnt=observation.corrected_centroid_source_event_count
    mag=observation.corrected_median_event_local_centroid_vector_pixels
    if pd.isna(cnt) or cnt<3 or pd.isna(mag):
        return {"eligible":False,"centroid_warning":None,
                "NASA_candidate_AND_centroid_warning":None}
    flag=axis_interval_nonzero(
        observation.corrected_bootstrap_95pct_x_interval,
        observation.corrected_bootstrap_95pct_y_interval)
    if flag is None:
        return {"eligible":False,"centroid_warning":None,
                "NASA_candidate_AND_centroid_warning":None}
    displacement=float(mag)>threshold
    review=bool(displacement and flag)
    official_score=observation.original_2026_NASA_score_unchanged
    applies=bool(review and pd.notna(official_score) and float(official_score)>=.5)
    return {"eligible":True,"centroid_warning":review,
            "NASA_candidate_AND_centroid_warning":applies}


def assess(frozen_file,development32_csv,holdout24_csv,holdout_manifest,out):
    settings=json.loads(Path(frozen_file).read_text())
    if settings["experiment_id"]!="TESS_32_DEVELOPMENT_TO_24_NEW_SOURCE_CENTROID_MAGNITUDE_GATE_20261108":
        raise ValueError("Wrong previously frozen development-derived threshold")
    threshold,training=checked_original_development_centroids(development32_csv,settings)
    old_gate=.05
    original_manifest=json.loads(Path(holdout_manifest).read_text())
    if original_manifest["experiment_id"]!="TESS_NEW_TO_STUDENT_24_STAR_FIXED_CENTROID_GATE_HOLDOUT_20261108":
        raise ValueError("Not the previously frozen 24-star no-score-selection holdout")
    dataframe=pd.read_csv(holdout24_csv)
    expected={x["uid"] for x in original_manifest["source_records"]}
    observed=set(dataframe.uid)
    if len(dataframe)!=24 or dataframe.uid.duplicated().any() or expected!=observed:
        raise ValueError("Missing/extra 24 holdout source UIDs; no silent sample exclusions allowed")
    original_class={x["uid"]:x["original_2025_historical_label"] for x in original_manifest["source_records"]}
    if any(row.published_2025_label!=original_class[row.uid] for row in dataframe.itertuples(index=False)):
        raise ValueError("24 source class labels changed after data collection")
    # Hard barrier: NO new 24 TESS source data is used to pick a rule.
    rows=[]
    for item in dataframe.itertuples(index=False):
        a=score_one(item,threshold)
        b=score_one(item,old_gate)
        r=item._asdict()
        r.update({
            "new_DEVELOPMENT_CALIBRATED_centroid_magnitude_threshold_pixels":threshold,
            "new_source_centroid_min_3_events_evaluable":a["eligible"],
            "new_source_centroid_warning_at_development_frozen_gate":a["centroid_warning"],
            "new_source_NASA_PC_with_dev_frozen_review_warning":a["NASA_candidate_AND_centroid_warning"],
            "previous_Untuned_Point05px_review_warning":b["centroid_warning"],
            "previous_Untuned_Point05px_NASA_PC_with_warning":b["NASA_candidate_AND_centroid_warning"]
        })
        # Verify original .05 previous row, if not null, matches again.
        old=item.frozen_fixed_centroid_manual_review_flag
        if pd.notna(old) and b["centroid_warning"] is not None:
            if (str(old).lower()=="true")!=b["centroid_warning"]:
                raise ValueError("Older completely untuned warning changed; do not alter frozen rule")
        rows.append(r)
    result=pd.DataFrame(rows)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    result.to_csv(out/"all_24_new_sources_compared_UNCHANGED_point05px_vs_DEV_CALIBRATED_gate.csv",index=False)
    c={"old_fixed_point05px":{},"new_calibrated_dev_95pct_eligible_positives":{}}
    for name,col in [
        ("old_fixed_point05px","previous_Untuned_Point05px_review_warning"),
        ("new_calibrated_dev_95pct_eligible_positives","new_source_centroid_warning_at_development_frozen_gate")
    ]:
        for lab in ("KP","CP","EB","NTP"):
            g=result[result.published_2025_label==lab]
            c[name][lab]={
                "n_original_sources":len(g),
                "n_eligible_with_3_events":int(g[col].notna().sum()),
                "n_flagged_for_manual_review_NOT_as_planet_veto":int((g[col]==True).sum())
            }
    positive=result.published_2025_label.isin(["KP","CP"])
    old_warn=result.previous_Untuned_Point05px_NASA_PC_with_warning==True
    new_warn=result.new_source_NASA_PC_with_dev_frozen_review_warning==True
    summary={
        "scope":"24 genuinely new-to-this-project original TESS stars, not guaranteed excluded from NASA 2026 neural-network training",
        "development_source_hash_verified":settings["source_development_csv_expected_SHA256"],
        "development_n_usable_2025_KP_CP":len(training),
        "development_reference_percentile_rule":settings["calibration_quantile"],
        "development_95th_higher_percentile_centroid_gate_pixels":threshold,
        "old_untuned_gate_pixels":old_gate,
        "holdout_manifest":original_manifest["experiment_id"],
        "new_frozen_24_source_ID_count":24,
        "number_2026_NASA_original_predictions":int(result.original_2026_model_has_exact_TCE_UID.sum()),
        "number_centroid_source_FITS_measured":int((result.source_original_status=="NASA_original_FITS_centroid_measured").sum()),
        "centroid_warning_evaluable_three_events":int(result.new_source_centroid_min_3_events_evaluable.sum()),
        "old_untuned_point05_warning_count":int((result.previous_Untuned_Point05px_review_warning==True).sum()),
        "new_calibrated_dev_warning_count":int((result.new_source_centroid_warning_at_development_frozen_gate==True).sum()),
        "new_dev_warning_on_NASA_original_score_ge_half_count":int(new_warn.sum()),
        "within_NASA_PC_new_review_warnings_published_KP_CP":int((new_warn&positive).sum()),
        "within_NASA_PC_new_review_warnings_published_EB_NTP":int((new_warn&~positive).sum()),
        "within_NASA_PC_old_untuned_review_warnings_published_KP_CP":int((old_warn&positive).sum()),
        "within_NASA_PC_old_untuned_review_warnings_published_EB_NTP":int((old_warn&~positive).sum()),
        "labels_by_rule":c,
        "scientific_caveats":[
            "This development-calibrated threshold was chosen AFTER inspecting the 32 development samples, but frozen BEFORE inspecting new 24-star model outputs, so do not claim original 32 were prospective.",
            "Thirteen positive development stars are far too few to robustly estimate a 95th percentile: method='higher' yields their single maximum.",
            "Comparing source-label warnings is a small historical sample enriched by class/MES rather than an unbiased planet false-alarm test.",
            "The new cohort is withheld from our centroid rule development, NOT proven absent from NASA ExoMiner v2.4.0 training.",
            "The centroid sidecar provides a manual review alert, does not modify the original NASA score or make independent physical planet determinations.",
            "NASA already has pixel-difference/centroid features. Significant astrophysical novelty cannot be claimed from reproducing these diagnostics.",
            "Never tune magnitude percentile, min event count or bootstrap rule on the 24 result."
        ]
    }
    (out/"real_24star_new_source_DEVELOPMENT_CALIBRATED_centroid_gate_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps({
        "n_frozen_new_sources":24,
        "n_centroid_evaluable":summary["centroid_warning_evaluable_three_events"],
        "threshold_from_other_32_training_sources_pixels":threshold,
        "old_untuned_point05_warnings":summary["old_untuned_point05_warning_count"],
        "new_calibrated_warnings":summary["new_calibrated_dev_warning_count"],
        "new_flags_on_NASA_original_planet_scores":summary["new_dev_warning_on_NASA_original_score_ge_half_count"],
        "flags_on_old_KP_CP_labels":summary["within_NASA_PC_new_review_warnings_published_KP_CP"],
        "flags_on_old_EB_NTP_labels":summary["within_NASA_PC_new_review_warnings_published_EB_NTP"],
        "no_NASA_model_modification":True
    },indent=2),flush=True)
    return summary


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--frozen",default="TESS_32_TO_24_CENTROID_POSITIVE_REFERENCE_GATE_FROZEN_2026_11_08.json")
    p.add_argument("--development-32",required=True)
    p.add_argument("--holdout-24",required=True)
    p.add_argument("--holdout-manifest",default="TESS_NEW_24STAR_CENTROID_RULE_HOLDOUT_FROZEN_2026_11_08.json")
    p.add_argument("--out",default="results/tess_new24_posthoc_source_calibrated_centroid_warning")
    a=p.parse_args()
    assess(a.frozen,a.development_32,a.holdout_24,a.holdout_manifest,a.out)
