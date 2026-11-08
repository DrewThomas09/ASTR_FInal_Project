# Two protected warnings coincide with genuine published Kepler stellar eclipses
**November 8, 2026 | Verified original NASA photometry and external ephemerides; a post-hoc physical corroboration, not fresh holdout testing.**

- [Successful observational follow-up workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42512589511)
- [Archived original-data figure, exact event offsets, independent reference parameters and source hashes](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42512589511/artifacts/13630380481)
- [Source code](recurrence_guard_external_ephemeris_audit.py) · [engineering tests](tests/test_recurrence_guard_ephemeris_audit.py)
- [Original prospective thirteen-star run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42512273665) · [original 13-source complete results](VERIFIED_RECURRENCE_GUARD_Q6_RESULTS_2026_11_08.md)

## Why an additional physical check was needed

In the first independent Q6 recurrence-preservation evaluation, the fixed safeguard protected a warning in Kepler-1647 (SAP) and one in Kepler-35 (PDCSAP). Both were already documented binary systems, and the guard's independently inferred repeat periods resembled published binary orbital periods or half-period aliases. However, **period similarity by itself is not proof** that the detected brightness decline is a real stellar eclipse.

For stronger physical grounding, we performed a separate **post-outcome**, source-verified comparison of *those two originally protected warning times* with independently reported primary and secondary stellar eclipse ephemerides, then replotted **unchanged genuine NASA Quarter 6 brightness measurements** around the predicted events. The original per-warning CSV was required to match SHA-256 `85a6000382a2911a072d637611e9eb85c38be5a56c5b3f423b94151c3e9d532f` before processing. Neither the original local-step detector nor the frozen recurrence-veto rule was changed.

## External binary timing, independently published

The NASA Exoplanet Archive DR25 binary-like KOI entries list stellar binary eclipse periods/epochs (historically labeled *false-positive planet candidates*) for these systems:

| Binary system | Published stellar orbital period | Published reference primary eclipse (BJD) | Independent source |
|---|---:|---:|---|
| Kepler-1647 (KOI-2939.01) | 11.258825027 d | 2454967.738 | [NASA Kepler-1647 overview](https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-1647) |
| Kepler-35 (KOI-2937.01) | 20.733748565 d | 2454965.847 | [NASA Kepler-35 overview](https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-35) |

The discovery study [Kostov et al. (2016)](https://doi.org/10.3847/0004-637x/827/1/86) describes **Kepler-1647 secondary stellar eclipses at phase 0.5526** relative to the primary. We used that independently published phase instead of mistakenly assuming secondary eclipses must occur at exactly phase 0.5. We converted BJD to Kepler's BKJD by subtracting 2454833.0, then advanced by integer multiples of the published stellar period to reach the frozen Quarter 6 warning timestamp.

**These epochs describe the binary stars' mutual eclipses, not the much longer orbital periods of the circumbinary planets.**

## Observed warning-versus-eclipse results

| Protected source | Original warning (BKJD) | Expected published stellar eclipse center (BKJD) | Measured timing residual |
|---|---:|---:|---:|
| **Kepler-1647 SAP** | 568.65048011 | 568.79497774 (secondary) | **−3.468 hours** |
| **Kepler-35 PDCSAP** | 568.13909099 | 568.25571987 (primary) | **−2.799 hours** |

A negative residual means our local-step warning occurred *before* the published eclipse center. That is physically plausible because stellar eclipse ingress — the start of the dimming — occurs before the light curve reaches minimum brightness.

The code also reloaded each star's **original** NASA MAST Q6 FITS and required it to match the unmodified source digests from the prior 13-star experiment:

- Kepler-1647, `kplr005473556-2010265121752_llc.fits`: SHA-256 `7e1d100455f556d427a64f8a6a5cd2f6da200ef73eb5dab7fabad1008c1890e3`.
- Kepler-35, `kplr009837578-2010265121752_llc.fits`: SHA-256 `c401d42c2939a9a218582268cd050a09d976b2404256eeaf177ff39b3555e2d2`.

**The resulting two-panel observational figure, `two_protected_real_eclipse_source_windows.png`, is the strongest figure from this new experiment.** Both raw SAP and NASA-corrected PDCSAP show deep real brightness troughs at the predicted stellar eclipse times; the original instrument-like warnings fall near the start of the observed decline. Thus protecting these measurements is a scientifically sensible alternative to unconditionally deleting them. No synthetic brightness dips were inserted into these figures, and no target's published period/epoch was supplied to the original protective algorithm.

## What this does and does not mean

**Supports:** two distinct previously untested known binaries produced original instrument-like warnings near independently predicted *stellar eclipses*. Our blind, flux-only recurrence guard recognized their repeating nature (Kepler-1647: 11.24 d, 7/7 other cycles; Kepler-35: 10.38 d half-period alias, 6/6 other cycles), preserving **21 actual NASA cadences per warning** that the old mask would have deleted. The real source light curves independently show that the local events are indeed astronomical-looking eclipse troughs.

**Does not establish:** automatic detection of new planets, more successfully recovered planet periods, a real survey false-positive reduction, independent statistical confirmation from a randomly selected cohort, or sensitivity to real uncorrected SPSDs. The strong ephemeris agreement was checked **after** the cohort produced these two warnings, making this a physical explanation of already observed results rather than a fresh blind test.

**Important negative comparator:** six original warning rows on Kepler-34 corresponded to three unique sharp dips ~27.79 days apart; the safeguard failed to protect them because its 22-day search cap was frozen beforehand. The published orbital period is ~27.80 days. Do not tune the existing star and call an after-the-fact change independent validation.

**AI use:** GPT-6 assisted the post-hoc independent reference search, ephemeris calculations, code, unit tests, NASA data retrieval, figure construction and narrative. Original numerical sources and scientific assumptions require student review and explicit AI assistance disclosure for the final course project.
