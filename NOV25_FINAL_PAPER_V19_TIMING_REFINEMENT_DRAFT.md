# Testing AI's Impact in Exoplanet Research

**Drew Thomas | ASTR/PHSC 12600 | Professor Buzasi | Working Version 19, November 25, 2026**

## Introduction: what I wanted to find out

Artificial intelligence can write computer code, explain equations, and work through large amounts of data. That makes it sound like a useful tool for scientific research. I wanted to find out what that claim means in practice. Could I use AI to rebuild a real astronomy technique, test it on actual measurements, and understand why it sometimes failed?

I chose the search for exoplanets, meaning planets that orbit stars other than our Sun. Most of these planets are much too far away for us to photograph directly. Instead, astronomers often look for tiny changes in a star's brightness. This interested me because it brings together several ideas from our class: measuring light, keeping accurate time, and using the motion of planets to understand what we observe.

My original proposal had two main parts. I would use generative AI to help write a program that searches for planet-like signals in NASA Kepler data. I would then build a relatively simple machine-learning model and compare it against a basic screening rule. As the work developed, I added two smaller questions. Could a period found in older telescope measurements predict future transits? And could subtracting telescope movement make another type of measurement more useful?

I was not trying to invent a completely new way of finding planets. Professional astronomy already has much stronger methods than the ones I could reasonably rebuild for this class. Instead, I wanted to see what AI made possible for someone learning the subject, and whether the results held up when I checked them carefully. The failures turned out to be just as useful as the successes.

## 1. How astronomers find planets by measuring light

The basic idea behind a transit search is fairly simple. Imagine watching a star and measuring how bright it looks every few minutes. If a planet passes between the star and the telescope, the planet blocks a tiny part of the starlight. On a graph, the brightness briefly drops and then returns to normal. Astronomers call this event a *transit*, and the graph is a *light curve*.

If the dips keep happening at regular intervals, they may be caused by an orbiting planet. The time between those dips is the planet's *orbital period*. For example, if a dip repeats every fourteen days, the object may be completing one orbit roughly every fourteen days. Kepler's third law then connects the period with the size of an orbit, provided we know the mass of the star [1].

But there is a catch. Not every dip is a planet. Two stars can eclipse one another, an instrument can briefly behave strangely, and light from a nearby star can mix with the light we are trying to measure. A program can be very good at finding a repeating pattern and still be wrong about what caused it. That difference between **finding a signal** and **explaining a signal** became the main theme of my research.

Before writing the program, I read the 2002 paper by Kovács, Zucker, and Mazeh on an established technique called *Box Least Squares*, or BLS [2]. Instead of looking for smooth waves, BLS looks for short, repeated drops in brightness. I also read work on how the Kepler team checked possible planets, including comparisons of different eclipses and tests for nearby stars [3, 4]. McCauliff and colleagues showed how machine learning could combine several measurements for screening [5], and the later ExoMiner research made clear how many different checks a professional system can use [6].

Those papers changed my expectations. I had originally thought it might be realistic to make a big improvement to planet detection. After seeing how much work had already gone into these systems, I decided that a smaller, carefully tested change would be more useful than claiming to have built a better NASA detector.

## 2. Building the first program

I used generative AI to help write and debug Python code that runs BLS through the Astropy astronomy library [7]. The program tries different periods and asks which one best lines up with repeated dips in a star's brightness. The best-fitting period is its answer. AI helped me implement the steps, but the underlying astronomy method is established research, not something the AI invented.

My first successful example was actually too easy. I created an artificial dip that repeated every 3.25 days and only allowed the program to search from 2.8 to 3.8 days. It found the correct answer, but I had already given it a very narrow range. This told me the code could run, not that it would perform well on real astronomy data.

The next problem was getting real data. My first attempt to download Kepler files directly returned an access error. I changed the program to use NASA's official MAST archive route, then learned how to read the FITS files that astronomers use [8]. These files contain the times of the measurements, the star's measured brightness, and flags showing when an observation may have a problem.

