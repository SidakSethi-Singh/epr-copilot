"""
Compliance & Penalty Resolution Engine for Waste Management / EPR System.
Provides deterministic calculation of:
- Green Credits under MoEFCC Green Credit Rules, 2023 for surplus waste utilization.
- Tier-based Environmental Compensation (EC) Penalties and formal CPCB Suspension Notices
  under Section 15 of Environment (Protection) Act, 1986 and Schedule II PWM Rules.
- Structured Audit Summaries citing specific government clauses.
"""

from typing import Dict, Any, Optional
from datetime import datetime


# Standard statutory benchmarks for FY 2026-27 under Schedule II (PWM Rules 2016 amended)
DEFAULT_MANDATED_UTILIZATION_PCT = 70.0  # 70% recycling / utilization target for FY 2026-27
GREEN_CREDIT_INCENTIVE_PER_MT = 2500.0   # Market trading floor for Green Credit units (INR)
BASE_EC_RATE_PER_MT = 5000.0             # Base statutory Environmental Compensation per MT


def evaluate_manifest_compliance(
    company_id: str,
    company_name: str,
    manifest_tonnage_introduced_mt: float,
    waste_utilized_mt: float,
    mandated_threshold_pct: float = DEFAULT_MANDATED_UTILIZATION_PCT,
    fiscal_year: str = "2026-27",
    consecutive_default_year: int = 1
) -> Dict[str, Any]:
    """
    Evaluates manifest / ERP waste utilization data against statutory CPCB guidelines.
    Returns structured audit result, green credits or tiered penalties, and suspension notices.
    """
    total_introduced = max(0.01, float(manifest_tonnage_introduced_mt or 0.01))
    utilized = max(0.0, float(waste_utilized_mt or 0.0))
    mandated_pct = max(1.0, min(100.0, float(mandated_threshold_pct or DEFAULT_MANDATED_UTILIZATION_PCT)))
    default_year = max(1, min(3, int(consecutive_default_year or 1)))

    mandated_mt = round((mandated_pct / 100.0) * total_introduced, 2)
    actual_utilization_pct = round((utilized / total_introduced) * 100.0, 1)
    shortfall_mt = round(max(0.0, mandated_mt - utilized), 2)
    surplus_mt = round(max(0.0, utilized - mandated_mt), 2)

    # 1. Determine Compliance Status
    if actual_utilization_pct >= mandated_pct:
        compliance_status = "COMPLIANT"
    elif actual_utilization_pct >= (mandated_pct * 0.75):
        compliance_status = "WARNING"
    else:
        compliance_status = "PENALIZED"

    # 2. Green Credits Calculation
    green_credits_earned = 0.0
    green_credit_monetary_value_inr = 0.0
    if compliance_status == "COMPLIANT" and surplus_mt > 0:
        green_credits_earned = round(surplus_mt, 2)  # 1 Credit per MT surplus
        green_credit_monetary_value_inr = round(green_credits_earned * GREEN_CREDIT_INCENTIVE_PER_MT, 2)

    # 3. Tiered Penalty Calculation & Suspension Notice
    penalty_rate_per_mt = 0.0
    penalty_tier = "NONE"
    total_penalty_inr = 0.0
    suspension_notice = None

    if shortfall_mt > 0:
        deficit_pct_of_target = (shortfall_mt / mandated_mt) * 100.0

        # Tier 1: Minor shortfall (< 15% deficit)
        if deficit_pct_of_target < 15.0 and default_year == 1:
            penalty_tier = "TIER_1_STANDARD"
            penalty_rate_per_mt = BASE_EC_RATE_PER_MT  # ₹5,000/MT
            total_penalty_inr = round(shortfall_mt * penalty_rate_per_mt, 2)
        # Tier 2: Moderate shortfall (15% to 40% deficit or Year 2 consecutive)
        elif (deficit_pct_of_target <= 40.0 and default_year <= 2) or default_year == 2:
            penalty_tier = "TIER_2_ESCALATED"
            penalty_rate_per_mt = BASE_EC_RATE_PER_MT * 2.0  # ₹10,000/MT
            total_penalty_inr = round(shortfall_mt * penalty_rate_per_mt, 2)
        # Tier 3: Severe shortfall (> 40% deficit or Year 3 consecutive)
        else:
            penalty_tier = "TIER_3_SEVERE_SUSPENSION"
            penalty_rate_per_mt = BASE_EC_RATE_PER_MT * 4.0  # ₹20,000/MT
            base_fine = shortfall_mt * penalty_rate_per_mt
            commission_surcharge = base_fine * 0.25  # 25% administrative surcharge fine
            total_penalty_inr = round(base_fine + commission_surcharge, 2)

        # Generate formal CPCB suspension payload if PENALIZED
        if compliance_status == "PENALIZED":
            suspension_notice = {
                "notice_id": f"CPCB/PWM/SUSP/{fiscal_year}/{company_id.replace(' ', '_')}",
                "issued_date": datetime.now().strftime("%Y-%m-%d"),
                "statutory_authority": "Central Pollution Control Board (CPCB) Enforcement Directorate",
                "governing_statutes": [
                    "Section 15, Environment (Protection) Act, 1986",
                    "Rule 13 & Schedule II (Paragraph 13), Plastic Waste Management Rules, 2016 (Amended)",
                    "CPCB Guidelines for Environmental Compensation Levy (G.S.R. 133(E))"
                ],
                "action_levied": "IMMEDIATE PORTAL TRADING SUSPENSION & SHOW-CAUSE NOTICE",
                "total_fine_inr": total_penalty_inr,
                "fine_breakdown": {
                    "shortfall_mt": shortfall_mt,
                    "statutory_ec_rate_per_mt": penalty_rate_per_mt,
                    "tier": penalty_tier,
                    "surcharge_applied": "25% Administrative Surcharge Commission" if penalty_tier == "TIER_3_SEVERE_SUSPENSION" else "None"
                },
                "curative_remedy": (
                    "Deposit the assessed Environmental Compensation into the CPCB Escrow Account within 15 calendar days "
                    "or procure verified Plastic Waste Processor (PWP) End-of-Life recycling credits to cure the shortfall."
                )
            }

    # 4. Generate Plain-text Statutory Citation Summary
    if compliance_status == "COMPLIANT":
        guideline_citation = (
            f"Statutory Benchmark Achieved: Pursuant to Schedule II, Clause 6.1 of the Plastic Waste Management "
            f"Rules, 2016 (MoEFCC G.S.R. 133(E)), {company_name} [{company_id}] successfully attained {actual_utilization_pct}% "
            f"waste utilization against the mandated {mandated_pct}% target for FY {fiscal_year}. "
            f"Surplus utilization of {surplus_mt} MT qualifies for {green_credits_earned} Green Credits "
            f"under the Green Credit Rules, 2023 (Notification S.O. 4458(E))."
        )
    elif compliance_status == "WARNING":
        guideline_citation = (
            f"Compliance Shortfall Notice (Warning Status): Under Rule 11.3 and Schedule II of PWM Rules, 2016, "
            f"{company_name} [{company_id}] registered {actual_utilization_pct}% waste utilization against the required {mandated_pct}%. "
            f"A deficit of {shortfall_mt} MT triggers a {penalty_tier} Environmental Compensation exposure of "
            f"₹{total_penalty_inr:,.0f} (₹{penalty_rate_per_mt:,.0f}/MT). A 30-day statutory cure window is active before escalation."
        )
    else:
        guideline_citation = (
            f"Statutory Breach & Penalty Order: {company_name} [{company_id}] has committed a major compliance default "
            f"under Schedule II Paragraph 13, PWM Rules, 2016 and Section 15 of Environment (Protection) Act, 1986. "
            f"Actual utilization of {actual_utilization_pct}% falls critically below the statutory {mandated_pct}% mandate for FY {fiscal_year}. "
            f"Shortfall of {shortfall_mt} MT attracts {penalty_tier} penalty of ₹{total_penalty_inr:,.0f} and immediate trading suspension."
        )

    return {
        "company_id": company_id,
        "company_name": company_name,
        "compliance_status": compliance_status,
        "fiscal_year": fiscal_year,
        "metrics": {
            "total_introduced_packaging_mt": total_introduced,
            "waste_utilized_mt": utilized,
            "mandated_threshold_pct": mandated_pct,
            "mandated_threshold_mt": mandated_mt,
            "actual_utilization_pct": actual_utilization_pct,
            "shortfall_mt": shortfall_mt,
            "surplus_mt": surplus_mt
        },
        "financial_resolution": {
            "net_credits_earned": green_credits_earned,
            "green_credit_monetary_value_inr": green_credit_monetary_value_inr,
            "fine_levied_inr": total_penalty_inr,
            "penalty_tier": penalty_tier,
            "penalty_rate_per_mt_inr": penalty_rate_per_mt
        },
        "statutory_guideline_summary": guideline_citation,
        "suspension_notice_payload": suspension_notice,
        "timestamp": datetime.now().isoformat()
    }


