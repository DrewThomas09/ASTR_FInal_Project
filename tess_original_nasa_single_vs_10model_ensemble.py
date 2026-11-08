"""Compare unchanged NASA ExoMiner v2.4.0 single and documented cv_ensemble.

Fixed eight previously studied TESS stars. Source identity uses exact TCE UID,
period and epoch alignment; no new-planet or independently trained-holdout claim.
"""
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd

def read(path,expect):
    first=Path(path).read_text().splitlines()[:32]
    header="\n".join(x for x in first if x.startswith("#"))
    for required in ("# Version Number: 2.4.0","# Task: planet-validation",
                     "# ExoMiner Model: "+expect):
        if required not in header:raise ValueError("NASA metadata mismatch "+required)
    df=pd.read_csv(path,comment="#")
    for key in ("uid","score","tce_period","tce_time0bk"):
        if key not in df: raise ValueError("NASA column missing "+key)
    if df.uid.duplicated().any():raise ValueError("Duplicate TCE UIDs")
    return df.set_index("uid")

def assess(manifest,single,ensemble,out):
    fixed=json.loads(Path(manifest).read_text())
    if fixed["experiment_id"]!="EXOMINER_V240_EIGHT_TESS_SINGLE_VS_CV_ENSEMBLE_20261108":
        raise ValueError("Wrong frozen source cohort")
    a,b=read(single,"single"),read(ensemble,"cv_ensemble")
    records=[]
    for row in fixed["sources"]:
        ident=row["UID"];r={"UID":ident,"TIC_ID":row["tic_id"],"historical_label":row["published_2025_label"],"single_found":ident in a.index,"ensemble_found":ident in b.index,"single_score":None,"ensemble_score":None,"same_period_within_1pct":None,"same_epoch_within_2hr":None,"ensemble_minus_single_score":None,"single_PC":None,"ensemble_PC":None,"decision_changed_on_same_ephemeris":None}
        if ident in a.index:
            s=a.loc[ident]
            r.update(single_score=float(s.score),single_PC=bool(s.score>=.5))
        if ident in b.index:
            t=b.loc[ident]
            r.update(ensemble_score=float(t.score),ensemble_PC=bool(t.score>=.5))
        if ident in a.index and ident in b.index:
            s,t=a.loc[ident],b.loc[ident]
            valid=bool(abs(float(t.tce_period/s.tce_period)-1)<=.01 and abs(float(t.tce_time0bk-s.tce_time0bk))<=2/24)
            r.update(same_period_within_1pct=bool(abs(float(t.tce_period/s.tce_period)-1)<=.01),
                same_epoch_within_2hr=bool(abs(float(t.tce_time0bk-s.tce_time0bk))<=2/24),
                ensemble_minus_single_score=float(t.score-s.score),
                decision_changed_on_same_ephemeris=bool((t.score>=.5)!=(s.score>=.5)) if valid else None)
        records.append(r)
    p=Path(out);p.mkdir(parents=True,exist_ok=True)
    df=pd.DataFrame(records);df.to_csv(p/"all_eight_original_NASA_single_vs_cv_ensemble_sources.csv",index=False)
    clean=df[df.decision_changed_on_same_ephemeris.notna()]
    summary={"requested_original_sources":8,"both_scores_matched":int((df.single_found&df.ensemble_found).sum()),
        "comparable_current_ephemerides":len(clean),
        "changes_in_binary_PC_decision_on_comparable_sources":int((clean.decision_changed_on_same_ephemeris==True).sum()),
        "max_absolute_model_score_change":float(df.ensemble_minus_single_score.abs().max()) if df.ensemble_minus_single_score.notna().any() else None,
        "individual_model_variance_not_exposed":"No standard deviation or 100-model ensemble confidence interval claimed without released individual member outputs.",
        "limitations":"Deliberately selected already-seen historical class/error sources; 2026 model train/exclusion unknown; ensemble is an existing NASA method and not a student classifier change."}
    (p/"same_TESS_source_single_vs_10model_ensemble_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":
    z=argparse.ArgumentParser()
    z.add_argument("--manifest",required=True);z.add_argument("--single",required=True);z.add_argument("--ensemble",required=True);z.add_argument("--out",required=True)
    x=z.parse_args();assess(x.manifest,x.single,x.ensemble,x.out)
