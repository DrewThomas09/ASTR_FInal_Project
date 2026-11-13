"""Independent NASA SPOC Data Validation product discovery for the two ground NEBs.

Read original pre-centroid frozen source host TIC, TOI, first SPOC two-minute
sector and unchanged original ExoFOP period/epoch/duration. Query MAST's
original TESS SPOC observations and find authentic DV report XML, PDF and
per-TCE summary files WITHOUT reading any DV offsets yet.

A TOI or observed transit in TESS does not imply that the NASA SPOC search
detected a matching threshold-crossing event; absence of a DV report is
not evidence of on-target source localization or nonexistence of transit.
"""
import argparse
import hashlib
import json
import re
from datetime import datetime,timezone
from pathlib import Path

from tess_two_neb_original_mast_discovery import compatible_target,tablerows

HOSTS={382437043:"1223.01",264303333:"2250.01"}
PRODUCT_GROUPS={"DVR","DVS","DVM","DVT"}
PATTERN=re.compile(
    r"(?:^|/)tess\d+-s(?P<first>\d{4})-s(?P<last>\d{4})-(?P<tic>\d{16})"
    r"(?:-(?P<tce>\d{2}))?-(?P<pipeline>\d{5})_(?P<suffix>dvr\.xml|dvr\.pdf|dvm\.pdf|dvt\.fits|dvs\.pdf)$",
    flags=re.I
)


def parse_dv_product(row,tic,obsid_to_spoc):
    try:
        obsid=int(row.get("obsID"))
    except (ValueError,TypeError):
        return None
    if obsid not in obsid_to_spoc:return None
    if str(row.get("productSubGroupDescription","")).upper() not in PRODUCT_GROUPS:
        return None
    name=str(row.get("productFilename","")).strip()
    uri=str(row.get("dataURI","")).strip()
    m=PATTERN.search(name)
    if m is None or int(m.group("tic"))!=int(tic):
        return None
    if not uri.startswith("mast:TESS/product/") or ".." in uri or m.group("first")=="":
        return None
    group=m.group("suffix").upper().split(".")[0]
    if group!=str(row["productSubGroupDescription"]).strip().upper():
        return None
    lo=int(m.group("first"));hi=int(m.group("last"))
    if lo<=0 or hi<lo:return None
    return {
        "TIC_ID":int(tic),
        "product_group":group,
        "product_filename":name,
        "original_MAST_product_URI":uri,
        "source_obsID":obsid,
        "source_observation_sector":obsid_to_spoc[obsid]["sector"],
        "original_DV_search_start_sector":lo,
        "original_DV_search_end_sector":hi,
        "original_DV_pipeline_instance_number":int(m.group("pipeline")),
        "original_DV_TCE_number_if_one_page":int(m.group("tce")) if m.group("tce") else None,
        "original_MAST_source_size_bytes_expected":row.get("size")
    }


def exact_spoc_dv_products(tic):
    from astroquery.mast import Observations
    o=Observations.query_criteria(obs_collection="TESS",target_name=str(tic))
    rows=tablerows(o)
    selected={}
    for r in rows:
        if not compatible_target(r.get("target_name"),tic):
            continue
        if str(r.get("provenance_name","")).upper()!="SPOC":
            continue
        try:
            sec=int(r.get("sequence_number"))
            obsid=int(r.get("obsid"))
            if sec<=0:continue
        except (ValueError,TypeError):
            continue
        selected[obsid]={"sector":sec,"original_spoc_obsid":obsid}
    if len(selected)>200:
        raise ValueError("Unexpected source SPOC observation abundance, stop instead of substituting")
    if not selected:
        products=[]
    else:
        sub=o[[int(r["obsid"]) in selected for r in rows]]
        products=tablerows(Observations.get_product_list(sub))
    matches=[]
    for p in products:
        exact=parse_dv_product(p,tic,selected)
        if exact:matches.append(exact)
    matches=sorted(matches,key=lambda a:(a["original_DV_search_start_sector"],
        a["original_DV_search_end_sector"],a["product_group"],a["product_filename"]))
    if len({x["original_MAST_product_URI"] for x in matches})!=len(matches):
        raise ValueError("Duplicated archived official DV original source URI")
    return len(rows),len(selected),len(products),matches


