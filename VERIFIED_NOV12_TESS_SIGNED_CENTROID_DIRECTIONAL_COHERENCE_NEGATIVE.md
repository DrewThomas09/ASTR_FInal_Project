# November 12, 2026: Real TESS signed-event centroid direction consistency does not reliably improve

**Result:** Verified original source-aligned exploratory follow-up: source-level directional consistency rose for **23/40** evaluable TESS stars and fell for **17/40** after subtracting the spacecraft pointing estimate. The median paired concentration change was **+0.0011843** (on a bounded 0–1 scale), with whole-star 20,000-replicate bootstrap 95% interval **[-0.009109, +0.050478]** and exploratory exact two-sided star-level sign **p=0.42959**. **No reliable improvement in directional consistency is established.**

## Scientific motivation and physical interpretation

The previous authentic 56-TESS-star experiment found that experimental `MOM_CENTR1/2 - POS_CORR1/2` subtraction often reduces **pre/post-event local centroid motion**, a drift proxy. A distinct concern is whether the corrected coordinates preserve the direction of an **in-event** centroid displacement across repeated observed transits or stellar eclipses. A repeated direction may be astrophysically informative, but it can equally arise from repeatable instrumental systematics; it is not a standalone localization truth criterion.

TESS photometric moment centroid columns `MOM_CENTR1/2` are original CCD image center-of-light coordinates. `POS_CORR1/2` estimate common spacecraft pointing motions. The TESS Data Validation (DV) process additionally uses *difference-image* point-spread-function centroid offsets for testing whether the dimming source is distinct from the target. **Neither our experimental simple subtraction nor repeatability measure is NASA's DV difference-image localization measurement.**

Official methods sources:
- [STScI original SPOC light-curve fields and POS_CORR interpretation](https://spacetelescope.github.io/notebooks/notebooks/MAST/TESS/beginner_tour_lc_tp/beginner_tour_lc_tp.html)
- [NASA TESS Science Data Products Description: DV pixel-level diagnostics and difference-image centroids](https://ntrs.nasa.gov/api/citations/20180007935/downloads/20180007935.pdf)
- [Research on source localization from TESS aperture and light centroid methods](https://doi.org/10.1093/mnras/stad3286)

## Exactly which original data were compared

- **56 distinct** previously inspected authentic NASA/TESS SPOC 2-minute source TIC light curves, using the exact **248** original paired event windows from the source-verified NASA ExoMiner++ v2.4.0 companion analysis.
- Original event identity was independently rechecked against star UID, TIC, sector cohort, original NASA event orbit index and observed predicted epoch.
- Two original 32/24 source-summary SHA256 pins were independently verified. All original *signed x/y* raw and adjusted event displacement norms were recomputed and reconciled to the earlier original 248-event norm-only audit; source file and sign-vector consistency must fail if altered.
- Per source, the signed in-event centroid vector is the observed in-event median minus the average of the pre- and post-event coordinate medians in original TESS detector pixels.
- Only **40/56** sources with at least three complete genuine events were evaluable. The **16** ineligible sources were not counted as improvement/failure. All 40 eligible had valid nonzero vector denominators.
- Every star counts **once**, regardless of how many of the 248 event windows it contributed. This follow-up was selected *after inspecting the older sample* and is expressly post-hoc.

For each source with vectors `v_1,...,v_n`, defined directional concentration:

`R = ||sum_i v_i|| / sum_i ||v_i||`

This is 0 for exactly canceling signed vectors and 1 for perfectly same-direction vectors. The source-paired difference is **R(corrected)-R(raw)** using the same event windows for both. No fitted threshold or external classification labels are used. `R` is a signal repeatability metric, *not* sky localization accuracy or a planet probability.

## Genuine-source results

| Source-level measure | Observed result |
|---|---:|
| Distinct original TESS stars | 56 |
| Original matched event windows | 248 |
| Sources with >=3 original events | 40 |
| Sources with R increase after subtraction | **23** |
| Sources with R decrease | **17** |
| Exact ties | 0 |
| Source-paired median R difference | **+0.0011843145** |
| Whole-star 20,000-bootstrap median R-change 95% interval | **[-0.00910867, +0.05047786]** |
| Exploratory two-sided source-level sign p | **0.42959051** |
| Both R increase and original median in-event shift magnitude decrease | **16** |

**Pre-inspected earlier 32-star cohort:** 23 eligible, **11** R improvements / **12** reductions, median difference **-0.00022013**.

**Previously new-to-project 24-star cohort:** 17 eligible, **12** R improvements / **5** reductions, median difference **+0.01565458**.

These cohorts were historically selected for prior tasks, differ in sample structure, are small, and **are not two prospectively balanced independent astrophysical truth sets**. The contrast across subgroups is exploratory and must not be presented as validated generalization.

## Conclusion and scope

The simple pointing subtraction can produce **smaller pre/post centroid movement** without a demonstrated **more repeatable in-event vector direction**. The bootstrap interval for repeatability crosses zero, and star-level direction signs show no statistically convincing systematic improvement. More fundamentally, even a high direction-concentration score cannot identify a real off-target eclipsing binary absent external source localization. No original NASA neural network weights, inference outputs, transit periods, stellar catalogs, labels or training data were changed.

**Thus the data do not support a claim of better exoplanet classification or better astrophysical source localization.** The next question is independent ground-based target/neighbor source truth, not another post-hoc threshold on these same 56 stars.

## Reproducibility and AI work

- [Successful original NASA/TESS source reanalysis: **270 regression tests passed**](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43301364382)
- [Original signed 248-event vector measurements, per-star tables, uncertainty summary and plot, artifact 13980444834](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43301364382/artifacts/13980444834)
- [Source-normalized executable directional consistency audit](tess_56star_signed_event_coherence_nov12.py)
- [Nine synthetic source-validator regression tests](tests/test_tess_56star_signed_event_coherence.py)
- [Pinned original-source reproducibility workflow](.github/workflows/tess-56star-raw-vs-poscorr-original-events.yml)

**AI assistance:** GPT-6 implemented the signed-source event pairing, source norm and hash validation, unit tests, workflow, whole-star statistics, figure and this methods/interpretation text. The student is responsible for scientifically checking the original FITS, figures, interpretation and final graded writing.
