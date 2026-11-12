"""Inspect source-pinned original ExoFOP ground WCS and AIJ pixel-aperture columns.

Not enough to equate AIJ T6/T11 with sky TIC identity: this source audit
documents whether genuine original ground WCS and original image coordinates
are available, but does not re-fit a transit or NASA model.
"""
import argparse,hashlib,io,json,re
from pathlib import Path

import pandas as pd
import requests
from astropy.io import fits
from astropy.wcs import WCS

CASES={
 382437043:{"ground_wcs_file_ID":906276,"aij_observed_aperture":"T6",
           "source_id":906268,"named_nearby_TIC":382437045},
 264303333:{"ground_wcs_file_ID":222164,"aij_observed_aperture":"T11",
           "source_id":222159,"named_nearby_TIC":1884344804},
}
WCS_URI="https://exofop.ipac.caltech.edu/tess/get_file.php?id={}"


def pixel_coord_columns(colnames,aperture):
    suffix="_"+aperture
    return [c for c in colnames if c.endswith(suffix) and
            any(s in c.lower() for s in ("x(","y(","xcent","ycent","x_image","y_image","xap","yap","x-axis","y-axis","x center","y center","ra_", "dec_"))]


def inspect(numeric_dir,ground_inventory,out):
    numeric_dir=Path(numeric_dir);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    inv=json.loads(Path(ground_inventory).read_text())
    sources={int(h["TIC_ID"]):h for h in inv["all_hosts_with_full_file_and_tseries_evidence"]}
    numeric=json.loads((numeric_dir/"two_ground_reported_NEB_numeric_AIJ_tseries_original_source_profile.json").read_text())
    full={int(x["TIC_ID"]):x for x in numeric["original_two_uploaded_aperture_source_records"]}
    rows=[]
    for tic,c in CASES.items():
        info=full[tic]
        name=info["original_filename"]
        path=numeric_dir/f"original_TIC{tic}_ExoFOP_file{c['source_id']}_{name}"
        original=path.read_bytes()
        if hashlib.sha256(original).hexdigest()!=info["original_table_source_SHA256"]:
            raise ValueError("Original ground numerical source SHA mismatch")
        srcs={int(x["original_exofop_file_ID"]):x for x in sources[tic]["original_user_file_evidence_queue"]}
        if c["ground_wcs_file_ID"] not in srcs or not srcs[c["ground_wcs_file_ID"]]["original_file_name"].endswith(".fits"):
            raise ValueError("Original ground sky WCS file absent from preexisting source catalog")
        df=pd.read_csv(io.BytesIO(original),sep="\t",low_memory=False)
        aperture=c["aij_observed_aperture"]
        pix=pixel_coord_columns(df.columns,aperture)
        allpos=[x for x in df.columns if
                any(n in x.lower() for n in ("x(fits)","y(fits)","xcent","ycent","ra_","dec_"))]
        entry={"TIC_ID":tic,"neighbor_TIC":c["named_nearby_TIC"],
               "observer_mapped_neb_aperture":aperture,
               "original_ground_AIJ_SHA256":info["original_table_source_SHA256"],
               "original_eligible_aperture_coordinate_columns":pix,
               "original_AIJ_example_coordinate_fields_all":allpos[:40],
               "original_AIJ_available_stellar_aperture_columns":[q for q in df.columns
                  if q.startswith("rel_flux_T")][:20],
               "astrometric_sky_coordinate_mapping_verified":False}
        url=WCS_URI.format(c["ground_wcs_file_ID"])
        try:
            resp=requests.get(url,timeout=(30,150))
            resp.raise_for_status()
            if len(resp.content)>250000000:raise ValueError("Ground WCS original FITS larger than 250MB cap")
            if resp.content[:6]!=b"SIMPLE":raise ValueError("ExoFOP original plate-solved file is not FITS bytes")
            entry["original_ground_WCS_SHA256"]=hashlib.sha256(resp.content).hexdigest()
            entry["original_ground_WCS_byte_size"]=len(resp.content)
            output_name=f"original_ExoFOP_ground_TIC{tic}_file{c['ground_wcs_file_ID']}_plate_solved.fits"
            (out/output_name).write_bytes(resp.content)
            with fits.open(io.BytesIO(resp.content),memmap=False) as hdus:
                entry["original_ground_WCS_HDU_summary"]=[{
                    "index":i,"kind":type(h).__name__,
                    "image_shape":list(h.data.shape) if getattr(h,"data",None) is not None and
                                  hasattr(h.data,"shape") else None,
                    "CTYPE1":h.header.get("CTYPE1"),
                    "CTYPE2":h.header.get("CTYPE2"),
                    "CRVAL1":h.header.get("CRVAL1"),
                    "CRVAL2":h.header.get("CRVAL2"),
                    "CRPIX1":h.header.get("CRPIX1"),
                    "CRPIX2":h.header.get("CRPIX2"),
                    "CD1_1":h.header.get("CD1_1"),
                    "CD2_2":h.header.get("CD2_2")
                } for i,h in enumerate(hdus)]
                candidate=[(i,h) for i,h in enumerate(hdus)
                    if "RA" in str(h.header.get("CTYPE1","")).upper() and
                       "DEC" in str(h.header.get("CTYPE2","")).upper()]
                entry["original_hdu_with_celestial_WCS"]=[i for i,h in candidate]
                entry["original_ground_plate_solved_fits_status"]="verified_source_file"
        except (requests.RequestException, ValueError, OSError) as ex:
            entry["original_ground_plate_solved_fits_status"]="source_missing_or_unreadable"
            entry["ground_WCS_error"]=str(ex)[:340]
        rows.append(entry)
        print("GROUND_PLATE_SOLVE_AVAILABILITY",json.dumps({
            "TIC":tic,"aperture":aperture,
            "original_AIJ_possible_xy_columns":pix,
            "AIJ_examples":allpos[:12],
            "FITS_source":entry["original_ground_plate_solved_fits_status"],
            "original_FITS_celestial_WCS_HDU":entry.get("original_hdu_with_celestial_WCS"),
            "shape":entry.get("original_ground_WCS_HDU_summary")},default=str),flush=True)
    data={"source_file_count":len(rows),
          "cases":rows,
          "physical_neighbor_mapping_test_performed":False,
          "limitations":["Original representative WCS image may not use exactly the same crop, origin, binning or axis orientation as the original AIJ measurement coordinates.",
                         "No automatic physical source confirmation; any pixel-to-sky match requires independent target-position consistency tests.",
                         "The already measured ground flux and original eclipse timings are not changed by downloading this WCS."]}
    (out/"two_original_ExoFOP_ground_image_WCS_and_aperture_pixel_source_inventory.json").write_text(
        json.dumps(data,indent=2,default=str)+"\n")
    return data


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--numeric-source",required=True)
    p.add_argument("--original-file-inventory",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    inspect(a.numeric_source,a.original_file_inventory,a.out)
