# First verified real-data findings — NASA Kepler DR25
Date: 2026-11-06
Source run: https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42282355449
Source artifact: https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42282355449/artifacts/13535418140

**Important:** The result is agreement with NASA's **historical automated Robovetter CANDIDATE / FALSE POSITIVE labels** on a preselected Kepler Objects of Interest catalog, NOT independently verified planet discovery or a mission-wide completeness/reliability estimate. The GitHub Actions job and artifact were inspected on 2026-11-06.

## Dataset and split

- Official source: NASA Exoplanet Archive `q1_q17_dr25_koi` (DR25 Kepler Objects of Interest).
- Downloaded and retained: **8,054** KOI signals from **6,923** distinct host stars.
- Class counts: **4,034 CANDIDATE**, **4,020 FALSE POSITIVE** (NASA's previous vetter classifications).
- Distinct test-split objects: **1,619** signals from **1,385** stars; **851** CANDIDATE and **768** FALSE POSITIVE.
- Training: 4,824 KOIs; validation: 1,611; test: 1,619. Star IDs do not overlap among partitions.
- Input columns: estimated orbital period, transit duration, transit depth and model signal-to-noise ratio; no NASA disposition scores or false-positive flags used as predictors.
- Missing transit depth and SNR: 59 rows each, median-imputed from training data; period/duration complete in catalog.
- Download CSV SHA-256: `c907e064c7369d4b073ba422283ddfbbf7499d472ec3cc0787254f3407e5e045`.

## Baseline comparison on untouched held-out stars

A single signal-strength threshold and an ordinary four-feature random forest each had thresholds chosen to target **90% candidate recall on validation stars**, not on the test stars. Their actual held-out recall differs, so **this is not a matched-recall test comparison**.

| Held-out measure | Signal-to-noise threshold | Four-feature random forest |
|---|---:|---:|
| Accuracy | 52.32% | 81.59% |
| Candidate recall | 90.95% | 87.19% |
| False-positive rate | 90.49% | 24.61% |
| Precision | 52.69% | 79.70% |
| True candidate / predicted candidate | 774 | 742 |
| False positive incorrectly flagged as candidate | 695 | 189 |
| Actual false-positive labeled and screened out | 73 | 579 |
| Candidate incorrectly screened out | 77 | 109 |
| Fraction flagged as candidate | 90.74% | 57.50% |

**Interpretation:** The forest is markedly more selective than SNR-only screening for reproducing historical Robovetter labels. It screens out many more labeled false positives but **misses 32 additional labeled candidates** on this split. We cannot say it dominates at the same test recall. High SNR is common even for astrophysical eclipsing-binary-like false positives.

## Proposed AI extension: review at exactly equal budgets

The extra experiment uses **four seeded random forests**, a validation-selected binary threshold, and compares three ways to choose cases for human review:

1. Random review (mean of 100 randomly selected sets).
2. Ordinary score-margin review: review the observations closest to the classifier decision boundary.
3. Margin plus ensemble disagreement: prioritize observations based on margin adjusted by how much the four forests disagree; the disagreement weight is chosen from a small grid using validation data only.

**All methods use exactly the same binary predictions and the same held-out stars.** The extension cannot improve the underlying classifier's predictions; it can only prioritize more useful cases for expert inspection. A referred case is **neither assumed correct nor silently removed from the original denominator**.

| Review budget | Random review: wrong automatic decisions | Ordinary margin | Margin + disagreement |
|---|---:|---:|---:|
| 10% of 1,619 | 263.74 average | 212 | 210 |
| 20% | 232.99 average | 164 | 164 |
| 30% | 203.89 average | 123 | 122 |
| 40% | 176.33 average | 93 | 94 |

Counts for random review are averages across 100 allocations and therefore fractional; the other counts are integers.

At **30% review budget**, both non-random methods review **486** of 1,619 signals:
- Plain margin: **123** wrong automatic decisions, including **23** historical candidate-class dismissals.
- Margin plus disagreement: **122** wrong automatic decisions, including **22** historical candidate-class dismissals.
- Paired host-star bootstrap: difference (enhanced minus plain) **−0.0618 wrong automatic decisions per 100 original signals**, approximate **95% interval [−0.3754, +0.2460]**. The interval includes zero, so **no convincing incremental improvement was demonstrated**.
- At 10% the enhanced method reduces errors by 2 cases; at 20% ties; at 40% it is worse by 1. Results are small and not robust.
- Do not call this a gain in planet discoveries; it is only a different ordering of human-review assignments against catalog labels.

## Diagnostic: scores versus historical vetter labels

The held-out four-forest ensemble had:
- Brier score against previous NASA Robovetter labels: **0.13036**.
- Binned expected calibration error against those labels: **0.03259** (10 requested bins; 9 occupied).
- Held-out candidate-label prevalence: **52.56%**.

The calibration curve **does not** imply a score of .9 corresponds to a 90% astrophysical probability that an observation contains a planet.

## Low-signal and long-period caveat

The predefined subgroup table for the 1,619 test cases contained:
- Period <10 days: 915 objects; 10–100 days: 564; >=100 days: 140.
- SNR <10: 154 objects; SNR 10–30: 702; SNR >=30: 752; 11 rows have missing SNR.
- At 30%-budget screening, the margin-only review method refers ~67.9% of the >=100-day subgroup and ~62.3% of the SNR<10 subgroup. Therefore the low number of automatic errors in those groups **does not mean the method is especially accurate there**; it may simply defer most difficult objects to experts.
- The **current subgroup summary omits missing SNRs** and has no per-subgroup false-dismissal denominators or confidence intervals. That needs correction before giving subgroup conclusions.

## Science conclusions — evidence and inferences kept separate

**Supported by real-data analysis:** A four-feature forest reproduced the historical catalog labels better than the tested SNR-only threshold on overall accuracy, precision and false-positive rate, but had lower candidate recall on holdout. Human review selected by classifier margin caught more errors than equal-budget random review. Adjusting the review ranking using disagreement between four seeded forests did **not** reliably beat the simpler margin rule.

**Our inference:** A useful incremental improvement probably requires **new physical information** (e.g., independent transit-event consistency, pixel centroid localization, or instrumental systematics checks), rather than a further transformation of the same four scalar features.

**Not established:** End-to-end discovery reliability, a new confirmed exoplanet, scientific superiority to the full Kepler pipeline or ExoMiner, true mission-wide false alarm probability, and actual hours of researcher time saved.

## Validity priorities following this analysis

1. Fix all automated tests (most recent CI run had one incorrect fixed 50-star test assumption, plus empty-subgroup division warnings).
2. Report missing-SNR subgroup rows explicitly and preserve correct denominators.
3. Preserve NASA artifact + exact input digest and make the raw DR25 results accessible from the successful Action.
4. Compare the same review policies across more grouped-by-star split seeds, **without tuning on held-out results**; consider uncertainty due to the single split.
5. Build a truly blind BLS experiment using **real Kepler light curves** (not only synthetic noise) and measure candidate event consistency. Treat that as a separate test until raw event-derived features are integrated into the catalog screening model.
6. Refrain from adding more deep-model variants unless the new measurements justify them.

## References and research integrity

- Kovacs et al. (2002), BLS: https://doi.org/10.1051/0004-6361:20020802
- McCauliff et al. (2015), Kepler random forests: https://doi.org/10.1088/0004-637X/806/1/6
- Thompson et al. (2018), DR25 Robovetter: https://doi.org/10.3847/1538-4365/aab4f9
- Robnik et al. (2026), defect- and event-aware Kepler vetting: https://doi.org/10.1093/mnras/stag419
- Source run and artifact at links above.
- Python source was developed with AI assistance. Student must independently review the analysis, source data, code, scientific assumptions and report interpretation under course requirements.
