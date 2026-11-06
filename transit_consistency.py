"""Exploratory per-event consistency checks for BLS transit candidates.

Inspired by established transit vetting (e.g., Robnik et al., MNRAS 2026).
These heuristic flags do not establish a planet or provide a calibrated FAP.
"""
import numpy as np
import pandas as pd


def individual_transit_checks(time,flux,period,epoch,duration,sigma=None):
    """Characterize successive dimming events at an independently fitted period.

    The local out-of-transit comparison uses 1.5–4 event durations.
    Missing or insufficiently sampled events are omitted, not marked as passes.
    """
    t=np.asarray(time,dtype=float);y=np.asarray(flux,dtype=float)
    if len(t)!=len(y) or not np.all(np.isfinite(t+y)):
        raise ValueError("Time and brightness arrays must have matching finite values")
    if not(np.isfinite(period) and np.isfinite(epoch) and np.isfinite(duration)):
        raise ValueError("Nonfinite ephemeris")
    if period<=0 or duration<=0 or duration>=period/3:
        raise ValueError("Implausible ephemeris or duration")
    if len(t)<20:
        raise ValueError("Too few points")
    if sigma is None:
        from blind_transit_benchmark import robust_sigma
        sigma=robust_sigma(y)
    sigma=float(sigma)
    if sigma<=0:
        raise ValueError("Invalid scatter estimate")
    events=[]
    kmin=int(np.floor((t.min()-epoch)/period))-1
    kmax=int(np.ceil((t.max()-epoch)/period))+1
    for number in range(kmin,kmax+1):
        center=float(epoch+number*period)
        dt=np.abs(t-center)
        mask_in=dt<duration/2
        mask_out=(dt>1.5*duration)&(dt<4*duration)
        nin=int(mask_in.sum());nout=int(mask_out.sum())
        if nin<3 or nout<6:
            continue
        depth=float(np.median(y[mask_out])-np.median(y[mask_in]))
        error=sigma*np.sqrt(1/nin+1/nout)
        events.append({"event":number,"center_day":center,"depth_ppm":depth*1e6,
                       "snr":depth/error,"n_in":nin,"n_out":nout})
    table=pd.DataFrame(events,columns=[
        "event","center_day","depth_ppm","snr","n_in","n_out"])
    if table.empty:
        return {"n_observable_events":0,"positive_depth_fraction":None,
                "dominance":None,"odd_even_depth_difference_ppm":None,
                "warning":"No adequately sampled individual events"},table
    positive_scores=np.maximum(table.snr.to_numpy(),0)**2
    dominance=(float(positive_scores.max()/positive_scores.sum())
               if positive_scores.sum()>0 else None)
    odd=table.loc[table.event%2==1,"depth_ppm"].to_numpy()
    even=table.loc[table.event%2==0,"depth_ppm"].to_numpy()
    odd_even=(float(np.median(odd)-np.median(even))
              if len(odd)>=2 and len(even)>=2 else None)
    fraction=float((table.depth_ppm>0).mean())
    warnings=[]
    if len(table)<3:
        warnings.append("fewer than three sampled transit events")
    if dominance is not None and dominance>.6:
        warnings.append("one event dominates positive-depth evidence")
    if fraction<.6:
        warnings.append("individual dips disagree with common transit template")
    return {"n_observable_events":int(len(table)),
            "positive_depth_fraction":fraction,
            "dominance":dominance,
            "odd_even_depth_difference_ppm":odd_even,
            "warning":"; ".join(warnings) if warnings else
            "No heuristic warning; this does NOT confirm a planet"},table


def inspect_from_bls(time,flux):
    """Fit period and epoch independently with blind BLS, then inspect events."""
    from blind_transit_benchmark import bls_peak
    peak=bls_peak(time,flux)
    result,table=individual_transit_checks(
        time,flux,peak["period_days"],peak["transit_time_days"],
        peak["duration_days"])
    return peak,result,table
