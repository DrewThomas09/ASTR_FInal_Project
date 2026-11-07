# Iterative BLS: second-pass planet recovery in real Kepler observations
ASTR 12600 · November 6, 2026

**Verified workflow:** https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42321423938
**Complete recorded iterations and figures:** https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42321423938/artifacts/13552579561

## Why this experiment was performed

The independent frozen external cohort (see `FROZEN_REAL_13STAR_VALIDATION_RESULTS.md`) found that the strongest BLS period was **7.6418 days around Kepler-18**, consistent with already confirmed Kepler-18 c rather than the chosen Kepler-18 b, and **10.8524 days around Kepler-20**, consistent with confirmed Kepler-20 c rather than Kepler-20 b.

This motivated a separate **exploratory development** test, coded after inspecting those failures. It is NOT independent validation. Sequential transit modeling and subtraction are established methods in exoplanet astronomy and cannot be claimed as a new invention.

## Algorithm

1. Download real Kepler Quarter 8 long-cadence quality-filtered PDCSAP photometry using the same official NASA MAST FITS loader; no published planet period is passed into BLS.
2. Search 1.5–15 days with Astropy BLS, and identify the highest-scoring periodic brightness dip.
3. Fit Astropy's box transit model at that recovered period/epoch/duration; subtract only the fitted model decrement, retaining the median brightness baseline.
4. Search residual flux again under identical period bounds. Repeat three times total; three is a fixed development choice.
5. Compare the three recovered periods to already confirmed planets **only after** the fits and publish all three peaks, including weak or repetitive results.

This code uses no new machine-learning architecture. The software was written with generative AI, while the mathematical BLS search is a preexisting published algorithm.

## Direct observations from the successful run

| Star | Iteration | BLS period (days) | Signal score (uncalibrated) | Published planet match |
|---|---:|---:|---:|---|
| Kepler-18 | 1 | 7.637935 | 80.67 | Kepler-18 c (~7.64159 d) |
| Kepler-18 | 2 | 14.859972 | 76.11 | Kepler-18 d (~14.85888 d) |
| Kepler-18 | 3 | 7.643794 | 13.66 | Still near Kepler-18 c; **not independent evidence of another planet** |
| Kepler-20 | 1 | 10.857780 | 64.63 | Kepler-20 c (~10.85410 d) |
| Kepler-20 | 2 | **3.696287** | 28.88 | **Kepler-20 b (~3.696115 d)** |
| Kepler-20 | 3 | 11.496705 | 16.47 | Unmatched; could be residual structure or noise |

### Verified scientific interpretation

- A real, independently confirmed small planet in the **Kepler-20 system** was recovered on the *second* search after the stronger first fitted signal had been removed. This establishes that multiple search iterations can be useful for existing multi-planet systems.
- For **Kepler-18**, a second known planet was recovered on the second pass, but the intended Kepler-18 b was **not** recovered by three iterations. The third peak recurred near the first period: subtracting a fitted box is not guaranteed to remove all of a real transit's light-curve shape.
- A large numerical peak score is not a calibrated planet probability and a second peak is not itself an additional confirmed planet.
- These two systems were chosen **because** the initial frozen experiment failed on their selected planet. Their successes cannot be counted as independent validation or added to the original frozen cohort's accuracy.

### Next research questions (future *independent* tests only)

1. Does subtracting the best physical transit template or masking the transit windows reduce repeated harmonics without erasing another real planet?
2. How many extra false-positive detections do repeated BLS passes produce on stars with no known strong transits?
3. Does the approach retain weak injected planets in real Kepler noise at controlled false alarm and equal computation budget?
4. Can we design a separate unbiased Kepler multi-planet holdout, publish it before model changes, and compare one-pass versus two-/three-pass period recovery?
5. Eclipsing-binary period-alias handling remains a distinct task; a planet at P will ALSO appear to have an event at P when plotted with 2P, so naive doubling is not a physical false-positive test.

## Primary references

- NASA Kepler-18 overview: https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-18
- NASA Kepler-20 overview: https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-20
- Box Least Squares, Kovacs et al. (2002): https://doi.org/10.1051/0004-6361:20020802
- Astropy BLS: https://docs.astropy.org/en/stable/timeseries/bls.html

## Authorship and limits

The draft and scripts were created with AI assistance and must be independently inspected by the student. A recovered period is not a new discovery; the planet was already confirmed. All source files, figures and run logs are retained through the Actions artifact.
