"""Original NASA/MAST SPOC mission Data Validation product discovery for 2 ground
aperture-sky-matched NEBs and 5 separate independently confirmed planet hosts.

These seven TIC, TOI and frozen first-sector source units were fixed in earlier
archived original source manifests. NO DV outcome, fitted source, score, TCE or
neighbor angle is used to replace any source, observation sector or ephemeris.

Official SPOC DV products include DVS (one TCE one-page PDF), DVR (complete
multi-TCE PDF/XML), DVM (mini report PDF) and DVT (DV time-series FITS).
The source-only discovery preserves all target-matched original MAST products,
including runs whose s-start to s-end range excludes frozen first sector;
it makes no claim that a DV TCE must match the original TOI transit.
"""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from tess_two_neb_original_mast_discovery import tablerows,compatible_target

TWO_OFFTARGET={
    382437043:("1223.01",382437045,1),
    264303333:("2250.01",1884344804,14),
}
FIVE_PLANETS={
    134537478:("501.01","KELT-14 b",7),
    36352297:("547.01","CoRoT-1 b",6),
    232038798:("1909.01","WASP-168 b",32),
    455135327:("490.01","HAT-P-30 b",7),
    452808876:("453.01","WASP-82 b",5),
}
DV_TYPES={"DVR":(".xml",".pdf"),"DVS":(".pdf",),"DVM":(".pdf",),
          "DVT":(".fits",)}
SOURCE_PATTERN=re.compile(r"-s(?P<first>[0-9]{4})-s(?P<last>[0-9]{4})-"
                          r"(?P<tic>[0-9]{16})-(?P<rest>.+)_dv[rmst](?:\.xml|\.pdf|\.fits)$",re.I)


def validate_fixed_manifests(frozen_neb,frozen_planets):
    if frozen_neb.get("experiment_id")!="ASTR_FIVE_NEW_NEB_SPOC_SOURCE_BLIND_WCS_EVAL_20261112":
        raise ValueError("Original ground NEB pre-centroid source lock not present")
    if frozen_planets.get("experiment_id")!=(
      "ASTR_NASA_AND_EXOFOP_KP_CONFIRMED_TRANSITING_ON_TARGET_CONTROL_SPOC_SOURCE_FROZEN_NOV12"):
        raise ValueError("Original independent NASA+ExoFOP known-planet source lock not present")
    if frozen_planets.get("original_TESS_centroids_viewed")!=0:
        raise ValueError("Planet source selected after viewing original centroid outcomes")
    rows_neb={int(x["TIC_ID"]):x for x in frozen_neb["source_records"]}
    rows_planets={int(x["TIC_ID"]):x for x in frozen_planets["source_records"]}
    if len(rows_neb)!=5 or len(rows_planets)!=5 or bool(set(rows_neb)&set(rows_planets)):
        raise ValueError("Original locked source cohorts changed")
    output={}
    for tic,(toi,neighbor,sector) in TWO_OFFTARGET.items():
        if tic not in rows_neb:raise ValueError("Original frozen ground source host absent")
        r=rows_neb[tic]
        if (r["TOI"]!=toi or
            int(r["original_neb_named_neighbor_TIC_not_physical_truth"])!=neighbor or
            int(r["selected_first_original_SPOC_2min_sector"])!=sector):
            raise ValueError("Original ground case/neighbor/first-sector source mutated")
        output[tic]={
            "TIC_ID":tic,"TOI":toi,"experiment_group":"prior_ground_aperture_sky_supported_neighbor_eclipse",
            "original_reported_neighbor_TIC":neighbor,
            "source_frozen_first_SPOC_2min_sector":sector,
            "original_ExoFOP_period_days":float(r["original_ExoFOP_period_days"]),
            "original_ExoFOP_epoch_BTJD":float(r["original_ExoFOP_epoch_BTJD"]),
            "original_ExoFOP_duration_days":float(r["original_ExoFOP_duration_days"]),
            "physical_neighbor_ground_support_from_separate_original_WCS_and_lightcurve":True,
            "mission_DV_diagnostic_data_seen_before_source_selection":False
        }
    for tic,(toi,planet,sector) in FIVE_PLANETS.items():
        if tic not in rows_planets:raise ValueError("Original frozen known-planet host absent")
        r=rows_planets[tic]
        if (r["TOI"]!=toi or r["NASA_confirmed_host_alias"]!=planet or
            int(r["selected_first_original_SPOC_2min_sector"])!=sector):
            raise ValueError("Original NASA/ExoFOP known-planet name or sector mutated")
        output[tic]={
            "TIC_ID":tic,"TOI":toi,"experiment_group":"prior_independently_NASA_and_ExoFOP_catalog_confirmed_transiting_planet",
            "official_NASA_confirmed_planet_alias":planet,
            "source_frozen_first_SPOC_2min_sector":sector,
            "original_ExoFOP_period_days":float(r["original_ExoFOP_period_days"]),
            "original_ExoFOP_epoch_BTJD":float(r["original_ExoFOP_epoch_BTJD"]),
            "original_ExoFOP_duration_days":float(r["original_ExoFOP_duration_days"]),
            "mission_DV_diagnostic_data_seen_before_source_selection":False
        }
    if len(output)!=7:
        raise ValueError("Exactly seven immutable source units required")
    return output


