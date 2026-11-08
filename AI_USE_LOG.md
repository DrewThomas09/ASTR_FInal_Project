# AI contribution and verification log

## 2026-11-04 | Initial detector design (AI-assisted)

**Task specified by researcher:** test whether generative AI can write a transit-search program and whether the program recovers known orbital periods. **AI work:** generated `exoplanet_detector.py` and synthetic injection test, with Astropy Box Least Squares as primary algorithm and a NumPy phase-folded fallback. AI generated plotting, CSV handling, and code-level explanations. **External method:** BLS originates from Kovacs, Zucker & Mazeh (2002); Astropy software is not an AI invention. **Verification:** synthetic known-period and noise-only runs. **Limitation:** the fallback search statistic does not provide a calibrated probability that a planet exists.

## 2026-11-04 to 2026-11-05 | Sensitivity and repeatability study (AI-assisted)

**AI work:** drafted repeatable simulation and detection-depth sensitivity code and report scaffolding. **Student responsibilities:** examine plotted light curves, distinguish noise from transit signals, and explain the result without claiming real-planet accuracy. **Data:** simulations, not NASA observations.

## 2026-11-06 | New candidate-screening improvement (AI-assisted)

**Task specified by researcher:** reproduce established exoplanet detection and add a modest, testable ML false-positive filter rather than only copying a standard detector. **AI work:** generated `ml_screening.py`, a random-forest comparison with an SNR-only screening rule, grouped train/validation/test splits, data validation, summary statistics, confusion matrix, and unit tests. Prepared README, Colab notebook, and research plan.

**Data intended:** NASA Exoplanet Archive Kepler Q1-Q17 DR25 KOI table (`q1_q17_dr25_koi`). **Four model inputs:** period, duration, depth, and fitted transit signal-to-noise. **Target:** NASA's historical `koi_pdisposition` Robovetter decisions. **Not used as predictors:** `koi_score`, false-positive flags, disposition labels, and identifiers.

**Tests performed:** 9 offline tests passed locally using synthetic catalog data. **Not yet performed:** actual NASA API download, real-data model training, evaluation on held-out NASA stars, and raw Kepler-69 recovery. **No claim:** no new planet found, no validated improvements or labor-hour savings, and no inference that the synthetic test statistics transfer to real data.

## What AI will and will not decide

AI is permitted to assist with: code scaffolding, explanation, debugging suggestions, charts, test writing, and documentation. Established algorithms, peer-reviewed papers, and NASA datasets provide the scientific method and evidence. The researcher must independently verify input provenance, review sample outputs, decide whether the experiment answers its question, and write/own the final scientific interpretation. Keep all additional AI conversations, code revisions, and fixes in this log before submission.

## Source papers (read and cite the originals)

- Kovacs, Zucker & Mazeh (2002), *A box-fitting algorithm in the search for periodic transits*. https://doi.org/10.1051/0004-6361:20020802
- McCauliff et al. (2015), *Automatic Classification of Kepler Planetary Transit Candidates*. https://doi.org/10.1088/0004-637X/806/1/6
- Thompson et al. (2018), *Planetary Candidates Observed by Kepler. VIII*. https://doi.org/10.3847/1538-4365/aab4f9
- Shallue & Vanderburg (2018), *Identifying Exoplanets with Deep Learning*. https://doi.org/10.3847/1538-3881/aa9e09
- Astropy BoxLeastSquares API: https://docs.astropy.org/en/stable/timeseries/bls.html
- NASA Kepler DR25: https://exoplanetarchive.ipac.caltech.edu/docs/Kepler_KOI_docs.html
## November 6, 2026 — AI-assisted research and experimental programming

