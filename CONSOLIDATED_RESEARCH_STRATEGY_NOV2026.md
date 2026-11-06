# Consolidated research strategy: AI-assisted exoplanet detection
Date: 2026-11-06 | ASTR 12600 | Research / methodology decision record

**Status:** Literature and code audit; **not evidence that our new models beat NASA or discovered planets**.

## Executive synthesis

After reviewing foundational exoplanet searches, modern Kepler/TESS vetting, October 2026 publications, and adjacent research on anomaly detection, uncertainty calibration, selective prediction and reproducibility, the best defensible idea for this class project is:

> **Can AI-assisted, physically motivated reliability checks help a conventional exoplanet search distinguish stable transits from misleading signals, and improve which ambiguous candidates are sent for human review at a fixed review budget?**

The student's novel contribution is a **careful ablation and failure-case analysis of a small reproducible pipeline**, not a previously unseen class of exoplanet detector. AI generates research code and can implement an ML classifier; *scientific correctness* is assessed independently with simulations, published objects, and untampered test data.

### Five major realizations (our inferences, not quotations from papers)

1. **Correcting the input can matter more than using a fancier classifier.** Robnik et al. (2026) show very large detection-recovery benefits from targeted local-defect removal, while their Bayes-factor statistic adds comparatively modest additional recovery under the same test conditions. This is an argument to prioritize proper noise and event modeling, not assume a deep network will solve bad photometry.
2. **Detection, noise rejection, astrophysical validation and telescope follow-up are four different decisions.** Signal BLS power is not a noise-only FAP; a small FAP does not exclude an eclipsing binary; a Kepler 'CANDIDATE' label is not an independently confirmed planet. Different diagnostics and ground truths are needed at each stage.
3. **The missing information is often physical, not a missing layer of machine learning.** Aggregate DR25 period, depth, duration and SNR cannot encode whether a nearby eclipsing binary caused the event, nor whether one instrumental dip dominated a folded curve. ExoMiner++ adds difference images, attitude signals, and unfolded flux; exoVetter employs pixel-level/centroid checks. With only four scalar inputs, any ML result faces an information ceiling.
4. **Evaluation design is a central scientific contribution.** Adjacent time-series anomaly detection studies (Xu & Bostrom 2026) show that test-set threshold tuning, modified benchmarks and weak baselines routinely make apparent advances unreproducible. Our own early BLS demonstration had the answer embedded in a 2.8-3.8 day search for a 3.25-day injected period. Fixing this is more scientifically valuable than adding another ensemble architecture.
5. **An economical review decision can be more useful than a perfect-looking score.** A candidate classifier serves an allocation problem: with a limited follow-up budget, how many historically credible signals can be retained, and how many known false-positive signals can be avoided? Decision thresholds and human-review fractions must be compared **at equal budgets and matched candidate recall**. This framing fits the student's statistics/economics interests.

## A. Comparative methods matrix (what is good, where it fails, should we use it?)

