"""Independent synthetic holdout: BLS, event consistency, and eclipse indicators.

Thresholds and the independent seed are frozen in source before GitHub Actions
executes this follow-up. Diagnostic choices were informed by an earlier pilot,
so this is still exploratory rather than confirmation of a population-wide gain.
"""
from pathlib import Path
import argparse, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from blind_transit_benchmark import (
    simulate, bls_peak, threshold_from_controls, NO_PLANET_KINDS,
    TEST_KINDS, PLANET_DEPTHS_PPM)
from event_vetting_ablation import classify_observation
from binary_eclipse_diagnostics import estimate_binary_indicators

FROZEN_SEED=20261107
FROZEN_CALIBRATION_PER_KIND=8
FROZEN_TEST_PER_CONDITION=8


def compare(output="results/binary_eclipse_followup",
            seed=FROZEN_SEED,
            calibration_per_kind=FROZEN_CALIBRATION_PER_KIND,
            per_condition=FROZEN_TEST_PER_CONDITION):
    if calibration_per_kind<4 or per_condition<4:
        raise ValueError("Insufficient synthetic calibration or holdout count")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(seed)
    calibration=[]
    for kind in NO_PLANET_KINDS:
        for _ in range(calibration_per_kind):
            sample_seed=int(rng.integers(1,2**32-1))
            t,f,_=simulate(sample_seed,kind=kind)
            calibrated=bls_peak(t,f)
            calibration.append({"kind":kind,"seed":sample_seed,
                                "score":calibrated["score"]})
    cal=pd.DataFrame(calibration)
    cal.to_csv(out/"null_calibration.csv",index=False)
    cutoff=threshold_from_controls(cal.score,.1)
    rows=[]
    for kind,depth in [(k,None) for k in TEST_KINDS]+[
        ("planet",d) for d in PLANET_DEPTHS_PPM]:
        for _ in range(per_condition):
            sample_seed=int(rng.integers(1,2**32-1))
            t,f,truth=simulate(sample_seed,kind=kind,
                               depth_ppm=depth or 1500)
            base=classify_observation(t,f,cutoff)
            eb=estimate_binary_indicators(t,f,base["period_days"],
                base["transit_time_days"],base["duration_days"])
            final=bool(base["enhanced_flag"] and not eb["binary_review_warning"])
            true_p=truth["injected_period_days"]
            correct=bool(true_p is not None and
                abs(base["period_days"]-true_p)/true_p<=.02)
            rows.append({
                "group":f"planet_{depth}ppm" if kind=="planet" else kind,
                "seed":sample_seed,"known_period_days":true_p,
                "predicted_period_days":base["period_days"],
                "correct_period":correct,"bls_score":base["score"],
                "bls_only":bool(base["baseline_flag"]),
                "event_checks":bool(base["enhanced_flag"]),
                "event_plus_binary_checks":final,
                "odd_even_warning":eb["odd_even_warning"],
                "secondary_warning":eb["secondary_warning"],
                "odd_even_ratio":eb["odd_even_depth_ratio"],
                "odd_even_statistic":eb["odd_even_statistic"],
                "secondary_snr":eb["secondary_snr"],
            })
    trials=pd.DataFrame(rows)
    trials.to_csv(out/"holdout_cases.csv",index=False)
    metrics=[]
    for group,data in trials.groupby("group",sort=False):
        for method in ("bls_only","event_checks","event_plus_binary_checks"):
            flags=data[method].astype(bool)
            isplanet=group.startswith("planet_")
            metrics.append({
                "group":group,"method":method,"n":int(len(data)),
                "flagged":int(flags.sum()),
                "flag_rate":float(flags.mean()),
                "correct_period_and_flagged":int((flags&data.correct_period).sum()) if isplanet else None,
                "period_recovery_and_flag_fraction":float((flags&data.correct_period).mean()) if isplanet else None,
                "scientific_note":"A veto cannot improve recall at fixed BLS threshold",
            })
    summary=pd.DataFrame(metrics)
    summary.to_csv(out/"comparison.csv",index=False)
    fig,ax=plt.subplots(figsize=(11,4))
    groups=list(summary.group.unique())
    x=np.arange(len(groups))
    for offset,method in zip((-.23,0,.23),("bls_only","event_checks","event_plus_binary_checks")):
        v=[summary.loc[(summary.group==g)&(summary.method==method),
             "flag_rate"].iloc[0] for g in groups]
        ax.bar(x+offset,v,width=.22,label=method.replace("_"," "))
    ax.set_xticks(x,groups,rotation=25,ha="right")
    ax.set(ylabel="Fraction flagged",ylim=(0,1.04),
           title="Fresh synthetic holdout: three transit screening strategies")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out/"binary_eclipse_followup.png",dpi=160)
    plt.close(fig)
    report={
      "data":"Simulated Kepler-like white/red noise and transits; NOT actual observed Kepler photometry",
      "seed":seed,"n_calibration":len(cal),"n_test":len(trials),
      "calibration_threshold":cutoff,
      "fixed_rules":{
        "odd_even_depth_ratio_min":.35,
        "odd_even_statistic_min":3.0,
        "secondary_depth_ratio_min":.30,
        "secondary_snr_min":5.0},
      "limitations":[
        "This is exploratory; decisions were inspired by previous pilot observations",
        "Small number of simulations per group",
        "Binary warnings can reject genuine planets, including occultations",
        "Classification of a periodic binary as nonplanet requires additional information",
        "No survey-wide planet reliability or mission sensitivity estimation"],
      "summary":json.loads(summary.to_json(orient="records")),
    }
    (out/"report.json").write_text(json.dumps(report,indent=2))
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="results/binary_eclipse_followup")
    p.add_argument("--per-condition",type=int,default=FROZEN_TEST_PER_CONDITION)
    args=p.parse_args()
    print(json.dumps(compare(output=args.out,per_condition=args.per_condition),indent=2))
