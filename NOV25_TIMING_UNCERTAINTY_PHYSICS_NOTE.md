# Why additional observing time improves an orbital-period estimate

## A quantitative connection to Lesson 3 and Appendix B

For a strictly periodic orbit, the predicted mid-transit time at integer orbit index n is t(n)=t0+nP. Two independent transit-time measurements with equal standard uncertainty s_t, separated by N known orbital cycles, yield P_hat=(t2-t1)/N and, using independent-error propagation, s_P=sqrt(2)*s_t/N. More widely separated timing measurements constrain the period more tightly. This assumes correct cycle counts, equal independent timing errors and no transit timing variations.

If m measured mid-transit times have equal independent errors, ordinary least squares estimates the slope P with standard uncertainty s_t/sqrt(sum((n_i-mean(n))^2)). For m consecutive transits the denominator is sqrt(m*(m^2-1)/12). As a purely illustrative comparison, five consecutively observed transit times give sqrt(10) in the denominator; twenty give sqrt(665), so the latter idealized slope standard error would be about 8.15 times smaller for the same s_t. These are not the actual transit counts or inferred uncertainty of our BLS fits. BLS fits a box template directly to brightness cadences; it is not this regression on separately measured mid-transit times.

Our original NASA data gave a Q8 span of 66.96 days and 2,767 usable brightness cadences; Q8–Q10 span of 264.88 days and 11,172 cadences. Both cadence count and span changed, so the experiment cannot isolate the effect of duration from additional observations. The measured reduction in disagreement with the NASA reference period (67.10-fold) is NOT a 67-fold reduction in formal uncertainty, and should not be expected for other systems.

Even when the period is accurate, an initial-epoch error affects every prediction. In the ideal linear model with uncertainty in epoch and period, Var(t_n)=Var(t0)+n^2 Var(P)+2n Cov(t0,P). If planets gravitationally perturb one another, the actual recurrence need not be exactly linear. Our fixed-period forecasts do not explicitly model such transit timing variations.

## Context from published astronomy

- Edwards et al., *MNRAS* 504, 5671–5684 (2021 issue; online 2020), https://doi.org/10.1093/mnras/staa1245. Their eight-target study illustrates the importance of follow-up timing and updated ephemerides; they used actual observations of different targets and a different method, not our Kepler experiment.
- Lissauer et al., *Planetary Science Journal* 5, 152 (2024), https://doi.org/10.3847/PSJ/ad0e6e, section 2.4 and conclusions. They explain that small formal period uncertainties may not fully account for transit timing variations, particularly over longer timescales. We do not assume a failed forecast is necessarily a TTV; it may reflect noise, an alias, wrong selected planet, data coverage or phase error.

## Relevance to the new replication

The precommitted 13-target replication tests whether the earlier success on Kepler-69 b generalizes to the previously fixed six-planet/seven-binary cohort. It uses identical BLS search bounds for both fits and the same original Q8-duration evaluation window. A named-planet period match (within 2%) and fixed phase evidence are required for the planet-specific endpoint. Known stellar binaries serve as controls because accurate eclipse forecasts do not identify a planetary cause.

[Precommitted protocol](NOV25_MULTIQ_COHORT_PROTOCOL.json) | [Code](nov25_multiq_cohort.py) | [GitHub Actions run](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/45667890631). The derivation above is a theoretical explanation, not a claim about unverified replication results.
