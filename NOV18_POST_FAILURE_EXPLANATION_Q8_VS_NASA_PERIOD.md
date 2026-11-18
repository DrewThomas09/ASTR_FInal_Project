# Post-failure explanatory check: how much does a more accurate period change the forecast?

**Exploratory analysis planned after seeing the November 18 Q12–Q13 failures. This is NOT another blind holdout.**

The original Quarter 8 BLS fit estimated 13.7133429855 days for Kepler-69 b. The established NASA archive period is 13.7223682 days. We will hold the same Q8-fitted starting transit time and the same duration. For each independently archived Q9–Q13 brightness series, compute the local dip in windows predicted by each of the two *fixed periods*, with exactly the same size windows and nearby reference data.

No fitting to Q9–Q13, no new free timing shift, and no picking a more favorable NASA period. If the NASA-period windows contain deeper dips while the Q8-only predictions stop finding them, it would support the explanation that **small period errors compound over time**, not that the star stopped showing transits.

The NASA reference period was already used as the historical benchmark in the project; this comparison is intended as a physics explanation rather than another measurement of AI model discovery performance.

Source: https://exoplanetarchive.ipac.caltech.edu/overview/Kepler-69

The analysis will also report the number of usable windows and the actual archival FITS SHA-256 values. It does not estimate an independent false-alarm probability.
