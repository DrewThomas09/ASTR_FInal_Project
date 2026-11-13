"""Synthetic exact-source NASA SPOC DV product filters: no original DV is read."""
import pytest
from tess_seven_original_SPOC_official_DV_product_discovery_nov13 import (
    validate_fixed_manifests,original_SPOC_DV_products,TWO_OFFTARGET,FIVE_PLANETS
)


def source_locks():
    n={"experiment_id":"ASTR_FIVE_NEW_NEB_SPOC_SOURCE_BLIND_WCS_EVAL_20261112",
       "source_records":[]}
    p={"experiment_id":"ASTR_NASA_AND_EXOFOP_KP_CONFIRMED_TRANSITING_ON_TARGET_CONTROL_SPOC_SOURCE_FROZEN_NOV12",
       "original_TESS_centroids_viewed":0,"source_records":[]}
    for tic,(toi,near,sector) in TWO_OFFTARGET.items():
        n["source_records"].append({
            "TIC_ID":tic,"TOI":toi,
            "original_neb_named_neighbor_TIC_not_physical_truth":near,
            "selected_first_original_SPOC_2min_sector":sector,
            "original_ExoFOP_period_days":2.,
            "original_ExoFOP_epoch_BTJD":1000.,
            "original_ExoFOP_duration_days":.1
        })
    for j in range(3):
        n["source_records"].append({"TIC_ID":91000000+j})
    for tic,(toi,name,sector) in FIVE_PLANETS.items():
        p["source_records"].append({
            "TIC_ID":tic,"TOI":toi,"NASA_confirmed_host_alias":name,
            "selected_first_original_SPOC_2min_sector":sector,
            "original_ExoFOP_period_days":2.,
            "original_ExoFOP_epoch_BTJD":1000.,
            "original_ExoFOP_duration_days":.1
        })
    return n,p


def test_all_prior_sources_sectors_ephemerides_are_locked_and_unmodified():
    n,p=source_locks()
    r=validate_fixed_manifests(n,p)
    assert len(r)==7
    assert r[382437043]["source_frozen_first_SPOC_2min_sector"]==1
    assert r[264303333]["original_reported_neighbor_TIC"]==1884344804
    assert r[134537478]["official_NASA_confirmed_planet_alias"]=="KELT-14 b"
    p["original_TESS_centroids_viewed"]=1
    with pytest.raises(ValueError,match="after viewing"):
        validate_fixed_manifests(n,p)


def test_offtarget_first_sector_never_reassigned_after_seeing_DV_availability():
    n,p=source_locks()
    n["source_records"][0]["selected_first_original_SPOC_2min_sector"]=22
    with pytest.raises(ValueError,match="first-sector"):
        validate_fixed_manifests(n,p)


def test_original_SPOC_exact_TIC_parent_and_DV_filename_and_uri_filter():
    tic=382437043
    def obj(name,kind,uri=None,obs=123):
        return {"obsID":obs,"productFilename":name,
          "dataURI":uri or "mast:TESS/product/"+name,
          "productSubGroupDescription":kind,"size":100}
    stem="tess2021000000000-s0001-s0014-0000000382437043-"
    rows=[
      obj(stem+"00001_dvr.xml","DVR"),
      obj(stem+"01-00001_dvs.pdf","DVS"),
      obj(stem+"00001_dvt.fits","DVT"),
      obj(stem+"00001_dvm.pdf","DVM"),
      obj(stem+"00001_dvr.xml","DVR"),
      obj(stem.replace("0000000382437043","0000000382437045")+"00001_dvr.xml","DVR"),
      obj(stem+"00001_dvr.pdf","DVR",obs=456),
      obj(stem+"00001_lc.fits","LC"),
      obj(stem+"00002_dvr.xml","DVR","https://wrong.example/DV.xml"),
    ]
    obs=[{"obsid":123,"target_name":str(tic),"provenance_name":"SPOC",
          "sequence_number":1},
         {"obsid":456,"target_name":"382437045","provenance_name":"SPOC",
          "sequence_number":1}]
    keep,rej=original_SPOC_DV_products(obs,rows,tic,first_sector=1)
    assert len(keep)==4
    assert {x["MAST_original_DV_product_group"] for x in keep}=={
      "DVR","DVS","DVT","DVM"}
    assert all(x["source_frozen_first_sector_within_DV_processed_sector_range"] for x in keep)
    assert all(x["exact_original_host_TIC_ID"]==tic for x in keep)
    assert rej["repeated_DV_URI_across_SPOC_obs_rows"]==1
    assert rej["DV_not_original_exact_TIC_or_format"]>=2


def test_original_dv_sectors_excluding_frozen_first_sector_are_never_claimed_matched():
    tic=382437043
    name="tess2021000000000-s0027-s0028-0000000382437043-00001_dvr.xml"
    obs=[{"obsid":123,"target_name":str(tic),"provenance_name":"SPOC",
          "sequence_number":28}]
    keep,_=original_SPOC_DV_products(obs,[{
        "obsID":123,"productFilename":name,
        "dataURI":"mast:TESS/product/"+name,"productSubGroupDescription":"DVR",
        "size":200
    }],tic,first_sector=1)
    assert len(keep)==1
    assert keep[0]["source_frozen_first_sector_within_DV_processed_sector_range"] is False
    assert keep[0]["filename_DV_start_sector"]==27
