"""Find authentic archival two-minute TESS SPOC products for two ExoFOP NEBs.

This is source/product discovery only; no planet classifications, synthetic data,
or acceptance of nearby aperture targets as the original observed target.
"""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

TICS = {54364414: "2041.01", 82302240: "4255.01"}
REQUIRED = ("TIC ID", "TOI", "Epoch (BJD)", "Period (days)", "Duration (hours)")


def source_ephemerides(raw):
    reader = csv.DictReader(raw.decode("utf-8-sig").splitlines())
    if not set(REQUIRED).issubset(reader.fieldnames or []):
        raise ValueError("Original public ExoFOP ephemeris fields missing")
    found = {}
    for row in reader:
        try:
            tic = int(row["TIC ID"])
        except (TypeError, ValueError):
            continue
        if tic not in TICS or str(row["TOI"]).strip() != TICS[tic]:
            continue
        if tic in found:
            raise ValueError("Duplicate ExoFOP target-TOI ephemeris")
        try:
            epoch=float(row["Epoch (BJD)"])
            period=float(row["Period (days)"])
            duration_hours=float(row["Duration (hours)"])
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid original ExoFOP transit epoch/period/duration") from exc
        if not (2457000 < epoch < 2600000 and 0 < period < 3653 and
                0 < duration_hours/24 < .30*period):
            raise ValueError("Unphysical ExoFOP timing or duration for TIC " + str(tic))
        found[tic] = {
            "TIC_ID":tic,"TOI":TICS[tic],
            "original_ExoFOP_epoch_BJD":epoch,
            "original_ExoFOP_epoch_BTJD":epoch-2457000,
            "original_ExoFOP_period_days":period,
            "original_ExoFOP_duration_days":duration_hours/24,
            "reported_sectors_unverified":row.get("Sectors",""),
            "broad_TFOPWG_disposition_not_neighbor_truth":row.get("TFOPWG Disposition",""),
        }
    if set(found)!=set(TICS):
        raise ValueError("Original ExoFOP catalogue missing exact named TIC and TOI rows")
    return found


def compatible_target(observation_target, tic):
    """Refuse a nearby aperture host with a different TIC identification."""
    s=str(observation_target).strip()
    if re.fullmatch(r"\d+",s):
        return int(s)==int(tic)
    return False


def filter_original_products(observations, products, tic):
    """Pure filtering of MAST field dictionaries for independently tested identity."""
    known = {}
    for row in observations:
        if not compatible_target(row.get("target_name"),tic):
            continue
        if str(row.get("provenance_name","")).strip().upper()!="SPOC":
            continue
        try:
            sector=int(row.get("sequence_number"))
            obsid=int(row.get("obsid"))
        except (ValueError,TypeError):
            continue
        if sector<=0:
            continue
        known[obsid]=sector
    result=[]
    exact=f"{tic:016d}"
    for row in products:
        try:
            obsid=int(row.get("obsID"))
        except (ValueError,TypeError):
            continue
        if obsid not in known:
            continue
        file=str(row.get("productFilename",""))
        uri=str(row.get("dataURI",""))
        group=str(row.get("productSubGroupDescription","")).upper()
        if group not in ("LC","TP"):
            continue
        if not (file.endswith("_lc.fits") if group=="LC" else file.endswith("_tp.fits")):
            continue
        if exact not in file or not uri.startswith("mast:"):
            continue
        result.append({
            "TIC_ID":int(tic),"sector":known[obsid],"product_group":group,
            "official_observation_id":obsid,
            "productFilename":file,"MAST_original_dataURI":uri,
            "product_bytes_expected":row.get("size")
        })
    result.sort(key=lambda r:(r["sector"],r["product_group"],r["productFilename"]))
    return result


def tablerows(table):
    out=[]
    for r in table:
        row={}
        for k in table.colnames:
            v=r[k]
            row[k]=v.item() if hasattr(v,"item") else str(v)
            if isinstance(row[k],bytes):
                row[k]=row[k].decode(errors="replace")
        out.append(row)
    return out


def discover(original_csv, out):
    from astroquery.mast import Observations
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    b=Path(original_csv).read_bytes()
    ephemerides=source_ephemerides(b)
    full={}
    for tic,old in ephemerides.items():
        response=dict(old,original_exofop_snapshot_sha256=hashlib.sha256(b).hexdigest())
        try:
            obs=Observations.query_criteria(obs_collection="TESS",target_name=str(tic))
            o=tablerows(obs)
            response["MAST_observations_returned"]=len(o)
            strict=[r for r in o if compatible_target(r.get("target_name"),tic) and
                    str(r.get("provenance_name","")).upper()=="SPOC"]
            response["exact_tic_SPOC_observation_rows"]=len(strict)
            response["observation_provenances_returned"]=sorted(set(
                str(x.get("provenance_name")) for x in o))
            if len(strict)>150:
                raise ValueError("Unexpectedly many original SPOC observation matches")
            if len(strict):
                selected=set(int(s["obsid"]) for s in strict)
                indexed=obs[[int(row["obsid"]) in selected for row in o]]
                products=tablerows(Observations.get_product_list(indexed))
            else:
                products=[]
            r=filter_original_products(strict,products,tic)
            response["exact_original_TESS_SPOC_2min_products"]=r
            sectors=sorted(set(x["sector"] for x in r))
            response["original_SPOC_sectors_with_both_LC_and_TP"]=[
                sector for sector in sectors if {"LC","TP"}.issubset({
                    x["product_group"] for x in r if x["sector"]==sector})
            ]
            response["discovery_status"]="success"
        except Exception as exc:
            response["discovery_status"]="error"
            response["discovery_error"]=str(exc)[:350]
            response["original_SPOC_sectors_with_both_LC_and_TP"]=[]
            response["exact_original_TESS_SPOC_2min_products"]=[]
        full[str(tic)]=response
        print("MAST_DISCOVERY",json.dumps({
            "tic":tic,"toi":old["TOI"],"period":old["original_ExoFOP_period_days"],
            "epoch_BTJD":old["original_ExoFOP_epoch_BTJD"],
            "reported_sectors":old["reported_sectors_unverified"],
            "status":response["discovery_status"],
            "SPOC_observation_rows":response.get("exact_tic_SPOC_observation_rows"),
            "LC_TP_available_sectors":response["original_SPOC_sectors_with_both_LC_and_TP"],
            "error":response.get("discovery_error")
        }),flush=True)
    report={
        "purpose":"MAST authentic 2-minute SPOC LC+TP source discovery for two post-hoc reported NEBs",
        "original_public_exofop_snapshot_sha256":hashlib.sha256(b).hexdigest(),
        "target_count":len(full),
        "cases":full,
        "limitations":[
            "Querying products does not verify FITS header TICID/SECTOR or obtain ground-based source truth.",
            "No new TESS moment-centroid measurement, NASA score, or physical localization evaluated.",
            "If original two-minute SPOC LC/TP is unavailable, do not substitute QLP or TESS-SPOC FFI as equivalent.",
            "Both cases selected post-hoc from earlier observed ExoFOP reports."
        ]
    }
    (out/"two_NEB_TESS_SPOC_original_MAST_product_discovery.json").write_text(
        json.dumps(report,indent=2,default=str)+"\n",encoding="utf-8")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-exofop-csv",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    discover(a.original_exofop_csv,a.out)
