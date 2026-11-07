# Additional Reference Books, TESS Thesis Preview, and Scientific Writing Method
**ASTR 12600 / exoplanet-detection project | Source review, 7 November 2026**

## Source inventory and access limitations

These notes synthesize **new student-provided materials**, with source page references in terms of **PDF page number**, not the printed page shown at bottom of the page. The books are multi-author educational references, not single benchmark experiments. Do not present their explanatory examples as results from our own code. Do not upload licensed PDF originals, reproduced figures, or extensive text to this public repository.

1. **A. P. Hatzes, 2020, *The Doppler Method for the Detection of Exoplanets***, AAS/IOP Astronomy, DOI [10.1088/2514-3433/ab46a3](https://doi.org/10.1088/2514-3433/ab46a3). Student PDF: \`978-0-7503-1689-7.pdf\`, **330 pages**. Most applicable: Ch. 7 on periodograms, false-alarm significance and sampling (PDF ~pp. 145–180); Chs. 9–11 on stellar activity and filtering (PDF ~pp. 205–294); Ch. 8 on Keplerian orbital models (PDF ~pp. 181–204).
2. **E. Gilbert, 2022, *The Detection and Characterization of Exoplanets Around M Dwarf Stars Using TESS***, University of Chicago Astronomy and Astrophysics doctoral dissertation. Student PDF: \`out.pdf\`, **24-page publisher-style PREVIEW**: title, table of contents, abstracts, introduction, and the very beginning of Chapter 2 only. **The detailed text of chapters 2–6 is NOT included in the attached PDF.** Content after page 24 can be identified only through its table of contents and figure captions, not independently examined here.
3. **T. L. Campante, N. C. Santos & M. J. P. F. G. Monteiro, eds., 2018, *Asteroseismology and Exoplanets: Listening to the Stars and Searching for New Worlds***, Springer, DOI [10.1007/978-3-319-59315-9](https://doi.org/10.1007/978-3-319-59315-9). Student PDF: \`978-3-319-59315-9.pdf\`, **288 pages**. Most useful individual contributions:
   - D. Huber, *Synergies Between Asteroseismology and Exoplanetary Science*, printed pp. 119 onward, PDF ~pp. 131–145.
   - R. F. Díaz, *Modelling Light and Velocity Curves of Exoplanet Hosts*, printed pp. 199 onward, PDF ~pp. 206–230.
   - M. Oshagh, *Noise Sources in Photometry and Radial Velocities*, printed pp. 239 onward, PDF pp. 246–256.
   - S. Barros & J. P. Faria, *Tutorial: Detecting Planetary Transits and Radial-Velocity Signals*, printed pp. 267–274, **PDF pp. 273–280**.

All literature observations below are drawn from these attached materials unless explicitly labeled **project interpretation/proposal**.

## I. Hatzes (2020): the statistical discipline behind searching for periodic signals

### What the book's research method looks like

Hatzes explains a measurement technique as an **error budget**: (a) what astrophysical quantity can be observed; (b) which hardware converts it to a number; (c) what changes that number without a planet; (d) what analysis separates a periodic Keplerian signal from everything else; and (e) what controls or independent information are required before accepting a planet.

For the Doppler method the observation is a small wavelength displacement of stellar spectral lines, not a flux dip. Its nonrelativistic relation is Δλ/λ = v/c, so measuring radial velocity requires extremely stable wavelength calibration and careful modeling of stellar spectral variability (book Ch. 1, PDF p. 29; Chs. 2–6).

The book stresses that signal interpretation is conditional on observing schedule and noise. Chapter 7 walks through Fourier transforms and Lomb–Scargle methods, then explains spectral windows, aliases, false-alarm probability, bootstrapping and iterative prewhitening. Chapters 9–11 challenge the apparent “planet” interpretation with stellar rotation, spots, spectral line diagnostics, filtering, and Gaussian processes.

### Particularly useful methods and observations

**Heteroskedastic errors (Ch. 7, PDF pp. 151–154):** The generalized Lomb–Scargle (GLS) model weights observations by individual uncertainty and jointly fits a floating offset. The example in book Figure 7.4 (PDF p. 154) contrasts classical LS, which picks a ~50-day peak, against weighted GLS/BGLS, which recover an injected 105-day signal in a particular constructed example. This does NOT mean GLS always beats LS or that it directly replaces BLS for a transit; it demonstrates that differing uncertainties can radically change period ranking.

**Spectral window (Ch. 7, pp. 157–161):** Observing at irregular, intermittent times causes the true periodic signal to be convolved with the spectral window in the frequency domain. A forest of peaks can arise from one signal; another signal can be aliased by undersampling. Figure 7.12 (PDF p. 161) shows a sub-day sine wave sampled nightly becoming indistinguishable from a substantially longer-period sine wave. The corresponding project lesson is to examine **actual cadence/gaps, trial-grid resolution and harmonic families** before interpreting a BLS “winner.” Do not apply a simple sinusoidal alias equation to box transits without checking the photometric sampling.

**Empirical significance (Ch. 7, PDF pp. 168–175):** The book discusses false-alarm probabilities, bootstrap/randomization, and the hazards of fitting successive peaks once the data contain only noise. In its iterative-prewhitening discussion it explicitly warns that one can *always fit the highest remaining peak*, even if it is just noise. That directly applies to our iterative BLS development.

**Activity as a confounder (Chs. 9–10, PDF pp. 205–267):** Rotationally modulated spots, plage, convective blueshift and stellar oscillations can create spurious periods. Activity indicators, line bisectors, chromaticity and time evolution can help reject apparent planets in RV. These are **spectroscopic evidence channels**, generally not present in our Kepler-only photometric files. Do not claim that our existing transit model can measure bisectors or radial velocities from light curves.

**Filtering robustness (Ch. 11, PDF pp. 270–290):** Hatzes presents Fourier prewhitening, local trend fitting / floating chunk offsets, and quasi-periodic Gaussian processes. Crucially, smoothing or filtering can also remove the planet signal; local trend fitting works best when the planet period is appreciably shorter than the stellar activity timescale (see section 11.2, PDF p. 280). The comparisons in Table 11.2 (PDF p. 288) show broadly compatible RV-amplitude estimates across different activity treatments for selected published systems; the author advises skepticism when only one analysis approach reveals the purported planet.

**RV challenge (Ch. 11, PDF p. 289):** The book describes a challenge in which multiple research teams analyzed simulated planetary RV datasets; methods with Bayesian correlated-noise approaches appeared comparatively successful in that case. This is a **review of another experiment**, not an evaluation of our transit code.

### Strengths and limitations of using this book in our paper

- Strength: Provides a physical reason why uncertainty weighting, survey window functions, period aliases, red-noise treatment, and independent robustness checks belong in the *Methods* and *Discussion*.
- Limitation: It primarily studies **radial velocities**, with different data, error sources and signal morphologies. We may transfer the statistical principles, but we should not compare its RV false-alarm rates or amplitude errors numerically against our Kepler-photometry BLS recovery.

**Concrete method to borrow:** Attach to each detected signal a **signal audit**: actual time baseline; number of unique covered transit events; gaps; candidate period and strongest aliases; estimated point errors / time-correlated noise; sensitivity to one defensible preprocessing variation; and an independently calibrated false-alarm test.

## II. Springer (2018): from a discovery statistic to a physical orbital model

### Barros & Faria tutorial, PDF pp. 273–280

This chapter is a remarkably clear example of a methods section organized around a *reproducible sequence of inference*:

1. **Observe flux versus time**, run BLS across a declared trial period/frequency range, and display (a) the raw light curve, (b) BLS periodogram, and (c) folded transit at the best period. Their Figure 1 (PDF p. 275) places all three together. **Our project should reproduce this three-panel diagnostic form**, with axis units, chosen search bounds, and the actual observing cadence.
2. **Fit a physical transit model rather than a box** (PDF pp. 275–276). The toy box is designed for *detection*. A physically meaningful transit fit needs period, midtransit time, radius ratio, impact geometry, ingress/egress and limb darkening. The tutorial uses \`batman\` and least-squares minimization (\`lmfit\`) and explicitly assumes a circular orbit at this stage.
3. **Check the star** (p. 276). Approximate depth δ ≈ (Rp/Rstar)^2; a transit duration also constrains orbital geometry relative to the **stellar density** under particular orbit assumptions. That density is not “measured for free” by a BLS periodogram.
4. **Independent radial velocities** (p. 277). Analyze unevenly spaced RV measurements with appropriately uncertainty-weighted Lomb–Scargle, then check whether flux and RV are consistent with a common orbital period.
5. **Estimate parameter uncertainties using a joint Bayesian model** (pp. 278–279). The tutorial writes down the Gaussian likelihood, adds a possible extra \`jitter\` term beyond quoted measurement noise, incorporates priors and samples an MCMC posterior (\`emcee\`). It asks students to inspect corner plots and chain convergence.
6. **Sensitivity to assumptions** (p. 279). Compare priors, test fixed versus free periods and **oversample/integrate the transit model** rather than evaluate it only at coarse exposure times.

**Noteworthy detail:** The worked example is the known K2 system **EPIC 211089792 / K2-29 / WASP-152** with a period around **3.25 days** (PDF p. 274), coincidentally the period used in our original toy simulation. Do not treat this textbook example as an independent planet discovery or as proof that our parameter-search range was unbiased.

**Why it matters:** Our current code's BLS peaks and feature model support only early-stage **detection/candidate screening**. A physical transit model and uncertainty distributions would upgrade the scientific interpretation, but would still not prove that an astrophysical eclipse is planetary rather than binary. RV observations may be unavailable for Kepler targets and are a **future extension**, not mandatory for this course experiment.

### Oshagh noise-source chapter, PDF pp. 246–256

The chapter organizes stellar noise **by physical process and characteristic timescale**, rather than pretending it is one random Gaussian number:

| Stellar effect | Physical origin | Impact on a flux search | Possible safeguard |
|---|---|---|---|
| Oscillations | Acoustic modes of star | Minute-scale correlated fluctuations | Match cadence and noise treatment to transit duration; avoid erasing ingress/egress |
| Granulation | Convective bright/dark surface cells | Correlated flux variations on minutes–hours | Use noise-aware models or compare preprocessing strategies |
| Rotation/active regions | Spots and faculae varying over rotation/time | Slowly evolving baseline, apparent repeat events, transit-shape contamination | Model the activity instead of blindly clipping/baseline subtracting |

The chapter directly notes (PDF p. 248) that longer exposures can suppress oscillations but may degrade recovery/shape measurement for brief transits. On pp. 249–251 it identifies stellar granulation as potentially comparable to small-planet signals. These are reasons to test our stellar-noise preprocessor by **recovery of injected real transits**, not just by a lower residual standard deviation.

**Project inference:** Avoid “lower residual RMS = better astronomical preprocessing.” A smoother light curve may simply have suppressed real narrow dips. We need a Pareto comparison between injected signal recovery and null false alarms at equal conditions.

### Huber stellar-density chapter, PDF pp. 131–138

Huber shows that transit depth and duration do not independently identify a planet's physical radius without information about the host star. Under certain assumptions, stellar density inferred from transit geometry can be compared with independent asteroseismic density. Nonzero orbital eccentricity and periastron geometry change transit duration (see PDF p. 136, Eq. 5 and Figure 4).

**Project inference:** A “duration consistency” filter must be a **soft diagnostic with stellar-property uncertainty and eccentric-orbit tolerance**, not a strict hard veto based on a fixed solar-type stellar density. For our simple star-agnostic feature set, this becomes an explicit limitation rather than a missing one-line formula.

### Díaz physical model chapter, PDF pp. 206–230

Díaz distinguishes a *mathematical model of the physics* from a simple periodicity search, derives relevant orbital/flux relations and discusses probabilistic inference and priors. The crucial scientific-writing point is to **state the assumptions before drawing inferences from the fitted parameters**: circular orbit, limb-darkening prescription, contamination, independent errors, model mismatch.

**Project inference:** Report two separate results: (i) performance of a detection algorithm at finding periods, and (ii) accuracy/credibility of physical parameter estimates, if we actually perform physical fits. Do not conflate them.

## III. Gilbert (2022): a model of mature astrophysics research writing — limited to preview

**IMPORTANT ACCESS NOTE:** The student-uploaded \`out.pdf\` is only **24 pages**, ending near the opening of Chapter 2. It is NOT the full dissertation. Claims about full methods/results in Chapters 2–6 below are supported by its **table of contents, figure lists, abstracts and Chapter 1 introduction**; the later technical chapter texts have **not** been inspected.

**What is directly present:**
- The abstract and introduction (PDF pp. 12–23) motivate a specific observational problem: low-mass M-dwarf stars provide comparatively favorable transit/RV detectability but often show stellar spots and flares that complicate inference.
- The thesis uses a linked sequence of **three astronomical case studies with different activity regimes** (quiet TOI-700; active young AU Mic; flaring Proxima Centauri). This is a coherent scientific argument across multiple chapters rather than a collection of unrelated planet descriptions.
- The table of contents (PDF pp. 4–5) outlines a repeated logic: data/observations → targeted methods → parameter estimation and independent validation → discussion → conclusion.
- The figure lists (PDF pp. 6–9) reveal the intended evidence: raw vs cleaned light curves, folded transit fits, uncertainty envelopes, stellar rotation, individual transits, dynamical timing differences, and injection/recovery sensitivity plots. These are **figure titles and captions**, not the full data shown in the unavailable later pages.
- Its introductory text explicitly situates the new method against existing Kepler and TESS literature and describes the physical reason for star-specific activity modeling.

**Preview-only claims that must stay labeled as such:** The abstract and figure captions describe modeled flare removal for Proxima Centauri, injection recovery of small signals, and a comparison with sigma-clipping; these could motivate our tests but **their detailed data cleaning, thresholds, sampling and uncertainty derivations cannot be reconstructed from this 24-page excerpt**. To make an exact code-level comparison with Gilbert, obtain the complete thesis or the linked peer-reviewed chapter papers (Gilbert et al. 2020, 2021a, 2021b).

**The writing pattern worth emulating:**
- Establish why the measurement is difficult.
- Identify a real, physically motivated source of interference (e.g., flares or stellar rotation).
- Choose test cases where the interference differs.
- Explain data provenance and preprocessing in enough detail to reproduce it.
- Fit the signal and calculate uncertainty.
- Show both successes and failures of detection.
- Run injections or independent follow-up to establish what a “nondetection” can actually rule out.
- Separate evidence from broader claims about exoplanet habitability or occurrence rates.

**Important inference:** A nondetection of a weak transiting signal is informative **only within the experiment's measured detection limits and window function**. Without injection sensitivity, “no detected planet” tells us little about the true absence of a planet.

## IV. What these new sources add to the existing four-paper critical review

Our original foundation was Kovács 2002 (BLS), McCauliff 2015 (classify Kepler TCEs), Thompson 2018 (DR25 population selection/reliability), and Robnik et al. 2026 (non-Gaussian defects, individual-transit checks and matched false-alarm recovery).

The new sources provide a **missing physical/measurement layer**:

| Previously known problem | Additional insight from books/thesis preview | Experimental implication |
|---|---|---|
| BLS reports half/double periods | Hatzes: spectral-window sampling aliases compound harmonic confusion | Compare P, P/2, 2P and actual sampling/window rather than classifying any maximum as true |
| Noise-only data always produce peaks | Hatzes: empirical significance and when to STOP iterative prewhitening | Freeze null thresholds and require significance before every new candidate |
| Signal sometimes lost in preprocessing | Oshagh: genuine stellar noise and real transits overlap in time/frequency | Plot retained injection depth and recovery as well as residual noise level |
| Transits may be non-box-shaped | Barros & Faria: use BLS for search then physical, exposure-integrated transit fit | Separate period detection from transit-shape/parameter estimation |
| Transit duration could identify artifacts | Huber: density, eccentricity, impact parameter and limb darkening complicate duration | Do not build a hard duration veto using unknown stellar parameters |
| Candidate type still ambiguous | Barros & Faria: test RV as complementary evidence; Hatzes: spectral activity diagnostics | Flag that catalog-level photometry alone does not “confirm a planet” |
| Good performance on ideal data may fail | Gilbert preview: case studies across diverse stellar activity; Hatzes: filter comparison | Include an unseen high-activity, low-activity, gap-heavy sample |
| Student paper needs strong academic structure | Gilbert and Springer tutorials: physics → reproducible data/method → figures/uncertainty → limits | Use an explicit research-paper outline and figure checklist below |

### New conceptual conclusions (our synthesis, not verbatim source claims)

1. **Preprocessing is an estimator, not a neutral step.** Any rule deciding which data to modify changes the detectable-planet population and introduces its own selection effects. Therefore, preprocessor evaluation must count true transits *removed* as well as artifacts suppressed.
2. **Inference should be layered:** detection peak → statistically significant periodic event → astrophysically plausible transit model → candidate vs alternative physical explanation → independently confirmed/validated object. Each stage needs its own success metric.
3. **A highly regular period can still be a stellar phenomenon**, and a real planet's observed transits can depart from strict periodicity via TTVs or be altered by stellar flares. Both false positives and false negatives matter.
4. **Methods can be robust in one dataset and fragile in another.** The external frozen binary failure already in this repo is exactly the kind of result a responsible Discussion should retain, not retroactively explain away by tuning.
5. **Combining evidence only helps if the new modality exists.** Independent RV measurements would be powerful for physical confirmation but our available Kepler flux files and KOI features do not contain those RV data; claim only what is measured.

## V. Practical choices for the next reproducible experiment

### Suggested title/research question

**Does conservative, physically motivated stellar/noise preprocessing improve the recovery of injected exoplanet transits over ordinary BLS at the same independently measured false-alarm rate?**

This is an implementable *Robnik-inspired* rather than *Robnik-replication* question, with supporting scientific reasons from Hatzes, Oshagh, Barros/Faria and Gilbert.

**Competing methods (freeze definitions before testing):**
- **A: Standard BLS** on the same Kepler photometry and a fixed period/duration grid.
- **B: BLS with one conservative, documented preprocessing step** addressing artifact edges, local nonphysical discontinuities and/or physically motivated stellar variability. If trying multiple steps, select using only development/calibration data.
- **C (optional ablation): B + per-transit evidence audit** analogous to published individual-transit consistency diagnostics; label clearly which method is actually implemented and what remains heuristic.
- **D (external comparator, optional): transit-fitting stage** using \`batman\` only on candidates to compare physical residuals/parameters. This is not a drop-in replacement for the detection pipeline.

**Controls and measurement:**
- Define a target selection *before* inspection, from stars that were not hand-picked for success. Record source products, observation quarters/cadence, Kepler IDs, stellar activity proxies and filtering choices.
- Inject signals with recorded periods, epochs, depths, durations and optionally transit-timing offsets. Include at least shallow/high-SNR controls, red-noise cases and gap-near events.
- Build **null controls** with astrophysical-like noise and artifact structure, not merely independent Gaussian random numbers. Any inversion, scrambling or resampling null should have its symmetry/contamination limitations acknowledged (Thompson DR25).
- Use **independent calibration and held-out test cases**. Measure per-star FAP and correct-period recovery on both methods under the SAME measured FAP budget. Publish denominators, interval estimates, thresholds and exactly how period aliases were scored.
- Stratify results by **SNR/depth**, **period/number of transits**, **stellar noise/activity** and **gap proximity**. Display failures, not just global recovery percentages.
- Report the **number of genuine injected transit points/total injected signal lost after preprocessing**. A lower RMS or prettier plot is not evidence of higher completeness.
- Respect the astrophysical distinction between *detecting a periodic photometric event*, *vetting astrophysical false-positive interpretations* and *confirming the presence of a planet*.

**Falsifiable null:** At a fixed calibrated FAP, the chosen preprocessor provides no increase in held-out correct-period recovery. If there is no statistically meaningful improvement, report a negative result and analyze which noise classes explain that finding.

### Figures: prioritize evidence, not decoration

1. **Three-panel detection example:** actual raw/processed light curve; common-grid BLS power; phase-folded data plus model (Springer tutorial Fig. 1).
2. **Evidence-preservation example:** one real transit with original flux, filtered flux and injection truth; quantify any depth suppression.
3. **Matched-FAP curve** or two points with binomial uncertainty: correctly recovered injections versus false-alarm rate, with same null/test pools (Robnik et al. 2026 Fig. 6 model).
4. **Failure-mode grid:** alias P/2/P/2x, near-gap defects, missed low-SNR and variable individual transits.
5. **Subgroup summary:** performance as period/transit count and stellar-noise intensity vary, with denominators.

## VI. How to write the final paper like the sources — without imitating their prose

The source authors do not just announce an algorithm; they construct an argument from a physical cause to an observable signature, show the statistical assumptions, then limit the conclusion to actual evidence.

Use a compact journal-style manuscript structure with ordinary, direct scientific prose:

**Abstract (150–220 words).** State the photometric detection problem and known failure mode, methods/baselines and data source, held-out evaluation method, most important numerical result with uncertainty (only after tested), and conclusion. Avoid claims of new planets or improvements until demonstrated.

**1. Introduction.** (a) Why transits reveal planets; (b) why realistic stellar/instrument noise makes weak signals hard; (c) BLS as established baseline (Kovács); (d) role of downstream vetting and selection effects (McCauliff, Thompson); (e) modern individual-transit and defect modeling (Robnik); (f) our narrow testable question and scope.

**2. Data and Methods.**
  - 2.1 Data sources, observational baseline, stellar sample, mission/cadence, inclusion/exclusion, missing points.
  - 2.2 Astrophysical model and key equations. Define δ ≈ (Rp/Rstar)^2 **under small-planet/uniform-star approximation**, BLS search settings and transit parameters; discuss limits of a square model.
  - 2.3 Proposed preprocessing. Show explicit algorithm, all masks/hyperparameters, and why it might affect signals.
  - 2.4 Control generation and injections; explain that flux-level injection is not a DR25 pixel-level replication.
  - 2.5 Model comparisons and statistical evaluation: independent calibration/test, period tolerance, aliases, detection threshold, null FAP, denominators and intervals.
  - 2.6 Reproducibility: environment, random seeds, repository commit, input-data checksums and run commands.

**3. Results.** Show exact findings *without explaining them away*; distinguish recovered injections from naturally cataloged signals; write numbers with sample sizes and uncertainty; discuss Figs. 1–5 in the order the research question demands.

**4. Discussion.** Interpret why preprocessor succeeded or failed, conditions of success, where original assumptions break, risks of missing real planets, relation to **matched** published benchmarks and non-comparable published benchmark statistics. Clearly separate prior exploratory/frozen test from new held-out results.

**5. Conclusion and Next Steps.** One bounded conclusion, what might generalize and what evidence is needed; consider star-specific Gaussian processes, TTV robustness, centroid data and independent follow-up as separate next steps.

**AI-use reflection** (course-specific): Describe how generative AI assisted literature review/code, what it got wrong, and how independent verification revealed failures and changed the project. Source text/figures in this note are paraphrased; never present GPT-assisted claims or tests as independently validated unless they were.

### Writing standards exemplified in the sources

- Define every physical quantity, unit, and model assumption **before** using an equation.
- Indicate observational provenance: mission, quarter/sector, cadence, time baseline, pipeline/flux product.
- For plots: show data, model, axis units and uncertainty; a caption should say what was done and what a viewer should infer.
- Distinguish **detection statistic**, **statistical significance**, **classification score**, **physical parameter posterior**, **catalog reliability**, and **planet confirmation**.
- Do not report only the best-case examples; use counterexamples and negative results as evidence about scope.
- Numerical comparisons to papers require the same evaluation task, dataset regime and false-alarm definition, or a plainly stated difference.
- References: primary papers for novel techniques, specialized references for instrument/stellar physics, and books for methodological explanations. Cite the original research where available.

## VII. Sources to access if a true benchmark replication becomes necessary

- Complete Gilbert dissertation or **Gilbert et al. (2021a)**, source of the Proxima Centauri flare-removal injection study; **Gilbert et al. (2021b)** for AU Mic stellar activity and transit modeling; full technical methods currently absent from uploaded preview.
- Robnik et al. (2026) code and matched FAP injection protocol (already cited in original four-paper review).
- Hatzes references to GLS (Zechmeister & Kürster 2009), quasi-periodic GP studies and RV Challenge are useful **adjacent** examples, not direct photometric detection comparisons.
- Barros & Faria's tutorial public code is identified in the Springer text: https://github.com/iastro-pt/AzoresTE1 (not executed or independently verified in this reading step).

## Method/AI provenance

This is a source-based secondary synthesis prepared with AI assistance. For the two full books, focus was placed on their relevant chapters and selected rendered figures, **not an assertion that every page of both books was analyzed at the same depth**. For the Gilbert file, only the 24-page preview is accessible. No new program was run, no new observations downloaded and no experimental performance claim was established in this step.
