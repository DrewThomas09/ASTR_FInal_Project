"""Validation-selected review triage: margin-only versus model-disagreement.

Uses historical NASA Robovetter labels, not independently confirmed planets.
Classifier scores are NOT calibrated astronomical planet probabilities.
"""
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
import ml_screening as base

FEATURES=base.FEATURES


def select_review_cutoff(confidence,target_review=.30):
    values=np.asarray(confidence,dtype=float)
    if len(values)<10 or not np.isfinite(values).all():
        raise ValueError("Need >=10 valid validation confidence values")
    if not 0<target_review<1:
        raise ValueError("target review fraction must be in (0,1)")
    return float(np.quantile(values,target_review))


def triage_evaluation(y,pred,review):
    """All rows are counted; review is neither a success nor a planet detection."""
    y=np.asarray(y,dtype=int)
    pred=np.asarray(pred,dtype=bool)
    review=np.asarray(review,dtype=bool)
    if not(len(y)==len(pred)==len(review)):
        raise ValueError("Array lengths mismatch")
    auto=~review
    wrong=(pred!=y)
    return {"n":int(len(y)),"auto_n":int(auto.sum()),
            "review_n":int(review.sum()),
            "review_fraction":float(review.mean()),
            "auto_wrong_count":int(np.sum(wrong&auto)),
            "auto_error_rate":float(np.mean(wrong[auto])) if auto.any() else None,
            "false_dismissals_auto":int(np.sum((y==1)&(~pred)&auto)),
            "false_acceptances_auto":int(np.sum((y==0)&pred&auto)),
            "candidates_sent_to_review":int(np.sum((y==1)&review)),
            "false_positives_sent_to_review":int(np.sum((y==0)&review)),
            "underlying_binary":base.metrics(y,pred)}


def star_bootstrap_difference(stars,y,pred,baseline_review,enhanced_review,
                              seed=12600,reps=400):
    """Paired bootstrap by host star, preserving intra-star clustering."""
    stars=np.asarray(stars)
    unique,inverse=np.unique(stars,return_inverse=True)
    wrong=(np.asarray(pred)!=np.asarray(y))
    a=np.asarray(baseline_review,dtype=bool)
    b=np.asarray(enhanced_review,dtype=bool)
    rng=np.random.default_rng(seed)
    diffs=[]
    for _ in range(reps):
        drawn=rng.integers(0,len(unique),len(unique))
        weights=np.bincount(drawn,minlength=len(unique))[inverse]
        aa=(~a)*weights
        bb=(~b)*weights
        if aa.sum()==0 or bb.sum()==0:
            continue
        diffs.append(float(np.sum(wrong*bb)/bb.sum()-np.sum(wrong*aa)/aa.sum()))
    if len(diffs)<max(20,reps*.7):
        return {"ci95":None,"reason":"Not enough valid bootstrap draws"}
    return {"ci95":[float(z) for z in np.quantile(diffs,[.025,.975])],
            "direction":"enhanced minus margin-only: negative means less auto error",
            "bootstrap_draws":len(diffs)}




def fixed_budget_mask(uncertainty, fraction):
    """Rank examples by uncertainty WITHOUT labels and review exactly round(n*b)."""
    scores=np.asarray(uncertainty,dtype=float)
    if scores.ndim!=1 or not np.isfinite(scores).all():
        raise ValueError("Expected one finite uncertainty score per example")
    if not 0<=fraction<=1:
        raise ValueError("Budget outside [0,1]")
    n=int(np.floor(len(scores)*fraction+.5))
    selection=np.argsort(-scores,kind="stable")[:n]
    mask=np.zeros(len(scores),dtype=bool)
    mask[selection]=True
    return mask


