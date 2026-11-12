# November 12, 2026: additional five-source TESS cohort frozen BEFORE looking at new centroids

**Scope:** A centroid-unseen, new-to-this-student-project follow-up cohort derived from source-original public ExoFOP ground-observation notes and original MAST SPOC two-minute light-curve/target-pixel product metadata. **It is NOT independently truth-verified**, not proven absent from NASA's own training set, and not a prospectively randomized survey cohort.

## Scientific reason for the new cohort

The initial one-star off-target TOI-4255.01 study gave visually promising sector-level corrected centroid alignment but *neither paired within-sector bootstrap interval excluded zero improvement*. A sector-61 shifted control aligned just as closely away from the actual eclipse. Testing additional host stars is scientifically preferable to repeatedly tuning the same one-star result.

The earlier external source process screened an exact dated ExoFOP public TOI catalog snapshot: 8,175 TOI entries, 1,322 broad FP source status entries, 868 unique FP TICs with some reported ground-based time-series follow-up and valid timing. From a deterministic thirty-target note review, 21 hosts had explicitly reported photometric `NEB` notes. Excluding two already examined post-hoc original targets left **19 distinct new source-note leads**. A strict original NASA/MAST SPOC **2-minute** target-name matching query identified **10 distinct hosts with genuine matching LC and TP products**. No light curves or centroid signals were opened at the source-selection stage.

The 10-host original ExoFOP neighbor-catalog audit fetched all ten public nearby-target astrometry CSVs and matched TIC IDs explicitly named in the earlier NEB notes. Five had **exactly one other TIC** reported in such a note and present in the independent neighbor astrometry table, one had more than one matched named TIC and four had none. Importantly, a named TIC may be ruled out or unrelated to the physical eclipse, so these are research candidates only. No independent original uploaded ground-based light-curve photometry was inspected or certified at this stage.

## Frozen exact source records

The following five candidates were fixed in the *pre-centroid* manifest, with one source sector per host selected strictly as the **lowest numbered actual original SPOC 2-minute LC/TP sector**. This prevents selectively choosing a sector that displays a flattering correction.

| TOI | Genuine TESS host TIC | Frozen first sector | ExoFOP note-named and externally catalog-matched nearby TIC |
|---|---:|---:|---:|
| TOI-1330.01 | 357457104 | 15 | 1973994316 |
| TOI-1223.01 | 382437043 | 1 | 382437045 |
| TOI-3712.01 | 354442783 | 59 | 518660670 |
| TOI-2846.01 | 66151343 | 61 | 66151336 |
| TOI-2250.01 | 264303333 | 14 | 1884344804 |

These TIC IDs, sectors, original full MAST LC and TP product URIs, original ExoFOP period/epoch/duration, exact neighbor catalog RA/Dec, separation/position angle, source-hash-selected record order, and all missing-label warnings are frozen as a single *full JSON source artifact*. **No replacement stars will be chosen if an actual light curve, event window, WCS or note match fails.**

**Immutable original artifact digest:** `c5c32ce8d114d3dc37b2cf138061e0810ed057165f9bc25e4ae2bebfe906ea5f`. Upstream candidate/source artifact SHA256 pins are embedded in the frozen file.

## Scientific limits, before performing follow-up

- The new-star source selection is **blind only to our five stars' TESS centroid outcomes**, not independent of our previously read ExoFOP source notes or NASA's own model training.
- The five note-named TICs are **not automatically proven to be the genuine eclipsing neighbors**. Separate ground-based observation records, full light curves and precise eclipse timing are required to verify real physical truth.
- The primary descriptive question is whether genuine observed source event moment centroid shifts move **away from** the independent cataloged neighbor more closely after an exploratory pointing correction, not whether an exoplanet has been correctly confirmed.
- Report all five hosts, source FITS errors, missing/invalid epochs, WCS inconsistencies, source-level angular comparisons and deliberately fixed quarter-phase controls. Independent units are **host TICs, not multiple sectors or repeated transit events**.
- A statistical improvement in exoplanet planet/false-positive classification requires a separate independently verified label cohort with both on- and off-target sources; this sample alone cannot demonstrate it.

## Reproducibility

- [Completed 19-lead real MAST original SPOC coverage screen: 10 distinct 2-minute source hosts](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43318451723/artifacts/13989536578).
- [Completed all-ten ExoFOP real neighbor source catalogs: five single-TIC named catalog matches](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43318756858/artifacts/13990050729).
- [Successful source-FROZEN-before-centroids GitHub run, three source integrity tests](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43319246311).
- [Exact frozen JSON manifest and original SHA pins](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43319246311/artifacts/13988614232).
- [Frozen source selector implementation](tess_five_new_neb_frozen_source_manifest.py).
- [Prospective relative-to-centroid exact source list](.github/workflows/tess-five-new-neb-frozen-precentroid.yml).

**AI contribution disclosure:** GPT-6 authored public source screening, external neighbor crosschecks, frozen source selection and deterministic first-sector choice, source integrity tests and this research note. Students should independently review original ground-based photometry and interpretation before using these notes as verified physical labels or submitting course work.
