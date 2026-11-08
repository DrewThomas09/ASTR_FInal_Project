"""Unit tests of frozen SAP-vs-PDCSAP SPSD label accounting, not astronomy performance."""
import numpy as np
import pytest

from real_spsd_external_cohort import (
    cohort_manifest, common_flux_rows, cluster_archival_events,
    unique_match, paired_event_rows, summarize
)


def test_frozen_external_cohort_has_12_non_repeated_stars():
    m = cohort_manifest()
    assert len(m["targets"]) == 12
    assert m["quarter"] == 6
    assert all(t["kic"] != 7461601 for t in m["targets"])


def test_simultaneous_flux_filter_retains_nonzero_archival_quality():
    t = np.arange(600, dtype=float) / 48.
    sap = np.full(600, 15000.)
    pdc = np.full(600, 14500.)
    q = np.zeros(600, dtype=int)
    q[10] = 1024
    sap[20] = np.nan
    result = common_flux_rows(t, sap, pdc, q, min_cadences=500)
    assert result[-1] == 1
    assert len(result[0]) == 599
    assert (result[3] == 1024).sum() == 1


def test_simultaneous_data_reject_bad_time_order():
    t = np.arange(600, dtype=float) / 48.
    t[100] = t[99]
    with pytest.raises(ValueError):
        common_flux_rows(t, np.ones(600), np.ones(600), np.zeros(600,int))


def test_markers_cluster_within_predeclared_half_day_window():
    t = np.arange(0, 15, .02)
    q = np.zeros(len(t),dtype=int)
    for stamp in [1.0, 1.02, 1.04, 3.0]:
        q[np.argmin(abs(t-stamp))] |= 1024
    events = cluster_archival_events(t,q)
    assert len(events) == 2
    assert [e["marked_cadences"] for e in events] == [3,1]


def test_archival_bit_is_not_generic_flag():
    t = np.arange(600)/48.
    q = np.zeros(600,dtype=int)
    q[15]=128; q[20]=1152
    ev=cluster_archival_events(t,q)
    assert len(ev)==1
    assert ev[0]["marked_cadences"] == 1


def test_unique_match_does_not_reuse_one_warning_for_two_events():
    events=[{"event_id":0,"archived_time_bkjd":10.},
            {"event_id":1,"archived_time_bkjd":10.15}]
    matched, unused=unique_match(events,[10.08])
    assert len(matched)==1
    assert unused==[]


def test_unmatched_warning_is_not_called_false_positive():
    events=[{"event_id":0,"archived_time_bkjd":10.1,"marked_cadences":1}]
    rows,sap_unused,pdc_unused=paired_event_rows(123,events,[11.],[10.12])
    assert rows[0]["sap_match"] is False
    assert rows[0]["pdc_match"] is True
    assert sap_unused == [0] and pdc_unused==[]


def test_exact_boundary_counts_as_match():
    events=[{"event_id":0,"archived_time_bkjd":10.,"marked_cadences":1}]
    matched,_=unique_match(events,[10.22],tolerance=.22)
    assert 0 in matched


def test_reject_posthoc_tolerance_changes():
    with pytest.raises(ValueError):
        unique_match([],[],tolerance=.5)
    with pytest.raises(ValueError):
        cluster_archival_events(np.arange(10.),np.zeros(10,int),merge_days=.6)


def test_summarize_includes_unavailable_and_no_archival_events():
    stars=[
        {"kic":1,"status":"analyzed","n_archived_event_clusters":0,
         "n_sap_warnings":2,"n_pdc_warnings":0,"n_sap_unmatched_warnings":2,
         "n_pdc_unmatched_warnings":0},
        {"kic":2,"status":"source_or_analysis_error"},
    ]
    report=summarize(stars,[],[{"kic":1},{"kic":1}])
    assert report["n_planned_stars"] == 2
    assert report["n_analyzed_stars"] == 1
    assert report["n_unavailable_stars"] == 1
    assert report["n_archived_spsd_event_clusters"] == 0
    assert report["n_sap_unmatched_warnings"] == 2
    assert report["no_new_exoplanet_discovery"] is True


def test_mcnemar_paired_label_category_accounting():
    stars=[
        {"status":"analyzed","n_archived_event_clusters":4,
         "n_sap_warnings":3,"n_pdc_warnings":2,
         "n_sap_unmatched_warnings":0,"n_pdc_unmatched_warnings":0}]
    rows=[
        {"sap_match":True,"pdc_match":True},
        {"sap_match":True,"pdc_match":False},
        {"sap_match":False,"pdc_match":True},
        {"sap_match":False,"pdc_match":False}]
    report=summarize(stars,rows,[])
    assert report["archival_event_detection"] == {
        "both":1,"sap_only":1,"pdc_only":1,"neither":1}
