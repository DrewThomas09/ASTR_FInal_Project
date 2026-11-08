# ExoMiner / ExoMiner++ Full Technical Audit and Honest Replication Roadmap
**ASTR / PHSC 12600 | Source-verified research review | November 8, 2026**

**Scientific classification task:** NASA's ExoMiner models primarily **vet** threshold-crossing events (TCEs) that an upstream Kepler/TESS search and data-validation pipeline already found. They do **not** on their own establish a wholly new search over untouched telescope pixels, and candidate classification does **not** equal independent spectroscopic planet confirmation. This file must never treat our Kepler 4-feature random forest as ExoMiner or present incomparable balanced-accuracy values as a head-to-head challenge.

## 1. Three major generations and actual outcomes

### Original ExoMiner: 2021 paper / 2022 journal, original Kepler

Publication: Valizadegan et al. (2022), *ExoMiner: A Highly Accurate and Explainable Deep Learning Classifier that Validates 301 New Exoplanets*, https://arxiv.org/html/2111.10009 (original arXiv Nov 2021; ApJ 926:120 in Feb 2022).  NASA news: https://science.nasa.gov/universe/exoplanets/new-deep-learning-method-adds-301-planets-to-keplers-total-count/.

- **301 new planets statistically validated** from previously available Kepler candidates after applying high-confidence automated vetting and validation criteria. Statistical validation is not the same as a fresh radial-velocity dynamical mass measurement.
- At a strict **99% test precision** decision operating point, the model had **93.6% planet recall**, compared with **76.3%** for the strongest classifier in that paper's benchmark. This is recall on their study's vetted labels and splits, not an all-star raw-signal search completeness number.
- The team subsequently used a **multiplicity boost** on multi-planet hosts to statistically validate another **69** exoplanets. NASA's January 2026 public summary cites **370** ExoMiner-validated Kepler planets as an aggregate historical outcome: https://science.nasa.gov/open-science/deep-learning-exoplanets-tess/.
- Key design: multiple specialized branches derived from expert Data Validation reports; full-orbit 301-point light curve, 31-point local transit, odd/even, secondary eclipse, stellar/diagnostic scalars and **centroid-related diagnostics**, with individual branch outputs fused before the final sigmoid planet confidence. Original illustrated architecture: https://ntrs.nasa.gov/api/citations/20220013180/downloads/Jenkins_IEEE_SPIN_2022_Aug_26_2022.pdf.

### ExoMiner++: TESS 2-minute cadence 2025 study

Valizadegan et al., *ExoMiner++: Enhanced Transit Classification and a New Vetting Catalog for 2-Minute TESS Data*, AJ 170:287, https://arxiv.org/html/2502.09790. Official source: https://github.com/nasa/ExoMiner; published study data Zenodo DOI https://doi.org/10.5281/zenodo.15466292.

- Processed approximately **204,729** TESS SPOC TCEs across the first 67 TESS sectors and 85 transit-search runs; 57,162 were labeled for supervised comparison, while **147,567** retained an **unknown/uncertain** label for prospective candidate vetting (paper Section VII).
- Its labeled TESS subclass set included **3,681 exoplanet-class TCEs** and **53,481 nonplanet-class TCEs**, with known planets (KP), confirmed planets (CP), brown dwarfs (BD), eclipsing binaries (EB), astrophysical false positives (FP), and nontransiting phenomena (NTP). *TCE rows are not all independent planets*: the same event can appear in different overlapping sectors. See paper Tables 2–3.
- With **Kepler+TESS multi-source training and longer-sector-run aggregation**, the paper's **best reported labeled TESS comparison** achieved **precision 0.933**, **recall 0.951**, **PR AUC 0.976**, **ROC AUC 0.998**, **accuracy 0.992** (paper Table 6). These are conditional on selected **labeled TCEs**, not future unknown-candidate confirmation precision.
- For **147,567 unknown TCEs**, the model classified **7,330 TCE observations as possible planet candidates**. These should NOT be called newly discovered/confirmed exoplanets. Many matched existing catalog TOIs; after matching previously known candidates and applying additional conservative rules, the authors produced a much smaller follow-up shortlist.
- In a limited **later label-update sanity check**, 147/151 subsequently confirmed-planet TCEs and 95/142 subsequently false-positive TCEs were classified correctly (paper Section VII). This is informative but not a controlled real-sky incident discovery benchmark; the paper reports approximately 0.76 precision and 0.97 recall within that selected label-change subset.
- Architectural extensions include **unfolded individual transits** (20 × 31), **pixel difference images** (off-target contamination), **periodograms**, **flux trends**, and **momentum-dump/spacecraft artifacts**, in addition to original views. The paper compared convolutional individual-event extraction against a transformer and found the convolutional design better in its experiment. Its branch ablation used TESS-only data: baseline **PR AUC 0.897**; add flux trend **0.923**; difference images **0.904**; periodogram **0.911**; unfolded flux **0.913**; momentum dump **0.897** (Table 11). **These are baseline-plus-one-branch tests; do not sum the gains.** The momentum branch showed little benefit, partly because few relevant TCEs survive the upstream data pipeline.

