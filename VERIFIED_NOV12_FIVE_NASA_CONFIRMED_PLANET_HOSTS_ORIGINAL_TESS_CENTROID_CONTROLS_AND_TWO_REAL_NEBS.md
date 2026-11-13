# November 12, 2026: five new independently catalogued confirmed-planet hosts, original SPOC centroid control experiment

**Main result:** We selected and froze **five completely separate, previously centroid-unseen transiting exoplanet host TICs** by requiring original ExoFOP "KP" *and* the separate NASA Exoplanet Archive `pscomppars` confirmed transiting-planet status with an exact TIC and consistent period, before looking at any of their TESS centroid values. All five had genuine original SPOC two-minute target light-curve and target-pixel products at their **preselected earliest available sectors**. Using unchanged original published periods, epochs and durations, the source-exact science pipeline recovered **46 complete raw/corrected same-orbit observed transit windows**, all **46 with positive median local PDCSAP transit depth**, plus **two fixed ±P/4 pseudo-event controls per host**.

Across **five independent host TICs** the exploratory correction `MOM_CENTR - POS_CORR` reduced **median in-transit centroid-vector amplitude in all five**, median source-level reduction **+0.00020326 TESS detector pixels** (positive = reduced). However, the exact two-sided source-level sign-test was **p=0.0625**, and reduction of an astrophysical centroid amplitude is **not automatically better source localization**, planet/false-positive discrimination or NASA classification. Local pre/post centroid drift was reduced in **four of five** (exploratory sign p **0.375**) and **increased substantially in CoRoT-1 b**, demonstrating this is not universally improved instrument stability.

## Source selection was frozen BEFORE the five target moment centroids

The original official source-only [GitHub Actions run 43346848609](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43346848609) obtained the NASA Archive original `pscomppars` source (SHA256 `22be1dc766df9abe4f40c0e821bd87ce24ec4e60f4ac27283f98ae65f9c6d2d0`) and the unchanged 8,175-row ExoFOP TOI snapshot (SHA256 `5b54c8a9a74593dec8380fa2db3d9c5bc1757f0da4842c42a47a2dde81`). It found **443** independently catalog-concordant, unique eligible TICs after period and prior-source exclusions, then selected exactly five by a prespecified SHA256 order; only **five** original MAST source availability queries were needed and all five had genuine SPOC 2-minute LC/TP FITS product pairs. No `MOM_CENTR`, `POS_CORR` or mission model output was opened in source selection. The [complete original source-frozen JSON, catalog CSV and URI records](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43346848609/artifacts/14001463866) were archived **before the actual science data workflow**.

| NASA independently confirmed planet | Host TIC | Original ExoFOP TOI | Frozen first SPOC 2-min sector | Actual genuine paired transits |
|---|---:|---:|---:|---:|
| **KELT-14 b** | 134537478 | 501.01 | 7 | **13** |
| **CoRoT-1 b** | 36352297 | 547.01 | 6 | **13** |
| **WASP-168 b** | 232038798 | 1909.01 | 32 | **5** |
| **HAT-P-30 b** | 455135327 | 490.01 | 7 | **7** |
| **WASP-82 b** | 452808876 | 453.01 | 5 | **8** |
| **Total: 5 independent hosts** | | | | **46 original real events** |

No duplicates of any of the prior 56 original TESS TICs, the earlier tutorial pilot, the two previously inspected ExoFOP source-note cases, or the five candidate neighboring-eclipse hosts were selected. These planet classifications **are not newly demonstrated by this project**, and NASA Exoplanet Archive classification does not prove independence from NASA ExoMiner++ training data or an independent original high-resolution ground-on-target source-label audit.

## Original event centroid measurements per independent host

The source analysis downloaded and checked original NASA SPOC FITS per host/sector, obtained original 2D `MOM_CENTR1/2` and `POS_CORR1/2`, actual `PDCSAP_FLUX`, true quality-zero timestamps and the original sector-specific target-pixel WCS. It measured exactly the same real source transit windows in raw and exploratory pointing-corrected modes, with no post-hoc event-epoch shift or changed observation sector. Observed NASA host catalog positions were consistent with original target header positions to **better than 0.46 arcseconds** for all five stars.

| Confirmed planet | Real transits | Original raw median in-event centroid norm (pixels) | After experimental POS_CORR subtraction | Raw-minus-corrected improvement (pixels) | Original raw median local pre/post drift → corrected |
|---|---:|---:|---:|---:|---|
| **KELT-14 b** | 13 | 0.00045674 | 0.00027227 | **+0.00018447** | 0.0022632 → 0.0003742 |
| **CoRoT-1 b** | 13 | 0.00159822 | 0.00129164 | **+0.00030658** | **0.0007182 → 0.0035468 (worse)** |
| **WASP-168 b** | 5 | 0.00067585 | 0.00031058 | **+0.00036526** | 0.0012629 → 0.0011726 |
| **HAT-P-30 b** | 7 | 0.00030264 | 0.00028616 | **+0.00001648** | 0.0042712 → 0.0010625 |
| **WASP-82 b** | 8 | 0.00035727 | 0.00015400 | **+0.00020326** | 0.0069866 → 0.0015682 |

