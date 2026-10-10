import pytest
from rag.calculator import (
    calculate_liability,
    get_target,
    get_annual_return_deadline,
    get_rules_version,
    _safe_tonnage,
)

def test_safe_tonnage():
    assert _safe_tonnage(100.5) == 100.5
    assert _safe_tonnage("50") == 50.0
    assert _safe_tonnage(-10) == 0.0
    assert _safe_tonnage("nan") == 0.0
    assert _safe_tonnage("inf") == 0.0
    assert _safe_tonnage(float("nan")) == 0.0
    assert _safe_tonnage(float("inf")) == 0.0
    assert _safe_tonnage(None) == 0.0
    assert _safe_tonnage("invalid_string") == 0.0
    assert _safe_tonnage(10_000_000) == 0.0  # exceeds default max_mt


def test_calculate_liability_baseline():
    result = calculate_liability(
        pibo_type="Brand Owner",
        fiscal_year="2026-27",
        tonnages={"cat_1": 100.0, "cat_2": 200.0, "cat_3": 50.0, "cat_4": 0.0},
    )

    assert result["pibo_type"] == "Brand Owner"
    assert result["fiscal_year"] == "2026-27"
    assert result["total_introduced_packaging_mt"] == 350.0

    # In 2026-27: Cat 1 is 70%, Cat 2 is 50%, Cat 3 is 50%, Cat 4 is 70%
    # Obligations: 100*0.70 + 200*0.50 + 50*0.50 = 70 + 100 + 25 = 195 MT
    assert result["total_recycling_obligation_mt"] == 195.0

    # In 2026-27 recycled content (verified rules):
    # Cat 1 is 40% (40 MT), Cat 2 is 10% (20 MT), Cat 3 is 5% (2.5 MT) = 62.5 MT
    assert result["total_recycled_content_required_mt"] == 62.5

    # EC exposure: 195 MT * 5000 INR = 975,000 INR
    assert result["potential_ec_penalty_exposure_inr"] == 975_000

    # EC Escalation
    esc = result["ec_escalation_by_consecutive_year"]
    assert esc["year_1_total_inr"] == 975_000
    assert esc["year_2_total_inr"] == 195 * 10000
    assert esc["year_3_total_inr"] == 195 * 20000

    # Refund schedule percentages (75/60/40)
    assert "75% refund" in result["ec_refund_schedule"]["year_1_fulfillment"]
    assert "60% refund" in result["ec_refund_schedule"]["year_2_fulfillment"]
    assert "40% refund" in result["ec_refund_schedule"]["year_3_fulfillment"]

    # Waste-to-Energy recovery bridge
    assert "energy_recovery" in result
    energy = result["energy_recovery"]
    assert energy["non_recycled_energy_feedstock_mt"] == (200.0 - 100.0) + (50.0 - 25.0)  # 125 MT
    assert energy["cement_kiln_coprocessing_thermal_mwh"] > 0
    assert energy["waste_to_energy_electrical_mwh"] > 0


def test_golden_vectors_from_roadmap():
    """Validates the 5 statutory golden vectors specified in report.md §7 and proper_roadmap.md."""
    # 1. Cat II, EPR target 100 MT, FY 2027-28 -> min recycling = 60 MT
    r1 = calculate_liability(fiscal_year="2027-28", tonnages={"cat_2": 100.0})
    assert r1["categories"]["cat_2"]["recycling_obligation_mt"] == 60.0

    # 2. Cat I, EPR target 100 MT, FY 2026-27 -> min recycling = 70 MT
    r2 = calculate_liability(fiscal_year="2026-27", tonnages={"cat_1": 100.0})
    assert r2["categories"]["cat_1"]["recycling_obligation_mt"] == 70.0

    # 3. Cat IV, EPR target 100 MT, FY 2026-27 -> min recycling = 70 MT (was incorrectly 100% in MVP)
    r3 = calculate_liability(fiscal_year="2026-27", tonnages={"cat_4": 100.0})
    assert r3["categories"]["cat_4"]["recycling_obligation_mt"] == 70.0

    # 4. Cat III, 100 MT plastic-layer weight, FY 2026-27 -> recycled content = 5 MT (was 10 in MVP)
    r4 = calculate_liability(fiscal_year="2026-27", tonnages={"cat_3": 100.0})
    assert r4["categories"]["cat_3"]["recycled_content_required_mt"] == 5.0

    # 5. Shortfall 10 MT, 2nd consecutive year -> EC rate is 10,000 INR/MT = 100,000 INR
    r5 = calculate_liability(fiscal_year="2026-27", tonnages={"cat_1": 10.0 / 0.70})
    esc = r5["ec_escalation_by_consecutive_year"]
    assert esc["year_2_rate_inr_per_mt"] == 10000
    assert esc["year_3_rate_inr_per_mt"] == 20000


def test_calculate_liability_malformed_inputs():
    result = calculate_liability(
        pibo_type="Producer",
        fiscal_year="invalid-year",  # should default to 2026-27
        tonnages={"cat_1": "nan", "cat_2": -100, "cat_3": None},
    )
    assert result["fiscal_year"] == "2026-27"
    assert result["total_introduced_packaging_mt"] == 0.0
    assert result["total_recycling_obligation_mt"] == 0.0
    assert result["potential_ec_penalty_exposure_inr"] == 0


def test_get_target():
    res = get_target("2025-26")
    assert res["found"] is True
    assert res["recycling_targets_pct"]["cat_1"] == 60
    assert res["recycling_targets_pct"]["cat_4"] == 60  # verified Cat IV ramp
    assert "_meta" in res

    res_invalid = get_target("1999-00")
    assert res_invalid["found"] is False


def test_get_annual_return_deadline():
    deadline = get_annual_return_deadline()
    assert "June 30" in deadline["statutory_date"]
    assert "31 Oct" in deadline["current_extended_date"]
    assert "31 Dec" in deadline["current_extended_date"]
    assert "_meta" in deadline


def test_get_rules_version():
    meta = get_rules_version()
    assert "ruleset_version" in meta
    assert "verified_on" in meta
    assert meta["ruleset_version"] == "2026-10-10.1"