- Research planning: AI compared BLS, Kepler pipeline, NASA DR25 Robovetter, transit-shape modeling, random forests, AstroNet, ExoMiner, and 2024–2026 instrumental artifact, calibration, and domain-shift research. Literature references and caveats are recorded in `RECENT_METHODS_AND_FAILURE_AUDIT_2024_2026.md`. These findings are *from published work*, not novel model results.
- Code authorship: GPT-6 generated the new `blind_transit_benchmark.py`, `ml_uncertainty_triage.py`, unit tests, and notebook integration. Core astronomical BLS calculations are supplied by **Astropy**, not a newly invented AI method. The ML classifier is from **scikit-learn**.
- Research design: Existing BLS demonstrations had effectively known the target period. The new synthetic simulation deliberately randomizes injected period and epoch and uses a broad search range; test nulls include noise and instrumental-like controls. Both generators and evaluation code were AI-assisted.
- ML design: A four-model ensemble is used to compare a baseline decision-margin review rule with an alternative that also incorporates model-score disagreement. Both variants use the same training/test stars and the same final binary predictions, differing only in which cases they refer to humans. This is a **new implementation and experiment for this class**, not a previously unknown scientific technique.
- Tests: New modules and triage evaluation passed **nine offline software tests** on simulated or constructed data locally. The actual Astropy BLS run and NASA DR25 performance remain unverified here; do not present simulations as real observational results.
- Human-scientific responsibilities: validate the NASA CSV source and its historical labels; independently run the Colab notebook; inspect failure cases and confusion matrices; check that no target-leaking variables were included; interpret the tradeoff between missed candidates and review workload; write independent conclusions and acknowledge all AI assistance under the instructor's rules.
- Known limitations: Small synthetic controls do not represent the full noise distribution of Kepler observations; BLS is not a proof of a planet; historical KOI dispositions are not independently confirmed planets; ensemble disagreement is not a calibrated physical probability.

## November 6, 2026 — Transit-consistency extension

- GPT-6 generated `transit_consistency.py` and its tests and added the diagnostic to the Colab notebook.
- The method inspects repeated dimming events *after* an independently fitted BLS period and transit epoch, rather than using the injected truth to choose the event times.
- Quantities: number of adequately sampled events, fraction showing a dip, share of positive-depth evidence contributed by the strongest event, and descriptive odd/even transit-depth difference.
- Heuristic rules are not calibrated probabilities of a planet or NASA-grade vetting thresholds. True transit timing variations, gaps, low SNR, and inaccurate fitted periods could cause warnings on genuine planets.
- Twelve offline tests across the new simulated data, ML triage and event diagnostics passed locally. No full Astropy transit-search performance claim has been verified; independent Colab testing is required.

## November 6, 2026 — Consolidation and adjacent literature

- GPT-6 reviewed primary methods and recent papers through November 6, 2026, and produced `CONSOLIDATED_RESEARCH_STRATEGY_NOV2026.md`.
- Research spans Kepler/TESS BLS detection, DR25 Robovetter, transit diagnostics, exoVetter (2026), ExoMiner++ (2025), RAVEN (2026), false-alarm null templates (2025), individual-transit vetting (2026), and statistical literature on selective prediction, calibrated uncertainty, distribution shift and evaluation leakage.
- Original deductions **proposed by AI** include prioritizing physical measurement integrity over model complexity, allocating a fixed human follow-up budget, and distinguishing signal, instrumental noise, astrophysical scenarios and catalog label mimicry. These are hypotheses and recommendations, not independently established findings.
- AI generated the research document, summary comparisons and GitHub Issues #6 and #7; no new astronomy measurements or real NASA model performance was produced in this research-only step.
- Student verification tasks: read the primary references and evaluate whether paper results generalize to our selected stars/labels; run the actual Colab experiments and interpret the quantitative comparisons. Cite and disclose AI research assistance as appropriate.

## November 6, 2026 — Reproducibility, selective-review tuning and calibration

