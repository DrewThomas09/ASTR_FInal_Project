# Paired audit of November 7 frozen Kepler experiment

**Scope:** descriptive analysis of archived outcomes. This does not add new observations, rerun BLS, or retune the detector. No exoplanet discovery is claimed.

## Paired recovery (same injection, two methods)

### no_added_defect
Standard BLS recovered **21/36**; local step mask **22/36**. Exact paired disagreements: 0 baseline-only and 1 step-only; conditional exact two-sided binomial p = **1**. Each group comprises only 6 independent stellar hosts. This p-value ignores within-star dependence and cannot establish survey performance.
Observed recovery difference: **+2.78 percentage points**; block bootstrap sensitivity range (host resampling, descriptive only) **[+0.00, +8.33] pp**. Its boundaries are not proof of a real population effect with just six chosen stars.
At the standard BLS **numerical** threshold: 21 baseline and 21 step recoveries. This is NOT equal false-alarm-rate calibration. The step mask removed 0 true transit cadences in 0 injected cases.

### synthetic_spsd_like_step
Standard BLS recovered **18/36**; local step mask **19/36**. Exact paired disagreements: 0 baseline-only and 1 step-only; conditional exact two-sided binomial p = **1**. Each group comprises only 6 independent stellar hosts. This p-value ignores within-star dependence and cannot establish survey performance.
Observed recovery difference: **+2.78 percentage points**; block bootstrap sensitivity range (host resampling, descriptive only) **[+0.00, +8.33] pp**. Its boundaries are not proof of a real population effect with just six chosen stars.
At the standard BLS **numerical** threshold: 18 baseline and 19 step recoveries. This is NOT equal false-alarm-rate calibration. The step mask removed 8 true transit cadences in 1 injected cases.

## Constructed proxy-null false triggers

- **no_added_defect**: standard 4/24 flagged, step 4/24; paired baseline-only 0, step-only 0; exact conditional p = 1. These inverted/rolled synthetic controls are not a measured mission false-alarm rate.
- **synthetic_spsd_like_step**: standard 13/24 flagged, step 10/24; paired baseline-only 3, step-only 0; exact conditional p = 0.25. These inverted/rolled synthetic controls are not a measured mission false-alarm rate.

## Interpretation

The correct conclusion remains that extra local preprocessing has **not** shown a benefit on unmodified PDC-corrected Kepler measurements. On artificially constructed discontinuities the local mask rescued one specific wrong-period case, but it also deleted genuine transit samples. The chosen sample, proxy controls, heterogeneous stellar noise and shared calibration scores are too weak to establish broad performance gains.

**Statistical caveat:** The exact paired test is informative about discordant case counts, but because trials share stars, it is not a fully independent astronomical hypothesis test. The host resampling is shown to reveal sensitivity to selection, not as a population-wide confidence interval.

**Provenance:** Re-run with the unmodified `all_paired_injection_trials.csv`, `heldout_proxy_nulls.csv`, and `frozen_method_thresholds.json` from the original Actions run 42402819710 (artifact 13585948128). Software drafted with generative AI; all observational findings must be reviewed independently by the student.