"""ASTR 12600: exploratory DR25 feature-ablation audit.

Compares subsets of the four original NASA precomputed KOI features on the
SAME frozen host-disjoint split and original NASA catalog as the main experiment.
Variant definitions and outcome metrics are documented before running this file.
This is a retrospective method check of a previously explored split, NOT fresh
confirmatory data, end-to-end detection accuracy or confirmed exoplanets.
"""
import argparse, hashlib, json, pathlib
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, confusion_matrix, balanced_accuracy_score
from ml_screening import load_data,split_by_star,cutoff

SHA="c907e064c7369d4b073ba422283ddfbbf7499d472ec3cc0787254f3407e5e045"
FEATURES=["koi_period","koi_duration","koi_depth","koi_model_snr"]
VARIANTS={
 "All four":FEATURES,
 "Without period":["koi_duration","koi_depth","koi_model_snr"],
 "Without duration":["koi_period","koi_depth","koi_model_snr"],
 "Without depth":["koi_period","koi_duration","koi_model_snr"],
 "Without SNR":["koi_period","koi_duration","koi_depth"],
 "Period and duration":["koi_period","koi_duration"],
 "Depth only":["koi_depth"],
 "SNR only":["koi_model_snr"],
}
def evaluate(csv,out):
    source=pathlib.Path(csv)
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if digest!=SHA: raise RuntimeError("NASA source SHA changed: "+digest)
    df=load_data(source,download=False)
    assert len(df)==8054 and df.kepid.nunique()==6923
    train,valid,test=split_by_star(df,12600)
    assert [len(train),len(valid),len(test)]==[4824,1611,1619]
    y=df.label.to_numpy()
    x=np.log1p(df[FEATURES].clip(lower=0).astype(float))
    rows=[];outputs=[]
    for name,cols in VARIANTS.items():
        model=make_pipeline(SimpleImputer(strategy="median"),RandomForestClassifier(
            n_estimators=120,max_depth=9,min_samples_leaf=3,random_state=12600,n_jobs=-1))
        model.fit(x.iloc[train][cols],y[train])
        validation=model.predict_proba(x.iloc[valid][cols])[:,1]
        testscore=model.predict_proba(x.iloc[test][cols])[:,1]
        threshold=cutoff(validation,y[valid],desired=.90)
        pred=testscore>=threshold
        tn,fp,fn,tp=confusion_matrix(y[test],pred,labels=[0,1]).ravel()
        rows.append({
            "feature_set":name,"features":"; ".join(cols),
            "n_features":len(cols),"test":len(test),
            "test_host_stars":int(df.iloc[test].kepid.nunique()),
            "accuracy":float((pred==y[test]).mean()),
            "balanced_accuracy":float(balanced_accuracy_score(y[test],pred)),
            "candidate_recall":float(tp/(tp+fn)),
            "false_positive_rate":float(fp/(fp+tn)),
            "ROC_AUC":float(roc_auc_score(y[test],testscore)),
            "historical_candidates_retained":int(tp),
            "historical_candidates_rejected":int(fn),
            "historical_false_positives_accepted":int(fp),
            "historical_false_positives_rejected":int(tn),
            "validation_selected_threshold":float(threshold)
        })
        outputs.append(pd.DataFrame({"kepid":df.iloc[test].kepid.to_numpy(),
          "label":y[test],"feature_set":name,"score":testscore,"prediction":pred.astype(int)}))
        print(name,rows[-1]["balanced_accuracy"],rows[-1]["ROC_AUC"],flush=True)
    out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
    data=pd.DataFrame(rows)
    data.to_csv(out/"feature_ablation_metrics.csv",index=False)
    pd.concat(outputs,ignore_index=True).to_csv(out/"feature_ablation_predictions.csv",index=False)
    # Conditional host-bootstrap contrast: full vs no-depth, not re-tuned or independent.
    full=outputs[0];less=outputs[3]; yy=full.label.to_numpy(dtype=int)
    a=full.prediction.to_numpy(dtype=int);b=less.prediction.to_numpy(dtype=int)
    hostids=full.kepid.to_numpy();groups=[np.flatnonzero(hostids==h) for h in np.unique(hostids)]
    rng=np.random.default_rng(20261115)
    boot=[]
    for i in range(1200):
        ids=np.concatenate([groups[k] for k in rng.integers(len(groups),size=len(groups))])
        if len(np.unique(yy[ids]))==2:
            boot.append(balanced_accuracy_score(yy[ids],a[ids])-balanced_accuracy_score(yy[ids],b[ids]))
    summary={
      "model":"120-tree depth-9 random forest, train-median imputation",
      "source_sha256":SHA,"source_rows":len(df),
      "split_seed":12600,"star_separated":[len(train),len(valid),len(test)],
      "same_original_heldout_reused":True,
      "target_validation_candidate_recall":0.90,
      "primary_contrast":"four features minus same forest without depth, balanced accuracy",
      "primary_contrast_point":float(rows[0]["balanced_accuracy"]-rows[3]["balanced_accuracy"]),
      "primary_contrast_host_bootstrap_95":np.quantile(boot,[.025,.975]).tolist(),
      "bootstrap_seed":20261115,
      "bootstrap_reps":len(boot),
      "boundary":"retrospective feature ablation for NASA historical pipeline labels only; no new independent test or physical confirmation",
      "variants":rows
    }
    (out/"feature_ablation_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(1,2,figsize=(11,4.3),layout="constrained")
    names=data.feature_set.tolist()[::-1]
    axs[0].barh(names,100*data.balanced_accuracy.to_numpy()[::-1],color="#365771")
    axs[0].set(xlim=(0,100),xlabel="Balanced accuracy (%)",title="Historic-label accuracy balanced by class")
    axs[1].barh(names,data.ROC_AUC.to_numpy()[::-1],color="#a2674b")
    axs[1].set(xlim=(0,1),xlabel="ROC AUC",title="Ranking of previous NASA vetting labels")
    for a0 in axs:a0.spines[["top","right"]].set_visible(False)
    fig.suptitle("Kepler DR25: what changes when catalog features are omitted?")
    fig.savefig(out/"kepler_four_feature_ablation.png",dpi=210,bbox_inches="tight")
    plt.close(fig)
    print(json.dumps({"sha":digest,"rows":len(df),"contrast":summary["primary_contrast_point"]},indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--csv",default="data/kepler_dr25_source_v13.csv")
    p.add_argument("--out",default="results/feature_ablation_v13")
    args=p.parse_args();evaluate(args.csv,args.out)
