# AI-assisted exoplanet research | ASTR 12600

**Research question:** Can an AI coding assistant reproduce an established transit-search technique, and can a simple machine-learning vetting step reduce false positives compared with a single-feature rule?

This project **does not claim to discover or confirm an exoplanet**. It combines two scientific tasks:

1. **Transit signal search:** use the established Box Least Squares method (Astropy when installed) to find repeating brightness dips in simulated star measurements and, optionally, in public Kepler-69 observations.
2. **Machine-learning candidate screening:** train a four-feature random forest on NASA Kepler DR25 KOI metadata to predict historical `CANDIDATE` vs `FALSE POSITIVE` *Robovetter* labels, then compare it with an SNR-only threshold at a similar validation-set recall target.

The ML module is an **incremental screening experiment**, not a new astronomical discovery method. The core result may be positive, negative, or inconclusive.

## Simplest workflow (Google Colab, no local installation)

Open `Kepler_AI_Project_Colab.ipynb` in [Google Colab](https://colab.research.google.com/), then choose **Runtime > Run all**. The simulation runs without NASA access. The ML section attempts to download the Kepler DR25 data once; if NASA is unavailable it prints the exact CSV URL for browser download and upload. The notebook does not invent results when the download fails.

The known Kepler-69 light-curve example is optional, because MAST downloads can occasionally fail or require longer processing.

## Running on a computer

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests
python exoplanet_detector.py --mode synthetic --force-numpy --output results/synthetic
python sensitivity_study.py --output results/sensitivity --trials 12
python ml_screening.py --download --output results/ml
```

If NASA is temporarily unavailable, open the exact URL printed by `python ml_screening.py --download` in a browser, save the file as `data/kepler_dr25.csv`, then run:

```bash
python ml_screening.py --csv data/kepler_dr25.csv --output results/ml
```

Optional raw Kepler light curve:

```bash
python exoplanet_detector.py --mode kepler --output results/kepler69
```

## What each file does

- `exoplanet_detector.py` - raw light-curve transit search and figures, plus synthetic injection.
- `sensitivity_study.py` - controlled study of detection versus transit depth at fixed simulated noise.
- `validation_study.py` - additional synthetic signal and noise controls.
- `ml_screening.py` - NASA DR25 download, leakage-safe model training, comparison, graphs, and CSV/JSON results.
- `Kepler_AI_Project_Colab.ipynb` - all steps in one browser-friendly notebook.
- `tests/` - unit and offline workflow tests, which **use synthetic catalog rows**.
- `AI_USE_LOG.md` - transparent log of AI-authored software and what human verification remains.
- `RESEARCH_PLAN.md` - study design, relevant published papers, caveats, and deadlines.

## Scientific precautions

- Historical Robovetter labels are *not* independent ground truth; this experiment measures agreement with them.
- `koi_score`, `koi_fpflag_*`, disposition decisions, and IDs **are not model predictors**.
- Data are split by Kepler host-star ID (`kepid`) to prevent same-star leakage across train/validation/test.
- Model decision thresholds are chosen only from the validation group; held-out test results remain independent.
- "Fraction flagged" is a screening workload proxy, **not astronomer-hours saved**.
- The Box Least Squares peak alone is not a calibrated false-alarm probability.
- All results must identify whether they came from simulated or real NASA data.

## Status (2026-11-06)

- Implemented and locally tested: transit simulation, BLS-inspired backup, sensitivity study, random forest, group splits, evaluation and plots.
- 9 offline tests passed when running `python -m pytest -q tests`.
- NASA/MAST real-data retrieval and real classifier performance **not verified** in this environment; run the notebook in an internet-connected environment and report the observed values.

Coursework: AI-generated code and other assistance must be disclosed under the instructor's academic integrity rules. The student remains responsible for understanding the code and interpreting the scientific results.