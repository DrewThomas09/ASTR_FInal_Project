# From Measuring Starlight to Reproducing ExoMiner

The hunt for exoplanets is often overlooked in discussions of open-weight models and predictive machine learning. In this paper, I intend not only to examine the methods researchers use to identify planets outside our solar system, but also to explore whether AI can help reproduce a complicated scientific model and make small improvements to it.

Starting off, we need to understand the history of calibration.

## How did we get from measuring stars to finding planets?

One of the main ideas from this course is that science depends on what we can actually measure. For much of astronomical history, researchers were limited to observing the position, motion, and brightness of distant objects. Improving a telescope was only part of the problem. Astronomers also needed to **calibrate** their instruments and understand which changes came from the stars themselves and which came from the atmosphere, the telescope, or measurement error.

This connects directly to Lesson 2, where we discussed the difference between **luminosity** and **flux**. Luminosity is the total energy a star emits per second, while flux is the energy we receive per second per unit area. For a star radiating equally in all directions, the relationship is

\[
F=\frac{L}{4\pi d^2}.
\]

The farther away the star is, the less light reaches us per unit area. We cannot simply point a telescope at another star and measure its total luminosity directly. We measure the light that arrives at our detector. For this project, the important quantity is how that **measured flux changes over time**.

The first confirmed planets beyond our solar system were not discovered by directly photographing them. In 1992, astronomers found planets by measuring tiny changes in the timing of radio pulses from a pulsar. In 1995, researchers discovered **51 Pegasi b**, the first confirmed planet orbiting a Sun-like star, by measuring how the planet's gravity caused its star to move back and forth. This is the **radial-velocity method**, which uses Doppler shifts in the star's light. It is a good example of how something invisible can be identified through its measurable effect on another object.

Our project focuses on a different method: **transits**. By 1999, astronomers had observed an exoplanet passing in front of its host star. When a planet crosses the star from our viewpoint, it blocks some of the light and causes a temporary dip in measured flux. If that happens repeatedly, researchers can estimate the planet's orbital period.

The amount of light blocked depends roughly on the areas of the planet and star:

\[
\text{Transit depth}\approx\left(\frac{R_{\mathrm{planet}}}{R_{\mathrm{star}}}\right)^2.
\]

For example, a Jupiter-sized planet crossing a Sun-sized star can block about **1%** of its light. An Earth-sized planet blocks only around **0.0084%**, or **84 parts per million**. This is why calibration becomes so important. A tiny instrumental change or a natural fluctuation in a star's brightness can be mistaken for a small planet.

The transit method also brings in two other parts of our course. In Lesson 3, we discussed how accurately scientists can measure **time**; here, the time between repeated dips is what helps identify an orbit. In Lessons 5 and 6, we studied **Kepler's laws** and gravity. Kepler's third law connects orbital period to orbital size, so measuring the timing of a transit tells us something about the physical system that produced it. We are not simply finding patterns in a graph. We are using measurements of light and time to infer how an object moves through space.

## How we arrived at ExoMiner

The launch of NASA's **Kepler telescope in 2009**, followed by **TESS in 2018**, changed the scale of exoplanet research. Instead of a small number of individual observations, astronomers could analyze long sequences of brightness measurements from enormous numbers of stars. These measurements form **light curves**, with flux on one axis and time on the other.

The first part of our project was researching how those curves are analyzed. We started with **Box Least Squares (BLS)**, an established algorithm that searches for periodic dips in brightness. We implemented it on real Kepler observations because it is a clear way to connect the physics of transits to a working computer program.

However, BLS can identify a repeating dip without knowing what caused it. A second star in a binary system can produce an eclipse. A telescope can register a sudden change caused by its own instruments. Stellar activity can also change a light curve. As a result, finding a *possible* transit is different from showing that the object is a planet.

That led us to NASA's **ExoMiner** research. The original ExoMiner model, described in a 2022 paper, helped statistically validate **301 Kepler exoplanets**. The newer **ExoMiner++** models extend this approach to TESS observations. Rather than rely on a few numbers, ExoMiner examines multiple views of a candidate signal, including the full brightness pattern, individual transits, odd and even events, possible secondary eclipses, and evidence of instrument problems or nearby stars. A neural network combines these measurements to help decide whether a detected event looks planetary.

In simple terms, a transit-search algorithm asks, **“Is there a repeating dip?”** ExoMiner asks, **“Is that dip more consistent with a planet, a star, or something wrong with the data?”** The important distinction is that ExoMiner generally **evaluates candidate signals that have already been found**; it does not automatically discover and confirm planets directly from raw telescope data.

## The difficult part: finding the right data

Once we chose ExoMiner, I initially expected the hardest part to be recreating its neural network. Instead, a major challenge was figuring out **which data and model versions actually belonged together**.

The 2022 ExoMiner paper, the 2025 ExoMiner++ release, and the 2026 updates are not the same experiment. They use different versions, telescope missions, input formats, and evaluation procedures. Having a paper and a GitHub repository does not necessarily give us everything needed to reproduce the published results.

We had to work through several sources. The **NASA Exoplanet Archive** provided Kepler catalog measurements and earlier classifications. The **Mikulski Archive for Space Telescopes (MAST)** provided original Kepler light-curve files with observation times, measured flux, and quality flags. These were necessary for working with real telescope measurements rather than only NASA's previous labels.

For ExoMiner++, we traced the 2025 research paper to the team's **Zenodo dataset** and its matching NASA **GitHub release**. We acquired and verified two original TESS catalogs: **57,162 labeled transit-event records** and **147,567 previously unlabeled records** containing published ExoMiner++ scores. We also had to check the recorded star identities and observing periods, because the same star can appear more than once. Treating every row as a separate planet would exaggerate the amount of independent evidence.

The hardest remaining dataset is the **actual neural-network input**, rather than the catalog of results. The published TESS training examples come in a separate compressed archive of about **19 GB**. Those examples still need the correct processing and normalization before we can fairly reproduce the model. We have identified the archive but **have not yet downloaded it or retrained the complete ExoMiner++ network**.

This was an unexpected lesson from the project. Reproducing scientific research is not just copying code. We need the right observations, the right processing steps, the right training labels, and the right definition of a successful result.

## What we have built and what we want to improve

