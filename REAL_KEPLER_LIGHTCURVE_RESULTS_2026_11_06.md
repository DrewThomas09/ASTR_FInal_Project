# Independently verified real Kepler light-curve results
2026-11-06 | ASTR 12600 | Observation-based feasibility study

**Run:** https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42319839037
**Artifact:** https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42319839037/artifacts/13551514247

The archived raw source is NASA MAST Kepler **PDCSAP** long-cadence FITS; download used the official MAST API URI after the static archive host returned HTTP 403. All astronomy numbers below come from the successful workflow's stored JSON, CSV and figures. These are independently inspected results, not AI predictions of what a hypothetical run might yield.

## 1. Real known planet: Kepler-69 b

- Kepler target: **KIC 8692861**, observation **Quarter 8**.
- Quality-filtered flux points: **2,767**, covering BKJD **735.38–802.34**.
- Input FITS: `kplr008692861-2011073133259_llc.fits`; SHA256 `2a91205f2f40e494da7fea65d7932e54735ac67bedc5584e87f8e9f685ad11c0`.
- Published Q1–17 DR25 catalog period: **13.7223682 days** (NASA Exoplanet Archive). Source: https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-69
- Astropy Box Least Squares fit: **13.7133429855 days**, using a *predeclared 1.5–20-day* search range.
- Difference: **0.00902521 days** or **0.06577%** of the reference period.
- Fitted depth: **529 ppm**; fitted duration **0.153 days**. The fitted values depend on the quarter, detrending and BLS template.
- Five sufficiently sampled fitted transit events. Each individual event showed a positive estimated depth, the strongest accounted for ~22.3% of the sum of squared positive depth-SNR contributions, and the odd/even median depth difference was ~24.6 ppm. No simple event-consistency warning was triggered.
- **Limitations:** A successful single-quarter known-target fit does not estimate survey-wide detection rate or independent planet confirmation. The target identity and broad period range were selected for a sanity check; only the exact 13.7223682-day period was withheld until after fitting. This is not a blind *target-selection* experiment.

## 2. Injected planets in *observed* Kepler brightness variability

- Comparison target **KIC 2436365**, Quarter 2, **3,662** quality-filtered cadences (BKJD 169.79–258.47).
- Input FITS: `kplr002436365-2009259160929_llc.fits`; SHA256 `00d41d21662c81706546445197ce85cf2a8f4f8dcebad0320f68375649ed6c96`.
- The target is used in official Kepler/Lightkurve data-quality notebooks: https://spacetelescope.github.io/mast_notebooks/notebooks/Kepler/instrumental_noise_1_data_gaps_and_quality_flags/instrumental_noise_1_data_gaps_and_quality_flags.html
- Each synthetic box transit had a random orbit of **2.1–9.8 days**, with random epoch and duration, injected **after** the fixed 301-cadence running-median detrend. Actual star brightness noise, sampling and gaps were preserved.
- BLS tested 1.5–12 day periods, without receiving the injected period.
- **500 ppm:** 1/3 fitted periods within 2% of injection.
- **1,500 ppm:** 3/3 fitted periods within 2%.
- **4,000 ppm:** 3/3 fitted periods within 2%.

**Limitations:** Only 3 trials per depth—too few for reliable completeness estimates. Recovery here measures fitted-period accuracy, NOT the fraction passing a statistically controlled detection threshold. These are *synthetic* box transits added to *real* stellar noise; they are not observations of nine actual planets. The preprocessed baseline star is not proved planet-free.

## 3. What this proves and what it does not

**Supported:** The AI-assisted pipeline can download two genuine Kepler light curves, parse real quality flags, apply fixed preprocessing, fit a published planet's period to within 0.066%, characterize individual events, and recover most stronger injected signals in a small actual-noise test.

**Not supported:** a new planet, population-level sensitivity, full control of instrument false-alarm rates, planetary-source localization, precise planet occurrence, or a statistically established advantage over published NASA pipelines.

## 4. Next preregistered experiment

A separate independently held-out test of BLS alone versus BLS plus event-consistency and physically motivated binary/eclipsing-binary diagnostics. It must report **both** false alarms retained and true simulated planets lost. Any thresholds informed by this preliminary experiment must be frozen before a new holdout run. True planets can have a secondary occultation; any such veto may reject real planets.

## 5. Reproducibility

The source and exact FITS SHA256 are recorded in `real_kepler_summary.json` within the Action artifact. The saved plots are `kepler69b_folded.png` and `real_noise_injection.png`, and all individual-event/injection CSVs are retained. Original public data come from NASA MAST; code is AI-generated and student scientific interpretation must be independently verified.
