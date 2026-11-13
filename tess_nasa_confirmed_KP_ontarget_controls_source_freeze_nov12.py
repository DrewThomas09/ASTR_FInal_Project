"""Freeze independently catalogued confirmed transiting-planet control hosts before reading centroid data.

Two original public sources:
  * pinned ExoFOP official TIC/TOI catalog original byte snapshot
  * fresh NASA Exoplanet Archive official PSCompPars confirmed-transiting catalogue
Matching requires exact TIC and matching period, TOI TFOPWG KP, noncontroversial
non-circumbinary NASA confirmed transiting planet and original real SPOC two-minute
LC+TP product availability. This is *catalogue confirmed*, not independent
photometric on-target sky localization or independence from NASA model training.
No MOM_CENTR, POS_CORR or classification scores are read in this step.
"""
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

import requests

from exofop_neb_candidate_screen import excluded_tics
from tess_neb_new_host_precentroid_original_spoc_coverage import original_mast_coverage

NASA_TAP="https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
TAP_QUERY=("select pl_name,hostname,tic_id,tran_flag,cb_flag,pl_controv_flag,"
           "pl_orbper,pl_tranmid,ra,dec from pscomppars "
           "where tran_flag=1 and tic_id is not null")
EXOFOP_SEED="ASTR_CONFIRMED_PLANET_CONTROL_20261112_BEFORE_MOMCENTR"
EXCLUDED_EXTRA={54364414,82302240,357457104,382437043,354442783,66151343,264303333}
MAX_ORIGINAL_MAST_QUERIES=30
N_PREDECLARED_HOSTS=5


def match_tic(tic):
    text=str(tic or "").strip()
    m=re.fullmatch(r"(?:TIC\s*)?([0-9]{6,11})(?:\.0)?",text,flags=re.I)
    return int(m.group(1)) if m else None


def finite_positive(text):
    try:
        x=float(text)
        return x if 0<x<float("inf") else None
    except (TypeError,ValueError):
        return None


def original_nasa_confirmed_transiting_rows(raw):
    d=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    req={"tic_id","pl_name","tran_flag","cb_flag","pl_controv_flag","pl_orbper","ra","dec"}
    if not req.issubset(d.fieldnames or []):
        raise ValueError("NASA original PSCompPars source is missing required confirmed planet columns")
    stars={}
    counts=Counter()
    for r in d:
        counts["original_nasa_transiting_rows"]+=1
        tic=match_tic(r.get("tic_id"))
        if tic is None:
            counts["missing_or_ambiguous_TIC"]+=1
            continue
        try:
            if int(float(r["tran_flag"]))!=1 or int(float(r["cb_flag"]))!=0 or int(float(r["pl_controv_flag"]))!=0:
                counts["not_noncontroversial_single_host_transiting_planet"]+=1
                continue
        except (ValueError,TypeError):
            counts["missing_physical_flags"]+=1
            continue
        p=finite_positive(r.get("pl_orbper"))
        ra=finite_positive(r.get("ra"))
        try:dec=float(r.get("dec"))
        except (ValueError,TypeError):dec=None
        if p is None or p>6 or ra is None or dec is None or not -90<=dec<=90:
            counts["period_or_sky_unusable"]+=1
            continue
        stars.setdefault(tic,[]).append({
            "NASA_confirmed_planet":str(r["pl_name"]).strip(),
            "NASA_transit_period_days":p,
            "NASA_host_ra_deg":ra,
            "NASA_host_dec_deg":dec,
            "NASA_confirmation_basis":"official PSCompPars listing with tran_flag=1, cb_flag=0, pl_controv_flag=0"
        })
        counts["NASA_TIC_confirmed_transit_and_period_rows"]+=1
    return stars,counts


