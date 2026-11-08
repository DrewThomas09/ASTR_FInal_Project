"""Post-hoc paired validity audit of the FROZEN Kepler localized-step study.

Reads original archived per-case files. Does not rerun, retune or expand the
astronomical experiment. Paired exact tests are conditional on discordant
cases; repeated trials from one star are not independent stellar sources.
The star-bootstrap below is a descriptive sensitivity analysis, not a survey
population confidence interval. Proxy nulls are not a Kepler false-alarm sample.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest

BASELINE = "standard_bls"
TREATMENT = "localized_step_mask"
METHODS = (BASELINE, "previous_gap_edge_mask", TREATMENT)


def _ensure_cols(df: pd.DataFrame, expected: set[str], name: str) -> None:
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"{name} missing columns: {sorted(missing)}")
    if df.empty:
        raise ValueError(f"{name} must not be empty")
    if not (df.status == "success").all():
        raise ValueError(f"{name} has non-success rows; report exclusions separately")


def _pairs(df: pd.DataFrame, keys: list[str], kind: str) -> pd.DataFrame:
    if df.duplicated(keys + ["method"]).any():
        raise ValueError(f"{kind} has duplicate case/method entries")
    observed = set(df.method.unique())
    if observed != set(METHODS):
        raise ValueError(f"{kind} methods differ from frozen experiment: {observed}")
    n_methods = df.groupby(keys)["method"].nunique()
    if (n_methods != len(METHODS)).any():
        raise ValueError(f"{kind} incomplete paired observations")
    return df


def _cluster_interval(frame: pd.DataFrame, base: str, treatment: str,
                      seed: int, reps: int) -> list[float]:
    """Resample host stars, carrying every within-host realization as a block."""
    if reps < 100:
        raise ValueError("at least 100 bootstrap replicates required")
    by_host = []
    for _, group in frame.groupby("kic"):
        by_host.append((int(group[base].sum()), int(group[treatment].sum()), len(group)))
    blocks = np.asarray(by_host, dtype=float)
    rng = np.random.default_rng(seed)
    sample = rng.integers(0, len(blocks), (reps, len(blocks)))
    selected = blocks[sample]
    vals = ((selected[:, :, 1] - selected[:, :, 0]).sum(axis=1) /
            selected[:, :, 2].sum(axis=1))
    return [float(v) for v in np.quantile(vals, [.025, .975])]


def _compare(frame: pd.DataFrame, b: str, t: str, seed: int, reps: int):
    base = frame[b].astype(bool)
    test = frame[t].astype(bool)
    n = len(frame)
    base_only = int((base & ~test).sum())
    new_only = int((~base & test).sum())
    discordant = base_only + new_only
    p = float(binomtest(new_only, discordant, .5).pvalue) if discordant else 1.
    return {
        "n_matched_cases":n,
        "n_independent_host_stars":int(frame.kic.nunique()),
        "baseline_flagged_or_recovered":int(base.sum()),
        "localized_flagged_or_recovered":int(test.sum()),
        "both":int((base & test).sum()),
        "neither":int((~base & ~test).sum()),
        "baseline_only":base_only,
        "localized_only":new_only,
        "difference_fraction_local_minus_base":float(test.mean() - base.mean()),
        "exact_two_sided_p_conditional_discordance":p,
        "host_block_bootstrap_95_percent_descriptive":_cluster_interval(frame,b,t,seed,reps),
        "per_host_difference": [
           {"kic":int(k),"n":int(len(g)),
            "baseline":int(g[b].astype(bool).sum()),
            "localized":int(g[t].astype(bool).sum()),
            "difference_fraction":float(g[t].astype(bool).mean()-g[b].astype(bool).mean())}
           for k,g in frame.groupby("kic")
        ]
    }


def audit(injections: pd.DataFrame, proxy_nulls: pd.DataFrame,
          thresholds: dict, seed: int = 20261108, reps: int = 10000) -> dict:
    _ensure_cols(injections, {"status","case","kic","condition","method",
       "depth_ppm","recovered","period_correct","peak_score",
       "n_true_transit_cadences_masked","method_removed_cadences"}, "injections")
    _ensure_cols(proxy_nulls, {"status","kic","condition","proxy_index",
                               "method","score"}, "proxy_nulls")
    for m in METHODS:
        if m not in thresholds or not np.isfinite(thresholds[m].get("score_threshold", np.nan)):
            raise ValueError(f"Invalid or absent calibration threshold for {m}")
    _pairs(injections,["case","kic","condition"],"injections")
    _pairs(proxy_nulls,["kic","condition","proxy_index"],"proxy_nulls")
    for case,g in injections.groupby("case"):
        if g["kic"].nunique() != 1 or g["condition"].nunique()!=1 or g["depth_ppm"].nunique()!=1:
            raise ValueError(f"Inconsistent truth for case {case}")
    out = {"study":"Frozen Nov 7 Kepler exoplanet experiment: post-hoc paired audit",
           "input_policy":"Archived raw result CSVs only; no refitting or changing thresholds",
           "calibration_thresholds":{m:float(thresholds[m]["score_threshold"]) for m in METHODS},
           "paired_planet_recovery":[],"paired_proxy_null_flags":[],
           "warnings":[
             "The samples are purposively selected stellar hosts, not random Kepler targets.",
             "The 36 trials per condition are clustered on 6 real stars; binomial and star-bootstrap results are exploratory.",
             "An exact McNemar p-value on paired injections does not establish population significance when host trials are dependent.",
             "The inverted/rolled constructed proxy nulls cannot estimate actual survey false alarm probability.",
             "Same numerical threshold is only a mechanistic sensitivity check, NOT matched false-alarm-rate calibration.",
             "Comparisons were already observed; this audit performs no fresh independent validation or prospective claim."
           ]}
    for i,condition in enumerate(sorted(injections.condition.unique())):
        sub = injections[injections.condition == condition].copy()
        if not np.isfinite(sub.peak_score).all():
            raise ValueError("Nonfinite fitted scores in injection data")
        # Recoveries must match recorded frozen period and detection cutoffs.
        truth = sub.period_correct.astype(bool) & sub.apply(
            lambda r: r.peak_score>thresholds[r.method]["score_threshold"],axis=1)
        if not np.array_equal(truth.to_numpy(),sub.recovered.astype(bool).to_numpy()):
            raise ValueError("Archived recovered labels disagree with frozen thresholds and period test")
        matrix = sub.pivot(index=["case","kic","condition"], columns="method", values="recovered").reset_index()
        cmp = _compare(matrix,BASELINE,TREATMENT,seed+i,reps)
        # Diagnostic only: apply baseline numerical threshold to treatment's score.
        treat = sub[sub.method==TREATMENT].set_index("case")
        base = sub[sub.method==BASELINE].set_index("case")
        if set(treat.index)!=set(base.index):
            raise ValueError("Cannot construct common-threshold pairs")
        same_cutoff = (treat.period_correct.astype(bool) &
                       (treat.peak_score > thresholds[BASELINE]["score_threshold"]))
        cmp["common_baseline_numeric_threshold_diagnostic"] = {
            "standard_recovered_at_original_threshold":int(base.recovered.astype(bool).sum()),
            "step_recovered_at_baseline_numeric_threshold":int(same_cutoff.sum()),
            "note":"Not a same-FAP test: the score distributions and source-dependent control calibration differ."
        }
        # Distinguish any discarded transit measurement from arbitrary cadence masking.
        cmp["localized_mask_costs"]={
           "n_true_transit_cadences_masked":int(treat.n_true_transit_cadences_masked.sum()),
           "n_total_cadences_masked":int(treat.method_removed_cadences.sum()),
           "cases_losing_one_or_more_true_transit_cadences":int((treat.n_true_transit_cadences_masked>0).sum()),
        }
        cmp["condition"]=condition
        out["paired_planet_recovery"].append(cmp)
    for i,condition in enumerate(sorted(proxy_nulls.condition.unique())):
        sub=proxy_nulls[proxy_nulls.condition==condition].copy()
        if not np.isfinite(sub.score).all():
            raise ValueError("Nonfinite proxy-null score")
        sub["flagged"] = sub.apply(lambda r: bool(r.score>thresholds[r.method]["score_threshold"]),axis=1)
        matrix=sub.pivot(index=["kic","condition","proxy_index"],columns="method",values="flagged").reset_index()
        cmp=_compare(matrix,BASELINE,TREATMENT,seed+200+i,reps)
        cmp["condition"]=condition
        out["paired_proxy_null_flags"].append(cmp)
    return out


def write_report(out: dict, dest: Path) -> None:
    lines=["# Paired audit of November 7 frozen Kepler experiment", "",
           "**Scope:** descriptive analysis of archived outcomes. This does not add new observations, rerun BLS, or retune the detector. No exoplanet discovery is claimed.",""]
    lines.extend(["## Paired recovery (same injection, two methods)",""])
    for x in out["paired_planet_recovery"]:
        c=x["condition"]
        lines.append(f"### {c}")
        lines.append(f"Standard BLS recovered **{x['baseline_flagged_or_recovered']}/{x['n_matched_cases']}**; local step mask **{x['localized_flagged_or_recovered']}/{x['n_matched_cases']}**. Exact paired disagreements: {x['baseline_only']} baseline-only and {x['localized_only']} step-only; conditional exact two-sided binomial p = **{x['exact_two_sided_p_conditional_discordance']:.3g}**. Each group comprises only {x['n_independent_host_stars']} independent stellar hosts. This p-value ignores within-star dependence and cannot establish survey performance.")
        ci=x["host_block_bootstrap_95_percent_descriptive"]
        lines.append(f"Observed recovery difference: **{100*x['difference_fraction_local_minus_base']:+.2f} percentage points**; block bootstrap sensitivity range (host resampling, descriptive only) **[{100*ci[0]:+.2f}, {100*ci[1]:+.2f}] pp**. Its boundaries are not proof of a real population effect with just six chosen stars.")
        lines.append(f"At the standard BLS **numerical** threshold: {x['common_baseline_numeric_threshold_diagnostic']['standard_recovered_at_original_threshold']} baseline and {x['common_baseline_numeric_threshold_diagnostic']['step_recovered_at_baseline_numeric_threshold']} step recoveries. This is NOT equal false-alarm-rate calibration. The step mask removed {x['localized_mask_costs']['n_true_transit_cadences_masked']} true transit cadences in {x['localized_mask_costs']['cases_losing_one_or_more_true_transit_cadences']} injected cases.")
        lines.append("")
    lines.extend(["## Constructed proxy-null false triggers",""])
    for x in out["paired_proxy_null_flags"]:
        lines.append(f"- **{x['condition']}**: standard {x['baseline_flagged_or_recovered']}/{x['n_matched_cases']} flagged, step {x['localized_flagged_or_recovered']}/{x['n_matched_cases']}; paired baseline-only {x['baseline_only']}, step-only {x['localized_only']}; exact conditional p = {x['exact_two_sided_p_conditional_discordance']:.3g}. These inverted/rolled synthetic controls are not a measured mission false-alarm rate.")
    lines.extend(["","## Interpretation","",
     "The correct conclusion remains that extra local preprocessing has **not** shown a benefit on unmodified PDC-corrected Kepler measurements. On artificially constructed discontinuities the local mask rescued one specific wrong-period case, but it also deleted genuine transit samples. The chosen sample, proxy controls, heterogeneous stellar noise and shared calibration scores are too weak to establish broad performance gains.","",
     "**Statistical caveat:** The exact paired test is informative about discordant case counts, but because trials share stars, it is not a fully independent astronomical hypothesis test. The host resampling is shown to reveal sensitivity to selection, not as a population-wide confidence interval.","",
     "**Provenance:** Re-run with the unmodified `all_paired_injection_trials.csv`, `heldout_proxy_nulls.csv`, and `frozen_method_thresholds.json` from the original Actions run 42402819710 (artifact 13585948128). Software drafted with generative AI; all observational findings must be reviewed independently by the student."
    ])
    dest.write_text("\n".join(lines)+"\n")


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results",type=Path,required=True,
                        help="Directory extracted from unchanged 2026-11-07 original workflow artifact")
    parser.add_argument("--out",type=Path,default=Path("results/paired_validity_audit"))
    parser.add_argument("--bootstrap-reps",type=int,default=10000)
    args=parser.parse_args()
    inputs=args.results
    result=audit(pd.read_csv(inputs/"all_paired_injection_trials.csv"),
                 pd.read_csv(inputs/"heldout_proxy_nulls.csv"),
                 json.loads((inputs/"frozen_method_thresholds.json").read_text()),
                 reps=args.bootstrap_reps)
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/"paired_audit.json").write_text(json.dumps(result,indent=2))
    write_report(result,args.out/"PAIRED_VALIDITY_AUDIT.md")
    print((args.out/"PAIRED_VALIDITY_AUDIT.md").read_text())

if __name__=="__main__":
    main()

