# Building an interpretable transit-centroid companion to NASA ExoMiner++ (original TESS SPOC photometry)
**Scientific protocol committed 2026-11-08, prior to running the new event-local centroid code on the reused stars. This file is a method, not a successful-result claim.**

## A physics-based source-location question

A transit occurs when an intervening object blocks part of a star's light. A reduced **flux** measurement alone does not determine **which star** in the detector aperture actually dimmed. TESS has approximately **21 arcseconds per detector pixel**, and physically neighboring stars may enter an aperture.

The standard first moment of a pixel flux image is

`C_x(t) = sum_j [x_j f_j(t)] / sum_j f_j(t)`, `C_y(t) = sum_j [y_j f_j(t)] / sum_j f_j(t)`.

NASA SPOC already computes flux-weighted `MOM_CENTR1` and `MOM_CENTR2` (CCD column and row coordinates, in pixels) in the original 2-minute TESS light-curve FITS. `POS_CORR1` and `POS_CORR2` record common field-of-view motion estimates from pointing/motion polynomials; missing correction measurements must **not** be treated as zeros.

Instead of fitting the complete neural network, a **separate AI-assisted companion** asks whether moment-centroid coordinates differ in a local, transit-associated way. For an original NASA-predicted TCE with orbital period P, transit epoch T0 and duration D, the cadence center is `T_k = T0 + kP`.

Only original NASA FITS rows with quality bitmask exactly zero, finite positive measured flux, and finite centroid coordinates are eligible. For each event:
- **In-transit window:** `|t - T_k| <= 0.5D`
- **Pre-event sideband:** `[-min(3.5D, 0.44P), -1.5D]`
- **Post-event sideband:** `[1.5D, min(3.5D, 0.44P)]`
- A valid event must have at least **3 actual measured in-transit cadences** and **6 measured cadences in EACH flanking window**. Do not interpolate gaps or replace missing astrophysical data with constant flux or centroid.
- **Experimental pointing-corrected coordinate:** `C'_x(t) = MOM_CENTR1(t) - POS_CORR1(t)`; similarly for `C'_y(t)`. This is our proposed exploratory transformation, **not necessarily the official NASA model's centroid method**.
- Local shift vector: `Delta C_k = median(C' | in) - 0.5 * [median(C' | pre) + median(C' | post)]`. Medians are computed *componentwise* in CCD pixels. A separate original **raw MOM_CENTR without subtraction** diagnostic measures sensitivity to pointing correction.
- Source-level summary: median of signed event delta-x and delta-y over separate independent observed events, with norm `sqrt(median(delta_x)^2 + median(delta_y)^2)`.
- **Uncertainty:** bootstrap **whole event vectors**, not individual 2-minute cadences, for 500 replicates and 95% descriptive x/y intervals. Three events minimum. This is not a calibrated centroid significance because both star activity and instrument effects cause correlated noise.

### Fixed illustrative manual-review rule (NOT a replacement for NASA classification)

Before looking at actual shift statistics, the experiment froze a simple, intentionally conservative **human-review warning only**, not a newly trained veto or mission-validated false-alarm calibration:

1. At least **three separate observed events** with proper in/pre/post source measurements;
2. Median **two-dimensional local shift >= 0.05 CCD pixels** (roughly 1.05 arcseconds at 21 arcsec/pixel);
3. The event-bootstrap 95% interval for at least one signed axis does not contain zero.

The official NASA probability/score is **never altered** by this experimental flag. The output can say `manual_review_required` beside `NASA_original_score`, but cannot turn it into a new physical planet validation or new false-alarm classification. A prior KP/CP-labeled source being flagged is a **warning that a naïve veto could harm known positives**, not proof the earlier label is wrong.

The threshold was chosen for an **engineering feasibility demonstration**, not estimated from a clean independent calibration set. A credible threshold would require many labeled examples and empirical false-alarm budgets; **these have not been acquired for this code**. Other unresolved source-locus issues include large source apertures, strongly correlated pointing drift, saturated stars, secondary eclipses, background events and unexpected TCE aliasing.

## Exactly which original data and model were used

- Published 2025 ExoMiner++ TESS SPOC 2-minute S1-S67 source: `https://zenodo.org/records/15466293`, original labeled CSV MD5 `c79f3651d556e71f7878a46f960d09b4`.
- TESS/MAST original SPOC 2-minute light-curve `_lc.fits` files, with original source header `TICID` and `SECTOR` **required to match the specific NASA TCE**. Files come from official NASA pipeline execution, not internet-generated light-curve illustrations.
- Official unmodified **NASA ExoMiner++ v2.4.0** model container digest: `ghcr.io/nasa/exominer@sha256:1b7ffac9db8afe1787ec9a0464ed8cc16ab91b7a280e6e824c27e3a121b0c6e9`.
- [Frozen 32 original source TICs and 2025 categories](TESS_32STAR_CENTROID_ALIAS_COMPANION_FROZEN_2026_11_08.json) consist **exactly** of [16 previously selected balanced KP/CP/EB/NTP cases](TESS_16STAR_OFFICIAL_EXOMINER_COHORT_FROZEN_2026_11_08.json) and [16 older 2025 model errors](TESS_16STAR_2025_ERRORS_VS_2026_FROZEN_2026_11_08.json). These **have previously been inspected by the AI assistant and cannot be treated as fresh unseen stars**, even though centroid values themselves were not inspected before the fixed formula was committed.
- [Source-checked code](tess_original_moment_centroid_companion.py); [real and synthetic-source test suite](tests/test_tess_original_moment_centroid_companion.py); [reproducible official NASA original-data workflow](.github/workflows/nasa-exominer-32star-centroid-companion.yml).

## Pre-specified engineering evaluation, not independent planet sensitivity

- Preserve **all 32 requested host sources** and exact 2025 event UIDs, including every missing event, incompatible period alias, original FITS, or centroid field.
- Report original official NASA v2.4.0 raw score and raw catalog label unchanged; report centroid shifts only if observed and legitimate; no source labels used in extraction.
- Tabulate missingness by class, event count and the number flagged for **manual review**.
- Do not call raw 2025 label agreement an independent 2026 model precision estimate; source signal period/UID may change between versions, as shown in prior [real 224-test identity audit](VERIFIED_EXOMINER_2025_VS_2026_EVENT_IDENTITY_CORRECTION_2026_11_08.md).
- Even a positive association between shift and source class would not establish a distinct improvement beyond NASA, because contemporary **ExoMiner already includes centroid and difference-image branches**.

### Scientific external documentation

- Space Telescope Science Institute MAST notebook, original TESS LC fields (MOM_CENTR1/2, POS_CORR1/2): https://spacetelescope.github.io/mast_notebooks/notebooks/TESS/beginner_tour_lc_tp/beginner_tour_lc_tp.html
- NASA TESS Science Data Products Description, section on LC moments, centroid-error and spacecraft-motion fields: https://ntrs.nasa.gov/api/citations/20180007935/downloads/20180007935.pdf
- NASA TESS instrument information, 21 arcsec pixel scale and aperture crowding: https://heasarc.gsfc.nasa.gov/docs/tess/telescope_information.html
- Original ExoMiner++ 2025 researchers' source, DOI: https://zenodo.org/records/15466293

**AI contribution disclosure:** GPT-6 wrote the physically motivated centroid processing, safety checks, source provenance audit and scientific interpretation. This is a classroom research tool, not a NASA flight pipeline modification, and the student must inspect primary source results and disclose AI assistance.
