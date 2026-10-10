"""
EPR Compliance Copilot - Server & API

Run with:
    .venv/bin/python app.py

Then open http://localhost:5000
"""

import os
import time
import logging
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

# Structured logging configuration (IMP-008)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("epr_copilot")

from rag.chain import ask, get_llm_status
from rag.calculator import get_target, get_annual_return_deadline, calculate_liability
from rag.knowledge_base import KNOWLEDGE_BASE
from rag.parser import parse_packaging_text, get_sample_invoices
from rag.validator import validate_packaging_artwork, get_sample_artworks
from rag.marketplace import get_marketplace_data, optimize_procurement
from rag.leaderboard import compute_leaderboard
from rag.circular_economy import evaluate_road_reuse

app = Flask(__name__)
# 64 KB request ceiling to prevent unbounded payload DOS attacks (IMP-003)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024


@app.route("/health")
def health():
    """Liveness & readiness probe endpoint (IMP-010)."""
    status = get_llm_status()
    return jsonify({
        "status": "ok",
        "kb_chunks": len(KNOWLEDGE_BASE),
        "is_live": status["is_live"],
        "provider": status["provider"],
        "rules_version": "2026-10-10.1",
        "verified_on": "10 Oct 2026",
    }), 200


@app.route("/")
def index():
    status = get_llm_status()
    return render_template(
        "index.html",
        live_mode=status["is_live"],
        provider_label=status["label"],
        kb_size=len(KNOWLEDGE_BASE),
        rules_version="2026-10-10.1",
        verified_on="10 Oct 2026",
    )


@app.route("/api/status")
def api_status():
    return jsonify(get_llm_status())


@app.route("/api/rules-version")
def api_rules_version():
    """Single source of truth versioning endpoint (Person 3 / Hour 1)."""
    return jsonify({
        "rules_version": "2026-10-10.1",
        "verified_on": "10 Oct 2026",
        "verified_by": "Gazette & CPCB Statutory Review Team",
        "cpcb_schedule": "Schedule II of Plastic Waste Management Rules, 2016 (Amended)",
        "source": "MoEFCC G.S.R. 133(E), 2022/2024/2026 Amendments"
    })


COMPLIANCE_PROFILES = {
    "Brand Owner": {
        "title": "Brand Owner (BO)",
        "description": "Any person or company who sells any commodity under a registered brand label.",
        "applicable_rules": [
            "Mandatory CPCB Registration before placing packaging in market",
            "Category I–IV Annual Recycling Targets (50% to 80% ramp)",
            "Mandatory Recycled Content in packaging (Rule 13 mandate)",
            "Rule 11 Labeling: CPCB Reg No, Polymer Resin Symbol, QR Code",
            "Filing Annual Return Form-VII by statutory deadline (June 30)",
            "Mandatory procurement of EPR Certificates from verified PWPs"
        ],
        "exemptions": "Micro and Small Enterprises (MSEs) under MSMED Act 2006 are exempt from EPR targets (pre-consumer reporting only).",
        "penalties": "Environmental Compensation (₹5,000 to ₹20,000/MT escalating) + Section 15 EPA 1986 prosecution."
    },
    "Producer": {
        "title": "Producer (P)",
        "description": "Persons engaged in manufacture or import of carry bags or multi-layered packaging or plastic sheets.",
        "applicable_rules": [
            "Mandatory registration on Common EPR Portal",
            "Maintain audited records of virgin polymer purchased & supplied",
            "Mandatory 120 micron minimum thickness on carry bags / sheets",
            "Sale restricted only to registered PIBOs and authorized converters",
            "Quarterly and Annual return filings with batch traceability"
        ],
        "exemptions": "Exempt from recycling target on quantities supplied to registered Brand Owners who assume liability.",
        "penalties": "Closure of manufacturing unit, power/water disconnection, and EC forfeiture."
    },
    "Importer": {
        "title": "Importer (I)",
        "description": "Persons who import plastic packaging products or products with plastic packaging into India.",
        "applicable_rules": [
            "Customs port clearance tied to valid CPCB EPR Registration Certificate",
            "100% liability on all imported packaging weight across Cat I-IV",
            "Mandatory certificate procurement for equivalent imported volume",
            "Annual filing of Form-VII with bill of entry details"
        ],
        "exemptions": "Zero exemptions on imported packaging volume.",
        "penalties": "Customs detention of consignments + EC penalties."
    },
    "Seller": {
        "title": "Seller of Raw Virgin Polymers",
        "description": "Entities manufacturing or trading raw plastic resins (introduced in 2026 amendment).",
        "applicable_rules": [
            "Mandatory portal onboarding & raw resin traceability reporting",
            "Prohibited from selling virgin polymer to unregistered PIBOs",
            "Submission of quarterly sales data mapped to buyer GSTIN"
        ],
        "exemptions": "No recycling certificate purchase mandate directly, but strict supply KYC obligation.",
        "penalties": "Blacklisting on CPCB portal and prosecution under EPA 1986."
    }
}