I kept only observations without those quality flags and removed slow changes in brightness using a fixed running-median calculation. This made short dips easier to see, although it also means the processing could change the appearance of some real events. Importantly, I used NASA's already-processed Kepler brightness data. I did not recreate the raw telescope pixels or NASA's entire processing system.

### A known planet gave the first real result

I tested the program on Kepler-69 b, a planet NASA had already identified. Using 2,767 usable measurements from Kepler Quarter 8, the program estimated a period of **13.713343 days**. NASA's published period is **13.722368 days** [9]. The difference was only **0.0658%**.

That result mattered because the program had recovered nearly the correct period from genuine measurements, not from an artificial example. Still, I had chosen a star with a known planet, so this was a check of whether my reconstruction worked. It was not the discovery of a new planet.

I also tried placing artificial transits into real Kepler stellar noise. The program found the correct period in one of three tests with shallow, 500-parts-per-million dips, but in all three tests at each of the two larger depths of 1,500 and 4,000 parts per million. That suggested a straightforward problem: weak signals are harder to find. The sample was far too small to claim a general detection rate, but it helped me see why the strength of a signal matters.

The next test was less encouraging. I ran the same general search on a preselected group of other known Kepler systems. It recovered the intended planet's period for only **three of six** planet-host targets. In several systems with two eclipsing stars, the program reported a period close to **half** the stars' real orbital period. A simple warning I had added for binary stars missed those cases. The lesson was that doing well on one familiar planet did not mean the program was ready to analyze unfamiliar stars.

I also noticed a different problem with systems containing more than one planet. The program usually reported the strongest dip first, which was not always the particular planet I wanted it to find. I experimented with removing the first fitted signal and searching the remaining data. On Kepler-20, a second search recovered the already-known period of Kepler-20 b after finding Kepler-20 c. It still failed to recover the intended Kepler-18 b signal after three searches. This was helpful for development, but it was not a new discovery or a fair test of a brand-new method. Kepler researchers had already used repeated searches to find additional planets [4].

## 3. Could a period found in old data predict later dips?

By this point I had learned that matching a known period was not the same as making a useful prediction. So I changed the test. Instead of letting the program fit the same data again and again, I asked it to use older observations to predict dips in later observations.

In one experiment I used Kepler Quarter 6 to calculate the period and timing, then checked Quarter 7 without adjusting the prediction. Six of ten planned known planet-host stars passed the fixed test, three failed, and one did not have usable later data. Both of the two stellar-binary controls also passed. This was an important warning. A repeating dip may be predictable even when it comes from one star eclipsing another, rather than a planet.

The most useful new experiment came from returning to Kepler-69 b. Our Quarter 8 period was only 0.0658% away from NASA's value, which sounded extremely close. But that small difference equals about **13 minutes each orbit**. If you use the wrong period over and over, the mistake grows. After thirty orbits, it can add up to about **6.5 hours**.

I decided to see what would happen if I kept my Quarter 8 answer completely fixed and used it to predict the times of dips in later Kepler data. The first follow-up test on Quarter 9 was set before I opened its brightness measurements. After seeing that result, I separately set the next tests for Quarters 10 and 11, and later for Quarters 12 and 13. In each case, I kept the same original period, starting time, and dip duration. I did not move the predicted windows after seeing the later data.

The results tell a clear story. In Quarter 9, **all seven** well-observed predicted windows showed a dip. In Quarter 10, it was **six out of six**. In Quarter 11, it was **five out of six usable windows**; two other predicted times did not have enough nearby measurements to check properly. But by Quarter 12 and Quarter 13, **none of the six usable windows in either quarter** showed the expected dip. All of those failures are included in the results rather than removed.

| Kepler data | Dips at the times predicted by our Quarter 8 program | Mean brightness dip in those windows |
|---|---:|---:|
| Quarter 9 | 7 of 7 | 493 ppm |
| Quarter 10 | 6 of 6 | 138 ppm |
| Quarter 11 | 5 of 6 usable | 89 ppm |
| Quarter 12 | 0 of 6 | -112 ppm |
| Quarter 13 | 0 of 6 | -97 ppm |

The smaller numbers in later quarters were not evidence that the planet was getting smaller. The program was checking the wrong times. A negative average dip here just means that the star was not dimmer in those particular windows. It does not mean the planet made the star brighter.

