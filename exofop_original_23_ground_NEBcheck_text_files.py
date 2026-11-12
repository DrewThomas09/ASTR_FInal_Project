"""Retrieve ORIGINAL public ExoFOP ground photometry NEBcheck and observer files.

Frozen file IDs were chosen from the original 184-file ExoFOP inventory
by name, BEFORE examining the files' physical content. Each original source
must match its file-ID and host-TIC in that snapshot. No image analysis or
astrophysical labels are inferred from mere note/filename matches.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import requests

BASE="https://exofop.ipac.caltech.edu/tess/get_file.php"
SELECTION={
  357457104:[77056,77058,77441,77430,77054],
  382437043:[906269,906272,906274],
  354442783:[242172,900932,900935,1030623,242168],
  66151343:[248978,248979,886150,886159,886161,248973],
  264303333:[213368,222160,222162,213367],
}
NEB_CUE=re.compile(
    r"(?i)\b(?:NEB|PNEB|eclips(?:e|ing)|"
    r"not\s+clear|not\s+eclipsing|NEBcheck|neighbor|contaminat|"
    r"phot\.\s*disp|TIC\s*\d{6,11})\b"
)
RECOGNIZED_TEXT=(".txt",".dat",".tbl",".csv")

def chosen_original_file_entries(inventory):
    hosts=inventory["all_hosts_with_full_file_and_tseries_evidence"]
    if {int(h["TIC_ID"]) for h in hosts}!=set(SELECTION):
        raise ValueError("Original frozen five-source evidence inventory changed")
    result=[]
    for h in hosts:
        tic=int(h["TIC_ID"])
        available={int(x["original_exofop_file_ID"]):x for x in h["original_user_file_evidence_queue"]}
        for fid in SELECTION[tic]:
            if fid not in available:
                raise ValueError(f"Original selected uploaded file ID {fid} not found in host {tic} original source inventory")
            item=available[fid]
            name=str(item["original_file_name"])
            if not name.lower().endswith(RECOGNIZED_TEXT):
                raise ValueError(f"Chosen original file is not an expected text photometry or evidence source: {name}")
            if any(x in name for x in ("/","\\","..")):
                raise ValueError("Unsafe uploaded source filename")
            result.append({
                "host_TIC_ID":tic,
                "original_reported_neighbor_TIC_ID":int(h["named_neighbor_candidate_TIC_ID"]),
                "original_file_ID":fid,
                "original_file_name":name,
                "original_description":item.get("original_observer_supplied_description",""),
                "original_observer":item.get("original_observer_name",""),
                "source_public_file_URL":BASE+"?id="+str(fid),
            })
    return result


def inspect_original_text(source_bytes,neighbor_tic,preview_limit=10):
    if not source_bytes:
        raise ValueError("Original uploaded ground observation file is empty")
    raw=source_bytes[:32768].lower()
    if b"<html" in raw[:1000] or b"<!doctype html" in raw[:500]:
        raise ValueError("Original ExoFOP file returned HTML rather than the claimed uploaded source")
    if b"\x00" in source_bytes[:4096]:
        raise ValueError("Original attachment appears binary rather than ground photometry text")
    text=source_bytes.decode("utf-8-sig",errors="replace")
    lines=text.splitlines()
    if not lines:
        raise ValueError("Original uploaded text source has no lines")
    visible=[x.strip()[:290] for x in lines if x.strip()]
    hits=[]
    for i,line in enumerate(lines):
        if NEB_CUE.search(line):
            hits.append({"original_line_number":i+1,"original_line_excerpt":line[:360]})
    matched=[x for x in hits if str(neighbor_tic) in x["original_line_excerpt"]]
    return {
        "original_file_line_count":len(lines),
        "original_excerpt_first_nonblank_lines":visible[:preview_limit],
        "original_physical_source_keyword_line_count":len(hits),
        "original_keyword_context_lines_first_30":hits[:30],
        "number_of_lines_mentioning_canonical_neighbor_TIC":len(matched),
        "original_lines_with_reported_neighbor_first_12":matched[:12],
        "ground_based_neighbor_eclipse_independently_verified":False,
    }


def run(inventory_file,out):
    inventory_file=Path(inventory_file)
    raw_inventory=inventory_file.read_bytes()
    inventory=json.loads(raw_inventory)
    selected=chosen_original_file_entries(inventory)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    items=[]
    for entry in selected:
        row=dict(entry)
        url=row["source_public_file_URL"]
        try:
            r=requests.get(url,timeout=(20,75),headers={
                "User-Agent":"ASTR-University-Public-Original-ExoFOP-Photometry-Source/1.0"
            })
            r.raise_for_status()
            if len(r.content)>16000000:
                raise ValueError("Source uploaded file exceeds safe 16MB text limit")
            value=inspect_original_text(r.content,row["original_reported_neighbor_TIC_ID"])
            row.update(
                source_download_status="success",
                original_uploaded_file_source_SHA256=hashlib.sha256(r.content).hexdigest(),
                original_uploaded_file_size_bytes=len(r.content),
                original_source_text_evidence=value)
            (out/f"TIC{row['host_TIC_ID']}_file{row['original_file_ID']}_{row['original_file_name']}").write_bytes(r.content)
        except (requests.RequestException,ValueError) as exc:
            row.update(source_download_status="failed",
                       original_download_or_source_format_error=str(exc)[:270],
                       original_uploaded_file_source_SHA256=None,
                       original_source_text_evidence=None)
        # Keep true source excerpts, but never convert an excerpt into a verified physical classification.
        print("ORIGINAL_GROUND_SOURCE",json.dumps({
            "host_TIC":row["host_TIC_ID"],
            "reported_neighbor_TIC":row["original_reported_neighbor_TIC_ID"],
            "original_file_ID":row["original_file_ID"],
            "file_name":row["original_file_name"],
            "status":row["source_download_status"],
            "error":row.get("original_download_or_source_format_error"),
            "source_text_first_lines":(
                row["original_source_text_evidence"]["original_excerpt_first_nonblank_lines"][:3]
                if row["original_source_text_evidence"] else []),
            "reported_neighbor_source_mentions":(
                row["original_source_text_evidence"]["number_of_lines_mentioning_canonical_neighbor_TIC"]
                if row["original_source_text_evidence"] else None),
        }),flush=True)
        items.append(row)
    report={
        "purpose":"Source-preserving download of 23 fixed original ExoFOP observer files to inspect ground NEBcheck data and photometry content, NOT automatic eclipse truth",
        "original_five_host_ground_file_inventory_SHA256":hashlib.sha256(raw_inventory).hexdigest(),
        "frozen_external_uploaded_file_ID_selection_by_TIC":{str(k):v for k,v in SELECTION.items()},
        "fixed_original_file_ids_attempted":len(selected),
        "original_text_files_downloaded_and_verified":sum(x["source_download_status"]=="success" for x in items),
        "original_upload_download_failures":sum(x["source_download_status"]!="success" for x in items),
        "new_true_ground_based_NEB_physical_source_labels_verified":0,
        "original_observer_source_file_details":items,
        "research_limitations":[
            "Selection of file IDs was frozen using filenames/descriptions from original inventory, before viewing their physical contents.",
            "An original text NEBcheck source line or a TIC mention is not a physical photometric reanalysis; a source may be ruled out or a control star.",
            "NEBcheck source documents and original full AIJ measurements must be parsed and a neighbor aperture matched explicitly to sky TIC before claiming an eclipse location.",
            "No NASA pretrained exoplanet classification scores, weights, or source labels have changed.",
            "No source with a failed download is silently substituted with a different neighbor file or a fabricated observation."
        ],
    }
    (out/"23_frozen_original_ExoFOP_ground_uploads_NEBcheck_and_photometry_text_audit.json").write_text(
        json.dumps(report,indent=2)+"\n")
    print("SUMMARY",json.dumps({
        "original_files_attempted":len(selected),
        "original_ground_text_files_verified":report["original_text_files_downloaded_and_verified"],
        "original_source_errors":report["original_upload_download_failures"],
        "host_TICs":[int(k) for k in SELECTION],
        "physically_verified_true_eclipsing_neighbor_TICs":0,
    }),flush=True)
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-ground-inventory",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.original_ground_inventory,a.out)
