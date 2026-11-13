"""Prospective *out-of-quarter* Kepler transit-ephemeris prediction.

Search Q6 with Astropy BLS using flux and time alone. Freeze fitted period,
epoch, duration and only THEN open Q7; NEVER optimize anything on Q7.
Evaluate whether Q6 transit centers forecast local Q7 brightness dips and
how strong that effect is relative to pre-specified alternative Q7 phases.

A binary also shows coherent eclipses: this is a periodic astrophysical
signal-replication check, NOT planet validation or a mission false alarm rate.
"""
# Re-execution marker, November 13 2026: use the original frozen Q6/Q7 protocol unchanged.
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from blind_transit_benchmark import bls_peak, robust_sigma
from real_kepler_lightcurve import fetch_kepler_quarter

MANIFEST = "Q6_TO_Q7_BLIND_PREDICTIVE_VALIDATION_FROZEN_2026_11_08.json"


def load_manifest(path=MANIFEST):
    x=json.loads(Path(path).read_text())
    subjects=x["published_sources"]
    if (len(subjects)!=12 or len({int(s["kic"]) for s in subjects})!=12 or
        x["training_quarter"]!=6 or x["prospective_test_quarter"]!=7):
        raise ValueError("Frozen 12-star cross-quarter source list altered")
    if sum(s["role"]=="previously_published_planet_host" for s in subjects)!=10:
        raise ValueError("Frozen planet-source stratum changed")
    if sum(s["role"]=="previously_analyzed_known_eclipsing_binary_control" for s in subjects)!=2:
        raise ValueError("Frozen binary control stratum changed")
    cfg=x["method_frozen"]
    exact={
        "bls_train_period_min_days":1.0, "bls_train_period_max_days":20.0,
        "bls_frequency_factor":0.8,
        "min_expected_transit_events_in_Q7":2,
        "min_in_transit_cadences_per_event":3,
        "min_baseline_cadences_per_event":6,
        "positive_event_depth_fraction_at_least":0.6,
        "phase_null_shift_count":1000,
        "phase_null_random_seed":2026110817
    }
    for field,value in exact.items():
        if cfg[field]!=value:raise ValueError(f"Frozen settings changed: {field}")
    if cfg["bls_durations_days"]!=[.09,.15,.24]:
        raise ValueError("BLS duration grid changed")
    return x


def forecast_events(time,flux,period,epoch,duration,
                    inner_scale=1.5,outer_scale=3.5,
                    minimum_in=3,minimum_out=6):
    """All event windows anchored only on prior-quarter period/phase.

    The two sidebands are outside the expected transit, truncated at ±0.4
    orbital cycles so the local comparison does not overlap adjacent
    predicted events; this diagnostic estimates local depths not planet sizes.
    """
    t=np.asarray(time,dtype=float);f=np.asarray(flux,dtype=float)
    if (t.ndim!=1 or f.shape!=t.shape or len(t)<500 or
        np.any(np.diff(t)<=0) or not np.isfinite(t+f).all() or
        period<=0 or duration<=0 or duration>=period/3):
        raise ValueError("Invalid observing series or period")
    outer=min(outer_scale*duration,.4*period)
    inner=inner_scale*duration
    if outer<=inner:
        return []
    first=int(np.ceil((t[0]+outer-epoch)/period))
    last=int(np.floor((t[-1]-outer-epoch)/period))
    events=[]
    for k in range(first,last+1):
        center=float(epoch+k*period)
        inside=np.abs(t-center)<=duration/2
        distant=np.abs(t-center)
        side=(distant>=inner)&(distant<=outer)
        if inside.sum()<minimum_in or side.sum()<minimum_out:
            continue
        depth=float(np.median(f[side])-np.median(f[inside]))
        events.append({
            "orbit_index":int(k),
            "predicted_epoch_bkjd":center,
            "in_transit_cadences":int(inside.sum()),
            "nearby_baseline_cadences":int(side.sum()),
            "local_depth_fraction":depth,
            "positive_local_depth":bool(depth>0),
        })
    return events


