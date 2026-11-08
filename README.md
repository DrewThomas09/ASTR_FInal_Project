# AI-assisted exoplanet detection | ASTR 12600

## November 8: Paired statistical validity audit of the frozen study

[New paired analysis and interpretation](PAIRED_VALIDITY_AUDIT_2026_11_08.md) · [reproducible analysis code](paired_validity_audit.py) · [regression tests](tests/test_paired_validity_audit.py) · [hash-verified audit workflow](.github/workflows/paired-validity-audit.yml).

Reanalyzing the **original archived case-level results without changing the frozen detector**, the local step method yielded exactly one extra recovery among 36 matched injections in each condition. Both conditions had zero baseline-only cases and one local-only case (**exact two-sided discordance p = 1.00** each). On constructed defective proxy nulls, standard BLS flagged 13/24 and local step 10/24, with three baseline-only discordances (**p = 0.25**). These exploratory exact tests do not establish population significance because only six independent stars contributed repeated cases. On real-no-artifact photometry, all light curves were unchanged and the apparent extra recovery vanished under the baseline numerical score threshold. In the synthetic defect condition, eight genuine transit cadences were deleted from **one** KIC 9002278 injection. This is a statistical and reproducibility extension, **not** a new astronomical experiment, a true survey FAP comparison, or proof of superiority.

## November 8: Fresh, prospectively frozen *real* instrumental-defect study

[Precommitted 12-star Quarter 6 cohort and frozen rules](REAL_SPSD_EXTERNAL_COHORT_FROZEN_2026_11_08.json) · [exact reproducible instrument experiment](real_spsd_external_cohort.py) · [full analysis methods and caveats](REAL_SPSD_EXTERNAL_COHORT_METHODS.md) · [automated GitHub Action](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/workflows/real-spsd-external-cohort.yml).

This experiment applies the unchanged November 7 local-step detector to **both original SAP_FLUX and NASA PDC-corrected PDCSAP_FLUX at the same timestamps** for twelve *preselected* Kepler Quarter 6 stars. The known favorable teaching example KIC 7461601 is explicitly **excluded**. Only after detection does the experiment match candidate step onsets to original FITS bit-1024 SPSD archival event markers; all star download failures remain reported. Every source FITS SHA-256, matched event, unmatched warning and limitation is retained. **The original NASA run subsequently completed; see the verified negative outcome in the next section**; no unflagged warning is presumed a genuine false positive, and there is no new planet detection claim.

## November 8 verified: New real-Q6 source audit and binary eclipse contamination

**[Full, source-verified Kepler Quarter 6 negative observational result](VERIFIED_REAL_SPSD_EXTERNAL_Q6_RESULTS_2026_11_08.md)** · [original independent study run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42510882421), 96 regression tests passing. In the preselected twelve-star Quarter 6 SAP-versus-PDCSAP cohort, **ten real MAST star files were usable**, but **none** contained an archival SPSD quality-bit-1024 event. The original detector generated six original-SAP and seven PDC-corrected warnings; **without archived positive events, sensitivity to real SPSDs cannot be measured here**, and the warnings are not proven false alarms. Keep the two unavailable stars in the source denominator.

**[Full Kepler-47 physically grounded, POST-HOC eclipse analysis](VERIFIED_KEPLER47_ECLIPSE_CHECK_2026_11_08.md)** · [successful original-artifact and 104-test GitHub run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42511250474) · [saved original numerical table and plot](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42511250474/artifacts/13629303214). Seven distinct warning times were on KIC 10020423, an eclipsing binary: five within 0.1 d of Orosz et al. (2019) published *stellar* eclipse predictions, six within 0.3 d. Holding the seven event spacings fixed, 425/20,000 phase offsets gave at least five matches within 0.1 d; 1498/20,000 gave six within 0.3 d. These conditional phase shifts **are not confirmatory p-values**, because the star and matching windows were examined after the initial cohort output. This observation motivates periodic-event safeguards and tests on future untouched binary and authentic instrument-defect samples, not new discovery claims.

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
