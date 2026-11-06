"""Reproducible transit-search demonstration (not a discovery claim).

AI authored; BLS is the published method of Kovacs, Zucker and Mazeh (2002).
Scientific calculations are implemented through Astropy, not a new ML model.
"""
from pathlib import Path
import argparse, json
import numpy as np
import matplotlib.pyplot as plt

def simulate_light_curve(seed=12600, planet=True, period_days=3.25,
                         depth=0.004, duration_days=0.16, noise=0.001):
    rng = np.random.default_rng(seed)
    t = np.arange(0, 65, 1/48)
    flux = 1 + rng.normal(0,noise,len(t))
    if planet:
        phase = (t - 0.92 + period_days/2)%period_days-period_days/2
        flux[np.abs(phase)<duration_days/2] -= depth
    return t, flux

def detect(t,flux,min_period=2.8,max_period=3.8):
    """Return strongest *candidate*, which can occur even without a planet."""
    from astropy.timeseries import BoxLeastSquares
    periods = np.linspace(min_period,max_period,2000)
    durations = np.array([0.08,0.12,0.16,0.20])
    model = BoxLeastSquares(t,flux,dy=np.full(len(t),0.001))
    power = model.power(periods,durations,objective="snr")
    i = int(np.argmax(power.power))
    result = {"best_period_days":float(power.period[i]),
              "depth_ppm":float(power.depth[i])*1e6,
              "transit_duration_hours":float(power.duration[i])*24,
              "peak_snr_statistic":float(power.power[i])}
    return result,periods,np.asarray(power.power)

def run(planet=True,seed=12600,out="results/transits",depth=0.004):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    t,flux=simulate_light_curve(seed=seed,planet=planet,depth=depth)
    result,periods,scores=detect(t,flux)
    result.update({"source":"SIMULATED, not real Kepler observations",
                   "injected_period_days":3.25 if planet else None,
                   "period_error_days":abs(result["best_period_days"]-3.25) if planet else None})
    label="planet_injected" if planet else "noise_only"
    fig,axes=plt.subplots(2,1,figsize=(8,6))
    axes[0].scatter(t,flux,s=1.5)
    axes[0].set(xlabel="Time (days)",ylabel="Relative stellar flux",
                title="Simulated stellar brightness")
    axes[1].plot(periods,scores,lw=1)
    axes[1].axvline(result["best_period_days"],color="gray",linestyle="--")
    axes[1].set(xlabel="Trial period (days)",ylabel="BLS detection score",
                title="Box Least Squares periodicity search")
    fig.tight_layout();fig.savefig(out/(label+".png"),dpi=170);plt.close(fig)
    (out/(label+".json")).write_text(json.dumps(result,indent=2))
    return result

def sensitivity_study(out="results/sensitivity",trials=12):
    """Keep noise level fixed and compare recovery at three transit depths."""
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for depth_ppm in (4000,1500,500):
        recovered=0
        errors=[]
        for i in range(trials):
            t,y=simulate_light_curve(seed=12600+i,depth=depth_ppm/1e6)
            result,_,_=detect(t,y)
            error=abs(result["best_period_days"]-3.25)
            errors.append(error)
            recovered+=error<0.05
        rows.append({"depth_ppm":depth_ppm,"recovered":recovered,
                     "trials":trials,"median_period_error_days":float(np.median(errors))})
    import pandas as pd
    df=pd.DataFrame(rows)
    df.to_csv(out/"sensitivity_summary.csv",index=False)
    fig,ax=plt.subplots(figsize=(6,3.5))
    ax.bar(df.depth_ppm.astype(str),100*df.recovered/df.trials)
    ax.set(xlabel="Simulated transit depth (ppm)",ylabel="Correct period recovered (%)",
           ylim=(0,105),title="Sensitivity to weaker transits")
    fig.tight_layout();fig.savefig(out/"sensitivity.png",dpi=170);plt.close(fig)
    return df

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="results/transits")
    a=p.parse_args()
    print("Injected planet:",run(out=a.output))
    print("Noise-only:",run(planet=False,out=a.output))
    print(sensitivity_study())
