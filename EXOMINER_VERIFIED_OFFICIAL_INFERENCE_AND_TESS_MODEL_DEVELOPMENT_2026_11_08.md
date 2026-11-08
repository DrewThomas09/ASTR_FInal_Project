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

