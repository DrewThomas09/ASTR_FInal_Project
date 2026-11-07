# Part I — Annotated Literature Review: Four Foundational Papers
**ASTR 12600 final project | Research notes, 7 November 2026**

**Scope and provenance:** These notes are based directly on the four complete PDFs provided by the student, not just abstracts: \`aa2422.pdf\` (Kovács et al., 2002; 9 pages), \`1408.1496v2.pdf\` (McCauliff et al., 2015; 14 pages), \`nihms-966303.pdf\` (Thompson et al., 2018; NASA-author manuscript, 101 pages including appendices and references), and \`stag419.pdf\` (Robnik et al., 2026; 16 pages). PDF page numbers in parentheses below are **displayed pages within the uploaded PDF**, not necessarily journal pagination. Descriptive statements below reflect these sources; interpretations and proposed tests are marked as such.

## Executive synthesis: one astronomical problem, four different statistical tasks

The papers do **not** all attempt to estimate the same quantity:

1. **Detection:** Kovács et al. ask if periodic box-shaped flux dips can be recovered against photometric noise. Output: a prominent period and detection statistic.
2. **Classification of detected events:** McCauliff et al. classify already-discovered **threshold crossing events (TCEs)** as planet candidates (PC), astrophysical false positives (AFP), or nontransiting phenomena (NTP), based on engineered diagnostic measurements.
3. **Catalog vetting plus survey-level completeness/reliability:** Thompson et al. explain how NASA's automated DR25 **Robovetter** assigns candidate/false-positive dispositions, and calibrate the selection using injected transits and inverted/scrambled false alarms.
4. **Noise-aware search plus stronger vetting:** Robnik et al. build a complete pipeline for suppressing local defects, evaluating separate events, applying physical period/duration priors, and extracting multiple distinct candidates from a single detection scan.

**Major realization:** The hardest problem is not always whether an algorithm can *find a sharp, repeated dip*. It is whether the significance survives realistic instrumental/starlight noise and whether the dip is produced by a planet rather than a binary, contamination, or an artifact. More sophisticated AI trained on a restricted catalog cannot invent missing pixel-level or per-event information.

---

## Paper 1. Kovács, Zucker & Mazeh (2002): where detection begins

**Citation:** *A box-fitting algorithm in the search for periodic transits*, A&A 391, 369–377; https://doi.org/10.1051/0004-6361:20020802.

**Paper question:** Classical Fourier/sinusoidal searches work well for broadly sinusoidal variable stars, but exoplanet transits are brief, nonsinusoidal, box-like dimmings. Can a period-search statistic exploit that shape more effectively?

**Method, in plain language (PDF pp. 1–3):**
- Choose a trial orbital period P; fold the measurements so that repeated events overlay one another.
- Choose a candidate transit window / duration qP and fit two brightness levels: in-transit dimmer level and out-of-transit baseline.
- Minimize weighted squared residuals. Use the maximum “signal residue” as a period-dependent BLS power and identify promising peaks.
- Search period, duration, and transit epoch; the algorithm is a *template matcher*, not a physically verified planet classifier.
- The authors define signal-detection efficiency **SDE = (SR_peak - mean(SR)) / sd(SR)** (their Eq. 6, PDF p. 3). They also define an effective SNR **α = (depth / noise SD) sqrt(N q)** (Eq. 11, PDF p. 5), linking detection to the number of in-transit measurements.

**What the paper actually demonstrates:**
- In controlled synthetic noise, using a box-shaped model markedly outperforms contemporary Fourier and other period-finding alternatives for shallow, short-duration transits (Figs. 6–11).
- A simulation-specific effective SNR near **α ~6** is a rough transition toward detectability under their assumptions, **not a universal Kepler false-alarm cutoff**.
- The authors explicitly describe strong harmonics/subharmonics (fractional or multiple periods) of real signals (PDF p. 3), highly relevant to our observed half-period binary aliases and repeated planet signals.

**Limitations from the paper's setup and our interpretation:**
- Their derivations and many performance simulations rely on comparatively simple, often Gaussian photometric noise and strictly periodic, ideal box-shaped transits.
- Detection statistics depend on grid resolution, transit duty cycle, time baseline and trial-period search size; p. 4 discusses how the false-peak distribution changes with the number of trial frequencies (a look-elsewhere issue).
- Period aliases are present even when the signal is real. A correct BLS maximum does not imply a genuine planet.
- Our Astropy BLS reproduces the **established algorithmic family**, not every numerical detail of the original 2002 simulated study.

**Figures to study:** Fig. 1 (PDF p. 2) for period/folded-signal example; Figs. 3–4 (p. 4) for dependence on transit phase and bin resolution; Figs. 5–6 (pp. 4–5) for noise-only SDE calibration and detection versus α.

**Testable project idea:** Benchmark BLS period recovery as a function of injected depth and compare exact period versus P/2 and 2P aliases, under *identical* simulated and observed Kepler noise. Freeze the trial period grid and calibrate any flag threshold on independent null cases. Do not treat an uncalibrated maximum as a detection.

---

## Paper 2. McCauliff et al. (2015): what a random forest can and cannot classify

**Citation:** *Automatic Classification of Kepler Planetary Transit Candidates*, ApJ 806, 6; https://doi.org/10.1088/0004-637X/806/1/6.

**Paper question (PDF pp. 1–2):** The Kepler pipeline produced too many threshold crossing events for purely manual classification. Can a random forest learn patterns in pipeline-derived diagnostics to triage events into PC, AFP, and NTP?

**Method and data (PDF pp. 5–11):**
- Observations came from **Kepler Q1–Q12**, not the final Q1–Q17 DR25 dataset. The authors describe **18,407 TCEs** in that pipeline catalog.
- Labels for PC/AFP were matched to historical Kepler Objects of Interest, while NTP labels came from human triage; the original labeled class distribution was highly imbalanced. The paper says 11,304 NTP, 2,879 PC, and 393 AFP in the training set (PDF p. 5).
- **237 initial attributes** from instrument/filter diagnostics, transit-model fits, centroid/difference images and related tests were pruned to **77 attributes** based on permutation importance and feature correlation (PDF pp. 7–8).
- Their random forest used **15,000 trees** and about sqrt(77) = 9 candidate attributes per split, with out-of-bag predictions for internal assessment (PDF p. 10).
- Features such as **ephemeris correlations between detected signals on the same star**, MESmax/MESmin, odd/even fits, and centroid offsets carry information absent from our basic period/duration/depth/SNR model. The p. 3 conceptual decision tree explicitly uses MES ratio and centroid offset to distinguish different physical types.

**Reported outcomes (careful distinction):**
- The authors report out-of-bag error of **2.19%** for the unweighted forest; after weighting votes under their cost/loss selection, out-of-bag error fell to **1.34%** (PDF p. 11).
- Later, on their combined prior-corrected confusion matrix (Table 4, PDF p. 13), the quoted overall classification error is **5.85%**; if confusion between AFP and NTP is ignored, planet/nonplanet error is **2.81%**. The 5.85%, 2.81%, 2.19% and 1.34% values are **different evaluation/aggregation conditions**, not interchangeable model scores.
- Figure 7 (p. 11) reports **PC vs AFP AUC ≈0.9522 overall**, declining to about **0.8229** for periods greater than 100 days (larger uncertainty in that subgroup). This supports concern about sparse long-period training data.
- A later-disposition test (Tables 2–3, p. 12–13) reveals substantial AFP errors where **secondary eclipses and off-aperture contamination** were identified using information missing from the model's features. This is a direct acknowledgment of the limits of catalog-feature models.

**Important weaknesses highlighted by the source:**
- If the survey discovers increasingly small and long-period objects, its original labeled sample ceases to represent new inputs. The authors explicitly examine this **training/distribution shift** in §7.1.
- Label priors vary as the survey and candidate definitions evolve; their correction for excluded eclipsing binaries changes the confusion matrix and overall reported error.
- Out-of-bag validation is useful, but it is not the same as a modern star-grouped, independently selected test of a future survey, and it does not establish physical truth for every historical label.
- The model only uses measurements already produced by upstream Kepler routines; it does not independently analyze missing pixels or poorly represented light-curve defects.

**Figures to study:** Fig. 1 (p. 3) simple forest structure; Figs. 5–6 (pp. 8–10) astrophysical feature distributions; Tables 1–4 and Fig. 7 (pp. 11–13) error accounting and long-period dependence.

**Direct relation to our project:** Our held-out DR25 four-feature forest achieved **81.6% agreement with historical NASA binary candidate/false-positive labels** (not real-planet accuracy). It cannot be scored “18.4% error vs their 5.85%” as a fair match because this is a **different two-class subset, different era, different selected events, different predictors and different evaluation**. Our weak performance on binary vetting is scientifically consistent with their argument that missing secondary/centroid diagnostics cause errors, but the numerical experiments are not equivalent.

**Testable project idea:** Compare (A) the same four-feature classifier and (B) an expanded feature set including independently computed per-event depth inconsistency/secondary evidence **on the same actual candidate sample**, *if the features can be linked correctly to KOIs*. Keep an unchanged host-star split and use distinct train/validation/test stars. A fair historical reproduction of McCauliff requires recreating the original three classes and comparable TCE sample, not merely increasing our feature count.

---

## Paper 3. Thompson et al. (2018): why “candidate” is not the same as “planet”

**Citation:** *Planetary Candidates Observed by Kepler. VIII. A Fully Automated Catalog with Measured Completeness and Reliability Based on Data Release 25*, ApJS 235; https://doi.org/10.3847/1538-4365/aab4f9.

**Paper question:** A Kepler candidate list is scientifically useful only if researchers can quantify **what it misses** (completeness) and **how many entries are spurious** (reliability). The paper establishes the DR25 Robovetter and selection-function measurements.

**Catalog and methodology (PDF pp. 1–12 and later §§3, 7):**
- Four years, **Q1–Q17**, yielded **32,534 nonrogue observed TCEs**, and the final DR25 KOI catalog contains **8,054 KOIs**, of which **4,034** were dispositioned as *planet candidates*. The remaining KOIs are historical Robovetter false positives, not necessarily independently proven nonplanets.
- They distinguish **observed TCEs**, **injected TCEs**, **inverted TCEs**, and **scrambled TCEs**. The latter are diagnostic controls intended to resemble non-planet false alarms.
- Realistic transit injection experiments begin at calibrated **pixel data** and propagate through the Kepler search/vetting pipeline. This is more rigorous than our tiny box-transit injections into already flattened light curves.
- **Inverted** curves create control dimmings from upward residuals; **year/quarter scrambled** data disrupt real orbital periodicities while trying to preserve certain Kepler seasonal systematics. Neither perfectly reproduces the true nuisance population (the authors explicitly discuss inversion asymmetry and scrambled-data limitations in §2.3).
- The catalog uses disposition metrics, false-positive flags, and a disposition score. The score is based on variability of automated dispositions under Monte Carlo perturbations and **is not a direct probability that a planet physically exists** (see §3.2).

**Reported quantitative performance, with exact subgroup restrictions (abstract, p. 1):**
- **Period under 100 days**, all observed stars: vetting completeness >85% and reliability against instrumental/stellar-noise false alarms >98%.
- **Low-SNR, 200–500-day** objects, all searched stars: **73.5% completeness and 37.2% reliability**.
- For the comparable **FGK dwarf-star subset** in that long-period low-SNR regime: **76.7% completeness and 50.5% reliability**.
- These are **survey/selection-function estimates**, not accuracy scores of a four-feature model. The reliability definition here focuses on false alarms from stellar or instrumental noise, not all astrophysical false-positive scenarios.

**Failure mechanisms identified by the authors:**
- Insufficient phase coverage; long periods leave only a few observed transits.
- Correlated stellar noise, artifacts after cosmic-ray-induced pixel sensitivity drops, and periodic **rolling-band** signatures at Kepler's approximate 372-day spacecraft orbit (§2.1, Fig. 1).
- If a candidate is rejected during vetting, it never reaches the catalog, creating a tradeoff between completeness and reliability.
- The distributions and consequences differ by period, SNR, transit count and stellar type; a single headline error rate does not characterize the whole problem.
- The methods for simulating noise may miss real artifacts. The authors explicitly acknowledge that inversion requires a symmetry not fully present in Kepler systematics (PDF p. 11).

**Figures/sections to study:** first-page abstract performance numbers; §2.1–2.3 for observed/injected/inverted/scrambled TCEs; §3.2 for score interpretation; §7 for selection-function estimates, period/SNR stratification and the completeness/reliability tradeoff. The author-manuscript PDF is 101 pages with additional technical appendices, not 101 pages of uninterrupted article text.

**Critical takeaway for OUR current ML:** Predicting the DR25 \`koi_pdisposition\` outcome is **partly predicting the decision of a sophisticated established rule-based vetter using summary measurements of the same signals**. It is not proof that our model discovers true planets or beats NASA's full pipeline. The input set consists of the already-filtered KOIs, not all 32,534 TCEs or all observed stars. This creates severe *population conditioning*, and an algorithm's catalog-label accuracy cannot estimate survey completeness or reliability without injection/null controls.

**Testable project idea:** Use exactly the same matched injected-transit/false-alarm control population for all versions of a detector. Report (1) correctly recovered injected periods, (2) un-injected control detections per light curve, (3) false-dismissal of genuine signals, and (4) coverage/abstention. Avoid using historically labeled KOIs as the only measure of physical truth.

---

## Paper 4. Robnik, Seljak, Jenkins & Bryson (2026): our most relevant physical benchmark

**Citation:** *Exoplanet transit search at the detection limit: detection and false alarm vetting pipeline*, MNRAS 547; https://doi.org/10.1093/mnras/stag419.
**Public implementation identified by the authors (PDF p. 2):** https://github.com/JakobRobnik/exo-probability

**The paper's central issue (PDF pp. 1–2):** Folding multiple stellar dimmings at one period can conceal that the individual events have different shapes, noise levels, or sudden instrumental jumps. In **Figure 1 (PDF p. 2)**, KOI 7894.01 looks plausible in the folded plot but visibly contains discontinuities in individual transit windows. This illustrates information loss in conventional catalog-style vetting.

**Pipeline (paper Fig. 3, PDF p. 3) — three linked stages:**

**A. Pre-processing (§§2–3, pp. 2–4).**
- Use public Kepler PDCSAP data, known planet candidates and stellar parameters.
- Estimate stellar correlated noise in the Fourier domain; apply an *outlier Gaussianization* transformation intended to suppress isolated spikes while preserving correlated structures such as transits.
- Search for and mask significant localized defects: sudden pixel sensitivity dropouts and discontinuity templates (including 30 timescales spanning 45 minutes–2 days and thresholded high scores).
- Account for transit timing variations (TTVs) of sufficiently strong known planets before masking those signals, reducing contamination and period interference.
- Remove narrow instrumental or stellar harmonics from the spectral noise estimate.

**B. Detection (§4, pp. 5–7).**
- Use matched-filter planet transit templates and a prior incorporating stellar density, period, phase and expected transit duration.
- Combine signal strength with prior information into an approximation of a **Bayes-factor ranking statistic**. Figure 4 (PDF p. 6) shows that a simple SNR threshold has a period-dependent “look elsewhere” false-peak penalty; their prior-aware statistic is roughly more uniform in period under the simulated null.
- Distinguish **threshold crossing peaks** (TCPs) from independent **threshold crossing events** (TCEs). Peaks from one actual signal can appear at harmonic periods; their Algorithm 1 revises competing peak evidence after masking the strongest signal to identify multiple candidates with less repeated full-search computation.
- The authors explicitly compare this to the conventional approach of repeating a full search after removing an identified event, which is conceptually similar to our exploratory iterative BLS. **Therefore, multi-pass removal is NOT a novel algorithm that we invented.**

**C. Vetting (§5, pp. 7–8).**
- Calculate a more accurate Bayes factor for promising candidates (24-point Gaussian quadrature reported for their low-dimensional integral).
- Test each individual transit against **localized defect** templates and treat near-gap events (within 20 hours of a large >=20-hour gap) as suspicious. A candidate is warned if removing spurious transits reduces its *squared combined SNR* by >50%.
- Use a **transit significance consistency** test: individual event SNRs should fluctuate around expectations; a too-large variance (chi-square-based test) leads to a warning at p<0.01.
- This is more specific and statistically motivated than our current heuristics such as a 60% positive-event fraction or thresholded odd/even depth ratios. **We must not claim to have introduced per-event consistency tests into astronomy.**

**Injection benchmark (§6, PDF p. 8, Fig. 6):**
- **5,000 randomly selected Kepler stars**; invert their flux before searching to limit detection of real planets; inject or do not inject planet signals and run the same pipeline.
- Injected **periods 200–500 days**, radii normally distributed around **2 Earth radii** with SD **0.2 Earth radii**, plus sampled phase/duration priors.
- True recovery requires fitted period within **1%** and transit phase within **0.5 days** of the injection. False-alarm probability (FAP) is the fraction of **un-injected stars** with a vetted candidate exceeding a threshold. The ROC therefore has a *per-star* denominator.
- At **FAP = 1%**, the authors report the largest gain from localized-defect removal (**factor ~70** in their experimental comparison), followed by additional gains from spurious-transit checking (~17%) and significance consistency (~52%); the prior-aware Bayes statistic yields an additional ~7% rather than a huge stand-alone improvement. These percentages/factor are source-reported at this specific operating point and sequential ablation, **not universal independent effects that can be added**, and the plot uses logarithmic FAP on the horizontal axis.
- Figure 6 is especially valuable for our report: it measures **true injected-signal recovery at the same false alarm rate**, with bootstrap uncertainty bands. This is the standard our tests should emulate, at least on a smaller scale.

**Further application and limitations (§§7–8, pp. 9–11):**
- They reanalyze previously cataloged candidate stars and find much agreement for short period/high SNR, but reject multiple low-SNR long-period candidates as suspected artifacts. These are conclusions from their method, **not independently observed proof that each disputed signal is noise**.
- Their own vetting sometimes warns on **confirmed planets with TTVs** because the significance consistency model assumed a strictly periodic ephemeris.
- The localized defect bank cannot detect artifact shapes it does not model. Time-varying noise and complicated astrophysical binaries remain distinct issues.
- Their ROC injection study primarily probes **long-period, low-signal** planets and instrumental false alarms, not whether a short-period binary with nearly equal eclipses can be physically ruled out using one-dimensional flux alone.
- The study makes a methodological comparison under a particular simulated null and chosen prior; its reported gain is conditional on that design.

**Figure-by-figure reading priority:**
- Fig. 1 (p. 2): folded signal versus five individual transit windows, the best demonstration of information loss.
- Fig. 3 (p. 3): all three stages of their pipeline.
- Fig. 4 (p. 6): period-dependent false alarms for SNR vs prior-aware statistic.
- Fig. 6 (p. 8): rigorous matched-FAP ROC ablation; directly useful as the exemplar of correct quantitative evaluation.
- Fig. 7 (p. 9): divergence from historic candidate catalog by period and signal significance.

**Important limitation for any “our model vs paper” headline:** Their 200–500-day, four-year, 5,000-star, inverted-flux injection benchmark is fundamentally different from our **single-quarter, 0.9–15-day, tiny-sample BLS experiments**, and from our random forest classifying already selected KOIs. We may accurately compare methods and qualitative failure modes today, but **we cannot legitimately compare 8/8 synthetic binary exclusions with their FAP=1% detection improvement**.

---

## Consolidated comparisons: what each method knows and where it loses information

| Paper / system | Input to decision | What it measures | Most relevant missing information / risk | Our fair replication task |
|---|---|---|---|---|
| 2002 BLS | Flux versus time, trial periods, box templates | Periodic box-fit power / candidate period | Aliases, red noise, isolated artifacts, binary-vs-planet ambiguity | Same BLS grid and heldout injected periods |
| 2015 random forest | 77 engineered TCE diagnostics | PC / AFP / NTP consistency with labels | Priors, distribution shift, omitted pixels/secondary/contamination, OOB ≠ future independent truth | Same TCE population and common 3-class labels needed for numerical reproduction |
| 2018 DR25 Robovetter | Full Kepler detection and diagnostic products | KOI dispositions plus measured vetting selection effects | Long-period false alarms; imperfect inverted/scrambled nulls; not all AFP fully resolved | Injection-vs-null calibration, report completeness and reliability separately |
| 2026 Robnik pipeline | Full light curves, noise model, priors, event windows | Detection, null FAP, multi-event extraction, defect-aware vetting | Unknown defect morphologies, variable transit times, assumption/model mismatch | Recreate Fig. 6-style equal-FAP ablation on compatible population |

### Three non-obvious findings from comparing the *actual full texts*

1. **Our current prototype solves a much easier classification problem than the benchmark.** The 2015 forest starts from all types of TCEs and explicitly separates instrumental noise from astrophysical impostors; our 4-feature DR25 model sees only the KOIs retained after prior vetting and a binary label. The difference is not “77 features versus four”; it is a different target population, truth definition, and task.
2. **The information bottleneck is physical, not necessarily algorithmic.** Robnik's Fig. 1 shows how a high-quality folded dip can conceal obvious bad individual events. McCauliff's later mislabeled AFPs require secondary/centroid diagnostics that its learned feature set did not contain. A decision tree, neural network or ensemble cannot recover omitted evidence. But just **adding an odd/even rule** is also insufficient, as our independent 13-star binary test showed.
3. **The greatest published gain in the 2026 paper is *before* period searching.** Localized-defect removal was reported to change injected recovery vastly more than changing the final Bayes ranking statistic. This suggests that our next carefully controlled intervention should target *measurement cleaning and gap-adjacent artifacts* before adding additional ML layers.

### What is established by our code, independent of these papers?

- Baseline Astropy BLS found the already confirmed **Kepler-69b** period within ~0.066% in one real quarter.
- Four-feature DR25 forest: **81.6%** agreement with historical candidate/FP labels on 1,619 held-out KOIs, but lower test recall than the SNR-only rule and no independent planet confirmation.
- Margin-plus-ensemble-disagreement triage: **122** wrong automatic decisions vs **123** for plain uncertainty review at equal 30% review budget; confidence interval crosses zero, **not a compelling ML improvement**.
- Simple physical binary warning: good on one previously characterized binary and a simplified synthetic cohort but **0 warnings among 6 real published binaries** in a prospectively frozen convenience cohort. That is **negative external validation**. Four of the six were fitted at P/2 aliases.
- Exploratory iterative BLS: a second pass found an already confirmed **Kepler-20b** signal after the first found Kepler-20c; Kepler-18b still not found within three passes. The evaluated systems were selected after failure inspection, thus **not an independent improvement estimate**.

No individual paper cited here offers ground truth that would magically make these outcomes into independent detection of new exoplanets.

---

## Next experiment: one focused, falsifiable comparison inspired by Robnik Fig. 6

**Hypothesis A (pre-processing):** For signals near an individual data discontinuity or gap, a simple *physically specified, local defect-aware pre-search step* will reduce false peaks and may improve injected-planet recovery at a **matched, independently calibrated false alarm rate** versus the same untouched BLS. This is a classroom-scale test of an established idea, *not invention of defect removal*.

**Feasible design, to freeze BEFORE evaluation:**
1. Take public real Kepler photometry from several stars independent of the existing Kepler-69/Kepler-20 development examples. Preserve raw FITS checksums, quality flags, time gaps and the exact same processing of all comparators.
2. Define two pipelines: **BLS-alone** versus **identical BLS with a fixed artifact/near-gap pre-processing rule**; never alter BLS grid, injections or scored references between groups.
3. Generate independent calibration controls from actual stellar flux with conservative source handling, and a held-out suite of known synthetic transits with varying depth, period, phase, duration, gap proximity and nuisance defect type. State clearly that post-detrending flux injection is **not equivalent to DR25 pixel-level injection**.
4. Pick *separate* detection thresholds for each method on their **own calibration null sample** to achieve the same measured false-alarm budget; report per-star FAP and test-set binomial uncertainty. Never choose a cutoff after inspecting the test injections.
5. On **unseen test flux**, count exact-period injection recoveries (and aliases separately), false triggers per un-injected star, and genuine signals removed by artifact processing; report condition-by-condition denominators. Use a minimum practical number of trials before making confident rate claims.
6. Then do a three-way ablation: unchanged BLS, BLS + pre-processing, BLS + pre-processing + **Robnik-style per-event contribution check** (specific paper rule, not our crude prior heuristic). Its value is the *incremental matched-FAP gain*, if any.
7. Inspect failure examples: long-period two-transit coverage, masking a genuine real transit, false positives near data gaps, and cases where the periodogram reports a harmonic. Test the same rule on a separate real star sample before asserting generality.

**Null hypothesis:** At a matched false-alarm rate under this chosen experiment, defect-aware processing does *not* improve injected-period recovery relative to ordinary BLS.
**Alternative:** It increases correct-period recovery without an unacceptable increase in missed genuine signals on a fresh test sample.

**Practical guardrail:** If access to a runnable version of the authors' [public code](https://github.com/JakobRobnik/exo-probability) permits a truly matched pipeline comparison, attempt it. Otherwise call the experiment **Robnik-inspired ablation**, not a replication of the complete 2026 pipeline. A 70x claim from their 5,000-star benchmark must never be copied onto our smaller study.

## Open methodological questions for the next literature pass

- How sensitive is Robnik's defect classifier to rare defects not in its template bank? Which failure modes could be detected without full power-spectrum modeling?
- Would a conservative transit-exclusion mask during preprocessing avoid erasing real planets, or does it make it easier to hide artifacts? How should TTV planets be protected?
- Can a calibrated multi-peak search distinguish independent planets from harmonics without a full new BLS scan?
- For near-equal eclipsing binaries, would the necessary discriminating information be pixel centroid changes or stellar parameters—not just the light curve?
- How do the assumptions underlying inverted Kepler controls affect rare asymmetric noise defects? Can we bound their effect?
- What is the minimum scientifically fair sample and runtime for a matched-FAP experiment before the course final deadline?

## Suggested Part I narrative sequence

1. **Physics and measurement:** Kepler's third law explains periodicity; depth is approximately (Rp/Rstar)^2 for an ideal small planet; stellar and detector variations contaminate the measurement.
2. **Original method:** BLS exploits the sharp dip (Kovács 2002), but returns a *periodic fit*, not a confirmed planet.
3. **Learning from diagnostics:** McCauliff (2015) uses a random forest to map engineered search/validation features into three candidate categories; incomplete features and changing survey populations create limitations.
4. **Scientific quality assurance:** Thompson (2018) makes completeness, reliability and injected/false controls essential; DR25 labels are useful but not definitive astrophysical truth.
5. **Modern improvement:** Robnik (2026) treats localized defects, individual event evidence and prior-aware candidate ranking together and tests matched-FAP injected recovery.
6. **Our contribution:** We attempt a transparent, smaller-scale reproduction and one careful ablation; early results—including clear failures—inform but do not replace the independent test.

## Reading checklist and bibliography integrity

These are **annotated source-grounded research notes**, not polished final prose; all four papers have been inspected with full-text extraction and selected figure renders. The exact quoted source results and captions should be checked again when writing the final report; numerical comparisons must retain each study's data definition, sample restriction, evaluation condition and uncertainty. Author contribution: source synthesis, candidate experiment design and draft wording were assisted by GPT-6; student should independently assess methods, analyses, primary-source claims and final scientific conclusions.

### Four primary works
1. Kovács G., Zucker S., Mazeh T. (2002). *A box-fitting algorithm in the search for periodic transits.* A&A 391, 369–377. doi:10.1051/0004-6361:20020802.
2. McCauliff S. D. et al. (2015). *Automatic Classification of Kepler Planetary Transit Candidates.* ApJ 806:6. doi:10.1088/0004-637X/806/1/6.
3. Thompson S. E. et al. (2018). *Planetary Candidates Observed by Kepler. VIII. A Fully Automated Catalog with Measured Completeness and Reliability Based on Data Release 25.* ApJS 235. doi:10.3847/1538-4365/aab4f9.
4. Robnik J., Seljak U., Jenkins J. M., Bryson S. (2026). *Exoplanet transit search at the detection limit: detection and false alarm vetting pipeline.* MNRAS 547. doi:10.1093/mnras/stag419.