def per_100_input_metrics(y, pred, review):
    """Review outcomes are unknown, NOT counted as correct classifications."""
    y=np.asarray(y,dtype=int)
    pred=np.asarray(pred,dtype=bool)
    review=np.asarray(review,dtype=bool)
    if not(len(y)==len(pred)==len(review)) or not len(y):
        raise ValueError("Expected equally sized nonempty arrays")
    auto=~review
    wrong=(pred!=y)&auto
    dismissed=(y==1)&(~pred)&auto
    false_accept=(y==0)&pred&auto
    return {
        "review_n":int(review.sum()),
        "review_fraction":float(review.mean()),
        "wrong_auto":int(wrong.sum()),
        "wrong_auto_per_100_input":float(100*wrong.mean()),
        "candidate_false_dismissals_auto":int(dismissed.sum()),
        "candidate_false_dismissals_per_100_candidates":(
            float(100*dismissed.sum()/(y==1).sum()) if np.any(y==1) else None),
        "false_positive_auto_per_100_input":float(100*false_accept.mean()),
        "auto_error_fraction":float(np.mean((pred!=y)[auto])) if auto.any() else None,
    }


def paired_budget_ci(stars,y,pred,a_review,b_review,seed=12600,reps=400):
    """Paired host-star bootstrap difference B minus A in errors per 100 inputs.

    The CI is conditional on fitted models and the realized held-out sample.
    """
    stars=np.asarray(stars)
    unique,inverse=np.unique(stars,return_inverse=True)
    y=np.asarray(y)
    wrong=(np.asarray(pred,dtype=bool)!=y)
    a=np.asarray(a_review,dtype=bool)
    b=np.asarray(b_review,dtype=bool)
    deltas=((wrong&(~b)).astype(float)-(wrong&(~a)).astype(float))
    rng=np.random.default_rng(seed)
    values=[]
    for _ in range(reps):
        ids=rng.integers(0,len(unique),len(unique))
        weights=np.bincount(ids,minlength=len(unique))[inverse]
        values.append(float(100*np.average(deltas,weights=weights)))
    return {"difference_B_minus_A_per_100":float(100*deltas.mean()),
            "ci95":[float(v) for v in np.quantile(values,[.025,.975])],
            "reps":reps,"resampling_unit":"Kepler host star"}


def fair_review_budget_comparison(y,pred,stars,margin,ensemble_stability,
                                  budgets=(.10,.20,.30,.40),seed=12600):
    """Identical binary predictions & exactly equal review counts per budget.

    Random-review baseline averages 100 label-blind random allocations.
    """
    y=np.asarray(y,dtype=int)
    pred=np.asarray(pred,dtype=bool)
    strategies={"margin_only":-np.asarray(margin,dtype=float),
                "margin_plus_disagreement":-np.asarray(ensemble_stability,dtype=float)}
    rows=[]
    reviews_at_30={}
    for budget in budgets:
        for name,uncertainty in strategies.items():
            mask=fixed_budget_mask(uncertainty,budget)
            metrics=per_100_input_metrics(y,pred,mask)
            rows.append({"budget":float(budget),"method":name,**metrics})
            if abs(budget-.30)<1e-8:
                reviews_at_30[name]=mask
        rng=np.random.default_rng(seed+int(budget*10000))
        random_rows=[]
        for _ in range(100):
            mask=fixed_budget_mask(rng.random(len(y)),budget)
            random_rows.append(per_100_input_metrics(y,pred,mask))
        # All methods review identical number of cases, even when budget*n rounds.
        average={}
        for key in ("wrong_auto","wrong_auto_per_100_input",
                    "candidate_false_dismissals_auto",
                    "candidate_false_dismissals_per_100_candidates",
                    "false_positive_auto_per_100_input","auto_error_fraction"):
            values=[item[key] for item in random_rows if item[key] is not None]
            average[key]=float(np.mean(values)) if values else None
        rows.append({"budget":float(budget),"method":"random_review",
                     "review_n":int(random_rows[0]["review_n"]),
                     "review_fraction":float(random_rows[0]["review_fraction"]),
                     **average,"random_replicates":100})
    comparison=pd.DataFrame(rows)
    paired=paired_budget_ci(stars,y,pred,reviews_at_30["margin_only"],
                  reviews_at_30["margin_plus_disagreement"],seed=seed) if (
                  "margin_only" in reviews_at_30) else None
    return comparison,paired,reviews_at_30


