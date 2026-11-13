"""Preserve full NASA SPOC multi-sector PRF source-position discordance on two
original ground-sky-supported nearby eclipsing binaries, with five confirmed
planet first-sector controls.

All NASA PRF numerical input comes from SHA-verified original official DVR XML
previously associated with the published TOI via period, epoch, and explicit
TOI-ID checks; all source and first-sector choices were frozen beforehand.

Later sectors of a multi-sector DV report are POST-HOC, not replacements of
original first-sector matched TESS moment centroid or target pixel results.
Sectors are not independent stars and no p-values are calculated.
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

TWO_GROUND={382437043:"1223.01",264303333:"2250.01"}
KNOWN_CONTROLS={36352297:"CoRoT-1 b",134537478:"KELT-14 b",
 232038798:"WASP-168 b",452808876:"WASP-82 b",455135327:"HAT-P-30 b"}
MAX_TIC_HEADER_REFERENCE_MISMATCH_ARCSEC=8.


def first_unique_matched_candidate(record):
    original=record.get("exact_original_SPOC_TCE_and_PRF_results")
    if not original or not original.get("only_one_TOI_compatible_TCE"):
        return None
    matched=[x for x in original["official_original_NASA_SPOC_TCE_and_sector_PRF_diagnostics_all"]
             if x["NASA_DV_TCE_unique_candidate_eligibility_prior_to_examining_PRF"]]
    return matched[0] if len(matched)==1 else None


def physical_fit_quality(original_row,require_neighbor):
    """No false 0,-1 MAST PRF sentinel, no weird unrelated sky reference."""
    near=original_row.get("original_mission_PRF_source_to_original_ground_reported_neighbor_arcsec")
    host=original_row.get("original_mission_PRF_source_to_original_external_host_arcsec")
    target=original_row.get("original_DV_catalog_TIC_reference_to_original_external_NASA_host_arcsec")
    offsets=original_row.get("original_official_SPOC_DV_TIC_reference_offsets",{})
    sky=offsets.get("skyOffset",{})
    uncertainty=sky.get("uncertainty")
    return bool(
        original_row.get("original_PRF_ra_dec_uncertainties_valid")
        and host is not None and np.isfinite(host)
        and (not require_neighbor or (near is not None and np.isfinite(near)))
        and target is not None and np.isfinite(target)
        and target<=MAX_TIC_HEADER_REFERENCE_MISMATCH_ARCSEC
        and uncertainty is not None and np.isfinite(uncertainty) and uncertainty>0
        and original_row.get("original_DV_numberOfTransits") is not None
        and original_row["original_DV_numberOfTransits"]>0
    )


def source_all_sector_audit(original_record,with_neighbor):
    tce=first_unique_matched_candidate(original_record)
    if tce is None:
        return {"TIC_ID":original_record["original_source_host_TIC"],
                "TOI":original_record["original_public_ExoFOP_TOI"],
                "status":"no_unique_original_TOI_ephemeris_matched_official_TCE",
                "all_original_DV_sectors":[]}
    allrows=tce["original_DV_all_sector_diff_image_fit_results"]
    first=int(original_record["source_original_SPOC_2min_first_sector"])
    if len(allrows)!=len({int(x["original_DV_sector"]) for x in allrows}):
        # Do not arbitrarily collapse two target tables on same sector.
        duplicate=True
    else:
        duplicate=False
    output=[]
    for x in allrows:
        valid=physical_fit_quality(x,with_neighbor)
        host=x.get("original_mission_PRF_source_to_original_external_host_arcsec")
        near=x.get("original_mission_PRF_source_to_original_ground_reported_neighbor_arcsec")
        label=(("closer_to_ground_neighbor" if near<host else "closer_to_target_host")
               if valid and with_neighbor and host is not None and near is not None
               else "not_a_ground_neighbor_case" if valid and not with_neighbor else "unusable_official_PRF_fit")
        output.append({
            "original_NASA_DV_observed_sector":int(x["original_DV_sector"]),
            "real_original_DV_TCE_transits_used_this_sector":x["original_DV_numberOfTransits"],
            "this_is_preselected_original_first_SPOC_two_min_sector":int(x["original_DV_sector"])==first,
            "original_PRF_position_valid_and_independent_target_header_consistent":valid,
            "original_DV_tic_source_SKY_offset_arcsec":x["original_official_SPOC_DV_TIC_reference_offsets"]["skyOffset"]["value"],
            "original_DV_tic_source_SKY_offset_uncertainty_arcsec":x["original_official_SPOC_DV_TIC_reference_offsets"]["skyOffset"]["uncertainty"],
            "original_DV_PRF_source_sep_from_independent_TESS_host_arcsec":host if valid else None,
            "original_DV_PRF_source_sep_from_independent_ground_reported_neighbor_arcsec":near if valid else None,
            "physical_closest_original_catalog_source":label,
            "invalid_original_SPOC_PRF_fit_is_NOT_assigned_zero_sky_position":not valid,
            "original_DV_control_image_offsets":x["original_official_SPOC_DV_OUT_OF_TRANSIT_offsets"],
            "original_DV_PRF_original_RA_Dec_source_record":x["original_DIFFERENCE_IMAGE_PRF_fit"]
        })
    output.sort(key=lambda z:z["original_NASA_DV_observed_sector"])
    valid=[x for x in output if x["original_PRF_position_valid_and_independent_target_header_consistent"]]
    official_first=[x for x in output if x["this_is_preselected_original_first_SPOC_two_min_sector"]]
    result={
        "TIC_ID":original_record["original_source_host_TIC"],
        "TOI":original_record["original_public_ExoFOP_TOI"],
        "source_group":original_record["source_group"],
        "original_NASA_DV_xml_source_SHA256":original_record["original_report_file_SHA256"],
        "original_NASA_DV_xml_report_sector_range":[
            original_record["official_DV_report_start_sector"],
            original_record["official_DV_report_end_sector"]],
        "original_source_frozen_first_sector":first,
        "original_match_to_ExoFOP_TOI_both_period_and_phase":True,
        "predeclared_one_source_first_sector_preserved_separately":True,
        "original_DV_sectors_record_count_all_including_no_or_invalid_PRF":len(output),
        "duplicate_sector_target_tables_preserved_not_collapsed":duplicate,
        "all_original_DV_sectors":output,
        "number_DV_sectors_with_usable_PRF_source_fit":len(valid),
        "original_first_sector_exactly_one_record":len(official_first)==1,
        "original_first_sector_PRF_usable":bool(
            len(official_first)==1 and official_first[0][
                "original_PRF_position_valid_and_independent_target_header_consistent"]),
        "original_first_sector_PRF_source_label":(official_first[0][
                "physical_closest_original_catalog_source"] if len(official_first)==1
                else "first_sector_missing_or_duplicated")
    }
    if with_neighbor:
        result.update({
            "original_DV_sectors_with_valid_fits_closer_to_ground_neighbor":sum(
                x["physical_closest_original_catalog_source"]=="closer_to_ground_neighbor" for x in valid),
            "original_DV_sectors_with_valid_fits_closer_to_primary":sum(
                x["physical_closest_original_catalog_source"]=="closer_to_target_host" for x in valid),
            "original_DV_sectors_with_invalid_PRF_or_source_QC":len(output)-len(valid),
            "no_source_label_classification_or_sector_significance_inferred":True
        })
    else:
        result["first_sector_PRF_separation_from_confirmed_planet_host_arcsec"]=(
            official_first[0]["original_DV_PRF_source_sep_from_independent_TESS_host_arcsec"]
            if len(official_first)==1 else None)
    result["status"]="all_original_sector_results_preserved"
    return result


def run(verified_prf_json,out):
    p=Path(verified_prf_json)
    data=json.loads(p.read_bytes())
    if not data["diagnostic_only_not_new_ground_truth"] or data["original_sources_attempted"]!=7:
        raise ValueError("Not original seven-source official PRF TCE-ephemeris matched audit")
    rows={int(x["original_source_host_TIC"]):x for x in data[
        "all_original_NASA_DV_host_TCE_and_per_sector_PRF_source_records"]}
    if set(rows)!=set(TWO_GROUND)|set(KNOWN_CONTROLS):
        raise ValueError("Official original source cohort seven TIC identities not preserved")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    results=[]
    for tic in sorted(rows):
        row=source_all_sector_audit(rows[tic],tic in TWO_GROUND)
        results.append(row)
        if tic in TWO_GROUND and row["status"]=="all_original_sector_results_preserved":
            name=TWO_GROUND[tic]
            xs=[];host=[];near=[]
            for r in row["all_original_DV_sectors"]:
                if not r["original_PRF_position_valid_and_independent_target_header_consistent"]:
                    continue
                xs.append(r["original_NASA_DV_observed_sector"])
                host.append(r["original_DV_PRF_source_sep_from_independent_TESS_host_arcsec"])
                near.append(r["original_DV_PRF_source_sep_from_independent_ground_reported_neighbor_arcsec"])
            if xs:
                fig,ax=plt.subplots(figsize=(9.3,5))
                ax.scatter(xs,host,marker="o",label="NASA PRF source → original primary TIC")
                ax.scatter(xs,near,marker="x",label="NASA PRF source → independently ground-matched neighbor TIC")
                for x,y in zip(xs,host):ax.plot([x,x],[y,near[xs.index(x)]],color="gray",alpha=.3)
                ax.axvline(row["original_source_frozen_first_sector"],linestyle="--",color="gray",
                           label="Original frozen first SPOC 2-minute sector")
                ax.set(xlabel="Original NASA SPOC DV observing sector",
                       ylabel="Official mission PRF fitted transit source sky separation, arcsec",
                       title=f"TOI-{name}: original official NASA DV per-sector PRF source disagreement")
                ax.legend(fontsize=9,frameon=False)
                fig.text(.5,.01,"Original valid PRF sectors only; sectors not independent stars and no nearest-star accuracy inferred",
                         ha="center",fontsize=8)
                fig.tight_layout(rect=[0,.04,1,1])
                fig.savefig(out/f"TOI_{name}_original_NASA_DV_allsector_PRF_target_vs_ground_neighbor.png",dpi=180)
                plt.close(fig)
        print("ORIGINAL_OFFICIAL_SPOC_DV_PER_SECTOR_SOURCE_DISCORDANCE",
              json.dumps(row),flush=True)
    ground=[r for r in results if r["TIC_ID"] in TWO_GROUND]
    known=[r for r in results if r["TIC_ID"] in KNOWN_CONTROLS]
    report={
        "experiment":"Source-fixed original 2 off-target ground-sky-supported eclipse systems and 5 separately confirmed planet hosts; official NASA mission SPOC DV per-sector PRF source quality and discordance study",
        "original_NASA_SPOC_DV_ephemeris_matched_7source_SHA256":hashlib.sha256(
            p.read_bytes()).hexdigest(),
        "actual_distinct_original_TIC_host_count":7,
        "two_original_ground_supported_offtarget_candidate_sources":ground,
        "five_independent_catalog_confirmed_planet_host_PRF_controls":known,
        "first_sector_original_target_not_replaced_with_later_sector":True,
        "per_sector_counts_are_NOT_independent_source_stars":True,
        "can_this_determine_NASA_ExoMiner_accuracy_or_a_new_planet":False,
        "interpretation_limits":[
            "Original NASA SPOC official fitted difference-image PRF coordinates are from an independently mission-produced DV XML, unlike our simple positive-only pixel difference center. Both can fail at faint blended sources.",
            "The two previously ground-aperture-sky corroborated off-target neighbors are fixed before the report: later DV sectors are displayed as exploratory instrument/geometry stability checks, NOT first-sector source replacements.",
            "Each source's official TCE is matched to the original independent ExoFOP TOI period and epoch before centroid use. The XML can lack TOI ID labels in old reports, and matching does not independently confirm ground eclipse identity.",
            "A missing official PRF position reported as value=0,uncertainty=-1 is invalid; never interpret as sky origin.",
            "Sectors are repeated observations of the same host and of a blended TESS pixel response, so do not perform a sector-level sign test or claim independent planet/false-positive localization accuracy.",
            "A fitted PRF source position nearer the original TIC primary does NOT refute separate original ground observer aperture dimming in a named neighbor; conversely, closer-to-neighbor sectors do not validate a universal correction.",
            "Large confirmed-planet source offsets can arise from blending, uncertainties, PRF assumptions and catalog astrometric/centroid reference mismatch. This source control sample is not independently ground-imaged.",
            "All real original mission per-sector records and data quality failures are preserved without favorable-sector exclusion, TCE reassignment or changes to NASA's ExoMiner++ pretrained scores."
        ]
    }
    (out/"original_two_ground_NEBS_full_NASA_SPOC_DV_multisector_PRF_source_discordance_and_five_planet_controls.json").write_text(
        json.dumps(report,indent=2,default=str)+"\n")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-seven-NASA-DV-PRF-results",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.original_seven_NASA_DV_PRF_results,a.out)
