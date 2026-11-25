# Testing AI's Impact in Exoplanet Research

**Drew Thomas | ASTR/PHSC 12600 | Professor Buzasi | Autumn 2026**

> **Research question:** Can generative AI help reproduce and meaningfully evaluate established techniques used to identify exoplanets from telescope measurements?

This project follows the [November 5 submitted proposal](PROPOSAL_TO_RESULTS_RESEARCH_AND_CLASS_LINKS.md). It uses authentic public **NASA Kepler** observations to reproduce a transit search, then studies a deliberately small model for separating NASA's historical planetary-candidate labels from false-positive labels. The core distinction is between **detecting a convincing signal** and **correctly identifying its physical cause**. A smaller TESS measurement test is clearly marked as supplemental.

**New November 18 independent timing study (not yet inserted into Version 16 paper):** A fixed Quarter 8 period forecast for Kepler-69 b found dips in **7/7 usable Q9 windows, 6/6 Q10, and 5/6 Q11**, but found **0/6 in Q12 and 0/6 in Q13**. In a clearly marked *retrospective explanatory check*, substituting NASA's more accurate known period (while keeping the Q8 starting epoch) recovered **6/6** in both of those later quarters. The transit pattern did not disappear: the original clock slowly drifted away from it. Read the [plain-English research explanation and original-data evidence](NOV18_PLAIN_ENGLISH_KEPLER69B_RESEARCH_RESULTS.md). These results are **not** new planet discoveries or estimates of survey-wide performance.

**Earlier quantitative refinement (November 15):** [the two-part Q6-to-Q7 forecast and a retrospective eleven-star Holm correction](NOV15_Q6_Q7_TWO_PART_RULE_AND_MULTIPLE_TESTING_V12.md) | [source-verified numeric script](v12_q6_q7_posthoc_phase_audit.py) | [original-data figure](figures/kepler_q6_q7_two_part_rule_v12.svg). The downloadable **Version 12** research paper is a focused 24-page PDF/DOCX with 14 main scientific figures; the full earlier technical results are preserved.

**Current focus:** [Version 13 focused paper and verified original-source feature-ablation results](NOV15_FOCUSED_PAPER_AND_FEATURE_ABLATION_V13.md). The new model test explains which of the four Kepler catalog measurements the forest benefits from using; the longer analyses remain archived.

**Polished Version 15 final-paper release:** [7-page paper, 2,615 main-body words, four fully labeled figures and document QA](NOV15_POLISHED_FINAL_PAPER_V15_QA.md). The updated Word/PDF files are provided in the project conversation; original source data and scripts remain here.

**Current narrative-first research paper (Version 16):** [documented research process, experimental setbacks, and verified Kepler outcomes](NOV15_RESEARCH_PROCESS_NARRATIVE_V16.md). The revised six-page DOCX/PDF files are available directly in the project conversation. The longer technical studies remain archived.

**Current as of November 17, 2026:** The [updated November 20 project status report](NOV_20_STATUS_UPDATE_CONCISE_1_TO_2_PAGE_ORIGINAL_DATA_RESULTS_DRAFT.md) reflects the **Version 16** six-page, 2,720-word research-process paper. The report documents the actual early simulations, NASA FITS handling, external Kepler failures, frozen Q6-to-Q7 predictions, model comparisons, and the smaller TESS follow-up. The formatted 2-page status report and the current final-paper PDF/DOCX are available in the project conversation. The status report is prepared for Canvas; it has **not been submitted**.

**Current accessible manuscript (November 18, Version 17):** [Plain-English final-paper draft](NOV18_FINAL_PAPER_V17_PLAIN_ENGLISH_DRAFT.md). It keeps the November 5 proposal's original Kepler transit-search and four-feature machine-learning tests, adds the verified Q8-to-Q13 clock-drift experiment, and preserves the failed approaches and limited TESS follow-up. It is about 3,250 main-text words, with bibliography and completed lecture checklist. [The Word/PDF build with charts](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/44313736252) succeeded; see the downloadable paper artifact in the run. **The manuscript is not yet submitted to Canvas.**