SAMPLE_AUDIT_MANIFESTS = {
    "fmcg_compliant": {
        "company_id": "CPCB-MH-BO-2024-9102",
        "company_name": "Bharat Beverages & Snacks Ltd",
        "manifest_tonnage_introduced_mt": 1200.0,
        "waste_utilized_mt": 960.0,  # 80% utilization vs 70% mandate
        "mandated_threshold_pct": 70.0,
        "fiscal_year": "2026-27",
        "consecutive_default_year": 1
    },
    "retail_warning": {
        "company_id": "CPCB-DL-BO-2025-4421",
        "company_name": "Metro Retail Packaging Hub",
        "manifest_tonnage_introduced_mt": 500.0,
        "waste_utilized_mt": 300.0,  # 60% utilization vs 70% mandate (deficit < 25%)
        "mandated_threshold_pct": 70.0,
        "fiscal_year": "2026-27",
        "consecutive_default_year": 1
    },
    "msme_penalized": {
        "company_id": "CPCB-GJ-P-2023-1188",
        "company_name": "Gujarat Polymer Converters LLP",
        "manifest_tonnage_introduced_mt": 850.0,
        "waste_utilized_mt": 255.0,  # 30% utilization vs 70% mandate (deficit > 50%)
        "mandated_threshold_pct": 70.0,
        "fiscal_year": "2026-27",
        "consecutive_default_year": 2
    }
}


def get_sample_manifests() -> Dict[str, Any]:
    return SAMPLE_AUDIT_MANIFESTS
