"""Original SPOC 2-minute TESS event centroid versus independently cataloged NEB.

Original TOI-4255.01 target is TIC 82302240, with external ExoFOP reported
eclipsing source TIC 82302236. Uses original ExoFOP timing and source
coordinates; original MAST SPOC LC and TPF (WCS) only. Exploration/post-hoc.
This is NOT a new planet or an improvement to NASA ExoMiner++.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import urlencode

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.wcs import WCS

from tess_original_moment_centroid_companion import (
    load_tess_centroid_columns, event_centroid_shifts
)

TIC=82302240
NEIGHBOR=82302236
TOI="4255.01"
KNOWN_SECTORS=(61,62)
MAST_FILE_ENDPOINT="https://mast.stsci.edu/api/v0.1/Download/file"


def select_exact_source_products(report):
    if not isinstance(report,dict) or str(TIC) not in report.get("cases",{}):
        raise ValueError("No original source-verified MAST discovery for exact TIC")
    items=report["cases"][str(TIC)].get("exact_original_TESS_SPOC_2min_products",[])
    selected={}
    for sector in KNOWN_SECTORS:
        group={}
        for kind in ("LC","TP"):
            matches=[r for r in items if int(r["TIC_ID"])==TIC and
                     int(r["sector"])==sector and r["product_group"]==kind and
                     f"{TIC:016d}" in r["productFilename"] and
                     r["MAST_original_dataURI"].startswith("mast:TESS/product/")]
            if len(matches)!=1:
                raise ValueError(
                    f"Expected exactly one original TIC {TIC} sector {sector} {kind}; observed {len(matches)}"
                )
            group[kind]=matches[0]
        selected[sector]=group
    return selected


def download_original_mast(uri,destination,max_bytes=380000000):
    """Request original MAST bytes, fail on HTML, errors or oversized files."""
    if not uri.startswith("mast:TESS/product/") or ".." in uri:
        raise ValueError("Not an original TESS MAST product URI")
    path=Path(destination)
    path.parent.mkdir(parents=True,exist_ok=True)
    h=hashlib.sha256();amount=0
    with requests.get(MAST_FILE_ENDPOINT,params={"uri":uri},stream=True,timeout=(30,150)) as r:
        r.raise_for_status()
        with path.open("wb") as handle:
            for block in r.iter_content(chunk_size=1048576):
                if not block:continue
                amount+=len(block)
                if amount>max_bytes:
                    path.unlink(missing_ok=True)
                    raise ValueError("Original MAST product exceeded maximum accepted size")
                h.update(block)
                handle.write(block)
    with path.open("rb") as source:
        if source.read(6)!=b"SIMPLE":
            raise ValueError("Official MAST product is not original FITS bytes")
    return {"source_bytes":amount,"source_sha256":h.hexdigest(),
            "official_product_uri":uri,"source_filename":path.name}


def neighbor_catalog_row(csv_bytes):
    import csv,io
    reader=csv.DictReader(io.StringIO(csv_bytes.decode("utf-8-sig")))
    cols=reader.fieldnames or []
    needed=["TIC ID","RA","Dec","Separation (arcsec)",
            "Position Angle (deg E. of N.)"]
    if not set(needed).issubset(cols):
        raise ValueError("Original nearby astrometry lacks RA/Dec or source geometry")
    hits=[]
    for row in reader:
        try:
            if int(row["TIC ID"])!=NEIGHBOR:continue
            ra=float(row["RA"]);dec=float(row["Dec"])
            sep=float(row["Separation (arcsec)"])
            pa=float(row["Position Angle (deg E. of N.)"])
        except (TypeError,ValueError) as e:
            raise ValueError("Invalid original neighbor astrometry") from e
        if not (0<=ra<360 and -90<=dec<=90 and 0<sep<1000 and 0<=pa<360):
            raise ValueError("Unphysical original catalog neighbor coordinates")
        hits.append({"neighbor_TIC":NEIGHBOR,"neighbor_RA_deg":ra,
                     "neighbor_Dec_deg":dec,"catalog_separation_arcsec":sep,
                     "catalog_position_angle_deg":pa})
    if len(hits)!=1:
        raise ValueError("No unique independent catalog row for original neighbor TIC")
    return hits[0]


def sky_wcs_from_tpf(path,tic,sector):
    """Build genuine TPF FLUX column-5 TAN WCS from original FITS header.

    TPF WCS maps small image pixel x/y to sky and is parallel to CCD
    column/row. A translation of pixel origin does not affect direction.
    """
    with fits.open(path,memmap=False) as hdus:
        h0=hdus[0].header
        if int(h0.get("TICID",-1))!=int(tic) or int(h0.get("SECTOR",-1))!=int(sector):
            raise ValueError("Original TPF FITS TICID/SECTOR does not match LC or TOI")
        h=hdus[1].header
        required=("1CRPX5","2CRPX5","1CRVL5","2CRVL5",
                  "1CDLT5","2CDLT5","1CTYP5","2CTYP5",
                  "11PC5","12PC5","21PC5","22PC5")
        missing=[k for k in required if k not in h]
        if missing:
            raise ValueError("Original TPF FLUX WCS missing: "+",".join(missing))
        w=WCS(naxis=2)
        w.wcs.crpix=[float(h["1CRPX5"]),float(h["2CRPX5"])]
        w.wcs.crval=[float(h["1CRVL5"]),float(h["2CRVL5"])]
        w.wcs.cdelt=[float(h["1CDLT5"]),float(h["2CDLT5"])]
        w.wcs.pc=np.array([[float(h["11PC5"]),float(h["12PC5"])],
                          [float(h["21PC5"]),float(h["22PC5"])]])
        w.wcs.ctype=[str(h["1CTYP5"]),str(h["2CTYP5"])]
        w.wcs.cunit=["deg","deg"]
        if not ("RA" in w.wcs.ctype[0].upper() and
                "DEC" in w.wcs.ctype[1].upper()):
            raise ValueError("Unexpected original TPF celestial coordinate axes")
        target=SkyCoord(float(h0["RA_OBJ"])*u.deg,float(h0["DEC_OBJ"])*u.deg)
        return w,target,{
            "original_TPF_header_target_RA_deg":float(h0["RA_OBJ"]),
            "original_TPF_header_target_Dec_deg":float(h0["DEC_OBJ"]),
            "camera":int(h0.get("CAMERA",-1)),
            "ccd":int(h0.get("CCD",-1)),
            "sector":sector,
            "original_WCS_reference":"SPOC TPF PIXELS extension, original FLUX column-5 TAN WCS, reference cadence",
        }


def position_geometry(w,target,neighbor_catalog):
    n=SkyCoord(neighbor_catalog["neighbor_RA_deg"]*u.deg,
               neighbor_catalog["neighbor_Dec_deg"]*u.deg)
    pa=float(target.position_angle(n).deg)%360
    sep=float(target.separation(n).arcsec)
    nominal_sep=float(neighbor_catalog["catalog_separation_arcsec"])
    pa_error=abs((pa-neighbor_catalog["catalog_position_angle_deg"]+180)%360-180)
    x0,y0=w.all_world2pix(float(target.ra.deg),float(target.dec.deg),0)
    x1,y1=w.all_world2pix(float(n.ra.deg),float(n.dec.deg),0)
    v=np.array([x1-x0,y1-y0],dtype=float)
    if not np.isfinite(v).all() or np.linalg.norm(v)<=0:
        raise ValueError("Original TPF WCS cannot map real target-to-neighbor vector")
    # Verification of matched independent positions; no forcing fit.
    trustworthy=(abs(sep-nominal_sep)<=max(1.2,.20*nominal_sep) and pa_error<=17)
    return {
        "target_to_neighbor_CCD_pixel_vector":v.tolist(),
        "neighbor_catalog_separation_arcsec":nominal_sep,
        "header_to_neighbor_angular_separation_arcsec":sep,
        "header_to_neighbor_position_angle_deg":pa,
        "position_angle_difference_from_original_catalog_deg":pa_error,
        "catalog_sky_geometry_consistent_with_TPF_target_position":bool(trustworthy),
        "expected_simple_two_source_moment_centroid_direction_CCD":(-v/np.linalg.norm(v)).tolist(),
        "original_TPF_WCS_target_cutout_pixel":[float(x0),float(y0)],
        "original_TPF_WCS_neighbor_cutout_pixel":[float(x1),float(y1)],
    }


def physical_away_alignment(vector,target_to_neighbor):
    v=np.asarray(vector,dtype=float)
    toward=np.asarray(target_to_neighbor,dtype=float)
    if v.shape!=(2,) or toward.shape!=(2,) or not np.isfinite(v).all() or not np.isfinite(toward).all():
        raise ValueError("Invalid WCS-aligned centroid vector")
    nv=float(np.linalg.norm(v));nr=float(np.linalg.norm(toward))
    if nv==0 or nr==0:return None
    cos=float(np.clip(-np.dot(v,toward)/(nv*nr),-1,1))
    return float(np.rad2deg(np.arccos(cos)))


def paired_original_events(frame,period,epoch,duration,geometry=None):
    raw=event_centroid_shifts(frame,period,epoch,duration,mode="raw")
    corrected=event_centroid_shifts(frame,period,epoch,duration,mode="corrected")
    r={int(e["orbit_index"]):e for e in raw}
    c={int(e["orbit_index"]):e for e in corrected}
    if len(r)!=len(raw) or len(c)!=len(corrected):
        raise ValueError("Duplicate source event orbit")
    pairs=[]
    for orbit in sorted(set(r)&set(c)):
        a,b=r[orbit],c[orbit]
        if abs(a["predicted_NASA_TCE_center_BTJD"]-b["predicted_NASA_TCE_center_BTJD"])>1e-10:
            raise ValueError("Original paired source epoch disagreement")
        row={
          "orbit_index":orbit,
          "original_ephemeris_predicted_center_BTJD":a["predicted_NASA_TCE_center_BTJD"],
          "n_actual_quality_zero_inside_cadences":a["n_cadences_inside"],
          "n_actual_pre_event_cadences":a["n_cadences_pre"],
          "n_actual_post_event_cadences":a["n_cadences_post"],
          "original_PDCSAP_local_flux_depth":a["local_relative_flux_depth"],
          "original_raw_local_prepost_movement_pixels":a["local_pre_post_vector_norm_pixels"],
          "pointing_subtracted_local_prepost_movement_pixels":b["local_pre_post_vector_norm_pixels"]
        }
        for mode,e in (("raw",a),("pointing_subtracted",b)):
            vx=float(e["local_in_minus_flanking_x_pixels"])
            vy=float(e["local_in_minus_flanking_y_pixels"])
            row[mode+"_signed_x_CCD_pixels"]=vx
            row[mode+"_signed_y_CCD_pixels"]=vy
            row[mode+"_vector_norm_pixels"]=float(np.hypot(vx,vy))
            if geometry is not None:
                row[mode+"_angle_away_from_known_neighbor_deg"]=physical_away_alignment(
                    [vx,vy],geometry["target_to_neighbor_CCD_pixel_vector"])
        pairs.append(row)
    return pairs,{"raw_original_event_windows":len(raw),
                  "corrected_original_event_windows":len(corrected),
                  "exact_same_orbit_event_pairs":len(pairs),
                  "missing_raw_orbits":sorted(set(c)-set(r)),
                  "missing_corrected_orbits":sorted(set(r)-set(c))}


def summarize_pairs(pairs,geometry,sector):
    result={"sector":sector,"usable_paired_original_events":len(pairs),
            "n_observed_events_with_positive_PDCSAP_depth":sum(
                e["original_PDCSAP_local_flux_depth"]>0 for e in pairs),
            "minimum_three_complete_events":len(pairs)>=3}
    if not pairs:
        result["source_directional_assessment"]="not_evaluable_no_paired_events"
        return result
    for mode in ("raw","pointing_subtracted"):
        x=np.array([e[mode+"_signed_x_CCD_pixels"] for e in pairs])
        y=np.array([e[mode+"_signed_y_CCD_pixels"] for e in pairs])
        v=[float(np.median(x)),float(np.median(y))]
        result[mode+"_median_signed_vector_pixels"]=v
        result[mode+"_median_vector_amplitude_pixels"]=float(np.hypot(*v))
        if geometry["catalog_sky_geometry_consistent_with_TPF_target_position"]:
            result[mode+"_median_vector_angular_difference_away_neighbor_deg"]=physical_away_alignment(
                v,geometry["target_to_neighbor_CCD_pixel_vector"])
        else:
            result[mode+"_median_vector_angular_difference_away_neighbor_deg"]=None
    result["median_PDCSAP_local_depth"]=float(np.median([e["original_PDCSAP_local_flux_depth"] for e in pairs]))
    result["median_raw_before_after_centroid_drift_pixels"]=float(np.median(
        [e["original_raw_local_prepost_movement_pixels"] for e in pairs]))
    result["median_adjusted_before_after_centroid_drift_pixels"]=float(np.median(
        [e["pointing_subtracted_local_prepost_movement_pixels"] for e in pairs]))
    result["source_directional_assessment"]=(
        "descriptive_only_posthoc_not_physical_validation"
        if result["minimum_three_complete_events"] and
        geometry["catalog_sky_geometry_consistent_with_TPF_target_position"]
        else "not_evaluable_insufficient_event_coverage_or_WCS_consistency")
    return result


def plot_events(pairs,sector,out):
    if not pairs:return
    arr=pd.DataFrame(pairs)
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    axes[0].scatter(arr["original_ephemeris_predicted_center_BTJD"],
                    arr["original_PDCSAP_local_flux_depth"],s=23)
    axes[0].axhline(0,ls="--",color="grey",lw=.8)
    axes[0].set(xlabel="Original ExoFOP predicted center (BTJD)",
                ylabel="Local PDCSAP flux dip (fraction)",
                title="Original observed event-window depths")
    axes[1].scatter(arr["original_raw_local_prepost_movement_pixels"],
                    arr["pointing_subtracted_local_prepost_movement_pixels"],s=23)
    mx=float(max(arr["original_raw_local_prepost_movement_pixels"].max(),
                 arr["pointing_subtracted_local_prepost_movement_pixels"].max()))
    axes[1].plot([0,mx],[0,mx],ls="--",color="grey",lw=.8)
    axes[1].set(xlabel="Original raw pre/post centroid motion (pixels)",
                ylabel="After POS_CORR subtraction (pixels)",
                title="Measured local drift, not planet accuracy")
    fig.suptitle(f"TOI {TOI}, original TESS SPOC sector {sector} (post-hoc)")
    fig.tight_layout()
    fig.savefig(Path(out)/f"TOI4255_sector{sector}_original_source_event_physics.png",dpi=175)
    plt.close(fig)


def run(discovery_json,original_nearby_csv,out,working):
    report=json.loads(Path(discovery_json).read_text())
    product_pairs=select_exact_source_products(report)
    ephemeris=report["cases"][str(TIC)]
    period=float(ephemeris["original_ExoFOP_period_days"])
    epoch=float(ephemeris["original_ExoFOP_epoch_BTJD"])
    duration=float(ephemeris["original_ExoFOP_duration_days"])
    nearby_bytes=Path(original_nearby_csv).read_bytes()
    neighbor=neighbor_catalog_row(nearby_bytes)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    working=Path(working);working.mkdir(parents=True,exist_ok=True)
    rows=[]
    for sector in KNOWN_SECTORS:
        r={"sector":sector,"TIC_ID":TIC,"TOI":TOI,"original_reported_neighbor_TIC":NEIGHBOR}
        source_dir=working/f"s{sector}"
        try:
            original={}
            for group in ("LC","TP"):
                product=product_pairs[sector][group]
                f=source_dir/product["productFilename"]
                original[group]=download_original_mast(product["MAST_original_dataURI"],f)
                original[group]["file_path_local"]=str(f)
            r["original_source_provenance"]={key:{
                k:v for k,v in val.items() if k!="file_path_local"}
                for key,val in original.items()}
            frame,meta=load_tess_centroid_columns(original["LC"]["file_path_local"],TIC,sector)
            r["original_LC_source"]=meta
            w,target,wcs_meta=sky_wcs_from_tpf(original["TP"]["file_path_local"],TIC,sector)
            r["original_TPF_WCS_source"]=wcs_meta
            r["external_neighbor_catalog"]=neighbor
            g=position_geometry(w,target,neighbor)
            r["real_catalog_and_TPF_WCS_geometry"]=g
            pairs,account=paired_original_events(frame,period,epoch,duration,g)
            r["source_event_accounting"]=account
            r["science"]=summarize_pairs(pairs,g,sector)
            pd.DataFrame(pairs).to_csv(
                out/f"TOI4255_sector{sector}_original_SPOC_same_event_centroids.csv",index=False)
            plot_events(pairs,sector,out)
            r["source_status"]="processed"
        except (ValueError,KeyError,OSError,requests.RequestException) as ex:
            r["source_status"]="not_evaluable"
            r["source_error"]=str(ex)[:400]
            r["science"]={"source_directional_assessment":"not_evaluable"}
        print("SOURCE_ANALYSIS",json.dumps({
            "sector":sector,"status":r["source_status"],
            "error":r.get("source_error"),
            "event_accounting":r.get("source_event_accounting"),
            "science":r.get("science")
        }),flush=True)
        rows.append(r)
    output={
        "analysis":"two originally cataloged, post-hoc off-target NEB example; one real TESS source, two independently verified source sectors",
        "TIC_ID":TIC,"TOI":TOI,
        "ground_reported_neighbor_TIC_ID":NEIGHBOR,
        "original_ExoFOP_ephemeris":{
            "period_days":period,"epoch_BTJD":epoch,"duration_days":duration},
        "MAST_product_discovery_sha256":hashlib.sha256(Path(discovery_json).read_bytes()).hexdigest(),
        "original_ExoFOP_neighbor_catalog_sha256":hashlib.sha256(nearby_bytes).hexdigest(),
        "sector_records":rows,
        "n_original_SPOC_sectors_processed":sum(r["source_status"]=="processed" for r in rows),
        "n_original_SPOC_sectors_not_evaluable":sum(r["source_status"]!="processed" for r in rows),
        "interpretation_limits":[
            "These cases were selected after inspection of original ground-based ExoFOP notes; NOT a blind test.",
            "The original observed TESS 2-min SPOC FITS, source hash and TPF WCS determine every measurement and direction.",
            "A simple two-star blended centroid should shift away from a fading neighbor, but complex apertures and instrumental effects can invert or obscure this.",
            "ExoFOP ephemerides may not match original SPOC events if the period is aliased or source identity differs; unobserved windows stay unobserved.",
            "Directional alignment is descriptive only even when a nearby neighbor is externally cataloged; no causal validation of the source or new exoplanet.",
            "No NASA ExoMiner++ 2026 neural weights, scores, labels, or official difference-image diagnostics were changed."
        ]
    }
    (out/"TOI4255_original_TESS_SPOC_WCS_offtarget_vector_case_study.json").write_text(
        json.dumps(output,indent=2,default=str)+"\n")
    return output


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--mast-discovery",required=True)
    p.add_argument("--exofop-neighbors",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--working",required=True)
    a=p.parse_args()
    run(a.mast_discovery,a.exofop_neighbors,a.out,a.working)
