"""Synthetic AstroImageJ source-reader tests, NOT ground eclipse results."""
import json
import pytest
from exofop_two_NEB_original_ground_AIJ_numeric_sources import (
    EXPECTED,select_original_file,validate_source_csv_table
)


def aij_table(aperture="T6",rows=30):
    s=f"Label\tBJD_TDB\trel_flux_T1\trel_flux_{aperture}\n"
    s+="".join(f"f{i}\t{2459000+i/10000:.6f}\t{.9+i/50000:.7f}\t{.8+i/50000:.7f}\n" for i in range(rows))
    return s.encode()


def test_true_reported_aperture_not_neighbor_catalog_TIC_as_flux_column():
    a=validate_source_csv_table(aij_table("T6"),"T6")
    assert a["original_AIJ_BJD_TDB_and_neighbor_finite_positive_rows"]==30
    assert a["original_AIJ_first_BJD_TDB"]>=2459000
    assert a["original_table_numeric_flux_has_NOT_YET_been_used_for_eclipse_measurement"]
    with pytest.raises(ValueError,match="missing actual BJD"):
        validate_source_csv_table(aij_table("T6"),"T11")


def test_missing_valid_numeric_aperture_cannot_be_substituted():
    with pytest.raises(ValueError,match="No sufficient genuine"):
        validate_source_csv_table(aij_table(rows=5),"T6")


def test_html_source_and_unverified_external_file_id_are_invalid():
    with pytest.raises(ValueError,match="absent or non-text"):
        validate_source_csv_table(b"<html>no data</html>","T6")
    inventory={"all_hosts_with_full_file_and_tseries_evidence":[{"TIC_ID":382437043,
        "original_user_file_evidence_queue":[{
           "original_exofop_file_ID":906268,
           "original_file_name":"original_ground_measurements.tbl"
        }]}]}
    assert select_original_file(inventory,382437043,906268)["original_exofop_file_ID"]==906268
    with pytest.raises(ValueError,match="Missing original"):
        select_original_file(inventory,382437043,999999)


def test_two_original_observer_claims_are_not_equated_to_independent_verified_truth():
    assert set(EXPECTED)=={382437043,264303333}
    assert EXPECTED[382437043]["AIJ_aperture"]=="T6"
    assert EXPECTED[264303333]["AIJ_aperture"]=="T11"
