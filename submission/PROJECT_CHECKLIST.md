# Project Elements Checklist Form

Drew Thomas | ASTR/PHSC 12600

Testing AI in Exoplanet Research

## Synthesis of Lecture Material

| Lecture Number/Topic | Concepts included in the Project | Location in the Project/Essay/Write-Up |
|---|---|---|
| Lesson 2 — Luminosity and flux | The difference between a star's emitted light and the light received at a telescope. Transit dips and the effect of nearby stars on measured brightness. | Sections 1, 2, and 5 |
| Lesson 3 — Time | Repeating events as a way to measure time. Predicting future transits and explaining how a small period error accumulates. | Sections 1 and 3 |
| Lesson 6 — Kepler's laws and Newtonian gravity (Optional Bonus) | Orbital periods and their connection to gravity. Why both planets and eclipsing stars can produce regular dimmings. | Sections 1, 2, and 3 |

## Quantitative analysis

### Briefly describe the quantitative analysis component of your project

I measured Kepler-69 b's period, compared it with the published value, and tested later transit predictions using fits from one and three quarters. I repeated the comparison on six other named planets and seven binary systems, retaining unsuccessful and unavailable cases. I compared a random forest with a signal-strength rule on 1,619 held-out NASA records. I also tested motion correction on 56 TESS stars and used 2,000 simulated events to compare source identification under twelve noise conditions.

### Where is the quantitative component(s) found, within your project, essay, and/or write-up?

Section 2 gives the recovered Kepler-69 b period and the tests on other systems. Section 3 contains the timing calculations, later-quarter predictions, and comparisons of fits using one and three quarters. Section 4 reports classification accuracy, candidate recall, and false-positive rates. Section 5 reports the real TESS motion comparison and the separately identified simulation. The supporting GitHub repository provides the code, experimental protocols, and recorded results.
