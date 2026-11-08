# Deliberately post-hoc NASA model diagnostic inspection: five persistent 2025-vs-2026 disagreements

**2026-11-08 | These 5 cases were selected AFTER examining the 2026 model scores in the separate FROZEN 16-error stress test. They are NOT a new unseen test set, and no accuracy claim may be calculated from this subset.**

Source: [full locked 2025 error cohort](TESS_16STAR_2025_ERRORS_VS_2026_FROZEN_2026_11_08.json), original NASA v2.4.0 results [run #42523749559](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42523749559).

| Original TCE UID | Original 2025 label and score | Official 2026 v2.4.0 score | Observed event windows | Research question |
|---|---|---|---:|---|
| 29960109-1-S4 | NPC, **0.51278** | **0.99340** | 8 | Why a source labeled nonplanet is assigned extremely high planetary confidence; inspect pixel difference and centroid, not infer contamination from TIC identifiers |
| 354518617-1-S6 | NTP, **0.62279** | **0.94333** | 2 | Why two local candidate windows and an NTP label nevertheless receive very high validation score; inspect raw quality/instrument flags and event shapes |
| 165493409-1-S10 | EB, **0.87124** | **0.74654** | 2 | Why the claimed stellar eclipsing binary remains above a planet-candidate threshold; examine odd/even, secondary and period aliases, recognizing short sector limits |
| 466840711-1-S11 | KP, **0.18026** | **0.13729** | 6 | Why a previously known planet label is scored low despite multiple source event windows; inspect centroid and transit morphology |
| 158623531-1-S3 | KP, **0.30750** | **0.18358** | 2 | Assess sparse coverage and physical signal morphology behind persistently low score for a known-planet label |

The purpose is **qualitative failure analysis of original NASA's complete input evidence**, not selection of a tuned model threshold. Use NASA's `--plot_inputs_to_model` option in the same immutable NASA v2.4.0 container and preserve source FITS, centroid, difference-image and DV report provenance wherever available. Missing input plots and failed source products must be reported.

Only after investigating these concrete cases should we propose one falsifiable new feature/processing change. Test such a change on **separate new stars chosen before changing the algorithm** and at the same false-alarm budget.

This inspection does NOT directly modify the NASA neural-network weights and does not independently verify the original 2025 astrophysical class labels. AI-assisted selection and source review must be disclosed in the final project.
