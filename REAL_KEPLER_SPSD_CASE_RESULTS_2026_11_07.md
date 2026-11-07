# One documented REAL Kepler instrument defect: SAP versus PDC correction
**November 7, 2026 | Source:** NASA MAST Kepler Quarter 6, KIC 7461601. **Status:** complete source-verified illustrative observation, not independent detector benchmarking.

[Verified run and tests](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42403352082) · [Full source outputs and figure](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42403352082/artifacts/13586631074) · [Predeclared example](KNOWN_SPSD_REAL_STAR_FROZEN.json) · [Source code](real_spsd_case_study.py).

## Rationale and source

NASA/STScI's [Kepler electronic-noise instructional notebook](https://spacetelescope.github.io/mast_notebooks/notebooks/Kepler/instrumental_noise_4_electronic_noise/instrumental_noise_4_electronic_noise.html) uses KIC 7461601, Q6, to demonstrate a cosmic-ray-associated sudden pixel sensitivity dropout (SPSD) and its correction in the PDC light-curve product. The official event's FITS quality value **1152** combines the flags for a cosmic ray in the optimal aperture and a sudden sensitivity dropout.

This is a **target specifically chosen because it was previously known to contain the event**, so it provides a useful annotated case study but **cannot be called independent external validation** or contribute to estimates of the classifier's sensitivity, specificity, false alarm rate or planet recovery.

## Dataset and analysis

- Official MAST file: `kplr007461601-2010265121752_llc.fits`. Original source SHA-256: `aa744d4861e56a44b99b7981fd6d729fc1f47ac230e03510d78406c1b073d301`.
- **4,272** cadences with valid, positive simultaneous SAP and PDCSAP flux; the figure deliberately **retains flagged cadences** so the defect is visible. Our separate planet-recovery experiments exclude nonzero-quality cadences; this visualization has a different measurement policy, disclosed here.
- SAP_FLUX is the original simple aperture photometric series (uncorrected aperture flux); PDCSAP_FLUX is the pipeline-corrected time series. Both were normalized with the same 301-point median procedure for plotting and the fixed step-screening rule.
- The published quality label occurs at **BKJD 547.8892493463**. The **identical unchanged** local-step heuristic, which did **not receive the known event epoch or quality flag**, detected a persistent negative step in original SAP flux at **BKJD 547.9096836451**.
- The difference is **0.02043430 days, or ~29.42 minutes**, approximately one Kepler long cadence.
- On the PDC-corrected PDCSAP flux, the same heuristic gave **no localized-step warning near the archival flag** (in fact zero warning events in the analyzed series).

## Scientific significance

This is a stronger physical demonstration than our toy discontinuity injections: **a known and independently flagged actual instrumental event is visually obvious in SAP, our simple search detects its onset within one cadence, and the post-processing Kepler pipeline largely removes the step in PDCSAP.**

The figure **known_kepler_spsd_sap_vs_pdc.png** in the workflow artifact illustrates both time series around the archived event. The red dashed line denotes the archived quality flag; the blue line in the SAP panel denotes the estimated onset of our step detector. This is an explanatory diagnostic plot, not a new astronomical detection.

The observation explains our newer six-star experiment's **negative natural-data result**: many of the most obvious SPSD-like defects have already been removed by the much more sophisticated NASA PDC pipeline before our code sees the PDCSAP flux. Our extra detector did not mask any naturally occurring observations in those 36 no-defect injected trials, so its apparent 1-case gain there was entirely due to a lower score cutoff, not a physical correction.

This real example also motivates examining the data product hierarchy and source provenance before adding more ML complexity. As established by Aigrain et al. (2017) and Robnik et al. (2026), meaningful defect handling requires distinguishing instrumental changes from genuine stellar events and preserving astronomical signal.

## Limits (do not overstate)

1. The target was **selected for an already published known defect**. It cannot yield representative sensitivity/specificity or a statistically established method advantage.
2. The fixed heuristic finds one obvious large jump; it can miss small, variable, recovery-shaped or unflagged defects, and sometimes remove real transits. Neither this nor the six-star ablation validates universal false-positive screening.
3. Comparison of SAP and PDC is **not a direct algorithm-versus-algorithm fair test**: PDC was run by the official mission pipeline with its own co-trending corrections, aperture/quality processing and full instrument context; our script is only a simple local change detector.
4. The known quality flag is an instrumental label, not a physical planet classification.
5. No radial-velocity or centroid localization was analyzed, and no new planet is claimed.
6. Our 2017 Aigrain ARC2 and 2026 Robnik comparisons remain **methodological**, not numeric reproductions.
7. The original photometric file, fit and script results should be checked by the student independently; source reading, code, analysis and this report were generated with AI assistance.

## Reproducibility

From an internet-connected environment install the repository requirements, then run `python real_spsd_case_study.py --out results/real_spsd_case`. The official archive file is cached with its SHA-256; the saved plot and original JSON summary can be downloaded from GitHub Actions. The illustrative reference was precommitted in [KNOWN_SPSD_REAL_STAR_FROZEN.json](KNOWN_SPSD_REAL_STAR_FROZEN.json), not chosen post-hoc after inspecting model output.
