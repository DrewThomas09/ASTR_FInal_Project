"""Development-only positive real Kepler SPSD check of the frozen recurrence guard.

KIC 7461601 Q6 was a PREVIOUSLY studied known SPSD in the official STScI
tutorial. This is a historical engineering/physical sanity check ONLY;
it is not an independent control, a survey sensitivity estimate, a new
planet, nor a source to retune any frozen setting against.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import pandas as pd
from recurrence_guard_q6 import evaluate_target, load_protocol
from localized_discontinuity import localized_downward_step_mask

KNOWN_KIC = 7461601
EXPECTED_FITS_SHA = "aa744d4861e56a44b99b7981fd6d729fc1f47ac230e03510d78406c1b073d301"
KNOWN_SOURCE = {
    "kic": KNOWN_KIC,
    "name": "KIC 7461601 official previously published Kepler SPSD example",
    "role": "historical_known_positive_not_an_independent_holdout",
    "source": "https://spacetelescope.github.io/mast_notebooks/notebooks/Kepler/instrumental_noise_4_electronic_noise/instrumental_noise_4_electronic_noise.html"
}


def analyze(out):
    new_settings=load_protocol()["recurrence_guard"]
    old_settings=json.loads(Path("LOCALIZED_STEP_STUDY_FROZEN_2026_11_07.json").read_text())["preprocessing"]
    rows, warnings=evaluate_target(KNOWN_SOURCE,6,old_settings,new_settings)
    if len(rows)!=2:
        raise ValueError("SAP and PDCSAP historical control must both be analyzed")
    if any(row["original_fits_sha256"]!=EXPECTED_FITS_SHA for row in rows):
        raise ValueError("The official known-positive Q6 FITS source was changed")
    if any(row["n_spsd_archival_event_clusters"]==0 for row in rows):
        raise ValueError("Previously documented Q6 quality-bit SPSD is missing")
    output=Path(out);output.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(output/"known_spsd_original_vs_guard.csv",index=False)
    pd.DataFrame(warnings).to_csv(output/"known_spsd_warning_details.csv",index=False)
    report={
        "scope":"KNOWN previously published instrument defect, historical DEVELOPMENT CONTROL only, NOT independent validation",
        "source_kic":KNOWN_KIC,"quarter":6,
        "original_fits_sha256":EXPECTED_FITS_SHA,
        "per_flux_product":rows,
        "observed_warnings":warnings,
        "summary":"The original and guarded masks are unchanged from the frozen design. If the guard protects a known archival SPSD warning, report that as a safety failure; do not change threshold afterward or claim independent control reliability.",
        "source":"STScI official Kepler electronic noise notebook, KIC 7461601 Q6, documented SPSD quality bit1024 (combined example 1152)",
        "limits":"Not a fresh independent holdout, not a statistically valid SPSD sensitivity or false-alarm estimate."
    }
    (output/"known_spsd_safety_summary.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2),flush=True)
    return report


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default="results/known_spsd_safety")
    a=parser.parse_args()
    analyze(a.out)
