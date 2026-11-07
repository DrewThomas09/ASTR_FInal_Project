"""Ablation: BLS alone versus BLS with a physical event-consistency veto.

This is a *synthetic* evaluation, distinct from the NASA DR25 catalog model.
The additional veto uses only independently fitted BLS information; the hidden
injected period is used AFTER prediction solely to score recovery.

Important: event vetting can never increase recall at the SAME BLS threshold.
We report the change in recall, false-control flags and a diagnostic warning
rate. These are toy experimental false flags, not Kepler survey FAP.
"""
from pathlib import Path
import argparse, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from blind_transit_benchmark import (
    bls_peak, simulate, threshold_from_controls, NO_PLANET_KINDS,
    TEST_KINDS, PLANET_DEPTHS_PPM)
from transit_consistency import individual_transit_checks


def event_accepts(diagnostics):
    """A prespecified, intentionally simple heuristic veto."""
    n = diagnostics.get("n_observable_events")
    fraction = diagnostics.get("positive_depth_fraction")
    dominance = diagnostics.get("dominance")
    odd_even = diagnostics.get("odd_even_depth_difference_ppm")
    if n is None or n < 3 or fraction is None or fraction < .60:
        return False
    if dominance is None or dominance > .60:
        return False
    # Only evaluate odd/even differences when both groups had >=2 events.
    # This ratio is not a calibrated eclipsing-binary false-positive probability.
    if odd_even is not None and abs(odd_even)>0:
        median_depth = diagnostics.get("median_depth_ppm")
        if median_depth is not None and median_depth>0:
            if abs(odd_even)/median_depth > .75:
                return False
    return True


def classify_observation(time, flux, threshold, bounds=(1.5,12.),
                         frequency_factor=5.):
    """Blind BLS then event check, with NO injected truth passed in."""
    peak=bls_peak(time,flux,bounds=bounds,frequency_factor=frequency_factor)
    diagnostic,events=individual_transit_checks(
        time,flux,peak["period_days"],peak["transit_time_days"],
        peak["duration_days"])
    if len(events):
        positive=events.loc[events.depth_ppm>0, "depth_ppm"]
        diagnostic["median_depth_ppm"]=float(positive.median()) if len(positive) else None
    else:
        diagnostic["median_depth_ppm"]=None
    baseline=bool(peak["score"]>threshold)
    accepts=event_accepts(diagnostic)
    return {
        **peak,
        "baseline_flag":baseline,
        "event_veto_pass":accepts,
        "enhanced_flag":baseline and accepts,
        "event_count":diagnostic["n_observable_events"],
        "event_dominance":diagnostic["dominance"],
        "positive_event_fraction":diagnostic["positive_depth_fraction"],
        "event_warning":diagnostic["warning"],
    }


def summarized(trials):
    rows=[]
    for name,group in trials.groupby("group",sort=False):
        isplanet=name.startswith("planet_")
        for method in ("baseline","enhanced"):
            flagged=group[method+"_flag"].astype(bool)
            recovered=(flagged & group["correct_period"]).sum() if isplanet else None
            rows.append({
                "group":name,"method":method,"n":int(len(group)),
                "flagged":int(flagged.sum()),
                "fraction_flagged":float(flagged.mean()),
                "correct_period_and_flagged":int(recovered) if isplanet else None,
                "correct_period_recovery_fraction":float(recovered/len(group)) if isplanet else None,
            })
    return pd.DataFrame(rows)


def experiment(output="results/event_ablation",per_condition=5,
               calibration_per_kind=8,seed=12600):
    if per_condition<3 or calibration_per_kind<4:
        raise ValueError("Need adequate independent validation and test examples")
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(seed)
    # Calibration set: independent null-only light curves.
    calibrations=[]
    for kind in NO_PLANET_KINDS:
        for _ in range(calibration_per_kind):
            t,f,_=simulate(int(rng.integers(1,2**32-1)),kind=kind)
            peak=bls_peak(t,f)
            calibrations.append({"kind":kind,"peak_score":peak["score"]})
    control_df=pd.DataFrame(calibrations)
    control_df.to_csv(out/"calibration_controls.csv",index=False)
    threshold=threshold_from_controls(control_df.peak_score,.10)

    conditions=[(kind,None) for kind in TEST_KINDS]
    conditions += [("planet",depth) for depth in PLANET_DEPTHS_PPM]
    rows=[]
    for kind,depth in conditions:
        for i in range(per_condition):
            sample_seed=int(rng.integers(1,2**32-1))
            t,f,truth=simulate(sample_seed,kind=kind,depth_ppm=depth or 1500)
            result=classify_observation(t,f,threshold)
            actual=truth["injected_period_days"]
            correct=bool(
                actual is not None and
                abs(result["period_days"]-actual)/actual <=.02)
            rows.append({
                "group":f"planet_{depth}ppm" if kind=="planet" else kind,
                "sample_seed":sample_seed,
                "injected_period_days":actual,
                "injected_depth_ppm":depth if kind=="planet" else None,
                "correct_period":correct,**result,
            })
    trials=pd.DataFrame(rows)
    trials.to_csv(out/"blinded_holdout.csv",index=False)
    comparison=summarized(trials)
    comparison.to_csv(out/"ablation_comparison.csv",index=False)
    fig,ax=plt.subplots(figsize=(9,4))
    x=np.arange(len(comparison.group.unique()))
    names=list(comparison.group.unique())
    a=[comparison.loc[(comparison.group==g)&(comparison.method=="baseline"),
        "fraction_flagged"].iloc[0] for g in names]
    b=[comparison.loc[(comparison.group==g)&(comparison.method=="enhanced"),
        "fraction_flagged"].iloc[0] for g in names]
    ax.bar(x-.18,a,width=.36,label="BLS only")
    ax.bar(x+.18,b,width=.36,label="BLS + event checks")
    ax.set_xticks(x,names,rotation=25,ha="right")
    ax.set_ylim(0,1.05)
    ax.set_ylabel("Fraction flagged as candidate")
    ax.set_title("Synthetic holdout: tradeoff from additional event vetting")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out/"event_ablation.png",dpi=150)
    plt.close(fig)
    report={
        "data_provenance":"SIMULATED brightness observations; not real Kepler data",
        "n_test":len(trials),
        "n_calibration_null":len(control_df),
        "calibrated_on":["white_noise","red_noise","single_dip"],
        "heldout_classes":list(trials.group.unique()),
        "score_threshold":threshold,
        "recovery_definition":"Flag + fitted orbital period within 2% of injected period",
        "interpretation_limitations":[
            "Small synthetic test samples; uncertain empirical fractions",
            "Event checks cannot increase sensitivity at fixed BLS threshold",
            "Astrophysical binaries are not ruled out by a low instrumental FAP",
            "No real noise injection in this experiment"],
        "groups":json.loads(comparison.to_json(orient="records")),
    }
    (out/"event_ablation_report.json").write_text(json.dumps(report,indent=2))
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="results/event_ablation")
    p.add_argument("--per-condition",type=int,default=5)
    p.add_argument("--calibration-per-kind",type=int,default=8)
    a=p.parse_args()
    print(json.dumps(experiment(a.output,a.per_condition,a.calibration_per_kind),indent=2))
