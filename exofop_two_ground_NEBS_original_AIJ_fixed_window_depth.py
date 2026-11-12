"""Reanalyze ORIGINAL ExoFOP ground-based AIJ T6/T11 eclipse aperture flux.

Two source candidates were selected from previously read observer notes,
and original NEBcheck report predicted ingress/egress windows are obtained
from SHA-verified source text BEFORE reading numeric ground flux outcomes.
No searching for the deepest possible window or alternate aperture.

One ground event per target: bootstrap intervals are descriptive, not a
calibrated independent astrophysical discovery or NASA ExoMiner accuracy.
"""
import argparse
import hashlib
import io
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from exofop_two_NEB_original_ground_AIJ_numeric_sources import EXPECTED

PRE_COMMITTED_OTHER_APERTURES=("T2","T3","T4","T5")
BOOTSTRAPS=5000
SEED=2026111211


def original_ephemeris_window(neb_table_source,original_bjd):
    """Build absolute original BJD from published NEBcheck decimal-day window.

    Original NEBcheck writes the fractional/running JD-day portion; use only
    the observed timestamps to choose which integer day is in the recorded
    observation (never use flux to shift the eclipse). 
    """
    def extract(which):
        rexp=rf"Predicted\s+{which}\s+time\s*:\s*([-+]?[0-9]*\.?[0-9]+)"
        hits=re.findall(rexp,neb_table_source,flags=re.I)
        if len(hits)!=1:
            raise ValueError("Original observer NEBcheck has no unique prescribed "+which+" time")
        return float(hits[0])
    ingress=extract("ingress")
    egress=extract("egress")
    if not np.isfinite([ingress,egress]).all() or egress<=ingress or egress-ingress>1:
        raise ValueError("Observer original predicted eclipse window is physically invalid")
    bjd=np.asarray(original_bjd,dtype=float)
    if len(bjd)<30 or not np.isfinite(bjd).all() or not np.all(np.diff(bjd)>0):
        raise ValueError("Original ground BJD time rows must be real, finite, increasing")
    day=int(np.rint(float(np.median(bjd))-.5*(ingress+egress)))
    absolute_ingress=day+ingress
    absolute_egress=day+egress
    if not (bjd.min()<absolute_ingress<absolute_egress<bjd.max()):
        raise ValueError("Original observer-predicted ingress/egress not observed within this original AIJ table")
    return {
        "original_NEBcheck_ingress_original_day_part":ingress,
        "original_NEBcheck_egress_original_day_part":egress,
        "source_time_only_nearest_integer_day":day,
        "prescribed_full_BJD_TDB_ingress":absolute_ingress,
        "prescribed_full_BJD_TDB_egress":absolute_egress,
        "window_days":egress-ingress,
        "no_photometry_shift_or_fitted_transit_epoch":True
    }


def depth_from_true_original_aperture(t,flux,ingress,egress,boot=BOOTSTRAPS,seed=SEED):
    t=np.asarray(t,dtype=float)
    y=np.asarray(flux,dtype=float)
    if t.shape!=y.shape or t.ndim!=1 or not np.all(np.diff(t)>0):
        raise ValueError("Original time and ground aperture flux cannot be matched")
    valid=np.isfinite(y)&(y>0)&np.isfinite(t)
    before=valid&(t<ingress)
    inevent=valid&(t>=ingress)&(t<=egress)
    after=valid&(t>egress)
    nb,ni,na=int(before.sum()),int(inevent.sum()),int(after.sum())
    if min(nb,ni,na)<5:
        return {
            "status":"not_evaluable_original_ground_time_or_aperture_cadence",
            "n_genuine_baseline_pre":nb,"n_original_in_window":ni,"n_genuine_baseline_post":na,
            "measured_depth_ppt":None,
        }
    pre=np.median(y[before]);post=np.median(y[after])
    baseline=.5*(pre+post)
    inside=np.median(y[inevent])
    if not np.isfinite(baseline) or baseline<=0:
        raise ValueError("Invalid original positive ground aperture baseline")
    depth=1000*(baseline-inside)/baseline
    # Descriptive fixed-width block bootstrap preserves local autocorrelation
    # approximately but does not prove eclipse timing or aperture identity.
    def block_resample(z,n,block,rng):
        arr=np.asarray(z,dtype=float)
        starts=rng.integers(0,len(arr),size=(n,int(np.ceil(len(arr)/block))))
        offsets=np.arange(block,dtype=int)
        idx=(starts[:,:,None]+offsets[None,None,:])%len(arr)
        return arr[idx.reshape(n,-1)[:,:len(arr)]]
    rng=np.random.default_rng(seed)
    sample_n=boot
    p=block_resample(y[before],sample_n,4,rng)
    q=block_resample(y[inevent],sample_n,4,rng)
    r=block_resample(y[after],sample_n,4,rng)
    base=.5*(np.median(p,axis=1)+np.median(r,axis=1))
    ds=1000*(base-np.median(q,axis=1))/base
    return {
        "status":"measured_original_ground_AIJ_aperture",
        "n_genuine_baseline_pre":nb,"n_original_in_window":ni,"n_genuine_baseline_post":na,
        "original_ground_baseline_pre_flux":float(pre),
        "original_ground_baseline_post_flux":float(post),
        "original_ground_in_window_median_flux":float(inside),
        "measured_depth_ppt":float(depth),
        "descriptive_fixed_four_cadence_block_bootstrap_95pct_ppt":np.quantile(ds,[.025,.975]).tolist(),
        "fraction_block_bootstrap_resamples_showing_dimming":float((ds>0).mean()),
        "warning":"One previously selected original ground event; block bootstrap is approximate/correlated and not a formal source-discovery significance"
    }