@app.route("/api/compliance-check/<entity>")
def api_compliance_check(entity):
    profile = COMPLIANCE_PROFILES.get(entity) or COMPLIANCE_PROFILES["Brand Owner"]
    return jsonify(profile)


@app.route("/api/samples/invoices")
def api_samples_invoices():
    return jsonify(get_sample_invoices())


@app.route("/api/parse_invoice", methods=["POST"])
def api_parse_invoice():
    data = request.get_json(force=True) or {}
    text = data.get("invoice_text", "")
    result = parse_packaging_text(text)
    return jsonify(result)


@app.route("/api/samples/artworks")
def api_samples_artworks():
    return jsonify(get_sample_artworks())


@app.route("/api/validate_artwork", methods=["POST"])
def api_validate_artwork():
    data = request.get_json(force=True) or {}
    text = data.get("artwork_text", "")
    result = validate_packaging_artwork(text)
    return jsonify(result)


@app.route("/api/marketplace")
def api_marketplace():
    return jsonify(get_marketplace_data())


@app.route("/api/marketplace/optimize", methods=["POST"])
def api_marketplace_optimize():
    data = request.get_json(force=True) or {}
    obligations = data.get("obligations", {})
    result = optimize_procurement(obligations)
    return jsonify(result)


@app.route("/api/leaderboard")
def api_leaderboard():
    return jsonify(compute_leaderboard())


@app.route("/api/road-reuse/evaluate", methods=["POST"])
def api_road_reuse_evaluate():
    data = request.get_json(force=True) or {}
    polymer = data.get("polymer", "ldpe")
    try:
        tonnage = float(data.get("tonnage", 0.0) or 0.0)
    except (ValueError, TypeError):
        tonnage = 0.0
    result = evaluate_road_reuse(polymer, tonnage)
    return jsonify(result)


@app.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.get_json(force=True) or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400
    if len(question) < 3:
        return jsonify({"error": "question must be at least 3 characters"}), 400
    if len(question) > 1000:
        return jsonify({"error": "question must not exceed 1000 characters"}), 400

    start_t = time.time()
    result = ask(question)
    elapsed_ms = round((time.time() - start_t) * 1000, 1)

    logger.info(
        "POST /api/ask - question_len=%d citations=%d mode=%s latency=%.1fms",
        len(question),
        len(result.get("citations", [])),
        result.get("mode", "unknown"),
        elapsed_ms,
    )
    return jsonify(result)


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    data = request.get_json(force=True) or {}
    pibo_type = data.get("pibo_type", "Brand Owner")
    fiscal_year = data.get("fiscal_year", "2026-27")
    tonnages = data.get("tonnages", {})

    result = calculate_liability(
        pibo_type=pibo_type,
        fiscal_year=fiscal_year,
        tonnages=tonnages,
    )
    logger.info(
        "POST /api/calculate - pibo_type=%s fy=%s total_mt=%.1f",
        pibo_type,
        fiscal_year,
        result.get("total_introduced_packaging_mt", 0.0),
    )
    return jsonify(result)


@app.route("/api/target/<fiscal_year>")
def api_target(fiscal_year):
    return jsonify(get_target(fiscal_year))


@app.route("/api/deadline")
def api_deadline():
    return jsonify(get_annual_return_deadline())


@app.route("/api/kb")
def api_kb():
    """Expose the knowledge base so users can inspect exact citations and confidence."""
    return jsonify([
        {k: v for k, v in chunk.items() if k != "text"} | {"text_preview": chunk["text"][:140] + "..."}
        for chunk in KNOWLEDGE_BASE
    ])


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=debug, port=port)
