"""
Circular Economy & Road Manufacturing Plastic Reuse Engine.
Statutory standards under:
- Indian Roads Congress IRC:SP:98-2020 (Guidelines for use of waste plastic in hot bituminous mixes)
- Ministry of Road Transport & Highways (MoRTH) Circular RW/NH-33044/27/2019-S&R (P&B)
- CPCB End-of-Life (EOL) disposal credit guidelines for plastic packaging.
"""

from typing import Dict, Any

# IRC:SP:98-2020 Polymer Suitability Matrix
POLYMER_ROAD_SUITABILITY = {
    "ldpe": {
        "name": "LDPE / LLDPE (Category II Flexible)",
        "suitability": "EXCELLENT",
        "suitability_pct": 100,
        "irc_standard": "IRC:SP:98-2020 (Clause 4.2)",
        "recommended_blend_pct": "6% to 8% by weight of Bitumen (VG-30)",
        "melting_temp_c": "110°C - 120°C",
        "shred_size_mm": "2mm to 4mm",
        "benefits": "Increases Marshall Stability by 25%, prevents rutting, improves water resistance.",
        "prohibited": False,
        "reason": "Softens at coating temperature (160°C) without burning; binds perfectly with hot aggregate."
    },
    "hdpe": {
        "name": "HDPE (Category I Rigid / Regrind)",
        "suitability": "GOOD",
        "suitability_pct": 90,
        "irc_standard": "IRC:SP:98-2020 (Clause 4.2)",
        "recommended_blend_pct": "6% by weight of Bitumen",
        "melting_temp_c": "130°C - 135°C",
        "shred_size_mm": "2mm to 3mm",
        "benefits": "Higher tensile strength, increases load bearing capacity for heavy vehicular traffic.",
        "prohibited": False,
        "reason": "Requires high-shear shredding and slightly higher mixing temperature."
    },
    "pp": {
        "name": "Polypropylene (PP - Category II / Woven Sacks)",
        "suitability": "EXCELLENT",
        "suitability_pct": 95,
        "irc_standard": "IRC:SP:98-2020 (Clause 4.2)",
        "recommended_blend_pct": "7% to 8% by weight of Bitumen",
        "melting_temp_c": "160°C - 165°C",
        "shred_size_mm": "2mm to 4mm",
        "benefits": "Exceptional softening point elevation; prevents road bleeding in peak Indian summers (45°C+).",
        "prohibited": False,
        "reason": "Ideal thermal stability matching bitumen pug mill temperatures."
    },
    "mlp": {
        "name": "Multi-Layered Plastics (MLP - Category III Foil/Polymer Laminates)",
        "suitability": "HIGHLY RECOMMENDED FOR END-OF-LIFE",
        "suitability_pct": 85,
        "irc_standard": "IRC:SP:98-2020 & MoRTH Circular 2019",
        "recommended_blend_pct": "8% by weight of Bitumen",
        "melting_temp_c": "120°C - 160°C",
        "shred_size_mm": "2mm to 4mm (dust-free)",
        "benefits": "Diverts non-recyclable metallized pouches from landfills into durable road infrastructure.",
        "prohibited": False,
        "reason": "CPCB grants full End-of-Life (EOL) EPR certificates for MLP channeled to road construction."
    },
    "pet": {
        "name": "PET Bottles (Category I Rigid)",
        "suitability": "NOT RECOMMENDED FOR DIRECT BITUMEN MIX",
        "suitability_pct": 30,
        "irc_standard": "IRC:SP:98-2020 (Requires chemical glycolysis first)",
        "recommended_blend_pct": "Not suitable in raw shredded form",
        "melting_temp_c": "> 250°C",
        "shred_size_mm": "N/A",
        "benefits": "Higher economic value in bottle-to-bottle recycling and rPET textile fiber spinning.",
        "prohibited": False,
        "reason": "Melting point (255°C) exceeds hot bitumen mixing temperature (160°C); fails to melt and forms brittle weak spots."
    },
    "pvc": {
        "name": "PVC (Polyvinyl Chloride - Category I / Pipes / Blisters)",
        "suitability": "STRICTLY ILLEGAL & PROHIBITED",
        "suitability_pct": 0,
        "irc_standard": "IRC:SP:98-2020 (Clause 4.3 BANNED LIST)",
        "recommended_blend_pct": "0% (STRICTLY FORBIDDEN)",
        "melting_temp_c": "Degrades at 140°C",
        "shred_size_mm": "N/A",
        "benefits": "NONE. Toxic and corrosive.",
        "prohibited": True,
        "reason": "Decomposes at 140°C releasing lethal chlorine gas, dioxins, and hydrochloric acid. Corrodes road equipment and causes cancer."
    }
}


def evaluate_road_reuse(polymer_code: str, tonnage_mt: float) -> Dict[str, Any]:
    """
    Evaluates whether a plastic waste stream is suitable for road construction
    under IRC:SP:98-2020 and calculates environmental road-km impact.
    """
    key = polymer_code.lower().strip()
    spec = POLYMER_ROAD_SUITABILITY.get(key) or POLYMER_ROAD_SUITABILITY["ldpe"]
    tonnage = max(0.0, float(tonnage_mt or 0.0))

    # Real highway construction metric:
    # 1 km of 2-lane National Highway (7m wide, 40mm bituminous concrete) uses approx 10 MT bitumen.
    # At 8% plastic blend ratio, 1 km consumes ~0.8 MT of plastic waste (~800 kg).
    plastic_per_km_mt = 0.8
    potential_km_paved = round(tonnage / plastic_per_km_mt, 1) if not spec["prohibited"] else 0.0

    # 1 MT of flexible plastic waste is approx 1,000,000 single-use pouches/carry bags
    pouches_diverted_from_landfill = int(tonnage * 1_000_000)

    # CPCB End-of-life credit value: ~Rs 1,800 to Rs 2,500 / MT
    eol_credit_value_inr = round(tonnage * 2100.0, 2) if not spec["prohibited"] else 0.0

    return {
        "polymer_evaluated": spec["name"],
        "tonnage_input_mt": tonnage,
        "suitability_status": spec["suitability"],
        "suitability_score_pct": spec["suitability_pct"],
        "is_prohibited": spec["prohibited"],
        "irc_standard_clause": spec["irc_standard"],
        "recommended_blend_pct": spec["recommended_blend_pct"],
        "melting_temperature": spec["melting_temp_c"],
        "shredding_spec": spec["shred_size_mm"],
        "technical_verdict": spec["reason"],
        "road_impact": {
            "potential_highway_km_paved": potential_km_paved,
            "single_use_plastics_diverted": pouches_diverted_from_landfill,
            "estimated_cpcb_eol_credit_value_inr": eol_credit_value_inr
        },
        "governing_circular": "MoRTH Circular RW/NH-33044/27/2019-S&R (P&B) for National Highway Construction"
    }
