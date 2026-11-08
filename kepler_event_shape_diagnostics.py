"""Interpretable event-level light-curve morphology, a proposed ExoMiner *companion* diagnostic.

This module does NOT load, reproduce, modify, or outperform official NASA ExoMiner.
It adds physical checks to an existing Kepler candidate ephemeris:
(1) post-event baseline recovery versus a persistent detector step;
(2) odd-even eclipse depth differences, sensitive to common P/2 aliases.

No classification threshold is fitted here, no labels enter feature extraction,
and neither a recurring dip nor a small step is in itself proof of a planet.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from exominer_inspired_kepler_views import validate_light_curve
from blind_transit_benchmark import bls_peak
from real_kepler_lightcurve import fetch_kepler_quarter


def median_abs_noise(values):
    """Robust scatter estimator, with a small strictly numerical floor."""
    x=np.asarray(values,dtype=float)
    if x.size<3:
        return 0.0
    return float(1.4826*np.median(np.abs(x-np.median(x))))


def event_shape_measurements(time,flux,period,epoch,duration,
                             inner_offset=1.5,outer_offset=3.5,
                             min_inside=3,min_each_side=6):
    """Measure LOCAL original flux geometry at prespecified ephemeris, with gaps.

    The event center is strictly an upstream period/epoch. We never optimize
    its timing against the evaluation segment or consult source labels.
    A valid event needs observed cadences *on both sides*; no synthetic
    interpolated flux is counted as an observed datum.
    """
    t,f=validate_light_curve(time,flux,period,epoch,duration)
    outer=min(outer_offset*duration,.44*period)
    inner=inner_offset*duration
    if outer<=inner or min_inside<2 or min_each_side<2:
        raise ValueError("Invalid sideband geometry")
    first=int(np.ceil((t[0]+outer-epoch)/period))
    last=int(np.floor((t[-1]-outer-epoch)/period))
    records=[]
    for k in range(first,last+1):
        center=float(epoch+k*period)
        delta=t-center
        inside=np.abs(delta)<=.5*duration
        before=(delta>=-outer)&(delta<=-inner)
        after=(delta>=inner)&(delta<=outer)
        n_inside=int(inside.sum())
        n_before=int(before.sum())
        n_after=int(after.sum())
        if (n_inside<min_inside or n_before<min_each_side or
            n_after<min_each_side):
            continue
        pre=float(np.median(f[before]))
        post=float(np.median(f[after]))
        center_flux=float(np.median(f[inside]))
        baseline=.5*(pre+post)
        signed_depth=baseline-center_flux
        step=post-pre
        # The local noise estimator is based ONLY on the observed sidebands.
        # It is not an independent astrophysical false-alarm calibration.
        scatter=median_abs_noise(np.r_[f[before],f[after]])
        records.append({
            "orbit_index":int(k),"parity":("odd" if k%2 else "even"),
            "predicted_epoch_bkjd":center,
            "n_in_transit":n_inside,"n_before":n_before,"n_after":n_after,
            "median_pre_flux":pre,"median_during_flux":center_flux,
            "median_post_flux":post,
            "signed_local_depth_fraction":float(signed_depth),
            "post_minus_pre_fraction":float(step),
            "absolute_post_pre_step_fraction":float(abs(step)),
            "local_baseline_MAD_noise_fraction":scatter,
            "persistent_step_over_depth_plus_noise":float(
                abs(step)/(abs(signed_depth)+max(scatter,1e-12))),
            "measured_positive_depth":bool(signed_depth>0)
        })
    return records


def summarize_shape_events(records,bootstrap_repeats=1500,bootstrap_seed=12600):
    """Use independent EVENT units, not individual cadences or phase shifts.

    Odd/even bootstrap is descriptive within one host; no survey-wide p value
    or NASA model gain can be inferred. Never infer a planet from this result.
    """
    if not records:
        return {
            "usable_event_count":0,"odd_event_count":0,"even_event_count":0,
            "median_signed_local_depth_fraction":None,
            "median_abs_persistent_step_fraction":None,
            "median_persistent_step_over_depth_plus_noise":None,
            "median_odd_even_depth_difference_fraction":None,
            "odd_even_descriptive_bootstrap_95pct_interval":None,
            "odd_even_descriptive_separates_zero":None,
            "scope":"No usable original-measurement event windows; do not invent observations"
        }
    odd=np.array([r["signed_local_depth_fraction"] for r in records
                  if r["parity"]=="odd"],dtype=float)
    even=np.array([r["signed_local_depth_fraction"] for r in records
                   if r["parity"]=="even"],dtype=float)
    depth=np.array([r["signed_local_depth_fraction"] for r in records])
    step=np.array([r["absolute_post_pre_step_fraction"] for r in records])
    ratio=np.array([r["persistent_step_over_depth_plus_noise"] for r in records])
    result={
        "usable_event_count":len(records),
        "odd_event_count":len(odd),"even_event_count":len(even),
        "median_signed_local_depth_fraction":float(np.median(depth)),
        "positive_depth_event_fraction":float(np.mean(depth>0)),
        "median_abs_persistent_step_fraction":float(np.median(step)),
        "median_persistent_step_over_depth_plus_noise":float(np.median(ratio)),
        "median_odd_even_depth_difference_fraction":None,
        "odd_even_descriptive_bootstrap_95pct_interval":None,
        "odd_even_descriptive_separates_zero":None,
        "scope":"Descriptive local morphology only; no planet validation, independent sky FAP, or NASA-ExoMiner improvement"
    }
    # Minimum three independent observed epochs of *each parity*; otherwise
    # the odd/even difference is an anecdote, not an event-level interval.
    if len(odd)>=3 and len(even)>=3:
        difference=float(np.median(odd)-np.median(even))
        rng=np.random.default_rng(bootstrap_seed)
        # Events, NOT flux cadences, are bootstrap resampling units.
        ob=rng.choice(odd,size=(bootstrap_repeats,len(odd)),replace=True)
        eb=rng.choice(even,size=(bootstrap_repeats,len(even)),replace=True)
        diffs=np.median(ob,axis=1)-np.median(eb,axis=1)
        lower,upper=(float(x) for x in np.quantile(diffs,[.025,.975]))
        result.update({
            "median_odd_even_depth_difference_fraction":difference,
            "odd_even_descriptive_bootstrap_95pct_interval":[lower,upper],
            "odd_even_descriptive_separates_zero":bool(lower>0 or upper<0),
            "odd_even_caveat":"Resample individual observed events within this star; this is not a population CI or a new independent detection."
        })
    return result


def summarize_one(time,flux,period,epoch,duration):
    events=event_shape_measurements(time,flux,period,epoch,duration)
    return summarize_shape_events(events),events


def run_real_kepler_demonstration(out_dir="results/real_kepler_event_shape_diagnostics",
                                  quarter=6):
    """Use previously known published stars for explanation, NOT independent accuracy."""
    if quarter not in (6,7):
        raise ValueError("Source-only demo restricted to Kepler Q6/Q7")
    dest=Path(out_dir)
    dest.mkdir(parents=True,exist_ok=True)
    sources=[
        (11804465,"Kepler-12","published_known_planet_host"),
        (9837578,"Kepler-35","published_known_stellar_eclipsing_binary")
    ]
    results=[]
    for kic,name,role in sources:
        t,flux,provenance=fetch_kepler_quarter(f"KIC {kic}",quarter)
        # Critically: period/epoch/duration from flux-only blind BLS, not
        # from the published physical label or comparison sources.
        peak=bls_peak(t,flux,bounds=(1.5,20.),frequency_factor=1.5)
        result,events=summarize_one(
            t,flux,peak["period_days"],peak["transit_time_days"],
            peak["duration_days"])
        base=f"KIC{kic}_Q{quarter}"
        pd.DataFrame(events).to_csv(dest/f"{base}_observed_event_morphology.csv",index=False)
        results.append({
            "kic":kic,"source_name":name,"published_role_for_interpretation_only":role,
            "quarter":quarter,
            "source_original_fits_filename":provenance["file"],
            "source_original_FITS_SHA256":provenance["sha256"],
            "n_quality_filtered_original_cadences":len(t),
            "upstream_Q_only_BLS":peak,
            "event_shape":result,
            "events_table":f"{base}_observed_event_morphology.csv"
        })
        print(json.dumps({
            "source":name,"quarter":quarter,
            "blind_fitted_period_days":peak["period_days"],
            "observed_events":result["usable_event_count"],
            "event_median_depth":result["median_signed_local_depth_fraction"],
            "odd_even_difference":result["median_odd_even_depth_difference_fraction"],
            "odd_even_interval":result["odd_even_descriptive_bootstrap_95pct_interval"],
            "median_step_over_local_depth_plus_noise":
                result["median_persistent_step_over_depth_plus_noise"]
        },indent=2),flush=True)
    report={
        "experiment":"Real MAST Kepler event morphology with frozen BLS-like upstream search; exploratory *known-system* check, no NASA model inference",
        "stellar_sample_is_preselected_and_previously_examined":True,
        "no_automatic_planet_or_star_label":True,
        "not_a_validation_of_proposed_exominer_model_gain":True,
        "source_results":results,
        "scientific_limitations":[
            "Odd/even and secondary diagnostics already exist in official ExoMiner. No novelty claim for restating them.",
            "Single-quarter event-bootstrap intervals only represent timing window variability within each example star.",
            "Detrending 301-cadence rolling median can suppress longer transits and introduce shape artifacts.",
            "Need actual instrument quality or injected step truth, full official model, and separate preregistered holdout for any performance claims."
        ]
    }
    (dest/f"real_source_event_shape_summary_Q{quarter}.json").write_text(
        json.dumps(report,indent=2)+"\n")
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default="results/real_kepler_event_shape_diagnostics")
    parser.add_argument("--quarter",type=int,default=6)
    a=parser.parse_args()
    run_real_kepler_demonstration(a.out,a.quarter)
