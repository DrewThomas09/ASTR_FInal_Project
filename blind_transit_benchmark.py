"""Blind transit injection/recovery benchmark.

Scientific status: synthetic exercise, not NASA Kepler survey completeness.
BLS is a published algorithm provided by Astropy, not newly invented ML.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PERIOD_SEARCH = (1.5, 12.0)
DURATIONS_DAYS = (0.09, 0.15, 0.24)
FALSE_ALARM_TARGET = .10
NO_PLANET_KINDS = ("white_noise", "red_noise", "single_dip")
TEST_KINDS = NO_PLANET_KINDS + ("binary_like",)
PLANET_DEPTHS_PPM = (500, 1500, 4000)


def simulate(seed, kind="planet", depth_ppm=1500, baseline=48., cadence=.03,
             measurement_sigma=.001):
    """Draw random period, phase, duration and missing data; includes controls."""
    if kind not in ("planet", *TEST_KINDS):
        raise ValueError("Unknown kind: " + str(kind))
    rng = np.random.default_rng(seed)
    t = np.arange(0, baseline, cadence)
    f = 1 + rng.normal(0, measurement_sigma, len(t))
    if kind in ("planet", "red_noise", "single_dip", "binary_like"):
        eps = rng.normal(0, .00018, len(t))
        red = np.zeros(len(t))
        for j in range(1, len(t)):
            red[j] = .94*red[j-1] + eps[j]
        f += red
        f += .00025 * np.sin(2*np.pi*t/rng.uniform(6,13)+rng.uniform(0,2*np.pi))
    truth = {"kind":kind, "seed":int(seed), "injected_period_days":None,
             "injected_depth_ppm":0., "injected_duration_days":None}
    if kind == "planet":
        period = float(rng.uniform(2.1, 9.8))
        duration = float(rng.uniform(.10,.20))
        epoch = float(rng.uniform(0.,period))
        phase = (t-epoch+period/2)%period-period/2
        f[np.abs(phase)<duration/2] -= depth_ppm/1e6
        truth.update(injected_period_days=period,
                     injected_depth_ppm=float(depth_ppm),
                     injected_duration_days=duration)
    elif kind == "single_dip":
        center=float(rng.uniform(5,baseline-5))
        duration=float(rng.uniform(.1,.22))
        f[np.abs(t-center)<duration/2] -= rng.uniform(.003,.007)
    elif kind == "binary_like":
        period=float(rng.uniform(4,9))
        epoch=float(rng.uniform(0,period))
        duration=float(rng.uniform(.1,.18))
        primary=(t-epoch+period/2)%period-period/2
        secondary=(t-epoch-period/2+period/2)%period-period/2
        f[np.abs(primary)<duration/2] -= .005
        f[np.abs(secondary)<duration/2] -= .0025
    # Shared gaps across all classes; no truth values passed into detector.
    mask = rng.random(len(t)) > .04
    for _ in range(3):
        start=rng.uniform(0,baseline-1)
        mask &= ~((t>=start)&(t<=start+rng.uniform(.12,.75)))
    return t[mask], f[mask], truth


def robust_sigma(flux):
    d=np.diff(np.asarray(flux,dtype=float))
    med=np.median(d)
    return float(max(np.median(np.abs(d-med))/(0.6744897501960817*np.sqrt(2)),1e-6))


def bls_peak(times, flux, bounds=PERIOD_SEARCH, frequency_factor=5.):
    """Blind period search over a predeclared broad range using Astropy BLS."""
    from astropy.timeseries import BoxLeastSquares
    times=np.asarray(times,dtype=float);flux=np.asarray(flux,dtype=float)
    if len(times)<100 or not np.all(np.isfinite(times+flux)):
        raise ValueError("Insufficient finite measurements")
    sigma=robust_sigma(flux)
    m=BoxLeastSquares(times,flux,dy=np.full_like(flux,sigma))
    r=m.autopower(DURATIONS_DAYS, minimum_period=bounds[0],
                  maximum_period=bounds[1], objective="snr",
                  frequency_factor=frequency_factor)
    k=int(np.nanargmax(r.power))
    return {"period_days":float(r.period[k]),"score":float(r.power[k]),
            "depth_ppm":float(r.depth[k])*1e6,
            "duration_days":float(r.duration[k]),"transit_time_days":float(r.transit_time[k]),"sigma_estimate":sigma}


def threshold_from_controls(scores, target_fpr=FALSE_ALARM_TARGET):
    """Only calibration controls set the threshold; not a survey-wide FAP."""
    x=np.asarray(scores,dtype=float)
    if len(x)<8 or not np.all(np.isfinite(x)):
        raise ValueError("Need >=8 finite calibration examples")
    if not 0<target_fpr<1:
        raise ValueError("target_fpr should be between 0 and 1")
    return float(np.quantile(x,1-target_fpr,method="higher"))


def summarize_trials(table):
    rows=[]
    for name,g in table.groupby("group",sort=False):
        n=len(g); selected=int(g.flagged.sum())
        correct=int(g.recovered.sum()) if name.startswith("planet_") else None
        rows.append({"group":name,"count":n,"flagged":selected,
                     "fraction_flagged":float(selected/n),
                     "correct_and_flagged":correct,
                     "recovery_fraction":float(correct/n) if correct is not None else None})
    return pd.DataFrame(rows)


def run_experiment(outdir="results/blind",seed=12600,per_condition=8,
                   target_fpr=FALSE_ALARM_TARGET,frequency_factor=5.):
    """Precalibrate null peak scores and evaluate independent holdout stars."""
    if per_condition<4:
        raise ValueError("Minimum 4 simulated stars per category")
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    n=per_condition*(len(NO_PLANET_KINDS)+len(TEST_KINDS)+len(PLANET_DEPTHS_PPM))
    samples=np.random.SeedSequence(seed).spawn(n)
    seeds=iter([int(s.generate_state(1)[0]) for s in samples])
    null_scores=[]
    for kind in NO_PLANET_KINDS:
        for _ in range(per_condition):
            t,f,_=simulate(next(seeds),kind=kind)
            null_scores.append(bls_peak(t,f,frequency_factor=frequency_factor)["score"])
    limit=threshold_from_controls(null_scores,target_fpr)
    records=[]
    conditions=[(kind,None) for kind in TEST_KINDS]
    conditions += [("planet",depth) for depth in PLANET_DEPTHS_PPM]
    for kind,depth in conditions:
        for _ in range(per_condition):
            s=next(seeds)
            t,f,truth=simulate(s,kind=kind,depth_ppm=depth or 1500)
            peak=bls_peak(t,f,frequency_factor=frequency_factor)
            flagged=bool(peak["score"]>limit)
            correct=bool(kind=="planet" and flagged and
                abs(peak["period_days"]-truth["injected_period_days"]) /
                truth["injected_period_days"] < .02)
            records.append({"seed":s,"group":f"planet_{depth}ppm" if kind=="planet" else kind,
                            "known_true_period_days":truth["injected_period_days"],
                            **peak,"flagged":flagged,"recovered":correct})
    trials=pd.DataFrame(records)
    trials.to_csv(out/"holdout_trials.csv",index=False)
    summary=summarize_trials(trials)
    summary.to_csv(out/"summary.csv",index=False)
    fig,ax=plt.subplots(figsize=(8,4.5))
    ax.bar(summary.group,summary.fraction_flagged)
    ax.set_ylim(0,1.05)
    ax.set_ylabel("Fraction of independent simulations")
    ax.set_title("Synthetic BLS: null-calibrated threshold, blind period")
    ax.tick_params(axis="x",rotation=25)
    fig.tight_layout()
    fig.savefig(out/"blind_detection_by_group.png",dpi=170);plt.close(fig)
    report={"source":"SYNTHETIC ONLY (not real Kepler results)",
            "search_period_days":list(PERIOD_SEARCH),
            "target_control_fpr":target_fpr,
            "empirical_null_threshold":limit,
            "calibration_count":len(null_scores),
            "holdout_count":len(trials),
            "limitations":"Simple noise surrogates; no real Kepler survey completeness or FAP",
            "summary":json.loads(summary.to_json(orient="records"))}
    (out/"method_and_results.json").write_text(json.dumps(report,indent=2))
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="results/blind")
    p.add_argument("--per-condition",type=int,default=8)
    p.add_argument("--seed",type=int,default=12600)
    p.add_argument("--target-fpr",type=float,default=.10)
    args=p.parse_args()
    print(json.dumps(run_experiment(args.output,args.seed,args.per_condition,
                                    args.target_fpr),indent=2))