I then did a separate follow-up to understand the failure. After seeing the results, I kept the same starting transit time but replaced my estimated period with NASA's more accurate, published period. With that period, **all six** usable windows in Quarter 12 and **all six** in Quarter 13 showed dips again. The average dips were about 513 and 558 parts per million. That strongly supports the idea that my original period was slowly drifting out of step with the real transits.

This last comparison was done *after* the original predictions failed. I knew NASA's published value already, so it would not be fair to count that as a second blind success. Its purpose was to explain the failure. The results are archived with the original NASA file identifiers and the computer code [10].

### Improving the prediction rather than just explaining the failure

The next question was whether we could correct the problem without giving the program NASA's published answer. In an AI-assisted continuation of the experiment, the same BLS search was applied to the brightness measurements from Quarters 8, 9 and 10 together. The original Quarter 8 fit had used 2,767 measurements spanning approximately 67 days. The combined fit used 11,172 measurements spanning 265 days. The longer observing interval meant that even a small mistake in the period would cause dips far apart in time to fall out of alignment.

The new estimated period was 13.722233693 days. Compared with NASA's 13.7223682-day value, the original error of 0.06577% fell to 0.00098%. Instead of accumulating around 13 minutes of error per orbit, the new period differs from the catalog value by about 11.6 seconds per orbit. These comparisons measure disagreement with the reference rather than the uncertainty of either period.

To test whether this mattered in practice, both fits were frozen and applied to later quarters using the same 0.153-day transit window. Quarters 12 and 13 were already familiar from the previous experiment, so they were treated as development comparisons rather than independent tests. Quarters 14 through 17 had not previously been evaluated in this project. The results were as follows [15].

| Evaluation quarter | Positive dips, Q8-only fit | Positive dips, Q8–Q10 fit |
|---|---:|---:|
| Q12 (previously examined) | 0/6 | 6/6 |
| Q13 (previously examined) | 0/6 | 6/6 |
| Q14 (new) | 0/6 | 6/6 |
| Q15 (new) | 3/6 | 6/6 |
| Q16 (new) | 2/5 | 5/5 |
| Q17 (new) | 0/2 | 2/2 |
| Total, new quarters | 5/19 | 19/19 |

The five positive windows in the original model did not mean that it was still reliably predicting transits. Its average measured dip was negative in every one of those four quarters. A stricter comparison with alternative phases, specified before the evaluation, was passed by the combined model in all four new quarters and by the original model in none. Quarter 17 had only two usable windows, so its evidence is limited.

This was the first refinement in this part of the project that produced a clear improvement on subsequent original brightness data. It used more observations and a longer observing interval, not a new algorithm. It also tested one known planet, not a fresh sample of stars. Nevertheless, it illustrates how a very small error in a measured period can undermine a forecast, and how extending the interval over which we measure the recurrence can help. Astronomers care about this because telescopes need to know when an event will happen, sometimes months or years after the original measurements. Published work on updating transit predictions makes the same general point [11].

## 4. Can machine learning help separate possible planets from false alarms?

Finding dips was only one part of my original proposal. I also wanted to see whether a simple machine-learning model could make better screening decisions than a single basic rule.

I used records from NASA's Kepler Data Release 25 catalog. Each record already had measurements calculated by NASA, including the estimated orbital period, transit duration, dip depth, and signal-to-noise ratio. Signal-to-noise ratio, or SNR, is a way of describing how clearly a signal stands out from background variation. I trained a *random forest*, which combines the decisions of many simple decision trees, to predict whether NASA's earlier automated screening had marked a signal as a **candidate** or a **false positive**.

For a fairer comparison, I kept stars in the training set separate from stars in the final test set. This helped avoid giving the model information about the same star during both training and testing. I then compared the forest with two alternatives: logistic regression using the same four measurements, and a simple rule based mainly on SNR.

On **1,619 held-out signals**, the forest agreed with NASA's historical labels **81.6%** of the time. Logistic regression agreed **77.3%** of the time, while the SNR-only rule agreed **52.3%** of the time. These are meaningful differences, but the forest was not simply better in every way. It rejected more of the records NASA had marked as false positives, yet it also rejected more records NASA had marked as possible planet candidates.

