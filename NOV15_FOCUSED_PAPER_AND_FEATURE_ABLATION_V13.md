# A focused final paper and tested Kepler model-feature experiment

**ASTR/PHSC 12600 | 15 November 2026 | Drew Thomas**

The main paper was revised from the lengthy Version 12 document into **2,540 words of main prose**, excluding references, figure captions and the professor's required checklist. The course rubric specifies **at least 2,500 words**; it does not impose a maximum. The formatted **Version 13** document is eight Letter-size pages, with four primary source-backed figures, ten research/data references and the completed checklist. The full technical archive and all original failures remain intact.

## Research focus

The project strictly follows the November 5 submitted proposal. It asks whether generative AI can help implement established Kepler transit measurements and whether a modest machine-learning model screens historical NASA Kepler labels more selectively than signal strength alone.

The revised paper emphasizes: (1) reproduce the **13.713343-day** period of known Kepler-69 b versus NASA's **13.722368-day** value (relative difference **0.0658%**); (2) show why a larger known-target experiment and a time-separated Q6-to-Q7 test yield both successes and binary false-positive controls; (3) compare the original four-feature forest with simple SNR and logistic baselines on **1,619 host-held-out signals**; (4) document the failed period-aware cutoff experiment and the smaller negative TESS pointing experiment; (5) explain the physics through flux, time, Kepler's laws, and laboratory measurement uncertainty.

The generative AI contribution is explained **within the research methods** (source-file reading, preprocessing, BLS search, model comparison and debugging). It is not presented as an administrative disclosure.

## New feature-ablation experiment (original NASA data)

The [successful original-source workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43776316541) ran on November 15 using the original **8,054-row NASA Kepler DR25** data source. The workflow checked that the raw downloaded CSV matched frozen **SHA-256 `c907e064c7369d4b073ba422283ddfbbf7499d472ec3cc0787254f3407e5e045`** before fitting. All variants used the same existing 4,824/1,611/1,619 signal host-disjoint train/validation/test split (seed 12600), `log1p` transforms and training-set-median imputation. The forests used 120 trees, depth 9, and minimum leaf size 3. Each decision cutoff was selected on validation stars with 90% intended historical-candidate recall.

| Random-forest inputs | Balanced accuracy | Historical-candidate recall | Historical-FP acceptance | ROC AUC |
|---|---:|---:|---:|---:|
| **All four** | **81.29%** | 87.19% | 24.61% | 0.8857 |
| Without period | 71.33% | 90.83% | 48.18% | 0.7860 |
| Without duration | 77.17% | 88.72% | 34.38% | 0.8467 |
| Without depth | 78.55% | 88.48% | 31.38% | 0.8664 |
| Without SNR | 80.55% | 86.49% | 25.39% | 0.8777 |
| Period and duration | 73.99% | 89.78% | 41.80% | 0.7975 |
| Depth only (forest) | 67.17% | 90.60% | 56.25% | 0.7179 |
| SNR only (forest) | 66.59% | 90.60% | 57.42% | 0.6752 |

The biggest performance loss came from omitting **orbital period**. The same forest without depth lost **2.74 percentage points of balanced accuracy** relative to the full model. A 1,200-resample whole-host bootstrap estimated the conditional difference in the interval **+1.34 to +4.32 points**. Omitting SNR alone caused a smaller change once the other three measurements remained, although a shallow four-feature forest cannot establish which physical measurement *causes* a previous NASA vetting decision.

**Boundary:** The study reuses the **previously analyzed** 1,619-signal test split, so it is an **exploratory model-comparison experiment**, not independent confirmation on unexamined stars. These outcomes concern NASA's historical `koi_pdisposition` candidate/false-positive labels, **not confirmed physical planet identities**. A **random forest trained on SNR alone** is also a different baseline from the original **single-threshold SNR rule** (the latter had 52.32% accuracy). They should not be conflated.

## Reproducing the experiment

- [Frozen study specification](V13_FEATURE_ABLATION_PROTOCOL_FROZEN_2026_11_15.json)
- [Original-source training and audit code](v13_kepler_feature_ablation.py)
- [Completed workflow and archived source, all eight fitted predictions, table, and figure](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43776316541/artifacts/14186278144)
- [Original four-feature model output for independent numerical comparison](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42513638366/artifacts/13630680897)

The feature-ablation workflow reproduced the **original full forest's 1,619 predictions and NASA labels exactly**, with a maximum saved score difference of approximately 3.3 × 10⁻¹⁶ from the original workflow. The main paper includes these exploratory results alongside the original Kepler and TESS findings; the longer source research reports remain available for full audit.

**Scientific literature used to design the work:** Kovács, Zucker and Mazeh (2002), BLS; McCauliff et al. (2015), Kepler random forests; Thompson et al. (2018), DR25 Robovetter; Batalha et al. (2010), false-positive checks; Valizadegan et al. (2022), ExoMiner. The connection to the class is through Lesson 2 (flux), Lesson 3 (timing), Lessons 5–6 (orbital motion), and the speed-of-light lab/Appendix B (precision, accuracy and uncertainty).
