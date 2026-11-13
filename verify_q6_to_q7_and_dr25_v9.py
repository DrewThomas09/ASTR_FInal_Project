"""Verify original Kepler Q6->Q7 holdout and archived high-SNR screening counts.
Usage: python verify_q6_to_q7_and_dr25_v9.py FORECAST.zip MODEL.zip
Reads the unchanged successful 2026-11-13 source run and archived 1,619
NASA KOI predictions; no refitting, no threshold tuning, no network calls.
"""
import sys,io,json,zipfile,hashlib
import pandas as pd
import numpy as np

ORIGINAL_PREDICTION_SHA="3682e0be30506ddcfe4bbb0c683ed6884454c5e5fb8d946922fb48248712663"

def verify(forecast_archive,model_archive):
    with zipfile.ZipFile(forecast_archive) as z:
        plan=json.loads(z.read("frozen_input_manifest.json"))
        summary=json.loads(z.read("q6_to_q7_summary.json"))
        stars=pd.read_csv(io.BytesIO(z.read("all_12_prespecified_sources.csv")))
        events=pd.read_csv(io.BytesIO(z.read("q7_individual_predicted_event_depths.csv")))
        phases=pd.read_csv(io.BytesIO(z.read("q7_phase_shift_nulls.csv")))
    assert len(plan["published_sources"])==12
    assert plan["training_quarter"]==6 and plan["prospective_test_quarter"]==7
    assert plan["method_frozen"]["no_test_reoptimization"] is True
    assert plan["method_frozen"]["phase_null_shift_count"]==1000
    assert len(stars)==12 and stars.kic.nunique()==12
    assert len(events)==145 and len(phases)==11000
    assert stars.status.eq("both_original_FITS_analyzed").sum()==11
    assert summary["new_published_planet_host_stratum"]["positive_predicted_dip_evidence"]==6
    assert summary["previously_examined_binary_controls"]["positive_predicted_dip_evidence"]==2
    for row in stars.itertuples():
        if row.status!="both_original_FITS_analyzed":
            assert row.source_name=="Kepler-17"
            continue
        star_events=events.loc[events.kic==row.kic]
        comparisons=phases.loc[phases.kic==row.kic]
        assert len(star_events)==int(row.n_usable_predicted_events_q7)
        assert len(comparisons)==1000
        positives=float((star_events.local_depth_fraction>0).mean())
        fraction=(1+(comparisons.mean_local_depth>=row.mean_predicted_event_depth).sum())/(len(comparisons)+1)
        assert np.isclose(positives,row.positive_event_fraction)
        assert np.isclose(fraction,row.relative_phase_shift_fraction)
        assert bool(row.predictive_evidence)==(positives>=.6 and fraction<=.01)
    with zipfile.ZipFile(model_archive) as z:
        raw=z.read("primary_heldout_paired_predictions.csv")
    assert hashlib.sha256(raw).hexdigest()==ORIGINAL_PREDICTION_SHA
    d=pd.read_csv(io.BytesIO(raw))
    assert len(d)==1619 and d.kepid.nunique()==1385
    strong=d.loc[(d.koi_model_snr>=100)&d.koi_depth.notna()]
    assert len(strong)==391
    y=strong.historical_nasa_candidate_label
    p=strong.prediction_random_forest
    assert int(y.sum())==79 and int((y==0).sum())==312
    assert int(((y==0)&(p==0)).sum())==291
    assert int(((y==1)&(p==0)).sum())==24
    deep=strong.koi_depth>=10000
    assert (int(deep.sum()),int(y[deep].sum()),int((~deep).sum()),int(y[~deep].sum()))==(260,22,131,57)
    result={"planned_sources":12,"usable_source_pairs":11,
            "planet_hosts_passed_out_of_planned": "6/10",
            "binary_controls_passed": "2/2",
            "predicted_event_windows":len(events),
            "phase_comparisons":len(phases),
            "high_snr_koi":len(strong),
            "historic_false_positive_labels":312,
            "forest_rejected_high_snr_historic_false_positives":291,
            "forest_missed_high_snr_historic_candidates":24}
    print(json.dumps(result,indent=2))
    return result
if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("Usage: python verify_q6_to_q7_and_dr25_v9.py FORECAST.zip MODEL.zip")
    verify(sys.argv[1],sys.argv[2])
