import math
from typing import Any, Dict, List, Optional, Union
from rag.rules import (
    load_rules,
    get_ruleset_version,
    get_verified_on,
    get_recycling_min_pct,
    get_recycled_content_pct,
    get_ec_rate,
    get_refund_pct,
    get_deadlines,
    get_statutory_annual_return_date,
    get_cert_price_ranges,
)

SUPPORTED_FISCAL_YEARS = [
    "2024-25",
    "2025-26",
    "2026-27",
    "2027-28",
    "2028-29",
]

ROMAN_TO_LEGACY = {
    "I": "cat_1",
    "II": "cat_2",
    "III": "cat_3",
    "IV": "cat_4",
    "V": "cat_5",
}

CATEGORY_MAP = {
    "cat_1": "I",
    "cat_2": "II",
    "cat_3": "III",
    "cat_4": "IV",
    "cat_5": "V",
    "I": "I",
    "II": "II",
    "III": "III",
    "IV": "IV",
    "V": "V",
}

CATEGORY_NAMES = {
    "I": "Category I: Rigid Plastics",
    "II": "Category II: Flexible Plastics",
    "III": "Category III: Multilayered Plastics (MLP)",
    "IV": "Category IV: Compostable Plastics",
    "V": "Category V: Biodegradable Plastics",
}

def _safe_tonnage(val: Any, max_mt: float = 1_000_000.0) -> float:
    if val is None or isinstance(val, (bool, list, dict)):
        return 0.0
    try:
        numeric_val = float(val)
        if math.isnan(numeric_val) or math.isinf(numeric_val):
            return 0.0
        if numeric_val < 0.0 or numeric_val > max_mt:
            return 0.0
        return numeric_val
    except (ValueError, TypeError):
        return 0.0

def get_target(fiscal_year: str) -> Dict[str, Any]:
    rules = load_rules()
    if fiscal_year in rules.get("recycling_min_pct", {}):
        cat_map_targets = {}
        cat_map_content = {}
        for cat_num, cat_roman in [("cat_1", "I"), ("cat_2", "II"), ("cat_3", "III"), ("cat_4", "IV")]:
            target_pct = get_recycling_min_pct(fiscal_year, cat_roman)
            if target_pct is not None:
                cat_map_targets[cat_num] = target_pct
            content_pct = get_recycled_content_pct(fiscal_year, cat_roman)
            if content_pct is not None:
                cat_map_content[cat_num] = content_pct
        return {
            "fiscal_year": fiscal_year,
            "found": True,
            "recycling_targets_pct": cat_map_targets,
            "recycled_content_pct": cat_map_content,
            "source": "Schedule II, Clause 7 of PWM Rules (MoEFCC Notification G.S.R. 133(E))",
            "rules_version": get_ruleset_version(),
            "verified_on": get_verified_on(),
        }
    return {
        "fiscal_year": fiscal_year,
        "found": False,
        "message": f"No verified target matrix in database for {fiscal_year}. Supported years are: {', '.join(SUPPORTED_FISCAL_YEARS)}.",
        "rules_version": get_ruleset_version(),
        "verified_on": get_verified_on(),
    }

def get_annual_return_deadline() -> Dict[str, Any]:
    rules = load_rules()
    statutory_date = get_statutory_annual_return_date()
    deadlines = get_deadlines()
    return {
        "statutory_date": statutory_date,
        "statutory_date_description": f"Rule 11.3 statutory filing deadline: {statutory_date} following financial year",
        "deadlines": deadlines,
        "rules_version": get_ruleset_version(),
        "verified_on": get_verified_on(),
    }

def compute_q_tonnage(
    category_key: str,
    declared_tonnage: float,
    prior_year_tonnages: Optional[Dict[str, Any]],
) -> float:
    if not prior_year_tonnages:
        return declared_tonnage
    
    cat_roman = CATEGORY_MAP.get(category_key, category_key)
    legacy_key = ROMAN_TO_LEGACY.get(cat_roman, "")
    prior_data = None
    for candidate_key in [category_key, cat_roman, legacy_key]:
        if candidate_key and candidate_key in prior_year_tonnages:
            prior_data = prior_year_tonnages[candidate_key]
            break
    
    if prior_data is None:
        return declared_tonnage

    if isinstance(prior_data, (list, tuple)) and len(prior_data) == 2:
        y1 = _safe_tonnage(prior_data[0])
        y2 = _safe_tonnage(prior_data[1])
        return (y1 + y2) / 2.0
    elif isinstance(prior_data, dict) and len(prior_data) >= 2:
        vals = [_safe_tonnage(v) for v in list(prior_data.values())[:2]]
        return sum(vals) / 2.0

    return declared_tonnage

