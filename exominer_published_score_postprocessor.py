"""Frozen ExoMiner++ 2025 original published score postprocessing experiment.

Builds TWO NEW logistic postprocessors on NASA's *released* 10-fold TESS
scores. The unmodified original neural score remains in the source CSV:
(1) score-only calibration; (2) same score + physical scalar metadata.
Neither is a retrained NASA CNN. Every student postprocessor is evaluated
out-of-fold on TIC-disjoint published source groups.

The frozen preregistration is EXOMINER_PUBLISHED_SCORE_POSTPROCESSOR_FROZEN_2026_11_08.json.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score,roc_auc_score,confusion_matrix,precision_score,recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from tess_scalar_ai_assisted_replication import host_bootstrap_delta_ap


POSITIVE={"KP","CP"}
NEGATIVE={"EB","NTP","FP","NEB","NPC","BD"}


def load_public_source(path,frozen_path):
    config=json.loads(Path(frozen_path).read_text())
    if config.get("experiment_id")!="EXOMINER_PLUSPLUS_PUBLISHED_OOF_SCORE_POSTPROCESSOR_ABLATION_20261108":
        raise ValueError("Wrong frozen published-score postprocessor experiment")
    digest=hashlib.md5()
    size=0
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):
            size+=len(chunk);digest.update(chunk)
    if size!=config["source_original_byte_count"] or digest.hexdigest()!=config["source_original_MD5"]:
        raise ValueError("Source not exact official original Zenodo publication")
    df=pd.read_csv(path)
    if (len(df)!=config["expected_rows"] or
        df.target_id.nunique()!=config["expected_TIC_hosts"] or
        df.uid.duplicated().any() or set(df.fold.unique())!=set(range(10))):
        raise ValueError("ExoMiner++ canonical TCE/host/fold inventory altered")
    if (df.groupby("target_id").fold.nunique()>1).any():
        raise ValueError("Target star leaks into multiple published folds")
    if set(df.label.unique())!=POSITIVE|NEGATIVE:
        raise ValueError("Original NASA 2025 class label definitions changed")
    if (df.score.isna().any() or not df.score.between(0,1).all() or
        not np.isfinite(df.score.to_numpy(dtype=float)).all()):
        raise ValueError("Original ExoMiner++ crossvalidated score missing or invalid")
    return df,config


def design(df,enhanced=False):
    """No labels, host ID, epoch, or other model-generated predictions as features."""
    source=np.clip(df.score.to_numpy(dtype=float),1e-6,1-1e-6)
    logit=np.log(source/(1-source))
    if not enhanced:
        return logit[:,None]
    nums=[]
    for key in ("tce_period","tce_duration","tce_max_mult_ev"):
        x=df[key].to_numpy(dtype=float)
        if not np.isfinite(x).all() or not (x>0).all():
            raise ValueError("Missing/invalid original NASA physical scalar")
        nums.append(np.log1p(x))
    ruwe=df.ruwe.to_numpy(dtype=float)
    if np.isinf(ruwe).any() or np.any(ruwe[np.isfinite(ruwe)]<=0):
        raise ValueError("Gaia RUWE must be positive when observed")
    ratio=(df.tce_duration/df.tce_period).to_numpy(dtype=float)
    if not np.isfinite(ratio).all() or (ratio<=0).any():
        raise ValueError("Invalid duration/period ratio")
    return np.column_stack([logit,*nums,np.log1p(ruwe),np.log1p(ratio)])


def fit_frozen_folds(df,settings,enhanced=False):
    y=df.label.isin(POSITIVE).to_numpy(dtype=int)
    folds=df.fold.to_numpy(dtype=int)
    X=design(df,enhanced=enhanced)
    out=np.full(len(df),np.nan)
    entries=[]
    for hold in range(10):
        tr=folds!=hold; te=folds==hold
        if set(df.loc[tr,"target_id"]) & set(df.loc[te,"target_id"]):
            raise AssertionError("TIC collision across train/test")
        model=Pipeline([
            ("impute",SimpleImputer(strategy="median",keep_empty_features=True)),
            ("scale",StandardScaler()),
            ("calibrator",LogisticRegression(
                C=settings["model"]["C"],max_iter=settings["model"]["max_iter"],
                solver=settings["model"]["solver"],class_weight=None))
        ])
        model.fit(X[tr],y[tr])
        out[te]=model.predict_proba(X[te])[:,1]
        entries.append({
            "original_NASA_2025_fold":hold,
            "train_star_count":int(df.loc[tr,"target_id"].nunique()),
            "test_star_count":int(df.loc[te,"target_id"].nunique()),
            "test_TCE_observation_count":int(te.sum()),
            "positive_research_labels":int(y[te].sum()),
            "number_model_features":X.shape[1],
            "training_only_median_imputer_and_scaler":True
        })
    if not np.isfinite(out).all() or not np.all((out>=0)&(out<=1)):
        raise RuntimeError("Out-of-fold calibrator predictions incomplete")
    return out,entries


def metric(y,s):
    y=np.asarray(y,dtype=int)
    p=np.asarray(s)>=.5
    tn,fp,fn,tp=(int(x) for x in confusion_matrix(y,p,labels=[0,1]).ravel())
    return {
        "average_precision":float(average_precision_score(y,s)),
        "ROC_AUC":float(roc_auc_score(y,s)),
        "score_threshold":.5,
        "precision_at_0_5":float(precision_score(y,p,zero_division=0)),
        "recall_at_0_5":float(recall_score(y,p,zero_division=0)),
        "tp":tp,"tn":tn,"fp":fp,"fn":fn
    }


def run(labeled,config_path,out_dir):
    df,config=load_public_source(labeled,config_path)
    y=df.label.isin(POSITIVE).to_numpy(dtype=int)
    raw=df.score.to_numpy(dtype=float)
    score_only,audit1=fit_frozen_folds(df,config,enhanced=False)
    plus,audit2=fit_frozen_folds(df,config,enhanced=True)
    original_metrics=metric(y,raw)
    base_metrics=metric(y,score_only)
    added_metrics=metric(y,plus)
    d=float(added_metrics["average_precision"]-base_metrics["average_precision"])
    uncertainty=host_bootstrap_delta_ap(
        df.target_id.to_numpy(),y,score_only,plus,
        n_rep=config["confidence_interval"]["repetitions"],
        seed=config["confidence_interval"]["random_seed"])
    by_fold=[]
    for i in range(10):
        w=df.fold.eq(i).to_numpy()
        by_fold.append({
            "fold":i,"n_star_hosts":int(df.loc[w,"target_id"].nunique()),
            "n_TCE_rows":int(w.sum()),
            "n_original_2025_planet_class":int(y[w].sum()),
            "raw_original_published_NASA_score_AP":float(average_precision_score(y[w],raw[w])),
            "score_only_calibrated_AP":float(average_precision_score(y[w],score_only[w])),
            "score_plus_physics_AP":float(average_precision_score(y[w],plus[w]))
        })
    report={
        "scope":"Two NEW AI-assisted logistic calibration models on original 2025 ExoMiner++ published out-of-fold scores; NOT full NASA CNN retraining or new planet discovery",
        "source_DOI":config["source_version_doi"],
        "source_MD5":config["source_original_MD5"],
        "n_original_2025_TESS_TCE_observations":len(df),
        "n_distinct_TIC_host_stars":int(df.target_id.nunique()),
        "n_KP_CP_positive_original_labels":int(y.sum()),
        "n_ruwe_missing":int(df.ruwe.isna().sum()),
        "n_CV_star_disjoint_folds":10,
        "original_unmodified_researcher_2025_ExoMinerplusplus_metrics":original_metrics,
        "NEW_score_only_calibration_metrics":base_metrics,
        "NEW_score_plus_physical_metadata_metrics":added_metrics,
        "PRIMARY_delta_AP_new_extended_minus_new_score_only":d,
        "PRIMARY_star_cluster_bootstrap":uncertainty,
        "result_is_statistically_resolved_only_if_cluster_CI_excludes_zero":bool(
            uncertainty["delta_AP_95pct_star_cluster_CI"][0]>0 or
            uncertainty["delta_AP_95pct_star_cluster_CI"][1]<0),
        "precommitted_training_design":config,
        "per_published_NASA_2025_fold":by_fold,
        "limitations":[
            "2025 NASA out-of-fold scores are supplied by researchers rather than generated by the current code.",
            "This postprocessor is trained on the historical published 2025 TESS labels, and tenfold star separation does not imply fresh mission-independent planet truth.",
            "Current 2026 operational NASA ExoMiner++ v2.4.0 uses a different model/data version; the postprocessing finding must be separately validated before applying it to that model.",
            "NASA already uses RUWE and transit geometry diagnostics; adding them to calibration is not intrinsically a new astrophysical feature.",
            "This is a frozen historical score-calibration experiment, not a newly detected exoplanet or a demonstrated increase in survey planet yield."
        ]
    }
    folder=Path(out_dir);folder.mkdir(parents=True,exist_ok=True)
    pd.DataFrame({
        "uid":df.uid,"target_id":df.target_id,"fold":df.fold,
        "historical_2025_label":df.label,"original_nasa_score_unmodified":raw,
        "NEW_score_only_calibrated_holdout":score_only,
        "NEW_score_plus_physical_metadata_holdout":plus
    }).to_csv(folder/"all_57162_original_TESS_source_aligned_model_scores.csv",index=False)
    pd.DataFrame(by_fold).to_csv(folder/"original_10fold_score_calibration_comparison.csv",index=False)
    (folder/"frozen_score_calibration_analysis.json").write_text(json.dumps(report,indent=2)+"\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import precision_recall_curve
    fig,ax=plt.subplots(figsize=(8,5))
    for s,label in ((raw,"Unmodified NASA ExoMiner++ published"),
                    (score_only,"New score-only calibration"),
                    (plus,"New calibrated score + physical metadata")):
        precision,recall,_=precision_recall_curve(y,s)
        ax.plot(recall,precision,label=f"{label} (AP {average_precision_score(y,s):.4f})")
    ax.axhline(y.mean(),ls="--",color="black",lw=1)
    ax.set(xlabel="Recall on released NASA 2025 KP/CP labels",
           ylabel="Precision on released NASA 2025 KP/CP labels",
           title="Original NASA v1 published scores and two new TIC-heldout calibrators",
           xlim=(0,1),ylim=(0,1.02))
    ax.legend(loc="lower left",fontsize=8)
    fig.tight_layout()
    fig.savefig(folder/"NASA_2025_original_score_vs_frozen_two_calibrators.png",dpi=160)
    plt.close(fig)
    print(json.dumps({
        "n_orig_TCEs":len(df),"n_TIC_hosts":df.target_id.nunique(),
        "published_NASA_AP":original_metrics["average_precision"],
        "calibrated_score_only_AP":base_metrics["average_precision"],
        "augmented_score_plus_physics_AP":added_metrics["average_precision"],
        "primary_delta_AP":d,
        "primary_host_bootstrap_CI":uncertainty["delta_AP_95pct_star_cluster_CI"],
        "statistically_resolved":report["result_is_statistically_resolved_only_if_cluster_CI_excludes_zero"],
        "scope":"Historical NASA v1 published-score postprocessing, NOT current NASA v2.4 inference"
    },indent=2),flush=True)
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--labeled",required=True)
    parser.add_argument("--protocol",default="EXOMINER_PUBLISHED_SCORE_POSTPROCESSOR_FROZEN_2026_11_08.json")
    parser.add_argument("--out",default="results/official_2025_exominer_score_postprocessor")
    args=parser.parse_args()
    run(args.labeled,args.protocol,args.out)