That trade-off matters. Suppose we make a model very strict so that it rarely lets a false alarm through. It might also throw away real planets. A high accuracy number can hide that problem, especially when the two groups are not equally common. This is why I looked at missed candidate labels and false-positive labels instead of reporting only the percentage correct.

I looked more closely at the candidate-labeled signals with periods of at least 100 days. Of 71 such signals in the original test set, the forest retained 44 and rejected 27. The median period of the rejected group was 359 days, compared with 166 days for the retained group. Their median transit depth was also smaller, about 482 rather than 915 parts per million. This is consistent with a problem we would expect from the physics: longer periods mean fewer opportunities to observe a transit, and shallower dips are harder to distinguish from noise. But this comparison describes the records the model missed; it does not establish the cause of each error or tell us whether those signals were real planets.

In a separate, previously frozen test split, I tried making the model more willing to accept signals with longer periods. In one recorded long-period comparison, the number of NASA candidate-labeled signals it retained increased from **42 of 58** to **57 of 58**. That sounded promising until I checked the cost: the accepted false-positive-labeled signals also rose from **28 of 87** to **64 of 87**. The overall balance became worse. I kept the original negative result rather than just reporting the improvement in candidate recovery.

There is another important limit here. NASA's old candidate labels are **screening decisions**, not proof that each marked signal is actually a planet. Also, the four measurements I used had already been calculated by NASA. My machine-learning model was **not connected directly to the BLS program** from the earlier experiment. It was a second, related test of whether AI-assisted coding could help reproduce a useful classification method. Larger NASA systems, including ExoMiner, use far more information [6]. I did not outperform those systems or claim to reproduce them.

## 5. One small attempt to improve a telescope measurement

My reading also brought up a problem that was different from finding the repeating period. Sometimes several stars are so close together in a telescope image that their light overlaps. If a nearby star dims, the *center of the combined light* can appear to move. Astronomers can use that movement to help decide which star actually caused the dip.

I wondered whether subtracting some of the telescope's own pointing movement would make this measurement more useful. I tried a simple correction on a separate set of measurements from NASA's TESS telescope. I treated this as an extra experiment, not as part of the Kepler classifier.

The correction reduced one measure of local motion in **44 of 56 stars**. At first, that seemed encouraging. But the more important question was whether this made it easier to identify the star responsible for a dip. In the smaller follow-up checks, I did not find reliable evidence of that improvement. A graph can look steadier while still giving no better answer about the physical cause.

That result also needs context. Professional Kepler and TESS teams already use sophisticated corrections for telescope motion and other instrument effects [12]. I was testing one simple adjustment, not inventing a correction they had overlooked. In fact, removing movement indiscriminately could erase a genuine shift caused by a nearby eclipsing star.

To investigate why that correction might fail, I added a controlled computer simulation with AI assistance [14]. Imagine two stars one pixel apart, with one four times brighter than the other. If the bright target dims, the center of their combined light moves toward the neighbor. If the neighbor dims, it moves in the opposite direction. I used the same total brightness decrease in both cases, so the direction of the centroid shift was the only clue to which star had dimmed.

The simulation compared 2,000 events in each of twelve combinations of pointing instability and reference-star measurement noise. The same events were evaluated both with and without correction. When the simulated pointing displacement was large and the reference measurement was precise, the correct source was identified in 52.3% of cases before correction and 83.2% afterward. When there was no simulated pointing error and the reference was noisy, accuracy instead fell from 84.0% to 59.2%.

The reason is simple. Subtracting a reference measurement removes the movement shared by the two measurements, but it also adds the reference's own uncertainty. In this simplified model the correction lowers the expected squared centroid error only when the common pointing displacement is more uncertain than the reference measurement of that displacement. This follows directly from the independent-error propagation we covered in the lab. The simulation assumes the movement is shared perfectly and uses chosen noise levels, not actual TESS measurements. It explains a possible reason for the earlier real-data result, but does not prove what caused it or demonstrate an improvement in a professional telescope.

