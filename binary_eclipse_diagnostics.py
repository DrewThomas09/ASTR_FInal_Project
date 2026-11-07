"""Physically motivated checks for eclipsing-binary-like transit impostors.

These are heuristic diagnostics, NOT a validated binary classifier or planet
confirmation. At half the binary orbit, alternating primary/secondary eclipses
can cause unequal odd/even transit depths. At the full orbital period a
secondary eclipse may appear halfway between primary eclipses.

Real planets can also exhibit secondary occultations. These indicators should
trigger scientific review, not be interpreted as certain false positives.
"""
import numpy as np
from blind_transit_benchmark import robust_sigma
from transit_consistency import individual_transit_checks


def estimate_binary_indicators(time, flux, period, epoch, duration):
    t=np.asarray(time,dtype=float)
    f=np.asarray(flux,dtype=float)
    result,events=individual_transit_checks(
        t,f,period,epoch,duration,sigma=robust_sigma(f))
    primary_positive=events.loc[events.depth_ppm>0,"depth_ppm"].to_numpy()
    primary_ppm=float(np.median(primary_positive)) if primary_positive.size else None

    odd=events.loc[events.event%2==1,"depth_ppm"].to_numpy()
    even=events.loc[events.event%2==0,"depth_ppm"].to_numpy()
    odd_even_ratio=None
    odd_even_z=None
    if len(odd)>=2 and len(even)>=2 and primary_ppm is not None and primary_ppm>0:
        difference=float(abs(np.median(odd)-np.median(even)))
        odd_even_ratio=difference/primary_ppm
        # Include an empirical between-event scatter, so the score does not
        # pretend every event is an independent white-noise observation.
        scale=np.sqrt(np.var(odd,ddof=1)/len(odd)+
                      np.var(even,ddof=1)/len(even))
        odd_even_z=difference/max(scale,1e-9)
    # Look for a *separate* decrease halfway through the fitted orbital period.
    # Limit the local comparison interval so it does not overlap a primary event.
    opposite_center=epoch+period/2
    phase=(t-opposite_center+period/2)%period-period/2
    d=np.abs(phase)
    in_eclipse=d<duration/2
    max_outer=min(4*duration,.38*period)
    out_eclipse=(d>1.5*duration)&(d<max_outer)
    secondary_depth_ppm=None
    secondary_snr=None
    if in_eclipse.sum()>=3 and out_eclipse.sum()>=6:
        secondary_depth_ppm=float(
            (np.median(f[out_eclipse])-np.median(f[in_eclipse]))*1e6)
        uncertainty=robust_sigma(f)*np.sqrt(1/in_eclipse.sum()+1/out_eclipse.sum())
        secondary_snr=secondary_depth_ppm/max(uncertainty*1e6,1e-6)
    # Fixed rules specified before the new held-out experiment.
    odd_even_warning=bool(odd_even_ratio is not None and
        odd_even_z is not None and odd_even_ratio>.35 and odd_even_z>3)
    secondary_warning=bool(secondary_depth_ppm is not None and
        primary_ppm is not None and primary_ppm>0 and
        secondary_depth_ppm/primary_ppm>.30 and secondary_snr is not None and
        secondary_snr>5)
    return {
      "n_events":int(len(events)),
      "primary_depth_ppm":primary_ppm,
      "odd_even_depth_ratio":odd_even_ratio,
      "odd_even_statistic":odd_even_z,
      "secondary_depth_ppm":secondary_depth_ppm,
      "secondary_snr":secondary_snr,
      "odd_even_warning":odd_even_warning,
      "secondary_warning":secondary_warning,
      "binary_review_warning":bool(odd_even_warning or secondary_warning),
      "scientific_caveat":"Exploratory binary-like indicator: real planets can have occultations; this is not proof of a false positive",
    }
