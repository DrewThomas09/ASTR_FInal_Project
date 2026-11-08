"""ExoMiner-*inspired* feature view tests; these do not test NASA's model."""
import json
import numpy as np
import pytest
from exominer_inspired_kepler_views import (
    VIEW_SIZES, validate_light_curve, normalized_phase, binned_median,
    individual_event_views, build_prototype_views
)


def sample(period=4.5, duration=.16, depth=.009, secondary=0, seed=19):
    t=np.arange(0,90,.02043)
    f=1+np.random.default_rng(seed).normal(0,.00015,len(t))
    primary=normalized_phase(t,period,2.)
    f[np.abs(primary)<duration/2]-=depth
    if secondary:
        phase2=normalized_phase(t,period,2.+.5*period)
        f[np.abs(phase2)<duration/2]-=secondary
    return t,f,period,2.,duration


def test_documented_view_shapes_match_design_without_claiming_nasa_inference():
    t,f,p,e,d=sample()
    arrays,notes=build_prototype_views(t,f,p,e,d)
    for key,wanted in VIEW_SIZES.items():
        assert arrays[key].shape==wanted
    assert "Not accepted by pretrained ExoMiner++" in notes["not_nasa_model_input"]
    assert arrays["prototype_unfolded_20_by_31"].shape==(20,31)


def test_correct_transit_phase_has_local_depth():
    t,f,p,e,d=sample()
    views,_=build_prototype_views(t,f,p,e,d)
    local=views["prototype_local_flux"][:,0]
    edge=np.r_[local[:5],local[-5:]]
    assert float(np.median(edge)-np.median(local[14:17]))>.005


def test_secondary_eclipse_branch_detects_eb_only_if_secondary_exists():
    a=sample(secondary=.005)
    b=sample(secondary=0)
    va,_=build_prototype_views(*a)
    vb,_=build_prototype_views(*b)
    center_a=float(np.median(va["prototype_secondary_flux"][14:17,0]))
    center_b=float(np.median(vb["prototype_secondary_flux"][14:17,0]))
    assert center_b-center_a>.003


def test_odd_even_are_orbit_based_and_not_adjacent_cadences():
    t,f,p,e,d=sample()
    cycle=np.rint((t-e)/p).astype(int)
    phase=normalized_phase(t,p,e)
    f[(np.abs(phase)<d/2)&((cycle%2)==0)]-=.011
    views,_=build_prototype_views(t,f,p,e,d)
    even=float(np.median(views["prototype_local_even_flux"][14:17,0]))
    odd=float(np.median(views["prototype_local_odd_flux"][14:17,0]))
    assert odd-even>.006


def test_20_row_unfolded_stack_has_a_dip_on_every_observed_event():
    t,f,p,e,d=sample()
    views,meta=build_prototype_views(t,f,p,e,d)
    assert meta["n_usable_individual_events"]>=19
    data=views["prototype_unfolded_20_by_31"]
    mask=views["prototype_unfolded_20_by_31_observed"]
    assert data.shape==(20,31)
    for i in range(meta["n_events_in_20_row_stack"]):
        valid=np.flatnonzero(mask[i,13:18])+13
        assert len(valid)>0
        assert data[i,valid].min()<.995


def test_padding_is_neutral_but_explicitly_masked_not_fake_evidence():
    t,f,p,e,d=sample(period=12)
    views,meta=build_prototype_views(t,f,p,e,d)
    n=meta["n_events_in_20_row_stack"]
    assert 2<=n<20
    data=views["prototype_unfolded_20_by_31"]
    mask=views["prototype_unfolded_20_by_31_observed"]
    assert np.all(data[n:]==1.)
    assert not mask[n:].any()
    assert np.isnan(views["prototype_unfolded_epochs_bkjd"][n:]).all()


def test_binning_missing_time_cadences_are_not_called_measurements():
    t=np.array([-1.0,-.8,.8,1.0])
    f=np.array([1.,1.,.99,1.])
    binned,occupied=binned_median(t,f,31,1.1)
    assert binned.shape==(31,)
    assert int(occupied.sum())<=4
    assert np.all(binned[~occupied]==1.)


def test_invalid_time_order_rejected_and_no_source_is_mutated():
    t,f,p,e,d=sample()
    copy=f.copy()
    with pytest.raises(ValueError):
        build_prototype_views(t[::-1],f[::-1],p,e,d)
    _=build_prototype_views(t,f,p,e,d)
    assert np.array_equal(copy,f)


def test_no_data_in_local_window_avoids_invented_transit():
    t=np.arange(0,90,.02043)
    f=np.ones_like(t)
    t=t[np.abs(normalized_phase(t,4.5,2.))>.41]
    f=np.ones_like(t)
    views,meta=build_prototype_views(t,f,4.5,2.,.16)
    assert meta["n_usable_individual_events"]==0
    assert not views["prototype_local_flux_observed"].any()
    assert not views["prototype_unfolded_20_by_31_observed"].any()


def test_transit_truth_is_not_needed_by_view_builder():
    t,f,p,e,d=sample()
    a,_=build_prototype_views(t,f,p,e,d)
    b,_=build_prototype_views(t,f,p,e,d)
    for key in VIEW_SIZES:
        assert np.array_equal(a[key],b[key])


def test_phase_wraps_at_half_period():
    p=4
    sample_t=np.array([-2.,-.1,0.,.1,2.])
    phase=normalized_phase(sample_t,p,0)
    assert np.all(phase>=-2)
    assert np.all(phase<2)
    assert phase[0]==-2 and phase[-1]==-2
