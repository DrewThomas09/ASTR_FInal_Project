# November 12, 2026 — precommitted new five-star confirmed-planet control source set, before reading original TESS centroids

The preceding source-frozen five off-target-neighbor-TIC *candidate* investigation did not show a robust source-level improvement from the exploratory `MOM_CENTR - POS_CORR` correction. Independent follow-up review of original observer ground data subsequently strengthened the sky and light-curve evidence for exactly two of those candidate neighbors (TOI-1223.01 T6/TIC382437045 and TOI-2250.01 T11/TIC1884344804), not all five source-note labels.

To avoid repeatedly testing the same two selected systems, this new investigation uses **five completely separate host stars whose planets are independently listed in the official NASA Exoplanet Archive as confirmed transiting planets and in ExoFOP as known planets**. The five exact source identifiers, original SPOC 2-minute FITS product pairs, first sectors and published ephemerides were frozen **prior to viewing any of their source centroid values**, not selected based on the result.

## Independent source catalogs and exact source-selection protocol

1. Reuse the immutable original **ExoFOP 8,175-row catalog snapshot** from the earlier original FP/NEB research, original SHA256 `5b54c8a9a74593dec8380fa2db3d9c5bc1757f0da4842c42a47a2dde81`.
2. Independently request the original NASA Exoplanet Archive `pscomppars` confirmed transiting-planet source with `tran_flag=1` and a nonempty TIC; its original 2026-11-12 SHA256 was `22be1dc766df9abe4f40c0e821bd87ce24ec4e60f4ac27283f98ae65f9c6d2d0`. Keep original `pl_name`, `tic_id`, sky coordinates, orbital period, `cb_flag` and `pl_controv_flag`.
3. Require **ExoFOP TFOPWG disposition KP**, exact NASA-confirmed TIC host identity, non-circumbinary and non-controversial NASA flags, confirmed planet transit flag, period consistency better than **1%**, original ExoFOP reported period **≤6 days**, and a physically usable original TOI epoch/duration. This yields **443 distinct NASA/ExoFOP-concordant eligible host TICs** before the final MAST two-minute source requirement.
4. Exclude all **56 earlier original TESS cohort TICs**, the historic pilot star, both previously inspected TOI-2041/4255 post-hoc source cases, and all **five** previously analyzed new ExoFOP NEB-note neighbor hosts; do not reuse a pre-examined source.
5. Order candidate host TICs by a fixed **SHA256 seed** and examine MAST **SPOC original 2-minute target-matching LC and target-pixel FITS product availability only**. Screen at most 30 hosts and freeze the *first five* with exactly paired original LC+TP products. Freeze the **lowest-numbered actual source sector** per host; no observation period or star may be reselected after centroid access.
6. Preserve both independent source catalogs' original byte hashes, source candidate filtering counts, all product URIs, original published TOI period/epoch/duration, no-centroid declaration, and any failures in one original JSON source artifact.

## Exact frozen real-source selected host units

| Independent confirmed exoplanet | Original NASA/ExoFOP host TIC | Original TOI | Source-frozen first SPOC 2-minute sector |
|---|---:|---:|---:|
| **KELT-14 b** | **134537478** | **501.01** | **7** |
| **CoRoT-1 b** | **36352297** | **547.01** | **6** |
| **WASP-168 b** | **232038798** | **1909.01** | **32** |
| **HAT-P-30 b** | **455135327** | **490.01** | **7** |
| **WASP-82 b** | **452808876** | **453.01** | **5** |

All **five** exact source availability probes succeeded, with no replacements or rejected first-sector sources; the catalog preparation work examined **zero actual TESS moment centroid measurements**. The successful [source-only workflow 43346848609](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43346848609), original source products and full [frozen precentroid artifact](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43346848609/artifacts/14001463866) prove the temporal source freeze.

## Predeclared actual original-source experiment

Use original archived MAST SPOC **2-minute LC/TP FITS** for each of exactly those five TICs and earliest source sectors. Validate `TICID`, `SECTOR`, genuine WCS, original source SHA, and independent NASA catalog star coordinates. Read actual original `MOM_CENTR1/2`, `POS_CORR1/2`, original `PDCSAP_FLUX`, and original source quality-zero timestamps, using **published unrefitted ExoFOP TOI period, epoch, duration**.

For every genuine complete in-event cadence window, calculate exactly paired raw in-minus-flanking CCD centroid vector and the same-vector after exploratory `MOM_CENTR - POS_CORR`, *without* changing NASA's published pretrained ExoMiner++ model. At **two fixed quarter-orbit phase offsets (`-0.25P`, `+0.25P`)**, measure identically complete pseudo-event windows as source-specific instrument controls, preserving the caveat that other planets or variability may appear in those control windows.

Compare per *independent host* TIC, not per transit:
- **Median raw and adjusted in-event 2-D centroid vector norms** in original CCD pixels; reduction is a measurement change, **not automatically better astrophysical classification**.
- **Median flanking pre/post centroid motion** in the same source event windows, a local instrumental stability proxy.
- **Raw/adjusted event minus median of fixed quarter-phase control vector norms**, measuring whether signal-like centroid displacement at the published transit ephemeris differs from pseudo-event epochs.
- Original source-level counts and whether at least **3 complete real transit windows and at least 3 windows for each fixed phase control** permit a source-level contrast. Preserve sources failing coverage.
- Descriptive source-level signs, 20,000 whole-host bootstrap median intervals and exact sign-test p-values where eligible, not event-window pseudoreplication.

**Important physics:** Even when a genuine transit occurs **on the target**, an unresolved **non-eclipsing** neighboring star can pull a flux-weighted blended centroid *toward* that neighbor when the target dims. Therefore do not assume an authentic confirmed transiting planet always has identically zero moment-centroid shift or a zero direction angle. No ground-based original pixel-level on-target photometric localization was carried out here, so catalogue confirmation is a high-confidence external positive control **but not an independently truth-labeled imaging-validation sample**.

## Key limits

Original NASA confirmed planet status is different from no overlap with original NASA ExoMiner training or direct independent sky-source localization. This is a comparison of source-preserving centroid measurement behavior across five previously centroid-unseen, real transiting planetary hosts; it does not establish improved discrimination of planets versus false positives. The prior two original ground-observed neighbors are separately retained as off-target case studies. Their original event denominators are small, particularly TOI-1223.01 with two original first-sector windows.

**Disclosure:** GPT-6 authored the original NASA+ExoFOP source matcher, source-exact MAST availability screen, precommitted statistical protocol, science execution and synthetic integrity tests. The student should review original astronomical sources and conclusions and disclose assistance in course work.
