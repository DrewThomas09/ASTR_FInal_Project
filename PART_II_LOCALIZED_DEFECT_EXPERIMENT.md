# Part II: independent localized-discontinuity experiment

**Design frozen before observations.** The source-cohort list, artifact parameters, control thresholds, period range, and scoring rules are locked in [the original JSON manifest](LOCALIZED_STEP_STUDY_FROZEN_2026_11_07.json).

## Why it is scientifically justified

The [Kepler Data Processing Handbook](https://archive.stsci.edu/missions-and-data/kepler/documents/data-release-notes) explains that cosmic rays and spacecraft behavior can generate sudden pixel sensitivity dropouts (SPSDs). The official PDC pipeline corrects many of them; our available PDCSAP data are therefore **already corrected photometry**, not untouched pixels.

[Aigrain et al. 2017](https://doi.org/10.1093/mnras/stx1422), *Robust, open-source removal of systematics in Kepler data*, explicitly distinguish detecting a discontinuity, classifying it as a defect rather than an astrophysical signal, and correcting it. Their ARC2 Bayesian systematics model goes substantially beyond our simple code. [Robnik et al. 2026](https://doi.org/10.1093/mnras/stag419) use a richer local-defect template bank, noise model, and matched false-alarm recovery evaluation. Our project does not replicate either published pipeline.

The research question is narrower: **Can a fixed, interpretable detector for persistent negative brightness steps improve known artificial transit recovery against standard BLS, under the same source measurements and fixed proxy-controlled thresholds?**

## Three compared methods

1. **Standard BLS**: the original Astropy Box Least Squares transit search, without any additional masks.
2. **Previously tested gap-edge mask + BLS**: remove measurements near long observation gaps. A previous frozen study found no improvement (2/12 vs 2/12 on its one usable held-out star).
3. **New persistent-step mask + BLS**: screen for a sudden negative first difference exceeding fixed amplitude and noise-proxy thresholds. Compare median flux in windows before, shortly after and later after the step. A persistent decrease is masked over a fixed 0.44-day window; a short transit that recovers should generally not meet the persistence requirement. This heuristic does not prove the physical origin of the change.

All methods use the **same** fixed BLS period/duration grid, data processing and known artificially injected signals. The step detector receives no injected planet period, injected artifact onset, or historical planet identity.

## Real data and independent cohort

Two preselected calibration stars: **Kepler-11** (KIC 6541920) and **Kepler-22** (KIC 10593626), Quarter 8. Six independently selected held-out stars: **Kepler-36** (KIC 11401755), **Kepler-37** (8478994), **Kepler-62** (9002278), **Kepler-78** (8435766), **Kepler-100** (6521045), and **Kepler-145** (8494142), all planned Quarter 8.

Stars and quarters were selected before seeing step-detector outcomes. All source-file exceptions remain in the denominator. Published planets' orbital periods are not provided to the detector, and these planet-host stars **must not be treated as planet-free negative controls**.

Artificial box transits (400, 1,000 or 2,200 parts per million, 2.1–9.8-day periods) are inserted into the actual NASA PDCSAP stellar flux **before** the common 301-cadence median detrend.

## Two separately reported conditions

- **No added instrument defect**: the original measured Kepler variability and sampling, with artificial transit signals. This measures whether additional masking helps or hurts on already PDC-corrected observed light curves.
- **A known, stylized SPSD-like defect**: a simulated abrupt 0.6–1.2% flux decrease with partial exponential recovery and persistent offset, added before detrending. This is a controlled stress test of an intentionally simplified nuisance, **not a realistically modeled Kepler CCD/pixel event**. A favorable score on such defects does not establish success on natural artifacts.

For each injected case, **all three methods see the same exact synthetic planet and the same defect**. The final study reports recovery improvement, lost true-planet samples, source failures, per-method test thresholds, and whether the step detector found the known injected discontinuity.

## Statistical precautions

Calibration stars alone determine each method's score cutoff at the same upper empirical quantile of *inverted and rolled stellar-flux proxy nulls*, with and without added artificial defects. These proxy controls are **not survey false-alarm probabilities**: they can contain contamination and are not independent planet-free Kepler stars. Test stars and their injected truths cannot influence the thresholds.

Recovery requires **both** (1) a fitted period within 2% of the known injected period, and (2) a BLS score above its calibration threshold. We must report exact and aliased periods separately where relevant, plus all genuine injected transit samples removed by preprocessing.

The study uses only a handful of purposively selected real Kepler stars and multiple correlated simulations per star. Small descriptive confidence intervals do not generalize to the full mission. In particular, the results are **not numerically comparable to Robnik's 5,000-star, long-period, matched-FAP benchmark**.

## How to reproduce

The algorithm is in [localized_discontinuity.py](localized_discontinuity.py). The complete comparison is in [localized_step_ablation.py](localized_step_ablation.py). The tests are in [test_localized_discontinuity.py](tests/test_localized_discontinuity.py) and [test_localized_step_ablation.py](tests/test_localized_step_ablation.py).

Run the [GitHub Actions experiment](.github/workflows/localized-step-study.yml) to retrieve original public FITS files, check all tests, apply the frozen protocol, and preserve complete CSV/JSON outputs and plots. Alternatively, run the script on an internet-connected Python environment using the repository requirements. Report *observed* results only after the workflow completes and logs are inspected.

## Importance for the final paper

**Part I (research):** Compare BLS, NASA PDC, Aigrain's ARC2, and Robnik's defect-aware pipeline, including what each actually measures and the physical information needed to disambiguate a planet from a defect.

**Part II (implementation):** Present the earlier failed gap-mask experiment, the present three-arm controlled comparison, and every omitted source or eliminated transit cadence. Avoid selecting a convenient success after the outcome is visible.

**Part III (reflection):** Evaluate whether a small rule translates from constructed physical defect examples to observed telescope data, and why AI-generated code and statistically weak controls are insufficient to establish a new planet-discovery advance.

This research protocol and implementation were drafted with AI assistance; the student must independently verify methods, outputs, references and course academic-integrity requirements.