def source_aij_timeseries_bytes(raw,neighbor_aperture):
    table=pd.read_csv(io.BytesIO(raw),sep="\t",low_memory=False)
    cols=["BJD_TDB","rel_flux_"+neighbor_aperture]+[
        "rel_flux_"+a for a in PRE_COMMITTED_OTHER_APERTURES]
    if "rel_flux_T1" in table:
        cols.append("rel_flux_T1")
    if not set(cols).issubset(table.columns):
        raise ValueError("Original AIJ table lacks source aperture or fixed comparison apertures: "+str(set(cols)-set(table.columns)))
    selected=table[cols].copy()
    for col in cols:
        selected[col]=pd.to_numeric(selected[col],errors="coerce")
    if selected.BJD_TDB.isna().any() or not np.all(np.diff(selected.BJD_TDB)>0):
        raise ValueError("Original ground source BJD_TDB rows are missing or misordered")
    return selected


def verified_file(path,sha):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=sha:
        raise ValueError("Ground original source SHA changed from prior uploaded-file audit")
    return raw


def run(source_dir,original_neb_dir,original_prior_audit,out):
    source_dir=Path(source_dir)
    original_neb_dir=Path(original_neb_dir)
    audit=json.loads(Path(original_prior_audit).read_text())
    prior={int(r["original_file_ID"]):r for r in audit["original_observer_source_file_details"]}
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    records=[]
    for host,known in EXPECTED.items():
        item=dict(TIC_ID=host,TOI=known["TOI"],
                  note_reported_neighbor_TIC_ID=known["ground_neighbor_TIC_ID"],
                  original_reported_aperture=known["AIJ_aperture"])
        try:
            numeric_json=json.loads((source_dir/
                "two_ground_reported_NEB_numeric_AIJ_tseries_original_source_profile.json").read_text())
            matches=[r for r in numeric_json["original_two_uploaded_aperture_source_records"]
                     if int(r["TIC_ID"])==host]
            if len(matches)!=1 or matches[0]["source_retrieval_status"]!="success":
                raise ValueError("Original ground numeric file missing or source failed")
            info=matches[0]
            file=source_dir/f"original_TIC{host}_ExoFOP_file{known['original_ExoFOP_file_ID']}_{info['original_filename']}"
            raw=verified_file(file,info["original_table_source_SHA256"])
            aij=source_aij_timeseries_bytes(raw,known["AIJ_aperture"])
            neb_info=prior.get(known["report_original_NEBcheck_file_ID"])
            if not neb_info or int(neb_info["host_TIC_ID"])!=host:
                raise ValueError("Original observer NEBcheck target source not pinned")
            neb_file=original_neb_dir/f"TIC{host}_file{known['report_original_NEBcheck_file_ID']}_{neb_info['original_file_name']}"
            neb_text=verified_file(neb_file,neb_info["original_uploaded_file_source_SHA256"]).decode("utf-8-sig",errors="replace")
            timing=original_ephemeris_window(neb_text,aij.BJD_TDB)
            item.update(
                actual_original_numeric_AIJ_table_SHA256=info["original_table_source_SHA256"],
                actual_original_NEBcheck_report_SHA256=neb_info["original_uploaded_file_source_SHA256"],
                original_report_predicted_ephemeris_window=timing,
                original_observing_aperture_depths={}
            )
            times=aij["BJD_TDB"].to_numpy(dtype=float)
            report_apertures=["T1",*PRE_COMMITTED_OTHER_APERTURES,known["AIJ_aperture"]]
            report_apertures=list(dict.fromkeys(report_apertures))
            for aperture in report_apertures:
                col="rel_flux_"+aperture
                if col not in aij.columns:continue
                stats=depth_from_true_original_aperture(
                    times,aij[col].to_numpy(dtype=float),
                    timing["prescribed_full_BJD_TDB_ingress"],
                    timing["prescribed_full_BJD_TDB_egress"],
                    seed=SEED+host%10000+int(aperture[1:]))
                item["original_observing_aperture_depths"][aperture]=stats
            item["reported_neighbor_aperture_result"]=item["original_observing_aperture_depths"][known["AIJ_aperture"]]
            comparison=[v["measured_depth_ppt"] for k,v in item["original_observing_aperture_depths"].items()
                        if k in PRE_COMMITTED_OTHER_APERTURES and v["status"]=="measured_original_ground_AIJ_aperture"]
            item["median_fixed_other_aperture_depth_ppt"]=float(np.median(comparison)) if comparison else None
            item["ground_photometry_status"]="original_aperture_photometry_measured"
            # Plot actual observed relative flux around the original NEBcheck ingress/egress.
            fig,ax=plt.subplots(figsize=(8,4.2))
            for aperture in [known["AIJ_aperture"],"T2","T3","T4"]:
                col="rel_flux_"+aperture
                if col not in aij:continue
                y=aij[col].to_numpy(dtype=float)
                if not np.isfinite(y[y>0]).any():continue
                before=(times<timing["prescribed_full_BJD_TDB_ingress"])&np.isfinite(y)&(y>0)
                after=(times>timing["prescribed_full_BJD_TDB_egress"])&np.isfinite(y)&(y>0)
                if not before.any() or not after.any():continue
                baseline=.5*(np.median(y[before])+np.median(y[after]))
                if baseline<=0:continue
                ax.plot((times-np.median(times))*24,(y/baseline-1)*1000,
                        "." if aperture==known["AIJ_aperture"] else "-",
                        label=f"{aperture} {'reported neighbor' if aperture==known['AIJ_aperture'] else 'other field'}",
                        markersize=3,alpha=.75)
            ax.axvspan((timing["prescribed_full_BJD_TDB_ingress"]-np.median(times))*24,
                       (timing["prescribed_full_BJD_TDB_egress"]-np.median(times))*24,
                       alpha=.12,color="grey",label="original observer-predicted window")
            ax.set(xlabel="Hours relative to median original BJD_TDB",
                   ylabel="Relative flux versus outside-window baseline (ppt)",
                   title=f"Original ground AstroImageJ TOI {known['TOI']}: T{known['AIJ_aperture'][1:]}")
            ax.legend(fontsize=8,frameon=False)
            fig.tight_layout()
            fig.savefig(out/f"original_ground_TOI{known['TOI']}_reported_neighbor_aperture_vs_fixed_controls.png",dpi=175)
            plt.close(fig)
        except (ValueError,OSError,KeyError) as exc:
            item["ground_photometry_status"]="not_evaluable"
            item["ground_photometry_error"]=str(exc)[:360]
        print("ORIGINAL_GROUND_ECLIPSE_DEPTH",json.dumps({
            "host_TIC":host,"TOI":known["TOI"],"aperture":known["AIJ_aperture"],
            "status":item["ground_photometry_status"],
            "source_reported_neighbor_depth":item.get("reported_neighbor_aperture_result"),
            "other_aper_depths":item.get("original_observing_aperture_depths"),
            "original_ingress_egress":item.get("original_report_predicted_ephemeris_window"),
            "error":item.get("ground_photometry_error")
        }),flush=True)
        records.append(item)
    report={
        "research_question":"Do the actual original ground AIJ measurements show a flux dip in the reported neighboring star aperture at the original observer NEBcheck predicted ingress and egress?",
        "original_reported_cases":records,
        "two_distinct_host_stars_attempted":len(records),
        "original_ground_neighbor_aperture_cases_with_measurements":sum(x["ground_photometry_status"]=="original_aperture_photometry_measured" for x in records),
        "independent_ground_aperture_astrometric_TIC_mapping_reverified_from_original_image":False,
        "formal_physical_source_truth_confirmed":False,
        "scope":[
            "NEBcheck ingress/egress are read unchanged from original source reports and mapped to original full BJD using observation timestamps only, never shifted to optimize observed depth.",
            "Simple equal-weight pre/post local baseline and signed median in-window depth evaluated on original ground AIJ reported neighbor aperture, original target and fixed T2–T5 controls.",
            "Four-cadence block bootstrap describes uncertainty conditional on one ground event and model choices, not a calibrated detection p-value.",
            "T1 host may be saturated per original observer notes and is not a valid negative control without aperture corrections.",
            "T6/T11 physical sky TIC identification is attributed to original observer notes, not independently plate-solved using an observed ground pixel image.",
            "No use of original TESS centroid scores, ExoMiner model classifications, re-fit transit ephemerides or reselected ground aperture to optimize outcomes."
        ]
    }
    (out/"two_ground_NEB_original_AIJ_fixed_reported_ingress_egress_aperture_flux_results.json").write_text(
        json.dumps(report,indent=2)+"\n")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-AIJ-files",required=True)
    p.add_argument("--original-neb-files",required=True)
    p.add_argument("--prior-source-audit",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.original_AIJ_files,a.original_neb_files,a.prior_source_audit,a.out)