### ExoMiner++ 2.0: TESS full-frame-image study, January 2026

Martinho et al. (2026), *ExoMiner++ 2.0: Vetting TESS Full-Frame Image Transit Signals*, https://arxiv.org/html/2601.14877; official repository has a `v2.0.0-arxiv` release and a later operational v2.1 model spec.

- Extends TESS TCE vetting to **full-frame-image (FFI)**-derived SPOC events, increasing available sky coverage and complexity of blended sources, with **neighbor-star brightness/location image encoding** to target off-star false positives.
- On the paper's multi-source evaluation, reported **FFI PR AUC about 0.952** (versus 0.967 on the compared 2-minute source dataset). On a five-fold combined-source comparison at a threshold of 0.5, the **old ExoMiner++** showed PR AUC **0.962**, precision **0.913**, recall **0.912**, whereas **2.0** showed PR AUC **0.958**, precision **0.922**, recall **0.865**. Improvements were subclass-specific; 2.0 **did not win every global metric**. Paper Tables 3 and 6. Do not conflate the 2025 v1.0.0 training population with the 2026 v2.1 deployment inputs.
- Paper reports **2,831 previously unlabeled FFI TCEs with score >0.5** and 447 with score >0.95, but no unknown TCE with >0.99 in that study. These are **TCE candidate rankings**, not confirmed independent exoplanets.

## 2. What is currently actually deployed: model specification (June 2026)

Official model card: https://github.com/nasa/ExoMiner/blob/main/docs/models_specs.md (published **June 2026**, pipeline **v2.1**). Run guide: https://github.com/nasa/ExoMiner/blob/main/docs/running-exominer-pipeline.md.

**Two distinct current scoring tasks** (not one unqualified universal planet-probability estimator):

- **Planet validation**: binary Planet / Not-Planet model, weighted cross-entropy, 10-fold CV, newer dataset of TESS SPOC 2-minute sectors 1–98 (internal training example description ~13% planet).
- **Photometric vetting**: three outcomes **PC** (planet candidate), **AFP** (astrophysical false positive), **NTP** (non-transiting phenomenon), with a different sector 1–98 training composition and unweighted loss.

