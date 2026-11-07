"""Physics/engineering checks on new localized-step rule; not survey accuracy."""
import json
from pathlib import Path

import numpy as np
import pytest
from localized_discontinuity import (
    localized_downward_step_mask,synthetic_spsd_like_step)
from kepler_preprocessing import normalize_flux


PARAMS=json.loads(Path("LOCALIZED_STEP_STUDY_FROZEN_2026_11_07.json").read_text())["preprocessing"]


def fixture():
    t=np.arange(0,66,.02043)
    raw=25000*(1+np.random.default_rng(701).normal(0,.0002,len(t)))
    return t,raw


def test_stylized_step_detected_at_unknown_epoch():
    t,raw=fixture()
    source=raw.copy()
    changed,_=synthetic_spsd_like_step(t,raw,23.4,.011,.75,.45)
    mask,diagnostic=localized_downward_step_mask(t,normalize_flux(changed),PARAMS)
    assert np.array_equal(raw,source)  # no data mutation
    assert diagnostic["n_persistent_step_events"]>=1
    assert any(abs(event["time_bkjd"]-23.4)<.15
               for event in diagnostic["detected_events"])
    assert not mask[np.argmin(abs(t-23.4))]


def test_standalone_short_transit_is_not_stable_step():
    t,raw=fixture()
    changed=raw.copy()
    phase=(t-21.17+2.)%4.-2.
    changed[np.abs(phase)<.08]*=.990
    mask,diagnostic=localized_downward_step_mask(t,normalize_flux(changed),PARAMS)
    assert diagnostic["n_persistent_step_events"]==0
    assert mask.all()


def test_one_cadence_drop_does_not_persist():
    t,raw=fixture()
    raw[np.argmin(abs(t-20.))]*=.978
    mask,diagnostic=localized_downward_step_mask(t,normalize_flux(raw),PARAMS)
    assert diagnostic["n_persistent_step_events"]==0
    assert mask.all()


def test_stylized_step_is_multiplicative_and_non-mutating():
    t,raw=fixture()
    before=raw.copy()
    updated,onward=synthetic_spsd_like_step(t,raw,20.,.01,1.,.45)
    assert np.array_equal(raw,before)
    assert np.all(updated[~onward]==raw[~onward])
    assert np.all(updated[onward]<raw[onward])
    assert updated[-1]/raw[-1]==pytest.approx(1-.01*.45,rel=.001)


def test_no_known_planet_label_or_epoch_is_required():
    t,raw=fixture()
    mask,diagnostic=localized_downward_step_mask(t,normalize_flux(raw),PARAMS)
    assert mask.shape==t.shape
    assert "source_label" not in diagnostic
    assert "planet_period" not in diagnostic


def test_invalid_inputs_rejected():
    t,raw=fixture()
    with pytest.raises(ValueError):
        synthetic_spsd_like_step(t,raw,19.,-.05,.8,.4)
    with pytest.raises(ValueError):
        localized_downward_step_mask(t[::-1],raw[::-1],PARAMS)
