# Frozen external SAP versus PDCSAP SPSD study (November 8, 2026)

**Status:** Prospective design and code are committed. Do not claim an observed result until a complete GitHub Actions run on official files has been inspected.

## Scientific question

Does the same unchanged, deliberately simple local negative-step detector show a different ability to identify **Kepler-archived instrument-discontinuity markers** on uncorrected `SAP_FLUX` versus PDC-corrected `PDCSAP_FLUX`? The two brightness measurements come from the **same** official FITS file and cadences, so comparisons are paired within a physical star.

The prior KIC 7461601 Q6 positive example was selected because STScI had already shown a dropout; it is **excluded** from the new independent sample. The [twelve Q6 source IDs and all analysis settings were committed in the frozen manifest](REAL_SPSD_EXTERNAL_COHORT_FROZEN_2026_11_08.json) before analyzing new files. The convenience sample was selected using publicly named Kepler sources, not a probabilistic sample of telescope targets.

## Archival label and blinding

The [Kepler Archive Manual](https://archive.stsci.edu/kepler/manuals/KDMC-10008-005-Archive_Manual.pdf) defines **SAP_QUALITY bit 11 (integer value 1024)** as a detected sudden pixel sensitivity dropout (SPSD). A bit may coexist with other flags, so the correct test is `(quality & 1024) != 0`, not equality with 1024 or the illustrative 1152. The STScI [Electronic Noise Kepler tutorial](https://spacetelescope.github.io/mast_notebooks/notebooks/Kepler/instrumental_noise_4_electronic_noise/instrumental_noise_4_electronic_noise.html) demonstrates one actual SPSD and how PDC can correct the brightness step.

- Fit both products separately with `localized_downward_step_mask` and the **unchanged November 7 detector settings**; neither fit sees the archival quality marker.
- Preserve flagged time points for this instrument diagnostic: otherwise the actual change may be removed before testing. Keep exactly the same finite, positive, joint-valid timestamps and indices for the SAP and PDCSAP fits.
- Only **after** collecting both lists of detected onsets, evaluate against SPSD markers from original `SAP_QUALITY`.
- Group marked cadences less than or equal to 0.45 days apart as one *archival event cluster*. This avoids counting a short train of flags as distinct independent defects.
- Match warnings to clusters by nearest time, *one-to-one without replacement*, within 0.22 days (approximately 5.3 hours). Never use known flag timestamps to guide the detection itself.
- Missing Quarter 6 files and invalid source records stay in the planned denominator. If the independent cohort contains no assessable SPSD flags, report that and do **not** calculate a putative detection sensitivity.

## Outputs and honest denominators

The workflow saves the original source SHA-256 for every available FITS file and also saves the frozen protocol, all 12 source rows, each archival event, unmatched predicted warnings, a summary JSON, and two diagnostic graphs when supported by data.

The primary result is the pair of counts at *archivally flagged events*:
1. Both SAP and PDCSAP match;
2. SAP matches but PDCSAP does not;
3. PDCSAP matches but SAP does not;
4. Neither matches.

A comparison of these discordances may be informative, but events are clustered within just a few purposively selected stars. Do not equate them with independent Kepler mission-level measurements. If desired, report an exact paired two-sided test with the explicit caveat of host dependence, but do not use p-values alone to claim superiority.

Also report unmatched detector warnings **as unmatched quality annotations, not false positives**. The archival flag is incomplete as a ground truth standard and PDC corrections themselves may depend on archived quality metadata. There is no known planet-free control sample here and no claim of exoplanet detection or physical planet confirmation.

## Relationship to the old experiments

- November 7, 2026: artificial planets and synthetic-looking steps injected into preconditioned PDCSAP; limited gain in one constructed defect and no natural-data preprocessing benefit.
- November 7, 2026: a single **already known** KIC 7461601 Q6 dropout showed a blind detection near the NASA quality label in SAP but not PDCSAP.
- **This new study:** check the fixed rule on genuinely observed files at preselected additional star IDs. This tests generalization to archival instrument annotations but does **not** compare the full NASA PDC algorithm against our rule as competitors, and does not measure recovery or true false-alarm probability for exoplanets.

## Reproduction

With the repository requirements installed:

```bash
python -m pytest -q tests/test_real_spsd_external_cohort.py
python real_spsd_external_cohort.py \
  --manifest REAL_SPSD_EXTERNAL_COHORT_FROZEN_2026_11_08.json \
  --out results/real_spsd_external_cohort
```

The [GitHub Actions workflow](.github/workflows/real-spsd-external-cohort.yml) runs the test suite and analysis on public NASA MAST. If the remote archive becomes unavailable, the report must list every failed KIC rather than replacing targets. Scientific interpretation, the source files, and AI contribution must be checked by the student before the ASTR 12600 final submission.

## Primary sources

- STScI/MAST, *Instrumental noise in Kepler and K2 #4: Electronic Noise*, \u003chttps://spacetelescope.github.io/mast_notebooks/notebooks/Kepler/instrumental_noise_4_electronic_noise/instrumental_noise_4_electronic_noise.html\u003e.
- STScI, *Kepler Archive Manual*, table 2-3 quality flags, \u003chttps://archive.stsci.edu/kepler/manuals/KDMC-10008-005-Archive_Manual.pdf\u003e.
- NASA Exoplanet Archive, *Kepler Data Products Overview*, \u003chttps://exoplanet.ipac.caltech.edu/docs/Kepler_Data_Products_Overview.html\u003e.
