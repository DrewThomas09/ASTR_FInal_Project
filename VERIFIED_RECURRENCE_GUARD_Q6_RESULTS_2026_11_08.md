# Verified independent Kepler Q6 recurrence-preservation safeguard: honest results
**November 8, 2026 | Final code & data verified.**

- [Prospectively frozen 13-star sample and every scientific threshold](RECURRENCE_GUARD_Q6_FROZEN_2026_11_08.json)
- [Reproducible detection code](recurrence_guard_q6.py) and [tests](tests/test_recurrence_guard_q6.py)
- [Successful full-code GitHub Actions run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42512273665)
- [Original results artifact: 13 FITS source SHA-256s, every warning and periodicity decision, fixed input manifest, chart and full execution log](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42512273665/artifacts/13629589069)
- [Original experiment method and exact limitations](RECURRENCE_GUARD_Q6_METHODS_2026_11_08.md)

## Question and what was actually changed

Can a minimal, astrophysically informed **recurrence safeguard** prevent our earlier simple local discontinuity mask from erasing repeated stellar eclipses, while retaining warnings on apparently nonrecurring brightness changes?

The **original step-warning detector and its numerical settings were not changed**. A newly added method scans only flux and timestamps from the *same star* for independently repeated recovering dips at 2.5–22 days; a warning's ±0.22-day data mask is suppressed only when at least three **other** events pass fixed local-depth and coverage rules. Published binary periods, source labels, planet identities and NASA quality flags are **not** inputs to this scan, but are permitted in scoring **afterward**.

Eight published eclipsing binaries and five named transiting-planet hosts were selected *before new source files were opened*, and earlier development example Kepler-47 is excluded. All observations are genuine MAST Kepler Q6, with both SAP_FLUX and PDCSAP_FLUX examined on the same source cadences. This is not a trained artificial neural network or new planet detection algorithm; it is a physics-inspired preservation layer developed with AI-assisted code.

## Corrected final independent results

| Source/data measure | Verified result |
|---|---:|
| Planned binary + single-host planet stars | **8 + 5 = 13** |
| Official Q6 Kepler FITS available and analyzed | **13/13** |
| Simultaneously valid positive SAP and PDCSAP cadences per star | **4,272** |
| Baseline local-step warnings in SAP | **4** |
| Baseline local-step warnings in PDCSAP | **6** |
| Total warning rows before safeguard | **10** |
| Warning rows given periodic-eclipse protection | **2/10** |
| Observed cadence-mask removals avoided (SAP + PDCSAP) | **42** |
| Quality-bit-1024 *actual archived SPSD* positive event clusters | **0** |

Counts are intentionally **method-level**. The same Kepler-34 warning times occur in both products and do not represent six independent stellar events. Also, 42 spared *photometric measurements* are not 42 known planets or distinct events, and the two protected warnings are both in purposefully selected known eclipsing binaries.

### Positive preservation case A — Kepler-1647 (KIC 5473556)

- Method: **raw SAP**. Original localized-step warning: **BKJD 568.65048011**.
- **Published stellar binary period**: about **11.2588 days** (Kostov et al. 2016 and archived DR25 binary-like KOI record).
- **Our flux-derived recurrence period, without receiving that publication**: **11.24 days**, discrepancy about **0.17%**.
- **7 other valid orbital cycles** also showed qualifying recovered short dips; **7/7 matched** at the fixed depth threshold.
- Guard restored the **21 original SAP samples** in the warning neighborhood that the baseline local-step mask would have excluded.
- Published references explicitly describe **primary and secondary stellar eclipses** with depths near 20% and 17%. The algorithm's close orbital-period recovery is strong physical *corroboration* that the protected event is related to the stellar binary, not proof of independent planet detection.

### Positive preservation case B — Kepler-35 (KIC 9837578)

- Method: **PDC-corrected PDCSAP**. One original local-step warning at **BKJD 568.13909099** was protected.
- **Published stellar binary period**: about **20.7337 days**.
- **Our flux-derived period**: **10.38 days**, a **half-period alias** (difference from half the published period about **0.125%**). A 10.38-day signal does **not** mean the circumbinary planet's orbital period is 10.38 days. The published planet period is much longer.
- **6/6 other valid trial cycles** passed the recurring-dip test.
- The guard restored **21 PDCSAP observations** otherwise removed.
- A *second* unrelated warning in the same PDCSAP series at BKJD 599.40265529 was **not protected** because the fixed local coverage/trough rules did not establish periodic recurrence.

