"""Real original SPOC target-pixel difference-image *descriptive* NEB localization test.

Two previously ground-WCS-aperture supported off-target eclipsing candidates.
Source TIC / neighbor, first original SPOC sector, original untouched TPF
product URI and published ExoFOP transit ephemeris were all frozen *before
any* new difference-image pixels were extracted.

Observed original TPF FLUX cube (quality zero) is analyzed using a fixed
median-in-event minus equal-median-pre/post method analogous to our existing
centroid method; only bit-8 moment-centroid selected TPF pixels determine
peak and positive-only difference-image centroid. This is NOT official NASA
PRF/difference-image vetting, an actual photometric PRF fit or new source
location truth. The physical neighbor is only ~1.2-1.5 TESS pixels away
and point-spread blending and spacecraft systematics can be severe.
"""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from astropy.io import fits

from tess_toi4255_original_spoc_neb_vector_case import (
    download_original_mast,sky_wcs_from_tpf
)

EXACT_HOSTS={382437043:382437045,264303333:1884344804}
PHASES=(0.,-.25,+.25)
BIT_MOM=8
MIN_IN=3
MIN_FLANK=6
ELIGIBLE_TRUE_EVENTS=3
ELIGIBLE_EACH_CONTROL_EVENTS=3


def true_per_event_pixel_differences(t,cube,quality,source_mask,period,epoch,duration,phase=0.):
    """No interpolation, event time fitting, pixel source choice or imputation."""
    t=np.asarray(t,dtype=float)
    cube=np.asarray(cube,dtype=float)
    quality=np.asarray(quality)
    selected=np.asarray(source_mask,dtype=bool)
    if cube.ndim!=3 or t.ndim!=1 or cube.shape[0]!=len(t) or quality.shape!=t.shape:
        raise ValueError("Original TPF time, pixel and quality row shapes inconsistent")
    if selected.shape!=cube.shape[1:] or not selected.any():
        raise ValueError("Original bit-8 centroid aperture shape or pixels invalid")
    if not (np.isfinite([period,epoch,duration,phase]).all() and
            0<period and 0<duration<.3*period and abs(phase)<=.5):
        raise ValueError("Invalid original TOI period epoch duration or original phase control")
    if len(t)<30 or not np.isfinite(t).all() or not np.all(np.diff(t)>0):
        raise ValueError("Original TPF observation times not increasing or not finite")
    valid=np.isfinite(cube[:,selected]).all(axis=1)&(quality==0)
    inn=1.5*duration
    outer=min(3.5*duration,.44*period)
    if outer<=inn:
        raise ValueError("Original source pre/post comparison windows overlap original transit")
    center_epoch=epoch+phase*period
    first=int(np.ceil((t[0]+outer-center_epoch)/period))
    last=int(np.floor((t[-1]-outer-center_epoch)/period))
    events=[]
    for k in range(first,last+1):
        center=float(center_epoch+k*period)
        dt=t-center
        active=(np.abs(dt)<=.5*duration)&valid
        before=(dt>=-outer)&(dt<=-inn)&valid
        after=(dt>=inn)&(dt<=outer)&valid
        n=[int(before.sum()),int(active.sum()),int(after.sum())]
        if n[0]<MIN_FLANK or n[1]<MIN_IN or n[2]<MIN_FLANK:
            continue
        pre=np.median(cube[before],axis=0)
        pos=np.median(cube[after],axis=0)
        mid=np.median(cube[active],axis=0)
        pixel_diff=.5*(pre+pos)-mid
        if not np.isfinite(pixel_diff[selected]).all():
            continue
        events.append({
            "orbit":k,"original_source_center_BTJD":center,
            "original_pre_event_quality_zero_rows":n[0],
            "original_true_window_quality_zero_rows":n[1],
            "original_post_event_quality_zero_rows":n[2],
            "measured_out_minus_in_TPF_flux_image_electrons_per_second":pixel_diff
        })
    return events,{
        "original_source_flux_cube_rows":len(t),
        "original_quality_zero_and_finite_bit8_pixel_rows":int(valid.sum()),
        "original_prespecified_complete_outminusin_event_images":len(events),
        "original_uninterpolated_first_full_window_orbit":first,
        "original_uninterpolated_last_full_window_orbit":last
    }