To understand the problem before reproducing the full neural network, we first built a smaller machine-learning model. Using **8,054 historical Kepler candidate and false-positive records**, we trained a random forest on four measurements: orbital period, transit duration, depth, and signal-to-noise ratio. It achieved **81.29% balanced accuracy** on a held-out set of stars, outperforming the simpler models we tested. However, it was predicting **NASA's earlier classifications**, not independently confirming planets, so this is not a direct comparison with ExoMiner++.

We then examined the original brightness measurements more closely. A rule intended to remove sudden instrument-related drops in brightness also flagged **genuine stellar eclipses**. We tested a safeguard that recognized repeating events and preserved **42 observations** around two such warnings. These events came from eclipsing binary stars, not new planets, but they revealed a possible problem with removing observations too aggressively.

We also tested whether an orbital period found in one Kepler observing quarter could predict dips in the next quarter. It did for **six of nine usable known planet-host systems**, but it also worked for **both known eclipsing-binary controls**. This showed that finding a repeating signal is not enough: we still need to identify its physical cause.

More recently, we began reconstructing **some of the same types of input views** used by ExoMiner: full and close-up light curves, odd and even transits, secondary-eclipse checks, and individual-event views. On the known eclipsing binary Kepler-35, the odd and even events looked dramatically different because a simple period search had chosen about half the binary's actual orbital period. This helped us understand why NASA's model looks at separate events instead of relying on a single period and depth. **These inputs are a prototype, not a complete ExoMiner replication.**

Our plan is to use AI as a research and programming assistant to help reproduce the **official pretrained ExoMiner++ model**, verify its outputs on the correct TESS data, and then test a modest change. One idea is to examine more carefully whether a sudden drop looks like a real transit that returns to its normal brightness, or an instrumental change that persists. We also want to test whether checking alternative orbital periods can help reject confusing binary-star signals.

ExoMiner++ already includes related checks, so adding them by itself would not count as an improvement. We would have to test whether our specific modification performs better **than the original model using the same observations**. Ultimately, we want to compare how many real or realistically injected planetary signals each method recovers **without accepting more false alarms**.

This brings the project back to the course's central question: **what can we learn from a measurement, and how confident should we be in the conclusion?** The telescope measures a small change in incoming starlight. Physics helps explain what that change could mean. Machine learning helps organize enormous amounts of evidence. Our experiment is about whether AI can make it easier to reproduce and improve that process while remaining honest about what the data actually show.


## The experiment: what does it take to reproduce a complicated model?

Once I understood what ExoMiner was trying to do, I divided the practical work into two questions. First, could I use AI to help recreate the steps that lead to a planet classification? Second, once the original system was working, could I use AI to propose and test a small change without making its predictions less reliable?

I started smaller than ExoMiner itself. The first model used four numbers already reported in the Kepler catalog: the estimated orbital period, the length and depth of the transit, and its signal-to-noise ratio. I trained a **random forest**, a model that combines many decision trees, and compared it with simpler methods. I also made sure observations of the same star did not appear in both the training data and the held-out test data. Otherwise, the model might appear to perform well because it had already seen information about that star.

On the historical Kepler labels, the random forest achieved **81.29% balanced accuracy**, compared with **76.61%** for logistic regression and **50.23%** for a signal-to-noise-only rule. Balanced accuracy averages how well a model recognizes each of the two classes, rather than letting one large class dominate the score. Further tests showed that the forest's improvement over those comparison models was statistically meaningful **for agreement with these historical labels**. It still did not mean that we had independently identified 81% of real planets. NASA's earlier classifications were the answers our model was trying to reproduce.

This was useful because it gave us a working baseline. But it also showed why recreating ExoMiner would require much more than adding more trees. ExoMiner looks at the *shape of the light itself*, not just four summary numbers.

### Going back to the actual telescope measurements

The next step was to work with the original NASA light-curve files. These files include when each observation was made, how much light the telescope recorded, and flags indicating possible problems with the measurement. The brightness measurements need to be cleaned and normalized carefully so that we are looking for changes relative to the star's usual flux, not mistaking gaps or bad measurements for transits.

Using AI-assisted Python code, I recreated some of the inputs that appear in ExoMiner. One view shows the star's brightness across a complete possible orbit. Another zooms in on the expected transit. Two more separate alternating **odd and even** events, and another checks for a possible eclipse on the opposite side of the orbit. I also created a view containing up to **20 individual transit events**, so that one unusual dip cannot simply disappear inside an average.

There was an important technical challenge here: not every expected transit has measurements available. A telescope may stop observing the star, or some data may be flagged as unreliable. At first glance, an empty part of a light curve might look like an ordinary brightness measurement if it is filled with a default number. I therefore kept a separate record showing which parts of each view actually contained observations. The goal was to stop the model from treating missing information as evidence.

Two examples helped explain why these extra inputs matter. For **Kepler-12**, a known planet-host system, the fitted period was about **4.44 days**, and the repeated transit dips looked relatively consistent. For **Kepler-35**, a known eclipsing-binary system, the simple transit search selected a period of about **10.37 days**, roughly half the stars' actual orbital period. The odd and even dips looked very different because the program was mixing two different stellar eclipses. A model that checked only whether the light dimmed repeatedly might get confused. A model that compared the separate events would have much more information.

These were useful demonstrations of the physics behind ExoMiner. They were **not yet a recreation of its neural network**. NASA's model also uses information we had not reconstructed, including more detailed instrument diagnostics and pixel-level evidence showing where a signal originates.

### Checking whether we could reproduce the published results

In parallel, I worked with the actual ExoMiner++ TESS catalogs. These contain the model's already-published classifications and scores. Before analyzing them, we verified that the downloaded files matched the researchers' originals. Even a simple mistake, such as using a different release of the catalog, would make a reported replication difficult to trust.

The labeled catalog contained **57,162 transit-event records from 17,206 stars**. We checked that the researchers' ten evaluation groups did not place the same star into different groups. We also recreated a precision-recall analysis from the scores in the released catalog. Its average precision was about **0.970**, which confirmed that we could read and evaluate the published scoring data correctly.

However, this result belongs to **NASA's already-trained ExoMiner++ models**. We did not generate those scores with a neural network trained by our project. The comparison also reminded me why a very high overall score can be misleading: many records are repeated observations, and the mix of known planets and nonplanets is not the same as the mix of objects a new sky survey would encounter.

