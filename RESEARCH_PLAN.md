# Study design and milestones

## One research question, two parts

Can AI-assisted programming replicate a standard transit search, and does a lightweight random-forest screening step reduce false positives relative to screening on signal-to-noise alone?

**Part A: transit search** (established BLS, not ML). Inject a 3.25-day transit into simulated noisy observations and recover it, then vary transit depth (e.g. 4,000 / 1,500 / 500 parts per million) while holding the same noise realization fixed. Run noise-only controls. Report period error and the rate at which the algorithm recovers the injected period. A peak on noise alone is not a discovery.

**Part B: candidate vetting** (genuine ML). Work with NASA Kepler Q1-Q17 DR25 table `q1_q17_dr25_koi`, label `koi_pdisposition`, features `koi_period`, `koi_duration`, `koi_depth`, `koi_model_snr`. Using the same Kepler star never cross train, validation and test groups (group by `kepid`). Train one random forest. For each method, select a cutoff achieving at least 90% candidate recall on **validation** data; then report held-out recall, false-positive rate and screening fraction. A lower screening fraction only counts as an improvement if test recall stays acceptably close.

The candidate-vetting labels reflect the historical automated NASA Robovetter, not independently confirmed planets. Candidate classification is a different stage from searching raw photometry for dips. Treat the work as an educational baseline comparison, not a new astrophysical discovery.

## Minimum deliverables

1. Runnable code and explicit AI-contribution log.
2. From simulation: period recovery, noise-only control and depth sensitivity figure.
3. From the NASA catalog: comparison CSV, screening fraction figure and confusion matrix, only if the real download succeeds.
4. An accompanying report explaining transit depth (~ planet radius squared / star radius squared), Kepler's third law, sources of false positives, and methodological limitations.
5. Class checklist linking at least two lectures: time/period measurement and Newtonian gravitation/Kepler laws. Optionally light and measurement uncertainty.

## Schedule

- **November 6:** proposal. Code skeleton and simulation are ready; ML screening code is generated, but real NASA analysis is still pending.
- **Before November 20:** load real DR25 CSV, run split and training, inspect results and produce project status report. If download fails, retain simulation and record blocker explicitly.
- **December 11:** final project, figures, code documentation, research interpretation, citations, and checklist.

## Quick fallback / time control

If the NASA download fails: use NASA's browser CSV export and re-run the existing script. If real Kepler-69 photometry download fails: skip that optional demonstration. Do not add neural networks, a dashboard, or a new-planet search to the core deliverable. The project remains a valid *replication plus one measured extension* if it clearly distinguishes simulated from real evidence.