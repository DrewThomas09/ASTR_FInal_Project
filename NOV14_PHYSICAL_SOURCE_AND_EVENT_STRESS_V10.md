# Kepler physical-source identification and single-event stress test
ASTR/PHSC 12600 | November 14, 2026 | Original NASA Kepler Q6-to-Q7 follow-up

## Connection to the November 5 proposal
This is a targeted analysis of the already completed, period-frozen Kepler transit search. It addresses the distinction between detecting a periodic drop in flux and establishing which physical body caused it. It does **not** replace the original random forest study, alter the predeclared Q6-to-Q7 test, or treat the secondary TESS adjustment as the main project.

## Important correction: the binary controls also host confirmed planets
The [original successful 12-target Kepler Q6-to-Q7 study](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43512648584/artifacts/14079785749) fitted Box Least Squares periods using original Kepler Quarter 6 measurements, then tested the same phase/period in Quarter 7 without refitting. Six of ten published planet-host targets and both prespecified eclipsing-binary controls met its fixed periodic-dip criteria.

However, **Kepler-35 and Kepler-47 are themselves published circumbinary planetary systems**. The short-period signal that passed the test in each case follows the **eclipsing stars**, rather than the much longer confirmed planetary orbit. The distinction is signal-specific, not host-specific.

| Original Q6 source | Q6 fitted peak | Published stellar binary period | Shortest confirmed planet period |
|---|---:|---:|---:|
| Kepler-35 | 10.371079 days | about 20.7337 days | Kepler-35 b: about 131.458 days |
| Kepler-47 | 7.449822 days | about 7.44838 days | Kepler-47 b: about 49.5 days |

Kepler-35's BLS peak is about **0.5002 times the binary period**, a characteristic half-period eclipse alias. Kepler-47's peak is about **1.00019 times the binary period**, almost an exact stellar-orbit match. The planet orbital periods are not what the short-period BLS search recovered.

External published astronomy used for physical identification: **Welsh et al. (2012)**, *Transiting circumbinary planets Kepler-34 b and Kepler-35 b*, Nature 481, 475–479, [DOI: 10.1038/nature10768](https://doi.org/10.1038/nature10768); **Orosz et al. (2012)**, *Kepler-47: a transiting circumbinary multiplanet system*, Science 337, 1511–1514, [DOI: 10.1126/science.1228380](https://doi.org/10.1126/science.1228380).

## Why Kepler-30 failed despite a very small phase comparison fraction
The archived **six original Quarter 7 predicted event windows** for Kepler-30 produced local depths (parts per million), in time order:

| Predicted orbit index | Local dimming (ppm) | Positive? |
|---|---:|---|
| 6 | -54.2 | No |
| 7 | +62.7 | Yes |
| 8 | **+19,093.9** | Yes |
| 9 | -635.0 | No |
| 10 | -209.3 | No |
| 11 | +735.9 | Yes |

The unaltered observed **mean** was **+3,165.9 ppm** and the **median** was **+4.5 ppm**. Just **3/6** windows had positive local depths. The original phase-shift comparison was 0.000999, but the predeclared protocol also required **at least 60% of event windows positive**. Kepler-30 therefore **failed the combined frozen rule**.

For one strictly labeled exploratory sensitivity check, omitting only the largest +19,093.9-ppm event changes the remaining **five-event mean to -19.7 ppm** and positive fraction to **2/5**. By contrast, Kepler-12 had **20/20** positive predicted windows and a mean of **+15,639.5 ppm**; after omitting its strongest window the 19-event mean still was **+15,605.3 ppm**. **This is not a re-run of the original phase-shift null distribution** or a newly preregistered statistical test. It identifies how one anomalously deep measurement can dominate a mean and why the separate consistency requirement mattered.

## Original evidence, experiment limitations and class relevance
The original-data source is the [successful November 13 Kepler Quarter 6-to-7 artifact](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43512648584/artifacts/14079785749). It retains all twelve planned systems, FITS SHA-256 records, 145 predicted Q7 windows and 11,000 within-star comparison phases. The original trial remains **6/10** planned planet hosts, **2/2** already-known stellar-binary control signals, and one unavailable later-quarter target. The paper's new Figure 8 and the local **V10 research ZIP** contain the reconstructed scientific graphic, an original-source analysis script and exact calculated JSON outputs.

This comparison adds physics to the experiment: **Lesson 2** concerns flux and which stars contribute the detected light, **Lesson 3** concerns prediction of event times, and **Lessons 5–6** distinguish stellar binary orbital periods from planetary periods under gravitational dynamics. **Lab 1 and Appendix B** explain why a precise and reproducible measurement does not necessarily identify the correct physical source.

Neither a short period nor the discovery of a planet elsewhere in the same system proves that the particular periodic eclipse measured here is planetary. The results strengthen interpretation of the submitted Kepler experiments; they are not new exoplanet discoveries or an improvement over NASA's full professional vetting pipeline.