The hardest part of the full replication remains reproducing the inputs and preprocessing for the actual neural network. The researchers released approximately **19 GB of compressed TESS training examples**, separate from the much smaller catalogs. Those inputs still have to be matched to the correct model version, split by star, and normalized using training data rather than information from the test set. At this stage, we have verified the catalogs and built a prototype of several input views. We have since **run NASA's official pretrained model on one documented TESS target**, but **have not retrained ExoMiner++ or reproduced its full published benchmark**.

### What went wrong, and why those failures mattered

Not every experiment improved the result. One early idea was to adjust the classification threshold for planets with longer orbital periods. The change helped retain more objects labeled as candidates, but it also admitted many more false positives, so overall balanced accuracy became worse. It was a useful reminder that finding more apparent planets is not an improvement if the method also mistakes substantially more nonplanets for planets.

The same problem appeared when we tried to protect real brightness dips from being removed as instrument errors. Our safeguard preserved **42 telescope measurements** associated with two real stellar-eclipse warnings. That showed the data-cleaning rule could remove legitimate astronomical information. But those events were **stellar eclipses, not new planetary discoveries**, and the safeguard also missed other eclipses. We still need enough genuine instrument-error examples to test whether a new rule would accidentally preserve bad data.

AI helped us write, run, and check these experiments, but it did not prevent mistakes. For example, one attempt to download the official catalog failed because the archive rejected the requested file format. Another automated test failed because the test removed observations from a slightly narrower time window than the code was supposed to examine. We corrected those problems, but neither correction counted as a scientific improvement. That distinction matters: **getting a program to run successfully is not the same as proving its conclusions are right**.

## The next test: can AI help improve a model without breaking it?

We have now run the **official pretrained ExoMiner++ model** on a documented TESS target and saved its original prediction. The next stage is to expand that run into a properly selected set of observations and compare NASA's unmodified system with a version containing one specific, independently tested change.

The modification I want to investigate is how the system handles ambiguous changes in brightness. A planet transit usually returns toward the star's normal flux after the planet passes. An instrument problem may cause a more persistent change. I want to test whether examining that difference, along with the consistency of individual events and possible half-period errors, helps the system reject misleading signals **without deleting real transit information**.

ExoMiner++ already checks several related things. Therefore, I cannot claim this is a new idea simply because AI helped implement it. The question is whether our particular method adds useful information **beyond what the existing system already uses**.

To test that fairly, the original model and the modified model would need to examine the same previously unseen stars. We would choose the evaluation rules before looking at the answers and compare how many known or artificially injected planet signals each method identifies **at the same false-alarm rate**. If the modified version finds more planets but also accepts more eclipsing binaries or instrument errors, the result would be a trade-off rather than a clear success.

That is the larger purpose of this project. I am using exoplanet detection as a way to test whether AI can help someone work with a difficult, established scientific system: understand the original research, reproduce its data and methods, find a specific weakness, and test a small change. The hardest part is not getting AI to generate a more complicated algorithm. It is making sure the algorithm still respects the underlying physics and produces evidence that another researcher could check.


## Further model development: moving from prototypes to the real NASA network

After building the earlier Kepler prototypes, I wanted to make sure we were not mistaking a good-looking simulation for a successful replication. We therefore tried running NASA's **actual ExoMiner++ software**, using the researchers' published instructions, rather than recreating the appearance of its outputs ourselves.

Our first attempt did not work. The NASA program needed to rewrite part of its input file, but our automated runner had mounted that file as read-only. Once we found the precise source of the error, we made a writable copy of the input and kept the original untouched. This was a software problem rather than a problem with astronomy, but it was another example of why reproduction requires attention to small technical details.

The corrected experiment succeeded. The official pretrained model downloaded the original TESS observations and other diagnostic measurements for **TIC 167526485, Sector 6**, the example used in NASA's documentation. It processed the signal using the official neural network, **ExoMiner version 2.4.0**, and returned a **planet-validation score of 0.0203**, with a classification of **NOT_PC** (not a planet candidate). The detected event's reported period was about **5.01 days**. The original spacecraft data were processed through the official pipeline, with exactly one transit-like event successfully scored. The model and its result were not our own recreation; we preserved the NASA model version, software image identifier, logs, and exact output CSV so we can repeat the run.

This was the first time the project actually ran ExoMiner++ itself. It did not confirm that the program is correct for every star, and one example cannot reproduce the published accuracy of the entire system. But it removed an important obstacle: we now know how to run and inspect the genuine scientific software, not just the simpler programs we created before it.

### A small feature experiment on the same TESS catalog

I also wanted to test whether a relatively small change could make a simpler model more useful. For this experiment, we used the **57,162 previously labeled TESS event records** from the 2025 ExoMiner++ dataset and divided them by their original ten published groups of host stars. This prevented observations of the same star from appearing in both training and testing data.

We first trained a random forest using **orbital period, transit duration, estimated planet radius, and signal strength**. Then we created an otherwise identical model with two additional inputs. The first measured the **fraction of the orbit occupied by the event**, which gives the model some information about the geometry of an apparent transit. The second used **Gaia's RUWE measurement**, a measure of how well a star's apparent motion fits the expected astrometric model. Unusually large RUWE values can sometimes suggest a companion star or other complications, although they are not direct proof of a binary.

Both models were trained and tested on exactly the same source records and the same ten star-separated folds. We froze the feature choices and model settings before running the comparison, rather than continuing to change the model until we got a result we liked.

The four-feature model achieved an **average precision of 0.6211**. The six-feature model increased that to **0.6446**, an improvement of about **0.0234**. For context, using the researchers' already-published ExoMiner++ scores on those same TESS records gave an average precision of **0.9704**. We did not retrain NASA's neural network to produce that last number; it was a comparison with the official published results.

At first, the small increase seemed promising. However, the statistical test was less convincing. By repeatedly resampling whole stars rather than individual event rows, we estimated a 95% uncertainty interval for the feature change of approximately **-0.0110 to +0.0537**. Because this interval includes zero, we could not rule out that the apparent increase was due to the particular sample of stars. Moreover, at the default score threshold of 0.5, the modified random forest actually had slightly worse precision and recall than the original random forest.

