# November 12, 2026: Does stabilizing TESS pointing proxies also suppress in-event centroid shifts?

**Status:** Source-verified exploratory *follow-up* to the original 56-star TESS pointing-correction analysis. It is NOT a new planet classifier, a new discovery, a blind test, or an independent localization-accuracy measurement.

## Physical question and original source

We previously established that subtracting the TESS SPOC spacecraft pointing estimate `POS_CORR1/2` from measured `MOM_CENTR1/2` commonly lowers a **local pre/post-event displacement proxy**. An immediate concern is whether the subtraction also decreases the **in-event vs flanking centroid displacement**, which might sometimes contain a real off-target astrophysical eclipse signature. Both are measured detector-pixel norms, not physically verified sky-position errors.

This analysis consumes the 248 exactly paired original observed source-event windows from 56 genuinely observed TESS SPOC two-minute stellar light curves previously produced by the [frozen source run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43291965755). It does not refit or rerun the NASA ExoMiner++ neural network, change a single NASA classification score, change source cohorts, add measurements, or treat the 248 event windows as 248 independent stars.

Upstream paired-event CSV SHA256: `afbf01056b9000f8370fdb6a86048ff8a516c06dc2b604ab872c3f5811948ffe`. The original frozen 32-star and 24-star source summary SHA256 hashes remain verified by the upstream runner, which fails on missing, mismatched, duplicated or nonfinite event data.

## Source-level results (56 independent star units)

| Direction after subtracting POS_CORR | In-event centroid shift smaller | In-event centroid shift not smaller | All stars |
|---|---:|---:|---:|
| Pre/post movement smaller (stability proxy improves) | **32** | **12** | **44** |
| Pre/post movement not smaller | **6** | **6** | **12** |
| All stars | **38** | **18** | **56** |

No exact-zero ties occurred. Here, each "smaller" observation is a difference between raw and adjusted **within-star medians of observed event windows**. Importantly, the 32 same-direction changes do **not** mean 32 real astrophysical off-target signals were erased. A smaller measured in-event shift could indicate either less instrumental noise or loss of true spatial-discrimination information; these data do not distinguish them.

Cohort details:

- Earlier 32 previously examined sources (146 observed events): pointing drift reduced in **28/32**; in-event shift reduced in **23/32**; both reduced in **21/32**.
- Additional 24 sources previously withheld from our rule development (102 observed events): pointing drift reduced in **16/24**; in-event shift reduced in **15/24**; both reduced in **11/24**. These sources are **not verified absent from NASA's own training data**.
- Under the prior three-event minimum eligibility rule, **30/40** sources showed lower pre/post drift; **28/40** showed lower in-event shift.

## Sensitivity to star aggregation and influential observations

The original main analysis took each source's median across its observed events. An alternative sensitivity that uses each star's **mean** across its observed event windows, still weighing stars once, also identified **44/56** stars with reduced pre/post movement and **12/56** with an increase. The median across star-level paired reductions changed from **0.0010352 pixels** (within-star medians) to **0.0014098 pixels** (within-star means), showing that effect **magnitude** is sensitive to aggregation even when the sign counts are stable.

A **leave-one-star-out sensitivity**, recomputing the median of star-paired differences 56 times, returned positive median reductions in **all 56** recomputations. Those medians ranged from **0.0010261** to **0.0010442** pixels. This checks that no *single* observed star drives the group median; it does **not** remove selection bias, autocorrelation within stars, instrumental confounding, or other systematic errors.

No new p-values were searched or used to promote the post-hoc joint table. The earlier star-level bootstrap interval and sign-test concern the *stability proxy*, not whether any planetary label was correctly classified.

## Interpretation

Our conclusion is narrower but stronger: an elementary instrument-pointing correction **often stabilizes the recorded moment-centroid movement proxy**, a result that is robust to dropping any one observed star. **The same correction also reduces in-event measured centroid shifts in many of those stars, creating an unresolved scientific trade-off.** Because the project has no independent source-position or binary-eclipse localization truth for these 56 targets, there is no evidence that the correction improves TESS astrophysical discrimination or NASA ExoMiner++ accuracy.

This is exactly why a physical check and a properly independent validation denominator matter. The observed decrease in noise-like motion cannot be automatically equated with a scientifically better detector.

## Executable provenance

- [Successful original-source follow-up workflow (261 tests passed)](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43294890871)
- [Original event/source tables, trade-off JSON, code logs and new plot (artifact 13977873521)](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43294890871/artifacts/13977873521)
- [New deterministic analysis script](tess_56star_pointing_tradeoff_sensitivity_nov12.py)
- [Seven new synthetic regression tests](tests/test_tess_56star_pointing_tradeoff_sensitivity.py)
- [Pinned workflow](.github/workflows/tess-56star-raw-vs-poscorr-original-events.yml)
- [Earlier complete source-level centroid methods and bootstrap report](VERIFIED_NOV12_TESS_56STAR_RAW_VS_POINTING_CORRECTED_CENTROID_ROBUSTNESS.md)

**AI assistance disclosure:** GPT-6 drafted the follow-up analysis, visualization and synthetic tests; inspected successful GitHub Actions original-source logs; interpreted the reproducible source-level output; and prepared this note. The student should review all quantitative and scientific claims, and acknowledge AI contributions in the course submission.
