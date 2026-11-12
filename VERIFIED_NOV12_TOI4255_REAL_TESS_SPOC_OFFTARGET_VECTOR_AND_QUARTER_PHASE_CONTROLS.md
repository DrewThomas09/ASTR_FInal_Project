# November 12, 2026: Actual TOI-4255.01 TESS 2-minute data and an inconclusive centroid-direction improvement

**Source-verified exploratory one-host demonstration, not an independent exoplanet validation.** The comparison uses authentic MAST TESS SPOC two-minute light-curve/target-pixel FITS for a previously selected nearby-eclipsing-binary (NEB) report. NASA ExoMiner++ v2.4.0 weights and original outputs were **not** rerun or changed.

## Original external physical question

Ground-based follow-up notes for **TOI-4255.01 (TIC 82302240)** report an off-target eclipsing source **TIC 82302236**. An independent public ExoFOP nearby-target astrometry table identifies that neighboring TIC at **5.10 arcseconds**, position angle **31.21° east of north**, consistent with the observing note's approximate 5.0 arcseconds. For an idealized static two-source blend, the in-eclipse first-moment centroid should shift **away** from the dimming neighbor, so the expected approximate sky position angle of the shift is **211.21°**. A real instrument aperture has additional sources, PSF and pointing effects, so this is a *directional surrogate*, not ground-truth sky localization.

The original public ExoFOP TOI catalog provides period **2.5057108 days**, epoch **BTJD 2964.80591**, and original event duration (read directly from the checksum-preserved catalog). The exact epoch is shifted by the external published period, *not optimized* on a new TESS centroid result. Only original quality-zero SPOC cadences and measured centroid fields are used; no interpolated events or synthetic flux measurements enter the science.

## Important source coverage denominator

The first two post-hoc ExoFOP cases were TOI-2041.01 and TOI-4255.01. The exact original MAST two-minute SPOC product discovery returned **no matching 2-minute SPOC observation** for TOI-2041.01/TIC 54364414; it cannot silently be substituted with TESS-SPOC FFI data. For TOI-4255.01, original two-minute SPOC LC and target-pixel files were found for **sectors 61 and 62**. The original file TICID, sector and SHA256 digests were checked before processing, and the *FLUX column's genuine original TAN WCS* from the TPF (not a guessed plate-scale rotation) was used for target-to-neighbor detector direction. Both original FITS-source hashes were reproduced without change by the later sensitivity workflow.

The analysis therefore contains **one distinct TESS target star, two original instrument sectors, and 18 complete same-orbit event windows**. It does **not** contain two independent validation stars or an independently held-out NASA neural training sample.

## True original observed event window results

| Original source measure | TESS sector 61 | TESS sector 62 |
|---|---:|---:|
| Fully matched genuine observed event windows | 8 | 10 |
| Original locally positive flux dips | 8 | 9 |
| Median measured local PDCSAP flux dip | 0.2572% | 0.3046% |
| Original raw moment centroid angle from predicted *away-neighbor* direction | **55.95°** | **153.84°** |
| Experimental `MOM_CENTR - POS_CORR` angle | **14.39°** | **15.56°** |
| Raw source-event median signed vector amplitude | 0.0002145 px | 0.0000981 px |
| Corrected source-event median signed vector amplitude | 0.0001881 px | 0.0002347 px |
| Median raw *before/after* local centroid motion proxy | 0.001331 px | 0.001497 px |
| After pointing subtraction: before/after motion proxy | 0.001592 px | 0.001392 px |

These are **actual original SPOC source measurements**, not a simulation. Smaller alignment angle is a better geometric point estimate under the stated physical hypothesis. Yet the original drift proxy became *larger* in sector 61, showing that before/after measurement stability and geometric alignment are different objectives.

## Source-SHA pinned robustness on the same physical events

After observing the first two striking geometric point estimates, we designed an **explicitly post-hoc** sensitivity study. It **downloaded both original LC/TP FITS again**, verified their SHA256s against the earlier archival output, verified all 18 original event-orbit identities and signed original vectors numerically, and kept the original ephemeris, duration and source identity unchanged. It used 20,000 paired *within-sector event* bootstrap resamples to describe how uncertain these estimates are **within this one star**; this is *not* 20,000 independent stars or a mission false-positive test.

