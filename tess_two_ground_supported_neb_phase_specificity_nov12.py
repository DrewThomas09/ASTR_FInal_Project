"""Physical-away-direction phase-specificity on two independently positioned ground-aperture eclipses.

Inputs are *already preserved* original TESS SPOC five-host signed same-event
source JSON and independent original ExoFOP actual ground AIJ/WCS physical
source association, not newly tuned periods, scores or TESS positions.

At each of the originally frozen ±P/4 phase controls, compare original
moment-centroid median vector projected onto the *physical* away-from-neighbor
direction (an off-target fading object moves the blended centroid away).
This is two selected post-hoc cases, one with only two original TESS events;
zero classifier accuracy or generalizable source-localization claims.
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


GROUND_AUDITED_HOSTS={382437043:382437045,264303333:1884344804}
FIXED_PHASES=(-.25,.25)


def vector_projection_away(vector,neighbor_vector):
    v=np.asarray(vector,dtype=float)
    n=np.asarray(neighbor_vector,dtype=float)
    if v.shape!=(2,) or n.shape!=(2,) or not np.isfinite(v).all() or not np.isfinite(n).all():
        raise ValueError("Invalid original sky-to-CCD vectors")
    length=float(np.hypot(*n))
    if length<=0:raise ValueError("No physical neighbor direction")
    return float(-np.dot(v,n)/length)


def original_source_projected_phases(tess_row):
    neighbor=tess_row["original_external_neighbor_in_TESS_WCS"]
    if neighbor["catalog_sky_geometry_consistent_with_TPF_target_position"] is not True:
        raise ValueError("Original TESS TPF source sky WCS geometry inconsistent with external catalog")
    vector=neighbor["target_to_neighbor_CCD_pixel_vector"]
    true=tess_row["true_original_event_results"]
    if "usable_paired_original_events" not in true:
        raise ValueError("Original actual event count absent")
    controls=tess_row["same_original_source_quarter_phase_controls"]
    if len(controls)!=2 or tuple(float(x["phase_offset_from_original_ephemeris_in_P"]) for x in controls)!=FIXED_PHASES:
        raise ValueError("Original controls not the exact frozen ±P/4 time shifts")
    payload={"original_observed_true_complete_windows":int(true["usable_paired_original_events"]),
             "all_original_fixed_phase_controls":[],"true_signal":{}}
    for mode in ("raw","pointing_subtracted"):
        v=true.get(mode+"_median_signed_vector_pixels")
        payload["true_signal"][mode+"_centroid_signed_away_projection_pixels"]=(
            vector_projection_away(v,vector) if v is not None else None)
        payload["true_signal"][mode+"_median_centroid_vector_norm_pixels"]=true.get(
            mode+"_median_vector_amplitude_pixels")
        payload["true_signal"][mode+"_angular_mismatch_away_neighbor_deg"]=true.get(
            mode+"_median_vector_angular_difference_away_neighbor_deg")
    payload["true_signal"]["median_original_PDCSAP_local_flux_depth"]=true.get(
        "median_PDCSAP_local_depth")
    payload["true_signal"]["n_actual_genuine_positive_flux_event_windows"]=true.get(
        "n_observed_events_with_positive_PDCSAP_depth")
    for c in controls:
        sci=c["control_source_results"]
        row={"original_frozen_phase_offset_in_orbital_period":float(
            c["phase_offset_from_original_ephemeris_in_P"]),
            "original_paired_phase_control_windows":int(sci["usable_paired_original_events"]),
            "positive_flux_phase_control_windows":int(sci.get(
                "n_observed_events_with_positive_PDCSAP_depth",0)),
            "median_local_PDCSAP_photometric_depth":sci.get("median_PDCSAP_local_depth")}
        for mode in ("raw","pointing_subtracted"):
            vec=sci.get(mode+"_median_signed_vector_pixels")
            row[mode+"_centroid_signed_away_projection_pixels"]=(
                vector_projection_away(vec,vector) if vec is not None else None)
            row[mode+"_angular_mismatch_away_neighbor_deg"]=sci.get(
                mode+"_median_vector_angular_difference_away_neighbor_deg")
        payload["all_original_fixed_phase_controls"].append(row)
    # All 3 windows criterion was precommitted for the original five-host study;
    # TOI 1223 with two original event windows remains descriptive/ineligible.
    eligibility=(true["usable_paired_original_events"]>=3 and
                 all(c["original_paired_phase_control_windows"]>=3 for c in
                     payload["all_original_fixed_phase_controls"]))
    payload["minimum_three_true_and_each_fixed_phase_control_for_source_level_summary"]=eligibility
    for mode in ("raw","pointing_subtracted"):
        null=[c[mode+"_centroid_signed_away_projection_pixels"]
              for c in payload["all_original_fixed_phase_controls"]]
        trueproj=payload["true_signal"][mode+"_centroid_signed_away_projection_pixels"]
        payload[mode+"_true_minus_pooled_phase_control_signed_away_excess_pixels"]=(
            float(trueproj-np.median(null)) if
            trueproj is not None and all(x is not None for x in null)
            else None)
    x=payload["pointing_subtracted_true_minus_pooled_phase_control_signed_away_excess_pixels"]
    y=payload["raw_true_minus_pooled_phase_control_signed_away_excess_pixels"]
    payload["pointing_correction_gain_in_true_phase_specific_signed_away_projection_pixels"]=(
        float(x-y) if x is not None and y is not None else None)
    return payload


def run(tess_results,ground_WCS,ground_flux,out):
    original_tess=Path(tess_results).read_bytes()
    original_ground_WCS=Path(ground_WCS).read_bytes()
    original_ground_flux=Path(ground_flux).read_bytes()
    source=json.loads(original_tess)
    g=json.loads(original_ground_WCS)
    phot=json.loads(original_ground_flux)
    if source["exact_new_host_star_count_attempted"]!=5:
        raise ValueError("Original five-host TESS source selection changed")
    sky_rows={int(x["host_TIC_ID"]):x for x in g["original_sky_source_records"]}
    flux_rows={int(x["TIC_ID"]):x for x in phot["original_reported_cases"]}
    tess_rows={int(x["TIC_ID"]):x for x in source["all_original_source_results"]}
    if set(GROUND_AUDITED_HOSTS)-set(sky_rows)|set(GROUND_AUDITED_HOSTS)-set(flux_rows):
        raise ValueError("Original two physical ground aperture TIC results missing")
    output=[]
    for host,neighbor in GROUND_AUDITED_HOSTS.items():
        sk=sky_rows[host];flux=flux_rows[host];tess=tess_rows[host]
        if sk.get("status")!="audited" or sk.get(
            "original_ground_reported_neighbor_aperture_matches_external_TIC_within_fixed_5arcsec") is not True or sk.get(
            "original_ground_target_T1_matches_TESS_target_within_fixed_8arcsec") is not True:
            raise ValueError("Original ground aperture sky source is not physically catalog-position crosschecked")
        if sk["original_external_neighbor_candidate_TIC_ID"]!=neighbor or tess[
            "external_note_named_neighbor_candidate_TIC"]!=neighbor:
            raise ValueError("Changed original source or neighbor physical TIC")
        if flux["reported_neighbor_aperture_result"]["status"]!="measured_original_ground_AIJ_aperture" or flux[
            "reported_neighbor_aperture_result"]["measured_depth_ppt"]<=0:
            raise ValueError("No actual positive time-resolved original ground neighbor eclipse measurement")
        rec={
            "TIC_ID":host,"TOI":tess["TOI"],"real_ground_aperture_external_neighbor_TIC":neighbor,
            "original_ground_aperture_to_TIC_sky_offset_arcsec":sk[
                "original_ground_reported_neighbor_aperture_sky_offset_arcsec"],
            "actual_original_ground_aperture_measured_dip_ppt":flux[
                "reported_neighbor_aperture_result"]["measured_depth_ppt"],
            "ground_source_aperture_original_image_catalog_consistent":True,
            "original_selected_sector":tess["original_SPOC_sector"],
            "original_TESS_direct_same_event_and_quarter_phase_comparison":
                original_source_projected_phases(tess),
            "original_TESS_reanalysis_note":"Original fixed first sector, no raw-source re-download and no event-time refit.",
            "original_ground_truth_reanalysis_limit":"Observer-reduced ground photometry and image WCS; independent CCD photometric re-reduction not done"
        }
        print("TRUTH_SUPPORTED_OFFTARGET_PHASE_DIRECTION",json.dumps({
            "TIC":host,"TOI":tess["TOI"],
            "ground_neighbor_TIC":neighbor,
            "original_TESS_actual_events":rec[
                "original_TESS_direct_same_event_and_quarter_phase_comparison"][
                "original_observed_true_complete_windows"],
            "phase_specific_signed_away_projection":
                rec["original_TESS_direct_same_event_and_quarter_phase_comparison"]
        }),flush=True)
        output.append(rec)
    eligible=[r for r in output if r["original_TESS_direct_same_event_and_quarter_phase_comparison"][
       "minimum_three_true_and_each_fixed_phase_control_for_source_level_summary"]]
    report={
        "purpose":"Reassess original raw versus pointing-adjusted TESS signed source-direction projection specifically at two actual ground-aperture and sky TIC supported eclipse candidates, against original fixed ±P/4 pseudo-event phases",
        "n_physically_ground_aperture_sky_corroborrated_original_NEBS":len(output),
        "original_TESS_five_host_source_sha256":hashlib.sha256(original_tess).hexdigest(),
        "original_ground_sky_WCS_source_sha256":hashlib.sha256(original_ground_WCS).hexdigest(),
        "original_ground_numerical_photometry_results_source_sha256":hashlib.sha256(original_ground_flux).hexdigest(),
        "original_two_ground_source_records":output,
        "eligible_host_stars_under_original_3_actual_and_3_each_control_windows":len(eligible),
        "descriptive_median_gain_on_eligible_whole_host_only_pixels":float(np.median([
            r["original_TESS_direct_same_event_and_quarter_phase_comparison"][
            "pointing_correction_gain_in_true_phase_specific_signed_away_projection_pixels"]
            for r in eligible])) if eligible else None,
        "scientific_limitations":[
            "The two physically supported neighbor cases were selected after prior observer and source inspection, not a new blinded statistical holdout.",
            "A signed away-neighbor projection is a simplified two-source moment-centroid physical proxy, not NASA mission PRF difference-image localization.",
            "Original phase controls may contain other transits, activity or instrumental events; true-minus-control comparison is exploratory.",
            "TOI1223 had only two genuine original first-sector SPOC complete events, so it cannot be promoted to an eligible independent host-level replicate.",
            "The test uses no new original TESS sectors, arbitrary event phase optimization, changed ExoMiner network scores, or synthetic astronomical observations.",
            "No planet/false-positive classifier accuracy or reliable generic physical source localization effect can be inferred from one or two source units."
        ]
    }
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/"two_ground_sky_corroborrated_neb_original_TESS_phase_specific_signed_away_projected_vectors.json").write_text(
        json.dumps(report,indent=2)+"\n")
    fig,ax=plt.subplots(figsize=(9,4.7))
    labels=[];raws=[];correcteds=[]
    for r in output:
        s=r["original_TESS_direct_same_event_and_quarter_phase_comparison"]
        labels.append("TOI "+r["TOI"])
        raws.append(s["raw_true_minus_pooled_phase_control_signed_away_excess_pixels"])
        correcteds.append(s["pointing_subtracted_true_minus_pooled_phase_control_signed_away_excess_pixels"])
    x=np.arange(len(labels))
    ax.bar(x-.19,raws,.38,label="MOM_CENTR raw")
    ax.bar(x+.19,correcteds,.38,label="MOM_CENTR - POS_CORR")
    ax.axhline(0,color="gray",linewidth=.8)
    ax.set(xticks=x,xticklabels=labels,
        ylabel="Event − quarter-phase-control away-neighbor projection, CCD pixels",
        title="Actual ground-observed nearby eclipse star candidates; original TESS signed geometry")
    ax.legend(frameon=False)
    fig.text(.5,.012,"TOI1223 is under original 3-event eligibility: descriptive only; 2 pre-inspected source cases",
             ha="center",fontsize=8)
    fig.tight_layout(rect=[0,.04,1,1])
    fig.savefig(out/"original_ground_supported_two_NEBS_TESS_true_minus_phase_control_signed_away.png",dpi=180)
    plt.close(fig)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-five-TESS",required=True)
    p.add_argument("--original-ground-sky",required=True)
    p.add_argument("--original-ground-flux",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.original_five_TESS,a.original_ground_sky,a.original_ground_flux,a.out)
