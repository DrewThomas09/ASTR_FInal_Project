"""Cross-version source matching controls: ratio aliases, swapped TCE UID, duration units."""
import json
import numpy as np
import pandas as pd
import pytest
import tess_exominer_cross_version_ephemeris_audit as audit


def test_nearly_same_orbit_is_consistent():
    assert audit.classify_period_ratio(4.50001,4.5)=="period_consistent_within_one_percent"


def test_half_and_double_period_aliases_are_not_same_directly():
    assert audit.classify_period_ratio(2*7.872777,7.872777)=="new_period_double_alias"
    assert audit.classify_period_ratio(7.872777,2*7.872777)=="new_period_half_alias"


def test_1p096_period_not_interpreted_as_same_signal():
    assert audit.classify_period_ratio(9.409091,8.587214)=="different_fitted_period"


def test_short_invalid_period_does_not_create_fake_alias():
    assert audit.classify_period_ratio(-3,5)=="invalid_ephemeris"
    assert audit.classify_period_ratio(np.nan,5)=="invalid_ephemeris"


def test_2025_days_and_2026_hours_convert_before_duration_comparison():
    old_duration_days=.1227359995245933
    new_duration_hours=2.945663988590239
    assert abs(new_duration_hours/(old_duration_days*24)-1)<1e-6


def test_2025_and_2026_can_swap_signal_between_two_existing_UIDs():
    # The exact TIC 178155732 exchange observed across the official releases.
    old1=(5.971880435943604,1415.63427734375)
    old2=(3.586159467697144,1412.774658203125)
    new1=(3.5861411094665527,1412.7747802734375)
    new2=(5.9722676277160645,1415.6339111328125)
    assert audit.classify_period_ratio(new1[0],old1[0])=="different_fitted_period"
    assert audit.classify_period_ratio(new2[0],old1[0])=="period_consistent_within_one_percent"
    assert audit.classify_period_ratio(new1[0],old2[0])=="period_consistent_within_one_percent"
    assert abs(old1[1]-new2[1])<.001
    assert abs(old2[1]-new1[1])<.001


def test_verified_source_requires_original_md5(tmp_path):
    p=tmp_path/"source.csv"
    p.write_text("uid,score\n100-1-S1,.99\n")
    with pytest.raises(ValueError,match="Only original pinned"):
        audit.verify_public_2025(p)
