# November 12, 2026 — Two original ExoFOP ground-reported NEB neighbors corroborated by public astrometry

**Scope:** two consciously **post-hoc demonstration candidates** chosen after an original public 30-target follow-up-note inspection. They are **not** a fresh physically truth-verified holdout, and the original TESS moment-centroid model has **not** been evaluated on either source.

## Why this is more informative than the historical EB label

The original ExoFOP public TOI table downloaded November 12 had **8,175** TOI records; **1,322** had broad TFOPWG `FP` dispositions. That field did not encode the `NEB` or `EB` physical photometric subtype directly. Requiring a positive public time-series observation count and a valid reported catalog ephemeris, while excluding the earlier **56 personally inspected TESS stars plus one pilot**, yielded **868 distinct false-positive-labeled TIC hosts** for further evidence review. These are **not** 868 nearby eclipsing binaries.

The first fixed SHA256-ordered 30 FP host targets were screened using **original public ExoFOP observing-note CSVs**. All 30 notes were fetched with zero errors. **21/30** notes carried an explicit `NEB` or `PNEB` photometric-disposition token, **1/30** carried only an `EB/BEB/SEB` photometric-disposition token, **1/30** only mentioned NEBs without such a disposition, and **7/30** did not have a clearly matching NEB phrase. These counts are original **text evidence leads** and cannot stand in for spatial source verification. Notes that say NEBs were *ruled out* can still contain the term NEB. Original catalog snapshot SHA256: `5b54c8a9a74593dec8380fa2db3d9c5bc1757f0da4842bb5282c42a47a2dde81`.

Two follow-up records went one step further: their original public notes explicitly reported a different TIC as the eclipsing source, along with a nearby angular separation. These named sources were cross-checked against **a separate ExoFOP nearby-target astrometry table** for the same main TIC, rather than being taken solely from the prose.

| Original TESS TOI target | Ground-based note names eclipsing neighbor | Original note separation | Independent nearby-target table separation | Catalog position angle (east of north) |
|---|---|---:|---:|---:|
| TOI-2041.01 / TIC **54364414** | TIC **54364420** | **23.4 arcsec** | **23.82 arcsec** | **101.25°** |
| TOI-4255.01 / TIC **82302240** | TIC **82302236** | **5.0 arcsec** | **5.10 arcsec** | **31.21°** |

Both original notes contained the named nearby TIC and an explicit reported NEB photometric disposition; both catalog requests succeeded and uniquely returned that nearby TIC and a consistent angular distance (within **2 arcseconds** of the note). The raw nearby-source CSVs, each SHA256 digest and the full source-note snapshot digest are archived. The first case's follow-up note describes a nearby source labeled T11 and a repeated event on TIC 54364420; the second describes a ground-based eclipse in a neighbor labeled T2, TIC 82302236, and states that the original event is not on the target. These are **reported external ground-based results**; original uploaded light-curve FITS and source images remain to be examined independently.

**Relative to the approximate TESS 21 arcsec/pixel plate scale**, the cited sky separations are about **1.13** and **0.24** TESS pixels. This illustrates why a small measured moment-centroid change does not identify a physical source location by itself: both an eclipse depth and the relative flux contributions of all aperture stars matter.

## The two-source physics check (the direction is not toward the dimming neighbor)

For a simplified unresolved aperture with target star flux `F_t` at coordinate 0 and nearby star `F_n` at position `d` along the target-to-neighbor axis, the out-of-eclipse flux-weighted centroid is

`C_out = F_n*d/(F_t+F_n).`

If the *neighbor* becomes dimmer by fractional depth `δ`, then

`C_in = (1-δ)*F_n*d/(F_t+(1-δ)*F_n).`

Subtracting gives

`ΔC = C_in - C_out = - δ*F_t*F_n*d / [(F_t+F_n)*(F_t+(1-δ)*F_n)].`

For positive fluxes and a genuine eclipse (`δ>0`), the result has the **opposite sign** to the target-to-neighbor position vector: the measured first-moment centroid typically shifts **away from the dimming off-target neighbor**. It is *not* correct to infer that a simple moment-centroid shift points toward the eclipsing star. This derivation assumes a fixed two-source blend and ignores spacecraft motion, finite aperture response, detector PSF and additional blends. NASA's difference-image PRF localization is a more sophisticated and different measurement.

In sky coordinates, the predicted direction *away* from the named neighbor, for the above simple model, would have a position angle approximately **281.25°** for TOI-2041.01 and **211.21°** for TOI-4255.01. **These predictions have not been compared with measured TESS centroid vectors** and are not declared pass/fail. The TESS detector row/column coordinates require sector-specific WCS mapping before any comparison with sky position angles.

## Exact reproducibility

- [Archived original publicly sourced 8,175-TOI catalog + 868-FP follow-up review pool](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43302487226/artifacts/13981608471)
- [30 original ExoFOP public observation-note downloads (11 source parsing tests pass)](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43302814103/artifacts/13982685958)
- [22 exact original public photometric-disposition note excerpt review rows, anchored to archived note sources](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43303219599/artifacts/13983375315)
- [Successful two-source same-TIC nearby astrometry check (4 tests pass), with original separate nearby catalog rows and notes](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43303521905/artifacts/13983715366)
- [Astrometry source-audit script](exofop_two_reported_neb_astrometry_crosscheck.py), [four tests](tests/test_exofop_two_reported_neb_astrometry_crosscheck.py), [source-check workflow](.github/workflows/exofop-two-posthoc-neb-astrometry.yml)

The next necessary physical experiment is to acquire the **original TESS SPOC 2-minute time-series/TCE event identity for these exact two TOIs**, preserve all missing-observation and period-alias cases, compare original raw and experimentally pointing-subtracted *signed* event vectors in sector-specific WCS sky coordinates, and inspect the original ground-based reported eclipse evidence. These selected examples remain **post-hoc demonstrations only**. A generalizable improvement claim requires a separately and prospectively locked new source cohort, not this 30-source note-screen-derived pair.

**AI assistance disclosure:** GPT-6 authored source retrieval scripts, original documentation parsing, source/TIC matching, uncertainty/denominator safeguards, the two-source blending explanation and this draft. The student must independently verify the original FITS, the ground follow-up diagrams and final scientific interpretations. Neither NASA pretrained model nor the prior 56-star source data were altered.
