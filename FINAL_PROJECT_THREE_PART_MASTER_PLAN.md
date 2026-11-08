# ASTR 12600 Final Project: Three-Part Master Plan
Date: 2026-11-07
Target final submission: 2026-12-11 11:59pm CST
Status-update deadline: 2026-11-20 11:59pm CST

**Working title:** Can AI Improve Exoplanet Detection? Replication, Measured Improvements, and the Limits of Automated Scientific Research

**Central question:** Can generative AI help a researcher reproduce published exoplanet transit detection/vetting methods, identify a genuine weakness, and implement a simple modification that performs better on controlled comparisons and independent telescope observations? What does success or failure reveal about reliability in AI-assisted science?

**Output:** Python program and reproducible notebook in GitHub, accompanied by a substantive report with figures, method explanations, independent evaluation, annotated AI-use log, bibliography, and the required course checklist. Because the non-essay final project format requires a minimum 300-word write-up but the rubric heavily weights depth, aim for ~2,000–2,500 substantive words plus figures and appendix, adjusting to actual outcomes.

## Report architecture — exactly three principal parts

### Part I. Preliminary research and proposed improvements (about 35% of written discussion)
The *why*; not a generic chronology.

1. Explain transit photometry from first principles: a stellar flux decrease when a body passes in front; transit depth approximately (R_planet/R_star)^2 under ideal assumptions; repeated transits yield orbital period; Kepler's third law P^2 proportional to a^3 for a given host mass. Establish that a dip is not sufficient to establish a planet.
2. Group past work into **method families**, always answering four questions: How does it work? What data does it require? What is its demonstrated strength? Where does it fail?
   - Traditional periodic searches: Kovacs, Zucker & Mazeh (2002) Box Least Squares.
   - Noise-aware Kepler search and survey vetting: Jenkins/TPS; Thompson et al. (2018) DR25 Robovetter.
   - Better physical transit templates: Hippke & Heller (2019), Transit Least Squares.
   - Tabular machine learning: McCauliff et al. (2015) random forest.
   - Neural networks and multiple diagnostics: Shallue & Vanderburg (2018) AstroNet; ExoMiner and ExoMiner++ (2022/2025).
   - Modern false-alarm and individual-event work: Robnik & Seljak (2025), Robnik et al. (2026); exoVetter (2026).
   - Adjacent ideas: calibration, uncertainty-aware review, data leakage and train/test shift; separate physics from ML methodology.
3. Synthesize **three observed gaps** as hypotheses, not claims of unprecedented novelty:
   - Noise/false alarms: individual events and secondary/odd-even eclipses can reveal impostors but may reject real planets.
   - Wrong periods and aliases: BLS often finds half the binary orbital period.
   - Multi-planet systems: a single highest-power event can conceal additional planets.
4. Include a short, sourced comparison matrix with citation and what evidence would test each proposed improvement.

**Deliverable:** 2–3 figures/diagrams explaining transit geometry, detection-vs-vetting pipeline, and literature timeline/method comparison. Reference the original papers and avoid overclaiming novelty.

### Part II. Implementation and quantitative evaluation (about 45%)
The *what we actually did*. Separate **published method replication**, **controlled improvements**, **independent tests**, and **observed limitations**.

**A. Original baseline:** Astropy implementation of published BLS. Document exact FITS data source, quality flags, time baseline, normalization, trial-period window, BLS score and output. Use real Kepler-69b to check the published period:
- Published: 13.7223682 days.
- Our real Q8 fit: 13.7133429855 days; relative error 0.06577%.
- This is a case study, **not** a general sensitivity measurement or new discovery.

