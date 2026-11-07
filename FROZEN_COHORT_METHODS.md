# Frozen external cohort — scientific selection and evaluation plan

## Purpose
Evaluate our *existing* odd/even and secondary-eclipse **review warning**, with no further threshold tuning, on an independently selected (relative to the two earlier development examples) set of real Kepler objects.

The exact data manifest was committed **before** downloading/evaluating the observations:
[real_external_cohort_frozen.json](real_external_cohort_frozen.json).
The executable: [real_external_cohort.py](real_external_cohort.py).
The automated run: [Frozen external cohort workflow](.github/workflows/frozen-external-cohort.yml).

## How the 13 objects were chosen

- **Six independently listed confirmed planets:** Kepler-18 b (KIC 8644288), Kepler-19 b (KIC 2571238), Kepler-20 b (KIC 6850504), Kepler-21 b (KIC 3632418), Kepler-68 b (KIC 11295426), Kepler-93 b (KIC 3544595). Their separate planetary statuses, stellar IDs, and approximate periods appear in the NASA Exoplanet Archive Kepler overview pages linked in the JSON manifest.
- **Seven published Kepler eclipsing binaries:** KIC 1026032 appears in the STScI MAST Kepler Eclipsing Binary catalog; KIC 2305543, 2306740, 3248019, and 3654950 are among published eclipsing-binary **twin candidates** in an astronomy comparison table; KIC 4544587 and 9851944 have individual spectroscopic/photometric studies identifying eclipsing binary systems.
- These are **purposively chosen, nonrandom targets** with published periods in 0.9–15 days. The exact choice has not been optimized for our predicted outcomes; however, it is a *convenience sample* of accessible known objects, not an unbiased population sample.
- The two earlier demonstration objects, **KIC 8692861** and **KIC 10661783**, are not included in the new cohort.
- All objects use the **same Q8 long-cadence data policy** and **same broad 0.9–15-day BLS period bounds**. If a Q8 FITS is absent or a target was only observed at short cadence, the download remains a **failed/unavailable test**, not a case to discard and replace after seeing outcomes.

## Frozen signal analysis

1. Download FITS from official MAST product API, saving SHA-256 of each actual file. Preserve quality-flag and preprocessing rules (SAP_QUALITY == 0, PDC-SAP, 301-cadence median detrend).
2. Use Astropy BLS at uniform search bounds 0.9–15 days, without any historical period as input.
3. Apply the **unchanged** code in `binary_eclipse_diagnostics.py`. The combined review warning requires odd/even eclipse depth discrepancy or a sufficiently strong secondary eclipse. A warning means *request further study*, not *delete candidate*.
4. **Only after** fitting, compare the measured period with literature period. An exact match within 2% is distinct from a half-/double-period alias. A fit to an unrelated period is *unmatched*.
5. Report every planned target, every download/processing failure, every unmatched or aliased period, every binary warning, and the precise denominator for any fraction.
6. For scientifically interpretable group summaries, primary warning counts are **conditional on an exact period match**, because a different fitted period may correspond to another planet, a harmonic, or noise. Separate counts of unavailable/unmatched cases are critical, not optional.
7. Provide descriptive Wilson intervals where possible, but do not treat them as representative population confidence intervals; the sample was not randomized and numbers will be small.
8. Do not change thresholds after looking at this cohort. A future version may improve processing or tests, but then needs an additional untouched sample or explicit *development* labeling.

## Source anchors

- Kepler DR25 confirmed system/KOI documentation: https://exoplanetarchive.ipac.caltech.edu/docs/API_kepcandidate_columns.html
- NASA archive system overviews: https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-18 ; https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-19 ; https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-20 ; https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-21 ; https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-68 ; https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-93
- STScI 2015 Kepler Eclipsing Binary catalog (2,878 systems): https://archive.stsci.edu/kepler/eclipsing_binaries.html
- Published twin-candidate binary table: https://academic.oup.com/view-large/357094419
- KIC 4544587 eccentric pulsating EB: https://academic.oup.com/mnras/article/434/2/925/1076715
- KIC 9851944 pulsating EB: https://doi.org/10.3847/0004-637X/826/1/69
- Kepler EB catalog methodology: Kirk et al. (2016), AJ: https://doi.org/10.3847/0004-6256/151/3/68

## Scientific warnings

The physical warning is **not** a new NASA-quality exoplanet validator; secondary eclipse signals also occur in some genuine hot exoplanets. The BLS score is not a calibrated false-alarm probability here, and a failed single-quarter BLS fit does not change the independently confirmed identity of a planet. In a multi-planet system, the highest-power signal may correspond to a *different* known planet from the one listed.

This text and code are AI-assisted. ASTR 12600 student should verify the labels, spectra/light curves and limitations against original papers and discuss AI assistance per course instructions.
