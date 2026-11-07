# Real Kepler preprocessing ablation — first completed external run (negative result)
**Date:** 7 November 2026. **Source:** NASA Kepler Q2/Q8 PDCSAP FITS. **Status:** verified from completed GitHub Actions logs and saved artifact.

- [Successful full regression + astronomy workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42400548553), run on commit `019756894ab96ca37dc7dbfc7e19f9e8b15c03e9`.
- [Download the nine original CSV, JSON, plot and log outputs](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42400548553/artifacts/13584998475).
- [Frozen manifest from before the first experimental run](PREPROCESSING_ABLATION_FROZEN.json); [detailed methods](PREPROCESSING_ABLATION_METHODS.md).
- [Implementation](preprocessing_ablation.py), [raw FITS and injection helper](kepler_preprocessing.py), [unit tests](tests/test_kepler_preprocessing.py). GitHub Actions reported **64 unit tests passed**.

## Exact research question

Does the prespecified mask of 0.2 days on either side of Kepler observing gaps longer than 0.5 days improve ordinary Astropy Box Least Squares detection of shallow **artificial** transits injected into **genuine** Kepler stellar photometry? Tests use thresholds chosen separately by each method on calibration controls.

**Important distinction:** This is a simplistic **near-gap mask**, not Robnik et al.'s (2026) data-driven localized artifact model, Fourier noise treatment, matched-filter Bayes factor or validated long-period survey pipeline. The control curves are inverted and rolled observed flux; they are *proxy nulls* and cannot establish Kepler survey FAP.

## Original frozen design and accountability

The source and algorithms were locked before evaluation. Synthetic box transits were inserted multiplicatively into unflattened pipeline PDCSAP flux **before** both methods received the same 301-cadence median normalization. Both used the same BLS search range (1.5–12 days), three transit durations, and a 2%-of-injected-period scoring rule. Each method received its own calibrated score cutoff from the same type of proxy nulls. No historical period/injection truth was passed to BLS.

| Predeclared split | Star | Quarter | Data points passing quality filter | Large gaps | Points removed by gap mask | Outcome |
|---|---|---:|---:|---:|---:|---|
| Calibration | KIC 2436365 | 2 | 3,662 | 4 | 77 | Analyzed |
| Calibration | KIC 8462852 | 8 | 2,660 | 1 | 17 | Analyzed |
| **Held-out** | **KIC 11904151** | 8 | — | — | — | **Not processed: official public FITS endpoints returned HTTP 404** |
| **Held-out** | **KIC 11026764** | 8 | **2,535** | 1 | **15** | **Analyzed** |

Original source SHA-256 values for the three downloaded FITS files appear in `source_accountability.csv`. The failed source remains in the intended denominator; we did **not** replace it after looking at outcomes.

**Fatal limitation of statistical breadth:** despite the four-star study plan, only **one independent held-out star** was actually analyzed. All 12 injection cases and 10 proxy nulls on this star share the same stellar noise realization, so they are **not 12 independent astrophysical stars**.

## Calibration and results

**Separate proxy thresholds, fixed on calibration stars only:**
- Ordinary BLS: threshold **278.047626**, 20 calibration proxy controls from two calibration stars.
- Gap-masked BLS: threshold **280.734694**, 20 calibration proxy controls from the same calibration stars.
- A higher threshold is *not* intrinsically better or worse because the score distribution changes under processing. No true false-alarm probability was calibrated.

**Held-out artificial planet recovery:** a detection must exceed its method-specific threshold AND recover the injection's known period within 2%.

| Artificial transit depth | Test count | Standard BLS recovered | Gap-masked BLS recovered | Signal retention under gap mask |
|---|---:|---:|---:|---|
| 400 ppm | 4 | **0/4** | **0/4** | mean ~98.49% of injection-induced differential flux preserved; 2 injected cadences removed |
| 1,000 ppm | 4 | **0/4** | **0/4** | 100% of injection-induced differential flux preserved |
| 2,200 ppm | 4 | **2/4** | **2/4** | 100% preserved |
| **Overall** | **12** | **2/12** | **2/12** | One real target, three depth strata |

Paired cross-method outcomes: **2 recovered by both**, **10 by neither**, **0 standard-only**, **0 gap-mask-only**. No held-out injection was rescued by near-gap masking. The available data therefore do not support a performance improvement.