| Layer or method | Leading literature and results | Principal fault / invalid extrapolation | Feasibility and recommendation |
|---|---|---|---|
| **BLS** periodic transit search | Kovacs et al. 2002; Astropy implementation. Fast simple baseline on photometric light curves | The maximum periodogram peak exists even for pure noise; rectangular shape, period aliases, sparse coverage, and correlated noise cause false signals | **Core baseline**; make it blind, use Astropy's frequency-aware autopower, matched controls |
| **Kepler TPS / Robovetter** | Jenkins et al. 2010; Thompson et al. 2018; uniform multi-test DR25 vetting | Reliability/completeness vary with SNR and period; noisy/astrophysical false positives need different tests; labels are algorithmic outcomes | **Reference comparator**, not a system to beat wholesale |
| **Transit Least Squares** | Hippke & Heller 2019; physically realistic limb-darkened template | More compute, helps signal-shape matching but does not by itself distinguish instrumental or binary FPs | **Optional shape baseline**, not required to pass |
| **Localized-defect removal + event vetting** | Robnik et al., MNRAS Mar. 2026: injection into real Kepler light curves, individual transits, significance consistency | Can reject true planets with transit timing variations (TTV); noise templates cannot capture every defect; complicated end-to-end | **Highest physical value**, implement small diagnostic and negative controls; don't claim original invention |
| **Null Signal Templates (NST)** | Robnik & Seljak, PNAS Oct. 2025; empirical star-specific false-alarm estimation | Requires correct null perturbation and whole-search calibration; old inversion/scramble nulls can miss instrumental behavior | **Research benchmark / stretch**; cannot call current simple null threshold a real FAP |
| **LEO-Vetter** | Kunimoto et al. 2025/2026: flux and pixel-level tests, simulated injection/recovery | Simulated noise reliability is not same as actual astrophysical FP exclusion; can be difficult without pixel products | **Methods checklist**, potentially use existing diagnostics before coding new ones |
| **exoVetter** | Dallas et al., PASP Oct. 2026: modular photometric and centroid diagnostics; tested on 324,530 TESS light curves with Kepler reference stars | "Kepler as ground truth" is strongest when a signal is independently known, but KOI catalog status is still not perfect truth; may need image products | **Top practical inspiration**; consider official code as reference, don't reimplement all tests |
| **McCauliff RF / current four-feature forest** | McCauliff et al. 2015, and our DR25 four-feature baseline | KOI label mimicry; missing centroid, secondary eclipse, unfolded time series; class selection bias | **Required basic ML comparison**, but not sufficient to establish a better detector |
| **AstroNet / ExoMiner / ExoMiner++** | Shallue & Vanderburg 2018, Valizadegan et al. 2022/2025; strong neural classifier work with richer diagnostics | Expensive training data, specialized inputs and labels, Kepler to TESS distribution shift; a neural score is not a new discovery | **Read and cite, do not retrain**; borrow error taxonomy |
| **RAVEN** | Hadjigeorghiou et al. Oct. 2026 RASTI: scenario-specific simulated ML, Bayesian priors; 97% precision but 66% recall on 1361 external TOIs at specified threshold | High precision may hide many misses; defined mission/period/depth operating domain; prior assumptions | **Performance interpretation reference**; show precision–recall/review tradeoff |
| **CNN single-transit detection** | Salinas et al., Oct. 2026 arXiv preprint: synthetic-trained CNN vs trapezoidal baseline on 120 confirmed planets | Periodic BLS cannot characterize single events; preprint and selected sample; synthetic calibration not survey validity | **Outside scope**, cite as explicit blind spot |
| **Cross-mission domain adaptation** | Kopparapu et al. July 2026; Kepler-only or TESS-only models underperform cross-mission, joint training improves | Instrument shift undermines confidence transfer; labels and selection differ | **Limit claims to Kepler** |
| **Gaussian-process stellar variability** | Aigrain & Foreman-Mackey 2023 review | Modeling can absorb shallow real transit if misconfigured; compute complexity | **Noise rationale**, not necessary to train a GP |
| **Selective classification / abstain** | Geifman & El-Yaniv 2017, 2019 | Declining difficult cases lowers automatic error even if the core classifier is unchanged; review fraction must be charged | **Recommended measurable ML extension**, evaluate risk–coverage |
| **Conformal prediction** | Angelopoulos & Bates 2023; Walls et al. 2026 on radio galaxy ambiguous labels | Marginal coverage assumptions include exchangeability and accurate reference label; shift/ambiguous labels can invalidate intended interpretation; not a planet-probability guarantee | **Optional interpretation, not minimum build** |
| **FDR / repeated testing** | Benjamini & Hochberg 1995 | Searching many periods and many stars requires a valid null distribution. Do not apply FDR to uncalibrated BLS powers | **Clarify statistical significance**, calibrate correctly before population-level claims |
| **Time-series anomaly benchmark audits** | Xu & Bostrom Oct. 2026; Cacciagrano et al. Sep. 2026 | Test-set threshold tuning, baseline underspecification, entity leakage or unrealistic score adjustments | **Mandatory evaluation standard** |

## B. Six concrete findings that change our project

### B1. 2026: input cleaning can outweigh mathematical score sophistication
Robnik et al. (MNRAS March 2026, section 6) report that under their injected Kepler tests, removal of localized defects had the biggest effect on true signal recovery at fixed false alarm rate, while the Bayes-factor-versus-SNR difference was comparatively small. **Do not extrapolate those percentage gains to our data.** Implication: prioritize actual systematics and corrupted-event controls over adding an exotic ML model.

### B2. 2025: calibrating a null is a *separate scientific problem*
Robnik & Seljak (PNAS 2025) show that inverting and scrambling Kepler data may not reproduce the correct false alarm distribution. They alter event timing templates to create a data-driven null; discuss their reported star-specific FAP estimates separately from astrophysical false positive probabilities. Our current threshold based on 3 toy null classes with few examples is **a toy threshold** only. A claim of 10% true survey FAP would be wrong.

