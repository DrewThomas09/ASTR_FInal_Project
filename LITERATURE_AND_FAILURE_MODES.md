# Literature review and methodological audit
ASTR 12600 · 2026-11-06 · Research stage: literature and design; **no new real-data performance claim**

## Main question
**Can a small, transparent, AI-assisted reliability check reduce misleading transit candidates at the same sensitivity to NASA-labeled Kepler planet candidates, especially for weak and long-period signals?**

The project combines (a) generative AI used to draft/review scientific software, (b) a traditional physical transit-search method, and (c) an ML classifier or diagnostic gate. These are **three distinct roles**. Improvements must be **measured**, not assumed.

## 1. Landscape of earlier methods

| Method | What it does | Published contribution | Important limitation for our problem |
|---|---|---|---|
| Other discovery methods: radial velocity, astrometry, gravitational microlensing, direct imaging | Detect stellar motion, gravitational lensing, or planet light rather than periodic dimming | NASA's taxonomy of exoplanet detection methods | Different instruments and datasets; beyond the present Kepler transit-photometry scope |
| BLS, Kovacs et al. 2002 | Periodic search for box-shaped flux decrements | Simple statistical signal discovery | Always has a numerical highest peak even for pure noise; rectangular templates can mismatch actual limb-darkened transits; signal significance needs independent evaluation |
| Kepler Transiting Planet Search (TPS), Jenkins et al. 2010 and Tenenbaum et al. 2015 | Wavelet-adaptive matched filtering after noise conditioning; transit-like threshold crossing events | Designed for time-correlated stellar and instrument noise | Nonstationary/stellar artifacts and coherent oscillations are difficult; finding a TCE does not establish that it is a planet |
| Transit Least Squares (TLS), Hippke & Heller 2019 | Models limb darkening and ingress/egress rather than only boxes | Authors report better recovery of small shallow planets than BLS in their particular injection tests (~10% improvement) | Higher complexity; astrophysical false positives still possible; not a novel algorithm we can claim to invent |
| Kepler Robovetter, Thompson et al. 2018 (DR25) | Uniform rules for not-transit-like, eclipsing binaries, centroid offsets, and ephemeris matches | Uses injected transits and inverted/scrambled light curves to characterize completeness and reliability | Completeness/reliability tradeoff, notably long-period low-MES regime; its candidate/FP labels are **not independent planet confirmation** |
| Random-forest vetting, McCauliff et al. 2015 | Classify precomputed candidate attributes | Established that ML can assist catalog vetting | Published paper identifies failure when secondary eclipse or pixel contamination information is absent and deterioration on new period distributions |
| AstroNet, Shallue & Vanderburg 2018 | CNN on folded transit views | Successful ranking and two newly validated planets | A classification model applied to detections, not a general independent discovery or confirmation system; model and data complexity |
| ExoMiner, Valizadegan et al. 2021/2022 | Deep network integrating multiple domain-specific diagnostic signals | NASA reports 301 candidates newly statistically validated; 99% precision comparison in paper | Requires expert-designed diagnostic features; validation process is distinct from identifying peaks, and good aggregate performance need not be uniform across regimes |
| ExoMiner++, 2025–2026 | Extends deep-learning vetting to TESS and heterogeneous observations | Continues adapting models to broader data and measurement conditions | Domain shifts, crowded fields, model complexity; **already** includes uncertainty and crowding work, so we cannot claim those as unprecedented |
| Injection/recovery, inverted/scrambled nulls, confidence scoring | Evaluate sensitivity and false alarms rather than just output a score | NASA DR25 published systematic completeness/reliability framework | Requires careful simulation assumptions; white-noise simulations alone are not sufficient |

A transit is a temporary dimming, and physically its rough depth scales as `(planet radius / star radius)^2`. A recurring dip is a **candidate signal**, not a confirmed planet. Other planet-detection techniques use different physical evidence.

### Critical, source-grounded findings

1. **Noise/variability:** Kepler's TPS uses adaptive wavelet matched filtering precisely because time series contain correlated, nonstationary stellar and instrument noise. White Gaussian noise alone is an unrealistic evaluation.
2. **Transit shape:** TLS already improves the physical template, so “use a more realistic shape than BLS” is not original in the astronomical literature.
3. **False positives are a solved *category*, not a solved *problem*:** DR25 Robovetter explicitly tests eclipsing binaries, background contamination, and non-transit-like signals. A generic extra random forest is not automatically progress.
4. **Weak and long-period signals remain difficult:** Thompson et al. report, for low-SNR candidates at 200–500 days around FGK dwarfs, Robovetter completeness of ~76.7% and catalog reliability of ~50.5% under their defined sample conditions. This is a literature finding, **not** a figure measured by our project.
5. **Missing information:** McCauliff et al. report that some random-forest mistakes followed from omitted secondary-eclipse and pixel-level contamination diagnostics. More training alone cannot recover information the features never included.
6. **Evaluation differs from discovery:** High candidate-classification accuracy against a vetter's labels can mean predicting that vetter's judgments; it is not necessarily detecting or validating new planets.

