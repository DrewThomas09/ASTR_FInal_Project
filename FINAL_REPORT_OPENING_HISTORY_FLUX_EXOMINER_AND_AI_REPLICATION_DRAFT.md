# Testing AI's Impact in Exoplanet Research
**Drew Thomas · ASTR 12600 · Professor Buzasi · Final report working draft**

*This is the proposal-aligned main report. The long research and code audit, including the more complicated TESS and NASA ExoMiner work, is preserved separately in* [the technical appendix](ARCHIVE_LONGFORM_EXOMINER_TESS_TECHNICAL_DRAFT_BEFORE_PROPOSAL_ALIGNMENT.md). *This draft describes results already measured with original public data. It does not claim to have trained or improved NASA's ExoMiner model.*

## The question I wanted to answer

Artificial intelligence is being presented as a tool that could change scientific research. It can write code, sort through large datasets, and find patterns that would take people a long time to identify. But I wanted to test something more specific: **can AI help someone without a professional astronomy background reproduce a real research method, and can it help improve the results?**

I chose exoplanets, which are planets orbiting stars outside our solar system. We have good reasons to believe that they are common, but most are far too distant and faint to see directly. Astronomers often have to work out whether a planet exists by studying small changes in the light they receive from a star. This connects directly to the class: we measure *flux* (the light reaching a detector), measure *time* between events, and use Kepler's laws to understand the motion that could cause those events.

I used generative AI to help write and debug Python code, and I used publicly available observations and catalog records from NASA's **Kepler** mission. The experiment had three parts. First, I tried to reproduce a familiar way of finding possible planets. Second, I tested whether a simple machine-learning model could better sort likely planets from false alarms. Third, after researching the limits of these techniques, I tried one smaller adjustment to a related telescope measurement to see whether cleaner data would actually produce a better scientific answer.

The first two parts are the **main Kepler experiment promised in my proposal**. The third is a separate exploratory follow-up using NASA's **TESS** telescope. It does not replace the Kepler analysis and was not added to the Kepler classifier.

## 1. How does a telescope find a planet it cannot see?

Imagine watching the same star over and over. Most of the time, the amount of light reaching the telescope stays fairly steady. If a planet passes between us and the star, it blocks a small amount of that light for a short time. The amount of light drops, then returns to normal.

A single dip is not enough to prove that a planet is there. A telescope problem, a star changing in brightness, or an eclipse involving two stars can look similar. But if the dips repeat at a fairly regular interval, the pattern begins to look more like an orbit. The time between repeated dips is the *orbital period*.

This also explains why the observations are connected to physics rather than just pattern recognition. The size of the dip gives a rough clue about the planet's size relative to its star. The time between dips tells us how long the orbit takes. Kepler's third law connects that period to the size of the orbit, assuming we know something about the star's mass.

The basic challenge is **finding a very small repeating drop in a noisy set of brightness measurements**, while remembering that not every repeating drop is caused by a planet.

## 2. First experiment: can AI help reproduce a real planet-search method?

I asked generative AI to help implement **Box Least Squares**, or **BLS**, a standard technique astronomers use to search a light curve for a regular pattern of dips. A *light curve* is simply a graph of how a star's brightness changes over time.

BLS checks many possible orbital periods. At each one, it asks whether short, regularly spaced dimming events fit the observations better than a flat brightness level. The best-looking repeating pattern becomes a possible planet signal.

To see whether the AI-assisted code was working, I tested it on real Kepler observations of a star already known to host a planet: **Kepler-69 b**. The planet was not discovered by this project. Using an original NASA Kepler Quarter 8 light-curve file, the program examined **2,767 usable brightness measurements** and found a repeating pattern.

The result was encouraging:

| Measurement | Result |
|---|---:|
| Previously published orbital period | **13.722 days** |
| Period found by our AI-assisted BLS program | **13.713 days** |
| Difference | **About 0.066%** |

The program also found five sufficiently observed dimming events within that telescope observation period. In simple terms, **AI helped me build code that could find the correct repeating pattern in real telescope data**.

This is a successful reproduction of an established research technique, not a discovery of another planet. I deliberately chose a known planetary system to check whether the code behaved sensibly. That made it a useful first test, but it does not tell us how well the program would perform if we pointed it at thousands of unfamiliar stars.

*Suggested Figure 1: the actual Kepler-69 b brightness measurements folded onto the detected period, from the original [real Kepler source experiment](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42319839037/artifacts/13551514247). The figure should show a repeating dip, with a caption explaining that this is a previously known planet, not a new discovery.*

## 3. Second experiment: can machine learning tell better signals from false alarms?

Finding a repeating dip is only the beginning. There is another problem: **some very convincing-looking dips are not planets**. A pair of stars eclipsing one another, for example, can produce a clear repeating pattern. So I wanted to test whether machine learning could do a better job than a simple rule at separating signals NASA had previously marked as possible planets from signals NASA had marked as false positives.

