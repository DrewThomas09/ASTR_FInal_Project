# November 12, 2026 — Independent numerical ground-aperture verification of two externally reported nearby eclipse events

**Original evidence and fixed-window result:** After the 5-host genuine SPOC 2-minute centroid test failed to show a consistent pointing-subtraction localization benefit, we downloaded actual original ExoFOP ground observing **time-resolved AstroImageJ photometry** to check whether two of the putative neighboring eclipses are measurable in the sky source apertures described by ground observers. **Both the observer-identified T6 and T11 apertures show large fixed-window dimmings**, and the sign of each dip survived three original-source-preserving baseline alternatives. This is not NASA ExoMiner classification improvement, not a new planet, and not yet independently plate-solved source TIC mapping.

## Why five source-note NEB labels cannot be treated as five confirmed physical off-target eclipses

The earlier new-to-the-project five-source original SPOC study used five TICs chosen before their moment-centroid measurements and known nearby sky TIC coordinates named in historical ExoFOP observer notes. When we examined the uploaded *primary ground follow-up* observer notes rather than relying on catalog dispositions, the source labels became much less homogeneous:

| Original TOI | Original observer evidence | What it does and does not imply |
|---|---|---|
| **TOI-1223.01**, host TIC 382437043 | LCO-SSO 2023-03-03 observer describes an **on-time ~33-ppt dip** in nearby **T6/TIC 382437045**, ~24.6 arcseconds from target; the primary host image was saturated | Strong observer-reported NEB aperture, original flux reanalysis below; target T1 is not a reliable negative control |
| **TOI-2250.01**, host TIC 264303333 | LCO-McD 2021-07-10 observer describes **possible nearby eclipsing binary T11/TIC 1884344804**, ~31.6 arcseconds away, with a deep ~350+ ppt V-shaped light curve; target saturated | Strong observer-reported *possible* NEB aperture, original flux reanalysis below; not a mission-confirmed source claim |
| TOI-1330.01 | Ground 2020-08-09 T1 saturated and nearest T2–T4 not resolved; another observation had approximate 6, 17 and 43 ppt events in several apertures with inadequate precision. Original T4 TIC1973994316 was considered possible, **not unique** | **Ambiguous** ground source, unsuitable as a confirmed localizable NEB |
| TOI-3712.01 | Ground report describes source photometry compromised by contaminated apertures and an apparent transit attributed to instrumental systematics | **Ambiguous / possible instrumental false alarm**, not verified independent off-target neighbor |
| TOI-2846.01 | Ground 2021-12-16 notes possible *early* target egress; 2022-10-17 notes report no event and clearing many neighbors | **Conflicting or on-target suggestions**, not verified off-target source TIC66151336 |

These evidence categories do not alter the genuine SPOC centroid measurements or invalidate their earlier **2/4 better, 2/4 worse** descriptive comparison relative to note-named positions. They *do* prevent any interpretation that the four evaluable hosts were four ground-truth-certified off-target eclipsing binaries.

## Source-original ExoFOP records and no outcome-based file selection

- An official ExoFOP uploaded-file inventory contained **184** original uploaded file records across five hosts and **11** ground observing time-series summaries. The initial broad filename categorization marked **46** files as possible numerical evidence, including imaging, notes and spectra; **46 cannot be equated to 46 numerical light curves**.
- **23 observer uploads** were identified by file ID from the original unchanged catalog *before viewing their contents* and downloaded, **23/23** authentic original source bytes with SHA256 digests. These included raw NEBcheck field-star tables, observer notes and numerical AstroImageJ measurement tables. The relevant externally reported aperture/source identifiers were **T6/TIC382437045** and **T11/TIC1884344804**.
- We separately downloaded the exact original full ground AstroImageJ `.tbl` sources for T6 and T11, preserving source SHA256 and original BJD_TDB observations. TOI-1223.01 has **162** source measurement rows, BJD **2460006.973591–2460007.143903**, ground ExoFOP file ID **906268**. TOI-2250.01 has **84** rows, BJD **2459405.710594–2459405.883665**, file ID **222159**.
- The source's actual NEBcheck reports (IDs **906269** and **222160**) were separately SHA256 checked. Their **observer-predicted ingress and egress** were read before flux calculation, with no transit center, aperture selection or event duration optimized on observed flux.

## Numerical reproduction at original fixed observer-predicted eclipse times

| Original source / reported nearby aperture | Observed pre-event rows | Inside rows | Post-event rows | Pre/post averaged baseline dip | Descriptive 5,000 fixed 4-cadence block-bootstrap interval |
|---|---:|---:|---:|---:|---:|
| **TOI-1223.01 / T6** | 46 | 100 | 16 | **39.0304 ppt (3.90%)** | **[32.9558, 43.5608] ppt** |
| **TOI-2250.01 / T11** | 27 | 32 | 25 | **259.7492 ppt (25.97%)** | **[142.6008, 345.1763] ppt** |