def match_original_exofop_kp_to_nasa(original_exofop,nasa,excluded):
    d=csv.DictReader(io.StringIO(original_exofop.decode("utf-8-sig")))
    required={"TIC ID","TOI","TFOPWG Disposition","Period (days)","Epoch (BJD)","Duration (hours)"}
    if not required.issubset(d.fieldnames or []):
        raise ValueError("Pinned original ExoFOP TIC/TOI snapshot missing required catalog fields")
    counts=Counter()
    candidates={}
    for row in d:
        counts["original_exofop_toi_rows"]+=1
        if str(row.get("TFOPWG Disposition","")).strip().upper()!="KP":
            continue
        counts["original_KP_rows"]+=1
        tic=match_tic(row.get("TIC ID"))
        if tic is None or tic in excluded:
            counts["excluded_or_bad_host_TIC"]+=1
            continue
        p=finite_positive(row.get("Period (days)"))
        duration=finite_positive(row.get("Duration (hours)"))
        epoch=finite_positive(row.get("Epoch (BJD)"))
        if p is None or p>6 or duration is None or epoch is None or not 2457000<epoch<2600000:
            counts["no_short_period_original_KP_ephemeris"]+=1
            continue
        d_days=duration/24
        if not (0<d_days<.2*p):
            counts["duration_incompatible_with_orbit"]+=1
            continue
        hits=[n for n in nasa.get(tic,[]) if abs(n["NASA_transit_period_days"]/p-1)<.01]
        if len(hits)!=1:
            counts["no_unique_independent_NASA_confirmed_planet_same_TIC_and_period"]+=1
            continue
        h=hits[0]
        toi=str(row["TOI"]).strip()
        if not re.fullmatch(r"[0-9]{1,6}\.[0-9]{2}",toi):
            counts["invalid_TOI"]+=1
            continue
        sortkey=hashlib.sha256((EXOFOP_SEED+"|"+str(tic)+"|"+toi).encode()).hexdigest()
        result={
            "TIC_ID":tic,"TOI":toi,
            "source_selection_seeded_sha256_before_centroids":sortkey,
            "NASA_confirmed_host_alias":h["NASA_confirmed_planet"],
            "NASA_confirmed_transiting_planet_catalog_period_days":h["NASA_transit_period_days"],
            "NASA_confirmed_host_catalog_RA_deg":h["NASA_host_ra_deg"],
            "NASA_confirmed_host_catalog_Dec_deg":h["NASA_host_dec_deg"],
            "original_ExoFOP_TFOPWG_Disposition":"KP",
            "original_ExoFOP_period_days":p,
            "original_ExoFOP_epoch_BTJD":epoch-2457000,
            "original_ExoFOP_duration_days":d_days,
            "NASA_period_fractional_difference":abs(h["NASA_transit_period_days"]/p-1),
            "NASA_archive_confirmed_transit_and_ExoFOP_KP_agree":True,
            "independently_verified_on_target_ground_lightcurve_source":False,
            "NASA_ExoMiner_classifier_prediction_not_queried":True,
            "MOM_CENTR_or_POS_CORR_not_queried":True
        }
        # For multiple TOI rows around one host, select deterministically without
        # consulting centroid or flux, yielding one independent source unit.
        if tic not in candidates or sortkey<candidates[tic]["source_selection_seeded_sha256_before_centroids"]:
            candidates[tic]=result
    ordered=sorted(candidates.values(),key=lambda x:x["source_selection_seeded_sha256_before_centroids"])
    counts["unique_independent_NASA_and_KP_concordant_host_TICs"]=len(ordered)
    return ordered,counts


def choose_product_pair(candidate,available):
    sectors=sorted(set(int(s) for s in available["genuine_2min_SPOC_LC_TP_sectors"]))
    if not sectors:
        raise ValueError("No exact original SPOC 2-minute source product pair")
    sector=sectors[0]
    pairs={}
    for kind in ("LC","TP"):
        hits=[p for p in available["matching_original_SPOC_products"]
              if p["product_group"]==kind and
              int(p["sector"])==sector and
              int(p["TIC_ID"])==int(candidate["TIC_ID"]) and
              f"{candidate['TIC_ID']:016d}" in p["productFilename"]]
        if len(hits)!=1:
            raise ValueError("No unique original TIC/first-sector SPOC source "+kind+" product")
        pairs[kind]=hits[0]
    return sector,pairs


