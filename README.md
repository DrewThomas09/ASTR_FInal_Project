# AI-Assisted Exoplanet Transit Search and Screening

Drew Thomas | ASTR/PHSC 12600 | Professor Buzasi

This project uses public NASA data to study how repeated dips in a star's brightness can reveal an orbiting object. It combines a standard transit search, a small machine-learning classifier, and tests of when additional measurements improve a result. The main timing result is that a longer observing baseline improved predictions for selected known systems. The classifier better reproduced historical catalog labels than a simple signal-strength rule, with a tradeoff in missed candidates.

## Submission materials

Start with the final paper. The PDF preserves the final document layout, and the browser version is convenient for reading on GitHub.

| Document | Read or download | Editable copy |
|---|---|---|
| Final paper | [PDF](submission/ASTR_Final_Paper.pdf) · [Browser version](submission/FINAL_PAPER.md) | [Word](submission/ASTR_Final_Paper.docx) |
| Project check-in | [PDF](submission/ASTR_Project_Check_In.pdf) | [Word](submission/ASTR_Project_Check_In.docx) |
| Code-review guide | [PDF](submission/ASTR_Code_Review_Guide.pdf) · [Browser version](CODE_REVIEW.md) | [Word](submission/ASTR_Code_Review_Guide.docx) |
| Submission checklist | [PDF](submission/ASTR_Project_Checklist.pdf) | [Word](submission/ASTR_Project_Checklist.docx) |

The check-in records an earlier stage of the project. The final paper includes the later timing experiments and their results.

**Repository link for course submission:** https://github.com/DrewThomas09/ASTR_FInal_Project

## Main results

| Study | Finding | Evidence |
|---|---|---|
| Kepler-69 b transit timing | Fitting Quarters 8–10 instead of Quarter 8 alone increased positive transit windows from 5/19 to 19/19 in newly evaluated Quarters 14–17. Passing quarters increased from 0/4 to 4/4 using the same window duration. | [Report](NOV25_MULTIQ_EPHEMERIS_VERIFIED_RESULTS.md) · [Table](nov25_multiq_verified_quarter_comparison.csv) |
| Replication across 13 systems | Among six planet hosts, quarters passing both the named-period and timing criteria increased from 4/24 to 12/24. Binary controls increased from 6/15 to 14/15 on the separate timing criterion. | [Report](NOV25_MULTIQ_COHORT_VERIFIED_RESULTS.md) · [All evaluation rows](nov25_multiq_cohort_verified_rows.csv) · [Summary](nov25_multiq_cohort_verified_summary.json) |
| Historical NASA label screening | On 1,619 signals from held-out stars, the random forest matched labels in 81.59% of cases versus 52.32% for the signal-strength rule. Candidate recall was lower: 87.19% versus 90.95%. | [Initial results](REAL_NASA_DR25_RESULTS_2026_11_06.md) · [Three-model validation](VERIFIED_DR25_PAIRED_SIGNIFICANCE_2026_11_08.md) |
| Pointing correction | The real TESS test reduced a local motion measure in 44/56 stars without reliably improving source identification. A separate simulation showed how subtracting a noisy reference can add error. | [Real observations](VERIFIED_NOV12_TESS_56STAR_RAW_VS_POINTING_CORRECTED_CENTROID_ROBUSTNESS.md) · [Simulation](NOV25_CONTROLLED_POINTING_SIMULATION_RESULTS.md) |

These results concern selected known systems and historical screening labels. Repeated quarters from one star are related observations. A recurring dip can come from another planet, a binary star, or another source; timing alone does not identify it. The project did not establish a new planet discovery or an improvement over NASA's full detection pipeline. The controlled pointing experiment is simulated data, separate from the astronomical observations.

## Review the code

The [code-review guide](CODE_REVIEW.md) maps each result to its source code, tables, and reproduction commands. The committed reports and tables can be reviewed in a browser without downloading NASA observations.

| Part of the project | Main files |
|---|---|
| Read and normalize original Kepler observations | [real_kepler_lightcurve.py](real_kepler_lightcurve.py) |
| Standard Box Least Squares search | [blind_transit_benchmark.py](blind_transit_benchmark.py), function `bls_peak` |
| One-star timing comparison | [nov25_multiq_ephemeris.py](nov25_multiq_ephemeris.py) · [Fixed protocol](NOV25_MULTIQ_EPHEMERIS_PROTOCOL.json) |
| 13-system timing comparison | [nov25_multiq_cohort.py](nov25_multiq_cohort.py) · [Fixed protocol](NOV25_MULTIQ_COHORT_PROTOCOL.json) |
| Catalog classifier and statistical checks | [ml_screening.py](ml_screening.py) · [dr25_paired_statistical_validation.py](dr25_paired_statistical_validation.py) |
| Controlled pointing simulation | [nov25_controlled_pointing_simulation.py](nov25_controlled_pointing_simulation.py) · [Complete results](nov25_pointing_results.csv) |

### Local setup

Python 3.11 matches the research workflows. Clone the repository, create an environment, and run commands from the repository directory.

```text
git clone https://github.com/DrewThomas09/ASTR_FInal_Project.git
cd ASTR_FInal_Project
python -m venv .venv
```

Activate it with `source .venv/bin/activate` on macOS or Linux, or `.venv\Scripts\activate.bat` in Windows Command Prompt. Then install the dependencies and run the short offline checks:

```text
python -m pip install -r requirements.txt
python -m pytest -q tests/test_project.py tests/test_kepler_fits_io.py
```

These checks use simulated inputs and temporary FITS files. They test program behavior, not astronomical accuracy. The [guide](CODE_REVIEW.md#run-the-programs-locally) gives separate commands for real-data runs, catalog screening, and the controlled simulation, including output folders and download requirements. Package versions are specified as ranges, so a new environment may produce small numerical differences.

## Research record

The research code underlying the final analysis is preserved at [commit 427f378](https://github.com/DrewThomas09/ASTR_FInal_Project/tree/427f378f57710de389052ce14b1ce9f031d9c606). The [Actions history](https://github.com/DrewThomas09/ASTR_FInal_Project/actions) contains workflow logs and available result bundles.

- [Proposal, research results, and course connections](PROPOSAL_TO_RESULTS_RESEARCH_AND_CLASS_LINKS.md)
- [Long-period error and review-cost audit](NOV13_KEPLER_LONG_PERIOD_ERROR_AND_COST_AUDIT.md)
- [Period-aware threshold experiment with a negative result](VERIFIED_DR25_PERIOD_AWARE_THRESHOLD_NEGATIVE_2026_11_08.md)
- [Real TESS tests: successful and unsuccessful approaches](VERIFIED_NOV13_FULL_RESULTS_WHAT_WORKED_WHAT_FAILED_NASA_TESS_PRF_BENCHMARK.md)
- [AI assistance log](AI_USE_LOG.md)
- [Earlier repository index](archive/README_before_submission.md)

Dated notes and earlier notebooks preserve the development history. The submission materials at the top of this page are the final course documents; the dated notes provide supporting evidence and earlier analyses.
