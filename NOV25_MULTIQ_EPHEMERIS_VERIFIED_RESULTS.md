# November 25: A longer baseline improves Kepler-69 b transit timing

**Original NASA observations; completed, source-verified workflow.** This is a method refinement of a single known planet's ephemeris, not a planet discovery or a new transit-search algorithm.

## Actual data and experiment

The [protocol](NOV25_MULTIQ_EPHEMERIS_PROTOCOL.json) was committed before the experiment (commit 277380fba9bca5b355641f29b1aff2d3ad860cf5). The [workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/45667308389) completed successfully. The [artifact](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/45667308389/artifacts/15048900185) contains all model fits, event windows, phase comparisons, source SHA-256 hashes and the figure; artifact ZIP SHA-256 reported by the workflow: `bd10545ca30a9ce6619e421bcffef69f9821d2f5bf52e0729ccb192aa2346880`.

Both models used the same broad 1.5–20 day BLS search, with existing independent per-quarter normalization. Q8 alone was compared with concatenated Q8–Q10. Both fits were frozen before opening the later evaluation observations. The published NASA period was used only for comparison after the fits. The primary evaluation used an identical 0.153-day window duration (the original Q8 fit) for both methods, so the longer native fitted duration of the refined model does not explain its improvement.

| Model | Cadences | Time span (days) | Estimated period (days) | Absolute reference error (%) | Absolute reference drift per orbit (seconds) |
|---|---:|---:|---:|---:|---:|
| Q8 only | 2767 | 66.96 | 13.713342985504 | 0.06577009 | 779.779 |
| Q8–Q10 | 11172 | 264.88 | 13.722233693299 | 0.00098020 | 11.621 |

NASA reference: 13.7223682 days. Absolute period error against that catalog value fell by 98.510%, a factor of 67.10. These are differences against the reference, not confidence intervals or independently established true period uncertainties.

## Primary results: same 0.153-day duration

| Quarter | Evaluation status | Q8-only positive/usable | Q8–Q10 positive/usable | Q8-only mean dip (ppm) | Q8–Q10 mean dip (ppm) | Q8-only phase fraction | Q8–Q10 phase fraction |
|---:|---|---:|---:|---:|---:|---:|---:|
| 12 | Previously examined | 0/6 | 6/6 | -111.74 | 554.48 | 0.977023 | 0.000999 |
| 13 | Previously examined | 0/6 | 6/6 | -97.24 | 571.64 | 0.994006 | 0.000999 |
| 14 | New later evaluation | 0/6 | 6/6 | -125.37 | 515.54 | 1.000000 | 0.000999 |
| 15 | New later evaluation | 3/6 | 6/6 | -62.65 | 544.99 | 0.954046 | 0.000999 |
| 16 | New later evaluation | 2/5 | 5/5 | -98.38 | 504.14 | 0.977023 | 0.000999 |
| 17 | New later evaluation | 0/2 | 2/2 | -165.91 | 585.76 | 0.995005 | 0.000999 |

Previously examined Q12–13: 0/12 versus 12/12 positive windows; 0/2 versus 2/2 quarters passed the fixed criterion. Newly evaluated Q14–17: 5/19 versus 19/19 positive windows; 0/4 versus 4/4 quarters passed. Both models had the same usable-window counts in each quarter, although their predicted times differ. All six evaluation quarters were available. Each model had 22 centers within the Q14–17 observing spans, of which 19 passed coverage requirements. The native-duration sensitivity comparison gave the same window counts and pass/fail outcomes.

The phase criterion requires at least two usable windows, at least 60% positive local depths, and a within-star phase comparison fraction no greater than 0.01 based on 1,000 alternative phases. The positive-window count alone does not establish transit detection: the five positive Q8-only windows in Q15–16 had negative *quarter mean* depths and failed the phase test. The phase fraction is not a calibrated mission false-alarm probability. The Q17 conclusion rests on only two usable windows.

## What changed

A longer observing baseline makes a small error in the recurrence period easier to distinguish. The original fit was about 13 minutes short per orbit; the new fit was about 11.6 seconds short relative to NASA's period. For 30 orbits the reference-relative period-only drift decreases from 6.50 hours to 5.81 minutes. The actual forecasts also depend on the fitted starting epoch, which was independently estimated by both fits.

This is a genuine improvement of our prediction on the same known star using additional training data and a standard algorithm. The target was deliberately chosen after previous results, the catalog period was already known to us, the later observations come from the same star, and the longer time span and greater number of measurements changed together. We cannot infer how well this works on other stars or that AI itself invented a better astronomical algorithm. Q12–13 are exploratory development comparisons, not fresh holdout evidence.

- [Frozen experimental protocol](NOV25_MULTIQ_EPHEMERIS_PROTOCOL.json)
- [Exact analysis code](nov25_multiq_ephemeris.py)
- [All 24 output rows transcribed programmatically from the successful job log](nov25_multiq_verified_quarter_comparison.csv)
- [Full original-source analysis artifact, including figure and source manifest](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/45667308389/artifacts/15048900185)
- [Timing physics and prior measurement](NOV25_TIMING_DRIFT_PHYSICS_AND_REFINEMENT.md)

The AI assistant implemented and executed this continuation; the student must independently review, understand, and acknowledge the assistance before submitting course work.