def spatial_summary_fixed_bit8(events,bit8_mask,host_xy,neighbor_xy):
    """Measure generic pixel differences, not calibrated eclipse-source positions."""
    mask=np.asarray(bit8_mask,dtype=bool)
    host=np.asarray(host_xy,dtype=float)
    neighbor=np.asarray(neighbor_xy,dtype=float)
    if not events:
        return {"status":"no_original_complete_pixel_difference_events",
                "n_original_complete_real_TPF_difference_images":0},None
    stack=np.stack([r["measured_out_minus_in_TPF_flux_image_electrons_per_second"]
                    for r in events])
    image=np.median(stack,axis=0)
    if image.shape!=mask.shape or not np.isfinite(image[mask]).all():
        raise ValueError("Original source difference-image mask or flux data invalid")
    # Fixed estimator; all original bit-8 source pixels, positive-only weights.
    pixels=np.where(mask,np.maximum(image,0),0)
    total=float(pixels.sum())
    points=np.argwhere(mask)
    ypk,xpk=points[np.argmax(image[mask])]
    peak=np.array([float(xpk),float(ypk)])
    count_pos=int(((image>0)&mask).sum())
    summary={
        "status":"original_TPF_fixed_selected_pixel_diff_image",
        "n_original_complete_real_TPF_difference_images":len(events),
        "actual_original_mask_pixel_count":int(mask.sum()),
        "original_selected_pixel_positive_difference_count":count_pos,
        "median_original_selected_pixel_delta_Flux_electrons_per_second":float(
            np.median(image[mask])),
        "original_selected_pixel_sum_signed_diff_electrons_per_second":float(
            image[mask].sum()),
        "original_selected_pixel_sum_positive_clipped_diff_electrons_per_second":total,
        "brightest_out_minus_in_selected_pixel_xy_zero_origin":peak.tolist(),
        "brightest_pixel_delta_flux_electrons_per_second":float(image[ypk,xpk]),
        "brightest_pixel_distance_from_host_CCD_pixels":float(np.linalg.norm(peak-host)),
        "brightest_pixel_distance_from_neighbor_CCD_pixels":float(np.linalg.norm(peak-neighbor)),
        "brightest_pixel_is_geometrically_closer_to_reported_neighbor":bool(
            np.linalg.norm(peak-neighbor)<np.linalg.norm(peak-host)),
        "not_official_NASA_DV_difference_image_or_PSF_sky_fit":True
    }
    if total>0:
        iy,ix=np.indices(image.shape)
        center=np.array([float((pixels*ix).sum()/total),
                         float((pixels*iy).sum()/total)])
        summary.update({
            "positive_pixel_weighted_diff_image_xy_zero_origin":center.tolist(),
            "positive_pixel_diff_image_centroid_to_host_CCD_pixels":float(
                np.linalg.norm(center-host)),
            "positive_pixel_diff_image_centroid_to_neighbor_CCD_pixels":float(
                np.linalg.norm(center-neighbor)),
            "positive_pixel_diff_image_center_closer_to_reported_neighbor":bool(
                np.linalg.norm(center-neighbor)<np.linalg.norm(center-host))
        })
    else:
        summary.update({
            "positive_pixel_weighted_diff_image_xy_zero_origin":None,
            "positive_pixel_diff_image_centroid_to_host_CCD_pixels":None,
            "positive_pixel_diff_image_centroid_to_neighbor_CCD_pixels":None,
            "positive_pixel_diff_image_center_closer_to_reported_neighbor":None
        })
    return summary,image