- AI authored `dataset_manifest.py`, `calibration_audit.py`, additional tests and notebook integration, and revised `ml_uncertainty_triage.py`.
- The catalog manifest records the SHA-256 hash of the exact data file and observations/stars/labels/missingness so that data provenance can be checked.
- The ML disagreement weighting is selected by a small preregistered grid using the validation sample, not unseen test labels. All methods are evaluated at identical held-out human-review budgets, and per-row scores/review choices are saved for audit. Overfitting to validation remains a limitation.
- The calibration diagnostic is **read-only on held-out predictions** and evaluates consistency with historical NASA vetting decisions; it does NOT calibrate the probability of a physically real planet. No fitted probability transform is trained on test labels.
- Local six-test smoke suite of an earlier standalone fixed-budget experiment passed; new GitHub-only regression tests and full NASA workflow have not been independently verified in this session. Do not report real-data performance.

## November 6, 2026 — Verified catalog results and live-light-curve experiment

- AI retrieved and analyzed actual GitHub Actions logs and the `dr25-scientific-analysis` ZIP artifact. The run processed 8,054 historical Kepler DR25 KOIs and completed training/evaluation. Report: `REAL_NASA_DR25_RESULTS_2026_11_06.md`.
- AI initially coded the feature pipelines and selective-review ranking. Validation observed no convincing advantage of disagreement-enhanced review over the simpler uncertainty-margin approach; this negative result must be reported as such.
- AI fixed an automated test that assumed at least 50 stars in a 20% split of 210 simulated stars; the correct test validates exact host membership. It also guarded against division by zero when a subgroup contains no false-positive examples. GitHub Actions then reported a successful test run.
- AI authored `real_kepler_lightcurve.py`, new physics sanity tests, and `.github/workflows/real-kepler-lightcurve.yml` for an independent public-data Kepler quarter, and for injecting known artificial transits into real Kepler stellar variability. This new experiment was not yet verified at the time of the source-code commit.
- The student's role remains to interpret astrophysical meaning, distinguish exact-period versus alias recovery, and assess whether raw measurement diagnostics are genuinely informative versus the existing catalog labels. Published periods are used only as after-the-fact reference comparisons.

## November 6, 2026 — Observed Kepler and physical-vetting follow-ups

- GPT-6 authored a bounded MAST URI download fallback and fixed the published Kepler-69b DR25 orbital-period reference after checking NASA's archive. Earlier MAST searches had timed out and direct archive URL access returned 403; the MAST product API eventually succeeded.
- A GitHub Actions run successfully fit Kepler-69b's period on genuine Q8 PDCSAP flux and injected nine known transits into real Q2 observations of KIC 2436365. Exact FITS SHA-256 identifiers, preprocessing, numeric results and limitations are preserved in `REAL_KEPLER_LIGHTCURVE_RESULTS_2026_11_06.md`.
- AI implemented and ran `event_vetting_ablation.py`: 35 independent synthetic holdout cases showed limited benefit from generic individual-event checks (one of five binary impostors rejected, no gain in planet recovery). Saved in `FIRST_EVENT_VETTING_ABLATION_2026_11_06.md`.
- AI then implemented physical odd/even-depth and secondary-eclipse diagnostics in `binary_eclipse_diagnostics.py`, ran `eclipse_vetting_followup.py` on 56 fresh synthetic cases, and documented eight of eight deliberately unequal binary eclipses rejected with no additional rejection of BLS-detected simulated planets. This is exploratory and may not generalize; see `BINARY_ECLIPSE_SYNTHETIC_FOLLOWUP_2026_11_06.md`.
- An additional real Kepler test using KIC 10661783 as a published eclipsing binary was committed in `real_known_planet_vs_binary.py` and `.github/workflows/real-binary-controls.yml`. Its actual observed result should be inspected separately before scientific interpretation.
- These methods and analysis text were AI-assisted. Student responsibilities: independent code checking, primary-source reading, interpretation of true/false detections and false-dismissal risks, and disclosure under course rules. Do not claim a new planet or population-level robustness based on these examples.

## November 6, 2026 — Two-real-object observational binary check completed

