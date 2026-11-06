# Deep research audit: current exoplanet methods and failure modes (2024–2026)

Review date: November 6, 2026. Scope: AI-assisted Kepler transit searches and candidate vetting, with TESS methods as a comparison. Status: **literature review and audit only**. This document reports published results and directly visible code limitations; it does **not** claim our method outperformed NASA.

## What is actually new?

The scientific literature already contains (1) statistical detection, (2) transit-shape models, (3) AI classification of vetted signals, (4) pixel- and centroid-level checks, (5) per-transit consistency diagnostics, (6) calibrated false-alarm tests, (7) Bayesian scenario modeling, and (8) human-review/triage workflows. We cannot honestly claim to invent any of those categories.

A defensible new *course project* is a small, transparent and independently evaluated **stress test of AI-generated scientific code**: reproduce a baseline; add one physically motivated robustness/abstention rule; measure whether its incremental benefit is real, and show precisely where it fails. The original contribution is the preregistered comparison, code audit, and negative-case analysis, not a new astrophysical field-wide method.

## A. Recent peer-reviewed/accepted research: what to learn and what can go wrong

### A1. Robnik & Seljak, PNAS 2025 — Null Signal Templates

Paper: "Reassessment of Kepler's habitable zone Earth-like exoplanets with data-driven null signal templates," doi:10.1073/pnas.2513927122 (published Oct. 7, 2025).

**Finding:** The authors construct null-signal templates by perturbing transit times. Inverting light curves fails for asymmetric outliers; scrambling observation blocks may eliminate periodic instrumental artifacts. Their method aims for star-specific false-alarm probability and changed the assessment of several borderline, long-period candidates. The paper discusses Kepler's ~372.57-day spacecraft/orbital artifact and cautions that null models can be wrong.

**Faults to test:** white-noise controls, naive scrambling, flux inversion, sample-specific look-elsewhere correction, one global FAP threshold, confusing "1% FAP" with a 99% probability of a planet, and assuming FAP from instrumental noise also rules out eclipsing binaries.

**Scientific caution:** This is a *specific published method and interpretation*, not proof all previously classified candidates were wrong. Our small undergraduate project should not independently overturn a catalog designation.

Source: https://doi.org/10.1073/pnas.2513927122 ; https://pubmed.ncbi.nlm.nih.gov/41055991/

### A2. Robnik, Seljak, Jenkins & Bryson, MNRAS March 2026 — Transit search at detection limit

Paper: "Exoplanet transit search at the detection limit: detection and false alarm vetting pipeline," doi:10.1093/mnras/stag419 (published March 18, 2026).

**Finding:** Removing localized defects and evaluating whether *individual* transits contribute consistently can improve completeness at fixed false alarm rate. A folded light curve can look convincing although constituent events are measurement discontinuities (illustration: KOI 7894.01). The authors compare a Bayesian test statistic, defect removal, and per-transit checks via injections.

**Important limitation acknowledged by authors:** genuine transit timing variations can trigger a transit-consistency alarm; searches near detection limits may drop real low-SNR, long-period candidates. A diagnostic that protects against spurious dips can also erase real planets. Their reported gains are measured on their injection and vetting setup, not guaranteed for our code.

**Faults to test:** one anomalous transit dominates total significance; folded-only features lose raw event details; automatic removal of discontinuities can suppress real transit; fixed-period ephemeris for TTV systems; "highest BLS peak = discovery."

Source: https://doi.org/10.1093/mnras/stag419 ; code https://github.com/JakobRobnik/exo-probability

### A3. Hadjigeorghiou et al., RAVEN, RASTI Oct. 2026

Paper: "RAVEN: RAnking and Validation of ExoplaNets," doi:10.1093/rasti/rzag080 (published Oct. 19, 2026).

