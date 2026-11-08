"""Controls for exact historical TESS source and host-frozen scalar model."""
import hashlib
import numpy as np
import pandas as pd
import pytest

from tess_scalar_ai_assisted_replication import (
    make_design_matrix,labels_and_folds,metrics_at_frozen_threshold,
    host_bootstrap_delta_ap,verify_pinned_source
)


def fake_tce(n=20):
    ids=np.arange(n)
    return pd.DataFrame({
        "uid":[f"i-{i}" for i in ids],
        "target_id":ids+1000,
        "label":np.where(ids%2==0,"KP","EB"),
        "fold":ids%10,
        "score":np.where(ids%2==0,.8,.1),
        "tce_period":np.full(n,4.5),
        "tce_duration":np.full(n,.12),
        "tce_prad":np.full(n,2.),
        "tce_max_mult_ev":np.full(n,12.),
        "ruwe":np.where(ids%3==0,np.nan,1.3)
    })


def freeze_for_fake():
    return {
        "expected_TCE_row_count":20,"expected_unique_TIC_hosts":20,
        "label_positive":["KP","CP"],
        "label_negative":["NTP","EB","NEB","FP","NPC","BD"]}


def test_tce_label_and_fold_integrity_starts_correct():
    df=fake_tce()
    y,fold=labels_and_folds(df,freeze_for_fake())
    assert int(y.sum())==10 and set(fold)==set(range(10))


def test_same_target_in_different_original_fold_is_rejected():
    df=fake_tce()
    df.loc[1,"target_id"]=df.loc[0,"target_id"]
    spec=freeze_for_fake()
    spec["expected_unique_TIC_hosts"]=19
    with pytest.raises(ValueError,match="Same star appears"):
        labels_and_folds(df,spec)


def test_another_user_id_does_not_become_a_second_independent_event():
    df=fake_tce()
    df.loc[3,"uid"]=df.loc[2,"uid"]
    with pytest.raises(ValueError,match="more than once"):
        labels_and_folds(df,freeze_for_fake())


def test_extra_derived_duty_cycle_and_ruwe_are_distinct_from_baseline():
    df=fake_tce()
    basic=make_design_matrix(df,False)
    extra=make_design_matrix(df,True)
    assert basic.shape==(20,4) and extra.shape==(20,6)
    assert np.allclose(basic,extra[:,:4])
    assert np.isclose(extra[0,4],np.log1p(.12/4.5))
    assert np.isnan(extra[0,5])


def test_source_checksum_and_bytes_must_match(tmp_path):
    f=tmp_path/"one.csv"
    f.write_bytes(b"some fake NASA numbers")
    with pytest.raises(ValueError,match="differs from frozen"):
        verify_pinned_source(f,{"original_md5":hashlib.md5(f.read_bytes()).hexdigest()})


def test_score_metrics_derive_exact_confusion():
    y=np.array([1,1,0,0])
    s=np.array([.9,.2,.7,.1])
    m=metrics_at_frozen_threshold(y,s)
    assert m["tp"]==1 and m["tn"]==1
    assert m["fp"]==1 and m["fn"]==1
    assert m["precision_at_0_5"]==.5


def test_host_bootstrap_uses_entire_groups_and_keeps_zero_change_at_zero():
    stars=np.repeat(np.arange(20),3)
    labels=np.repeat(np.arange(20)%2,3)
    scores=np.where(labels==1,.75,.18)
    outcome=host_bootstrap_delta_ap(stars,labels,scores,scores,n_rep=30,seed=12)
    assert outcome["host_star_cluster_count"]==20
    assert outcome["valid_bootstraps"]==30
    assert outcome["delta_AP_95pct_star_cluster_CI"]==[0.,0.]


def test_negative_physical_features_rejected():
    df=fake_tce()
    df.loc[0,"tce_period"]=-1
    with pytest.raises(ValueError,match="finite and positive"):
        make_design_matrix(df,False)
