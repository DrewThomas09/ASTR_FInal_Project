# November 12, 2026: an additional limitation of our TESS centroid warning

**New scientific finding:** The ability to evaluate a source with our original source-centroid warning is strongly affected by its fitted orbital period and by how many complete, original TESS observing windows it provides. This is an **exploratory, post-hoc analysis** of the already archived original NASA v2.4.0 / TESS SPOC run results, not a new independent NASA model-validation dataset and not a proposed gain in its classifier.

## Source-original results and reproducibility

The two original-source experiment runs were:
- [32 previously inspected development stars, original NASA model and real TESS moment-centroid measurements](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42526063290): 23/32 source stars had at least 3 complete original events; 9/32 were not evaluable under the pre-existing warning.
- [24 additional, student-development-disjoint stars, genuine NASA model and original TESS moment-centroid measurements](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42526495887): 17/24 had at least 3 complete original events; 7/24 were not evaluable.
- The authentic TESS source measurements and fixed eligibility criterion predate this follow-up. We made no new stellar selections or modifications to ExoMiner original scores, event cadences, thresholds or pretrained weights.

Across **56 distinct original sources**, **40** were evaluable and **16** lacked sufficient complete, quality-zero, source-centroid event windows. None of those 16 should be counted as successful nonflags or proof of safe transit-source attribution.

The 24 additional stars were **six each** original historical KP, CP, EB and NTP labels. The three-event minimum produced:

| Historical label | Frozen sources | Evaluable | Missing |
|---|---:|---:|---:|
| KP (known planets) | 6 | 5 | 1 |
| CP (candidate planets) | 6 | 5 | 1 |
| EB (eclipsing binaries) | 6 | 6 | 0 |
| NTP (nontransiting phenomena) | 6 | 1 | 5 |

Original NASA v2.4.0 current fitted orbital period had a strong association with the **original actual complete event count** in the 24-source group: **Spearman rho −0.895319**; 10,000-star-bootstrap 95% interval **[−0.960566, −0.720541]**; 100,000-permutation plus-one two-sided Monte Carlo p **0.0000099999** with zero permutations at least as extreme. The association remains **rho −0.902536** when excluding the two old/new half/double-period aliases, leaving **22** period-consistent sources. With only **6 EB** and **6 NTP**, the exploratory two-sided Fisher exact p for eligible versus not eligible was **0.01515**. This class comparison was chosen **after** inspecting the original sample; it is not preregistered.

The explanation is mainly physical and observational: finite TESS sectors offer fewer repeated observed transits for long periods, and the historical NTP sources in this selected sample tended to have longer fitted periods. This makes the diagnostic's three-event eligibility **differential missingness**, not random sample loss. It is not a statement that NTP objects inherently have smaller centroid displacements.

## A second limitation: no room for a new corrected false positive

On these particular 24 previously frozen sources, the unchanged NASA original model score at 0.5 already agreed with **all 24** older published binary categories (12 KP/CP scores ≥.5; 12 EB/NTP scores <.5). This is **not** independent 100% planet detection accuracy: sources were deliberately selected, historical labels are not independent physical truth, and NASA's model may have encountered the stars in training. It does imply that under these older labels the additional centroid veto could not improve the number of NASA-accepted historical EB/NTP cases, because this particular comparison contained **zero such cases to correct**.

The full experiment is in [`tess_source_eligibility_period_bias_nov12.py`](tess_source_eligibility_period_bias_nov12.py), with its [GitHub Actions source-original-data reproduction](.github/workflows/tess-56star-eligibility-period-bias-nov12.yml). The completed, one-off student submission paper also includes a supplementary Figure 7 and a candid paragraph on the event-selection bias.

**The bottom-line result remains:** The earlier centroid review did not demonstrate an incremental benefit beyond original NASA ExoMiner++ v2.4.0. This new audit makes our evaluation limits clearer and reinforces the importance of **event identity, telescope observation coverage and statistical denominator accounting** before comparing scientific models. No neural improvement, newly discovered planet or independently verified mission classification rate is claimed.

**AI assistance disclosure:** GPT-6 assisted code, input audits, statistical tests, plotting, and drafting. Student interpretation and course submission remain the student's responsibility.