def original_SPOC_DV_products(observations,products,tic,first_sector):
    """SPOC original DV only: exact numeric target TIC and exact product file TIC.

    Do not mistake a different nearby aperture target or unrelated HLSP/QLP
    as a NASA SPOC target's mission data validation report.
    """
    allowed={}
    for o in observations:
        if not compatible_target(o.get("target_name"),tic):continue
        if str(o.get("provenance_name","")).strip().upper()!="SPOC":continue
        try:allowed[int(o["obsid"])]=int(o["sequence_number"])
        except (ValueError,KeyError,TypeError):continue
    seen={}
    rejection=Counter()
    for p in products:
        try:obsid=int(p.get("obsID"))
        except (ValueError,TypeError):
            rejection["no_original_observation_parent"]+=1
            continue
        if obsid not in allowed:
            rejection["not_exact_original_SPOC_host_observation"]+=1
            continue
        kind=str(p.get("productSubGroupDescription","")).upper().strip()
        if kind not in DV_TYPES:
            rejection["other_original_SPOC_product_type"]+=1
            continue
        filename=str(p.get("productFilename",""))
        uri=str(p.get("dataURI",""))
        match=SOURCE_PATTERN.search(filename)
        if (not match or int(match["tic"])!=int(tic) or
            not any(filename.lower().endswith(ext) for ext in DV_TYPES[kind]) or
            not uri.startswith("mast:TESS/product/") or ".." in uri):
            rejection["DV_not_original_exact_TIC_or_format"]+=1
            continue
        first=int(match["first"]);last=int(match["last"])
        if first>last or first<1:
            rejection["impossible_DV_sector_range"]+=1
            continue
        if uri in seen:
            rejection["repeated_DV_URI_across_SPOC_obs_rows"]+=1
            continue
        obj={
           "exact_original_host_TIC_ID":int(tic),
           "MAST_original_DV_product_group":kind,
           "filename":filename,
           "MAST_original_dataURI":uri,
           "MAST_parent_observation_ID":obsid,
           "MAST_observed_sector":allowed[obsid],
           "filename_DV_start_sector":first,
           "filename_DV_end_sector":last,
           "source_frozen_first_sector_within_DV_processed_sector_range":bool(
              first<=first_sector<=last),
           "TCE_period_or_source_identity_verified":False,
           "original_product_expected_size_bytes":p.get("size"),
           "original_product_description":str(p.get("description","")),
        }
        seen[uri]=obj
    order={"DVR":0,"DVS":1,"DVT":2,"DVM":3}
    keep=sorted(seen.values(),key=lambda r:(
        not r["source_frozen_first_sector_within_DV_processed_sector_range"],
        -int(r["filename_DV_end_sector"]),
        r["filename"],order[r["MAST_original_DV_product_group"]]))
    return keep,dict(rejection)


def original_mast_full_DV_lookup(tic,first_sector):
    from astroquery.mast import Observations
    observations=Observations.query_criteria(
        obs_collection="TESS",target_name=str(tic))
    rows=tablerows(observations)
    original=[x for x in rows if compatible_target(x.get("target_name"),tic)
          and str(x.get("provenance_name","")).upper()=="SPOC"]
    if len(original)>160:
        raise ValueError("Unexpected original TESS SPOC row abundance")
    if original:
        ids={int(x["obsid"]) for x in original}
        selected=observations[[int(x["obsid"]) in ids for x in rows]]
        prod=tablerows(Observations.get_product_list(selected))
    else:prod=[]
    catalog,rejections=original_SPOC_DV_products(original,prod,tic,first_sector)
    return len(rows),len(original),len(prod),catalog,rejections


