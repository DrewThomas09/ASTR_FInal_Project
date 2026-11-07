# Real Kepler observational check: a known planet and a published eclipsing binary
ASTR 12600 | November 6, 2026 (GitHub run recorded November 7 UTC)

Source workflow (successful): https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42320396449
Complete archived outputs: https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42320396449/artifacts/13552612820
Script: `real_known_planet_vs_binary.py`
Physical diagnostic: `binary_eclipse_diagnostics.py`

## The scientific question

A repeating brightness dip can come from a planet crossing a star or from one star passing in front of another in an eclipsing binary. Could a simple, AI-assisted detector use **event-level physical information** to flag a known eclipsing binary without incorrectly warning on a known planet?

This is a **two-object external sanity check** of an established astronomical concept. It is not a survey-wide test, a new planet discovery, or proof that the screening technique works reliably for arbitrary objects.

## Actual NASA Kepler observations and provenance

Both targets use public Kepler Quarter 8 long-cadence PDCSAP flux downloaded as FITS from the NASA MAST archive via its official product API. The processing masks cadences with nonzero SAP_QUALITY or invalid flux, divides by a 301-point running median to suppress slow variability, then normalizes flux. Such flattening can modify actual transit/eclipse depths; all recovered measurements are dependent on this fixed preprocessing.

| Known object | Public identity | Quality-filtered cadences | Source FITS SHA-256 |
|---|---|---:|---|
| Confirmed exoplanet Kepler-69 b | KIC 8692861 | 2,767 | `2a91205f2f40e494da7fea65d7932e54735ac67bedc5584e87f8e9f685ad11c0` |
| Published eclipsing binary | KIC 10661783 | 2,717 | `ed9938a61e629f4e3d17a41d1bb7768c8a7a1e524e39594919b14bad218f8dfd` |

These are actual telescope brightness observations, not simulated stars. Target identities and general transit-vetting purpose were chosen in advance; the precise published periods were not fed to the BLS fits and were used only afterward for evaluation. The search bounds differ between examples, so this is not a statistically matched blind survey search.

## Result 1: Kepler-69 b (known planet)

- Previously published orbital period: **13.7223682 days**, NASA Exoplanet Archive DR25.
- BLS best-fit period from real Kepler Quarter 8 brightness: **13.7133429855 days**.
- Relative period difference: **0.06577%**, absolute difference ~0.009025 days.
- Broad search interval used before period comparison: **1.5–20 days**.
- Estimated BLS depth: ~529 parts per million (ppm); duration 0.153 day.
- Per-event diagnostics: **5 observable transits**, median positive primary depth ~565 ppm, odd/even depth ratio **0.0435**, odd/even statistic **1.25**.
- Half-period secondary depth estimate: **-36.4 ppm**, heuristic secondary statistic **-0.94**.
- Binary-specific review warning: **FALSE**.

Interpretation: On this one known planet, the physically motivated test did not falsely identify binary-like eclipses. It is a useful positive sanity check, not a representative estimate of sensitivity.

## Result 2: KIC 10661783 (known eclipsing binary)

- Previously published orbital period: **1.23136326 days** (Miszuda et al. 2021, MNRAS, https://doi.org/10.1093/mnras/stab1597).
- BLS best-fit period: **1.23141743275 days**.
- Relative period difference: **0.0043994%**.
- Search interval used before comparing with the publication: **0.9–6 days**.
- Fitted BLS box depth: ~152,209 ppm (not an independently modeled binary radius or depth).
- Event checks: **49 adequately sampled eclipses**, median primary depth ~180,988 ppm.
- Odd/even depth ratio **0.00818**, difference statistic **0.415**, so **odd/even warning FALSE**.
- A distinct eclipse at half-orbital phase: estimated depth ~**102,748 ppm** and a very large internal secondary-depth significance statistic (~**236.7**).
- Secondary-eclipse warning: **TRUE**; combined binary-review warning: **TRUE**.

Interpretation: The binary was recognized through a strong **secondary eclipse**, not by unequal odd/even eclipses. This shows why a robust physical-vetting system needs both kinds of tests: if the period fitter recovers a binary's full orbital period, odd/even comparisons can appear perfectly consistent even for a binary.

## Contrast and key scientific inference

| Check | Real planet Kepler-69b | Real binary KIC 10661783 |
|---|---|---|
| Orbital period recovered close to published reference | Yes | Yes |
| Primary brightness events recur consistently | Yes | Yes |
| Significant binary-like secondary event in this implementation | No | Yes |
| Final binary-review warning | False | True |

**Realization:** Merely finding a precise period or multiple consistent brightness dips cannot establish that a planet exists. A binary may provide a *more convincing* periodic signal than a planet. The astrophysical information contained in **other eclipse phases** can distinguish types of systems that the basic BLS score conflates.

This concept is well established in published vetting literature (including NASA's Kepler Robovetter); our contribution is an original implementation and carefully documented sequence of simulations, verification, and failure-driven improvements for ASTR 12600.

## Limitations and next scientific steps

1. **Only two real objects:** these are demonstrations, not estimated true-positive, false-positive, completeness, or reliability rates. One cannot derive sensitivity/specificity from one example per class.
2. **Very unequal eclipse depths:** KIC 10661783 is a comparatively easy binary example; equally deep binaries, grazing binaries, blends, and pulsating stars may be harder.
3. **No source-position check:** the four-feature NASA model and one-dimensional BLS plots do not show which star inside an observing aperture caused the transit. Pixel centroid and difference-image checks need additional products.
4. **Uncalibrated secondary statistic:** the large per-event 'SNR' is an approximate heuristic using scatter estimated from measurements, not a calibrated statistical false-alarm probability in correlated noise.
5. **Real planets can exhibit occultations:** an eclipse-like feature should trigger **review**, not automatic deletion of a planet from the catalog.
6. **Unmatched search bounds and prior selection:** the two tests use different period windows selected for the case-study purpose. Their recovery differences are not a controlled comparison of which type is easier to discover.
7. **Next experiment:** before further changing thresholds, expand the external test to several **independently selected known planets and published eclipsing binaries** using the exact same frozen physical rules. Report the denominator, number of warnings in each group, missed planet warnings, ambiguous cases, and error bars. Then investigate representative failure cases and the effect of detrending.

## Project evidence, not to conflate

- Real Kepler DR25 historical label classification: `REAL_NASA_DR25_RESULTS_2026_11_06.md`. Forest outperformed SNR baseline in specificity/accuracy but had lower test recall; extra ensemble disagreement did not show a robust gain.
- Real Kepler-69b transit search and synthetic injections in real Kepler noise: `REAL_KEPLER_LIGHTCURVE_RESULTS_2026_11_06.md`.
- Synthetic BLS event-ablation study: `FIRST_EVENT_VETTING_ABLATION_2026_11_06.md` and `BINARY_ECLIPSE_SYNTHETIC_FOLLOWUP_2026_11_06.md`.
- This document: **two actual, previously characterized astronomical systems** used as an external check of the physical warning rule.

## Research disclosure

GPT-6 generated the code, tests, study documentation, and proposed interpretation, with published Astropy algorithms and NASA Kepler measurements. The student should independently verify cited references, processing, values, interpretation, and assignment policy. No independent confirmed-planet discovery is claimed.
