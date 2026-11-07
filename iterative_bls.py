"""Exploratory iterative BLS for multi-planet systems.

Motivation: in frozen external real-star cohort, BLS found Kepler-18c rather
than selected Kepler-18b and Kepler-20c rather than selected Kepler-20b.
This is a *post-hoc development experiment*, not an independent validation.

Each iteration fits the strongest BLS box transit, subtracts that model, then
searches residual flux over the SAME period window. Published orbital periods
are used only AFTER fitting, to evaluate what the code actually found.
"""
from __future__ import annotations
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from astropy.timeseries import BoxLeastSquares
from blind_transit_benchmark import bls_peak,robust_sigma
from real_kepler_lightcurve import fetch_kepler_quarter

WINDOW=(1.5,15.)
MAX_COMPONENTS=3
STARS=[
 {"name":"Kepler-18","kic":8644288,"quarter":8,
  "published_planets":{"Kepler-18 b":3.504725,"Kepler-18 c":7.64159,
                       "Kepler-18 d":14.85888},
  "source":"https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-18"},
 {"name":"Kepler-20","kic":6850504,"quarter":8,
  "published_planets":{"Kepler-20 b":3.696115,"Kepler-20 c":10.854095934},
  "source":"https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-20"},
]


def subtract_best_transit(time,flux,peak):
    """Remove only the published Astropy BLS model, retaining baseline."""
    t=np.asarray(time,dtype=float)
    f=np.asarray(flux,dtype=float)
    if t.shape!=f.shape or len(t)<100:
        raise ValueError("Need same-length long series")
    model=BoxLeastSquares(t,f,dy=np.full(len(f),robust_sigma(f))).model(
      t,peak["period_days"],peak["duration_days"],peak["transit_time_days"])
    if len(model)!=len(t) or not np.all(np.isfinite(model)):
        raise ValueError("BLS transit model contains invalid values")
    return f-(model-np.median(model))


def search_iteratively(time,flux,n_components=MAX_COMPONENTS,bounds=WINDOW):
    """Return independent-looking BLS peaks with progressively modeled flux."""
    if not 1<=n_components<=5:
        raise ValueError("Number of components must be 1 through 5")
    original=np.asarray(flux,dtype=float)
    residual=original.copy()
    rows=[]
    for iteration in range(1,n_components+1):
        peak=bls_peak(time,residual,bounds=bounds)
        rows.append({"iteration":iteration,**peak})
        residual=subtract_best_transit(time,residual,peak)
    return pd.DataFrame(rows),residual


def match_reference_period(period,targets,tolerance=.02):
    """All known periods are held out from search; check only after BLS."""
    comparisons=sorted([
      (name,float(abs(period/p-1))) for name,p in targets.items()
    ],key=lambda x:x[1])
    name,error=comparisons[0]
    return {"closest_known_planet":name,
            "closest_period_error_fraction":error,
            "within_2pct_of_known_planet":bool(error<tolerance)}


def run(outdir="results/iterative_planet_search"):
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    collected=[]
    for star in STARS:
        print(f"Processing {star['name']} (KIC {star['kic']})",flush=True)
        try:
            t,f,origin=fetch_kepler_quarter(f"KIC {star['kic']}",
                                              star["quarter"])
            frames,residual=search_iteratively(t,f)
            frames["star"]=star["name"]
            frames["source_hash"]=origin["sha256"]
            for idx,peak in frames.iterrows():
                m=match_reference_period(float(peak["period_days"]),
                                         star["published_planets"])
                for k,v in m.items():frames.loc[idx,k]=v
            frames.to_csv(out/f"{star['name']}_iterations.csv",index=False)
            collected.extend(frames.to_dict(orient="records"))
            fig,axes=plt.subplots(2,1,figsize=(9,6),sharex=True)
            axes[0].plot(t,f,".",ms=1)
            axes[0].set(ylabel="Observed normalized flux",
                        title=f"{star['name']}: strongest BLS event subtraction")
            axes[1].plot(t,residual,".",ms=1)
            axes[1].set(xlabel="Time (BKJD)",
                        ylabel="Residual flux after three BLS models")
            fig.tight_layout()
            fig.savefig(out/f"{star['name']}_residual.png",dpi=150)
            plt.close(fig)
            print(frames[["iteration","period_days","score",
                          "closest_known_planet","within_2pct_of_known_planet"]].
                  to_string(index=False),flush=True)
        except Exception as exc:
            (out/f"{star['name']}_error.txt").write_text(
                f"{type(exc).__name__}: {str(exc)[:450]}\n")
            collected.append({"star":star["name"],"status":"error",
                              "error_type":type(exc).__name__,
                              "error":str(exc)[:450]})
            print("Failed:",type(exc).__name__,str(exc)[:150],flush=True)
    data=pd.DataFrame(collected)
    data.to_csv(out/"all_iterations.csv",index=False)
    status={
      "scope":"POST-HOC exploratory development, NOT independent holdout",
      "data":"Actual NASA Kepler Q8 PDCSAP observations",
      "targets":[s["name"] for s in STARS],
      "search_period_days":list(WINDOW),
      "max_iterations":MAX_COMPONENTS,
      "detector":"Astropy BLS box-model sequential residual subtraction",
      "important_limitations":[
        "Model subtraction can erase or distort real overlapping transits",
        "Periodogram peak is not calibrated as a genuine detection",
        "Additional peaks may be aliases, variability, or artifacts",
        "Known-planet matches checked only after fitting",
        "These stars were identified as failures during earlier cohort testing",
        "Performance improvement cannot be claimed on reused development stars"],
      "records":json.loads(data.to_json(orient="records"))
    }
    (out/"iterative_summary.json").write_text(json.dumps(status,indent=2))
    return status


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="results/iterative_planet_search")
    a=p.parse_args()
    run(a.out)
