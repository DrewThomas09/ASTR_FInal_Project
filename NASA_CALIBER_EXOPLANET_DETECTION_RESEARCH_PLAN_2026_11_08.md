# A NASA-Caliber Upgrade Path: Physically Validated, Event-Safe Exoplanet Transit Detection
**ASTR/PHSC 12600 | Research-design revision | November 8, 2026**
**Status: research proposal + ongoing real Q6 → Q7 holdout experiment. This is NOT a NASA-approved study or a claim that our pipeline beats NASA.**

## Executive decision: change our scientific question

**Earlier question:** Can AI reproduce NASA's prior Robovetter candidate/false-positive labels?

**Proposed research question:** *Can a physically interpretable, non-destructive treatment of ambiguous photometric drops improve the recovery of real planetary transits in original Kepler/TESS brightness time series, without increasing the rate of instrumental/astrophysical false alarms?*

The earlier four-feature random forest's retrospective **81.29% balanced agreement** with prior NASA DR25 labels is statistically strong relative to weaker comparison models, but NASA's much more sophisticated [ExoMiner++](https://github.com/nasa/ExoMiner) already analyzes multi-view original light-curve and pixel-level diagnostics at a more advanced scale. The NASA [January 22, 2026 article](https://science.nasa.gov/open-science/deep-learning-exoplanets-tess/) says new models are being developed toward detecting signals, not only scoring given candidate events. A four-column KOI-label model cannot credibly be called a novel NASA-level discovery system.

The harder problem that our *actual raw telescope data* revealed is **destructive preprocessing**: the local anomaly detector can mistake stellar-eclipse ingress for an instrumental jump. In two previously untested binary hosts (Kepler-35 and Kepler-1647) a fixed periodicity safeguard protected 42 genuine original light-curve samples near predicted known eclipses, but it missed several genuine longer-period binary eclipses (Kepler-34). Importantly, preserving **stellar eclipses**, not planets, proves only that the original mask can destroy valid astrophysical information. It gives a physical failure mode to investigate, NOT demonstrated improvement in planet discovery.

## Three increasingly valuable, falsifiable hypotheses

### H1 — Cross-quarter predictive evidence (now implemented, exploratory pilot)

Fit a blind orbital period, time of first transit and duration from **Kepler Quarter 6 only**. Before opening Quarter 7, freeze the period and phase and ask whether a dip appears when and where the Q6 model predicts it in the later time series. We have committed [the prospective source and threshold manifest](Q6_TO_Q7_BLIND_PREDICTIVE_VALIDATION_FROZEN_2026_11_08.json), [code](q6_to_q7_blind_ephemeris_validation.py), [tests](tests/test_q6_to_q7_blind_ephemeris_validation.py), and [an official archived-data workflow](.github/workflows/kepler-q6-to-q7-blind-prediction.yml) selecting **ten separate previously published planet hosts**, plus **two explicitly previously studied eclipsing binaries** (negative controls for *planet identification*, not for periodicity).

- **No Q7 period/epoch optimization.** Q7 is a genuine future-data *time holdout*. FITS source hashes, missing data, all predicted events and per-source outcome are archived.
- A local Q7 event-depth statistic measures dimming at *fixed predicted times*, compared with 1,000 fixed-seed alternate orbital phase offsets as a descriptive internal null. At least two valid future predicted windows and 60% positive local depths required.
- **The phase-shift fraction is not a NASA-calibrated false alarm probability**: phases in one star are dependent, true binaries can pass, and published planet hosts may have different astrophysical signals. Count **stars**, not phase-shift trials, as the independent sample.
- Q6 single-quarter period error can drift by many transit durations before Q7, so failure is not proof of a spurious planet. Transit-timing variations (TTVs) likewise violate constant-period forecasts. Test these failure cases without adjusting the frozen pilot parameters.
- The separately studied binary controls must demonstrate that future-quarter coherence **does not establish planetary identity**. The question is whether candidate ephemerides predict real repeatable signals, not whether a source is confirmed a planet.

**Scientific novelty limits:** Predicting transit events in later photometry is not a novel invention; this is a low-budget, unusually explicit time-holdout experiment that makes our scientific inference more credible.

### H2 — Reversible artifact management rather than deleting photometric data (priority discovery algorithm)

The proposed actionable method is **event-aware, reversible downweighting**. Do not unconditionally remove data around a likely sudden sensitivity dropout. For each individual event, estimate two competing explanations:

1. **Instrument-change hypothesis:** persistent offset after an abrupt drop, quality-bit 1024 (if known), discontinuity across boundaries, pixel-level/instrument flags, quarter-specific behavior.
2. **Astrophysical-transit hypothesis:** localized recovery of baseline flux, repeated projected orbital phase, compatible transit duration and ingress/egress, consistent depth across individual transits or an allowance for justified TTV.

If evidence is ambiguous, preserve the original sample and report uncertainty; do **not** force a planet or instrument label. Test a continuum of fixed **robust weights** or a two-model likelihood approach against three clear baselines:

- Unmasked BLS/TLS (no data deletion).
- Existing original local-step destructive mask.
- Existing simple period-recurrence-protection guard.

**Primary endpoint:** fraction of injected *planetary events* recovered at a predeclared fixed false-alarm or vetting-alert budget; this is not the number of observational cadences preserved. **Safety endpoint:** fraction of independently archived genuine SPSD events that remain unprotected and correctly downweighted, plus the number of genuine injected transits accidentally suppressed. We require measured both; an algorithm that never masks anything cannot be called superior merely because it preserves more astrophysical samples.

**Specific hard case:** Kepler-34 showed three recurrent eclipse-like epochs at ~27.79 days, but the frozen 22-day rule protected none. A period-blind model of **local recovery shape** (short eclipse versus persistent step) could address that particular design weakness. However, Kepler-34 is already development-exposed and cannot be the untouched validation target for a tuned next version.

### H3 — More genuine weak planets at matched false alarm rate (NASA-grade full benchmark)

Move beyond 0.9–20-day, single-quarter demonstrations. Conduct a **blinded injection/recovery** study using *real original Kepler or TESS observing noise* and physically meaningful, limb-darkened planetary transit models. Include both realistic weak transits and challenging controls: stellar eclipses at half-period aliases, transit timing variability, single-cadence cosmic-ray-like outliers, SPSD-like partial recovery, pointing/thermal trends, and multiple-planet overlaps.

Compare:
- Standard box least squares **BLS**.
- [Transit Least Squares](https://doi.org/10.1051/0004-6361/201834672) **TLS**, which uses limb darkening and ingress/egress and may be a stronger baseline for small planets.
- The existing destructive mask, existing recurrence safeguard and our new **reversible event-aware** proposal.
- Where data and compute permit, publish a comparison against [NASA's DR25 Robovetter](https://github.com/nasa/kepler-robovetter), official reference TCE/injection products, and the well-specified [Robnik et al. (2026)](https://doi.org/10.1093/mnras/stag419) paper. Robnik et al. already address localized defects and individual-transit vetting, so we must **not** imply this area is unexplored.

**All methods get the exact same selected stars, sampled flux, injection truths, search period range, candidate budget, calibration stars, star-disjoint test stars and original quality flags.** The injected truth is **never passed to the detection code**. Use the full detection problem, not just preselected KOIs with historical NASA vetter labels.

**Primary performance curve:** fraction of injected true planets recovered **vs. empirical false-alarm rate**, evaluated at a predeclared alert budget on **independent host stars**. At minimum report points for separate injected depth ranges (100–500, 500–1500, >1500 ppm), period bins and transit count; separate original observations from planet injections and simulated instrumental defects. Important: a simple star without a known planet does **not** prove there are zero real planets, and time-inverted/shifted light curves are at best *imperfect proxy nulls* unless the original reference protocol explicitly establishes their use.

**Statistical design:** preregister one primary contrast, e.g. **planet recovery fraction at ≤1% calibrated false alerts per independent source** versus BLS/TLS on the *same heldout targets*. Predeclared paired host-level permutation, exact discordance where appropriate, and star-block bootstrap 95% interval; keep all negative trials. Allow a two-sided alpha=0.05 only when calibration and holdout are actually independent and event truth is externally controlled. A nominal p-value on previously explored Robovetter labels is **not equivalent**.

**Initial scale for development versus NASA-style validation:** Begin with 20–50 new stars to validate acquisition and code, then target several hundred to thousands of distinct star-quarter observations and a preregistered number of recoverable injected signals after measuring pilot event discordance. The 2026 Robnik et al. study used ~5,000 randomly selected Kepler stars and injected periods **200–500 days**, very different from our short, selected-star pilot. Do not advertise performance comparability unless both experiments truly use matched data and injections.

## What NASA scientists would need before using results

A NASA-useful deliverable is not primarily a leaderboard or a neural network. It should be a **reusable scientific decision aid** that accepts public photometry and outputs:

1. **Exactly reproducible FITS provenance** (MAST original filename, data release, observation quarter, SHA-256, processing code and complete environment).
2. **Detections in actual observed flux**, not only classifiers of NASA's previous classifications. Ephemeris, BLS/TLS scores, predicted future transit windows, and measured event depths.
3. **Physics-based rejection or abstention diagnostics:** odd/even depth inconsistency, secondary stellar eclipse, phase-fold shapes, TTV/alias uncertainty, original quality-bit anomaly indicators and risk of removing true flux.
4. **Off-target contamination test using target pixel files:** compare in-transit and out-of-transit difference images/centroids to locate the signal relative to the target star. NASA DR25 documents pixel offsets as a key route to identifying background binaries; original SAP/PDCSAP scalar flux alone cannot resolve them.
5. **Independent validation** on novel stars, later observing quarters and explicitly measured injection ground truth, with confidence intervals, false alarms and recall as a function of signal depth and period.
6. **A transparent ranked follow-up queue**, with expected ephemeris and uncertainty, audit of all failures and specific reasons for planetary/stellar/instrument suspicion. A flagged target is a *candidate*, never automatically a confirmed exoplanet.

## Suggested title and claim hierarchy

**More credible project title:**
**“When Instrument Correction Erases Real Transits: A Physics-Guided, Predictively Validated Kepler Search.”**

**What our project presently demonstrates (as of the new cross-quarter study being evaluated):**
- Correct reproduction of known exoplanet periods using established BLS on selected NASA flux; strongest historical KOI-label RF agreement above simple baselines with retrospective statistical significance.
- Strong, original astrophysical *failure-mode evidence*: a local instrumental-step detector can flag genuine stellar eclipses, and a narrow recurrence guard can preserve real eclipse cadences in two previously untested binary systems.
- Meaningful negatives: the guard misses eclipses beyond its fixed search range; simple period-aware threshold calibration worsened historical classification balanced accuracy; previous frozen external binary vetting failed.
- **The Q6→Q7 prospective photometric forecast is an experiment, not an established success until the actual run and its failures are inspected.**

**What is NOT demonstrated:** discovery of a previously unreported planet, increased mission-wide planet completeness, superiority to NASA's full Robovetter or ExoMiner++, corrected pixel-level false positives, or valid population-level superiority of our event-safe guard.

**A high-impact future conclusion if H2/H3 were genuinely verified:** *“On N previously unseen stars and X realistic injected planetary signals, the event-aware model increased recovery from A% to B% at the same calibrated false-alarm budget, a paired host-star difference of Δ percentage points (95% CI [...], p=...), while retaining sensitivity to independently archived instrumental defects and surviving cross-quarter prediction tests.”*

We cannot fill those numbers until a fully matched, untouched injection/false-alarm experiment runs.

## References to treat as actual methodological competitors

- NASA ExoMiner++ (2026), [NASA Science report](https://science.nasa.gov/open-science/deep-learning-exoplanets-tess/) and [released modeling/pipeline code](https://github.com/nasa/ExoMiner).
- NASA Kepler [public data products, DR25 pixel-level transit injections, scrambled/inverted controls and completeness/reliability materials](https://exoplanetarchive.ipac.caltech.edu/docs/Kepler_Data_Products_Overview.html).
- NASA [Kepler DR25 Robovetter released source](https://github.com/nasa/kepler-robovetter) and [pixel-based KOI vetting definitions](https://exoplanetarchive.ipac.caltech.edu/docs/API_kepcandidate_columns.html).
- Hippke and Heller (2019), [TLS search](https://doi.org/10.1051/0004-6361/201834672).
- Robnik, Seljak, Jenkins and Bryson (2026), [at-the-detection-limit Kepler transit search, event vetting and systematics modeling](https://doi.org/10.1093/mnras/stag419).
- The [genuine out-of-quarter predictor manifest](Q6_TO_Q7_BLIND_PREDICTIVE_VALIDATION_FROZEN_2026_11_08.json) and [actual script](q6_to_q7_blind_ephemeris_validation.py) are the immediate reproducible application.

**Academic and AI disclosure:** GPT-6 assisted the literature research, experimental design, code, unit tests, evaluation framework and this written proposal. The student must read the source papers, independently interpret all figures and statistical conclusions, check NASA data citations, and disclose AI assistance under their course rules.
