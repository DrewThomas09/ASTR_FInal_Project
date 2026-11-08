**Same-source TESS physics integration is now complete:** [NASA pretrained v2.4.0 plus independently coded original-TESS event measurements](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519715623) ([complete original source + inference and sidecar artifact](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519715623/artifacts/13633161147)). For original SPOC `167526485-1-S6` source FITS SHA256 `41365d738d2a872378a12a4d49068ccdf317710fd04179d6aa8542b4e66f3078`, **14,592** quality-zero cadences, our event-sidecar finds **four** real ~1.14–1.24% flux dips and median before/after recovery ratio **0.04039**, while the **unchanged** NASA pretrained planet-validation result is score **0.020304145, NOT_PC**. The two odd/two even events are explicitly insufficient for an interval; no planetary mechanism or NASA improvement was proven. See [complete technical result](EXOMINER_VERIFIED_OFFICIAL_INFERENCE_AND_TESS_MODEL_DEVELOPMENT_2026_11_08.md).

## November 8: Full official NASA pretrained inference now succeeded; real TESS model ablation completed

**[Audited scientific writeup with raw NASA source IDs, limits, exact scores, empirical uncertainty](EXOMINER_VERIFIED_OFFICIAL_INFERENCE_AND_TESS_MODEL_DEVELOPMENT_2026_11_08.md)** and [continuing first-person course report](FINAL_REPORT_OPENING_HISTORY_FLUX_EXOMINER_AND_AI_REPLICATION_DRAFT.md).

**Authentic NASA ExoMiner++ software was actually run** in [successful official TESS pretrained inference](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519263267), with [official original score, source-tracking CSV, model digest and logs](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519263267/artifacts/13632672462): ExoMiner **v2.4.0**, NASA Git commit **59d3f43**, container `sha256:1b7ffac9db8afe1787ec9a0464ed8cc16ab91b7a280e6e824c27e3a121b0c6e9`. NASA documentation target **TIC 167526485, Sector 6**, one official original TESS TCE `167526485-1-S6`: original period **5.01159 d**, duration **6.96083 h**, official planet-validation neural score **0.020304145**, disposition **NOT_PC**. This is **one pretrained pipeline execution**, no original neural-net retraining, no new planet or population performance claim. The first pilot failed because the NASA code rewrote an input mounted read-only; fixed by mounting a writable copy.

In a separate [**193-test** original source NASA 2025 TESS real-data RF ablation](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519431316) ([all 57,162 new fold-heldout predictions, curves, cluster CI](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519431316/artifacts/13633080778)), our new four-feature scalar RF had AP **0.62114**, versus **0.64456** when adding transit duty cycle and Gaia RUWE; **prespecified ΔAP=+0.02341 with host-block 95% CI [-0.01101,+0.05375]**, so not a resolved significant gain. At threshold 0.5, both precision and recall **worsened**. Published ExoMiner++ 2025 model historical-score AP **0.97036** is the original NASA-team **released score**, not a score we trained its CNN to obtain. The feature choice and ten identical **star-disjoint** folds were frozen prior to training, and RUWE is already used by NASA's contemporary ExoMiner so this is not an original scientific innovation.

Also [**185-test** verified real Kepler Q6+Q7 event-recovery development](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519123518) ([original MAST source FITS digests and four observed event tables](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519123518/artifacts/13633010940)) studied pre/during/post brightness and odd/even event depths for known planet-host Kepler-12 and eclipsing binary Kepler-35. Every individual-event odd/even bootstrap interval crossed zero, despite visually striking prior folded binary patterns. This **negative/inconclusive outcome is preserved**. New [same-TESS-source recovery companion](tess_official_event_recovery_companion.py) is a *post-hoc descriptive sidecar*, not altered NASA model weights or demonstrated improved classification.

## Final report introduction: history of calibration, transit photometry and ExoMiner replication

**[Read/edit the full student-voice opening report draft](FINAL_REPORT_OPENING_HISTORY_FLUX_EXOMINER_AND_AI_REPLICATION_DRAFT.md).** Connects course Lesson 2 (flux versus luminosity and inverse-square law), Lesson 3 (timing), Lessons 5–6 (orbital physics), and Lesson 7 (light) to the history of exoplanet discovery, transit depth, Kepler/TESS methods and ExoMiner's multi-view neural vetting. Explains original MAST and Exoplanet Archive sources, the actual Zenodo 57,162 labeled/147,567 unlabeled TESS records, the still-undownloaded ~19 GB training archive, and **what is genuinely replicated versus still planned**. The text acknowledges the AI-assisted code/data work and does not claim the current prototype outperforms NASA.

# AI-assisted exoplanet detection | ASTR 12600

## November 8: Actual official ExoMiner++ TESS catalogs now acquired and reproducibly audited

