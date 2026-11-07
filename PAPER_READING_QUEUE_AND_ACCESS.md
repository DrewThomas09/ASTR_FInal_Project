# Research Paper Reading Queue — ASTR 12600 Final Project
Updated: November 7, 2026

**Access check:** All seven papers below have an openly accessible publisher or author-hosted full text or arXiv copy. No university login is essential to begin. Do not request institutional credentials or redistribute publisher-licensed copies.

## Access using your University of Chicago account (verified November 7, 2026)

**The first seven papers listed below have free full-text copies**, so a CNetID sign-in is **not required** for those links. If you prefer the publisher version or encounter a paywall, University of Chicago Library's current off-campus system is **OpenAthens**. The University explicitly advises:

1. Begin at [UChicago Library](https://www.lib.uchicago.edu/) and find the title/DOI through the library catalog or Articles Plus. **Click the library-provided full-text link**; if access is licensed and you are off campus, it prompts you to sign in with your **CNetID**.
2. On a publisher site that supports institutional sign-in, use **Sign in / Access through your institution → University of Chicago**, then follow the university OpenAthens login.
3. Alternatively, install **LibKey Nomad**, which UChicago recommends to find subscribed articles directly while browsing publisher pages; it can direct you to interlibrary loan if needed.
4. Do **not** purchase a paper merely because a direct publisher DOI link shows a price. Try the free arXiv/PMC link or the Library's licensed route first.
5. Never send passwords or authentication codes to the research project or GitHub.

Official University instructions: [Proxy & Off-Campus Access](https://www.lib.uchicago.edu/borrow/access-privileges/offcampus/); [Off-Campus Guide (OpenAthens, LibKey Nomad)](https://guides.lib.uchicago.edu/off-campus/Home).

**Access limitation:** This confirms the university's authentication route, not whether a particular publisher's *licensed* version is included in the current account. For these papers the freely accessible copies already solve that issue. GitHub repository access is separate from university library access.

## First four source papers reviewed

**Reviewed against student-provided complete PDFs, with exact figure/page references:** Kovács (2002), McCauliff (2015), Thompson (2018), and Robnik (2026). Read the [critical synthesis](PART_I_FOUR_PAPER_CRITICAL_REVIEW.md) before adding more papers. The next action is not another catalog of summaries but a test matching false-alarm rates.

## Priority 1: read these three in full first

### 1. Robnik, Seljak, Jenkins & Bryson (2026) — PRIMARY PHYSICAL-METHOD BENCHMARK
*Exoplanet transit search at the detection limit: detection and false alarm vetting pipeline.* MNRAS 547, stag419.
- Published open-access article: https://academic.oup.com/mnras/article/547/3/stag419/8527731
- Free full manuscript/PDF: https://arxiv.org/pdf/2601.07465
- DOI: https://doi.org/10.1093/mnras/stag419
- Read questions: How are local light-curve defects removed? What precisely constitutes per-transit inconsistency? How does their multi-candidate algorithm avoid repeating aliases? Which metrics, injection distributions, baseline sample and false-alarm calibration support each reported gain? What can their methods **not** infer?
- Comparison requirement: Our present 1–20-day/quarter-length tests and simplified binary simulations DO NOT reproduce their long-period/whole-mission injections. Avoid presenting percentages as a head-to-head replication until matching the experiment.

### 2. McCauliff et al. (2015) — SECONDARY ML PAPER BENCHMARK
*Automatic Classification of Kepler Planetary Transit Candidates.* ApJ 806:6.
- Free full arXiv PDF: https://arxiv.org/pdf/1408.1496
- Publisher free-access full text: https://doi.org/10.1088/0004-637X/806/1/6
- Read questions: What three candidate labels did the original work predict? How were labels established? Which of their many attributes encode secondary eclipses/centroid position? How was cross-validation performed? What are the consequences of evolving survey candidate distributions?
- Comparison requirement: Their ~5.85% classification error and our ~18.41% DR25 heldout binary-label error are NOT apples-to-apples: different population, labels, attributes, data release and validation design.

### 3. Thompson et al. (2018) — DATA PROVENANCE / ROBOVETTER GROUND TRUTH
*Planetary Candidates Observed by Kepler. VIII. A Fully Automated Catalog with Measured Completeness and Reliability Based on Data Release 25.* ApJS 235:38.
- NIH PMC free full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC7477822/
- Read questions: How were the 8,054 KOIs selected from TCEs? What separates Robovetter CANDIDATE from FALSE POSITIVE? What are injection/inversion/scrambled test samples? How do completeness, reliability, vetting score and astrophysical false positives differ? What uncertainties do the labels carry?
- Our 8,054-rows NASA CSV and train/test classification are based on **this historical vetter outcome**; that does not establish independent planet truth.

## Priority 2: physical method foundation and plausible improvements

### 4. Kovacs, Zucker & Mazeh (2002) — ORIGINAL BASELINE
*A box-fitting algorithm in the search for periodic transits.* A&A 391, 369–377.
- Open-access published article: https://doi.org/10.1051/0004-6361:20020802
- Read: box-shaped search, transit durations, detection statistic, noise assumptions, false peaks and frequency grid. Our actual implementation uses Astropy's published BoxLeastSquares method.

### 5. Hippke & Heller (2019) — STRONGER PHYSICAL TEMPLATE
*Optimized transit detection algorithm to search for periodic transits of small planets.* A&A 623, A39.
- Open-access article: https://doi.org/10.1051/0004-6361/201834672
- Read: limb-darkened template vs box, injection-recovery outcomes, computational tradeoffs, risk of assuming that a better match proves a planet.

### 6. Robnik & Seljak (2025) — FALSE-ALARM CALIBRATION
*Reassessment of Kepler's habitable zone Earth-like exoplanets with data-driven null signal templates.* PNAS 122, e2513927122.
- NIH PMC free full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC12541445/
- Author preprint PDF: https://arxiv.org/pdf/2509.07409
- Read: null signal templates, effect of instrumental noise and stellar variability, how significance is calibrated, why inverting/scrambling can produce incorrect nulls, distinction between instrumental false alarms and astrophysical eclipsing binaries.

### 7. Dallas et al. (2026) — MOST RECENT MODULAR VETTING COMPARISON
*ExoVetter and a TESS Exoplanet Transit Search of Kepler Stars as Ground Truth.*
- Free full preprint PDF: https://arxiv.org/pdf/2610.32949
- Read: modular physical diagnostics, pixel centroid tests, evaluation against different instrument data, catalog-specific selection effects, and open-source implementation.
- Scope warning: TESS evaluation and Kepler reference stars are not the same as our DR25 KOI task.

## Optional background for the literature review (no urgent downloads)
- Shallue & Vanderburg (2018), CNN / AstroNet: https://doi.org/10.3847/1538-3881/aa9e09
- Valizadegan et al., ExoMiner/ExoMiner++ (2022/2025): https://arxiv.org/abs/2111.10009 ; https://arxiv.org/abs/2502.09790
- Public NASA Kepler data and Lightkurve/Astropy algorithm documentation: https://exoplanetarchive.ipac.caltech.edu/ ; https://docs.astropy.org/en/stable/timeseries/bls.html

## If a student wants to upload PDFs into this conversation
Not necessary for paper availability: the public links above are accessible. However, attaching the exact PDF of **#1 Robnik 2026** and **#2 McCauliff 2015** is useful for stable page/figure-by-figure annotation. If convenient, add **#3 Thompson 2018**. No institutional password, paid publisher account, or private academic credentials should ever be shared.

## What happens once we read the first three
For each: source metadata, methodology flowchart in plain language, exact sample/population, data-generation process, baselines, metrics/threshold, strongest quantitative evidence, failure modes acknowledged by authors, whether original code/data are available, and precisely which pieces we can reproduce with our current code.

Then prepare **one honest comparison table** contrasting the source paper's task with our current implementation. Avoid comparing published performance percentages from entirely different statistical questions.

## Traceability
This reading queue was assembled through AI-assisted web verification of source availability and abstracts/full article pages. It is not yet a finished full-paper annotated literature review. The researcher/student must read and verify the methods, figures and interpretation before scientific claims are finalized.
