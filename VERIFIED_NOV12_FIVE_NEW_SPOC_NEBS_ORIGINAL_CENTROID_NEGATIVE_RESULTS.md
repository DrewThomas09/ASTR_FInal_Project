# November 12, 2026 — Five newly pre-frozen real TESS source hosts do NOT reproduce the single-star pointing-correction alignment gain

**Result:** Exploratory original NASA/TESS SPOC 2-minute source reanalysis of five previously centroid-unseen host TICs and **63 genuinely observed, raw/adjusted same-event windows**, chosen and frozen on source-only criteria *before* their TESS centroid values were inspected. All **five** original light-curve/target-pixel sources were processed, but one had only two complete observed events and did not meet the fixed three-event eligibility rule. The remaining four stars split **2 better / 2 worse** in the alignment of their signed in-event moment centroid vector with the idealized direction **away from** the ExoFOP note-named nearby TIC. Median source-level raw-minus-adjusted angular mismatch was **-6.6477124 degrees** (adjustment slightly worse), with exploratory 20,000 whole-host bootstrap 95% interval **[-47.1639631, +17.9507058] degrees** and exploratory exact two-sided source-level sign **p=1.0**. **No reliable or generalizable physical source-localization improvement is established.**

## Origin of the independent-of-student-centroids cohort

The previous, deliberately selected **TOI-4255.01** example produced encouraging corrected angle *point estimates* in two original TESS sectors, but the paired event-bootstrap uncertainty intervals crossed zero and one quarter-phase control displayed nearly the same angular alignment without a median local brightness dip. We therefore did not retune that target's thresholds or reuse its two sectors as independent stars.

The follow-up began from a checksum-preserved original ExoFOP public TOI catalog and 30 previously inspected public observing-note records. Of 21 note records containing explicitly coded NEB/PNEB photometric dispositions, **19** remained as new TIC source-note leads after previous-system exclusions. An exact TIC/sector original MAST SPOC two-minute **LC and TP FITS product** search identified **10** new source hosts, and a distinct independently requested ExoFOP nearby-star catalog crosscheck identified **five** hosts with one matching named nearby TIC in the relevant notes. The five TIC identities, the **lowest-numbered sector with an original SPOC LC/TP product pair**, external catalog coordinates, original TOI period/epoch/duration, and the original MAST source product URIs were all fixed **before viewing centroid outcomes**. Fixed pre-centroid manifest SHA256: `c5c32ce8d114d3dc37b2cf138061e0810ed057165f9bc25e4ae2bebfe906ea5f`.

**Crucial limitation:** Selecting unseen-to-our-centroid-analysis sources is not the same as a NASA-training-independent or truth-labeled validation set. Ground-based notes may name multiple neighbors or report a candidate previously ruled out. Merely finding an explicitly reported NEB status and a matching astrometric TIC does **not** independently prove that that particular nearby TIC produced the eclipse. No independent ground-based original light curve was reanalyzed to certify the physical label in this five-source run. The results below are **directions relative to catalog-matched note-named neighbors**, not verified true-source location accuracy.

## Original observed TESS source data and descriptive results

Each star contributed only the original complete actual quality-zero SPOC observed event windows at its unchanged publicly archived ExoFOP TOI period, epoch and duration. The original TPF celestial WCS was read from the same sector's verified FITS; no arbitrary pixel-to-sky rotation, synthetic eclipse, period optimization, reselected sector or replacement star was used.

| Original TOI / host TIC | First fixed SPOC sector | Note-named nearby TIC | Matched source event windows | Local positive flux dips | Raw mismatch from predicted away-neighbor direction | Corrected mismatch | Raw minus corrected (positive = better) |
|---|---:|---:|---:|---:|---:|---:|---:|
| TOI-1330.01 / 357457104 | 15 | 1973994316 | **10** | 10 | **46.09°** | **60.54°** | **-14.46°** |
| TOI-1223.01 / 382437043 | 1 | 382437045 | **2** | 2 | 31.71° | 97.41° | **Ineligible: only 2 events** |
| TOI-3712.01 / 354442783 | 59 | 518660670 | **13** | 12 | **165.18°** | **164.02°** | **+1.16°** |
| TOI-2846.01 / 66151343 | 61 | 66151336 | **8** | 7 | **4.49°** | **51.65°** | **-47.16°** |
| TOI-2250.01 / 264303333 | 14 | 1884344804 | **30** | 20 | **50.32°** | **32.37°** | **+17.95°** |

