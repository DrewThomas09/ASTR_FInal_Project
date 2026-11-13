"""Synthetic source-selection engineering tests: NOT evidence of observed planets."""
import csv
import io
import pytest

from tess_nasa_confirmed_KP_ontarget_controls_source_freeze_nov12 import (
    original_nasa_confirmed_transiting_rows,
    match_original_exofop_kp_to_nasa,
    choose_product_pair,match_tic,EXCLUDED_EXTRA,N_PREDECLARED_HOSTS
)


def source_nasa():
    f=io.StringIO()
    writer=csv.DictWriter(f,fieldnames=["pl_name","hostname","tic_id","tran_flag",
        "cb_flag","pl_controv_flag","pl_orbper","pl_tranmid","ra","dec"])
    writer.writeheader()
    writer.writerow({"pl_name":"Test-1 b","hostname":"Test-1","tic_id":"TIC 123456789",
      "tran_flag":1,"cb_flag":0,"pl_controv_flag":0,"pl_orbper":2.0001,
      "pl_tranmid":2459001,"ra":72.3,"dec":-15.0})
    writer.writerow({"pl_name":"Test-2 b","hostname":"Test-2","tic_id":"TIC 222222222",
      "tran_flag":1,"cb_flag":1,"pl_controv_flag":0,"pl_orbper":2.0,
      "pl_tranmid":2459001,"ra":71.2,"dec":-16.0})
    writer.writerow({"pl_name":"Test-3 b","hostname":"Test-3","tic_id":"TIC 333333333",
      "tran_flag":1,"cb_flag":0,"pl_controv_flag":1,"pl_orbper":2.0,
      "pl_tranmid":2459001,"ra":71.2,"dec":-16.0})
    return f.getvalue().encode()


def source_exofop():
    f=io.StringIO()
    writer=csv.DictWriter(f,fieldnames=["TIC ID","TOI","TFOPWG Disposition",
         "Period (days)","Epoch (BJD)","Duration (hours)"])
    writer.writeheader()
    writer.writerow({"TIC ID":123456789,"TOI":"1234.01","TFOPWG Disposition":"KP",
         "Period (days)":2.0,"Epoch (BJD)":2459001,"Duration (hours)":3.})
    writer.writerow({"TIC ID":222222222,"TOI":"1235.01","TFOPWG Disposition":"KP",
         "Period (days)":2.0,"Epoch (BJD)":2459001,"Duration (hours)":3.})
    writer.writerow({"TIC ID":333333333,"TOI":"1236.01","TFOPWG Disposition":"KP",
         "Period (days)":2.0,"Epoch (BJD)":2459001,"Duration (hours)":3.})
    return f.getvalue().encode()


def test_no_false_transiting_ground_labels_from_kp_alone():
    nasa,counts=original_nasa_confirmed_transiting_rows(source_nasa())
    assert list(nasa)==[123456789]
    controls,scan=match_original_exofop_kp_to_nasa(source_exofop(),nasa,set())
    assert len(controls)==1
    c=controls[0]
    assert c["TIC_ID"]==123456789
    assert c["NASA_archive_confirmed_transit_and_ExoFOP_KP_agree"] is True
    assert c["independently_verified_on_target_ground_lightcurve_source"] is False
    assert c["MOM_CENTR_or_POS_CORR_not_queried"] is True
    assert c["original_ExoFOP_epoch_BTJD"]==pytest.approx(2001)


def test_no_already_centroid_inspected_host_reselected_as_control():
    nasa,_=original_nasa_confirmed_transiting_rows(source_nasa())
    controls,_=match_original_exofop_kp_to_nasa(source_exofop(),nasa,{123456789})
    assert controls==[]
    assert 382437043 in EXCLUDED_EXTRA
    assert N_PREDECLARED_HOSTS==5


def test_original_mast_requires_exact_TIC_in_filename_and_first_sector_both_lc_tp():
    tic=123456789
    filename=f"tess-s0001-{tic:016d}-0001-s_lc.fits"
    tpfilename=f"tess-s0001-{tic:016d}-0001-s_tp.fits"
    products=[
       {"product_group":"LC","sector":1,"TIC_ID":tic,"productFilename":filename,"MAST_original_dataURI":"mast:TESS/a"},
       {"product_group":"TP","sector":1,"TIC_ID":tic,"productFilename":tpfilename,"MAST_original_dataURI":"mast:TESS/b"},
       {"product_group":"LC","sector":2,"TIC_ID":tic,"productFilename":filename.replace("s0001","s0002"),"MAST_original_dataURI":"mast:TESS/c"},
       {"product_group":"TP","sector":2,"TIC_ID":tic,"productFilename":tpfilename.replace("s0001","s0002"),"MAST_original_dataURI":"mast:TESS/d"}]
    source={"genuine_2min_SPOC_LC_TP_sectors":[2,1],"matching_original_SPOC_products":products}
    sector,pair=choose_product_pair({"TIC_ID":tic},source)
    assert sector==1
    assert pair["LC"]["MAST_original_dataURI"]=="mast:TESS/a"
    broken=dict(source,matching_original_SPOC_products=products[1:])
    with pytest.raises(ValueError,match="No unique"):
        choose_product_pair({"TIC_ID":tic},broken)


def test_missing_and_ambiguous_tic_are_not_reinterpreted_as_host():
    assert match_tic("TIC 123456789")==123456789
    assert match_tic("TIC 123456789.0")==123456789
    assert match_tic("other identifier")==None
