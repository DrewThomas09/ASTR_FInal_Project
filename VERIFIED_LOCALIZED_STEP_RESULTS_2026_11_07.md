# Frozen 6-star localized-discontinuity experiment: verified findings
**Date:** November 7, 2026. **Result:** limited conditional gain on a synthetic-defect stress test, with **no demonstrated benefit from masking on unmodified Kepler observations**.

- [Successful NASA / unit-test workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42402819710)
- [Original unmodified 10-file Actions artifact](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42402819710/artifacts/13585948128), including all per-case CSV, plots, thresholds, original FITS SHA-256, science limitations and run log.
- [Frozen pre-run manifest](LOCALIZED_STEP_STUDY_FROZEN_2026_11_07.json), [physics/methodology protocol](PART_II_LOCALIZED_DEFECT_EXPERIMENT.md), [detector](localized_discontinuity.py), [experiment script](localized_step_ablation.py), [browser-based notebook](Kepler_Localized_Step_Study_Colab.ipynb).
- Verification: GitHub Actions completed successfully and ran **74 passing regression tests** on the same code revision as the astronomy study.

## Question and independent design

Does masking fixed windows around *data-driven, persistent downward brightness discontinuities* rescue injected artificial planet transits when compared with standard BLS and the previous near-gap mask, without unreasonable loss of planet signal or an increase in false triggers on calibration-type proxies?

The original source manifest was committed **before this cohort was observed**. Two calibration stars were Kepler-11 (KIC 6541920) and Kepler-22 (KIC 10593626); six untouched-for-this-method held-out stars were Kepler-36 (11401755), Kepler-37 (8478994), Kepler-62 (9002278), Kepler-78 (8435766), Kepler-100 (6521045), and Kepler-145 (8494142). All used official NASA MAST Quarter 8, DR25 PDCSAP long-cadence FITS with quality filtering and the same 301-cadence median detrending. **All eight original source FITS files were available.** Each file's original SHA-256 appears in `all_star_sources.csv`.

The test injected known 400, 1,000, and 2,200 ppm box transits into real stellar photometry before detrending, with two independent trials per depth/condition per star. Thus each method handled **36 matched planet injections without an added artifact and 36 matched planet injections with a known artificial step**, total 72 independent random injections but **only six independent held-out stellar sources**. The 216 rows in the per-method CSV represent repeated comparisons on those 72 identical injections, not 216 independent planets.

The artificial step was a 0.6–1.2% immediate brightness decrease with partial exponential recovery to a persistent offset, designed to resemble one broad instrumental failure mechanism. The result is contingent on that simplified simulation, **not** measurements of natural PDC-corrected SPSDs or real telescope hardware.

## Independent method-specific control calibration

Each method was assigned a detection threshold from 32 independently seeded **constructed proxy null realizations on the same two calibration stars**. Controls were inverted and rolled observed light curves, with or without an artificial step. They are not known planet-free stars. They do **not** measure NASA mission false alarm probability (FAP).

| Method | Frozen BLS score threshold |
|---|---:|
| Unmodified BLS | 89.21260 |
| Original near-gap BLS | 89.23510 |
| Localized-step-mask BLS | 79.37290 |

A lower threshold is not itself a success. Because it differs between methods, a difference in recovery must be decomposed into **preprocessing** versus **threshold** effects, which is done below.

## Held-out correct-period-and-threshold recovery

| Input condition | Known injected depth | n | Standard BLS | Previous near-gap mask | New localized step mask |
|---|---|---:|---:|---:|---:|
| Unmodified Kepler PDCSAP | 400 ppm | 12 | 3 | 2 | 3 |
| Unmodified Kepler PDCSAP | 1,000 ppm | 12 | 6 | 6 | 7 |
| Unmodified Kepler PDCSAP | 2,200 ppm | 12 | 12 | 12 | 12 |
| **Natural-data total** | — | **36** | **21** | **20** | **22** |
| Real PDCSAP + known synthetic step | 400 ppm | 12 | 0 | 0 | 0 |
| Real PDCSAP + known synthetic step | 1,000 ppm | 12 | 7 | 7 | 8 |
| Real PDCSAP + known synthetic step | 2,200 ppm | 12 | 11 | 10 | 11 |
| **Synthetic-defect total** | — | **36** | **18** | **17** | **19** |

Criterion: BLS score strictly above the method's frozen calibration threshold **and** fitted period within 2% of the known artificially injected period. The known period was supplied **only to scoring, after fitting**; unlike Robnik et al., this metric does not require an independent transit-phase match.

### Critical ablation of the apparent improvements

