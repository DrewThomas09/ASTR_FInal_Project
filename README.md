# AI-assisted exoplanet detection | ASTR 12600

**Research question:** Can AI-assisted work reproduce and critically evaluate established exoplanet transit searches, then make a modest, physically motivated change that improves weak-signal recovery on an honest, comparable test? We report negative results and separate candidate vetting from confirmation.

## Current experimental implementation: source-inspired preprocessing ablation

**Starting point:** [source-grounded adjacent methods and writing review](ADJACENT_EXOPLANET_METHODS_AND_SCIENTIFIC_WRITING.md) and [four core papers](PART_I_FOUR_PAPER_CRITICAL_REVIEW.md).

**New experimental files:** [frozen experimental manifest](PREPROCESSING_ABLATION_FROZEN.json), [methods/protocol](PREPROCESSING_ABLATION_METHODS.md), [raw FITS preprocessing and injection module](kepler_preprocessing.py), [paired BLS ablation](preprocessing_ablation.py), [unit tests](tests/test_kepler_preprocessing.py), and [GitHub Actions observational experiment](.github/workflows/kepler-gap-study.yml) and [Google Colab notebook](Kepler_Preprocessing_Colab.ipynb).

We compare ordinary **Astropy BLS** with the *same BLS search* after one fixed and conservative **0.2-day near-gap mask around gaps >0.5 days**. Both are evaluated on the same synthetic transit events injected into genuine NASA Kepler PDCSAP flux **before** common detrending. Calibration and held-out stars are disjoint. Detection thresholds are determined only by separate, constructed inverted/rolled-flux **proxy** calibration nulls. We also measure how many real injected transit measurements the mask discards.

**Scientific caution:** Until the real-data workflow successfully completes and its CSV/JSON output is inspected, **no change in recovery, detection rate or false alarms is established**. Even a successful run measures a small *proxy-null* exercise, not the Kepler mission false-alarm probability or a full reproduction of Robnik et al. (2026). Earlier 13-star real binary-vetting failures remain an important counterexample to apparent success on demonstration stars.

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
