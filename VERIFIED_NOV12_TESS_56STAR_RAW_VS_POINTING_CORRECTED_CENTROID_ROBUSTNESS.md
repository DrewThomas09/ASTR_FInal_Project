# November 12, 2026: Source-verified test of the TESS pointing correction in our centroid sidecar

**New empirical question:** When I subtract the original TESS SPOC spacecraft-pointing estimate (`POS_CORR1/2`) from the moment-centroid coordinates (`MOM_CENTR1/2`), does it make the recorded centroid **more stable locally** around the same measured transit windows? This is a **different question** from whether ExoMiner detects planets more accurately.

## Source and method

This is an **exploratory secondary analysis**, done *after* the earlier centroid experiments. It reuses the **56 distinct original TESS SPOC 2-minute star light curves** already independently inspected by the student project: the 32 previously studied stars from [original NASA ExoMiner++ v2.4.0 run 42526063290](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42526063290) and the 24 additional stars from [original NASA run 42526495887](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42526495887). Both versions of each star's calculated original real event window were loaded from the existing workflow result archives; the model was **not** rerun, retrained, or supplied any newly modified inputs.

For all **248 actual complete matched original observed event windows**, I paired the unadjusted `MOM_CENTR` measurements and the exploratory `MOM_CENTR-POS_CORR` result by **exact star UID, orbit index, and original NASA TCE event center**. Events with missing raw/corrected counterparts or NaNs fail the analysis rather than producing fabricated source changes.

For one event, the pre/post stability *proxy* is the Euclidean distance between the **median before-event centroid** and **median after-event centroid** in original detector pixels. I computed each star's *median across its own observed events* and then compared the two source-level numbers. Each star counts **once** in the signed-rank/sign comparison, not once per TESS cadence or per transit. A **20,000-replicate whole-star bootstrap** resamples the 56 paired source vectors to quantify uncertainty in the **median source-paired reduction**. The source selection, thresholds and reported tests are exploratory and were not independently preregistered.

**Original source SHA256 pins:** 32-source NASA/TESS summary `84367f439fb58164a28768fd838288d205c6bdd4375c68b6f5e647580c471ea5`; 24-source summary `5a480b898fd3e54e84f2d60eb4f422a628d3d3aa7fe93da985b2c3f3d9e9f08a`. All raw and adjusted values are independently traceable to the original NASA/TESS same-light-curve source-event tables in these artifacts.

## Full observed results

| Physical metric | Original uncorrected moment centroid | Experimental moment centroid minus POS_CORR |
|---|---:|---:|
| Independent source TIC stars with valid event windows | **56** | **56** |
| All original matched observed full-event windows | **248** | **248** |
| Median of per-star event-median **pre/post local centroid displacement** | **0.003139 pixel** | **0.001400 pixel** |
| Median of per-star event-median **in-transit centroid displacement** | **0.000763 pixel** | **0.000648 pixel** |

The ratio of the two group medians for the **pre/post drift proxy** is about **0.446** (a **55.4% smaller group median** after the adjustment). More directly, the **median of the within-star paired reductions** is **0.001035 pixels**, with a **star-bootstrap 95% interval [0.000738, 0.001891] pixels**. The correction reduced local pre/post centroid displacement for **44/56 stars** and increased it for **12/56**; the two-sided exploratory source-level **exact sign-test p = 2.09 × 10^-5**, and paired Wilcoxon p = **3.67 × 10^-5**.

- Earlier 32 star cohort: **28/32** had lower pre/post local centroid movement after subtraction and **4/32** increased.
- Additional 24-star cohort: **16/24** improved and **8/24** worsened.
- If restricted to the previously defined **40 stars with at least three usable event windows**, **30/40** improved and **10/40** worsened (exploratory exact source-level two-sided sign p **0.00222**).
- The magnitude of in-transit local centroid shift also fell for **38/56 stars**, but increased for **18/56**. **This does not imply better discrimination**: an astrophysical off-target eclipse may itself cause a real centroid displacement, which could be suppressed by subtraction.

## Interpretation and limits

These results justify saying **our experimental pointing adjustment often stabilizes the *measured local moment centroid*** on the selected original stars. **They DO NOT show** the adjusted value corresponds more accurately to the true angular position of a transiting star, correctly identifies off-target eclipses, or improves the NASA neural model. The pre/post displacement is only a **drift proxy** and can include real astrophysical or source-mask changes. Crucially, `MOM_CENTR - POS_CORR` is **not** NASA ExoMiner's difference-image centroid branch and was not a new neural input supplied to ExoMiner.

All 56 stars were **already analyzed** by the student project and were historically class-balanced/error enriched rather than representative survey stars. NASA's original pretrained 2026 training exclusions for these TESS targets remain unverified. The measured gain was tested on the *same physically observed sources*, not a random or prospective sample. Repeated event-level windows are **not** treated as 248 independent stars, and astrophysical/instrumental systematics remain.

The strongest conclusion is a methodological distinction important for the final ASTR paper: **stabilizing an instrument measurement is easier to establish than improving a scientific classification system.**

## Reproducibility

- **Verified successful GitHub Actions run:** [run 43291965755](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43291965755); **254 scientific regression tests passed**, including five additional strict source-pairing and invalid-data failure-mode tests, source SHA pins and same-event comparisons succeeded, original source-level sample size rechecked.
- **Complete original event-aligned source results and figure:** [GitHub Actions artifact 13975484787](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43291965755/artifacts/13978490345)
- **Executable primary source reproducibility script:** [`tess_56star_paired_pointing_motion_robustness_nov12.py`](tess_56star_paired_pointing_motion_robustness_nov12.py)
- **Pinned official GitHub workflow:** [`.github/workflows/tess-56star-raw-vs-poscorr-original-events.yml`](.github/workflows/tess-56star-raw-vs-poscorr-original-events.yml)
- The 16-page editable **Times New Roman student research paper** (including the completed course checklist), single-page status update, seven earlier figures and new **Figure 8** were generated as ChatGPT downloadable artifacts, **not automatically submitted to Canvas**.

**AI assistance disclosure:** GPT-6 helped implement the original source comparison, compute uncertainty, generate the figure, check the source hashes, draft the scientific write-up and revise the Times New Roman submission documents. The student is responsible for interpretation, review, and course submission.
