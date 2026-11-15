"""Reproduce source-backed Q7 odd/even event-depth audit from original frozen Q6 -> Q7 output.
Usage: python v11_q7_odd_even_reproduction.py kepler_q6_q7_original_20261113.zip
No periods, epochs, candidate labels or original study pass/fail cutoffs are changed.
"""
import hashlib, io, sys, zipfile, json
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

SHA = "9eb71ebf72014a8392949923d95e2c9b3cc633047809e10bd0f67229dc558dac"

def main(source):
    raw=open(source, "rb").read()
    assert hashlib.sha256(raw).hexdigest()==SHA, "Expected unchanged original NASA-derived archive"
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        events=pd.read_csv(io.BytesIO(z.read("q7_individual_predicted_event_depths.csv")))
        cohort=pd.read_csv(io.BytesIO(z.read("all_12_prespecified_sources.csv")))
        plan=json.loads(z.read("frozen_input_manifest.json"))
    assert len(cohort)==12 and len(events)==145
    assert plan["method_frozen"]["no_test_reoptimization"] is True
    rows=[]
    for name,g in events.groupby("source_name"):
        even=(g.loc[g.orbit_index%2==0, "local_depth_fraction"]*1e6).to_numpy()
        odd=(g.loc[g.orbit_index%2==1, "local_depth_fraction"]*1e6).to_numpy()
        p=mannwhitneyu(even,odd,method="exact",alternative="two-sided").pvalue
        rows.append(dict(source_name=name,n_even=len(even),n_odd=len(odd),
            even_median_ppm=float(np.median(even)),
            odd_median_ppm=float(np.median(odd)),nominal_p=float(p)))
    df=pd.DataFrame(rows).sort_values("source_name").reset_index(drop=True)
    order=np.argsort(df.nominal_p.to_numpy())
    raw_adj=np.array([(len(df)-i)*df.nominal_p.iloc[j] for i,j in enumerate(order)])
    adj=np.empty(len(df))
    adj[order]=np.minimum(1.0,np.maximum.accumulate(raw_adj))
    df["holm_11star_p"]=adj
    assert len(df)==11 and (df.holm_11star_p>=.05).all()
    k=df.set_index("source_name").loc["Kepler-35"]
    ratio=k.odd_median_ppm/k.even_median_ppm
    assert abs(ratio-3.357321255)<0.0001
    assert abs(k.nominal_p-2/70)<1e-10
    df.to_csv("v11_kepler_q7_odd_even_all_11.csv",index=False)
    print(df.to_string(index=False))
    print("Kepler-35 larger/smaller parity median:",ratio)
    print("A retrospective physical diagnostic, NOT validated binary screening.")

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("python v11_q7_odd_even_reproduction.py FROZEN_Q6_Q7.zip")
    main(sys.argv[1])
