"""Source-pinned original TESS TPF optimal SAP vs moment-centroid pixel masks.

The original TESS SPOC target pixel APERTURE extension uses bit value 2
for pixels in optimal SAP photometry and bit value 8 for moment centroids.
We project the physically ground-observed NEB TIC's original independent
RA/Dec onto original FLUX WCS to compare geometric mask inclusion.
This is NOT a PRF contamination fraction or source-classification accuracy.
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import requests
from astropy.io import fits

from tess_toi4255_original_spoc_neb_vector_case import (
    download_original_mast,sky_wcs_from_tpf
)

CASES={382437043:382437045,264303333:1884344804}
BIT_OPTIMAL_SAP=2
BIT_MOMENT_CENTROID=8


def analyze_mask(w,mask,target_ra_dec,neighbor_ra_dec):
    arr=np.asarray(mask)
    if arr.ndim!=2 or not np.issubdtype(arr.dtype,np.integer):
        raise ValueError("Original TESS aperture bitmask is not integer 2D")
    target=np.asarray(w.all_world2pix(*target_ra_dec,0),dtype=float)
    neighbor=np.asarray(w.all_world2pix(*neighbor_ra_dec,0),dtype=float)
    if not np.isfinite(np.r_[target,neighbor]).all():
        raise ValueError("Original source sky coordinates not represented by finite TPF WCS")
    result={
        "original_TPF_APERTURE_yx_shape":list(arr.shape),
        "original_primary_target_cutout_xy_zero_origin":target.tolist(),
        "original_external_neighbor_cutout_xy_zero_origin":neighbor.tolist(),
        "original_TPF_neighbor_distance_from_primary_CCD_pixels":float(np.linalg.norm(neighbor-target)),
        "neighbor_within_available_TPF_cutout_pixel_centers_extent":bool(
            -.5<=neighbor[0]<arr.shape[1]-.5 and -.5<=neighbor[1]<arr.shape[0]-.5),
        "original_APERTURE_integer_bitmask_matrix":arr.astype(int).tolist(),
        "geometric_pixel_mask_DOES_NOT_ESTIMATE_PRF_photon_capture_fraction":True,
    }
    for name,bit in [("original_optimal_SAP",BIT_OPTIMAL_SAP),
                     ("original_moment_centroid",BIT_MOMENT_CENTROID)]:
        sel=(arr.astype(np.int64)&bit)!=0
        y,x=np.nonzero(sel)
        cells=np.c_[x,y] if len(x) else np.empty((0,2))
        near=(int(np.rint(neighbor[0])),int(np.rint(neighbor[1])))
        inside=(0<=near[0]<arr.shape[1] and 0<=near[1]<arr.shape[0])
        result[name+"_selected_pixels"]=int(sel.sum())
        result[name+"_neighbor_nearest_CCD_pixel"]=list(near)
        result[name+"_neighbor_nearest_CCD_pixel_in_mask"]=bool(
            inside and sel[near[1],near[0]])
        result[name+"_nearest_selected_CCD_pixel_center_distance_from_neighbor_pixels"]=(
            float(np.linalg.norm(cells-neighbor,axis=1).min()) if len(cells) else None)
        result[name+"_nearest_selected_CCD_pixel_center_distance_from_primary_pixels"]=(
            float(np.linalg.norm(cells-target,axis=1).min()) if len(cells) else None)
        result[name+"_all_selected_pixel_cutout_xy"]=[[int(a),int(b)] for a,b in cells]
    return result


def run(frozen_source,original_ground_sky,out,working):
    frozen_file=Path(frozen_source)
    frozen=json.loads(frozen_file.read_text())
    if frozen.get("experiment_id")!="ASTR_FIVE_NEW_NEB_SPOC_SOURCE_BLIND_WCS_EVAL_20261112":
        raise ValueError("Original genuine ground NEB TESS frozen host manifest absent")
    candidates={int(x["TIC_ID"]):x for x in frozen["source_records"]}
    ground=json.loads(Path(original_ground_sky).read_text())
    original_skies={int(x["host_TIC_ID"]):x for x in ground["original_sky_source_records"]}
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    working=Path(working);working.mkdir(parents=True,exist_ok=True)
    records=[]
    for tic,near_tic in CASES.items():
        row={"host_TIC_ID":tic,"original_external_NEb_TIC_ID":near_tic}
        try:
            if tic not in candidates or tic not in original_skies:
                raise ValueError("Ground source physically corroborated TIC not in original source-frozen list")
            c=candidates[tic];g=original_skies[tic]
            if not g["original_ground_reported_neighbor_aperture_matches_external_TIC_within_fixed_5arcsec"] or not g[
                "original_ground_target_T1_matches_TESS_target_within_fixed_8arcsec"]:
                raise ValueError("Physical ground source association failed original predefined WCS checks")
            if int(c["original_neb_named_neighbor_TIC_not_physical_truth"])!=near_tic or int(
                g["original_external_neighbor_candidate_TIC_ID"])!=near_tic:
                raise ValueError("Original ground and frozen TESS physical neighbor TIC mismatch")
            sector=int(c["selected_first_original_SPOC_2min_sector"])
            p=c["original_MAST_products"]["TP"]
            if int(p["TIC_ID"])!=tic or int(p["sector"])!=sector or p["product_group"]!="TP":
                raise ValueError("Not source-frozen first-sector original SPOC TPF")
            file=working/f"original_TIC{tic}"/p["productFilename"]
            row["original_SPOC_TPF_bytes_SHA_provenance"]=download_original_mast(
                p["MAST_original_dataURI"],file)
            w,primary,wcs=sky_wcs_from_tpf(file,tic,sector)
            with fits.open(file,memmap=False) as f:
                if len(f)<3 or str(f[2].header.get("EXTNAME","")).upper()!="APERTURE":
                    raise ValueError("Original SPOC TPF APERTURE extension absent")
                mask=np.asarray(f[2].data)
                if "FLUX" not in f[1].data.names:
                    raise ValueError("Original SPOC TPF FLUX field absent")
            geometry=analyze_mask(
                w,mask,(float(primary.ra.deg),float(primary.dec.deg)),
                (float(c["original_nearby_catalog_RA_deg"]),
                 float(c["original_nearby_catalog_Dec_deg"])))
            row.update(status="processed",original_fixed_SPOC_sector=sector,
                original_TPF_sky_WCS_header=wcs,original_TPF_binary_mask_geometry=geometry)
            fig,axes=plt.subplots(1,2,figsize=(9.5,4.5))
            for ax,name,bit in zip(axes,["SPOC SAP photometry","SPOC moment centroid"],
                                   [BIT_OPTIMAL_SAP,BIT_MOMENT_CENTROID]):
                ax.imshow(((mask&bit)!=0).astype(int),cmap="Greys",
                          interpolation="nearest",origin="lower",vmin=0,vmax=1)
                tx,ty=geometry["original_primary_target_cutout_xy_zero_origin"]
                nx,ny=geometry["original_external_neighbor_cutout_xy_zero_origin"]
                ax.scatter([tx],[ty],marker="+",s=100,label="Host TIC")
                ax.scatter([nx],[ny],marker="x",s=95,label="Ground NEB TIC")
                ax.set(title=name,xlabel="Original TPF x (pixel)",ylabel="Original TPF y (pixel)")
                ax.legend(frameon=False,fontsize=8)
            fig.suptitle(f"TOI {c['TOI']}, original SPOC sector {sector}")
            fig.text(.5,.015,"Mask-pixel proximity is not an exact neighbor photon-capture fraction.",
                     ha="center",fontsize=8)
            fig.tight_layout(rect=[0,.04,1,.96])
            fig.savefig(out/f"TOI{c['TOI']}_original_TPF_SAP_vs_MOM_mask_and_NEb_positions.png",dpi=175)
            plt.close(fig)
        except (ValueError,KeyError,OSError,requests.RequestException) as e:
            row.update(status="not_evaluable",source_error=str(e)[:400])
        print("ORIGINAL_TESS_SPOC_PHYSICAL_NEIGHBOR_APERTURE_MASK",json.dumps({
            "host_TIC":tic,"neighbor_TIC":near_tic,"status":row["status"],
            "sector":row.get("original_fixed_SPOC_sector"),
            "mask":row.get("original_TPF_binary_mask_geometry"),
            "error":row.get("source_error")}),flush=True)
        records.append(row)
    report={
        "question":"Are the ground-supported eclipsing neighbors geometrically within the original SPOC SAP and/or moment-centroid pixels in their frozen first-sector two-minute TPF?",
        "original_frozen_source_manifest_SHA256":hashlib.sha256(frozen_file.read_bytes()).hexdigest(),
        "n_original_ground_supported_source_hosts_attempted":len(records),
        "n_source_TPF_mask_result_evaluable":sum(x["status"]=="processed" for x in records),
        "original_source_mask_and_neighbor_position_results":records,
        "cautions":[
            "Bit 2 marks SAP optimal aperture, bit 8 marks moment-centroid aperture in original TESS products. Source pixel coordinates from real TPF FLUX WCS.",
            "Neighbor nearest selected pixel indicates geometrical inclusion only, not true point-response-function photon capture or background corrections.",
            "SPOC PDCSAP flux is not just unmodified summation of the original SAP mask, and centroid method may use different pixels.",
            "Original TPF source sectors, TICs, target and neighbor positions are frozen before centroid exposure; no replacements.",
            "These cases were selected based on earlier observer notes, not a new pre-registered blind physical source validation.",
            "No NASA ExoMiner++ weights, scores, official difference-image vetting, or verified new planet classification is changed."
        ]
    }
    (out/"original_two_ground_NEBS_SPOC_TPF_SAP_and_moment_centroid_mask_geometry.json").write_text(
        json.dumps(report,indent=2,default=str)+"\n")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-frozen-five",required=True)
    p.add_argument("--original-ground-sky",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--working",required=True)
    a=p.parse_args()
    run(a.original_frozen_five,a.original_ground_sky,a.out,a.working)
