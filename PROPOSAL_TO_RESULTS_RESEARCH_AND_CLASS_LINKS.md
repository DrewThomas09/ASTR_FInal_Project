# November 5 proposal: research, method choices and course connections
**ASTR/PHSC 12600 | Working research companion | November 13, 2026**

## Submitted proposal is controlling
The uploaded one-page proposal, `Drew Thomas - Testing AI's impact in Exoplanet Research`, signed November 5, 2026, asks whether AI can **replicate/improve established exoplanet techniques**, using original NASA Kepler observations,  Python, a conventional transit search, and a simple ML classifier. It promises an SNR screening comparison using accuracy, false-positive rate, candidate recovery, source code, figures, quantified evidence and reflection about AI versus human scientific judgment. The proposal itself **does not promise TESS, ExoMiner replication, or discovery of a new planet**. Do not rewrite the submitted proposal or retrospectively suggest those were initial commitments.

## What was actually done, and where to reproduce it

| Original commitment or optional extension | Original evidence | Source code | Main report |
|---|---|---|---|
| Kepler transit search from original stellar flux | [Kepler Q8 original FITS summary and artifact](REAL_KEPLER_LIGHTCURVE_RESULTS_2026_11_06.md), period 13.71334 d vs 13.72237 d | [real_kepler_lightcurve.py](real_kepler_lightcurve.py), [blind_transit_benchmark.py](blind_transit_benchmark.py) | Section 2 |
| Quantitative comparison vs simple screening | [Held-out DR25 metrics](REAL_NASA_DR25_RESULTS_2026_11_06.md), 1,619 test signals | [ml_screening.py](ml_screening.py), [dr25_paired_statistical_validation.py](dr25_paired_statistical_validation.py) | Section 3 |
| Evaluate robustness and missed candidates | [Paired host-level report](VERIFIED_DR25_PAIRED_SIGNIFICANCE_2026_11_08.md), long-period 44/71 forest retained vs 66/71 logistic | Same model code; frozen original predictions in workflow artifact | Section 3 |
| Document original data sources | NASA MAST and Exoplanet Archive records, recorded source hashes | Python and frozen protocol files in root | Methods and References |
| Optional small physical correction, not in proposal | [TESS 56-star source measurements and negative validations](VERIFIED_NOV13_FULL_RESULTS_WHAT_WORKED_WHAT_FAILED_NASA_TESS_PRF_BENCHMARK.md) | TESS experiment scripts in repository | Section 5 |

## Paper-by-paper research notes

### 1. Kovács, Zucker & Mazeh (2002), Astronomy & Astrophysics 391, 369-377
**Article:** *A box-fitting algorithm in the search for periodic transits.* DOI: https://doi.org/10.1051/0004-6361:20020802.

**Problem they addressed:** Weak, short-lasting periodic dimming is not well represented by a smooth sinusoidal variation. The authors proposed finding repeating box-like departures from a steady flux level while scanning trial frequencies and durations. Their detection significance depends on both how deep the event is and the measurement noise.

**How it changed this project:** Motivated our first benchmark: use a documented BLS library implementation on a real single-quarter Kepler light curve, with the search range fixed before checking the numerical published period. We explicitly measured the relative period error.

**What we did NOT reproduce:** We did not rederive the full 2002 statistical analysis, compare every detector from that paper, or independently establish its detection thresholds.

### 2. McCauliff et al. (2015), The Astrophysical Journal 806, 6
**Article:** *Automatic Classification of Kepler Planetary Transit Candidates.* DOI: https://doi.org/10.1088/0004-637X/806/1/6.

**Problem:** A transit-like dip can come from a planetary transit, a stellar eclipse or instrumental noise. Manual vetting does not scale easily. The authors trained a random forest on numerous diagnostic measurements from Kepler and highlighted problems when inference moves to different period populations.

**How it changed this project:** We used a much smaller four-number forest, avoided confusing label agreement with planet proof, and added a long-period subgroup diagnosis when the model rejected more candidates than expected. We also compared a same-four-input logistic regression to the forest.

**Crucial non-comparison:** Their reported classification error and our 81.59% label agreement concern **different labeled populations, features, splits and objectives**. We never call ours a reproduction or improvement of their reported performance.

### 3. Thompson et al. (2018), ApJS 235, 38
**Article:** *Planetary Candidates Observed by Kepler VIII: A Fully Automated Catalog with Measured Completeness and Reliability Based on Data Release 25.* DOI: https://doi.org/10.3847/1538-4365/aab4f9.

**Problem:** Labeling many events as planet candidates requires a systematic process and estimates of both missing real planets (completeness) and accepting false signals (reliability). The Robovetter paper used simulated injected transit events and false alarm controls, including period/SNR subgroup analysis.

**How it changed this project:** The actual target column `koi_pdisposition` in the DR25 KOI table was treated as a **historical screening label**. Our performance is not a planet-occurrence or completeness claim. We report false-positive rate and candidate recall alongside accuracy; our very small injection demonstration is clearly marked insufficient to estimate population completeness.

**Source note:** The DR25 KOI table can be checked directly against NASA Exoplanet Archive column definitions: https://exoplanetarchive.ipac.caltech.edu/docs/API_kepcandidate_columns.html.

### 4. Kepler team (2010), ApJ Letters 713, L103
**Article:** *Pre-spectroscopic False-Positive Elimination of Kepler Planet Candidates.* DOI: https://doi.org/10.1088/2041-8205/713/2/L103.

