from rag.audit_engine import evaluate_manifest_compliance, get_sample_manifests


def test_audit_engine_compliant_green_credits():
    # 1200 MT introduced, 960 MT utilized (80% vs 70% mandate)
    res = evaluate_manifest_compliance(
        company_id="CPCB-TEST-01",
        company_name="Green Packaging Corp",
        manifest_tonnage_introduced_mt=1200.0,
        waste_utilized_mt=960.0,
        mandated_threshold_pct=70.0,
        fiscal_year="2026-27"
    )

    assert res["compliance_status"] == "COMPLIANT"
    assert res["metrics"]["actual_utilization_pct"] == 80.0
    # 840 MT mandated -> 120 MT surplus -> 120 Green Credits
    assert res["financial_resolution"]["net_credits_earned"] == 120.0
    assert res["financial_resolution"]["fine_levied_inr"] == 0.0
    assert res["suspension_notice_payload"] is None
    assert "Green Credit Rules, 2023" in res["statutory_guideline_summary"]


def test_audit_engine_warning_status():
    # 500 MT introduced, 300 MT utilized (60% vs 70% mandate)
    res = evaluate_manifest_compliance(
        company_id="CPCB-TEST-02",
        company_name="Moderate Packagers",
        manifest_tonnage_introduced_mt=500.0,
        waste_utilized_mt=300.0,
        mandated_threshold_pct=70.0,
        fiscal_year="2026-27"
    )

    assert res["compliance_status"] == "WARNING"
    assert res["metrics"]["shortfall_mt"] == 50.0
    assert res["financial_resolution"]["net_credits_earned"] == 0.0
    assert res["financial_resolution"]["fine_levied_inr"] > 0
    assert res["suspension_notice_payload"] is None


def test_audit_engine_penalized_suspension_notice():
    # 850 MT introduced, 255 MT utilized (30% vs 70% mandate)
    res = evaluate_manifest_compliance(
        company_id="CPCB-TEST-03",
        company_name="Defaulting Converters",
        manifest_tonnage_introduced_mt=850.0,
        waste_utilized_mt=255.0,
        mandated_threshold_pct=70.0,
        fiscal_year="2026-27",
        consecutive_default_year=2
    )

    assert res["compliance_status"] == "PENALIZED"
    assert res["financial_resolution"]["fine_levied_inr"] > 0
    assert res["suspension_notice_payload"] is not None
    assert "IMMEDIATE PORTAL TRADING SUSPENSION" in res["suspension_notice_payload"]["action_levied"]
    assert "Section 15, Environment (Protection) Act, 1986" in res["suspension_notice_payload"]["governing_statutes"]
