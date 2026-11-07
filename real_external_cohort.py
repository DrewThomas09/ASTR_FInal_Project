"""Frozen external cohort: independent published Kepler planets and binaries.

The cohort list lives in real_external_cohort_frozen.json, committed BEFORE
this pipeline ran. No known orbital period is passed into BLS or vetting.
All 13 targets, including missing downloads and ambiguous period fits, remain
visible in the outcome table. Class outcomes are NOT NASA survey rates.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from real_kepler_lightcurve import fetch_kepler_quarter
from blind_transit_benchmark import bls_peak
from binary_eclipse_diagnostics import estimate_binary_indicators


def period_status(recovered, published, tolerance=.02):
    """Label exact / 1:2 or 2:1 alias / unmatched; all are scientifically distinct."""
    if not (np.isfinite(recovered) and np.isfinite(published)
            and recovered>0 and published>0):
        return "invalid_fit", None
    tests=[("exact",1.),("half_period_alias",.5),("double_period_alias",2.)]
    residuals=[(name,float(abs(recovered-published*fac)/(published*fac)))
               for name,fac in tests]
    name,error=min(residuals,key=lambda x:x[1])
    return (name if error<=tolerance else "unmatched",error)


def wilson_interval(successes, total, z=1.96):
    """Descriptive binomial interval, not a population guarantee for a nonrandom sample."""
    if not total:
        return None
    p=successes/total
    den=1+z*z/total
    mid=(p+z*z/(2*total))/den
    half=z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/den
    return [float(max(0,mid-half)),float(min(1,mid+half))]


def run_target(item,bounds):
    t,f,source=fetch_kepler_quarter(f"KIC {int(item['kic'])}",int(item["quarter"]))
    # The published period is NEVER provided to the detector.
    fitted=bls_peak(t,f,bounds=tuple(bounds))
    diagnostics=estimate_binary_indicators(t,f,
                    fitted["period_days"],fitted["transit_time_days"],
                    fitted["duration_days"])
    match,error=period_status(
        fitted["period_days"],float(item["period_days"]))
    return {
        "status":"analyzed", "kic":int(item["kic"]),
        "class":item["kind"],"name":item["name"],
        "reference":item["source"],"period_source_days":float(item["period_days"]),
        "search_bounds_days":list(bounds),
        "measured_period_days":fitted["period_days"],
        "period_relation":match,"best_alias_relative_error":error,
        "exact_period_match":match=="exact",
        "binary_review_warning":diagnostics["binary_review_warning"],
        "odd_even_warning":diagnostics["odd_even_warning"],
        "secondary_warning":diagnostics["secondary_warning"],
        "secondary_snr":diagnostics["secondary_snr"],
        "odd_even_depth_ratio":diagnostics["odd_even_depth_ratio"],
        "n_observable_events":diagnostics["n_events"],
        "n_quality_cadences":source["cadences_after_quality_mask"],
        "fits_sha256":source["sha256"], "fits_file":source["file"],
        "BLS_signal_score_UNCALIBRATED":fitted["score"],
        "interpretation":"This is only a binary-like REVIEW warning, never proof of an actual binary or absence of a planet",
    }


def summarize(df,planned):
    results={"n_planned":int(planned),
      "n_successful_analysis":int((df.status=="analyzed").sum()),
      "n_errors":int((df.status!="analyzed").sum()),
      "search_period_relations":df.period_relation.fillna("not_analyzed").value_counts().to_dict(),
      "by_class":{}}
    for kind,part in df.groupby("class"):
        analyzed=part[part.status=="analyzed"]
        matched=analyzed[analyzed.period_relation=="exact"]
        n=len(matched)
        warnings=int(matched.binary_review_warning.astype(bool).sum())
        results["by_class"][kind]={
          "n_planned":int(len(part)),
          "n_analyzed":int(len(analyzed)),
          "n_failed_download_or_processing":int(len(part)-len(analyzed)),
          "n_exact_period":int(n),
          "n_half_or_double_alias":int(analyzed.period_relation.isin(
              ["half_period_alias","double_period_alias"]).sum()),
          "n_unmatched":int((analyzed.period_relation=="unmatched").sum()),
          "n_warned_among_exact_period_cases":warnings,
          "exact_period_warning_fraction":float(warnings/n) if n else None,
          "wilson95_descriptive_interval":wilson_interval(warnings,n),
          "warning_fraction_comment":"Conditional on period recovery, not a population-wide detection rate",
        }
    return results


def save_outputs(rows,out,planned):
    df=pd.DataFrame(rows)
    df.to_csv(out/"all_attempted_targets.csv",index=False)
    summary=summarize(df,planned)
    summary["provenance_warning"]=[
        "Convenience sample selected by published identity and period",
        "Prior two demonstration stars are excluded",
        "All 13 intended targets are preserved, including failed access and unmatched period",
        "No thresholds changed based on individual or test-cohort results",
        "Binary review warning is not a planet-probability or a definitive classification",
        "Values conditional on quarter, BLS window, flux preprocessing and exact-period recovery",
    ]
    (out/"cohort_summary.json").write_text(json.dumps(summary,indent=2))
    return summary


def main(manifest="real_external_cohort_frozen.json",
         output="results/real_external_cohort"):
    plan=json.loads(Path(manifest).read_text())
    stars=plan["targets"]
    if plan["bounds"]!=[.9,15] or len(stars)<10:
        raise ValueError("Frozen manifest bounds or cohort size differ")
    ids=[int(x["kic"]) for x in stars]
    if len(set(ids))!=len(ids) or set(ids)&{8692861,10661783}:
        raise ValueError("Duplicate targets or development examples in external cohort")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    # Record source manifest byte-for-byte before any observations arrive.
    (out/"frozen_cohort_snapshot.json").write_bytes(Path(manifest).read_bytes())
    rows=[]
    for i,item in enumerate(stars,1):
        print(f"[{i}/{len(stars)}] {item['kind']} {item['name']} Q{item['quarter']}",
              flush=True)
        try:
            row=run_target(item,plan["bounds"])
            print(" period relationship:",row["period_relation"],
                  " binary warning:",row["binary_review_warning"],flush=True)
        except Exception as ex:
            row={"status":"error","kic":int(item["kic"]),
                 "name":item["name"],"class":item["kind"],
                 "reference":item["source"],
                 "period_source_days":float(item["period_days"]),
                 "period_relation":None,
                 "binary_review_warning":None,
                 "error_type":type(ex).__name__,
                 "error_message":str(ex)[:400]}
            print(" ERROR:",row["error_type"],row["error_message"],flush=True)
        rows.append(row)
        # Crash-safe outputs preserve the failed case and successful partial work.
        report=save_outputs(rows,out,len(stars))
    report=save_outputs(rows,out,len(stars))
    plot=pd.read_csv(out/"all_attempted_targets.csv")
    fig,ax=plt.subplots(figsize=(10,4))
    colors=[1 if v=="planet" else 0 for v in plot["class"]]
    x=np.arange(len(plot))
    for j,r in plot.iterrows():
        if r.status=="analyzed":
            label=r.period_relation
            marker="o" if label=="exact" else "x"
            y=1 if r.binary_review_warning==True else 0
            ax.scatter(j,y,marker=marker,s=100,c="tab:blue" if r["class"]=="planet" else "tab:orange")
        else:
            ax.scatter(j,.5,marker="s",s=85,c="grey")
    ax.set_xticks(x,[str(v) for v in plot.name],rotation=50,ha="right")
    ax.set_ylim(-.25,1.25)
    ax.set_yticks([0,.5,1],["No binary warning","Data unavailable","Binary review warning"])
    ax.set_title("Real Kepler cohort: all selected targets, including missing/aliased cases")
    fig.tight_layout()
    fig.savefig(out/"cohort_warning_audit.png",dpi=160)
    plt.close(fig)
    print(json.dumps(report,indent=2))
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",default="real_external_cohort_frozen.json")
    p.add_argument("--out",default="results/real_external_cohort")
    args=p.parse_args()
    main(args.manifest,args.out)
