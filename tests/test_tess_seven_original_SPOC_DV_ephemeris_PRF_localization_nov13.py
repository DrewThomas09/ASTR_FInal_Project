"""Synthetic NASA official DVR XML tests, never substitute actual TESS PRF sky values."""
import xml.etree.ElementTree as ET
import pytest
from tess_seven_original_SPOC_DV_ephemeris_PRF_localization_nov13 import (
    safe_float,correct_TCE_period_and_epoch,source_DV_TCEs,
    extract_first_sector_dv_PRF,coord_from_xml,SKY_TARGET_CONSISTENCY_ARCSEC
)
from astropy.coordinates import SkyCoord
from astropy import units as u


def node(name,**kw):
    return ET.Element(name,{str(k):str(v) for k,v in kw.items()})


def sky(c,ra,dec):
    for key,value in (("raDegrees",ra),("decDegrees",dec),
                      ("row",50.0),("column",400.0)):
        c.append(node(key,value=value,uncertainty=.001))


def xml_example(period=2.,epoch=100.,toi=None,sector=14,source_ra=100.00015):
    root=node("dvTargetResults",ticId=264303333)
    pp=ET.SubElement(root,"planetResults",{
        "planetNumber":"1",**({"toiId":toi} if toi is not None else {})})
    pp.append(node("planetCandidate",orbitalPeriodInDays=period,epochTjd=epoch,
                   observedTransitCount=8))
    di=ET.SubElement(pp,"differenceImageResults",sector=sector,numberOfTransits=8)
    ET.SubElement(di,"qualityMetric",attempted="true",valid="true",value="1.0")
    sky(ET.SubElement(di,"ticReferenceCentroid"),100.,20.)
    sky(ET.SubElement(di,"controlImageCentroid"),100.,20.)
    sky(ET.SubElement(di,"differenceImageCentroid"),source_ra,20.)
    return root


def ground_source():
    return {
      "TIC_ID":264303333,"TOI":"2250.01",
      "source_frozen_first_SPOC_2min_sector":14,
      "original_ExoFOP_period_days":2.,
      "original_ExoFOP_epoch_BTJD":100.,
      "original_ExoFOP_duration_days":.1,
      "original_primary_NASA_ra":100.,"original_primary_NASA_dec":20.,
      "original_nearby_catalog_RA_deg":100.00016,
      "original_nearby_catalog_Dec_deg":20.,
    }


def test_strict_ephemeris_match_and_phase_fold_are_required_before_interpreting_PRF():
    pp=node("planetCandidate",orbitalPeriodInDays=2.,epochTjd=100.)
    assert correct_TCE_period_and_epoch(pp,2.,102.,.1)["match"] is True
    assert not correct_TCE_period_and_epoch(pp,3.,102.,.1)["match"]
    assert not correct_TCE_period_and_epoch(
        node("planetCandidate",orbitalPeriodInDays=2.,epochTjd=100.6),2.,100.,.1)["match"]
    assert safe_float(float("nan")) is None
    assert SKY_TARGET_CONSISTENCY_ARCSEC==8.


def test_same_period_but_explicit_different_TOI_label_is_rejected():
    s=ground_source()
    xml=xml_example(toi="9999.01")
    r=source_DV_TCEs(xml,s,ground=s)
    assert r["original_TCEs_meeting_TESS_TOI_period_and_epoch_and_ID_rules"]==0
    assert r["same_ephemeris_first_sector_localization_status"]=="no_unambiguous_original_TOI_corresponding_TCE"
    assert r["official_original_NASA_SPOC_TCE_and_sector_PRF_diagnostics_all"][0][
        "all_original_TCE_timing_compatibility_checks"]["official_explicit_TOI_ID_compatible"] is False


def test_ground_neighbor_PRF_sky_position_measured_in_only_original_first_sector():
    s=ground_source()
    r=source_DV_TCEs(xml_example(),s,ground=s)
    assert r["only_one_TOI_compatible_TCE"] is True
    p=r["official_original_NASA_SPOC_TCE_and_sector_PRF_diagnostics_all"][0]
    assert p["original_DV_first_sector_fit_count"]==1
    z=p["original_DV_first_sector_fit_records_all"][0]
    assert z["original_first_sector_DV_position_quality_guard_passed"] is True
    assert z["official_PRF_fit_closer_to_original_ground_NEb_than_original_host"] is True
    r=source_DV_TCEs(xml_example(sector=99),s,ground=s)
    assert r["only_one_TOI_compatible_TCE"]
    assert r["same_ephemeris_first_sector_localization_status"]=="same_ephemeris_TCE_but_original_frozen_sector_DV_image_missing"