## 2. Audit of *our current GitHub code*

**Priority 0 — search-range bias:** `exoplanet_detector.py` uses `detect(... min_period=2.8, max_period=3.8)` with simulated planet period fixed at 3.25 days. Thus the “successful recovery” is **conditioned on a narrow, correct window** and is not a fair blind planet search. Do not cite it as unconstrained discovery performance.

**Priority 0 — no false-alarm decision rule:** Calling the maximum BLS score “detected” without a null-calibrated threshold creates false impressions. BLS returns a strongest period even for a star without transits.

**Priority 0 — simulation simplicity:** Current synthetic data use white Gaussian noise with simple rectangular dips, fixed period/duration and nearly continuous evenly spaced observations. Real stellar noise includes slow trends, gaps, spot modulation, flares and instrumental artifacts. Any claimed sensitivity improvement must be tested on harder controls.

**Priority 0 — not end-to-end yet:** `ml_screening.py` trains on catalog features already calculated by NASA. It does not receive candidates extracted by our raw BLS program. The comparison is **catalog vetting**, not a complete novel detection pipeline.

**Priority 0 — incomplete real-data verification:** The real NASA Kepler DR25 training/evaluation run is not yet independently verified. Never use synthetic testing metrics as if they were results from Kepler.

**Priority 1 — label circularity:** `koi_pdisposition` is assigned by the Robovetter. Matching that label is interesting but not definitive evidence of a real planet. Never use `koi_score`, `koi_fpflag_*`, `koi_disposition`, or disposition comments as model inputs. These are direct or near-direct vetting outcomes.

**Priority 1 — selection bias:** The DR25 KOI table contains a selected subset of pipeline TCEs. KOI “false positives” are not identical to the full population of rejected non-transit-like events. Results measured on KOIs cannot be extrapolated to every Kepler search signal.

**Priority 1 — statistical uncertainty:** One random group split and a nominal 90% **validation** recall do not imply equal recall on held-out stars. Need test-set paired comparisons, confidence intervals and explicit period/SNR subgroup checks.

**Good practices already in the repo:** Four interpretable non-disposition features, train/validation/test partition grouped by host star, validation-selected cutoffs, and an SNR-only control. Preserve these.

## 3. Ranked improvements

### A — Recommended first: risk-aware *catalog vetting* and a fair comparison

Do not build a larger neural network. Add a modest, explainable **uncertainty/robustness layer** on top of the existing DR25 random forest.

1. First reproduce the existing SNR-only and random-forest results on **real** DR25 data with grouped-by-star train/validation/test splits.
2. Report candidate recall, false positive rate, precision, review fraction and the confusion matrices **on untouched held-out stars**.
3. Break performance down into *predefined* orbital-period bands (`<10`, `10–100`, `>=100` days) and signal-to-noise bands; report sample counts to avoid misleading small groups.
4. Introduce a **review/abstain category** for close-to-threshold predictions or disagreements between a small ensemble of independently seeded forests. Select operating cutoffs on validation only. A score is not automatically a calibrated probability.
5. Test whether selective human review reduces **high-confidence false-positive decisions** or improves weak/long-period candidate retention. Compare **at matched candidate recall or matched review fraction** and show the tradeoff, not a single inflated accuracy number.
6. Estimate uncertainty with bootstrapping **at the host-star level** on held-out predictions; preserve class and star grouping.
7. Treat gains as provisional if CI includes zero, if a group is too small, or if improvements disappear across repeated grouped splits.

This extension is not wholly unprecedented: DR25 Robovetter uses a disposition score, and later models can express ensemble uncertainty. The *classroom contribution* is the exact minimal workflow, bias-aware evaluation, and test of whether it helps a weak-signal subgroup under controlled constraints.

### B — Second: make transit search genuinely blind and stress-tested

