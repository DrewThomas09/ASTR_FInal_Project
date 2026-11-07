"""Offline Kepler quality-bit annotation tests. No archive data required."""
import numpy as np
from real_spsd_case_study import marked_spsd_cadences,select_published_example


def test_bit_mask_and_combination_are_distinct():
    t=np.array([540.,547.,549.,551.])
    flags=np.array([0,1152,1024,128],dtype=np.int64)
    result=marked_spsd_cadences(t,flags)
    assert result["flag_1152_times"].tolist()==[547.]
    assert result["spsd_bit_times"].tolist()==[547.,549.]
    assert select_published_example(result)==547.


def test_no_quality_flag_returns_none_not_fabricated_time():
    result=marked_spsd_cadences(np.arange(8.),np.zeros(8,dtype=np.int64))
    assert select_published_example(result) is None


def test_reference_choice_is_closest_published_case():
    flags={"flag_1152_times":np.array([530.,548.,590.]),
           "spsd_bit_times":np.array([530.,548.,590.])}
    assert select_published_example(flags,547.)==548.