**Finding:** Gradient-boosted trees and Gaussian-process classifiers, trained on simulated transit and eight astrophysical FP scenarios plus real systematic examples, are combined with astrophysical priors. On an external set of 1,361 preclassified TOIs the authors report precision 97% and recall 66% (distinct from their within-simulation AUC values). The first version has design restrictions: TESS SPOC light curves, periods 0.5–16 days, transit depths >300 ppm.

**Faults to test:** high precision masking poor recall; domain restrictions overlooked; synthetic scenario coverage incomplete; planet likelihood treated as if prior independent; comparing AUC from simulations against real catalog labels; probability calibration not transported to a different target population.

Source: https://doi.org/10.1093/rasti/rzag080

### A4. RAVEN large-scale survey, MNRAS 2026

Paper: "Automatic search for transiting planets in TESS-SPOC FFIs with raven," doi:10.1093/mnras/stag512 (2026).

**Finding:** Over 2.2 million TESS stellar light curves searched with BLS + ML + statistical validation. Despite sophisticated screening, additional candidate checks identified signals from neighboring sources, large transit depth changes between sectors, harmonics of true periods outside search range, partial transits near gaps, and low-SNR solutions with poor fits.

**Faults to test:** half/double/triple-period aliases; separate-sector inconsistencies; partial eclipses on gap edges; sources off target; candidate probability computed from a wrong periodic alias; BLS values changing after subsequent physical fitting; incompletely sampled transits; false confidence in single-transit periods.

Source: https://doi.org/10.1093/mnras/stag512

### A5. LEO-Vetter, 2025 preprint

Paper: "LEO-Vetter: Fully Automated Flux- and Pixel-Level Vetting of TESS Planet Candidates to Support Occurrence Rates," arXiv:2509.10619 (posted Sept. 2025).

**Finding:** Uniform automated candidate-screening of TESS signals with flux and pixel-level astrophysical and instrumental tests, designed to support completeness/reliability estimation. The arXiv paper reports 91% completeness and 97% reliability against noise/systematic false alarms in simulated tests; the qualifying reference distribution is critical.

**Faults:** excluding pixel-level information when sky blending is important; transferring simulated performance percentages to the true mission distribution; ignoring that "reliability against noise" is different from excluding astrophysical eclipsing binaries; subjective human vetting influencing the training reference.

Source: https://arxiv.org/abs/2509.10619

### A6. ExoMiner++ (journal Oct. 2025) and 2.0 repository work

Paper: "ExoMiner++: Enhanced Transit Classification and a New Vetting Catalog for 2-Minute TESS Data" (published Oct. 27, 2025); arXiv draft https://arxiv.org/abs/2502.09790.

**Finding:** Adds separate views of unfolded light curves, difference images, spacecraft attitude control, flux trends and periodograms, with transfer learning from Kepler to TESS. The NASA ExoMiner repository also lists a more recent ExoMiner++ 2.0 FFI code release.

**Faults:** our four tabular features miss most causes of nonplanetary detections; Kepler-label transfer to TESS has dataset shift; model performance can depend on how spacecraft attitude and pixel data were preprocessed; complicated systems can be less interpretable.

Sources: https://arxiv.org/abs/2502.09790 ; https://github.com/nasa/ExoMiner

### A7. Kopparapu et al., AJ July 2026 — Instrument-agnostic prioritization

Paper: "Toward Instrument-agnostic Exoplanet Candidate Prioritization," doi:10.3847/1538-3881/ae7d0f (published July 20, 2026).

**Finding:** A study of 11 models using six catalog parameters found that training on Kepler alone or TESS alone produces difficulties on the other mission because the parameter distributions differ. Joint training helped performance across both instruments.

**Faults:** assumption that accuracy generalizes across spacecraft, observing cadence, stellar populations, candidate selection, catalog pipeline versions, or mission thresholds. A model can learn an instrument's sample distribution rather than planetary physics.

Source: https://doi.org/10.3847/1538-3881/ae7d0f

### A8. Salinas et al., MNRAS Feb. 2025 — Transformer-based detection

