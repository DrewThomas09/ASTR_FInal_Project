# Verified Q6 NASA instrument-label follow-up: a negative observational result
**November 8, 2026 | Experimental status: completed and independently archived.**

- [Frozen 12-star manifest](REAL_SPSD_EXTERNAL_COHORT_FROZEN_2026_11_08.json) committed before the first run of the new observations.
- [Successful official GitHub Actions test and NASA study](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42510882421): **96 software regression tests passed**.
- [Unmodified original source-data artifact](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42510882421/artifacts/13629890365) contains all target records, original FITS SHA-256 hashes, archived marker rows, warning timestamps, plot, and raw log.
- [Scientific design](REAL_SPSD_EXTERNAL_COHORT_METHODS.md), [analyzing script](real_spsd_external_cohort.py), [11 new tests](tests/test_real_spsd_external_cohort.py).

## What we actually tried

The previous experiment's simple negative-step heuristic detected one **preidentified** genuine Kepler instrumental discontinuity in original SAP brightness but not in corrected PDCSAP on the documented KIC 7461601 Quarter 6 example. That star was intentionally removed from this follow-up. We selected twelve fixed *other* KIC sources and attempted official MAST Kepler Quarter 6 FITS. On each accessible star we applied the **same unchanged detector** to the identical timestamps of original `SAP_FLUX` and NASA-corrected `PDCSAP_FLUX`. Only *after* finding candidate steps did the analysis read the official `SAP_QUALITY` bit-1024 labels for sudden pixel sensitivity dropout events. No detector threshold was tuned on this cohort and no failed target was replaced.

This is an instrument-data check, **not** an exoplanet classification experiment and **not** a randomized sample of Kepler stars. Original quality-flagged cadences were retained to make possible defects observable, unlike earlier planet-search experiments which removed flagged samples.

## Verified observed data

| Quantity | Result |
|---|---:|
| Planned unique Kepler stars | 12 |
| Successfully analyzed official Q6 star files | **10** |
| Planned files unavailable | **2** |
| Paired valid timestamps per usable star | 4,272 |
| Total usable paired brightness measurements | 42,720 |
| Original archived bit-1024 SPSD event clusters | **0** |
| Step warnings in original SAP | 6 |
| Step warnings in corrected PDCSAP | 7 |
| Total method-level warning rows | **13** |

The two unavailable targets were KIC **3248033** and **4852528**. On the fixed official filename/Quarter 6 requests, MAST returned HTTP 404 and the archive mirror returned HTTP 403. **The planned denominator remains 12**, not 10. The 10 analyzed sources each had 126 joint-invalid FITS rows excluded for the joint positive/finite-flux comparison; nonzero-quality flags were *not* excluded merely because they were flagged.

**Critical scientific conclusion:** **ZERO** of the ten usable source files contained an archival SPSD bit-1024 event after joint-valid filtering, and the archived original-row count was also zero. Therefore the main targeted outcome — sensitivity at genuine archived instrumental steps — is **not estimable** on this cohort. It would be misleading to call zero matched defects evidence that either detector fails. Nor can we divide the seven PDCSAP warnings or six SAP warnings by archived label counts to claim a false-positive rate, since the label set is not a complete ground truth for instrumental, astrophysical, or timing anomalies.

## A physical problem our code exposed

The 13 warning rows were concentrated in two stars:

- **Kepler-9 host (KIC 3323887):** one SAP warning (at BKJD 567.8946343), no PDCSAP warning.
- **Kepler-47 host (KIC 10020423):** five SAP warnings and seven PDCSAP warnings. The SAP five are a subset of the seven PDCSAP warning epochs. Together these represent **seven distinct times**, not 12 distinct physical events. The remaining eight usable stars had no warnings in either product.

Because Kepler-47 is a **known eclipsing binary star system**, these warnings motivated a separately labeled **post-hoc** physical timing check against its published primary and secondary eclipses. That analysis must not be added to the frozen instrument-detection success rate, and it does not establish that the warnings are false positives. See [Kepler-47 follow-up](VERIFIED_KEPLER47_ECLIPSE_CHECK_2026_11_08.md).

## Interpretation for the final project

This experiment is valuable **because it was allowed to fail to answer the primary question**. The predetermined sources supplied no positive archival event labels. It demonstrates the distinction between a reliable reproducible program and a scientifically informative test sample; an algorithm cannot be validated at a target event if no target events are actually present.

The result also illustrates a physical ambiguity: steep brightness declines in Kepler time series can arise from an **instrumental defect** or a **genuine astrophysical eclipse**, and an algorithm that checks only local step shape does not necessarily know which happened. The next method should distinguish coherent orbital recurrence from a one-off instrument change and should be evaluated on a *new*, independent set of actual labeled events and binary systems before any performance claim.

**Do not characterize this as a new planet discovery, a measured increase in detector sensitivity, or a representative estimate of Kepler instrumental-error statistics.**

## Provenance, cited sources, and AI use

- NASA/STScI, [Kepler instrumental electronic-noise tutorial](https://spacetelescope.github.io/mast_notebooks/notebooks/Kepler/instrumental_noise_4_electronic_noise/instrumental_noise_4_electronic_noise.html), for bit-1024 event context.
- STScI, [Kepler Archive Manual](https://archive.stsci.edu/kepler/manuals/KDMC-10008-005-Archive_Manual.pdf), quality-bit definitions.
- Official MAST public FITS checksums, source URLs and per-target failures are in `all_planned_targets.csv` in the saved [original experiment artifact](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42510882421/artifacts/13629890365).
- GPT-6 assisted protocol, code, tests, checks and this prose. The student remains responsible for independently examining archived FITS, verifying paper claims, interpreting science, and disclosing AI support under the ASTR/PHSC 12600 course policy.