**B. Catalog ML baseline and extension:** Four-feature sklearn random forest vs signal-to-noise-only rule on 8,054 NASA DR25 KOIs. Group train/validation/test by host star; no disposition score or outcome flags as inputs. Held out: 1,619 catalog signals.
- Signal-strength-only threshold: test accuracy 52.3%, candidate recall 91.0%, FPR 90.5%.
- Four-feature forest: test accuracy 81.6%, candidate recall 87.2%, FPR 24.6%.
- These test recalls differ despite a validation threshold goal; **DO NOT describe these particular results as a matched-test-recall comparison**.
- Same-budget manual review: plain margin 123 wrong automatic decisions, margin plus forest disagreement 122 at 30% review on 1,619 signals. The paired host-bootstrap interval includes zero: no convincing incremental improvement.
- Label interpretation: predicts historical NASA Robovetter CANDIDATE/FP dispositions among already selected KOIs, **not independently confirmed planet truth**.

**C. Improved physical tests on light curves:** Blind period fitting, individual-event consistency, secondary/odd-even eclipse checks, then controlled ablations on synthetic transits and real data.
- In a deliberately simple 56-case synthetic holdout, BLS flagged all 8 binary-like cases; event checks flagged 7; event + binary diagnostic flagged 0. This was an exploratory result on simplified binaries and does not establish realistic reliability.
- The early two-real-star test worked (Kepler-69b did not trigger binary warning; KIC 10661783 did).
- **Critical independent result:** a new frozen cohort of 13 published real Kepler stars analyzed 12/13 files. On the 6 analyzed known binaries, **ZERO** binary warnings were triggered, including 4 half-period aliases and 2 exact-period cases. Among 6 listed planets, the intended period was recovered for 3. This is a **negative external validation** and must be central, not buried.

**D. Multi-planet post-hoc follow-up:** Build an iterative BLS variant that subtracts the first modeled transit and looks again.
- Kepler-20: the first pass finds already known Kepler-20c (~10.858 d); second pass recovers known Kepler-20b (~3.6963 d).
- Kepler-18: recovered Kepler-18c and d but did NOT recover b within three passes; later iteration repeated an alias/residual near c.
- These stars were selected after seeing failures in section C, so this is **development evidence**, not untouched external validation. A future independent cohort is needed.

**Quantitative figures (priority order):**
1. Real Kepler-69b light curve + recovered period annotation.
2. BLS/noise and binary vetting control comparison (simple vs enhanced, with n per class).
3. NASA DR25 held-out confusion matrix/baseline comparison (truth definition in caption).
4. Figure showing frozen real 13-star cohort: exact/alias/unmatched/no data, and binary review warnings.
5. Kepler-20 first/second-pass brightness/residual demonstration.
Avoid unnecessary graphics that do not answer a scientific question.

**Methods assurance:** Publish code and environment, user-assisted AI-use log, fixed seeds, FITS SHA-256s, separate training/testing stars, preregistered selection before independent runs and all recorded failures. Distinguish synthetic from real and BLS detection from ML catalog vetting. The two are not a single end-to-end pipeline unless raw events are matched to KOI rows.

### Part III. Reflection, comparison with established research, next steps (about 20%)
The *what does this prove / not prove?* The reflection should analyze at least one **negative result** rather than repeating marketing claims about AI.

**Key reflection questions:**
- Which coding tasks did generative AI accelerate? How did independent tests reveal AI-generated scientific assumptions or mistakes, including the first narrow 2.8–3.8-day BLS search for a 3.25-day injected planet?
- What improved? Real Kepler period replication, four-feature DR25 label screening relative to SNR alone, recovery of a second known signal in Kepler-20.
- What failed? Ensemble disagreement did not significantly beat margin-only triage; external real-binary vetting failed on a 13-star sample; weak 500-ppm signals were poorly recovered in small examples; iterative model occasionally re-detected the first signal.
- Why? Model features omit independent pixels/centroids; period aliases; signal averaging loses event structure; real stellar variability; sample and label selection; mismatch between synthetic and observed distributions.
- What changes would be required for credible improvement? Alias-aware astrophysical comparison with physical model and pixel checks, stronger baseline and threshold calibration, fresh external holdout, multi-quarter datasets, and repeatable false-alarm measurements.
- What is the scientific lesson? AI is an effective coding/research assistant, not a substitute for physical judgment, independent validation, or careful test design.

## Primary published-paper benchmark: make this distinction explicit