The approximate descriptive Wilson 95% intervals show uncertainty: for 0/4 recovered the interval is **[0%, 49.0%]**; for 2/4 it is **[15.0%, 85.0%]**. With shared stellar noise and intentionally small samples, they do not provide representative population inference.

**Held-out constructed proxy nulls:** each method flagged **0/10**. Their 0/10 descriptive upper Wilson 95% bound is ~**27.8%**. These controls were made from inverted, randomly rolled real flux and are *not guaranteed* to reproduce physical Kepler instrumental false alarms. Do **not** describe either number as mission FAP=0.

## Why this negative result is scientifically informative

1. The mask affected only **15/2,535 = 0.592%** of quality-filtered test cadences. On this one test star, a rule that changes so few points may have little ability to change the BLS periodogram or the decision.
2. It demonstrably removed **two genuine injected transit cadences** in the shallowest group. Smoother/cleaner light curves are not automatically better for planet detection. Here this caused no change in the number of threshold-passing correct-period recoveries, but the loss remains relevant.
3. **Detection of 400- and 1,000-ppm injections remained difficult** under the high proxy-calibrated thresholds: 0/4 at each depth in both methods. This is a potential failure of the small-quarter, star-specific regime and unrepresentative proxy-null calibration, not proof that such planets are intrinsically undetectable by Kepler.
4. The proposed real-data sample was weakened by **a missing fixed-quarter source file**, illustrating an important reproducibility/data-availability limitation. We must specify quarter selection and availability *before* future evaluation instead of silently swapping stars.
5. The hypothesis that **targeted detection of actual instrumental discontinuities** can help is still open. The published Robnik et al. pipeline identifies localized defects from data and then vets individual transits. Our near-gap mask is not equivalent and did not address a demonstrated defect in the test star.

## Comparison with published research — no apples-to-apples numerical claim

**Kovács, Zucker & Mazeh (2002):** original box fitting; our Astropy implementation uses the established method and is compared to itself with just one extra mask. Period aliases and look-elsewhere effects persist.

**Hatzes (2020):** stellar measurements, uneven sampling and aliases matter; the source motivates auditing timestamps and noise models. This book is primarily on Doppler radial velocities, not a statistical standard for our flux data.

**Oshagh; Barros and Faria (2018):** stellar activity and preprocessing can alter transit signal amplitude; physical transit fitting and independent RV data provide additional information beyond BLS score. We haven't implemented physical fits here.

**Thompson et al. (2018):** reliability and completeness must be measured using representative injection/null populations. We use a small exploratory flux-level proxy instead.

**Robnik et al. (2026):** 5,000-star, long-period 200–500-day experiment, extensive localized-defect removal and matched false-alarm-rate recovery. **Our one usable held-out Q8 star with 2.1–9.8-day injected periods and proxy nulls is NOT a replication**, and our 2/12 correct-period recovery cannot be numerically compared to their recovery percentages.

**Gilbert (2022):** supplied excerpt emphasizes stellar activity and the importance of modeling flares; only the first 24 PDF pages are available for our review, not her full technical thesis chapters.

## What we should improve next (requires NEW unseen test data)

1. **Data availability protocol:** select quarters based on catalog evidence *before running outcomes*, record all excluded targets, and use at least several independently held-out stars. The present cohort must not be silently expanded and recounted as untouched validation.
2. **A stronger physically justified artifact treatment:** compare a local step/change-point model or nuisance-template veto, while protecting genuine transit windows. Use the same strict paired-injection metric and count transits lost.
3. **Proxy calibration validation:** obtain more representative nulls and actual known-star controls; differentiate instrumental artifact FAP from astrophysical eclipsing binaries and catalog classification.
4. **More powerful injection study:** vary period, depth/SNR, number of observed events, correlated-noise level and distance to gaps; show paired sample counts, source hashes and uncertainty with independent stars.
5. **Retain negative results and scope:** existing binary-vetting cohort missed all six real binaries; this gap-mask pilot also shows no advantage. Both belong in the final Reflection section.

## Research integrity

These code files, unit tests, literature interpretations and this methods/results narrative were produced with generative AI assistance. The student's responsibility is to independently check the source files, quantitative results, astrophysical assumptions, course policy and final write-up. This experiment demonstrates **no new exoplanet discovery and no externally established improvement over the published survey pipeline**.
