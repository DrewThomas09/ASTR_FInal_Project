# Kepler-47: direct observed stellar-eclipse light-curve crosscheck
**November 8, 2026 | Complete NASA-source visualization; *post-hoc* scientific interpretation.**

- [Successful Actions workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42511647491), with **109 passing regression tests**.
- [Original-data figure, local warning windows, warning photometry CSV, source digest and log](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42511647491/artifacts/13629373540).
- [Reproducible source script](kepler47_phase_fold_diagnostic.py) · [unit tests](tests/test_kepler47_phase_fold_diagnostic.py) · [previous warning-to-eclipse timing analysis](VERIFIED_KEPLER47_ECLIPSE_CHECK_2026_11_08.md).

## Why this matters

Our fixed localized negative-step detector found seven unique warning epochs on **KIC 10020423 / Kepler-47**, a published eclipsing binary. Five lay within 2.4 hours of the 2019 Orosz et al. published stellar eclipse centers and six within 7.2 hours. But *timing alone* does not show the actual brightness behavior. This follow-up therefore opens the **unmodified official NASA Kepler Quarter 6 source FITS file**, uses the original SAP_FLUX and PDCSAP_FLUX at precisely aligned timestamps, and shows both measurements folded at the published stellar binary orbital period.

This work is **not independent validation**: we chose the binary star because the earlier frozen cohort generated warnings there. It also must not be confused with the much longer orbital periods of the circumbinary planets.

## Full photometric and source verification

- Original source: `kplr010020423-2010265121752_llc.fits` from official NASA MAST Kepler Q6.
- Actual downloaded FITS SHA-256 (must equal the prior untouched Q6 observational study): `3ab0b21547c32cce04b474ecfd210b894632552121d70d9821fbb677997d332c`.
- **4,272** jointly valid, positive, timestamp-aligned cadences; 126 non-joint-valid original rows excluded. Archived SPSD quality bit 1024 appeared in **zero** valid cadences.
- Same fixed 301-cadence median normalization used by the earlier source-analysis implementation, applied separately to the two original flux products.
- Warning times were loaded from the original archived 12-star experiment and required SHA-256 `1be4b1c9e28f31ad506cfed191c7818a9aa8d1627a269a87d89de3c6bc0a0b99`; the new plotting script does not run or tune the detector, and **cannot invent or shift warning events**.
- Published Orosz et al. (2019) primary period: **7.44837568 days**; the independently published secondary eclipse has orbital phase **0.48738179** relative to the primary, not artificially forced to exactly phase 0.5.

## What the real light curves show

**Figure 1: `kepler47_original_sap_pdc_binary_phase.png`.** Plotting all Q6 points modulo the published **stellar binary** period produces the same prominent repeating eclipse pattern in both SAP and PDC-corrected PDCSAP photometry. The deep primary eclipses cluster at phase 0/1. The shallower secondary eclipses occur near phase 0.487. Original detector warnings are marked as triangles, not optimized to fit the physical prediction. This shows a genuine recurring astrophysical brightness feature in the original spacecraft observations rather than a synthetic injection.

**Figure 2: `kepler47_first_three_warning_lightcurve_windows.png`.** The three earliest warning epochs, selected *by chronological order* without filtering by apparent fit quality, are plotted individually in a half-day window around the nearest published secondary eclipse. In all three, the original and corrected flux series undergo a localized brightness decline close to the independent eclipse prediction. The warning markers occur shortly before the published eclipse center. This supports the possibility that the detector responds to a physically real eclipse's **ingress** (the period when brightness starts dropping), as opposed to a separate instrument discontinuity.

These are **observational figures**, not a validated classifier of event physical causes. We cannot say with certainty that all five near-eclipse warnings resulted from an eclipse solely from event-time matching and these three windows. One of seven warning epochs was about 42.9 hours from any predicted primary or secondary eclipse center, and the code may also respond to other stellar activity or measurement noise.

## What this adds to the final paper

This is a particularly clear example for **Part III: Why AI-assisted code needs physical interpretation**.

- Our automatic rule examines local photometric shape and presumes a persistent sharp brightness fall could be instrumental.
- Observations of an actual known eclipsing binary provide a *different astrophysical explanation* for some similar shapes.
- The official NASA PDC correction preserves obvious astrophysical eclipses, while our extra local masking would eliminate samples near some flagged events.
- The six-star synthetic-step experiment previously removed **eight actual injected transit cadences** in one trial; this new real-binary example adds concrete physical plausibility to the concern about deleting real astronomical signals.
- Before any defensible gain could be claimed, an improved physical event-vetting policy should be trained or calibrated separately and tested on **untouched binary-star and independently source-labeled instrumental-event cohorts**.

This result naturally supports Lesson 6 (Kepler's laws and binary period), Lesson 5 (Newtonian orbital dynamics), and optional Lesson 3 (orbital phase and time measurement). See [the physics explanation](KEPLER47_COURSE_PHYSICS_EXPLAINED.md) for one worked eclipse-time calculation.

**Source and disclosure:** Orosz et al. (2019), *Discovery of a Third Transiting Planet in the Kepler-47 Circumbinary System*, DOI [10.3847/1538-3881/ab0ca0](https://doi.org/10.3847/1538-3881/ab0ca0). The code, checks, plots and explanatory text were AI-assisted; the student should independently inspect and interpret the evidence before submitting coursework.