def run(original_manifest,out):
    path=Path(original_manifest)
    b=path.read_bytes()
    source=json.loads(b)
    if source.get("experiment_id")!="ASTR_FIVE_NEW_NEB_SPOC_SOURCE_BLIND_WCS_EVAL_20261112":
        raise ValueError("Not previously pre-centroid frozen original host source")
    hosts={int(x["TIC_ID"]):x for x in source["source_records"]}
    if not set(HOSTS).issubset(hosts):
        raise ValueError("Original ground aperture host TICs not both originally frozen")
    result=[]
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for tic,toi in HOSTS.items():
        original=hosts[tic]
        if original["TOI"]!=toi:
            raise ValueError("Original ExoFOP event identity changed")
        first=int(original["selected_first_original_SPOC_2min_sector"])
        entry={
            "TIC_ID":tic,"TOI":toi,
            "original_source_frozen_SPOC_first_sector":first,
            "original_ExoFOP_epoch_BTJD":original["original_ExoFOP_epoch_BTJD"],
            "original_ExoFOP_period_days":original["original_ExoFOP_period_days"],
            "original_ExoFOP_duration_days":original["original_ExoFOP_duration_days"],
            "NASA_DV_available_is_not_guaranteed_to_be_same_TOI_signal":True,
            "prior_ground_pixel_data_or_centroid_not_used_to_choose_DV_product":True,
        }
        try:
            obs,nspoc,nproducts,products=exact_spoc_dv_products(tic)
            entry.update(
                original_TESS_MAST_observation_rows=obs,
                exact_original_TIC_SPOC_observations=nspoc,
                all_original_SPOC_product_rows_considered=nproducts,
                all_exact_original_SPOC_DV_products_untuned=products,
                original_DV_XML_products_all=[p for p in products if p["product_group"]=="DVR"
                                               and p["product_filename"].endswith("_dvr.xml")],
                original_DV_frozen_first_sector_search_covering_XML_products=[
                   p for p in products if p["product_group"]=="DVR"
                   and p["product_filename"].endswith("_dvr.xml")
                   and p["original_DV_search_start_sector"]<=first<=p["original_DV_search_end_sector"]],
                original_MAST_DV_product_discovery_status="queried_original_MAST")
        except Exception as exc:
            entry.update(
                original_MAST_DV_product_discovery_status="source_lookup_error",
                source_error=str(exc)[:400],
                all_exact_original_SPOC_DV_products_untuned=[],
                original_DV_XML_products_all=[],
                original_DV_frozen_first_sector_search_covering_XML_products=[])
        print("ORIGINAL_MAST_DV_SOURCE_DISCOVERY",json.dumps({
            "TIC":tic,"TOI":toi,"original_first_SPOC_sector":first,
            "status":entry["original_MAST_DV_product_discovery_status"],
            "n_DV_products":len(entry["all_exact_original_SPOC_DV_products_untuned"]),
            "n_XML":len(entry["original_DV_XML_products_all"]),
            "n_frozen_sector_covering_XML":len(entry[
                "original_DV_frozen_first_sector_search_covering_XML_products"]),
            "all_sector_covering_XML_filenames":[p["product_filename"] for p in entry[
                "original_DV_frozen_first_sector_search_covering_XML_products"]],
            "error":entry.get("source_error")}),flush=True)
        result.append(entry)
    report={
      "research_question":"Do authentic NASA SPOC mission Data Validation products (official PRF difference-image centroid XML) exist for the exact two prior externally ground-observed off-target TOIs at the independently source-frozen first TESS SPOC sectors?",
      "original_precentroid_five_host_manifest_SHA256":hashlib.sha256(b).hexdigest(),
      "exact_previously_ground_corroborrated_host_TICs_attempted":2,
      "original_source_DISCOVERY_only_no_DV_files_downloaded":True,
      "original_discovery_UTC":datetime.now(timezone.utc).isoformat(),
      "official_product_information_source":"MAST TESS SPOC original observation and get_product_list, no FFI HLSP substitution",
      "source_results_all_no_selection_on_centroid_outcomes":result,
      "scientific_limitations":[
        "A MAST DV XML product may include multiple detected TCE signals; TIC match alone cannot establish that NASA actually found the specific original ExoFOP off-target eclipse.",
        "A DV search spanning the first SPOC sector need not be identical to that sector's own TPF cadence scope; archive all original distinct search intervals and the exact list.",
        "If no DV product exists or no DV TCE matches the actual TOI ephemeris, that is a missing official source-localization comparator, not scientific proof the TOI is invalid.",
        "MAST products may contain NASA PRF centroid metrics with invalid (-1) uncertainties and quality flags; independent matching and validation must precede comparison.",
        "Do not substitute FFI TESS-SPOC products, arbitrary nearby star TCEs or PDF pictures as measurement truth.",
        "Preselected hosts are ground-report-followup-selected post-hoc, not prospectively sampled or independent NASA ExoMiner validation.",
        "No mission model trained scores, catalog classifications or original SPOC light curves modified."
      ]
    }
    (out/"original_two_ground_NEBS_MAST_SPOC_DV_product_availability_SOURCE_ONLY.json").write_text(
        json.dumps(report,indent=2,default=str)+"\n")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-frozen-source",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.original_frozen_source,a.out)