| Paired angle difference, raw minus corrected | Sector 61 | Sector 62 |
|---|---:|---:|
| Observed sample point estimate | +41.56° | +138.27° |
| Event-bootstrap 95% descriptive interval | **[-137.91°, +65.72°]** | **[-13.05°, +159.77°]** |
| Fraction of paired event resamples with corrected angle smaller | **53.4%** | **94.2%** |

**Neither uncertainty interval excludes no improvement (zero).** Sector 61 is especially unstable to the specific individual observed events. Sector 62 is more suggestive but still not decisive; the same astrophysical host and spacecraft systematics could influence all its events.

## Two quarter-period negative-control windows per sector

To test whether the corrected source direction aligns even *away from* the reported eclipse time, we compared the same original FITS with the event window centers shifted by **-P/4** and **+P/4** relative to the original ExoFOP ephemeris (chosen after the first real-event results but before viewing these controls). These controls are not guaranteed astrophysically clean; a binary could have secondary eclipses or other periodic variability, and a phase-shifted centroid correlation is not an independent source.

| Control summary | Sector 61 | Sector 62 |
|---|---:|---:|
| True eclipse pointing-corrected angle | **14.39°** | **15.56°** |
| -P/4 control corrected angle | 90.61° | 70.30° |
| +P/4 control corrected angle | **13.80°** | 152.02° |
| True median local PDCSAP flux dip | +0.2572% | +0.3046% |
| -P/4 control median local dip | +0.0493% | +0.0254% |
| +P/4 control median local dip | -0.0519% | -0.0182% |
| -P/4 matched actual observed windows | 9 | 8 |
| +P/4 matched actual observed windows | 8 | 10 |

**Key challenge:** In **sector 61, the +P/4 control displays almost the same corrected direction alignment (13.80°) as the real eclipse (14.39°), despite its negative median flux depth.** Thus the 14.39° figure by itself cannot be attributed to successful physical eclipse-source localization. Sector 62's true-event direction is more distinctive than its quarter-phase controls, but again the within-source bootstrap interval crosses zero.

We did not change the correction method, orbital period, time window, sample cohort, or angle after seeing these controls. All measurements remain observable, including unwelcome outcomes.

## Final interpretation

**Supported:** for one authentic external reported nearby eclipsing binary, original TESS observations yield two sector-level point estimates whose corrected centroid vectors align more closely than raw vectors with the predicted direction *away from* the cataloged neighbor. Source hashes, identities, WCS and flux event windows are reproducible.

**Not supported:** a robust statistically significant improvement in physical source localization, a uniquely transit-specific direction signature in both sectors, a new planet, or improved NASA ExoMiner++ classification. The sector 61 false-alignment control and broad bootstrap intervals specifically preclude the stronger claims.

The next *scientifically necessary* test would use several **new host stars with independently verified ground-based off-target eclipsing sources** selected before viewing their TESS moment-centroid values, including proper on-target comparison stars. Otherwise repeatedly adjusting this one system's methods will yield post-hoc overfitting.

## Source and verification archive

- [Original ExoFOP two reported NEB neighbor astrometry, names and position angles](VERIFIED_NOV12_EXOFOP_2_POSTHOC_REPORTED_NEB_NEIGHBOR_ASTROMETRY.md)
- [Original verified TOI-4255.01 S61/S62 NASA SPOC time-series/WCS run: **300 tests passed**](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43317149942)
- [Original observed eclipse events, source hashes, geometry and two true-event figures](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43317149942/artifacts/13988811619)
- [Exact original source-sha pinned quarter-phase and event-bootstrap follow-up: **303 tests passed**](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43317658123)
- [Original source event resamples, quarter-phase control CSVs, summary and true-versus-control figure](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43317658123/artifacts/13988303112)
- [Primary original LC/TP/WCS event analysis code](tess_toi4255_original_spoc_neb_vector_case.py)
- [Pinned same-source phase and paired event bootstrap control](tess_toi4255_source_pinned_quarter_phase_controls.py)
- [CI scientific verification for original true-event run](.github/workflows/tess-toi4255-original-spoc-wcs-event-vectors.yml)
- [CI scientific verification for source-pinned phase controls](.github/workflows/tess-toi4255-quarter-phase-source-controls.yml)

**AI-use disclosure:** GPT-6 implemented source-file acquisition, exoplanet ephemeris matching, FITS and true TPF WCS geometry, same-event raw/corrected centroid processing, plotting, source SHA guards, post-hoc within-star uncertainty, quarter-phase controls, scientific tests and drafting. The student must check the original source evidence and interpret the physics, and disclose AI assistance according to the course rules.
