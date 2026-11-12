"""Synthetic test fixtures, NOT source-verified astrophysical positions."""
import numpy as np
import pandas as pd
import pytest
from astropy.io import fits
from astropy.wcs import WCS

from exofop_two_ground_NEBS_actual_aperture_sky_WCS_ID import (
    median_original_ground_aperture_xy,ground_aperture_sky_position,
    original_ground_plate_wcs,NEIGHBOR_REVIEW_RADIUS_ARCSEC
)


def test_predefined_named_aperture_pixel_coordinates_not_any_pixel():
    data=pd.DataFrame({
       "X(FITS)_T1":np.array([500.,501.,499.]),
       "Y(FITS)_T1":np.array([500.,501.,499.]),
       "X(FITS)_T6":np.full(18,600.),
       "Y(FITS)_T6":np.full(18,550.)
    })
    with pytest.raises(ValueError,match="too few"):
        median_original_ground_aperture_xy(data,"T1")
    xy,stats=median_original_ground_aperture_xy(data,"T6")
    assert xy.tolist()==[600.,550.]
    assert stats["n_original_ground_pixel_aperture_rows"]==18
    with pytest.raises(ValueError,match="aperture columns absent"):
        median_original_ground_aperture_xy(data,"T11")


def test_exact_source_sha_original_ground_plate_wcs_and_FITS_origin_1(tmp_path):
    import hashlib
    w=WCS(naxis=2)
    w.wcs.crval=[120.,-20.]
    w.wcs.crpix=[50.,50.]
    w.wcs.cdelt=[-.0001,.0001]
    w.wcs.ctype=["RA---TAN","DEC--TAN"]
    path=tmp_path/"ground.fits"
    fits.PrimaryHDU(data=np.ones((100,100)),header=w.to_header()).writeto(path)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    s,shape=original_ground_plate_wcs(path,digest)
    assert shape==(100,100)
    sky=ground_aperture_sky_position(s,[50,50],shape)
    assert sky.ra.deg==pytest.approx(120.,abs=1e-8)
    assert sky.dec.deg==pytest.approx(-20.,abs=1e-8)
    with pytest.raises(ValueError,match="outside"):
        ground_aperture_sky_position(s,[150,50],shape)
    with pytest.raises(ValueError,match="SHA256"):
        original_ground_plate_wcs(path,"0"*64)


def test_no_posthoc_adjustment_of_declared_neighbor_review_tolerance():
    assert NEIGHBOR_REVIEW_RADIUS_ARCSEC==5.0
