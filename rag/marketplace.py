"""
EPR Credit Trading & Recycler (PWP) Marketplace Optimizer for EPR Copilot.
Connects PIBO statutory obligations to CPCB-registered Plastic Waste Processors (PWPs),
simulates real-time certificate spot pricing, and calculates net financial savings
versus default Environmental Compensation (EC) penalties.
"""

from typing import Dict, List, Any

# CPCB Registered Recycler Database (Sample Verified PWPs across Industrial Hubs)
VERIFIED_PWPS = [
    {
        "id": "PWP-GJ-01",
        "name": "Shree Ram Green Poly-Recyclers LLP",
        "location": "Surat, Gujarat",
        "cpcb_reg": "CPCB/PWP/GJ/2023/00142",
        "authorized_categories": ["cat_1", "cat_2"],
        "annual_capacity_mt": 18000,
        "available_credits_mt": 4200,
        "spot_rate_per_mt": {"cat_1": 3200, "cat_2": 2400},
        "rating": 4.9
    },
    {
        "id": "PWP-MH-04",
        "name": "Sahyadri Circular Polymers Pvt Ltd",
        "location": "Bhiwandi, Maharashtra",
        "cpcb_reg": "CPCB/PWP/MH/2024/00889",
        "authorized_categories": ["cat_1", "cat_2", "cat_3"],
        "annual_capacity_mt": 25000,
        "available_credits_mt": 8500,
        "spot_rate_per_mt": {"cat_1": 3400, "cat_2": 2600, "cat_3": 4800},
        "rating": 4.8
    },
    {
        "id": "PWP-TN-02",
        "name": "Coimbatore CleanTech Waste Processors",
        "location": "Coimbatore, Tamil Nadu",
        "cpcb_reg": "CPCB/PWP/TN/2023/00311",
        "authorized_categories": ["cat_2", "cat_3", "cat_4"],
        "annual_capacity_mt": 14000,
        "available_credits_mt": 3100,
        "spot_rate_per_mt": {"cat_2": 2300, "cat_3": 4500, "cat_4": 6200},
        "rating": 4.7
    },
    {
        "id": "PWP-UP-07",
        "name": "NCR Eco-Refining & Co-processing Industries",
        "location": "Greater Noida, Uttar Pradesh",
        "cpcb_reg": "CPCB/PWP/UP/2022/00642",
        "authorized_categories": ["cat_1", "cat_3"],
        "annual_capacity_mt": 30000,
        "available_credits_mt": 11000,
        "spot_rate_per_mt": {"cat_1": 3100, "cat_3": 4600},
        "rating": 4.9
    }
]

# Benchmark market spot prices per MT (CPCB Portal Exchange Estimates)
MARKET_SPOT_PRICES = {
    "cat_1": {"min": 2800, "avg": 3300, "max": 4200, "unit": "INR / MT"},
    "cat_2": {"min": 2000, "avg": 2500, "max": 3200, "unit": "INR / MT"},
    "cat_3": {"min": 4200, "avg": 4800, "max": 5800, "unit": "INR / MT"},
    "cat_4": {"min": 5500, "avg": 6500, "max": 8000, "unit": "INR / MT"},
}


def get_marketplace_data() -> Dict[str, Any]:
    """Returns real-time PWP quotes, benchmark prices, and active market status."""
    return {
        "status": "active",
        "exchange_platform": "CPCB Centralized EPR Portal Certificate Trading Window",
        "benchmark_spot_prices": MARKET_SPOT_PRICES,
        "verified_pwps": VERIFIED_PWPS,
        "total_available_credits_mt": sum(p["available_credits_mt"] for p in VERIFIED_PWPS)
    }


def optimize_procurement(obligations: Dict[str, float]) -> Dict[str, Any]:
    """
    Computes optimal certificate purchase strategy and compares against
    default Environmental Compensation (EC) penalty (Rs 5,000 / MT).
    """
    ec_penalty_rate_per_mt = 5000.0
    total_obligation_mt = sum(obligations.values())
    total_ec_penalty_inr = round(total_obligation_mt * ec_penalty_rate_per_mt, 2)

    category_costs = {}
    total_market_cost_inr = 0.0

    for cat_key, qty in obligations.items():
        if qty <= 0:
            continue
        spot = MARKET_SPOT_PRICES.get(cat_key, {"avg": 3500})
        cost = round(qty * spot["avg"], 2)
        total_market_cost_inr += cost
        category_costs[cat_key] = {
            "obligation_mt": qty,
            "avg_spot_rate_inr": spot["avg"],
            "total_procurement_cost_inr": cost,
            "ec_penalty_alternative_inr": round(qty * ec_penalty_rate_per_mt, 2)
        }

    net_savings_inr = round(max(0.0, total_ec_penalty_inr - total_market_cost_inr), 2)
    roi_pct = round((net_savings_inr / (total_market_cost_inr or 1.0)) * 100, 1) if total_market_cost_inr > 0 else 0.0

    return {
        "total_obligation_mt": total_obligation_mt,
        "total_market_procurement_cost_inr": total_market_cost_inr,
        "total_ec_penalty_inr": total_ec_penalty_inr,
        "net_savings_inr": net_savings_inr,
        "savings_roi_pct": roi_pct,
        "category_breakdown": category_costs,
        "procurement_verdict": f"Procuring verified PWP certificates saves Rs {net_savings_inr:,.0f} compared to paying statutory EC penalties."
    }
