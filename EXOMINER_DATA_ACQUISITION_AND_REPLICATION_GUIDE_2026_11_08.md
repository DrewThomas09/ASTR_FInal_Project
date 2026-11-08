# Getting the NASA ExoMiner Data We Need (Practical Reproduction Checklist)
**2026-11-08 | ASTR final project**

**Everything below uses PUBLIC scientific data and source code; no paid NASA access, API key, student upload or license purchase is required.** Hardware/network limits may require staging downloads rather than attempting the full set immediately.

## Start here: what each source actually contains

| Scientific requirement | Exact source | Acquisition | Size / caution |
|---|---|---|---|
| Historical labeled ExoMiner++ TESS candidate scores and TCE labels | **Zenodo v1 record 15466293**, `exominerplusplus_catalog_labeled_tces_s1-s67_tess-spoc-2min_complete_1-14-2025_1039.csv` | Public HTTPS CSV; source fingerprint pinned in [manifest](EXOMINER_PUBLIC_DATA_MANIFEST_2026_11_08.json) | **8,944,735 bytes**, MD5 `c79f3651d556e71f7878a46f960d09b4`; labels are *published* labels, not independent truth |
| 2025 ExoMiner++ UNK TCE vetting scores | Same Zenodo record `exominerplusplus_catalog_unk_tces_s1-s67_tess-spoc-2min_complete_1-16-2025_1014.csv` | Public HTTPS CSV, pinned original checksum | **36,391,080 bytes**, MD5 `0bad0922ea704cf429fd69bacb13b0c9`; unknown TCEs are **not planets proven by the model** |
| Matching 2025 ExoMiner++ tensor training examples | Same Zenodo record `tfrecords_tess-spoc-2min_s1-s67_9-24-2024_1159.tar.xz` | Public HTTPS archive, download only after validating catalog schema and matching original code release | **18,954,105,376 bytes** (~18.95 GB decimal), MD5 `1932be3c3504443e165e6192ace86278`; **does not include Kepler portion** of multi-source paper |
| Exact code used with above 2025 paper | https://github.com/nasa/ExoMiner/releases/tag/v1.0.0 | Clone GitHub with **tag v1.0.0**; lock its commit and environmental dependencies | Paper-matched historical version. Do **not** mix into current 2026 model by default |
| Run NASA's **currently deployed pretrained** TESS ExoMiner++ model on actual TCEs | https://github.com/nasa/ExoMiner/blob/main/docs/running-exominer-pipeline.md | Launch official NASA Podman container with a **TIC ID + sector run** CSV; it automatically fetches MAST SPOC **DV XML, LC FITS and catalog data** | Run time/network/memory depend on source count and ensemble selection; version may be different from v1.0.0 study |
| Original Kepler/TESS photons as processed light curves and target pixel series | https://mast.stsci.edu/ | Public MAST search and target acquisition; programmatic astroquery/lightkurve or direct archived URL | Avoid entire Kepler archive: NASA estimates ~3 TB light-curve data total and ~175 GB per quarter across all targets |
| Known Kepler TCE detections, false alarms, and DV diagnostics | https://exoplanetarchive.ipac.caltech.edu/docs/Kepler_TCE_docs.html; `q1_q17_dr25_tce` via TAP | Select source star/quarter/TCE and retrieve matched TCE parameters and source files | Original ExoMiner (2022) labeled **30,609 TCEs**, not the ~8k selected KOIs in our RF |
| Ground-truth **injections** and false-alarm calibrators to prove a new planet-search benefit | https://exoplanetarchive.ipac.caltech.edu/docs/Kepler_Data_Products_Overview.html | NASA DR25 pixel-level transit injection, inverted and scrambled flux controls and recovery flags | Crucial for **detection completeness at fixed false-alarm rate**; dataset design and selection must be frozen before scoring |

## Pilot phase 1 — acquire actual official labeled/unlabeled catalogs (automated)

Our [download/integrity script](scripts/download_exominer_public_catalogs.py) and [GitHub Actions workflow](.github/workflows/exominer-2025-download-catalogs.yml) are committed. The workflow streams only the **45.3 MB combined public CSVs**, verifies original Zenodo **size and MD5** and writes an inventory of every CSV column, the row counts, and any label-count distributions. **No 19 GB training archive is fetched in this pilot.** Consult the latest Actions run for its actual success/failure; the existence of the workflow alone is not proof of a successful download.

Use locally:
```bash
python scripts/download_exominer_public_catalogs.py \
  --manifest EXOMINER_PUBLIC_DATA_MANIFEST_2026_11_08.json \
  --out results/exominer_public_catalogs
```

