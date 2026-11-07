# Independent external Kepler cohort — 13 targets, negative result
ASTR 12600 · November 6, 2026 (workflow completed November 7 UTC)

**Verified successful external test:** https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42321227884
**Saved source CSV, frozen manifest, logs, plot:** https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42321227884/artifacts/13552807831

## Why this study matters

The previous real-world case study classified one obvious eclipsing binary as requiring review and did not flag one known planet. It was tempting to conclude that the physical vetting algorithm worked well on real stars. This new **prospectively frozen** set, selected from independent publications rather than our own model outcomes, shows why two convenient examples were not enough.

The list of **13 real target stars**, literature references, known orbital periods, uniform Q8 policy, and BLS search interval were committed in `real_external_cohort_frozen.json` *before* this run. The previous example stars (KIC 8692861 and KIC 10661783) were excluded. No warning thresholds were changed during the run.

Targets were selected purposively using NASA confirmed-planet records and published eclipsing-binary work, *not* randomly from the full population. For reasons including availability, observing cadence and sample construction, these observations cannot yield a mission-wide false-alarm or completeness estimate.

## Observations

All objects used the same **Kepler Q8 PDCSAP long-cadence data policy**, `SAP_QUALITY==0`, 301-cadence median detrending, and Astropy BLS search range **0.9–15 days**. FITS downloads were attempted using the official NASA MAST URI endpoint. Each successfully downloaded original source FITS has its SHA-256 recorded in `all_attempted_targets.csv`.

**13 predeclared targets: 6 confirmed planets, 7 published eclipsing binaries.**
**12 analyzed successfully; 1 unavailable at the chosen Q8 cadence (KIC 2305543).**

### Individual result table (read from saved output, not estimated)

| Target | Previously known class | Reference period, d | BLS period, d | Comparison | Binary warning |
|---|---|---:|---:|---|---|
| Kepler-18 b | Confirmed planet | 3.504725 | 7.641800 | Unmatched to *b* | No |
| Kepler-19 b | Confirmed planet | 9.286964 | 9.285008 | Exact within 2% | No |
| Kepler-20 b | Confirmed planet | 3.696115 | 10.852375 | Unmatched to *b* | No |
| Kepler-21 b | Confirmed planet | 2.785821 | 13.114060 | Unmatched | No |
| Kepler-68 b | Confirmed planet | 5.398753 | 5.400550 | Exact within 2% | No |
| Kepler-93 b | Confirmed planet | 4.726740 | 4.726541 | Exact within 2% | No |
| KIC 1026032 | Published EB | 8.460438 | 8.457206 | Exact within 2% | **No** |
| KIC 2305543 | Published EB | 1.3622735 | N/A | Q8 input unavailable | N/A |
| KIC 2306740 | Published EB | 10.306987 | 5.151749 | **Half-period alias** | No |
| KIC 3248019 | Published EB | 2.668222 | 1.334391 | **Half-period alias** | No |
| KIC 3654950 | Published EB | 8.134725 | 4.066865 | **Half-period alias** | No |
| KIC 4544587 | Published EB | 2.189094 | 2.189323 | Exact within 2% | **No** |
| KIC 9851944 | Published EB | 2.163902 | 1.082176 | **Half-period alias** | No |

### What these counts mean

| Scientific denominator | Verified outcome |
|---|---|
| Planet targets with available data | **6/6** |
| Planet targets where intended listed planet period was recovered | **3/6** |
| Known planet exact-period matches given a false binary warning | **0/3** |
| Binary targets with data | **6/7 planned** |
| Binary targets with exact orbital-period recovery | **2/6** |
| Binary targets with near-half-period alias | **4/6** |
| Binary warnings on the 2 exact-fit binaries | **0/2** |
| Binary warnings on all 6 analyzable binaries | **0/6** |

The last item must not be called a sensitivity estimate: it includes wrong-period cases, and this is a nonrandom, tiny convenience sample. But it reveals that the physical warning **failed to flag any binary in this independent cohort**. Its earlier success on the exceptionally clear KIC 10661783 was not representative of these harder examples.

## Scientific realizations

### 1. The majority of binaries can produce half-period aliases in this narrow observational experiment

Four of six successfully analyzed binaries produced BLS periods ~half the literature orbital period. At half the orbit, primary and secondary stellar eclipses may fold onto the same apparent transit phase. Our current secondary-eclipse test then examines the wrong phase and can entirely miss the binary nature. An odd/even warning does not automatically resolve this; noise, pulsation, uneven sampling and similar eclipse depths can defeat the threshold.

**Important restraint:** This is 4/6 in *our selected sample*, not evidence that a majority of all Kepler binaries behave this way.

### 2. Exact period recovery does not imply physical reliability

KIC 1026032 and KIC 4544587 had correctly fitted periods under the 2% rule, but neither triggered our binary warning. Some binaries have weak, overlapping or complicated secondary eclipses. This undermines any assertion that *adding one secondary-eclipse rule solves false positives*. We need independent diagnostics and more diverse data.

### 3. The strongest transit in a multi-planet star might not be the intended planet

Kepler-18 b's run selected a **7.6418-day period**; the previously confirmed **Kepler-18 c** has an approximately 7.6416-day period. Kepler-20 b's run selected **10.8524 days**, very close to the approximately 10.8541-day Kepler-20 c. These are therefore probably cases where BLS selected a *different previously confirmed planet around the same star*, rather than simply failing to find any planetary signal.

Primary references:
- Kepler-18 c: https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-18
- Kepler-20 c: https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-20
- NASA Kepler EB catalog: https://archive.stsci.edu/kepler/eclipsing_binaries.html

Kepler-21 b's unmatched 13.114-day signal is **not** attributable to another planet or physical noise source without further analysis; do not guess its identity.

### 4. What a rigorous fix would require

**Separate tasks, separate validation:**
- **Multi-planet:** implement iterative BLS to model and subtract the strongest fitted signal, searching residual light curves for a weaker planet. This is not novel in astronomy. Development examples are Kepler-18 and Kepler-20, followed by a **new untouched** set.
- **Eclipsing binaries:** test physically motivated half-period / double-period alternatives and explicitly compare alternating eclipse depths, but never flag solely because 2P produces another eclipse (because true planets also recur each orbit). More complex binaries may require pixel centroid, astrophysical model fits and spectroscopy.
- **Statistical validity:** no threshold adjustment on this cohort can count as new independent evidence. Reuse it **only for development and error analysis**, then reserve a separate dataset for a fresh final comparison.

## Summary for final report

**Key conclusion:** We initially reproduced the known Kepler-69b transit, found a simple candidate-classification advantage over signal-to-noise on historical DR25 labels, and then demonstrated that generic model disagreement added virtually no independent benefit. Physical secondary-eclipse screening looked excellent on one simple binary but **failed on an independently chosen external cohort**. A main challenge is period aliasing, combined with the information loss of single-strongest-period searches.

This negative result is scientifically useful because it demonstrates **why automated astronomical classification requires rigorous external validation** and why AI-assisted code that performs well on demonstration examples is not by itself trustworthy research software.

## Sources, code and integrity

`real_external_cohort_frozen.json`, `real_external_cohort.py`, `binary_eclipse_diagnostics.py`, workflow and full artifact are included above. This code and draft were developed with generative AI; the student must independently verify scientific interpretations and report the limitations and AI role.
