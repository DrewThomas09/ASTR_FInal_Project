# Verified statistical significance test: NASA DR25 historical vetter-label accuracy
**November 8, 2026 | Complete original-data GitHub Actions run.**

**This document does not claim new planets, confirmed exoplanet accuracy, or a statistically significant improvement in the physical Kepler eclipse-preservation rule.** It quantifies agreement with NASA's *historical automated candidate/false-positive labels*, which are not independent planetary ground truth. The historical NASA DR25 catalog and the primary seed 12600 split had already been examined earlier; these are retrospective statistical robustness results, not untouched confirmatory discovery evidence.

- [Successful original NASA DR25 scientific workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42513638366), **135 unit and integration tests passed**.
- [Saved original NASA source SHA, host-level predictions, 10 split outcomes, subgroup denominators, complete logs and figures](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42513638366/artifacts/13630680897).
- [Precommitted statistical protocol](DR25_STATISTICAL_VALIDATION_FROZEN_2026_11_08.json), committed before this additional training and inference run.
- [Complete model and statistical analysis source](dr25_paired_statistical_validation.py) and [host-clustering unit tests](tests/test_dr25_paired_statistical_validation.py).
- [NASA Exoplanet Archive definition of the Kepler `koi_pdisposition` column](https://exoplanetarchive.ipac.caltech.edu/docs/API_kepcandidate_columns.html).

## Why the comparison matters

The prior report compared a four-feature random forest with a high-recall SNR-only threshold. However, the held-out candidate recalls differed by several percentage points, so raw overall accuracy is not enough. The new pre-specified **balanced accuracy** statistic averages the recall of historical candidate labels and the specificity of historical false-positive labels. This mitigates class-imbalance effects but does **not** make operating points equal on the test set.

Both model cutoffs target approximately **90% historical-candidate recall on separate validation stars**, with no labels or observations from the held-out stars used to choose thresholds. The added conventional four-feature **logistic regression** baseline is stronger and more informative than SNR alone.

## Original data and primary split

- Source: exact NASA `q1_q17_dr25_koi` table, seven original selected columns, downloaded using the *unchanged* `ml_screening.nasa_url()` query. Raw CSV SHA-256 verified to match the November 6 run: `c907e064c7369d4b073ba422283ddfbbf7499d472ec3cc0787254f3407e5e045`.
- Retained objects: **8,054** KOI signals on **6,923** distinct hosts; historical labels: **4,034 CANDIDATE**, **4,020 FALSE POSITIVE**.
- Original grouped-by-star seed 12600 primary holdout: **1,619 signals from 1,385 different stars**, comprising **851 labeled candidates and 768 labeled false positives**.
- Inputs: orbital period, observed transit duration, transit depth and reported model SNR; all four log1p-transformed and median-imputed **from training data only** where needed. Label-derived NASA veto flags and disposition scores were not model inputs.
- Forest: `RandomForestClassifier(n_estimators=120, max_depth=9, min_samples_leaf=3)`.
- Logistic: four-feature median imputer + standardized logistic regression with `C=1`.
- SNR rule: log1p SNR, imputed from *training* median, with the same validation-candidate-recall selection policy.

## Verified heldout classification results

| Metric | SNR-only | Four-feature logistic | Four-feature random forest |
|---|---:|---:|---:|
| **Balanced accuracy** | **50.23%** | **76.61%** | **81.29%** |
| Overall accuracy | 52.32% | 77.27% | 81.59% |
| Candidate recall | 90.95% | 89.42% | **87.19%** |
| Historical false-positive rate | 90.49% | 36.20% | **24.61%** |
| Precision among candidate predictions | 52.69% | 73.24% | **79.70%** |
| Candidate labels rejected (FN) | **77** | **90** | **109** |
| FP labels incorrectly accepted as candidate | **695** | **278** | **189** |
| AUROC, continuous score | 0.3466 | 0.7803 | **0.8857** |

**Important trade-off:** the random forest screens out many more historical false positives, but **rejects 32 additional historical candidate labels compared with SNR-only, and 19 more than the logistic baseline**. It is not superior on every accuracy axis. AUROC is threshold-independent and favors the forest, but that does not establish astrophysical planet accuracy. The very poor SNR ranking reflects the particular preselected NASA KOI label set; high-significance signals can be strong false positives (e.g. stellar eclipses).

## Primary significance test: RandomForest versus SNR-only

Primary endpoint (previously frozen before this reanalysis): **forest minus SNR-only balanced accuracy on the original heldout stars**.

- Difference: **+0.31063**, or **+31.06 percentage points**.
- Paired 2,000-replicate **host-star-cluster bootstrap**, with every KOI of the same host resampled together: **95% interval [+0.28692, +0.33427]**, equivalent to **[+28.69, +33.43] pp**.
- Primary **two-sided host-level method-swap permutation test**: 20,000 randomized host-block method exchanges, seed 2026110801, with **zero** sampled permutations as extreme as the observed difference. Monte Carlo p-value with the standard +1 correction: **1/20,001 ≈ 0.000050**. This is a lower-resolution Monte Carlo bound; it is **not** a claim that the true exact p-value is zero or precisely 0.00005.
- Simple row-level exact McNemar counts: 596 KOIs forest correct/SNR wrong vs 122 forest wrong/SNR correct, with p≈9.40×10⁻⁷⁶. **This is only a supplementary, overly optimistic analysis**, because multiple KOIs can share host stars. The host-level permutation is the preferred inferential check.

At the conventional 0.05 threshold, there is very strong statistical evidence that **the tested forest agrees with historical NASA vetter labels better than this SNR-only baseline on the selected host-group holdout**.

## Stronger benchmark: forest versus four-feature logistic

Comparing methods that use **exactly the same four inputs** is a more useful test of nonlinear modeling.

- Difference in balanced accuracy: **81.29% − 76.61% = +4.68 percentage points**.
- Paired, host-resampled 95% interval: **[+2.39, +7.02] pp**. The interval excludes zero, suggesting a real difference in *retrospective historical label agreement*, but this was a **secondary, exploratory comparison**.
- Difference in AUROC: **0.8857 − 0.7803 = +0.1054**; paired host-bootstrap 95% interval **[+0.0809,+0.1300]**.
- The cost: **19 extra historical candidate labels dismissed** by the forest (109 vs 90), despite 89 fewer historical false positives admitted (189 vs 278).

The result supports a nonlinear relationship among the four transit measurements and NASA's historical vetter labels. It is not evidence the forest has learned a true physical planet-confirmation mechanism.

## Replication across ten grouped-star splits (do not pool p-values)

Additional group splits were fixed as seeds **12601 through 12609**, each using independent host sets within its own train/validation/test partition.

| Balanced-accuracy advantage | Median across 10 splits | Minimum | Maximum | Number positive |
|---|---:|---:|---:|---:|
| Forest minus SNR | **+30.07 pp** | +27.05 pp | +31.42 pp | **10/10** |
| Forest minus logistic | **+5.10 pp** | +3.19 pp | +6.26 pp | **10/10** |

The test stars **overlap between different splits**, so the ten estimates are not independent samples or ten separate discovery confirmations. Do not combine their p-values or present an unadjusted 10/10 binomial significance test. The consistency shows **robustness to how host stars were partitioned**, conditional on already explored catalog labels and existing model choices.

## A serious limitation: long-period candidates

The preserved primary-split subgroup breakdown revealed an astrophysically important trade-off in the **140 held-out signals with periods at least 100 days**:

| Long-period diagnostic | SNR-only | Four-feature logistic | Random forest |
|---|---:|---:|---:|
| NASA-labeled candidate recall, 71 positives | 62/71 (87.32%) | **66/71 (92.96%)** | **44/71 (61.97%)** |
| False-positive labels accepted, 69 negatives | 54/69 (78.26%) | 58/69 (84.06%) | **16/69 (23.19%)** |
| Overall accuracy in subgroup | 55.0% | 55.0% | **69.29%** |

The random forest is highly selective on long-period signals but misses **27 of 71 historical candidate labels**. The logistic rule retains 22 additional labeled candidates at the cost of admitting 42 additional labeled false positives in that subgroup. These figures cannot be summarized as simple model superiority; the operating threshold and the available false-positive review capacity matter.

Shorter-period and low-SNR bins, along with **11 missing-SNR holdout rows**, are preserved in the original subgroup CSV. Subgroup patterns were inspected after the original study and are **exploratory**; no long-period subgroup p-value is claimed as confirmatory.

## Boundaries of statistical significance

1. **Historical classification, not truth:** `koi_pdisposition` describes prior NASA Robovetter decisions, not independently confirmed physical planets. The catalog is itself a preselected subset of Kepler threshold-crossing signals. Labels can be imperfect.
2. **Previously explored data:** the source and the 12600 primary star split were already used for earlier development, so this strong p-value is retrospective/conditional and should not be sold as a new untouched validation.
3. **Accuracy ≠ completeness:** neither accuracy nor AUROC on these KOIs measures recovery of undiscovered planets, independent occurrence rates or mission-wide false alarm probabilities.
4. **Operating point trade-off:** validation recall targets were identical, but observed heldout recalls differed. Do not claim matched test recall.
5. **Astronomy physics project is distinct:** the newer light-curve recurrence guard had only **two** externally explained protected binary warnings and **zero** new archived positive SPSD events. It has no justified population-level statistically significant improvement claim at present.
6. **AI disclosure:** all added code, host-block inference, tests, figures and this explanatory draft were AI-assisted; the student should reproduce the source digest, results and statistics independently before grading.

**Recommended next scientific experiment:** apply a *predeclared* period-stratified threshold policy or event-level physical checks to new separately frozen star-group folds, with explicit long-period candidate-recall and false-positive tradeoffs, instead of choosing a policy based on heldout success alone.
