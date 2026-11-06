"""Offline tests; do not mistake synthetic tests for real Kepler performance."""
import numpy as np
import pandas as pd
import ml_screening
import exoplanet_detector

def synthetic_catalog(n=190):
    rng=np.random.default_rng(44)
    records=[]
    for i in range(n):
        for j in range(2 if i%9==0 else 1):
            candidate=int(rng.random()>.5)
            records.append(dict(kepid=100000+i,kepoi_name=f"KTEST.{i:05d}{j}",
                koi_pdisposition="CANDIDATE" if candidate else "FALSE POSITIVE",
                koi_period=float(rng.uniform(1,100)),koi_duration=float(rng.uniform(1,12)),
                koi_depth=float(rng.uniform(50,5000)),koi_model_snr=float(rng.uniform(3,30)),
                koi_score=candidate))
    return pd.DataFrame(records)

def test_same_star_does_not_cross_splits():
    df=synthetic_catalog()
    a,b,c=ml_screening.split_by_star(df.assign(label=(df.koi_pdisposition=="CANDIDATE").astype(int)))
    stars=[set(df.iloc[idx].kepid) for idx in [a,b,c]]
    assert not stars[0]&stars[1] and not stars[1]&stars[2] and not stars[0]&stars[2]

def test_recall_threshold():
    threshold=ml_screening.cutoff([0.2,0.3,0.6,0.9],[1,1,1,1],0.75)
    assert sum(s>=threshold for s in [0.2,0.3,0.6,0.9])>=3

def test_full_screening_pipeline(tmp_path):
    data=synthetic_catalog()
    data["label"]=(data.koi_pdisposition=="CANDIDATE").astype(int)
    out=ml_screening.experiment(data,tmp_path)
    assert "Random forest" in out["results"]
    assert (tmp_path/"comparison.csv").is_file()
    assert (tmp_path/"confusion_matrix.png").is_file()
    assert out["results"]["Random forest"]["validation"]["recall"]>=0.90

def test_simulator_reproducibility():
    t,a=exoplanet_detector.simulate_light_curve(seed=21)
    u,b=exoplanet_detector.simulate_light_curve(seed=21)
    assert np.array_equal(t,u) and np.array_equal(a,b)

def test_simulator_transit_reduces_flux():
    _,a=exoplanet_detector.simulate_light_curve(seed=21,planet=True)
    _,b=exoplanet_detector.simulate_light_curve(seed=21,planet=False)
    assert float(a.mean())<float(b.mean())
