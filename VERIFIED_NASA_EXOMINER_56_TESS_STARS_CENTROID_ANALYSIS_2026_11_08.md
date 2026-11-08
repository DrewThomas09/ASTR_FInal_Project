# Actual NASA ExoMiner++ on 56 TESS stars: original flux-weighted centroid and a failed simple review rule
**2026-11-08 | Reproducible two-cohort original-source astronomy study | not an improved NASA classifier**

## What was actually reproduced

The experiment uses the authentic, unmodified NASA ExoMiner++ **v2.4.0** pretrained `planet-validation / single` model and original public SPOC 2-minute TESS light-curve FITS. It tests whether a separate physically interpretable TESS centroid shift diagnostic contributes a useful *human-review* warning beside the full NASA neural output. The student's code **does not modify or retrain NASA's CNN**; the model already uses richer image-difference/centroid diagnostics.

Original source fields `MOM_CENTR1,MOM_CENTR2` measure the flux-weighted CCD centroid in pixels, while `POS_CORR1,POS_CORR2` record estimated field motion from pointing/PSF motion polynomials. We compute an exploratory corrected centroid `C'=MOM_CENTR-POS_CORR` (which is **not NASA's official difference-image centroid model**), then at each **original TCE period/epoch** compare its in-transit median position with the mean of pre- and post-transit centroid medians from the same event. Any missing or quality-flagged cadence remains missing. Minimum valid event: **3** in-transit observed positions and **6** each pre/post. The source-level median signed x and y shifts use actual separate event windows and **500** event-bootstrap resamples for *descriptive*, not model-independent, confidence intervals. Only stars with **at least 3 original events** get a computable review flag.

The frozen original illustrative review flag required **median vector centroid displacement >=0.05 TESS pixels** (~**1.05 arcseconds**, for ~21 arcsec/pixel) **and** a nonzero event-level bootstrap interval on either signed x or y axis. It was written before measuring the 32 development stars, and was carried forward unchanged to 24 new-to-student TIC hosts selected without access to any old or new NASA score. Threshold was not calibrated to an independent mission false-positive rate.

[Original NASA and MAST centroid field documentation](https://spacetelescope.github.io/mast_notebooks/notebooks/TESS/beginner_tour_lc_tp/beginner_tour_lc_tp.html) · [NASA TESS pixel scale (~21 arcsec/pixel)](https://heasarc.gsfc.nasa.gov/docs/tess/telescope_information.html) · [full precommitted experimental geometry and uncertainty](TESS_REAL_32STAR_TRANSIT_CENTROID_EXPERIMENT_PROTOCOL_2026_11_08.md)

## Exact original-source execution and outputs

| Research property | Earlier original 32-star development cohort | Different 24-star student source cohort |
|---|---:|---:|
| Original sources requested and official NASA pretrained TCEs matched | **32/32** | **24/24** |
| Genuine original TESS SPOC light curves and MOM_CENTR inputs recovered | **32/32** | **24/24** |
| Individual original *qualifying full-event centroid windows* observed | **146** | **102** |
| Stars with at least three full source events (rule evaluable) | **23** | **17** |
| Source stars lacking enough events for *any* flag | **9** | **7** |
| Original frozen **>=0.05-pixel** centroid review flags | **0** | **0** |
| Largest observed source median corrected centroid shift | **0.008222 px** | **0.020728 px** |
| Period identity versus original 2025 TCE IDs | **28** within 1%; **3** other period; **1** double alias | **22** within 1%; **1** half alias; **1** double alias |
| Original full-project regression tests passed | **235** | **240** |

**Verified original 32-star NASA/model-plus-centroid run:** [Actions #42526063290](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42526063290) and [all source FITS hashes, 39 original NASA model TCE results, 64 raw+corrected per-source event tables, original model log, plot and full all-32 CSV](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42526063290/artifacts/13636045410).

**Verified different 24-star NASA/model-plus-centroid run:** [Actions #42526495887](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42526495887) and [all source FITS hashes, 26 original NASA TCEs (24 originally requested source UID TCEs), 48 per-source raw/corrected event tables and unmodified NASA scores](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42526495887/artifacts/13635273257). The twenty-four hosts are **distinct from all earlier thirty-two source TICs and NASA's documentation example**; [source IDs were frozen before the original NASA inference](TESS_NEW_24STAR_CENTROID_RULE_HOLDOUT_FROZEN_2026_11_08.json) and [selection is reproducible from the score-excluded source catalog columns](scripts/reproduce_frozen_24star_centroid_holdout.py). They are not guaranteed excluded from NASA's own network training.

NASA version pinned for both runs:
`ghcr.io/nasa/exominer@sha256:1b7ffac9db8afe1787ec9a0464ed8cc16ab91b7a280e6e824c27e3a121b0c6e9`, v2.4.0, same original source ephemeris and TCE duration **hours**. The older 2025 published table stores duration **days**, and comparisons convert explicitly and flag altered period aliases.

### Why the initial centroid modification failed

Our original model-development hypothesis was that a strong transit-phase-localized centroid movement might help identify which source in the aperture produced an apparent brightness dip. The code *worked mechanically* on the original NASA light curves: it detected original moment centroids and estimated source-local shifts without synthetic interpolation or score changes. But **the chosen >=0.05 pixel rule was simply too large**, and flagged **zero of the 40 evaluable source stars** across both samples. Therefore it cannot be cited as a successful improvement.

Some historical **eclipsing binaries** had among the largest local centroid displacements. For instance previously EB-labeled `294206967-1-S10` produced **0.008222 px** and `318986273-1-S10` produced **0.006748 px**; both already had original NASA planet scores close to zero and were **correctly below the existing planet-candidate threshold**. In the separate 24-star cohort, previously EB-labeled `443171652-1-S6` had **0.020728 px**, `126586580-1-S7` **0.007832 px**, and `279569718-1-S12` **0.002453 px**: again the original neural network already assigned very low planet scores to these examples. These source-level shifts are in CCD pixels, not directly arcseconds of transit-source offset or a formally calibrated probability.

**No evidence of incremental NASA classifier gain:** even a warning based on the larger shifts might simply restate classifications already made correctly by NASA's internal difference-image and centroid branches. We should not lower the threshold *after inspecting* these examples and present the reselected threshold as a prespecified result.

## Additional separate development-calibrated gate

After observing the 32 original **development** centroid outcomes but **before inspecting the 24 new-source results**, a transparent *secondary* experimental warning threshold was frozen in [TESS_32_TO_24_CENTROID_POSITIVE_REFERENCE_GATE_FROZEN_2026_11_08.json](TESS_32_TO_24_CENTROID_POSITIVE_REFERENCE_GATE_FROZEN_2026_11_08.json). It is the 95th percentile (numpy method `higher`) of local centroid magnitudes from the **13** original development stars labeled KP/CP that had ≥3 complete observed centroid event windows: **0.0016012455384686 pixels**. Original 32 source CSV digest SHA256 `84367f439fb58164a28768fd838288d205c6bdd4375c68b6f5e647580c471ea5` is pinned to prevent silently changing training data. With 13 examples, a 95th `higher` quantile equals **their single maximum**, and is therefore statistically unstable.

The exact same three-event and nonzero-bootstrap-axis criterion remains. To avoid source leakage, the secondary threshold must be evaluated **only on the separate 24 original TESS stars that were not used to derive it**. We **must preserve and report any new-source false warnings on KP/CP labels**, not merely count EB/NTP hits. It is a **manual-review warning**, *not* a hard planet rejection or a modified trained NASA neural network. A "positive" result for historical-class warnings does not establish a new astrophysical detector. The [frozen analysis code](tess_centroid_32_to_24_frozen_calibration_eval.py) and [source-confirming workflow](.github/workflows/tess-centroid-32-to-24-precommitted-gate.yml) are committed; this section intentionally gives **no outcome for that secondary gate until its actual independent-to-project 24-source postprocessing is verified**.

## What an honest final project can claim

The meaningful engineering result is an **end-to-end reproducible independent telescope-measurement stream alongside NASA's complete pretrained model**, now run on **56 separate source stars** and **248 genuine qualifying individual event windows** across two source cohorts. This exposed a real research limitation: **the arbitrary chosen threshold failed**, and a development-derived much smaller threshold may still provide no advantage relative to the model's already-excellent pixel-level vetting.

The project does **not** yet show (i) improved ExoMiner++ neural model discrimination at equal false-alarm rate, (ii) independent exoplanet confirmations, (iii) true 2026 training-excluded classification generalization, or (iv) that `MOM_CENTR-POS_CORR` local shifts add information beyond existing ExoMiner centroid/difference-image diagnostics.

**AI disclosure:** GPT-6 authored original-data workflows, centroid science code and testing, source selection, threshold checks, comparison and technical writing; student must independently inspect and cite raw sources, diagrams and course expectations.

## Final result of the additional 32-development → 24-different-star calibrated rule

**[Original new-to-student 24-star experimental run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42526495887)**: **240 full tests passed**, original NASA v2.4.0 successfully processed **all 24 exact original source TCEs**, along with **26 total detected TCEs** from those stars, using **24 of 24 original source FITS**, **102 individual original-event centroid windows** and full original source hashes. The fixed .05px rule had **17** source stars with enough events and **0** warnings. [Raw all-source outputs and original model artifact 13635273257](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42526495887/artifacts/13635273257).

**[Actual source-verified development-calibrated comparison, run #42527143827](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42527143827)**: **249 scientific software tests passed**, the separate 24-source TICs and labels were independently **recreated exactly by the original SHA256 ordering without ever reading the 2025 `score` column**, and the previously frozen old 32-development positive-reference threshold was recomputed from the original SHA256-verified CSV, not fitted from the new 24 observations. [All 24 original-event aligned source outcomes, unchanged NASA scores, explicit threshold, independent star ID manifests, and negative result (artifact 13635706682)](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42527143827/artifacts/13635706682).

The new rule was fixed **after inspecting the 32 development source magnitudes but before examining the 24 new-source centroid magnitudes**: use the 95th percentile with NumPy `method='higher'` from the **13** eligible historical known/candidate planet source stars in the development set, `0.0016012455384686` original TESS CCD pixels, plus the *same* ≥3 observed events and one bootstrap signed-axis interval excluding zero. The old threshold of `0.05` pixels remained unchanged. It was a **fixed source-centroid human-review gate**, never a revised NASA neural-network output.

| Fixed metric, 24 stars not previously used in development | Original ≥0.05px rule | Additional development-learned >0.00160125px rule |
|---|---:|---:|
| Exact new-to-project TESS source TICs and NASA original TCEs scored | 24 | 24 |
| Same original TESS light curves with event-centroid measurements | 24 | 24 |
| Stars with enough original individual transit events for evaluation | 17 | 17 |
| **All source-centroid review warnings** | **0** | **5** |
| Original class **EB** stars triggering warning | 0 | **4** |
| Original class **KP** stars triggering warning | 0 | **1** |
| New warning **among official NASA score ≥ 0.5** | 0 | **1** |
| New warning on **historical nonplanet** signal that NASA had accepted | **0** | **0** |

Five true original TESS source cases crossed the calibrated warning threshold (not new discoveries):

| Original TESS TCE UID | Original 2025 label | NASA 2026 v2.4.0 **unmodified** planet score | Local event centroid magnitude | Interpretation |
|---|---|---:|---:|---|
| `78055054-1-S5` | KP (historically known planet) | **0.6008426** | **0.001665 px** | Additional review warning on a **planet-labeled source NASA accepts**. This is a potential false warning; NOT proof the model misidentified it, and would be harmful if used as a hard veto. |
| `10756751-1-S3` | EB | 0.0 | 0.001998 px | Centroid warning, but **NASA already rejected** this EB-labeled signal. |
| `126586580-1-S7` | EB | 0.000004190 | 0.007832 px | Centroid warning, already rejected by NASA. |
| `279569718-1-S12` | EB | 0.00000001235 | 0.002453 px | Centroid warning, already rejected by NASA. |
| `443171652-1-S6` | EB | 0.00000006162 | 0.020728 px | Strongest observed local displacement, but NASA already rejected the EB-labeled source. |

**Result: no incremental classification improvement.** The calibrated centroid warning found four older eclipsing-binary examples that NASA's existing model had **already assigned essentially zero planet probability**, plus **one known-planet-labeled observation currently accepted by NASA**. On these 24 new-to-development, historical-category examples, it neither repaired an accepted false positive nor gave new evidence of a real planet; hard-veto application would instead risk discarding a candidate already regarded as planetary. The result strongly argues **not** to add the simple centroid gate to NASA's operational inference. It is a useful negative experiment and emphasizes the importance of comparing a modification **against the full sophisticated NASA baseline**, not only against simplistic dip detection.

**What is and is not held out:** the twenty-four source stars were completely excluded from the **student's 32-star centroid development/calibration set** and chosen without accessing either 2025 or 2026 model scores, and all original source UIDs were verified. They were **not** proven to be excluded from **NASA's 2026 network training**, and the labels are retrospective researcher-published classifications. The 2025 and 2026 TCE ephemerides differ for some cases. No statement about new-planet confirmation, independent 2026 neural sensitivity or a statistically established population false-positive rate is justified.

**Engineering debugging transparently preserved:** the first postprocessing workflow failed three *synthetic fixture assertions* because the test wrote invalid JSON floating notation `[.001,.004]` instead of valid `[0.001,0.004]`; the second attempted source-reproduction process failed because invoking a script by path omitted the repository root from Python's import resolution. Both failures were fixed **without changing the frozen percentile, original source cohorts, actual NASA predictions, original-source hashes or real-data measurement code**. The successful run produced the exact original 24 source identities and scores and passed all **249** tests.

**Course-level lesson:** AI-generated and AI-assisted code can reproduce an enormous scientific pipeline and construct falsifiable additional diagnostics. But actual original-data testing can show that a promising change offers no incremental benefit, even when it works technically. The experiment is an effective demonstration of *why calibration, measurement uncertainty, telescope source contamination, controlled comparisons and honest negative findings matter*.

