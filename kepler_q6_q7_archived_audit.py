"""Summarize saved Kepler Q6/Q7 event-morphology tables from original MAST data.
Two quarter-specific BLS fits; not a blind Q6-fitted Q7 prediction.
Usage: python kepler_q6_q7_archived_audit.py event_morphology_artifact.zip
"""
import argparse, io, json, zipfile
import numpy as np
import pandas as pd

SOURCES=[(11804465,"Kepler-12"),(9837578,"Kepler-35")]
def main(archive):
    with zipfile.ZipFile(archive) as z:
        manifests={q:json.loads(z.read(f"real_source_event_shape_summary_Q{q}.json"))
                   for q in [6,7]}
        for kic,name in SOURCES:
            periods=[]; depths=[]
            print(name)
            for q in [6,7]:
                metadata=next(x for x in manifests[q]["source_results"]
                              if x["kic"]==kic)
                events=pd.read_csv(io.BytesIO(
                    z.read(f"KIC{kic}_Q{q}_observed_event_morphology.csv")))
                period=float(metadata["upstream_Q_only_BLS"]["period_days"])
                depth=100*float(np.median(events["signed_local_depth_fraction"]))
                periods.append(period);depths.append(depth)
                print(f"  Quarter {q}: period {period:.10f} d, "
                      f"{len(events)} events, median local depth {depth:.4f}%")
            print(f"  Independent-fit period difference: "
                  f"{abs(periods[0]-periods[1])*86400:.2f} s")
    print("These Q6/Q7 periods are fitted separately, not a blind forecast.")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("event_morphology_artifact")
    main(p.parse_args().event_morphology_artifact)
