#!/usr/bin/env python3
"""Fixed 13-source replication of longer-baseline Kepler timing; original NASA FITS."""
import json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from real_kepler_lightcurve import fetch_kepler_quarter
from blind_transit_benchmark import bls_peak
from q6_to_q7_blind_ephemeris_validation import phase_shift_null
from real_external_cohort import period_status
from nov18_kepler69b_q8_to_q9 import predicted_count_between

ROOT=Path(__file__).resolve().parent
PROTOCOL=ROOT/"NOV25_MULTIQ_COHORT_PROTOCOL.json"
OUT=ROOT/"results/nov25_multiq_cohort"
MODELS=("Q8-only","Q8-Q10")
QUARTERS=(14,15,16,17)
SETTINGS={"baseline_inner_window_duration_multipliers":1.5,
          "baseline_outer_window_duration_multipliers":3.5,
          "min_in_transit_cadences_per_event":3,
          "min_baseline_cadences_per_event":6,
          "min_expected_transit_events_in_Q7":2,
          "phase_null_random_seed":2026110817,
          "phase_null_shift_count":1000,
          "positive_event_depth_fraction_at_least":.6}

def run_target(item):
    kic=int(item["kic"]); name=item["name"]; kind=item["kind"]
    common=dict(kic=kic,name=name,kind=kind,reference_period_days=float(item["period_days"]))
    sources=[]; errors=[]; train={}; fits={}; fitrows=[]; rows=[]; events_all=[]; nulls_all=[]
    def fetch(q,split):
        try:
            t,f,src=fetch_kepler_quarter(f"KIC {kic}",q)
            sources.append(dict(kic=kic,name=name,split=split,**{k:v for k,v in src.items() if k not in ("kic","name")}))
            return t,f,src
        except Exception as e:
            errors.append(dict(**common,quarter=q,split=split,error=f"{type(e).__name__}: {e}"))
            return None
    for q in (8,9,10):
        data=fetch(q,"training")
        if data is not None: train[q]=data
    for model,qs in zip(MODELS,([8],[8,9,10])):
        missing=[q for q in qs if q not in train]
        row=dict(**common,model=model,training_quarters=qs,status="unavailable")
        if missing:
            row["error"]="Missing training quarters "+str(missing)
        else:
            try:
                t=np.concatenate([train[q][0] for q in qs]); f=np.concatenate([train[q][1] for q in qs])
                ix=np.argsort(t); t,f=t[ix],f[ix]
                assert np.all(np.diff(t)>0)
                m=bls_peak(t,f,bounds=(.9,15.),frequency_factor=5.)
                fits[model]=m
                row.update(status="fitted",n_cadences=len(t),baseline_days=float(t[-1]-t[0]),**m)
            except Exception as e: row["error"]=f"{type(e).__name__}: {e}"
        fitrows.append(row)
    # Both fits frozen before reading evaluation flux or comparing to known periods.
    (OUT/f"frozen_fits_{kic}.json").write_text(json.dumps(fitrows,indent=2)+"\n")
    for r in fitrows:
        if r["status"]=="fitted":
            rel,_=period_status(r["period_days"],common["reference_period_days"])
            r.update(period_relation=rel,relative_reference_error_pct=100*abs(r["period_days"]/common["reference_period_days"]-1))
        print("COHORT_FIT "+json.dumps(r),flush=True)
    duration=fits.get("Q8-only",{}).get("duration_days")
    for q in QUARTERS:
        test=fetch(q,"evaluation")
        for model in MODELS:
            row=dict(**common,quarter=q,model=model,status="unavailable",
                     named_period_match=None,pass_rule=None,named_period_and_pass=None)
            if model not in fits or duration is None: row["error"]="Missing fitted model or common Q8 duration"
            elif test is None: row["error"]="Missing evaluation observation"
            else:
                t,f,src=test; m=fits[model]
                try:
                    measures,events,nulls=phase_shift_null(t,f,m["period_days"],m["transit_time_days"],duration,SETTINGS,kic+100000*q)
                    relation,_=period_status(m["period_days"],common["reference_period_days"])
                    passed=bool(measures["predictive_evidence"])
                    row.update(status="analyzed",period_days=m["period_days"],period_relation=relation,
                               named_period_match=relation=="exact",pass_rule=passed,named_period_and_pass=passed and relation=="exact",
                               window_duration_days=duration,original_file=src["file"],source_sha256=src["sha256"],
                               n_cadences=len(t),centers=predicted_count_between(t.min(),t.max(),m["transit_time_days"],m["period_days"]),
                               usable_windows=len(events),positive_windows=sum(int(e["positive_local_depth"]) for e in events),
                               mean_depth_ppm=measures["mean_predicted_event_depth"]*1e6 if events else None,
                               phase_fraction=measures["relative_phase_shift_fraction"],phase_trials=measures["phase_shift_null_trials"])
                    events_all.extend(dict(kic=kic,quarter=q,model=model,**e) for e in events)
                    nulls_all.extend(dict(kic=kic,quarter=q,model=model,**n) for n in nulls)
                except Exception as e: row["error"]=f"{type(e).__name__}: {e}"
            rows.append(row); print("COHORT_ROW "+json.dumps(row),flush=True)
    # Store target outputs even if another worker fails.
    target_dir=OUT/"individual"; target_dir.mkdir(exist_ok=True)
    (target_dir/f"{kic}.json").write_text(json.dumps({"fits":fitrows,"rows":rows,"sources":sources,"errors":errors},indent=2)+"\n")
    return fitrows,rows,sources,errors,events_all,nulls_all

