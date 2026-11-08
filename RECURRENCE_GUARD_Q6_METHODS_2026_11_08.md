# Prospective Q6 test of a repetition-aware safeguard for stellar eclipses
**ASTR 12600 — November 8, 2026 | Protocol frozen before first evaluation.**

## Scientific motivation

Our November 7–8 experiments established three facts, not a new exoplanet discovery:

1. The unchanged local downward-step screen recognized a **known published instrument discontinuity** in raw Kepler SAP but not in corrected PDCSAP, on one preselected educational target.
2. In the initial six-star artificial-defect study it occasionally rescued a wrong BLS orbital period but also erased **eight genuine injected transit cadences** in one case. On ordinary corrected observations, there was **no demonstrated preprocessing benefit**.
3. A separate Q6 observational screen had zero independently archived SPSD-positive events, so it could not evaluate sensitivity. Many warnings clustered on **Kepler-47**, an eclipsing binary. Five of seven distinct warning times occurred within 2.4 hours of predicted *stellar* eclipses, and original NASA flux showed recurring eclipses in both SAP and PDCSAP.

We hypothesize that before deleting observations around a negative-step warning, a method should check whether **short-lived brightness dips repeat** at a common orbital period, as happens for real eclipses. The goal is preserving observational evidence, *not* proving planet identity or improving raw transit detection automatically.

## Freeze and new sources

[Pre-evaluation frozen manifest](RECURRENCE_GUARD_Q6_FROZEN_2026_11_08.json) was committed *before* running this group's Q6 observations. It records **eight published eclipsing binaries** (Kepler-16, -34, -35, -64, -413, -453, -1647, -1661) and **five transiting-planet hosts** (Kepler-1, -2, -3, -5 and -6). Source IDs, labels, references, all trial periods, recurrence thresholds, file policy and post-hoc metrics were frozen.

**The key scientific separation:** the binary or planet source class, published orbital period, and archival quality flag are *never passed into the recurrence detector*. They are used only after processing for descriptive comparison. Previously analyzed Kepler-47, Kepler-38 and the published KIC 7461601 instrument-positive example are excluded. All inaccessible Q6 source files remain in the original denominator; no source substitutions.

## Method implemented

On each official NASA MAST Q6 FITS, read TIME, original SAP_FLUX, corrected PDCSAP_FLUX and the source-file SHA-256. Keep matched, positive, finite observations, including archived nonzero-quality cadences because they may contain actual instrumental jumps. Detrend SAP and PDCSAP **separately** using the original 301-cadence median normalization; the two products retain **exactly the same timestamps**.

For each photometry product:

1. Run the *unchanged November 7* `localized_downward_step_mask` rule on flux and time only; retain every original warning epoch and the original destructive mask.
2. Around each warning, compare the 20th-percentile brightness in a short event window (−0.10 to +0.16 days) with the **lower** of two nearby background levels (−0.54 to −0.27, +0.29 to +0.56 days). Reject incomplete or gapped windows; require at least four samples per window and no local gap over 0.16 days.
3. Require a short-event depth exceeding **both 0.25% and four times the light curve's robust scatter estimate**.
4. Scan trial periods **2.5–22 days at 0.02-day intervals**. A candidate is *protected* if at least three *other*, separately sampled cycles also show a self-contained dip above the same depth threshold, with at least 75% support among all independently observable trial cycles. Trial period and phase are derived solely from the flux, without a reference to published orbital parameters.
5. If and only if the warning receives periodic protection, **do not mask its ±0.22-day neighborhood**. Otherwise retain the original local-step mask, unchanged. Protection is a temporary observational safeguard, not a binary/planet probability.

The most important distinction is between **persistent instrumental level changes** and **recovering, periodic eclipse shapes**. A permanent drop can create one large derivative, but its brightness does not return to a higher baseline around future repeats. This geometric requirement should reduce inappropriate repeated-event protection, though it cannot guarantee it.

## Limits and independent questions

The period search itself tries hundreds of possibilities: matching repeated dips may occur by chance in complex correlated stellar noise. There is **no true FAP calibration**, no training of a supervised AI model and no planet confirmation. This is a minimal, physics-inspired, AI-assisted coding and evaluation task.

Several deliberately retained binaries have published periods of 27–41 days, longer than the 22-day guard search. A single 90-day quarter often does not contain enough complete repeat eclipses, so **failure on these targets is expected from the fixed design**, not evidence that the system has no true eclipses. A short-period host may also have few or no original local-step warnings, leaving no opportunities to test veto effectiveness.

The Kepler SAP_QUALITY bit 1024 is an official instrument-discontinuity flag but is not an exhaustive label of all systematic errors. Unmatched warnings are never called proved false positives. If any bit-1024 events appear in this independent cohort, separately report how many the original mask identified and whether the new recurrence safeguard would wrongly protect them. If there are zero instrument positives again, **instrument preservation/sensitivity remain unestimated**.

The group is purposively selected, not a probability sample of mission targets; within-star cadences and warnings are correlated. Do not pool the percentages with previous synthetic-injection results as though they share populations or compare them numerically against Robnik et al. (2026), whose actual method, injected periods and noise controls differ.

## Reproducibility

- [Frozen input manifest](RECURRENCE_GUARD_Q6_FROZEN_2026_11_08.json)
- [Complete fixed algorithm, NASA FITS reader and measurement reporting](recurrence_guard_q6.py)
- [Offline engineering tests](tests/test_recurrence_guard_q6.py)
- [Workflow, source SHA tracking and original event artifacts](.github/workflows/recurrence-guard-q6.yml)

The script outputs every planned KIC, returned original FITS checksum, actual instrument quality-bit count, original and protected warnings in **both SAP and PDCSAP**, and the retained/deleted observation counts. Its independent test results are not reported until GitHub Actions completes and the original CSVs have been inspected.

## Independent references

- Kepler Eclipsing Binary Catalog: https://archive.stsci.edu/kepler/eclipsing_binaries.html
- Kepler-413 discovery, binary period 10.116 d: https://doi.org/10.1088/0004-637X/784/1/14
- Kepler binary-host table: https://academic.oup.com/mnras/article/488/3/3482/5497941
- NASA Kepler data characteristics handbook, quality flags and SPSD correction: https://stdatu.stsci.edu/kepler/manuals/Data_Characteristics.pdf
- Kepler-47 original post-hoc case: [real source and eclipse plots](KEPLER47_ORIGINAL_FLUX_VISUAL_CHECK_2026_11_08.md)

**AI use:** GPT-6 assisted protocol design, code, tests, methods documentation and interpretation. The student must personally understand, review and disclose this assistance and independently check all astrophysical assumptions before submitting graded work.
