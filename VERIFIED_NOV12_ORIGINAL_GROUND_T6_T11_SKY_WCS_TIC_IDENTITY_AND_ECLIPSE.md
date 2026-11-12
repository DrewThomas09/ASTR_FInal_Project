# November 12, 2026 — Original ground telescope pixel-to-sky WCS confirms two reported neighboring eclipse apertures

**Result: Source-preserving and reproducible geometric association.** We projected the original observer-measured AstroImageJ T6 and T11 aperture centroids using *separately uploaded original plate-solved ground telescope FITS celestial WCS images*, and compared their derived sky positions to the separately cataloged ExoFOP nearby-star TIC RA/Dec. Both observer-named neighboring TICs matched their corresponding real aperture positions under a fixed, predeclared **5-arcsecond positional review tolerance**. Independent original TESS SPOC target sky coordinates agreed with the ground image's measured T1 target positions under a predeclared **8-arcsecond tolerance**.

This is stronger evidence for the **identity of the reported ground eclipsing-source aperture**, paired with the authentic numerical light-curve dips, but remains a source-level post-hoc case study rather than independent NASA ExoMiner++ accuracy testing.

## Physical identities, true original ground images and observed positions

| Original TOI / TESS target | Original ground aperture selected from independent observer notes | Original ground plate-solved FITS uploaded source ID | Named off-target TIC | Ground image WCS aperture-to-external neighbor offset | Ground T1 aperture-to-original SPOC target offset |
|---|---|---:|---:|---:|---:|
| **TOI-1223.01 / TIC382437043** | **T6** | **906276** | **TIC382437045** | **0.436 arcsec** | **0.359 arcsec** |
| **TOI-2250.01 / TIC264303333** | **T11** | **222164** | **TIC1884344804** | **2.202 arcsec** | **1.658 arcsec** |

All values were computed from unmodified original files in the [successful source-evidence workflow, **339 software tests passed**](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43333211789). [Download the source-authenticated original sky-position results and SHA checks](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43333211789/artifacts/13996945506).

**Source-preserving method:** Each actual full ground AstroImageJ photometry table is identified by its original public ExoFOP file ID (TOI1223 original numeric file **906268**, TOI2250 **222159**) and verified against the SHA256 preserved *before this analysis*. The original ground WCS FITS file IDs, **906276** and **222164**, were selected by the archived original ground-file metadata before downloading their contents; their FITS bytes, primary-HDU sky WCS headers and SHA256 were separately preserved. Both genuine uploaded images have **4096×4096** pixel primary image arrays and original `RA---TAN-SIP` / `DEC--TAN-SIP` celestial WCS. For each ground aperture, the median real `X(FITS)_T6/T11` and `Y(FITS)_T6/T11` original measurement pixel coordinates were converted with original WCS **1-indexed FITS pixel origin**, preserving actual distortion and camera rotation. We did not guess the CCD's celestial position angle or use TESS's 21″/pixel approximate scale for this ground telescope conversion.

The independent comparison target positions came from the **genuine original TESS SPOC target-pixel FITS target RA/Dec** recorded in the prior five-star source study; the independent comparison neighbor positions came from the **separately archived ExoFOP nearby TIC astrometry CSV**. The source records were matched by exact TIC, not an approximate star name. The original T1 target sky check guards against gross origin, scale or camera-axis mistakes; original observer notes caution that the *photometry* of saturated T1 is not a valid blank control, a distinct issue from its astrometric location.

We had predeclared **≤5 arcseconds** for the catalog-matched neighbor and **≤8 arcseconds** for the separately measured original T1 target positions before viewing these angular offsets. Both systems satisfied both thresholds. The same source selection and original numerical ground eclipse timing remain unchanged.

## Combined physical evidence (do not overinterpret)

The geometric agreement should be considered together with the **actual original time-dependent ground observations**, not as an independent eclipse detector:

