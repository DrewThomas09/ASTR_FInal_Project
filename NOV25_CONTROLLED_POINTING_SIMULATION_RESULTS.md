# November 25: When does reference-star pointing correction actually help?

**Controlled synthetic experiment, ASTR/PHSC 12600.** This is a supplemental explanation of the earlier negative TESS source-localization result, not a fresh astronomical observation. The main research remains the Kepler transit search and historical-label classifier in the November 5 proposal.

## Design and physical interpretation

The [specification was committed before execution](NOV25_CONTROLLED_POINTING_SIMULATION_PROTOCOL.md). A target at x=0 pixels and a neighbor at x=1 pixel have fluxes 1 and 0.25 in arbitrary units. A 1,000 ppm total-light decrease removes 0.00125 flux units from exactly one star. From the flux-weighted centroid x=(F_target*x_target+F_neighbor*x_neighbor)/(F_target+F_neighbor), the out-of-event centroid is 0.2 pixels. The exact target-dimming shift is +0.000200200 pixels (toward the neighbor); the exact neighbor-dimming shift is -0.000800801 pixels (toward the target). This shows why the direction of movement, rather than simply its size, can identify the source in this two-star model.

For each of twelve conditions, simulate 1,000 events of each source type. The total brightness loss is identical in both classes. The raw measured centroid difference equals the true shift plus a common in/out pointing displacement plus science measurement noise. The corrected value subtracts a reference star's measured displacement. The source rule is fixed: positive shift means target, negative shift means neighbor. The same random events are used across all conditions and comparisons. These are 2,000 paired simulated events per setting, **not 24,000 independent observations**.

## Complete actual executed results

| Common displacement SD (pixels) | Reference noise SD (pixels per cadence) | Uncorrected source accuracy | Corrected source accuracy | Change (percentage points) |
|---:|---:|---:|---:|---:|
| 0 | 0.0005 | 83.95% | 83.15% | -0.80 |
| 0 | 0.002 | 83.95% | 71.85% | -12.10 |
| 0 | 0.006 | 83.95% | 59.15% | -24.80 |
| 0.0005 | 0.0005 | 77.00% | 83.15% | +6.15 |
| 0.0005 | 0.002 | 77.00% | 71.85% | -5.15 |
| 0.0005 | 0.006 | 77.00% | 59.15% | -17.85 |
| 0.002 | 0.0005 | 59.85% | 83.15% | +23.30 |
| 0.002 | 0.002 | 59.85% | 71.85% | +12.00 |
| 0.002 | 0.006 | 59.85% | 59.15% | -0.70 |
| 0.008 | 0.0005 | 52.30% | 83.15% | +30.85 |
| 0.008 | 0.002 | 52.30% | 71.85% | +19.55 |
| 0.008 | 0.006 | 52.30% | 59.15% | +6.85 |

In the highest common-displacement/cleanest-reference condition, 777 events became correctly assigned and 160 became incorrectly assigned, for a net 617 additional correct assignments among 2,000 events. RMSE went from 0.008109 to 0.000405 pixels. With no common pointing error and the noisiest reference, 144 became correct but 640 became incorrect; RMSE increased from 0.000352 to 0.002180 pixels. Class-specific counts, all RMSE values, paired Monte Carlo standard errors and exact results are included in the [CSV](nov25_pointing_results.csv). With a perfectly common shift, corrected results are invariant to common pointing SD by construction; this is not a real-telescope result.

## Why this happens: simple uncertainty calculation

Let J be the common in/out displacement, E_s the independent science centroid error, and E_r the reference centroid error. The raw error is J+E_s; the corrected error is E_s-E_r. Their expected variances are sigma_J^2+sigma_s^2 and sigma_s^2+sigma_r^2 respectively, where science and reference errors are differences of means. With 12 in-event and 24 out-of-event samples, sigma_r = s_r * sqrt(1/12 + 1/24), where s_r is the per-cadence reference error. In this ideal model, correction reduces expected squared centroid error only if sigma_J > sigma_r. For the three reference noise settings, the corresponding break-even common-displacement SDs are 0.000177, 0.000707 and 0.002121 pixels. This is a model-derived interpretation, not a measured TESS instrument specification. It is closely related to Appendix B's propagation of independent uncertainty and accuracy/precision distinction.

## What this adds to the project

The earlier real TESS test reduced a local motion proxy in 44/56 stars but did not reliably improve identification of the dimming source. This controlled simulation shows a possible mechanism: subtracting a noisy reference can add more error than it removes. It cannot establish that this mechanism caused the real TESS outcomes. The two-star blend, chosen signal depth/noise levels, equal source frequencies, Gaussian errors, and exactly shared pointing are simplifications; aperture effects, spatially variable systematics and real reference-star behavior are not modeled. No mission performance, astrophysical planet-validation accuracy or novel detection algorithm is claimed.

## Reproduction

- [Frozen pre-execution protocol](NOV25_CONTROLLED_POINTING_SIMULATION_PROTOCOL.md)
- [Executed Python script](nov25_controlled_pointing_simulation.py)
- [Complete result CSV](nov25_pointing_results.csv)
- Run: `python nov25_controlled_pointing_simulation.py` (NumPy 2.3.5, Matplotlib 3.10.8 used for this run). Generates the table and PNG/SVG figure.
- [Earlier real TESS experiment](VERIFIED_NOV13_FULL_RESULTS_WHAT_WORKED_WHAT_FAILED_NASA_TESS_PRF_BENCHMARK.md)
- Generative AI assisted in designing, implementing, executing and documenting this simulation. The student should independently review the derivation, reproduce the code, and acknowledge this assistance in the final work.
