"""Retrieve authentic public 2025 ExoMiner++ TESS catalogs only.

Verifies original Zenodo-record md5 + exact byte counts BEFORE use.
Does not fetch the ~19GB TFRecord training archive and does not treat
pretrained ExoMiner candidate scores as independent planet truth.

Usage:
  python scripts/download_exominer_public_catalogs.py \\
    --manifest EXOMINER_PUBLIC_DATA_MANIFEST_2026_11_08.json \\
    --out results/exominer_public_catalogs
"""
import argparse
import collections
import csv
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request


def verified_download(file_spec, target):
    target=Path(target)
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.is_file():
        hash_md5=hashlib.md5()
        size=0
        with target.open("rb") as f:
            for piece in iter(lambda:f.read(1024*1024),b""):
                hash_md5.update(piece)
                size+=len(piece)
        if (hash_md5.hexdigest()==file_spec["md5"] and
            size==file_spec["bytes"]):
            return {"status":"verified_existing","bytes":size,
                    "md5":hash_md5.hexdigest()}
        target.unlink()
    part=target.with_name(target.name+".part")
    for attempt in range(3):
        try:
            request=urllib.request.Request(
                file_spec["download_url"],
                headers={"User-Agent":"ASTR-University-Science-Reproducibility/1.0",
                         "Accept":"*/*"})
            md5=hashlib.md5()
            size=0
            with urllib.request.urlopen(request,timeout=100) as response:
                with part.open("wb") as dest:
                    while True:
                        chunk=response.read(1024*1024)
                        if not chunk: break
                        dest.write(chunk)
                        md5.update(chunk)
                        size+=len(chunk)
            if size!=file_spec["bytes"]:
                raise ValueError(
                    f"Official Zenodo file size mismatch: {size} "
                    f"expected {file_spec['bytes']}")
            if md5.hexdigest()!=file_spec["md5"]:
                raise ValueError(
                    f"Official Zenodo checksum mismatch: {md5.hexdigest()} "
                    f"expected {file_spec['md5']}")
            part.replace(target)
            return {"status":"downloaded_and_verified","bytes":size,
                    "md5":md5.hexdigest()}
        except Exception:
            part.unlink(missing_ok=True)
            if attempt==2: raise
            time.sleep(2*(attempt+1))
    raise AssertionError("Unreachable")


def inspect_csv(path):
    path=Path(path)
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        columns=reader.fieldnames
        if not columns: raise ValueError("Official CSV has no header")
        n=0
        # A set of common published TCE labels. Record all as metadata;
        # never infer any ground truth from an 'unknown' TCE score.
        selected=[col for col in columns if any(
            x in col.lower() for x in (
                "label","disposition","class","sector","tic_id","target_id",
                "tce_id","exominer","score","prob","period"))]
        counts={name:collections.Counter() for name in columns
                if any(x in name.lower() for x in ("label","disposition","class"))
                and len(name)<80}
        for record in reader:
            n+=1
            for key,count in counts.items():
                if len(count)<=30 or record[key] in count:
                    count[record[key]]+=1
    return {"row_count":n,"column_count":len(columns),"all_column_names":columns,
            "key_or_label_column_names":selected,
            "class_label_value_counts_if_available":{
                k:dict(v.most_common(31)) for k,v in counts.items()},
            "data_warning":"Published catalog classifications are not independent verified physical exoplanet truth."}


def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--manifest",default="EXOMINER_PUBLIC_DATA_MANIFEST_2026_11_08.json")
    cli.add_argument("--out",default="results/exominer_public_catalogs")
    args=cli.parse_args()
    manifest=json.loads(Path(args.manifest).read_text())
    if manifest["dataset_version_specific_doi"]!="10.5281/zenodo.15466293":
        raise ValueError("Zenodo version changed; create new frozen source manifest")
    folder=Path(args.out)
    folder.mkdir(parents=True,exist_ok=True)
    results=[]
    for item in manifest["pinned_catalog_files"]:
        if Path(item["key"]).name!=item["key"]:
            raise ValueError("Unexpected output filename")
        print("Official Zenodo catalog",item["role"],item["key"],flush=True)
        observed=verified_download(item,folder/item["key"])
        description=inspect_csv(folder/item["key"])
        results.append({"role":item["role"],"official_name":item["key"],
                        "official_md5":item["md5"],"validation":observed,
                        "contents":description})
        print("Verified:",observed["bytes"],"bytes;",
              description["row_count"],"rows;",
              description["column_count"],"columns",flush=True)
    report={
        "provenance":manifest["dataset_version_specific_doi"],
        "source_manifest":str(args.manifest),
        "catalogs":results,
        "download_large_training_tensors":False,
        "limitations":[
          "These are released NASA ExoMiner++ TESS SPOC event catalogs. Do not evaluate model scores against the same labels used to train and select them and claim an independent holdout.",
          "Catalog rows may contain repeated observing windows of the same TIC and planet. Group by host TIC and related event identifier.",
          "UNKNOWN-labeled ExoMiner scores are potential candidates, NOT confirmed planets.",
          "Replicating CNN training requires matching full input tensors from separate ~19GB archive and the v1.0.0 release.",
          "The operational 2026 pipeline uses a different model/dataset version; do not mix outputs without pinning version and task."
        ]}
    (folder/"inventory_verified_source_and_columns.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({
        "source_doi":report["provenance"],
        "catalog_summary":[{"name":c["role"],"rows":c["contents"]["row_count"],
                            "n_columns":c["contents"]["column_count"],
                            "file_bytes":c["validation"]["bytes"]}
                           for c in results]
    },indent=2),flush=True)


if __name__=="__main__":
    main()