**November 25 continuation (Version 18 working paper):** [updated accessible paper](NOV25_FINAL_PAPER_V18_WORKING_DRAFT.md) incorporates the existing long-period missed-candidate audit and a newly executed controlled pointing-instability experiment. In 2,000 paired simulated events per setting, a clean reference improved source assignment from 52.30% to 83.15% at the highest common displacement; a noisy reference reduced accuracy from 83.95% to 59.15% with no common displacement. [Frozen specification](NOV25_CONTROLLED_POINTING_SIMULATION_PROTOCOL.md) · [results and limitations](NOV25_CONTROLLED_POINTING_SIMULATION_RESULTS.md) · [Python](nov25_controlled_pointing_simulation.py) · [complete CSV](nov25_pointing_results.csv). These are synthetic results under idealized assumptions, not NASA mission measurements. Kepler remains the main research; the real TESS result is unchanged. Version 18 is a draft for student review, not submitted to Canvas.

**November 25 verified timing refinement (Version 19 working manuscript):** [read the updated paper](NOV25_FINAL_PAPER_V19_TIMING_REFINEMENT_DRAFT.md). The same BLS algorithm fitted to three early Kepler quarters rather than one reduced the known Kepler-69 b reference-period error from 0.06577% to 0.00098% (13 minutes versus 11.6 seconds per orbit). Using the same window duration, the refined fit produced 19/19 positive dips and passed the frozen within-star phase test in all four newly evaluated Q14–17 quarters; the Q8-only fit produced 5/19 positive windows and passed 0/4 quarters. Previously examined Q12–13 are reported separately. [Verified results and limitations](NOV25_MULTIQ_EPHEMERIS_VERIFIED_RESULTS.md) · [Frozen protocol](NOV25_MULTIQ_EPHEMERIS_PROTOCOL.json) · [Source code](nov25_multiq_ephemeris.py) · [All comparison rows](nov25_multiq_verified_quarter_comparison.csv) · [Successful original NASA data run and downloadable figure/data artifact](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/45667308389/artifacts/15048900185). One known star; this is an improvement to our own prediction with additional training data, not a new detection algorithm, mission-wide performance claim or new discovery. Version 19 is unsubmitted, for independent student review.

**November 25 expanded timing replication (Version 20 working paper):** [updated draft with a quantitative timing-uncertainty derivation](NOV25_FINAL_PAPER_V20_COHORT_WORKING_DRAFT.md) and [physics note](NOV25_TIMING_UNCERTAINTY_PHYSICS_NOTE.md). The earlier, unchanged six-planet/seven-binary cohort is now being evaluated with Q8-only versus Q8–Q10 fits on Q14–17 original observations. Planet-specific success requires both a named period match and the fixed phase test. [Precommitted protocol](NOV25_MULTIQ_COHORT_PROTOCOL.json) · [analysis code](nov25_multiq_cohort.py) · [workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/45667890631). At this update the workflow is in progress; no cohort outcome has been claimed.

## Start with the research paper

[**Main research report (Markdown)**](FINAL_REPORT_OPENING_HISTORY_FLUX_EXOMINER_AND_AI_REPLICATION_DRAFT.md) · [**November 20 status update**](NOV_20_STATUS_UPDATE_CONCISE_1_TO_2_PAGE_ORIGINAL_DATA_RESULTS_DRAFT.md) · [**Scientific articles and MEST lecture connections**](PROPOSAL_TO_RESULTS_RESEARCH_AND_CLASS_LINKS.md)

The current formatted **Version 16 process-first research paper** is six pages with approximately 2,720 main-text words, three main figures, a bibliography and the project checklist. The earlier Version 13 feature-ablation and other technical evidence are preserved as supporting research in this repository. The paper includes quantitative results, figures, literature, lessons, references and the professor's project checklist.

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
