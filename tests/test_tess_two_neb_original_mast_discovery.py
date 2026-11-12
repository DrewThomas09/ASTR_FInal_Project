"""Synthetic source/discovery tests (not simulated or observed TESS events)."""
import csv,io
import pytest

from tess_two_neb_original_mast_discovery import (
    source_ephemerides, compatible_target, filter_original_products
)

def source_csv():
    cols=["TIC ID","TOI","Epoch (BJD)","Period (days)",
          "Duration (hours)","Sectors","TFOPWG Disposition"]
    records=[
        [54364414,"2041.01",2459015.0,4.2,3.4,"27,28","FP"],
        [82302240,"4255.01",2459505.0,3.3,2.9,"42","FP"],
        [9999999,"2041.01",2459000.0,5.0,2.5,"6","FP"],
    ]
    z=io.StringIO()
    w=csv.writer(z);w.writerow(cols);w.writerows(records)
    return z.getvalue().encode()

def test_exact_exofop_id_and_toi_ephemeris_without_mismatched_sources():
    d=source_ephemerides(source_csv())
    assert len(d)==2
    assert d[54364414]["original_ExoFOP_epoch_BTJD"]==pytest.approx(2015)
    assert d[82302240]["original_ExoFOP_period_days"]==pytest.approx(3.3)
    assert d[54364414]["broad_TFOPWG_disposition_not_neighbor_truth"]=="FP"

def test_duplicated_original_target_toi_is_invalid():
    a=source_csv().decode().splitlines()
    with pytest.raises(ValueError,match="Duplicate"):
        source_ephemerides(("\n".join(a+[a[1]])+"\n").encode())

def test_bad_absolute_epoch_and_duration_are_rejected():
    with pytest.raises(ValueError,match="Unphysical"):
        source_ephemerides(source_csv().replace(b"2459015.0",b"1900.0"))
    with pytest.raises(ValueError,match="Unphysical"):
        source_ephemerides(source_csv().replace(b",3.4,",b",500.0,"))

def test_exact_TIC_filter_does_not_accept_neighbors():
    assert compatible_target("0000000054364414",54364414)
    assert compatible_target("54364414",54364414)
    assert not compatible_target("54364420",54364414)
    assert not compatible_target("TIC 54364414",54364414)

def test_original_spoc_LC_TP_only_and_exact_source_filename():
    tic=54364414
    f=f"tess2020-s0027-{tic:016d}-0120-s"
    obs=[dict(obsid=7,target_name=str(tic),provenance_name="SPOC",sequence_number=27),
         dict(obsid=8,target_name="54364420",provenance_name="SPOC",sequence_number=27),
         dict(obsid=9,target_name=str(tic),provenance_name="TESS-SPOC",sequence_number=27)]
    prods=[
        dict(obsID=7,productFilename=f+"_lc.fits",dataURI="mast:TESS/product/a_lc.fits",productSubGroupDescription="LC",size=3),
        dict(obsID=7,productFilename=f+"_tp.fits",dataURI="mast:TESS/product/a_tp.fits",productSubGroupDescription="TP",size=4),
        dict(obsID=8,productFilename=f.replace(str(tic),str(54364420))+"_lc.fits",dataURI="mast:TESS/product/b_lc.fits",productSubGroupDescription="LC",size=3),
        dict(obsID=9,productFilename=f+"_lc.fits",dataURI="mast:HLSP/x_lc.fits",productSubGroupDescription="LC",size=3),
    ]
    res=filter_original_products(obs,prods,tic)
    assert {x["product_group"] for x in res}=={"LC","TP"}
    assert {x["sector"] for x in res}=={27}
    assert len(res)==2

def test_missing_exact_target_or_original_SPOC_not_relabeled():
    assert filter_original_products([{"obsid":1,"target_name":"54364420","provenance_name":"SPOC","sequence_number":27}],
        [{"obsID":1,"productFilename":f"tess000-{54364420:016d}_lc.fits",
          "dataURI":"mast:TESS/product/x","productSubGroupDescription":"LC"}],54364414)==[]