- AI-authored `real_known_planet_vs_binary.py` ran successfully on genuine NASA MAST Q8 Kepler observations for published planet Kepler-69b (KIC 8692861) and eclipsing binary KIC 10661783. The historical periods were not provided to BLS and were used only afterward for comparison.
- Confirmed planet case: fitted orbital period 13.7133429855 versus published 13.7223682 days; the physical binary-specific secondary/odd-even warning was FALSE. Binary case: fitted period 1.23141743275 versus published 1.23136326 days; secondary eclipse was detected at an estimated 102,748 ppm and the warning was TRUE.
- Full source provenance, FITS digests, numeric calculations, and limitations were committed to `REAL_PLANET_VS_BINARY_VALIDATION_2026_11_06.md`.
- Both results are scientifically meaningful case-study sanity checks but NOT a validated population-level false-positive rate. AI-generated warnings are not verified physical planet probabilities; real planetary occultations and photometric contamination can produce similar signatures.
- The next verification goal is **frozen-rule assessment on several independent known planets and binaries** before any further hand tuning, including explicit counts of incorrectly warned genuine planets and missed binary warnings.
- The user/student must understand and independently verify the key steps, astronomy and conclusions, and disclose AI-assisted code and writing appropriately.

## November 6, 2026 — Frozen 13-star external evaluation and iterative BLS follow-up

- GPT-6 generated the source-verified target manifest `real_external_cohort_frozen.json` **before running** an external quarter-8 sample of six known planets and seven published binary systems. Earlier demonstration stars were excluded; original published orbital periods were used only after each model fit.
- GPT-6 generated `real_external_cohort.py` and a GitHub Actions workflow. Twelve of thirteen targets were analyzable; one source file could not be obtained under the fixed Q8 policy. All were included in the audit output.
- **Negative result:** None of the six analyzed published binaries triggered the current heuristic warning; four period fits returned half-period aliases, two returned exact periods with no warning. Three of six targeted confirmed planet periods were recovered; two others appeared to select different known planetary orbits in the same multi-planet systems. The previously successful two-object demo must not be generalized.
- The negative outcome was analyzed and recorded in `FROZEN_REAL_13STAR_VALIDATION_RESULTS.md`. GPT-6 also authored `iterative_bls.py` and a separate, explicitly **post-hoc exploratory** workflow on Kepler-18 and Kepler-20. Kepler-20b's previously known ~3.696-day period appeared on pass 2 after subtracting Kepler-20c; Kepler-18b still was not recovered by three iterations. These reused development stars and are **not** an independent accuracy test.
- AI generated the draft written interpretations, workflow scripts and GitHub Issues #9–#10 describing independent future tests. Any new hypothesis created from these experiments must be frozen and tested on separate unseen objects.
- Student responsibility: personally examine individual false-positive and missed-planet plots, independently explain period aliasing and multiple planets, check source status and scientific thresholds, and disclose all generative-AI programming/writing help according to the professor's requirements.

## November 7, 2026 — User-directed three-part project structure and benchmark choice

- User selected three fundamental components: (I) extensive critical literature review of existing methods and candidate improvements, (II) implementation and quantitative results, (III) reflection, next steps and comparison with an established research paper.
- GPT-6 reviewed `FinalProject.pdf`, the final checklist and course lectures, verified methodological claims from Kovacs et al. (2002), Thompson et al. (2018), McCauliff et al. (2015) and Robnik et al. (2026), then drafted `FINAL_PROJECT_THREE_PART_MASTER_PLAN.md`.
- The master plan identifies Robnik et al. (2026) as the primary physical-vetting methods comparison and McCauliff et al. (2015) as the secondary random-forest reference, and explicitly bars invalid quantitative comparisons across unmatched labels, periods and populations.
- Existing verified successes and negative outcomes are preserved. No new experimental results were generated when preparing this organizational plan. AI assisted with synthesis, drafting, and citations; final interpretation and academic accountability are the student's responsibility.

## November 7, 2026 — Source-grounded first-four-paper critical review