The original observer windows were **BJD_TDB 2460007.0212–2460007.1277 (T6)** and **BJD_TDB 2459405.7654–2459405.8325 (T11)**, mapped to the actual observation day using only original timestamps. These are genuine observed ground flux values, not simulated events or NASA model outputs.

Comparison to original observer claims:
- T6's remeasured **39.0 ppt** dip is broadly consistent with the observer's roughly **33 ppt** reported event. The reduction is conditional on the chosen baseline and original measurements.
- T11's remeasured **259.7 ppt** dip is a significant signed decrease and the same order as the observer's reported **350+ ppt** V-shaped event, but **does not numerically reproduce 350+ ppt**; differing detrending, aperture, window and noise properties may contribute and are not independently isolated.
- Both original host **T1** apertures were reported saturated, so their own small mean depths cannot serve as reliable non-eclipse controls. For TOI1223, several other field-star apertures exhibit strong instrumental/background trends; a simple high signed apparent dip in T2/T3 is **not** evidence of an eclipse in those other stars.

## Same-original-source baseline robustness without retuning event timing

A second separate original-file-SHA-locked follow-up recomputed both original midpoint depth measurements numerically, then compared (1) the median measured *pre-event* brightness only, (2) median *post-event* brightness only, and (3) a robust **Theil–Sen baseline trend fitted exclusively to pre/post-event source measurements**, with in-event flux not used to estimate the trend.

| Source aperture | Pre-only dip | Post-only dip | Outside-only Theil–Sen trend-adjusted dip | Consistent positive across all three? |
|---|---:|---:|---:|---|
| **TOI-1223.01 / T6** | **42.45 ppt** | **35.59 ppt** | **34.73 ppt** | **Yes** |
| **TOI-2250.01 / T11** | **296.88 ppt** | **218.48 ppt** | **269.54 ppt** | **Yes** |

The difference between TOI-2250.01 T11's pre-only and post-only estimates is large (**~78.4 ppt**), indicating significant source-level baseline/observational drift. Its sign remains positive, but a confident physical fit would need complete image and ensemble-comparison analysis.

For the same original TOI-1223.01 file, control field-star **T2** has pre-only signed depth **−235.69 ppt** and post-only **+447.63 ppt**, clearly demonstrating severe baseline-dependent instrumental/background effects: interpreting its mean-baseline +236.5 ppt as a unique eclipse is untenable. The reported T6 source aperture is considerably more consistent: its pre/post reference brightness differed by only **~7.1 ppt** of the baseline. These contrasting controls support analyzing the original ground measurements rather than blindly treating a generic false-positive catalog label as source truth.

**Scientific scope:** A measured ground aperture dimming is evidence that the observer-designated T6/T11 apertures contain real flux change under the specified analyses. Independent astrometric confirmation of *aperture T6/T11 → named TIC* using the original plate-solved ground image and original AIJ aperture pixel coordinates remains necessary. Two originally selected physical cases do not allow a star-level performance claim about the earlier five-star TESS correction.

## Preserved original-source and software evidence

- [Five-source original ExoFOP upload lists and ground observing-summary CSVs (all source hashes)](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43330747316/artifacts/13994982126).
- [All 23 original source observer uploads, full SHA256-pinned text NEBcheck/AIJ files](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43331123345/artifacts/13993674982).
- [Original observer notes and SHA-preserved NEBcheck table evidence review](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43331402785/artifacts/13995102484).
- [Original 162-/84-row full numerical T6/T11 AstroImageJ source tables](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43331725492/artifacts/13995556547).
- [Actual ground eclipse fixed original ingress/egress, 333-test successful full-science run and genuine light-curve plots](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43332062967/artifacts/13995865666).
- [Original-source SHA-preserving three-baseline sensitivity, full **336 tests passed**](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43332466646).
- [Numerical original-ground fixed-event analyzer](exofop_two_ground_NEBS_original_AIJ_fixed_window_depth.py), [same-source baseline sensitivity](exofop_two_original_ground_neb_baseline_robustness.py), and [source-locked CI workflow](.github/workflows/exofop-two-ground-source-baseline-sensitivity.yml).

**AI disclosure:** GPT-6 wrote all source retrieval, parser, original-ground source audits, original-image inventory, original same-event quantitative depth calculations, block-bootstrap uncertainty, trend robustness, diagrams, regression tests and this report. Student is responsible for checking original ground fits/tables and telescope systematic limitations, verifying actual spatial aperture-to-TIC mappings and disclosing AI assistance in course work.
