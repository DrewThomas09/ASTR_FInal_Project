"""Original ExoFOP ground-based follow-up evidence inventory for five frozen TESS hosts.

Download original per-TIC ExoFOP file list and time-series observation summary,
record original bytes and SHA256, and select potential light-curve evidence
attachments for human/physical follow-up inspection. A filename, note, or
observational summary alone is NOT ground-truth eclipse-localization proof.
Source identities are frozen in original pre-centroid repository artifact.
"""
import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path

import requests

BASE="https://exofop.ipac.caltech.edu/tess/"
BINARY_LIGHTCURVE = re.compile(
    r"(?:\b(?:lc|light.?curve|photom(?:etry|etric)|time.?series|detrended)\b|"
    r"(?:\.fits(?:\.gz)?|\.csv|\.dat|\.txt|\.tsv)\b)",
    re.I
)
VISUAL_PLOTS = re.compile(r"(?:plot|light.?curve|transit|eclips|photom|\.png|\.pdf|\.jpg)",re.I)
SOURCE_TOKEN = re.compile(r"\bTIC\s*[:#-]?\s*(\d{6,11})\b",re.I)

def original_csv_rows(blob,expected_any):
    try:
        text=blob.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Official ExoFOP source returned non-UTF8 text") from exc
    if text.lstrip()[:1] in ("<","{","[") or text.lower().startswith("error"):
        raise ValueError("Official original ExoFOP source appears HTML/error, not CSV")
    r=csv.DictReader(io.StringIO(text))
    fields=r.fieldnames or []
    if not fields or not any(any(t in field.lower() for t in expected_any) for field in fields):
        raise ValueError("ExoFOP original CSV has no expected field among "+str(fields))
    return list(r),fields


def evidence_queue(file_rows,fields,host_tic,neighbor_tic):
    def field_lookup(row,aliases):
        for key,value in row.items():
            norm=(key or "").lower().strip().replace("_"," ")
            if any(a in norm for a in aliases):
                return str(value or "").strip()
        return ""
    seen=[]
    for row in file_rows:
        name=field_lookup(row,["file name","filename"])
        typ=field_lookup(row,["type"])
        label=field_lookup(row,["description"])
        user=field_lookup(row,["user"])
        date=field_lookup(row,["date"])
        fid=field_lookup(row,["file id","fileid"])
        if not name or not fid:
            continue
        try:
            idnum=int(fid)
        except ValueError:
            continue
        if idnum<=0:
            continue
        annotation=(name+" "+label+" "+typ)
        neighbor_named=str(neighbor_tic) in annotation
        priority = (
            "candidate_numeric_ground_photometry" if BINARY_LIGHTCURVE.search(name+" "+label)
            and re.search(r"\.(?:fits(?:\.gz)?|csv|dat|txt|tsv)$",name,re.I)
            else "candidate_ground_source_plot" if VISUAL_PLOTS.search(annotation)
            else "uncategorized_original_upload"
        )
        seen.append({
            "host_TIC_ID":int(host_tic),"reported_neighbor_TIC_ID":int(neighbor_tic),
            "original_exofop_file_ID":idnum,
            "original_file_name":name,
            "original_file_type":typ,
            "original_observer_supplied_description":label,
            "original_observer_name":user,
            "original_upload_date":date,
            "mentions_reported_neighbor_in_file_metadata":neighbor_named,
            "evidence_category_for_review_NOT_verified":priority,
            "ground_based_photometry_file_bytes_downloaded":False,
            "actual_eclipse_in_specific_neighbor_verified":False
        })
    # Preserve all original IDs; sort deterministically by ID, then name.
    return sorted(seen,key=lambda x:(x["original_exofop_file_ID"],x["original_file_name"]))


