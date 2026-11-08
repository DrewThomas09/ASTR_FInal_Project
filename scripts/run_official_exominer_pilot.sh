#!/usr/bin/env bash
# Official pretrained NASA ExoMiner++ TESS pipeline runner (not our own model).
# Requires local Podman, internet, and the NASA container image. This script
# has NOT been executed or claimed to produce official scores in this repo.
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
tic_csv="$repo_root/exominer_official_pilot_tic_sector.csv"
out_dir="${1:-$repo_root/results/official_exominer_pilot}"
if ! command -v podman >/dev/null 2>&1; then
    echo "Podman not installed; see NASA docs https://github.com/nasa/ExoMiner/blob/main/docs/running-exominer-pipeline.md" >&2
    exit 2
fi
if [ ! -f "$tic_csv" ]; then
    echo "Missing NASA sample TIC CSV: $tic_csv" >&2
    exit 2
fi
mkdir -p "$out_dir"

echo "This runs the ORIGINAL official NASA TESS ExoMiner++ planet-validation model,"
echo "not our four-feature Kepler RF and not a new planet search."
echo "Reference TIC/sector comes from NASA's public ExoMiner run guide."
echo "Model: single pretrained NASA model. Results remain unverified until CSV and logs inspected."
echo "The container may download multiple public MAST data products."

podman pull ghcr.io/nasa/exominer
podman run --rm \
  --pids-limit=-1 \
  --shm-size=8g \
  -e OPENBLAS_NUM_THREADS=1 \
  -e OMP_NUM_THREADS=1 \
  -e TF_NUM_INTRAOP_THREADS=1 \
  -e TF_NUM_INTEROP_THREADS=1 \
  -v "$tic_csv:/tics_tbl.csv:ro" \
  -v "$out_dir:/outputs" \
  ghcr.io/nasa/exominer \
  --tic_ids_fp=/tics_tbl.csv \
  --output_dir=/outputs \
  --data_collection_mode=2min \
  --num_processes=1 \
  --num_jobs=1 \
  --get_mast_urls_dv_reports=false \
  --stellar_parameters_source=tess-spoc \
  --ruwe_source=unavailable \
  --task=planet-validation \
  --exominer_model=single \
  --max_model_workers=1

echo "Inspect $out_dir/predictions_spoc-tces_set.csv, all source failures and provenance."
echo "The existence of a score does NOT confirm a planet."