1. Change the period search to a **predeclared broad interval** (e.g., 1–20 days) and test on injected periods that vary and are not passed to the search function.
2. Use multiple durations and realistic observation gaps; compare the baseline with unchanged settings across both simulated planets and controls.
3. Add non-planet controls: slowly varying/red noise, individual nonperiodic dips, stellar modulation and alternating-depth binary-like eclipses. Use at least ~30–50 realizations per category if compute permits.
4. Derive at most two transparent diagnostics: (i) whether similar dips recur consistently across different transits; (ii) whether evidence is sensitive to alternate detrending or small perturbations. These diagnostics are inspired by published vetting literature and are **not novel astrophysical concepts**.
5. Set detection/review thresholds **on control simulations only**, then evaluate on untouched synthetic cases. Plot detection/false-alarm tradeoff at matched sensitivity. Repeat with one real known Kepler system when available.
6. Do **not** conflate this simulation-based BLS experiment with the NASA DR25 catalog classifier until a demonstrated feature pipeline connects them.

### C — Stretch only if A and B work: simple feature ablation

Compare the existing four-feature forest against the same model with one diagnostic feature removed; do not add an enormous model family. Report whether any change survives out-of-sample validation. If the dataset cannot provide the extra diagnostic, do not pretend it exists.

## 4. Preregistered comparison

**Primary hypothesis:** A validation-selected uncertainty-aware triage rule can reduce erroneous confident classifications on held-out KOIs, or reduce the fraction needing expert review, while retaining approximately the same recall for NASA's historical candidate class.

**Null:** It does not improve those measures over a standard four-feature random forest or SNR-only threshold.

**Primary data:** NASA Q1–Q17 DR25 KOI table `q1_q17_dr25_koi`; labels `koi_pdisposition`. No new detections are claimed. Supplemental data: independently seeded synthetic light curves with negative controls. NASA KOIs and raw-light-curve simulations address **different aspects** of the research question.

**A fair success criterion:** On held-out stars, show either (a) lower false-positive rate at comparable candidate recall, or (b) fewer automatic incorrect decisions after routing ambiguous cases to review, with review fraction reported. Also show period and SNR subgroup behavior. An outcome with no gain is still a valid result.

**Uncertainty and limitation:** Bootstrap paired differences at the host-star level. Do not claim generalized completeness or reliability of an astronomical survey without a full injection/recovery design.

## 5. Smallest feasible deliverable

- 1 reproducible Colab notebook and the underlying Python code
- 1 real-catalog grouped holdout experiment, with ordinary random forest vs SNR rule and an uncertainty/abstention variant
- 1 broad period blind synthetic BLS check with at least a noise control
- 3 figures: screening tradeoff, period-by-SNR subgroup results, and illustrative transit/noise search
- 1 table: ablation and test-set counts, plus an AI-use audit with code attribution
- An honest interpretation, including negative results and current limitations

## 6. Academic/practical integrity safeguards

- Generative AI writes code and helps research sources; **it does not certify correctness**.
- The student must be able to explain the formulas, train/test design, the result table, and limitations.
- Do not imply that BLS is itself machine learning or that KOI predictions establish newly confirmed exoplanets.
- Cite source datasets, algorithms and libraries; disclose AI assistance as required.
- Repository is currently PUBLIC. Do not commit credentials, keys, or nonpublic personal documents.

## 7. Primary references (verified public sources)

1. Kovacs, Zucker & Mazeh (2002), BLS, A&A: https://doi.org/10.1051/0004-6361:20020802
2. Jenkins et al. (2010), Kepler processing pipeline: https://doi.org/10.1088/2041-8205/713/2/L87
3. Tenenbaum et al. (2015), 17-quarter TCE pipeline: https://doi.org/10.1088/0067-0049/217/1/18
4. Hippke & Heller (2019), TLS: https://doi.org/10.1051/0004-6361/201834672
5. McCauliff et al. (2015), automatic candidate classification: https://doi.org/10.1088/0004-637X/806/1/6
6. Thompson et al. (2018), DR25 completeness and reliability: https://doi.org/10.3847/1538-4365/aab4f9
7. Shallue & Vanderburg (2018), AstroNet: https://research.google/pubs/identifying-exoplanets-with-deep-learning-a-five-planet-resonant-chain-around-kepler-80-and-an-eighth-planet-around-kepler-90/
8. Valizadegan et al. (2022), ExoMiner paper: https://arxiv.org/abs/2111.10009
9. NASA DR25 catalog notes (labels, selection, injection tests): https://exoplanetarchive.ipac.caltech.edu/docs/Q1Q17-DR25-KOIcompanion.html
10. NASA Kepler data products and injected TCEs: https://exoplanetarchive.ipac.caltech.edu/docs/Kepler_Data_Products_Overview.html
11. NASA ExoMiner implementation and recent extensions: https://github.com/nasa/ExoMiner
12. NASA overview of transit versus non-transit methods: https://science.nasa.gov/exoplanets/how-we-find-and-characterize/