This was **not a demonstrated improvement**. It was a completed experiment that showed the kind of trade-off we have to check. It also emphasized how much stronger the complete ExoMiner++ approach is than a model based only on a handful of summary measurements. Finally, RUWE and related geometric measurements already appear in NASA's more advanced models, so simply adding them to our small random forest would not be a new discovery.

### Testing the shapes of real events

Alongside that comparison, we continued developing a physical diagnostic on the original Kepler data. We measured the brightness immediately **before, during, and after each expected eclipse or transit**. The idea was that a temporary event should recover toward the earlier level of brightness, while some detector problems leave a longer-lasting change. We also compared the depths of alternate events to look for periods that are really half of a binary star's orbital period.

We applied the program to two previously known systems, **Kepler-12**, which hosts a known transiting planet, and **Kepler-35**, a system with eclipsing stars. We examined both Kepler **Quarter 6 and Quarter 7**, recording the actual observations used. The code found **20 and 18 usable events** for Kepler-12 in the two quarters, and **7 and 8 usable eclipses** for Kepler-35. On both stars, the local brightness usually recovered after the event. This was useful physical evidence, but it also showed an important limitation: **recovery alone cannot tell us whether the object is a planet or a star**, because stellar eclipses also end.

The earlier pictures of Kepler-35 showed very different odd and even eclipse shapes. However, when we calculated uncertainty from the smaller collection of *individual observed events*, the intervals for the depth difference still included zero. That meant the event-level statistical evidence was not as strong as the folded picture initially suggested. Rather than adjust the test until it became significant, we retained the inconclusive result.

This is exactly why I wanted to work on a well-established model instead of immediately building a replacement. Each additional input may appear physically reasonable, but a model improves only if the information helps on enough independent observations and does not create new mistakes.


### Connecting our new measurements to NASA's actual model

We have now been able to go one step further than examining separate Kepler examples. We ran the original NASA ExoMiner++ model and our additional brightness-recovery measurements on **the same TESS observation**.

The official model found one transit-like event for **TIC 167526485 in Sector 6**, with a reported period of about **5.01 days**. Its pretrained network assigned the signal a planet-validation score of **0.0203** and classified it as **not a planet candidate** at the standard threshold.

We then examined the original TESS flux measurements that NASA's pipeline had downloaded for this specific event. Our code identified **four separate brightness dips**, each around **1.1–1.2%** of the local light level. The star's measured brightness also returned close to its earlier level after each dip.

This result is interesting because it shows why the transit method needs more than a search for repeated changes in flux. By itself, the light curve looks like a series of real eclipses. But there are several things that might cause such a pattern, including planets, eclipsing stars, or light entering the telescope from another source. ExoMiner has access to additional diagnostics that our simple recovery check does not capture.

The result does **not** tell us why NASA rejected this particular signal, or whether the source was definitively a binary star or an instrument effect. It also does not yet show that our additional measurement improves the classification. But it proves that we can now examine **the same underlying telescope measurements as the actual ExoMiner model** and compare what each diagnostic reports, without modifying the original model's score.

### Where the development stands

The project has now moved through three distinct stages: a simple machine-learning baseline, reconstruction and testing of real transit measurements, and finally a successful run of the **official pretrained ExoMiner++ neural network**. We have also completed one small feature experiment on the TESS catalog, with a modest but statistically uncertain result.

We have now attached our event-recovery measurements to the **same TESS observations** used by NASA's real pretrained model for one documented source. The next stage is more demanding: testing a wider, fixed set of stars rather than relying on this single example. Only after this can we test whether an added input or modified decision rule helps the existing model rather than merely improving one of our smaller substitutes.

For a convincing conclusion, I would want to see more genuine or realistically injected planetary signals recovered **at the same false-alarm rate**, with uncertainty calculated across independent stars. If we cannot produce that evidence, our conclusion should be that AI helped us understand and reproduce a complex scientific workflow, but that we have **not yet demonstrated a better method for discovering planets**.


### Trying to improve ExoMiner's own predictions

After running the real NASA model, I wanted to get closer to the central question of the project: **can AI help make a small improvement to an already sophisticated model, rather than simply build a much weaker replacement?**

I designed another experiment using the researchers' own **2025 ExoMiner++ prediction scores**. Instead of training another random forest from scratch, I tested whether a simple model could improve those existing scores by considering additional physical information about the transit.

I made two versions of this experiment. The first used only ExoMiner++'s original score and tried to calibrate it statistically. The second used the same score but added the reported orbital period, transit duration, detection strength, Gaia's RUWE measurement, and the fraction of the orbit occupied by the transit. These quantities could plausibly help identify cases where an unusual orbital shape or unresolved stellar companion makes a signal less likely to be a planet.

To prevent an unfair comparison, both versions used exactly the same **57,162 historical TESS transit-event records** and the same ten groups of stars. A star held out for testing could not appear in the training data. I also fixed the choices of input measurements and model settings *before* running the comparison.

The experiment produced a result I had not hoped for, but one worth reporting. The original, unmodified ExoMiner++ scores had an average precision of **0.9704**. Calibrating those scores without additional measurements produced **0.9695**, and adding the extra physical measurements produced **0.9694**. The difference between the two new versions was effectively zero. When we calculated uncertainty across whole stars, the interval included both a small improvement and a small worsening.

This meant I could not claim that AI had improved ExoMiner++ with our proposed change. In fact, the original scores performed slightly better than either new version. This does not establish that no improvements are possible. It suggests something more specific: **the model already uses many of the same physical measurements, so adding a few summary numbers to its final score is not enough**.

Importantly, we tested a statistical *postprocessor* of NASA's already-published 2025 scores, not a newly trained version of its neural network. The exercise taught us how to construct a controlled experiment, preserve the original model as a baseline, and accept a negative result without changing the experiment until it looks successful. To test a more meaningful improvement, we need to examine the original light curves and instrument diagnostics on a larger set of stars, where the cause of an apparent transit is genuinely uncertain.


### Moving beyond one star: testing the real NASA model on sixteen systems

The next problem was that our first successful ExoMiner++ run involved only one target from NASA's documentation. That showed the software worked, but it did not tell us how it behaved across different astronomical signals.

