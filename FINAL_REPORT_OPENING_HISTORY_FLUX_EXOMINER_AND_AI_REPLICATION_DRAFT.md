# From Measuring Starlight to Reproducing ExoMiner: An AI-Assisted Exoplanet Project

## Introduction

The hunt for exoplanets is often overlooked in discussions of open-weight AI models and predictive machine learning. In this paper, I intend not only to examine the methods researchers use to identify planets beyond our solar system, but also to test whether AI can help reproduce a complicated scientific model and make small improvements to it.

Starting off, we need to understand the history of calibration.

## From measuring light to finding planets

Astronomy has always depended on making careful measurements of things we cannot physically reach. Long before scientists could identify a planet orbiting another star, they had to figure out how to measure a star's position, distance, motion, and brightness. More accurate instruments did not automatically produce more accurate conclusions. Astronomers also needed ways to calibrate their observations: to separate a real change in the object being observed from a change caused by the atmosphere, the telescope, or the measurement itself.

This is closely related to what we discussed in Lesson 2. **Luminosity** is the total power a star gives off, while **flux** is the amount of energy we receive per second per unit area. For a star radiating approximately equally in every direction, the relationship is

\[
F = \frac{L}{4\pi d^2}.
\]

A star can have a high luminosity and still appear faint if it is very far away. This distinction matters because telescopes do not directly measure a distant star's total luminosity. They record arriving light, which researchers convert into measurements of flux. For exoplanet detection, what matters most is often not the absolute brightness of the star but whether its **measured flux changes slightly over time**.

The way astronomers first found exoplanets was not by taking pictures of the planets themselves. In 1992, researchers identified planets by measuring changes in the timing of pulses from a neutron star. In 1995, the discovery of **51 Pegasi b**, the first confirmed planet around a Sun-like star, used the *radial-velocity method*. An orbiting planet pulls slightly on its star, causing the star to move toward and away from us. That motion produces small Doppler shifts in the star's light. The idea connects directly to our study of light and motion: a physical process changes an observable quantity, and the scientist must determine whether the measured effect is large and consistent enough to trust.

A different approach became especially important after astronomers observed a transit of **HD 209458 b** in 1999. Instead of measuring the star's motion, the **transit method** measures its brightness. If a planet crosses in front of its star from our point of view, it blocks a small fraction of the incoming light. The telescope records a dip, followed by a return to the normal flux level. If that dimming repeats at regular intervals, it may indicate an orbiting planet.

For a small planet crossing a roughly uniform stellar disk, the fractional loss of light is approximately

\[
\delta \approx \left(\frac{R_p}{R_*}\right)^2,
\]

where \(R_p\) is the planet's radius and \(R_*\) is the star's radius. A Jupiter-sized planet crossing a Sun-sized star blocks roughly **1%** of its light. An Earth-sized planet blocks only about **0.0084%**, or **84 parts per million**. Detecting something that small requires extremely precise calibration. A tiny change in telescope pointing, an instrument defect, or changes in the star itself can look like the signal we are searching for.

The transit method also ties together other topics from this class. Lesson 3 explored accurate measurement of **time**, which matters because a transit is identified partly by how often it repeats. Lessons 5 and 6 discussed gravity and **Kepler's laws**, including the relationship between orbital period and orbital size, \(P^2\propto a^3\) for planets orbiting the same dominant mass. When we measure the time between repeated transits, we are therefore learning something about the planet's orbit, not simply looking for a pattern in a spreadsheet.

## How researchers went from light curves to machine learning

The transit method became far more powerful with the launch of NASA's **Kepler telescope in 2009** and later **TESS in 2018**. Instead of watching a few stars at a time, these missions collected long sequences of brightness measurements for enormous numbers of stars. The resulting data are called **light curves**: graphs showing measured flux against time.

Initially, our research focused on the methods used to search these curves. One important technique is **Box Least Squares (BLS)**. BLS searches through possible orbital periods and transit durations, looking for repeated dips that fit a simple box-shaped model. It is relatively easy to understand and gives a useful starting point, so we implemented it on actual NASA Kepler observations.

The problem is that not every dip is a planet. A binary star can eclipse its companion. Stellar activity can change the measured brightness. Spacecraft motion and detector defects can also produce misleading drops. In fact, a convincing-looking repeating pattern is not always planetary: a stellar eclipsing binary can show almost the same timing structure. This means identifying *possible transits* is only the first step. Researchers then have to decide which signals deserve further investigation.