def run(frozen_file,original_mask_file,out,working):
    frozen_file=Path(frozen_file)
    frozen=json.loads(frozen_file.read_text())
    original_mask_file=Path(original_mask_file)
    mask_results=json.loads(original_mask_file.read_text())
    if frozen.get("experiment_id")!="ASTR_FIVE_NEW_NEB_SPOC_SOURCE_BLIND_WCS_EVAL_20261112":
        raise ValueError("Source frozen five-star experiment not from original prior precentroid source manifest")
    hosts={int(x["TIC_ID"]):x for x in frozen["source_records"]}
    evidence={int(x["host_TIC_ID"]):x for x in mask_results[
        "original_source_mask_and_neighbor_position_results"]}
    if not set(EXACT_HOSTS).issubset(hosts) or not set(EXACT_HOSTS).issubset(evidence):
        raise ValueError("Original TESS physical source exact host identities missing; cannot select replacements")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    working=Path(working);working.mkdir(parents=True,exist_ok=True)
    rows=[]
    for tic,neighbor in EXACT_HOSTS.items():
        source=hosts[tic];prior=evidence[tic]
        item={"original_TESS_host_TIC":tic,
              "original_ground_and_catalog_sky_supported_neighbor_TIC":neighbor,
              "TOI":source["TOI"],
              "original_sector_fixed_before_TESS_centroid_analysis":int(
                  source["selected_first_original_SPOC_2min_sector"])}
        try:
            if prior["status"]!="processed" or prior["original_external_NEb_TIC_ID"]!=neighbor or int(
                source["original_neb_named_neighbor_TIC_not_physical_truth"])!=neighbor:
                raise ValueError("Original exact verified source and original TPF mask source mismatch")
            product=source["original_MAST_products"]["TP"]
            sector=item["original_sector_fixed_before_TESS_centroid_analysis"]
            if int(product["TIC_ID"])!=tic or int(product["sector"])!=sector or product["product_group"]!="TP":
                raise ValueError("Original source-frozen MAST exact TPF product mismatched")
            destination=working/f"TIC{tic}"/product["productFilename"]
            md=download_original_mast(product["MAST_original_dataURI"],destination)
            if md["source_sha256"]!=prior["original_SPOC_TPF_bytes_SHA_provenance"]["source_sha256"]:
                raise ValueError("Original MAST TPF source SHA changed from earlier verified pixel-mask experiment")
            item["original_source_SHA_pinned_MAST_TPF"]=md
            w,primary,wmeta=sky_wcs_from_tpf(destination,tic,sector)
            with fits.open(destination,memmap=False) as h:
                data=h[1].data
                times=np.asarray(data["TIME"],dtype=float)
                q=np.asarray(data["QUALITY"],dtype=np.int64)
                cube=np.asarray(data["FLUX"],dtype=float)
                mask=np.asarray(h[2].data,dtype=np.int64)
            if cube.shape[1:]!=mask.shape:
                raise ValueError("Original source LC cube and original TPF bitmask shape differ")
            # Actual SPOC TPF can include missing-time cadences (NaN TIME) when
            # spacecraft data are absent. Exclude those original rows; never
            # impute dates or flux, and preserve the exact exclusion count.
            original_tpf_rows_before_missing_time_exclusion=len(times)
            original_finite_time_rows=np.isfinite(times)
            item["original_TPF_source_rows_all"]=original_tpf_rows_before_missing_time_exclusion
            item["original_TPF_missing_time_cadences_excluded"]=int((~original_finite_time_rows).sum())
            times=times[original_finite_time_rows]
            q=q[original_finite_time_rows]
            cube=cube[original_finite_time_rows]
            if len(times)<30 or not np.all(np.diff(times)>0):
                raise ValueError("Original TPF valid timestamps fewer than 30 or not strictly increasing")
            bit8=(mask&BIT_MOM)!=0
            p=prior["original_TPF_binary_mask_geometry"]
            target=p["original_primary_target_cutout_xy_zero_origin"]
            near=p["original_external_neighbor_cutout_xy_zero_origin"]
            this_target=np.asarray(w.all_world2pix(float(primary.ra.deg),float(primary.dec.deg),0),dtype=float)
            this_near=np.asarray(w.all_world2pix(float(source["original_nearby_catalog_RA_deg"]),
                                  float(source["original_nearby_catalog_Dec_deg"]),0),dtype=float)
            if max(np.linalg.norm(this_target-target),np.linalg.norm(this_near-near))>1e-7:
                raise ValueError("Original unchanged TPF source sky WCS differs from previous source-mask geometry")
            P=float(source["original_ExoFOP_period_days"])
            E=float(source["original_ExoFOP_epoch_BTJD"])
            D=float(source["original_ExoFOP_duration_days"])
            results=[]
            for frac in PHASES:
                events,coverage=true_per_event_pixel_differences(
                    times,cube,q,bit8,P,E,D,phase=frac)
                summary,image=spatial_summary_fixed_bit8(events,bit8,target,near)
                label="real_eclipse" if frac==0 else (
                    "minus_quarter_phase" if frac<0 else "plus_quarter_phase")
                row={
                    "original_unretimed_phase_offset_in_period":frac,
                    "original_observed_event_type":label,
                    "original_source_cadence_coverage":coverage,
                    "fixed_aperture_pixel_difference_spatial_result":summary
                }
                if events:
                    pd.DataFrame([{
                        "orbit_index":e["orbit"],
                        "original_center_BTJD":e["original_source_center_BTJD"],
                        "n_pre":e["original_pre_event_quality_zero_rows"],
                        "n_inside":e["original_true_window_quality_zero_rows"],
                        "n_post":e["original_post_event_quality_zero_rows"],
                        "original_selected_pixel_sum_signed_TPF_out_minus_in_electrons_per_second":float(
                            np.sum(e["measured_out_minus_in_TPF_flux_image_electrons_per_second"][bit8]))
                    } for e in events]).to_csv(
                        out/f"TIC{tic}_S{sector}_{label}_original_real_TPF_difference_per_event.csv",index=False)
                if image is not None:
                    # Respect the source-correct physical pixel coordinates, even
                    # when they lie close to other objects or field boundary.
                    fig,ax=plt.subplots(figsize=(5.5,4.8))
                    vals=image[bit8]
                    vlim=float(np.percentile(np.abs(vals),98)) if len(vals) else 1
                    if vlim==0:vlim=1
                    ax.imshow(image,origin="lower",interpolation="nearest",
                              vmin=-vlim,vmax=vlim,cmap="coolwarm")
                    ax.scatter([target[0]],[target[1]],marker="+",s=120,label="Target TIC")
                    ax.scatter([near[0]],[near[1]],marker="x",s=115,label="Ground NEB TIC")
                    ax.set(title=f"TOI {source['TOI']} S{sector}: {label}",
                           xlabel="Original SPOC TPF x pixel (zero origin)",
                           ylabel="Original SPOC TPF y pixel (zero origin)")
                    ax.legend(frameon=False)
                    fig.text(.5,.005,"Original out-minus-in pixel median; NOT official PRF difference-image source solution",
                             ha="center",fontsize=7)
                    fig.tight_layout(rect=[0,.05,1,1])
                    fig.savefig(out/f"TIC{tic}_S{sector}_{label}_original_TPF_pixel_difference.png",dpi=170)
                    plt.close(fig)
                results.append(row)
            if tuple(x["original_unretimed_phase_offset_in_period"] for x in results)!=PHASES:
                raise ValueError("Original precommitted real and fixed pseudo-event phase controls changed")
            item["original_TPF_real_and_fixed_phase_diff_image_results"]=results
            item["source_level_eligible_original_three_true_and_both_pseudoevent_windows"]=bool(
                all(r["fixed_aperture_pixel_difference_spatial_result"][
                    "n_original_complete_real_TPF_difference_images"]>=
                    (ELIGIBLE_TRUE_EVENTS if r["original_unretimed_phase_offset_in_period"]==0
                     else ELIGIBLE_EACH_CONTROL_EVENTS) for r in results))
            item["original_TPF_source_processing_status"]="processed"
        except (ValueError,KeyError,OSError,requests.RequestException) as e:
            item["original_TPF_source_processing_status"]="not_evaluable"
            item["original_TPF_source_error"]=str(e)[:430]
            item["source_level_eligible_original_three_true_and_both_pseudoevent_windows"]=False
        print("ORIGINAL_TPF_PIXEL_FLUX_DIFFERENCE_LOCALIZATION",json.dumps({
            "TIC":tic,"TOI":source["TOI"],"status":item["original_TPF_source_processing_status"],
            "source":item.get("original_TPF_real_and_fixed_phase_diff_image_results"),
            "source_error":item.get("original_TPF_source_error"),
            "eligible_source":item["source_level_eligible_original_three_true_and_both_pseudoevent_windows"],
        }),flush=True)
        rows.append(item)
    report={
        "question":"Can the original observed SPOC TPF pixel difference images for two externally ground-aperture-sky-matched neighboring eclipses visually/numerically localize original eclipse dimming nearer the off-target source than the primary, compared with fixed shifted-phase source controls?",
        "prior_source_frozen_manifest_SHA256":hashlib.sha256(frozen_file.read_bytes()).hexdigest(),
        "original_prior_TPF_photometric_centroid_mask_result_SHA256":hashlib.sha256(
            original_mask_file.read_bytes()).hexdigest(),
        "original_two_physical_source_TICs_attempted":2,
        "processed_original_TPF_difference_image_hosts":sum(
            x["original_TPF_source_processing_status"]=="processed" for x in rows),
        "source_TICs_eligible_at_predeclared_event_and_phase_control_rule":sum(
            x["source_level_eligible_original_three_true_and_both_pseudoevent_windows"] for x in rows),
        "original_source_TPF_pixel_difference_results":rows,
        "known_limitations":[
            "Original SPOC TPF FLUX difference images are median pixel-level pre/post versus in-transit differences, NOT official NASA calibrated PRF/difference-image source localization or ExoMiner input pipeline.",
            "Use only the first SPOC source sector pinned before reading centroids; do not choose a better-looking sector or event phase.",
            "Use original bit-8 moment-centroid pixel selection for this descriptive image estimator, not optimize the mask for a favorable source.",
            "The simple positive-pixel flux-weighted centroid and brightest pixel are heavily susceptible to spatial blending, pixel noise, instrumental background and source truncation.",
            "The target and neighbor are only 1–2 TESS pixels apart, below clean native TESS pixel resolution. An apparently closer peak is not a reliable unique source assignment.",
            "No image-level difference PRF model, systematics detrending, pixel covariance or independent ground raw-CCD image re-reduction is done.",
            "The original ExoFOP published epochs may alias real SPOC transit times, and the source-specific coverage counts are preserved rather than optimized.",
            "TOI-1223 had only two previously eligible original SPOC moment-centroid events; the phase-image source result cannot upgrade it to a new independent localization validation source.",
            "Controls at shifted quarter periods are not guaranteed clean physical nulls and may contain other real variability.",
            "No original NASA pretrained ExoMiner++ scores, official mission TCE labels or exoplanet classifications were changed."
        ]
    }
    (out/"two_real_ground_sky_NEBS_original_TPF_outminusin_pixel_difference_and_quarter_phase_results.json").write_text(
        json.dumps(report,indent=2)+"\n")
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--frozen-five-source-manifest",required=True)
    p.add_argument("--original-tpf-mask-results",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--working",required=True)
    a=p.parse_args()
    run(a.frozen_five_source_manifest,a.original_tpf_mask_results,a.out,a.working)
