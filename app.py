"""
EPR Compliance Copilot - Server & API

Run with:
    .venv/bin/python app.py

Then open http://localhost:5000
"""

import os
import time
import logging
from collections import defaultdict
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
from rag.calculator import get_target, get_annual_return_deadline, calculate_liability, get_rules_version
from rag.knowledge_base import KNOWLEDGE_BASE
from rag.parser import parse_packaging_text, get_sample_invoices
from rag.validator import validate_packaging_artwork, get_sample_artworks
from rag.marketplace import get_marketplace_data, optimize_procurement

app = Flask(__name__)
# 64 KB request ceiling to prevent unbounded payload DOS attacks (IMP-003)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024

# Simple in-memory rate limiter: max 15 requests per minute per IP on /api/ask (G17)
RATE_LIMIT_REQUESTS = 15
RATE_LIMIT_WINDOW_SEC = 60
_ip_request_history = defaultdict(list)


def _is_rate_limited(client_ip: str) -> bool:
    """Checks if client IP has exceeded the sliding window rate limit."""
    if app.config.get("TESTING"):
        return False
    now = time.time()
    history = _ip_request_history[client_ip]
    # Prune old timestamps
    _ip_request_history[client_ip] = [t for t in history if now - t < RATE_LIMIT_WINDOW_SEC]
    if len(_ip_request_history[client_ip]) >= RATE_LIMIT_REQUESTS:
        return True
    _ip_request_history[client_ip].append(now)
    return False


@app.route("/health")
def health():
    """Liveness & readiness probe endpoint with ruleset verification metadata."""
    status = get_llm_status()
    rules_meta = get_rules_version()
    return jsonify({
        "status": "ok",
        "kb_chunks": len(KNOWLEDGE_BASE),
        "is_live": status["is_live"],
        "provider": status["provider"],
        "rules_version": rules_meta["ruleset_version"],
        "rules_verified_on": rules_meta["verified_on"],
        "_meta": rules_meta,
    }), 200


@app.route("/")
def index():
    status = get_llm_status()
    rules_meta = get_rules_version()
    return render_template(
        "index.html",
        live_mode=status["is_live"],
        provider_label=status["label"],
        kb_size=len(KNOWLEDGE_BASE),
        rules_meta=rules_meta,
    )


@app.route("/api/status")
def api_status():
    return jsonify(get_llm_status() | {"_meta": get_rules_version()})


@app.route("/api/rules-version")
def api_rules_version():
    """Exposes current single-source-of-truth ruleset version and verification date."""
    return jsonify(get_rules_version())


COMPLIANCE_PROFILES = {
    "Brand Owner": {
        "title": "Brand Owner (BO)",
        "description": "Entity selling products under a registered brand label.",
        "applicable_rules": [
            "CPCB registration before placing packaging in the market",
            "Category I–IV annual recycling targets and recycled-content mandates",
            "Form-VII annual return by the applicable statutory deadline",
        ],
        "exemptions": "Confirm any MSME exemption against the current CPCB rules before relying on it.",
        "penalties": "Environmental Compensation may escalate from ₹5,000 to ₹20,000/MT for continuing default.",
    },
    "Producer": {
        "title": "Producer (P)",
        "description": "Manufacturer or importer of carry bags, plastic sheets, or multilayered packaging.",
        "applicable_rules": ["Common EPR Portal registration", "Audited virgin-polymer records", "Quarterly and annual traceability records"],
        "exemptions": "Obligations depend on the registered entity and supply-chain allocation.",
        "penalties": "Non-compliance can trigger Environmental Compensation and regulatory action.",
    },
    "Importer": {
        "title": "Importer (I)",
        "description": "Importer of plastic packaging or products packaged in plastic.",
        "applicable_rules": ["Valid CPCB EPR registration", "Category-wise imported-volume accounting", "Form-VII filing with bill-of-entry records"],
        "exemptions": "Confirm scope and volume treatment with current CPCB guidance.",
        "penalties": "Non-compliance may affect clearance and incur Environmental Compensation.",
    },
    "Seller": {
        "title": "Seller of Raw Virgin Polymers",
        "description": "Entity manufacturing or trading raw plastic resin.",
        "applicable_rules": ["Portal onboarding", "Buyer traceability", "Quarterly sales-data reporting where applicable"],
        "exemptions": "No blanket exemption should be assumed.",
        "penalties": "Regulatory action may include portal restrictions and prosecution.",
    },
}


@app.route("/api/compliance-check/<entity>")
def api_compliance_check(entity):
    return jsonify(COMPLIANCE_PROFILES.get(entity, COMPLIANCE_PROFILES["Brand Owner"]))


@app.route("/api/samples/invoices")
def api_samples_invoices():
    return jsonify(get_sample_invoices())


@app.route("/api/parse_invoice", methods=["POST"])
def api_parse_invoice():
    data = request.get_json(force=True) or {}
    return jsonify(parse_packaging_text(data.get("invoice_text", "")))


@app.route("/api/samples/artworks")
def api_samples_artworks():
    return jsonify(get_sample_artworks())


@app.route("/api/validate_artwork", methods=["POST"])
def api_validate_artwork():
    data = request.get_json(force=True) or {}
    return jsonify(validate_packaging_artwork(data.get("artwork_text", "")))


@app.route("/api/marketplace")
def api_marketplace():
    return jsonify(get_marketplace_data())


@app.route("/api/marketplace/optimize", methods=["POST"])
def api_marketplace_optimize():
    data = request.get_json(force=True) or {}
    return jsonify(optimize_procurement(data.get("obligations", {})))


@app.route("/api/ask", methods=["POST"])
def api_ask():
    client_ip = request.remote_addr or "127.0.0.1"
    if _is_rate_limited(client_ip):
        logger.warning("Rate limit exceeded for IP %s on /api/ask", client_ip)
        return jsonify({
            "error": "Rate limit exceeded. Please wait a minute before asking more questions.",
            "_meta": get_rules_version(),
        }), 429

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
        "POST /api/ask - question_len=%d citations=%d mode=%s verified=%s latency=%.1fms",
        len(question),
        len(result.get("citations", [])),
        result.get("mode", "unknown"),
        result.get("verification", {}).get("status", "unknown"),
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
        "POST /api/calculate - pibo_type=%s fy=%s total_mt=%.1f wte_mwh=%.1f",
        pibo_type,
        fiscal_year,
        result.get("total_introduced_packaging_mt", 0.0),
        result.get("energy_recovery", {}).get("waste_to_energy_electrical_mwh", 0.0),
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
    """Expose the knowledge base so users can inspect exact citations, metadata, and confidence."""
    return jsonify([
        {k: v for k, v in chunk.items() if k != "text"} | {"text_preview": chunk["text"][:140] + "..."}
        for chunk in KNOWLEDGE_BASE
    ])


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=debug, host="0.0.0.0", port=port)