**Recommended primary paper for the physical detection/vetting narrative:**
Robnik, Seljak, Jenkins & Bryson (2026), *Exoplanet transit search at the detection limit: detection and false alarm vetting pipeline*, MNRAS, doi:10.1093/mnras/stag419.
- This is the closest methodological analogue to our project: preprocessing, individual-transit checks, false-alarm vetting, and extracting multiple signals.
- Its paper evaluates injections into Kepler observations on ~5,000 stars, injected periods 200–500 days, and **true detection probability at fixed false-alarm rate**.
- Our current synthetic controls, single-quarter stars and 0.9–20-day searches do **NOT** match the paper's period range, target selection, noise calibrations, or null generation. **Do not compare their published recovery percentages against our 8/8 binary rejections or 1/3 weak-signal recoveries as though they measure the same quantity.**
- Defensible comparison **now**: side-by-side methodological elements, limitations, differences in sample/methods; our reproducible numerical within-study BLS vs extension ablations; our external test that failed.
- Defensible numerical head-to-head **later** (stretch): run an identical selected real Kepler injection test with both our baseline and an openly available implementation of the paper's specified diagnostic(s), using **the same stars, injection distribution, thresholds, and score denominators**. If we cannot reproduce the paper's design, say exactly that.

**Secondary published benchmark for the ML component:**
McCauliff et al. (2015), *Automatic Classification of Kepler Planetary Transit Candidates*, ApJ 806:6, doi:10.1088/0004-637X/806/1/6.
- Their early random forest used **77 attributes**, three classes (planet candidates, astrophysical false positives, instrumental/non-transit signals) and a different earlier Kepler dataset; the paper reports **5.85% overall classification error** and **2.81% candidate-related binary error** under their methodology.
- Our forest used **four** attributes, **two** historic DR25 KOI categories, **different** target definitions and a grouped-by-star heldout test, with **18.41% error** against the DR25 vetter labels (1 - 81.59% accuracy).
- These numbers may be shown in a *clearly labeled historical-context table*, but **they are not an apples-to-apples accuracy competition**. A causal claim that our classifier underperforms the McCauliff paper because of AI, or outperforms it because of a new rule, would be unsupported. For a valid quantitative paper replication, both methods must use the **same TCE catalog, same three labels, matching attributes and identical heldout split**; that is not yet implemented.

**Dataset/source paper:** Thompson et al. (2018), DR25 Robovetter, ApJS 235:38, doi:10.3847/1538-4365/aab4f9. This paper produced our historic KOI label dataset, so it must be cited as **data provenance**, not treated as an independent truth standard for confirming planets.

**Concluding language suggestion:** We reproduced established numerical methods and several real signals, but independent testing exposed serious alias and false-positive limitations. The project's improvement is a transparent, AI-assisted development/evaluation workflow with selected promising components, not a demonstrated superior survey detector.

### November 8 source-grounded extension: real astrophysical eclipses versus instrument defects

The [fresh twelve-source Kepler Q6 archive-label experiment](VERIFIED_REAL_SPSD_EXTERNAL_Q6_RESULTS_2026_11_08.md) was preselected and run on original NASA files. Ten sources were available; two planned failures remained in the denominator. The observed sources contained **no SPSD bit-1024 positive events**, making the primary natural-defect sensitivity question *unanswerable on this cohort*. Across those ten sources were only thirteen method-level warnings (six SAP, seven PDCSAP), twelve of them concentrated on known eclipsing-binary system Kepler-47.

[Independent published stellar ephemerides applied to those original warnings](VERIFIED_KEPLER47_ECLIPSE_CHECK_2026_11_08.md) show five of seven distinct warning times within ±0.1 days of a published binary eclipse, and six within ±0.3 days. The analysis is **post-hoc** and should be placed in Part III as a failure-mode investigation. With all warning intervals held fixed, a 20,000-offset binary phase-shift sensitivity exercise gave fractions 0.02125 and 0.0749 at those respective windows; these are not confirmatory p-values because the object and windows were examined after the outcome. The physical concern is that a local negative-step screen can confuse astrophysical variability with instrumental damage. Future work needs an untouched sample of *both* genuine source-labeled discontinuities and binaries before claiming a new repeatability veto.

