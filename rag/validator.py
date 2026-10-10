"""
Rule 11 Packaging Artwork & Labeling Compliance Validator for EPR Copilot.
Validates packaging artwork text, declarations, and QR specs against statutory requirements:
- Rule 11 of Plastic Waste Management Rules, 2016 (and 2022/2024 amendments)
- IS 14534 Guidelines for Recycling of Plastics
- IS/ISO 17088 for Compostable Plastic standards
"""

import re
from typing import Dict, List, Any


RULE_11_MANDATES = [
    {
        "id": "R11-REG",
        "title": "CPCB/SPCB Registration Number Declaration",
        "severity": "CRITICAL",
        "rule_clause": "Rule 11(1)(c) PWM Rules",
        "regex": r"(?:cpcb|spcb)[/\-_]?(?:pwm)?[/\-_]?[a-z0-9/\-_]{4,30}",
        "description": "Packaging must prominently display the CPCB/SPCB EPR Registration Number.",
        "penalty_risk": "Immediate seizure of non-compliant inventory + Section 15 EPA penalty."
    },
    {
        "id": "R11-POLYMER",
        "title": "Polymer Identification Mark & Recycling Symbol (IS 14534)",
        "severity": "CRITICAL",
        "rule_clause": "Rule 11(1)(a) & IS 14534",
        "regex": r"(?:pet[e]?|hdpe|pvc|ldpe|pp|ps|other|\b(?:code|symbol)\s*[1-7]\b|♻️?)",
        "description": "Standard resin identification code (1 to 7) and resin acronym must be embossed or printed.",
        "penalty_risk": "Labeling violation under Rule 11."
    },
    {
        "id": "R11-THICKNESS",
        "title": "Thickness Declaration (>= 120 Microns)",
        "severity": "HIGH",
        "rule_clause": "Rule 4(1)(c) & Rule 11(1)(a)",
        "regex": r"(\d{2,4})\s*(?:microns?|µm|mic|micron)",
        "description": "Carry bags and packaging films must declare thickness in microns (minimum 120 microns threshold).",
        "penalty_risk": "Prohibited sub-120 micron plastic ban under PWM Amendment 2022."
    },
    {
        "id": "R11-QR",
        "title": "Traceability QR Code / Barcode",
        "severity": "HIGH",
        "rule_clause": "Rule 11(1)(e) Amendment",
        "regex": r"(?:qr\s*code|scannable\s*qr|barcode|traceability\s*code|digital\s*watermark)",
        "description": "Traceable dynamic QR code linking to PIBO portal verification must be printed.",
        "penalty_risk": "Non-traceable packaging non-compliance notice."
    },
    {
        "id": "R11-COMPOST",
        "title": "Compostable Plastic IS/ISO 17088 Certificate & CPCB QR",
        "severity": "MEDIUM",
        "rule_clause": "Rule 11(1)(b) Compostable Plastic",
        "regex": r"(?:is/iso\s*17088|cpcb\s*compostable|cipet\s*certified)",
        "description": "If claimed compostable, packaging must declare compliance with IS/ISO 17088 and CIPET certificate number.",
        "penalty_risk": "Misbranding fine and cancellation of compostable clearance."
    }
]