def phase_shift_null(time,flux,period,epoch,duration,settings,star_key):
    """One Q7 time series, fixed BLS ephemeris, alternate random trial phases.

    These phase-shift fractions compare *phases within one star* and are NOT
    independently calibrated Kepler mission false-alarm probabilities.
    """
    m=forecast_events(
        time,flux,period,epoch,duration,
        inner_scale=settings["baseline_inner_window_duration_multipliers"],
        outer_scale=settings["baseline_outer_window_duration_multipliers"],
        minimum_in=settings["min_in_transit_cadences_per_event"],
        minimum_out=settings["min_baseline_cadences_per_event"])
    count=len(m)
    result={
        "n_usable_predicted_events_q7":count,
        "mean_predicted_event_depth":float(np.mean([e["local_depth_fraction"] for e in m])) if m else None,
        "median_predicted_event_depth":float(np.median([e["local_depth_fraction"] for e in m])) if m else None,
        "positive_event_fraction":float(np.mean([e["positive_local_depth"] for e in m])) if m else None,
        "relative_phase_shift_fraction":None,
        "phase_shift_null_trials":0,
        "predictive_evidence":False
    }
    if count<settings["min_expected_transit_events_in_Q7"]:
        return result,m,[]
    observed=result["mean_predicted_event_depth"]
    rng=np.random.default_rng(settings["phase_null_random_seed"]+int(star_key))
    requested=settings["phase_null_shift_count"]
    sampled=[]
    # Phase shifts cannot be within 2 event durations of the Q6 phase
    # estimate; otherwise we would call the same transit its own null.
    # This exclusion means the resulting p-value is NOT a sky-wide FAP.
    attempts=0
    while len(sampled)<requested and attempts<20*requested:
        attempts+=1
        shift=float(rng.uniform(0,period))
        if min(shift,period-shift)<=min(2*duration,.22*period):
            continue
        events=forecast_events(
            time,flux,period,epoch+shift,duration,
            inner_scale=settings["baseline_inner_window_duration_multipliers"],
            outer_scale=settings["baseline_outer_window_duration_multipliers"],
            minimum_in=settings["min_in_transit_cadences_per_event"],
            minimum_out=settings["min_baseline_cadences_per_event"])
        if len(events)<settings["min_expected_transit_events_in_Q7"]:
            continue
        sampled.append({
            "offset_days":shift,
            "number_events":len(events),
            "mean_local_depth":float(np.mean([e["local_depth_fraction"] for e in events])),
        })
    if len(sampled)<requested:
        # Do not misrepresent a sparse or short-period source as significant.
        return result,m,sampled
    sample=np.array([x["mean_local_depth"] for x in sampled],dtype=float)
    result["relative_phase_shift_fraction"]=float(
        (1+np.count_nonzero(sample>=observed))/(1+len(sample)))
    result["phase_shift_null_trials"]=len(sample)
    result["predictive_evidence"]=bool(
        result["relative_phase_shift_fraction"]<=.01
        and result["positive_event_fraction"]>=settings["positive_event_depth_fraction_at_least"])
    return result,m,sampled


def source_evaluation(source,settings):
    """Open Q7 only AFTER ALL Q6 BLS parameters are fixed."""
    kic=int(source["kic"])
    t6,f6,raw6=fetch_kepler_quarter(f"KIC {kic}",6)
    peak=bls_peak(t6,f6,
                  bounds=(settings["bls_train_period_min_days"],
                          settings["bls_train_period_max_days"]),
                  frequency_factor=settings["bls_frequency_factor"])
    # Source type and literature periods never affect the above search.
    # This is an explicit read barrier: Q7 data must not influence Q6 peak.
    t7,f7,raw7=fetch_kepler_quarter(f"KIC {kic}",7)
    measures,events,null=phase_shift_null(
        t7,f7,peak["period_days"],peak["transit_time_days"],
        peak["duration_days"],settings,kic)
    row={
        "kic":kic,"source_name":source["name"],
        "literature_role":source["role"],
        "status":"both_original_FITS_analyzed",
        "q6_original_FITS_SHA256":raw6["sha256"],
        "q7_original_FITS_SHA256":raw7["sha256"],
        "q6_original_file":raw6["file"],"q7_original_file":raw7["file"],
        "q6_n_original_quality_zero_cadences":len(t6),
        "q7_n_original_quality_zero_cadences":len(t7),
        "q6_train_best_period_days":peak["period_days"],
        "q6_train_best_epoch_bkjd":peak["transit_time_days"],
        "q6_train_best_duration_days":peak["duration_days"],
        "q6_BLS_score_uncalibrated":peak["score"],
        "q6_BLS_depth_ppm_uncalibrated":peak["depth_ppm"],
        "q7_noise_proxy_fraction":robust_sigma(f7),
        **measures
    }
    for r in events:
        r.update({"kic":kic,"source_name":source["name"],
                  "literature_role":source["role"]})
    for r in null:
        r.update({"kic":kic,"source_name":source["name"],
                  "literature_role":source["role"]})
    return row,events,null,(t6,f6),(t7,f7),peak


