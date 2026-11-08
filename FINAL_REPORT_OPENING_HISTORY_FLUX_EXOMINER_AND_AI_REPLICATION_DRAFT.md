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

### References and course connections

- ASTR/PHSC 12600: Lesson 2 (luminosity and flux); Lesson 3 (time and measurement); Lessons 5–6 (Kepler's laws and gravity); Lesson 7 (light).
- NASA: [How We Find and Characterize Exoplanets](https://science.nasa.gov/exoplanets/how-we-find-and-characterize/) and [30 Years of Exoplanets](https://science.nasa.gov/exoplanets/30-years-of-exoplanets-compilation/).
- Valizadegan et al. (2022), *ExoMiner: A Highly Accurate and Explainable Deep Learning Classifier That Validates 301 New Exoplanets*, *Astrophysical Journal*, 926, 120.
- Valizadegan et al. (2025), *ExoMiner++: Enhanced Transit Classification and a New Vetting Catalog for 2-Minute TESS Data*, *Astronomical Journal*, 170, 287.
- [NASA's ExoMiner code](https://github.com/nasa/ExoMiner); [official ExoMiner++ TESS data](https://zenodo.org/records/15466293).

**AI-use disclosure to retain in the final paper:** GPT-6 assisted literature review, code, public-data acquisition, tests, analysis, and report drafting. Scientific interpretations and any model improvements should be independently verified and disclosed in accordance with the course requirements.
