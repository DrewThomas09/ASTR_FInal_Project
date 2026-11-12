"""Five newly source-frozen SPOC-host centroid direction replication.

Original MAST SPOC two-minute LC/TP; original ExoFOP note-named candidate
neighbor positions and published TOI ephemerides. Selected before examining
these five host-star centroid results, but neither independently verified
ground-based neighbor eclipse truth nor excluded from NASA training.
No model weights, predictions, star identities or thresholds are altered.
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from scipy.stats import binomtest

from tess_original_moment_centroid_companion import load_tess_centroid_columns
from tess_toi4255_original_spoc_neb_vector_case import (
    download_original_mast, sky_wcs_from_tpf, position_geometry,
    paired_original_events, summarize_pairs
)

B=20000
SEED=2026111205
CONTROLS=(-.25,.25)


def check_source_manifest(spec):
    if spec.get("experiment_id")!="ASTR_FIVE_NEW_NEB_SPOC_SOURCE_BLIND_WCS_EVAL_20261112":
        raise ValueError("Wrong five-new-host source freeze")
    if not spec.get("source_manifest_frozen_prior_to_five_star_TESS_centroid_analysis"):
        raise ValueError("Sources not frozen before astronomical measurement")
    a=spec.get("source_records",[])
    if len(a)!=5 or len({int(x["TIC_ID"]) for x in a})!=5:
        raise ValueError("Not precisely five fixed new TIC host stars")
    if any(x.get("moment_centroid_vectors_extracted") or
           x.get("ground_based_eclipse_in_named_neighbor_independently_verified")
           for x in a):
        raise ValueError("Candidate source falsely labeled as verified or preexamined")
    return a


def source_direction_summary(eligible):
    """Star/host is the only unit in between-source descriptive uncertainty."""
    if not eligible:
        return {
            "n_new_host_stars_with_evaluable_direction":0,
            "scope":"No source-level angular comparison evaluable",
        }
    dif=np.array([r["corrected_alignment_gain_degrees"] for r in eligible],dtype=float)
    n=len(dif)
    ups=int((dif>1e-10).sum());downs=int((dif< -1e-10).sum());ties=int(n-ups-downs)
    stats={
        "n_new_host_stars_with_evaluable_direction":n,
        "n_new_hosts_corrected_angle_lower":ups,
        "n_new_hosts_corrected_angle_higher":downs,
        "n_new_hosts_exact_ties":ties,
        "median_new_host_angular_improvement_deg":float(np.median(dif)),
        "source_level_two_sided_exact_sign_p_exploratory":(
            float(binomtest(ups,ups+downs).pvalue) if ups+downs else None
        ),
    }
    if n>=2:
        rng=np.random.default_rng(SEED)
        draws=rng.integers(0,n,size=(B,n))
        stats["exploratory_20000_whole_host_bootstrap_95pct_median_angle_improvement_deg"]=np.quantile(
            np.median(dif[draws],axis=1),[.025,.975]).tolist()
    else:
        stats["exploratory_20000_whole_host_bootstrap_95pct_median_angle_improvement_deg"]=None
    return stats


def run(manifest,out,working):
    manifest=Path(manifest)
    spec=json.loads(manifest.read_text(encoding="utf-8"))
    targets=check_source_manifest(spec)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    working=Path(working);working.mkdir(parents=True,exist_ok=True)
    results=[]
    for source in targets:
        tic=int(source["TIC_ID"]);sector=int(source["selected_first_original_SPOC_2min_sector"])
        r=dict(
            TIC_ID=tic, TOI=source["TOI"],
            external_note_named_neighbor_candidate_TIC=int(
                source["original_neb_named_neighbor_TIC_not_physical_truth"]),
            original_SPOC_sector=sector,
            original_ExoFOP_P_days=float(source["original_ExoFOP_period_days"]),
            original_ExoFOP_epoch_BTJD=float(source["original_ExoFOP_epoch_BTJD"]),
            original_ExoFOP_duration_days=float(source["original_ExoFOP_duration_days"]),
            external_ground_truth_NEBS_independently_confirmed=False,
            prior_to_run_centroid_outcome_inspected=False,
        )
        try:
            files={}
            for group in ("LC","TP"):
                item=source["original_MAST_products"][group]
                if item["product_group"]!=group or int(item["TIC_ID"])!=tic or int(item["sector"])!=sector:
                    raise ValueError("Source manifest original TESS product identity mismatch")
                file=working/str(tic)/item["productFilename"]
                original=download_original_mast(item["MAST_original_dataURI"],file)
                r["original_MAST_"+group+"_source"]={
                    k:v for k,v in original.items()}
                files[group]=file
            frame,lc=load_tess_centroid_columns(files["LC"],tic,sector)
            r["original_SPOC_LC_header_and_data"]=lc
            w,sky,wcs=sky_wcs_from_tpf(files["TP"],tic,sector)
            r["original_SPOC_TPF_WCS_header"]=wcs
            neighbor=dict(
                neighbor_RA_deg=float(source["original_nearby_catalog_RA_deg"]),
                neighbor_Dec_deg=float(source["original_nearby_catalog_Dec_deg"]),
                catalog_separation_arcsec=float(source["original_nearby_catalog_separation_arcsec"]),
                catalog_position_angle_deg=float(source["original_nearby_catalog_position_angle_deg"])
            )
            direction=position_geometry(w,sky,neighbor)
            r["original_external_neighbor_in_TESS_WCS"]=direction
            P=r["original_ExoFOP_P_days"];E=r["original_ExoFOP_epoch_BTJD"];D=r["original_ExoFOP_duration_days"]
            events,counts=paired_original_events(frame,P,E,D,direction)
            r["original_real_event_counts"]=counts
            r["true_original_event_results"]=summarize_pairs(events,direction,sector)
            if events:
                pd.DataFrame(events).to_csv(
                    out/f"TIC{tic}_S{sector}_actual_original_TESS_SPOC_event_vectors.csv",index=False)
            r["source_direction_evaluable"]=bool(
                direction["catalog_sky_geometry_consistent_with_TPF_target_position"] and
                len(events)>=3 and
                r["true_original_event_results"]["raw_median_vector_angular_difference_away_neighbor_deg"] is not None and
                r["true_original_event_results"]["pointing_subtracted_median_vector_angular_difference_away_neighbor_deg"] is not None)
            if r["source_direction_evaluable"]:
                r["corrected_alignment_gain_degrees"]=float(
                    r["true_original_event_results"]["raw_median_vector_angular_difference_away_neighbor_deg"]-
                    r["true_original_event_results"]["pointing_subtracted_median_vector_angular_difference_away_neighbor_deg"])
            else:
                r["corrected_alignment_gain_degrees"]=None
            controls=[]
            for fraction in CONTROLS:
                ce,cnt=paired_original_events(frame,P,E+fraction*P,D,direction)
                cr=summarize_pairs(ce,direction,sector)
                controls.append({
                    "phase_offset_from_original_ephemeris_in_P":fraction,
                    "actual_observed_control_event_counts":cnt,
                    "control_source_results":cr,
                    "not_independent_noise_only_ground_truth":True
                })
            r["same_original_source_quarter_phase_controls"]=controls
            r["source_processing_status"]="processed"
        except (ValueError,KeyError,OSError,requests.RequestException) as ex:
            r["source_processing_status"]="not_evaluable"
            r["source_error"]=str(ex)[:400]
            r["source_direction_evaluable"]=False
            r["corrected_alignment_gain_degrees"]=None
        print("FROZEN_FIVE_SOURCE_RESULT",json.dumps({
            "TIC":tic,"TOI":source["TOI"],
            "status":r["source_processing_status"],
            "error":r.get("source_error"),
            "n_actual_events":r.get("original_real_event_counts"),
            "evaluable":r["source_direction_evaluable"],
            "angle_gain_deg":r["corrected_alignment_gain_degrees"],
            "science":r.get("true_original_event_results"),
        }),flush=True)
        results.append(r)
    good=[r for r in results if r["source_direction_evaluable"]]
    report={
        "experiment":"Five newly frozen authentic original TESS SPOC host stars, descriptive source-neighbor alignment; NOT independent physically verified NEB truth",
        "source_manifest_sha256":hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "all_five_source_outcomes_preserved":True,
        "exact_new_host_star_count_attempted":len(targets),
        "source_host_stars_with_usable_original_data":sum(r["source_processing_status"]=="processed" for r in results),
        "source_host_stars_missing_or_not_evaluable":sum(r["source_processing_status"]!="processed" for r in results),
        "star_level_directional_statistics":source_direction_summary(good),
        "all_original_source_results":results,
        "scientific_limitations":[
            "Five sources selected without viewing their moment centroids, but from already reviewed public ExoFOP NEB notes: not fully blind survey sampling.",
            "A single TIC named in an NEB source note and present in public nearby astrometry does NOT prove the ground-observed eclipse was in that particular neighbor.",
            "Exact first SPOC two-minute sector per star was frozen before this experiment; no choosing favorable target sectors after seeing results.",
            "Original public TOI ephemerides were not refitted; their possible period mismatch and finite source sector coverage may cause missing real dips.",
            "Repeated event orbits within a source are not distinct stars; any between-source p/CI uses only independent host TICs, not events.",
            "Neither original NASA ExoMiner++ weights nor pretrained mission scores were altered, and no new planets or validated NASA classifier accuracy is claimed."
        ]
    }
    (out/"five_frozen_NEB_new_TESS_SPOC_host_original_WCS_centroid_results.json").write_text(
        json.dumps(report,indent=2,default=str)+"\n")
    if good:
        fig,ax=plt.subplots(figsize=(10,4.8))
        names=[f"TOI {r['TOI']}" for r in good]
        raw=[r["true_original_event_results"]["raw_median_vector_angular_difference_away_neighbor_deg"] for r in good]
        corrected=[r["true_original_event_results"]["pointing_subtracted_median_vector_angular_difference_away_neighbor_deg"] for r in good]
        x=np.arange(len(good));width=.36
        ax.bar(x-width/2,raw,width,label="Raw MOM_CENTR")
        ax.bar(x+width/2,corrected,width,label="Experimental MOM_CENTR - POS_CORR")
        ax.set(xticks=x,xticklabels=names,ylim=(0,180),
               ylabel="Median vector angular mismatch (degrees)",
               title="Five original TESS host candidates: source-level directional comparison")
        ax.legend(frameon=False)
        fig.text(.5,.015,"Exploratory source-note association only, not verified eclipsing-source truth",ha="center",fontsize=9)
        fig.tight_layout(rect=[0,.04,1,1])
        fig.savefig(out/"five_new_source_hosts_original_WCS_direction_angle_comparison.png",dpi=180)
        plt.close(fig)
    print("SOURCE_LEVEL_RESULT",json.dumps({
        "attempted_new_host_TICs":len(targets),
        "processed_source_stars":report["source_host_stars_with_usable_original_data"],
        "evaluable_source_direction_hosts":len(good),
        "statistics":report["star_level_directional_statistics"],
        "validated_offtarget_nebs":0
    }),flush=True)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--frozen-source-manifest",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--working",required=True)
    a=p.parse_args()
    run(a.frozen_source_manifest,a.out,a.working)