### Important negative examples

**Kepler-34 (KIC 8572936):** There were **three original warning times on SAP and the same three on PDCSAP**, near BKJD 552.936341, 580.726539 and 608.516199. Consecutive warning separations are **27.79020 and 27.78966 days**, nearly matching the independently published **27.7958-day binary period**. **Zero** were protected. The main design reasons are clear: our frozen period range ends at 22 days, below this known binary period, and the fixed four-event support requirement can be difficult in a single ~90-day quarter. **Do not fix the search range now and reuse Kepler-34 as a fresh confirmation sample.**

**Kepler-16 (KIC 12644769):** One PDCSAP warning was not protected. Its measured local trough depth at the warning was approximately **0.065%**, below the frozen 0.25% floor; its reported binary period is also much longer than the 22-day search. The rule has real sensitivity limitations.

**Remaining nine analyzed stars without any original warnings:** Kepler-64, Kepler-413, Kepler-453, Kepler-1661, and the five planet hosts Kepler-1, -2, -3, -5 and -6. A no-warning source cannot contribute a positive or negative event-level comparison of the new safeguard.

**All 13 sources:** None had an original archived positive SPSD quality-bit-1024 marker. Thus **we still cannot measure performance on documented real instrument steps** in this independent cohort. Although the prior known positive KIC 7461601 demonstrates the old step rule, that preselected educational source is not part of this holdout and cannot serve as independent instrument-sensitivity validation.

## Engineering correction and provenance transparency

The **first** live workflow run `42512177474` compiled and completed, but its output mistakenly marked three valid binary-source analyses as errors because an engineering assertion checked the *originally removed* samples rather than the *originally retained* samples. This was an incorrect **mask-superset assertion**, not a physical detector decision. Before accepting the scientific results, we changed only this accounting assertion and added a regression test with an actually injected one-off step. The corrected complete run `42512273665` successfully analyzed **all 13 preselected stars** without any file failures; no hyperparameters, source selection or warning classification criteria were adjusted after observational outcomes. Both original and corrected workflow histories remain publicly inspectable.

The full program's own tests use synthetics to check that a repeating eclipse can qualify and an isolated step does not automatically qualify. Such unit tests **do not estimate astrophysical false alarms** or real instrument accuracy.

## Interpretation for the ASTR final paper

**Evidence now supports:** a simple physics-informed rule can preserve some original Kepler eclipse-like dips that our local instrument mask would otherwise erase, and it can recover a published stellar binary period or a near half-period alias from the real flux without being passed the literature. It also **misses clear repeating binaries outside its configured period range** and depends strongly on whether the original step screen produced a warning in the first place.

**Not supported:** a statistically established population-level increase in planet detection, a new verified planet, robust physical classification of every warning, actual survey false-alarm rate, natural SPSD sensitivity, or numerical superiority to published NASA PDC or Robnik et al. 2026.

A useful future study would use a separately selected cohort of documented genuine instrument-damage events and eclipsing binaries spanning 3–45 days, with enough observing quarters and **prospectively selected** analysis settings. The present 13 stars are now *development-exposed* and must not be reused as untouched validation for a tuned period range.

## Independent published references

- NASA MAST [Kepler Eclipsing Binary Catalog](https://archive.stsci.edu/kepler/eclipsing_binaries.html), KIC IDs, stellar binary period estimates and morphology.
- Kostov et al. (2016), [Kepler-1647b discovery, ApJ 827:86](https://doi.org/10.3847/0004-637x/827/1/86); published binary period and stellar eclipse shapes.
- Welsh et al. (2012), [Kepler-34 and Kepler-35 binary/circumbinary system discovery](https://lss.fnal.gov/archive/2012/pub/fermilab-pub-12-882-ppd.pdf) and [NASA Kepler-35 overview](https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-35).
- NASA [Kepler Data Characteristics Handbook](https://stdatu.stsci.edu/kepler/manuals/Data_Characteristics.pdf), original versus pipeline-corrected photometry and SPSD limitations.
- Robnik et al. (2026), DOI [10.1093/mnras/stag419](https://doi.org/10.1093/mnras/stag419), as a methodological comparison only.

**Disclosure:** GPT-6 generated/assisted the method, code, test suite, observational workflow, source-grounded verification and draft scientific report. The student must independently review the archived raw files, claims and model assumptions, write the actual course interpretation and disclose AI assistance.