Paper: "Exoplanet transit candidate identification in TESS full-frame images via a transformer-based algorithm," doi:10.1093/mnras/staf347.

**Finding:** Uses attention and time-series information to detect candidates in light curves without requiring a pre-known period or folded representation. The paper reports 214 new candidate systems including single-transit events.

**Faults:** a traditional BLS search assumes repeated periodic dips and may miss single/few transit events; learned sequence models require more data, careful labeling and safeguards against learning instrumental trends; newly identified *candidates* are not automatically confirmed planets.

Source: https://doi.org/10.1093/mnras/staf347

### A9. NotPlaNET, 2024 preprint — Human-vetting workload

Paper: "NotPlaNET: Removing False Positives from Planet Hunters TESS with Machine Learning," arXiv:2405.18278.

**Finding:** CNN classifies candidate photometric events using light curves, background and centroid information. It measures how many visually inspected examples can be skipped while retaining candidates in the held-out test sectors.

**Faults:** removing a percentage of images for manual inspection is a different task from discovering a planet; a highly selective sample of human-submitted transit-like curves is not the sky-wide population; sector differences and missed candidates matter.

Source: https://arxiv.org/abs/2405.18278

### A10. Astro-Hunters, Aug. 2026 preprint — Label provenance

Paper: "Astro-Hunters: Machine Learning for Exoplanet Transit Detection in TESS Photometry," arXiv:2608.18172. **Preprint**, not treated as peer-reviewed consensus here.

**Finding:** With identical model/features, changing how per-cadence training labels were generated caused much larger performance differences than swapping classifier architectures in this twelve-star experiment. The authors illustrate a near-perfect apparent AUC resulting from circular labels based on the model's own features.

**Faults:** synthetic/artificial labels revealing the answers; mislabeled epochs and timescales; per-cadence classification of transits too weak to resolve without phase folding; evaluating on the same hosts used to derive labels.

Source: https://arxiv.org/abs/2608.18172

### A11. DTARPS, AJ 2024 — Autoregressive search with random forest

Paper: "DIAmante TESS AutoRegressive Planet Search (DTARPS). I. Analysis of 0.9 Million Light Curves," doi:10.3847/1538-3881/ad29f0 (2024).

**Finding:** ARIMA noise treatment, Transit Comb Filter, and a random forest trained on synthetic injected planets and astrophysical distractors. Reported strong in-sample classifier test performance yet markedly lower confirmed-planet recall and many remaining alarms after real-field application.

**Faults:** simulated label distribution does not match real objects; nonstationary noise removal can alter transit shapes; in-sample recall is not out-of-population recall; candidate ranking is not validation.

Source: https://doi.org/10.3847/1538-3881/ad29f0

### A12. 2025 Kepler–K2–TESS transit timing paper

Paper: "Transit ephemerides and timing variations from Kepler and K2 to TESS," doi:10.1093/mnras/staf334 (2025).

**Finding:** Observing the same systems over a longer time reveals timing variations and changes in predicted epochs. Fixed-period templates can drift relative to real transits.

**Faults:** assuming exact period and unvarying transit midpoints; treating an actual timing variation as an instrumental glitch; predicting future transits from stale ephemerides.

Source: https://doi.org/10.1093/mnras/staf334

### A13. 2025 study of background Kepler candidates — Pixel-level validation

Paper: "Background exoplanet candidates in the original Kepler field," doi:10.1051/0004-6361/202451693.

**Finding:** Some centroid tests fail because a light-curve pixel aperture is too small or the field is crowded. A test that cannot be evaluated is not evidence of correct target location.

**Faults:** no centroid data; centroid falsely assumed normal when no adequate pixels; time-varying centroids; neighboring eclipsing binaries mistaken for target planets.

Source: https://doi.org/10.1051/0004-6361/202451693

### A14. 2026 review of Kepler eta-Earth biases

