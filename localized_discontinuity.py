"""Conservative localized discontinuity diagnostic for Kepler time-series flux.

Established context: Kepler PDC corrects many SPSDs; Aigrain et al. (2017)
separate discontinuity DETECTION, CLASSIFICATION and CORRECTION; Robnik et al.
(2026) use a much richer localized-defect template bank.

Our deliberately small classroom algorithm only seeks abrupt DOWNWARD
changes persisting longer than a short box-shaped transit, and MASKS a
predeclared neighborhood; it is neither their published implementation nor
a classifier of physical planets. Every masked real transit must be counted.
"""
from __future__ import annotations
import numpy as np
from blind_transit_benchmark import robust_sigma


def synthetic_spsd_like_step(time, raw_flux, start, depth_fraction,
                             decay_days, persistent_fraction):
    """Inject a stylized negative step with exponential partial recovery.

    This is a SOURCE-CONTROLLED nuisance injected into measured PDCSAP flux,
    not an archival SPSD label or a pixel-level instrument simulation.
    Does not modify caller's input.
    """
    t=np.asarray(time,float)
    f=np.asarray(raw_flux,float)
    if t.shape!=f.shape or t.ndim!=1 or len(t)<40:
        raise ValueError("Time and flux must be same-length 1D arrays")
    if (not 0<depth_fraction<.5 or decay_days<=0 or
            not 0<=persistent_fraction<=1 or not np.isfinite(start)):
        raise ValueError("Invalid synthetic discontinuity parameters")
    y=f.copy()
    elapsed=t-start
    affected=elapsed>=0
    if affected.any():
        profile=(persistent_fraction+
                 (1-persistent_fraction)*np.exp(-elapsed[affected]/decay_days))
        y[affected]*=(1-depth_fraction*profile)
    return y,affected


def localized_downward_step_mask(time,normalized_flux,settings):
    """Identify a substantial abrupt *persistent* decline with local medians.

    No known artifact epoch, injected period, injected depth, literature
    planet label or expected output class is provided to the detector.
    The candidate onset is a large negative first difference (not close to
    an observational gap). Both following windows must remain below the
    preceding baseline; a brief transit recovers and should be rejected.

    Kepler noise is correlated. A sigma-multiplier here is a conservative
    engineering screen, NOT a false-alarm probability or calibrated z-test.
    """
    t=np.asarray(time,float)
    f=np.asarray(normalized_flux,float)
    if t.ndim!=1 or t.shape!=f.shape or len(t)<50:
        raise ValueError("Expected time and normalized flux 1D arrays")
    if not np.all(np.isfinite(t)) or not np.all(np.isfinite(f)):
        raise ValueError("Nonfinite data")
    if np.any(np.diff(t)<=0):
        raise ValueError("Times must increase strictly")
    low=float(settings["step_min_negative_jump_fraction"])
    multiplier=float(settings["step_robust_noise_multiplier"])
    pre_outer,pre_inner=(float(x) for x in settings["step_local_pre_window_days"])
    post_inner,post_outer=(float(x) for x in settings["step_local_post_window_days"])
    late_inner,late_outer=(float(x) for x in settings["step_late_post_window_days"])
    minimum=int(settings["step_min_local_points"])
    persistent=float(settings["step_persistent_min_fraction"])
    half=float(settings["step_mask_half_width_days"])
    spacing=float(settings["step_candidate_separation_days"])
    if not (0<pre_inner<pre_outer and 0<post_inner<post_outer<=late_inner<late_outer
            and minimum>=3 and 0<persistent<1 and 0<half<spacing and low>0 and multiplier>0):
        raise ValueError("Invalid fixed detector settings")

    typical_cadence=float(np.median(np.diff(t)))
    if typical_cadence<=0: raise ValueError("Invalid cadence")
    local_noise=robust_sigma(f)
    minimum_jump=max(low,multiplier*np.sqrt(2)*local_noise)
    diffs=np.diff(f)
    # Do not match discontinuities across missing observing time.
    candidates=np.flatnonzero(
        (diffs<-minimum_jump)&(np.diff(t)<3.0*typical_cadence))+1
    detections=[]
    for i in candidates:
        onset=float(t[i])
        left=f[(t>=onset-pre_outer)&(t<=onset-pre_inner)]
        after=f[(t>=onset+post_inner)&(t<=onset+post_outer)]
        late=f[(t>=onset+late_inner)&(t<=onset+late_outer)]
        if min(len(left),len(after),len(late))<minimum:
            continue
        # If the windows themselves cross large gaps, refuse this candidate.
        # We do not claim a smooth baseline where there was no observation.
        windows=(
            t[(t>=onset-pre_outer)&(t<=onset-pre_inner)],
            t[(t>=onset+post_inner)&(t<=onset+post_outer)],
            t[(t>=onset+late_inner)&(t<=onset+late_outer)]
        )
        if any(np.any(np.diff(w)>3.0*typical_cadence) for w in windows):
            continue
        before=float(np.median(left))
        mid=float(np.median(after))
        far=float(np.median(late))
        jump=float(-diffs[i-1])
        drop_mid=before-mid
        drop_late=before-far
        if drop_mid>=persistent*jump and drop_late>=persistent*jump:
            detections.append({"time_bkjd":onset,
                               "jump_fraction":jump,
                               "post_minus_pre":mid-before,
                               "late_minus_pre":far-before,
                               "noise_proxy":local_noise})

    # Keep strongest local onset, not every cadence in a step's decline.
    selected=[]
    for d in sorted(detections,key=lambda x:-x["jump_fraction"]):
        if all(abs(d["time_bkjd"]-a["time_bkjd"])>spacing for a in selected):
            selected.append(d)
    selected.sort(key=lambda x:x["time_bkjd"])
    mask=np.ones(len(t),dtype=bool)
    for d in selected:
        mask &= np.abs(t-d["time_bkjd"])>half
    if int(mask.sum())<int(settings["step_min_retained"]):
        raise ValueError("Step mask leaves too few observation samples")
    report={"n_raw_step_candidates":int(len(candidates)),
            "n_persistent_step_events":int(len(selected)),
            "n_removed":int((~mask).sum()),
            "fraction_removed":float((~mask).mean()),
            "local_scatter":float(local_noise),
            "first_difference_threshold":float(minimum_jump),
            "detected_events":selected,
            "limits":"Heuristic, not independently confirmed SPSDs or statistical FAP"}
    return mask,report