SAMPLE_ARTWORKS = {
    "compliant_pet": {
        "title": "Compliant PET Water Bottle Label (Full Compliance)",
        "artwork_text": """
Brand: PureFlow Natural Spring Water (1000 ml)
Manufacturer: Himalayan Beverages Pvt Ltd, Solan, Himachal Pradesh
CPCB EPR Registration No: CPCB/PWM/BO/HP/2024/098812
Packaging Material: Polyethylene Terephthalate (PET - Resin Code 1) ♳
Recyclability Declaration: 100% Recyclable Plastic. Please crush the bottle after use.
Statutory Batch No: B-9982 | Scan QR Code below for CPCB EPR verification and recycling certificate trace:
[QR Code embedded: https://cpcb.nic.in/epr-verify?id=CPCB/PWM/BO/HP/2024/098812]
Thickness: Cap 850 Micron, Preform Wall 280 Micron
"""
    },
    "non_compliant_pouch": {
        "title": "Non-Compliant Multi-layer Snack Pouch (Multiple Violations)",
        "artwork_text": """
Tasty Crunch Spiced Potato Chips (Net Wt 50g)
Mfg by: Metro Confectionery, Industrial Area, Okhla, New Delhi
Ingredients: Potatoes, Edible Oil, Spices, Salt.
Best Before 6 months from packaging.
Keep in cool dry place.
(No EPR registration, no polymer code, no micron thickness declaration, no QR code)
"""
    },
    "borderline_ldpe": {
        "title": "Borderline E-Commerce Mailer Bag (Missing Thickness & CPCB Reg)",
        "artwork_text": """
Express Courier Security Envelopes
Material: Low Density Polyethylene (LDPE - Resin Code 4)
Recycle symbol printed: ♶
Manufactured in India for QuickShip D2C Logistics
Please dispose responsibly in dry waste bin.
Barcode: 8901234567890
"""
    },
    "synthetic_company": {
        "title": "Reliance Retail JioMart FMCG Packaging Artwork (Demo Synthetic)",
        "artwork_text": """
Brand: JioMart Fresh / Reliance Smart Everyday
Product: Premium Cashews (500g)
Packaged and Marketed by: Reliance Retail Ltd., Mumbai, Maharashtra
CPCB EPR Registration No: CPCB/PWM/BO/MH/2026/882199
Packaging Material Type: Multi-Layer Plastic (MLP - PET/Foil/PE)
Resin Code: Category III (7)
Thickness: 145 Micron (Compliant with PWM Rules Amendment > 120 Microns)
Please dispose of responsibly. Not for roadside litter.
[Traceability QR Code embedded: https://cpcb.nic.in/epr-verify?id=CPCB/PWM/BO/MH/2026/882199]
"""
    }
}


