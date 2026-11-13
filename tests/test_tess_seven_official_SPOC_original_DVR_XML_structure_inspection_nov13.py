"""Synthetic official SPOC XML element/sector source tests; no real NASA science."""
import xml.etree.ElementTree as ET
import pytest
from tess_seven_official_SPOC_original_DVR_XML_structure_inspection_nov13 import (
    local,choose_original_source_DV_XML,catalog_original_tce_science_structure,
    compact_original_structure,fetch_original_DV_XML
)


def candidate(first,last,group="DVR",file=None):
    name=file or f"tess2019000000000-s{first:04d}-s{last:04d}-0000000382437043-00011_dvr.xml"
    return {"MAST_original_DV_product_group":group,
      "filename":name,"exact_original_host_TIC_ID":382437043,
      "source_frozen_first_sector_within_DV_processed_sector_range":first<=1<=last,
      "filename_DV_start_sector":first,"filename_DV_end_sector":last,
      "MAST_original_dataURI":"mast:TESS/product/"+name}


def test_source_original_smallest_SPOC_interval_fixed_before_sky_results():
    row={"TIC_ID":382437043,"source_frozen_first_SPOC_2min_sector":1,
         "original_DV_product_catalog_all_original_runs":[candidate(1,96),
         candidate(1,13),candidate(1,36),candidate(2,14),candidate(1,1,"DVR"),
         candidate(1,1,"DVS","tess2019000000000-s0001-s0001-0000000382437043-01-00011_dvs.pdf")]}
    choice,eligible=choose_original_source_DV_XML(row)
    assert choice["filename_DV_start_sector"]==1
    assert choice["filename_DV_end_sector"]==1
    assert len(eligible)==4
    row["original_DV_product_catalog_all_original_runs"]=row[
        "original_DV_product_catalog_all_original_runs"][:4]
    assert choose_original_source_DV_XML(row)[0]["filename_DV_end_sector"]==13


def test_original_element_science_schema_with_namespace_and_multiple_TCEs():
    ns="{http://tess-spoc.nasa.gov/}"
    root=ET.Element(ns+"dvTargetResults",{"ticId":"382437043"})
    p=ET.SubElement(root,ns+"planetResults",{"planetNumber":"1","toiId":"TOI-1223.01"})
    candidate_el=ET.SubElement(p,ns+"planetCandidate")
    ET.SubElement(candidate_el,ns+"orbitalPeriod",{"value":"2.1","uncertainty":"0.001"})
    c=ET.SubElement(p,ns+"centroidResults")
    a=ET.SubElement(c,ns+"msTicCentroidOffsets")
    ET.SubElement(a,ns+"meanSkyOffset",{"value":"0.8","uncertainty":"0.2"})
    el=ET.SubElement(p,ns+"differenceImageResults")
    ET.SubElement(el,ns+"differenceImageCentroid",{"column":"16","row":"25"})
    report=catalog_original_tce_science_structure(root)
    assert local(root.tag)=="dvTargetResults"
    assert report["number_of_planetResults"]==1
    assert report["relevant_DV_tags_present"]["centroidResults"]==1
    assert report["relevant_DV_tags_present"]["differenceImageCentroid"]==1
    assert report["planetResults_original_science_source_samples"][0][
        "original_planetResults_attributes"]["toiId"]=="TOI-1223.01"
    assert len(compact_original_structure(root,maxdepth=1)["sample_direct_children"])==1


def test_official_MAST_URI_for_xml_only_and_source_verified():
    with pytest.raises(ValueError,match="official MAST"):
        fetch_original_DV_XML("https://example.com/fake_dvr.xml")
    with pytest.raises(ValueError,match="official MAST"):
        fetch_original_DV_XML("mast:TESS/product/fake_dvt.fits")
