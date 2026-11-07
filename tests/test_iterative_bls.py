"""Regression checks for sequential BLS; astrophysical recovery is separate."""
import numpy as np
import pytest

astropy=pytest.importorskip("astropy")
from iterative_bls import search_iteratively, match_reference_period, subtract_best_transit


def test_reference_matching_does_not_pass_truth_into_fitting():
    result=match_reference_period(7.6417,{"A":3.5,"B":7.64159})
    assert result["closest_known_planet"]=="B"
    assert result["within_2pct_of_known_planet"] is True


def test_subtracting_box_transit_preserves_shape():
    t=np.arange(0,42,.03)
    f=1+np.random.default_rng(45).normal(0,.0002,len(t))
    p=3.7;epoch=.6;duration=.15
    phase=(t-epoch+p/2)%p-p/2
    f[np.abs(phase)<duration/2]-=.010
    peaks,residual=search_iteratively(t,f,n_components=1,bounds=(1.5,9.))
    assert len(peaks)==1
    assert len(residual)==len(f)
    assert np.isfinite(residual).all()
    assert abs(peaks.iloc[0]["period_days"]-p)/p<.04
    assert np.std(residual)<np.std(f)


def test_component_count_is_bounded():
    with pytest.raises(ValueError):
        search_iteratively(np.arange(120),np.ones(120),n_components=0)
