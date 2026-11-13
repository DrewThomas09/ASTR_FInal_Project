"""ASTR 12600 Kepler model and event stability reanalysis, November 13 2026.
Reads the original v5 and v6 archived ZIPs, without refitting the classifier.
Usage: python kepler_matched_recall_and_event_bootstrap_v7.py MODEL.zip EVENTS.zip
"""
import io
import json
import sys
import zipfile
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, roc_auc_score

def fpr_at_ninety(y, score):
    fpr, tpr, _ = roc_curve(y, score)
    return float(np.interp(0.90, tpr, fpr))

def run(model_path, event_path):
    with zipfile.ZipFile(model_path) as z:
        data = pd.read_csv(z.open("primary_heldout_paired_predictions.csv"))
    assert len(data) == 1619 and data.kepid.nunique() == 1385
    labels = data.historical_nasa_candidate_label.to_numpy(dtype=int)
    assert labels.sum() == 851
    features = {
        "forest": "score_random_forest",
        "logistic": "score_logistic_4feature",
        "snr": "score_SNR_only",
    }
    scores = {name: data[col].to_numpy(dtype=float) for name, col in features.items()}
    host_groups = [g.index.to_numpy() for _, g in data.groupby("kepid", sort=True)]
    rng = np.random.default_rng(20261113)
    samples = {name: [] for name in features}
    samples["forest_minus_logistic"] = []
    for _ in range(2000):
        chosen = rng.integers(0, len(host_groups), len(host_groups))
        ix = np.concatenate([host_groups[int(k)] for k in chosen])
        yy = labels[ix]
        if np.unique(yy).size < 2:
            continue
        rates = {name: fpr_at_ninety(yy, s[ix]) for name, s in scores.items()}
        for name, value in rates.items():
            samples[name].append(value)
        samples["forest_minus_logistic"].append(rates["forest"] - rates["logistic"])
    result = {
        "method": "Retrospective ROC at 90% historical-label candidate recall; no new operational cutoff",
        "n_test_signals": 1619,
        "n_unique_stars": 1385,
        "bootstrap_seed": 20261113,
        "bootstrap_unit": "entire Kepler host star",
        "models": {},
    }
    for name, s in scores.items():
        result["models"][name] = {
            "fpr_at_recall_90": fpr_at_ninety(labels, s),
            "auroc": float(roc_auc_score(labels, s)),
            "star_bootstrap_interval_95": np.quantile(samples[name], [0.025, 0.975]).tolist(),
        }
    result["forest_minus_logistic_fpr_interval_95"] = np.quantile(
        samples["forest_minus_logistic"], [0.025, 0.975]
    ).tolist()
    result["quarter_events"] = {}
    with zipfile.ZipFile(event_path) as z:
        for kic, name in ((11804465, "Kepler-12"), (9837578, "Kepler-35")):
            item = {}
            for quarter in (6, 7):
                base = "data/event_tables/"
                events = pd.read_csv(io.BytesIO(z.read(
                    f"{base}KIC{kic}_Q{quarter}_observed_event_morphology.csv"
                )))
                summary = json.loads(z.read(
                    f"{base}real_source_event_shape_summary_Q{quarter}.json"
                ))
                params = next(record["upstream_Q_only_BLS"]
                    for record in summary["source_results"] if record["kic"] == kic)
                depths = 100 * events.signed_local_depth_fraction.to_numpy(float)
                rng_events = np.random.default_rng(20261113 + kic + quarter)
                resampled = depths[rng_events.integers(
                    len(depths), size=(10000, len(depths))
                )]
                item[f"Q{quarter}"] = {
                    "number_of_events": len(depths),
                    "period_days": params["period_days"],
                    "epoch_bkjd": params["transit_time_days"],
                    "median_depth_percent": float(np.median(depths)),
                    "event_bootstrap_median_interval_95": np.quantile(
                        np.median(resampled, axis=1), [0.025, 0.975]
                    ).tolist(),
                }
                if quarter == 7:
                    q7_centers = events.predicted_epoch_bkjd.to_numpy(float)
            period = item["Q6"]["period_days"]
            epoch = item["Q6"]["epoch_bkjd"]
            forecast_centers = epoch + np.rint((q7_centers - epoch) / period) * period
            item["retrospective_q6_forecast_vs_q7_refit_median_abs_minutes"] = float(
                np.median(np.abs(q7_centers - forecast_centers)) * 1440
            )
            result["quarter_events"][name] = item
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python script.py model_source.zip quarter_events.zip")
    run(sys.argv[1], sys.argv[2])
