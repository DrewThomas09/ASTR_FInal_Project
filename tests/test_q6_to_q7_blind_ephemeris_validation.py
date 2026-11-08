"""Engineering tests; real Kepler physics is evaluated separately in Actions."""
from pathlib import Path
import numpy as np
import pytest
import q6_to_q7_blind_ephemeris_validation as q


PROTOCOL=q.load_manifest()
OPT=PROTOCOL["method_frozen"]


def simulated_realistic_series():
    t=np.arange(0,90,.020433)
    f=1+np.random.default_rng(12).normal(0,.0002,len(t))
    return t,f


def add_transits(t,flux,p=4.0,epoch=2.0,depth=.007,duration=.15):
    out=flux.copy()
    phi=(t-epoch+p/2)%p-p/2
    out[np.abs(phi)<duration/2] -= depth
    return out


def test_new_sources_frozen_and_binary_controls_not_called_planets():
    assert len(PROTOCOL["published_sources"])==12
    assert len({s["kic"] for s in PROTOCOL["published_sources"]})==12
    assert sum("known_eclipsing_binary" in s["role"]
               for s in PROTOCOL["published_sources"])==2


def test_changed_manifest_cannot_silently_pass(tmp_path):
    bad=dict(PROTOCOL)
    bad["training_quarter"]=7
    path=tmp_path/"changed.json"
    import json
    path.write_text(json.dumps(bad))
    with pytest.raises(ValueError):
        q.load_manifest(path)


def test_recovered_individual_dip_windows_and_correct_epoch():
    t,f=simulated_realistic_series()
    f=add_transits(t,f)
    ev=q.forecast_events(t,f,p=4,epoch=2,duration=.15)
    assert len(ev)>=20
    assert sum(e["positive_local_depth"] for e in ev)==len(ev)
    assert np.median([e["local_depth_fraction"] for e in ev]) > .005


def test_predicted_events_absent_when_phase_is_wrong():
    t,f=simulated_realistic_series()
    f=add_transits(t,f)
    ev=q.forecast_events(t,f,p=4,epoch=3.0,duration=.15)
    assert len(ev)>=20
    assert np.median([e["local_depth_fraction"] for e in ev])<.001


def test_holdout_real_transit_is_predictive_against_shifted_phases():
    t,f=simulated_realistic_series()
    f=add_transits(t,f)
    options=dict(OPT)
    options["phase_null_shift_count"]=120
    r,ev,null=q.phase_shift_null(t,f,4,2,.15,options,1234)
    assert r["n_usable_predicted_events_q7"]>=20
    assert r["phase_shift_null_trials"]==120
    assert r["positive_event_fraction"]>.9
    assert r["relative_phase_shift_fraction"]<=.01
    assert r["predictive_evidence"]


def test_uninjected_holdout_does_not_invent_repeatable_dips():
    t,f=simulated_realistic_series()
    options=dict(OPT)
    options["phase_null_shift_count"]=120
    r,ev,null=q.phase_shift_null(t,f,4,2,.15,options,1255)
    assert r["n_usable_predicted_events_q7"]>=20
    assert r["phase_shift_null_trials"]==120
    assert not r["predictive_evidence"]


def test_binary_eclipses_can_pass_periodic_prediction_not_proof_of_planet():
    t,f=simulated_realistic_series()
    f=add_transits(t,f,p=4,depth=.015)
    options=dict(OPT)
    options["phase_null_shift_count"]=120
    r,_,_=q.phase_shift_null(t,f,4,2,.15,options,128)
    assert r["predictive_evidence"]


def test_sparse_windows_abstain_without_false_precision():
    t,f=simulated_realistic_series()
    restricted=t<6
    t=t[restricted];f=f[restricted]
    # forecast_events requires >=500 points so use high-cadence truncated
    t=np.arange(0,6,.01)
    f=np.ones(len(t))
    r,_,_=q.phase_shift_null(t,f,5,2,.15,OPT,123)
    assert r["relative_phase_shift_fraction"] is None
    assert not r["predictive_evidence"]


def test_invalid_ordered_time_is_rejected():
    t,f=simulated_realistic_series()
    with pytest.raises(ValueError):
        q.forecast_events(t[::-1],f[::-1],4,2,.15)


def test_summary_includes_sources_with_failed_downloads():
    rows=[
        {"kic":1,"literature_role":"previously_published_planet_host",
         "status":"both_original_FITS_analyzed",
         "n_usable_predicted_events_q7":5,"predictive_evidence":True},
        {"kic":2,"literature_role":"previously_published_planet_host",
         "status":"source_or_analysis_error"},
        {"kic":3,"literature_role":"previously_analyzed_known_eclipsing_binary_control",
         "status":"both_original_FITS_analyzed",
         "n_usable_predicted_events_q7":5,"predictive_evidence":True},
    ]
    out=q.summary(rows)
    p=out["new_published_planet_host_stratum"]
    assert p["planned"]==2
    assert p["analyzed_both_quarters"]==1
    assert p["unavailable_or_errors"]==1
    assert out["previously_examined_binary_controls"]["positive_predicted_dip_evidence"]==1


def test_future_Q7_is_not_opened_until_Q6_BLS_has_completed(monkeypatch):
    opened=[]
    t=np.arange(0,90,.02043); f=np.ones(len(t))
    def fetch(kic,quarter):
        opened.append(quarter)
        if quarter==7:
            assert "bls_complete" in opened
        return t+quarter*100,f,{"sha256":"test","file":f"quarter{quarter}"}
    def bls(times,flux,bounds,frequency_factor):
        assert opened==[6]
        opened.append("bls_complete")
        return {"period_days":5.0,"transit_time_days":600.,
                "duration_days":.15,"score":4.,"depth_ppm":500.}
    monkeypatch.setattr(q,"fetch_kepler_quarter",fetch)
    monkeypatch.setattr(q,"bls_peak",bls)
    options=dict(OPT)
    options["phase_null_shift_count"]=20
    row,_,_,_,_,_=q.source_evaluation(
        {"name":"Test","kic":999999,"role":"previously_published_planet_host"},options)
    assert opened==[6,"bls_complete",7]
    assert row["q6_train_best_period_days"]==5.