To make the test more useful, I selected **sixteen stars** from the public TESS catalog **before looking at the model's scores**. The group included four known planet systems, four candidate planet signals, four eclipsing binaries, and four examples labeled as nontransiting phenomena. Within each category, I deliberately included weaker and stronger detected signals so that the experiment would not consist only of the clearest examples.

I then ran NASA's actual pretrained **2026 ExoMiner++ model** on the matching telescope observations. The software found and scored **22 transit-like events** among the sixteen stars. Sixteen of those were the exact events I had chosen ahead of time. All sixteen were available for analysis, and our separate physical-measurement program successfully examined the same original TESS light curves.

The results were encouraging for reproducing the system. The model assigned scores above its default planet-candidate threshold to **all eight previously labeled planets or planet candidates**. It assigned scores below that threshold to **all eight eclipsing binaries or nontransiting phenomena**. In other words, its classifications agreed with the earlier published categories for **16 of the 16 selected events**.

However, this is not evidence that ExoMiner has 100% accuracy on newly discovered planets. These stars were previously studied, the sample was deliberately balanced by label, and we have not verified that the 2026 neural network was trained without them. The result is evidence that we can correctly run and inspect the original model across multiple classes, rather than a new independent measurement of its overall accuracy.

The extra physical measurements were also revealing. Across the sixteen original light curves, our program examined **81 individual brightness events**. One eclipsing-binary system, **TIC 318986273**, produced a very deep dip, roughly **11.6%** of the local stellar light, yet NASA's planet-validation score was almost zero. The brightness also returned close to normal after the eclipse. This showed that even a deep, repeatable, well-formed dip with a normal recovery can come from two stars rather than a planet.

That observation changed how I thought about our proposed modification. We originally hoped that tracking how the light recovers after a dip might distinguish genuine planetary transits from instrument problems. It may still be useful for studying certain instrument defects, but the sixteen-star experiment showed clearly that **it cannot distinguish planets from eclipsing binaries by itself**. Both phenomena can return to their normal brightness afterward. The model needs the additional evidence that ExoMiner already uses, including alternating eclipse shapes and evidence about which star produced the signal.

This is probably the most important lesson from the development work so far. AI helped us reconstruct the original analysis, write new measurements, and run the full NASA model on real data. But when we tested our small changes, the results repeatedly showed that the original system had good reasons for being more complicated. A meaningful improvement will have to target a weakness the full model actually misses, rather than adding a measurement that merely seems reasonable in isolation.


### Finding mistakes that the newer model still makes

The first sixteen-star experiment showed that we could run NASA's full neural network and match its decisions to earlier published categories. But because those cases were mostly straightforward, it did not tell us where the model needed help.

I therefore designed a more difficult experiment using the published **2025 ExoMiner++ results**. This time, I intentionally looked for signals that the earlier model had classified incorrectly: eight planet-related labels that it missed, and eight nonplanet labels that it accepted. I froze those sixteen star and event identifiers before running NASA's **2026 version** on them.

The newer model was able to process all sixteen original events and the original telescope measurements associated with them. Against the same historical labels, it corrected **seven of the sixteen earlier mistakes**. Four previously missed planet-related signals were now accepted, and three previously accepted nonplanet signals were now rejected. **Nine disagreements remained**, including four planet-related signals that the model still scored below 0.5 and five nonplanet-labeled signals that it still scored above 0.5.

This result was much more useful than simply reporting a high accuracy score. It gave us real examples to investigate. One source, **TIC 29960109**, was labeled as a nonplanet signal in the older catalog but received a 2026 planet-validation score of **0.993**. Another, **TIC 466840711**, carried a known-planet label but still received a low score of **0.137**. An eclipsing binary, **TIC 165493409**, still received a score of **0.747**, above the usual planet-candidate threshold.

It is important to be careful about what these differences mean. We selected these stars *because the earlier model got them wrong*, and the new model may have encountered some of them during its own training. The original classifications may also have changed as astronomers obtained more evidence. For these reasons, the experiment does not prove that the newer ExoMiner is more accurate on previously unseen planets, or that each historical classification represents final physical truth.

However, it does give us a much better way to develop the next version of our work. Instead of asking AI to add another feature simply because it sounds useful, we can investigate specific disagreements in the actual telescope measurements. The next step is to inspect NASA's detailed input views for the most persistent cases, including individual transits, possible secondary eclipses, detector-quality information, and the position of the light source. Only after understanding those failures should we propose a new adjustment and test it on different stars.

This has become an important part of the project's conclusion so far: **AI has made it possible to reproduce and investigate a complicated scientific model, but the most valuable improvements come from finding out where its physical reasoning may be incomplete, not from making the model more complicated for its own sake.**


### A closer look at the difficult signals

To investigate these disagreements, I used NASA's own ExoMiner pipeline to generate the **full diagnostic plots** for five of the most interesting cases. This was different from simply examining the final planet score. Each report contained several views of the measured light curve, odd and even transit events, possible secondary eclipses, the measured position of the light source, and images showing where the signal appeared on the telescope's detector.

These images helped show why a good-looking light curve does not necessarily make a convincing planet. **TIC 165493409**, historically labeled as an eclipsing binary, showed a well-defined, repeating dip, with similar-looking alternating events. Yet the centroid-position plot also changed around the transit. We cannot tell from the figure alone whether this means the event originated on a different star, but it is the sort of physical evidence that a basic transit-search algorithm would miss.

For **TIC 466840711**, which carried an earlier known-planet label but received a low score from the current model, NASA's diagnostic plots showed a deep dip accompanied by a much less stable overall light-curve trend. **TIC 158623531** showed an apparently clean dip, but the model had only two transit events available in that observing sector. In both cases, a simple test based only on the depth of the light curve would miss important complications.

The most surprising problem appeared when I compared the actual measurements used in the **2025 and 2026 model versions**. We found that the older released catalog recorded transit duration in **days**, while the current pipeline reported it in **hours**. We also found that the fitted period for TIC 158623531 was roughly **7.87 days in the older table** but **15.75 days in the newer model**, almost exactly twice as long. For another star, TIC 178155732, the newer catalog appeared to have **swapped which numbered event corresponded to each of its two detected periods**.

These findings changed how we interpret the earlier comparison. Just because two models produce a score for the same event identifier does not always mean they are evaluating the exact same proposed orbit. A period alias, revised ephemeris, or different event-number assignment can make an apparent change in classification misleading. Before claiming that the model has corrected a mistake, we need to verify that the underlying signal is really the same.