Paper: "Why Estimating eta-Earth Is Difficult: A Kepler-Centric Perspective," doi:10.1088/1538-3873/ae23fe.

**Finding:** Completeness, noise/systematics reliability, astrophysical FP probability, and source positional probability are distinct concepts; the science depends on selection effects and vetting policy.

**Faults:** calling false-alarm and astrophysical FP rates the same thing; comparing paper metrics without matching populations; using raw planet-candidate counts to infer planetary occurrence; taking a catalog disposition as independent confirmation.

Source: https://doi.org/10.1088/1538-3873/ae23fe

## B. Failure-mode register — what can go wrong, how to detect it, priority

Legend: P0 = would invalidate the main claim, P1 = material scientific limitation, P2 = secondary. "Published" means documented in cited work; "code" means checked directly in this repository; "risk" means a plausible issue requiring testing, not something proven to affect this project.

### Detection and signal generation

| Priority | Failure | Status / immediate test |
|---|---|---|
| P0 | Search period preselected near the true answer | CODE: detector default 2.8–3.8d with injected 3.25d; blind random-period holdout |
| P0 | Highest BLS peak always returned, including pure noise | CODE: require control-calibrated detection/review threshold |
| P0 | Only Gaussian white noise in simulator | CODE: inject correlated red noise, instrumental steps, stellar spot modulation and flares |
| P0 | One planet period and one fixed transit epoch in all main tests | CODE: use independent periods, phases, durations and seeds |
| P0 | Incorrect noise standard deviation passed to BLS | CODE: dy fixed to 0.001 even when simulation noise argument differs |
| P1 | Period aliasing at P/2, 2P, 3P or spacecraft harmonics | PUBLISHED: test physical recoveries versus harmonics; inspect both folded solutions |
| P1 | Uniform period spacing undersamples sharp peaks | RISK: compare to Astropy autoperiod/autopower, which uses frequency-aware spacing |
| P1 | Duration grid too coarse or physically implausible | CODE: only 0.08, 0.12, 0.16, 0.20 days; quantify recovery bias |
| P1 | Search assumes regular, repeated transits | PUBLISHED: test single-event, two-event and TTV cases; do not assign reliable period to 1 event |
| P1 | False positives near spacecraft momentum dumps/data gaps | PUBLISHED: inject partial transits adjacent to gaps |
| P1 | Long-term stellar variability creates repeating minima | PUBLISHED: use realistic starspot and quasi-periodic red-noise controls |
| P1 | Outlier removal clips real shallow transits | PUBLISHED: compare sensitivity before/after detrending |
| P1 | Detrending timescale removes long-duration transits | RISK: injection before vs after detrending; mask known transits while flattening |
| P1 | Quarter/sector offsets or flux contamination | PUBLISHED: include per-sector depth consistency when enough data |
| P1 | Even-odd eclipse depths imply binary rather than planet | PUBLISHED: inject unequal alternating eclipse depths and recover odd/even difference |
| P1 | A few instrumental dips dominate apparent multi-transit significance | PUBLISHED: leave-one-transit-out analysis and fraction of score contributed by strongest event |
| P1 | Background eclipsing binary blended with target | PUBLISHED: pixel difference image and centroid tests; light-curve features insufficient |
| P1 | Star radius and dilution unknown, so inferred planet radius is wrong | RISK: report uncertainty; avoid physical confirmation claim |
| P2 | Limb-darkened/grazing transit shape mismatches box | PUBLISHED: optionally compare TLS as *already-existing baseline*, not novel invention |
| P2 | Eccentric orbit produces unexpected duration | RISK: avoid rigid duration cuts without stellar information |
| P2 | Multiple planets and residuals interfere | RISK: inject multi-planet systems and verify iterated search does not overfit artifacts |
| P2 | Saturation/crowded aperture biases flux measurement | RISK: exclude or flag unavailable pixel localization; do not equate missing with pass |

### Training data, labels and cross-mission transfer

