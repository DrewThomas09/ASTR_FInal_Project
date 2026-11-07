# Initial physical-vetting ablation: what worked and what did not
Date: 2026-11-06 (UTC workflow 2026-11-07)
Run: https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42319932610
Artifact: https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42319932610/artifacts/13552831284

## Study design

A controlled, **synthetic** follow-up compared Astropy BLS (no-event veto) against exactly the same BLS fits plus a simple individual-transit check. The search range was fixed at 1.5–12 days, while injected orbital periods, epochs and phases were randomized. A BLS peak threshold of 9.5087 was selected using 24 independent **synthetic** null calibration stars (8 white-noise, 8 red-noise, 8 isolated-dip), with a nominal 10% upper-quantile target. The holdout had 35 different synthetic signals (5 per 7 categories).

A detection counted as *recovered* only when it passed the decision threshold **and** its fitted period was within 2% of the known injected period. A separate binary-like group simulates an eclipsing binary with unequal primary and secondary eclipses. That group was not used to choose the threshold.

## Results — independent synthetic holdout

| Simulation category | Number | BLS flags | BLS + event-check flags | Correct planet recoveries (BLS / event-check) |
|---|---:|---:|---:|---:|
| White noise only | 5 | 0 | 0 | N/A |
| Correlated/red noise | 5 | 0 | 0 | N/A |
| One isolated downward dip | 5 | 0 | 0 | N/A |
| Binary-like alternating eclipse | 5 | 5 | 4 | N/A |
| 500 ppm injected planet | 5 | 0 | 0 | 0 / 0 |
| 1,500 ppm injected planet | 5 | 2 | 2 | 2 / 2 |
| 4,000 ppm injected planet | 5 | 5 | 5 | 5 / 5 |

### Interpretation

1. The event check did not improve correct-period recovery in any group. A veto cannot increase recall with the BLS decision threshold held fixed.
2. It rejected **one of five** deliberately binary-like false-positive signals, leaving **four** despite apparently consistent repeated transits. That is insufficient evidence of a reliable improvement.
3. Every 500-ppm simulated transit fell below the control-derived threshold. A simple qualitative warning cannot recover a signal the detection stage never flags.
4. Small per-category denominators make any percentages highly uncertain. This is a toy experiment, **not** Kepler mission completeness, true false alarm probability, or astrophysical false-positive probability.

### Scientific realization

A binary star can show a highly stable periodic dimming pattern. A check that only asks whether the events recur and agree will not reliably separate it from a planet. This is why published Kepler vetting systems use **odd/even eclipse depth differences, secondary-eclipse checks and pixel/centroid localization** in addition to signal significance. The next version specifically measures alternating-depth/secondary evidence on a *new independent holdout*.

## Important methodological safeguard

The follow-up's diagnostic design is informed by this result, so its choice is exploratory and should not be represented as a completely untouched preregistered discovery. We freeze its code and simulation seed prior to that new run and clearly record the performance of all stages.

## Source and authorship

- `event_vetting_ablation.py` and `transit_consistency.py` in this repository.
- Underlying Box Least Squares is published: Kovacs et al. (2002), doi:10.1051/0004-6361:20020802.
- See Thompson et al. (2018), doi:10.3847/1538-4365/aab4f9, for Kepler DR25 transit vetting methods.
- All code and text drafted with generative AI assistance; the student should independently verify the scientific argument and underlying calculations.