Our literature review led us from traditional transit searches to NASA's automated vetting systems, and eventually to **ExoMiner**. The original ExoMiner paper, published in 2022, described a deep-learning model that helped statistically validate **301 Kepler planets**. The later **ExoMiner++** system extended the approach to TESS measurements, and the 2026 ExoMiner++ 2.0 work added further support for full-frame-image observations.

ExoMiner does not simply take one number and decide whether a star has a planet. It receives a possible transit signal already found by an upstream search and looks at **several types of evidence at once**. These include the overall brightness curve, a close-up of the transit, individual transit events, differences between odd and even transits, signs of secondary eclipses, information about the star, and diagnostics showing whether the apparent dimming might come from a nearby object or the instrument. A neural network learns how to combine these different views and assigns a classification or confidence score. In simple terms, it tries to automate parts of the checks an astronomer would make when deciding whether a signal looks planetary.

That was the point where the goal of our project changed. Rather than attempt to invent a better detector from scratch, we wanted to see **how much of an advanced scientific system we could reproduce with AI assistance**, and whether that reproduction would let us test small, understandable modifications.

## Reproducing the research was harder than finding a model online

Much of the early work involved tracing the data behind the papers. This turned out to be one of the most difficult parts of the project. The original ExoMiner paper, the 2025 ExoMiner++ model, and the later 2026 version do not all use the same telescope data, processing steps, or definitions of a positive example. Downloading a paper or a model's source code does not mean we have everything required to reproduce its results.

We ended up working through several public sources. The **NASA Exoplanet Archive** supplied earlier Kepler Objects of Interest and the historical candidate/false-positive labels for our first classifier. The **Mikulski Archive for Space Telescopes (MAST)** supplied original Kepler light-curve files, including the measured flux, observing times, and quality flags. Those files are necessary if we want to study real transits rather than only classification labels.

For ExoMiner++, we located the researchers' **Zenodo data release** and the matching NASA **GitHub source-code version**. We successfully retrieved and verified two published TESS catalogs: **57,162 labeled transit-event records** and **147,567 previously unlabeled records** containing ExoMiner++ scores. We used the original checksums to make sure we had the correct files. These were not 204,729 independent planets: one star can generate multiple event records across observing sectors, and a high model score does not make an unlabeled candidate a confirmed planet.

The hardest remaining acquisition is the model's **full training input**, not the catalog. The published TESS training examples occupy a separate compressed archive of approximately **19 GB**, with individual time-series views and other numerical inputs. Those data also require the correct normalization and train/test splits. We have identified that archive but **have not downloaded it or retrained the full neural network**. Even after downloading it, we would need to keep the 2025 training version separate from the newer operational ExoMiner++ model. Otherwise, we could accidentally compare different models and call the result a replication.

This work helped us understand that scientific reproducibility is much more than getting code to run. We have to know which telescope recorded the measurement, how the data were corrected, which version of the model produced the score, and whether two observations come from the same star. Without those checks, a machine-learning model can appear more accurate than it really is.

## What we have completed so far

To build up to ExoMiner, we began with a simpler four-feature **random forest** using **8,054 historical Kepler candidate and false-positive records**. The inputs were reported orbital period, transit duration, transit depth, and signal-to-noise ratio. On a held-out set grouped by star, this model achieved **81.29% balanced accuracy** against NASA's previous labels. It performed better than the simpler baselines we tested, but that does **not** mean it confirmed new planets or outperformed NASA's full vetting pipeline.

We then moved back to the actual light curves to understand the physics behind the errors. One problem we discovered was that a routine designed to remove sudden instrument-like changes in brightness could also flag **real stellar eclipses**. A recurrence-based safeguard preserved **42 original measurements** around two eclipse warnings in the Kepler-35 and Kepler-1647 systems. These were not planet discoveries, but they showed how data cleaning can unintentionally remove genuine astronomical information.

We also tested whether a signal found in one observing period predicted what happened later. We used Kepler Quarter 6 to estimate transit periods and then checked the predictions against Quarter 7 without refitting them. The rule passed on **six of nine usable known planet-host systems**, but it also passed on **both known eclipsing-binary controls**. This was an important negative lesson: the ability to predict a repeating dip is not, by itself, enough to decide that the object is a planet.

