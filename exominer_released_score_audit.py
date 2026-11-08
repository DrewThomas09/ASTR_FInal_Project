"""Source-pinned audit of already-published NASA ExoMiner++ 2025 TESS scores.

This ONLY reproduces descriptive published label-vs-score statistics.
It does not train any model, claim an independent holdout, or imply that
reported unlabeled scores have become confirmed physical planets.

Inputs: the exact 2025 NASA/USRA team's Zenodo record 15466293 CSVs.
Source fingerprints are required, not optional.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score, roc_auc_score, confusion_matrix,
    precision_score, recall_score, precision_recall_curve
)

KNOWN_PLANET_LABELS={"KP","CP"}
EXPECTED_CLASSES={"NTP","EB","CP","KP","NEB","FP","NPC","BD"}


def pinned_sources(manifest_path):
    manifest=json.loads(Path(manifest_path).read_text())
    if manifest.get("dataset_version_specific_doi")!="10.5281/zenodo.15466293":
        raise ValueError("Zenodo source version is not frozen")
    specs={x["role"]:x for x in manifest["pinned_catalog_files"]}
    if set(specs)!={"historically_labeled_TCEs",
                    "unlabeled_TCEs_with_published_scores"}:
        raise ValueError("Missing one released original catalog")
    return specs


def verify_catalog(path,spec):
    path=Path(path)
    digest=hashlib.md5()
    count=0
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            count+=len(chunk)
            digest.update(chunk)
    if count!=spec["bytes"] or digest.hexdigest()!=spec["md5"]:
        raise ValueError("Original Zenodo CSV source hash/size mismatch")
    return {"size_bytes":count,"published_md5":digest.hexdigest()}


def check_labeled_table(df):
    needed={"uid","target_id","label","tce_period","tce_max_mult_ev",
            "score","fold","tce_plnt_num"}
    if not needed.issubset(df.columns):
        raise ValueError("Missing essential ExoMiner++ published columns")
    if len(df)!=57162 or df.uid.duplicated().any():
        raise ValueError("Unexpected row count or duplicate official TCE UIDs")
    if set(df.label.dropna().unique())!=EXPECTED_CLASSES:
        raise ValueError("Unexpected or missing NASA published labels")
    if (df.score.isna().any() or
        not np.isfinite(df.score.to_numpy(dtype=float)).all() or
        not df.score.between(0,1).all()):
        raise ValueError("Invalid published score")
    if set(df.fold.unique())!=set(range(10)):
        raise ValueError("Expected ten published cross-validation folds")
    # Different sector observations of the same source must share one fold.
    leakage=int((df.groupby("target_id",observed=True).fold.nunique()>1).sum())
    if leakage:
        raise ValueError(f"Published host target appears in multiple folds: {leakage}")
    return {"host_fold_leakage_count":0,
            "unique_target_stars":int(df.target_id.nunique()),
            "unique_tce_uids":int(df.uid.nunique())}


def threshold_metrics(y,score,cutoff):
    y=np.asarray(y,dtype=bool)
    s=np.asarray(score,dtype=float)
    pred=s>=cutoff
    tn,fp,fn,tp=(int(v) for v in confusion_matrix(y,pred,labels=[False,True]).ravel())
    return {
        "threshold":float(cutoff),"n":len(y),
        "catalog_planet_labels":int(y.sum()),
        "catalog_nonplanet_labels":int((~y).sum()),
        "catalog_planet_precision":float(precision_score(y,pred,zero_division=0)),
        "catalog_planet_recall":float(recall_score(y,pred,zero_division=0)),
        "predicted_positive_TCE_rows":int(pred.sum()),
        "true_positive_TCE_rows":tp,"false_positive_TCE_rows":fp,
        "false_negative_TCE_rows":fn,"true_negative_TCE_rows":tn
    }


def score_summary(subset):
    y=subset.label.isin(KNOWN_PLANET_LABELS).to_numpy(dtype=bool)
    s=subset.score.to_numpy(dtype=float)
    npos=int(y.sum())
    # 3 long-period positives are not enough for interpretable AP estimates.
    return {
        "n_TCE_rows":len(subset),
        "n_unique_stars":int(subset.target_id.nunique()),
        "n_labeled_planets":npos,
        "n_other":int((~y).sum()),
        "average_precision_sklearn":(
            float(average_precision_score(y,s))
            if npos>=30 and int((~y).sum())>=30 else None),
        "roc_auc_sklearn":(
            float(roc_auc_score(y,s))
            if npos>=30 and int((~y).sum())>=30 else None),
        "threshold_0_5":threshold_metrics(y,s,.5)
    }


def run(labeled_path,unknown_path,manifest_path,out_dir):
    specs=pinned_sources(manifest_path)
    l_source=verify_catalog(labeled_path,specs["historically_labeled_TCEs"])
    u_source=verify_catalog(unknown_path,specs["unlabeled_TCEs_with_published_scores"])
    labeled=pd.read_csv(labeled_path)
    unknown=pd.read_csv(unknown_path,low_memory=False)
    census=check_labeled_table(labeled)
    if len(unknown)!=147567:
        raise ValueError("Unexpected original UNK catalog row count")
    if unknown["TCE ID"].duplicated().any():
        raise ValueError("Repeated official unlabeled TCE ID")
    if unknown["ExoMiner Score"].isna().any():
        raise ValueError("Missing published unlabeled score")
    if not unknown["ExoMiner Score"].between(0,1).all():
        raise ValueError("Unlabeled scores outside range [0,1]")

    y=labeled.label.isin(KNOWN_PLANET_LABELS).to_numpy(dtype=bool)
    s=labeled.score.to_numpy(dtype=float)
    overall=score_summary(labeled)
    class_counts={str(k):int(v) for k,v in labeled.label.value_counts().items()}
    by_fold=[]
    for fold,frame in labeled.groupby("fold",sort=True):
        by_fold.append({"fold":int(fold),**score_summary(frame)})
    by_label=[]
    for label,frame in labeled.groupby("label",sort=True):
        by_label.append({"label":str(label),"n":len(frame),
                         "median_published_score":float(frame.score.median()),
                         "count_published_score_ge_0_5":int((frame.score>=.5).sum()),
                         "count_published_score_ge_0_99":int((frame.score>=.99).sum())})

    def band_metrics(column,bounds,names):
        bucket=pd.cut(labeled[column],bins=bounds,labels=names,right=False)
        data=[]
        for name in names:
            df=labeled.loc[bucket==name]
            data.append({"category":name,**score_summary(df)})
        return data

    period=band_metrics("tce_period",[-np.inf,2,10,100,np.inf],
                        ["period<2d","period2to10d","period10to100d","period>=100d"])
    mes=band_metrics("tce_max_mult_ev",[-np.inf,10,15,30,np.inf],
                     ["MES<10","MES10to15","MES15to30","MES>=30"])
    pair_count=int(labeled.groupby(["target_id","tce_plnt_num"]).ngroups)
    repeated=int(labeled.duplicated(["target_id","tce_plnt_num"]).sum())
    same_pair_label_disagreement=int((
        labeled.groupby(["target_id","tce_plnt_num"]).label.nunique()>1).sum())

    output=Path(out_dir)
    output.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(by_fold).to_csv(output/"released_score_per_fold.csv",index=False)
    pd.DataFrame(by_label).to_csv(output/"released_score_by_class.csv",index=False)
    pd.DataFrame(period).to_csv(output/"released_score_period_subgroups.csv",index=False)
    pd.DataFrame(mes).to_csv(output/"released_score_MES_subgroups.csv",index=False)

    bad_fp=labeled.loc[~y & (s>=.5)].nlargest(40,"score")
    bad_fn=labeled.loc[y & (s<.5)].nsmallest(40,"score")
    columns=["uid","target_id","tce_plnt_num","label","tce_period",
             "tce_max_mult_ev","score","fold"]
    bad_fp[columns].to_csv(output/"published_label_disagreements_high_scored_nonplanets.csv",index=False)
    bad_fn[columns].to_csv(output/"published_label_disagreements_low_scored_knownplanets.csv",index=False)

    ustar=unknown["TIC ID"].nunique()
    nscore=unknown["ExoMiner Score"]
    report={
        "scientific_scope":"Descriptive re-evaluation of RELEASED 10-fold ExoMiner++ scores and labels; no retraining, no independent discovery, no fresh validation",
        "release":"Valizadegan et al. 2025 TESS SPOC 2-minute S1-S67 ExoMiner++ TESS+Kepler catalog",
        "source_version_DOI":"10.5281/zenodo.15466293",
        "labeled_source_integrity":l_source,
        "unknown_source_integrity":u_source,
        "cross_validation_group_integrity":census,
        "published_label_counts":class_counts,
        "catalog_planet_label_definition":"KP or CP are positives. All other published labels are negatives, including BD, EB, NEB, FP, NPC, NTP.",
        "labeled_TCE_released_score_performance":overall,
        "preselected_thresholds":[threshold_metrics(y,s,t) for t in (.5,.9,.95,.99)],
        "per_published_fold":by_fold,
        "label_subclass_summary":by_label,
        "period_subgroups":period,
        "MES_subgroups":mes,
        "repeated_observations_warning":{
            "unique_host_planet_number_pairs":pair_count,
            "additional_rows_reusing_host_and_planet_number":repeated,
            "pairs_with_different_published_labels_across_sector_runs":same_pair_label_disagreement,
            "note":"A host_id + tce_plnt_num across sector runs is NOT necessarily one identical physical event or invariant planetary truth: validate individual ephemerides before interpreting cross-sector label differences."
        },
        "released_unlabeled_catalog":{
            "number_of_TCE_rows":len(unknown),
            "number_distinct_TIC_stars":int(ustar),
            "number_distinct_UID":int(unknown["TCE ID"].nunique()),
            "number_scores_ge_0_5":int((nscore>=.5).sum()),
            "number_scores_gt_0_5":int((nscore>.5).sum()),
            "number_scores_ge_0_99":int((nscore>=.99).sum()),
            "number_targets_also_in_labeled_catalog":int(len(
                set(unknown["TIC ID"].dropna())&set(labeled.target_id))),
            "note":"These are scores on previously UNLABELED TCE observations, not astrophysically confirmed planets. Do not compare simple score thresholds directly to the published 7330 candidate-selection rule, which may include extra catalog logic or a different numerical cutoff."
        },
        "caveats":[
            "The 2025 paper's reported best PR-AUC ~0.976 and our ~0.970 released-score descriptive PR-AUC differ. They may use different aggregation, comparison samples or score conventions; do not claim exact replication of its Table 6 without resolving dataset/method differences.",
            "The 10 folds are a released researcher's CV table. They are not untouched future stars for OUR newly proposed model; scores were generated during the original paper's development.",
            "Multiple TCE observations from one host or same planet number are correlated; row-level confidence intervals/p-values would be invalid for population inference.",
            "Only 3 KP/CP positive event rows have published periods >=100 days in this catalog. Do NOT present a reliable long-period sensitivity estimate from that bin.",
            "Label CP/KP does not prove an independent raw-light-curve planet discovery; false alarm rate for all observed stars must be measured on unbiased population or injections.",
            "The 2022 original ExoMiner Kepler paper the user provided is a different publication and cohort than this 2025 TESS ExoMiner++ CSV release."
        ]
    }
    (output/"verified_released_score_audit.json").write_text(json.dumps(report,indent=2)+"\n")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    precision,recall,_=precision_recall_curve(y,s)
    fig,ax=plt.subplots(figsize=(7,5))
    ax.plot(recall,precision,lw=2,label=f"Published ExoMiner++ scores (AP={overall['average_precision_sklearn']:.3f})")
    ax.axhline(y.mean(),ls="--",lw=1,label=f"Catalog positive fraction={100*y.mean():.2f}%")
    ax.set(xlabel="Recall on released KP/CP labels",
           ylabel="Precision on released KP/CP labels",
           title="2025 TESS ExoMiner++ published scores — descriptive CV audit",
           xlim=(0,1),ylim=(0,1.02))
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(output/"published_score_precision_recall.png",dpi=150)
    plt.close(fig)
    print(json.dumps({
        "labeled_TCE_rows":len(labeled),
        "unique_labeled_target_stars":census["unique_target_stars"],
        "historical_KP_CP_labels":int(y.sum()),
        "published_score_average_precision":overall["average_precision_sklearn"],
        "published_score_ROC_AUC":overall["roc_auc_sklearn"],
        "threshold_0_5":overall["threshold_0_5"],
        "unlabeled_TCE_rows":len(unknown),
        "published_fold_host_leakage_count":census["host_fold_leakage_count"],
        "long_period_positive_labels":period[-1]["n_labeled_planets"],
        "warning":"Published score audit only; no original CNN retraining or independently calibrated planet discovery."
    },indent=2),flush=True)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--labeled",required=True)
    p.add_argument("--unknown",required=True)
    p.add_argument("--manifest",default="EXOMINER_PUBLIC_DATA_MANIFEST_2026_11_08.json")
    p.add_argument("--out",default="results/exominer_released_score_audit")
    a=p.parse_args()
    run(a.labeled,a.unknown,a.manifest,a.out)
