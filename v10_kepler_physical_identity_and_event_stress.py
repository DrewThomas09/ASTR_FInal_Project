"""Reproduce the Kepler Q6/Q7 physical clock and event outlier diagnostic.

Input: unchanged 2026-11-13 GitHub Actions artifact 14079785749 (ZIP).
Run: python v10_kepler_physical_identity_and_event_stress.py FORECAST.zip
This is a post-hoc interpretation of the originally frozen successful experiment,
not a new period fit or a rerun of its phase-shift hypothesis test.
"""
import io, json, sys, zipfile
import numpy as np
import pandas as pd
PUBLISHED = {
  "Kepler-35": {"stellar_binary": 20.7337, "planet_orbit": 131.458},
  "Kepler-47": {"stellar_binary": 7.44838, "planet_orbit": 49.5},
}
def run(path):
    with zipfile.ZipFile(path) as z:
        rows = pd.read_csv(z.open("all_12_prespecified_sources.csv"))
        events = pd.read_csv(z.open("q7_individual_predicted_event_depths.csv"))
        nulls = pd.read_csv(z.open("q7_phase_shift_nulls.csv"))
        plan = json.load(z.open("frozen_input_manifest.json"))
    assert len(rows)==12 and len(events)==145 and len(nulls)==11000
    assert plan["method_frozen"]["no_test_reoptimization"] is True
    out = {}
    for target in ["Kepler-12","Kepler-30","Kepler-35","Kepler-47"]:
        r = rows.loc[rows.source_name==target].iloc[0]
        e = events.loc[events.source_name==target].sort_values("predicted_epoch_bkjd")
        depth = e.local_depth_fraction.to_numpy()*1e6
        reduced = np.delete(depth, depth.argmax())
        out[target] = {
          "q6_bls_days":float(r.q6_train_best_period_days),
          "event_count":len(depth),
          "positive_events":int((depth>0).sum()),
          "mean_depth_ppm":float(depth.mean()),
          "median_depth_ppm":float(np.median(depth)),
          "deepest_event_ppm":float(depth.max()),
          "mean_without_deepest_ppm":float(reduced.mean()),
          "frozen_pass":bool(r.predictive_evidence),
        }
        if target in PUBLISHED:
            out[target]["published_physical_periods"] = PUBLISHED[target]
    assert out["Kepler-30"]["positive_events"]==3
    assert np.isclose(out["Kepler-30"]["mean_without_deepest_ppm"],-19.7435427191)
    assert out["Kepler-12"]["positive_events"]==20
    print(json.dumps(out, indent=2))
if __name__=="__main__": run(sys.argv[1])
