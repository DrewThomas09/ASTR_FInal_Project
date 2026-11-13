"""Synthetic NASA SPOC Data Validation source-identity regression tests.

These test product syntax only, not an actual TCE or NASA PRF centroid.
"""
import pytest
from tess_two_ground_neb_original_MAST_SPOC_DV_product_discovery_nov13 import (
    HOSTS,PRODUCT_GROUPS,parse_dv_product,PATTERN
)


def row(name,group="DVR",obsid=19,tic=382437043):
    return {"obsID":obsid,"productSubGroupDescription":group,
            "productFilename":name,
            "dataURI":"mast:TESS/product/"+name,
            "size":435677}


def test_actual_documented_original_tess_dv_product_filename_patterns():
    tic=382437043
    name=f"tess2021003000100-s0001-s0013-{tic:016d}-00226_dvr.xml"
    parsed=parse_dv_product(row(name),tic,{19:{"sector":1}})
    assert parsed["TIC_ID"]==tic
    assert parsed["original_DV_search_start_sector"]==1
    assert parsed["original_DV_search_end_sector"]==13
    assert parsed["product_group"]=="DVR"
    assert parsed["source_obsID"]==19
    assert parsed["original_MAST_product_URI"]=="mast:TESS/product/"+name


def test_genuine_dvs_pdf_dvt_fits_and_longer_campaign_names_match_unmodified():
    tic=264303333
    prefix=f"tess2020001000100-s0014-s0026-{tic:016d}"
    for suffix,group in (("01-00321_dvs.pdf","DVS"),
                         ("00321_dvr.pdf","DVR"),
                         ("00321_dvt.fits","DVT"),
                         ("00321_dvm.pdf","DVM")):
        p=parse_dv_product(row(prefix+"-"+suffix,group),tic,{19:{"sector":14}})
        assert p is not None
        assert p["product_group"]==group
        assert p["original_DV_search_start_sector"]==14
        assert p["original_DV_search_end_sector"]==26


def test_reject_wrong_tic_wrong_observation_wrong_group_and_outside_source():
    tic=382437043
    real=f"tess2019123456789-s0001-s0001-{tic:016d}-00219_dvr.xml"
    assert parse_dv_product(row(real),tic,{20:{"sector":1}}) is None
    assert parse_dv_product(row(real),999999999,{19:{"sector":1}}) is None
    assert parse_dv_product(row(real,"LC"),tic,{19:{"sector":1}}) is None
    unsafe=row(real)
    unsafe["dataURI"]="https://example.com/false_dvr.xml"
    assert parse_dv_product(unsafe,tic,{19:{"sector":1}}) is None
    assert parse_dv_product(row(real.replace("s0001-s0001","s0014-s0001")),tic,{19:{"sector":1}}) is None


def test_no_ground_truth_inferred_from_xml_availability_or_missing_tce():
    assert HOSTS=={382437043:"1223.01",264303333:"2250.01"}
    assert "DVR" in PRODUCT_GROUPS
    assert PATTERN.search("nonsense_dvr.xml") is None
