# Testing AI's Impact in Exoplanet Research

**Drew Thomas | ASTR/PHSC 12600 | Professor Buzasi | Autumn 2026**

> **Research question:** Can generative AI help reproduce and meaningfully evaluate established techniques used to identify exoplanets from telescope measurements?

This project follows the [November 5 submitted proposal](PROPOSAL_TO_RESULTS_RESEARCH_AND_CLASS_LINKS.md). It uses authentic public **NASA Kepler** observations to reproduce a transit search, then studies a deliberately small model for separating NASA's historical planetary-candidate labels from false-positive labels. The core distinction is between **detecting a convincing signal** and **correctly identifying its physical cause**. A smaller TESS measurement test is clearly marked as supplemental.

**Latest quantitative refinement (November 15):** [the two-part Q6-to-Q7 forecast and a retrospective eleven-star Holm correction](NOV15_Q6_Q7_TWO_PART_RULE_AND_MULTIPLE_TESTING_V12.md) | [source-verified numeric script](v12_q6_q7_posthoc_phase_audit.py) | [original-data figure](figures/kepler_q6_q7_two_part_rule_v12.svg). The downloadable **Version 12** research paper is a focused 24-page PDF/DOCX with 14 main scientific figures; the full earlier technical results are preserved.

## Start with the research paper

[**Main research report (Markdown)**](FINAL_REPORT_OPENING_HISTORY_FLUX_EXOMINER_AND_AI_REPLICATION_DRAFT.md) · [**November 20 status update**](NOV_20_STATUS_UPDATE_CONCISE_1_TO_2_PAGE_ORIGINAL_DATA_RESULTS_DRAFT.md) · [**Scientific articles and MEST lecture connections**](PROPOSAL_TO_RESULTS_RESEARCH_AND_CLASS_LINKS.md)

The formatted **Version 12 paper (Word and PDF)** and its original-data reproduction ZIP are provided as separate project deliverables. The paper includes quantitative results, figures, literature, lessons, references and the professor's project checklist.

## Experimental results, with denominators and limits

| Question | Original-data result | What it establishes |
|---|---|---|
| Can a simple transit search reproduce a known Kepler period? | Kepler-69 b: **13.713343 days** fitted versus **13.722368 days** published; **0.0658%** relative period error | Correct recovery of an established signal, not a new planet |
| How widely does that result generalize? | In a frozen 13-target Q8 cohort, **3/6** planet hosts recovered the intended named planet period; **4/6** analyzed binaries produced half-period aliases; one binary lacked Q8 data | A single successful known planet does not establish a high survey recovery rate |
| Can a period measured earlier predict *later* original brightness data? | Q6-only BLS fits passed the unchanged Q7 rule for **6/10** planned known planet hosts and **2/2** known eclipsing-binary controls; one host's Q7 file was unavailable | Later-time dimming is repeatable for some systems, but binary eclipses also predict well |
| Can four catalog features screen NASA's old Kepler vetting decisions? | On **1,619** host-held-out signals: **81.59%** forest accuracy versus **77.27%** logistic and **52.32%** SNR-only | Improved agreement with earlier *screening labels*, not independent astrophysical planet confirmation |
| Does more permissive long-period screening help? | Period-specific cutoff rescued historical candidate labels but reduced balanced accuracy on the separate frozen test split | Greater candidate recovery can cost too many additional false-positive referrals |
| Can a physical odd/even check explain a binary alias? | Kepler-35 Q7 median alternate-event depths **192,062 vs 57,207 ppm** (3.36x). Kepler-47 binary shows near-equal alternation. No eleven-star odd/even rank test survived Holm correction | Useful individual physical clue, **not** a general validated binary classifier |
| Does subtracting TESS telescope pointing movement improve source assignment? | Lower local-motion proxy in **44/56 stars**, but no consistent source-direction improvement in a separate small check | A steadier measurement need not improve physical identification |

