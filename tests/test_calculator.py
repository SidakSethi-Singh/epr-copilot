import pytest
import math
from rag.calculator import (
    calculate_liability,
    get_target,
    get_annual_return_deadline,
    _safe_tonnage,
    compute_q_tonnage,
)

def test_safe_tonnage_valid():
    assert _safe_tonnage(100.5) == 100.5
    assert _safe_tonnage("50") == 50.0
    assert _safe_tonnage(0) == 0.0

def test_safe_tonnage_invalid_and_edge_cases():
    assert _safe_tonnage(-10) == 0.0
    assert _safe_tonnage("nan") == 0.0
    assert _safe_tonnage("inf") == 0.0
    assert _safe_tonnage("-inf") == 0.0
    assert _safe_tonnage(float("nan")) == 0.0
    assert _safe_tonnage(float("inf")) == 0.0
    assert _safe_tonnage(float("-inf")) == 0.0
    assert _safe_tonnage(None) == 0.0
    assert _safe_tonnage("invalid_string") == 0.0
    assert _safe_tonnage([100]) == 0.0
    assert _safe_tonnage({"mt": 100}) == 0.0
    assert _safe_tonnage(True) == 0.0
    assert _safe_tonnage(False) == 0.0
    assert _safe_tonnage(1_000_001) == 0.0

def test_golden_vector_1_cat_i_2026_27():
    result = calculate_liability(
        fiscal_year="2026-27",
        tonnages={"cat_1": 100.0},
    )
    cat_1_data = result["categories"]["cat_1"]
    assert cat_1_data["recycling_obligation_mt"] == 70.0
    assert cat_1_data["recycling_target_pct"] == 70

def test_golden_vector_2_cat_ii_2027_28():
    result = calculate_liability(
        fiscal_year="2027-28",
        tonnages={"cat_2": 100.0},
    )
    cat_2_data = result["categories"]["cat_2"]
    assert cat_2_data["recycling_obligation_mt"] == 60.0
    assert cat_2_data["recycling_target_pct"] == 60

def test_golden_vector_3_cat_iv_2026_27():
    result = calculate_liability(
        fiscal_year="2026-27",
        tonnages={"cat_4": 100.0},
    )
    cat_4_data = result["categories"]["cat_4"]
    assert cat_4_data["recycling_obligation_mt"] == 70.0
    assert cat_4_data["recycling_target_pct"] == 70

def test_golden_vector_4_cat_iii_recycled_content():
    result = calculate_liability(
        fiscal_year="2026-27",
        tonnages={"cat_3": 500.0},
        plastic_layer_weights={"cat_3": 100.0},
    )
    cat_3_data = result["categories"]["cat_3"]
    assert cat_3_data["recycled_content_required_mt"] == 5.0
    assert cat_3_data["recycled_content_mandate_pct"] == 5

def test_golden_vector_5_ec_shortfall_2nd_consecutive_year():
    result = calculate_liability(
        consecutive_year_of_shortfall=2,
        shortfalls={"cat_1": 10.0, "cat_2": 0.0, "cat_3": 0.0, "cat_4": 0.0},
    )
    assert result["applicable_ec_rate_inr_per_mt"] == 10000
    assert result["potential_ec_penalty_exposure_inr"] == 100000

def test_golden_vector_6_ec_shortfall_1st_year():
    result = calculate_liability(
        consecutive_year_of_shortfall=1,
        shortfalls={"cat_1": 10.0, "cat_2": 0.0, "cat_3": 0.0, "cat_4": 0.0},
    )
    assert result["applicable_ec_rate_inr_per_mt"] == 5000
    assert result["potential_ec_penalty_exposure_inr"] == 50000

def test_golden_vector_7_refund_schedule():
    result = calculate_liability()
    percentages = result["ec_refund_schedule"]["refund_percentages"]
    assert percentages[:3] == [75, 60, 40]

def test_golden_vector_8_two_year_average_q():
    result = calculate_liability(
        fiscal_year="2026-27",
        prior_year_tonnages={"cat_1": [80.0, 120.0]},
    )
    cat_1_data = result["categories"]["cat_1"]
    assert cat_1_data["q_tonnage_mt"] == 100.0
    assert cat_1_data["recycling_obligation_mt"] == 70.0
    assert result["_meta"]["basis"] == "two_year_average"

def test_additional_vector_cat_i_2024_25():
    result = calculate_liability(
        fiscal_year="2024-25",
        tonnages={"cat_1": 100.0},
    )
    cat_1_data = result["categories"]["cat_1"]
    assert cat_1_data["recycling_obligation_mt"] == 50.0

def test_additional_vector_ec_year_3_plus():
    result = calculate_liability(
        consecutive_year_of_shortfall=3,
        shortfalls={"cat_1": 10.0, "cat_2": 0.0, "cat_3": 0.0, "cat_4": 0.0},
    )
    assert result["applicable_ec_rate_inr_per_mt"] == 20000
    assert result["potential_ec_penalty_exposure_inr"] == 200000

def test_end_of_life_remainder_calculation():
    result = calculate_liability(
        fiscal_year="2026-27",
        tonnages={"cat_1": 100.0, "cat_2": 100.0},
    )
    cat_1 = result["categories"]["cat_1"]
    cat_2 = result["categories"]["cat_2"]
    assert cat_1["remaining_to_end_of_life_routes_mt"] == 30.0
    assert cat_2["remaining_to_end_of_life_routes_mt"] == 50.0
    assert result["remaining_to_end_of_life_routes_mt"] == 80.0

def test_certificate_price_override():
    result = calculate_liability(
        fiscal_year="2026-27",
        tonnages={"cat_1": 100.0},
        cert_price_override_inr_per_mt={"cat_1": 5000.0},
    )
    cat_1 = result["categories"]["cat_1"]
    assert cat_1["estimated_cert_cost_range_inr"] == [350000, 350000]

def test_unsupported_fiscal_year_defaulting():
    result = calculate_liability(
        fiscal_year="2019-20",
        tonnages={"cat_1": 100.0},
    )
    assert result["fiscal_year"] == "2026-27"
    assert result["_meta"]["fy_defaulted"] is True

def test_get_target():
    res = get_target("2025-26")
    assert res["found"] is True
    assert res["recycling_targets_pct"]["cat_1"] == 60
    assert res["recycled_content_pct"]["cat_1"] == 30

    res_invalid = get_target("1999-00")
    assert res_invalid["found"] is False

def test_get_annual_return_deadline():
    deadline = get_annual_return_deadline()
    assert deadline["statutory_date"] == "06-30"
    assert len(deadline["deadlines"]) >= 2

def test_calculate_liability_malformed_inputs():
    result = calculate_liability(
        fiscal_year="invalid-year",
        tonnages={
            "cat_1": "nan",
            "cat_2": "-inf",
            "cat_3": 10_000_000,
            "cat_4": "invalid_string",
        },
        plastic_layer_weights={"cat_3": -50.0},
        shortfalls={"cat_1": "nan"},
    )
    assert result["fiscal_year"] == "2026-27"
    assert result["_meta"]["fy_defaulted"] is True
    assert result["total_introduced_packaging_mt"] == 0.0
    assert result["total_recycling_obligation_mt"] == 0.0
    assert result["potential_ec_penalty_exposure_inr"] == 0