| Priority | Failure | Status / immediate test |
|---|---|---|
| P0 | Training labels are NASA *Robovetter judgments*, not independently confirmed planets | CODE: label koi_pdisposition; call outcome agreement with DR25 vetter |
| P0 | KOI-selected sample is not all detections | CODE/RISK: document conditioning on KOI sample; do not report survey-wide completeness |
| P0 | Data leakage via vetting scores, disposition fields, minor flags | CODE: presently avoids those features; add assertions on forbidden columns |
| P0 | The same host appears in train and test | CODE: grouped-by-kepid split; preserve and test |
| P0 | A model copies features that define its own target label | PUBLISHED/RISK: audit provenance, label construction and feature importances |
| P1 | Confirmed planet/planet candidate/FP categories get conflated | RISK: retain precise NASA label definition in all plots |
| P1 | Different observation lengths accidentally predict the label | PUBLISHED/RISK: check if numeric features proxy baseline/cadence/sector |
| P1 | Different class prevalences change precision | RISK: show counts and prevalence; do not export PR without prior adjustment |
| P1 | Long-period/low-SNR stars rare in sample | RISK: grouped subanalysis with n and CI; no significance with sparse groups |
| P1 | Kepler results transfer falsely to TESS | PUBLISHED: validate separately before cross-mission claims |
| P1 | Positive/negative samples sourced from different processing pipelines | PUBLISHED/RISK: provenance-match and test features that encode acquisition source |
| P1 | Features missing centroid/secondary eclipse/pixel data | CODE/PUBLISHED: four-feature model cannot distinguish key astrophysical FPs |
| P1 | No timestamps or quarter IDs to test batch/instrument failure | CODE: Kepler KOI aggregate does not permit quarter-level artifact audit |
| P1 | Incomplete missing data treated as physical zero | CODE: negatives replaced NaN, median imputation; inspect missingness by class |
| P1 | Fitted physical parameters might be uncertain or biased at low SNR | RISK: compare measurement-quality groups; don't treat catalog features as error-free |
| P1 | Disposition labels and archives can be revised over time | RISK: record table/query/download date, hash, source version |
| P2 | Very bright/faint targets and unusual stellar classes shift performance | RISK: include magnitude/type if available, but adding columns changes design |
| P2 | Catastrophic confidence for out-of-distribution cases | RISK: calibrated abstention and OOD checks, never extrapolate confidence blindly |

### Metrics and statistical interpretation

| Priority | Failure | Status / immediate test |
|---|---|---|
| P0 | Comparing methods on different test populations or metrics | CODE/RISK: paired held-out predictions on identical stars and same labels |
| P0 | Claiming real-data results using synthetic tests | CODE: actual NASA training has not been verified |
| P0 | Presenting validation recall as test recall | CODE: cutoff set on validation only; report untouched test separately |
| P0 | Calculating confidence after looking at held-out results repeatedly | RISK: preregister design and freeze holdout; no iterative test tuning |
| P1 | High accuracy hides misses in a rare class | RISK: report TP/FP/TN/FN, recall, precision, FPR, PR curve and prevalence |
| P1 | AUC averaged over easy examples hides long-period failures | RISK: period/SNR subgroups with denominators |
| P1 | Random-forest output treated as calibrated true planet probability | RISK: probability calibration test and reliability curve on validation only |
| P1 | "We flag fewer" achieved by discarding real candidate signals | RISK: match recall or show full tradeoff |
| P1 | Abstention appears to improve accuracy by discarding hard cases | RISK: include all cases in totals; report coverage vs error/review cost |
| P1 | Binary label agreement mistaken for scientific discovery/validation | RISK: external confirmations and noise controls separately |
| P1 | Single train/test split hides high outcome variance | RISK: repeated grouped splits or host-level bootstrap, report CI and seed |
| P1 | Multiple period trials generate look-elsewhere false alarms | PUBLISHED: use null distribution of *max* search statistic, not single-trial p |
| P1 | Naive inversion/scramble changes artifact distribution | PUBLISHED: PNAS 2025 NST critique; controls must preserve relevant structure |
| P1 | FAP vs astrophysical FPP vs posterior planet probability conflated | PUBLISHED: label each distinct outcome |
| P2 | False positives counted per row when several KOIs share a star | RISK: both star-level and event-level denominators |
| P2 | No uncertainty bars on small subgroup differences | RISK: clustered CI; flag inconclusive results |
| P2 | Missing CPU/runtime reproducibility | RISK: time inference on same hardware, log compute/version |

