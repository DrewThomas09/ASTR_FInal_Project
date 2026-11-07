"""Tests of independent cohort bookkeeping, not actual astrophysical accuracy."""
import pandas as pd
from real_external_cohort import period_status,wilson_interval,summarize


def test_period_aliases_are_not_called_exact_period_recovery():
    assert period_status(5.,10.)[0]=="half_period_alias"
    assert period_status(20.,10.)[0]=="double_period_alias"
    assert period_status(10.01,10.)[0]=="exact"
    assert period_status(13.,10.)[0]=="unmatched"


def test_no_data_is_not_assumed_to_pass():
    data=pd.DataFrame([
      {"class":"planet","status":"analyzed","period_relation":"exact",
       "binary_review_warning":False},
      {"class":"planet","status":"error","period_relation":None,
       "binary_review_warning":None},
      {"class":"binary","status":"analyzed","period_relation":"exact",
       "binary_review_warning":True},
      {"class":"binary","status":"analyzed","period_relation":"half_period_alias",
       "binary_review_warning":False}
    ])
    s=summarize(data,4)
    assert s["n_planned"]==4 and s["n_errors"]==1
    assert s["by_class"]["planet"]["n_planned"]==2
    assert s["by_class"]["planet"]["n_exact_period"]==1
    assert s["by_class"]["binary"]["n_half_or_double_alias"]==1
    assert s["by_class"]["binary"]["n_warned_among_exact_period_cases"]==1


def test_wilson_interval_edge_cases():
    assert wilson_interval(0,0) is None
    lo,hi=wilson_interval(0,5)
    assert lo>=0 and hi<1
    lo,hi=wilson_interval(5,5)
    assert lo>0 and hi<=1
