# Exoplanet Research Project Check In

Drew Thomas | ASTR/PHSC 12600 | Professor Buzasi

November 20 check-in | Progress through November 17, 2026

## Project and progress

My project asks whether generative AI can help reproduce an astronomy method and test its limitations. The plan in my November 5 proposal was to search NASA Kepler observations for repeating dips in starlight, then compare a small machine-learning model with a simple screening rule. Both parts are now working. The main change has been the amount of testing needed to understand what their results mean.

I read the Box Least Squares paper by Kovács, Zucker and Mazeh, along with research by Batalha and Thompson on checking possible planets. Box Least Squares, or BLS, searches for short brightness dips that repeat at a regular interval. My first artificial example repeated every 3.25 days, but the program searched only between 2.8 and 3.8 days. Finding it showed that the code worked under easy conditions. I then moved to wider searches and real telescope measurements.

After an initial download failed, I obtained Kepler files through NASA's MAST archive. The program reads the astronomy files, removes missing or flagged observations, and divides the brightness by a running median to reduce slow changes before running Astropy's BLS implementation. It uses brightness measurements already processed by NASA.

## Results and limitations

The first real-data success was Kepler-69 b. The program estimated a period of 13.713343 days from Quarter 8 observations, compared with the published 13.722368 days, a difference of 0.0658%. Tests on other systems were less successful. It recovered the intended period for three of six known planet targets. Four of six usable eclipsing binaries produced a period close to half their actual orbital period, and the simple binary warning missed all six.

Some stars also have more than one planet, so the strongest dip can belong to a different planet from the one being sought. After fitting and removing the strongest signal in Kepler-20, a second search recovered the known Kepler-20 b period. The intended Kepler-18 b signal remained unrecovered after three searches.

I then used Quarter 6 observations to predict dimmings in Quarter 7 without changing the fitted period or timing. Six of ten planned planet-host systems passed, three failed, and one lacked usable later data. Both stellar-eclipse controls passed too. This showed why predicting a repeating dip does not establish that a planet caused it.

The separate machine-learning experiment used NASA's measurements of period, duration, dip depth, and signal-to-noise ratio. Stars used for training were kept separate from those used for testing. On 1,619 held-out signals, a random forest agreed with NASA's historical candidate and false-positive labels 81.6% of the time, compared with 52.3% for a simple signal-strength rule. The forest rejected more false-positive labels but also missed more candidate labels. A more permissive rule for longer periods recovered additional candidates while accepting still more false positives. These are comparisons with earlier screening decisions, not independently confirmed planet identities. This classifier is separate from the BLS program.

A supplementary TESS experiment subtracted recorded telescope movement from measurements of the center of a star's light. A local movement measure decreased for 44 of 56 stars, but further checks did not establish better identification of the star causing a dip.

## Remaining work

The paper now explains the research process, including the early simulation, data problems, successes, and failures. It connects Lesson 2's flux measurements, Lesson 3's timekeeping, Lesson 6's orbital motion, and Appendix B's discussion of uncertainty. The remaining work is to check the numerical claims, source links, and figure captions, complete the final formatting, and provide clear instructions for reviewing the code. The final paper, completed project checklist, and supporting code will be prepared for the December 11 deadline.

Generative AI assisted with coding, debugging, analysis, and writing.

## Supporting records

[Project repository](https://github.com/DrewThomas09/ASTR_FInal_Project)

[Kepler-69 b observations](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42319839037) | [Quarter 6 to Quarter 7 test](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43512648584) | [NASA catalog comparison](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42513638366)
