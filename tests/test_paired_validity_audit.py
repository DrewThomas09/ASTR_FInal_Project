"""Offline tests of matched-case statistics, not new Kepler performance."""
import numpy as np
import pandas as pd
import pytest
from paired_validity_audit import audit, METHODS, _compare


THRESHOLDS={m:{"score_threshold":5.0} for m in METHODS}


def cases():
    rows=[]
    # Two hosts, three known-planet injections each, one experimental gain.
    outcome=[(1,'a',1,1),(1,'b',0,1),(1,'c',0,0),
             (2,'d',1,1),(2,'e',0,0),(2,'f',0,0)]
    for star,case,base,step in outcome:
        for method in METHODS:
            recovered=step if method=='localized_step_mask' else base
            rows.append(dict(status='success',case=case,kic=star,
                             condition='synthetic_spsd_like_step',method=method,
                             depth_ppm=1000,recovered=bool(recovered),
                             period_correct=bool(recovered),
                             peak_score=8 if recovered else 1,
                             n_true_transit_cadences_masked=2 if case=='b' and method=='localized_step_mask' else 0,
                             method_removed_cadences=3 if method=='localized_step_mask' else 0))
    return pd.DataFrame(rows)


def nulls():
    rows=[]
    for star in (1,2):
        for j in range(3):
            for method in METHODS:
                flag= star==1 and j==1 and method=='standard_bls'
                rows.append(dict(status='success',kic=star,condition='synthetic_spsd_like_step',
                                 proxy_index=j,method=method,score=7. if flag else 2.))
    return pd.DataFrame(rows)


def test_matched_pairs_and_false_trigger_decomposition():
    r=audit(cases(),nulls(),THRESHOLDS,reps=1000)
    recovery=r['paired_planet_recovery'][0]
    assert (recovery['baseline_flagged_or_recovered'],recovery['localized_flagged_or_recovered'])==(2,3)
    assert (recovery['baseline_only'],recovery['localized_only'])==(0,1)
    assert recovery['exact_two_sided_p_conditional_discordance']==1.0
    assert recovery['localized_mask_costs']['n_true_transit_cadences_masked']==2
    assert recovery['localized_mask_costs']['cases_losing_one_or_more_true_transit_cadences']==1
    proxies=r['paired_proxy_null_flags'][0]
    assert (proxies['baseline_only'],proxies['localized_only'])==(1,0)
    assert len(recovery['per_host_difference'])==2


def test_exact_3_to_0_discordances_have_p_quarter():
    f=pd.DataFrame({'kic':[1]*4+[2]*4,'standard_bls':[True]*3+[False]*5,
                    'localized_step_mask':[False]*8})
    r=_compare(f,'standard_bls','localized_step_mask',4,1000)
    assert r['baseline_only']==3
    assert r['localized_only']==0
    assert r['exact_two_sided_p_conditional_discordance']==pytest.approx(.25)


def test_incomplete_method_pairing_is_rejected():
    a=cases();a=a.drop(a.index[0])
    with pytest.raises(ValueError,match='incomplete'):
        audit(a,nulls(),THRESHOLDS,reps=1000)


def test_repeated_method_case_is_rejected():
    a=cases();a=pd.concat([a,a.iloc[:1]],ignore_index=True)
    with pytest.raises(ValueError,match='duplicate'):
        audit(a,nulls(),THRESHOLDS,reps=1000)


def test_score_discrepancy_must_be_explained():
    a=cases();a.loc[a.index[0],'recovered']=False
    with pytest.raises(ValueError,match='disagree'):
        audit(a,nulls(),THRESHOLDS,reps=1000)


def test_no_silent_exclusion_of_failed_fit():
    a=cases();a.loc[a.index[0],'status']='fit_error'
    with pytest.raises(ValueError,match='non-success'):
        audit(a,nulls(),THRESHOLDS,reps=1000)


def test_invalid_threshold_is_rejected():
    bad={**THRESHOLDS,'localized_step_mask':{'score_threshold':np.nan}}
    with pytest.raises(ValueError,match='Invalid'):
        audit(cases(),nulls(),bad,reps=1000)


def test_bootstrap_seed_reproducibility():
    a=audit(cases(),nulls(),THRESHOLDS,seed=19,reps=1000)
    b=audit(cases(),nulls(),THRESHOLDS,seed=19,reps=1000)
    assert a==b

