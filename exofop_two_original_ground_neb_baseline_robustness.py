"""Source-SHA pinned two reported NEB ground flux baseline-systematics audit.

Reanalyse exact previously archived 162 and 84 original ExoFOP AIJ ground
photometry rows, SAME original NEBcheck event windows, and fixed apertures.
A measured dip is not independently plate-solved source localization, and
one night of data cannot validate NASA ExoMiner planet discrimination.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import theilslopes

from exofop_two_NEB_original_ground_AIJ_numeric_sources import EXPECTED
from exofop_two_ground_NEBS_original_AIJ_fixed_window_depth import (
    source_aij_timeseries_bytes,PRE_COMMITTED_OTHER_APERTURES,
    depth_from_true_original_aperture
)


def one_aperture_robustness(t,y,ingress,egress):
    t=np.asarray(t,dtype=float)
    y=np.asarray(y,dtype=float)
    positive=np.isfinite(y)&(y>0)
    pre=positive&(t<ingress)
    event=positive&(t>=ingress)&(t<=egress)
    post=positive&(t>egress)
    if min(pre.sum(),event.sum(),post.sum())<5:
        return {"status":"not_evaluable_original_ground_flux_coverage"}
    pp=float(np.median(y[pre]))
    po=float(np.median(y[post]))
    inside=float(np.median(y[event]))
    mid=.5*(ingress+egress)
    out=pre|post
    obs=t[out]-mid
    slope,intercept,lower_slope,upper_slope=theilslopes(y[out],obs)
    pred=intercept+slope*(t[event]-mid)
    if not np.isfinite(pred).all() or (pred<=0).any():
        raise ValueError("Robust original source outside-event flux fit predicts nonphysical baseline")
    detrended_depth=1000*(1-float(np.median(y[event]/pred)))
    back=(pp+po)/2
    fixed_depth=1000*(back-inside)/back
    return {
        "status":"actual_original_ground_timeseries_reanalyzed",
        "source_genuine_outside_event_pre_cadences":int(pre.sum()),
        "source_genuine_inside_event_cadences":int(event.sum()),
        "source_genuine_outside_event_post_cadences":int(post.sum()),
        "pre_only_baseline_depth_ppt":1000*(pp-inside)/pp,
        "post_only_baseline_depth_ppt":1000*(po-inside)/po,
        "equal_prepost_baseline_depth_ppt":fixed_depth,
        "original_prepost_baseline_relative_disagreement_ppt":1000*abs(po-pp)/back,
        "robust_theil_sen_outside_only_slope_flux_per_day":float(slope),
        "robust_theil_sen_outside_only_detrended_depth_ppt":float(detrended_depth),
        "all_three_fixed_baseline_methods_show_positive_dip":bool(
            pp>inside and po>inside and detrended_depth>0),
        "no_event_timestamp_refit_or_source_replacement":True,
        "caveat":"Post-hoc baseline sensitivity in a single original ground observing night; actual neighbor TIC mapping is original observer assignment"
    }


def run(original_two_ground,original_source_dir,out):
    original_two_ground=Path(original_two_ground)
    d=json.loads(original_two_ground.read_text())
    rows=d["original_reported_cases"]
    if len(rows)!=2 or {int(x["TIC_ID"]) for x in rows}!=set(EXPECTED):
        raise ValueError("Prior original two-neighbor output changed source host TICs")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    records=[]
    for prior in rows:
        tic=int(prior["TIC_ID"])
        known=EXPECTED[tic]
        info=prior["original_report_predicted_ephemeris_window"]
        if prior["ground_photometry_status"]!="original_aperture_photometry_measured":
            raise ValueError("Prior original scientific source failed; cannot silently choose replacement")
        original_name=next(
            x["original_filename"] for x in json.loads(
                (Path(original_source_dir)/
                "two_ground_reported_NEB_numeric_AIJ_tseries_original_source_profile.json").read_text()
            )["original_two_uploaded_aperture_source_records"] if int(x["TIC_ID"])==tic)
        file=Path(original_source_dir)/(
           f"original_TIC{tic}_ExoFOP_file{known['original_ExoFOP_file_ID']}_{original_name}")
        raw=file.read_bytes()
        sha=hashlib.sha256(raw).hexdigest()
        if sha!=prior["actual_original_numeric_AIJ_table_SHA256"]:
            raise ValueError("Original ground photometry source SHA256 changed")
        frame=source_aij_timeseries_bytes(raw,known["AIJ_aperture"])
        t=frame.BJD_TDB.to_numpy(dtype=float)
        ingress=float(info["prescribed_full_BJD_TDB_ingress"])
        egress=float(info["prescribed_full_BJD_TDB_egress"])
        result=dict(TIC_ID=tic,TOI=known["TOI"],
                    original_ground_source_SHA256=sha,
                    original_reported_neighbor_TIC_ID=known["ground_neighbor_TIC_ID"],
                    observer_mapped_aperture=known["AIJ_aperture"],
                    original_invariant_ingress_BJD_TDB=ingress,
                    original_invariant_egress_BJD_TDB=egress)
        groups={}
        for aperture in ["T1",*PRE_COMMITTED_OTHER_APERTURES,known["AIJ_aperture"]]:
            col="rel_flux_"+aperture
            if col not in frame:continue
            z=one_aperture_robustness(t,frame[col].to_numpy(dtype=float),ingress,egress)
            if z["status"]=="actual_original_ground_timeseries_reanalyzed":
                previous=prior["original_observing_aperture_depths"][aperture]
                if abs(z["equal_prepost_baseline_depth_ppt"]-previous["measured_depth_ppt"])>1e-6:
                    raise ValueError("Original fixed-window ground source depth or data changed")
            groups[aperture]=z
        result["fixed_original_aperture_robustness"]=groups
        result["reported_neighbor_results"]=groups[known["AIJ_aperture"]]
        result["neighbor_depth_remains_positive_across_three_methods"]=groups[
            known["AIJ_aperture"]].get("all_three_fixed_baseline_methods_show_positive_dip",False)
        result["not_independent_sky_plate_solved_source_identity"]=True
        records.append(result)
        print("ORIGINAL_GROUND_BASELINE_ROBUSTNESS",json.dumps({
            "TOI":known["TOI"],"TIC":tic,
            "observer_aperture":known["AIJ_aperture"],
            "neighbor_original_source_flux_methods":result["reported_neighbor_results"],
            "comparison_other_aperture_source_methods":{
                x:groups[x] for x in PRE_COMMITTED_OTHER_APERTURES}
        }),flush=True)
    report={
        "research_question":"Does original ExoFOP ground neighbor-aperture T6/T11 dip survive three fixed alternative baseline approaches without fitting a transit epoch or aperture?",
        "n_ground_observer_reported_NEB_cases":len(records),
        "n_ground_observer_reported_neighbor_apertures_consistent_across_three_baseline_methods":sum(
            x["neighbor_depth_remains_positive_across_three_methods"] for x in records),
        "all_original_same_file_same_window_results":records,
        "original_science_output_SHA256":hashlib.sha256(original_two_ground.read_bytes()).hexdigest(),
        "independently_verified_onsky_neighbor_TIC_by_our_ground_WCS_analysis":False,
        "scope":[
            "Pre/post medians and Theil-Sen outside-event-only trend are post-hoc robustness checks on exactly the same original ground event and fixed aperture.",
            "No alternate event times or reported neighbor aperture selection optimized on the observed flux.",
            "Original relative comparison star flux and target saturation may be affected by systematics; stability of one aperture alone is not proof of astrophysical source.",
            "These are 2 observed ground nights and 2 reported physical neighbors; not NASA training-independent mission validation and not a planet detection.",
        ]
    }
    (out/"two_original_ground_NEB_T6_T11_source_SHA_fixed_baseline_robustness.json").write_text(
        json.dumps(report,indent=2)+"\n")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-ground-output",required=True)
    p.add_argument("--original-numeric-AIJ-source",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.original_ground_output,a.original_numeric_AIJ_source,a.out)
