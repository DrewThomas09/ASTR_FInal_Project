# Original ExoMiner (2022) paper received; ExoMiner++ (2025) catalogs acquired and audited
**2026-11-08 | Primary artifacts now verified | No neural-network training or independent planet claim**

## What the user actually shared

The received `Valizadegan_2022_ApJ_926_120.pdf` is the **38-page original scientific paper** `ExoMiner: A Highly Accurate and Explainable Deep Learning Classifier That Validates 301 New Exoplanets` (ApJ 926:120, doi:10.3847/1538-4357/ac4399). **It is not a machine-readable catalog**. The original paper's Table 2 (p.15) reports **30,609 Kepler Q1–Q17 DR25 TCEs** in the author's vetted training set: **2,291 PC, 3,538 AFP and 24,779 NTP**. Table 3 and its machine-readable supplement publish original Kepler model scores, not the same 2025 TESS scores examined below. Its method also splits by *target star*, not by individual TCE row (p.15). No part of the original Kepler training tensors has been obtained by simply possessing the PDF.

## Official 2025 ExoMiner++ TESS published source acquisition

We **successfully downloaded two actual original public CSV datasets** from Zenodo version DOI **10.5281/zenodo.15466293**, whose parent concept is **10.5281/zenodo.15466292**, and cryptographically verified each original file against the archive's MD5 and exact byte count:

| Source | File size | MD5 | Verified rows | Columns |
|---|---:|---|---:|---:|
| `exominerplusplus_catalog_labeled_tces_s1-s67_tess-spoc-2min_complete_1-14-2025_1039.csv` | **8,944,735 bytes** | `c79f3651d556e71f7878a46f960d09b4` | **57,162** | 12 |
| `exominerplusplus_catalog_unk_tces_s1-s67_tess-spoc-2min_complete_1-16-2025_1014.csv` | **36,391,080 bytes** | `0bad0922ea704cf429fd69bacb13b0c9` | **147,567** | 16 |

**Actual reproducible original file download:** [successful checksummed GitHub Actions run #42516458999](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42516458999) and [uploaded original two-source artifact #13631476771](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42516458999/artifacts/13631476771).

[Data manifest](EXOMINER_PUBLIC_DATA_MANIFEST_2026_11_08.json) · [reusable downloader](scripts/download_exominer_public_catalogs.py) · [matching official release `nasa/ExoMiner@v1.0.0`](https://github.com/nasa/ExoMiner/releases/tag/v1.0.0).

No purchase or NASA account needed. The separate **18,954,105,376-byte (~19GB)** published TESS TFRecord archive has **not been downloaded** or trained on; its source checksum is pinned in the manifest and it specifically excludes the Kepler component of the 2025 paper's joint TESS+Kepler dataset.

## Verified published score sanity check

The project committed a dedicated [score audit script](exominer_released_score_audit.py), [regression tests](tests/test_exominer_released_score_audit.py) and a [successful full audit, 175 tests passed](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42516833534) that consumes exactly the pinned, independent original NASA-team CSV snapshots from the prior successful download run. [Machine-readable audited outputs, published-score precision/recall figure, subgroup tables and disagreement IDs](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42516833534/artifacts/13631493389).

- Labeled TESS SPOC rows: **57,162 TCE observations**, **17,206 unique TIC host stars**, all ten released `fold` IDs present. **Zero host stars appear in more than one published CV fold**, a good provenance check.
- Positive published categories (KP and CP): **1,835 KP + 1,846 CP = 3,681** (6.44%).
- Negative published categories: **53,481** rows, including **39,009 NTP, 12,738 EB, 816 NEB, 793 FP, 93 NPC and 32 BD**. `FP` and `NEB` are **published TESS subclasses**, do not translate into independent planetary ground truth.
- Using the released `score` values only (without training any model), the global **average precision (sklearn PR-AUC method) = 0.97036** and **ROC AUC = 0.99713**. The study paper's best reported **0.976** PR-AUC used its chosen comparison and aggregation setup. **Do not claim that a naive sum over this CSV exactly reproduces its table.**
- At released score ≥0.5, historical-label **precision = 92.37%**, **recall = 92.69%**; **3,412 TP, 282 FP, 269 FN, 53,199 TN**. At score ≥0.99, historical-label **precision = 98.86%**, **recall = 37.60%**. High published scores are not a guarantee of physical planetary truth outside the catalog's labeled population.
- Released `uid` is unique. However, there are only **26,624 distinct `(target_id,tce_plnt_num)` pairs**; **30,538 additional sector-run rows** repeat the same identifier combination, and **696 such combinations have differing catalog subclass labels** across observing windows. These labels may refer to different period aliases or actual phenomena and require ephemeris matching before treating them as literal contradictions. Rows are **not independent astrophysical objects**.
- The nominal **P≥100 days** subgroup contains **5,380 TCE rows but only 3 KP/CP positive examples**: completely inadequate for a scientifically calibrated long-period planet recall estimate. This is a meaningful population-coverage weakness of the labeled table, not evidence the official model fails to detect long-period planets in the wild.
- The lowest signal-strength subgroup (`tce_max_mult_ev < 10`) contains **423** published positive cases among **9,546** total TCE observations; the published scores at cutoff 0.5 retain **339** positives and miss **84**, with **49** misaccepted published negatives. We should test independent low-significance sources using new TCEs or simulated truth, not tune on the released fold scores.
- Unknown-catalog rows: **147,567** unique TCE IDs from **40,777** unique TIC stars, **7,229** scores ≥0.5 and **1,168** scores ≥0.99, with **11,136** TICs also occurring in the released labeled cohort. This score-only count is not the same selection process as the paper's **7,330 candidate observations**, which may use extra rules or a different cutoff; do not silently equate them.

## Scientific interpretation / next discriminating experiment

This is a **verified reproduction of the released published-score statistics and fold integrity**, not a newly trained ExoMiner model and not a new NASA planetary discovery. The 10 published out-of-fold scores were created by the original authors and the labels are already in the published model-development corpus.

**Highest-priority next contribution:** choose a truly independent, later-sector TESS TCE sample with frozen source selection/labels and run NASA's **actual version-pinned ExoMiner++ pretrained code**, then compare its published score against an event-aware physical feature/companion model (including multiple transits, odd/even uncertainty, persistent SPSD shape, quality flags and off-target pixel centroids) *on exactly identical sources*. The 2022 original paper explicitly discusses original confirmed-planet failures due to missing odd-even transit-depth variance and number of events, although these are **not proven to remain unaddressed in the 2025/2026 model**. Any claim of improvement must be demonstrated by paired holdout PR-AUC or recall at fixed high precision, or a separate upstream injection/recovery benchmark of true planetary signals at fixed false alarms. We should not choose a result by browsing published high-score false positives first and later calling them fresh holdout examples.

**AI assistance:** GPT-6 obtained public data, wrote manifest/code, performed checksum-backed numerical audit, authored this interpretation and coordinated software tests. Student must review and disclose AI use per course requirements.
