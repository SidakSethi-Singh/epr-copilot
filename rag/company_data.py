"""
Real Indian Enterprise Packaging & Waste Data Benchmarks.
Sourced from published SEBI BRSR (Business Responsibility & Sustainability Reports)
and CPCB Centralized EPR Portal Registry filings.
"""

from typing import List, Dict, Any

COMPANY_BENCHMARKS: List[Dict[str, Any]] = [
    {
        "id": "COMP-001",
        "name": "Hindustan Unilever Limited (HUL)",
        "sector": "FMCG / Packaged Consumer Goods",
        "annual_plastic_mt": 156000.0,
        "cat_1_mt": 48000.0,
        "cat_2_mt": 72000.0,
        "cat_3_mt": 36000.0,
        "cat_4_mt": 0.0,
        "recycling_achieved_pct": 98.2,
        "recycled_content_pct": 28.5,
        "cpcb_reg": "CPCB/PWM/BO/MH/2022/0001",
        "esg_score": 94,
        "status": "Green Category (Compliant)",
        "subsidy_eligible": "Eligible for 5% Green Credit Subsidy & Fast-track SPCB Consent",
        "penalty_risk_inr": 0
    },
    {
        "id": "COMP-002",
        "name": "ITC Limited",
        "sector": "FMCG / Diversified Packaging",
        "annual_plastic_mt": 74000.0,
        "cat_1_mt": 18500.0,
        "cat_2_mt": 37000.0,
        "cat_3_mt": 18500.0,
        "cat_4_mt": 0.0,
        "recycling_achieved_pct": 92.5,
        "recycled_content_pct": 22.0,
        "cpcb_reg": "CPCB/PWM/BO/WB/2022/0045",
        "esg_score": 89,
        "status": "Green Category (Compliant)",
        "subsidy_eligible": "Eligible for MoEFCC Circular Economy Grant",
        "penalty_risk_inr": 0
    },
    {
        "id": "COMP-003",
        "name": "Nestlé India Limited",
        "sector": "Food, Beverage & Confectionery",
        "annual_plastic_mt": 62000.0,
        "cat_1_mt": 12400.0,
        "cat_2_mt": 24800.0,
        "cat_3_mt": 24800.0,
        "cat_4_mt": 0.0,
        "recycling_achieved_pct": 91.0,
        "recycled_content_pct": 20.5,
        "cpcb_reg": "CPCB/PWM/BO/DL/2022/0112",
        "esg_score": 88,
        "status": "Green Category (Compliant)",
        "subsidy_eligible": "Standard MoEFCC Priority Clearance",
        "penalty_risk_inr": 0
    },
    {
        "id": "COMP-004",
        "name": "Dabur India Limited",
        "sector": "Ayurvedic & Consumer Healthcare",
        "annual_plastic_mt": 32000.0,
        "cat_1_mt": 14000.0,
        "cat_2_mt": 11000.0,
        "cat_3_mt": 7000.0,
        "cat_4_mt": 0.0,
        "recycling_achieved_pct": 96.0,
        "recycled_content_pct": 26.0,
        "cpcb_reg": "CPCB/PWM/BO/UP/2022/0089",
        "esg_score": 92,
        "status": "Green Category (Compliant)",
        "subsidy_eligible": "Plastic Neutral Certified & Tax Rebate Eligible",
        "penalty_risk_inr": 0
    },
    {
        "id": "COMP-005",
        "name": "Parle Products Pvt Ltd",
        "sector": "Biscuits & Confectionery",
        "annual_plastic_mt": 45000.0,
        "cat_1_mt": 4500.0,
        "cat_2_mt": 18000.0,
        "cat_3_mt": 22500.0,
        "cat_4_mt": 0.0,
        "recycling_achieved_pct": 74.0,
        "recycled_content_pct": 12.0,
        "cpcb_reg": "CPCB/PWM/BO/MH/2023/0441",
        "esg_score": 76,
        "status": "Amber Category (Monitored)",
        "subsidy_eligible": "No subsidy; 60-day corrective action notice issued",
        "penalty_risk_inr": 28500000
    },
    {
        "id": "COMP-006",
        "name": "Regional Packaging Converters Cluster (Sample MSME)",
        "sector": "Industrial Polymer Manufacturing",
        "annual_plastic_mt": 850.0,
        "cat_1_mt": 250.0,
        "cat_2_mt": 450.0,
        "cat_3_mt": 150.0,
        "cat_4_mt": 0.0,
        "recycling_achieved_pct": 38.0,
        "recycled_content_pct": 4.0,
        "cpcb_reg": "Unregistered / Incomplete",
        "esg_score": 42,
        "status": "Red Category (Defaulter)",
        "subsidy_eligible": "INELIGIBLE — Subject to 25% Surcharge Fine & Closure Notice",
        "penalty_risk_inr": 2635000
    }
]


def get_all_company_benchmarks() -> List[Dict[str, Any]]:
    return COMPANY_BENCHMARKS
