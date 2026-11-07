"""External astrophysical sanity check: known Kepler planet versus known binary.

Uses actual Kepler Q8 long-cadence PDC-SAP FITS through the bounded MAST URI
loader. Binary is KIC 10661783 with literature period 1.23136326 d.
Known planet is Kepler-69b, period 13.7223682 d (DR25).
Neither published period is passed to BLS. Outcomes are case studies only.
"""
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from real_kepler_lightcurve import fetch_kepler_quarter
from blind_transit_benchmark import bls_peak
from binary_eclipse_diagnostics import estimate_binary_indicators

CASE_STUDIES=(
  {"target":"KIC 8692861","quarter":8,"type":"confirmed_planet",
   "literature_period_days":13.7223682,"search_range_days":(1.5,20.),
   "reference":"NASA Exoplanet Archive Kepler-69b Q1-Q17 DR25"},
  {"target":"KIC 10661783","quarter":8,"type":"published_eclipsing_binary",
   "literature_period_days":1.23136326,"search_range_days":(.9,6.),
   "reference":"Miszuda et al. 2021 MNRAS doi:10.1093/mnras/stab1597"},
)


def evaluate_case(case,output):
    t,f,info=fetch_kepler_quarter(case["target"],case["quarter"])
    fit=bls_peak(t,f,bounds=case["search_range_days"])
    diag=estimate_binary_indicators(t,f,fit["period_days"],
                      fit["transit_time_days"],fit["duration_days"])
    expected=float(case["literature_period_days"])
    error=abs(fit["period_days"]-expected)/expected
    # A period half or double the literature value is an *alias*, not exact recovery.
    aliases={f"{factor:g}x":float(abs(fit["period_days"]-factor*expected)/(
             factor*expected)) for factor in (.5,1.,2.)}
    result={
        "known_class":case["type"],"published_period_reference":case["reference"],
        "published_period_days":expected,
        "BLS_period_search_bounds":list(case["search_range_days"]),
        "input_file_sha256":info["sha256"],"source":info,
        "measured_peak":fit,
        "period_relative_error":float(error),
        "half_or_double_period_alias_errors":aliases,
        "binary_specific_diagnostics":diag,
        "warning_interpretation":"A warning requests review; no warning does NOT prove a planet",
    }
    label="planet" if case["type"]=="confirmed_planet" else "binary"
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    (out/f"{label}_case.json").write_text(json.dumps(result,indent=2))
    phase=((t-fit["transit_time_days"]+fit["period_days"]/2)%
           fit["period_days"]-fit["period_days"]/2)
    fig,ax=plt.subplots(figsize=(8,3.5))
    ax.scatter(phase,f,s=2)
    ax.set(xlabel="Phase relative to fitted epoch (days)",
           ylabel="Kepler normalized flux",
           title=f"{case['target']} ({case['type'].replace('_',' ')})")
    fig.tight_layout()
    fig.savefig(out/f"{label}_folded.png",dpi=160)
    plt.close(fig)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="results/real_binary_comparison")
    a=p.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    results=[]
    for case in CASE_STUDIES:
        try:
            results.append(evaluate_case(case,out))
        except Exception as ex:
            (out/"run_error.txt").write_text(f"{case['target']}: {type(ex).__name__}: {ex}\n")
            raise
    report={"cases":results,"n_cases":len(results),
       "caution":"Two known systems are sanity checks only, not a sensitivity/false-positive-rate study"}
    (out/"comparison_summary.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