| Ground source candidate | Original measured in-event dip at fixed observer-predicted time | Descriptive 5k block-bootstrap 95% | Robust baseline trend-only adjusted dip |
|---|---:|---:|---:|
| **TOI-1223.01 T6 / TIC382437045** | **39.03 parts per thousand (3.90%)** | **[32.96, 43.56] ppt** | **34.73 ppt** |
| **TOI-2250.01 T11 / TIC1884344804** | **259.75 ppt (25.98%)** | **[142.60, 345.18] ppt** | **269.54 ppt** |

Original external observers explicitly reported a near-TIC T6 on-time ~33-ppt NEB (TOI1223) and a T11 possible off-target nearby eclipsing binary with a very deep event (TOI2250). These reports identify which ground aperture was to be examined; the original ground numerically measured dips and newly checked original image sky coordinates supply additional and more independent physical evidence supporting that association.

However, we have not performed a new photometric measurement from *raw CCD images* nor a new expert pixel-level source-segmentation analysis: both the full AIJ relative-flux time series and plate-solved representative FITS images originated from the same observer's reductions, even though their original source files are separately checked. Aperture cross-contamination, spatial crowding, calibration uncertainties, saturation of the primary targets, and the selected cases' post-hoc nature remain. **TOI2250 was described by its observer as a PNEB (possible NEB)** and should not silently be upgraded to a fully independently confirmed binary merely because the recorded flux and sky aperture are consistent.

## What this changes for the TESS centroid experiment

The initial original NASA/TESS five-host centroid test involved 63 real TESS event windows, 4 eligible host directions (2 raw→corrected better, 2 worse). Previously we were careful not to call the five historic note-named neighbors five known source-localized binaries. We now have **two well-supported ground-aperture/nearby-TIC sky matches** to follow up, not five equal-quality source truths.

**Important eligibility and statistical limitation:** TOI-1223.01 contributed only **2 complete original SPOC event windows in its first preselected TESS sector**, so it remains *ineligible* for the fixed 3-event source-level directional comparison. TOI-2250.01 had **30 observed first-sector event windows**, with centroid angular mismatch relative to its note-named neighbor improving from **50.32° raw** to **32.37° after correction**; this isolated point estimate is neither a calibrated confidence interval nor evidence that the method improves the physical source location on unrelated systems. That source had only 20/30 windows with locally positive measured TESS flux depth, so original ExoFOP ephemeris/source matching and off-eclipse contamination require attention.

The three remaining source candidates included ambiguous, conflicting or instrumental ground notes, so the observed 2/4 exploratory sign comparison cannot be rebranded as 2/4 verified true-source classification. **No NASA ExoMiner++ neural outputs, official difference-image centroids, model scores or planets were changed or discovered.**

## Authentic source artifacts and code

- [Original source-known 5-star TESS centroid experiment and negative/source-label limitation](VERIFIED_NOV12_FIVE_NEW_SPOC_NEBS_ORIGINAL_CENTROID_NEGATIVE_RESULTS.md)
- [Original 162-/84-row T6/T11 ground numerical eclipse and source-drift sensitivity](VERIFIED_NOV12_ORIGINAL_EXOFOP_GROUND_T6_T11_NEIGHBOR_APERTURE_ECLIPSE_AND_BASELINE_AUDIT.md)
- [Original plate-solved 4096² ground source FITS, TAN-SIP headers and AIJ xy inventory](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43332689126/artifacts/13994784711)
- [Original sky TIC match, per-TIC offsets, source SHA256 checks and full-science 339-test passing run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43333211789)
- [Ground source pixel-to-sky reproducible audit script](exofop_two_ground_NEBS_actual_aperture_sky_WCS_ID.py)
- [Exact original source artifact WCS and TIC check workflow](.github/workflows/exofop-two-ground-Neb-AIJ-pixel-to-sky-TIC-WCS.yml)
- [Independent source test controls](tests/test_exofop_two_ground_NEBS_actual_aperture_sky_WCS_ID.py)

**AI assistance disclosure:** GPT-6 wrote the source-exact ground WCS retrieval, celestial projection, original AIJ aperture TIC mapping, independent-original-TESS target check, match thresholds, regression tests, scientific analysis and this report. The student should verify the source data and interpretation and disclose these AI contributions. This is not an independent exoplanet discovery or NASA classifier improvement.
