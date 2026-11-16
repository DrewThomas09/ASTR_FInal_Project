# ASTR 12600: polished final research paper, Version 15

**November 15, 2026 | Drew Thomas | Original November 5 proposal retained**

## Delivered research-paper format

The formatted Word and PDF research paper provided in the current project conversation is **7 pages** and contains **2,615 main-body words**, **excluding the 160-word abstract**, figure captions, references and the required project checklist. The course asks for at least 2,500 words. The paper retains **four numbered, source-backed figures**, ten bibliography entries and the completed professor-provided checklist.

The paper was rendered from Word and every final page inspected. All four figures appear with their corresponding caption on the same page: **Figure 1 (page 3)** original Kepler-69 b light curve, **Figure 2 (page 4)** frozen Quarter 6-to-7 time-separated prediction checks, **Figure 3 (page 5)** historical NASA DR25 model comparison, **Figure 4 (page 6)** exploratory eight-model feature ablation. All references and the completed checklist fit on page 7 with no spillover page.

## Editorial and scientific improvements

1. **Reliable count:** body text now has 2,615 words *without* counting the abstract.
2. **Better measurement reasoning:** the difference between the fitted and published Kepler-69 b periods is 0.009025 day per orbit, about 13 minutes; an illustrative five-cycle forecast would separate by about 65 minutes. This is **not** a formal BLS uncertainty or an observed timing residual.
3. **Clearer feature-ablation interpretation:** the full forest's historical-label balanced accuracy was 81.29%, while removing catalog orbital period reduced it to 71.33%. The text explains that transit opportunity count scales roughly as T/P over a fixed observing window, while recognizing that the full DR25 catalog spans multiple years and that features are correlated. This is an exploratory feature-omission result, not a causal proof.
4. **Rebuilt Figure 2:** instead of tiny logarithmic plots, the new print-size figure lists each of eleven usable systems with its count of positive Quarter 7 event windows, empirical alternative-phase fraction, and original PASS/FAIL outcome. It explicitly flags Kepler-35 and Kepler-47 as stellar eclipse controls and Kepler-17 as unavailable.
5. **Tighter conclusion:** identifies the distinct tasks of detecting dimming, predicting repeatability and physically identifying the source, with the smaller negative TESS result remaining separate.
6. **Reproducibility:** an added *Data and code availability* section names public NASA archives, the repository, exact scripts and original successful workflow run IDs.

## Original data and reproducible code

- **Original Kepler-69 b photometry and BLS:** [original real-data run 42319839037](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42319839037) and [real_kepler_lightcurve.py](real_kepler_lightcurve.py)
- **Frozen Q6 to independent Q7 prediction:** [original successful run 43512648584](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43512648584), [protocol](Q6_TO_Q7_BLIND_PREDICTIVE_VALIDATION_FROZEN_2026_11_08.json), [q6_to_q7_blind_ephemeris_validation.py](q6_to_q7_blind_ephemeris_validation.py)
- **Original NASA DR25 host-separated classification:** [held-out predictions run 42513638366](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42513638366), [ml_screening.py](ml_screening.py)
- **Eight-feature-combination exploratory forests:** [successful run 43776316541](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43776316541), [v13_kepler_feature_ablation.py](v13_kepler_feature_ablation.py), and [frozen configuration](V13_FEATURE_ABLATION_PROTOCOL_FROZEN_2026_11_15.json)
- **Research articles and lecture topics:** [source and class map](PROPOSAL_TO_RESULTS_RESEARCH_AND_CLASS_LINKS.md)

This note records the finished paper's edits and validations. The actual 7-page DOCX/PDF files are downloadable directly from the conversation; the longer original technical analyses and experimental results remain in the GitHub repository. The original DR25 screening predictions are agreement with NASA's earlier vetting labels, **not** a list of confirmed planets. The Kepler BLS detector and catalog classifier remain separate experiments, as promised in the submitted proposal.
