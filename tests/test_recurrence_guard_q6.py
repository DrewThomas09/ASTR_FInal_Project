"""Offline recurrence-guard engineering tests, not real Kepler performance."""
import json
from pathlib import Path

import numpy as np
import pytest

from recurrence_guard_q6 import (
    MANIFEST, OLD_SETTINGS, load_protocol, validate_guard_config,
    local_dip_depth, candidate_periodic_context,
    run_original_and_guarded, results_summary
)
from kepler_preprocessing import normalize_flux
from localized_discontinuity import synthetic_spsd_like_step


GUARD=json.loads(Path(MANIFEST).read_text())["recurrence_guard"]
OLD=json.loads(Path(OLD_SETTINGS).read_text())["preprocessing"]


def fake_star():
    t=np.arange(0,88,.02043)
    f=1+np.random.default_rng(99).normal(0,.00015,len(t))
    return t,f


def recurring(t, f, epoch=20.1, period=7.45, amplitude=.017):
    y=f.copy()
    phase=(t-epoch+period/2)%period-period/2
    y[np.abs(phase)<.13]*=(1-amplitude)
    return y


def test_manifest_has_13_fresh_hosts_without_kepler47():
    cfg=load_protocol()
    assert len(cfg["sources"])==13
    assert len({row["kic"] for row in cfg["sources"]})==13
    assert 10020423 not in {row["kic"] for row in cfg["sources"]}
    assert sum(row["role"]=="published_eclipsing_binary"
               for row in cfg["sources"])==8


def test_guard_rejects_changed_frozen_parameters():
    settings=dict(GUARD)
    settings["minimum_other_cycles_showing_a_dip"]=2
    with pytest.raises(ValueError):
        validate_guard_config(settings)


def test_repeated_7p45_day_eclipse_is_protected_using_only_flux():
    t, raw=fake_star()
    f=recurring(t,raw)
    context=candidate_periodic_context(t,f,20.1,GUARD)
    assert context["protected_as_periodic"]
    assert context["supporting_other_cycles"]>=3
    assert context["recurrence_fraction"]>=.75
    assert context["recovered_period_days"] is not None
    assert abs(context["recovered_period_days"]-7.45)<.07 or (
        abs(context["recovered_period_days"]-14.9)<.10)


def test_isolated_box_transit_not_enough_to_be_periodic():
    t, f=fake_star()
    f[(t>=19.98)&(t<=20.20)] *= .98
    context=candidate_periodic_context(t,f,20.10,GUARD)
    assert not context["protected_as_periodic"]


def test_persistent_step_does_not_automatically_count_as_multiple_eclipses():
    t, f=fake_star()
    f[t>=26.2]*=.987
    info=candidate_periodic_context(t,f,26.2,GUARD)
    assert not info["protected_as_periodic"]


def test_realistic_spsd_like_step_on_stable_flux_not_periodic():
    t,f=fake_star()
    changed,_=synthetic_spsd_like_step(t,f,32.11,.012,.85,.4)
    prepared=normalize_flux(changed)
    info=candidate_periodic_context(t,prepared,32.11,GUARD)
    assert not info["protected_as_periodic"]


def test_gap_rejects_misleading_trough_window():
    t,f=fake_star()
    f=recurring(t,f)
    mask=~((t>19.98)&(t<20.24))
    assert local_dip_depth(t[mask],f[mask],20.1,GUARD) is None


def test_unchanged_step_screen_protects_noisy_unflagged_source():
    t, f=fake_star()
    base,guard,warnings=run_original_and_guarded(t,f,OLD,GUARD)
    assert base.shape == guard.shape == t.shape
    assert np.all(guard[~base])
    assert len(warnings)==0
    assert np.array_equal(base,guard)


def test_monotonic_time_is_required_and_inputs_not_mutated():
    t,f=fake_star()
    old=f.copy()
    with pytest.raises(ValueError):
        candidate_periodic_context(t[::-1],f[::-1],20.1,GUARD)
    assert np.array_equal(old,f)


def test_results_summary_includes_failed_targets_and_preserves_roles():
    plan={"sources":[{"kic":1},{"kic":2}]}
    rows=[{
        "kic":1,"status":"analyzed",
        "literature_role":"published_eclipsing_binary","product":"SAP",
        "n_original_step_warnings":1,"n_warnings_protected_as_periodic":0,
        "n_cadences_spared":0,"n_spsd_archival_event_clusters":0,
        "n_archival_spsd_events_with_protected_warning":0,
    }, {"kic":2,"status":"source_or_analysis_error"}]
    r=results_summary(rows,[],plan)
    assert r["n_planned_stars"]==2
    assert r["n_analyzed_stars"]==1
    assert r["n_missing_stars"]==1
    assert r["missing_kics"]==[2]


def test_keep_mask_superset_for_actual_detected_artificial_step():
    t,f=fake_star()
    raw=40000*f
    changed,_=synthetic_spsd_like_step(t,raw,23.4,.011,.75,.45)
    prepared=normalize_flux(changed)
    original, guarded, warnings=run_original_and_guarded(t,prepared,OLD,GUARD)
    assert len(warnings)>=1
    assert np.any(~original)
    # Recurrence guard can restore previously masked cadences but can never
    # mask additional cadences that the old detector kept.
    assert np.all(guarded[original])
    assert np.all(guarded.astype(int)>=original.astype(int))