**Strong caution:** The amplitude of a real in-transit moment centroid displacement need not vanish for a genuine planet **on the target star**. When the target fades and an unresolved constant neighbor does not, the flux-weighted centroid can move **toward** the neighbor; ground-positive confirmed planets thus do not constitute "zero displacement" controls. Reducing the genuine event's centroid vector can also erase valid source-localizing physical information.

### Independent host-level descriptive inference, not transit pseudoreplication

- **In-event norm raw minus corrected:** decreased in **5/5 independent hosts**, median host reduction **0.00020326 pixels**; exploratory 20,000-host-resample bootstrap median interval **[0.00001648, 0.00036526] pixels**, exact two-sided sign test **p = 0.0625**. These are small host counts; the bootstrap sign homogeneity is not evidence of classifier improvement.
- **Local before/after source drift raw minus corrected:** decreased in **4/5**, median host reduction **0.00188898 pixels**, exploratory bootstrap median interval **[−0.00282857, +0.00541840] pixels**, two-sided host sign **p = 0.375**. **CoRoT-1 b worsened:** original raw drift **0.0007182** vs corrected **0.0035468** pixels, which alone rules out universal instrument improvement.
- **Original actual event centroid norm excess over the two fixed ±P/4 pseudo-event windows:** raw-minus-corrected excess decreased in **4/5** hosts, median **+0.00009626 pixels**, exploratory bootstrap median interval **[−0.00019707, +0.00063064] pixels**, sign **p = 0.375**. The adjusted HAT-P-30 b showed an **increased event-specific centroid excess** (raw true-minus-controls **−0.00010946 pixels**, adjusted **+0.00008761 pixels**) despite its small reduction in raw event-vector norm. That can have ambiguous astrophysical interpretation.

All **5/5** were eligible for the predeclared minimum **≥3 real complete transit windows AND ≥3 in each shifted ±P/4 source control**. The unit of statistical analysis was a **host TIC**; the 46 distinct temporal windows are repeated observations within five hosts, not 46 independent stars.

## Physically supported nearby binary source counterexamples, reported separately

A separate source-exact reanalysis [run 43347269538](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43347269538) used the **already archived original five candidate NEB TESS source centroids** and original ground WCS/AIJ observations for TOI-1223.01 and TOI-2250.01. It projected the *signed* original TESS vector along the expected direction **away from** the eclipsing neighbor and compared the actual original event with the two unchanged ±P/4 phase controls.

- **TOI-2250.01 / ground T11/TIC1884344804**: 30 first-sector genuine TESS windows. Original raw actual-minus-shifted-control signed away-neighbor excess was **−0.00011171 pixels**, while experimentally adjusted excess was **+0.00024155 pixels**, an apparent **+0.00035326-pixel physical signed projection gain**. The corrected actual median direction also improved from **50.32° raw** to **32.37°**, though this is only one previously inspected source, not a blind cross-star replication.
- **TOI-1223.01 / ground T6/TIC382437045**: only **2** genuine first-sector event windows, **ineligible** under the prior three-event source rule. Its raw signed actual-minus-control excess **+0.00016889 pixels** worsened to corrected **−0.00012577**, an apparent **−0.00029466-pixel** physical projection change, described only as exploratory because the event sample is too small.

These two physical-source cases were already selected based on ground observer data, and no new stars or sectors were chosen after seeing the outcomes. The opposite direction of change underlines the risk of generalizing one visually appealing source result.

## Source records, reproducibility and scientific limits

- [Independent catalog and first-sector source lock protocol](FROZEN_NOV12_NASA_KP_FIVE_CONFIRMED_TRANSITING_PLANET_ON_TARGET_SOURCE_CONTROL_PROTOCOL.md)
- [Completed full original five confirmed-planet scientific run **351 tests passed**](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43347225538)
- [Original MAST 5-host LC/TP source hashes, **46 actual transit vectors**, 10 original fixed phase-control windows and plot](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43347225538/artifacts/14001678743)
- [Original two physically ground-supported neighbors' signed true-versus-quarter-phase controls, same 351-test source audit](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43347269538/artifacts/14001169022)
- [Main source-locked confirmed planet experiment code](tess_five_nasa_KP_confirmed_ontarget_original_SPOC_centroid_controls.py), [tests](tests/test_tess_five_nasa_KP_confirmed_ontarget_original_SPOC_centroid_controls.py) and [repeatable workflow](.github/workflows/tess-five-NASA-KP-confirmed-ontarget-original-centroids.yml)

**Conclusions must remain narrow:** The exploratory pointing subtraction alters authentic original TESS centroid and local noise metrics. It was not uniformly beneficial to local stability, and reduced amplitude is not proof of improved classification. No original NASA ExoMiner++ neural weights, pretrained scores, official mission source localizations, or planet labels were changed, and no genuinely independent ground-confirmed ON-target source images were reanalyzed to validate this on-target control cohort.

**Course AI disclosure:** GPT-6 wrote independent official NASA/ExoFOP catalog matching, source selection and freezing, MAST data retrieval, original real-event and quarter-phase control metrics, plots, statistical controls, report and tests. The student should personally inspect original source scientific records and interpretation before submitting.
