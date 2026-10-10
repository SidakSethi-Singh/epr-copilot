"""
AWS Textract Manifest & Weighbridge OCR Ingestion Engine.
Extracts structured compliance data from Indian GST E-Way Bills, Transporter Bilties,
and Industrial Weighbridge Slips (Vapi, Bhiwandi, Manesar, Guj / MH industrial corridors).
Connects to Amazon Textract with robust fallback for offline hackathon demos.
"""

import os
import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("epr_copilot.textract")

SAMPLE_TEXTRACT_MANIFESTS: Dict[str, Dict[str, Any]] = {
    "vapi_weighbridge": {
        "title": "Vapi GIDC Industrial Weighbridge Slip (Cat I Rigid HDPE)",
        "document_type": "WEIGHBRIDGE_COMPUTERIZED_SLIP",
        "raw_text": (
            "SHRI SAI AUTOMATED WEIGHBRIDGE - GIDC PHASE II, VAPI, GUJARAT\n"
            "RST NO: WB-2026/09421   DATE: 12-09-2026   TIME: 14:32 IST\n"
            "VEHICLE NO: GJ-15-XY-4401   TRANSPORTER: GUJARAT ROADWAYS\n"
            "CUSTOMER: BHARAT BEVERAGES & SNACKS LTD (GSTIN: 27AABCB9102K1ZP)\n"
            "RECEIVER: GUJARAT POLYMER RECYCLING PWP (CPCB REG: PWP-GJ-2024-0089)\n"
            "COMMODITY: POST-CONSUMER RIGID HDPE BOTTLES (PWM CATEGORY I)\n"
            "GROSS WT: 38.450 MT\n"
            "TARE WT:  13.950 MT\n"
            "NET WT:   24.500 MT (PLASTIC SCRAP)\n"
            "E-WAY BILL NO: 2418 9032 1104   EXPIRY: 14-09-2026\n"
            "OPERATOR SIGN: VERIFIED ELECTRONICALLY\n"
        ),
        "expected_category": "Category I (Rigid Plastics)",
        "consignor_gstin": "27AABCB9102K1ZP",
        "net_tonnage_mt": 24.50
    },
    "bhiwandi_eway": {
        "title": "Bhiwandi Logistics Hub GST E-Way Bill (Cat II Flexible LDPE)",
        "document_type": "GST_EWAY_BILL_SYSTEM",
        "raw_text": (
            "GOVERNMENT OF INDIA - GST E-WAY BILL SYSTEM (FORM GST EWB-01)\n"
            "E-Way Bill No: 2719 5543 8812   Generated Date: 18-09-2026\n"
            "From: METRO RETAIL PACKAGING HUB (GSTIN: 07AABCM4421L1ZT) DELHI\n"
            "To: ECO-PROCESSORS PVT LTD (GSTIN: 27AAACE1234F1Z5) BHIWANDI, MAHARASHTRA\n"
            "Vehicle No: MH-04-GP-8821\n"
            "Item: SINGLE-LAYER FLEXIBLE LDPE PACKAGING FILM (CATEGORY II PWM)\n"
            "HSN Code: 39232100   Total Quantity: 18.20 MT\n"
            "Gross Weight: 31.80 MT   Tare: 13.60 MT   Net Weight: 18.20 MT\n"
            "Statutory Declaration: SPCB Form IV Plastic Waste Manifest Accompanied\n"
        ),
        "expected_category": "Category II (Flexible Plastics)",
        "consignor_gstin": "07AABCM4421L1ZT",
        "net_tonnage_mt": 18.20
    },
    "manesar_mlp_bilty": {
        "title": "IMT Manesar Transporter Consignment Bilty (Cat III MLP)",
        "document_type": "TRANSPORTER_CONSIGNMENT_NOTE",
        "raw_text": (
            "NORTHERN CARRIERS FLEET LOGISTICS - IMT MANESAR SECTOR 8\n"
            "LR / BILTY NO: NC-HAR-99120   DATE: 04-10-2026\n"
            "CONSIGNOR: HARYANA SNACK PACKAGERS LTD (GSTIN: 06AABCH8811K1Z2)\n"
            "DESTINATION: CPCB AUTHORIZED CEMENT CO-PROCESSING KILN, RAJASTHAN\n"
            "VEHICLE NO: HR-55-AN-3019\n"
            "MATERIAL: POST-CONSUMER MULTI-LAYERED PLASTIC PACKAGING (CATEGORY III)\n"
            "END-OF-LIFE RECOVERY ROUTE: REFUSE DERIVED FUEL (RDF) / CO-PROCESSING\n"
            "WEIGHBRIDGE CERTIFICATE ATTACHED: NET 31.00 MT (31000 KGS)\n"
            "EPR DISPATCH AUTHORIZATION CODE: CPCB/EPR/MLP/2026/87102\n"
        ),
        "expected_category": "Category III (Multi-Layered Plastics)",
        "consignor_gstin": "06AABCH8811K1Z2",
        "net_tonnage_mt": 31.00
    }
}


