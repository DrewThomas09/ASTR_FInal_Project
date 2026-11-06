"""Offline shape and physics tests for real-data injection utilities.

Network access and the actual Kepler retrieval are tested separately in GitHub Actions.
"""
import numpy as np
import pytest
from real_kepler_lightcurve import insert_known_transit


def test_injection_does_not_mutate_original_observations():
    time=np.linspace(0,60,6001)
    original=np.ones_like(time)
    updated, mask=insert_known_transit(time,original,6.4,1.1,3000,.16)
    assert np.array_equal(original,np.ones_like(time))
    assert updated.shape==original.shape
    assert int(mask.sum())>0
    assert np.allclose(updated[mask],.997)
    assert np.allclose(updated[~mask],1.)


def test_injection_is_periodic_and_uses_no_target_labels():
    t=np.arange(0,60,.01)
    result,mask=insert_known_transit(t,np.ones_like(t),4.,.2,1000.,.1)
    phase=(t-.2+2)%4-2
    assert np.array_equal(mask,np.abs(phase)<.05)
    assert int(mask.sum())>0
    assert result[mask].mean()<result[~mask].mean()


def test_reject_unphysical_injections():
    t=np.arange(100)
    f=np.ones(100)
    with pytest.raises(ValueError):
        insert_known_transit(t,f,0.,0.,1000.,.1)
    with pytest.raises(ValueError):
        insert_known_transit(t,f,4.,0.,1000.,2.)
    with pytest.raises(ValueError):
        insert_known_transit(t,f,4.,0.,-1.,.1)
    with pytest.raises(ValueError):
        insert_known_transit(t,f[:-1],4.,0.,1000.,.1)
