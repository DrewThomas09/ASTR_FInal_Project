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