- User uploaded full PDFs of Kovács et al. (2002) BLS, McCauliff et al. (2015) 3-class random forest, Thompson et al. (2018) DR25 Robovetter and Robnik et al. (2026) complete false-alarm-vetting pipeline.
- GPT-6 extracted their complete textual contents and visually checked key figures, including Robnik Fig. 6 and McCauliff Table 1/Fig. 7. It authored `PART_I_FOUR_PAPER_CRITICAL_REVIEW.md` with source/page-specific methods, quantitative results, stated author limitations and explicitly distinguished interpretation.
- The literature review identifies data/information lost in phase-folding, missing diagnostic features, misleading historic catalog-label metrics and shifts in evaluation population; it outlines a future same-FAP controlled preprocessing experiment inspired by Robnik (2026), not yet executed.
- The paper's published factor-70 injection result and our small prior simulations have fundamentally different sample/period/noise definitions and are not directly comparable.
- No new model outputs or new exoplanet discoveries were generated during this paper-reading step; this is AI-assisted literature research and writing. Student should verify scientific reasoning and comply with academic contribution policies.

## November 7, 2026 — Adjacent-books and Gilbert dissertation-preview study

- User supplied three new PDFs: Hatzes (2020) 330-page RV-method textbook, Campante/Santos/Monteiro (eds., 2018) 288-page asteroseismology/exoplanets collected chapters, and Emily Gilbert (2022) **24-page dissertation preview only**.
- GPT-6 used text and selected rendered pages to identify the relevant literature on spectral windows, aliasing, heteroskedasticity, false-alarm thresholding, physical transit fits, stellar noise, activity modeling, stellar density and combined photometry/RV inference.
- Authored and committed `ADJACENT_EXOPLANET_METHODS_AND_SCIENTIFIC_WRITING.md` with detailed source-page pointers, important caveats, proposed experiments and journal-style report conventions. Did not copy publisher PDF text/images into the public repo.
- Gilbert's Chapter 2–6 full technical methods were **not present**: later results referenced only at abstract/contents/figure-caption level.
- No model changes, new tests, new NASA data or numerical advances were made in this reading task. Scientific conclusions, independent verification and final student contribution remain the student's responsibility.

## November 7, 2026 — Research-motivated BLS preprocessing experiment

- User asked to update the connected GitHub exoplanet research project based on the three newly supplied scientific references and our previous four-paper review.
- AI committed a **prospectively frozen** two-calibration/two-held-out Kepler star manifest, `PREPROCESSING_ABLATION_FROZEN.json`, before any new observational evaluation. It prescribes the BLS period range, injected depths/durations, fixed near-gap mask, proxy-null calibration method and honest scoring.
- AI authored `kepler_preprocessing.py`, `preprocessing_ablation.py`, `PREPROCESSING_ABLATION_METHODS.md`, deterministic tests and a dedicated GitHub Actions workflow. Artificial transits are multiplicatively injected into genuine Kepler PDCSAP photometry **before** the common 301-cadence detrend, and both methods receive the same injected events. The code measures omitted transit samples as a loss, not just false triggers.
- Calibration uses **constructed inverted/rolled flux proxy nulls** and does not establish actual Kepler false-alarm probabilities. Held-out test stars can contain genuine planets; this is an exploratory four-star comparison, not the 5,000-star long-period Robnik (2026) replication.
- AI fixed two testing-fixture assumptions that left fewer than the standard 500 retained data points, without changing the frozen scientific analysis settings. The corrected offline tests passed in GitHub Actions. New Kepler results must not be claimed until the workflow itself completes and its outcomes are examined.
- Work was drafted with AI assistance. The student must independently verify the paper-based motivation, astrophysical assumptions, code, statistics, and course academic-integrity rules.

## November 7, 2026 — Verified negative Kepler preprocessing experiment