**[Original NASA ExoMiner paper vs actual ExoMiner++ catalog distinction, all verified observed results](VERIFIED_EXOMINER_PUBLIC_CATALOGS_AND_RELEASED_SCORE_AUDIT_2026_11_08.md)**. The user-provided `Valizadegan_2022_ApJ_926_120.pdf` is the **2022 original 30,609-Kepler-TCE research paper**, not a CSV. The **2025 TESS ExoMiner++** source is a separate Zenodo dataset version [15466293](https://zenodo.org/records/15466293): **57,162 labeled TCE observations (17,206 distinct stars, 3,681 published KP/CP positives)** plus **147,567 unknown-label TCE observations (40,777 stars)**. Both ORIGINAL released CSVs were **actually downloaded and MD5/size verified** in [successful source-acquisition workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42516458999) and [archived original source files](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42516458999/artifacts/13631476771). [Source-locking manifest](EXOMINER_PUBLIC_DATA_MANIFEST_2026_11_08.json), [reusable original NASA CSV downloader](scripts/download_exominer_public_catalogs.py).

An [independent *released-score-only* audit](exominer_released_score_audit.py) of the same published historical scores [passed **175** full project tests](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42516833534) and [archived all real source-backed metrics, precision/recall figure and hard error IDs](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42516833534/artifacts/13631493389). **Released-score descriptive PR-AUC=0.97036, ROC-AUC=0.99713**, precision **92.37%** and recall **92.69%** at score ≥0.5; **no original model was trained and no independent discovery or population sensitivity was measured.** Exactly **zero** stars cross the published 10 CV folds, but many TCE rows repeat the same host/planet number across sector observations. Critically, **only three KP/CP positive rows have P≥100 days**, so do not claim this TESS score catalog independently establishes long-period planet sensitivity. The separate ~**18.95 GB** Zenodo TESS TFRecord training archive is **not yet downloaded**. Original 2025 TESS code release is [NASA v1.0.0](https://github.com/nasa/ExoMiner/releases/tag/v1.0.0); original 2022 Kepler paper and 2026 operational model are **different version/data tasks**.

## November 8: ExoMiner++ full-model audit and actual replication plan

**[Full source-grounded ExoMiner/ExoMiner++ audit and NASA model replication roadmap](EXOMINER_FULL_TECHNICAL_AUDIT_AND_REPLICATION_PLAN_2026_11_08.md)**. Original ExoMiner statistically validated **301** existing Kepler planetary candidates (later +69 by multiplicity boost). The 2025 TESS 2-minute ExoMiner++ study achieved **0.976 PR-AUC** on its labeled, aggregated, multi-source benchmark and identified **7,330 previously unlabeled TCE observations as potential planet candidates**, NOT confirmed planets. The 2026 ExoMiner++ 2.0 extends vetting to full-frame image TCEs, where its paper reports ~**0.952 PR-AUC**. The June 2026 operational v2.1 model spec describes **~1.424M trainable parameters** in a single model, separate planet-validation and 3-way photometric-vetting tasks, and global/local/unfolded/odd-even/secondary/centroid/pixel/periodogram/stellar-DV inputs. **The published metrics cannot be directly compared numerically to our four-feature Kepler DR25 forest** because source missions, TCE selection, label truth, and training/test protocols differ.

**Actual ASTR work begun:** [original Kepler ExoMiner-*inspired* multi-view diagnostic generator](exominer_inspired_kepler_views.py), [offline integrity tests](tests/test_exominer_inspired_kepler_views.py), and [Kepler-12 and Kepler-35 original FITS engineering workflow](.github/workflows/exominer-inspired-view-demo.yml). The prototype builds 301-bin global, 31-bin local/odd/even/secondary, and 20×31 individual-event views **with explicit missing-data masks**, but **does not use NASA's exact preprocessing or official CNN weights** and should never be presented as NASA ExoMiner inference. For genuine **official pretrained TESS model reproduction**, see the [Podman single-source launcher](scripts/run_official_exominer_pilot.sh) and [TESS TIC/sector example](exominer_official_pilot_tic_sector.csv), both modeled on [NASA's published run instructions](https://github.com/nasa/ExoMiner/blob/main/docs/running-exominer-pipeline.md); the official container has **NOT yet been run or validated** in this project.

**Verified original Kepler input demonstration:** [complete source-backed views and physical explanation](VERIFIED_EXOMINER_INSPIRED_REAL_FLUX_VIEWS_2026_11_08.md) · [successful 171-test workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42515740272) · [archived real NASA view arrays with missing-data masks and figures](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42515740272/artifacts/13631128224). Our 301-bin/global, 31-bin local/odd/even/secondary and 20×31 independent event views were produced from genuine Kepler-12 and Kepler-35 Q6 data. The **largest observed odd-even profile difference was 0.087% for Kepler-12 versus 33.27% for Kepler-35**, whose fitted 10.3713-day period is a **half-period alias of its approximately 20.734-day stellar binary orbit**. This is a strong illustrative *already-known system* showing the utility of NASA's existing odd/even features; it is **not a trained ExoMiner, independently confirmed new accuracy or a novel instrument classifier**.

**Recommended research improvement:** a reversible, physical event-consistency/instrument-damage diagnostic that contributes to genuine ExoMiner++ candidate vetting and is **ablation-tested against NASA's already present unfolded-flux, pixel contamination and momentum/periodogram branches**, and independently tested *upstream* for improved **real injected-planet detection at the same calibrated false-alarm budget**. Our current RF statistical significance is historical NASA label agreement, not a head-to-head with the NASA system.

## November 8: Stronger statistical accuracy tests — significant historical labels, NOT exoplanet discovery

**[Complete statistically tested NASA DR25 classification results](VERIFIED_DR25_PAIRED_SIGNIFICANCE_2026_11_08.md)** · [successful original-data 135-test workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42513638366) · [source-hash-verified 1,619 paired scores and 10 star-group split experiments](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42513638366/artifacts/13630680897) · [preregistered analysis design](DR25_STATISTICAL_VALIDATION_FROZEN_2026_11_08.json).

On the **same original NASA DR25 catalog** of 8,054 historical-labeled KOIs from 6,923 stars, using one heldout grouped-by-star test of 1,619 signals from **1,385 unique hosts**, the four-feature random forest achieved **81.29% balanced accuracy**, a conventional four-feature logistic model **76.61%**, and a simple validation-recall-calibrated SNR score **50.23%**. Forest minus SNR balanced accuracy was **+31.06 percentage points**, host-clustered 95% CI **[+28.69,+33.43] pp**, two-sided 20,000-host-swap permutation **p≈0.00005**. Forest minus logistic was **+4.68 pp**, 95% CI **[+2.28,+6.92] pp**, *exploratory* paired host permutation **p≈0.00010** from a [separate original-score, 149-test audit](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42514137142). The forest improved label screening primarily by **rejecting many more historical false-positive labels**; it also missed **32 more historically labeled candidates than SNR alone** and **19 more than logistic**. All ten grouped-host source splits showed a forest balanced-accuracy advantage over both baselines, but these overlapping splits are **not independent trials**.

**[New period-aware threshold attempt: verified negative result](VERIFIED_DR25_PERIOD_AWARE_THRESHOLD_NEGATIVE_2026_11_08.md)** · [144-test NASA validation workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42514013228) · [archived all ten NEW split decisions and sample sizes](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42514013228/artifacts/13630652118). A separate validation-only threshold by period bins rescued **15 more historical long-period candidate labels (42/58 → 57/58)**, but wrongly accepted **36 more long-period false-positive labels (28/87 → 64/87)**, reducing primary long-period balanced accuracy **70.11% → 62.36%** (paired host p **0.134**, not significant). It decreased overall balanced accuracy on **every one of 10 new grouped-host splits**. This policy is **not an improvement** and should not replace the original forest.

**Scientific integrity:** These p-values quantify agreement with **NASA's previous Robovetter CANDIDATE / FALSE POSITIVE labels**, not measured recovery or confirmation of real exoplanets, and the original DR25 source/split were previously explored. The independent physical eclipse-preservation guard has **only two externally explained protected binary warnings and no independent true SPSD-positive source**, so **no statistically significant physical detector improvement** has been demonstrated. See [the event-level power and source plan](PHYSICAL_GUARD_ACCURACY_SIGNIFICANCE_AND_POWER_PLAN_2026_11_08.md).

## November 8: Paired statistical validity audit of the frozen study

[New paired analysis and interpretation](PAIRED_VALIDITY_AUDIT_2026_11_08.md) · [reproducible analysis code](paired_validity_audit.py) · [regression tests](tests/test_paired_validity_audit.py) · [hash-verified audit workflow](.github/workflows/paired-validity-audit.yml).

Reanalyzing the **original archived case-level results without changing the frozen detector**, the local step method yielded exactly one extra recovery among 36 matched injections in each condition. Both conditions had zero baseline-only cases and one local-only case (**exact two-sided discordance p = 1.00** each). On constructed defective proxy nulls, standard BLS flagged 13/24 and local step 10/24, with three baseline-only discordances (**p = 0.25**). These exploratory exact tests do not establish population significance because only six independent stars contributed repeated cases. On real-no-artifact photometry, all light curves were unchanged and the apparent extra recovery vanished under the baseline numerical score threshold. In the synthetic defect condition, eight genuine transit cadences were deleted from **one** KIC 9002278 injection. This is a statistical and reproducibility extension, **not** a new astronomical experiment, a true survey FAP comparison, or proof of superiority.

## November 8: Fresh, prospectively frozen *real* instrumental-defect study

[Precommitted 12-star Quarter 6 cohort and frozen rules](REAL_SPSD_EXTERNAL_COHORT_FROZEN_2026_11_08.json) · [exact reproducible instrument experiment](real_spsd_external_cohort.py) · [full analysis methods and caveats](REAL_SPSD_EXTERNAL_COHORT_METHODS.md) · [automated GitHub Action](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/workflows/real-spsd-external-cohort.yml).

This experiment applies the unchanged November 7 local-step detector to **both original SAP_FLUX and NASA PDC-corrected PDCSAP_FLUX at the same timestamps** for twelve *preselected* Kepler Quarter 6 stars. The known favorable teaching example KIC 7461601 is explicitly **excluded**. Only after detection does the experiment match candidate step onsets to original FITS bit-1024 SPSD archival event markers; all star download failures remain reported. Every source FITS SHA-256, matched event, unmatched warning and limitation is retained. **The original NASA run subsequently completed; see the verified negative outcome in the next section**; no unflagged warning is presumed a genuine false positive, and there is no new planet detection claim.

## November 8 verified: New real-Q6 source audit and binary eclipse contamination

**[Full, source-verified Kepler Quarter 6 negative observational result](VERIFIED_REAL_SPSD_EXTERNAL_Q6_RESULTS_2026_11_08.md)** · [original independent study run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42510882421), 96 regression tests passing. In the preselected twelve-star Quarter 6 SAP-versus-PDCSAP cohort, **ten real MAST star files were usable**, but **none** contained an archival SPSD quality-bit-1024 event. The original detector generated six original-SAP and seven PDC-corrected warnings; **without archived positive events, sensitivity to real SPSDs cannot be measured here**, and the warnings are not proven false alarms. Keep the two unavailable stars in the source denominator.

**[Full Kepler-47 physically grounded, POST-HOC eclipse analysis](VERIFIED_KEPLER47_ECLIPSE_CHECK_2026_11_08.md)** · [successful original-artifact and 104-test GitHub run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42511250474) · [saved original numerical table and plot](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42511250474/artifacts/13629303214). Seven distinct warning times were on KIC 10020423, an eclipsing binary: five within 0.1 d of Orosz et al. (2019) published *stellar* eclipse predictions, six within 0.3 d. Holding the seven event spacings fixed, 425/20,000 phase offsets gave at least five matches within 0.1 d; 1498/20,000 gave six within 0.3 d. These conditional phase shifts **are not confirmatory p-values**, because the star and matching windows were examined after the initial cohort output. This observation motivates periodic-event safeguards and tests on future untouched binary and authentic instrument-defect samples, not new discovery claims.

### Original Kepler-47 light curves: physical confirmation of repeating eclipses

[Verified observational figure and explanation](KEPLER47_ORIGINAL_FLUX_VISUAL_CHECK_2026_11_08.md) · [successful Kepler 47 phase-fold workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42511647491) (**109 passing regression tests**) · [two original-photometry graphs and numerical outputs](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42511647491/artifacts/13629373540).

Using the **same hash-verified NASA Kepler-47 Q6 FITS** with 4,272 aligned flux observations, the new diagnostic folds both original SAP and NASA PDC-corrected PDCSAP at the published **7.44837568-day stellar binary period**. The two products both clearly display deep primary and shallower secondary eclipses. Each of the **first three warning-centered observational windows** contains a brightness decline close to the independently published secondary eclipse center; no times or warning thresholds were changed. This is a useful **post-hoc visual mechanism illustration**, not proof of a general independent instrument classifier or new exoplanet.

## November 8: Fresh 13-star periodic-eclipse safeguard and real-instrument safety check

**[Read the complete verified observational report](VERIFIED_RECURRENCE_GUARD_Q6_RESULTS_2026_11_08.md)** · [successful complete independent NASA workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42512273665) · [archived original source hashes, per-warning CSV and chart](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42512273665/artifacts/13629589069) · [frozen prospective manifest](RECURRENCE_GUARD_Q6_FROZEN_2026_11_08.json) · [reproducible new source code](recurrence_guard_q6.py).

A minimally changed *preservation safeguard*, operating only on the flux and time before consulting published source labels, searches for repeated locally recovering eclipse-like dips and prevents the destructive original step mask from deleting them. On **13 newly preselected independent Q6 Kepler stars** (eight published eclipsing binaries, five transiting planet hosts), all 13 source FITS were obtained, **10 original step warnings** arose (4 SAP, 6 PDCSAP), **two** were protected by recurrence, and **42 measurement cadences** were retained rather than masked. The protected cases were independent known binaries **Kepler-1647 (11.24-d detected vs 11.259-d published binary period, seven matching additional cycles)** and **Kepler-35 (10.38-d near *half* the 20.734-d published binary period, six matching additional cycles)**. This is a limited real-observation preservation result, not a planet discovery or quantified increase in planetary detection.

**The negative result must remain visible:** Kepler-34 produced **six original method-level warnings at three unique epochs** separated by ~27.79 days, close to its published 27.80-d binary period; the guard protected **none**, because its range was frozen at 2.5–22 days. One Kepler-16 warning and another Kepler-35 warning also remained unprotected. No source contained the archived positive bit-1024 SPSD event, so independent **real-instrument sensitivity remains unmeasurable** in this holdout.

**[Previously known genuine instrumental dropout safety workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42512522992)** on KIC 7461601 reused the unchanged guard: the original SAP detector flagged the known real dropout, the guard did **not** protect it as periodic, and the original **21 excluded cadences** remained excluded. This is a helpful previously examined **development control**, not additional independent validation. An initial run had three false source-error reports due a software-mask assertion checking the wrong set of indices; this was corrected without touching the science settings, a regression was added, and the full corrected 13-source run is the authoritative outcome.

### Verification beyond matching periods: two genuine published stellar eclipse images

[**Two original Kepler eclipse source plots and independent timing report**](VERIFIED_RECURRENCE_PROTECTED_STELLAR_ECLIPSES_2026_11_08.md) · [successful NASA/source/125-test Action](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42512589511) · [original 2-panel figure and per-event CSV](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42512589511/artifacts/13630380481).

The Kepler-1647 SAP warning occurred **3.468 hours before an independently published secondary stellar eclipse**, and the Kepler-35 PDCSAP warning **2.799 hours before a published primary stellar eclipse**. Reopened original NASA SAP and PDCSAP light curves show the deep eclipses precisely around both windows. The independent ephemerides were consulted **only after the frozen recurrence guard had selected those warnings**, not as inputs to the algorithm. This provides direct physical evidence that the 42 rescued telescope measurements overlap authentic stellar eclipse features, not a demonstration of better planet detection.

**Research question:** Can AI-assisted work reproduce and critically evaluate established exoplanet transit searches, then make a modest, physically motivated change that improves weak-signal recovery on an honest, comparable test? We report negative results and separate candidate vetting from confirmation.

**[Concise November 20 submission draft](NOV_20_STATUS_UPDATE_CONCISE_DRAFT.md)** and the [full project status draft](NOV_20_PROJECT_STATUS_REPORT_DRAFT.md) are ready for student review, citation verification, and submission-format editing. It integrates literature, NASA observations, the negative ablations, and a transparent AI-use statement.

## Real, NASA-labeled instrument defect: physical case study

[Verified Kepler KIC 7461601 Q6 SAP-versus-PDCSAP study](REAL_KEPLER_SPSD_CASE_RESULTS_2026_11_07.md) · [successful original-data workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42403352082) · [90-day source figure and JSON artifact](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42403352082/artifacts/13586631074).

An official NASA quality flag identifies an actual **sudden pixel sensitivity dropout at BKJD 547.889249**. The identical fixed rule from our newer six-star experiment found a **persistent negative step in original SAP aperture flux at BKJD 547.909684**, **one long cadence (~29.4 minutes)** after the archived event. In **NASA's PDC-corrected PDCSAP flux**, it reported no corresponding step warning. This is **one previously documented illustrative positive case**—not a representative detector validation or planet discovery. It explains why additional simple masking on already corrected PDCSAP photometry often changes nothing, while properly distinguishing measurement preprocessing from astrophysical classification.

## New verified experimental result — localized instrumental defects, November 7, 2026

**[Read the complete six-star observational and synthetic stress-test report](VERIFIED_LOCALIZED_STEP_RESULTS_2026_11_07.md).** This study was predeclared in [the frozen manifest](LOCALIZED_STEP_STUDY_FROZEN_2026_11_07.json), independently run in [GitHub Actions](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42402819710), and all **74 regression tests passed**. The full [10-file original results artifact](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42402819710/artifacts/13585948128) includes all case predictions, original FITS checksums, diagnostic plots, thresholds, and errors.

- **New externally preselected sample:** 2 Kepler calibration stars and **6 usable independent held-out stars**, with **36 matched synthetic planet injections on unmodified real PDCSAP flux** plus **36 with a known artificial downward step**. Three methods applied to the same cases: original BLS, previous near-gap masking, and new persistent step masking.
- **Without an added defect:** Standard BLS **21/36** recoveries; new localized-step method **22/36**. But the step method masked **nothing** in all 36 natural-flux injections; the extra flag arose **entirely from a lower method-specific calibration threshold**, NOT a physical improvement.
- **With a known artificial step:** Standard BLS **18/36**, local-step BLS **19/36**. The local detector identified **21/36** constructed step onsets, rescued **one** genuinely wrong BLS period, and erased **eight** true injected-transit cadences across the sample.
- **Held-out proxy-null flags:** no defect: both methods **4/24**. Added artificial step: standard BLS **13/24**, local-step method **10/24**. Proxy controls are deliberately inverted/rolled observed flux, **not true Kepler survey false-alarm controls**. These held-out rates differ dramatically from the calibration design's nominal 10% target.
- **Interpretation:** a limited conditional benefit on a tailored toy defect model, **no demonstrated real-photometry preprocessing advantage**, and no numerical evidence of superiority to published ARC2, NASA PDC, or Robnik et al. 2026. The negative findings and calibration failure are central to the final project's reflection.

[Scientific methods and source justification](PART_II_LOCALIZED_DEFECT_EXPERIMENT.md) · [New reproducible Colab notebook](Kepler_Localized_Step_Study_Colab.ipynb) · [Full executable code](localized_step_ablation.py).

## Latest actual observational result — preprocessing comparison (November 7)

[Complete negative-results report](REAL_KEPLER_PREPROCESSING_RESULTS_2026_11_07.md) · [successful code and experimental workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42400548553) · [download original artifact](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42400548553/artifacts/13584998475).

- **Result:** baseline BLS **2/12** and gap-edge-mask BLS **2/12** correct-period *threshold-passing* injections; 0/10 constructed proxy nulls flagged by either method. A one-star exploratory comparison, **not** evidence of robust equivalence or Kepler mission false-alarm performance.
- **Data issue retained:** KIC 11904151 Q8 file unavailable through the fixed official source; no replacement was selected. Mask affected 15/2,535 test cadences, including two injected shallow-transit observations.
- **Interpretation:** a simple near-gap mask did not improve weak-transit recovery here; Robnik's more sophisticated physical defect removal remains untested in this project. Study design, failure cases, false alarms and source hashes are preserved.

## Current experimental implementation: source-inspired preprocessing ablation

**Starting point:** [source-grounded adjacent methods and writing review](ADJACENT_EXOPLANET_METHODS_AND_SCIENTIFIC_WRITING.md) and [four core papers](PART_I_FOUR_PAPER_CRITICAL_REVIEW.md).

**New experimental files:** [frozen experimental manifest](PREPROCESSING_ABLATION_FROZEN.json), [methods/protocol](PREPROCESSING_ABLATION_METHODS.md), [raw FITS preprocessing and injection module](kepler_preprocessing.py), [paired BLS ablation](preprocessing_ablation.py), [unit tests](tests/test_kepler_preprocessing.py), and [successful real-data GitHub Actions experiment](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42400548553) and [Google Colab notebook](Kepler_Preprocessing_Colab.ipynb).

We compare ordinary **Astropy BLS** with the *same BLS search* after one fixed and conservative **0.2-day near-gap mask around gaps >0.5 days**. Both are evaluated on the same synthetic transit events injected into genuine NASA Kepler PDCSAP flux **before** common detrending. Calibration and held-out stars are disjoint. Detection thresholds are determined only by separate, constructed inverted/rolled-flux **proxy** calibration nulls. We also measure how many real injected transit measurements the mask discards.

**Verified negative finding (November 7):** [complete results and caveats](REAL_KEPLER_PREPROCESSING_RESULTS_2026_11_07.md). **64 offline tests passed** and real Kepler inputs were analyzed. Only **one of two preselected held-out stars** was available; across that star's 12 injections, both ordinary and gap-masked BLS recovered **2/12**. Both flagged 0/10 held-out *proxy* nulls. The mask discarded 15/2,535 real-quality cadences and two shallow injected transit samples. **No improvement is demonstrated.** This is *not* survey FAP or a replication of Robnik et al. (2026). Earlier failed external binary vetting remains equally important.

## Latest independently verified findings: external failure and multi-planet follow-up

- **Frozen 13-star external test:** [full negative-results report](FROZEN_REAL_13STAR_VALIDATION_RESULTS.md) with [frozen selections](real_external_cohort_frozen.json) and [official run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42321227884). Of 7 published binaries, 6 Q8 files were analyzed; **none** triggered our binary-specific warning, including 4 half-period aliases and 2 exact orbital periods. For 6 listed confirmed planets, BLS recovered 3 selected orbital periods; two other signals corresponded to different previously confirmed planets in the *same* systems. **This contradicts any broad claim of validation from the earlier two-star success.**
- **Exploratory multi-planet development:** [real Kepler iterative-BLS report](ITERATIVE_BLS_REAL_MULTIPLANET_RESULTS.md) and [successful run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42321423938). Modeling/subtracting the first BLS candidate in Kepler-20 allowed a second pass to recover the known **Kepler-20b 3.6963-day** period after Kepler-20c. For Kepler-18, passes found Kepler-18c and Kepler-18d but not selected Kepler-18b; one later period repeated the first. **This is post-hoc development, not a fresh statistical holdout.**
- **Next independent tests:** [alias-aware binary hypotheses](../../issues/9) and [validated multi-pass BLS with false-alarm controls](../../issues/10). No thresholds should be adjusted and re-tested on the same frozen cases as if independent results.

Scientific interpretation: Generative AI can help write working astrophysical code, but **an easily demonstrated success is not equivalent to a reliable astronomical classification method**. All caveats and known failures remain part of the final report.

## Adjacent exoplanet-methods references and scientific writing

New student-provided readings: A. P. Hatzes (2020) *The Doppler Method for the Detection of Exoplanets* (full textbook), Campante/Santos/Monteiro (eds., 2018) *Asteroseismology and Exoplanets* (full volume), and Emily Gilbert (2022) *The Detection and Characterization of Exoplanets Around M Dwarf Stars Using TESS* (**24-page excerpt only**). See [source-grounded method and writing notes](ADJACENT_EXOPLANET_METHODS_AND_SCIENTIFIC_WRITING.md). Highlights: sampling/window aliases, heteroskedastic uncertainties, stellar activity and dangerous over-filtering, BLS-to-physical-transit-fit workflow, density/eccentricity assumptions, joint RV/transit posterior, and a reproducible manuscript template. **No new measured performance accompanies these reading notes.**

## Part I literature review — first four complete papers

The student supplied complete PDFs of **Kovács et al. (2002)**, **McCauliff et al. (2015)**, **Thompson et al. (2018)**, and **Robnik et al. (2026)**. See the [annotated 4-paper critical review](PART_I_FOUR_PAPER_CRITICAL_REVIEW.md), which records each paper's original methods, reported quantitative results, figure/page pointers, limitations, relevant parallels with our actual experiments, and a proposed same-false-alarm-budget ablation. **Primary lesson:** detection, historical-label classification, survey completeness and physical planet confirmation are different scientific tasks. Our present headline percentages must not be compared across them without compatible experiments.

## Final project narrative (three parts)

**Read [FINAL_PROJECT_THREE_PART_MASTER_PLAN.md](FINAL_PROJECT_THREE_PART_MASTER_PLAN.md) first.** The final submission will be organized as **Part I — Preliminary research and limitations of existing methods; Part II — implementation, baseline replication and measured improvements; Part III — critical reflection and comparison with published papers**. The primary methods benchmark is **Robnik et al. (2026)** for event vetting/multiple transit extraction; **McCauliff et al. (2015)** is the ML comparison, and Thompson et al. (2018) documents the DR25 labels. The master plan explains why our raw performance numbers cannot be compared directly with published numbers from different datasets and evaluation protocols.

**Instructor requirements:** quantitative component, synthesis of at least two lessons, references, AI-contribution acknowledgement, and completed project-elements checklist appended to the explanatory write-up. Project status update due **November 20, 2026**, and final due **December 11, 2026**, both 11:59pm CST.

## Recent verified research results (November 6, 2026)

- **Real NASA DR25 catalog:** [verified 8,054-KOI experiment](REAL_NASA_DR25_RESULTS_2026_11_06.md), with 1,619 held-out signals. Four-feature forest greatly outperformed SNR alone on catalog-label accuracy/FPR, but had lower candidate recall; ensemble disagreement barely changed equal-budget review errors (123 vs 122; paired CI includes zero).
- **Real Kepler light curves:** [Kepler-69b and real-noise injection](REAL_KEPLER_LIGHTCURVE_RESULTS_2026_11_06.md). BLS recovered Kepler-69b's known 13.72237-day period at 13.71334 days (0.066% difference); 500ppm, 1500ppm and 4000ppm synthetic transits inserted into genuine KIC 2436365 Quarter 2 flux had exact-period recovery 1/3, 3/3 and 3/3. This small injection test has **no calibrated flag threshold**.
- **Early synthetic event checks:** [35-signal ablation](FIRST_EVENT_VETTING_ABLATION_2026_11_06.md) found simple per-event checks removed only one of five binary-like false positives, not the overall weak-signal detection problem.
- **Binary-specific physical checks:** [56-signal follow-up](BINARY_ECLIPSE_SYNTHETIC_FOLLOWUP_2026_11_06.md) found that an odd/even-depth/secondary-eclipse review layer rejected all eight deliberately binary-like signals in the fresh synthetic holdout, without rejecting any of the BLS-detected injected planets. This is **exploratory**, tiny, and not yet proof of robust performance on genuine astrophysical binaries.
- **Real external planet-vs-binary control: SUCCESS:** [verified two-real-object planet-versus-binary case study](REAL_PLANET_VS_BINARY_VALIDATION_2026_11_06.md). Using actual Kepler Quarter 8 brightness data, Kepler-69b generated no binary warning while published eclipsing binary KIC 10661783 triggered a strong secondary-eclipse warning. Both period fits closely matched published values. This remains a two-object sanity check, not a population-level false-positive estimate. [Successful workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42320396449).

These are **three separate evidence types**: historical NASA label classification, genuine Kepler observations, and synthetic injections/controls. Do not combine their percentages as though they represent one end-to-end astronomical detector.

## Start here (no software download)

1. Open [Google Colab](https://colab.research.google.com/).
2. Choose **File > Open notebook > GitHub** and enter `DrewThomas09/ASTR_FInal_Project`; select `Kepler_AI_Project_Colab.ipynb`.
3. Choose **Runtime > Run all**. The notebook installs required packages, writes the complete source files, runs the simulated experiments and attempts a NASA Kepler catalog download.
4. If NASA is unavailable, the notebook prints the exact CSV download URL and allows manual upload. **Do not report real-data performance numbers unless the CSV step succeeds.**
5. Download the resulting figures and numerical results. Keep `AI_USE_LOG.md` updated, and write your own analysis.

## Research synthesis and decision (November 6, 2026)

**Start with the [consolidated literature and experiment strategy](CONSOLIDATED_RESEARCH_STRATEGY_NOV2026.md)** before adding another model. It compares foundational Kepler methods, 2025–2026 exoVetter, ExoMiner++, RAVEN, Robnik's per-event and null-template methods, and adjacent selective classification, calibration, leakage and anomaly detection research. It states our original **inferences** separately from paper findings and documents limitations in the current code. The two new priorities are [equal-review-budget ML evaluation](../../issues/6) and [injection into real Kepler noise](../../issues/7).

**Methodology warning:** A model that sends more examples for human review will usually make fewer automatic errors; that is not in itself an improved classifier. Compare triage methods at equal review fraction, preserve all original test examples in the error accounting, and never describe NASA's Robovetter labels as independently confirmed planets.

## Research status (November 6, 2026)

The main scientific reference is [Deep 2024–2026 methods and failure audit](RECENT_METHODS_AND_FAILURE_AUDIT_2024_2026.md). It documents published methods and **verified limitations** of our code separately from risks requiring testing. Priority GitHub issues #3–#5 specify the required corrections before presenting real-data results. No claim of a new exoplanet or measured improvement has been made.

## What has been implemented?

- `exoplanet_detector.py`: simulate brightness observations, detect periodic dips with the published **Box Least Squares** (BLS) algorithm using Astropy, plot injected-planet and noise-only control. This is a traditional astronomy algorithm, **not machine learning**.
- `sensitivity_study.py`: a simulation comparing period recovery when the injected transit depth is 4,000, 1,500, or 500 parts per million.
- `ml_screening.py`: download NASA's Kepler DR25 Q1-Q17 KOI table, train a single random forest, compare with SNR-only screening, and output a confusion matrix and metric table.
- `validation_study.py`: run a positive-control and a noise-only example.
- `tests/test_project.py`: test grouped data splits, threshold behavior and a synthetic ML training workflow.
- `AI_USE_LOG.md`, `RESEARCH_PLAN.md`: research purpose, human responsibilities, methods and limitations.
- `Kepler_AI_Project_Colab.ipynb`: everything needed for the primary experiments in one notebook.

## What the proposed improvement means

Machine learning is used for **screening previously detected transit-like signals**, not as an original replacement for the astronomical BLS transit-search algorithm. We use four measured inputs: orbital period, transit duration, transit depth and signal-to-noise ratio. Training labels are historical NASA Robovetter decisions. We compare a random forest against SNR-only screening at a similar **validation-selected** candidate recall. Test stars are disjoint from training and validation stars.

**This does not confirm exoplanets or measure hours saved by astronomers.** A false-positive reduction on held-out historical classifications would be a measurable classroom result, not a new scientific discovery claim. A negative or inconclusive result is still scientifically worth reporting.

## Run locally (optional)

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests
python exoplanet_detector.py --output results/transits
python sensitivity_study.py --output results/sensitivity --trials 12
python ml_screening.py --download --output results/ml
```

If the automated NASA download fails, open the URL printed by the ML script, save it as `data/kepler_dr25.csv`, then run:

```bash
python ml_screening.py --csv data/kepler_dr25.csv --output results/ml
```

The downloaded CSV and outputs are excluded from Git by `.gitignore` to avoid accidentally committing data artifacts.

## Tested versus pending

**Verified as of November 6, 2026:** GitHub's offline test suite passed after correcting a fixed-star-count test assumption, and the NASA DR25 Actions workflow successfully downloaded and modeled 8,054 real catalog signals. Full results: [REAL_NASA_DR25_RESULTS_2026_11_06.md](REAL_NASA_DR25_RESULTS_2026_11_06.md). The new Kepler-69b light-curve workflow is a separate validation step; check its latest Action status before using any numbers.


## November 6: research-driven experiments added

The repository now includes **two new experimental modules** and their Colab cells:

- [`blind_transit_benchmark.py`](blind_transit_benchmark.py): randomized period, epoch, and duration injections; missing measurements; white/red noise, a single isolated dip, and a binary-like control. The BLS search range is **predeclared as 1.5–12 days**, while injected orbital periods are independently sampled from 2.1–9.8 days. A threshold chosen from separate control simulations is evaluated on a held-out synthetic sample. It outputs a full trial CSV, summary CSV and figure. This is a *synthetic stress test*, not a mission-calibrated false-alarm probability.
- [`ml_uncertainty_triage.py`](ml_uncertainty_triage.py): four independently seeded random forests, same historical DR25 labels and same held-out stars, comparing **ordinary classifier-margin review** against **margin plus ensemble-disagreement review**. It saves auto-error counts, fraction sent to human review, period/SNR subgroup table and paired star-bootstrap intervals. A review case is not counted as an automatic success.
- [`transit_consistency.py`](transit_consistency.py): inspects **individual predicted transit events** using the BLS-fitted period and epoch. It describes whether one dip dominates, whether multiple events support the same pattern, and any odd/even depth difference. These are **heuristic diagnostic warnings**, not calibrated astrophysical false-positive probabilities. This is an optional extension motivated by Robnik et al. (2026) and prior transit vetting, not an original discovery of the method.
- [`tests/test_new_experiments.py`](tests/test_new_experiments.py): new unit and synthetic-pipeline checks; an additional BLS smoke test runs in environments with Astropy installed. Individual-event sanity checks are in [`tests/test_transit_consistency.py`](tests/test_transit_consistency.py).
- [Full 2024–2026 research audit](RECENT_METHODS_AND_FAILURE_AUDIT_2024_2026.md), with methodological failure modes and the papers inspiring these additions.

**Quickstart:** Open [the Colab notebook](Kepler_AI_Project_Colab.ipynb), choose Runtime → Run all. The new blind simulation uses just four simulations per group for a quick preliminary run; increase `per_condition` to 8 or 12 for a less noisy illustration. These small samples are **not sufficient for a precise scientific false-positive rate**.

**Current verification:** Simulator, triage, and individual-event diagnostic logic passed twelve local offline tests. Astropy and external NASA access were unavailable in the local development container, but the full DR25 analysis subsequently **succeeded on GitHub Actions**. A separate MAST real-light-curve experiment is now included and must be checked independently. Do not report synthetic-test metrics as findings on real stars.

**Important:** The original `exoplanet_detector.py` remains unchanged as the **historical, biased-range baseline**, so old results can be replicated. Do not use its narrow-period success as proof of blind detection.


## Verification and data provenance enhancements (November 6, 2026)

The [NASA DR25 workflow](.github/workflows/nasa-dr25-study.yml) now also:

1. Generates an immutable-input [data manifest](dataset_manifest.py) containing SHA-256, labeled row counts, distinct host stars and missing-measurement counts. Raw downloaded data are not uploaded as an artifact.
2. Runs a **fixed human-review budget** comparison (10%, 20%, 30%, 40%) using [`ml_uncertainty_triage.py`](ml_uncertainty_triage.py): random review, ordinary score-margin review, and model-disagreement-enhanced review, always on identical held-out stars. The disagreement stabilizer is selected **using validation only**. A model's reviewed cases are not counted as successes.
3. Saves [per-observation held-out predictions](ml_uncertainty_triage.py) with raw model score, predicted historical label, star ID and 30%-budget review assignments so the reported comparisons are auditable.
4. Runs a **read-only** [calibration audit](calibration_audit.py). Its Brier score and calibration curve measure consistency with DR25's **historical Robovetter labels**, *not* the probability a planet exists.
5. Exports the metrics, figures and logs as a temporary GitHub Actions artifact. See [Actions](../../actions).

**Scientific status:** These additions are committed and have synthetic regression tests; the **NASA DR25 workflow has now been verified using its stored metrics and ZIP artifact**. Do not copy synthetic results into the actual report. Run the Colab notebook or inspect the workflow's `dr25-scientific-analysis` artifact after a successful workflow run.


## First verified NASA DR25 findings and the next independent check

- **Real catalog experiment:** [November 6 DR25 results](REAL_NASA_DR25_RESULTS_2026_11_06.md) and [successful workflow with downloadable figures](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42282355449). A four-feature forest achieved **81.6% historical-label accuracy** on 1,619 held-out KOIs, versus **52.3%** for the one-feature SNR screen; however, candidate recall differed, so these are not matched-recall comparisons. Adding model disagreement to ordinary margin-based review changed **123 to 122** wrong automatic decisions at a 30% review budget. The host-star bootstrap interval includes zero; **no reliable incremental gain is demonstrated**.
- **Scientific pivot:** [`real_kepler_lightcurve.py`](real_kepler_lightcurve.py) now checks one actual public Kepler-69 light curve against the previously published orbital period (used **only after** BLS fitting) and injects known synthetic transits into a second star's real measured brightness variations. Outputs come from the [real Kepler light-curve workflow](.github/workflows/real-kepler-lightcurve.yml). This is a narrow observational sanity check, **not an estimate of planet-discovery completeness or false-alarm rate**.
- **Verification:** Tests and real catalog run passed after a fixed-star-count test assumption was corrected. The new Lightkurve/MAST workflow requires its own successful external run before any of its numerical results may be cited.

## Scientific sources

- Kovacs, Zucker & Mazeh (2002): [Box-fitting algorithm](https://doi.org/10.1051/0004-6361:20020802)
- McCauliff et al. (2015): [Random forest classification of Kepler candidates](https://doi.org/10.1088/0004-637X/806/1/6)
- Thompson et al. (2018): [Kepler DR25 candidate catalog](https://doi.org/10.3847/1538-4365/aab4f9)
- Shallue & Vanderburg (2018): [Deep learning for exoplanets](https://doi.org/10.3847/1538-3881/aa9e09)
- [NASA Kepler candidate tables](https://exoplanetarchive.ipac.caltech.edu/docs/Kepler_KOI_docs.html)

**Academic integrity:** all AI-assisted programming and documentation must be disclosed as required by the instructor. The student is responsible for understanding the code and drawing scientific conclusions.