def test_unmatched_or_ambiguous_original_mission_TCE_cannot_be_classified():
    s=ground_source()
    r=source_DV_TCEs(xml_example(period=4.),s,ground=s)
    assert r["only_one_TOI_compatible_TCE"] is False
    root=xml_example()
    other=xml_example()[0]
    root.append(other)
    r=source_DV_TCEs(root,s,ground=s)
    assert r["original_TCEs_meeting_TESS_TOI_period_and_epoch_and_ID_rules"]==2
    assert r["only_one_TOI_compatible_TCE"] is False


def test_invalid_true_PRF_coords_not_filled_or_treated_as_source():
    src=ground_source()
    root=xml_example(source_ra=370.)
    r=source_DV_TCEs(root,src,ground=src)
    first=r["official_original_NASA_SPOC_TCE_and_sector_PRF_diagnostics_all"][0][
        "original_DV_first_sector_fit_records_all"][0]
    assert first["original_first_sector_DV_position_quality_guard_passed"] is False
    assert first["official_PRF_fit_closer_to_original_ground_NEb_than_original_host"] is None


def test_mission_official_PRF_zero_coordinates_with_negative_uncertainty_are_missing_not_real_sky():
    invalid=node("differenceImageCentroid")
    for key in ("raDegrees","decDegrees"):
        invalid.append(node(key,value=0.0,uncertainty=-1.0))
    assert coord_from_xml(invalid) is None
    root=xml_example()
    for el in root.iter("differenceImageCentroid"):
        for c in el:
            if c.tag in ("raDegrees","decDegrees"):
                c.attrib["value"]="0.0"
                c.attrib["uncertainty"]="-1.0"
    s=ground_source()
    r=source_DV_TCEs(root,s,ground=s)
    z=r["official_original_NASA_SPOC_TCE_and_sector_PRF_diagnostics_all"][0][
        "original_DV_first_sector_fit_records_all"][0]
    assert z["original_mission_PRF_source_to_original_external_host_arcsec"] is None
    assert z["official_PRF_fit_closer_to_original_ground_NEb_than_original_host"] is None
    assert z["original_first_sector_DV_position_quality_guard_passed"] is False


def test_confirmed_planet_source_uses_independent_NASA_archive_sky_coordinates():
    planet={
        "TIC_ID":36352297,"TOI":"547.01",
        "source_frozen_first_SPOC_2min_sector":14,
        "original_ExoFOP_period_days":2.,
        "original_ExoFOP_epoch_BTJD":100.,
        "original_ExoFOP_duration_days":.1,
        "NASA_confirmed_host_catalog_RA_deg":100.,
        "NASA_confirmed_host_catalog_Dec_deg":20.
    }
    r=source_DV_TCEs(xml_example(),planet,ground=None)
    assert r["only_one_TOI_compatible_TCE"] is True
    z=r["official_original_NASA_SPOC_TCE_and_sector_PRF_diagnostics_all"][0][
        "original_DV_first_sector_fit_records_all"][0]
    assert z["original_mission_PRF_source_to_original_external_host_arcsec"]>0.
    assert z["original_mission_PRF_source_to_original_ground_reported_neighbor_arcsec"] is None


def test_original_SPOC_explicit_PRF_quality_invalid_cannot_be_accepted_as_physical_sky_source():
    original=xml_example()
    for q in original.iter("qualityMetric"):
        q.attrib["valid"]="false"
    s=ground_source()
    r=source_DV_TCEs(original,s,ground=s)
    x=r["official_original_NASA_SPOC_TCE_and_sector_PRF_diagnostics_all"][0][
        "original_DV_first_sector_fit_records_all"][0]
    assert x["original_PRF_ra_dec_uncertainties_valid"]
    assert x["original_mission_PRF_qualityMetric"]["attempted"] is True
    assert x["original_mission_PRF_qualityMetric"]["valid"] is False
    assert x["original_first_sector_DV_position_quality_guard_passed"] is False
