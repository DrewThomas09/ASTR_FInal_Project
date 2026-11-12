"""Exploratory, source-aligned paired TESS raw-vs-POS_CORR centroid audit.

Original SPOC moment centroid pre/post drift is an instrument-stability PROXY.
This is NOT an independent source-localization validation or a NASA neural
model modification. Archived authentic NASA v2.4.0 source-event data only.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import binomtest,wilcoxon
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SOURCES=[
 ("prior_32","prior32/centroid_physics_analysis",
  "_observed_corrected_original_TESS_centroid_events.csv",
  "_observed_RAW_original_TESS_centroid_events.csv",32),
 ("additional_24","new24/24star_original_TESS_centroid_analysis",
  "_new_holdout_observed_corrected_event_centroids.csv",
  "_new_holdout_observed_raw_event_centroids.csv",24)]
D32="all_32_original_TESS_stars_unchanged_NASA_scores_and_centroid_windows.csv"
D24="all_24_UNSEEN_TO_OUR_CENTROID_RULE_source_TICs_with_NASA_original_scores.csv"
HASH32="84367f439fb58164a28768fd838288d205c6bdd4375c68b6f5e647580c471ea5"
HASH24="5a480b898fd3e54e84f2d60eb4f422a628d3d9e9f08a"

def read_original_events(root):
 rows=[]
 for cohort,relative,cor_suffix,raw_suffix,nstar in SOURCES:
  folder=Path(root)/relative
  csvs=sorted(folder.glob("*"+cor_suffix))
  if len(csvs)!=nstar:raise ValueError("Original frozen source star count changed: "+cohort)
  for cp in csvs:
   uid=cp.name[:-len(cor_suffix)]
   raw=folder/(uid+raw_suffix)
   if not raw.is_file():raise ValueError("Missing matching original raw TESS source event "+uid)
   c=pd.read_csv(cp);r=pd.read_csv(raw)
   keys=["orbit_index","predicted_NASA_TCE_center_BTJD"]
   if c.duplicated(keys).any() or r.duplicated(keys).any():raise ValueError("Duplicate original orbit")
   d=c.merge(r,on=keys,how="outer",validate="one_to_one",
             suffixes=("_corrected","_raw"),indicator=True)
   if len(d)!=len(c) or len(d)!=len(r) or not (d._merge=="both").all():
    raise ValueError("Original same-source orbit alignment failed "+uid)
   for row in d.itertuples(index=False):
    rec=dict(uid=uid,cohort=cohort,TIC_ID=int(uid.split("-")[0]),
       orbit_index=int(row.orbit_index),
       predicted_NASA_TCE_center_BTJD=float(row.predicted_NASA_TCE_center_BTJD))
    for prefix,field in [
       ("prepost","local_pre_post_vector_norm_pixels"),
       ("event","local_in_minus_flanking_vector_norm_pixels")]:
     for mode in ("raw","corrected"):
      x=float(getattr(row,field+"_"+mode))
      if not np.isfinite(x) or x<0:raise ValueError("Invalid measured TESS centroid quantity")
      rec[prefix+"_"+mode+"_pixels"]=x
    rows.append(rec)
 e=pd.DataFrame(rows)
 if len(e)!=248 or e.uid.nunique()!=56 or e.duplicated(["uid","orbit_index"]).any():
  raise ValueError("Must reproduce exactly 248 original NASA/TESS event pairs on 56 distinct original sources")
 return e

def run(root,out):
 root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=True)
 original={
   D32:root/"prior32/centroid_physics_analysis"/D32,
   D24:root/"new24/24star_original_TESS_centroid_analysis"/D24}
 for name,expected in [(D32,HASH32),(D24,HASH24)]:
  actual=hashlib.sha256(original[name].read_bytes()).hexdigest()
  if actual!=expected:raise ValueError("Original previously audited NASA source file SHA256 mismatch: "+name)
 e=read_original_events(root)
 grp=e.groupby(["uid","cohort","TIC_ID"],as_index=False).agg(
   n_source_observed_events=("orbit_index","size"),
   raw_prepost_pixel_median=("prepost_raw_pixels","median"),
   corrected_prepost_pixel_median=("prepost_corrected_pixels","median"),
   raw_event_pixel_median=("event_raw_pixels","median"),
   corrected_event_pixel_median=("event_corrected_pixels","median"))
 for metric in ("prepost","event"):
  grp["paired_"+metric+"_raw_minus_corrected_pixels"]=grp[
    "raw_"+metric+"_pixel_median"]-grp["corrected_"+metric+"_pixel_median"]
 if len(grp)!=56 or not (grp.n_source_observed_events>0).all():raise AssertionError("Missing source")
 rng=np.random.default_rng(20261112)
 def compare(metric):
  r=grp["raw_"+metric+"_pixel_median"].to_numpy()
  c=grp["corrected_"+metric+"_pixel_median"].to_numpy()
  d=r-c
  boot=rng.integers(0,56,size=(20000,56))
  q=np.quantile(np.median(d[boot],axis=1),[.025,.975])
  return dict(n_sources=56,
    original_raw_median_of_star_medians_pixels=float(np.median(r)),
    corrected_median_of_star_medians_pixels=float(np.median(c)),
    median_paired_star_difference_pixels=float(np.median(d)),
    whole_star_20k_bootstrap_95pct_difference_pixels=q.tolist(),
    n_source_stars_with_less_drift_after_adjustment=int((d>0).sum()),
    n_source_stars_with_more_drift_after_adjustment=int((d<0).sum()),
    exploratory_two_sided_sign_test_p=float(binomtest(int((d>0).sum()),56).pvalue),
    exploratory_wilcoxon_signed_rank_p=float(wilcoxon(r,c).pvalue),
    event_level_windows_reduced=int((e[metric+"_raw_pixels"]>e[metric+"_corrected_pixels"]).sum()))
 good=grp[grp.n_source_observed_events>=3]
 d=good.paired_prepost_raw_minus_corrected_pixels
 summary={
   "source_reference":"Original NASA ExoMiner++ v2.4.0 archived TESS SPOC 2-minute raw and experimentally POS_CORR-subtracted moment-centroid source event tables",
   "source_cohorts":{"previously_seen_stars":32,"later_new_to_student_stars":24},
   "n_original_source_TICs":len(grp),"n_original_matched_observed_event_windows":len(e),
   "n_stars_eligible_for_old_3event_rule":len(good),
   "prepost_pointing_stability_PROXY_not_ground_truth":compare("prepost"),
   "event_related_shift_not_classification_accuracy":compare("event"),
   "at_least_3event_sensitivity":{
      "sources":len(good),"reduced":int((d>0).sum()),"increased":int((d<0).sum()),
      "paired_median_reduction_pixels":float(d.median()),
      "exploratory_two_sided_source_sign_test_p":float(binomtest(int((d>0).sum()),len(good)).pvalue)},
   "cohorts":{},
   "original_source_sha256":{D32:HASH32,D24:HASH24},
   "scope_warnings":[
      "Exploratory post-hoc analysis of previously inspected original NASA stars; cannot infer generalization to NASA network-training-held-out sources.",
      "Pre/post source moment-centroid displacement is only a local proxy for drift and not astrophysical transit-source ground truth.",
      "Pointing subtraction may suppress real off-target eclipses; reduced event shifts do not imply better planet classification.",
      "The full authentic ExoMiner already uses pixel/centroid and DV inputs; the sidecar does not change model scores or weights.",
      "Stars, rather than 248 repeated event windows, are the independent units of resampling. Observational systematics remain."
   ]}
 for cohort,g in grp.groupby("cohort"):
  summary["cohorts"][cohort]=dict(
    source_stars=len(g),source_event_windows=int(g.n_source_observed_events.sum()),
    reduced=int((g.paired_prepost_raw_minus_corrected_pixels>0).sum()),
    increased=int((g.paired_prepost_raw_minus_corrected_pixels<0).sum()))
 e.to_csv(out/"248_original_TESS_raw_and_corrected_centroid_event_pairs.csv",index=False)
 grp.to_csv(out/"56_original_TESS_source_paired_centroid_medians.csv",index=False)
 (out/"TESS_pointing_adjustment_source_robustness_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
 plt.rcParams.update({"font.family":"serif","font.serif":["Times New Roman","Liberation Serif","DejaVu Serif"],"font.size":9.5})
 fig,(ax,bx)=plt.subplots(1,2,figsize=(10,4.5))
 for cohort,g in grp.groupby("cohort"):
  ax.scatter(g.raw_prepost_pixel_median,g.corrected_prepost_pixel_median,
   s=35,marker="o" if cohort=="prior_32" else "s",
   c="#333333" if cohort=="prior_32" else "#75464b",
   label="Earlier 32" if cohort=="prior_32" else "Additional 24",alpha=.85)
 lim=1.08*max(grp.raw_prepost_pixel_median.max(),grp.corrected_prepost_pixel_median.max())
 ax.plot([0,lim],[0,lim],color="#888888",linestyle="--",linewidth=1)
 ax.set(xlim=(0,lim),ylim=(0,lim),xlabel="Raw pre/post centroid displacement (pixels)",
 ylabel="After POS_CORR subtraction (pixels)",title="Source-level before/after stability")
 ax.spines[["top","right"]].set_visible(False);ax.legend(frameon=False,fontsize=8)
 diff=grp.paired_prepost_raw_minus_corrected_pixels.to_numpy()*1000
 edges=np.linspace(diff.min()-.3,diff.max()+.3,16)
 for low,high in zip(edges[:-1],edges[1:]):
  count=int(((diff>=low)&(diff<high)).sum())
  bx.bar((low+high)/2,count,width=(high-low)*.94,
    color="#494949" if (low+high)>=0 else "#996f71")
 bx.axvline(0,color="#444444",linestyle="--")
 bx.axvline(float(np.median(diff)),color="#75464b",linewidth=1.2,label="Median paired reduction")
 bx.set(xlabel="Raw minus adjusted difference (millipixels)",ylabel="Stars",
        title="44 reduced; 12 increased")
 bx.legend(frameon=False,fontsize=8);bx.spines[["top","right"]].set_visible(False)
 fig.suptitle("Original TESS source-centroid correction: paired 56-star test",fontsize=13)
 fig.subplots_adjust(left=.09,right=.98,wspace=.29,top=.82,bottom=.19)
 fig.savefig(out/"Original_TESS_56star_pointing_robustness_source_plot.png",dpi=185,bbox_inches="tight")
 print(json.dumps(summary,indent=2))
 return summary

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--source-root",required=True);p.add_argument("--out",required=True)
 a=p.parse_args();run(a.source_root,a.out)
