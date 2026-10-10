"""
Government ESG Benchmark Leaderboard & Subsidy vs Fine Allocation Engine.
Implements statutory classification:
- Green Category (Score >= 85): Eligible for MoEFCC Green Credit Subsidy & Priority Clearances
- Amber Category (Score 60-84): Conditional compliance with statutory cure period
- Red Category (Score < 60): Default status with 25% administrative surcharge fine & Section 15 EPA action
"""

from typing import List, Dict, Any
from rag.company_data import get_all_company_benchmarks


def compute_leaderboard() -> Dict[str, Any]:
    companies = get_all_company_benchmarks()

    # Sort descending by ESG score
    sorted_companies = sorted(companies, key=lambda x: x["esg_score"], reverse=True)

    green_count = sum(1 for c in sorted_companies if c["esg_score"] >= 85)
    amber_count = sum(1 for c in sorted_companies if 60 <= c["esg_score"] < 85)
    red_count = sum(1 for c in sorted_companies if c["esg_score"] < 60)

    total_waste_tracked_mt = sum(c["annual_plastic_mt"] for c in sorted_companies)
    total_penalty_exposure_inr = sum(c["penalty_risk_inr"] for c in sorted_companies)

    return {
        "total_enterprises_tracked": len(sorted_companies),
        "total_waste_tracked_mt": total_waste_tracked_mt,
        "total_statutory_penalties_exposed_inr": total_penalty_exposure_inr,
        "summary": {
            "green_compliant_count": green_count,
            "amber_monitored_count": amber_count,
            "red_defaulter_count": red_count
        },
        "subsidy_policy": {
            "green_incentive": "5% Green Credit Subsidy on next registered eco-product line + 3-year expedited SPCB Consent to Operate (CTO)",
            "amber_warning": "60-day statutory cure window to procure missing recycler credits",
            "red_penalty": "25% statutory surcharge fine added to default ₹5,000/MT Environmental Compensation + factory power/water disconnection notice"
        },
        "rankings": sorted_companies
    }
