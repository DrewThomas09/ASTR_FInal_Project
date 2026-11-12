# Next independent science test: externally localized nearby eclipsing binaries

**Protocol only — no results have been collected, no new stars selected, and no external-labeled sample has been run.** Frozen methodological requirements dated November 12, 2026, after the original 56-source exploratory experiments. No claim of independent verification until a fully frozen sample and source-truth artifact are created **before viewing the new TESS moment centroid outcomes**.

## Research question

Does an experimental TESS `MOM_CENTR - POS_CORR` correction preserve a transit-associated *spatial shift toward a physically independently known eclipse source* better or worse than original raw `MOM_CENTR`? Previous tests established only smaller local drift proxies and did not establish better direction concentration (23/40 increases, 17/40 decreases; star-bootstrap median CI spans zero).

This is a **different** question from whether NASA ExoMiner++ makes better planet classifications. NASA already uses original pixel/difference-image data. We must not replace its official difference-image centroid outputs with our simple moment-centroid code.

## Primary independent physical labels

Use openly documented *resolved ground-based follow-up photometry* and companion astrometry, not retrospective original NASA model scores.

- **Off-target positive:** an ExoFOP/TESS Follow-up SG1 **NEB** (nearby eclipsing binary), for which an independently measured dimming source is spatially distinct from the TESS aperture target. Store the TIC of the TESS target AND the nearby eclipsing source (or Gaia DR3 resolved companion ID), the measured angular separation and position angle or RA/Dec, follow-up epoch, time-series evidence, observer/reference URL, and exact orbital ephemeris. A generic historical label `EB`, `NTP`, `FP`, `PNEB` or unknown is **not proof of an independently confirmed nearby off-target binary**. PNEB may be placed in a separate exploratory set but not counted as confirmed NEB.
- **On-target control:** a ground-based confirmed **EB** physically localized to the observed TESS target (or a securely localized on-target transit). Record matching follow-up evidence, TIC, sector, period, ephemeris and astrometry. A historical TESS KP/CP label by itself does not prove independent on-target source localization.
- **Ambiguous:** conflicting, inaccessible, historic-only, or unresolved follow-up evidence. Preserve their count but *exclude from the truth-labeled comparison* rather than silently recoding as controls.

The difference between NEB and on-target EB is critical. Under a simple two-source blend, dimming a nearby contaminant makes a flux-weighted moment centroid move **away from** the dimming neighbor; a naive inference that the centroid shift points *toward* that neighbor has the opposite sign. In complex apertures an angular direction rule may fail entirely. NASA difference-image PRF localization is a useful separate comparator.

