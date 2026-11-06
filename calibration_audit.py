"""Read-only calibration audit of held-out Kepler DR25 *vetter-label* predictions.

A score of .90 is NOT a 90% scientific probability that a planet exists.
No calibration function is fit to held-out labels by this script.
"""
from pathlib import Path
import argparse, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def calibration_bins(scores,labels,nbins=10):
    p=np.asarray(scores,dtype=float)
    y=np.asarray(labels,dtype=int)
    if p.ndim!=1 or y.ndim!=1 or len(p)!=len(y) or len(y)<2:
        raise ValueError("Expected equal-length 1D arrays")
    if not np.isfinite(p).all() or np.any((p<0)|(p>1)):
        raise ValueError("Model scores must be finite numbers in [0,1]")
    if not set(np.unique(y)).issubset({0,1}):
        raise ValueError("Labels must be binary")
    if not isinstance(nbins,int) or nbins<2:
        raise ValueError("At least two bins are required")
    edges=np.linspace(0,1,nbins+1)
    which=np.minimum(np.searchsorted(edges,p,side="right")-1,nbins-1)
    rows=[]
    for idx in range(nbins):
        mask=which==idx
        if not mask.any():
            continue
        rows.append({
           "bin_start":float(edges[idx]),
           "bin_end":float(edges[idx+1]),
           "n":int(mask.sum()),
           "mean_model_score":float(p[mask].mean()),
           "candidate_label_fraction":float(y[mask].mean()),
           "absolute_label_calibration_gap":float(abs(p[mask].mean()-y[mask].mean()))})
    table=pd.DataFrame(rows)
    brier=float(np.mean((p-y)**2))
    ece=float(np.sum(table.n*table.absolute_label_calibration_gap)/len(y))
    return table,{"n":int(len(y)),"brier_score_against_vetter_labels":brier,
                  "expected_calibration_error_against_vetter_labels":ece,
                  "bins_requested":nbins,"bins_occupied":int(len(table)),
                  "sample_candidate_prevalence":float(y.mean()),
                  "mean_model_score":float(p.mean())}


def run(predictions_csv,output="results/ml_calibration",nbins=10):
    input_file=Path(predictions_csv)
    if not input_file.is_file():
        raise FileNotFoundError(input_file)
    df=pd.read_csv(input_file)
    if not {"model_score","label"}.issubset(df.columns):
        raise ValueError("Expected columns: model_score, label")
    bins,metrics=calibration_bins(df.model_score,df.label,nbins)
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    bins.to_csv(out/"calibration_bins.csv",index=False)
    metrics.update({
      "input_holdout_predictions_file":input_file.name,
      "label_definition":"Historical NASA DR25 Robovetter CANDIDATE/ FALSE POSITIVE",
      "not_proof_of_planet":"These scores and bins assess agreement with automatic catalog labels, not independent planetary truth",
      "evaluation_protocol":"Diagnostic only: do not tune classifier or thresholds on this same holdout"})
    (out/"calibration_summary.json").write_text(json.dumps(metrics,indent=2))
    fig,ax=plt.subplots(figsize=(6.5,5))
    ax.plot([0,1],[0,1],linestyle="--",label="Perfect label calibration")
    ax.scatter(bins.mean_model_score,bins.candidate_label_fraction,
               s=np.maximum(35,bins.n.to_numpy()*2.5))
    for _,row in bins.iterrows():
        ax.annotate(str(int(row["n"])),(row["mean_model_score"],row["candidate_label_fraction"]),
                    xytext=(4,3),textcoords="offset points",fontsize=8)
    ax.set(xlim=(0,1),ylim=(0,1),
           xlabel="Mean model candidate score",
           ylabel="Observed fraction with candidate label",
           title="Held-out score calibration against NASA vetter labels")
    ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(out/"calibration_curve.png",dpi=170);plt.close(fig)
    return metrics


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--predictions",default="results/ml_triage/holdout_predictions.csv")
    parser.add_argument("--out",default="results/ml_calibration")
    args=parser.parse_args()
    print(json.dumps(run(args.predictions,args.out),indent=2))
