#!/usr/bin/env python3
"""EXPLORATORY post-failure diagnosis, not a frozen new holdout.

Compare the original Q8-only period and NASA's published period using the SAME
fitted Q8 epoch and transit duration, without looking for a better Q9-Q13 phase.
"""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from real_kepler_lightcurve import fetch_kepler_quarter
from blind_transit_benchmark import bls_peak
from q6_to_q7_blind_ephemeris_validation import forecast_events

NASA_PERIOD_DAYS = 13.7223682


def run(out="results/kepler69b_post_failure_diagnosis"):
    outdir=Path(out)
    outdir.mkdir(parents=True,exist_ok=True)
    t8,f8,source8=fetch_kepler_quarter("KIC 8692861",8)
    fit=bls_peak(t8,f8,bounds=(1.5,20.),frequency_factor=5.)
    period=fit["period_days"]
    if abs(period-13.7133429855)>.02:
        raise ValueError("Q8 fit changed from prior published project version")
    t0=fit["transit_time_days"]
    duration=fit["duration_days"]
    all_rows=[];event_rows=[]
    for quarter in (9,10,11,12,13):
        t,f,source=fetch_kepler_quarter("KIC 8692861",quarter)
        for model,p in (("Q8-only",period),("NASA-period-with-same-Q8-epoch",NASA_PERIOD_DAYS)):
            events=forecast_events(t,f,p,t0,duration,
                    inner_scale=1.5,outer_scale=3.5,
                    minimum_in=3,minimum_out=6)
            depths=np.array([e["local_depth_fraction"] for e in events],float)
            row={
                "quarter":quarter,"period_model":model,"period_days":p,
                "Q8_fitted_start_epoch_bkjd":t0,"duration_days":duration,
                "n_usable_fixed_predicted_windows":len(events),
                "positive_windows":int(np.count_nonzero(depths>0)),
                "mean_fixed_window_depth_ppm":float(depths.mean()*1e6) if len(depths) else None,
                "median_orbit_index":float(np.median([e["orbit_index"] for e in events])) if events else None,
                "SHA256_original_NASA_FITS":source["sha256"]
            }
            all_rows.append(row)
            print(json.dumps(row),flush=True)
            event_rows.extend({"quarter":quarter,"model":model,**e} for e in events)
    pd.DataFrame(all_rows).to_csv(outdir/"fixed_window_compared_periods.csv",index=False)
    pd.DataFrame(event_rows).to_csv(outdir/"fixed_window_event_details.csv",index=False)
    summary={
        "type":"Post-hoc explanatory comparison after original Q12-Q13 failures; NOT a new blind test",
        "train_q8_bls":fit,"NASA_published_period_days":NASA_PERIOD_DAYS,
        "same_fitted_Q8_epoch_all_models":t0,
        "same_duration_all_models":duration,
        "results":all_rows,
        "limitations":"The NASA period was known before the study and chosen for a post-failure explanation. One known planet host, Q8 epoch held fixed, no later data tuned, no independent inference of physical planet origin."
    }
    (outdir/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    df=pd.DataFrame(all_rows)
    fig,ax=plt.subplots(figsize=(8.5,4.8))
    for label,group in df.groupby("period_model"):
        ax.plot(group["quarter"],group["mean_fixed_window_depth_ppm"],"o-",label=label)
    ax.axhline(0,color="black",lw=.7)
    ax.set(xlabel="Later Kepler observing quarter",ylabel="Average brightness dip in fixed windows (ppm)",xticks=[9,10,11,12,13])
    ax.legend()
    ax.set_title("One starting transit, two fixed periods: later observations")
    fig.tight_layout()
    fig.savefig(outdir/"fixed_period_comparison.png",dpi=180)
    plt.close(fig)
    print("POSTHOC_FIXED_PERIOD_COMPARISON_START")
    print(json.dumps(summary,indent=2))
    print("POSTHOC_FIXED_PERIOD_COMPARISON_END")
    return summary

if __name__=="__main__":
    run()
