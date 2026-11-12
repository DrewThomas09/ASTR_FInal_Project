"""Exploratory November 12 original TESS centroid-coverage audit.

Reads *unchanged* source-level outputs of two previously completed original
NASA ExoMiner++ v2.4.0 runs; never retrains model or edits original scores.
The 24-source group was fixed before 2026 score examination but is not known
NASA-training-disjoint. This post-hoc eligibility analysis is not preregistered.

Inputs are recovered from NASA original-source GitHub Actions artifacts:
run 42526063290 and run 42526495887.
"""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr,fisher_exact,rankdata
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEED=20261112

def science(dev_path,new_path,out_path,npermutations=100000):
    dev_path=Path(dev_path);new_path=Path(new_path)
    old=pd.read_csv(dev_path);new=pd.read_csv(new_path)
    needed_dev={"uid","TIC_ID","original_2025_historical_label",
        "corrected_usable_event_count","NASA_2026_period_days"}
    needed_new={"uid","TIC_ID","published_2025_label",
        "corrected_centroid_source_event_count","original_2026_fitted_period_days",
        "original_2026_NASA_score_unchanged","source_ephemeris_identity"}
    if not needed_dev.issubset(old.columns) or not needed_new.issubset(new.columns):
        raise ValueError("Not original NASA source centroid CSV schema")
    if len(old)!=32 or len(new)!=24 or old.TIC_ID.nunique()!=32 or new.TIC_ID.nunique()!=24:
        raise ValueError("Original frozen 32/24 source denominator changed")
    if set(old.TIC_ID)&set(new.TIC_ID):
        raise ValueError("Original 32 and 24 TIC cohorts overlap")
    label=new.published_2025_label
    if any(sum(label==x)!=6 for x in ("KP","CP","EB","NTP")):
        raise ValueError("Frozen 24 source category balance changed")
    n=new.corrected_centroid_source_event_count.to_numpy(dtype=float)
    p=new.original_2026_fitted_period_days.to_numpy(dtype=float)
    if not np.isfinite(n).all() or not np.isfinite(p).all():
        raise ValueError("Missing official source period or real event-window count")
    obs=float(spearmanr(p,n).statistic)
    rng=np.random.default_rng(SEED)
    rx=rankdata(p);ry=rankdata(n)
    rx=rx-rx.mean();ry=ry-ry.mean()
    denominator=float(np.linalg.norm(rx)*np.linalg.norm(ry))
    exceed=0
    for _ in range(npermutations):
        val=float(np.dot(rx,ry[rng.permutation(24)])/denominator)
        exceed+=abs(val)>=abs(obs)-1e-12
    p_perm=(exceed+1)/(npermutations+1)
    rng=np.random.default_rng(SEED+7)
    boot=[]
    for _ in range(10000):
        indices=rng.integers(0,24,size=24)
        if np.unique(p[indices]).size>1 and np.unique(n[indices]).size>1:
            boot.append(float(spearmanr(p[indices],n[indices]).statistic))
    ci=[float(x) for x in np.quantile(boot,[.025,.975])]
    stable=new[new.source_ephemeris_identity=="period_consistent_within_one_percent"]
    if len(stable)!=22:raise ValueError("Period-alias exclusions differ from original 24")
    stable_rho=float(spearmanr(stable.original_2026_fitted_period_days,
                              stable.corrected_centroid_source_event_count).statistic)
    eligible=n>=3
    by={x:{"total":int(sum(label==x)),
        "eligible":int(sum(eligible&(label.to_numpy()==x)))} for x in ("KP","CP","EB","NTP")}
    table=[[by["EB"]["eligible"],6-by["EB"]["eligible"]],
           [by["NTP"]["eligible"],6-by["NTP"]["eligible"]]]
    p_fisher=float(fisher_exact(table,alternative="two-sided").pvalue)
    align=int(sum((new.original_2026_NASA_score_unchanged>=.5)==
                  label.isin(["KP","CP"])))
    data={
      "audit_type":"Exploratory November 12, 2026 source-coverage analysis; NOT prespecified against original 2025 NASA model",
      "official_NASA_v240_star_counts":[32,24],
      "n_original_sources_with_three_complete_event_windows":[
          int(sum(old.corrected_usable_event_count>=3)),int(sum(eligible))],
      "n_not_evaluable_total":int(sum(old.corrected_usable_event_count<3)+sum(~eligible)),
      "new24_spearman_period_vs_qualifying_windows":obs,
      "new24_star_bootstrap_95pct_for_rho":ci,
      "permutation_trials":npermutations,
      "permutation_two_sided_p_plus_one":p_perm,
      "permutation_count_at_least_as_extreme":exceed,
      "period_consistent_22_sources_rho":stable_rho,
      "by_historical_class":by,
      "EB_vs_NTP_fisher_exact_2sided_p_exploratory":p_fisher,
      "EB_vs_NTP_eligible_ineligible_table":table,
      "new24_original_model_agreement_with_older_binary_historical_category_at_point5":align,
      "source_sha256":{dev_path.name:hashlib.sha256(dev_path.read_bytes()).hexdigest(),
                       new_path.name:hashlib.sha256(new_path.read_bytes()).hexdigest()},
      "limits":[
        "P values and intervals only describe the fixed, deliberately class-balanced source sample",
        "Only 22/24 old-event IDs have currently fitted periods agreeing within one percent",
        "Historical labels are not new planet truth; current pretrained model training overlaps unknown",
        "This sample has no accepted historical EB or NTP under the original NASA model, so the proposed additional veto has no such older-label error to correct",
        "Longer periods naturally reduce complete events in finite TESS sectors; rule eligibility is not random"
      ]
    }
    out=Path(out_path);out.mkdir(parents=True,exist_ok=True)
    (out/"real_TESS_24star_source_period_eligibility_summary.json").write_text(json.dumps(data,indent=2)+"\n")
    new.assign(eligible_three_events=eligible).to_csv(out/"all_original_24star_centroid_eligibility.csv",index=False)
    plt.rcParams.update({"font.family":"serif","font.size":10})
    fig,(ax,bx)=plt.subplots(1,2,figsize=(9.5,4.1),layout="constrained")
    markers={"KP":"o","CP":"s","EB":"^","NTP":"D"}
    colors={"KP":"#222222","CP":"#929292","EB":"#782f2f","NTP":"white"}
    for x in markers:
        q=new[label==x]
        ax.scatter(q.original_2026_fitted_period_days,q.corrected_centroid_source_event_count,
                   c=colors[x],edgecolors="#272727",marker=markers[x],s=50,label=x)
    ax.axhline(3,color="#777777",linestyle="--",linewidth=1)
    ax.set(xlabel="Current NASA fitted period (days)",ylabel="Complete original observed centroid-event windows")
    ax.text(.02,.04,f"Spearman rho = {obs:.3f}",transform=ax.transAxes,fontsize=9)
    ax.spines[["top","right"]].set_visible(False)
    ax.legend(frameon=False,ncol=2)
    vals=[by[x]["eligible"] for x in markers]
    y=np.arange(4)
    bx.barh(y,vals,color="#404040")
    bx.barh(y,[6-v for v in vals],left=vals,color="#e9e9e9",edgecolor="#bbbbbb",linewidth=.6)
    bx.set_yticks(y,list(markers))
    bx.invert_yaxis();bx.set_xlim(0,6.6)
    bx.set_xlabel("Original sources (dark = 3+ events)")
    bx.spines[["top","right"]].set_visible(False)
    for i,v in enumerate(vals):bx.text(v+.08,i,f"{v}/6",va="center")
    fig.savefig(out/"Real_TESS_24star_source_coverage_selection_bias.png",dpi=200,bbox_inches="tight")
    plt.close(fig)
    print(json.dumps({k:v for k,v in data.items() if k not in ("source_sha256","limits")},indent=2))
    return data

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--development32",required=True)
    parser.add_argument("--additional24",required=True)
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    science(args.development32,args.additional24,args.out)
