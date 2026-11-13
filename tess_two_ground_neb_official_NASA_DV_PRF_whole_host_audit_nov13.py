"""Source-level synthesis of real original NASA SPOC DV XML PRF centroid runs.

A source-only inventory was frozen before inspecting official NASA mission PRF
offsets. All 12 real original DVR XML files were then parsed with exact
original TOI TCE period and phase matching before any centroid comparison.

Six overlapping mission search runs per host are REPEATED REDUCTIONS of the
SAME source and SAME original first-sector difference image, not independent
new ground source truth, mission accuracy denominators or statistical trials.
Never pick a favorable processing campaign; earliest is primary even if invalid.
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HOSTS={382437043:"1223.01",264303333:"2250.01"}
FIRST_FROZEN_SECTORS={382437043:1,264303333:14}
EXPECTED_DV_ORIGINAL_RUNS_PER_HOST=6


def summarize_official_source(host):
    tic=int(host["TIC_ID"])
    if tic not in HOSTS or host["TOI"]!=HOSTS[tic]:
        raise ValueError("Original official source TIC/TOI was substituted")
    if int(host["original_frozen_TESS_SPOC_sector"])!=FIRST_FROZEN_SECTORS[tic]:
        raise ValueError("Original first sector changed after viewing NASA PRF")
    runs=host["source_archive_records_all_no_selection_on_offset"]
    if len(runs)!=EXPECTED_DV_ORIGINAL_RUNS_PER_HOST:
        raise ValueError("Expected 6 genuine NASA SPOC XML mission search runs per frozen host")
    serials=[]
    for r in runs:
        p=r["original_DV_XML_product"]
        if int(p["TIC_ID"])!=tic or int(p["original_DV_search_start_sector"])!=FIRST_FROZEN_SECTORS[tic]:
            raise ValueError("NASA official DV source campaign wrong host TIC or frozen starting sector")
        s={
            "source_filename":p["product_filename"],
            "NASA_DV_original_search_from_sector":int(p["original_DV_search_start_sector"]),
            "NASA_DV_original_search_to_sector":int(p["original_DV_search_end_sector"]),
            "original_run_order_from_frozen_source_inventory":len(serials)+1,
            "original_DV_original_XML_SHA256":r.get(
                "original_DV_XML_source_provenance",{}).get("original_source_SHA256"),
            "original_DV_parsing_status":r["original_DV_XML_source_processing_status"],
            "n_ephemeris_matched_original_TOI_TCEs":r.get("original_DV_ephemeris_matched_TCE_count_before_centroid",0),
            "n_valid_official_FIRST_SECTOR_difference_image_centroids":0,
            "quality_or_missingness_not_suppressed":None,
        }
        matches=r.get("original_DV_frozen_sector_PRF_differences_for_only_ephemeris_matched_TCEs",[])
        if len(matches)>1:
            raise ValueError("Ambiguous original TCE match not allowed to become source-truth")
        if (s["n_ephemeris_matched_original_TOI_TCEs"]!=1 or
            r["original_DV_XML_source_processing_status"]!="processed_original" or
            len(matches)!=1):
            s["quality_or_missingness_not_suppressed"]="No unique authentic period-phase-matched TCE, or malformed NASA first-sector source"
            serials.append(s)
            continue
        original_tce=matches[0]
        s["original_TCE_period_days"]=float(original_tce[
            "original_DV_original_TOI_ephemeris_match"]["original_NASA_DV_candidate_period_days"])
        s["original_TOI_match_time_phase_residual_days"]=float(original_tce[
            "original_DV_original_TOI_ephemeris_match"]["DV_to_original_TOI_wrapped_phase_difference_days"])
        rows=original_tce["original_DV_first_frozen_sector_difference_image_result_rows"]
        if len(rows)!=1:
            s["quality_or_missingness_not_suppressed"]=(
                f"Expected exactly one first-sector DI PRF result, found {len(rows)}")
            serials.append(s)
            continue
        first=rows[0]
        if int(first["original_DV_image_sector"])!=FIRST_FROZEN_SECTORS[tic]:
            raise ValueError("NASA difference-image original sector identity changed")
        qual=first["original_DV_image_quality_metric"]
        s["original_NASA_DV_quality_metric_value_as_reported"]=qual.get("value")
        s["original_NASA_DV_PRF_fit_attempted"]=qual.get("attempted")
        s["original_NASA_DV_PRF_fit_valid_as_reported"]=qual.get("valid")
        s["n_valid_official_FIRST_SECTOR_difference_image_centroids"]=int(
            bool(first["original_DV_first_sector_PRF_physically_interpretable"]))
        if s["n_valid_official_FIRST_SECTOR_difference_image_centroids"]==1:
            if qual.get("valid") is not True or qual.get("attempted") is not True:
                raise ValueError("Invalid official NASA quality flag falsely marked as valid")
            dh=float(first["original_NASA_DV_PRF_to_primary_host_arcsec"])
            dn=float(first["original_NASA_DV_PRF_to_ground_observed_neighbor_arcsec"])
            s["original_valid_NASA_DI_PRF_to_target_arcsec"]=dh
            s["original_valid_NASA_DI_PRF_to_ground_neighbor_arcsec"]=dn
            s["original_valid_PRF_nominally_closer_to_target"]=bool(dh<dn)
            s["original_valid_PRF_nominally_closer_to_ground_neighbor"]=bool(dn<dh)
            s["original_valid_PRF_angular_separation_target_vs_neighbor_arcsec"]=float(
                first["original_NASA_DV_PRF_source_target_to_neighbor_separation_arcsec"])
            s["original_NASA_PRF_ra_dec_original_fit_uncertainty_degrees"]=first[
                "original_DV_PRF_sky_centroid_angular_uncertainty_RA_Dec_degrees_not_correlated"]
            s["quality_or_missingness_not_suppressed"]="PRF attempted and official valid flag; centroid coordinates have reported original nonnegative formal uncertainties"
        else:
            s["quality_or_missingness_not_suppressed"]=(
                "Original NASA DV PRF invalid/unavailable; do not infer a physical location")
        serials.append(s)
    ends=[x["NASA_DV_original_search_to_sector"] for x in serials]
    if ends!=sorted(ends) or len(ends)!=len(set(ends)):
        raise ValueError("NASA source-only frozen search run order/identity changed")
    eligible=[x for x in serials if x["n_valid_official_FIRST_SECTOR_difference_image_centroids"]==1]
    primary=serials[0] # Frozen earliest archived campaign, regardless of quality
    return {
        "TIC_ID":tic,"TOI":HOSTS[tic],
        "original_first_sector":FIRST_FROZEN_SECTORS[tic],
        "n_original_NASA_SPOC_DV_search_runs_all":len(serials),
        "n_original_NASA_DV_runs_with_matching_TCE_period_phase":sum(
            x["n_ephemeris_matched_original_TOI_TCEs"]==1 for x in serials),
        "n_original_official_valid_PRF_results":len(eligible),
        "n_original_official_invalid_PRF_results":len(serials)-len(eligible),
        "number_of_independent_astrophysical_host_star_units":1,
        "n_valid_PRF_nominally_closer_to_primary":sum(x[
            "original_valid_PRF_nominally_closer_to_target"] for x in eligible),
        "n_valid_PRF_nominally_closer_to_ground_observed_neighbor":sum(x[
            "original_valid_PRF_nominally_closer_to_ground_neighbor"] for x in eligible),
        "primary_PRESELECTED_earliest_DV_search_run_even_if_invalid":primary,
        "all_original_SPOC_DV_XML_campaigns_no_outcome_based_pick":serials,
        "official_SPOC_DV_valid_PRF_source_distance_changes_across_search_runs_not_independent":True,
    }


def run(original_XML_PRF_artifact,out):
    path=Path(original_XML_PRF_artifact)
    original=path.read_bytes()
    report=json.loads(original)
    if (report.get("authentic_original_SPOC_DV_XML_products_queried")!=12 or
        report.get("exact_physical_ground_NEBS_attempted")!=2):
        raise ValueError("Original NASA SPOC source audit missing 12 authentic exact TIC original XML files")
    stars=report["all_original_host_source_DV_XML_TCE_and_PRF_results"]
    if {int(x["TIC_ID"]) for x in stars}!=set(HOSTS):
        raise ValueError("Unexpected original physical ground TIC source")
    summarized=[summarize_official_source(s) for s in stars]
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for rec in summarized:
        tic=rec["TIC_ID"]
        allruns=rec["all_original_SPOC_DV_XML_campaigns_no_outcome_based_pick"]
        valid=[x for x in allruns if x["n_valid_official_FIRST_SECTOR_difference_image_centroids"]==1]
        fig,ax=plt.subplots(figsize=(8.8,4.7))
        xs=[x["NASA_DV_original_search_to_sector"] for x in valid]
        host=[x["original_valid_NASA_DI_PRF_to_target_arcsec"] for x in valid]
        neb=[x["original_valid_NASA_DI_PRF_to_ground_neighbor_arcsec"] for x in valid]
        if xs:
            ax.plot(xs,host,"o-",label="To primary target catalog sky position")
            ax.plot(xs,neb,"s-",label="To original ground-reported neighbor TIC sky position")
        invalid=[x for x in allruns if x not in valid]
        for x in invalid:
            ax.axvline(x["NASA_DV_original_search_to_sector"],alpha=.15,linestyle=":")
            ax.annotate("invalid",xy=(x["NASA_DV_original_search_to_sector"],0),
                        xytext=(0,4),textcoords="offset points",
                        ha="center",fontsize=8)
        ax.set(
            xticks=[x["NASA_DV_original_search_to_sector"] for x in allruns],
            xlabel="End of SPOC mission DV search (all include frozen first sector)",
            ylabel="Official source PRF centroid to sky position (arcsec)",
            title=f"TOI {rec['TOI']}: real NASA SPOC first-sector difference-image PRF")
        ax.legend(frameon=False,fontsize=9)
        fig.text(.5,.015,"Original official quality-flag-invalid results retained, not plotted. Repeated reductions, not independent source samples.",
                 ha="center",fontsize=8)
        fig.tight_layout(rect=[0,.04,1,1])
        fig.savefig(out/f"TOI{rec['TOI']}_original_NASA_DV_first_sector_PRF_to_primary_vs_ground_neighbor.png",dpi=180)
        plt.close(fig)
    result={
        "scientific_question":"When the original NASA SPOC TCE period and transit phase agree with actual ExoFOP TOIs whose neighbor eclipses were measured on the ground, does the official first-sector PRF difference-image centroid nominally favor the primary target or that externally ground-corroborrated neighboring TIC?",
        "original_authentic_NASA_DV_12_XML_source_analysis_SHA256":hashlib.sha256(original).hexdigest(),
        "n_astrophysical_independent_original_TIC_host_units":len(summarized),
        "n_repeated_original_NASA_DV_XML_mission_processing_runs":sum(
            x["n_original_NASA_SPOC_DV_search_runs_all"] for x in summarized),
        "n_ephemeris_concordant_original_NASA_DV_run_TCEs":sum(
            x["n_original_NASA_DV_runs_with_matching_TCE_period_phase"] for x in summarized),
        "n_official_valid_first_sector_PRF_centroids_across_REPEATED_runs":sum(
            x["n_original_official_valid_PRF_results"] for x in summarized),
        "n_official_invalid_first_sector_PRF_centroids_across_REPEATED_runs":sum(
            x["n_original_official_invalid_PRF_results"] for x in summarized),
        "all_original_official_host_and_run_source_summary":summarized,
        "source_level_conclusion_limitations":[
            "The primary reported result is earliest original source-only frozen MAST DV search campaign for each host, even if its first-sector PRF is invalid. Later source campaigns are sensitivity/traceability only, not favorable result replacement.",
            "Each host remains ONE independent astrophysical source unit; its six official SPOC search runs reuse overlapping years and original first-sector time series, and cannot support a six-sample p-value.",
            "The original NASA TCE is matched on period within 1% and cyclic epoch phase within min(0.15 original orbit, 3 original ExoFOP transit durations) BEFORE opening any PRF centroid.",
            "NASA's official qualityMetric attempted/valid flags and nonnegative centroid RA/Dec uncertainties were required; omitted invalid source locations cannot be treated as zero offsets.",
            "Nominal closer-to-target or closer-to-neighbor PRF distance is not verified astrophysical source classification: original PRF uncertainty and point-spread blending can be large.",
            "Source selection was retrospective to original ground observer reports; source apertures were independently verified on sky but original ground raw flux frames not re-reduced independently.",
            "One original source with only two TPF event images and another with 30; raw pixel-difference localization failed independently and must not be glossed over.",
            "Official NASA SPOC DV PRF model is not the same as the exploratory MOM_CENTR - POS_CORR sidecar; no NASA pretrained ExoMiner++ accuracy, model weights or catalog labels changed."
        ]
    }
    (out/"two_ground_NEBS_official_NASA_DV_12_source_runs_whole_host_quality_and_PRF_audit.json").write_text(
        json.dumps(result,indent=2)+"\n")
    print("ORIGINAL_NASA_PRF_HOST_LEVEL_CONCLUSION",json.dumps({
        "sources":len(summarized),
        "all_original_DV_TCE_period_and_phase_matches":result[
            "n_ephemeris_concordant_original_NASA_DV_run_TCEs"],
        "valid_original_first_sector_PRF_across_repeated_source_runs":result[
            "n_official_valid_first_sector_PRF_centroids_across_REPEATED_runs"],
        "invalid_original_first_sector_PRF":result[
            "n_official_invalid_first_sector_PRF_centroids_across_REPEATED_runs"],
        "whole_independent_ground_eclipse_host_TIC_records":[{
            "TOI":x["TOI"],"host":x["TIC_ID"],
            "n_valid_PRF":x["n_original_official_valid_PRF_results"],
            "n_invalid_PRF":x["n_original_official_invalid_PRF_results"],
            "primary_earliest_run_last_sector":x[
                "primary_PRESELECTED_earliest_DV_search_run_even_if_invalid"][
                "NASA_DV_original_search_to_sector"],
            "primary_earliest_source_first_sector_PRF_valid":x[
                "primary_PRESELECTED_earliest_DV_search_run_even_if_invalid"][
                "n_valid_official_FIRST_SECTOR_difference_image_centroids"]==1,
            "primary_earliest_source_PRF_to_host":x[
                "primary_PRESELECTED_earliest_DV_search_run_even_if_invalid"].get(
                "original_valid_NASA_DI_PRF_to_target_arcsec"),
            "primary_earliest_source_PRF_to_reported_neighbor":x[
                "primary_PRESELECTED_earliest_DV_search_run_even_if_invalid"].get(
                "original_valid_NASA_DI_PRF_to_ground_neighbor_arcsec"),
            "valid_repeated_PRF_closer_to_target":x[
                "n_valid_PRF_nominally_closer_to_primary"],
            "valid_repeated_PRF_closer_to_neighbor":x[
                "n_valid_PRF_nominally_closer_to_ground_observed_neighbor"],
        } for x in summarized]
    }),flush=True)
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-DV-12-XML-results",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.original_DV_12_XML_results,a.out)
