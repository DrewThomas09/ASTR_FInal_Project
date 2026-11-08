"""A reproducible supervised TESS *scalar* companion baseline.

NOT the official NASA ExoMiner++ neural network. The historical official
published ExoMiner++ out-of-fold score is an immutable comparison column.
Use NASA team's original host-separated ten folds; no TIC/epoch/label or
NASA score may enter the scikit-learn fit. The selection and hyperparameters
were frozen in TESS_SCALAR_ABLATION_FROZEN_2026_11_08.json BEFORE running this
new model on the labels.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    average_precision_score, precision_recall_curve,
    roc_auc_score, confusion_matrix, precision_score, recall_score
)


BASIC=["tce_period","tce_duration","tce_prad","tce_max_mult_ev"]
EXTRA=["transit_duty_cycle_ratio","ruwe"]


def verify_pinned_source(path, frozen):
    data=Path(path)
    digest=hashlib.md5()
    n=0
    with data.open("rb") as file:
        for piece in iter(lambda:file.read(1024*1024),b""):
            digest.update(piece);n+=len(piece)
    if digest.hexdigest()!=frozen["original_md5"] or n!=8944735:
        raise ValueError("TESS source file differs from frozen published Zenodo snapshot")
    return {"md5":digest.hexdigest(),"exact_original_bytes":n}


def make_design_matrix(df, augmented=False):
    """Physically motivated log-transformed inputs, no target leakages."""
    if not set(BASIC+["ruwe"]).issubset(df.columns):
        raise ValueError("Required labeled TCE scalar features missing")
    if (df[BASIC].isna().any().any() or
        not np.isfinite(df[BASIC].to_numpy(dtype=float)).all() or
        (df[BASIC].to_numpy(dtype=float)<=0).any()):
        raise ValueError("Base physical scalar properties must be finite and positive")
    X=np.log1p(df[BASIC].to_numpy(dtype=float))
    if augmented:
        # Dimensional ratio, not a planet-specific label or catalogue score.
        ratio=(df["tce_duration"]/df["tce_period"]).to_numpy(dtype=float)
        if not np.isfinite(ratio).all() or (ratio<=0).any():
            raise ValueError("Invalid ratio or period in data")
        ruwe=df["ruwe"].to_numpy(dtype=float)
        if (np.isinf(ruwe).any() or np.any(ruwe[np.isfinite(ruwe)]<=0)):
            raise ValueError("Invalid RUWE")
        X=np.column_stack([X,np.log1p(ratio),np.log1p(ruwe)])
    return X


def labels_and_folds(df,manifest):
    required={"uid","target_id","label","fold","score"}
    if not required.issubset(df.columns):
        raise ValueError("Source data missing identity, label, fold or published model scores")
    if len(df)!=manifest["expected_TCE_row_count"]:
        raise ValueError("Original source row count changed")
    if df.target_id.nunique()!=manifest["expected_unique_TIC_hosts"]:
        raise ValueError("Original source distinct-star count changed")
    if df.uid.duplicated().any():
        raise ValueError("The same TCE observation UID occurs more than once")
    if set(df.fold.unique())!=set(range(10)):
        raise ValueError("Official source must contain ten fixed CV folds")
    positive=set(manifest["label_positive"])
    negative=set(manifest["label_negative"])
    if set(df.label.unique())!=positive|negative or positive&negative:
        raise ValueError("Source release label meanings changed")
    if (df.groupby("target_id").fold.nunique()>1).any():
        raise ValueError("Same star appears in training and test folds")
    y=df.label.isin(positive).to_numpy(dtype=np.int8)
    return y,df.fold.to_numpy(dtype=int)


def fixed_rf_model(spec):
    p=spec["model"]
    return RandomForestClassifier(
        n_estimators=p["n_estimators"],max_depth=p["max_depth"],
        min_samples_leaf=p["min_samples_leaf"],
        class_weight=p["class_weight"],
        n_jobs=p["n_jobs"],random_state=p["random_state"])


def train_frozen_oof(df,manifest,augmented):
    """Only fit on remaining nine published host folds for each test fold."""
    y,folds=labels_and_folds(df,manifest)
    matrix=make_design_matrix(df,augmented=augmented)
    predicted=np.full(len(df),np.nan,dtype=float)
    fold_log=[]
    for fold in range(10):
        train=folds!=fold
        test=folds==fold
        if not (train.any() and test.any()):
            raise AssertionError("Empty published fold")
        # Host-star collision is explicitly forbidden.
        if set(df.target_id[train])&set(df.target_id[test]):
            raise AssertionError("Host leakage despite input verification")
        # The imputer is never fit to the test fold.
        imputer=SimpleImputer(strategy="median",keep_empty_features=True)
        xtrain=imputer.fit_transform(matrix[train])
        xtest=imputer.transform(matrix[test])
        model=fixed_rf_model(manifest)
        model.fit(xtrain,y[train])
        predicted[test]=model.predict_proba(xtest)[:,1]
        fold_log.append({
            "fold":fold,"n_train_event_rows":int(train.sum()),
            "n_train_host_stars":int(df.target_id[train].nunique()),
            "n_test_event_rows":int(test.sum()),
            "n_test_host_stars":int(df.target_id[test].nunique()),
            "positive_labels_test":int(y[test].sum()),
            "imputer_fit_only_on_train_stars":True,
            "model_features":BASIC+(EXTRA if augmented else [])
        })
    if not np.isfinite(predicted).all() or not np.all((predicted>=0)&(predicted<=1)):
        raise AssertionError("Incomplete or invalid held-out published TCE scores")
    return predicted,fold_log


def metrics_at_frozen_threshold(y,score,threshold=.5):
    predicted=np.asarray(score)>=threshold
    tn,fp,fn,tp=(int(v) for v in confusion_matrix(y,predicted,labels=[0,1]).ravel())
    return {
        "average_precision_sklearn":float(average_precision_score(y,score)),
        "ROC_AUC":float(roc_auc_score(y,score)),
        "precision_at_0_5":float(precision_score(y,predicted,zero_division=0)),
        "recall_at_0_5":float(recall_score(y,predicted,zero_division=0)),
        "tp":tp,"fp":fp,"fn":fn,"tn":tn
    }


def host_bootstrap_delta_ap(host_ids,labels,left,right,n_rep=350,seed=2026110819):
    """Recompute paired delta AP from whole-star resampling, not TCE rows.

    Results are conditional on an already published observational cohort,
    not a prospective mission-wide uncertainty interval.
    """
    h=np.asarray(host_ids)
    y=np.asarray(labels,dtype=np.int8)
    a=np.asarray(left,dtype=float)
    b=np.asarray(right,dtype=float)
    if not (len(h)==len(y)==len(a)==len(b)):
        raise ValueError("Scores and IDs must align")
    stars,inverse=np.unique(h,return_inverse=True)
    # Sort source rows once: do not rescan every star against all TCEs.
    ordered=np.argsort(inverse,kind="stable")
    cuts=np.flatnonzero(np.diff(inverse[ordered]))+1
    bins=np.split(ordered,cuts)
    if len(stars)<15:
        raise ValueError("Need at least fifteen independent host clusters")
    rng=np.random.default_rng(seed)
    diffs=[]
    for _ in range(n_rep):
        chosen=rng.integers(0,len(stars),len(stars))
        idx=np.concatenate([bins[int(i)] for i in chosen])
        if len(np.unique(y[idx]))<2:
            continue
        diffs.append(float(average_precision_score(y[idx],b[idx])-
                           average_precision_score(y[idx],a[idx])))
    if len(diffs)<.95*n_rep:
        raise ValueError("Too few valid bootstrap samples")
    lo,hi=(float(v) for v in np.quantile(diffs,[.025,.975]))
    return {"host_star_cluster_count":len(stars),
            "valid_bootstraps":len(diffs),
            "delta_AP_95pct_star_cluster_CI":[lo,hi],
            "bootstrap_seed":seed,
            "scope":"Descriptive fixed-label historical TESS CV sample; cannot validate new physical planet discoveries"}


def run(labeled_path,output_dir="results/tess_scalar_ablation",
        manifest_path="TESS_SCALAR_ABLATION_FROZEN_2026_11_08.json"):
    spec=json.loads(Path(manifest_path).read_text())
    if spec.get("study_id")!="EXOMINER2025_TESS_SCALAR_AI_ASSISTED_REPLICATION_ABLATION_20261108":
        raise ValueError("Wrong prospective protocol")
    src=verify_pinned_source(labeled_path,spec)
    df=pd.read_csv(labeled_path)
    y,folds=labels_and_folds(df,spec)
    official=df.score.to_numpy(dtype=float)
    if not np.isfinite(official).all() or not np.all((official>=0)&(official<=1)):
        raise ValueError("Published official scores missing or invalid")
    baseline,b_log=train_frozen_oof(df,spec,augmented=False)
    augmented,a_log=train_frozen_oof(df,spec,augmented=True)
    b=metrics_at_frozen_threshold(y,baseline)
    a=metrics_at_frozen_threshold(y,augmented)
    n=metrics_at_frozen_threshold(y,official)
    primary_delta=float(a["average_precision_sklearn"]-b["average_precision_sklearn"])
    uncertainty=host_bootstrap_delta_ap(df.target_id,y,baseline,augmented,
                                        n_rep=350,seed=2026110819)
    per_fold=[]
    for k in range(10):
        where=folds==k
        per_fold.append({
            "fold":k,"test_TCE_rows":int(where.sum()),
            "test_unique_TIC_stars":int(df.target_id[where].nunique()),
            "positive_KP_CP":int(y[where].sum()),
            "RF4_AP":float(average_precision_score(y[where],baseline[where])),
            "RF4_plus_duty_RUWE_AP":float(average_precision_score(y[where],augmented[where])),
            "released_ExoMinerplusplus_AP":float(average_precision_score(y[where],official[where]))
        })
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame({
        "uid":df.uid,"target_id":df.target_id,"fold":folds,
        "original_published_class_label":df.label,"target_KP_or_CP":y,
        "RF4_new_10fold_star_OOF_score":baseline,
        "RF4_plus_duty_RUWE_new_10fold_star_OOF_score":augmented,
        "NASA_released_ExoMinerplusplus_10fold_score":official
    }).to_csv(out/"source_aligned_tess_10fold_OOF_predictions.csv",index=False)
    pd.DataFrame(per_fold).to_csv(out/"by_frozen_original_NASA_host_fold.csv",index=False)
    report={
        "scope":"AI-assisted new scalar random forest experiment, NOT actual ExoMiner neural network replication or official retraining",
        "source":src,
        "protocol_file":manifest_path,
        "n_original_TCE_rows":len(df),
        "n_unique_TIC_hosts":int(df.target_id.nunique()),
        "n_positive_KP_or_CP":int(y.sum()),
        "number_missing_RUWE":int(df.ruwe.isna().sum()),
        "baseline_RF4_historical_labels":b,
        "augmented_RF4_plus_duty_cycle_RUWE_historical_labels":a,
        "original_NASA_released_ExoMinerplusplus_scores_descriptive":n,
        "prespecified_primary_delta_AP_augmented_minus_baseline":primary_delta,
        "star_cluster_bootstrap_for_delta_AP":uncertainty,
        "published_host_fold_integrity":"Zero same-star train/test fold collisions",
        "by_fold":per_fold,
        "important_limitations":[
            "Only the two RFs are trained here; the official published NASA model scores are provided in original CSV.",
            "Adding RUWE is not a new ExoMiner feature: current official NASA models already use Gaia astrometric metadata.",
            "The scalar RF is trained with fewer inputs and lacks real photometry, pixel difference images, stellar DV diagnostics and Kepler transfer training used by ExoMiner++.",
            "A stronger RF score on the same historical labels would be a scalar-baseline result, not a proven physical exoplanet detection gain.",
            "No hyperparameters, threshold or features were reselected after evaluating released label holdouts."
        ]
    }
    (out/"frozen_TESS_scalar_model_evaluation.json").write_text(json.dumps(report,indent=2)+"\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(7,5))
    for values,label in [
        (baseline,"AI-assisted four-feature RF"),
        (augmented,"Four-feature RF + duty cycle / Gaia RUWE"),
        (official,"Published NASA ExoMiner++ score (NOT retrained)")
    ]:
        precision,recall,_=precision_recall_curve(y,values)
        ax.plot(recall,precision,label=f"{label} (AP={average_precision_score(y,values):.3f})")
    ax.axhline(float(y.mean()),ls="--",color="black",alpha=.5)
    ax.set(title="Same released TESS labels / 10 NASA host-star folds",
           xlabel="Recall (historical KP/CP classifications)",
           ylabel="Precision (historical KP/CP classifications)",
           xlim=(0,1),ylim=(0,1.02))
    ax.legend(fontsize=8,loc="lower left")
    fig.tight_layout()
    fig.savefig(out/"matched_TESS_PRC_scalar_RF_vs_original_NASA_released_score.png",dpi=160)
    plt.close(fig)
    print(json.dumps({
        "number_stars":report["n_unique_TIC_hosts"],
        "number_TCEs":report["n_original_TCE_rows"],
        "RF4_AP":b["average_precision_sklearn"],
        "RF4_augmented_AP":a["average_precision_sklearn"],
        "official_published_AP_not_retrained":n["average_precision_sklearn"],
        "augmentation_delta_AP":primary_delta,
        "augmentation_star_cluster_CI":uncertainty["delta_AP_95pct_star_cluster_CI"],
        "limit":"ExoMiner++ weights were NOT trained or run by this script"
    },indent=2),flush=True)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--labeled",required=True)
    p.add_argument("--out",default="results/tess_scalar_ablation")
    p.add_argument("--manifest",default="TESS_SCALAR_ABLATION_FROZEN_2026_11_08.json")
    a=p.parse_args()
    run(a.labeled,a.out,a.manifest)