**Sample denominators:** 5 physically different host TICs attempted, 5 processed using source-original SPOC LC/TP FITS; **63 total complete same-event raw/corrected observation windows**; **4** host TICs evaluable with three or more complete windows, comprising **61** observed windows; 1 host (TOI-1223.01) remains *inconclusive*, not counted as a negative or a successful correction. These are **four independent host units**, not 61 independent stars.

Other striking limitations:
- **TOI-1330.01:** raw-to-adjusted local before/after centroid motion proxy dropped from **0.001744** to **0.000478 pixels**, but the source alignment angle **worsened** from 46.09° to 60.54°. A cleaner instrument drift proxy is not necessarily better physical direction.
- **TOI-2846.01:** the original centroid already pointed within **4.49°** of the note-named neighbor's expected opposite direction; subtracting POS_CORR moved it to **51.65°**, and the local pre/post drift proxy also grew from **0.001735** to **0.005934 pixels**.
- **TOI-3712.01:** the nominal angular improvement is barely 1.16° and both raw and adjusted measurements remain over **164° away from the predicted direction**. Reporting that as a meaningful localization success would be misleading.
- **TOI-2250.01:** adjusted angle improved by 17.95°, but only **20 of 30** original measured windows had locally positive PDCSAP flux depth and the median flux dip was **0.00009866** of baseline (~0.0099%). This is an uncertain astrophysical association, not a confirmed eclipse localization.

## Source-level statistical result (not a mission-validation estimate)

Across the four eligible host stars:
- **2/4** had a smaller angular mismatch after correction, **2/4** had a larger mismatch.
- The **median of four paired host angular differences** (raw mismatch minus corrected mismatch) was **-6.6477124°**.
- The *exploratory* whole-host 20,000-bootstrap interval for that median was **[-47.1639631°, +17.9507058°]**, including zero.
- The exploratory exact two-sided sign-test **p = 1.0**, providing no evidence of a systematic directional gain.
- No regression over all 63 individual event windows may be interpreted as though those were independent target stars.
- Two fixed ±P/4 phase control windows per star were also measured and archived using the same original FITS. They are not guaranteed astrophysically blank controls; no post-hoc best control was used to select these five hosts.

The study **does not establish that the proposed pointing correction improves identification of real off-target eclipsing sources**, and even these directional outcomes are relative to *reported* rather than independently reverified eclipsing-neighbor locations. This experiment does not alter, retrain, improve or evaluate the full NASA pretrained ExoMiner++ classifier's independent astrophysical accuracy.

## What this adds scientifically

This is an important replication outcome: once source selection is frozen relative to the new centroid values, a visually interesting result from one previously inspected star **fails to show consistent improvement across newly examined, physically distinct stars**. The explanation could include inaccurate/ambiguous source-note identity, original TOI ephemeris aliases, weak transits, aperture blending, sector pointing behavior, and the weakness of the elementary moment-centroid subtraction compared with mission-grade difference-image analysis. The data do not isolate which mechanism dominates, so those explanations should be presented as possibilities, not discovered causes.

Next genuine progress depends on separately validating ground-based light-curve source identity for each neighbor and building an appropriate **on-target truth-labeled control**; selecting more stars purely by the observed centroid alignment would introduce outcome-based bias.

## Reproducibility and retained limitations

- [Successful original five-TIC SPOC LC/TP WCS scientific workflow: **317 tests passed**](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43319506539).
- [Original source-file SHA256 evidence, 63 measured event records, per-TIC descriptive controls, source-level statistics and figure](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43319506539/artifacts/13988829809).
- [New five-source cohort methodology and exact source-selection restrictions](VERIFIED_NOV12_FIVE_NEW_SPOC_NEBS_CENTROID_BLIND_SOURCE_COHORT.md).
- [Successful source-freeze workflow and exact source-manifest SHA proof](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43319246311/artifacts/13988614232).
- [Original science execution](tess_five_new_neb_original_source_centroid_experiment.py), [source-level test controls](tests/test_tess_five_new_neb_original_source_centroid_experiment.py), and [independent-source workflow](.github/workflows/tess-five-new-neb-original-centroids.yml).
- [Earlier one-star original real-event and negative phase-control study](VERIFIED_NOV12_TOI4255_REAL_TESS_SPOC_OFFTARGET_VECTOR_AND_QUARTER_PHASE_CONTROLS.md).

**AI use disclosure:** GPT-6 assisted with ExoFOP source parsing, original MAST source verification, algorithm implementation, tests, star-level statistical analysis, figure generation and this report. The student should inspect the source data and final astronomy conclusions and comply with the course's AI-disclosure requirements.