def run(repo_root,original_exofop_csv,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    pinned=Path(original_exofop_csv).read_bytes()
    if len(pinned)<10000:raise ValueError("Original ExoFOP source catalog too small")
    req=requests.get(NASA_TAP,params={"query":TAP_QUERY,"format":"csv"},
        timeout=(30,180),headers={"User-Agent":"Student-ASTR-TESS-NASA-Confirmed-Planet-OnTarget-Control-Source-Only/1.0"})
    req.raise_for_status()
    nasa_raw=req.content
    if len(nasa_raw)<10000:raise ValueError("Original NASA archive confirmed transiting planet source unexpectedly small")
    (out/"original_NASA_exoplanet_archive_PSCompPars_confirmed_transits_snapshot.csv").write_bytes(nasa_raw)
    nasa,count_nasa=original_nasa_confirmed_transiting_rows(nasa_raw)
    excluded=excluded_tics(repo_root)|EXCLUDED_EXTRA
    candidates,count_exofop=match_original_exofop_kp_to_nasa(pinned,nasa,excluded)
    selected=[];attempts=[]
    for c in candidates[:MAX_ORIGINAL_MAST_QUERIES]:
        attempt=dict(c)
        try:
            obs,nspoc,products,sectors=original_mast_coverage(c["TIC_ID"])
            attempt.update(
                source_coverage_status="success",
                original_MAST_TESS_obs_rows=obs,
                original_MAST_SPOC_exact_target_observation_rows=nspoc,
                genuine_2min_SPOC_LC_TP_sectors=sectors,
                matching_original_SPOC_products=products)
            sector,pair=choose_product_pair(c,attempt)
            frozen={**c,
                "selected_first_original_SPOC_2min_sector":sector,
                "original_MAST_products":pair,
                "original_all_matching_two_min_sectors":sectors,
                "selection_rule_frozen_before_centroid":"earliest actual SPOC LC+TP paired sector",
                "MOM_CENTR_or_POS_CORR_not_queried":True,
                "no_mission_classifier_score_inspected":True}
            selected.append(frozen)
        except Exception as exc:
            attempt.update(source_coverage_status="no_eligible_source_or_original_MAST_error",
                           source_error=str(exc)[:350])
        attempts.append(attempt)
        print("ON_TARGET_CATALOG_MAST_ONLY",json.dumps({
            "TIC":c["TIC_ID"],"TOI":c["TOI"],"confirmed":c["NASA_confirmed_host_alias"],
            "status":attempt["source_coverage_status"],
            "first_source_sector":attempt.get("genuine_2min_SPOC_LC_TP_sectors",[None])[0]
                 if attempt.get("genuine_2min_SPOC_LC_TP_sectors") else None,
            "source_stars_frozen_count_so_far":len(selected),
            "source_error":attempt.get("source_error")
        }),flush=True)
        if len(selected)==N_PREDECLARED_HOSTS:break
    # Preserve even failed/rejected source IDs and source counts. Do not replace on any
    # measured centroid outcomes, which have not yet been downloaded or examined.
    manifest={
        "experiment_id":"ASTR_NASA_AND_EXOFOP_KP_CONFIRMED_TRANSITING_ON_TARGET_CONTROL_SPOC_SOURCE_FROZEN_NOV12",
        "source_manifest_frozen_before_any_control_TESS_centroid_measurements":True,
        "original_NASA_PSCompPars_source_URL":req.url,
        "original_NASA_PSCompPars_source_SHA256":hashlib.sha256(nasa_raw).hexdigest(),
        "original_ExoFOP_catalog_source_SHA256":hashlib.sha256(pinned).hexdigest(),
        "original_NASA_source_row_counters":dict(count_nasa),
        "original_ExoFOP_source_row_counters":dict(count_exofop),
        "excluded_prior_56_pilot_ground_NEB_host_count":len(excluded),
        "predeclared_source_screen_rule":[
            "Use original ExoFOP source TFOPWG disposition KP AND a separate NASA Exoplanet Archive PSCompPars confirmed transit flag, no circumbinary/controversial flag, exact TIC and period difference <1%.",
            "Only valid ExoFOP original ephemeris P <= 6 days, event duration <0.2 period; all candidate rules fixed before source selection.",
            "Hash-order distinct host TICs with a fixed seed, query at most 30 independently matched candidates for MAST SPOC original two-minute LC and TP, freeze the first five eligible source hosts.",
            "Frozen sector is lowest-numbered actually available exact SPOC LC/TP product pair, no centroid or model output selection.",
            "On-target catalogue confidence does not independently prove pixel-level eclipse locality or absence of a nearby eclipsing contaminant."
        ],
        "predeclared_distinct_control_host_TICs_target":N_PREDECLARED_HOSTS,
        "distinct_original_catalog_verified_controls_frozen":len(selected),
        "original_MAST_availability_queries_executed":len(attempts),
        "full_source_screen_no_centroid_rejection_or_optimization":attempts,
        "source_records":selected,
        "independent_ground_based_on_target_image_photometry_verified_hosts":0,
        "original_TESS_centroids_viewed":0,
        "scope_not_train_independent_or_physically_truth_labeled":True
    }
    (out/"FROZEN_NASA_KP_on_target_five_original_SPOC_source_manifest_BEFORE_centroids.json").write_text(
        json.dumps(manifest,indent=2,default=str)+"\n")
    print("FROZEN_CONFIRMED_ON_TARGET_SOURCE_SUMMARY",json.dumps({
        "original_nasa_source_hash":manifest["original_NASA_PSCompPars_source_SHA256"],
        "original_exofop_source_hash":manifest["original_ExoFOP_catalog_source_SHA256"],
        "candidates_independently_catalog_concordant":len(candidates),
        "source_MAST_queries":len(attempts),
        "on_target_catalogue_confirmed_distinct_host_TICs":len(selected),
        "selected_sources":[{"TIC_ID":x["TIC_ID"],"TOI":x["TOI"],
             "NASA_confirmed_planet":x["NASA_confirmed_host_alias"],
             "frozen_first_sector":x["selected_first_original_SPOC_2min_sector"]}
             for x in selected],
        "moment_centroid_data_evaluated":0
    }),flush=True)
    return manifest


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-exofop-catalog",required=True)
    p.add_argument("--repo-root",default=".")
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.repo_root,a.original_exofop_catalog,a.out)
