"""Recheck the original frozen Kepler Q6->Q7 two-condition experiment (no refit).
Run: python v12_q6_q7_posthoc_phase_audit.py <original_frozen_forecast.zip>
This is a post hoc eleven-star multiple-comparison check, not a new predictor.
"""
import io,hashlib,json,sys,zipfile
import numpy as np
import pandas as pd
SHA="9eb71ebf72014a8392949923d95e2c9b3cc633047809e10bd0f67229dc558dac"
def main(path):
    raw=open(path,"rb").read()
    assert hashlib.sha256(raw).hexdigest()==SHA
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        stars=pd.read_csv(z.open("all_12_prespecified_sources.csv"))
        events=pd.read_csv(z.open("q7_individual_predicted_event_depths.csv"))
        null=pd.read_csv(z.open("q7_phase_shift_nulls.csv"))
        plan=json.load(z.open("frozen_input_manifest.json"))
    assert len(stars)==12 and len(events)==145 and len(null)==11000
    assert plan["method_frozen"]["no_test_reoptimization"]
    rows=[]
    for star in stars.itertuples():
        if star.status!="both_original_FITS_analyzed":
            assert star.source_name=="Kepler-17";continue
        e=events[events.kic==star.kic];n=null[null.kic==star.kic]
        assert len(n)==1000 and len(e)==int(star.n_usable_predicted_events_q7)
        positive=float((e.local_depth_fraction>0).mean())
        frac=(1+int((n.mean_local_depth>=star.mean_predicted_event_depth).sum()))/(1001)
        assert np.isclose(positive,star.positive_event_fraction)
        assert np.isclose(frac,star.relative_phase_shift_fraction)
        passed=(len(e)>=2 and positive>=.60 and frac<=.01)
        assert passed==bool(star.predictive_evidence)
        rows.append((star.source_name,len(e),positive,frac,passed))
    p=np.array([r[3] for r in rows],float)
    order=np.argsort(p,kind="stable");adj=np.empty(len(p))
    adj[order]=np.minimum(1.0,np.maximum.accumulate((len(p)-np.arange(len(p)))*p[order]))
    assert len(rows)==11 and sum(x[4] for x in rows)==8
    assert (p<=.01).sum()==9 and (adj<=.05).sum()==9
    for row,a in zip(rows,adj):print(row[0],row[1],round(row[2],4),round(row[3],6),round(a,6),row[4])
    print("Frozen successful forecasts: 8/11 observed; post-hoc phase tests under Holm: 9/11")
if __name__=="__main__":main(sys.argv[1])
