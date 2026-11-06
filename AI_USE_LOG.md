# AI contribution and verification log

## 2026-11-04 | Initial detector design (AI-assisted)

**Task specified by researcher:** test whether generative AI can write a transit-search program and whether the program recovers known orbital periods. **AI work:** generated `exoplanet_detector.py` and synthetic injection test, with Astropy Box Least Squares as primary algorithm and a NumPy phase-folded fallback. AI generated plotting, CSV handling, and code-level explanations. **External method:** BLS originates from Kovacs, Zucker & Mazeh (2002); Astropy software is not an AI invention. **Verification:** synthetic known-period and noise-only runs. **Limitation:** the fallback search statistic does not provide a calibrated probability that a planet exists.

## 2026-11-04 to 2026-11-05 | Sensitivity and repeatability study (AI-assisted)

**AI work:** drafted repeatable simulation and detection-depth sensitivity code and report scaffolding. **Student responsibilities:** examine plotted light curves, distinguish noise from transit signals, and explain the result without claiming real-planet accuracy. **Data:** simulations, not NASA observations.

## 2026-11-06 | New candidate-screening improvement (AI-assisted)

**Task specified by researcher:** reproduce established exoplanet detection and add a modest, testable ML false-positive filter rather than only copying a standard detector. **AI work:** generated `ml_screening.py`, a random-forest comparison with an SNR-only screening rule, grouped train/validation/test splits, data validation, summary statistics, confusion matrix, and unit tests. Prepared README, Colab notebook, and research plan.

**Data intended:** NASA Exoplanet Archive Kepler Q1-Q17 DR25 KOI table (`q1_q17_dr25_koi`). **Four model inputs:** period, duration, depth, and fitted transit signal-to-noise. **Target:** NASA's historical `koi_pdisposition` Robovetter decisions. **Not used as predictors:** `koi_score`, false-positive flags, disposition labels, and identifiers.

**Tests performed:** 9 offline tests passed locally using synthetic catalog data. **Not yet performed:** actual NASA API download, real-data model training, evaluation on held-out NASA stars, and raw Kepler-69 recovery. **No claim:** no new planet found, no validated improvements or labor-hour savings, and no inference that the synthetic test statistics transfer to real data.

## What AI will and will not decide

AI is permitted to assist with: code scaffolding, explanation, debugging suggestions, charts, test writing, and documentation. Established algorithms, peer-reviewed papers, and NASA datasets provide the scientific method and evidence. The researcher must independently verify input provenance, review sample outputs, decide whether the experiment answers its question, and write/own the final scientific interpretation. Keep all additional AI conversations, code revisions, and fixes in this log before submission.

## Source papers (read and cite the originals)

- Kovacs, Zucker & Mazeh (2002), *A box-fitting algorithm in the search for periodic transits*. https://doi.org/10.1051/0004-6361:20020802
- McCauliff et al. (2015), *Automatic Classification of Kepler Planetary Transit Candidates*. https://doi.org/10.1088/0004-637X/806/1/6
- Thompson et al. (2018), *Planetary Candidates Observed by Kepler. VIII*. https://doi.org/10.3847/1538-4365/aab4f9
- Shallue & Vanderburg (2018), *Identifying Exoplanets with Deep Learning*. https://doi.org/10.3847/1538-3881/aa9e09
- Astropy BoxLeastSquares API: https://docs.astropy.org/en/stable/timeseries/bls.html
- NASA Kepler DR25: https://exoplanetarchive.ipac.caltech.edu/docs/Kepler_KOI_docs.html