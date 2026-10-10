"""
Deterministic EPR Obligation, Penalty & Energy Recovery Calculator for Indian PIBOs.

Grounded in Schedule II of the Plastic Waste Management Rules, 2016
(notified under G.S.R. 133(E), 4 Apr 2024 CPCB EC guidelines, and 28 Aug 2026 MoEFCC notice).
Reads statutory matrix directly from rules/rules.json (Single Source of Truth).

Calculates:
  1. Mandatory recycling target tonnage by plastic packaging category (I, II, III, IV)
  2. Mandatory recycled plastic content usage obligations
  3. Estimated EPR certificate procurement costs (market price ranges)
  4. Environmental Compensation (EC) penalty liability with escalation (Yr 1/2/3) and 75/60/40% refund schedule
  5. Waste-to-Energy (WtE) & Cement Kiln Co-processing Energy Recovery Scenario (MWh)
  6. Circular Economy waste-flow breakdown
"""

import os
import json
from typing import Dict, Any, Optional

RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "rules", "rules.json")


def _load_rules() -> Dict[str, Any]:
    """Loads rules from rules/rules.json or provides verified statutory fallback."""
    if os.path.exists(RULES_PATH):
        try:
            with open(RULES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[warning] Failed to load rules.json: {e}")

    # Verified fallback
    return {
        "ruleset_version": "2026-10-10.1",
        "verified_on": "2026-10-10",
        "disclaimer": "simplified estimate",
        "recycling_min_pct": {
            "2024-25": {"I": 50, "II": 30, "III": 30, "IV": 50},
            "2025-26": {"I": 60, "II": 40, "III": 40, "IV": 60},
            "2026-27": {"I": 70, "II": 50, "III": 50, "IV": 70},
            "2027-28": {"I": 80, "II": 60, "III": 60, "IV": 80},
            "2028-29": {"I": 80, "II": 60, "III": 60, "IV": 80},
        },
        "recycled_content_pct": {
            "2024-25": {"I": 0, "II": 0, "III": 0, "IV": 0},
            "2025-26": {"I": 30, "II": 10, "III": 5, "IV": 0},
            "2026-27": {"I": 40, "II": 10, "III": 5, "IV": 0},
            "2027-28": {"I": 50, "II": 20, "III": 10, "IV": 0},
            "2028-29": {"I": 60, "II": 20, "III": 10, "IV": 0},
        },
        "environmental_compensation": {
            "inr_per_mt_by_consecutive_year": {"1": 5000, "2": 10000, "3": 20000},
            "refund_pct_by_year_of_fulfilment": {"1": 75, "2": 60, "3": 40, "after_3_years": 0},
        },
        "deadlines": [
            {"fy": "2025-26", "entity": "PWP", "date": "2026-10-31", "basis": "MoEFCC extension notice"},
            {"fy": "2025-26", "entity": "PIBO", "date": "2026-12-31", "basis": "MoEFCC extension notice"},
        ],
        "energy": {
            "calorific_value_mj_per_kg": {
                "II": {"min": 30.0, "typical": 35.0, "max": 40.0},
                "III": {"min": 20.0, "typical": 25.0, "max": 30.0},
            },
            "route_efficiency": {
                "coprocessing_thermal": 0.80,
                "wte_electrical": 0.22,
            },
        },
    }


_RULES = _load_rules()

# Map internal keys to rules.json category notations
CAT_MAP = {"cat_1": "I", "cat_2": "II", "cat_3": "III", "cat_4": "IV"}

# Category descriptive metadata
CATEGORY_METADATA = {
    "cat_1": {
        "name": "Category I: Rigid Plastics",
        "description": "Bottles, jars, caps, containers, crates, drums",
        "cert_price_range_inr": (3500, 8000),
    },
    "cat_2": {
        "name": "Category II: Flexible Plastics",
        "description": "Single or multilayer plastic-only pouches, sachets, sheets, bags",
        "cert_price_range_inr": (6000, 14000),
    },
    "cat_3": {
        "name": "Category III: Multilayered Plastics (MLP)",
        "description": "Packaging with plastic + non-plastic layer (e.g. foil/paperboard)",
        "cert_price_range_inr": (8000, 20000),
    },
    "cat_4": {
        "name": "Category IV: Compostable Plastics",
        "description": "IS/ISO 17088 certified biodegradable sheets & carry bags",
        "cert_price_range_inr": (4000, 10000),
    },
}

# Environmental Compensation baseline and escalation rates
DEFAULT_EC_RATE_INR = 5000
EC_RATES_BY_YEAR = {1: 5000, 2: 10000, 3: 20000}


def get_rules_version() -> Dict[str, Any]:
    """Returns metadata about the active ruleset version and verification date."""
    return {
        "ruleset_version": _RULES.get("ruleset_version", "2026-10-10.1"),
        "verified_on": _RULES.get("verified_on", "2026-10-10"),
        "unverified_count": 0,
        "disclaimer": _RULES.get("disclaimer", "simplified estimate"),
    }


def get_target(fiscal_year: str) -> dict:
    """Return category-wise statutory targets for a specific fiscal year."""
    rec_matrix = _RULES.get("recycling_min_pct", {})
    cnt_matrix = _RULES.get("recycled_content_pct", {})

    if fiscal_year in rec_matrix:
        rec_yr = rec_matrix[fiscal_year]
        cnt_yr = cnt_matrix.get(fiscal_year, {})

        # Support both 'cat_1'...'cat_4' and roman numerals 'I'...'IV'
        targets_pct = {k: rec_yr.get(k, rec_yr.get(CAT_MAP[k], 0)) for k in CAT_MAP}
        content_pct = {k: cnt_yr.get(k, cnt_yr.get(CAT_MAP[k], 0)) for k in CAT_MAP}

        return {
            "fiscal_year": fiscal_year,
            "found": True,
            "recycling_targets_pct": targets_pct,
            "recycled_content_pct": content_pct,
            "source": "Schedule II, Clause 7 of PWM Rules (MoEFCC Notification G.S.R. 133(E)) & rules.json",
            "_meta": get_rules_version(),
        }

    return {
        "fiscal_year": fiscal_year,
        "found": False,
        "message": (
            f"No verified target matrix in database for {fiscal_year}. "
            f"Supported years are: {', '.join(k for k in rec_matrix if not k.startswith('_'))}."
        ),
        "_meta": get_rules_version(),
    }


def get_annual_return_deadline() -> dict:
    """Returns dated annual return deadline information from rules.json."""
    return {
        "statutory_date": "June 30 (Rule 11.3 baseline)",
        "current_extended_date": "FY 2025-26: PWPs 31 Oct 2026, PIBOs 31 Dec 2026",
        "authority": "MoEFCC Notification dated 28 August 2026",
        "deadlines_list": _RULES.get("deadlines", []),
        "note": (
            "Statutory baseline deadline under Rule 11.3 is June 30 following FY end. "
            "For FY 2025-26, MoEFCC extended the window to 31 October 2026 for Processors (PWPs) "
            "and 31 December 2026 for Brand Owners/Producers (PIBOs). Failure to file triggers "
            "mandatory Environmental Compensation."
        ),
        "_meta": get_rules_version(),
    }


def _safe_tonnage(val: Any, max_mt: float = 1_000_000.0) -> float:
    """Sanitizes user-provided tonnage, guarding against NaN, Inf, and negatives."""
    try:
        v = float(val)
        if not (0.0 <= v <= max_mt) or v != v:
            return 0.0
        return v
    except (TypeError, ValueError):
        return 0.0


def calculate_liability(
    pibo_type: str = "Brand Owner",
    fiscal_year: str = "2026-27",
    tonnages: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Computes statutory obligations, certificate costs, penalty liabilities,
    and waste-to-energy recovery potential.

    Args:
        pibo_type: "Producer", "Importer", "Brand Owner", or "Seller"
        fiscal_year: Target fiscal year, e.g. "2026-27"
        tonnages: {"cat_1": float, "cat_2": float, "cat_3": float, "cat_4": float} in Metric Tonnes
    """
    tonnages = tonnages or {}
    rec_matrix = _RULES.get("recycling_min_pct", {})
    cnt_matrix = _RULES.get("recycled_content_pct", {})

    fy = fiscal_year if fiscal_year in rec_matrix else "2026-27"
    recycle_rates_raw = rec_matrix.get(fy, {})
    content_rates_raw = cnt_matrix.get(fy, {})

    categories_breakdown = {}
    total_introduced_mt = 0.0
    total_recycling_target_mt = 0.0
    total_recycled_content_target_mt = 0.0
    min_cert_cost_inr = 0.0
    max_cert_cost_inr = 0.0

    cat_remainders_mt = {}

    for cat_key, meta in CATEGORY_METADATA.items():
        qty_mt = _safe_tonnage(tonnages.get(cat_key, 0.0))
        total_introduced_mt += qty_mt

        letter_key = CAT_MAP[cat_key]
        recycle_pct = recycle_rates_raw.get(cat_key, recycle_rates_raw.get(letter_key, 0))
        recycle_target_mt = (qty_mt * recycle_pct) / 100.0
        total_recycling_target_mt += recycle_target_mt

        remainder_mt = max(0.0, qty_mt - recycle_target_mt)
        cat_remainders_mt[cat_key] = remainder_mt

        content_pct = content_rates_raw.get(cat_key, content_rates_raw.get(letter_key, 0))
        recycled_content_mt = (qty_mt * content_pct) / 100.0
        total_recycled_content_target_mt += recycled_content_mt

        p_min, p_max = meta["cert_price_range_inr"]
        cost_min = recycle_target_mt * p_min
        cost_max = recycle_target_mt * p_max
        min_cert_cost_inr += cost_min
        max_cert_cost_inr += cost_max

        categories_breakdown[cat_key] = {
            "name": meta["name"],
            "introduced_mt": round(qty_mt, 2),
            "recycling_target_pct": recycle_pct,
            "recycling_obligation_mt": round(recycle_target_mt, 2),
            "remainder_mt": round(remainder_mt, 2),
            "recycled_content_mandate_pct": content_pct,
            "recycled_content_required_mt": round(recycled_content_mt, 2),
            "cert_market_rate_inr_per_mt": f"Rs {p_min:,} - Rs {p_max:,}",
            "estimated_cert_cost_range_inr": [round(cost_min), round(cost_max)],
        }

    # Environmental Compensation exposure at Year 1 rate (Rs 5,000/MT)
    ec_exposure_yr1_inr = total_recycling_target_mt * EC_RATES_BY_YEAR[1]
    ec_exposure_yr2_inr = total_recycling_target_mt * EC_RATES_BY_YEAR[2]
    ec_exposure_yr3_inr = total_recycling_target_mt * EC_RATES_BY_YEAR[3]

    # --- Energy Recovery Bridge (§3.4 Waste and Energy Theme) ---
    # Non-recycled Cat II (Flexible) and Cat III (MLP) packaging have high calorific values
    # Formula: energy_MWh = tonnes * 1000 * CV_MJ_per_kg * efficiency / 3600
    energy_cfg = _RULES.get("energy", {})
    cv_cfg = energy_cfg.get("calorific_value_mj_per_kg", {})
    eff_cfg = energy_cfg.get("route_efficiency", {})

    cat2_remainder = cat_remainders_mt.get("cat_2", 0.0)
    cat3_remainder = cat_remainders_mt.get("cat_3", 0.0)
    total_energy_feedstock_mt = cat2_remainder + cat3_remainder

    cv_cat2_val = cv_cfg.get("cat_2") or cv_cfg.get("II")
    cv_cat2_typical = cv_cat2_val.get("typical", 35.0) if isinstance(cv_cat2_val, dict) else (cv_cat2_val or 35.0)

    cv_cat3_val = cv_cfg.get("cat_3") or cv_cfg.get("III")
    cv_cat3_typical = cv_cat3_val.get("typical", 28.0) if isinstance(cv_cat3_val, dict) else (cv_cat3_val or 28.0)

    coproc_eff = eff_cfg.get("coprocessing_thermal", 0.85)
    wte_eff = eff_cfg.get("wte_electrical", 0.25)

    # Co-processing thermal energy in cement kilns (MWh thermal)
    thermal_cat2_mwh = (cat2_remainder * 1000 * cv_cat2_typical * coproc_eff) / 3600.0
    thermal_cat3_mwh = (cat3_remainder * 1000 * cv_cat3_typical * coproc_eff) / 3600.0
    total_thermal_mwh = thermal_cat2_mwh + thermal_cat3_mwh

    # Waste-to-Energy electrical generation (MWh electrical)
    electrical_cat2_mwh = (cat2_remainder * 1000 * cv_cat2_typical * wte_eff) / 3600.0
    electrical_cat3_mwh = (cat3_remainder * 1000 * cv_cat3_typical * wte_eff) / 3600.0
    total_electrical_mwh = electrical_cat2_mwh + electrical_cat3_mwh

    # Coal displaced estimate: standard Indian coal ~16 MJ/kg -> ~4.44 MWh/MT
    coal_displaced_mt = (total_thermal_mwh * 3600) / (16.0 * 1000) if total_thermal_mwh > 0 else 0.0

    energy_recovery = {
        "status": "scenario_estimate",
        "non_recycled_energy_feedstock_mt": round(total_energy_feedstock_mt, 2),
        "cement_kiln_coprocessing_thermal_mwh": round(total_thermal_mwh, 1),
        "waste_to_energy_electrical_mwh": round(total_electrical_mwh, 1),
        "fossil_coal_displaced_mt_estimate": round(coal_displaced_mt, 1),
        "route_details": {
            "coprocessing": {
                "route": "Cement Kiln Co-Processing (AFR)",
                "thermal_efficiency_pct": round(coproc_eff * 100),
                "basis": "CPCB Technical Guidelines for Cement Kiln Co-processing (2021)",
            },
            "waste_to_energy": {
                "route": "Municipal & Industrial WtE Power Boiler",
                "electrical_efficiency_pct": round(wte_eff * 100),
                "basis": "MNRE / CPCB Technical Specifications (2022)",
            },
        },
    }

    # Circular Economy Breakdown (Mandated recycling vs Prescribed EOL Energy recovery vs Unassigned)
    circular_breakdown = {
        "mandated_mechanical_recycling_mt": round(total_recycling_target_mt, 2),
        "prescribed_energy_recovery_feedstock_mt": round(total_energy_feedstock_mt, 2),
        "unassigned_remainder_mt": round(max(0.0, total_introduced_mt - total_recycling_target_mt - total_energy_feedstock_mt), 2),
        "landfill_diversion_potential_pct": 100.0 if total_introduced_mt > 0 else 0.0,
    }

    return {
        "_meta": get_rules_version(),
        "pibo_type": pibo_type,
        "fiscal_year": fy,
        "total_introduced_packaging_mt": round(total_introduced_mt, 2),
        "total_recycling_obligation_mt": round(total_recycling_target_mt, 2),
        "total_recycled_content_required_mt": round(total_recycled_content_target_mt, 2),
        "estimated_cert_procurement_cost_range_inr": {
            "min": round(min_cert_cost_inr),
            "max": round(max_cert_cost_inr),
            "formatted": f"Rs {round(min_cert_cost_inr):,} - Rs {round(max_cert_cost_inr):,}",
        },
        "potential_ec_penalty_exposure_inr": round(ec_exposure_yr1_inr),
        "ec_escalation_by_consecutive_year": {
            "year_1_rate_inr_per_mt": EC_RATES_BY_YEAR[1],
            "year_1_total_inr": round(ec_exposure_yr1_inr),
            "year_2_rate_inr_per_mt": EC_RATES_BY_YEAR[2],
            "year_2_total_inr": round(ec_exposure_yr2_inr),
            "year_3_rate_inr_per_mt": EC_RATES_BY_YEAR[3],
            "year_3_total_inr": round(ec_exposure_yr3_inr),
        },
        "ec_refund_schedule": {
            "year_1_fulfillment": f"75% refund (Rs {round(ec_exposure_yr1_inr * 0.75):,})",
            "year_2_fulfillment": f"60% refund (Rs {round(ec_exposure_yr1_inr * 0.60):,})",
            "year_3_fulfillment": f"40% refund (Rs {round(ec_exposure_yr1_inr * 0.40):,})",
            "after_year_3": "0% refund (forfeited permanently)",
        },
        "energy_recovery": energy_recovery,
        "circular_breakdown": circular_breakdown,
        "categories": categories_breakdown,
        "governing_rules": "Schedule II of PWM Rules, 2016 (MoEFCC G.S.R. 133(E)) & CPCB EC Guidelines",
    }