This experiment reinforced something I had been learning from the start: **making a measurement look cleaner is not the same as making it more scientifically correct**.

## 6. What this taught me about AI and scientific research

AI made a real difference in how much work I could attempt. It helped me write Python functions, interpret error messages, handle astronomy file formats, and build comparisons that would have taken me much longer to set up alone. It was especially useful for trying an idea quickly and then changing the code when that idea did not work.

But the results were not automatically trustworthy because the code ran. My first artificial transit test was too easy. The first known-planet result looked impressive until I tried more systems. A machine-learning accuracy score looked strong until I examined which kinds of signals were being missed. A telescope correction lowered visible motion without proving better source identification, and a controlled simulation showed how a noisy reference can make a correction counterproductive. Finally, the new timing experiment showed that a 0.066% error could become large enough to miss every predicted transit window months later.

There was also a difference between what AI helped me *do* and what I needed to *understand*. AI helped implement standard algorithms. Deciding whether the experiment was fair, checking official NASA measurements, keeping failures in the results, and separating a planet from a repeating eclipse required knowledge of the underlying physics. I had to work out what each number actually meant instead of treating it as proof of success.

The project connects most directly to **Lesson 2**, because we are measuring the light that reaches a telescope; **Lesson 3**, because timing and repeated events are central to detecting transits; and **Lessons 5 and 6**, because gravity and Kepler's laws explain why planets have orbital periods. The uncertainty discussions in **Lab 1 and Appendix B** are also relevant. The final timing result is a particularly clear example: a small error in a measured period can become a large error when we use it repeatedly.

## Conclusion

I started this project wanting to find out whether AI could help reproduce or improve a real astronomical research method. The answer is **yes, with important limits**. AI helped me build a program that found the known period of Kepler-69 b to within 0.0658%. It also helped me build a small classifier that matched NASA's earlier screening labels more often than a simple SNR rule.

But neither result was enough by itself. The transit program struggled with other planets and with eclipsing binary stars. The classifier missed some historical candidates when it became stricter about false positives. The telescope-movement experiment made one measurement smaller without proving more accurate source identification. The controlled simulation helped explain why: correcting for movement can improve the result, but only if the correction does not introduce more noise than it removes.

The Kepler timing experiment gave me the most memorable example. Our predicted dips were visible in the first few later quarters, then disappeared from the original prediction windows. The more accurate published period explained why. The next AI-assisted experiment used three quarters of earlier measurements instead of one, without supplying the published period. The refined estimate differed from NASA's value by only about 11.6 seconds per orbit and passed the fixed prediction test in all four newly examined quarters. We had improved our own forecast for a known planet, not invented a new discovery method.

My conclusion is not that AI can replace astronomers. It is that AI can make serious methods more accessible, while the harder part of scientific research is often deciding what a result actually proves. A program can find a pattern, produce a confident-looking number, and still miss something important. Testing those limits was the most useful part of the project.

## References

[1] Kepler's Third Law and Newtonian gravity, as discussed in ASTR/PHSC 12600, Lessons 5-6, Autumn 2026.

[2] Kovács, G., Zucker, S., & Mazeh, T. (2002). "A box-fitting algorithm in the search for periodic transits." *Astronomy & Astrophysics*, 391, 369-377. https://doi.org/10.1051/0004-6361:20020802

[3] Batalha, N. M., et al. (2010). "Pre-spectroscopic False-Positive Elimination of Kepler Planet Candidates." *Astrophysical Journal Letters*, 713, L103-L108. https://doi.org/10.1088/2041-8205/713/2/L103

[4] Thompson, S. E., et al. (2018). "Planetary Candidates Observed by Kepler VIII: A Fully Automated Catalog..." *Astrophysical Journal Supplement Series*, 235, 38. https://doi.org/10.3847/1538-4365/aab4f9

[5] McCauliff, S. D., et al. (2015). "Automatic Classification of Kepler Planetary Transit Candidates." *Astrophysical Journal*, 806, 6. https://doi.org/10.1088/0004-637X/806/1/6

