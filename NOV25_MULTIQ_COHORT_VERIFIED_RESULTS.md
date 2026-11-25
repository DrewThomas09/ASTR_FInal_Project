# November 25: Expanded multi-quarter timing replication — verified results

**Status:** Successful GitHub Actions run using original archived NASA Kepler long-cadence FITS. The original [13-target cohort](real_external_cohort_frozen.json) and [new protocol](NOV25_MULTIQ_COHORT_PROTOCOL.json) were fixed before this run. Kepler-69 b is excluded. These are previously studied hosts, not newly selected or random targets, but Q14–17 are newly evaluated in this project.

## Design and provenance

Both models used identical BLS search bounds (0.9–15 days), preprocessing, and the original Q8 fitted duration for evaluation. The baseline used Q8 alone; the refinement used Q8–Q10 together. Fitted periods and epochs were fixed before reading later-quarter flux. Planet-specific success required a named reference period match within 2% AND the predeclared within-star phase criterion; binary controls were evaluated separately with phase evidence only. All missing inputs and all negative results are retained.

- [Successful workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/45667890631).
- [Full artifact: original-data provenance, code outputs, figure, errors, phase controls](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/45667890631/artifacts/15048765886); workflow-reported ZIP SHA-256: `6f9bb168a8c20b5236b1c1c3c752126d1d8935e30728ace73307fb37843d525b`.
- [All 26 model fits](nov25_multiq_cohort_verified_fits.csv), [all 104 model-quarter rows](nov25_multiq_cohort_verified_rows.csv), [summary](nov25_multiq_cohort_verified_summary.json): transcribed programmatically from completed job logs, not simulated.
- [Python implementation](nov25_multiq_cohort.py).

## Results

| Endpoint | Paired star-quarters | Q8-only passes | Q8–Q10 passes | Improved | Worsened | Both pass | Neither |
|---|---:|---:|---:|---:|---:|---:|---:|
| Named planet period + phase | 24 | 4 | 12 | 8 | 0 | 4 | 12 |
| Planet hosts, phase only | 24 | 9 | 19 | 12 | 2 | 7 | 3 |
| Binary controls, phase only | 15 | 6 | 14 | 9 | 1 | 5 | 0 |

All six planet targets supplied all four paired quarters. For the seven binary controls, only four systems and 15 of 28 planned quarters supplied paired results. KIC 2305543 lacked Q8/Q9 training data; KIC 3248019 and 3654950 lacked Q10; KIC 9851944 lacked Q15 evaluation data. Baseline-only results where present remain in the row file; they are not included in paired counts. No targets were substituted.

| Target | Type | Q8 period (days) | Q8–Q10 period (days) | Reference relation, baseline / refined | Original passing quarters | Refined passing quarters |
|---|---|---:|---:|---|---:|---:|
| Kepler-19 b | planet | 9.285008 | 9.287458 | exact / exact | 0/4 | 4/4 |
| Kepler-93 b | planet | 4.726541 | 4.726841 | exact / exact | 4/4 | 4/4 |
| Kepler-21 b | planet | 13.114060 | 13.532579 | unmatched / unmatched | 0/4 | 0/4 |
| Kepler-20 b | planet | 10.852375 | 10.853902 | unmatched / unmatched | 0/4 | 0/4 |
| Kepler-18 b | planet | 7.641800 | 14.858799 | unmatched / unmatched | 0/4 | 0/4 |
| Kepler-68 b | planet | 5.400550 | 5.399542 | exact / exact | 0/4 | 4/4 |
| KIC 1026032 | binary | 8.457206 | 8.459765 | exact / exact | 0/4 | 4/4 |
| KIC 2305543 | binary | Unavailable | Unavailable | unavailable / unavailable | — | — |
| KIC 2306740 | binary | 5.151749 | 10.307849 | half_period_alias / exact | 4/4 | 3/4 |
| KIC 3248019 | binary | 1.334391 | Unavailable | half_period_alias / unavailable | — | — |
| KIC 3654950 | binary | 4.066865 | Unavailable | half_period_alias / unavailable | — | — |
| KIC 4544587 | binary | 2.189323 | 2.189132 | exact / exact | 1/4 | 4/4 |
| KIC 9851944 | binary | 1.082176 | 1.081986 | half_period_alias / half_period_alias | 1/3 | 3/3 |

For planet targets the last columns require named-period and phase evidence. For binaries they require phase evidence only. A dash means no paired quarter, not zero observed passes. Period match means within 2%; it is a descriptive comparison to a published reference and not an independent planet confirmation.

## Interpretation

The planet-specific result increased from 4/24 (16.7%) to 12/24 (50%). Kepler-19 b and Kepler-68 b improved from 0/4 to 4/4; Kepler-93 b remained 4/4. For all three stars whose original fit already matched the named planet, the refined fit was closer to the catalog period. The other three named planets remained unmatched. On Kepler-20, for example, a highly repeatable 10.853902-day signal still did not match the 3.696115-day reference for the intended planet. Earlier evidence identified the nearby period with Kepler-20 c; this study alone does not independently determine which object caused that signal. On Kepler-18, the fit changed from 7.641800 to 14.858799 days, neither matching the named 3.504725-day period. No physical identification is inferred from that change.

For binary controls, phase-only passes increased from 6/15 to 14/15. KIC 2306740 changed from a half-period alias to an exact reference match, yet lost one phase-passing quarter. This shows a more accurate reference-period fit need not improve every timing test. The stronger recurring signals from known binaries also illustrate why phase coherence cannot itself establish a planet's identity.

## Limits

This is a purposeful small sample and a descriptive paired comparison, not a Kepler-wide detection rate. The 24 planet-star quarters are clustered within six stars; the 15 binary-star quarters are clustered within four stars. No independent-quarter significance test is reported. Repeated passes may reflect the same signal and data availability may affect the binary comparison. More data and longer baseline changed together. The method uses a standard BLS algorithm, and its strongest signal can belong to another planet, an eclipse, or another source. This is evidence for improved timing in selected systems, not evidence that AI discovered new planets or improved NASA's full pipeline. The student must review and understand the results and acknowledge AI assistance before submission.