### Software engineering and AI research integrity

| Priority | Failure | Status / immediate test |
|---|---|---|
| P0 | AI-written tests validate only that Python runs, not astronomy | CODE: require physical invariants and independent published benchmark |
| P0 | BLS demo and catalog ML are separate, not integrated end-to-end | CODE: clearly distinguish from true raw-data vetting pipeline |
| P1 | Notebook silently reports synthetic outputs in the real-data section | RISK: fail closed on failed NASA download; label outputs by source |
| P1 | Runtime library changes alter results | RISK: pin and record versions, fixed random seeds, save exact input query |
| P1 | User claims software reduces professional labor with no workload study | RISK: report only fraction flagged as proxy |
| P1 | Claiming originality for per-transit checks, calibration or transformers | PUBLISHED: methods existed; novelty is constrained ablation study |
| P1 | Auto-generated prose includes invented evidence | RISK: every number traceable to output or cited paper |
| P1 | Public repository exposes personal data or secrets | CODE: repo public at last verified check; never upload keys or private documents |
| P2 | Colab internet/limits make full light-curve tests infeasible | RISK: use a 10–30 star real-data subset, tabular DR25 as core |
| P2 | Time/date conversions between missions cause wrong epochs | RISK: check BKJD/BTJD/Julian Date offsets and flux normalization |

## C. Strongest and most feasible scientific experiment (revision)

**Question:** Can a simple, independent *transit-consistency warning* or *uncertainty-aware review option* detect misleading Kepler signals without unnecessarily rejecting weak candidates?

### Stage 0 — Ground truth must be stated precisely
- The Kepler DR25 KOI table provides **historical vetter labels** for a selected set of signals, not independently verified truth about every planet.
- Synthetic injection experiments provide known true transit properties by construction but depend on how realistically we model noise.
- A small set of confirmed Kepler planets provides external real-light-curve sanity checks but cannot estimate survey-wide reliability.
- Keep these outcomes separate throughout the report.

### Stage 1 — Reproduce the current ML baseline on real NASA DR25
- Four features: orbital period, duration, depth, model SNR.
- Exclude all disposition/vetting fields and object IDs as predictors.
- Train/validation/test grouped by host star.
- Measure full held-out confusion matrices, false-positive rate, candidate recall, precision and review fraction.
- Preselect period/SNR bins and report n per bin.
- If the real NASA CSV fails to load, report the blocker and do not manufacture results.

### Stage 2 — Add exactly one interpretation layer to the catalog model
Option A, least effort: set a **review zone** around decision scores or between conflicting base classifiers; report fraction requiring review and error rate among *auto-decided* cases. Compare with an SNR-only and plain forest review zone at matched coverage and recall. This is selective prediction, not a planet probability or validation.

Option B, more astronomical (only with real light curves): calculate per-transit agreement on a fixed period and test the score before/after dropping the single strongest event. Compare signal candidates to injected shallow planets, red-noise and outlier controls. **It cannot be computed from the present four KOI columns**. This avoids pretending an unmeasured diagnostic exists.

### Stage 3 — Correct the transit experiment to avoid answer leakage
- Inject blinded periods from a preregistered range 1–20 d and phase/duration/depth varied independently.
- Use Astropy's frequency-aware period grid.
- Evaluate noise-only, red-noise, isolated-dip, binary-like alternating-depth and gap-edge controls.
- Separate "a strongest peak exists" from "detection threshold passed."
- Report alias-aware period recovery and false alarm frequency by control category, plus runtime.

