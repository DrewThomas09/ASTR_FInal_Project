"""Reproducible screening comparison on the historical Kepler DR25 KOI catalog.

This script predicts NASA's past Robovetter labels, NOT independently confirmed planets.
Generated with AI assistance; review AI_USE_LOG.md before citing results.
"""
from pathlib import Path
from urllib.parse import urlencode
import argparse, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from sklearn.model_selection import GroupShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score

FEATURES = ["koi_period", "koi_duration", "koi_depth", "koi_model_snr"]
COLS = ["kepid", "kepoi_name", "koi_pdisposition"] + FEATURES
TABLE = "q1_q17_dr25_koi"

def nasa_url():
    query = "select " + ",".join(COLS) + " from " + TABLE
    return "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?" + urlencode({"query": query, "format": "csv"})

def load_data(path, download=False):
    path = Path(path)
    if not path.exists():
        if not download:
            raise FileNotFoundError("Download NASA CSV and save to " + str(path) + "\nURL: " + nasa_url())
        r = requests.get(nasa_url(), timeout=80)
        r.raise_for_status()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(r.content)
    df = pd.read_csv(path, comment="#")
    missing = set(COLS) - set(df.columns)
    if missing:
        raise ValueError("Missing columns: " + str(missing))
    df = df.loc[df.koi_pdisposition.isin(["CANDIDATE", "FALSE POSITIVE"]), COLS].copy()
    df = df.dropna(subset=["kepid", "kepoi_name"]).drop_duplicates("kepoi_name")
    df["label"] = (df.koi_pdisposition == "CANDIDATE").astype(int)
    for col in FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df.loc[~np.isfinite(df[col]) | (df[col] < 0), col] = np.nan
    if len(df) < 500 or df.label.nunique() != 2:
        raise ValueError("Unexpected NASA catalog or insufficient labeled observations")
    return df.reset_index(drop=True)

def split_by_star(df, seed=12600):
    y, groups = df.label.to_numpy(), df.kepid.to_numpy()
    allidx = np.arange(len(df))
    split1 = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
    trainval, test = next(split1.split(allidx, y, groups))
    split2 = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=seed + 1)
    a, b = next(split2.split(trainval, y[trainval], groups[trainval]))
    train, valid = trainval[a], trainval[b]
    for left, right in [(train, valid), (train, test), (valid, test)]:
        assert not set(groups[left]).intersection(groups[right]), "Same-star data leakage!"
    for ix in (train, valid, test):
        assert len(np.unique(y[ix])) == 2
    return train, valid, test

def cutoff(scores, labels, desired=0.90):
    positives = np.asarray(scores)[np.asarray(labels) == 1]
    if not len(positives):
        raise ValueError("Missing positive validation cases")
    k = int(np.ceil(desired * len(positives))) - 1
    return float(np.sort(positives)[::-1][k])

def metrics(y, pred):
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return dict(accuracy=float(accuracy_score(y, pred)),
                recall=float(recall_score(y, pred, zero_division=0)),
                precision=float(precision_score(y, pred, zero_division=0)),
                false_positive_rate=float(fp / (fp + tn)),
                fraction_flagged=float(np.mean(pred)),
                true_positive=int(tp), false_positive=int(fp),
                true_negative=int(tn), false_negative=int(fn))

def experiment(df, output="results/ml"):
    out = Path(output); out.mkdir(parents=True, exist_ok=True)
    train, valid, test = split_by_star(df)
    x = np.log1p(df[FEATURES].clip(lower=0).astype(float))
    y = df.label.to_numpy()
    forest = make_pipeline(
        SimpleImputer(strategy="median"),
        RandomForestClassifier(n_estimators=120, max_depth=9,
                               min_samples_leaf=3, random_state=12600, n_jobs=-1))
    forest.fit(x.iloc[train], y[train])
    snr_median = float(np.nanmedian(x.iloc[train].koi_model_snr))
    def snr(ix):
        return x.iloc[ix].koi_model_snr.fillna(snr_median).to_numpy()
    alternatives = {
       "SNR only": (snr(valid), snr(test)),
       "Random forest": (forest.predict_proba(x.iloc[valid])[:, 1],
                         forest.predict_proba(x.iloc[test])[:, 1]),
    }
    report = {}; rows = []
    for name, (vscore, tscore) in alternatives.items():
        selected = cutoff(vscore, y[valid])
        vpred = vscore >= selected
        tpred = tscore >= selected
        report[name] = {"threshold": selected,
                        "validation": metrics(y[valid], vpred),
                        "test": metrics(y[test], tpred)}
        rows.append({"method": name, **report[name]["test"]})
        if name == "Random forest":
            cm = confusion_matrix(y[test], tpred, labels=[0,1])
            fig, ax = plt.subplots(figsize=(5,4))
            ax.imshow(cm, cmap="Blues")
            ax.set_xticks([0,1], ["Screen out","Review"])
            ax.set_yticks([0,1], ["NASA false positive","NASA candidate"])
            for (i,j), count in np.ndenumerate(cm):
                ax.text(j,i,str(count),ha="center",va="center")
            ax.set_title("Holdout-star confusion matrix")
            fig.tight_layout(); fig.savefig(out/"confusion_matrix.png",dpi=170); plt.close(fig)
    table = pd.DataFrame(rows)
    table.to_csv(out/"comparison.csv",index=False)
    fig, ax = plt.subplots(figsize=(7,3))
    ax.barh(table.method, 100*table.fraction_flagged)
    ax.set_xlim(0,100)
    ax.set_xlabel("Test signals flagged (%)")
    ax.set_title("SNR threshold versus random-forest screening")
    fig.tight_layout(); fig.savefig(out/"screening_comparison.png",dpi=170); plt.close(fig)
    payload = {"dataset": TABLE, "n_rows": len(df),
               "n_train": len(train), "n_validation": len(valid), "n_test": len(test),
               "label_caveat": "Historical Robovetter classification; not confirmed planets",
               "features": FEATURES, "results": report}
    (out/"metrics.json").write_text(json.dumps(payload,indent=2))
    return payload

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv",default="data/kepler_dr25.csv")
    parser.add_argument("--download",action="store_true")
    parser.add_argument("--output",default="results/ml")
    a = parser.parse_args()
    try:
        result = experiment(load_data(a.csv,a.download),a.output)
        print(json.dumps(result,indent=2))
    except Exception as exc:
        print("NASA test not completed:",str(exc))
        print("Manual CSV link:",nasa_url())
        raise