Source documentation:
- [ExoFOP TOI public CSV download and per-target data access](https://exofop.ipac.caltech.edu/tess/Introduction_to_ExoFOP_php_functions.php).
- [ExoFOP uploaded ground-based time-series information](https://exofop.ipac.caltech.edu/tess/view_tseries.php).
- [TFOP SG1 NEB/EB distinction](https://astrodennis.com/TFOP_SG1_Guidelines_Latest.pdf).
- [NASA TESS pixel-level DV and difference-image centroid method](https://ntrs.nasa.gov/api/citations/20180007935/downloads/20180007935.pdf).
- [STScI original TESS light-curve centroid and motion fields](https://spacetelescope.github.io/notebooks/notebooks/MAST/TESS/beginner_tour_lc_tp/beginner_tour_lc_tp.html).

## Prospective sample, without inspecting new TESS centroid outcomes

1. Take a dated, SHA256-pinned snapshot of the public ExoFOP TOI catalog, follow-up observations, companion astrometry, and supporting references. ExoFOP entries can evolve: record each source's retrieval date and evidence version.
2. Exclude all **56 previously inspected original TESS TIC host stars**, prior NASA pilot source TICs, duplicate sectors/targets, ambiguous evidence, and systems with only a generic `FP` label.
3. Require **authentic original SPOC 2-minute light curve FITS**, correct TIC and sector, sufficient observations in the source sector, and a clearly identified eclipse period/epoch. Record every screened candidate, why accepted or excluded, and missing evidence. Do not replace missing observations with fake data.
4. Select as many externally confirmed NEB and on-target sources as eligibility permits, aiming for **12 off-target and 12 on-target** but reporting actual eligible counts (including zero) rather than substituting less-verified controls. Use a fixed SHA256-sort seed `ASTR_OFFTARGET_TRUTH_20261112` with period-coverage strata if sample availability supports it.
5. Freeze the selected TIC IDs, sources, independent follow-up location and orbital ephemerides **before extracting in-event centroid vectors** from the target's TESS FITS. The sample is student-project unseen but cannot be called independent of NASA training unless specifically established.
6. For period aliases (P/2, 2P), mismatched event IDs or source sectors, resolve using follow-up ephemerides and actual TESS photometry without optimizing the outcome; count unresolvable cases as unmatched, not successes.

## Analytic target and failure safeguards

**Primary physical assessment** (NEB cases only): compare the per-star angular concordance between **the opposite of the event-induced moment-centroid displacement vector** and the independently measured target-to-eclipsing-neighbor sky direction, after converting both into a consistent local CCD coordinate basis using official TESS WCS metadata. This is a directional *surrogate* derived under a simple blend model and must be flagged if dilution/point-spread systematics invalidate it. Estimate raw and experimental pointing-adjusted concordance on **identical** independently timed source events.

**Important:** no in-event shift is a reliable location estimator simply because its magnitude is large. For low-amplitude or insufficiently measured shifts, mark direction **not evaluable** using a fixed pre-data observational quality criterion rather than arbitrary post-hoc angular values. Ground-truth source position must come from follow-up/Gaia, not from the TESS centroid result being evaluated.

**Independent reference**: NASA official DV difference-image centroid source localization when available, recorded separately with uncertainty/significance. Do not call our simpler moment-centroid sidecar a replacement.

**Secondary outcome**: compare the original simple local pre/post stability proxy on these new sources. Report whether the direction changes trade off against drift reduction, rather than pooling metrics into a single cherry-picked "score."

**Numerator and denominator**: report attempted candidates, excluded due to evidence, valid NEB, valid on-target, source FITS coverage, period-matched, event-valid, and direction-evaluable. Repeated events and sectors of the same TIC are clustered at the **host/source level**, not counted as independent stars. Use a paired whole-host bootstrap for uncertainty and a prespecified paired sign/permutation analysis where appropriate; report power limits and avoid mission-level performance claims.

**Pre-analysis safety gate**: model score and "success" are **not used** to select sources or choose directional thresholds. Preserve physical failure cases (mask crowding, saturation, proper-motion astrometry, inverted event signs, missing WCS, orbital aliases, finite observation gaps). Additional exploratory corrections must be clearly dated **after** this primary analysis.

## What will and will not count as a result

- A **positive descriptive result** requires genuine independent source truth + authentic same-event TESS data + verified WCS direction + prespecified star-paired analysis. Even that would establish an auxiliary localization proxy association only, not higher ExoMiner++ accuracy.
- A **negative or inconclusive result** (too few NEBs, off-target direction close to zero, worse alignment after subtraction) remains a valid scientific outcome.
- A claim of **better ExoMiner++ exoplanet discrimination** requires a separate, genuinely independent NASA model evaluation at fixed operating point and sufficiently powered on-target/off-target truth labels. This protocol is **not** that evaluation.

## Immediate work before execution

The original 56-star signed-vector study has been completed and shown **no reliable directional concentration improvement**. The immediate uncompleted step here is to acquire, validate, pin and independently review the external ground-based truth-evidence dataset. No synthetic proxy or 2025 historical class can fill this role.

**AI-use disclosure:** GPT-6 assisted with the literature comparison, source schema and design of this proposed pre-data protocol. The student must audit the follow-up references and final eligibility sample before running or presenting a truth-labeled experiment.
