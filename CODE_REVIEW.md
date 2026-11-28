# Reviewing the Exoplanet Research Code

Drew Thomas | ASTR/PHSC 12600 | Professor Buzasi

The public repository contains the Python programs, fixed experiment plans, result tables, and supporting research notes used in the paper. The main results can be checked in a web browser. Running the programs is optional.

Repository: https://github.com/DrewThomas09/ASTR_FInal_Project

The research code reviewed for this guide is commit `427f378f57710de389052ce14b1ce9f031d9c606`, dated November 25, 2026. A fixed copy is available at https://github.com/DrewThomas09/ASTR_FInal_Project/tree/427f378f57710de389052ce14b1ce9f031d9c606.

## Review the results first

**Kepler transit timing.** Start with [the Kepler-69 b timing report](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/NOV25_MULTIQ_EPHEMERIS_VERIFIED_RESULTS.md), then open [the comparison table](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/nov25_multiq_verified_quarter_comparison.csv). For the paper's primary comparison, select `window_mode = common_q8_duration` and `split = new_later_quarter`. These rows compare two fits on Quarters 14–17 using the same transit-window duration. The original fit produced 5 positive windows out of 19 and passed the phase test in 0 of 4 quarters. The fit using three quarters produced 19 positive windows out of 19 and passed in all four quarters. A positive window alone is not sufficient to pass the test.

**Replication across other stars.** Read [the 13-system report](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/NOV25_MULTIQ_COHORT_VERIFIED_RESULTS.md). Its [26 fit records](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/nov25_multiq_cohort_verified_fits.csv), [104 evaluation records](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/nov25_multiq_cohort_verified_rows.csv), and [summary](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/nov25_multiq_cohort_verified_summary.json) retain successful, failed, and unavailable cases. For planet hosts, `named_period_and_pass` requires a period within 2% of the intended planet's reference and passing timing evidence. The paired comparison is 4/24 versus 12/24 quarters. Binary controls use `pass_rule`, giving 6/15 versus 14/15 paired quarters across four systems. The quarters are repeated observations of the same stars, not independent planets.

**Machine learning.** [The DR25 results](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/REAL_NASA_DR25_RESULTS_2026_11_06.md) give the complete confusion counts. On 1,619 held-out signals, the random forest matched historical NASA labels in 81.59% of cases, compared with 52.32% for the signal-strength rule. Candidate recall was 87.19% versus 90.95%. The forest rejected more historical false positives and also rejected 32 additional candidate-labeled signals. The 90% recall target was selected on validation stars, so it was not guaranteed on held-out stars. The labels are historical screening decisions.

**Pointing correction.** [The real TESS result](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/VERIFIED_NOV12_TESS_56STAR_RAW_VS_POINTING_CORRECTED_CENTROID_ROBUSTNESS.md) is separate from [the controlled simulation](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/NOV25_CONTROLLED_POINTING_SIMULATION_RESULTS.md). The simulation's [complete table](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/nov25_pointing_results.csv) contains twelve noise conditions applied to the same 2,000 simulated events. It is not a table of 24,000 independent astronomical observations.

## Follow the main code

For the timing study, read these functions in order.

1. [real_kepler_lightcurve.py](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/real_kepler_lightcurve.py), `fetch_kepler_quarter`: retrieves NASA observations, removes unusable measurements, and divides the flux by a 301-measurement running median. It records each source filename and SHA-256 checksum.
2. [blind_transit_benchmark.py](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/blind_transit_benchmark.py), `bls_peak`: calls Astropy's Box Least Squares search and returns a fitted period, starting time, and transit duration. This is an established method.
3. [nov25_multiq_ephemeris.py](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/nov25_multiq_ephemeris.py), `main`: fits Q8 alone and Q8–Q10 together before evaluating later data. The primary comparison uses the Q8 transit duration for both models.
4. [nov25_multiq_cohort.py](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/nov25_multiq_cohort.py), `run_target` and `summarize`: repeats the comparison across the fixed 13-system sample. The summary counts only quarters with results from both models.

