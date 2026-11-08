"""Offline physical plot accounting; no NASA source or event accuracy is asserted."""
import numpy as np
import pytest

from kepler47_phase_fold_diagnostic import (
    phase_primary, secondary_phase,
    summarize_flux_at_archived_warnings,
)
from kepler47_eclipse_warning_check import (
    EPHEMERIDES,BKJD_REFERENCE_BJD
)


def test_primary_binary_phase_wraps_periodically():
    e=EPHEMERIDES["primary"]
    t=e["epoch_bjd"]-BKJD_REFERENCE_BJD
    period=e["period_days"]
    assert float(phase_primary(t)) == pytest.approx(0,abs=1e-12)
    assert float(phase_primary(t+period)) == pytest.approx(0,abs=1e-12)


def test_secondary_binary_phase_not_forced_to_half():
    phase=secondary_phase()
    assert .45<phase<.51
    assert abs(phase-.5)>.005


def test_phase_is_in_range_and_shape_preserved():
    t=np.arange(0,51,.33)
    phase=phase_primary(t)
    assert phase.shape == t.shape
    assert np.all((phase>=0)&(phase<1))


def test_archived_warning_times_must_be_original_fits_cadences():
    t=np.arange(0,100,.02043)
    sap=np.ones(len(t));pdc=np.ones(len(t))
    warning=t[40]
    rows=[{"warning_time_bkjd":float(warning),
           "seen_in_SAP":True,"seen_in_PDCSAP":True}]
    x=summarize_flux_at_archived_warnings(t,sap,pdc,rows)
    assert len(x)==1
    assert x[0]["normalized_sap_at_warning"]==1
    assert x[0]["normalized_pdcsap_at_warning"]==1


def test_nonexistent_warning_time_is_rejected():
    t=np.arange(0,100,.02043)
    with pytest.raises(ValueError):
        summarize_flux_at_archived_warnings(
            t,np.ones(len(t)),np.ones(len(t)),
            [{"warning_time_bkjd":16.001234}])