### Physical illustration after the binary timing audit

A further reproducible [Kepler-47 raw SAP versus PDCSAP phase-folded demonstration](KEPLER47_ORIGINAL_FLUX_VISUAL_CHECK_2026_11_08.md) downloaded the *original* official NASA source and verified the same SHA-256 as in the prospective Q6 experiment. Both flux products retain the expected published primary and secondary stellar eclipse shapes when folded on the **7.44837568-day binary period**; the three earliest originally flagged warning windows show brightness declines near predicted secondary eclipses. The independently validated NASA workflow passed **109 software tests**. Use the **binary phase-fold figure** as the physical bridge between Lesson 6 and Part III's post-hoc warning-interpretation lesson, with an explicit caveat that no independent population accuracy has been established.

### New prospective eclipse-preservation test (November 8)

Use the [verified 13-star recurrence-guard study](VERIFIED_RECURRENCE_GUARD_Q6_RESULTS_2026_11_08.md) as the strongest *honest within-study* attempt to correct the failure revealed by Kepler-47. The unchanged localized-step mask produced 10 warning rows; a blinded, flux-only 2.5–22-day repetition heuristic protected two warning windows (known independent Kepler-1647 and Kepler-35 binaries), retaining **42 previously masked actual NASA measurement cadences**. Its inferred repetition periods closely matched the stellar binary period or a half-period alias *without published values being input to the algorithm*. Equally importantly, it **missed all six SAP/PDCSAP warnings at three Kepler-34 eclipse times**, a published ~27.8-day binary beyond the frozen 22-day range. All 13 target files were available. Zero targets had an official quality-bit-1024 SPSD event, so **true instrument-defect safety/sensitivity remains unestimated on the independent sample**. The only previously known real-SPSD developmental control was correctly *not* protected as periodic, but cannot be generalized. Use Kepler-34 failure as an explicit physical and statistical limit in Part III, and retain the two historical workflow engineering runs in the AI log.

## Course alignment: explicit rubric and checklist map

From the instructor's *FinalProject.pdf*: project is **35% of course grade**; grading includes **40% depth/scope/quantitative accuracy**, **15% writing**, **15% originality/perspective**, **10% synthesis of at least two lectures**, **5% bibliography**, **5% proposal**, **10% status report**. For a non-essay computer program, a **minimum 300-word explanatory write-up** is required and **every project must have a quantitative component**. The **Project Elements Checklist Form** must be completed and appended to the write-up.