def validate_packaging_artwork(artwork_text: str) -> Dict[str, Any]:
    """
    Evaluates packaging label text against CPCB Rule 11 statutory requirements.
    Calculates compliance score, flags missing clauses, and checks thickness.
    """
    if not artwork_text or not artwork_text.strip():
        return {
            "score": 0,
            "status": "NON-COMPLIANT",
            "findings": [],
            "passed_count": 0,
            "failed_count": len(RULE_11_MANDATES),
            "recommendations": ["Submit artwork label text for statutory evaluation."]
        }

    lower_text = artwork_text.lower()
    findings = []
    passed = 0
    total_checks = 4  # Standard non-compostable checks (or 5 if compostable claimed)
    is_compostable_claimed = "compostable" in lower_text or "biodegradable" in lower_text

    # 1. Registration Number
    reg_match = re.search(RULE_11_MANDATES[0]["regex"], lower_text)
    if reg_match:
        passed += 1
        findings.append({
            "check": RULE_11_MANDATES[0]["title"],
            "status": "PASS",
            "matched_text": reg_match.group(0),
            "clause": RULE_11_MANDATES[0]["rule_clause"],
            "severity": "LOW"
        })
    else:
        findings.append({
            "check": RULE_11_MANDATES[0]["title"],
            "status": "FAIL",
            "message": "Missing CPCB/SPCB Registration Number (e.g. CPCB/PWM/BO/...).",
            "clause": RULE_11_MANDATES[0]["rule_clause"],
            "severity": RULE_11_MANDATES[0]["severity"]
        })

    # 2. Polymer Identification Code
    poly_match = re.search(RULE_11_MANDATES[1]["regex"], lower_text)
    if poly_match:
        passed += 1
        findings.append({
            "check": RULE_11_MANDATES[1]["title"],
            "status": "PASS",
            "matched_text": poly_match.group(0),
            "clause": RULE_11_MANDATES[1]["rule_clause"],
            "severity": "LOW"
        })
    else:
        findings.append({
            "check": RULE_11_MANDATES[1]["title"],
            "status": "FAIL",
            "message": "No resin identification code (1 to 7) or polymer name detected.",
            "clause": RULE_11_MANDATES[1]["rule_clause"],
            "severity": RULE_11_MANDATES[1]["severity"]
        })

    # 3. Thickness Check (>= 120 microns)
    thick_match = re.search(RULE_11_MANDATES[2]["regex"], lower_text)
    if thick_match:
        val = int(thick_match.group(1))
        if val >= 120:
            passed += 1
            findings.append({
                "check": RULE_11_MANDATES[2]["title"],
                "status": "PASS",
                "matched_text": f"{val} microns (Compliant: >= 120 µm)",
                "clause": RULE_11_MANDATES[2]["rule_clause"],
                "severity": "LOW"
            })
        else:
            findings.append({
                "check": RULE_11_MANDATES[2]["title"],
                "status": "FAIL",
                "message": f"Declared thickness of {val} microns is ILLEGAL under Rule 4(1)(c) (< 120 micron threshold).",
                "clause": RULE_11_MANDATES[2]["rule_clause"],
                "severity": "CRITICAL"
            })
    else:
        findings.append({
            "check": RULE_11_MANDATES[2]["title"],
            "status": "WARNING",
            "message": "No explicit micron thickness declared. Required for carry bags and flexible films.",
            "clause": RULE_11_MANDATES[2]["rule_clause"],
            "severity": "HIGH"
        })

    # 4. QR Code & Traceability
    qr_match = re.search(RULE_11_MANDATES[3]["regex"], lower_text)
    if qr_match:
        passed += 1
        findings.append({
            "check": RULE_11_MANDATES[3]["title"],
            "status": "PASS",
            "matched_text": qr_match.group(0),
            "clause": RULE_11_MANDATES[3]["rule_clause"],
            "severity": "LOW"
        })
    else:
        findings.append({
            "check": RULE_11_MANDATES[3]["title"],
            "status": "FAIL",
            "message": "No dynamic QR code or traceability mechanism declared.",
            "clause": RULE_11_MANDATES[3]["rule_clause"],
            "severity": RULE_11_MANDATES[3]["severity"]
        })

    # 5. Compostable check if applicable
    if is_compostable_claimed:
        total_checks += 1
        comp_match = re.search(RULE_11_MANDATES[4]["regex"], lower_text)
        if comp_match:
            passed += 1
            findings.append({
                "check": RULE_11_MANDATES[4]["title"],
                "status": "PASS",
                "matched_text": comp_match.group(0),
                "clause": RULE_11_MANDATES[4]["rule_clause"],
                "severity": "LOW"
            })
        else:
            findings.append({
                "check": RULE_11_MANDATES[4]["title"],
                "status": "FAIL",
                "message": "Compostable plastic claimed but missing mandatory IS/ISO 17088 CIPET certification mark.",
                "clause": RULE_11_MANDATES[4]["rule_clause"],
                "severity": "CRITICAL"
            })

    score = round((passed / total_checks) * 100)
    status = "COMPLIANT" if score >= 80 else ("NEEDS REVISION" if score >= 50 else "NON-COMPLIANT")

    recommendations = []
    if not reg_match:
        recommendations.append("Print your official CPCB registration number: 'CPCB/PWM/BO/YYYY/XXXXXX'.")
    if not poly_match:
        recommendations.append("Add the IS 14534 recycling resin triangle with polymer code (1 for PET, 2 for HDPE, etc.).")
    if not thick_match or (thick_match and int(thick_match.group(1)) < 120):
        recommendations.append("Ensure thickness is at least 120 microns and printed explicitly on flexible films.")
    if not qr_match:
        recommendations.append("Embed a high-contrast scannable QR code linking to your CPCB EPR verification link.")

    return {
        "score": score,
        "status": status,
        "passed_checks": passed,
        "total_checks": total_checks,
        "findings": findings,
        "recommendations": recommendations,
        "cpcb_rule_reference": "Rule 11 of PWM Rules 2016 (Schedule II)"
    }


def get_sample_artworks() -> Dict[str, Any]:
    return SAMPLE_ARTWORKS