### B3. October 2026: use independent instruments/diagnostics where possible
Dallas et al., exoVetter (PASP 2026), use more sensitive Kepler observations of TESS stars as external reference information. Insight: stronger evidence comes from measurements not created by the algorithm being assessed. For a small class experiment, a few independently confirmed Kepler planets and known eclipsing binaries are useful sanity checks **in addition** to injections, not substitutes for large-scale reliability estimates.

### B4. 2026 adjacent statistics: human review has a coverage cost
Selective classification literature explicitly studies risk–coverage tradeoffs; automatically predicting only easy cases raises accuracy on answered cases. Our existing ML triage variant tracks review fraction, but it should also report **false-dismissals per 100 original inputs**, **underlying candidate recall** and **recovered correct candidates among all cases**. An abstention can be useful only if its rate and remaining errors are visible.

### B5. 2026 adjacent astronomy: different confidence signals disagree
Walls et al. (RASTI May 2026) found weak correlation between conformal set measures and predictive entropy for ambiguous-label radio galaxies. Although this is **not an exoplanet experiment**, it warns that ensemble disagreement, score margin, and confidence do not measure identical uncertainty. Our ensemble disagreement should be treated as an empirical ranking heuristic until verified on untouched outcomes.

### B6. October 2026 adjacent ML: test-set threshold tuning is a real problem
Xu & Bostrom (Machine Learning Oct. 2026) reviewed 18 influential time-series anomaly studies and identified leakage, altered benchmarks and unspecified classical baselines. Their discussion notes seven papers using test-set optimal thresholds. We must freeze thresholds, period windows, class definitions, and cost criteria on a validation set **before opening the test results**. Even a successful Colab run can produce invalid research if this protocol is violated.

## C. Direct audit of our current GitHub implementation

Verified from code on 2026-11-06:

1. `exoplanet_detector.py` is an old *narrow-range demo* (2.8–3.8 d search around injected 3.25 d); preserve it as a negative example, never cite it as blind discovery.
2. `blind_transit_benchmark.py` now uses injection periods 2.1–9.8 d and predeclared search 1.5–12 d. This fixes a key leakage flaw **but is still synthetic**.
3. The blind benchmark has a small, global null calibration sample (3 control types times `per_condition`); threshold is not star-specific, and the default Colab quick run uses very small per-group samples. No credible precision for a 1% astronomical false alarm rate.
4. The synthetic artifact families remain simplified: white/red noise, isolated drop, binary-like alternation and random gaps. Real data contain systematics not included here (stellar activity, momentum dumps, dilution, source contamination).
5. `transit_consistency.py` checks event dominance and odd/even depths on an *independently fitted* BLS ephemeris. Good start; however, true low-N, weak or TTV planets can fail the warning. Some negative controls still need event-level actual light curve verification; successful local unit tests do not establish BLS pipeline benefit.
6. `ml_screening.py` predicts the historical `koi_pdisposition` label with four scalar DR25 measurements, using a host-group split. This is **not** raw-light-curve detection or confirmed-planet validation; the KOI population is selected by a prior pipeline.
7. `ml_uncertainty_triage.py` compares margin-only vs margin plus forest-disagreement ranking, but both variants use the **same four random forests and same binary predictions**. Any gain is reallocation of review, *not* better underlying classification. Document it precisely.
8. Ensemble seeds are correlated replicas of the same model class with same training set. Model disagreement is **not** independently verified measurement uncertainty or a calibrated planet posterior.
9. Real NASA DR25 model accuracy and full Astropy blind-search performance have **not been verified** in the previous development environment; do not claim an improvement based on synthetic software tests.
10. The code does not yet link BLS-extracted individual transit diagnostic features to NASA KOI catalog rows. These are currently **two distinct experimental tracks**. A combined end-to-end detector is a stretch, not a completed artifact.
11. Current BLS "sigma" estimator from differenced flux assumes a relatively simple noise process. In highly autocorrelated stellar variability, its nominal SNR is not calibrated; need injected-real-noise tests to estimate actual error frequency.
12. Our existing comparison needs a **random-review** or standard margin-review baseline at the **same review fraction** before attributing a gain to model-disagreement logic. A single held-out split is fragile; use star-cluster bootstrap and report subgroup sample sizes.

