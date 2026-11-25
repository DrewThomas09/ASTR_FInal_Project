#!/usr/bin/env python3
"""Multi-quarter timing refinement of one known planet. Frozen Nov 25 protocol.
No reference period in BLS fitting; Q12/Q13 were previously examined;
Q14-Q17 are later observations not previously reported in this study.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from real_kepler_lightcurve import fetch_kepler_quarter
from blind_transit_benchmark import bls_peak
from q6_to_q7_blind_ephemeris_validation import phase_shift_null
from nov18_kepler69b_q8_to_q9 import predicted_count_between

ROOT=Path(__file__).resolve().parent
PROTOCOL=ROOT/"NOV25_MULTIQ_EPHEMERIS_PROTOCOL.json"
OUT=ROOT/"results/nov25_multiq_ephemeris"
KIC=8692861

def main():
    cfg=json.loads(PROTOCOL.read_text())
    assert cfg["kic"]==KIC and cfg["training"]["baseline"]==[8] and cfg["training"]["refined"]==[8,9,10]
    assert cfg["development_evaluation"]==[12,13] and cfg["new_later_evaluation"]==[14,15,16,17]
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/PROTOCOL.name).write_bytes(PROTOCOL.read_bytes())
    sources=[]; train={}
    for q in cfg["training"]["refined"]:
        t,f,info=fetch_kepler_quarter(f"KIC {KIC}",q)
        train[q]=(t,f); sources.append({"split":"training",**info})
    def fit(qs):
        t=np.concatenate([train[q][0] for q in qs]); f=np.concatenate([train[q][1] for q in qs])
        order=np.argsort(t); t,f=t[order],f[order]
        assert np.all(np.diff(t)>0)
        return {"quarters":qs,"n_cadences":len(t),"baseline_days":float(t.max()-t.min()),
                **bls_peak(t,f,bounds=(1.5,20.),frequency_factor=5.)}
    models={"Q8-only":fit([8]),"Q8-Q10":fit([8,9,10])}
    # Persist before opening any evaluation light curve.
    (OUT/"frozen_fits.json").write_text(json.dumps(models,indent=2)+"\n")
    print("FROZEN MODELS "+json.dumps(models),flush=True)
    if abs(models["Q8-only"]["period_days"]-13.7133429855)>.02:
        raise RuntimeError("Original Q8 baseline failed reproducibility check.")
    settings={"baseline_inner_window_duration_multipliers":1.5,
              "baseline_outer_window_duration_multipliers":3.5,
              "min_in_transit_cadences_per_event":3,
              "min_baseline_cadences_per_event":6,
              "min_expected_transit_events_in_Q7":2,
              "phase_null_random_seed":2026110817,
              "phase_null_shift_count":1000,
              "positive_event_depth_fraction_at_least":.6}
    common_duration=models["Q8-only"]["duration_days"]
    rows=[]; events_all=[]; nulls_all=[]
    for q in cfg["development_evaluation"]+cfg["new_later_evaluation"]:
        split="previously_examined" if q in cfg["development_evaluation"] else "new_later_quarter"
        try:
            t,f,info=fetch_kepler_quarter(f"KIC {KIC}",q)
            sources.append({"split":split,**info})
        except Exception as exc:
            for name in models:
                for mode in ("common_q8_duration","native_fit_duration"):
                    rows.append(dict(quarter=q,split=split,model=name,window_mode=mode,status="unavailable",error=f"{type(exc).__name__}: {str(exc)}"))
            print("UNAVAILABLE Q"+str(q)+": "+str(exc),flush=True)
            continue
        for name,m in models.items():
            cached={}
            for mode,d in (("common_q8_duration",common_duration),("native_fit_duration",m["duration_days"])):
                if d not in cached:
                    cached[d]=phase_shift_null(t,f,m["period_days"],m["transit_time_days"],d,settings,KIC+100000*q)
                measures,events,nulls=cached[d]
                row=dict(quarter=q,split=split,model=name,window_mode=mode,status="analyzed",
                         original_file=info["file"],source_sha256=info["sha256"],
                         n_cadences=len(t),period_days=m["period_days"],epoch_bkjd=m["transit_time_days"],
                         duration_days=d,centers=predicted_count_between(t.min(),t.max(),m["transit_time_days"],m["period_days"]),
                         usable_windows=len(events),positive_windows=sum(int(e["positive_local_depth"]) for e in events),
                         mean_depth_ppm=measures["mean_predicted_event_depth"]*1e6 if events else None,
                         phase_fraction=measures["relative_phase_shift_fraction"],
                         phase_trials=measures["phase_shift_null_trials"],pass_rule=measures["predictive_evidence"])
                rows.append(row)
                events_all.extend(dict(quarter=q,model=name,window_mode=mode,**e) for e in events)
                nulls_all.extend(dict(quarter=q,model=name,window_mode=mode,**n) for n in nulls)
                print("RESULT "+json.dumps(row),flush=True)
    df=pd.DataFrame(rows)
    df.to_csv(OUT/"quarter_comparison.csv",index=False)
    pd.DataFrame(events_all).to_csv(OUT/"event_windows.csv",index=False)
    pd.DataFrame(nulls_all).to_csv(OUT/"phase_controls.csv",index=False)
    (OUT/"source_manifest.json").write_text(json.dumps(sources,indent=2)+"\n")
    # NASA's published value enters only here as a descriptive comparator.
    published=13.7223682
    references={name:{"relative_period_error_pct":100*abs(m["period_days"]-published)/published,
        "signed_drift_minutes_per_orbit":1440*(m["period_days"]-published)} for name,m in models.items()}
    primary=df[df.window_mode.eq("common_q8_duration") & df.status.eq("analyzed")].copy()
    totals={}
    for split in ("previously_examined","new_later_quarter"):
        totals[split]={}
        for name in models:
            g=primary[primary.split.eq(split)&primary.model.eq(name)]
            totals[split][name]={"analyzed_quarters":int(len(g)),"positive_windows":int(g.positive_windows.sum()) if len(g) else 0,
                                "usable_windows":int(g.usable_windows.sum()) if len(g) else 0,
                                "passing_quarters":int(g.pass_rule.sum()) if len(g) else 0}
    report={"scope":"Single known planet; exploratory method refinement; new later quarters not used in either fit",
            "fits":models,"NASA_reference_period_days":published,"postfit_comparison":references,
            "primary_common_duration_totals":totals,"all_results":rows,
            "limitations":["Previously observed Q12/Q13 are development comparisons, not new holdout",
                "More training observations than Q8 baseline; longer time span rather than novel detection algorithm",
                "Positive window depths are not independently confirmed transits or an estimate of survey completeness",
                "Internal phase comparison is not a mission-wide false-alarm probability"]}
    (OUT/"summary.json").write_text(json.dumps(report,indent=2)+"\n")
    if len(primary):
        fig,ax=plt.subplots(figsize=(9,4.6),layout="constrained")
        for name,color in [("Q8-only","#777777"),("Q8-Q10","#800000")]:
            g=primary[primary.model.eq(name)]
            ax.plot(g.quarter,g.mean_depth_ppm,"o-",label=name,color=color)
        ax.axhline(0,color="#777777",lw=.8)
        ax.axvline(13.5,color="#888888",ls="--",lw=1)
        ax.set(xlabel="Evaluation quarter (Q12–13 previously examined)",ylabel="Mean fixed-window dip (ppm)",xticks=[12,13,14,15,16,17])
        ax.legend(frameon=False);ax.set_title("Kepler-69 b: one quarter vs three quarters of timing data")
        fig.savefig(OUT/"multiq_timing_comparison.png",dpi=180);plt.close(fig)
    print("MULTIQ_SUMMARY_START",flush=True)
    print(json.dumps(report,indent=2),flush=True)
    print("MULTIQ_SUMMARY_END",flush=True)

if __name__=="__main__": main()