All Kepler successes and failures are kept. **The random forest uses NASA's precomputed Kepler KOI catalog features, not features derived by our own BLS program**, so these are related analyses rather than a validated end-to-end planet-discovery system.

## Original evidence and exact research files

**Transit search and timing:** [Kepler-69 b original light curve](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42319839037) · [preselected Q8 external sample](FROZEN_REAL_13STAR_VALIDATION_RESULTS.md) · [predeclared Q6-to-Q7 protocol](Q6_TO_Q7_BLIND_PREDICTIVE_VALIDATION_FROZEN_2026_11_08.json) · [successful Q6-to-Q7 original observations, all twelve sources](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43512648584/artifacts/14079785749) · [source-backed outcomes](NOV13_Q6_Q7_GENUINE_TEMPORAL_VALIDATION_AND_DEPTH_V9.md).

**Candidate screening and methods:** [NASA DR25 host-held-out model predictions](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42513638366/artifacts/13630680897) · [period-aware negative experiment](VERIFIED_DR25_PERIOD_AWARE_THRESHOLD_NEGATIVE_2026_11_08.md) · [long-period error and decision-cost audit](NOV13_KEPLER_LONG_PERIOD_ERROR_AND_COST_AUDIT.md) · [strong-SNR false-positive investigation](NOV13_SNR_STRENGTH_VS_PHYSICAL_VETTING_RESEARCH_V8.md).

**New physical interpretation:** [November 15 all-eleven-star odd/even Q7 event audit](NOV15_KEPLER_Q7_ODD_EVEN_PHYSICAL_DIAGNOSTIC.md) · [reproduce the original data table](v11_q7_odd_even_reproduction.py) · [odd/even source-data figure](figures/kepler_q7_odd_even_physical_v11.svg) · [binary physical periods and Kepler-30 outlier](NOV14_PHYSICAL_SOURCE_AND_EVENT_STRESS_V10.md).

**Supplementary TESS experiment:** [why a smaller centroid-motion number did not reliably improve source localization](VERIFIED_NOV13_FULL_RESULTS_WHAT_WORKED_WHAT_FAILED_NASA_TESS_PRF_BENCHMARK.md).

## How to reproduce the most recent result

Download the **unchanged** original [Q6-to-Q7 workflow artifact](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43512648584/artifacts/14079785749). It contains `q7_individual_predicted_event_depths.csv`, the source manifest and full individual results. Then run:

```bash
python v11_q7_odd_even_reproduction.py path/to/original_forecast_artifact.zip
```

It checks source SHA-256 `9eb71ebf72014a8392949923d95e2c9b3cc633047809e10bd0f67229dc558dac`, recalculates the even/odd event depths and eleven-source Holm-adjusted comparisons, and saves a machine-readable CSV. The separately supplied Version 11 ZIP also includes the more detailed plotting script and original figure assets, with a clean-room reproduction check.

## Physics and literature

The experiments connect to **Lesson 2** (measured flux, light blending and angular resolution), **Lesson 3** (timing and recurrence), **Lessons 5–6** (orbital periods, stellar binaries and Kepler's third law), and **Lab 1/Appendix B** (precision, accuracy and uncertainty).

Research foundations: **Kovács, Zucker & Mazeh (2002)** for Box Least Squares; **McCauliff et al. (2015)** for multi-feature Kepler screening; **Thompson et al. (2018)** and **Batalha et al. (2010)** for planet-candidate vetting; **Welsh et al. (2012)** and **Orosz et al. (2012)** for the physical binary and planet orbits. Detailed bibliographic links and the role of each paper appear in the research report.

## Research scope

Generative AI helped implement and debug the Python methods; their numerical outputs were checked against original NASA-derived records and the published astronomical methods. The existing results do **not** claim discovery of a previously unknown planet, reproduction of NASA's full ExoMiner pipeline, or a proven improvement in professional mission-wide detection performance.

Earlier repository research notes are preserved in [the unabridged README archive](ARCHIVE_ORIGINAL_README_BEFORE_NOV15_2026_RESTRUCTURE.md) rather than occupying the project front page.
