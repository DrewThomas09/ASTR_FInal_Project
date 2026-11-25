# November 25 timing refinement: why a small period error matters

The original Quarter 8 fit used 2,767 quality-filtered NASA measurements over BKJD 735.38–802.34 (66.96 days). It returned 13.7133429855 days for Kepler-69 b, with a fitted transit duration of 0.153 days. The NASA reference period is 13.7223682 days. Source: [verified Q8 experiment](REAL_KEPLER_LIGHTCURVE_RESULTS_2026_11_06.md).

For a fixed initial transit epoch, predicted time after N orbits is t(N) = t0 + N P. Relative to the reference period, its timing drift from period error alone is N(P_fit - P_ref).

The original period difference is 12.9963 minutes per orbit and the half-width of the fitted transit window is 1.836 hours. If the starting epoch were exact, the center of the reference transit would be outside that original predicted window after about 8.48 orbits (first integer crossing after 9 orbits, about 123.5 days). Initial-epoch error, actual duration and sampling can alter this crossover. It is not an empirical detection cutoff: partly overlapping windows and noise can still give positive measured dips.

| Number of orbits | Elapsed reference time (days) | Absolute accumulated period-only drift (hours) |
|---:|---:|---:|
| 0 | 0.0 | 0.00 |
| 5 | 68.6 | 1.08 |
| 10 | 137.2 | 2.17 |
| 20 | 274.4 | 4.33 |
| 30 | 411.7 | 6.50 |
| 40 | 548.9 | 8.66 |
| 50 | 686.1 | 10.83 |
| 60 | 823.3 | 13.00 |

Increasing the observing span should constrain the recurrence period by observing events separated by more cycles, analogous to measuring a clock across a longer interval. This is why we are comparing the same BLS algorithm fitted to Q8 alone with Q8–Q10 jointly. Neither fitted period will use the published reference number. Previously examined Q12–13 are labeled as development comparisons; Q14–17 are preselected later evaluations, and every failure will be reported. Both models will use the same Q8 duration in the primary comparison.

- [Fixed protocol](NOV25_MULTIQ_EPHEMERIS_PROTOCOL.json)
- [Analysis code](nov25_multiq_ephemeris.py)
- [Original-data workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/45667308389)

The table above is a mathematical consequence of already verified original data, not new observational results. The new workflow must complete and be checked before new quantitative success or failure can be claimed. This is a refinement of a known planet's ephemeris, not an independent discovery or a demonstrated improvement to NASA's entire pipeline.
