# November 12, 2026 — original SPOC pixel-mask reality check for two ground-sky-supported nearby eclipses

**New original NASA/TESS result:** Both externally corroborated nearby eclipsing-source TICs are *geometrically within* their first-sector original two-minute SPOC target-pixel-file optimal-SAP **and** flux-weighted moment-centroid pixel masks. Their nearest projected original TESS pixels were selected by both masks. For each source, the SPOC **photometry (APERTURE bit value 2) and moment-centroid (bit value 8) masks were actually identical at the selected pixels**. Original source digest, initial precentroid source lock and original ground WCS source match were verified; **357 scientific regression tests passed**. This establishes likely pixel-level exposure to a neighboring star, **not** the actual fraction of the nearby star's point-response-function light captured.

## Why this matters

The original numerical ground eclipse measurements and the independently cataloged brightness ratios predicted an approximately **293 ppm** diluted TESS brightness dip for TOI-1223.01 and **92.5 ppm** for TOI-2250.01. Original measured SPOC source dips were **351 ppm** and **98.7 ppm**, respectively. The simple model assumes all of both stars' flux enters TESS's photometric measurement. But the target stars and off-target neighbors are distinct sky points at ~24.5″ and ~31.4″ separation, meaning roughly **1–2 native detector pixels apart**. A nearby star may contribute more or less flux than the full-collection approximation, and SAP photometry and MOM centroids need not use the same pixels. We therefore tested their **actual, original archived pipeline-selected masks**, not a guessed TESS aperture.

## Original target pixel source and geometric results

The original TPF files were fetched with the original source-frozen MAST `mast:TESS/product/...` URI and exact TIC/sector identity from the **pre-centroid archived five-source manifest**. Their bytes' SHA256 were preserved in the source audit. The true source catalog sky coordinates were independently corroborated earlier by actual ground-telescope aperture/plate-solved FITS WCS checks (T6 offset **0.436 arcseconds** and T11 **2.202 arcseconds** from the named TIC). Each cataloged neighbor was projected into the actual reference SPOC target pixel **FLUX celestial WCS**, without an assumed camera angle or arcsecond/pixel conversion. The pipeline's source-defined **APERTURE extension** was decoded bitwise: `(mask & 2) != 0` means selected optimal SAP, and `(mask & 8) != 0` means selected moment centroid.

| Independent sky source | Original SPOC sector | Original 2-minute TPF cutout | Target-to-neighbor projected separation | SAP bit-2 selected pixels | Moment bit-8 selected pixels | Neighbor nearest pixel in SAP? | In moment centroid? |
|---|---:|---|---:|---:|---:|---|---|
| **TOI-1223.01**, target TIC382437043, neighbor **TIC382437045** | **1** | **11×11** | **1.23695 original TPF pixels** | **19** | **19** | **Yes** | **Yes** |
| **TOI-2250.01**, target TIC264303333, neighbor **TIC1884344804** | **14** | **11×11** | **1.53924 original TPF pixels** | **16** | **16** | **Yes** | **Yes** |

For TOI-1223.01, the original independent catalog neighbor projects to CCD cutout **(x=4.9873,y=5.0068)**, its nearest pixel **(5,5)**, lying only **0.0144 pixels** from the projected star. The primary target projects to **(5.9453,5.7893)**. For TOI-2250.01, neighbor projects to **(4.8017,5.7228)** with nearest selected pixel **(5,6)** (**0.3408 pixels** from star), primary to **(3.9305,4.4539)**. In both source cutouts, the bits 2/8 selected **identical** sets, not a distinct centroid-only or photometry-only region.

These findings are a physically useful *geometric* precondition for a neighboring eclipsing star to perturb the original moment centroid and blended photometric brightness simultaneously. However, **an aperture pixel covering the star's projected center does not quantify how much of the star's PSF/PRF actually enters the aperture**, and `PDCSAP_FLUX` is not simply a full-image, all-source sum. Consequently, no precise measured source throughput fraction or improved ExoMiner model source localization follows from this source mask experiment.

## Instrument/source limitations and next step

- The original TPF masks are a **source-specific and sector-specific reference data product**, not evidence that their selected pixels are identical across sectors or targets.
- The two neighboring sources are roughly 1.2–1.5 pixels from the primary, so spatial blending is severe and photometric extraction can mix source contributions.
- The exact primary/neighbor positions used here were frozen in earlier independent ExoFOP/ground WCS records, and no source was replaced after inspecting the mask.
- Even though the neighbor's nearest pixel is in both masks, the true flux contributions depend on TESS PRF, optical distortion, subpixel coordinates, aperture shape, background, and source processing.
- The earlier two-source flux agreement (**92.5 ppm expected vs 98.7 ppm observed** in TOI-2250.01) remains **post-hoc physical consistency** and cannot be elevated to a prospectively validated source-location gain.
- A new, independently calculated *original TPF pixel-level true-event minus local pre/post brightness difference image*, compared with fixed ±P/4 pseudo-event differences, may reveal whether changing light is geometrically concentrated around the reported nearby TIC. But it must not be conflated with NASA SPOC's official PRF-calibrated difference-image localization, and can be noisy/crowded at this resolution.

## All-source reproducibility

- [Original source-specific NASA TPF source-mask experiment, **357 tests passed**](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43348300280).
- [Exact two 11×11 TPF original bit-matrices, sky projections, original source SHA and two actual aperture-mask plots](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43348300280/artifacts/14001843974).
- [Original physical ground-neighbor TIC sky checks](VERIFIED_NOV12_ORIGINAL_GROUND_T6_T11_SKY_WCS_TIC_IDENTITY_AND_ECLIPSE.md).
- [Original ground-measured eclipse + observed TESS physical dilution experiment, **355 tests passed**](https://github.com/DrewThomas09/ASTR_FInal_Project/actions/runs/43347801391).
- [Exact original source TPF mask code](tess_two_ground_neb_original_TPF_aperture_mask_check_nov12.py), [synthetic integrity tests](tests/test_tess_two_ground_neb_original_TPF_aperture_mask_check_nov12.py) and [source-pinned workflow](.github/workflows/tess-two-ground-NEB-original-TPF-SAP-vs-MOM-mask.yml).

**AI contribution disclosure:** GPT-6 wrote original TESS source download, pixel mask bit logic, WCS source sky projection, figures, source-hash assertions, tests, research interpretation and this note. Student must independently verify source observations and be explicit about AI assistance.
