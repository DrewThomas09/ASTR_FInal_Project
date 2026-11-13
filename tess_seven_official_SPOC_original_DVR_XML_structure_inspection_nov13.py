"""Inspect official original SPOC NASA DVR XML structure on seven already frozen
TESS host TICs, using deterministic first-available DV product ranges.

Archive XML contains official fitted TCE timing, planetResults, PRF-derived
differenceImageResults/centroidResults. This audit does NOT assume any TCE is
the originally selected TOI: a subsequent exact period/epoch match is required.
No official DV PDF, trained network score or unverified source is substituted.

If an exact single-sector DV is available, prefer it; otherwise choose
the smallest containing published DV start/end sector interval, then original
filename lexicographic. All other original discovery records remain archived.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import requests

from tess_seven_original_SPOC_official_DV_product_discovery_nov13 import (
    TWO_OFFTARGET,FIVE_PLANETS
)

MAST_ENDPOINT="https://mast.stsci.edu/api/v0.1/Download/file"
MAX_XML_BYTES=12000000
MIN_XML_BYTES=500
SCIENCE_TAGS={
    "planetCandidate","allTransitsFit","modelParameters","planetResults",
    "centroidResults","differenceImageMotionResults","msTicCentroidOffsets",
    "msControlCentroidOffsets","differenceImageResults",
    "ticReferenceCentroid","controlImageCentroid","differenceImageCentroid",
    "ticCentroidOffsets","controlCentroidOffsets","differenceImagePixelData",
    "summaryQualityMetric","summaryOverlapMetric","trapezoidalFit"
}

def local(tag):
    return str(tag).split("}")[-1]


def choose_original_source_DV_XML(record):
    tic=int(record["TIC_ID"])
    first=int(record["source_frozen_first_SPOC_2min_sector"])
    values=[p for p in record["original_DV_product_catalog_all_original_runs"]
          if p["MAST_original_DV_product_group"]=="DVR" and
             p["filename"].lower().endswith("_dvr.xml") and
             p["source_frozen_first_sector_within_DV_processed_sector_range"] is True
             and int(p["exact_original_host_TIC_ID"])==tic and
             int(p["filename_DV_start_sector"])<=first<=int(p["filename_DV_end_sector"])]
    values.sort(key=lambda r:(
        int(r["filename_DV_end_sector"])-int(r["filename_DV_start_sector"]),
        r["filename_DV_start_sector"],r["filename"]))
    return (values[0] if values else None),values


def fetch_original_DV_XML(uri):
    if not uri.startswith("mast:TESS/product/") or ".." in uri or not uri.lower().endswith("_dvr.xml"):
        raise ValueError("Source URL not an official MAST NASA SPOC DVR XML file")
    with requests.get(MAST_ENDPOINT,params={"uri":uri},timeout=(30,150),stream=True) as r:
        r.raise_for_status()
        chunks=[];count=0;h=hashlib.sha256()
        for block in r.iter_content(chunk_size=32768):
            if not block:continue
            count+=len(block)
            if count>MAX_XML_BYTES:
                raise ValueError("Original NASA SPOC DV XML exceeds declared size ceiling")
            chunks.append(block);h.update(block)
    raw=b"".join(chunks)
    if len(raw)<MIN_XML_BYTES or not raw.lstrip().startswith(b"<?xml"):
        raise ValueError("MAST returned no original XML file or XML source abnormally small")
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("Untrusted DTD/XML entity in source")
    root=ET.fromstring(raw)
    if local(root.tag) not in ("dvTargetResults","dvResults","dvResultsCollection"):
        raise ValueError("Unexpected NASA DV XML top-level node "+local(root.tag))
    return root,{"original_XML_bytes":len(raw),"original_source_SHA256":h.hexdigest(),
                 "source_MAST_uri":uri,"root_tag":local(root.tag)}


def attrs_clean(e,max_values=30):
    return {str(k):str(v)[:250] for k,v in list(e.attrib.items())[:max_values]}


def compact_original_structure(element,maxdepth=3,maxchildren=30,depth=0):
    """Record actual science metadata, not base64, pixels or large numeric arrays."""
    d={"element_name":local(element.tag)}
    if element.attrib:d["original_attributes"]=attrs_clean(element)
    if element.text and element.text.strip() and len(element.text.strip())<180:
        d["short_scalar_text"]=element.text.strip()
    if depth<maxdepth:
        child=list(element)
        if child:
            d["direct_child_count"]=len(child)
            d["sample_direct_children"]=[
                compact_original_structure(c,maxdepth,maxchildren,depth+1)
                for c in child[:maxchildren]]
            if len(child)>maxchildren:d["children_truncated"]=True
    return d


def catalog_original_tce_science_structure(root):
    planets=[e for e in root.iter() if local(e.tag)=="planetResults"]
    tags=Counter(local(x.tag) for x in root.iter())
    targetmeta={
        "original_root_attributes":attrs_clean(root),
        "root_direct_children_names":[local(c.tag) for c in list(root)[:35]],
        "number_of_planetResults":len(planets),
        "all_original_XML_elements_count":sum(tags.values()),
        "relevant_DV_tags_present":{x:int(tags[x]) for x in sorted(SCIENCE_TAGS) if tags[x]},
        "all_XML_local_tag_counts_top40":tags.most_common(40)
    }
    observations=[]
    for e in planets[:20]:
        record={"original_planetResults_attributes":attrs_clean(e),
                "direct_element_names":[local(c.tag) for c in e],
                "numeric_DV_fields_not_yet_matched_to_external_TOI":True}
        for c in e:
            name=local(c.tag)
            if name not in SCIENCE_TAGS:continue
            if name in ("differenceImageResults","centroidResults"):
                record[name]={
                    "element_attributes":attrs_clean(c),
                    "immediate_children":[local(y.tag) for y in list(c)[:40]],
                    "nested_candidate_science_elements":[{
                        "DV_tag":local(z.tag),
                        "attributes":attrs_clean(z),
                        "direct_children":[compact_original_structure(y,maxdepth=1)
                            for y in list(z)[:8]]
                    } for z in c.iter() if local(z.tag) in (
                        "differenceImageMotionResults","msTicCentroidOffsets",
                        "msControlCentroidOffsets","summaryQualityMetric",
                        "differenceImageCentroid","ticReferenceCentroid",
                        "controlImageCentroid","ticCentroidOffsets",
                        "controlCentroidOffsets")][:60]
                }
            else:
                record[name]=compact_original_structure(c,maxdepth=3,maxchildren=15)
        observations.append(record)
    targetmeta["planetResults_original_science_source_samples"]=observations
    targetmeta["planetResults_truncated"]=len(planets)>20
    return targetmeta


def run(source_availability,out):
    source=Path(source_availability)
    src=source.read_bytes()
    catalog=json.loads(src)
    if (catalog["exact_source_hosts_attempted"]!=7 or
        not catalog["no_Raw_or_POS_CORR_or_DV_PRF_centroid_values_read"]):
        raise ValueError("Original seven source-only DV inventory not preserved")
    records=catalog["all_seven_original_source_host_and_official_DV_product_records"]
    if {int(x["TIC_ID"]) for x in records}!=set(TWO_OFFTARGET)|set(FIVE_PLANETS):
        raise ValueError("Official DV XML requests changed originally frozen source identities")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    results=[]
    for source_host in sorted(records,key=lambda x:x["TIC_ID"]):
        tic=int(source_host["TIC_ID"])
        selected,eligible=choose_original_source_DV_XML(source_host)
        row={"host_TIC_ID":tic,"TOI":source_host["TOI"],
             "original_external_source_group":source_host["experiment_group"],
             "frozen_first_SPOC_2min_sector":source_host["source_frozen_first_SPOC_2min_sector"],
             "all_eligible_official_same_source_first_sector_XML_candidates":eligible,
             "number_eligible_original_xmls":len(eligible),
             "original_DV_to_ExoFOP_TCE_match_known":False}
        if selected is None:
            row["source_result_status"]="no_original_first_sector_containing_official_DVR_XML"
        else:
            row["deterministically_chosen_smallest_range_original_DV_XML_product"]=selected
            try:
                root,metadata=fetch_original_DV_XML(selected["MAST_original_dataURI"])
                row["real_downloaded_original_NASA_DV_XML_SHA_and_source"]=metadata
                row["real_original_NASA_SPOC_DV_TCE_and_centroid_XML_structure"]=(
                    catalog_original_tce_science_structure(root))
                row["source_result_status"]="original_official_DV_XML_parsed_unmatched_TCE"
            except (ValueError,requests.RequestException,ET.ParseError) as e:
                row["source_result_status"]="original_DV_XML_download_or_parsing_failed"
                row["source_error"]=str(e)[:500]
        print("OFFICIAL_NASA_SPOC_XML_STRUCTURE",json.dumps({
            "host":tic,"TOI":row["TOI"],"status":row["source_result_status"],
            "frozen_first_sector":row["frozen_first_SPOC_2min_sector"],
            "XML_candidates_original":len(eligible),
            "selected_DV_name":selected["filename"] if selected else None,
            "original_NASA_XML_SHA":row.get("real_downloaded_original_NASA_DV_XML_SHA_and_source"),
            "original_DV_TCE_count":row.get("real_original_NASA_SPOC_DV_TCE_and_centroid_XML_structure",{}).get("number_of_planetResults"),
            "original_DV_science_structure":row.get("real_original_NASA_SPOC_DV_TCE_and_centroid_XML_structure"),
            "error":row.get("source_error")
        }),flush=True)
        results.append(row)
    report={
        "research_question":"Can we retrieve genuine official NASA SPOC mission DVR XML from the smallest published first-sector-containing original target-exact DV sector range for each of seven frozen source TICs, while preserving all TCEs unassigned to their ExoFOP TOI until original period/epoch agreement is verified?",
        "source_only_original_official_DV_inventory_SHA256":hashlib.sha256(src).hexdigest(),
        "source_lock_count":len(records),
        "source_selection":"Smallest inclusive DV start-end sector range containing original first SPOC 2-min sector; tie original filename ascending; all other XML candidates included, without looking at TCE results.",
        "original_DV_XML_sources_retrieved":sum(
            x["source_result_status"]=="original_official_DV_XML_parsed_unmatched_TCE" for x in results),
        "exact_all_seven_selected_original_NASA_DV_source_and_unmatched_TCE_structure":results,
        "no_manual_star_or_sector_substitution":True,
        "not_a_TCE_source_location_validation_yet":True,
        "original_NASA_ExoMiner_scores_changed":False,
        "limitations":[
            "An official target TIC DV results XML may contain zero, one or several TCEs; a TCE's existence does not establish it corresponds to the published original target TOI.",
            "Source selection picks smallest DV interval including the frozen original source sector, not necessarily an isolated single-sector report, and may include many later sectors.",
            "All official centroid fields here are only inventoried to establish schema, not treated as measured TOI source localization until independently verified ephemeris matching.",
            "Missing XML or star/sector-specific DV is preserved as missing; no substitute target, cross-mission HLSP or later sector is allowed.",
            "Only official NASA archived original SPOC DV XML for source-identical TIC is accepted, with original source file SHA and deterministic URI archived.",
            "No original NASA ExoMiner++ pretrained model scores, weights, labels or official planet designations changed."
        ]
    }
    (out/"seven_official_SPOC_firstsector_DVR_XML_original_TCE_source_structure_UNMATCHED.json").write_text(
        json.dumps(report,indent=2,default=str)+"\n")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-seven-DV-availability",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.original_seven_DV_availability,a.out)