### Stage 4 — Decide whether the extension helps
- Primary effect: change in false-positive rate at approximately fixed candidate recall or change in confidently wrong automatic decisions at matched review fraction.
- Estimate confidence by bootstrapping by host star for real KOIs and by independent simulated star for injections.
- Study long-period and weak-SNR cases, but if few examples remain, label inconclusive.
- Keep original code and conditions so every change can be ablated fairly.

**No promise:** The extra layer may be worse than the baseline, especially for true TTV planets or when model scores are not calibrated. That negative result is meaningful.

## D. Ranked next tasks

1. **Immediate / P0:** run real NASA DR25 experiment, save query and label counts, baseline metrics and CSV hash.
2. **Immediate / P0:** fix narrow BLS search and fixed injected period; add control-calibrated significance decision, multi-period tests.
3. **Next / P1:** add subgroup table (period, SNR, counts) and proper host-bootstrap uncertainty.
4. **Next / P1:** add controlled abstention/triage to forest, with matched coverage comparisons.
5. **Stretch:** inspect individual transits of selected *real* Kepler stars and run a simple leave-one-transit-out check; do not claim end-to-end feature integration.
6. **Later, not needed for final:** real-noise Kepler injection/recovery and pixel-level contamination analysis.
7. **Not recommended:** train a new CNN/transformer, claim first false-positive filter, train on disposition score, or run a million-star survey.

## E. Source key: primary and recent references

- Robnik & Seljak (2025), PNAS, Null Signal Templates: https://doi.org/10.1073/pnas.2513927122
- Robnik et al. (2026), MNRAS, detection-limit pipeline: https://doi.org/10.1093/mnras/stag419
- Hadjigeorghiou et al. (2026), RASTI, RAVEN: https://doi.org/10.1093/rasti/rzag080
- RAVEN survey (2026), MNRAS: https://doi.org/10.1093/mnras/stag512
- Kunimoto et al. (2025), LEO-Vetter preprint: https://arxiv.org/abs/2509.10619
- Valizadegan et al. (2025), ExoMiner++: https://arxiv.org/abs/2502.09790
- Kopparapu et al. (2026), AJ, cross-instrument learning: https://doi.org/10.3847/1538-3881/ae7d0f
- Salinas et al. (2025), transformer transit search: https://doi.org/10.1093/mnras/staf347
- Poleo et al. (2024), NotPlaNET preprint: https://arxiv.org/abs/2405.18278
- Eldin (2026), Astro-Hunters preprint: https://arxiv.org/abs/2608.18172
- Melton et al. (2024), DTARPS: https://doi.org/10.3847/1538-3881/ad29f0
- Kepler/K2 to TESS TTV study (2025): https://doi.org/10.1093/mnras/staf334
- Background Kepler centroid study (2025): https://doi.org/10.1051/0004-6361/202451693
- Kepler demographic uncertainty (2026): https://doi.org/10.1088/1538-3873/ae23fe
- Thompson et al. (2018), DR25 catalog vetting: https://doi.org/10.3847/1538-4365/aab4f9
- Astropy BLS documentation: https://docs.astropy.org/en/stable/timeseries/bls.html
- NASA historical KOI catalog documentation: https://exoplanetarchive.ipac.caltech.edu/docs/PurposeOfKOITable.html

## F. Provenance of claims in this file

- The studies' methods and reported statistics are **published-author claims** and are not yet reproduced by this student project.
- The file/line issues referring to exoplanet_detector.py and ml_screening.py were confirmed by reading the current GitHub source on 2026-11-06.
- The failure-mode register contains many **risks to test**, not proven defects. Only code-tagged items are directly observed defects.
- The proposed experimental improvement is a **new implementation and comparison for this course project**, not a novel published astronomical technique.
