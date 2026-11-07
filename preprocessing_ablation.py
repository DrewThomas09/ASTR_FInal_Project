"""Source-grounded *exploratory* Kepler gap-neighborhood preprocessing ablation.

The 2026 Robnik et al. paper studies much more sophisticated artifact models,
longer baselines and true false-alarm controls. This modest study does NOT
replicate that paper's pipeline or permit numerical cross-paper claims.

Two pipelines:
    A: normal 301-point median flattening + Astropy BLS.
    B: the SAME flattening and Astropy BLS, but exclude cadences near
       large observational gaps, using a fixed input-independent rule.
Both receive the same injected planets in real Kepler PDCSAP measurements.

Thresholds are calibrated on a proxy inverted/rolled light-curve distribution
from calibration stars only, and then frozen for heldout stars. These proxy
controls are not real survey false-alarm probabilities.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from blind_transit_benchmark import bls_peak, threshold_from_controls
from kepler_preprocessing import (
    load_raw_kepler_quarter, normalize_flux, gap_edge_mask,
    inject_before_detrending, injected_signal_retention,
    proxy_inverted_rolled_flux,
)

METHODS=("standard_bls", "gap_edge_mask_bls")


def wilson_interval(successes, total, z=1.96):
    """Descriptive binomial interval, wide for small purposive samples."""
    if total == 0:
        return None
    p=successes/total
    d=1+z*z/total
    c=(p+z*z/(2*total))/d
    h=z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/d
    return [max(0.,c-h),min(1.,c+h)]


def evaluate_peak(time,flux,mask,bounds,factor):
    """Everything but the fixed preprocessing mask is identical."""
    peak=bls_peak(time[mask],flux[mask],bounds=tuple(bounds),
                  frequency_factor=float(factor))
    return peak


def load_stars(members,report):
    result=[]
    for entry in members:
        kic=int(entry["kic"]);quarter=int(entry["quarter"])
        print(f"Reading KIC {kic} Q{quarter}",flush=True)
        try:
            t,raw,source=load_raw_kepler_quarter(kic,quarter)
            mask,info=gap_edge_mask(
                t,gap_days=float(report["preprocessing"]["gap_threshold_days"]),
                edge_days=float(report["preprocessing"]["edge_mask_days"]),
                minimum_remaining=int(report["preprocessing"]["minimum_remaining_cadences"]))
            result.append({"kic":kic,"quarter":quarter,"time":t,"raw":raw,
                           "mask":mask,"gap_info":info,"source":source})
        except Exception as e:
            result.append({"kic":kic,"quarter":quarter,
                           "error_type":type(e).__name__,
                           "error_message":str(e)[:280]})
            print("Source unavailable",kic,type(e).__name__,str(e)[:100],flush=True)
    return result


def null_rows(stars,plan,seed,name):
    rows=[]
    bounds=plan["bls"]["period_days"];factor=plan["bls"]["frequency_factor"]
    count=int(plan["null_proxy"]["per_star"])
    for star in stars:
        if "error_type" in star:
            rows.append({"split":name,"kic":star["kic"],"status":"source_error",
                         "error_type":star["error_type"]})
            continue
        t=star["time"]
        baseline=normalize_flux(star["raw"])
        rng=np.random.default_rng(np.random.SeedSequence([seed,star["kic"]]))
        for i in range(count):
            roll_seed=int(rng.integers(1,2**32-1))
            control,roll=proxy_inverted_rolled_flux(baseline,roll_seed)
            for method in METHODS:
                mask=np.ones(len(t),bool) if method==METHODS[0] else star["mask"]
                try:
                    peak=evaluate_peak(t,control,mask,bounds,factor)
                    rows.append({
                        "split":name,"kic":star["kic"],"status":"success",
                        "control_index":i,"roll_seed":roll_seed,"roll_amount":roll,
                        "method":method,"peak_score":peak["score"],
                        "peak_period_days":peak["period_days"],
                        "n_retained":int(mask.sum()),
                    })
                except Exception as e:
                    rows.append({"split":name,"kic":star["kic"],
                                 "control_index":i,"method":method,
                                 "status":"fit_error","error_type":type(e).__name__,
                                 "error_message":str(e)[:160]})
    return pd.DataFrame(rows)


def calibrate_thresholds(df,plan):
    thresholds={}
    for method in METHODS:
        scores=df.loc[(df.method==method)&(df.status=="success"),"peak_score"]
        if len(scores)<8:
            raise RuntimeError(f"Too few usable proxy calibration controls for {method}")
        limit=threshold_from_controls(scores,
            float(plan["decision"]["target_calibration_proxy_flag_fraction"]))
        thresholds[method]={"threshold":float(limit),"n_control":int(len(scores)),
                            "n_calibration_hosts":int(df.loc[
                              (df.method==method)&(df.status=="success"),"kic"].nunique())}
    return thresholds


def injection_rows(stars,plan,thresholds):
    rng=np.random.default_rng(int(plan["injections"]["seed"]))
    bounds=plan["bls"]["period_days"];factor=plan["bls"]["frequency_factor"]
    n=int(plan["injections"]["per_depth_per_star"])
    rows=[]
    for star in stars:
        if "error_type" in star:
            rows.append({"kic":star["kic"],"status":"source_error",
                         "error_type":star["error_type"],
                         "error_message":star["error_message"]})
            continue
        t=star["time"];raw=star["raw"];mask=star["mask"]
        base_clean=normalize_flux(raw)
        for depth in plan["injections"]["depths_ppm"]:
            for iteration in range(n):
                p=float(rng.uniform(*plan["injections"]["period_uniform_days"]))
                epoch=float(t.min()+rng.uniform(0,p))
                duration=float(rng.uniform(*plan["injections"]["duration_uniform_days"]))
                changed,inside=inject_before_detrending(t,raw,p,epoch,depth,duration)
                inj_clean=normalize_flux(changed)
                keep_ratio=injected_signal_retention(base_clean,inj_clean,inside,mask)
                for method in METHODS:
                    selected=np.ones(len(t),bool) if method==METHODS[0] else mask
                    key=f"{star['kic']}-{depth}-{iteration}"
                    base={"status":"success","kic":star["kic"],
                          "quarter":star["quarter"],"case":key,
                          "depth_ppm":int(depth),"draw_index":iteration,
                          "injected_period_days":p,"injected_epoch_days":epoch,
                          "duration_days":duration,
                          "method":method,
                          "n_injected_points":int(inside.sum()),
                          "n_injected_points_masked":int((inside&~selected).sum()),
                          "gap_mask_fraction":float((~mask).mean()),
                          "injected_differential_flux_retention":(
                              keep_ratio if method==METHODS[1] else 1.0),
                          "n_observed_points":int(len(t)),
                          "n_method_points":int(selected.sum())}
                    try:
                        peak=evaluate_peak(t,inj_clean,selected,bounds,factor)
                        flagged=peak["score"]>thresholds[method]["threshold"]
                        period_error=float(abs(peak["period_days"]-p)/p)
                        exact=bool(period_error<float(
                            plan["bls"]["orbital_period_tolerance_fraction"]))
                        rows.append({**base,"fitted_period_days":peak["period_days"],
                                     "period_error_fraction":period_error,
                                     "period_correct":exact,"peak_score":peak["score"],
                                     "flagged":bool(flagged),
                                     "recovered":bool(flagged and exact)})
                    except Exception as e:
                        rows.append({**base,"status":"fit_error",
                                     "error_type":type(e).__name__,
                                     "error_message":str(e)[:150],
                                     "flagged":False,"recovered":False})
    return pd.DataFrame(rows)


def summaries(injections,null_test,plan,thresholds,sources):
    result={"scope":"EXPLORATORY small experiment, NOT Robnik 2026 reproduction",
      "dataset":"Genuine NASA Kepler PDCSAP Q2/Q8 photometry with artificial box transits injected BEFORE median detrending",
      "source_stars":sources,
      "frozen_manifest":"PREPROCESSING_ABLATION_FROZEN.json",
      "thresholds":thresholds,
      "proxy_null_warning":plan["null_proxy"]["warning"],
      "recovery":"Flagged by method-specific calibration threshold AND period within 2% of injected period; no phase criterion",
      "limitations":[
        "Small purposively selected, nonrandom sample of stars",
        "Inverted and rolled real photometry is a proxy null, not true per-star survey FAP",
        "Source stars can already contain real planetary or stellar periodic signals",
        "No NASA pipeline pixel-level injection; no controlled false-positive astrophysical labels",
        "Mask changes number of available measurements and can remove real transits",
        "Short periods in one quarter; results do not generalize to long-period Earth analogs",
        "Raw photometry comes from pipeline PDCSAP, not untouched spacecraft pixels",
        "A BLS score and even a correct injected period do NOT establish an independently confirmed new planet"],
      "recovery_by_depth":[],
      "null_flags_by_method":[],
      "paired_outcomes":{}}
    good=injections[injections.status=="success"]
    for (method,depth),subset in good.groupby(["method","depth_ppm"]):
        n=len(subset);k=int(subset.recovered.sum())
        result["recovery_by_depth"].append({
          "method":method,"depth_ppm":int(depth),"n":int(n),
          "recovered":k,"recovery_fraction":k/n,
          "wilson_95_descriptive":wilson_interval(k,n),
          "mean_fraction_added_flux_retained":float(subset["injected_differential_flux_retention"].mean()),
          "n_injected_observations_masked":int(subset["n_injected_points_masked"].sum())})
    nulls=null_test[null_test.status=="success"].copy()
    for method,subset in nulls.groupby("method"):
        n=len(subset);k=int((subset.peak_score>thresholds[method]["threshold"]).sum())
        result["null_flags_by_method"].append({
          "method":method,"n_proxy":int(n),"flagged":k,
          "flag_fraction_proxy_ONLY":k/n,
          "wilson_95_descriptive":wilson_interval(k,n)})
    paired=good.pivot(index="case",columns="method",values="recovered")
    if all(m in paired.columns for m in METHODS):
        paired=paired.dropna(subset=list(METHODS))
        a=paired[METHODS[0]].astype(bool)
        b=paired[METHODS[1]].astype(bool)
        result["paired_outcomes"]={
          "n_paired":int(len(paired)),
          "both_recovered":int((a&b).sum()),
          "baseline_only":int((a&~b).sum()),
          "gap_mask_only":int((~a&b).sum()),
          "neither":int((~a&~b).sum())}
    return result


def figures(injections,report,out):
    rows=report["recovery_by_depth"]
    if not rows:
        return
    depths=sorted(set(r["depth_ppm"] for r in rows))
    fig,ax=plt.subplots(figsize=(8,4))
    x=np.arange(len(depths))
    for j,method in enumerate(METHODS):
        vals=[next((r["recovery_fraction"] for r in rows
                    if r["method"]==method and r["depth_ppm"]==dep),np.nan)
              for dep in depths]
        ax.bar(x+(j-.5)*.36, vals,width=.35,label=method.replace("_"," "))
    ax.set_xticks(x,[f"{n} ppm" for n in depths])
    ax.set(ylim=(0,1.05),xlabel="Known injected transit depth",
           ylabel="Correct-period AND threshold-passing fraction",
           title="Real Kepler noise: exploratory paired BLS ablation")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out/"recovery_comparison.png",dpi=160)
    plt.close(fig)


def run(manifest="PREPROCESSING_ABLATION_FROZEN.json",
        output="results/preprocessing_ablation"):
    plan=json.loads(Path(manifest).read_text())
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    if (len(plan["calibration_stars"])!=2 or len(plan["heldout_stars"])!=2
            or plan["bls"]["period_days"]!=[1.5,12]):
        raise ValueError("Frozen design changed unexpectedly")
    ids=[v["kic"] for v in plan["calibration_stars"]+plan["heldout_stars"]]
    if len(set(ids))!=4:
        raise ValueError("Calibration and test stars must be disjoint")
    (out/"manifest_snapshot.json").write_bytes(Path(manifest).read_bytes())
    calibration=load_stars(plan["calibration_stars"],plan)
    heldout=load_stars(plan["heldout_stars"],plan)
    source_rows=[]
    for split,stars in [("calibration",calibration),("heldout",heldout)]:
        for star in stars:
            source_rows.append({
                "split":split,"kic":star["kic"],"quarter":star["quarter"],
                "status":"source_error" if "error_type" in star else "analyzed",
                "sha256":None if "error_type" in star else star["source"]["sha256"],
                "file":None if "error_type" in star else star["source"]["file"],
                "n":None if "error_type" in star else len(star["time"]),
                "n_gaps":None if "error_type" in star else star["gap_info"]["n_long_gaps"],
                "n_masked":None if "error_type" in star else star["gap_info"]["n_masked"],
                "error_type":star.get("error_type")})
    pd.DataFrame(source_rows).to_csv(out/"source_accountability.csv",index=False)
    cal=null_rows(calibration,plan,int(plan["null_proxy"]["calibration_seed"]),"calibration")
    cal.to_csv(out/"calibration_proxy_nulls.csv",index=False)
    thresholds=calibrate_thresholds(cal,plan)
    (out/"frozen_thresholds.json").write_text(json.dumps(thresholds,indent=2))
    print("Frozen proxy calibration thresholds:",thresholds,flush=True)
    testnull=null_rows(heldout,plan,int(plan["null_proxy"]["holdout_seed"]),"heldout")
    testnull.to_csv(out/"heldout_proxy_nulls.csv",index=False)
    testinj=injection_rows(heldout,plan,thresholds)
    testinj.to_csv(out/"heldout_injection_cases.csv",index=False)
    report=summaries(testinj,testnull,plan,thresholds,source_rows)
    (out/"results_and_limits.json").write_text(json.dumps(report,indent=2))
    figures(testinj,report,out)
    print(json.dumps(report,indent=2),flush=True)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",default="PREPROCESSING_ABLATION_FROZEN.json")
    p.add_argument("--out",default="results/preprocessing_ablation")
    args=p.parse_args()
    run(args.manifest,args.out)
