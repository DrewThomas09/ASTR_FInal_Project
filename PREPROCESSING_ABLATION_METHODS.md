# Part II: real Kepler preprocessing experiment (frozen protocol)

## What changed in the software

This is the first code experiment directly motivated by the expanded source review of Hatzes (2020), the Springer chapters by Barros and Faria/Oshagh/Huber (2018), and the matched false-alarm evaluation logic of Robnik et al. (2026). The previous experiments are preserved, including the real 13-star negative result and multi-planet post-hoc demonstration. **No success should be claimed until a complete real-data run and logs have been inspected.**

The executable experiment is [`preprocessing_ablation.py`](preprocessing_ablation.py), its reusable logic is [`kepler_preprocessing.py`](kepler_preprocessing.py), and its design was frozen before the first run in [`PREPROCESSING_ABLATION_FROZEN.json`](PREPROCESSING_ABLATION_FROZEN.json). The latest run and downloadable CSV/figures can be found in [the dedicated GitHub Actions workflow](.github/workflows/preprocessing-ablation.yml).

## Scientific question

Does excluding cadences within **0.2 days** of either side of a **gap longer than 0.5 days** make an ordinary BLS transit search more effective, given the same simulated transit signals and method-specific detection thresholds selected using separate proxy controls?

This is a deliberately simple classroom-scale *near-gap mask*, **not** the physically rich localized defect bank, noise model or Bayesian detection statistic of Robnik et al. (2026). If masking does not help, this is a useful negative result. If it helps on these four stars, a larger independent test is still required.

## Data, baseline and competing method

- Official Kepler Q2/Q8 **PDCSAP_FLUX** long-cadence FITS obtained through NASA MAST. Stars and quarters are listed in the locked JSON, without substitution after outcomes become visible. The source's FITS SHA-256, gaps and any download failures are recorded.
- Remove invalid, nonpositive and nonzero-quality-flag cadences. The original **unflattened** PDCSAP flux is retained for the artificial transit injection.
- Inject known box dips **multiplicatively before median detrending**: flux_new = flux_original × (1 - depth_ppm/1e6) for times inside the injected transit. This is injection into real measured photometry, not into spacecraft detector pixels; the original target can have existing unknown planetary signals.
- Apply the **same** fixed 301-sample running-median normalization to both methods. Method A then feeds all retained quality cadences to Astropy BLS; Method B excludes near-gap edges. The BLS period grid, duration choices, signal statistic and fitted peak search are identical for both methods.
- The injected orbit period is randomized between 2.1 and 9.8 days with a randomized phase, depth from 400/1000/2200 ppm and duration 0.11–0.19 days. Published planet periods or injected true periods are **not inputs** to the BLS search.
- A recovered transit must have a BLS score exceeding the method's calibration threshold **and** have fitted orbital period within 2% of the actual injected period. We do not presently demand a phase match, so this metric is deliberately weaker than some published injection tests.

## Calibration and evaluation (limits matter)

- Two preselected stars supply **calibration controls**. Two different, previously unused-for-preprocessing-selection stars supply **held-out experiment cases**. This is not a random or representative sample from the full Kepler mission.
- The controls are made by inverting and circularly rolling each star's *detrended real flux*. These are **constructed proxy nulls**, not proof of a planet-free star or a realistic complete instrumental null distribution; the operation also changes alignment of real defects to observation gaps.
- On calibration stars only, the 90th-percentile BLS peak (method-specific) is used as an approximate **10% proxy-control flag target**. The finite calibration sample means that actual true false-alarm probability is unknown. The test pool uses different stars and random seeds from calibration.
- On held-out stars, separately report (a) flagged proxy-null fraction and wide 95% Wilson intervals, (b) period-and-threshold injection recovery for every depth and method, (c) paired cases improved and harmed by masking, (d) injection signal retained versus removed near gaps, and (e) every source exception.
- No paper-level comparison using published discovery/reliability percentages is legitimate unless both methods share **the same stars, injected periods, controls, and false-alarm definition**. The current result is described as **Robnik-inspired**, not reproduction of their 5,000-star, 200–500-day study.

## Scientific reason for the test

Hatzes emphasizes that sampling gaps, aliases and poor noise treatment can generate misleading periodic peaks. Oshagh and Gilbert's TESS thesis preview underscore that stellar activity and real transits may occupy overlapping timescales: making a curve visually smooth can make a real planet harder to recover. Robnik et al. report that local artifact removal can strongly improve recovery at a matched false-alarm budget, but the effect is conditional on their carefully constructed artifact model. Our minimal mask tests just **one interpretable component** without assuming it must help.

## Predeclared failure modes

- A near-gap mask can remove genuine transit cadences, reducing recovery or increasing period errors.
- If there are few substantial gaps, the method may be effectively identical to baseline BLS.
- Strong existing planets or stellar activity in control stars can contaminate the proxy null, and rolling/inversion may produce unrealistic noise/edge relationships.
- Measuring an empirical 10% proxy-control flag rate with roughly twenty calibration realizations is imprecise. Confidence intervals are descriptive only and stars are reused within each pool; estimates cannot be treated as independent draws from the population.
- A one-quarter experiment misses long-period signals and is not a test of Earth analog sensitivity.
- The pre-existing BLS `robust_sigma` and 301-cadence flattening may be sensitive to correlated noise and can distort transit geometry; this experiment does not solve those problems.
- Real eclipsing binaries will not necessarily be removed by a near-gap mask; the independently observed period-alias failures remain unresolved.

## How to reproduce

Run `python -m pytest -q tests` for offline invariants. For a local machine or Colab with internet access and suitable Python packages, run `python preprocessing_ablation.py --out results/preprocessing_ablation`. Alternatively, open the workflow's **Run workflow** control on GitHub. It downloads official FITS files, keeps an exact frozen manifest snapshot, and saves generated results/plots under the workflow's artifact. Results should be inspected before inclusion in the final paper.

## Relationship to the final paper

The source review forms **Part I**; this experiment forms one subsection of **Part II**; any negative or ambiguous result belongs in **Part III** with method limitations and explicit comparison against Robnik et al.'s stronger, differently designed benchmark. Preserve the DR25 classification, external binary failure and iterative multi-planet result as separate experiments with their own labels and test populations.

This methodology and code were drafted with generative AI assistance. The researcher must independently check astrophysical interpretation, source licenses, experiment behavior, citations and the course AI-use rules.