[6] Valizadegan, H., et al. (2022). "ExoMiner: A Highly Accurate and Explainable Deep Learning Classifier That Validates 301 New Exoplanets." *Astrophysical Journal*, 926. https://doi.org/10.3847/1538-4357/ac4399

[7] Astropy Collaboration. "Box Least Squares." *Astropy documentation*. https://docs.astropy.org/en/stable/timeseries/bls.html

[8] Mikulski Archive for Space Telescopes (MAST). *NASA Kepler observations and data products*. https://archive.stsci.edu/missions-and-data/kepler

[9] NASA Exoplanet Archive. *Kepler-69 planetary-system overview*, including DR25 Kepler-69 b orbital period. https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-69

[10] Thomas, D. (2026). *AI-assisted Kepler study: source code, archived measurement outputs, and frozen Q8-to-Q9, Q10-Q11, Q12-Q13 analyses*. https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/NOV18_PLAIN_ENGLISH_KEPLER69B_RESEARCH_RESULTS.md

[11] Edwards, B., et al. (2021). "Original Research by Young Twinkle Students (ORBYTS): Ephemeris Refinement of Transiting Exoplanets." *Monthly Notices of the Royal Astronomical Society*, 504, 5671-5684. https://doi.org/10.1093/mnras/staa1245

[12] NASA Kepler Science Office. *Kepler Data Characteristics Handbook*, discussion of PDC instrument-systematics correction. https://archive.stsci.edu/kepler/manuals/Data_Characteristics.pdf

[13] Lissauer, J. J., et al. (2024). "Updated Catalog of Kepler Planet Candidates: Focus on Accuracy and Orbital Periods." *Planetary Science Journal*, 5, 152. https://doi.org/10.3847/PSJ/ad0e6e

[14] Thomas, D. (2026). *Controlled pointing-instability simulation: fixed protocol, AI-assisted source code, and all twelve synthetic outcomes*. https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/NOV25_CONTROLLED_POINTING_SIMULATION_RESULTS.md

[15] Thomas, D. (2026). *AI-assisted multi-quarter Kepler-69 b timing refinement: frozen protocol, original NASA FITS provenance, complete forecast results and reproducible analysis*. https://github.com/DrewThomas09/ASTR_FInal_Project/blob/main/NOV25_MULTIQ_EPHEMERIS_VERIFIED_RESULTS.md

**Acknowledgment of assistance:** Generative AI assisted with code development, debugging, running the November 25 continuation experiments, and drafting explanations and figures. All original-source results are documented in the repository. This working manuscript is for student review and independent verification before submission.

## Project Elements Checklist Form

**Synthesis of Lecture Material**

| Lecture Number/Topic | Concepts included in the Project | Location in the Project/Essay/Write-Up |
|---|---|---|
| Lesson 2: Light and measurement | Stellar brightness, flux, and why overlapping stars can confuse a telescope | Sections 1, 2, and 5 |
| Lesson 3: Time | Measuring recurring dips and predicting future events from a fitted period | Sections 1 and 3 |
| Lesson 6: Kepler's Laws (optional bonus) | Orbital periods, gravity, and why stellar binaries can confuse simple transit searches | Sections 1, 2, and 6 |

**Quantitative analysis**

**a) Briefly describe the quantitative analysis component of your project:** I recovered a known Kepler-69 b period and calculated its percentage error. I then tested that same frozen period against real later-quarter NASA brightness measurements, counting usable prediction windows and checking the effect of accumulated timing error. A refinement used Q8–Q10 jointly and compared both fixed fits on Q12–Q17, separating previously examined Q12–Q13 from newly evaluated Q14–Q17. Separately, I compared a four-feature random forest, logistic regression, and SNR-only screening on 1,619 held-out NASA Kepler records, and measured a simple TESS pointing correction on 56 stars. A supplemental, clearly labeled synthetic experiment compared raw and corrected centroid source assignment in twelve paired noise conditions, with 2,000 events per condition.

**b) Where is the quantitative component found?** Sections 2-5, especially the Kepler period calculation, original forecast and multi-quarter refinement tables in Section 3, the held-out machine-learning scores in Section 4, and the TESS motion result and controlled simulation in Section 5.
