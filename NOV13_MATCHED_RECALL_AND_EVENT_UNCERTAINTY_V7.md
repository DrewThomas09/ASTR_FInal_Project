# Matched-recall Kepler model audit and quarter-level uncertainty
ASTR/PHSC 12600 | November 13, 2026

## A fairer model comparison
The previously frozen NASA DR25 holdout includes 1,619 KOI signals from 1,385 distinct host stars, including 851 historical CANDIDATE and 768 FALSE POSITIVE labels. The original validation-selected model thresholds did not have identical test recall. To compare the same score-retrieval objective, this study interpolates the **retrospective ROC false-positive rate at exactly 90% historical candidate-label recall**, using the same previously saved scores. There is no classifier retraining.

| Model ranking | Historical FP acceptance at 90% candidate-label recall | 95% host-bootstrap interval | AUROC |
|---|---:|---:|---:|
| Random forest | **28.39%** | 24.27%-33.47% | 0.8857 |
| Four-feature logistic | **36.72%** | 32.86%-41.27% | 0.7803 |
| SNR-only rule | **89.39%** | 86.86%-92.26% | 0.3466 |

Bootstrap: **2,000 draws of whole host stars**, preserving all KOIs from each sampled star, seed 20261113. The paired forest-minus-logistic FPR difference is **-8.33 percentage points** with 95% host-bootstrap interval **[-13.17,-3.12] points**. The 90% point uses the test labels, so this is **not** a new deployable threshold or untouched model validation. These are NASA's *historical vetting labels*, not physical planet confirmations.

## Real Quarter 6 and Quarter 7 event-level stability
Previously archived original Kepler photometry measurements were reanalyzed using **10,000 bootstrap resamples of individual event depths per quarter**.

| Known system | Quarter 6 median depth, 95% event-bootstrap CI | Quarter 7 median depth, CI |
|---|---|---|
| Kepler-12, known planet host | 20 events, **1.5506%** [1.5379%, 1.5563%] | 18 events, **1.5660%** [1.5336%, 1.5850%] |
| Kepler-35, eclipsing binary | 7 events, **19.1658%** [18.6100%, 22.6356%] | 8 events, **21.1102%** [19.0628%, 22.5352%] |

Periods fitted **independently** in Q6 and Q7 differed by **36.52 seconds** for Kepler-12 and **87.57 seconds** for Kepler-35. Q6 fitted timing compared with **reoptimized** Q7 event centers gave median absolute offsets of **10.24 minutes** and **75.02 minutes**. This is a retrospective agreement check, **not** a prospectively frozen Q6-only forecast of untouched Q7 flux. Intervals are conditional on the particular selected stars and events.

## Sources and reproducibility
- [Original DR25 heldout model predictions](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42513638366/artifacts/13630680897)
- [NASA Kepler Q6/Q7 observed event tables](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519123518/artifacts/13633010940)
- [Q6 original folded-flux arrays](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42515740272/artifacts/13631128224)
- Reproduction code, frozen source archives, a three-panel Figure 9, and the numerical output JSON are packaged in the updated v7 research ZIP alongside the formatted Word/PDF manuscript.

## What it does and does not establish
The forest separates *historical NASA vetter labels* more selectively than logistic or SNR at the same retrospectively imposed candidate recovery in this sample. The separately fitted quarters demonstrate repeatable observed dimming in both a known planet host and a stellar binary. The custom BLS detector still does **not** feed its measurements directly into the random forest, so the analysis does not establish end-to-end discovery accuracy.

**MEST connections:** Lesson 2 (relative measured flux), Lesson 3 (timing), Lessons 5-6 (Kepler's laws), Lab 1 and Appendix B (precision, accuracy and measurement uncertainty).