"""Engineering tests of post-hoc published stellar eclipse crosscheck."""
import pytest
from recurrence_guard_external_ephemeris_audit import (
    PUBLICATION,nearest_published_eclipse,load_protected_rows,evaluate_timings
)


def test_kepler35_warning_precedes_known_primary_stellar_eclipse():
    r=nearest_published_eclipse(568.1390909870752,PUBLICATION[9837578])
    assert r["eclipse_type"]=="primary"
    assert r["residual_hours"]==pytest.approx(-2.799093,abs=.01)


def test_kepler1647_warning_precedes_known_secondary_stellar_eclipse():
    r=nearest_published_eclipse(568.650480110693,PUBLICATION[5473556])
    assert r["eclipse_type"]=="secondary"
    assert r["residual_hours"]==pytest.approx(-3.467943,abs=.02)


def test_published_ephemeris_does_not_get_passed_to_detector():
    rows=[
        {"kic":"5473556","product":"SAP","warning_time_bkjd":"568.650480110693",
         "recovered_period_days":"11.24","supporting_other_cycles":"7",
         "other_cycles_with_valid_windows":"7","jump_fraction":".0037",
         "archival_spsd_event_near_warning":"False"}
    ]
    matched=evaluate_timings(rows)
    assert len(matched)==1
    assert matched[0]["recovered_period_without_published_input"]==11.24
    assert matched[0]["published_stellar_period_days"]>11.25


def test_wrong_warning_original_csv_is_rejected(tmp_path):
    fake=tmp_path/"fake.csv"
    fake.write_text("protected_as_periodic,kic\nTrue,5473556\n")
    with pytest.raises(ValueError,match="unmodified frozen"):
        load_protected_rows(fake)


def test_cannot_silently_omit_extra_protected_source():
    with pytest.raises(KeyError):
        evaluate_timings([{
            "kic":"9999999","warning_time_bkjd":"560","product":"SAP",
            "recovered_period_days":"7","supporting_other_cycles":"7",
            "other_cycles_with_valid_windows":"7","jump_fraction":".02",
            "archival_spsd_event_near_warning":"False"}])
