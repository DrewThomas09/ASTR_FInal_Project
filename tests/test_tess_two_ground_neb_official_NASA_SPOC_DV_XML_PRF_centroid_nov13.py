"""Synthetic official NASA TESS SPOC XML schemas; not real source truth."""
import pytest

from tess_two_ground_neb_official_NASA_SPOC_DV_XML_PRF_centroid_nov13 import (
    HOSTS,PHASE_MATCH_DURATIONS,PERIOD_MATCH_FRACTION,
    original_nasa_dv_source_xml,source_tce_match,
    original_dv_match_centroids,wrapped_phase_separation_days,metric_element
)


def source(tic=382437043,p=1.5,epoch=1450.,quality=True,planet_id=1):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
    <dv:dvTargetResults xmlns:dv="http://www.nasa.gov/2018/TESS/DV" ticId="{tic}" planetCandidateCount="1" sectorsObserved="001">
      <dv:planetResults planetNumber="{planet_id}">
        <dv:planetCandidate>
          <dv:orbitalPeriod value="{p}" uncertainty="0.001"/>
          <dv:transitEpoch value="{epoch}" uncertainty="0.0005"/>
        </dv:planetCandidate>
        <dv:differenceImageResults sector="1">
          <dv:ticReferenceCentroid>
            <dv:raDegrees value="70" uncertainty="0.00001"/>
            <dv:decDegrees value="-15" uncertainty="0.00001"/>
          </dv:ticReferenceCentroid>
          <dv:differenceImageCentroid>
            <dv:raDegrees value="70.0005" uncertainty="0.00001"/>
            <dv:decDegrees value="-15.0001" uncertainty="0.00001"/>
          </dv:differenceImageCentroid>
          <dv:qualityMetric attempted="true" valid="{'true' if quality else 'false'}" value="0.8"/>
        </dv:differenceImageResults>
      </dv:planetResults>
    </dv:dvTargetResults>'''.encode()


def test_exact_source_identity_period_and_epoch_match_BEFORE_prf_read():
    root,allplan,meta=original_nasa_dv_source_xml(source(),382437043)
    assert meta["original_DV_root_ticId"]==382437043
    assert meta["original_DV_actual_planetResults_count"]==1
    c=allplan[0]
    assert c["original_NASA_DV_candidate_period_days"]==pytest.approx(1.5)
    assert c["original_NASA_DV_candidate_epoch_BTJD"]==pytest.approx(1450)
    assert source_tce_match(c,1.5,1450.,.1)[
        "matches_published_original_TOI_period_and_phase_before_any_centroid_read"]
    assert not source_tce_match(c,3.,1450.,.1)[
        "matches_published_original_TOI_period_and_phase_before_any_centroid_read"]
    assert not source_tce_match(c,1.5,1450.5,.1)[
        "matches_published_original_TOI_period_and_phase_before_any_centroid_read"]


def test_actual_official_nasa_sky_prf_direction_no_swap():
    root,_,_=original_nasa_dv_source_xml(source(),382437043)
    r=original_dv_match_centroids(
        list(root)[0],1,(70.,-15.),(70.00051,-15.0001))
    assert r["n_valid_original_NASA_DV_PRF_first_sector_centroids"]==1
    m=r["original_DV_first_frozen_sector_difference_image_result_rows"][0]
    assert m["original_NASA_DV_PRF_nominally_closer_to_externally_ground_reported_neighbor"]
    assert m["original_NASA_DV_PRF_to_ground_observed_neighbor_arcsec"]<m[
        "original_NASA_DV_PRF_to_primary_host_arcsec"]
    assert m["original_DV_first_sector_PRF_physically_interpretable"]


def test_invalid_official_quality_cannot_be_promoted_to_valid_sky_localization():
    root,_,_=original_nasa_dv_source_xml(source(quality=False),382437043)
    r=original_dv_match_centroids(
        list(root)[0],1,(70.,-15.),(70.00051,-15.0001))
    assert r["n_valid_original_NASA_DV_PRF_first_sector_centroids"]==0
    bad=source().replace(b'uncertainty="0.00001"',b'uncertainty="-1"',1)
    root,_,_=original_nasa_dv_source_xml(bad,382437043)
    assert original_dv_match_centroids(list(root)[0],1,(70.,-15.),(70.00051,-15.0001))[
        "n_valid_original_NASA_DV_PRF_first_sector_centroids"]==1  # target TIC invalid, but PRF DI valid


def test_wrapped_phase_measured_cyclic_not_far_history_dates_and_XML_forgery_rejected():
    assert wrapped_phase_separation_days(1450.,1450.+19*1.5+.01,1.5)==pytest.approx(.01,abs=1e-12)
    assert PERIOD_MATCH_FRACTION==.01
    assert PHASE_MATCH_DURATIONS==3
    assert HOSTS=={382437043:"1223.01",264303333:"2250.01"}
    with pytest.raises(ValueError,match="exact requested"):
        original_nasa_dv_source_xml(source(tic=382437043),264303333)
    malicious=source().replace(b'<dv:dvTargetResults',b'<!DOCTYPE foo><dv:dvTargetResults')
    with pytest.raises(ValueError,match="embedded"):
        original_nasa_dv_source_xml(malicious,382437043)