1. **No defect added:** the localized-step rule detected **0 persistent steps in 36 injection light curves** and masked **0 measurements**. The BLS period and score were **exactly identical to ordinary BLS in all 36 cases**. The one extra recovery (22 vs 21) arose **solely because its method-specific threshold is lower**: in KIC 8494142 with a 1,000-ppm injection, identical BLS peak score **80.21458** passed the localized method's 79.37290 cutoff but failed the baseline's 89.21260 cutoff. Thus this group demonstrates **NO actual light-curve preprocessing advantage**.
2. **Artificial step added:** the localized detector marked an onset in **21/36** injected-source cases, matching the known synthetic step within the frozen 0.22-day matching tolerance in all 21 triggered cases. It masked **393 total cadences across 36 evaluated source-injection time series** and removed **eight genuine artificial transit cadences**. These are repeated time-series measurements, not 393 different physical Kepler samples. The baseline BLS score/period differed from localized BLS in exactly those **21/36** cases.
3. **One verifiable case of physical recovery:** the artificial-step condition's only discordant recovered injection occurred on KIC 8494142 at 1,000 ppm. Standard BLS selected an **incorrect period** at score **117.08440**. The localized mask selected the **correct injected period** at score **103.21693**, above BOTH methods' thresholds. Therefore that one recovered signal was genuinely caused by changing the photometry, not merely by choosing a more permissive detection cutoff. The other 35 artificial-step cases showed no difference in final correct-period recovery classification.
4. **Threshold-versus-mask distinction:** applying the **baseline numerical score threshold of 89.21260** to the local-step outputs as a diagnostic (not a full matched-FAP test) yields **21/36** recoveries on natural flux and **19/36** on synthetic-step flux. This confirms the natural-data one-case difference is purely a threshold artifact, whereas the artificial-step one-case gain survives that numerical threshold substitution. The score distributions differ, so this post-hoc substitution **is not itself a valid same-FAP comparison**.

**Interim judgment:** the method can fix one specifically constructed step-induced wrong-period detection but does not demonstrably improve general exoplanet recovery. It also removes real injected planetary samples, which creates an additional risk of missed signals.

## Proxy-null false-trigger analysis

The same two method-specific calibration thresholds were frozen before evaluation on 24 **held-out constructed proxy null realizations** per condition and method (four per each of six stars).

| Held-out proxy-null condition | n | Standard BLS flagged | Near-gap flagged | Local-step flagged |
|---|---:|---:|---:|---:|
| No artificial step | 24 | 4 | 4 | 4 |
| With artificial step | 24 | 13 | 13 | **10** |

Among the synthetic-step proxies, the local-step method reduced flagged cases by **3/24**, while retaining the same count on clean proxies. All three flag differences favor the local mask and there are no local-only flags, but the sample is far too small and star-correlated for a strong statistical claim.

**This is NOT comparable to 10% true FAP.** The held-out synthetic-step proxy flag fraction remained **10/24 = 41.7%**, versus **13/24 = 54.2%** for standard BLS. Both are much higher than the intended 10% calibration-tail target, illustrating that different real stellar systems, artificial instrumental defects and unreliable proxy null construction can defeat calibration generalization.

As an exploratory decomposition, applying the baseline's numerical threshold to the localized score gives the **same 10/24 flagged step proxies**, consistent with at least part of the reduction coming from actual changes to selected-period scores. Nevertheless, that is not calibrated astrophysical reliability.

## Scientific limitations and what we learned

- These are known artificial transits injected into **actual** public Kepler photometry; they are NOT new planet discoveries. Kepler-36, Kepler-37, etc. were deliberately chosen as identified hosts and can contain genuine transits already, so they are not clean physical nulls.
- The artificial defect's waveform matches the persistence heuristic by design. The 21/36 correct onset matches demonstrate response to a specific constructed discontinuity, **not** sensitivity to authentic residual SPSDs.
- The algorithm masked the neighborhood of each step without performing a full astrophysical classification. A physically genuine long eclipse or unusual stellar brightness drop could be removed.
- The natural-data result offers no preprocessing gain because no persistent step was found.
- The artificial-step signal rescue count is only **1/36**, giving no meaningful evidence of broad superiority across astronomy targets.
- Calibration from two stars and 32 proxy draws per method is insufficient to stabilize true mission false-alarm rates. Its held-out proxy fractions were not matched to the calibration target. A robust comparison with the 2026 Robnik paper requires the same data population, injected period regime, noise controls and selection denominator.
- Each depth/condition contains only 12 events spread across 6 real stellar hosts. Cases within a host share stellar noise; naive standard errors would overstate precision.
- We cannot declare that the new simple mask exceeds published ARC2, Kepler PDC, or Robnik's physical-vetting pipeline. It addresses only one crude model of a localized instrumental nuisance, and PDC has already corrected many actual SPSDs.

## What to do next without p-hacking

1. **Stop tuning on these six held-out stars.** The present results are a complete, finished frozen exploratory evaluation; preserving it (including the negative natural-data finding) makes the report stronger.
2. **Compare established physical alternatives more directly:** PDC-corrected PDCSAP vs uncorrected SAP, or a published localized-defect routine, using separately chosen untouched sources and **source-grounded real defect flags** rather than only invented steps. The Kepler instrument guide includes known cosmic-ray/SPSD case studies.
3. **Strengthen null calibration** with source-specific distribution validation and enough independent target stars to estimate threshold stability. Study the impact of correlated samples and negative-control labels.
4. **Improve transit preservation** if developing a new method: the step detector deleted eight real injected transit samples. Any future correction/mask policy must report missed planets, not just instrumental artifacts flagged.
5. **Paper comparison:** our small 2.1–9.8-day/quarter, source-conditioned proxy-null experiment is a scientific demonstration of concepts from [Robnik et al. (2026)](https://doi.org/10.1093/mnras/stag419) and [Aigrain et al. (2017)](https://doi.org/10.1093/mnras/stx1422), not a numerical reproduction of their whole-survey results.

## Reproducibility and AI disclosure

This document was prepared from verified saved CSV/JSON, event-level inspection, and successful GitHub Actions logs. GPT-6 authored the research code, test suite, scientific protocol, initial analysis and explanatory text with AI assistance. The student must independently inspect raw outputs and physical assumptions before making academic claims and disclose AI use under course requirements. The frozen manifest and original measurements remain available through the workflow's archived data; retention should extend through the December 11 final-submission deadline.
