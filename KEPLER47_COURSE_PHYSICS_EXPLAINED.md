# Physics explained: why Kepler-47 exposes a false instrumental-step warning
**ASTR/PHSC 12600 | Teaching note and final-report cross-reference**

This note explains the observation in [the verified Kepler-47 warning study](VERIFIED_KEPLER47_ECLIPSE_CHECK_2026_11_08.md). The stellar binary period and primary/secondary eclipse ephemerides are from **Orosz et al. (2019)**, DOI [10.3847/1538-3881/ab0ca0](https://doi.org/10.3847/1538-3881/ab0ca0). Our warning times come from original NASA Kepler Quarter 6 measurements.

## First: what actually causes a brightness dip?

A transiting **planet** blocks some of its star's light. Ignoring limb darkening and grazing effects, its fractional brightness reduction is approximately

```text
Transit depth = (planet radius / host-star radius)^2
```

A brightness decline is only a **transit-like measurement**, however. In an **eclipsing binary**, one **star** periodically passes in front of the other. This can produce deep and repeated changes resembling planetary transits. Separately, a telescope may show a sudden change in how sensitively one pixel records light; that is an **instrumental** discontinuity rather than an astrophysical eclipse.

Our local-step heuristic sees normalized light and looks for a sharp downward jump followed by a change in the local baseline. It does not know whether the source is a planet, a star, or an instrument. That is the physical gap in the current method.

## Lesson 6: Kepler's laws connect repeated events to orbital motion

The orbital period is the time needed to repeat an orbit. For two stars with total mass `M1+M2` and relative orbit semimajor axis `a`, the Newtonian version of Kepler's third law is:

```text
P^2 = 4*pi^2 * a^3 / [G*(M1+M2)]
```

Kepler-47 contains a stellar binary with a published orbital period of about **7.44837568 days**. Because the orbital geometry is viewed close to edge-on, recurrent eclipses can occur at particular orbital phases. These are **stellar** eclipses associated with the 7.448-day binary, not the longer-period transits of the planets that orbit around both stars.

We compute a binary phase for each observed measurement:

```text
binary phase = fractional part of [(time - published primary eclipse epoch) / P]
```

The primary eclipse occurs near phase 0 (equivalently phase 1); the published secondary eclipse occurs at a slightly different phase from exactly 0.5. That is why the comparison should use the **separate published primary and secondary epochs**, rather than assuming secondary always occurs exactly halfway through the cycle.

## Lesson 5: Gravity is the reason that orbital periods recur

Newton's law of gravitational attraction supplies the acceleration needed for the stars' orbital motion. Their masses and separation govern their orbital period, but **neither gravity nor Kepler's law can tell a photometer directly what caused a particular light loss**. The time series must be examined to separate an orbital eclipse from stellar variability, background-star contamination, and instrument behavior.

## Lesson 3: Timing and measurement are essential

NASA Kepler's TIME column is measured in **BKJD**, defined as `BJD - 2454833.0`. To use an independently published eclipse at barycentric Julian date `2454959.427964`, first subtract `2454833` to get its reference BKJD, then add whole multiples of the published orbital period to predict events in Quarter 6.

For example, one warning occurred at **BKJD 550.933616**. The nearest predicted *secondary stellar eclipse* was at approximately **BKJD 550.985394**, so the warning preceded the expected eclipse center by:

```text
(550.933616 - 550.985394) days * 24 hours/day = -1.24 hours
```

The sign indicates the earlier warning occurred **before** the predicted eclipse center. It is plausible that the steepest brightness decrease occurs around the beginning of an eclipse rather than exactly at the minimum. The remaining warning timings must be inspected separately; one of the seven was about 43 hours from any nearest predicted stellar eclipse center.

## What the result teaches us about AI-assisted astronomy

A program can be internally correct, reproducible, and pass every engineering regression test, yet still draw the wrong **physical interpretation**. In this project, many of the local-step warnings in Kepler-47 occurred near independently predicted binary eclipses, even though there was no official SPSD quality-bit positive event in this quarter.

The time alignment is **exploratory**, because we noticed Kepler-47 after seeing its warning-rich result. It does **not** confirm the physical cause of every warning or establish that the detector is worse or better at the mission level. A future trustworthy correction rule would have to protect real periodic eclipse/transit events while still detecting known instrumental events, and validate both tasks using untouched stellar sources.

**AI disclosure:** GPT-6 drafted this explanation and the linked code. The student should verify the equations, published orbital references, event timestamps, and physical interpretation before using this material in a graded submission.
