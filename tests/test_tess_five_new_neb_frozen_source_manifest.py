"""Synthetic engineering tests for a pre-centroid source manifest."""
import pytest
from tess_five_new_neb_frozen_source_manifest import freeze

def inputs():
    stars=[]
    candidates=[]
    for i in range(5):
        tic=11111111+i;neighbor=21111111+i
        prods=[]
        for sector in (17,15):
            for kind in ("LC","TP"):
                prods.append(dict(TIC_ID=tic,sector=sector,product_group=kind,
                    productFilename=f"tess000-s{sector:04d}-{tic:016d}-0120-s_{kind.lower()}.fits",
                    MAST_original_dataURI=f"mast:TESS/product/test{tic}/{kind}"))
        stars.append({
            "TIC_ID":tic,"TOI":f"{100+i}.01",
            "genuine_2min_SPOC_LC_TP_sectors":[17,15],
            "matching_original_SPOC_products":prods,
            "original_exofop_period_days":3.0,
            "original_exofop_epoch_BTJD":2015.,
            "original_exofop_duration_days":.1,
            "deterministic_sha256_precentroid_order":f"a{i}"})
        candidates.append({
            "TIC_ID":tic,"TOI":f"{100+i}.01",
            "independent_nearby_catalog_matched_unique_other_TICs":[neighbor],
            "pointing_corrected_centroid_seen":False,
            "note_mentioned_other_TICs":[{
                "mentioned_TIC_ID":neighbor,
                "nearby_catalog_match":{
                    "original_catalog_neighbor_RA_deg":100.,
                    "original_catalog_neighbor_DEC_deg":-30.,
                    "original_catalog_separation_arcsec":6.,
                    "original_catalog_position_angle_deg":80.}
            }]})
    return {"source_leads_with_original_SPOC_2min_LC_and_TP":10,
            "source_available_only_NEED_manual_external_ground_based_evidence":stars},{"not_yet_truth_validated_single_named_neighbor_source_candidates":candidates}

def test_freezes_five_unique_original_hosts_and_earliest_sector_without_centroid():
    a,b=inputs()
    r=freeze(a,b)
    assert len(r)==5
    assert all(s["selected_first_original_SPOC_2min_sector"]==15 for s in r)
    assert all(s["moment_centroid_vectors_extracted"] is False for s in r)
    assert all(s["ground_based_eclipse_in_named_neighbor_independently_verified"] is False for s in r)

def test_prior_source_or_centroid_exposed_target_rejected():
    a,b=inputs()
    b["not_yet_truth_validated_single_named_neighbor_source_candidates"][0]["pointing_corrected_centroid_seen"]=True
    with pytest.raises(ValueError,match="Ambiguous external neighbor"):
        freeze(a,b)

def test_external_source_duplicate_neighbors_rejected():
    a,b=inputs()
    b["not_yet_truth_validated_single_named_neighbor_source_candidates"][0]["independent_nearby_catalog_matched_unique_other_TICs"]=[21111111,22222222]
    with pytest.raises(ValueError,match="Ambiguous external neighbor"):
        freeze(a,b)