- GPT-6 inspected GitHub Actions run `42400548553` with **64 passing offline tests** followed by real NASA FITS downloads and the frozen BLS-versus-gap-mask experiment. Saved original CSV/JSON data artifact ID `13584998475`.
- Both calibration stars were processed, while one of the two preselected held-out stars (KIC 11904151 Q8) failed the official public FITS download with HTTP 404. KIC 11026764 Q8 was the **only** successful held-out light curve; no post-hoc replacement was made.
- Baseline and masked methods each recovered **2 of 12** artificial injected periods at the chosen proxy-calibrated thresholds. Both flagged **0 of 10** held-out proxy nulls. Masking removed 15/2,535 cadences and two injected shallow-planet measurements. Calibration thresholds were 278.047626 (baseline) and 280.734694 (masked), each based on 20 calibration proxies.
- GPT-6 wrote `REAL_KEPLER_PREPROCESSING_RESULTS_2026_11_07.md` with full source SHA-256 provenance, sample denominators, wide descriptive uncertainty, failures, comparison with the **non-equivalent** Robnik paper, and next independent research requirements.
- This is a verified **negative pilot result**, not a verified claim that preprocessing never helps. Only one held-out star was available. Constructed proxy nulls do not measure true Kepler survey FAP; repeated injections on one star do not constitute many independent astrophysical stars.
- No thresholds/period/depths/selection criteria were tuned to rescue the outcome. The AI-generated software, results and text must be independently checked and disclosed according to the course policy.

## November 7, 2026 — New precommitted six-star localized-defect ablation (verified)

- GPT-6 researched Kepler's SPSD PDC correction, Aigrain et al. (2017) ARC2 discontinuity methods, and Robnik et al. (2026) physical defect templates. It proposed a much simpler heuristic persistent-negative-step mask and explicitly rejected the claim that it reproduced ARC2, PDC, or Robnik.
- GPT-6 committed `LOCALIZED_STEP_STUDY_FROZEN_2026_11_07.json` before running analysis: 2 calibration and 6 held-out Kepler Q8 star identities, input conditions, synthetic step profile, transits, fixed heuristic parameters, BLS grid and calibration/metric definitions. It authored `localized_discontinuity.py`, `localized_step_ablation.py`, regression tests, a dedicated Actions workflow, a Colab notebook and a technical protocol.
- The test suite originally had a **syntax error in an AI-written test function name**, which GPT-6 fixed without changing scientific code or predeclared settings. The verified workflow run `42402819710` then passed **74 tests** and successfully analyzed all eight selected public FITS sources. The original 10-file experiment artifact is `13585948128`.
- AI examined actual saved per-case CSV and source JSON: no-added-defect group baseline 21/36 recovered vs local-step 22/36, but identical search scores and no masking; the one difference is solely a lower proxy-calibrated score threshold (a *notable caution against claiming a data-processing gain*). Artificial-defect condition baseline 18/36 vs local-step 19/36; local heuristic matched 21/36 artificial onsets, erased eight real artificial-planet cadences, and rescued one previously wrong-period fit. Proxy-null flags were unchanged at 4/24 without artifacts and reduced from 13/24 to 10/24 with artificial steps, **not true survey FAP**.
- GPT-6 wrote the source-grounded `VERIFIED_LOCALIZED_STEP_RESULTS_2026_11_07.md` report, explicitly limiting causal claims and preserving negative results. As of this result, no statistically established exoplanet discovery advance has been demonstrated. Code, scientific interpretations and writing were AI-assisted; the student is responsible for understanding, checking and disclosing them as required by the instructor.

## November 7, 2026 — Real flagged Kepler instrumental event (illustrative)

- GPT-6 located an official STScI MAST tutorial that independently identifies a cosmic-ray-associated SPSD for KIC 7461601 Quarter 6 (quality value 1152). This is a **known-positive selection**, not a blind independent sample.
- AI extended the MAST file loader to support the source-documented Q6 archive timestamp 2010265121752; wrote and tested `real_spsd_case_study.py`, a simple source-reference flag reader and `.github/workflows/real-spsd-case.yml`.
- The workflow `42403352082` succeeded with nine focused tests; its real FITS fingerprint is `aa744d4861e56a44b99b7981fd6d729fc1f47ac230e03510d78406c1b073d301`.
- The archive marks a dropout at BKJD 547.8892493463 in **SAP_FLUX**, and our fixed heuristic—not given the label—found a step at 547.9096836451, one 29.4-minute long cadence later. It did NOT warn on the PDC-corrected PDCSAP brightness. The quality-labeled cadence was intentionally retained for this figure, unlike the usual planet-detection quality filter.
- GPT-6 rendered/inspected the SAP-vs-PDC figure, committed `REAL_KEPLER_SPSD_CASE_RESULTS_2026_11_07.md`, and disclosed that the target was selected because of its previously documented signal. This is a physical teaching example and not a claim of mission-wide detection rate, physical planet validation, or algorithm superiority.
- This source-backed case and previous six-star ablation should be interpreted together: NASA PDC itself handles some major instrumental defects before our code sees the preprocessed data. The student should independently verify all work and acknowledge AI assistance.