def run(original_frozen_neb,original_frozen_planets,out):
    files=[Path(original_frozen_neb),Path(original_frozen_planets)]
    contents=[x.read_bytes() for x in files]
    old,known=[json.loads(x) for x in contents]
    selection=validate_fixed_manifests(old,known)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for tic in sorted(selection):
        obj=dict(selection[tic])
        try:
            obs,spoc,allproducts,eligible,excluded=original_mast_full_DV_lookup(
                tic,obj["source_frozen_first_SPOC_2min_sector"])
            obj.update(
                MAST_source_product_discovery_status="success",
                original_MAST_all_obs_targetname_count=obs,
                original_TESS_SPOC_exact_TIC_observations=spoc,
                original_SPOC_all_products_queried=allproducts,
                original_SPOC_other_product_exclusions=excluded,
                original_DV_product_catalog_all_original_runs=eligible,
                original_DV_product_types_available=sorted(set(
                    p["MAST_original_DV_product_group"] for p in eligible)),
                original_DV_distinct_sector_ranges=sorted(set(
                    (p["filename_DV_start_sector"],p["filename_DV_end_sector"])
                    for p in eligible)),
                original_DV_products_containing_fixed_first_sector=sum(
                    p["source_frozen_first_sector_within_DV_processed_sector_range"]
                    for p in eligible))
        except Exception as e:
            obj.update(
                MAST_source_product_discovery_status="error",
                MAST_original_discovery_error=str(e)[:440],
                original_DV_product_catalog_all_original_runs=[],
                original_DV_product_types_available=[],
                original_DV_products_containing_fixed_first_sector=0)
        print("MAST_ORIGINAL_OFFICIAL_SPOC_DV",json.dumps({
            "host_TIC":tic,"TOI":obj["TOI"],
            "experiment_group":obj["experiment_group"],
            "status":obj["MAST_source_product_discovery_status"],
            "n_all_original_DV_products":len(obj["original_DV_product_catalog_all_original_runs"]),
            "fixed_sector_DV_products":obj["original_DV_products_containing_fixed_first_sector"],
            "DV_product_types":obj["original_DV_product_types_available"],
            "available_sector_ranges":obj.get("original_DV_distinct_sector_ranges",[]),
            "error":obj.get("MAST_original_discovery_error")
        }),flush=True)
        rows.append(obj)
    report={
        "research_question":"Do official original MAST SPOC mission Data Validation target-exact DVR XML/PDF, DVS PDF, DVT FITS or DVM PDF source artifacts exist for the two original external ground-aperture sky-matched NEBs and five separately confirmed planet controls, and do their filename processed-sector ranges include our frozen first source sector?",
        "experiment":"Source-only availability audit, no DV TCE or centroid outcome inspected, no planet classification",
        "original_prior_centroid_frozen_five_NEB_manifest_SHA256":hashlib.sha256(contents[0]).hexdigest(),
        "original_prior_centroid_frozen_five_confirmed_planet_manifest_SHA256":hashlib.sha256(contents[1]).hexdigest(),
        "exact_source_hosts_attempted":7,
        "source_hosts_by_original_prior_label":{
            "prior_ground_aperture_sky_supported_neighbor_eclipse":2,
            "prior_independently_NASA_and_ExoFOP_catalog_confirmed_transiting_planet":5},
        "source_hosts_with_any_official_original_SPOC_DV_product":sum(
            bool(x["original_DV_product_catalog_all_original_runs"]) for x in rows),
        "source_hosts_with_official_DV_including_frozen_first_sector":sum(
            x["original_DV_products_containing_fixed_first_sector"]>0 for x in rows),
        "all_seven_original_source_host_and_official_DV_product_records":rows,
        "no_Raw_or_POS_CORR_or_DV_PRF_centroid_values_read":True,
        "read_original_DV_XML_PDF_FITS_bytes":False,
        "scientific_limits":[
            "The MAST original SPOC DV product listing is not itself a claim that an original pipeline threshold-crossing-event TCE corresponds to the published TOI ephemeris.",
            "Some stars have no publicly released NASA SPOC DV output even with source-matched original 2-minute LC and TP; missing cannot be substituted with independent HLSP TESS-SPOC or another sector.",
            "Some official DVR files combine several sectors and TCEs; a frozen first sector must fall within filename sector range before comparing same-sector results. All other runs are retained but labeled not first-sector comparable.",
            "All five known planet hosts were catalog-confirmed before any new MOM centroid outcomes and before this official DV source list was fetched, but are not train-independent or independently ground imaged.",
            "The two source-note-derived ground NEBs already had ground WCS and eclipse measured; they are not a newly selected blind validation sample.",
            "No NASA original source classifier, weights, ExoMiner++ scores, or officially fitted PRF coordinates have been changed."
        ]
    }
    (out/"ORIGINAL_SEVEN_TIC_NASA_SPOC_DV_UNCHANGED_SOURCE_PRODUCT_AVAILABILITY.json").write_text(
        json.dumps(report,indent=2,default=str)+"\n")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-five-neb-source-manifest",required=True)
    p.add_argument("--original-five-known-planet-source-manifest",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.original_five_neb_source_manifest,
        a.original_five_known_planet_source_manifest,a.out)