For this experiment, I downloaded **8,054 records** from NASA's Kepler catalog, involving **6,923 different stars**. These records contain historical NASA screening labels: **4,034 'candidate' signals** and **4,020 'false positive' signals**. That distinction matters. A 'candidate' is a promising signal that may be a planet, **not necessarily a fully confirmed planet**.

I compared two approaches:

- **Simple rule:** Judge the signal mainly by how strong it is compared with the background noise. This is called the signal-to-noise ratio. It is an understandable first screen, but even a very strong signal can come from two stars eclipsing each other.
- **Machine-learning model:** Use a *random forest*, which looks for patterns across several measurements rather than relying on one cutoff. I gave it four pieces of information NASA already measured: the suspected orbital period, how long the dip lasts, how deep the dip is, and how strong the signal is relative to the noise.

The dataset was divided into **training, validation, and testing groups**. Most records were used to teach the model. A separate group was used to choose its decision cutoff. The final **1,619 records, from 1,385 stars**, were held back until evaluation. Stars in the test set did not also appear in the training or validation sets. That was important because the model should not get credit for already knowing the specific stars it was being tested on.

### What happened?

| On NASA's held-out Kepler records | Simple signal-strength rule | Random forest |
|---|---:|---:|
| Matched NASA's previous labels correctly | **52.3%** | **81.6%** |
| Historical false positives incorrectly called candidates | **695** | **189** |
| Historical candidates incorrectly rejected | **77** | **109** |

**The random forest was substantially better at reproducing NASA's previous screening labels overall.** Out of the same 768 historically labeled false positives in the test set, the machine-learning model incorrectly accepted only **189**, compared with **695** for the simple rule.

However, there was a trade-off. The random forest also rejected **32 more historical candidates** than the simpler rule. In astronomy, throwing away a promising signal matters, because one of those rejected candidates could turn out to be a real planet. The two methods were tuned on validation data to aim for a similar candidate-recovery rate, but their actual recovery rates on the held-out test set were different. It would be misleading to say the random forest was better at *everything*.

We also tested a more ordinary statistical model that used the same four measurements. It achieved **77.3%** overall label agreement. The random forest's **81.6%** result was better, suggesting that machine learning could pick up more complicated relationships than a simple statistical cutoff or a straight-line model. This was encouraging, but it was still a comparison to **historical NASA labels**, not a test against independently confirmed planet identities.

*Suggested Figure 2: two simple side-by-side bar charts showing overall historical-label agreement (52.3% versus 81.6%) and the number of labeled false positives incorrectly accepted (695 versus 189). Use the authentic saved model outputs in the [NASA Kepler catalog experiment](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42513638366/artifacts/13630680897).*

## 4. After researching existing methods, what could we try to improve?

This was the part I found most interesting. By this point, I had shown that AI could help implement an existing search method and build a machine-learning model that performed better than a simple screen on the available labels.

But there was a limit to what those results meant. Our model was working with four numbers that astronomers had already calculated. It was not looking directly at every source of trouble in the original telescope measurements. Also, NASA's existing detection and validation systems were already far more advanced than the small model I had built. Trying to claim that my basic classifier outperformed professional planetary research would not make sense.

So instead of writing an entirely new detection method, I looked for **one specific measurement problem that was easy to explain and possible to test**.

A telescope is not perfectly still. Tiny changes in its pointing can change where a star's light lands on the detector. That movement can sometimes be confused with a real change in where the light is coming from. The *center of light* is important because it can help determine whether the dip comes from the target star or a nearby star.

Here is the simple idea we tested:

**What if we take the recorded movement of the telescope and subtract it from the measured movement of the star's light? Would that help make the measurement more trustworthy?**

This was a research-based, small adjustment to an existing measurement, not the only possible way to improve exoplanet research. I tested it as a **separate extension using NASA's TESS data**, because TESS provides both the measured center of light and an estimate of the telescope's pointing correction in its public records. These extra results are **not Kepler model scores**, and I did not feed the adjusted centroid into our Kepler random forest.

## 5. Third experiment: did the pointing adjustment help?

I used original observations from **56 TESS stars**. For each star, I compared the movement of the measured center of light before and after subtracting the recorded telescope pointing correction.

At first, the change looked promising: **44 of the 56 stars** showed a reduction in a simple local movement measure. In everyday language, the adjusted measurement was usually steadier.

But I then had to ask a harder question: **Does a steadier measurement actually tell us more accurately which star dimmed?**

Imagine two stars so close together that the telescope blends their light into one spot. If the star on the left gets dimmer, the combined center of light can shift toward the star on the right. That shift is **real information** about which star changed. An adjustment that merely makes every shift smaller could erase part of that information along with unwanted telescope movement.

I therefore tested the correction on **five additional stars** that had previously been flagged as possible nearby-eclipse cases. I chose those new stars before opening their centroid measurements. Four had enough complete repeated events for the planned comparison. In **two** systems, the adjusted shift pointed in a more physically plausible direction; in the **other two**, it got worse.

