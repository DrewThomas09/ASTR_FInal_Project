# Actual NASA ExoMiner++ inference and matched TESS feature-development results
**2026-11-08 | Completed original-data experiments (not a discovery claim)**

## The first real original NASA pretrained model execution

**[Verified successful real pretrained model inference](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519263267)** · **[exact official-original prediction and log artifact](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519263267/artifacts/13632672462)** · [official runner](.github/workflows/nasa-exominer-real-pretrained-pilot.yml).

This is the first actual full NASA model processing in our project, not our own classifier or a re-creation of its appearance:

| Property verified directly from saved original NASA output | Value |
|---|---|
| Official NASA model code | **ExoMiner 2.4.0**, Git commit **59d3f43**, release date **2026-10-12** |
| Container immutable repo digest | `ghcr.io/nasa/exominer@sha256:1b7ffac9db8afe1787ec9a0464ed8cc16ab91b7a280e6e824c27e3a121b0c6e9` |
| Official model | **planet-validation**, **single** pretrained model, TESS SPOC 2-minute cadence |
| NASA tutorial data | **TIC 167526485, Sector 6**, one original SPOC threshold-crossing event `167526485-1-S6` |
| Official TCE duration | **6.960829 hours** |
| Official TCE period | **5.011590 days** |
| Reported transit depth | **10,861.08 ppm** (TCE measurement, not validated physical planet) |
| Official unmodified neural-network score | **0.020304145** |
| Official class at score 0.5 threshold | **NOT_PC** |
| Original TCEs found / normalized / scored | **1 / 1 / 1**; available source data and difference images successfully processed |
| Inference and NASA source preprocessing phase | **31.66 seconds** after container initialization |
| Source fidelity | Original NASA output `predictions_spoc-tces_set.csv` saved with its own full version/column header; `master_tce_tracking_summary.csv`, exact image digest and NASA logs archived |

