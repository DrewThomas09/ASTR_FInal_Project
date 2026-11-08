"""Kepler light-curve views *inspired by* ExoMiner diagnostic inputs.

NOT a NASA ExoMiner or ExoMiner++ model. The tensor shapes resemble
published ones (global 301, local 31, unfolded 20x31), but the precise
normalization, scalar features, pixel images, mission and preprocessing
do NOT match the pretrained NASA TESS model. Never feed this output to
that model or describe it as a replication of ExoMiner's predictions.

Physical purpose: make individual transit / odd-even / secondary eclipse
structure inspectable in the existing ASTR Kepler project and produce
a reusable testable precursor to a genuinely matched NASA replication.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np

from blind_transit_benchmark import bls_peak
from real_kepler_lightcurve import fetch_kepler_quarter

VIEW_SIZES={
    "prototype_global_flux": (301,1),
    "prototype_local_flux":(31,1),
    "prototype_local_odd_flux":(31,1),
    "prototype_local_even_flux":(31,1),
    "prototype_secondary_flux":(31,1),
    "prototype_unfolded_20_by_31":(20,31),
}
# These shapes are compatible in SIZE with some NASA model views, not
# compatible in preprocessing/normalization/model semantics.


def validate_light_curve(time,normalized_flux,period,epoch,duration):
    t=np.asarray(time,dtype=float)
    f=np.asarray(normalized_flux,dtype=float)
    if t.ndim!=1 or f.shape!=t.shape or len(t)<500:
        raise ValueError("Require at least 500 aligned Kepler cadences")
    if (not np.isfinite(t).all() or not np.isfinite(f).all()
        or np.any(np.diff(t)<=0) or np.any(f<=0)):
        raise ValueError("Flux must be finite, positive and time ascending")
    if (not all(np.isfinite(z) for z in [period,epoch,duration])
        or period<=0 or duration<=0 or duration>=period/3):
        raise ValueError("Invalid frozen transit ephemeris or duration")
    return t,f


def normalized_phase(time,period,epoch):
    """Phase relative to the frozen transit center, in days."""
    t=np.asarray(time,dtype=float)
    return (t-epoch+.5*period)%period-.5*period


def binned_median(phase,flux,bins,window):
    """Neutral pad empty bins but ALWAYS return a separate occupancy mask.

    The empty-bin mask is scientifically necessary: neutral padding is not
    evidence of a real out-of-transit brightness measurement.
    """
    x=np.asarray(phase,dtype=float)
    y=np.asarray(flux,dtype=float)
    if (x.ndim!=1 or y.shape!=x.shape or not np.isfinite(x+y).all()
        or bins<=2 or window<=0):
        raise ValueError("Invalid data or bin design")
    edges=np.linspace(-window,window,bins+1)
    index=np.searchsorted(edges,x,side="right")-1
    valid=(index>=0)&(index<bins)
    values=np.ones(bins,dtype=np.float32)
    counts=np.bincount(index[valid],minlength=bins)
    for i in np.flatnonzero(counts):
        values[i]=np.float32(np.median(y[valid & (index==i)]))
    observed=(counts>0)
    if len(values)!=bins or len(observed)!=bins:
        raise AssertionError("Unexpected shape")
    return values,observed.astype(bool)


def individual_event_views(time,flux,period,epoch,duration,
                           n_stack=20,local_bins=31,half_width_scale=2.5):
    """Chronological local views per independently observed predicted epoch.

    Use only ephemeris supplied by the upstream detection step. Do NOT look
    up published planet periods or infer truth of any local event. Missing
    repeated events produce explicit False valid masks in padded rows.
    """
    t,f=validate_light_curve(time,flux,period,epoch,duration)
    half_width=min(half_width_scale*duration,0.45*period)
    first=int(np.ceil((t[0]+half_width-epoch)/period))
    last=int(np.floor((t[-1]-half_width-epoch)/period))
    events=[]
    for k in range(first,last+1):
        center=epoch+k*period
        near=(t>=center-half_width)&(t<=center+half_width)
        inside=(np.abs(t-center)<=duration/2)
        if near.sum()<8 or np.sum(inside)<3:
            continue
        array,valid=binned_median(t[near]-center,f[near],local_bins,half_width)
        events.append({
            "orbit_number":int(k),
            "predicted_epoch_bkjd":float(center),
            "n_observed_cadences":int(near.sum()),
            "n_transit_window_cadences":int(inside.sum()),
            "flux":array,
            "observed_bin_mask":valid,
        })
    # Sample evenly spaced chronological events to avoid preferentially
    # selecting only the deepest / apparently most planet-like events.
    choose=np.arange(len(events))
    if len(events)>n_stack:
        choose=np.rint(np.linspace(0,len(events)-1,n_stack)).astype(int)
    selected=[events[int(i)] for i in choose]
    values=np.ones((n_stack,local_bins),dtype=np.float32)
    mask=np.zeros((n_stack,local_bins),dtype=bool)
    epoch_ids=np.full(n_stack,np.nan,dtype=float)
    for i,ev in enumerate(selected):
        values[i]=ev["flux"]
        mask[i]=ev["observed_bin_mask"]
        epoch_ids[i]=ev["predicted_epoch_bkjd"]
    return values,mask,epoch_ids,events


def build_prototype_views(time,flux,period,epoch,duration):
    """Build all source-only flux views with masks, without NASA proprietary DV.

    Published reference values, NASA physical labels, pixel contamination
    measurements, and even source identity are never used in this function.
    """
    t,f=validate_light_curve(time,flux,period,epoch,duration)
    phase=normalized_phase(t,period,epoch)
    window=min(2.5*duration,.45*period)
    outputs={}
    metadata={}
    def add(name,ph,observed_flux,bins,halfwidth):
        values,mask=binned_median(ph,observed_flux,bins,halfwidth)
        outputs[name]=values[:,None]
        outputs[name+"_observed"]=mask[:,None]
        metadata[name+"_occupied_bins"]=int(mask.sum())

    add("prototype_global_flux",phase,f,301,period/2)
    add("prototype_local_flux",phase,f,31,window)
    # Odd and even are distinct observed transit ORBITS, not alternating
    # adjacent cadences; otherwise the diagnostic would be meaningless.
    orbit=np.rint((t-epoch)/period).astype(np.int64)
    for label,parity in [("odd",1),("even",0)]:
        where=((orbit%2)==parity)&(np.abs(phase)<=window)
        add("prototype_local_"+label+"_flux",phase[where],f[where],31,window)

    secondary_phase=normalized_phase(t,period,epoch+period/2)
    add("prototype_secondary_flux",secondary_phase,f,31,window)
    matrix,valid,epochs,all_events=individual_event_views(
        t,f,period,epoch,duration)
    outputs["prototype_unfolded_20_by_31"]=matrix
    outputs["prototype_unfolded_20_by_31_observed"]=valid
    outputs["prototype_unfolded_epochs_bkjd"]=epochs
    metadata.update({
        "source":"Original Kepler quality-masked normalized observed flux",
        "n_observed_cadences":len(t),
        "period_days_from_search":float(period),
        "epoch_bkjd_from_search":float(epoch),
        "duration_days_from_search":float(duration),
        "n_usable_individual_events":len(all_events),
        "n_events_in_20_row_stack":min(len(all_events),20),
        "n_padded_empty_events":max(20-len(all_events),0),
        "not_nasa_model_input":"This is a self-built prototype using similar shapes; no exact NASA normalization, pixel images, DV diagnostics or TESS sector provenance. Not accepted by pretrained ExoMiner++.",
        "no_planet_claim":"Recurring stellar binary eclipses and other astrophysical/systematic patterns can produce the same views."
    })
    for k,shape in VIEW_SIZES.items():
        if outputs[k].shape!=shape:
            raise AssertionError(f"Unexpected shape {k}: {outputs[k].shape}, wanted {shape}")
    return outputs,metadata


def write_demo(kic,quarter,out_dir):
    t,f,source=fetch_kepler_quarter(f"KIC {int(kic)}",quarter)
    # Preexisting BLS is the upstream candidate proposal generator.
    # Do not pass catalog/planet label, source identity, orbital truth to BLS.
    found=bls_peak(t,f,bounds=(1.5,20.),frequency_factor=1.5)
    views,meta=build_prototype_views(
        t,f,found["period_days"],found["transit_time_days"],found["duration_days"])
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    name=f"KIC{int(kic)}_Q{int(quarter)}"
    np.savez_compressed(out/f"{name}_prototype_views_with_masks.npz",**views)
    report={
        "scope":"Engineering demonstration of approximate ExoMiner-like physical flux views; not trained ExoMiner, not NASA-compatible arrays and no planet confirmation",
        "star_kic":int(kic),"quarter":int(quarter),
        "official_original_FITS":source["file"],
        "original_FITS_sha256":source["sha256"],
        "blind_q6_bls":found,
        "metadata":meta,
        "arrays":{k:list(v.shape) for k,v in views.items()}
    }
    (out/f"{name}_prototype_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(3,1,figsize=(9,8))
    ax[0].plot(np.arange(301),views["prototype_global_flux"][:,0],"o-",markersize=2)
    ax[0].set(xlabel="Phase bin (301, full orbit)",
              ylabel="Normalized flux",
              title=f"KIC {kic}: full orbital view, candidate period {found['period_days']:.4f}d")
    for key,label in [("prototype_local_flux","All transits"),
                      ("prototype_local_odd_flux","Odd transits"),
                      ("prototype_local_even_flux","Even transits"),
                      ("prototype_secondary_flux","Secondary phase")]:
        ax[1].plot(np.linspace(-2.5,2.5,31),
                   views[key][:,0],marker=".",label=label)
    ax[1].set(xlabel="Offset (transit durations)",
              ylabel="Normalized flux",title="Local, odd/even and secondary views")
    ax[1].legend(fontsize=8)
    image=views["prototype_unfolded_20_by_31"].copy()
    missing=~views["prototype_unfolded_20_by_31_observed"]
    ax[2].imshow(np.ma.array(image,mask=missing),
                 aspect="auto",interpolation="nearest",origin="lower")
    ax[2].set(xlabel="Local transit bin (31)",
              ylabel="Selected event row (up to 20)",
              title="Unfolded per-event view (unobserved cells explicitly masked)")
    fig.tight_layout()
    fig.savefig(out/f"{name}_prototype_views.png",dpi=160)
    plt.close(fig)
    print(json.dumps({
        "name":name,"original_fits_sha256":source["sha256"],
        "fitted_period_days":found["period_days"],
        "usable_events":meta["n_usable_individual_events"],
        "main_shapes":{k:list(views[k].shape) for k in VIEW_SIZES},
        "claim":"Input representation ONLY, not an ExoMiner inference or improved detector"
    },indent=2),flush=True)
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--kic",type=int,default=11804465)
    p.add_argument("--quarter",type=int,default=6)
    p.add_argument("--out",default="results/exominer_inspired_kepler_views")
    a=p.parse_args()
    write_demo(a.kic,a.quarter,a.out)


if __name__=="__main__":
    main()
