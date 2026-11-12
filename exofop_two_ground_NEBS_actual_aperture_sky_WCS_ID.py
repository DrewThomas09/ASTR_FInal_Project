"""Independent sky-position test of original ground observer T6/T11 apertures.

Original:
* original ExoFOP observer full AstroImageJ BJD_TDB photometry sources
* separate original plate-solved representative ground image FITS WCS
* separate ExoFOP public neighboring TIC astrometry
* NASA SPOC primary target RA/Dec (for independent target sky check)
No re-selection of aperture, TIC, transit timing, source or model outputs.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.wcs import WCS

from exofop_two_NEB_original_ground_AIJ_numeric_sources import EXPECTED
from tess_neb_newhost_external_neighbor_candidate_audit import read_neighbor_astrometry

# Frozen *before reading original ground sky-separation outcomes*. These are
# descriptive review tolerances, not learned classifier thresholds.
NEIGHBOR_REVIEW_RADIUS_ARCSEC=5.0
TARGET_REVIEW_RADIUS_ARCSEC=8.0

WCS_FILE_ID={382437043:906276,264303333:222164}


def median_original_ground_aperture_xy(df,aperture):
    cols=("X(FITS)_"+aperture,"Y(FITS)_"+aperture)
    if not set(cols).issubset(df.columns):
        raise ValueError("Original ground AIJ X(FITS), Y(FITS) aperture columns absent")
    x=pd.to_numeric(df[cols[0]],errors="coerce").to_numpy(dtype=float)
    y=pd.to_numeric(df[cols[1]],errors="coerce").to_numpy(dtype=float)
    keep=np.isfinite(x)&np.isfinite(y)
    if keep.sum()<15:
        raise ValueError("Original AIJ aperture has too few real sky pixel coordinates")
    xy=np.array([np.median(x[keep]),np.median(y[keep])],dtype=float)
    if not np.isfinite(xy).all() or np.any(xy<1):
        raise ValueError("Original FITS image aperture median coordinates invalid")
    return xy,{"n_original_ground_pixel_aperture_rows":int(keep.sum()),
               "original_FITS_pixel_x_median":float(xy[0]),
               "original_FITS_pixel_y_median":float(xy[1]),
               "original_FITS_pixel_x_peak_to_peak":float(np.ptp(x[keep])),
               "original_FITS_pixel_y_peak_to_peak":float(np.ptp(y[keep]))}


def original_ground_plate_wcs(fits_file,expected_sha):
    path=Path(fits_file)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=expected_sha:
        raise ValueError("Original ground plate-solved image FITS SHA256 differs from original provenance")
    with fits.open(path,memmap=False) as hdus:
        h=hdus[0].header
        if "RA" not in str(h.get("CTYPE1","")).upper() or "DEC" not in str(h.get("CTYPE2","")).upper():
            raise ValueError("Original observer plate-solved FITS has no celestial primary WCS")
        w=WCS(h).celestial
        data=hdus[0].data
        if data is None or data.ndim!=2:
            raise ValueError("Original image source has no two-dimensional sky detector data")
        shape=tuple(int(x) for x in data.shape)
    return w,shape


def ground_aperture_sky_position(w,xy,shape):
    x,y=np.asarray(xy,dtype=float)
    if not (1<=x<=shape[1] and 1<=y<=shape[0]):
        raise ValueError("Ground original AIJ FITS pixel position lies outside plate-solved image")
    sky=w.all_pix2world([[x,y]],1)
    ra,dec=(float(v) for v in sky[0])
    if not np.isfinite([ra,dec]).all() or not (-90<=dec<=90):
        raise ValueError("Original ground image WCS did not yield valid sky coordinates")
    return SkyCoord(ra*u.deg,dec*u.deg,frame="icrs")


def audit_one(tic,known,previous_wcs,original_numeric_dir,neighbor_catalog_dir,original_tess_target):
    base=Path(original_numeric_dir)
    profile=json.loads((base/"two_ground_reported_NEB_numeric_AIJ_tseries_original_source_profile.json").read_text())
    hits=[x for x in profile["original_two_uploaded_aperture_source_records"] if int(x["TIC_ID"])==tic]
    if len(hits)!=1 or hits[0]["source_retrieval_status"]!="success":
        raise ValueError("Original ground numerical source TIC and source profile missing")
    meta=hits[0]
    src=(base/f"original_TIC{tic}_ExoFOP_file{known['original_ExoFOP_file_ID']}_{meta['original_filename']}")
    raw=src.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=meta["original_table_source_SHA256"]:
        raise ValueError("Original observer ground AIJ numeric source SHA256 changed")
    import io
    df=pd.read_csv(io.BytesIO(raw),sep="\t",low_memory=False)
    name=f"original_ExoFOP_ground_TIC{tic}_file{WCS_FILE_ID[tic]}_plate_solved.fits"
    original_wcs_file=Path(previous_wcs)/name
    prior_records=json.loads((Path(previous_wcs)/
       "two_original_ExoFOP_ground_image_WCS_and_aperture_pixel_source_inventory.json").read_text())
    w_record=[s for s in prior_records["cases"] if int(s["TIC_ID"])==tic]
    if len(w_record)!=1 or w_record[0]["original_ground_plate_solved_fits_status"]!="verified_source_file":
        raise ValueError("Ground original sky plate-solved WCS source was not verified")
    w,shape=original_ground_plate_wcs(original_wcs_file,w_record[0]["original_ground_WCS_SHA256"])
    near_bytes=(Path(neighbor_catalog_dir)/
      f"original_ExoFOP_TIC_{tic}_nearby_astrometry.csv").read_bytes()
    neighbors=read_neighbor_astrometry(near_bytes,tic)
    neighbor=int(known["ground_neighbor_TIC_ID"])
    if neighbor not in neighbors:
        raise ValueError("Original independent neighbor TIC not in original ExoFOP nearby catalog")
    neighbor_source=neighbors[neighbor]
    independent_neighbor=SkyCoord(
        neighbor_source["original_catalog_neighbor_RA_deg"]*u.deg,
        neighbor_source["original_catalog_neighbor_DEC_deg"]*u.deg)
    theader=original_tess_target
    raw_ra=theader["original_TPF_header_target_RA_deg"]
    raw_dec=theader["original_TPF_header_target_Dec_deg"]
    independent_target=SkyCoord(float(raw_ra)*u.deg,float(raw_dec)*u.deg)
    results={}
    for aperture in ("T1",known["AIJ_aperture"]):
        xy,meta_xy=median_original_ground_aperture_xy(df,aperture)
        sky=ground_aperture_sky_position(w,xy,shape)
        results[aperture]={
            **meta_xy,
            "ground_plate_solved_RA_deg":float(sky.ra.deg),
            "ground_plate_solved_Dec_deg":float(sky.dec.deg),
            "angular_offset_from_exofop_named_neighbor_arcsec":float(
                sky.separation(independent_neighbor).arcsec),
            "angular_offset_from_original_TESS_target_arcsec":float(
                sky.separation(independent_target).arcsec)
        }
    ap=known["AIJ_aperture"]
    target_dist=results["T1"]["angular_offset_from_original_TESS_target_arcsec"]
    neighbor_dist=results[ap]["angular_offset_from_exofop_named_neighbor_arcsec"]
    return {
        "TOI":known["TOI"],"host_TIC_ID":tic,
        "original_external_neighbor_candidate_TIC_ID":neighbor,
        "original_aperture":ap,
        "real_AI_J_source_SHA256":hashlib.sha256(raw).hexdigest(),
        "original_plate_solved_ground_WCS_SHA256":w_record[0]["original_ground_WCS_SHA256"],
        "original_external_neighbor_catalog_SHA256":hashlib.sha256(near_bytes).hexdigest(),
        "original_TESS_target_sky_RA_deg":float(raw_ra),
        "original_TESS_target_sky_Dec_deg":float(raw_dec),
        "external_catalog_neighbor_RA_deg":float(independent_neighbor.ra.deg),
        "external_catalog_neighbor_Dec_deg":float(independent_neighbor.dec.deg),
        "original_ground_pixel_aperture_sky_measurements":results,
        "original_ground_target_T1_matches_TESS_target_within_fixed_8arcsec":bool(
            target_dist<=TARGET_REVIEW_RADIUS_ARCSEC),
        "original_ground_reported_neighbor_aperture_matches_external_TIC_within_fixed_5arcsec":bool(
            neighbor_dist<=NEIGHBOR_REVIEW_RADIUS_ARCSEC),
        "original_ground_reported_neighbor_aperture_sky_offset_arcsec":neighbor_dist,
        "original_ground_T1_host_aperture_sky_offset_arcsec":target_dist,
        "source_lifetime_warnings":[
            "Ground original representative plate-solved image and original AIJ aperture coordinates may be from slightly different registered frames or pixel origins.",
            "A sky position match validates the original observer aperture identity geometrically, not uniquely whether the dimming is astrophysical rather than an image artifact.",
            "T1 target image reported saturated; geometric original target coordinate agreement is a crosscheck not quantitative flux evidence.",
            "Ground original image WCS derives from observer uploaded plate solution, not independent Gaia astrometry re-reduction.",
            "No ExoMiner predictions, weights, or mission classifiers are altered."
        ]
    }


def run(ground_wcs_dir,ground_numeric_dir,neighbor_catalog_dir,prior_tess_results,out):
    prior_tess=json.loads(Path(prior_tess_results).read_text())
    if prior_tess["exact_new_host_star_count_attempted"]!=5:
        raise ValueError("Original five-TESS-host anchor invalid")
    targetdata={int(row["TIC_ID"]):row["original_SPOC_TPF_WCS_header"]
                for row in prior_tess["all_original_source_results"]
                if row.get("source_processing_status")=="processed"}
    data=[]
    for tic,known in EXPECTED.items():
        try:
            if tic not in targetdata:
                raise ValueError("No true original NASA TESS target RA/Dec for ground independent source verification")
            rec=audit_one(tic,known,ground_wcs_dir,ground_numeric_dir,neighbor_catalog_dir,targetdata[tic])
            rec["status"]="audited"
        except (ValueError,OSError,KeyError) as e:
            rec={"TOI":known["TOI"],"host_TIC_ID":tic,"original_aperture":known["AIJ_aperture"],
                 "status":"not_evaluable","source_error":str(e)[:400]}
        print("GROUND_SOURCE_SKY_IDENTITY",json.dumps({
            "host_TIC_ID":tic,"TOI":known["TOI"],"status":rec["status"],
            "target_offset_arcsec":rec.get("original_ground_T1_host_aperture_sky_offset_arcsec"),
            "neighbor_offset_arcsec":rec.get("original_ground_reported_neighbor_aperture_sky_offset_arcsec"),
            "neighbor_position_within_fixed_radius":rec.get("original_ground_reported_neighbor_aperture_matches_external_TIC_within_fixed_5arcsec"),
            "error":rec.get("source_error")
        }),flush=True)
        data.append(rec)
    result={
        "purpose":"First original ExoFOP ground sky-aperture WCS source TIC identity crosscheck for observer-designated T6/T11 eclipse signals",
        "original_ground_WCS_image_source_retrieval_not_reselected":True,
        "original_two_TICs":len(data),
        "source_position_measurements_evaluable":sum(x["status"]=="audited" for x in data),
        "catalog_matched_independent_original_aperture_neighbor_TICs":sum(x.get(
            "original_ground_reported_neighbor_aperture_matches_external_TIC_within_fixed_5arcsec",False) for x in data),
        "original_sky_source_records":data,
        "calibration_limitations":[
            "Ground telescope source imaging and WCS are original observer-supplied images and original registered AIJ photometry; apparent WCS match is not a separate professional re-reduction.",
            "A candidate aperture can physically overlap a neighbor in crowded or saturated frames. Inspect original image, source segmentation, and aperture radius for independent contamination assessment.",
            "True eclipsing-neighbor classification requires both an unambiguous ground source position and a robust measured time-dependent flux dip. This records source geometric consistency, not a classifier-validation result.",
            "Two previously inspected ground cases cannot be used to infer a representative ExoMiner model gain."
        ]
    }
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/"two_ground_NEBS_actual_AIJ_aperture_WCS_to_external_TIC_sky_identity.json").write_text(
        json.dumps(result,indent=2)+"\n")
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-ground-WCS",required=True)
    p.add_argument("--original-ground-AIJ",required=True)
    p.add_argument("--original-neighbor-catalogs",required=True)
    p.add_argument("--original-TESS-source-results",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.original_ground_WCS,a.original_ground_AIJ,
        a.original_neighbor_catalogs,a.original_TESS_source_results,a.out)
