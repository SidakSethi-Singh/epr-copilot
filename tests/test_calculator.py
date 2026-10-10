from rag.calculator import calculate_liability, get_target, get_annual_return_deadline, _safe_tonnage


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

    # In 2026-27: Cat 1 is 70%, Cat 2 is 50%, Cat 3 is 50%, Cat 4 is 100%
    # Obligations: 100*0.70 + 200*0.50 + 50*0.50 = 70 + 100 + 25 = 195 MT
    assert result["total_recycling_obligation_mt"] == 195.0

    # In 2026-27 recycled content: Cat 1 is 40% (40 MT), Cat 2 is 20% (40 MT), Cat 3 is 10% (5 MT) = 85 MT
    assert result["total_recycled_content_required_mt"] == 85.0

    # EC exposure: 195 MT * 5000 INR = 975,000 INR
    assert result["potential_ec_penalty_exposure_inr"] == 975_000

    # Refund schedule percentages
    assert "85% refund" in result["ec_refund_schedule"]["year_1_fulfillment"]
    assert "60% refund" in result["ec_refund_schedule"]["year_2_fulfillment"]
    assert "30% refund" in result["ec_refund_schedule"]["year_3_fulfillment"]


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

    res_invalid = get_target("1999-00")
    assert res_invalid["found"] is False


def test_get_annual_return_deadline():
    deadline = get_annual_return_deadline()
    assert "June 30" in deadline["statutory_date"]