## D. Ranked ideas by scientific leverage, novelty, feasibility

Ranking is our inference, not a published result.

| Rank | Idea | Why worthwhile | Feasibility | Decision |
|---|---|---|---|---|
| 1 | **Trustworthiness under blinded period/noise stress tests** | Directly addresses a verified code flaw and scientific false alarms; interpretable quantitative results | HIGH | **Core experiment A** |
| 2 | **Workload-constrained / selective ML screening on NASA DR25** | Strong statistics angle; independent held-out results; tests whether extra uncertainty measure selects better review cases | HIGH after NASA CSV | **Core experiment B** |
| 3 | **Event-level robustness ablation** (individual transits, one-event dominance, odd/even depths) | Physically motivated and tied to 2026 literature; complements aggregate model scores | MEDIUM with light curves | **Illustrative physical test**, optional real 5–15 stars |
| 4 | **Inject synthetic planets into *real* Kepler noise** | Addresses simulation-to-real gap; honest independent known truth for injected features | MEDIUM-HIGH cost/data | **Best next scientific upgrade** if Colab works |
| 5 | Simple confidence calibration / reliability diagram | Demonstrates whether numerical forest score is credible on DR25 labels | MEDIUM | **Small extra analysis**, do not treat as planet posterior |
| 6 | Pixel source-location check using exoVetter | Addresses astrophysical FP class scalar tabular ML misses | MEDIUM-HIGH, requires TPF | **Stretch only** |
| 7 | Calibrate full star-specific NST FAP | Strong statistical research but requires careful template distribution and many repeated trials | HIGH complexity | **Read/cite, don't reimplement** |
| 8 | Train full CNN/transformer | Already extensively studied; large data/compute/debug cost; unclear marginal insight | LOW feasibility | **Avoid** |
| 9 | Claim systematic novel exoplanet discovery | Infeasible with current data and verification | Very low | **Avoid** |

## E. Locked minimal scientific protocol for final project

### Track A: Search reliability under controlled measurement corruption
Data: blind simulated light curves with randomly injected periods, epochs, depths and durations; ideally inject into **real quiet-star Kepler residuals** for a follow-up. Negative controls: independent noise, correlated noise, one sudden sensitivity drop, one isolated dip, binary-like alternating dips, gaps and potentially stellar spot modulation.

Baseline: same Astropy BLS search and event parameter window across all conditions.
Enhancement: append an event-level consistency *warning*; do not quietly remove events and count as improvement.
Evaluation:
- `period_recovery`: correct period within a prespecified relative tolerance **and candidate flagged**; separate 2P or P/2 aliases from exact-period recoveries.
- `control_false_flag_fraction`: fraction flagged across **held-out controls of each type**, with sample counts.
- Report confidence intervals for each group and the runtime.
- Avoid the phrase "survey-wide false alarm probability" unless methods/controls actually justify it.
- Preserve negative cases and manually inspect representative light curves.

### Track B: ML vetting on catalog labels
Data: NASA Kepler DR25 KOI table, features period, duration, depth and SNR, historical automated Robovetter outcome as label; separate stars across train/validation/test; forbid disposition scores/flags/comments from features.

Baselines: (i) SNR-only rule; (ii) ordinary four-feature RF; (iii) random-review and decision-margin review at fixed review budget.

Enhancement: margin + ensemble-disagreement review *ranking*, not a new classifier.
Evaluation on one untouched test set:
- Candidate recall, false-positive rate, precision and confusion matrix;
- Review fraction, confident wrong classifications **per 100 starting candidates**, and false candidate dismissals **per 100 starting candidates**;
- Equal review budget (e.g., 20%, 30%, 40%) and, where relevant, equal candidate recall rather than cherry-picked points;
- Host-star bootstrap for paired effect, period/SNR subgroup counts and CIs;
- AUC/PR only as supplementary diagnostics, with prevalence shown.

**Cost-sensitive framing:** For each hypothetical review budget `B` observations, estimate how many of the *historically labeled* candidates receive correct automatic decisions and how many ambiguous cases are deferred. This is not an actual workload-hours estimate.

### Cross-track synthesis / honesty
Track A detects transits in raw simulated/time-series data. Track B vets already-extracted KOIs using tabular features. They **cannot be treated as one pipeline** unless a feature extraction and matching step actually joins them. Scientific narrative is: two complementary tests of AI-assisted automated research and reliability, not a proven end-to-end discovery machine.

