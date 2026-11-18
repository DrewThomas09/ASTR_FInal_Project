# November 18 research extension: period recovery versus transit forecasting

**Status:** New deterministic calculation and external literature check. **Not** a new analysis of held-out flux or a modification of the Version 16 paper/November 20 status report.

## New quantitative research check

The original Kepler-69 b Q8 Box Least Squares search fitted a period of **13.7133429855 days** (see [Version 16 research process](NOV15_RESEARCH_PROCESS_NARRATIVE_V16.md)). NASA's Q1-Q17 DR25 catalog reference is **13.7223682 days**; NASA lists a transit duration of **5.1231 +/- 0.0357 hours** and a transit depth of **571.1 +/- 6.5 ppm** ([NASA Kepler-69](https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-69)).

The fitted-minus-reference period error of **0.065770%** corresponds to **12.99631 minutes per orbit**. If both periods are held fixed and their epochs coincide initially, the model predictions separate by

`abs(predicted_midtime_Q8 - predicted_midtime_DR25) = N * abs(P_Q8 - P_DR25)`.

At 6, 12, 18 and 24 orbits, the differences are **77.978, 155.956, 233.934, and 311.911 minutes**, respectively. The last is approximately the complete published transit duration, after **329.3 days**. See [reproducible calculation](nov18_kepler69b_ephemeris_drift.py).

**Crucial limitation:** This is *not* a measured future-transit error or an uncertainty interval. It is a deterministic sensitivity calculation under equal starting epochs and two constant periods. The original BLS fitted epoch is required before attempting an actual forecast; transit-timing variations and observational uncertainties can change outcomes.

## Next test: unretuned, held-out Q9 transit timing

Preselect Kepler-69 b and verify that original Q9 PDC-SAP observations exist and are usable. Fix the Q8 fitted period, epoch and duration before examining Q9. For every Q8-predicted Q9 window, record data coverage, local depth and timing residual, with quality-flag exclusions. Compare to 1,000 fixed within-star phase-offset controls for contextual evidence, and include all unavailable/negative windows in the denominator. Report the independent-quarter **event-forecast result separately from period error**, and do not substitute a more favorable target/quarter after seeing outcomes. A preselected known eclipsing-binary control can demonstrate why reliable repeated dips still do not confirm planets. This is a proposed protocol, **not** a run we claim to have completed.

## Three literature cross-checks

1. **DR25 labels do not establish planetary identity.** [NASA's DR25 KOI description](https://exoplanetarchive.ipac.caltech.edu/docs/PurposeOfKOITable.html) warns that uniform vetting can classify a few confirmed planets as false positives and vice versa. [Lissauer et al. 2024, PSJ 5, 152](https://doi.org/10.3847/PSJ/ad0e6e) reexamines Kepler candidates and their periods. Thus our **81.6%** figure is historical **catalog-label agreement**, not independently validated planet classification.
2. **Iterative planet search was established Kepler practice.** [Twicken et al. 2016, AJ 152, 158](https://www.ipac.caltech.edu/publication/2016AJ....152..158T) explains how Kepler fits/removes discovered events and searches remaining data for more signals. Our second-pass Kepler-20 b recovery is an AI-assisted reproduction/development case, not a newly invented method.
3. **Pointing corrections already exist.** The [Kepler Archive Manual, section 2.3.1.1](https://archive.stsci.edu/kepler/manuals/KDMC-10008-003-Archive_Manual.pdf) describes PDC correcting instrumental drifts while retaining astrophysical signals. Our Q8 uses NASA-processed **PDCSAP_FLUX**. Lower TESS centroid motion in 44/56 stars does not prove correct localization of the eclipsing object; NASA [difference-imaging/centroid validation](https://ntrs.nasa.gov/citations/20190029148) addresses the distinct physical source question.

**Implication for the final:** Keep the completed three-part Kepler/classifier/TESS story intact. If the independent Q9 experiment is actually executed and verified, a compact new finding could contrast *period agreement* with *ability to forecast later dips*. Do not insert an untested result into the report.
