# AI-assisted exoplanet detection | ASTR 12600

**Research question:** Can generative AI help reproduce established exoplanet transit-search techniques, and can a lightweight ML filter improve screening of candidate signals compared with a basic signal-strength rule?

## Start here (no software download)

1. Open [Google Colab](https://colab.research.google.com/).
2. Choose **File > Open notebook > GitHub** and enter `DrewThomas09/ASTR_FInal_Project`; select `Kepler_AI_Project_Colab.ipynb`.
3. Choose **Runtime > Run all**. The notebook installs required packages, writes the complete source files, runs the simulated experiments and attempts a NASA Kepler catalog download.
4. If NASA is unavailable, the notebook prints the exact CSV download URL and allows manual upload. **Do not report real-data performance numbers unless the CSV step succeeds.**
5. Download the resulting figures and numerical results. Keep `AI_USE_LOG.md` updated, and write your own analysis.

## What has been implemented?

- `exoplanet_detector.py`: simulate brightness observations, detect periodic dips with the published **Box Least Squares** (BLS) algorithm using Astropy, plot injected-planet and noise-only control. This is a traditional astronomy algorithm, **not machine learning**.
- `sensitivity_study.py`: a simulation comparing period recovery when the injected transit depth is 4,000, 1,500, or 500 parts per million.
- `ml_screening.py`: download NASA's Kepler DR25 Q1-Q17 KOI table, train a single random forest, compare with SNR-only screening, and output a confusion matrix and metric table.
- `validation_study.py`: run a positive-control and a noise-only example.
- `tests/test_project.py`: test grouped data splits, threshold behavior and a synthetic ML training workflow.
- `AI_USE_LOG.md`, `RESEARCH_PLAN.md`: research purpose, human responsibilities, methods and limitations.
- `Kepler_AI_Project_Colab.ipynb`: everything needed for the primary experiments in one notebook.

## What the proposed improvement means

Machine learning is used for **screening previously detected transit-like signals**, not as an original replacement for the astronomical BLS transit-search algorithm. We use four measured inputs: orbital period, transit duration, transit depth and signal-to-noise ratio. Training labels are historical NASA Robovetter decisions. We compare a random forest against SNR-only screening at a similar **validation-selected** candidate recall. Test stars are disjoint from training and validation stars.

**This does not confirm exoplanets or measure hours saved by astronomers.** A false-positive reduction on held-out historical classifications would be a measurable classroom result, not a new scientific discovery claim. A negative or inconclusive result is still scientifically worth reporting.

## Run locally (optional)

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests
python exoplanet_detector.py --output results/transits
python sensitivity_study.py --output results/sensitivity --trials 12
python ml_screening.py --download --output results/ml
```

If the automated NASA download fails, open the URL printed by the ML script, save it as `data/kepler_dr25.csv`, then run:

```bash
python ml_screening.py --csv data/kepler_dr25.csv --output results/ml
```

The downloaded CSV and outputs are excluded from Git by `.gitignore` to avoid accidentally committing data artifacts.

## Tested versus pending

**Verified offline** on November 6, 2026: a prior full local development package passed nine offline tests and produced simulated transit and classification outputs. GitHub Actions contains a separate test suite for this repository. **Pending:** run the actual DR25 download and ML training in an internet-connected Colab session, examine the metrics, and independently check the scientific interpretation. The optional Kepler-69b light-curve example is in the downloadable development package, **not currently part of this GitHub repository**.

## Scientific sources

- Kovacs, Zucker & Mazeh (2002): [Box-fitting algorithm](https://doi.org/10.1051/0004-6361:20020802)
- McCauliff et al. (2015): [Random forest classification of Kepler candidates](https://doi.org/10.1088/0004-637X/806/1/6)
- Thompson et al. (2018): [Kepler DR25 candidate catalog](https://doi.org/10.3847/1538-4365/aab4f9)
- Shallue & Vanderburg (2018): [Deep learning for exoplanets](https://doi.org/10.3847/1538-3881/aa9e09)
- [NASA Kepler candidate tables](https://exoplanetarchive.ipac.caltech.edu/docs/Kepler_KOI_docs.html)

**Academic integrity:** all AI-assisted programming and documentation must be disclosed as required by the instructor. The student is responsible for understanding the code and drawing scientific conclusions.