Both timing scripts use `phase_shift_null` in [q6_to_q7_blind_ephemeris_validation.py](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/q6_to_q7_blind_ephemeris_validation.py). It compares predicted dips with 1,000 alternative phases within the same star. Its fraction is not a calibrated mission-wide false-alarm probability. `period_status` in [real_external_cohort.py](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/real_external_cohort.py) checks the reference-period relation separately.

For the classifier, read [ml_screening.py](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/ml_screening.py). `split_by_star` keeps the same star out of different partitions, `cutoff` chooses thresholds from validation data, and `metrics` reports the confusion counts. [dr25_paired_statistical_validation.py](https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/dr25_paired_statistical_validation.py) adds logistic regression and repeated splits. The classifier uses NASA catalog measurements, not measurements produced by the project's transit-search program.

## Run the programs locally

Python 3.11 matches the research workflows. Download the repository using GitHub's **Code → Download ZIP** button and extract it, or run the following commands in a terminal. Run later commands from the repository directory.

```text
git clone https://github.com/DrewThomas09/ASTR_FInal_Project.git
cd ASTR_FInal_Project
python -m venv .venv
```

Activate the environment with `source .venv/bin/activate` on macOS or Linux, or `.venv\Scripts\activate.bat` in Windows Command Prompt. Then install the listed packages.

```text
python -m pip install -r requirements.txt
```

These requirements use version ranges rather than an exact environment lock. Small numerical differences can occur with different package versions. Keep a separate copy of the committed result tables when comparing a new run.

**Offline software checks**

```text
python -m pytest -q tests/test_project.py tests/test_kepler_fits_io.py
```

These tests check star separation, threshold selection, simulated data, and reading FITS files without downloading NASA data. They check program behavior, not astronomical accuracy. The full suite is available with `python -m pytest -q tests`.

**Controlled pointing simulation**

```text
python nov25_controlled_pointing_simulation.py
```

This needs no NASA download. It writes `nov25_pointing_results.csv`, `nov25_pointing_simulation.png`, and `nov25_pointing_simulation.svg` in the repository directory. It replaces the local copy of that result CSV.

**Original NASA observations**

```text
python real_kepler_lightcurve.py
python nov25_multiq_ephemeris.py
python nov25_multiq_cohort.py
```

These are separate runs. The first recovers Kepler-69 b and tests simulated transits added to real stellar measurements. The second reproduces the one-star timing refinement. The third reproduces the 13-system comparison. Their outputs are in `results/real_kepler/`, `results/nov25_multiq_ephemeris/`, and `results/nov25_multiq_cohort/` respectively. The last two include fit records, individual event windows, alternative-phase comparisons, summaries, and source information.

NASA access is required unless the original FITS files are already under `data/kepler_fits/` with their original filenames. Downloads and timing comparisons take longer than the offline checks. The cohort run uses four worker processes. An unavailable file remains an unavailable case rather than a zero detection.

**Catalog screening**

```text
python ml_screening.py --download --output results/ml
```

This downloads the catalog to `data/kepler_dr25.csv` if that file is absent. It writes `comparison.csv`, `metrics.json`, and figures under `results/ml/`. The broader three-model comparison is:

```text
python dr25_paired_statistical_validation.py --csv data/kepler_dr25.csv
```

Its results go to `results/dr25_inference/`. This second command requires the original catalog checksum recorded in the fixed protocol and stops if the input differs. Do not change that check to make a different download count as the archived experiment.

## Supporting records

The repository's Actions tab contains the original workflow logs and available downloadable result bundles. The committed tables above provide a simpler route for checking the paper's numbers. The early `Kepler_AI_Project_Colab.ipynb` notebook contains introductory simulations and catalog screening, but does not reproduce the later timing studies. The paper's timing results should be reviewed through the two November 25 scripts and their fixed protocols.
