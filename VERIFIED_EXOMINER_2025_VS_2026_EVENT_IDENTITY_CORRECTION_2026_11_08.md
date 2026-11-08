# Correcting the NASA ExoMiner++ 2025-versus-2026 error comparison: event identity and physical units
**2026-11-08 | Source-verified original-catalog comparison | 224 tests passed**

## Why this correction was necessary

A previous [original unchanged NASA v2.4.0 retrospective error stress test](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42523749559) found that, among **16 historical model errors intentionally selected from the original 2025 ExoMiner++ TESS catalog**, the new 2026 model's binary decisions agreed with the **2025 published class labels** for 7/16 exact original TCE UID strings and disagreed for 9/16. All sixteen were genuinely scored and had original TESS SPOC light curves available, but this was **not** an independent accuracy test. The scientific flaw is that the same named **TCE UID can refer to a different fitted period and/or event order across pipeline versions**. The exact previous 7/9 numbers remain valid as **UID-string/label agreement counts**, not automatically same-physical-signal changes.

The subsequent [five NASA-generated original input diagnostic PDFs](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42524313382/artifacts/13634628262) exposed possible changes in fitted ephemerides. This motivated a separate **post-hoc source-integrity audit**, without changing any NASA weights, scores, original labels, selection or statistical cutoff.

**[Successfully completed original-data identity-audit workflow #42525161027](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42525161027)** · [all sixteen rows, old/new periods/epochs, converted durations and alternate-UID candidates (artifact 13635356093)](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42525161027/artifacts/13635356093) · [reproducible Python code](tess_exominer_cross_version_ephemeris_audit.py) · [source/alias/units tests](tests/test_tess_exominer_cross_version_ephemeris_audit.py).

Original **2025 labeled public source** verified against exact MD5 `c79f3651d556e71f7878a46f960d09b4`, length **8,944,735 bytes**; original **2026 NASA neural scores** downloaded unchanged from the prior genuine 16-error original NASA container artifact. **224 tests passed**. All 16 frozen original UIDs were evaluated and preserved in the output.

## Actual observed version mismatch

| Identity status | Number of original frozen UIDs | Legitimate inference |
|---|---:|---|
| Same UID and original source period within **1%** | **13** | Period-consistent identity, but still not guaranteed identical astrophysical source or physical class |
| Same UID but 2026 period almost exactly **2×** original 2025 period | **1** | A potential period alias; whether the same underlying eclipses were linked must be checked |
| Same UID but different fitted periods | **2** | Cannot assume the same physical signal; one known swapped the order of TCE numbers across releases |
| **All original frozen sources accounted for** | **16** | No post-hoc exclusions or loss of hard failures |

Among the **13 period-consistent source UID records** only, new 2026 scores agreed with original 2025 historical labels for **7** and still disagreed for **6**. The other **3** are identity/alias complications, **not automatically three proven persistent mistakes**. All 16 remain in the original frozen cohort accounting.

### Exact examples from original source rows, not conjecture

**TIC 158623531-1-S3: near-exact 2× period alias.** Original 2025 released `tce_period=7.872776985` d; original 2026 actual inference output `tce_period=15.745845795` d; ratio **2.00003707**; event epoch difference just **0.00024414 d** (~21 seconds). The fitted candidate may trace alternating/missing transit events at twice the period, but whether these reflect the same planet is not established by the ratio alone. Original 2025 KP-class source score **0.307499**, newer v2.4.0 score **0.183578**. Do not claim the newer model rejected the same planet until comparing actual periods/phase and label source.

**TIC 354518617-1-S6: incompatible old/new period and epoch.** Original 2025 period **8.587213516 d**, newer 2026 **9.409090996 d** (ratio **1.09570945**); epochs changed from **1472.356079 BTJD** to **1471.546875 BTJD** (difference **0.8092041 d**). Original NTP-label score **0.62279266**, newer model score **0.943334**. The same raw UID describes **not obviously the same ephemeris**, so a raw score change is not safely attributable to an improved or worse model decision on a single common event.

**TIC 178155732: the original `-1`/`-2` signal ordering swapped.** Original 2025 `178155732-1-S4` had **P=5.971880436d, epoch=1415.634277 BTJD**; new 2026 **`178155732-2-S4`** has **P=5.972267628d, epoch=1415.633911 BTJD**, aligning in period to within **0.0065%** and epoch to **0.0003662d** (~32 seconds). Conversely, original 2025 `178155732-2-S4` had **P=3.586159468d, epoch=1412.774658 BTJD**, while new 2026 **`178155732-1-S4`** has **P=3.586141109d, epoch=1412.774780 BTJD**, aligning to period within **0.0005%** and epoch to **0.0001221d** (~11 seconds). The **old TCE #1** published score **0.100623** and **new TCE #1** score **0.272399** are therefore **not scores for the same fitted candidate period**, despite matching their visible `-1` UID. The 2026 TCE #2 score on old #1's period is **0.016874**. Both source labels are historical CP and neither new TCE has been independently physically validated here.

**DO NOT mix TCE duration units:** `tce_duration` in the original 2025 released labeled NASA-team CSV is stored in **DAYS**, but `tce_duration` in the official 2026 operational model prediction output is **HOURS**. Convert old `tce_duration * 24` before comparing. For example TIC 466840711 original 2025 duration **0.122736d** equals **2.945664h**, matching the 2026 output **2.945664h**, not a 24× event change. The old and current ephemeris periods for this case align; its persistent historical KP-versus-2026 NOT_PC disagreement is a genuine **period-consistent model-versus-label disagreement** deserving independent source-label and contamination review.

## Scientific status and what remains to prove

1. **The 2025/2026 published catalog error comparison is now qualified by actual event identity.** Previous 7/9 counts are correct by UID/label strings; the **more careful period-consistent subset gives 7 resolved, 6 persist, 3 ambiguous or aliased**. The classification of the other three as “not period-consistent” was introduced **after inspecting** the data for scientific correctness, **not** to increase model accuracy. The other 13 can still include false model-label equivalences.
2. The original 2025/2026 neural networks and training populations differ. The current 2026 pretrained model may have seen the 2025 stars, so **no prospective model-accuracy/planet-recovery improvement is established** by this comparison.
3. NASA already has period, transit, pixel and centroid diagnostics. Our source-identity QA is an **improvement to the evaluation and reproducibility protocol**, not evidence that our AI-produced code improves the physical classifier.
4. Next astronomy-grade task: independently match full **period, epoch, duration and source pixel location** to genuine physical transits, cross-check NASA official DV PDF processing versions, and then freeze a **new star-disjoint evaluation** for any instrument/ephemeris-aware modified classifier. Compare at the same empirical false-alarm budget and report host-block uncertainty.

## Original sources / reproducibility

- NASA original published 2025 ExoMiner++ TESS labeled source: https://zenodo.org/records/15466293
- NASA current model code and input documentation: https://github.com/nasa/ExoMiner
- Frozen 16 old-error source manifest: [TESS_16STAR_2025_ERRORS_VS_2026_FROZEN_2026_11_08.json](TESS_16STAR_2025_ERRORS_VS_2026_FROZEN_2026_11_08.json)
- [Original unchanged NASA v2.4.0 model output on 16 historical errors](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42523749559/artifacts/13634607477)
- [All 16 original period/epoch/duration cross-version re-analysis records](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42525161027/artifacts/13635356093)

**AI use:** GPT-6 compared original NASA source schemas/ephemerides, coded QA and tests, executed verification and wrote this note. The student must independently inspect the results and disclose assistance per course requirements.
