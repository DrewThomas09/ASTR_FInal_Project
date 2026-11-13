"""Synthetic TESS SPOC mask/WCS test fixture, NOT original observed pixels."""
import numpy as np
import pytest
from astropy.wcs import WCS
from tess_two_ground_neb_original_TPF_aperture_mask_check_nov12 import (
    analyze_mask,BIT_OPTIMAL_SAP,BIT_MOMENT_CENTROID,CASES
)


def makewcs():
    w=WCS(naxis=2)
    w.wcs.crpix=[3.,3.]
    w.wcs.crval=[100.,20.]
    w.wcs.cdelt=[-.0001,.0001]
    w.wcs.ctype=["RA---TAN","DEC--TAN"]
    return w


def test_two_physical_masks_are_distinct_and_original_source_positions_fixed():
    assert BIT_OPTIMAL_SAP==2
    assert BIT_MOMENT_CENTROID==8
    assert CASES=={382437043:382437045,264303333:1884344804}
    a=np.zeros((5,5),dtype=int)
    a[2,2]=2|8|1
    a[3,3]=8|1
    w=makewcs()
    primary=w.all_pix2world([[2.,2.]],0)[0]
    neb=w.all_pix2world([[3.,3.]],0)[0]
    z=analyze_mask(w,a,primary,neb)
    assert z["original_optimal_SAP_selected_pixels"]==1
    assert z["original_moment_centroid_selected_pixels"]==2
    assert z["original_optimal_SAP_neighbor_nearest_CCD_pixel_in_mask"] is False
    assert z["original_moment_centroid_neighbor_nearest_CCD_pixel_in_mask"] is True
    assert z["neighbor_within_available_TPF_cutout_pixel_centers_extent"]
    assert z["original_TPF_neighbor_distance_from_primary_CCD_pixels"]==pytest.approx(2**.5,rel=.03)


def test_no_mask_photon_capture_claim_and_source_invalid_fail():
    w=makewcs()
    x=analyze_mask(w,np.zeros((5,5),dtype=int),[100.,20.],[100.0001,20.])
    assert x["original_optimal_SAP_selected_pixels"]==0
    assert x["original_optimal_SAP_nearest_selected_CCD_pixel_center_distance_from_neighbor_pixels"] is None
    assert x["geometric_pixel_mask_DOES_NOT_ESTIMATE_PRF_photon_capture_fraction"] is True
    with pytest.raises(ValueError,match="integer 2D"):
        analyze_mask(w,np.array([[1.1,2.2]]),[100.,20.],[100.0001,20.])