This was another example of something AI was useful for: not merely generating a modification, but **helping identify a problem with the data and how the scientific experiment was being compared**. We therefore built a **source-identity check directly into our evaluation software**, comparing both model versions' fitted periods, epochs, transit durations, and event identifiers. On the same original sixteen difficult sources, the code found **thirteen period-consistent entries**, **one near-exact doubled-period alias**, and **two entries where the fitted period changed substantially**. Among the thirteen period-consistent cases, the current model agreed with the older labels on seven and still disagreed on six. The three other cases need separate physical-signal matching, so I no longer treat their raw event-number comparisons as proof of a persistent classification error. The corrected experiment passed **224 software tests**. This did not make ExoMiner better at finding planets, but it improved the scientific validity of our attempt to measure whether the model had changed.


### Our latest experiment: testing where the light actually comes from

After finding that a simple change to ExoMiner's classification scores did not make the results better, I wanted to return to the actual measurements. One idea from our earlier research was that a suspicious brightness dip might be easier to identify if we also measured whether the light appeared to move across the telescope's detector during the event.

This connects directly to what we studied in class about **flux and calibration**. TESS does not measure the total luminosity of a star directly. It records light reaching a set of pixels, each of which may include light from more than one star. If one of those stars dims, the average position of the light in the pixels can shift. Astronomers call that average position the **centroid**.

We used the original NASA TESS files to measure that position immediately **before, during, and after** the expected transit. We also tried removing the estimated motion of the spacecraft itself, because an instrument moving slightly is not the same thing as a star moving across the sky. The program required real observations on both sides of each event. If an observation was missing or marked as unreliable, we did not fill in an imaginary value.

Our first experiment used **32 previously examined stars**. NASA's actual pretrained ExoMiner model classified the original signals, while our separate code calculated how much the centroid moved. The additional program successfully processed the original light curves of **all 32 stars** and measured **146 separate usable events**. However, only 23 of those stars had at least three events with enough measurements for our confidence calculation.

We originally set a rule to flag a signal for extra review if its centroid moved at least **0.05 pixels**, roughly one arcsecond on TESS's detector, with consistent evidence across observed events. The largest median shift we actually measured was only **0.0082 pixels**. As a result, **not one star was flagged**.

This was a clear negative result: the code worked, but the threshold was too conservative to be useful. Instead of changing the cutoff and presenting the new version as though it had always been our plan, we kept the result and tested the same rule on **24 additional stars** that we had not used during development. We selected those stars from the published catalog without looking at either model's scores. They gave us **102 more real observed events**, and again the 0.05-pixel rule flagged **no sources**.

We then tried one controlled adjustment. Using only the previously examined 32-star group, we selected a new, smaller threshold of approximately **0.0016 pixels** based on the largest centroid shifts among thirteen usable planet-labeled examples. We fixed that threshold **before examining the new 24-star centroid results** and applied it to those different stars without changing anything else.

This time, the program identified **five sources for manual review**. Four had earlier classifications as **eclipsing binaries**, while one had an earlier **known-planet** label. That initially sounded like an improvement because the new rule had identified the stellar eclipses.

But when we compared these warnings with NASA's complete model, an important problem appeared. **ExoMiner had already rejected all four binary-star signals.** The only new warning affecting a source that NASA had accepted belonged to the known-planet-labeled signal **TIC 78055054**, which ExoMiner had given a score of approximately **0.60**.

In other words, our new rule did not fix a demonstrated mistake. It mostly repeated decisions NASA had already made and risked rejecting something that astronomers had previously classified as a planet. We therefore could not describe the modification as making ExoMiner more accurate.

This was probably our most useful lesson in the project. It is relatively easy to use AI to produce another algorithm, generate an interesting plot, or suggest a reasonable-sounding feature. It is much harder to show that the feature improves a model that already uses detailed physical information. In this case, testing **56 different stars and 248 real observed transit or eclipse windows** was enough to demonstrate that our apparently promising change did **not** provide an established benefit.

I still think this was a productive use of AI in research. We went from reading a paper, to running the original NASA software, to building our own measurement from telescope observations, to designing a controlled comparison and rejecting a change that did not work. The result was not a new planet or a better neural network, but a clearer understanding of **why the original scientific model is complicated and how difficult it is to improve responsibly**.

### A further check: did a quieter instrument measurement make it a better scientific measurement?

After completing the original 56-star experiment, I asked one further question: could subtracting TESS's own estimated pointing motion improve the stability of the recorded moment-centroid coordinates? I used the same **248 original, paired observed event windows** rather than introducing a newly selected set of stars. For each star, I compared the median before/after-event centroid movement before and after subtracting the `POS_CORR` coordinates. The adjusted motion proxy fell in **44/56** stars and rose in **12/56**. The median paired reduction was about **0.001035 CCD pixels**; a 20,000-replicate whole-star bootstrap gave a 95% interval of **0.000738–0.001891 pixels**. This was a real, source-checked numerical change, but it showed only that the *measured local centroid displacement proxy* was smaller, not that the actual stellar sky position was known more accurately.

I then added a separate robustness test because this kind of correction could hide information that helps distinguish a genuine on-target planetary transit from an off-target stellar eclipse. In **32 of 56** stars, both the before/after drift proxy and the *in-event centroid shift* became smaller. In **12** stars, the drift proxy improved without a smaller in-event shift; the remaining **12** were split equally between an in-event-only reduction and neither quantity decreasing. These are physical measurement comparisons, **not planet-vs-binary classification outcomes**. Smaller in-event motion could mean better removal of spacecraft jitter, or it could mean suppression of an astrophysically useful displacement. Without independently verified source locations, our experiment cannot tell.

The result did not depend on any one observed star: dropping each star in turn left the median paired drift reduction positive in all **56** recalculations, from about **0.001026 to 0.001044 pixels**. Replacing the within-star event median with its mean still found **44/56** sources with lower drift, although the estimated magnitude changed. Our source-aligned [GitHub workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43294890871) reproduced these results from the original NASA/TESS artifacts and passed **261 software tests**. The [new source-level trade-off diagram and tables](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43294890871/artifacts/13977873521) remain supplementary figures until I select and caption them for the final paper.