**Do not commit 19 GB of training data or FITS telescope files into GitHub source control.** Keep external original data in cache, a local data volume or cloud object storage and record source digests, keys and derived small-metadata outputs in Git. Download labels first, verify identifiers and available official prediction/sector columns, and freeze any new evaluation sample **before inspecting its scores**.

## Pilot phase 2 — real official NASA pretrained inference, no raw-file manual assembling

NASA's **current** pipeline accepts this exact CSV structure:
```csv
tic_id,sector_run
167526485,6-6
```

The [NASA reference sample in our GitHub repo](exominer_official_pilot_tic_sector.csv) and [local Podman launcher](scripts/run_official_exominer_pilot.sh) are installed, but the actual pretrained NASA image **has not yet been executed**, and no resulting NASA predictions are claimed.

On a machine with Podman installed and started, a reliable internet connection and sufficient memory:

```bash
podman pull ghcr.io/nasa/exominer:latest
bash scripts/run_official_exominer_pilot.sh
```

The launcher calls the NASA image with `--tic_ids_fp` and `--data_collection_mode=2min`, `--task=planet-validation`, `--exominer_model=single`, writing outputs under `results/official_exominer_pilot`. This should query the public NASA MAST light curve / DV products and the stellar parameter source automatically. First inspect the actual prediction CSV, missing/source errors and original normalized input plots. **Pin the image version/digest for scientific comparability**: `latest` can change. NASA supports separate photometric-vetting classifications (PC/AFP/NTP); do not mix this with planet validation.

## Phase 3 — build a real independent accuracy and discovery test

For **same-data, same-label model comparison**:
1. Freeze an authentic, *unseen* catalog of host stars and stratified TCE classes, avoiding any overlap with published training/validation stars when possible. The released scores of an already-trained model on its training catalog do **not** constitute independent test results.
2. Run official pretrained ExoMiner++ on exactly those public TESS TCEs; track all failed downloads, multiple sector observations of the same TIC and different aliases of the same event.
3. Add our physically interpretable instrument/alias diagnostic to a compatible, version-pinned model and ablate it against the complete unmodified ExoMiner++ network, not a hand-weakened baseline.
4. Evaluate precision-recall AUC, **recall at fixed validated precision** and class-specific errors with **host-clustered CIs** and preregistered test hypotheses.

For the **more important novel planet detection experiment**, work upstream of ExoMiner:
1. Freeze a separate set of raw Kepler/TESS source hosts and observation periods, with true planetary injection parameters kept hidden from the detection software.
2. Download only those original NASA FITS light curves/pixel files and record checksums, valid cadence counts, and quality bit flags.
3. Run the same BLS/TLS searches with/without any new artifact-sensitive processing.
4. Measure *injected planet recovery* **at the same empirical false alert budget**, as well as independent archived instrumental SPSD controls and known stellar eclipsing binaries. Never treat every cadence or 1,000 phase randomizations on the same star as independent observations.

## What the user needs to do

**To retrieve the CSV catalogs: nothing** — no account credentials are necessary and the GitHub acquisition job can run automatically, subject to the remote archive availability and GitHub resource limits.

**To run the pretrained NASA model:** provide a computer or authorized cloud runtime where Podman can run the official container and download MAST data. We can use a GitHub Actions runner for small pilots *if container and memory limits allow*, but the image has not yet been exercised in this environment.

**To retrain the 2025 CNN exactly:** reserve storage for the ~19 GB compressed TESS TFRecords plus extracted training examples and reproducible compute. The official publication says its Zenodo TESS TFRecords **exclude Kepler inputs**, so obtaining and reproducing the multi-source training experiment may require additional original Kepler data and preprocessing.

## Citations / public official provenance

- NASA ExoMiner++ v1 published dataset, CC BY 4.0: https://zenodo.org/records/15466293 (concept DOI: https://doi.org/10.5281/zenodo.15466292)
- Matching code release: https://github.com/nasa/ExoMiner/releases/tag/v1.0.0
- Current pretrained model guide: https://github.com/nasa/ExoMiner/blob/main/docs/running-exominer-pipeline.md
- Official model v2.1 feature specifications: https://github.com/nasa/ExoMiner/blob/main/docs/models_specs.md
- NASA MAST publicly archived science observations: https://mast.stsci.edu/
- NASA Exoplanet Archive DR25 TCE catalog: https://exoplanetarchive.ipac.caltech.edu/docs/Kepler_TCE_docs.html
- NASA DR25 injections and false-alarm controls: https://exoplanetarchive.ipac.caltech.edu/docs/Kepler_Data_Products_Overview.html

**AI use:** GPT-6 researched sources and authored acquisition manifest, scripts, workflow and this explanation. All results require student verification and course-compliant disclosure.
