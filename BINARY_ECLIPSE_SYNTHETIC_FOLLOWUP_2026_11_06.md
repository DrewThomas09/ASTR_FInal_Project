# Follow-up: Binary-specific vetting on a separate synthetic holdout
Date: 2026-11-06 (GitHub Actions log date 2026-11-07)
Verified run: https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42320188670
Results ZIP: https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42320188670/artifacts/13552691595

## Why we ran it

Our first ablation (see FIRST_EVENT_VETTING_ABLATION_2026_11_06.md) showed that **regular, convincing-looking transit events can be caused by eclipsing binaries**. A generic event-consistency check rejected only 1/5 simulated binaries. This motivated *explicitly* inspecting alternating odd/even eclipse depths and secondary eclipses.

The new `binary_eclipse_diagnostics.py` computes:
- Differences in successive odd/even transit depths, relative to their mean positive depth.
- An empirical odd/even difference statistic using between-event scatter.
- Evidence of an additional eclipse halfway between fitted primary eclipses.
- A non-probabilistic **review warning**. It does not prove an object is an eclipsing binary.

The follow-up run uses **new independent synthetic draws**, fixed rules and seed 20261107, three null calibration classes with 24 separate calibration examples, and **56 held-out test examples**: eight each of white noise, red noise, an isolated dip, binary-like eclipses, and injected 500-, 1,500-, or 4,000-ppm planets.

These choices were informed by an earlier pilot and are therefore **exploratory**, not a fully independent prospectively preregistered experiment.

## Verified comparison

| Holdout class (8 each) | BLS flags | BLS + simple event checks | BLS + event and binary-specific checks |
|---|---:|---:|---:|
| White noise | 0 | 0 | 0 |
| Correlated noise | 0 | 0 | 0 |
| One isolated dip | 2 | 0 | 0 |
| Binary-like primary and secondary eclipses | **8** | **7** | **0** |
| 500-ppm planet | 0 | 0 | 0 |
| 1,500-ppm planet | 2 | 2 | 2 |
| 4,000-ppm planet | 8 | 8 | 8 |

All recovered artificial planets were checked against their known injected period with a 2% tolerance.

**Promising preliminary result:** binary-specific eclipse checks rejected all eight binary-like false-positive signals that the plain BLS search had flagged. These tests did not sacrifice a **previously BLS-flagged** artificial planet in this small sample.

**Important negative result:** NONE of the 500-ppm synthetic transits passed the BLS threshold. The new veto does not solve the weak-signal detection problem.

## Why the new veto worked

The recorded eight binary-like holdout cases all triggered an **odd-even warning**. Their observed alternating depth ratios ranged from roughly 0.45 to 1.52 relative to the main positive depth, and the between-event difference scores exceeded 3.1. The secondary-eclipse warning did not trigger in these cases, presumably because many BLS fits selected the half-period alias at which both eclipse families occupy the same folded phase. The method is an application of **established astronomical vetting concepts**, not a new scientific discovery category.

Three unflagged red-noise control cases also had odd-even warnings; this reinforces that the diagnostic alone is NOT evidence that the source is an astrophysical binary. The ordering matters: one must first have a candidate detection, then apply physical review checks.

## Limits of the result

- These were simplified **synthetic** binaries with deliberately different primary/secondary depths; real eclipses can have similar depths, grazing shapes and complex pulsations.
- Only eight examples per group. No meaningful population-level false-positive estimate can be inferred.
- An eclipse warning may also fire for genuine planetary occultations, orbit timing variations, or correlated instrumental noise. Treat it as **human review required**, not automatic proof the signal is nonplanetary.
- The baseline threshold was derived from synthetic white/red/single-dip controls, not an astrophysically representative false-positive prior.
- No new model was trained; the contribution is a transparency-focused physical diagnostic layer and controlled comparison.
- No test here demonstrates the ability to rescue weaker planets that BLS never detected.

## Next scientific verification

Run the same newly coded diagnostic on two **real** Kepler stellar light curves: Kepler-69b as a known planet example, and a published eclipsing binary (KIC 10661783, period about 1.231363 days) as a real astrophysical impostor. Before calling the method robust, the operating characteristics must be checked across a larger physical sample and with event-level uncertainties.

## Source code and references

- `eclipse_vetting_followup.py`, `binary_eclipse_diagnostics.py`, `event_vetting_ablation.py`, `real_kepler_lightcurve.py`
- Kepler BLS algorithm: Kovacs, Zucker & Mazeh (2002), doi:10.1051/0004-6361:20020802
- NASA DR25 vetting: Thompson et al. (2018), doi:10.3847/1538-4365/aab4f9
- Independent binary reference: study of KIC 10661783, doi:10.1093/mnras/stab1597 (published orbital period 1.23136326 days).
- AI authored these scripts and experimental summaries; student must independently review and acknowledge AI assistance.