## November 7, 2026 — November 20 instructor status-update draft

- GPT-6 drafted `NOV_20_PROJECT_STATUS_REPORT_DRAFT.md` (~950 words) from source-verified prior actual results and the instructor's three-part project structure. It preserves every negative result and distinguishes previously known exoplanets from simulated injections and instrument quality flags.
- This draft was AI-authored, not independently written by the student; independent review and adherence to the course's AI policy are required before submission.

## November 8, 2026 — Frozen-outcome paired statistics and reproducibility (AI-assisted)

- AI retrieved the **original November 7 GitHub Actions artifact** (run 42402819710), including 216 method-level injection rows and 144 constructed proxy-null method rows, before computing any new result. No additional Kepler data were downloaded and no original model, star selection, thresholds, or injection truth were modified.
- GPT-6 authored `paired_validity_audit.py`, eight synthetic regression tests in `tests/test_paired_validity_audit.py`, the new interpretation report, and `.github/workflows/paired-validity-audit.yml` to rerun statistics on SHA-256-checked original inputs. The eight new offline tests passed in local execution.
- Observed matched comparisons: 21 vs 22 of 36 natural-flux recoveries; 18 vs 19 of 36 synthetic-step recoveries, with 0 baseline-only and 1 local-only recovery in either group. Exact two-sided paired-discordance p = 1.00 in each. Constructed step-proxy flag comparisons were 13 vs 10 of 24 (3 baseline-only, 0 step-only), p = 0.25. These are descriptive because the data comprise repeated trials on only six stellar hosts; **not survey-level inference or independent scientific validation**.
- The new audit isolated that all eight lost injected transit cadences arose from one KIC 9002278 artificial-step injection. A common numeric-score-threshold crosscheck is presented solely as a mechanistic sensitivity analysis, not matched real false-alarm-rate calibration.
- **Student responsibilities:** inspect the archived raw results, explain why one discordance does not establish improved performance, and decide what interpretation belongs in the final submission. Full credit and disclosure of AI-derived statistical code and draft writing are required by the course.

## November 8, 2026 — Fresh Kepler Q6 real-SPSD cohort protocol (AI-assisted)

- Based on the independent STScI Kepler archive quality-flag definitions, AI designed and committed an explicit **12-star prospective Quarter 6 cohort** in `REAL_SPSD_EXTERNAL_COHORT_FROZEN_2026_11_08.json`, before running its new observations. Previously used KIC 7461601 is excluded. Target selection is a convenience sample, not random source selection; the source table and all missing targets must be preserved in the result.
- GPT-6 drafted `real_spsd_external_cohort.py`, its 11 static tests, the methods/caveats document and an automated action. Detection uses the *unchanged* earlier local-step heuristic with identical joint-valid timestamps for original SAP and PDC-corrected PDCSAP. Archival SAP_QUALITY bit-1024 labels are consulted only **after** both detections, matched within an original fixed 0.22-day window and de-duplicated within 0.45 days.
- Unmatched warnings are not confirmed false positives, quality bit 1024 does not guarantee exhaustive instrument-truth labeling, and no planet detection is claimed. **Status at protocol commit: new NASA observational outputs not yet verified.** If the official-data job fails, record all sources/failures and do not invent or select replacement cases.
- Student must inspect original NASA files, verify the archive label semantics, reproduce and interpret every result independently, and disclose AI coding and draft-writing assistance in the submitted final project.