def summary(rows):
    planet=[r for r in rows if r["literature_role"]=="previously_published_planet_host"]
    control=[r for r in rows if r["literature_role"]=="previously_analyzed_known_eclipsing_binary_control"]
    def counts(group):
        analyzed=[r for r in group if r["status"]=="both_original_FITS_analyzed"]
        return {"planned":len(group),"analyzed_both_quarters":len(analyzed),
                "unavailable_or_errors":len(group)-len(analyzed),
                "with_2plus_valid_Q7_event_windows":sum(int(r["n_usable_predicted_events_q7"]>=2) for r in analyzed),
                "positive_predicted_dip_evidence":sum(int(r["predictive_evidence"]) for r in analyzed),
                "not_predictive_including_failures":len(group)-sum(int(r["predictive_evidence"]) for r in analyzed)}
    return {
      "scope":"Q6 BLS physically predicts Q7, WITHOUT using Q7 to choose periods or phases; known planet hosts NOT fresh planet discoveries",
      "new_published_planet_host_stratum":counts(planet),
      "previously_examined_binary_controls":counts(control),
      "interpretation":"Q7 predictive evidence establishes repeatable dimming at a Q6-selected phase, not whether the source is a planetary transit rather than a stellar eclipse. Phase-shift p is not a survey FAP; no statistical population effect claimed.",
      "guardrails":[
        "Reported planet hosts can have strongest Q6 BLS signals unrelated to listed planets.",
        "Even low Q7 phase-shift fractions do not distinguish an eclipsing binary from a planet.",
        "True NASA mission reliability needs independent injected pixels, vetted TCE controls, and centroid/off-target tests.",
        "Preselected known hosts do not measure new planet discoveries or blind all-star completeness.",
        "Phase tests and transit events within one star are correlated; count hosts, not 1000 phase shifts, for population inference.",
        "Single-quarter Q6 period errors and TTV may cause forecast failure despite genuine planets.",
      ]
    }


def run(outdir="results/out_of_quarter_validation",manifest=MANIFEST):
    cfg=load_manifest(manifest)
    options=cfg["method_frozen"]
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    (out/"frozen_input_manifest.json").write_bytes(Path(manifest).read_bytes())
    observations=[];all_events=[];all_null=[]
    for source in cfg["published_sources"]:
        print(f"New Q6-Q7 source: {source['name']} KIC={source['kic']}",flush=True)
        try:
            record,events,null,first,second,peak=source_evaluation(source,options)
            observations.append(record)
            all_events.extend(events);all_null.extend(null)
            print(f"  Q6 period {peak['period_days']:.5f}d; Q7 {record['n_usable_predicted_events_q7']} event windows; Q7 phase fraction {record['relative_phase_shift_fraction']}, predictive={record['predictive_evidence']}",flush=True)
            if cfg["published_sources"].index(source) < 3:
                import matplotlib
                matplotlib.use("Agg")
                import matplotlib.pyplot as plt
                t6,f6=first;t7,f7=second
                p=peak["period_days"]; t0=peak["transit_time_days"]
                phase6=(t6-t0+p/2)%p-p/2
                phase7=(t7-t0+p/2)%p-p/2
                fig,axs=plt.subplots(2,1,figsize=(10,7),sharex=True)
                axs[0].plot(phase6,f6,".",ms=1.5,label="Training Q6")
                axs[1].plot(phase7,f7,".",ms=1.5,label="Untouched time-holdout Q7")
                for ax in axs:
                    ax.axvline(0,ls="--",color="black")
                    ax.set(xlim=(-.60,.60),ylabel="Normalized NASA PDCSAP flux")
                    ax.legend(loc="lower left")
                axs[1].set(xlabel="Phase relative to Q6-fitted predicted transit (days)")
                fig.suptitle(f"{source['name']}: predicted period {p:.5f} d (Q7 never fitted)")
                fig.tight_layout()
                fig.savefig(out/f"KIC{source['kic']}_Q6_to_Q7_phase.png",dpi=170)
                plt.close(fig)
        except Exception as e:
            observations.append({
                "kic":int(source["kic"]),"source_name":source["name"],
                "literature_role":source["role"],"status":"source_or_analysis_error",
                "exception_class":type(e).__name__,"error":str(e)[:500]
            })
            print(f"  Unavailable/error: {type(e).__name__}: {str(e)[:190]}",flush=True)
    pd.DataFrame(observations).to_csv(out/"all_12_prespecified_sources.csv",index=False)
    pd.DataFrame(all_events).to_csv(out/"q7_individual_predicted_event_depths.csv",index=False)
    pd.DataFrame(all_null).to_csv(out/"q7_phase_shift_nulls.csv",index=False)
    result=summary(observations)
    (out/"q6_to_q7_summary.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2),flush=True)
    if result["new_published_planet_host_stratum"]["analyzed_both_quarters"]==0:
        raise RuntimeError("No prospectively new planet hosts available; see failure table")
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="results/out_of_quarter_validation")
    p.add_argument("--manifest",default=MANIFEST)
    a=p.parse_args()
    run(a.out,a.manifest)