def calculate_liability(
    pibo_type: str = "Brand Owner",
    fiscal_year: str = "2026-27",
    tonnages: Optional[Dict[str, Any]] = None,
    prior_year_tonnages: Optional[Dict[str, Any]] = None,
    plastic_layer_weights: Optional[Dict[str, Any]] = None,
    plastic_layer_weight_mt: Optional[Union[float, Dict[str, Any]]] = None,
    consecutive_year_of_shortfall: int = 1,
    shortfalls: Optional[Dict[str, Any]] = None,
    shortfall_mt: Optional[Union[float, Dict[str, Any]]] = None,
    cert_price_override_inr_per_mt: Optional[Dict[str, float]] = None,
    epr_target_basis: Optional[str] = None,
    as_of: Optional[str] = None,
) -> Dict[str, Any]:
    tonnages = tonnages or {}
    plastic_layer_weights = dict(plastic_layer_weights or {})
    if isinstance(plastic_layer_weight_mt, dict):
        plastic_layer_weights.update(plastic_layer_weight_mt)
    
    shortfalls_input_provided = shortfalls is not None or shortfall_mt is not None
    effective_shortfalls = dict(shortfalls or {})
    if isinstance(shortfall_mt, dict):
        effective_shortfalls.update(shortfall_mt)
    elif isinstance(shortfall_mt, (int, float)):
        effective_shortfalls["cat_1"] = float(shortfall_mt)

    cert_price_override_inr_per_mt = cert_price_override_inr_per_mt or {}

    fy_defaulted = False
    chosen_fy = fiscal_year
    if chosen_fy not in SUPPORTED_FISCAL_YEARS:
        chosen_fy = "2026-27"
        fy_defaulted = True

    two_year_average_used = prior_year_tonnages is not None and len(prior_year_tonnages) > 0
    cat_iii_basis_assumed = False

    total_introduced_mt = 0.0
    total_q_mt = 0.0
    total_recycling_target_mt = 0.0
    total_recycled_content_target_mt = 0.0
    total_end_of_life_mt = 0.0
    min_cert_cost_inr = 0.0
    max_cert_cost_inr = 0.0
    total_shortfall_mt = 0.0

    categories_breakdown = {}
    cert_prices_table = get_cert_price_ranges()
    meta_cert_prices = cert_prices_table.get("_meta", {})
    as_of_val = as_of or meta_cert_prices.get("as_of", "2026-10-10")

    active_categories = ["I", "II", "III", "IV"]
    for cat_roman in active_categories:
        cat_legacy_key = ROMAN_TO_LEGACY.get(cat_roman, f"cat_{cat_roman.lower()}")
        raw_qty = tonnages.get(cat_legacy_key, tonnages.get(cat_roman, 0.0))
        declared_qty = _safe_tonnage(raw_qty)
        total_introduced_mt += declared_qty

        q_qty = compute_q_tonnage(cat_roman, declared_qty, prior_year_tonnages)
        total_q_mt += q_qty

        recycle_pct = get_recycling_min_pct(chosen_fy, cat_roman) or 0
        recycle_target_mt = (q_qty * recycle_pct) / 100.0
        total_recycling_target_mt += recycle_target_mt

        eol_share_mt = max(0.0, q_qty - recycle_target_mt)
        total_end_of_life_mt += eol_share_mt

        content_pct = get_recycled_content_pct(chosen_fy, cat_roman) or 0
        layer_weight_input = plastic_layer_weights.get(cat_roman, plastic_layer_weights.get(cat_legacy_key))
        if cat_roman == "III" and layer_weight_input is None and isinstance(plastic_layer_weight_mt, (int, float)):
            layer_weight_input = plastic_layer_weight_mt

        if layer_weight_input is not None:
            plastic_layer_weight = _safe_tonnage(layer_weight_input)
        else:
            plastic_layer_weight = declared_qty
            if cat_roman == "III":
                cat_iii_basis_assumed = True

        recycled_content_mt = (plastic_layer_weight * content_pct) / 100.0
        total_recycled_content_target_mt += recycled_content_mt

        cert_range = cert_prices_table.get(cat_roman, {})
        low_price = cert_range.get("low", 0) or 0
        high_price = cert_range.get("high", 0) or 0
        
        override_val = cert_price_override_inr_per_mt.get(cat_roman, cert_price_override_inr_per_mt.get(cat_legacy_key))
        if override_val is not None:
            safe_override = _safe_tonnage(override_val)
            low_price = safe_override
            high_price = safe_override

        cat_min_cost = recycle_target_mt * low_price
        cat_max_cost = recycle_target_mt * high_price
        min_cert_cost_inr += cat_min_cost
        max_cert_cost_inr += cat_max_cost

        if shortfalls_input_provided:
            specific_shortfall = effective_shortfalls.get(cat_roman, effective_shortfalls.get(cat_legacy_key, 0.0))
            cat_shortfall_mt = _safe_tonnage(specific_shortfall)
        else:
            cat_shortfall_mt = recycle_target_mt
        total_shortfall_mt += cat_shortfall_mt

        categories_breakdown[cat_legacy_key] = {
            "name": CATEGORY_NAMES.get(cat_roman, cat_roman),
            "category_code": cat_roman,
            "introduced_mt": round(declared_qty, 2),
            "q_tonnage_mt": round(q_qty, 2),
            "recycling_target_pct": recycle_pct,
            "recycling_obligation_mt": round(recycle_target_mt, 2),
            "remaining_to_end_of_life_routes_mt": round(eol_share_mt, 2),
            "recycled_content_mandate_pct": content_pct,
            "recycled_content_required_mt": round(recycled_content_mt, 2),
            "plastic_layer_weight_basis_mt": round(plastic_layer_weight, 2),
            "cert_market_rate_inr_per_mt": f"Rs {int(low_price):,} - Rs {int(high_price):,}",
            "estimated_cert_cost_range_inr": [round(cat_min_cost), round(cat_max_cost)],
            "shortfall_mt": round(cat_shortfall_mt, 2),
        }

    clamped_consecutive_year = max(1, int(consecutive_year_of_shortfall))
    ec_rate_inr = get_ec_rate(clamped_consecutive_year)
    ec_exposure_inr = total_shortfall_mt * ec_rate_inr

    refund_1 = get_refund_pct(1)
    refund_2 = get_refund_pct(2)
    refund_3 = get_refund_pct(3)

    rate_table = {
        "1": get_ec_rate(1),
        "2": get_ec_rate(2),
        "3+": get_ec_rate(3),
    }

    rules_meta = {
        "rules_version": get_ruleset_version(),
        "verified_on": get_verified_on(),
        "fy_defaulted": fy_defaulted,
        "basis": "two_year_average" if two_year_average_used else "simplified_estimate",
        "cat_iii_basis_assumed": cat_iii_basis_assumed,
        "status_flags": ["needs_verify"],
        "disclaimer": "simplified estimate",
    }

    return {
        "pibo_type": pibo_type,
        "fiscal_year": chosen_fy,
        "total_introduced_packaging_mt": round(total_introduced_mt, 2),
        "total_q_mt": round(total_q_mt, 2),
        "total_recycling_obligation_mt": round(total_recycling_target_mt, 2),
        "remaining_to_end_of_life_routes_mt": round(total_end_of_life_mt, 2),
        "total_recycled_content_required_mt": round(total_recycled_content_target_mt, 2),
        "total_shortfall_mt": round(total_shortfall_mt, 2),
        "consecutive_year_of_shortfall": clamped_consecutive_year,
        "applicable_ec_rate_inr_per_mt": ec_rate_inr,
        "ec_rate_table_inr_per_mt": rate_table,
        "potential_ec_penalty_exposure_inr": round(ec_exposure_inr),
        "estimated_cert_procurement_cost_range_inr": {
            "min": round(min_cert_cost_inr),
            "max": round(max_cert_cost_inr),
            "formatted": f"Rs {round(min_cert_cost_inr):,} - Rs {round(max_cert_cost_inr):,}",
            "as_of": as_of_val,
            "status": meta_cert_prices.get("status", "needs_verify"),
        },
        "ec_refund_schedule": {
            "year_1_fulfillment": f"{refund_1}% refund (Rs {round(ec_exposure_inr * refund_1 / 100.0):,})",
            "year_2_fulfillment": f"{refund_2}% refund (Rs {round(ec_exposure_inr * refund_2 / 100.0):,})",
            "year_3_fulfillment": f"{refund_3}% refund (Rs {round(ec_exposure_inr * refund_3 / 100.0):,})",
            "after_year_3": "0% refund (forfeited permanently)",
            "refund_percentages": [refund_1, refund_2, refund_3, 0],
        },
        "categories": categories_breakdown,
        "governing_rules": "Schedule II of PWM Rules, 2016 (MoEFCC)",
        "_meta": rules_meta,
    }