**Failed run and correction:** First container [run #42519002488](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519002488) failed with `OSError: [Errno 30] Read-only file system: '/tics_tbl.csv'`, in NASA's `process_inputs()`: it intentionally rewrites a normalized copy of `tic_ids_fp` during setup. Our wrapper was changed to mount a writable **scratch copy** of NASA's publicly documented input, preserving the original CSV untouched. The successful re-run produced authentic scores without changing NASA's weights or inference settings. This matters because the engineering was genuinely reproduced, rather than asserted from a README.

This v2.4.0 inference is **not the same model as the original 2025 published v1.0.0 TESS cross-validation scores**. One documented, nonrandom TESS target is a **pipeline feasibility check**, not a sensitivity, reliability, confirmation or new-discovery claim. Also, current ExoMiner is primarily **vetting detected SPOC TCEs**, not independently detecting all planets in raw pixels.

## A prespecified, fully trained feature-change experiment on published TESS TCEs

**[Precommitted frozen design](TESS_SCALAR_ABLATION_FROZEN_2026_11_08.json)** · [complete original-data training code](tess_scalar_ai_assisted_replication.py) · [reproducible successful 193-test Actions run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519431316) · [complete predictions, per-fold metrics and PR curves](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519431316/artifacts/13633080778).

- **57,162** original public 2025 TESS SPOC labeled TCE observations, **17,206** host TICs, **3,681** KP or CP positive published labels; source Zenodo version DOI `10.5281/zenodo.15466293` and original MD5 `c79f3651d556e71f7878a46f960d09b4` were verified before training.
- **Ten** original NASA research-team host-separated folds were reused. No star was in more than one fold. All **57,162** predictions for each new RF were made with that star's entire fold **excluded** from training. Training-only imputation. No NASA ExoMiner score, physical source ID, labels or ephemeris times fed to the model.
- **Baseline:** 80-tree random forest, depth 9, minimum leaf size 6, balanced_subsample weighting, four logged scalars: candidate orbital period, transit duration, inferred planet radius and multiple-event detection statistic.
- **Proposed small adjustment (same RF hyperparameters and split):** Add transit duty-cycle ratio (duration/period) and Gaia RUWE astrometric measurement, motivated by eclipse geometry and possible stellar companions. **Not a newly invented NASA ExoMiner feature**; current NASA ExoMiner already includes richer geometric and Gaia inputs.
- Model settings/features and primary endpoint were frozen **before** seeing this experiment's original-source results. Main endpoint: **augmented minus baseline pooled held-out Average Precision (AP)**. **350** target-star-cluster bootstrap resamples, seed `2026110819`, for a descriptive interval; all sector observations of a TIC resampled together.

| Audited metric / historical KP+CP published labels | Four-feature new RF | Six-feature new RF | Original NASA ExoMiner++ **published** scores |
|---|---:|---:|---:|
| Pooled Average Precision | **0.62114** | **0.64456** | **0.97036** |
| ROC AUC | 0.95294 | 0.95585 | 0.99713 |
| Precision, threshold 0.5 | **40.68%** | **39.99%** | **92.37%** |
| Recall, threshold 0.5 | **87.58%** | **86.42%** | **92.69%** |
| Historical nonplanets incorrectly accepted | 4,702 | 4,774 | 282 |
| Historical planets missed | 457 | 500 | 269 |

**Prespecified AP delta:** `+0.02341445`, with **95% TIC-star cluster bootstrap CI `[-0.01101365,+0.05374695]`** across **350** valid replicates. This interval includes zero. The simple additional features give a *modest but statistically inconclusive AP gain* and actually **worsen both precision and recall** at score≥0.5. Do **not** describe this as a statistically significant gain. More important, ExoMiner++ remains substantially better at the **published historical label-reproduction task**; it has waveform, pixel and additional diagnostics missing from the RF.

The original NASA 2025 model score is **read from its published catalog**, not a CNN trained or run during this matched scalar experiment. It includes a different model feature set and the 2025 paper's Kepler/TESS training regime. The comparison illustrates what we cannot yet replicate, **not** proof that our new model has improved the NASA CNN.

## Original Kepler light-curve input-feature and physical event-recovery development

**[Actual NASA Q6/Q7 two-system experiments, 185 full software tests passed](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519123518)** · [complete source-flux manifests/individual event tables](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519123518/artifacts/13633010940) · [new coded event recovery and odd/even measurements](kepler_event_shape_diagnostics.py) · [ten regression tests](tests/test_kepler_event_shape_diagnostics.py).

For **two previously examined known systems**, the program ran upstream, blind-quarter BLS on **original NASA Kepler FITS** and measured pre/during/post brightness around each predicted event, with quality masks and a full set of observed cadences on **both** sides. Median pre/post differences are a possible persistent detector-step diagnostic; alternate-epoch depth differences are a possible half-period binary alias diagnostic. These additional features are **not official ExoMiner inputs, predictions or a discovery test**.

| Quarter / source | Original quality-filtered observed event count | Fitted 1-quarter BLS period (d) | Median local depth | Odd-even median depth difference and event-bootstrap 95% interval |
|---|---:|---:|---:|---|
| Q6 Kepler-12, known planet host | 20 | 4.43830 | 0.01551 | +0.000065, CI [-0.000168, +0.000368] |
| Q7 Kepler-12, known planet host | 18 | 4.43788 | 0.01566 | -0.000269, CI [-0.000656, +0.000234] |
| Q6 Kepler-35, known stellar eclipsing binary | 7 | 10.37126 | 0.19166 | -0.01457, CI [-0.06571, +0.00832] |
| Q7 Kepler-35, known stellar eclipsing binary | 8 | 10.37025 | 0.21110 | -0.02039, CI [-0.03459, +0.04758] |

**All four event-level odd/even intervals cross zero**, even though the prior 31-bin phase-folded Q6 Kepler-35 shapes visibly differed by tens of percent: these are different statistics with different sampling/uncertainty. The new event-level result is **not a statistically resolved binary discrimination gain**. Similarly, both real planetary and binary events recover to similar baseline brightness after an eclipse: **post-event recovery alone does not differentiate planets from stellar binaries**. This is exactly the type of *negative result* we should preserve honestly.

The new TESS-specific [companion diagnostic](tess_official_event_recovery_companion.py) is designed to read **the same NASA SPOC LC FITS and official prediction CSV** used by the successful 2026 model, while leaving its score unchanged; check its separate dedicated workflow for whether source FITS/analysis actually succeeded. Do not claim this script modifies the NASA neural network: it is a physics-feature sidecar and only a candidate for a subsequent **matched controlled ablation**.

## Next credible milestone

1. Replicate official v2.4.0 inference on a **fixed, diverse positive/negative TESS source cohort**, with original pixels and light curves, recording missing/error cases and keeping all scores unchanged.
2. Add event-recovery and ephemeris P/2/P/2P diagnostics to these **same** TESS input examples; compare paired results, ideally by training an experimental calibrated *companion* or ablated neural branch while preserving a complete official baseline. Test the new addition on **new withheld host stars**, never fit and evaluate on the same ones.
3. Run NASA realistic planet-injection/recovery tests **at fixed empirical false-alarm budget**, with host-level uncertainty. Only then can any change be called an exoplanet-detection improvement rather than an engineering example.

**AI disclosure:** GPT-6 located public NASA/Zenodo data, authored code, performed original-data execution and testing, worked through the read-only input error, analyzed uncertainty and drafted prose. The student must independently review the scientific claims and comply with course AI-use policies.

## The same TESS data: completed physical feature sidecar beside official neural inference

**[Successful same-input NASA + descriptive event-recovery Actions run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519715623)** and **[archived actual original NASA predictions + SHA-verified MAST source metadata + all four per-event measurements](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42519715623/artifacts/13633161147)**. The [physical companion code](tess_official_event_recovery_companion.py) and [source-matching/immutability tests](tests/test_tess_official_event_recovery_companion.py) are in main.

This is a new step beyond the previous separate Kepler demo: **both methods were run on the exact same original TESS light-curve source and TCE ephemeris**.

- NASA SPOC raw-source file: `tess2018349182500-s0006-0000000167526485-0126-s_lc.fits`, original SHA256 `41365d738d2a872378a12a4d49068ccdf317710fd04179d6aa8542b4e66f3078`.
- **14,592** quality-zero original TESS 2-minute cadences in the sidecar, and the original unmodified NASA v2.4.0 **planet-validation score 0.020304145 / NOT_PC** for `167526485-1-S6`.
- At the NASA TCE's original period ~**5.01159 days** and epoch, the independent recovery code found **4 real flux dips** with locally normalized depths **1.138%, 1.167%, 1.236%, 1.224%**. Median event depth **1.195%**.
- Post- versus pre-event median flux recovered fairly closely: across the four events, median `|post-pre|/(|local depth|+noise)` is **0.04039**. This statistic is descriptive, not a NASA feature, an independently calibrated probability or a physical planetary proof.
- There were only **two odd and two even** real event windows. The preregistered event-level uncertainty rule correctly **does not report an odd/even confidence interval** with fewer than three per group, avoiding false precision.
- **Important scientific result:** a remarkably repeatable `~1.2%` dip can receive a low planet-validation score once NASA considers its broader stellar and pixel diagnostics. We did **not** determine the astrophysical/instrumental source of this event or demonstrate the ExoMiner classification is independently correct. Recovery to baseline is insufficient to distinguish a planetary transit from an eclipsing star.
- No original NASA neural weights or decisions were changed. The sidecar reports its metrics alongside, rather than modifying the official `predictions_spoc-tces_set.csv` score.

**Meaning for model development:** we have proven end-to-end **input co-location** of official NASA ExoMiner and our own optical-event processing on an original space-telescope source. The next *scientific* requirement is a large, previously unexamined TESS cohort with controlled full-model-versus-augmented comparison before any claim of improving NASA exoplanet discrimination.


## New model-development result: a controlled attempt to improve the published ExoMiner++ score

**[Frozen research question and hyperparameters, committed before fitting](EXOMINER_PUBLISHED_SCORE_POSTPROCESSOR_FROZEN_2026_11_08.json)** · [new fitted-model source](exominer_published_score_postprocessor.py) · [original-2025 real-data successful Actions run, **211 tests passed**](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42523223355) · [all 57,162 exact-UID matched out-of-fold scores, model logs, plotted original-score PR curves and cohort-bootstrap interval](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42523223355/artifacts/13633912673).

**Question:** could a small, reproducible AI-assisted statistical postprocessor actually improve the **NASA team's published 2025 ExoMiner++ neural scores** when orbital duration, period, signal strength and Gaia RUWE are included? This is more directly linked to NASA's actual strong prediction scores than our earlier four-feature random forests. It is **not** a modification of NASA's pretrained neural-network weights.

Frozen design: use NASA/USRA released TESS SPOC 2-minute 2025 original catalog Zenodo `10.5281/zenodo.15466293`, original MD5 `c79f3651d556e71f7878a46f960d09b4`. **57,162** historical TCE observations, **17,206** distinct stars, 3,681 published KP/CP positives; preserve the **original authors' 10 star-disjoint out-of-fold assignments**. Fit on the other nine source folds and predict only each excluded star's TCEs. Baseline fitted postprocessor: logistic regression on only the logit-transformed original released NASA score. Additional-feature postprocessor: **identical** fixed logistic regression with the logit original NASA score *plus* log-transformed original period, duration, MES, Gaia RUWE and duration/period ratio. Train-only median-imputation and scaling. Fixed C=0.3, threshold 0.5, no test-driven tuning. Primary endpoint: average-precision delta **new augmented minus new score-only**; whole-TIC bootstrap 350 draws, seed 2026110823.

| Historical label metric / NASA 2025 released data | Raw NASA scores, unmodified (not trained here) | New NASA-score-only calibration | New NASA score + physics calibration |
|---|---:|---:|---:|
| **Average precision / PR-AUC** | **0.9703595** | **0.9694660** | **0.9693761** |
| ROC AUC | 0.9971312 | 0.9970308 | 0.9970612 |
| Precision, threshold 0.5 | 92.366% | 92.565% | 92.515% |
| Recall, threshold 0.5 | 92.692% | 92.339% | 92.339% |
| TP / FP / FN | 3412 / 282 / 269 | 3399 / 273 / 282 | 3399 / 275 / 282 |

**Primary change:** **−0.00008989 AP** with whole-star 95% bootstrap interval **[−0.00119364, +0.00098342]**. The interval crosses zero, so **there is no statistically resolved score improvement**. Even the newly calibrated score-only baseline slightly trails the unmodified original NASA ranks. Relative to score-only recalibration, the extra physics metadata accepted two more historical negatives at threshold 0.5 while recovering no additional historical positive labels. This makes the tested feature change a **negative/inconclusive finding, not a claim of optimization success**.

The first full software test run had **one test-fixture error**, not a model or source data error: an intended cross-fold contamination fixture used rows 0 and 10, which both came from fold 0. We changed the synthetic test to compare rows 0 and 1, which genuinely belong to different folds. **No model settings, source cohort, threshold, science labels or evaluation settings were modified after seeing the result.** The corrected original-source workflow passed **211** tests.

**Interpretation:** ExoMiner++'s learned classification is already strong on its own historical labeled TESS sample, and a simple reweighting of published scalar attributes contributes no reliable gain. The trial does not prove further improvements are impossible: original model version 2025 differs from current 2026 v2.4.0, and new sources/instrument artifact recovery may create different failure modes. Any next candidate improvement needs **event-level flux and instrument evidence on newly held-out sources**, not just more catalog numbers.


## Verified larger experiment: NASA v2.4.0 on 16 **score-blind-selected** TESS host stars

**[Exact cohort frozen BEFORE looking at this cohort's pretrained scores](TESS_16STAR_OFFICIAL_EXOMINER_COHORT_FROZEN_2026_11_08.json)** · [Original TIC/sector input file](tess_16star_official_exominer_tics.csv) · [actual official v2.4.0 cohort+original-FITS run: success, **204 full regression tests passed**](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42522859511) · [all unchanged model outputs, source logs, 16 original FITS SHA256 identifiers, 81 individual event diagnostics and plotted scores](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42522859511/artifacts/13634466730).

**Study purpose:** go beyond the one documented NASA example without cherry-picking subjects based on model performance. The sample is a **feasibility and model-behavior study**, not a test on guaranteed new exoplanets.

### Frozen source selection, actual NASA run and coverage

The source was the exactly **MD5-pinned original published 2025 labeled TESS SPOC 2-minute table**, DOI `10.5281/zenodo.15466293`. Before reviewing the 2026 pretrained model's scores on this cohort, the candidate list was frozen as follows: four published historical label strata **KP, CP, EB, NTP**, with two TCEs per stratum from **7≤multiple-event statistic<20** and two from **20≤statistic<80**. All targets were single-sector runs **S3–S12** with period 2–10 days, duration 0.05–0.4 days, and selected by a **fixed SHA256 ordering of original TCE UID, without ever reading the source score**. Sixteen distinct TIC stars and sixteen exact original TCE UIDs were fixed in the cohort manifest. This was **not** a random census of all TESS stars or a fresh independent holdout from the original 2026 model training population.

Actual original NASA model: **unchanged ExoMiner++ v2.4.0 single pretrained binary planet-validation model** running the **same previously verified immutable Docker image digest**, with official NASA SPOC DV, original LC and difference-image processing. The pipeline completed successfully in **177.55 seconds** after image preparation and scored **22 SPOC TCE observations total** from these sixteen stars. Of the 22, exactly **16 were the prespecified historical event IDs**; the six other TCEs were not silently counted as independent or reclassified into our preregistered primary source cohort.

**Source retention:** **16 of 16 exact TCE UIDs scored by NASA**, **16 of 16 same original TIC+sector MAST FITS recovered for our independent postprocessor**, **16 unique original SHA256 file identities**, and **81 actual observed individual-event windows** assessed. All sixteen requested IDs appear in `all_16_frozen_stars_including_failed_sources.csv`, along with explicit source-missing/analysis-error statuses if applicable. None were missing in this run.

### Original model's raw scores versus the published historical label strata

| Originally published 2025 source label | n exact preselected TCEs | NASA 2026 original score range | Count with raw score ≥0.5 |
|---|---:|---|---:|
| KP (known planets) | 4 | 0.830526–0.929169 | **4/4** |
| CP (candidate planets) | 4 | 0.894892–0.979924 | **4/4** |
| EB (stellar eclipsing binaries) | 4 | 8.52e−10–0.000739 | **0/4** |
| NTP (non-transiting phenomena) | 4 | 1.41e−19–0.00002098 | **0/4** |

Thus, among these **exact 16 previously labeled observations**, the pretrained NASA v2.4.0 decisions agree with the earlier KP/CP-versus-EB/NTP grouping on **8/8 positives and 8/8 negatives** (TP 8, FN 0, FP 0, TN 8). **This is not 100% model accuracy on new or independent planets**. The cohort was deliberately balanced by label and signal range, it is very small, and the 2026 model's training exclusions have not been verified. These sources may overlap or closely resemble its development data. There is **no meaningful survey-wide accuracy interval or independent detection/false-alarm probability** based on these 16 cases.

### Physical findings from the exact SAME original TESS light curves

Our **independent sidecar** [source](tess_exominer_16star_cohort_audit.py) uses the official output TCE period, epoch and duration to inspect *original quality-zero NASA SPOC PDCSAP flux* on the same original TIC/sector FITS, with no invented observed cadences. It measures per-event pre/during/post medians, a `|post-pre|/(|event depth|+noise)` recovery ratio, and odd/even depth differences where enough true event epochs exist. It neither modifies NASA's neural scores nor feeds additional measurements back into the network.

| Originally labeled class | Median original 2026 NASA score | Median observed local depth | Median original TESS pre/post step ratio | Available full-event windows |
|---|---:|---:|---:|---:|
| KP | **0.8549** | **0.6915%** | **0.0322** | 4–7 events/star |
| CP | **0.9571** | **1.0968%** | **0.0658** | 4–8 events/star |
| EB | **~0.000012** | **1.8757%** | **0.0550** | 6–8 events/star |
| NTP | **~0.000003** | **0.0268%** | **0.1146** | 2–3 events/star |

These **median-of-event medians** are small-group descriptive statistics, not estimates of a general class distribution. The recovery step ratios for known planetary transits **overlap strongly** with those of stellar eclipses. That is a **negative result for using recovery alone to certify a planet**; both planets and eclipsing binaries can produce genuine temporary dimming that returns to the baseline.

Concrete source-backed example: previously labeled **eclipsing binary TIC 318986273 / Sector 10** has median local eclipse depth **~11.59%** and returns relatively closely to baseline (step ratio ~0.0293), yet NASA gives it a planet-validation score **8.5 × 10⁻¹⁰**, correctly matching the historic EB group. Conversely, previously labeled **non-transit signal TIC 177308817 / Sector 9** shows a local median dip **~2.19%** but receives a NASA score **~2.1 × 10⁻⁵**. Those cases illustrate why a dramatic brightness dip or a clean return to normal does **not** independently establish a planet. We have not separately proven the physical mechanism behind the NTP event or why NASA chose each score.

**Overall evidence:** the official NASA model is reproducibly runnable on multiple genuine original source files and sharply separates this frozen historical class-balanced demonstration cohort. Our physically interpretable extra event metrics work on the **same** telescope measurements, but **they do not presently provide a validated improvement over NASA's model**. Moreover, current NASA ExoMiner already uses individual transit, odd/even and source-centroid branches, so our sidecar cannot be called original novelty merely for reconstructing those concepts. The next legitimate test needs previously withheld host stars, fully documented 2026 training exclusions, comparison at a common false-alarm rate and possibly controlled instrument-step injections.


## Harder result: what happens to the ExoMiner++ errors from 2025 when scored by the 2026 model?

**[Original source, score-dependent error-challenge selection committed before the new scores](TESS_16STAR_2025_ERRORS_VS_2026_FROZEN_2026_11_08.json)** · [full genuine model + matching original SPOC FITS experiment: 217 tests passed](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42523749559) · [unchanged original 2025 and 2026 scores, all 16 source manifests, original flux-event measurements and paired figure](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42523749559/artifacts/13634607477) · [paired source audit code](tess_exominer_2025_error_challenge.py).

**Research question:** the first class-balanced study achieved 16/16 agreement with historical labels, which was useful software verification but did not identify failure modes. A **separate, deliberately difficult cohort** was instead selected from cases that **the published original 2025 ExoMiner++ model got wrong** against its original labels: 8 historic KP/CP observations with NASA 2025 scores below 0.5 (**2025 false negatives**) and 8 historically negative-source observations (EB/NTP/FP/NPC etc.) with 2025 scores at least 0.5 (**2025 false positives**). Selection used the old 2025 score **on purpose**, plus a fixed source-hash sorting algorithm, but **no 2026 model scores**. Strict original public Zenodo source MD5, TIC+sector+TCE UID, original 2025 labels and score thresholds were verified.

The **actual unchanged official NASA ExoMiner++ v2.4.0** container then scored all 16 exact original 2025 event IDs, with **17 total SPOC TCE scores** across these original stars, **16 matched previously selected TCEs**, and **16/16 matched original TESS SPOC light curves** independently examined by our physical sidecar. The original NASA processing/inference elapsed ~**94.77 seconds** after source download/container startup. No original science cases disappeared from the denominator; there were **zero missing original TCE UIDs**.

### All outcomes against the ORIGINAL historical 2025 class label

| Historical 2025 ExoMiner++ model error category, deliberately selected | Earlier mistakes | New 2026 model now agrees with old label | Error persists in 2026 |
|---|---:|---:|---:|
| Older model missed KP/CP-labeled planets/candidates | 8 | **4** | **4** |
| Older model accepted nonplanet-labeled EB/NTP/FP/NPC TCEs | 8 | **3** | **5** |
| **Total** | **16** | **7** | **9** |

These are **7 resolved and 9 persistent disagreements with original 2025 labels**, not proof that the 2026 model is inherently better or worse on independent stars. **This population is intentionally enriched for the original model's errors and cannot yield either a general accuracy estimate or a fair original-versus-new aggregate precision/recall comparison.** Moreover, the 2026 model may have been trained on these same older public sources, original labels may be incomplete or changed, and a model score is not independent physical follow-up.

### Specific persisted cases for error analysis

| Exact original TESS source UID | Historical 2025 category | Original published 2025 score | Real NASA 2026 score | Independently measured full source event windows | Question to inspect with original DV and model evidence |
|---|---|---:|---:|---:|---|
| `29960109-1-S4` | NPC (not a planet class) | 0.5128 | **0.9934** | 8 | Very confident current planet score against earlier nonplanet classification; inspect pixel localization, DV target/candidate association and nature of the original label |
| `354518617-1-S6` | NTP | 0.6228 | **0.9433** | 2 | Strong current planet score with only two event windows passing independent sideband-validity checks; inspect pipeline TCE windows and original quality flags |
| `165493409-1-S10` | EB | 0.8712 | **0.7465** | 2 | Persistently planet-like score for an earlier eclipsing-binary label; check secondary eclipse, period alias and pixel difference images |
| `466840711-1-S11` | KP | 0.1803 | **0.1373** | 6 | Persistently low score despite a previously known planet label and multiple observable windows; check ephemeris and photometric/source contamination |
| `158623531-1-S3` | KP | 0.3075 | **0.1836** | 2 | Earlier planet label still low under current classifier; short sector sample and missing event information may matter, without proving causation |

Other persistent source cases are `178155732-1-S4` (CP, 2025 0.1006 → 2026 0.2724), `460205581-1-S11` (CP, 0.0960 → 0.0329), `49899799-1-S4` (FP, 0.8388 → 0.7103), and `101395259-1-S9` (FP, 0.8396 → 0.7812). Actual reference scores with all precision are in archived `all_16_prespecified_2025_model_errors_and_actual_2026_outcomes.csv`.

Examples that changed historical 2025 error status: `422655579-1-S4` (KP label; 2025 0.1163 → 2026 **0.7420**) and `167554898-1-S6` (EB label; 2025 0.6266 → 2026 **0.0491**). These are examples of changed model behavior on an old-source retrospective sample; without a version-matched architecture ablation, the evidence cannot tell us which new feature or new training data was responsible.

**Physics implication:** for the nine persistence cases, simply increasing the sensitivity to flux dips would likely make some of the historically negative examples worse, while automatically vetoing deep dips could reject historically known planet sources. Some sources show only one or two usable independently checked event windows, so an odd/even median-difference test may be **unavailable**, not negative. The next useful engineering change must be driven by **actual NASA detailed model input diagnostics and original source-position evidence**, rather than inventing another catalog threshold.

### Focused engineering diagnostic, not a new test cohort

The five-source [non-blind, qualitative input-inspection plan](TESS_5_PERSISTENT_DISAGREEMENTS_INPUT_REVIEW_2026_11_08.md) documents why we selected two persistent known-planet disagreements and three strong nonplanet-label disagreements for detailed full original NASA input plot and DV report inspection. The [official NASA diagnostic-plot generation workflow](.github/workflows/nasa-exominer-five-disagreement-inputs.yml) was committed. **The selection is made AFTER looking at the new 2026 scores: it is valid for debugging, never as a statistically independent test.** Do not claim any generated PDF/model input graphic until the workflow actually completes and the output is inspected.


## Completed NASA native 29-page input-plot investigation of five difficult cases

[**Successful original unchanged NASA ExoMiner v2.4.0 run #42524313382**](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42524313382) · [Five original NASA input-summary PDFs and MAST DV-report products (artifact 13634628262)](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42524313382/artifacts/13634628262) · [**complete source-by-source original figure review**](NASA_FIVE_PERSISTENT_TESS_ERRORS_ORIGINAL_INPUT_FIGURES_REVIEW_2026_11_08.md).

The **actual** NASA original pretrained model re-scored **5 of 5** persistent disagreement TCEs and generated **29 pages of native input views**: four six-page PDFs and one five-page PDF covering global/local source flux, odd/even events, secondary events, centroid-to-target offsets, momentum-dump flags, periodograms, and source pixel difference/SNR plots (where available). These are direct official NASA ExoMiner model-input diagnostic figures, NOT illustrations invented for this project.

A separate official `dv_reports_all_jobs.csv` lists **9 sets of MAST DV report URLs across five TCE identifiers** (four source IDs with two available report products, and one with one). The report links were found, **not** all followed and independently reviewed. These **five targets were chosen after seeing 2026 scores**, valid for software and physical diagnosis, NOT prospective accuracy inference.

**Important observations**: the original native plots visibly show a periodic narrow dimming for older NPC source TIC `29960109-1-S4` despite NASA's high new score ~0.9934; an obvious central phased primary dip and a phase-local centroid-offset excursion for older EB TIC `165493409-1-S10` despite score ~0.7465; deep/noisy flux and structured variability for older KP TIC `466840711-1-S11` despite score ~0.1373; and only two source event windows (one odd/one even) for older KP TIC `158623531-1-S3` despite score ~0.1836. Old NTP `354518617-1-S6` has strongly structured flux-trend changes, a local-event photometric dip, and a momentum flag, while the original NASA score ~0.9433 stays above the candidate threshold. **These are inspection-based hypotheses only; no independent astrophysical source label confirmation and no quantified transit-caused centroid displacement or correct-model-attribution claim is supported by the images.**

### Discovered cross-version event identity / unit pitfalls

The NASA native source figures led to checking original **pretrained-model-generated ephemerides** rather than only previously archived scores. The original **2025 released labeled TESS table expresses `tce_duration` in DAYS**; the real **2026 v2.4.0 `predictions_spoc-tces_set.csv` expresses `tce_duration` in HOURS**. Any code comparing duration must explicitly multiply original `tce_duration` by 24 before joining it to operational model outputs. No model improvement can be claimed from a unit-handling bug.

Original NASA source measurements also show **TCE identity is not stable solely because the UID string matches**:
- Original KP TIC `158623531-1-S3`: **2025 P=7.87277699 d**, 2026 P=**15.74584579 d**, a **2.000037×** ratio. Epochs align to ~0.00024 d. This is a near-exact 2× period alias (not a guaranteed changed physical source); the score comparison needs an explicit alias flag.
- Original NTP TIC `354518617-1-S6`: **2025 P=8.58721352 d** and 2026 P=**9.40909100 d** (about **+9.57%**), and fitted epochs differ by **0.80920 d**. An identical UID is NOT sufficient to assert an identical fitted signal.
- Original candidate TIC `178155732` **has a direct TCE-number swap**: the 2025 `-1-S4` P=**5.97188044 d** is matched by the 2026 **`-2-S4`** P=**5.97226763 d** (epoch difference ~0.00037 d). Conversely, the 2025 `-2-S4` P=**3.58615947 d** is now the 2026 **`-1-S4`** P=**3.58614111 d** (epoch difference ~0.00012 d). Same-number UID `-1-S4` across releases therefore compares two **different period/epoch candidates**. A model error cannot safely be called resolved or persistent for the same physical signal by comparing that UID alone.

**Consequent qualification of the previously reported 7 resolved / 9 persistent outcomes:** these were entirely valid counts of **agreement with historical labels by raw matched UID strings**, but an identically named row across model versions may be a period alias, new event or transposition. We must separate **source UID agreement** from **signal-ephemeris agreement**, and not inflate or undercount model improvement by pretending these are identical tasks.

The new [cross-version source identity / duration-unit audit](tess_exominer_cross_version_ephemeris_audit.py), [seven identity-focused regression tests](tests/test_tess_exominer_cross_version_ephemeris_audit.py), and [reproducible original-source workflow](.github/workflows/exominer-cross-version-ephemeris-identity.yml) were committed after noticing this issue, as a **post-hoc methodological correction** (not a preregistered performance win). The source-locked 16-case output and any revised counts should be reported **only after the code actually passes and archived source rows are inspected**.

