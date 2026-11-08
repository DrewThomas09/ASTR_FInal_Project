# Period-aware threshold modification: tested, did NOT improve balanced accuracy
**November 8, 2026 | Verified NASA DR25 historical label study, negative result retained.**

This is **an exploratory response to a previously observed model weakness**, not a truly untouched confirmation study. The outcome was not chosen to favor the new model. All raw observations, original source digest, 10 host-group splits, validation thresholds, negative outcomes and software test results remain visible.

- [Prospectively fixed policy, before this variant was evaluated](PERIOD_AWARE_DR25_VALIDATION_FROZEN_2026_11_08.json)
- [Actual new method code](dr25_period_aware_recall_experiment.py) · [validation-only threshold checks](tests/test_dr25_period_aware_recall_experiment.py)
- [Successful 144-test official NASA workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42514013228)
- [Archived source SHA, complete individual test predictions, first-split and 10-split tradeoffs, all thresholds, graph and logs](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42514013228/artifacts/13630652118)

## Hypothesis, method and why the comparison is fair

The existing four-feature random forest had lower-than-desired historical candidate-label recall for very long orbital periods. Instead of fitting another deep network, we tested whether a **validation-calibrated period-specific decision threshold** can improve long-period operating performance.

The **random-forest scores, features and architecture were identical** for the two methods. The original method used a single cutoff selected on validation stars to target 90% recall. The new method kept the same score but selected three validation-only cutoffs for **P < 10 days**, **10 ≤ P < 100 days**, and **P ≥ 100 days**, each targeting 90% *validation* candidate recall. A bin with fewer than 30 validation candidates would fall back to the global cutoff. **No heldout labels were used to choose thresholds**.

We froze **ten new grouped-by-star seeds, 14000–14009**, prior to this additional experiment. Within each seed, training, validation and test hosts were separate; different splits overlap stars and are not ten independent replications.

**Prespecified primary outcome:** long-period (>100 days) balanced-accuracy difference on first split 14000, new policy minus original global threshold. Other metrics capture candidate-sensitivity versus false-positive tradeoff. All results are retrospective NASA **Robovetter label agreement**, not confirmed planetary outcomes.

## Primary new split results: long period ≥100 days

On 145 heldout long-period signals from 140 unique stars, of which 58 had historical NASA `CANDIDATE` labels and 87 had `FALSE POSITIVE` labels:

| Measure | Original global cutoff | Period-specific cutoff |
|---|---:|---:|
| Correctly accepted historical candidates | 42/58 | **57/58** |
| Candidate recall | 72.41% | **98.28%** |
| Historical false-positive labels incorrectly accepted | **28/87** | 64/87 |
| False-positive rate | **32.18%** | 73.56% |
| Balanced accuracy | **70.11%** | 62.36% |
| Overall historical-label accuracy | **69.66%** | 55.17% |

The *new* policy saved **15** previously rejected historical candidates (16 missed → 1 missed), **but it wrongly accepted 36 more historical false-positive labels** (28 → 64). That changes long-period balanced accuracy by **−7.76 percentage points**, not a gain.

- Two-sided **host-level paired method-swap permutation**, 20,000 resamples, seed 2026110803: **p = 0.1336**. This is **not statistically significant at 0.05** for the prespecified long-period balanced-accuracy contrast.
- Host-clustered 2,000-replicate 95% percentile interval for the balanced-accuracy change: **[−15.53, +0.03] pp**, which narrowly includes zero.
- Host-clustered 95% interval for **candidate recall change**: **[+15.15, +37.74] pp**.
- Host-clustered 95% interval for **false-positive-rate change**: **[+30.59, +52.18] pp**.

The new threshold is an **operating point tradeoff**, not increased underlying classifier discrimination. Because it does not change ranking scores, it has exactly the **same ROC AUC** as the original forest.

## Overall test performance (all periods) also worsened

On the same seed 14000 split, 1,605 KOIs from independent heldout hosts:

| Measure | Global forest | Period-aware forest |
|---|---:|---:|
| Historical candidate recall | 91.05% | 92.56% |
| Historical false-positive rate | **33.13%** | 39.41% |
| Balanced accuracy | **78.96%** | 76.58% |
| Overall label accuracy | **78.82%** | 76.39% |
| Historical candidates wrongly rejected | 71 | **59** |
| Historical false-positive labels wrongly accepted | **269** | 320 |

Overall balanced accuracy fell **2.38 percentage points** on this heldout split, with a star-clustered 95% interval **[−3.96, −0.94] pp**. Thus the method appears to make overall catalog label screening worse on that split, despite modestly improved candidate recall.

## Ten-split sensitivity (do not pool)

| Metric | Number of worse splits | Number of better splits | Median improvement (new minus old) |
|---|---:|---:|---:|
| Long-period balanced accuracy | **9** | 1 | **−6.89 pp** |
| Overall balanced accuracy | **10** | 0 | **−1.81 pp** |

Long-period balanced-accuracy changes ranged from **−10.54 pp to +1.39 pp**; overall changes ranged from **−2.58 pp to −1.11 pp**. These splits re-use catalog hosts, so they do not justify an independent 10-trial binomial p-value or an overconfident population significance claim.

## Scientific conclusion

**The new period-aware threshold should not replace the original forest.** It greatly reduces rejection of historical long-period candidates at the cost of an even larger increase in accepted historical false positives and lower balanced accuracy. The central risk has not been fixed; it has simply been moved.

A defensible future improvement needs **additional physical information**—such as consistent individual transit events, independent pixel centroids, verified binary eclipses or instrument-defect features—not another threshold chosen after inspecting outcomes. A high-accuracy classifier still needs to report the candidates it misses.

As with the other experiments, NASA's historical DR25 dispositions are imperfect **classifications of previously selected Kepler Objects of Interest**, not independent real-exoplanet ground truth. This test does not measure new exoplanet recovery, actual mission FAP, astronomical occurrence rates or safety in genuine SPSD examples.

**AI use and review:** GPT-6 assisted protocol, code, regression tests, statistical analysis and draft. The student must independently check original NASA output, thresholds, actual denominators, astronomical reasoning and AI disclosure.
