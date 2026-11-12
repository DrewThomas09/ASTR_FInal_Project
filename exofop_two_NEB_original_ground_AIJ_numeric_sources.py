"""Direct original ground AstroImageJ relative-photometry FITS-independent data.

Two observer-reported on-neighbor cases preselected from original ExoFOP
ground notes and NEBcheck tables BEFORE retrieving these numeric full
ground photometry files. This step preserves source bytes and checks whether
the reported T6/T11 aperture columns/timestamps actually exist.
NO eclipse depth or independent source validation is asserted yet.
"""
import argparse
import hashlib
import io
import json
import math
import re
from pathlib import Path

import pandas as pd
import requests

EXPECTED={
 382437043: {
    "TOI":"1223.01","ground_neighbor_TIC_ID":382437045,
    "original_ExoFOP_file_ID":906268,"AIJ_aperture":"T6",
    "note_original_file_ID":906274,
    "report_original_NEBcheck_file_ID":906269,
 },
 264303333: {
    "TOI":"2250.01","ground_neighbor_TIC_ID":1884344804,
    "original_ExoFOP_file_ID":222159,"AIJ_aperture":"T11",
    "note_original_file_ID":222162,
    "report_original_NEBcheck_file_ID":222160,
 },
}
BASE="https://exofop.ipac.caltech.edu/tess/get_file.php"

def validate_source_csv_table(blob,aperture):
    if not blob or b"\x00" in blob[:4096] or b"<html" in blob[:4096].lower():
        raise ValueError("Original ExoFOP ground-based AIJ table is absent or non-text")
    text=blob.decode("utf-8-sig",errors="strict")
    if "\t" not in text.splitlines()[0]:
        raise ValueError("AstroImageJ ground photometry source is not a tab-separated table")
    table=pd.read_csv(io.StringIO(text),sep="\t",low_memory=False)
    needed=["BJD_TDB","rel_flux_"+aperture]
    missing=[c for c in needed if c not in table.columns]
    if missing:
        raise ValueError("Ground original AIJ source missing actual BJD and reported neighbor aperture: "+str(missing))
    jd=pd.to_numeric(table["BJD_TDB"],errors="coerce")
    flux=pd.to_numeric(table["rel_flux_"+aperture],errors="coerce")
    valid=jd.notna()&flux.notna()&(flux>0)
    if valid.sum()<15:
        raise ValueError("No sufficient genuine ground original AIJ time-series rows for source aperture")
    if jd[valid].min()<2400000 or jd[valid].max()>3000000:
        raise ValueError("Original full BJD must include actual Julian day, not arbitrary timestamp")
    dates=jd[valid].to_numpy(dtype=float) if False else None
    stats={
        "original_AIJ_total_source_rows":int(len(table)),
        "original_AIJ_BJD_TDB_and_neighbor_finite_positive_rows":int(valid.sum()),
        "original_AIJ_first_BJD_TDB":float(jd[valid].min()),
        "original_AIJ_last_BJD_TDB":float(jd[valid].max()),
        "original_AIJ_columns_count":len(table.columns),
        "original_AIJ_relative_flux_columns":[c for c in table.columns if c.startswith("rel_flux_T")],
        "original_ground_reported_neighbor_flux_field":"rel_flux_"+aperture,
        "original_ground_target_flux_field_present":"rel_flux_T1" in table,
        "original_neighbor_aperture_original_observer_reported":aperture,
        "original_neighbor_aperture_physical_ID_mapping_from_observer_note_NOT_independently_derived":True,
        "original_table_numeric_flux_has_NOT_YET_been_used_for_eclipse_measurement":True,
    }
    return stats


def select_original_file(inventory,tic,file_id):
    hosts=[h for h in inventory["all_hosts_with_full_file_and_tseries_evidence"]
           if int(h["TIC_ID"])==int(tic)]
    if len(hosts)!=1:
        raise ValueError("Unexpected original ground catalog host TIC")
    files=[f for f in hosts[0]["original_user_file_evidence_queue"]
           if int(f["original_exofop_file_ID"])==int(file_id)]
    if len(files)!=1 or not str(files[0]["original_file_name"]).lower().endswith(".tbl"):
        raise ValueError("Missing original exact ground measurement .tbl file ID")
    return files[0]


def run(inventory_path,out):
    inventory_path=Path(inventory_path)
    raw=inventory_path.read_bytes()
    inventory=json.loads(raw)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    results=[]
    for tic,info in EXPECTED.items():
        chosen=select_original_file(inventory,tic,info["original_ExoFOP_file_ID"])
        row=dict(info,TIC_ID=tic,original_filename=chosen["original_file_name"])
        url=BASE+"?id="+str(info["original_ExoFOP_file_ID"])
        row["official_ExoFOP_original_file_url"]=url
        try:
            response=requests.get(url,timeout=(25,100),
                headers={"User-Agent":"ASTR-Student-Original-Ground-AstroImageJ-Followup/1.0"})
            response.raise_for_status()
            body=response.content
            if len(body)>25000000:
                raise ValueError("Original uploaded measurement file exceeded 25MB")
            profile=validate_source_csv_table(body,info["AIJ_aperture"])
            dst=out/f"original_TIC{tic}_ExoFOP_file{info['original_ExoFOP_file_ID']}_{chosen['original_file_name']}"
            dst.write_bytes(body)
            row.update(original_table_source_SHA256=hashlib.sha256(body).hexdigest(),
                       original_table_bytes=len(body),
                       verified_original_AIJ_table_source_profile=profile,
                       source_retrieval_status="success")
        except (requests.RequestException,UnicodeDecodeError,ValueError) as exc:
            row.update(source_retrieval_status="failed",
                       source_error=str(exc)[:350],
                       verified_original_AIJ_table_source_profile=None)
        print("GROUND_AIJ_NUMERIC_SOURCE",json.dumps({
            "TIC":tic,"TOI":info["TOI"],"known_neighbor_TIC":info["ground_neighbor_TIC_ID"],
            "observer_aperture":info["AIJ_aperture"],
            "status":row["source_retrieval_status"],
            "stats":row["verified_original_AIJ_table_source_profile"],
            "error":row.get("source_error")
        }),flush=True)
        results.append(row)
    report={
        "purpose":"Two original observer-reported neighboring eclipse targets, exact original ExoFOP AIJ measurement numerical tables source-only validation before flux depth evaluation",
        "original_five_host_ExoFOP_inventory_sha256":hashlib.sha256(raw).hexdigest(),
        "original_two_uploaded_aperture_source_records":results,
        "original_numeric_source_files_with_actual_neighbor_aperture":sum(x["source_retrieval_status"]=="success" for x in results),
        "physical_onsky_eclipsing_neighbor_confirmed_by_independent_flux_reanalysis":False,
        "limitations":[
            "These two targets were selected based on previously examined published ground observer notes and NEBcheck tables; source-file content was unseen before retrieval.",
            "The numerical source files contain original full BJD_TDB and observer-selected neighbor T6/T11 time-series apertures; these are not yet confirmed to dim statistically.",
            "Source ID of an AIJ aperture comes from observer notes, not an independent re-extraction of spatial apertures from sky image.",
            "Instrument-specific trends, dilution, saturation and local comparison stars require further explicit uncertainty checks before physical truth claims."
        ]
    }
    (out/"two_ground_reported_NEB_numeric_AIJ_tseries_original_source_profile.json").write_text(
        json.dumps(report,indent=2)+"\n")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-inventory",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.original_inventory,a.out)
