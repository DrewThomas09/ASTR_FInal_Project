"""Synthetic TPF pixel cube fixtures. NOT observed physical eclipse localizations."""
import numpy as np
import pytest
from tess_two_ground_neb_original_TPF_pixel_difference_images_nov12 import (
    EXACT_HOSTS,PHASES,true_per_event_pixel_differences,spatial_summary_fixed_bit8,
    ELIGIBLE_TRUE_EVENTS,ELIGIBLE_EACH_CONTROL_EVENTS
)

def synthetic_TPF():
    t=np.arange(0,12,.02)
    cube=np.full((len(t),5,5),100.,dtype=float)
    # Exactly specified synthetic eclipses: center at 1,3,5,...
    for k in range(6):
        inside=np.abs(t-(1+2*k))<=.1
        cube[inside,3,3]-=30
    mask=np.zeros((5,5),dtype=bool)
    mask[1:5,1:5]=True
    q=np.zeros(len(t),dtype=int)
    return t,cube,q,mask


def test_correct_original_pixel_difference_recovers_fixed_neighbor_dimming():
    t,cube,q,mask=synthetic_TPF()
    events,coverage=true_per_event_pixel_differences(
        t,cube,q,mask,period=2.,epoch=1.,duration=.2,phase=0.)
    assert len(events)>=4
    for e in events:
        assert e["measured_out_minus_in_TPF_flux_image_electrons_per_second"][3,3]==pytest.approx(30)
    result,img=spatial_summary_fixed_bit8(events,mask,host_xy=[2,2],neighbor_xy=[3,3])
    assert result["brightest_pixel_is_geometrically_closer_to_reported_neighbor"]
    assert result["positive_pixel_diff_image_center_closer_to_reported_neighbor"]
    assert img[3,3]==pytest.approx(30)
    assert result["original_selected_pixel_positive_difference_count"]==1


def test_fixed_quarter_shift_should_not_be_called_true_eclipse():
    t,cube,q,mask=synthetic_TPF()
    controls,counts=true_per_event_pixel_differences(
        t,cube,q,mask,period=2.,epoch=1.,duration=.2,phase=.25)
    value,image=spatial_summary_fixed_bit8(controls,mask,[2,2],[3,3])
    assert value["original_selected_pixel_sum_positive_clipped_diff_electrons_per_second"]==pytest.approx(0,abs=1e-8)
    assert value["positive_pixel_weighted_diff_image_xy_zero_origin"] is None


def test_ground_supported_original_hosts_and_control_phases_are_fixed():
    assert EXACT_HOSTS=={382437043:382437045,264303333:1884344804}
    assert PHASES==(0.,-.25,.25)
    assert ELIGIBLE_TRUE_EVENTS==3 and ELIGIBLE_EACH_CONTROL_EVENTS==3


def test_missing_source_masks_or_bad_periods_fail_not_synthetic_values():
    t,cube,q,mask=synthetic_TPF()
    with pytest.raises(ValueError,match="bit-8"):
        true_per_event_pixel_differences(t,cube,q,np.zeros_like(mask),2.,1.,.2)
    with pytest.raises(ValueError,match="Invalid original"):
        true_per_event_pixel_differences(t,cube,q,mask,2.,1.,3.)
    with pytest.raises(ValueError,match="shapes inconsistent"):
        true_per_event_pixel_differences(t,cube[:-1],q,mask,2.,1.,.2)
    assert spatial_summary_fixed_bit8([],mask,[2,2],[3,3])[0][
        "status"]=="no_original_complete_pixel_difference_events"