def parse_manifest_with_textract(document_bytes: Optional[bytes] = None, raw_text: Optional[str] = None) -> Dict[str, Any]:
    """
    Parses manifest text using Amazon Textract when credentials exist,
    falling back to statutory regex parser for offline/demo reliability.
    """
    extracted_text = raw_text or ""
    provider_used = "Statutory Heuristic Parser (Local)"

    # 1. Attempt AWS Textract invocation if document_bytes provided
    if document_bytes and os.environ.get("AWS_REGION"):
        try:
            import boto3
            client = boto3.client("textract", region_name=os.environ.get("AWS_REGION", "ap-south-1"))
            response = client.detect_document_text(Document={"Bytes": document_bytes})
            blocks = response.get("Blocks", [])
            lines = [b["Text"] for b in blocks if b.get("BlockType") == "LINE"]
            if lines:
                extracted_text = "\n".join(lines)
                provider_used = "Amazon Textract (Live Bedrock / AWS Cloud)"
        except Exception as e:
            logger.warning("Amazon Textract call failed, falling back to heuristic parser: %s", e)

    # 2. Extract structured statutory fields
    net_weight_mt = 0.0
    gross_weight_mt = 0.0
    tare_weight_mt = 0.0

    # Net weight regex (e.g. "NET WT: 24.500 MT", "Total Quantity: 18.20 MT", "NET 31.00 MT")
    net_match = re.search(r"(?:NET\s*(?:WT|WEIGHT)?|TOTAL\s*QUANTITY)[:\s]+([0-9]+\.?[0-9]*)\s*(?:MT|TONS|KGS)?", extracted_text, re.IGNORECASE)
    if net_match:
        val = float(net_match.group(1))
        # If in KGS (> 1000), convert to MT
        net_weight_mt = round(val / 1000.0, 2) if val > 500 else round(val, 2)

    # Gross & Tare
    gross_match = re.search(r"GROSS\s*(?:WT|WEIGHT)?[:\s]+([0-9]+\.?[0-9]*)", extracted_text, re.IGNORECASE)
    if gross_match:
        gross_weight_mt = round(float(gross_match.group(1)), 2)

    tare_match = re.search(r"TARE\s*(?:WT|WEIGHT)?[:\s]+([0-9]+\.?[0-9]*)", extracted_text, re.IGNORECASE)
    if tare_match:
        tare_weight_mt = round(float(tare_match.group(1)), 2)

    if net_weight_mt == 0.0 and gross_weight_mt > 0 and tare_weight_mt > 0:
        net_weight_mt = round(max(0.0, gross_weight_mt - tare_weight_mt), 2)

    # Vehicle No (e.g., GJ-15-XY-4401 or MH-04-GP-8821)
    veh_match = re.search(r"\b([A-Z]{2}[-\s]?[0-9]{1,2}[-\s]?[A-Z]{1,3}[-\s]?[0-9]{4})\b", extracted_text)
    vehicle_no = veh_match.group(1).upper() if veh_match else "NOT_DETECTED"

    # GSTIN (15 characters: 2 digits + 5 letters + 4 digits + 1 letter + 1 digit + Z + 1 alphanumeric)
    gstin_match = re.search(r"\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})\b", extracted_text)
    gstin = gstin_match.group(1) if gstin_match else "UNREGISTERED"

    # E-Way Bill Number (12 digits)
    eway_match = re.search(r"(?:E-?WAY\s*BILL\s*(?:NO)?)[:\s]+([0-9\s]{12,16})", extracted_text, re.IGNORECASE)
    eway_bill_no = eway_match.group(1).replace(" ", "") if eway_match else "NONE"

    # Plastic Category Detection
    category = "Category I (Rigid Plastics)"
    if re.search(r"(?:category\s*iii|mlp|multi-layer)", extracted_text, re.IGNORECASE):
        category = "Category III (Multi-Layered Plastics)"
    elif re.search(r"(?:category\s*ii|flexible|film|ldpe)", extracted_text, re.IGNORECASE):
        category = "Category II (Flexible Plastics)"
    elif re.search(r"(?:category\s*iv|biodegradable|compostable)", extracted_text, re.IGNORECASE):
        category = "Category IV (Biodegradable Plastics)"

    confidence_score = 0.95 if (net_weight_mt > 0 and vehicle_no != "NOT_DETECTED") else 0.70

    return {
        "status": "SUCCESS",
        "provider": provider_used,
        "confidence_score": confidence_score,
        "extracted_manifest": {
            "vehicle_number": vehicle_no,
            "consignor_gstin": gstin,
            "eway_bill_number": eway_bill_no,
            "pwm_category": category,
            "weights": {
                "gross_weight_mt": gross_weight_mt,
                "tare_weight_mt": tare_weight_mt,
                "net_plastic_weight_mt": net_weight_mt
            }
        },
        "audit_bridge_payload": {
            "company_id": f"CPCB-GSTIN-{gstin[:6]}",
            "company_name": f"Entity [{gstin}]",
            "manifest_tonnage_introduced_mt": net_weight_mt,
            "waste_utilized_mt": round(net_weight_mt * 0.85, 2),  # Processed batch yield
            "mandated_threshold_pct": 70.0
        },
        "raw_text_preview": extracted_text[:280] + ("..." if len(extracted_text) > 280 else "")
    }


def get_sample_textract_manifests() -> Dict[str, Any]:
    return SAMPLE_TEXTRACT_MANIFESTS
