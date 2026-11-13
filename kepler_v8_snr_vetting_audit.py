"""Reproduce SNR-vetting audit from archived Kepler DR25 held-out predictions.
Usage: python kepler_v8_snr_vetting_audit.py <primary_heldout_paired_predictions.csv> --out outdir
"""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss

SHA="3682e0be30506ddcfe4bbb0c683ed6884454c5e5fbf8d946922fb48248712663"

def run(path, out):
    path=Path(path);out=Path(out);out.mkdir(exist_ok=True,parents=True)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==SHA
    d=pd.read_csv(path)
    assert len(d)==1619 and d.kepid.nunique()==1385
    y=d.historical_nasa_candidate_label.to_numpy(dtype=int)
    assert y.sum()==851
    snr=d.koi_model_snr.to_numpy(dtype=float)
    edges=[0,10,30,100,float("inf")]
    names=["under 10","10 to under 30","30 to under 100","100 or above"]
    mask=[np.isfinite(snr)&(snr>=edges[j])&(snr<edges[j+1]) for j in range(4)]
    rf=d.score_random_forest.to_numpy(dtype=float)
    lg=d.score_logistic_4feature.to_numpy(dtype=float)
    groups=[v.index.to_numpy() for _,v in d.groupby("kepid",sort=True)]
    rnd=np.random.default_rng(2026111308)
    draws=np.zeros((2000,4))
    delta=[]
    for i in range(2000):
        ix=np.concatenate([groups[int(k)] for k in rnd.integers(0,len(groups),size=len(groups))])
        for j,band in enumerate(mask):
            eligible=band[ix]
            draws[i,j]=y[ix][eligible].mean()
        delta.append(brier_score_loss(y[ix],lg[ix])-brier_score_loss(y[ix],rf[ix]))
    rows=[]
    for j,(name,m) in enumerate(zip(names,mask)):
        sub=d.loc[m];n=len(sub);c=int(sub.historical_nasa_candidate_label.sum())
        rows.append({"band":name,"signals":n,"candidate_labels":c,"false_positive_labels":n-c,
                     "candidate_share":c/n,"median_depth_ppm":float(sub.koi_depth.median()),
                     "star_bootstrap95":np.quantile(draws[:,j],[.025,.975]).tolist()})
    assert [(v["signals"],v["candidate_labels"]) for v in rows]==[(154,80),(702,464),(361,227),(391,79)]
    result={"original_csv_sha256":SHA,"n_signals":1619,"n_hosts":1385,"missing_snr":11,
      "bands":rows,"moderate_minus_high":rows[1]["candidate_share"]-rows[3]["candidate_share"],
      "moderate_minus_high95":np.quantile(draws[:,1]-draws[:,3],[.025,.975]).tolist(),
      "brier_forest":brier_score_loss(y,rf),"brier_logistic":brier_score_loss(y,lg),
      "brier_difference95":np.quantile(delta,[.025,.975]).tolist(),
      "scope":"Historical NASA KOI screening labels, not independently confirmed planets."}
    (out/"results.json").write_text(json.dumps(result,indent=2)+"\n")
    pd.DataFrame(rows).to_csv(out/"snr_bins.csv",index=False)
    print(json.dumps(result,indent=2))
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("csv");a.add_argument("--out",default="results/v8")
    p=a.parse_args();run(p.csv,p.out)