def summarize(fits,rows):
    report={}
    for kind in ("planet","binary"):
        group=[r for r in rows if r["kind"]==kind]; fitgroup=[r for r in fits if r["kind"]==kind]
        pairs=[]
        for kic in sorted(set(r["kic"] for r in group)):
            for q in QUARTERS:
                pair=[r for r in group if r["kic"]==kic and r["quarter"]==q]
                if len(pair)==2 and all(r["status"]=="analyzed" for r in pair):
                    pairs.append(tuple(next(r for r in pair if r["model"]==m) for m in MODELS))
        def compare(key):
            return {"baseline_pass":sum(int(a[key]) for a,b in pairs),"refined_pass":sum(int(b[key]) for a,b in pairs),
                    "improved":sum(int(not a[key] and b[key]) for a,b in pairs),"worsened":sum(int(a[key] and not b[key]) for a,b in pairs),
                    "both":sum(int(a[key] and b[key]) for a,b in pairs),"neither":sum(int(not a[key] and not b[key]) for a,b in pairs)}
        target_rows=[]
        for kic in sorted(set(r["kic"] for r in group)):
            ps=[(a,b) for a,b in pairs if a["kic"]==kic]
            ft=[r for r in fitgroup if r["kic"]==kic]
            a,b=(next(r for r in ft if r["model"]==m) for m in MODELS)
            target_rows.append({"kic":kic,"name":a["name"],"paired_quarters":len(ps),
                "baseline_relation":a.get("period_relation","unavailable"),"refined_relation":b.get("period_relation","unavailable"),
                "baseline_reference_error_pct":a.get("relative_reference_error_pct"),"refined_reference_error_pct":b.get("relative_reference_error_pct"),
                "baseline_phase_pass":sum(int(x["pass_rule"]) for x,y in ps),"refined_phase_pass":sum(int(y["pass_rule"]) for x,y in ps),
                "baseline_named_pass":sum(int(x["named_period_and_pass"]) for x,y in ps),"refined_named_pass":sum(int(y["named_period_and_pass"]) for x,y in ps)})
        exact_both=[r for r in target_rows if r["baseline_relation"]==r["refined_relation"]=="exact"]
        endpoint="named_period_and_pass" if kind=="planet" else "pass_rule"
        hk="named_pass" if kind=="planet" else "phase_pass"
        report[kind]={"planned_targets":len(target_rows),"planned_target_quarters":len(target_rows)*len(QUARTERS),
                      "paired_analyzed_quarters":len(pairs),"phase_only":compare("pass_rule"),
                      "named_period_and_phase":compare("named_period_and_pass"),
                      "host_level_primary":{"paired_hosts":sum(int(r["paired_quarters"]>0) for r in target_rows),
                           "improved":sum(int(r["refined_"+hk]>r["baseline_"+hk]) for r in target_rows),
                           "worsened":sum(int(r["refined_"+hk]<r["baseline_"+hk]) for r in target_rows),
                           "equal_with_paired_data":sum(int(r["paired_quarters"]>0 and r["refined_"+hk]==r["baseline_"+hk]) for r in target_rows)},
                      "both_exact_period_hosts":len(exact_both),
                      "reduced_period_error_among_both_exact":sum(int(r["refined_reference_error_pct"]<r["baseline_reference_error_pct"]) for r in exact_both),
                      "targets":target_rows}
    return report

def main():
    cfg=json.loads(PROTOCOL.read_text()); old=json.loads((ROOT/"real_external_cohort_frozen.json").read_text())
    assert cfg["targets"]==old["targets"] and len(cfg["targets"])==13
    assert cfg["training"]["period_bounds_days"]==[.9,15] and cfg["evaluation"]["quarters"]==list(QUARTERS)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/PROTOCOL.name).write_bytes(PROTOCOL.read_bytes())
    with ProcessPoolExecutor(max_workers=4) as pool: results=list(pool.map(run_target,cfg["targets"]))
    fits,rows,sources,errors,events,nulls=([r for result in results for r in result[i]] for i in range(6))
    assert len(fits)==26 and len(rows)==104 and len({(r["kic"],r["quarter"],r["model"]) for r in rows})==104
    for name,data in (("fits",fits),("quarter_results",rows),("event_windows",events),("phase_controls",nulls),("source_manifest",sources),("errors",errors)):
        pd.DataFrame(data).to_csv(OUT/f"{name}.csv",index=False)
    report=summarize(fits,rows)
    (OUT/"summary.json").write_text(json.dumps(report,indent=2)+"\n")
    targets=[r for k in ("planet","binary") for r in report[k]["targets"]]
    x=np.arange(len(targets)); base=[r["baseline_named_pass"] if i<6 else r["baseline_phase_pass"] for i,r in enumerate(targets)]
    ref=[r["refined_named_pass"] if i<6 else r["refined_phase_pass"] for i,r in enumerate(targets)]
    fig,ax=plt.subplots(figsize=(12,5),layout="constrained")
    ax.bar(x-.18,base,.36,label="Q8 only",color="#888888"); ax.bar(x+.18,ref,.36,label="Q8–Q10",color="#800000")
    for i,r in enumerate(targets):
        if r["paired_quarters"]<4: ax.text(i,.1,f'{r["paired_quarters"]}/4 available',rotation=90,ha="center",va="bottom",fontsize=8)
    ax.axvline(5.5,color="black",ls=":",lw=1);ax.set_xticks(x,[r["name"] for r in targets],rotation=45,ha="right")
    ax.set(ylim=(0,4.4),ylabel="Passing later quarters (of four planned)",yticks=range(5))
    ax.set_title("Planet hosts: named period + phase evidence | Binary controls: phase evidence only",fontsize=12)
    ax.legend(frameon=False);fig.savefig(OUT/"cohort_forecast_comparison.png",dpi=180);plt.close(fig)
    print("COHORT_SUMMARY "+json.dumps(report),flush=True)

if __name__=="__main__": main()