This follow-up did not rescue the earlier neural-model improvement claim. Instead, it sharpened the difference between **a cleaner observation, a better physical interpretation, and a genuinely more accurate classification**. They are three separate propositions, and only the first, defined by our narrow drift proxy, has been supported by the present test. The follow-up was exploratory and post-hoc; it should not be portrayed as an independent blind validation.

### Does the pointing correction preserve the direction of a repeated eclipse?

I wanted to check one further thing before calling this a success. A consistent *direction* of centroid motion from one observed eclipse to the next could carry evidence about a physical light source in the aperture. To test whether the pointing adjustment preserved that information, I went back to the **original signed x and y centroid displacement vectors**, matched by actual NASA event orbit and epoch, and verified that the signed values reproduced the previously archived magnitudes. This was a new exploratory analysis of the **same** observed 56 stars and 248 event windows, not a fresh validation sample.

Only **40 stars** had at least three fully observed events and could be compared meaningfully. I used a bounded measure, the length of the sum of all observed in-event displacement vectors divided by the sum of their individual lengths. If the displacement vectors always point the same way, the measure is one; if they point in canceling directions, it is closer to zero. After subtracting the estimated spacecraft pointing motion, directional consistency **increased for 23 stars and decreased for 17**. The median paired change was about **+0.0012**, with a whole-star bootstrap 95% interval of **-0.0091 to +0.0505** and an exploratory paired sign-test p-value of **0.43**. The interval crosses zero, so these data **do not establish a reliable improvement**. The two originally selected cohorts also differed: 11/23 eligible earlier stars improved, compared with 12/17 eligible later stars. Those small cohorts were not prospectively designed to test this contrast.

This does not invalidate the earlier finding that the local before/after centroid drift proxy became smaller. It shows why I need to distinguish a *quieter instrumental measurement* from a *more reliable physical interpretation*. Without independent observations identifying which star in the aperture actually eclipsed, a stable centroid direction cannot prove a correctly localized planet or eclipsing binary. This experiment did not retrain or modify NASA's pretrained ExoMiner++ network.

The complete [source-paired audit and 270-test verification](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43301364382) includes the [original signed event vectors and source-level plot](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43301364382/artifacts/13980444834). I have also written an [independent follow-up protocol](NEXT_TESS_OFFTARGET_NEB_EXTERNAL_TRUTH_VALIDATION_PROTOCOL_NOV12.md) that calls for real ground-based identification of nearby eclipsing binaries, distinct from ordinary historical EB classifications. It is a protocol, **not completed new-source validation**, and it must not be used to claim better planet detection.

### A concrete external-source example: where did the light actually fade?

Our difficulty with the moment centroid suggested a more physical question: can a ground-based observer identify which **neighboring star** inside the TESS aperture actually dimmed? I screened original public ExoFOP follow-up records and learned that the broad `FP` disposition in its downloadable catalog is not, by itself, a label for a nearby eclipsing binary. Out of 8,175 listed TOIs, 1,322 carried that broad label, and 868 distinct uninspected host stars had both catalog ephemerides and reported time-series follow-up observations. I did not treat those 868 as confirmed eclipsing binaries. In a fixed 30-target sample of their public observing notes, 21 records contained an explicit NEB or possible-NEB photometric designation, although even those textual labels require direct examination of the reported observation.

Two cases offered unusually concrete source information. The original notes for **TOI-2041.01 (TIC 54364414)** identify **TIC 54364420** as the nearby eclipsing source, and a separate published nearby-star table places it **23.82 arcseconds** away at a sky position angle of **101.25°**. The notes for **TOI-4255.01 (TIC 82302240)** identify **TIC 82302236**, and the separate nearby-star table finds a separation of **5.10 arcseconds** at **31.21°**. These compare with the notes' approximate 23.4- and 5.0-arcsecond separations. Both independent astrometric lookups matched the specifically named TIC. These are carefully documented **post-hoc source-evidence examples**, not a fresh blind evaluation of our centroid method. I have not yet compared their original TESS event-centroid vectors with their sky directions or independently reanalyzed the uploaded ground-based eclipse plots.

There is also an important physical detail I initially needed to clarify: if the *neighboring* star fades, a simple flux-weighted centroid shifts **away from that neighbor**, not toward it. Let the target at position zero have flux `F_t` and the neighboring star at distance `d` have flux `F_n`. The centroid before the eclipse is `F_n d/(F_t+F_n)`; if the neighbor's light decreases by a fraction `δ`, the centroid shift is `-δ F_t F_n d/[(F_t+F_n)(F_t+(1-δ)F_n)]`. The negative sign shows the direction. This idealized two-star calculation helps explain why simply interpreting a centroid displacement as the eclipse's sky location would be wrong without considering the light from both stars, the aperture, and spacecraft motion. At about 21 arcseconds per TESS pixel, the two neighbor separations are approximately **1.13 and 0.24 detector pixels**, yet their expected *centroid changes* can be much smaller depending on the stars' relative brightness and eclipse depth.

The [public ExoFOP source, neighbor-astrometry cross-checks and negative sample-selection caveats](VERIFIED_NOV12_EXOFOP_2_POSTHOC_REPORTED_NEB_NEIGHBOR_ASTROMETRY.md) are fully archived. This is a useful opening for further independent investigation, but it does **not** change our principal finding: none of the attempted auxiliary preprocessing or centroid tests has shown a validated improvement in NASA's original exoplanet classification.

### Testing the TESS data against a known nearby eclipsing source

The external source measurements gave me a way to make the experiment more concrete. I checked the original NASA/MAST archive for actual 2-minute TESS light curves and target-pixel files for both of the previously discussed systems. **TOI-2041.01 did not have a matching original 2-minute SPOC observation returned**, so I did not silently use a different type of light curve. But for **TOI-4255.01**, the original TESS SPOC observations contained matching light-curve and pixel files in **sectors 61 and 62**. Those original FITS files allowed us to read the flux, measured centroid, spacecraft pointing estimate and detector's real map of sky directions. We used the original ExoFOP eclipse period of **2.5057108 days** and externally recorded epoch rather than tuning the timing to get a better outcome.