### When to stop
If model disagreement does **not** lower errors at comparable review fractions, report that no incremental gain was observed and discuss how correlated forests and label ambiguity limit the method. If event vetting rejects real shallow transits or TTV planets, report that tradeoff. This is scientifically interesting.

## F. References (links point to paper, publisher, documentation or official archive)

1. Kovacs, Zucker & Mazeh (2002), Box Least Squares. https://doi.org/10.1051/0004-6361:20020802
2. Jenkins et al. (2010), Kepler data processing / transit search. https://doi.org/10.1088/2041-8205/713/2/L87
3. Hippke & Heller (2019), Transit Least Squares. https://doi.org/10.1051/0004-6361/201834672
4. Thompson et al. (2018), Kepler DR25. https://doi.org/10.3847/1538-4365/aab4f9
5. McCauliff et al. (2015), Kepler ML vetting. https://doi.org/10.1088/0004-637X/806/1/6
6. Shallue & Vanderburg (2018), Deep-learning Kepler study. https://doi.org/10.3847/1538-3881/aa9e09
7. Aigrain & Foreman-Mackey (2023), Gaussian processes in astronomical time series. https://doi.org/10.1146/annurev-astro-052920-103508
8. Valizadegan et al. (2025), ExoMiner++. https://arxiv.org/abs/2502.09790
9. Kunimoto et al. (2025/2026), LEO-Vetter. https://doi.org/10.3847/1538-3881/ae070a
10. Robnik & Seljak (2025), null signal templates. https://doi.org/10.1073/pnas.2513927122
11. Robnik et al. (2026), detection limit/individual events. https://doi.org/10.1093/mnras/stag419
12. Dallas et al. (2026), exoVetter (PASP, Oct. 2026). https://doi.org/10.1088/1538-3873/aeab34
13. Hadjigeorghiou et al. (2026), RAVEN. https://doi.org/10.1093/rasti/rzag080
14. RAVEN 2.2M-TESS-star survey (2026). https://doi.org/10.1093/mnras/stag512
15. Kopparapu et al. (2026), Kepler–TESS instrument transfer. https://doi.org/10.3847/1538-3881/ae7d0f
16. Salinas et al. (2026 **preprint**), single-transit ML calibrated uncertainties. https://arxiv.org/abs/2610.24882
17. Geifman & El-Yaniv (2017), selective classification. https://proceedings.neurips.cc/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html
18. Geifman & El-Yaniv (2019), SelectiveNet. https://proceedings.mlr.press/v97/geifman19a.html
19. Guo et al. (2017), confidence calibration. https://proceedings.mlr.press/v70/guo17a.html
20. Angelopoulos & Bates (2023), conformal prediction tutorial. https://doi.org/10.1561/2200000101
21. Walls et al. (2026), uncertain astronomy radio-galaxy labels. https://doi.org/10.1093/rasti/rzag033
22. Xu & Bostrom (2026), time-series anomaly benchmark failures. https://doi.org/10.1007/s10994-026-07183-y
23. Cacciagrano et al. (2026), classical versus deep time-series anomaly detection. https://doi.org/10.1016/j.iswa.2026.200717
24. Sasse et al. (2025), supervised ML leakage review. https://doi.org/10.1186/s40537-025-01193-8
25. Benjamini & Hochberg (1995), controlling false discovery rate. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x
26. Astropy Box Least Squares documentation. https://docs.astropy.org/en/stable/timeseries/bls.html
27. NASA Exoplanet Archive Kepler table background. https://exoplanetarchive.ipac.caltech.edu/docs/PurposeOfKOITable.html
28. NASA ExoMiner repository (official implementation). https://github.com/nasa/ExoMiner

## Research provenance

- This synthesis is AI-assisted literature research and reasoning. Paper methods/results above are author-reported, not independently replicated for this student project.
- Sections "Five major realizations", "Ranked ideas" and "Cost-sensitive framing" are **our proposed deductions**, informed by published work, not claims that the research papers themselves recommend this specific project.
- Statements on code defects are based on inspection of the GitHub repository. Actual NASA model outcomes have not been verified.
- The paper list includes a **2026 preprint**, clearly labeled. Methods may change with peer review.
- Do not quote a model score as planet posterior probability or a code smoke test as astronomical validation.