**Reported v2.1 inputs** (not interchangeable with 2025 paper's shapes):
- Local phase-folded flux **[31,1]**, global flux **[301,1]**; odd/even 31-point local views; weak secondary 31-point; local centroid [31,1]; unfolded independent transit event stack **[20,31]**.
- Flux-trend view **[301,1]**; normal and momentum-related periodograms **[674,1]**; local momentum artifact view **[31,1]**.
- Pixel difference image, out-of-transit image and image-SNR arrays **[55,55,5]** each, together with image quality information; pixel stack requires relevant original mission products, not scalar flux alone.
- Stellar and DV/TCE scalars (period, number observed/expected transits, signal significance, morphology, estimated radius, Gaia RUWE and other measures). Precise field names in the official card.
- Multi-input 1D/2D/3D CNNs and scalar branches, fused in a dense classification head; the model card reports **1,424,003 trainable parameters** for the described individual network, and learning rate ~4.176e-5, PReLU, Adam and crossentropy.
- Deployment supports a **single model**, ~10-model averaged CV ensemble, and ~100-model full CV ensemble, which the run guide describes as increasingly robust but more computationally costly. Ensemble spread is epistemic disagreement, *not* a physical probability of contamination.
- An integrated official **Podman** pipeline accepts `tic_id, sector_run` CSV, retrieves public TESS SPOC light curves and DV XML plus stellar properties, preprocesses/normalizes inputs, then loads pretrained model and writes scored TCE tables. Official command to inspect arguments: `podman run ghcr.io/nasa/exominer --help`. The official guide also supports local Python execution and custom compatible Keras models.

**Important experimental constraint:** do not feed our Kepler Q6 PDCSAP or our four-dimensional `ml_screening.py` table into the TESS ExoMiner++ model and describe the output as valid ExoMiner scores. Its mission-specific TCE identifiers, data-validation products, normalization transforms and tensor dimensions are essential.

## 3. Exact current state of our ASTR project versus ExoMiner

| Research stage | Our ASTR code and verified scope | NASA's system | Gap to close |
|---|---|---|---|
| Transit proposal | `blind_transit_benchmark.py` / `real_kepler_lightcurve.py` run Astropy BLS on normalized quarter-level flux; a few known source periods checked | SPOC TPS creates TCEs from multi-sector photometry and documents event/centroid diagnostics | Multi-quarter detection completeness, robust search, physically vetted TCE distribution |
| Training labels | `ml_screening.py` uses **8,054 Kepler DR25 historical KOI labels** CANDIDATE vs FALSE POSITIVE; already selected by NASA pipeline | Kepler/TESS vetted TCE labels; false positives broken into multiple physical subclasses; some later labels use external follow-up | Our historical KOI binary label is NOT confirmed physical planetary truth or same dataset |
| Feature space | Just **four numerical values**: period, transit duration, depth, model SNR | 20×31 individual-event stack, 301/31 folded flux, odd-even, secondary, centroid, pixel images, quality/periodogram, stellar/DV scalars | Multi-view time series and pixels are entirely missing from our classifier |
| Model | Median-imputed **120-tree, max depth 9 random forest**; simple logistic and SNR controls | Multiple specialized convolutional branches + dense fusion; 1.42M trainable parameters in v2.1 single network | A random forest cannot be described as an ExoMiner implementation |
| Validation | **1,619** heldout historical KOIs / **1,385** distinct stars. Forest BA 81.29%, logistic 76.61%, SNR 50.23%. Host paired permutation significant but dataset and main split pre-explored | Cross-validation grouped by target/event, independent labels/diagnostics; high precision operating points and subclass studies | Same split, TCE population, ground truth and calibration needed for a valid head-to-head |
| Signal preservation | `recurrence_guard_q6.py` protected two already-known **stellar eclipses** and 42 original cadences on 13 stars; no new labeled instrument SPSD positives in holdout | Official pixel/quality/systematics vetting is integral to preprocessing | Need strong real SPSD controls, genuine planetary transit injection recovery |
| Physical generalization | `q6_to_q7_blind_ephemeris_validation.py` Q6-BLS predicts Q7 transit-like dimming on six of nine available planet hosts, **and on both known stellar binary controls** | Separate planetary vetting beyond period coherence | Future-quarter prediction tests periodicity, **not planet identity** |
| Multi-signal search | `iterative_bls.py` exploratory subtraction recovered known signals in selected multi-planet systems but also aliases | SPOC TCE creation and ExoMiner vetting work across multiple candidate events | Disjoint source validation and prevention of duplicate/alias detections |
| Overall end-to-end success | No measurement yet of **more real/injected planets at identical empirical false alarms** | Large-scale trusted mission software + published catalogs | True central science/engineering benchmark |

**No scientifically valid cross-project statement:** “our 81% vs NASA's 99% means NASA is 18 points better” or “our paired p-value means we improved on ExoMiner.” These use *different datasets, class proportions, label provenance and tasks*.

## 4. A practical three-layer replication plan — same official outputs first

### Layer A — exact pretrained ExoMiner++ inference (most important first)

1. Pin an exact published **official commit/tag, model file hash, and compatible dataset** for one selected task. **Recommended first target: the TESS 2-minute `planet-validation` task** with the official model and release data; *do not* jump between 2025 study inputs, 2026 2.0 FFI manuscript and June 2026 v2.1 without recording their differences.
2. Acquire a **small, externally chosen TESS SPOC TCE target set** (e.g. 20 known KPs, 20 catalog FPs, 20 EBs, 20 NTPs selected with fixed seed, same sector-run selection policy). Include external catalog identifiers and full original provenance before inspecting model scores. This is a **sanity check**, not independent published accuracy inference.
3. On a computer with supported Podman, run the **unchanged NASA `ghcr.io/nasa/exominer`** image (or installed Python source). Input one `tic_id,sector_run` CSV and initially a **single pretrained model**. The exact official guide supplies volume maps and CLI options; the image is not bundled in our GitHub and **has not yet been run**. Expected verified output is `predictions_spoc-tces_set.csv`, per-TCE inputs, logs and provenance.
4. Repeat with the 10-model and 100-model ensembles **on identical TCEs**, optionally computing disagreement; never claim that higher inference model counts represent independent astrophysical evidence. This would be a real ExoMiner++ **replication of pretrained scoring**, not our own trained equivalent.

### Layer B — rebuild and fairly evaluate a compact multi-view model

1. Use the **original released preprocessed TESS input examples** from the correct matching ExoMiner++ study/Zenodo release, with strict target-star/group-wise folds. On Kepler, produce our own small **ExoMiner-inspired** view extractor for engineering only; do not claim its output equals NASA's exact normalized tensors.
2. Compare on **same folds and same label definitions**, sequentially:
   - Four-scalar RF/logistic baseline.
   - 301/31 folded flux CNN or small gradient-boosted model using measured shape features.
   - + odd/even and secondary eclipse views.
   - + **20×31 unfolded individual transits** to detect inconsistent single events and aliases.
   - + periodogram and source-quality/trend summaries.
   - + target pixel / difference-image contamination diagnostics.
3. Evaluate **PR-AUC, ROC-AUC, precision/recall at fixed high precision, calibration, class-specific EB/AFP/NTP errors**, and long-period/low-MES subsets. Do not choose thresholds from final test stars.
4. Only when identical dataset/task are available compare directly with the **unmodified NASA official model predictions** on those exact observations. Our smaller Kepler KOI catalog model remains a separate descriptive baseline otherwise.

### Layer C — potential real research contribution, not another model size contest

**Recommended feature:** an **event-level instrumental-change versus repeating astrophysical-event confidence branch** inspired by our real Kepler-35/-1647 eclipse failures.

Candidate views: per-transit ingress/egress local recovery; persistence after the event; individual transit train consistency; quality flag changes, spacecraft pointing/momentum coincident triggers; nearest transit pixel-centroid shift. It could produce three physical outputs **planetary-like**, **stellar-eclipse-like**, **instrument-change-like**, with explicit **abstain** on ambiguous cases. However, the current TESS ExoMiner++ already has unfolded-transit, momentum/periodogram, pixel/centroid branches: novelty must be established as an **incremental, statistically measurable alternative to those particular existing features**, not as if no one thought of individual events or instruments before.

Two credible success endpoints:

- **Classification extension:** after freezing a same-version ExoMiner++ model and TCE population, measure a **paired improvement in PR-AUC or recall at ≥99% heldout precision** (with a separate threshold calibration group), especially on *instrument-versus-EB hard negatives*. A small class-conditional gain that survives stellar/pixel holdouts is worth reporting; an improvement on one preselected EB is not.
- **Upstream detection extension:** compare our reversible event-aware search against BLS/TLS on **genuine original Kepler/TESS light curves with limb-darkened injected planets** and both real/controlled artifact negatives, measuring **injected planet recovery at the same calibrated alert/FAP budget**. This can complement ExoMiner; it is not an ExoMiner replacement because it operates *before* the model's TCE stage.

**Statistical safeguards:** independent hosts and independent observing periods; separate training/threshold-calibration and final holdout; fixed source IDs and seeds; grouped confidence intervals; true physical injection labels; no post-selection tuning; published negative and unavailable sources; no reusing past Kepler-34/-35/-47 development examples as fresh validation; avoid grouping repeated sector TCE observations as independent new exoplanets. For a post-hoc candidate review, link host and ephemeris and never relabel a near-half-period binary as a newly found planet.

## 5. Practical resource estimate and next actual actions

- The official v2.1 model card lists **~1.424M** parameters in one neural net. The official guide says **single ~1.5M, CV ensemble ~15M, full CV ensemble ~150M total parameters**; the latter are many separate models, not one giant 150M-parameter network. Computer/CPU inference is feasible for a few examples using the published container with memory overhead, while faithful **multi-branch training and complete CV** demands larger preprocessed data and serious GPU/CPU resources. The 2025 paper reports early stopping within 300 epochs and ~80 seconds per model epoch on V100 GPUs for its training setup; **that is a historical paper setup, not a guaranteed runtime or cost for our environment**.
- **Next executable step:** create a **clearly non-NASA-compatible prototype** for local/global flux, odd-even, secondary and 20×31 individual events using our genuine Kepler light curves; preserve empty-bin masks and source hashes. This validates physical input representation without misrepresenting the output as ExoMiner++ inference.
- **Next actual ExoMiner replication:** run the unchanged pretrained NASA container on a small, frozen, TESS-specific TIC-and-sector TCE list, save **real official predictions CSV**, compare with available public benchmark rows, then pin hashes. A 0.99 model score is not automatically a scientifically calibrated 99% posterior planetary probability across all sky populations.
- **Next independent improvement test:** decide *before training* whether the main goal is classifying given TCEs better **or** recovering new planets from raw light curves. These are distinct competitions. Given our observed astrophysical/data-loss problem, prioritize **event-safe detection upstream**, then ExoMiner-compatible candidate vetting second.

## Sources (verified on Nov 8, 2026)

1. Valizadegan et al. (2021/2022) original: https://arxiv.org/html/2111.10009
2. NASA original announcement: https://science.nasa.gov/universe/exoplanets/new-deep-learning-method-adds-301-planets-to-keplers-total-count/
3. NASA 2026 cumulative 370 and ExoMiner++ candidate update: https://science.nasa.gov/open-science/deep-learning-exoplanets-tess/
4. Valizadegan et al. (2025), 2-minute ExoMiner++ paper Tables 2, 3, 6, 11 & Section VII: https://arxiv.org/html/2502.09790
5. Martinho et al. (2026), FFI 2.0, Tables 3, 6, 7: https://arxiv.org/html/2601.14877
6. NASA ExoMiner official public code and project definition: https://github.com/nasa/ExoMiner
7. NASA June 2026 **v2.1** model specifications and exact feature tensor dimensions: https://github.com/nasa/ExoMiner/blob/main/docs/models_specs.md
8. Official Podman command, task, TIC input and model ensemble options: https://github.com/nasa/ExoMiner/blob/main/docs/running-exominer-pipeline.md
9. Released 2025 preprocessed source data: https://doi.org/10.5281/zenodo.15466292
10. Current local comparison results: [NASA DR25 label agreement](VERIFIED_DR25_PAIRED_SIGNIFICANCE_2026_11_08.md), [true observed stellar eclipse behavior](VERIFIED_RECURRENCE_PROTECTED_STELLAR_ECLIPSES_2026_11_08.md), [blind quarter-to-quarter physical predictive study](Q6_TO_Q7_BLIND_PREDICTIVE_VALIDATION_FROZEN_2026_11_08.json).

**AI use:** GPT-6 assembled the reference review, comparison and replication roadmap, and assisted original project coding. Student must personally verify all source claims, methods and numerical results and disclose AI use to the instructor.