**Problem:** Eclipsing stars and blended neighboring stars can mimic planets. Original vetting methods compare odd/even transit depths, look for secondary eclipses and study flux-weighted centroids and in/out-of-event difference images to locate the source of the dimming.

**How it changed this project:** Motivated our event-consistency check and later the **separate TESS centroid test**. It also supplied the reason for rejecting an easy but wrong conclusion: if a nearby star actually dims, a shift in the measured center of light is not necessarily noise.

**Limitation:** TESS point-correction subtraction is our simple follow-up; it is **not** a published, validated improvement to this Kepler team's techniques.

### 5. Valizadegan et al. (2022), The Astrophysical Journal
**Article:** *ExoMiner: A Highly Accurate and Explainable Deep Learning Classifier That Validates 301 New Exoplanets.* DOI: https://doi.org/10.3847/1538-4357/ac4399.

**Problem:** Multiple different physical diagnostics need to be integrated to evaluate candidate signals. ExoMiner uses an explicitly richer network than our small forest, including specialized data views.

**How it changed this project:** Explained why our four scalar features omit detailed transit morphology, odd/even and spatial source information. It made it inappropriate to claim we outperformed NASA's existing validation work or recreated ExoMiner. We preserve detailed ExoMiner research in [the archived technical document](ARCHIVE_LONGFORM_EXOMINER_TESS_TECHNICAL_DRAFT_BEFORE_PROPOSAL_ALIGNMENT.md), **not** as the assigned Kepler main experiment.

### Additional official references
- [NASA Exoplanet Archive Kepler-69 reference period and stellar system](https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-69).
- [NASA DR25 pipeline dispositions and parameter definitions](https://exoplanetarchive.ipac.caltech.edu/docs/API_kepcandidate_columns.html).
- [Astropy BoxLeastSquares API](https://docs.astropy.org/en/stable/timeseries/bls.html).
- [NASA MAST Kepler data](https://archive.stsci.edu/missions-and-data/kepler).

## MEST lecture and lab mapping, with original uploaded PDF pages

| Source | Actual class concept | How the program uses it |
|---|---|---|
| **Lesson 2: Geometry and Measurement**, PDF slides **40-41** | Star's intrinsic luminosity versus observed flux; `F = L/(4πd²)` | Normalized Kepler light curve is a detector measurement of varying relative flux, not total luminosity |
| **Lesson 2**, slides **49-50** | Diffraction and resolution limits | Spatially blended nearby stars can produce misleading centroid shifts or diluted eclipses |
| **Lesson 3: Time**, including slide **3** and timekeeper discussion | Reliable measurement of elapsed time and repeatable periods | BLS uses timestamps to fit a repeating transit period |
| **Lesson 6: Kepler's Laws**, slides **1-8** | Ellipses, equal-area motion and `P² ∝ a³` | Orbital period inferred from repeated dimming is related to orbit scale, conditional on stellar mass |
| **Lesson 5/6: Newtonian gravity** | Dynamical relation `P² = 4π²a³/G(M_star+M_planet)` | Caution against interpreting photometric period as an independently measured orbital size or planet confirmation |
| **Lab 1: Speed of Light**, especially lab uncertainty discussion | Compare measured vs accepted value, uncertainty, precision and instrument limits | Our 0.06577% period error is a reference comparison and must not be called a discovery probability |
| **Lab Manual Appendix B**, PDF page **3** | Accuracy vs precision; random versus systematic errors | A lower centroid scatter is not necessarily more accurate identification of the dimming source |

This mapping names topics actually present in the uploaded slide decks, not invented course activities. Include the official *Final Project Checklist Form.docx* with a completed lecture table at final submission.

## Tested small refinements, without inflated claims

1. **Kepler quality filtering and median normalization:** `SAP_QUALITY==0`, PDC-SAP flux, 301-cadence window; produced an interpretable known-target BLS fit. We did **not** measure an isolated raw-versus-corrected performance gain.
2. **Individual events:** Five adequately sampled dips; median odd/even difference around 24.6 ppm. This was a consistency diagnostic, not proof of planetary origin.
3. **Simulated transits in real Kepler noise:** 500 ppm: 1/3 period recoveries; 1,500 and 4,000 ppm: 3/3 each. Not a planet detection-efficiency estimate.
4. **ML experimental fairness:** 4,824/1,611/1,619 grouped-by-host train/validation/test, feature preprocessing with train-only imputation, cutoffs based on validation stars, four-feature logistic control, long-period failure reporting.
5. **TESS centroid subtract-pointing experiment:** 44/56 lower local movement proxy, but only 2/4 expected source directions improved in the separately chosen usable subset. No demonstrated classifier or source-location improvement.

## Source data and reproducibility

The Python code, archived Kepler observations, NASA catalog dispositions, group-separated test outputs and original figure files are maintained in the repository. The programs can be evaluated by reproducing the Kepler-69 b period, checking the model's confusion-matrix counts and examining the TESS correction's physical limitations.

## Relevant project submission requirements
Course *FinalProject.pdf* says a research paper requires **at least 2,500 words**, includes a quantitative component, synthesizes **at least two lectures** (third for optional bonus), cites external work, and appends the official checklist. The **November 20 status update** is a different deliverable from the **December 11 final**, and this is preparatory work rather than an uploaded Canvas submission.
