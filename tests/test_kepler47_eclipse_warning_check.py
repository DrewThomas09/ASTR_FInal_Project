"""Post-hoc binary ephemeris check math: deterministic tests only."""
import pytest

from kepler47_eclipse_warning_check import (
    BKJD_REFERENCE_BJD, EPHEMERIDES, KEPLER47,
    nearest_published_eclipse, analyze_original_warnings, report,
    circular_phase_shift_sensitivity
)


def test_primary_epoch_exact():
    t=EPHEMERIDES["primary"]["epoch_bjd"] - BKJD_REFERENCE_BJD
    r=nearest_published_eclipse(t)
    assert r["eclipse_type"]=="primary"
    assert abs(r["residual_days"]) < 1e-9


def test_secondary_cycle_after_50_orbits():
    e=EPHEMERIDES["secondary"]
    t=e["epoch_bjd"]-BKJD_REFERENCE_BJD+50*e["period_days"]
    r=nearest_published_eclipse(t)
    assert r["eclipse_type"]=="secondary"
    assert abs(r["residual_days"])<1e-9


def test_original_warning_times_deduplicated_across_flux_products():
    times=[550.9336158230508,558.3920544248394,
           588.1846313945789,595.4385715831377,
           612.6026676026813,614.3803690897039,
           621.8180872265584]
    sap=[times[j] for j in [0,2,3,4,6]]
    pdc=times
    rows=[
        {"kic":str(KEPLER47),"product":product,
         "warning_time_bkjd":str(t)}
        for product,group in [("SAP",sap),("PDCSAP",pdc)]
        for t in group]
    analyzed=analyze_original_warnings(rows)
    summary=report(analyzed)
    assert summary["n_distinct_warning_epochs"]==7
    assert summary["n_sap_distinct_epochs"]==5
    assert summary["n_pdcsap_distinct_epochs"]==7
    assert summary["n_warnings_in_both_products"]==5
    assert summary["n_within_0p1_day_of_published_stellar_eclipse"]==5
    assert summary["n_within_0p3_day_of_published_stellar_eclipse"]==6


def test_other_targets_not_selected():
    rows=[{"kic":"3323887","product":"SAP","warning_time_bkjd":"567.89"}]
    assert analyze_original_warnings(rows)==[]


def test_unknown_flux_product_rejected():
    rows=[{"kic":str(KEPLER47),"product":"magic",
           "warning_time_bkjd":"550.93"}]
    with pytest.raises(ValueError):
        analyze_original_warnings(rows)


def test_ephemeris_uses_kepler_bkjd_not_raw_bjd():
    near=nearest_published_eclipse(550.9336158230508)
    assert near["eclipse_type"]=="secondary"
    assert abs(near["residual_days"]) < .1


def test_phase_shift_keeps_warning_structure_and_is_deterministic():
    from kepler47_eclipse_warning_check import analyze_original_warnings
    t=[550.9336158230508,558.3920544248394,588.1846313945789,
       595.4385715831377,612.6026676026813,614.3803690897039,
       621.8180872265584]
    rows=[{"kic":str(KEPLER47),"product":"PDCSAP",
           "warning_time_bkjd":str(x)} for x in t]
    table=analyze_original_warnings(rows)
    result=circular_phase_shift_sensitivity(table)
    assert result["n_warning_epochs"]==7
    assert result["phase_shift_grid_size"]==20000
    assert result["fractions_ge_observed"]["0.1_days"]["observed_close_warnings"]==5
    assert result["fractions_ge_observed"]["0.3_days"]["observed_close_warnings"]==6
    assert .01<result["fractions_ge_observed"]["0.1_days"]["fraction_of_joint_shifts_at_least_as_aligned"]<.04
    assert .05<result["fractions_ge_observed"]["0.3_days"]["fraction_of_joint_shifts_at_least_as_aligned"]<.12


def test_phase_sensitivity_refuses_changed_exploratory_grid():
    with pytest.raises(ValueError):
        circular_phase_shift_sensitivity([],n_offsets=200)
