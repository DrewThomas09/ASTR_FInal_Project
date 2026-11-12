"""Engineering-only tests; synthetic coordinates are not TESS source evidence."""
import csv
import io
import numpy as np
import pandas as pd
import pytest
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS

from tess_toi4255_original_spoc_neb_vector_case import (
    TIC, NEIGHBOR, KNOWN_SECTORS, select_exact_source_products,
    neighbor_catalog_row, position_geometry, physical_away_alignment,
    paired_original_events, summarize_pairs
)


def manifest(valid=True):
    products=[]
    for sector in KNOWN_SECTORS:
        for kind in ("LC","TP"):
            products.append({
                "TIC_ID":TIC if valid else 1,
                "sector":sector,"product_group":kind,
                "productFilename":f"tess2023-s{sector:04d}-{TIC:016d}-0120-s_{kind.lower()}.fits",
                "MAST_original_dataURI":f"mast:TESS/product/sector{sector}_{kind}"
            })
    return {"cases":{str(TIC):{"exact_original_TESS_SPOC_2min_products":products}}}


def original_neighbor_csv(duplicates=False):
    lines=[
        "TIC ID,TOI,RA,Dec,Separation (arcsec),Position Angle (deg E. of N.)",
        "82302236,4255.01,100.000278,10.0,5.10,31.21",
        "82302233,4255.01,100.000278,10.0,6.00,51.11",
    ]
    if duplicates:lines.append(lines[1])
    return ("\n".join(lines)+"\n").encode()


def test_exact_original_MAST_pair_refuses_wrong_source():
    assert set(select_exact_source_products(manifest()))==set(KNOWN_SECTORS)
    with pytest.raises(ValueError,match="exactly one"):
        select_exact_source_products(manifest(valid=False))


def test_original_neighbor_row_and_duplicate_fail_closed():
    row=neighbor_catalog_row(original_neighbor_csv())
    assert row["neighbor_TIC"]==NEIGHBOR
    assert row["catalog_separation_arcsec"]==pytest.approx(5.1)
    with pytest.raises(ValueError,match="unique"):
        neighbor_catalog_row(original_neighbor_csv(duplicates=True))


def test_original_exofop_sexagesimal_RA_and_DEC_are_not_misread_as_degrees():
    blob=(
        "TIC ID,TOI,RA,Dec,Separation (arcsec),Position Angle (deg E. of N.)\n"
        "82302236,4255.01,08:17:24.6,-35:15:12.1,5.10,31.21\n"
    ).encode()
    x=neighbor_catalog_row(blob)
    assert x["neighbor_RA_deg"]==pytest.approx(124.3525,abs=.00001)
    assert x["neighbor_Dec_deg"]==pytest.approx(-35.2533611111,abs=.00001)


def test_moment_centroid_offtarget_neighbor_physically_points_away_not_toward():
    assert physical_away_alignment([-1,0],[1,0])==pytest.approx(0.)
    assert physical_away_alignment([1,0],[1,0])==pytest.approx(180.)
    assert physical_away_alignment([0,1],[1,0])==pytest.approx(90.)
    assert physical_away_alignment([0,0],[1,0]) is None


def test_WCS_sky_neighbor_direction_not_pixel_angle_guess():
    w=WCS(naxis=2)
    w.wcs.crpix=[5,5]
    w.wcs.crval=[100.,10.]
    w.wcs.cdelt=[-.0058,.0058]
    w.wcs.ctype=["RA---TAN","DEC--TAN"]
    target=SkyCoord(100*u.deg,10*u.deg)
    n=target.directional_offset_by(31.21*u.deg,5.1*u.arcsec)
    g=position_geometry(w,target,{
        "neighbor_RA_deg":n.ra.deg,
        "neighbor_Dec_deg":n.dec.deg,
        "catalog_separation_arcsec":5.10,
        "catalog_position_angle_deg":31.21
    })
    assert g["catalog_sky_geometry_consistent_with_TPF_target_position"]
    assert g["header_to_neighbor_angular_separation_arcsec"]==pytest.approx(5.1,abs=.001)
    assert g["position_angle_difference_from_original_catalog_deg"]<.01
    assert np.linalg.norm(g["target_to_neighbor_CCD_pixel_vector"])>0


def test_same_genuine_orbit_in_and_out_windows_preserved_in_pairing():
    t=np.arange(0,12,.01)
    phase=(t-1.+1)%2-1
    inside=np.abs(phase)<.075
    flux=np.ones(len(t))-inside.astype(float)*.012
    x=300.+.008*t + inside.astype(float)*(-.01)
    y=500.+.01*t
    f=pd.DataFrame({
        "time_BTJD":t,
        "relative_PDCSAP_flux":flux,
        "raw_moment_CCD_x_pixels":x,
        "raw_moment_CCD_y_pixels":y,
        "pointing_correction_x_pixels":.008*t,
        "pointing_correction_y_pixels":.01*t,
        "corrected_moment_x_pixels":x-.008*t,
        "corrected_moment_y_pixels":y-.01*t
    })
    geom={
        "target_to_neighbor_CCD_pixel_vector":[1.,0.],
        "catalog_sky_geometry_consistent_with_TPF_target_position":True
    }
    pairs,account=paired_original_events(f,2.,1.,.15,geom)
    assert len(pairs)>=4
    assert account["exact_same_orbit_event_pairs"]==len(pairs)
    assert all(z["original_PDCSAP_local_flux_depth"]>.005 for z in pairs)
    assert np.median([z["pointing_subtracted_angle_away_from_known_neighbor_deg"] for z in pairs])<5
    outcome=summarize_pairs(pairs,geom,sector=61)
    assert outcome["minimum_three_complete_events"] is True
    assert outcome["source_directional_assessment"]=="descriptive_only_posthoc_not_physical_validation"