**At least two grounded course lecture connections:**
- **Lesson 6 (Kepler's Laws):** periodic orbital motion, ellipses, Kepler's third law, using fitted period to characterize orbit, alias P vs P/2 vs 2P.
- **Lesson 5 (Newtonian gravity):** gravity supplies the centripetal acceleration of a planetary orbit; rough relation P^2 = 4 pi^2 a^3 / [G(M_star + M_planet)] (Newtonian approximation); physical reason periods relate to orbital distance.
- **Optional bonus: Lesson 3 (Time):** astronomical time measurement, periodicity, cadence, timing windows and orbital period errors. Lesson 2 measurement/geometry is also relevant to relative radii via transit depth but use the strongest three.

**Numerical component location:** Section II, method/metric tables, BLS fitted-vs-known periods, confusion matrices, group counts, 95% uncertainty where warranted, and model performance comparisons. A sample worked calculation: for Kepler-69b, |13.7133429855 - 13.7223682| / 13.7223682 × 100 = **0.06577% period error**.

**Deliverables:** (i) program and notebook; (ii) final written discussion; (iii) bibliography; (iv) AI-use disclosure; (v) completed instructor checklist as appendix.

## Near-term writing and build schedule

**By Nov 20:**
- Finalize the literature/method comparison and pick Robnik 2026 as primary methodological paper.
- Present the successful NASA DR25 experiment; the independent 13-star binary failure; real Kepler-69 period result; Kepler-20 second-pass result.
- Submit the 1–2 page project status update describing these accomplishments and changes from the proposal, as required.

**Nov 21–Dec 4:**
- Stabilize reproducible scripts; select a **fresh** untouched multi-planet cohort if doing further experimental work.
- Avoid endless hypothesis changes; prioritize explainable figures and one scientifically compelling comparison.
- Validate all literature quotes, figures, scripts, and references.

**Dec 5–11:**
- Write the three-section final report, append source bibliography, append completed checklist, and double-check course lecture connections.
- Upload digital write-up and GitHub/program link to Canvas by Dec 11 at 11:59pm CST.

## Primary references

1. Kovacs et al. (2002), original BLS: https://doi.org/10.1051/0004-6361:20020802
2. McCauliff et al. (2015), three-class Kepler random forest: https://doi.org/10.1088/0004-637X/806/1/6
3. Thompson et al. (2018), NASA DR25 catalog: https://doi.org/10.3847/1538-4365/aab4f9
4. Shallue & Vanderburg (2018), deep learning: https://doi.org/10.3847/1538-3881/aa9e09
5. Hippke & Heller (2019), TLS: https://doi.org/10.1051/0004-6361/201834672
6. Valizadegan et al. (2022), ExoMiner: https://arxiv.org/abs/2111.10009
7. Valizadegan et al. (2025), ExoMiner++: https://arxiv.org/abs/2502.09790
8. Robnik & Seljak (2025), null template calibration: https://doi.org/10.1073/pnas.2513927122
9. Robnik et al. (2026), physical vetting and multiple candidates: https://doi.org/10.1093/mnras/stag419
10. MAST public Kepler archive: https://archive.stsci.edu/kepler/
11. Astropy BLS implementation: https://docs.astropy.org/en/stable/timeseries/bls.html

## Research integrity

The literature synthesis and code drafting were assisted by GPT-6. The student retains responsibility for understanding the physics and mathematics, auditing any numerical values, selecting/investigating methods, writing genuinely understood scientific conclusions, and complying with the instructor's requirements on original individual work and disclosure. Never present a published or standard technique as a novel discovery, or a successful synthetic test as proof of real observational reliability.

### November 7 implementation update: frozen observational and synthetic defect experiment

The full method and verified result are in [PART_II_LOCALIZED_DEFECT_EXPERIMENT.md](PART_II_LOCALIZED_DEFECT_EXPERIMENT.md) and [VERIFIED_LOCALIZED_STEP_RESULTS_2026_11_07.md](VERIFIED_LOCALIZED_STEP_RESULTS_2026_11_07.md). The prospectively selected two-calibration/six-held-out-star experiment compared baseline BLS, old gap masking, and a new fixed persistent-step mask. On the **natural** light curves, the new method's extra 1/36 recovered injection came from a **different threshold**, with no input processing differences. On deliberately injected **instrument-like steps**, the new mask corrected one wrong-period fit among 36 cases and reduced constructed proxy false triggers from 13/24 to 10/24, but removed eight genuine artificial transit cadences. These remain exploratory and do **not** reproduce published mission-scale, long-period matched-FAP benchmarks. Use this as a central case study in Part III about scientific validation and the limits of AI-coded methods.

### Independent instrument-label example (November 7)

A new **illustrative**, not unbiased, case uses [KIC 7461601 Q6](REAL_KEPLER_SPSD_CASE_RESULTS_2026_11_07.md), an official STScI-documented sudden sensitivity dropout. Our fixed step heuristic detected the genuine flagged sudden decline in the original SAP aperture flux within one ~29.4-minute Kepler cadence, but did not mark it on the presearch-conditioned PDCSAP series. This source-backed observation provides physical context for why our six-star, already-PDC-corrected experiment yielded **no genuine natural-step flags**. Use the full SAP/PDC figure and archived FITS fingerprint in Part I (physical problem) or Part III (instrument data limitations). Do NOT count one preselected positive example toward independent classifier sensitivity or a false alarm rate.
