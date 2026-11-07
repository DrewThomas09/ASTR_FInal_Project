"""Offline deterministic checks for event-vetting ablation (no telescope download)."""
import pandas as pd
from event_vetting_ablation import event_accepts, summarized


def test_good_repeated_events_pass_heuristic():
    d={"n_observable_events":5,"positive_depth_fraction":1.,
       "dominance":.24,"odd_even_depth_difference_ppm":50,
       "median_depth_ppm":1000}
    assert event_accepts(d)


def test_single_defect_is_rejected():
    d={"n_observable_events":5,"positive_depth_fraction":.7,
       "dominance":.88,"odd_even_depth_difference_ppm":None}
    assert not event_accepts(d)


def test_binary_alternating_depth_is_rejected():
    d={"n_observable_events":6,"positive_depth_fraction":1.,
       "dominance":.20,"odd_even_depth_difference_ppm":2500,
       "median_depth_ppm":2800}
    assert not event_accepts(d)


def test_genuine_low_n_event_can_be_rejected_a_scientific_limitation():
    d={"n_observable_events":2,"positive_depth_fraction":1.,
       "dominance":.5,"odd_even_depth_difference_ppm":None}
    assert not event_accepts(d)


def test_ablation_cannot_increase_flags():
    df=pd.DataFrame({
      "group":["planet_500ppm","planet_500ppm","single_dip","single_dip"],
      "baseline_flag":[True,True,True,False],
      "enhanced_flag":[False,True,False,False],
      "correct_period":[True,False,False,False]})
    report=summarized(df)
    for group,segment in report.groupby("group"):
        base=segment.loc[segment.method=="baseline","flagged"].iloc[0]
        improved=segment.loc[segment.method=="enhanced","flagged"].iloc[0]
        assert improved<=base
    baseline=report.loc[(report.group=="planet_500ppm") &
                        (report.method=="baseline"),"correct_period_and_flagged"].iloc[0]
    assert baseline==1