I also tried the same adjustment on a completely separate group of **five stars known to host transiting planets**, with **46 complete transit events**. All five showed a smaller measured in-transit centroid shift after correction. But that by itself does not prove an improvement, because some part of an in-transit shift may be real. In one of the five confirmed planetary systems, the correction actually made the local movement measure worse.

Finally, I compared two of the suspected neighboring-eclipse systems with genuine ground-based follow-up observations and NASA's own source-position reports. The ground observations supported fading light in nearby-star apertures. However, the simple TESS pixel images and NASA's fitted source positions were not consistent enough to assign the same dimming event confidently to one star across observations.

**The result was mixed.** The correction often made the measurement *look less noisy*, but our further checks **did not show that it reliably made the underlying planet-versus-false-positive decision better**.

This is an important distinction: **we measured a change in telescope data, not a verified increase in planetary classification accuracy**. The full, more technical experiments and all the disappointing cases are saved in [the NASA/TESS results scorecard](VERIFIED_NOV13_FULL_RESULTS_WHAT_WORKED_WHAT_FAILED_NASA_TESS_PRF_BENCHMARK.md); they do not need to take over this Kepler-focused paper.

*Optional Figure 3: a simple diagram of two blended stars and the center of light shifting when one star dims. This explains why a smaller centroid shift is not automatically better. A detailed 22-sector NASA PRF table is not necessary in the main report.*

## 6. What did AI really contribute, and where did it need human judgment?

The most useful thing about AI was not that it independently discovered new astronomical facts. It was that it could help me **turn an idea into working code**. AI assisted with writing the Python programs, reading the public telescope files, debugging errors, preparing plots, and setting up comparisons. That made a kind of analysis that normally takes a substantial amount of specialized programming much more accessible.

At the same time, several apparent improvements did not hold up under closer checks. A stronger model missed more historically labeled candidates. A cleaner centroid signal was not necessarily better at identifying the source star. Some follow-up labels turned out to be less certain than they initially appeared, and some NASA source-position results were not valid measurements at all.

Those were moments when a human still had to ask basic scientific questions. Were we measuring the right thing? Were the comparison groups fair? Did a classification label mean a confirmed planet, or just a promising signal? Was a change in a graph evidence of better detection, or merely evidence that the code changed the numbers?

I would not have been able to treat AI output as a final scientific conclusion without checking the original NASA records and the physics behind the results. That is part of the result of the project, not an inconvenience to hide.

## Conclusion

I began with a straightforward question: **could AI help someone reproduce and possibly improve real exoplanet research methods?**

**On reproduction, the answer was yes.** The AI-assisted BLS code found the known Kepler-69 b orbital period to within **0.066%** using real NASA observations.

**On machine-learning screening, the result was also encouraging, with an important qualification.** Our small random forest matched NASA's historical Kepler candidate/false-positive labels **81.6%** of the time, compared with **52.3%** for a simple signal-strength rule. It rejected far fewer historically labeled false positives but also missed more candidates. This was not proof that it could confirm planets or outperform NASA's full professional pipeline.

**On improving a measurement, the answer was less clear.** The additional TESS pointing adjustment reduced a local movement measure in **44 of 56 stars**, but it did not consistently improve the information needed to decide which star produced a dip. Making data look more stable does not necessarily make the scientific answer more accurate.

The larger lesson is that AI can make sophisticated research techniques more accessible. It can help build tools and test ideas quickly. **But it cannot remove the need to understand the observations, choose fair comparisons, and check whether a numerical improvement answers the actual scientific question.**

## Original research records and references

**Original code, source measurements and reproducibility**

- [Kepler-69 b original real telescope light-curve BLS source and figure](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42319839037/artifacts/13551514247).
- [Kepler DR25 original catalog holdout: model comparisons, predictions and charts](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/42513638366/artifacts/13630680897).
- [Kepler DR25 original-data findings](REAL_NASA_DR25_RESULTS_2026_11_06.md) and [statistical validation and known tradeoffs](VERIFIED_DR25_PAIRED_SIGNIFICANCE_2026_11_08.md).
- [TESS original-data extension: results that worked and results that failed](VERIFIED_NOV13_FULL_RESULTS_WHAT_WORKED_WHAT_FAILED_NASA_TESS_PRF_BENCHMARK.md).
- [Python source code and test suite](https://github.com/DrewThomas09/ASTR_FInal_Project).

**Scientific background**

- Kovács, Zucker and Mazeh (2002), the Box Least Squares transit search: https://doi.org/10.1051/0004-6361:20020802.
- McCauliff et al. (2015), machine learning in Kepler transit vetting: https://doi.org/10.1088/0004-637X/806/1/6.
- Thompson et al. (2018), Kepler DR25 automated planet-candidate vetting: https://doi.org/10.3847/1538-4365/aab4f9.

**AI-use disclosure:** Generative AI (GPT-6) substantially assisted with literature explanation, Python implementation, source downloads, tests, calculations, visualizations, and drafting. Original NASA data and historical catalog classifications are external sources, not observations made by the AI. The student should personally verify all numerical claims, interpret the science, and disclose AI assistance in the submitted course work. This draft has not been submitted.
