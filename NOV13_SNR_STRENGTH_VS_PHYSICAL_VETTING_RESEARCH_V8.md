# Original Kepler research: why signal strength is not planetary identity
ASTR/PHSC 12600 | November 13, 2026

## Original NASA observations and methods
The November 5 proposal asked whether AI could help reproduce and evaluate methods for identifying exoplanets. This analysis returns to the frozen, star-separated Kepler DR25 screening experiment rather than training or tuning a new model. The input was the original 1,619 held-out Kepler Object of Interest records from 1,385 distinct host stars.

Source: https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42513638366/artifacts/13630680897
Original heldout predictions CSV SHA256: 3682e0be30506ddcfe4bbb0c683ed6884454c5e5fbf8d946922fb48248712663
Underlying NASA DR25 catalog source SHA256: c907e064c7369d4b073ba422283ddfbbf7499d472ec3cc0787254f3407e5e045

## Original-data results
The primary holdout included 851 historical NASA CANDIDATE labels and 768 historical FALSE POSITIVE labels. Eleven records had missing model signal-to-noise ratio, excluded only from the following SNR-binned analysis.

| Catalog transit SNR | Signals | Historical candidates | Historical false positives | Candidate-label share | Median depth |
|---|---:|---:|---:|---:|---:|
| Under 10 | 154 | 80 | 74 | 51.95% | 129.6 ppm |
| 10 to under 30 | 702 | 464 | 238 | 66.10% | 211.0 ppm |
| 30 to under 100 | 361 | 227 | 134 | 62.88% | 556.1 ppm |
| 100 or above | 391 | 79 | 312 | 20.20% | 31,525.9 ppm |

The share historically labeled as candidates was **45.89 percentage points lower** at SNR 100+ than at SNR 10-30. Using 2,000 whole-star bootstrap resamples (all KOIs from each sampled host retained), the approximate 95% interval for the moderate-minus-high share was **[40.50, 51.22] percentage points**.

Many strong transit-like signals are extremely deep. A stellar binary eclipse can produce a high signal-to-noise event while not being a planetary transit. The original Kepler-35 stellar-binary measurements are a separate physical example of this distinction. We do not claim that every historically false-positive-labeled signal is a binary or that an SNR bin estimates planet occurrence in the sky.

## Model scores and scientific interpretation
On the same frozen 1,619-signal holdout, the random forest's Brier error against the historical NASA vetting labels was **0.13117**, compared with **0.18248** for the four-feature logistic regression. The logistic-minus-forest difference was **+0.05132**, with 95% whole-star bootstrap interval **[+0.04085, +0.06143]**.

Brier error here is the mean squared deviation between a saved model score and an earlier screening label. These scores are not probabilities of physically confirmed exoplanets. This audit uses previously inspected test records, so the source-backed intervals are conditional descriptive checks, not a new independent observational validation.

The source figures in the Word/PDF paper show 1,608 original NASA catalog SNR/depth records and a second score-to-label comparison in Appendix B. The script kepler_v8_snr_vetting_audit.py reproduces the reported counts and uncertainty from the unchanged original prediction table.

## Connections to astronomy and class
Lesson 2: measured relative flux and bright blended eclipses. Lesson 3: repeated timing and transit-event detectability. Lessons 5-6: orbital period, binaries and half-period aliases under Kepler's laws. Lab 1 and Appendix B: precision, accuracy and uncertainty. The four-feature forest screens NASA's already extracted transit summaries rather than analyzing the raw light curves from the separate BLS detector; the combined project therefore does not establish end-to-end exoplanet discovery accuracy.

Research sources: Kovacs, Zucker and Mazeh (2002), DOI 10.1051/0004-6361:20020802; McCauliff et al. (2015), DOI 10.1088/0004-637X/806/1/6; Thompson et al. (2018), DOI 10.3847/1538-4365/aab4f9; Batalha et al. (2010), DOI 10.1088/2041-8205/713/2/L103; NASA Kepler KOI source definitions https://exoplanetarchive.ipac.caltech.edu/docs/API_kepcandidate_columns.html.