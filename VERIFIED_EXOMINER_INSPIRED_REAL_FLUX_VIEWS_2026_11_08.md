# Verified ExoMiner-inspired Kepler flux-view engineering demonstration
**2026-11-08 | Demonstration of useful physical evidence, NOT official NASA ExoMiner inference and NOT independent classifier validation.**

[Source code](exominer_inspired_kepler_views.py) · [test suite](tests/test_exominer_inspired_kepler_views.py) · [successful official-NASA-photometry Actions run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42515740272) · [archived observed figures and arrays](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42515740272/artifacts/13631128224).

This reproducible **small software-engineering prototype** extracts physically interpretable views inspired by NASA's published ExoMiner design: a 301-bin full-orbit brightness profile, 31-bin local profile, separate odd and even orbital transit shapes, 31-bin opposite-phase (secondary eclipse) profile, and a chronological **20×31 individual event** stack. Missing light-curve bins and absent event rows have **explicit occupancy masks** and are not silently treated as true flux measurements. It does not include actual TESS SPOC DV reports, official pixel difference images, centroid motion, labels, NASA normalization, neural-network weights or model inference, so it is **not ExoMiner or an ExoMiner++ compatible feature set**.

## Original observed Kepler data and numerical results

The code ran standard upstream BLS on original official **Kepler Q6 corrected PDCSAP** brightness, with existing project normalization and quality flags. NASA source FITS SHA-256s are recorded.

| Previously studied demonstration star | Frozen-source fits SHA-256 prefix | Blind Q6 fitted repetition | Usable real repeating individual event windows | Largest odd-versus-even local-bin brightness difference |
|---|---|---:|---:|---:|
| **Kepler-12**, known planet host, KIC 11804465 | `8cfcf587466e6bc2` | **4.4383043 d** | **20** | **0.0008685** normalized brightness (0.0869%) |
| **Kepler-35**, known eclipsing-binary host, KIC 9837578 | `c401d42c2939a9a` | **10.3712604 d** | **8** | **0.3326877** normalized brightness (33.27%) |

The reported maximum bin difference is an **exploratory post-hoc descriptive shape comparison**, not a noise-normalized, calibrated planet/binary significance score. It depends on the cadence, local normalization and sampling geometry. A single binary and a single known planet host do **not** prove accuracy or population separation.

### Why the comparison is useful

**Kepler-12:** the full orbital fold displays a repeated, localized dip at one phase; odd/even transit profiles nearly overlap and the opposite-phase/secondary view is essentially flat. These are physically consistent with ordinary primary transits. But a low-secondary, repeatable dip does **not independently prove a planet**, since certain grazing or diluted binaries can resemble planets.

**Kepler-35:** the BLS period of ~10.37 days is essentially **half the known stellar-binary orbital period ~20.7337 days**. At this alias, alternately observed eclipses have substantially different shapes and timings, creating extreme odd/even disagreement, even though the profile at halfway around the *incorrect* 10.37-day BLS orbital cycle is essentially flat. Thus a **secondary-eclipse-only diagnostic at the fitted half-period can miss the binary**, while a correctly constructed alternating-orbit morphology view may expose the alias. This complements the previously documented failure of our naive binary vetting on real stars.

**Most important caveat:** NASA ExoMiner already incorporates odd/even eclipse diagnostics, so this is **a successful reproduction of the physical motivation for an existing NASA feature**, not a newly invented classifier improvement or a direct ExoMiner model replication. To claim a new contribution we must test a **better alias-aware or instrument-safe measurement above and beyond this existing baseline**, across preselected previously unseen binary/planet TCEs and equal false-positive budgets.

## Reproducibility and protections

- The official FITS names and SHA-256 digests are in the original archived JSON.
- Flux views are derived from the **blind Q6 BLS period and epoch**, not the published planet or binary periods.
- The image plots are generated from the original measured source brightness; neither binary nor planet signals were artificially injected in these two plots.
- Empty 31-point bins and padded rows in the 20-event view are tracked by separate binary observation masks. In the Kepler-35 figure, all rows after its eight independently sampled events are explicitly missing (not 12 invented transit windows).
- Entire scientific regression suite **171 tests passed** in the final actual Kepler source workflow. An earlier pre-run test failed because the test deliberately removed all points within ±0.36 days, not the full ±0.40-day local view, so 0.36–0.40 day edge bins were legitimately populated. The test-only missing-window setup was corrected to ±0.41 day; **no science algorithm settings were retuned**.
- NASA source code, model weights and full canonical preprocessing were **not** downloaded or executed here.

**Consequence for the final project:** show this Kepler-12-versus-Kepler-35 contrast as a small physical explanation of why ExoMiner uses multiple diagnostic branches, then move to official TESS model inference on exact NASA tensors and paired holdout studies before any claim of improved classification or discoveries.

**AI disclosure:** GPT-6 assisted code, tests, provenance checks, plots and scientific interpretation. Student should independently verify published orbital periods, original source hashes, interpretation and course AI disclosure.
