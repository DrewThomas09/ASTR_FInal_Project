"""Read actual uploaded observer notes and NEBcheck reports, preserving original SHA.

This is human-review evidence extraction, not mechanical proof of which star
eclipsed. All observer source documents were fixed by file ID before download.
"""
import argparse
import hashlib
import json
from pathlib import Path

NOTE_IDS={
 357457104:[77058,77430],
 382437043:[906274],
 354442783:[900935],
 66151343:[248979,886161],
 264303333:[222162],
}
TABLE_IDS={
 357457104:[77056,77441],
 382437043:[906269,906272],
 354442783:[242172,900932,1030623],
 66151343:[248978,886150,886159],
 264303333:[213368,222160],
}


def exact_original_source(source_dir,record):
    path=Path(source_dir)/(
        f"TIC{record['host_TIC_ID']}_file{record['original_file_ID']}_"
        f"{record['original_file_name']}")
    if not path.is_file() or record["source_download_status"]!="success":
        raise ValueError("Missing original observer source file")
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=record["original_uploaded_file_source_SHA256"]:
        raise ValueError("Original ExoFOP uploaded ground source SHA256 mismatch")
    return raw.decode("utf-8-sig",errors="replace")


def concise_source_sections(text,max_lines=20):
    lines=[line.strip() for line in text.splitlines() if line.strip()]
    # Preserve original row context; do not convert a negation into a detection.
    likely=[
        (i+1,line) for i,line in enumerate(text.splitlines())
        if any(t in line.lower() for t in (
            "result", "neb", "not detect", "no detect", "ruled out", "cleared",
            "confirmed", "t1 ", "t2 ", "t3 ", "t4 ", "t6 ", "t11 ",
            "tic 1","tic 2","tic 3","tic 5","tic 6"))
    ]
    return {
        "nonempty_lines":len(lines),
        "opening_source_lines":[x[:450] for x in lines[:max_lines]],
        "select_physical_interpretation_cue_lines":[
            {"line":i,"quoted_original_line":s[:750]} for i,s in likely[:40]
        ],
        "source_proof_status":"review_only_original_text_not_reanalyzed_ground_flux"
    }


def run(prior_audit_json,source_dir,original_inventory,out):
    audit=json.loads(Path(prior_audit_json).read_text())
    inventory=json.loads(Path(original_inventory).read_text())
    if len(audit["original_observer_source_file_details"])!=23:
        raise ValueError("Source evidence count no longer the prespecified 23")
    if inventory["five_host_unique_TICs"]!=5:
        raise ValueError("Ground source catalog changed")
    lookup={int(x["original_file_ID"]):x for x in audit["original_observer_source_file_details"]}
    report=[]
    for host in inventory["all_hosts_with_full_file_and_tseries_evidence"]:
        tic=int(host["TIC_ID"])
        neighbors=int(host["named_neighbor_candidate_TIC_ID"])
        item={"host_TIC_ID":tic,"TOI":host["TOI"],
              "reported_neighbor_TIC_ID":neighbors,"observer_notes":[],
              "original_NEBcheck_tables":[],"all_original_AIJ_measurement_filenames_from_inventory":[
                  x["original_file_name"] for x in host["original_user_file_evidence_queue"]
                  if x["original_file_name"].lower().endswith(".tbl")]}
        for ids,key in ((NOTE_IDS,"observer_notes"),(TABLE_IDS,"original_NEBcheck_tables")):
            for fid in ids[tic]:
                if fid not in lookup or int(lookup[fid]["host_TIC_ID"])!=tic:
                    raise ValueError("Original ground source ID not included in pre-specified 23")
                text=exact_original_source(source_dir,lookup[fid])
                details=concise_source_sections(text,max_lines=14 if key=="original_NEBcheck_tables" else 32)
                item[key].append({
                    "source_original_file_ID":fid,
                    "source_original_file_name":lookup[fid]["original_file_name"],
                    "original_source_SHA256":lookup[fid]["original_uploaded_file_source_SHA256"],
                    "original_unedited_reviewer_excerpts":details,
                    "physical_eclipse_source_verified":False
                })
        report.append(item)
        print("ORIGINAL_GROUND_REVIEW",json.dumps({
            "TIC":tic,"TOI":item["TOI"],"neighbor":neighbors,
            "observer_note_openings":[{
                "file_ID":x["source_original_file_ID"],
                "first_lines":x["original_unedited_reviewer_excerpts"]["opening_source_lines"][:14]
            } for x in item["observer_notes"]],
            "NEB_table_headers":[{
                "file_ID":x["source_original_file_ID"],
                "first_lines":x["original_unedited_reviewer_excerpts"]["opening_source_lines"][:10]
            } for x in item["original_NEBcheck_tables"]],
            "all_original_AIJ_table_names":item["all_original_AIJ_measurement_filenames_from_inventory"]
        }),flush=True)
    result={
        "purpose":"Actual original ExoFOP ground followup notes + NEBcheck table content for five fixed TESS host star sources",
        "source_original_23_download_audit_SHA256":hashlib.sha256(Path(prior_audit_json).read_bytes()).hexdigest(),
        "all_five_untouched_source_review_records":report,
        "source_trust_caveats":[
            "Text reviews include contradictory or negated observations, not automatic positive NEB proof.",
            "Original NEBcheck table results need original aperture-specific photometry, source coordinate mapping and timing check to establish physical eclipse source.",
            "No original TESS pointing correction method or five-TIC outcomes were changed on the basis of these notes.",
        ]
    }
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/"original_five_TIC_ground_observer_notes_and_NEBcheck_review.json").write_text(
        json.dumps(result,indent=2)+"\n")
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-23-audit",required=True)
    p.add_argument("--original-files-dir",required=True)
    p.add_argument("--original-inventory",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.original_23_audit,a.original_files_dir,a.original_inventory,a.out)
