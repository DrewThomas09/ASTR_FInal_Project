# Real Kepler quarters and external-sample uncertainty

**ASTR/PHSC 12600 | November 13, 2026 | Source-backed extension to the submitted Kepler proposal**

## Scope
This note adds a physical comparison of **two already characterized Kepler systems** using the original preserved NASA Quarter 6 and Quarter 7 photometry results. Those quarters were **fitted independently**, so this is a **retrospective repeatability and event-shape comparison**, not a blind Quarter 6-based prediction of future Quarter 7 dips.

The full predeclared [Q6-to-Q7 forecasting protocol](Q6_TO_Q7_BLIND_PREDICTIVE_VALIDATION_FROZEN_2026_11_08.json) and [implementation](q6_to_q7_blind_ephemeris_validation.py) remain separate. A completed, source-verified 12-star forecast output was not available in this research audit, so no forecast success rate has been assigned.

## What the original records show

The following numbers were recalculated from these two already completed workflow artifacts:
- [NASA-derived 2026 Q6/Q7 individual event-morphology tables](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519123518/artifacts/13633010940)
- [Original Q6 binned event shapes and missing-bin masks](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42515740272/artifacts/13631128224)

| Observed system | Q6 fitted period | Q7 fitted period | Difference between fits | Q6 events / median depth | Q7 events / median depth |
|---|---:|---:|---:|---:|---:|
| Kepler-12, previously known planet host | 4.4383042534 d | 4.4378815777 d | **36.52 seconds** | 20 / 1.551% | 18 / 1.566% |
| Kepler-35, known eclipsing stellar binary | 10.3712603922 d | 10.3702468682 d | **87.57 seconds** | 7 / 19.166% | 8 / 21.110% |

**Why it matters:** both systems produced readily repeated dips, yet Kepler-35's fitted period of about 10.37 days is a near half-period alias of its roughly 20.734-day published **stellar binary** orbit. An apparently precise, repeatable BLS result does not tell us whether a planet or a stellar eclipse caused the dimming.

The quarter-to-quarter differences above reflect two independently optimized fits, with different observations and sampling. **They are not formal period confidence intervals**, not estimates of survey completeness, and not a time-holdout forecast. The original Q6 odd/even folded morphology is much more asymmetric for the stellar binary; small event sample sizes and broad within-star event resampling intervals prevent claiming that parity alone was validated as a binary detector.

## The frozen external-cohort results deserve a wider uncertainty discussion

The separately preselected [13-object Kepler Q8 cohort](FROZEN_REAL_13STAR_VALIDATION_RESULTS.md) included six published planet-host targets, seven published eclipsing-binary targets, and one binary whose planned Q8 data were unavailable. Among the **six analyzed planet hosts**, BLS recovered the intended known planet period in **3/6**; among the **six analyzed binaries**, **4/6** produced a half-period alias and **0/6** tripped the simple binary warning.

Under an illustrative independent binomial model, Wilson 95% intervals would be approximately **18.8%-81.2%** for 3/6, **30.0%-90.3%** for 4/6, and **0%-39.0%** for 0/6. **These are not survey-wide population confidence intervals** because the objects were selected purposively. They merely show how little six observations can determine even under favorable sampling assumptions.

## A necessary methodological distinction

The research paper contains two **parallel** Kepler demonstrations:
1. Box Least Squares fitted raw Kepler light curves for selected stars, including failed and aliased cases.
2. A small forest screened NASA's **pre-computed DR25 KOI catalog features** (period, duration, transit depth, and pipeline model SNR) against the historical `koi_pdisposition` labels.

The forest was **not trained on features extracted by our BLS program**, so the reported 81.6% historical-label accuracy is not an end-to-end performance measurement for our custom transit detector. Kepler DR25 labels are pre-existing vetting decisions, not independently confirmed physical exoplanets. This distinction makes the inference more precise.

## Literature and class connections

[Kovács, Zucker & Mazeh (2002)](https://doi.org/10.1051/0004-6361:20020802) explains periodic box searches; [Batalha et al. (2010)](https://doi.org/10.1088/2041-8205/713/2/L103) explains binary and blend vetting; [Thompson et al. (2018)](https://doi.org/10.3847/1538-4365/aab4f9) explains DR25 catalog completeness, reliability, and historical labels. Course Lesson 2 concerns observed flux, Lesson 3 repeat timing, Lessons 5-6 Kepler's law and orbital periods, and the first lab and Appendix B address measurement uncertainty and precision versus accuracy.

**Paper inclusion:** The expanded Word/PDF manuscript incorporates this new four-panel archived-data graphic as **Figure 6**, plus links to the original runs as **Reference [17]**. The figure is newly prepared from authentic saved measurements; the underlying Quarter 6 and Quarter 7 analyses were completed previously.