def run(frozen_manifest,out,timeout=55):
    p=Path(frozen_manifest)
    raw=p.read_bytes()
    frozen=json.loads(raw)
    if frozen.get("experiment_id")!="ASTR_FIVE_NEW_NEB_SPOC_SOURCE_BLIND_WCS_EVAL_20261112":
        raise ValueError("Incorrect pre-frozen source manifest")
    records=frozen.get("source_records",[])
    if len(records)!=5 or len({int(x["TIC_ID"]) for x in records})!=5:
        raise ValueError("Changed original five host identities")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    hosts=[]
    for x in records:
        tic=int(x["TIC_ID"])
        other=int(x["original_neb_named_neighbor_TIC_not_physical_truth"])
        host={
            "TIC_ID":tic,"TOI":x["TOI"],
            "named_neighbor_candidate_TIC_ID":other,
            "source_note_and_neighbor_catalog_not_sufficient_for_physical_truth":True,
            "TESS_new_source_centroid_result_not_consulted":True,
        }
        for key,route,params in [
            ("filelist","download_filelist.php",{"id":str(tic),"output":"csv"}),
            ("time_series_summaries","download_tseries.php",{"target":str(tic),"output":"csv"})
        ]:
            url=BASE+route
            try:
                r=requests.get(url,params=params,timeout=timeout,
                         headers={"User-Agent":"ASTR-University-Original-Followup-File-Evidence/1.0"})
                r.raise_for_status()
                body=r.content
                if len(body)>40000000:raise ValueError("ExoFOP public evidence table too large")
                # Validate CSV *before* recording it as original source data.
                rows,fields=original_csv_rows(body,["tic","file","toi","telescope","camera","date","filter"])
                path=out/f"ExoFOP_original_TIC{tic}_{key}.csv"
                path.write_bytes(body)
                digest=hashlib.sha256(body).hexdigest()
                host[key]={
                    "status":"success",
                    "original_source_url":r.url,
                    "source_bytes":len(body),"original_source_SHA256":digest,
                    "source_csv_columns":fields,"source_csv_row_count":len(rows),
                }
                if key=="filelist":
                    host["original_user_file_evidence_queue"]=evidence_queue(rows,fields,tic,other)
                    host["candidate_numeric_file_count"]=sum(y["evidence_category_for_review_NOT_verified"]=="candidate_numeric_ground_photometry" for y in host["original_user_file_evidence_queue"])
                    host["candidate_plot_file_count"]=sum(y["evidence_category_for_review_NOT_verified"]=="candidate_ground_source_plot" for y in host["original_user_file_evidence_queue"])
                else:
                    # Save complete, unchanged summaries for human review.  No automated
                    # interpretation of NEB/EB physical source from text labels.
                    host["original_followup_time_series_summary_row_count"]=len(rows)
                    host["example_observation_notes_first_five"]= [
                        {k:str(v)[:500] for k,v in row.items()
                         if k and ("note" in k.lower() or "date" in k.lower() or "type" in k.lower()
                                    or "coverage" in k.lower() or "tel" in k.lower())}
                        for row in rows[:5]
                    ]
            except (requests.RequestException,ValueError) as e:
                host[key]={"status":"error","error":str(e)[:350]}
                if key=="filelist":
                    host["original_user_file_evidence_queue"]=[]
                    host["candidate_numeric_file_count"]=0
                    host["candidate_plot_file_count"]=0
            print("GROUND_SOURCE_EVIDENCE",json.dumps({
                "TIC":tic,"TOI":x["TOI"],"named_neighbor":other,
                "filelist":host.get("filelist",{}).get("status"),
                "file_count":host.get("filelist",{}).get("source_csv_row_count"),
                "potential_numeric_photometry_files":host["candidate_numeric_file_count"],
                "potential_plot_files":host["candidate_plot_file_count"],
                "time_series_summary_count":host.get("original_followup_time_series_summary_row_count"),
                "status_timeseries":host.get("time_series_summaries",{}).get("status")
            }),flush=True)
            if key=="time_series_summaries":
                break
        hosts.append(host)
    result={
        "purpose":"Five pre-frozen actual TESS sources: original uploaded ExoFOP ground followup FILE metadata and TIME SERIES observation summaries",
        "precentroid_frozen_manifest_sha256":hashlib.sha256(raw).hexdigest(),
        "five_host_unique_TICs":len(hosts),
        "original_exofop_file_catalogs_fetched":sum(z.get("filelist",{}).get("status")=="success" for z in hosts),
        "original_exofop_tseries_summaries_fetched":sum(z.get("time_series_summaries",{}).get("status")=="success" for z in hosts),
        "hosts_with_candidate_numeric_ground_photometry_attachment":sum(z.get("candidate_numeric_file_count",0)>0 for z in hosts),
        "all_hosts_with_full_file_and_tseries_evidence":hosts,
        "ground_eclipse_source_truth_verified_count":0,
        "scope":[
            "This is a direct original ExoFOP public evidence retrieval, not original uploaded ground photometric flux reduction.",
            "An ExoFOP file list or observing-summary note cannot independently prove which neighbor eclipsed.",
            "Original observer-uploaded source files must be downloaded and visually/numerically checked before any physical truth claim.",
            "No TESS moment-centroid data, NASA model weights or scores are selected based on external file descriptions.",
            "Keep all five source denominators, missing source files, and conflicting observer notes."
        ]
    }
    (out/"five_new_original_ExoFOP_ground_photometry_FILELIST_AND_TSERIES_inventory.json").write_text(
        json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("SUMMARY",json.dumps({
        "original_five_hosts":len(hosts),
        "original_file_lists":result["original_exofop_file_catalogs_fetched"],
        "original_tseries_summary_tables":result["original_exofop_tseries_summaries_fetched"],
        "host_sources_with_potential_numeric_followup_files":result["hosts_with_candidate_numeric_ground_photometry_attachment"],
        "original_public_uploaded_eclipse_flux_data_verified":0,
        "actual_neb_neighbor_truth_verified":0,
    }),flush=True)
    return result


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--frozen-source-manifest",required=True)
    a.add_argument("--out",required=True)
    x=a.parse_args()
    run(x.frozen_source_manifest,x.out)
