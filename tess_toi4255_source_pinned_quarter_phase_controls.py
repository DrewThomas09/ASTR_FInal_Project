"""Original TESS TOI 4255 phase-shift controls and within-star bootstrap.

Post-hoc sensitivity, using EXACT prior LC/TP source SHA256 and original
ExoFOP ephemeris. The two observed sectors are NOT independent stars.
Resampling events estimates descriptive within-source uncertainty, not
mission-scale false-positive rate or new ExoMiner validation.
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

from tess_original_moment_centroid_companion import load_tess_centroid_columns
from tess_toi4255_original_spoc_neb_vector_case import (
    TIC, NEIGHBOR, KNOWN_SECTORS,
    select_exact_source_products,download_original_mast,
    sky_wcs_from_tpf,neighbor_catalog_row,position_geometry,
    paired_original_events,summarize_pairs,physical_away_alignment
)

PHASE_OFFSETS=(-.25,.25)
BOOTSTRAPS=20000
SEED=2026111201


def median_direction_angle(x,y,direction):
    if not len(x) or len(x)!=len(y):
        return None
    return physical_away_alignment(
        [float(np.median(x)),float(np.median(y))],direction
    )


def bootstrap_paired_event_angles(frame, direction, seed=SEED, draws=BOOTSTRAPS):
    required=(
        "raw_signed_x_CCD_pixels","raw_signed_y_CCD_pixels",
        "pointing_subtracted_signed_x_CCD_pixels",
        "pointing_subtracted_signed_y_CCD_pixels"
    )
    if not set(required).issubset(frame.columns):
        raise ValueError("Prior frozen original observed event vector columns missing")
    x=frame[list(required)].to_numpy(dtype=float)
    if x.ndim!=2 or x.shape[1]!=4 or len(x)<3 or not np.isfinite(x).all():
        raise ValueError("Insufficient actual finite paired source-event vectors")
    direction=np.asarray(direction,dtype=float)
    if direction.shape!=(2,) or not np.isfinite(direction).all() or np.linalg.norm(direction)<=0:
        raise ValueError("Invalid external astrometric WCS direction")
    n=len(x)
    rng=np.random.default_rng(seed)
    ids=rng.integers(0,n,size=(draws,n))
    med=np.median(x[ids],axis=1)
    target_to_neighbor=direction/np.linalg.norm(direction)
    def angles(v):
        d=-np.einsum("ij,j->i",v,target_to_neighbor)
        n=np.linalg.norm(v,axis=1)
        good=n>0
        out=np.full(len(v),np.nan)
        out[good]=np.rad2deg(np.arccos(np.clip(d[good]/n[good],-1,1)))
        return out
    a=angles(med[:,:2])
    b=angles(med[:,2:])
    good=np.isfinite(a)&np.isfinite(b)
    if good.sum()<.95*draws:
        raise ValueError("Too many zero-magnitude original event bootstrap vectors")
    difference=(a-b)[good]
    raw_obs=median_direction_angle(x[:,0],x[:,1],direction)
    cor_obs=median_direction_angle(x[:,2],x[:,3],direction)
    if raw_obs is None or cor_obs is None:
        raise ValueError("Zero observed median event vector")
    return {
        "n_original_event_units_within_same_star":int(n),
        "raw_observed_angle_deg":raw_obs,
        "corrected_observed_angle_deg":cor_obs,
        "observed_raw_minus_corrected_angle_deg":float(raw_obs-cor_obs),
        "bootstrap_draws_requested":draws,
        "finite_paired_bootstrap_draws":int(good.sum()),
        "exploratory_event_bootstrap_95pct_raw_minus_corrected_angle_deg":np.quantile(
            difference,[.025,.975]).tolist(),
        "exploratory_fraction_resampled_samples_with_angle_improvement":float(
            (difference>0).mean()),
        "warning":"WITHIN THE SAME STAR/SECTOR event resampling only; correlated telescope systematics are not removed; not independent source validation"
    }


def strict_original_event_values(prior, now):
    """Reanalysis must exactly reproduce earlier published event/orbit vectors."""
    cols=(
        "original_ephemeris_predicted_center_BTJD",
        "raw_signed_x_CCD_pixels","raw_signed_y_CCD_pixels",
        "pointing_subtracted_signed_x_CCD_pixels",
        "pointing_subtracted_signed_y_CCD_pixels",
        "original_PDCSAP_local_flux_depth"
    )
    a=pd.DataFrame(prior).sort_values("orbit_index").reset_index(drop=True)
    b=pd.DataFrame(now).sort_values("orbit_index").reset_index(drop=True)
    if len(a)!=len(b) or not np.array_equal(a.orbit_index,b.orbit_index):
        raise ValueError("Previously fixed original observed source event identities changed")
    if not np.allclose(a[list(cols)].to_numpy(dtype=float),
                       b[list(cols)].to_numpy(dtype=float),rtol=1e-8,atol=1e-9):
        raise ValueError("Previously pinned source event values changed")
    return True


def run(prior_dir,source_discovery,original_neighbors,out,working):
    prior_dir=Path(prior_dir)
    source_discovery=Path(source_discovery)
    report=json.loads(source_discovery.read_text())
    manifest=select_exact_source_products(report)
    first=json.loads((prior_dir/
       "TOI4255_original_TESS_SPOC_WCS_offtarget_vector_case_study.json").read_text())
    if first["TIC_ID"]!=TIC or first["TOI"]!="4255.01":
        raise ValueError("Not the same original physically reported TIC")
    earlier={int(r["sector"]):r for r in first["sector_records"]}
    if set(earlier)!=set(KNOWN_SECTORS):
        raise ValueError("Prior original SPOC sector provenance changed")
    exo=report["cases"][str(TIC)]
    P=float(exo["original_ExoFOP_period_days"])
    E=float(exo["original_ExoFOP_epoch_BTJD"])
    D=float(exo["original_ExoFOP_duration_days"])
    if abs(P-first["original_ExoFOP_ephemeris"]["period_days"])>1e-12 or abs(
       E-first["original_ExoFOP_ephemeris"]["epoch_BTJD"])>1e-9:
        raise ValueError("No original ExoFOP ephemeris change allowed")
    neighbor=neighbor_catalog_row(Path(original_neighbors).read_bytes())
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    working=Path(working);working.mkdir(parents=True,exist_ok=True)
    final=[]
    for sector in KNOWN_SECTORS:
        prior=earlier[sector]
        if prior["source_status"]!="processed":
            raise ValueError("Previous original sector did not successfully process")
        meta={"sector":sector,"original_source_FITS_reused_not_reselected":True}
        paths={}
        for group in ("LC","TP"):
            product=manifest[sector][group]
            path=working/f"s{sector}"/product["productFilename"]
            current=download_original_mast(product["MAST_original_dataURI"],path)
            previous=prior["original_source_provenance"][group]
            if current["source_sha256"]!=previous["source_sha256"]:
                raise ValueError("Original TESS FITS SHA256 changed from first analysis")
            paths[group]=str(path)
            meta[group+"_SHA256"]=current["source_sha256"]
        frame,oldmeta=load_tess_centroid_columns(paths["LC"],TIC,sector)
        w,target,_=sky_wcs_from_tpf(paths["TP"],TIC,sector)
        geometry=position_geometry(w,target,neighbor)
        if not geometry["catalog_sky_geometry_consistent_with_TPF_target_position"]:
            raise ValueError("New WCS source geometry not consistent with original independent catalog")
        past_geo=prior["real_catalog_and_TPF_WCS_geometry"]
        if not np.allclose(geometry["target_to_neighbor_CCD_pixel_vector"],
                           past_geo["target_to_neighbor_CCD_pixel_vector"],atol=1e-10,rtol=1e-9):
            raise ValueError("External neighbor-to-TESS WCS direction changed")
        real_pairs,account=paired_original_events(frame,P,E,D,geometry)
        original_table=pd.read_csv(prior_dir/
                f"TOI4255_sector{sector}_original_SPOC_same_event_centroids.csv")
        strict_original_event_values(original_table,real_pairs)
        meta["frozen_original_eclipse_events_reproduced"]=len(real_pairs)
        meta["source_identical_orbit_pairs"]=account
        meta["original_same_event_direction_uncertainty"]=bootstrap_paired_event_angles(
            original_table,geometry["target_to_neighbor_CCD_pixel_vector"],
            seed=SEED+sector)
        controls=[]
        for fraction in PHASE_OFFSETS:
            # The same actual physical cadence data are measured at quarter-
            # period windows, chosen before looking at these control values.
            offset_E=E+fraction*P
            events,counts=paired_original_events(frame,P,offset_E,D,geometry)
            physical=summarize_pairs(events,geometry,sector)
            controls.append({
                "phase_offset_fraction_of_original_period":fraction,
                "offset_center_BTJD":offset_E,
                "same_actual_FITS_control_window_event_counts":counts,
                "control_measurements":physical,
                "not_true_eclipse_windows":True
            })
            if events:
                p=out/f"TOI4255_sector{sector}_control_{'minus' if fraction<0 else 'plus'}_quarter_period.csv"
                pd.DataFrame(events).to_csv(p,index=False)
        meta["quarter_phase_shifted_source_controls"]=controls
        print("CONTROL_RESULTS",json.dumps({
            "sector":sector,
            "original_event_uncertainty":meta["original_same_event_direction_uncertainty"],
            "quarter_phase_controls":controls
        }),flush=True)
        final.append(meta)

    summary={
        "purpose":"source-SHA pinned original SPOC same-TOI posthoc phase control and within-star event-bootstrap sensitivity",
        "TIC_ID":TIC,"TOI":"4255.01","reported_NEB_TIC_ID":NEIGHBOR,
        "source_sha256_original_event_snapshot":hashlib.sha256(
            (prior_dir/"TOI4255_original_TESS_SPOC_WCS_offtarget_vector_case_study.json").read_bytes()
        ).hexdigest(),
        "quarter_phase_offsets_preselected_before_control_analysis":list(PHASE_OFFSETS),
        "number_of_distinct_TIC_host_stars":1,
        "number_of_original_SPOC_sectors":2,
        "source_sector_sensitivity":final,
        "scientific_limits":[
            "Source and controls are from one post-hoc selected NEB, not two independent host stars.",
            "The original 8 and 10 source eclipse windows were exactly reproduced from SHA-pinned original 2-minute TESS SPOC FITS.",
            "Quarter-period windows can contain other stellar variability, secondary binary eclipses, or residual systematics; not perfect astrophysical noise-only controls.",
            "Resampling repeated eclipse windows within the same star does not create independent source stars and does not measure mission-level false-positive or planet validation accuracy.",
            "The simple two-star centroid direction is a surrogate, not NASA DV difference-image PRF localization.",
            "No NASA ExoMiner++ model weights or pretrained outputs modified; no new planet claimed."
        ]
    }
    (out/"TOI4255_same_original_source_quarter_phase_control_and_angle_bootstrap.json").write_text(
        json.dumps(summary,indent=2)+"\n")
    # Plain descriptive companion figure, no error bars masquerading as mission truth.
    fig,axes=plt.subplots(1,2,figsize=(10,4.4))
    for i,sector in enumerate(KNOWN_SECTORS):
        z=final[i]
        a=z["original_same_event_direction_uncertainty"]
        ctr=z["quarter_phase_shifted_source_controls"]
        axes[i].plot([0,1,2],[
            a["corrected_observed_angle_deg"],
            ctr[0]["control_measurements"].get("pointing_subtracted_median_vector_angular_difference_away_neighbor_deg") or np.nan,
            ctr[1]["control_measurements"].get("pointing_subtracted_median_vector_angular_difference_away_neighbor_deg") or np.nan,
        ],"o-",label="Pointing subtracted")
        axes[i].plot([0,1,2],[
            a["raw_observed_angle_deg"],
            ctr[0]["control_measurements"].get("raw_median_vector_angular_difference_away_neighbor_deg") or np.nan,
            ctr[1]["control_measurements"].get("raw_median_vector_angular_difference_away_neighbor_deg") or np.nan,
        ],"s--",label="Raw MOM_CENTR")
        axes[i].set(xticks=[0,1,2],xticklabels=["Real eclipse","-P/4","+P/4"],
                    ylim=(0,180),ylabel="Angular mismatch (degrees)",
                    title=f"Same TIC, TESS sector {sector}")
        axes[i].legend(frameon=False,fontsize=9)
    fig.suptitle("Off-target neighbor direction at true and shifted windows (post-hoc control)")
    fig.tight_layout()
    fig.savefig(out/"TOI4255_original_SPOC_true_vs_quarter_phase_WCS_direction.png",dpi=170)
    plt.close(fig)
    return summary


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--prior-results",required=True)
    p.add_argument("--mast-discovery",required=True)
    p.add_argument("--exofop-neighbors",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--working",required=True)
    a=p.parse_args()
    run(a.prior_results,a.mast_discovery,a.exofop_neighbors,a.out,a.working)