def experiment(df,output="results/ml_triage",seed=12600,review_target=.30):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    train,valid,test=base.split_by_star(df,seed)
    y=df["label"].to_numpy(dtype=int)
    stars=df["kepid"].to_numpy()
    X=np.log1p(df[list(FEATURES)].clip(lower=0).astype(float))
    validation=[];holdout=[]
    for i in range(4):
        model=make_pipeline(SimpleImputer(strategy="median"),
            RandomForestClassifier(n_estimators=90,max_depth=9,
                min_samples_leaf=3,random_state=seed+i,n_jobs=-1))
        model.fit(X.iloc[train],y[train])
        validation.append(model.predict_proba(X.iloc[valid])[:,1])
        holdout.append(model.predict_proba(X.iloc[test])[:,1])
    v=np.asarray(validation)
    t=np.asarray(holdout)
    avg_val=v.mean(axis=0);avg_test=t.mean(axis=0)
    std_val=v.std(axis=0);std_test=t.std(axis=0)
    decision=base.cutoff(avg_val,y[valid],.90)
    margin_val=np.abs(avg_val-decision)
    margin_test=np.abs(avg_test-decision)
    # Select uncertainty weighting ONLY on validation stars.
    # Final test-star labels are never used to choose this parameter.
    val_decisions=avg_val>=decision
    weighting_grid=(.01,.02,.04,.08,.16)
    validation_trials=[]
    for weight in weighting_grid:
        uncertainty=-(margin_val/(weight+std_val))
        validation_review=fixed_budget_mask(uncertainty,.30)
        val_metrics=per_100_input_metrics(y[valid],val_decisions,validation_review)
        validation_trials.append({"weight":weight,
            "wrong_auto":val_metrics["wrong_auto"],
            "false_dismissals_auto":val_metrics["candidate_false_dismissals_auto"]})
    # Prefer the conventional margin rule on exact ties.
    chosen_weight=min(validation_trials,key=lambda x:(
        x["wrong_auto"],x["false_dismissals_auto"],-x["weight"]))["weight"]
    stability_val=margin_val/(chosen_weight+std_val)
    stability_test=margin_test/(chosen_weight+std_test)
    margin_cut=select_review_cutoff(margin_val,review_target)
    stability_cut=select_review_cutoff(stability_val,review_target)
    original_review=margin_test<margin_cut
    new_review=stability_test<stability_cut
    pred=avg_test>=decision
    a=triage_evaluation(y[test],pred,original_review)
    b=triage_evaluation(y[test],pred,new_review)
    report={"dataset":"q1_q17_dr25_koi",
            "label_caveat":"Robovetter judgments, not independently confirmed planets",
            "methods":{"margin_only":a,"margin_plus_disagreement":b},
            "train_n":len(train),"validation_n":len(valid),"test_n":len(test),
            "validation_recall_goal":.90,
            "validation_review_goal":review_target,
            "decision_threshold":float(decision),
            "validation_weight_trials":validation_trials,
            "chosen_disagreement_weight":chosen_weight,
            "paired_star_bootstrap":star_bootstrap_difference(
                stars[test],y[test],pred,original_review,new_review,seed),
            "caveat":"Not real-planet probabilities; no true NASA results until data loaded"}
    # Equal-budget comparison: holds binary predictions fixed across policies.
    # Disagreement stabilizer chosen using validation stars only.
    equal_budget, paired_budget, review_masks = fair_review_budget_comparison(
        y[test],pred,stars[test],margin_test,stability_test,seed=seed)
    equal_budget.to_csv(out/"equal_budget_comparison.csv",index=False)
    # Save every held-out score and review assignment for reproducibility.
    holdout=df.iloc[test][["kepid","kepoi_name","koi_period",
                           "koi_model_snr","label"]].copy()
    holdout["model_score"] = avg_test
    holdout["ensemble_disagreement"] = std_test
    holdout["predicted_candidate"] = pred.astype(int)
    holdout["review_margin_30pct"] = review_masks["margin_only"]
    holdout["review_disagreement_30pct"] = review_masks["margin_plus_disagreement"]
    holdout.to_csv(out/"holdout_predictions.csv",index=False)
    report["equal_budget"]={
        "budgets":[.10,.20,.30,.40],
        "strategies":["random_review","margin_only","margin_plus_disagreement"],
        "same_classification_predictions":True,
        "reviewed_cases_count_equal_by_budget":True,
        "paired_error_difference_at_30pct":paired_budget,
        "random_control_repetitions":100,
        "interpretation":"Reallocation of review, not improvement to underlying classifier"}
    fig2,ax2=plt.subplots(figsize=(7.2,4.2))
    for name,part in equal_budget.groupby("method"):
        ax2.plot(part.budget*100,part.wrong_auto_per_100_input,
                 marker="o",label=name.replace("_"," "))
    ax2.set(xlabel="Review budget (% of all signals)",
            ylabel="Incorrect automatic decisions per 100 original signals",
            title="Equal review budgets: same held-out stars")
    ax2.legend(fontsize=8)
    fig2.tight_layout()
    fig2.savefig(out/"equal_budget_tradeoff.png",dpi=170)
    plt.close(fig2)
    groups=[]
    for feature,edges,labels in [
        ("koi_period",[-np.inf,10,100,np.inf],["<10 d","10-100 d",">=100 d"]),
        ("koi_model_snr",[-np.inf,10,30,np.inf],["<10","10-30",">=30"])]:
        bins=pd.cut(df.iloc[test][feature],edges,labels=labels,right=False)
        for label in labels:
            mask=(bins==label).to_numpy(dtype=bool)
            if not mask.any():
                continue
            # Fair subgroup comparison at exactly 30% whole-sample review budget.
            old=triage_evaluation(y[test][mask],pred[mask],
                                  review_masks["margin_only"][mask])
            new=triage_evaluation(y[test][mask],pred[mask],
                                  review_masks["margin_plus_disagreement"][mask])
            groups.append({"variable":feature,"range":label,"n":int(mask.sum()),
                           "margin_review_fraction":old["review_fraction"],
                           "ensemble_review_fraction":new["review_fraction"],
                           "margin_auto_wrong":old["auto_wrong_count"],
                           "ensemble_auto_wrong":new["auto_wrong_count"],
                           "small_group_warning":bool(mask.sum()<25)})
    pd.DataFrame(groups).to_csv(out/"subgroups.csv",index=False)
    pd.DataFrame([
       {"method":name,**{k:val for k,val in d.items() if k!="underlying_binary"}}
       for name,d in report["methods"].items()
    ]).to_csv(out/"triage_summary.csv",index=False)
    fig,ax=plt.subplots(figsize=(7,3.6))
    err=[100*a["auto_error_rate"] if a["auto_error_rate"] is not None else np.nan,
         100*b["auto_error_rate"] if b["auto_error_rate"] is not None else np.nan]
    review=[100*a["review_fraction"],100*b["review_fraction"]]
    pos=np.arange(2)
    ax.bar(pos-.16,err,width=.32,label="Error among auto-decided (%)")
    ax.bar(pos+.16,review,width=.32,label="Sent for review (%)")
    ax.set_xticks(pos,["Margin","Margin + disagreement"])
    ax.set_ylabel("Percent")
    ax.set_title("Held-out star classifications: report the review tradeoff")
    ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(out/"triage_tradeoff.png",dpi=170);plt.close(fig)
    (out/"triage_metrics.json").write_text(json.dumps(report,indent=2))
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--csv",default="data/kepler_dr25.csv")
    p.add_argument("--download",action="store_true")
    p.add_argument("--output",default="results/ml_triage")
    a=p.parse_args()
    print(json.dumps(experiment(base.load_data(a.csv,a.download),a.output),indent=2))
