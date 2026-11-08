# Verified Kepler-47 binary-eclipse alignment: exploratory follow-up
**November 8, 2026 | POST-HOC observational diagnosis, not prespecified planet detection.**

[Successful original-source GitHub Actions run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42511250474) · [machine-readable results, event table, and diagnostic figure](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42511250474/artifacts/13629303214) · [analysis source](kepler47_eclipse_warning_check.py) · [offline regression tests](tests/test_kepler47_eclipse_warning_check.py).

The most recent complete workflow checked the SHA-256 of the *original* warning CSV from the fixed Quarter 6 instrumental-defect experiment (run `42510882421`), executed **104 passing tests**, and used the Kepler-47 eclipsing-binary timing information published in **Orosz et al. (2019)**. This follow-up applies **no refitted astronomical detection method, no new mask threshold, and no new candidate claim**.

## Why this target was studied

In the frozen twelve-target observational cohort, **ten** official Kepler Q6 light curves were usable and **none** carried the archived SPSD bit-1024 event marker. Although the experiment could not evaluate actual SPSD recognition sensitivity, the unchanged detector generated 13 method-level warning rows: one on Kepler-9 and **twelve on Kepler-47** (five SAP warnings and seven PDCSAP warnings). The five SAP warning timestamps exactly overlapped five of the seven PDCSAP warning timestamps, leaving **seven unique warning epochs**.

Crucially, Kepler-47 is an **astrophysical eclipsing binary**. An obvious potential physical error is interpreting genuine, periodically recurring stellar eclipses as isolated brightness discontinuities. This possibility was identified **after examining the new outputs**, so everything below is *exploratory*, not independent validation.

## Independently published orbital timing model

Orosz et al. (2019), *Discovery of a Third Transiting Planet in the Kepler-47 Circumbinary System*, **Astronomical Journal 157, 174**, DOI [10.3847/1538-3881/ab0ca0](https://doi.org/10.3847/1538-3881/ab0ca0), reports corrected binary-star eclipse ephemerides:

| Stellar eclipse | Period (days) | Reference eclipse epoch (BJD) |
|---|---:|---:|
| Primary | 7.44837568 | 2454963.246137 |
| Secondary | 7.44837596 | 2454959.427964 |

The Kepler mission time column uses **BKJD = BJD - 2454833.0**. For every original detector-warning time, we calculated the closest predicted primary or secondary eclipse using the published ephemeris. The original seven time stamps were read only from the archived experiment CSV; the source file's SHA-256 was required to match `1be4b1c9e28f31ad506cfed191c7818a9aa8d1627a269a87d89de3c6bc0a0b99`.

## Actual warning-by-warning comparison

| Kepler warning (BKJD) | Closest published eclipse | Offset (hours) | SAP and PDCSAP warning? |
|---|---|---:|---|
| 550.933616 | Secondary | -1.24 | Both |
| 558.392054 | Secondary | -1.00 | PDCSAP only |
| 588.184631 | Secondary | -1.02 | Both |
| 595.438572 | Secondary | -5.69 | Both |
| 612.602668 | Primary | -42.91 | Both |
| 614.380369 | Primary | -0.24 | PDCSAP only |
| 621.818087 | Primary | -0.50 | Both |

Thus **5/7 unique warning epochs were within 0.1 days (2.4 hours)** of the closest predicted binary eclipse and **6/7 within 0.3 days (7.2 hours)**. The more distant warning at BKJD 612.602668 is *not* explained by a near-center binary-eclipse match under either exploratory window. We cannot infer all warnings are eclipse-related.

These offsets are comparisons to **stellar** eclipses in the binary orbit, not the ~49.5-, ~187-, or ~303-day circumbinary *planet* transit periods. The stellar eclipses repeat far more frequently, so a generic negative-step classifier can fail to separate periodic stellar variability from one-off instrument changes.

## Conditional phase-shift sensitivity (added post-hoc)

To see whether the observed clustering near predicted eclipses is a fragile coincidence under a simple reference construction, we moved **all seven observed warning epochs together** through 20,000 equally spaced offsets covering one 7.44837568-day binary orbit. We preserved the original time intervals and warning clustering. For each shifted sequence we evaluated the count within each fixed exploratory matching window; no detector was re-run and no warning was deleted.

| Window (closest predicted primary/secondary) | Observed close epochs | Joint shifts meeting/exceeding observed | Fraction |
|---|---:|---:|---:|
| ±0.1 day | 5 of 7 | 425/20,000 | **0.02125** |
| ±0.3 day | 6 of 7 | 1498/20,000 | **0.0749** |

**These fractions are NOT confirmatory p-values.** The Kepler-47 target and the 0.1/0.3-day windows were considered after identifying an unusually warning-rich object in the 12-star cohort. The exercise is conditional on that selection and ignores uncertainty in the physical relationship between the eclipse center and the maximum local derivative on the light curve. It merely illustrates that the entire repeated warning sequence is fairly closely aligned with this system's orbital eclipse timing under one reasonable post-hoc reference.

Importantly, the phase shift preserves the dependence of the warnings within one star and avoids treating the seven epochs or the five cross-product repeats as independent physical sources. It is still **not** a mission-wide false-positive estimate, a population inference, or evidence that our algorithm can reliably classify eclipsing binaries.

## Conclusions, follow-up and implications for the final report

**Supported:** five of seven warning times lie within 2.4 hours of published Kepler-47 binary eclipse centers. Most warnings in this star also occur in *both* raw SAP and corrected PDCSAP, consistent with — but not proving — a real repeating astrophysical signal that PDC should not necessarily remove. The fixed detector had **zero** archived SPSD bit-1024 labels to match anywhere in this separate cohort.

**Plausible, NOT proven:** the local discontinuity mask may be accidentally labeling some real binary eclipses as instrument defects. This could cause real astronomy signal removal, echoing our earlier eight deleted injected transit samples in the artificial-step test.

**Necessary future independent test:** freeze a new sample of both publicly classified eclipsing binaries and source-labeled authentic instrument discontinuities before running a *new* periodic-event / local-defect separation rule. Evaluate sensitivity to documented defects and false deletion of genuine stellar eclipses on **new** stars. Do not keep changing thresholds on Kepler-47 or combine its post-hoc evidence with prospective holdout performance.

**Academic disclosure:** GPT-6 assisted with code, audit, statistics, writing and source comparison. The student should inspect original observational files and ephemerides, validate the interpretations, and disclose generative-AI contributions under the ASTR 12600 rubric.
