# Why the physical eclipse-preservation improvement is not yet statistically significant
**ASTR/PHSC 12600 | November 8, 2026 | Honest statistical-power and source-selection plan**

## What the independent astronomical experiments actually support

Our prospectively fixed [13-star Kepler Quarter 6 experiment](VERIFIED_RECURRENCE_GUARD_Q6_RESULTS_2026_11_08.md) tested eight known eclipsing binaries and five planet-host stars with the previously frozen local-step mask plus a new flux-only recurrence-preserving safeguard.

- All **13/13** source FITS were analyzable.
- The original step rule emitted **ten method-level warning rows**, all concentrated in four binary host stars. Some SAP and PDCSAP rows refer to the same physical event and must not be counted as independent successes.
- The new safeguard protected **two warning rows in two distinct binary host stars**, preventing the deletion of **42 original photometric samples** across both products.
- Original-source plots and independently published eclipse epochs provide post-hoc corroboration that the two protected events correspond to genuine stellar eclipses, but the comparisons were not blind to the selected protected cases.
- Kepler-34 had three recurrent eclipse-like epochs seen in both products, none protected because the binary period is about 27.8 days and the detector had a frozen 22-day cap. A negative result, not a reason to retune the same cohort.
- **Zero of the 13 source files had an archived Kepler quality-bit-1024 positive event** for a genuine sudden pixel sensitivity dropout (SPSD). Thus we cannot estimate sensitivity or the probability of mistakenly protecting real instrument damage on an independent source population.

Our single previously published KIC 7461601 SPSD was correctly left *unprotected*, but it was inspected during method development and cannot be pooled as fresh independent confirmation.

**Bottom line:** a method that can only restore previously masked samples necessarily appears to "save" some observations. For significance on **accuracy**, the independent scientific truth must establish which observations deserve protection and which represent genuine instrument defects. Two post-hoc verified eclipse examples are inadequate for a general sensitivity/specificity or significance estimate.

## Event-level significance limits on the two physically explained examples

For illustration **only**, there are two distinct, later corroborated eclipse-warning host cases in which the new method preserved data and the original mask did not. A naive paired exact discordance test with two improvements and zero losses gives **two-sided p = 0.50** (one-sided p = 0.25). This is **not a valid confirmatory comparison** because the observations were selected after finding protected warnings and the old rule was deliberately designed to mask every warning. A small p-value manufactured by counting every removed cadence or the same eclipse in SAP and PDCSAP as independent would be *pseudoreplication*.

Do not claim a significant improvement in the exoplanet-detection task from these data. Do not combine these results with the large and significant **historical NASA KOI classification** results: those use different labels, methods and scientific endpoints.

## How many authentic instrumental events might we need?

The [Kepler Data Processing Handbook](https://archive.stsci.edu/kepler/manuals/KSCI-19081-002-KDPH.pdf) states that roughly **3% of Kepler light curves** contain one or more noticeable downward step discontinuities *per quarter*. This is a general systematics statement, **not an established probability of having Kepler quality-bit-1024 positive annotations**. It provides only a rough illustrative prevalence scenario.

If each independent **star-quarter** were Bernoulli with true probability **p=0.03**, the binomial distribution suggests:

| Planning target | Star-quarters required under independent 3% model |
|---|---:|
| ≥1 true step with 95% chance | **99** |
| ≥10 true steps with 80% chance | **416** |
| ≥10 true steps with 95% chance | **521** |
| ≥30 true steps with 80% chance | **1,147** |
| ≥30 true steps with 95% chance | **1,313** |

Under that illustrative model, a 13-star single-quarter cohort has about a **67% chance of yielding zero visible SPSDs**, which means our observed zero is unsurprising. Counts would be *larger* if the actual archived bit-1024 incidence is less than 3%, and correlated systematics or repeated stars break the simple binomial assumptions. These figures are **preliminary source-acquisition planning numbers**, not a formal statistical power calculation for a method-difference test.

## Scientifically credible follow-up design

1. **Preselect true instrumental positives from a separate archive-label population**, based only on the published original `SAP_QUALITY & 1024` flag (before detector processing), plus a comparable independent set of binary eclipses with published primary/secondary timing and a fixed negative-control set. Archive original source IDs, file SHA-256 hashes, quarter, selection seed and all failures.
2. **Disjoint source stars:** exclude every previously studied KIC, not just the historical SPSD example. Distinct quarters from the same star should be grouped in all confidence interval calculations. Store each external binary period/epoch but do **not** give it to the flux-only detector.
3. **Freeze actual event-level scoring:** match instrument events to warnings one-to-one within ±0.22 days, with special care that bit 1024 is placed on the last good cadence before detected SPSD, not necessarily exactly at the brightness jump. For binary eclipses score warnings against archived eclipse centers/ingress windows and report ambiguous cases instead of declaring them genuine.
4. **Compare paired decisions fairly:** count on each independent host or archived physical event (not every cadence) whether the old and new masks would wrongly remove a real eclipse or wrongly preserve a genuine instrument defect. Use a **host-block permutation/exact paired test** and a **star-clustered bootstrap CI** with all denominators.
5. **Set power before gathering data:** specify a scientifically important improvement (e.g. a 15-percentage-point reduction in erasing real stellar eclipses while maintaining no more than a 5-percentage-point increase in unmasked real instrument events). Estimate required **discordant independent stars** from pilot event frequencies and freeze a final target count. Do not increase N just until p crosses 0.05 or after browsing results.
6. **Do not substitute null labels:** inverted or rolled photometric curves, unflagged quarters and confirmed planet hosts do not prove a light curve is free of real instrumental or astrophysical anomalies.
7. **Report negative tests.** If archived true defects are rare or the rule fails to protect deep binaries beyond 22 days, say the current sample is underpowered or the method has a physically demonstrated coverage limitation. Never claim success merely because code tests passed.

## Where the current statistical significance really lies

The separate [NASA DR25 host-clustered classifier study](VERIFIED_DR25_PAIRED_SIGNIFICANCE_2026_11_08.md) found a **+31.06 percentage-point balanced-accuracy advantage over an SNR-only label-screening rule**, with a **[+28.69,+33.43] percentage-point host-bootstrap interval** and a two-sided host-level conditional permutation Monte Carlo p approximately **0.00005**. This result is statistically strong **only for agreement with historical NASA Robovetter candidate/false-positive labels**. It is a *different task* from detecting a new physical planet or preserving an authentic SPSD, so the results must not be pooled into a single headline accuracy metric.

**Ethics and AI contribution:** GPT-6 assisted this power note and prior code. Student must review source definitions, all statistical assumptions, selection limits and references, and acknowledge AI involvement in the final submission.