I found **eight complete observed event windows** in sector 61 and **ten** in sector 62, with positive brightness dips in eight and nine of them respectively. I compared the direction of the signed centroid displacement with the predicted direction **away from** the reported nearby eclipsing star TIC 82302236, measured in the actual TESS detector coordinates using the target-pixel FITS WCS. In sector 61, the original raw centroid was **55.95°** from that expected direction, versus **14.39°** after subtracting the pointing estimate. In sector 62, the corresponding angles were **153.84°** and **15.56°**. These were initially striking observations because both sectors showed a closer geometric match after correction, using the same real events without changing their times or the published source position.

But I wanted to know if those were stable results rather than lucky point estimates. We downloaded the *same original files a second time*, verified their SHA256 hashes and reproduced all 18 original event measurements before running another comparison. I resampled complete event vectors within each sector **20,000 times**, keeping the raw and adjusted versions of each event paired. The sector 61 95% descriptive interval for the angular improvement was **-137.91° to +65.72°**; the sector 62 interval was **-13.05° to +159.77°**. Both intervals include zero. These are within-one-star uncertainty calculations, not 20,000 new stellar systems or independent proof of improved detection.

I also checked actual observed windows one-quarter of the orbital period **before and after** the expected eclipses, without adjusting any settings after viewing their results. The sector 61 result was a particularly useful warning: a non-eclipse control at **+P/4** had a corrected angle of **13.80°**, almost as close to the predicted source direction as the actual eclipse measurement at **14.39°**, although its median observed brightness did not show a dip. Sector 62 was more encouraging: its actual eclipse aligned at **15.56°**, versus **70.30°** and **152.02°** at the two shifted control phases. Yet the wide bootstrap interval and the fact that all these observations belong to **one chosen target star** prevent a confident claim of improved physical source localization.

This is an example of why the project is about **research verification**, not simply using AI to produce a nicer-looking result. The correction produced a plausible physical alignment in some original NASA measurements, but the negative control and uncertainty checks showed that this is not yet established as a reliable new exoplanet vetting tool. It did not change NASA ExoMiner's predictions, and I have not discovered or validated a new planet. The underlying [source-checked 303-test result and all the original-data controls](VERIFIED_NOV12_TOI4255_REAL_TESS_SPOC_OFFTARGET_VECTOR_AND_QUARTER_PHASE_CONTROLS.md) document both the promising observations and the reasons I could not claim success.

### Did that promising alignment survive new stars?

After the TOI-4255.01 result, I wanted to avoid continuing to tune a method around a single favorable target. The original ExoFOP ground-based follow-up notes gave us 19 previously unexamined host-star leads. A strict original MAST search found actual two-minute TESS SPOC light curves and target-pixel files for ten of them, and five had one neighboring TIC mentioned in an explicit NEB follow-up note and also listed in the independent nearby-star catalog. **I fixed those five hosts, their cataloged neighboring stars, the original TOI orbital timing, and the lowest-numbered available SPOC sector for each before measuring any of their centroid values.** These were new *to our centroid analysis*, not necessarily absent from NASA's training data. A note that names a nearby star also does not, by itself, prove from original follow-up photometry that this was the true eclipsing source.

The new test successfully processed the original TESS observations for **all five** frozen stars. Together they produced **63 complete observed, same-event raw and pointing-corrected centroid windows**. One target, TOI-1223.01, had only **two** complete events; we left it inconclusive rather than treating it as a success or a failure. Of the remaining four sources, two had a smaller angular mismatch with the predicted direction away from the named neighboring star after pointing subtraction, and **two became worse**. The largest deterioration was for **TOI-2846.01**, where the original centroid already pointed just **4.49°** from the idealized direction but the adjusted centroid moved to **51.65°**. For **TOI-1330.01**, the pointing adjustment reduced our local drift proxy substantially but **worsened** the directional match from **46.09° to 60.54°**. That is a concrete example of a technically quieter measurement not necessarily yielding a more useful physical interpretation.

The four-source median angular improvement (raw mismatch minus corrected mismatch) was **−6.65°**; its exploratory whole-star bootstrap 95% interval was **−47.16° to +17.95°**, and the two-sided source-level sign-test p-value was **1.0**. The interval is broad, so I cannot confidently conclude the correction is generally worse either. The more important point is that the dramatic improvement seen in one earlier selected star **did not replicate consistently across these newly examined hosts**. The analysis retained every fixed star and every failed eligibility check rather than choosing which results to report. All original source file checks, event measurements, WCS coordinate conversions, quarter-period controls, tests and plots are archived in a [317-test successful workflow](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43319506539). The [five-star research note](VERIFIED_NOV12_FIVE_NEW_SPOC_NEBS_ORIGINAL_CENTROID_NEGATIVE_RESULTS.md) discusses each result and the remaining uncertainty about true ground-based eclipse-source identity.

This is the distinction that kept coming up in my research: using AI to write a new feature is relatively easy, but making a scientific improvement claim means testing it **without selecting on the result** and comparing against independent physical evidence. Here, the new observations did not demonstrate that our elementary pointing subtraction improved actual source localization, and they certainly did not establish any higher planet-vetting accuracy than NASA's complete ExoMiner++ system.

### References and course connections

- ASTR/PHSC 12600: Lesson 2 (luminosity and flux); Lesson 3 (time and measurement); Lessons 5–6 (Kepler's laws and gravity); Lesson 7 (light).
- NASA: [How We Find and Characterize Exoplanets](https://science.nasa.gov/exoplanets/how-we-find-and-characterize/) and [30 Years of Exoplanets](https://science.nasa.gov/exoplanets/30-years-of-exoplanets-compilation/).
- Valizadegan et al. (2022), *ExoMiner: A Highly Accurate and Explainable Deep Learning Classifier That Validates 301 New Exoplanets*, *Astrophysical Journal*, 926, 120.
- Valizadegan et al. (2025), *ExoMiner++: Enhanced Transit Classification and a New Vetting Catalog for 2-Minute TESS Data*, *Astronomical Journal*, 170, 287.
- [NASA's ExoMiner code](https://github.com/nasa/ExoMiner); [official ExoMiner++ TESS data](https://zenodo.org/records/15466293).

**AI-use disclosure to retain in the final paper:** GPT-6 assisted literature review, code, public-data acquisition, tests, analysis, and report drafting. Scientific interpretations and any model improvements should be independently verified and disclosed in accordance with the course requirements.
