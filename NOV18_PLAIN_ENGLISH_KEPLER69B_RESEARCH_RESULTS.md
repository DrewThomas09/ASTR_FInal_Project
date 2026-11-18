# November 18: What we learned about predicting future exoplanet transits

**Plain-English research note | ASTR/PHSC 12600 | Original NASA Kepler light curves | November 18, 2026**

## The question

Can an AI-assisted computer program look at an older set of telescope measurements, figure out how often a known exoplanet passes in front of its star, and correctly predict future passes?

The telescope cannot see the planet directly in these light curves. Instead it measures the star's brightness. When the planet passes in front, a tiny part of the starlight is blocked. This looks like a small dip in a graph. We used an established astronomy algorithm, **Box Least Squares (BLS)**, which AI helped us write and run. We did **not** invent BLS, and we did **not** discover a new planet.

## Part 1: A good estimate

From actual NASA **Quarter 8** measurements of Kepler-69 b, our BLS program calculated that the star would dim every **13.713343 days**. NASA's published period is **13.722368 days**. That looks very close: only **0.0658%** apart.

But the small difference amounts to **about 13 minutes per orbit**. Errors like that add up over time.

## Part 2: Test the predictions on data the program has not used

We kept the Q8 period, starting time, and transit duration unchanged, then checked original Kepler measurements from later quarters. We did not move the predicted dip times after seeing the data.

| Later data | Predicted windows with visible dips | Number of predicted windows with enough data | Average measured dip |
|---|---:|---:|---:|
| Quarter 9 | 7 | 7 | 493 parts per million |
| Quarter 10 | 6 | 6 | 138 parts per million |
| Quarter 11 | 5 | 6 | 89 parts per million |
| Quarter 12 | 0 | 6 | -112 parts per million |
| Quarter 13 | 0 | 6 | -97 parts per million |

Another two predicted centers in Q11 had insufficient nearby sampling and were excluded from its usable-window total, not counted as dips. A *negative* depth in Q12 or Q13 does not mean the planet made the star brighter. It means our **fixed, incorrectly timed windows did not contain the transit dip**.

This was a real observational test with archived NASA brightness data, **not a simulation**. The first three later quarters passed the fixed within-star phase-comparison rule, but Q12 and Q13 failed. There is no independent survey-wide detection-rate claim from this single known star.

## Part 3: Did the transits really disappear?

After seeing those failures, we did a separate **explanatory** comparison: keep the *same Q8 starting transit time* and *same transit duration*, but substitute NASA's already-published, more accurate orbital period.

| Later data | Q8 fitted period: windows with dips | NASA's reference period: windows with dips |
|---|---:|---:|
| Q9 | 7/7 | 7/7 |
| Q10 | 6/6 | 6/6 |
| Q11 | 5/6 | 6/6 |
| Q12 | 0/6 | 6/6 |
| Q13 | 0/6 | 6/6 |

The Q12 and Q13 dips reappeared at the times predicted by the more accurate period. In those quarters their average brightness decreases were about **513 and 558 parts per million**. This makes accumulated timing error a convincing explanation for why the original forecast stopped working.

**Important:** We chose to check NASA's published period after observing the failures. That makes this last comparison **retrospective**, not a second blind forecasting experiment and not a new algorithmic breakthrough.

## What it means in everyday language

Imagine a clock that gains 13 minutes every time a certain event happens. At first it seems almost perfectly accurate. After 30 repeats, it is off by about **6.5 hours**. If you show up at the old predicted time, you miss the event even though it happened normally.

That is the lesson of our experiment. AI helped create code that found a real repeating signal, and the early forecasts worked. The later forecasts failed not because the star stopped dimming, but because the original clock slowly became inaccurate. A small percentage error can matter a lot when we need to predict an actual time.

## What we have not shown

- This does **not** prove the physical nature of a previously unknown planet. Kepler-69 b was already established.
- We used NASA's **processed** PDC-SAP flux measurements, not the telescope's raw pixels.
- A positive dip inside a predicted window does not rule out eclipsing binary stars or other false positives in general.
- This is one known target, so it does not establish a success rate for finding planets across all stars.
- The 1,000 alternative phase comparisons were **within the same star**. They are not independently calibrated mission-wide false-alarm probabilities.
- The NASA reference period was known in advance, but the direct two-period comparison was chosen **after** seeing the later-quarter results. It is an explanation, not confirmation of a new method.

## Research evidence and reproducibility

- **Original predeclared Q9 experiment:** [frozen rules](NOV18_Q8_TO_Q9_FORECAST_PROTOCOL_FROZEN.json), [script](nov18_kepler69b_q8_to_q9.py), [successful original NASA data run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/44310362405).
- **Longer horizon, Q10–Q11:** [frozen rules](NOV18_Q8_TO_Q10_Q11_LONGER_FORECAST_FROZEN.json), [script](nov18_kepler69b_q8_to_q10_q11.py), [successful original NASA data run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/44310853470).
- **Further horizon, Q12–Q13:** [frozen rules](NOV18_Q8_TO_Q12_Q13_FROZEN.json), [script](nov18_kepler69b_q8_to_q12_q13.py), [original NASA data failure results](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/44311241440).
- **Retrospective two-period explanation:** [method note](NOV18_POST_FAILURE_EXPLANATION_Q8_VS_NASA_PERIOD.md), [script](nov18_kepler69b_postfailure_nasa_period_check.py), [results and figure](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/44311652276).
- **Published planet information:** [NASA Exoplanet Archive: Kepler-69](https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-69), DR25 KOI reference period **13.7223682 days**, Q8 FITS source [MAST Kepler light curves](https://archive.stsci.edu/missions-and-data/kepler).
- **Why period forecasts drift in real astronomy:** [Edwards et al., *Original Research by Young Twinkle Students (ORBYTS): Ephemeris Refinement of Transiting Exoplanets*, MNRAS (2021)](https://doi.org/10.1093/mnras/staa1245).

Each GitHub Actions run stored the original FITS source SHA-256 values, individual fixed-window measurements, and results. The results above were read from those successful runs; they are not invented examples.

## Connection to class material

**Lesson 3 (Time)**: timing repeated events is useful only if the clock is accurate enough. **Lesson 6 (Kepler's laws)**: the orbital period sets the recurrence of a planet's transits. **Lab 1 and Appendix B (measurement uncertainty)**: even an apparently small measurement error can have important consequences. These are genuine course connections, not additional independent experimental findings.

## One short paragraph usable in the final report (adapt into your own voice)

I wanted to see whether the computer program could do more than find a period close to the correct one. I used its Quarter 8 measurement to predict when Kepler-69 b would block starlight during later quarters, without changing the prediction afterward. It found all seven usable dips in Quarter 9 and continued to find some in Quarters 10 and 11, but it missed all six tested windows in both Quarters 12 and 13. The reason became clearer when I compared the result against NASA's more accurate orbital period. The later dips were still there, just several hours away from the times predicted by my original model. That showed me why a 0.066% period error, which initially seemed very small, can make a difference when predicting events many months later. AI made it possible for me to build and test the program, but understanding why the predictions failed required looking more closely at the physics and at the actual measurements.