Most recently, we began producing some of the same **types of diagnostic inputs** that ExoMiner uses: a full light curve folded by orbital phase, close-up transit views, odd and even events, and individual transit images. On the known binary **Kepler-35**, the odd and even eclipses differed dramatically because a simple search favored approximately half the true stellar orbital period. This made clear why a model needs to examine the physical shape of separate events rather than rely entirely on one reported period and depth. **These are ExoMiner-inspired inputs, not yet a reproduction of the NASA neural network itself.**

## Where AI comes in, and what we plan to change

The main question I want to investigate is not whether AI can write a piece of code that looks like a NASA project. It is whether AI can help a researcher **understand, reproduce, test, and then carefully modify** an existing scientific system. In our case, AI has helped read papers and documentation, write Python code, locate archived data products, automate downloads, generate tests, and compare observed results with the predictions of physical models. It has also made mistakes that required corrections and independent checks. The purpose of the project is to see how useful this assistance is when the work has to meet actual scientific standards.

Our next step is to run the **official pretrained ExoMiner++ model** on a small, carefully selected set of original TESS events. Once we can reproduce the same outputs with the correct data and model version, we can test a limited change rather than redesign the entire system. The modification we are considering would pay more attention to the difference between a real transit and a sudden instrument defect. For example, does the brightness return to its original level after the event? Does the shape repeat at a consistent phase? Could a detected period actually be half of an eclipsing binary's orbital period? Where the evidence is uncertain, could we preserve or downweight the measurement instead of deleting it?

There is an important limitation: ExoMiner++ already examines individual transits, odd/even differences, and several instrument-related clues. Simply adding those features would not be an original scientific improvement. We would need to show that our specific change performs better **than the existing model with those features already included**. The comparison should use the same stars and observations, and should report both the real signals recovered and the false positives introduced.

For a more ambitious test, we could inject realistic artificial planetary transits into real telescope measurements, keep the true injection parameters hidden from the detector, and see whether the modified system recovers more planets **at the same false-alarm rate**. That would be stronger evidence than increasing agreement with old labels.

Ultimately, this project connects two ideas that have come up repeatedly in class: the importance of **careful physical measurement**, and the need to test whether a model actually explains what we observe. A telescope does not see an exoplanet directly when it records a transit. It measures a very small change in received starlight. Everything that follows, from calibration to orbital calculations to neural-network classification, depends on interpreting that change correctly. My goal is to see whether AI can make this scientific process more accessible and easier to improve, while keeping the measurement, physics, and evidence at the center.

## References and course connections

- ASTR/PHSC 12600, **Lesson 2**: luminosity, flux, distance, and the inverse-square law; **Lesson 3**: measurement of time; **Lessons 5–6**: Kepler's laws, gravitation, and orbital motion; **Lesson 7**: the nature of light.
- NASA, [How We Find and Characterize Exoplanets](https://science.nasa.gov/exoplanets/how-we-find-and-characterize/).
- NASA, [30 Years of Exoplanets](https://science.nasa.gov/exoplanets/30-years-of-exoplanets-compilation/).
- Valizadegan et al. (2022), *ExoMiner: A Highly Accurate and Explainable Deep Learning Classifier That Validates 301 New Exoplanets*, *Astrophysical Journal*, 926, 120.
- Valizadegan et al. (2025), *ExoMiner++: Enhanced Transit Classification and a New Vetting Catalog for 2-Minute TESS Data*, *Astronomical Journal*, 170, 287.
- [NASA ExoMiner source code](https://github.com/nasa/ExoMiner); [published ExoMiner++ TESS catalogs and training data](https://zenodo.org/records/15466293).
- ASTR project: [historical Kepler classifier validation](VERIFIED_DR25_PAIRED_SIGNIFICANCE_2026_11_08.md), [original eclipse protection results](VERIFIED_RECURRENCE_PROTECTED_STELLAR_ECLIPSES_2026_11_08.md), [ExoMiner replication audit](EXOMINER_FULL_TECHNICAL_AUDIT_AND_REPLICATION_PLAN_2026_11_08.md).

**AI disclosure for student review:** GPT-6 helped with literature review, code development, data collection, testing, analysis and drafting. All scientific claims and model comparisons must be checked against the original sources; student should review and adapt the final narrative to reflect personal understanding and the course rules.
