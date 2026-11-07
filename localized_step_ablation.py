"""Frozen follow-up: physical discontinuity masking versus previous Kepler BLS.

Three *established baseline / exploratory* approaches run on identical
source-host data and synthetic-injection truth:
- BLS with no extra masking
- BLS with old fixed gap-edge masking (previous negative control)
- BLS with local persistent-step onset screening and a narrow mask

Two input conditions are reported SEPARATELY:
- Natural observed, PDC-corrected Kepler light curves
- The same data PLUS a known stylized SPSD-like downward step

Artificial transit/step injection precedes the common normalization.
The source star may already contain planets or activity. Inverted/rolled
proxy nulls do NOT establish true survey FAP. No class label or known
injection parameters are passed into the fitting method.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from blind_transit_benchmark import bls_peak,threshold_from_controls
from kepler_preprocessing import (
 load_raw_kepler_quarter,normalize_flux,gap_edge_mask,
 inject_before_detrending,injected_signal_retention)
from localized_discontinuity import (
 localized_downward_step_mask,synthetic_spsd_like_step)

METHODS=("standard_bls","previous_gap_edge_mask","localized_step_mask")


def wilson(k,n):
    if n==0: return None
    z=1.96
    p=k/n; denom=1+z*z/n
    center=(p+z*z/(2*n))/denom
    delta=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/denom
    return [float(max(0,center-delta)),float(min(1,center+delta))]


def draw_artifact(t,raw,entry,rng,enabled):
    if not enabled:
        return np.asarray(raw,float).copy(),None
    cfg=entry["artifact_injections"]
    margin=float(cfg["start_time_margin_days"])
    if t.max()-t.min()<=2*margin:
        raise ValueError("Not enough observing time for a source-independent step")
    start=float(rng.uniform(t.min()+margin,t.max()-margin))
    amplitude=float(rng.uniform(*cfg["fractional_step_depth_range"]))
    tau=float(rng.uniform(*cfg["decay_timescale_days"]))
    persistence=float(rng.uniform(*cfg["persistent_fraction_range"]))
    changed,_=synthetic_spsd_like_step(t,raw,start,amplitude,tau,persistence)
    return changed,{"onset_bkjd":start,"amplitude_fraction":amplitude,
                    "tau_days":tau,"persistent_fraction":persistence}


def load_selected(stars,config,role):
    loaded=[]
    for case in stars:
        kic=int(case["kic"]);quarter=int(case["quarter"])
        print(role,kic,"Q",quarter,flush=True)
        try:
            t,raw,source=load_raw_kepler_quarter(kic,quarter)
            gap,report=gap_edge_mask(
                t, gap_days=float(config["preprocessing"]["gap_threshold_days"]),
                edge_days=float(config["preprocessing"]["gap_edge_days"]),
                minimum_remaining=int(config["preprocessing"]["step_min_retained"]))
            loaded.append({"role":role,"kic":kic,"quarter":quarter,
              "t":t,"raw":raw,"gap_mask":gap,
              "source":source,"gap_summary":report})
            print("  usable cadences",len(t),"gap mask removed",report["n_masked"],flush=True)
        except Exception as exc:
            loaded.append({"role":role,"kic":kic,"quarter":quarter,
                           "status":"source_error","error_type":type(exc).__name__,
                           "error_message":str(exc)[:300]})
            print("  inaccessible:",str(exc)[:210],flush=True)
    return loaded


def get_masks(star,flux,cfg):
    t=star["t"]
    step,diag=localized_downward_step_mask(
        t,flux,cfg["preprocessing"])
    return {
      "standard_bls":np.ones(len(t),bool),
      "previous_gap_edge_mask":star["gap_mask"],
      "localized_step_mask":step,
    },diag


def fit_method(t,flux,mask,config):
    return bls_peak(
        t[mask],flux[mask],
        bounds=config["bls"]["period_days"],
        frequency_factor=config["bls"]["frequency_factor"])


def source_accountability(stars):
    rows=[]
    for star in stars:
        ok="status" not in star
        rows.append({
          "role":star["role"],"kic":star["kic"],"quarter":star["quarter"],
          "status":"analyzed" if ok else star["status"],
          "points":len(star["t"]) if ok else None,
          "source_sha256":star["source"]["sha256"] if ok else None,
          "source_FITS":star["source"]["file"] if ok else None,
          "gap_points_removed":star["gap_summary"]["n_masked"] if ok else None,
          "error_type":star.get("error_type"),
          "error_message":star.get("error_message")})
    return rows


def calibration_proxy_rows(stars,config,seed,role):
    """Use independent proxy null seeds for calibration versus heldout."""
    n=int(config["calibration"]["proxy_nulls_per_star_per_condition"]
          if role=="calibration" else
          config["heldout_nulls"]["per_star_per_condition"])
    conditions=tuple(config["artifact_injections"]["conditions"])
    rows=[]
    for star in stars:
        if "status" in star: continue
        t=star["t"]
        origin=normalize_flux(star["raw"])
        # Different seed per star/role: no calibration-to-test copied samples.
        rng=np.random.default_rng(np.random.SeedSequence([seed,star["kic"]]))
        for cond in conditions:
            added=cond=="synthetic_spsd_like_step"
            for j in range(n):
                roll=int(rng.integers(1,len(t)))
                null=1.-np.roll(origin-1.,roll)
                # Normalize the proxy null after artifact injection, using
                # exactly the same median window as injected-planet cases.
                broken,artifact=draw_artifact(t,null,config,rng,added)
                prepared=normalize_flux(broken)
                masks,step_report=get_masks(star,prepared,config)
                for method,mask in masks.items():
                    try:
                        peak=fit_method(t,prepared,mask,config)
                        rows.append({
                          "status":"success","kic":star["kic"],
                          "role":role,"condition":cond,"proxy_index":j,
                          "method":method,"score":peak["score"],
                          "period_days":peak["period_days"],
                          "step_warning_count":step_report["n_persistent_step_events"],
                          "step_mask_points":step_report["n_removed"],
                          "truth_artifact_onset_bkjd":artifact["onset_bkjd"] if artifact else None,
                          "n_retained":int(mask.sum()),"roll":roll})
                    except Exception as exc:
                        rows.append({
                          "status":"fit_error","kic":star["kic"],
                          "role":role,"condition":cond,"proxy_index":j,
                          "method":method,"error_type":type(exc).__name__,
                          "error_message":str(exc)[:170]})
    return pd.DataFrame(rows)


def calibrate(csv,config):
    thresholds={}
    for method in METHODS:
        values=csv.loc[(csv.status=="success")&(csv.method==method),"score"]
        if len(values)<12:
            raise RuntimeError(f"Insufficient independent calibration proxy realizations for {method}")
        threshold=threshold_from_controls(
            values,config["calibration"]["nominal_proxy_null_tail_fraction"])
        thresholds[method]={"score_threshold":float(threshold),
                            "n_calibration_proxies":int(len(values)),
                            "n_calibration_stars":int(csv.loc[
                                (csv.status=="success")&(csv.method==method),
                                "kic"].nunique())}
    return thresholds


def injected_rows(stars,config,thresholds):
    rows=[]
    conds=tuple(config["artifact_injections"]["conditions"])
    depths=tuple(config["planet_injections"]["depths_ppm"])
    n=int(config["planet_injections"]["trials_per_depth_condition_star"])
    for star in stars:
        if "status" in star: continue
        t=star["t"];raw=star["raw"]
        for cond_idx,cond in enumerate(conds):
            has_artifact=cond=="synthetic_spsd_like_step"
            for depth in depths:
                for j in range(n):
                    seed=np.random.SeedSequence([
                        int(config["planet_injections"]["seed"]),
                        int(config["artifact_injections"]["seed"]),
                        star["kic"],cond_idx,int(depth),j])
                    rng=np.random.default_rng(seed)
                    period=float(rng.uniform(*config["planet_injections"]["period_range_days"]))
                    epoch=float(t.min()+rng.uniform(0,period))
                    duration=float(rng.uniform(*config["planet_injections"]["duration_range_days"]))
                    corrupt,artifact=draw_artifact(t,raw,config,rng,has_artifact)
                    with_planet,inside=inject_before_detrending(
                        t,corrupt,period,epoch,int(depth),duration)
                    unchanged=normalize_flux(corrupt)
                    prepared=normalize_flux(with_planet)
                    masks,step_report=get_masks(star,prepared,config)
                    center=artifact["onset_bkjd"] if artifact else None
                    detected_onsets=[v["time_bkjd"] for v in step_report["detected_events"]]
                    maskwidth=float(config["preprocessing"]["step_mask_half_width_days"])
                    correct_artifact_hit=(center is not None and any(
                        abs(center-x)<=maskwidth for x in detected_onsets))
                    # Do not pass period or artifact truth to either the step mask
                    # or the BLS detector. They are used below ONLY for scoring.
                    key=f"{star['kic']}-{cond}-{depth}-{j}"
                    for method,mask in masks.items():
                        row={
                          "status":"success","case":key,"kic":star["kic"],
                          "condition":cond,"depth_ppm":int(depth),
                          "iteration":j,"method":method,
                          "injected_period_days":period,
                          "injected_epoch_bkjd":epoch,
                          "injected_duration_days":duration,
                          "true_artifact_onset_bkjd":center,
                          "n_true_transit_cadences":int(inside.sum()),
                          "n_true_transit_cadences_masked":int((inside&~mask).sum()),
                          "signal_retention_fraction":injected_signal_retention(
                              unchanged,prepared,inside,mask),
                          "method_removed_cadences":int((~mask).sum()),
                          "n_step_detections":step_report["n_persistent_step_events"],
                          "step_hit_known_artifact":bool(correct_artifact_hit),
                          "step_onsets_bkjd":json.dumps(detected_onsets)}
                        try:
                            peak=fit_method(t,prepared,mask,config)
                            correct=abs(peak["period_days"]-period)/period < config["bls"]["max_period_error_fraction"]
                            flagged=peak["score"]>thresholds[method]["score_threshold"]
                            row.update({
                              "peak_score":peak["score"],
                              "measured_period_days":peak["period_days"],
                              "period_error_fraction":abs(peak["period_days"]-period)/period,
                              "period_correct":bool(correct),"flagged":bool(flagged),
                              "recovered":bool(correct and flagged)})
                        except Exception as exc:
                            row.update({"status":"fit_error",
                                        "error_type":type(exc).__name__,
                                        "error_message":str(exc)[:170],
                                        "period_correct":False,
                                        "flagged":False,"recovered":False})
                        rows.append(row)
    return pd.DataFrame(rows)


def make_summary(sources,calibration,thresholds,nulls,trials,config):
    report={
      "study":"Predeclared exploratory local step detector vs standard and near-gap BLS",
      "dataset":"Kepler DR25 PDCSAP real Q8 measurements + known synthetic planets and optionally stylized steps BEFORE same detrend",
      "sources":sources,
      "thresholds":thresholds,
      "n_planned_calibration_hosts":len(config["calibration_stars"]),
      "n_planned_heldout_hosts":len(config["heldout_stars"]),
      "n_usable_heldout_hosts":int(sum(
          row["role"]=="heldout" and row["status"]=="analyzed" for row in sources)),
      "per_condition_results":[],
      "per_condition_proxy_nulls":[],
      "paired_results":[],
      "science_limits":[
          "Only a handful of purposively selected real Kepler stars",
          "Calibration proxy nulls are inverted and rolled brightness, not known planet-free instrument nulls; these measure no true Kepler FAP.",
          "Synthetic SPSD-like discontinuities were designed to have a persistent downward step; success on such defects is conditional on an artificial model.",
          "Many injections on the same host share stellar noise and are not independent stars; Wilson intervals are descriptive only.",
          "Kepler PDC already removes many real SPSDs; no claim of detection/repair of an independently labeled real spacecraft defect.",
          "Preprocessing can delete genuine injected planet cadences; report that number.",
          "Fitted injected period within 2% and above threshold is not independent planet confirmation.",
          "Not a replication of Robnik et al. 2026 matched long-period mission injection study."
      ]
    }
    good=trials[trials.status=="success"]
    for (cond,depth,method),group in good.groupby(["condition","depth_ppm","method"]):
        n=int(len(group)); k=int(group.recovered.astype(bool).sum())
        report["per_condition_results"].append({
            "condition":cond,"depth_ppm":int(depth),"method":method,
            "n_trials":n,"n_recovered":k,
            "recovery_fraction":k/n,"wilson_95_descriptive":wilson(k,n),
            "n_distinct_stars":int(group.kic.nunique()),
            "n_real_transit_cadences_deleted":int(group.n_true_transit_cadences_masked.sum()),
            "mean_signal_retained":float(group.signal_retention_fraction.mean()),
            "n_step_flags_total":int(group.n_step_detections.sum())})
    usable_nulls=nulls[nulls.status=="success"]
    for (cond,method),g in usable_nulls.groupby(["condition","method"]):
        k=int((g.score>thresholds[method]["score_threshold"]).sum())
        n=len(g)
        report["per_condition_proxy_nulls"].append({
            "condition":cond,"method":method,
            "n_proxy":int(n),"n_flagged":k,
            "proxy_flag_fraction":k/n,"n_distinct_stars":int(g.kic.nunique()),
            "wilson_95_descriptive":wilson(k,n)})
    for cond,group in good.groupby("condition"):
        pivot=group.pivot(index="case",columns="method",values="recovered")
        pivot=pivot.dropna(subset=list(METHODS)) if all(m in pivot.columns for m in METHODS) else pd.DataFrame()
        if not pivot.empty:
            a=pivot["standard_bls"].astype(bool)
            b=pivot["localized_step_mask"].astype(bool)
            c=pivot["previous_gap_edge_mask"].astype(bool)
            report["paired_results"].append({
                "condition":cond,"n_paired":len(pivot),
                "baseline_only":int((a&~b).sum()),
                "localized_only":int((~a&b).sum()),
                "both":int((a&b).sum()),
                "neither":int((~a&~b).sum()),
                "old_gap_only_vs_baseline":int((~a&c).sum()),
                "old_gap_losses_vs_baseline":int((a&~c).sum())})
    return report


def chart(report,out):
    for condition in ("no_added_defect","synthetic_spsd_like_step"):
        groups=[r for r in report["per_condition_results"] if r["condition"]==condition]
        if not groups: continue
        depths=sorted(set(g["depth_ppm"] for g in groups))
        x=np.arange(len(depths));fig,ax=plt.subplots(figsize=(9,4))
        for i,method in enumerate(METHODS):
            values=[next((g["recovery_fraction"] for g in groups if
                          g["method"]==method and g["depth_ppm"]==d),np.nan)
                    for d in depths]
            ax.bar(x+(i-1)*.25,values,width=.245,label=method.replace("_"," "))
        ax.set_xticks(x,[f"{int(d)} ppm" for d in depths])
        ax.set(ylabel="Fraction of injections recovered",
               xlabel="Transit depth",ylim=(0,1.04),
               title=f"Real Kepler photometry — {condition.replace('_',' ')}")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(out/f"recovery_{condition}.png",dpi=160)
        plt.close(fig)


def experiment(manifest="LOCALIZED_STEP_STUDY_FROZEN_2026_11_07.json",
               output="results/localized_step_study"):
    cfg=json.loads(Path(manifest).read_text())
    if len(cfg["calibration_stars"])!=2 or len(cfg["heldout_stars"])!=6:
        raise ValueError("The source manifest cohort has been modified")
    ids=[int(x["kic"]) for x in cfg["calibration_stars"]+cfg["heldout_stars"]]
    if len(set(ids))!=len(ids):
        raise ValueError("Calibration/heldout host overlap")
    if cfg["methods"]!=list(METHODS):
        raise ValueError("Predeclared methods mismatch code")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    (out/"frozen_manifest.json").write_bytes(Path(manifest).read_bytes())
    calibration=load_selected(cfg["calibration_stars"],cfg,"calibration")
    heldout=load_selected(cfg["heldout_stars"],cfg,"heldout")
    sources=source_accountability(calibration+heldout)
    pd.DataFrame(sources).to_csv(out/"all_star_sources.csv",index=False)
    proxy_cal=calibration_proxy_rows(
       calibration,cfg,int(cfg["calibration"]["seed"]),"calibration")
    proxy_cal.to_csv(out/"calibration_proxies.csv",index=False)
    thresholds=calibrate(proxy_cal,cfg)
    (out/"frozen_method_thresholds.json").write_text(json.dumps(thresholds,indent=2))
    print("Calibration thresholds",json.dumps(thresholds),flush=True)
    nulls=calibration_proxy_rows(
        heldout,cfg,int(cfg["heldout_nulls"]["seed"]),"heldout")
    nulls.to_csv(out/"heldout_proxy_nulls.csv",index=False)
    test=injected_rows(heldout,cfg,thresholds)
    test.to_csv(out/"all_paired_injection_trials.csv",index=False)
    result=make_summary(sources,proxy_cal,thresholds,nulls,test,cfg)
    (out/"summary_and_limits.json").write_text(json.dumps(result,indent=2))
    chart(result,out)
    print(json.dumps(result,indent=2),flush=True)
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--manifest",default="LOCALIZED_STEP_STUDY_FROZEN_2026_11_07.json")
    parser.add_argument("--out",default="results/localized_step_study")
    args=parser.parse_args()
    experiment(args.manifest,args.out)
