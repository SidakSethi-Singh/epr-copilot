import hashlib
import logging
import os
import time
from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

load_dotenv()

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
from rag.audit_engine import evaluate_manifest_compliance, get_sample_manifests
from rag.rules import get_ruleset_version, get_verified_on, get_rules_status_summary


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
    default_limits=[],
)

@app.errorhandler(400)
def handle_bad_request(err):
    desc = getattr(err, "description", "Bad Request")
    return jsonify({"error": str(desc), "code": 400}), 400

@app.errorhandler(404)
def handle_not_found(err):
    return jsonify({"error": "Not Found", "code": 404}), 404

@app.errorhandler(413)
def handle_payload_too_large(err):
    return jsonify({"error": "Payload Too Large", "code": 413}), 413

@app.errorhandler(429)
def handle_rate_limit(err):
    response = jsonify({"error": "Rate limit exceeded", "code": 429})
    response.status_code = 429
    retry_after = getattr(err, "retry_after", 60)
    response.headers["Retry-After"] = str(retry_after)
    return response

@app.errorhandler(500)
def handle_internal_server_error(err):
    return jsonify({"error": "Internal Server Error", "code": 500}), 500

@app.route("/health")
def health():
    status = get_llm_status()
    return jsonify({
        "status": "ok",
        "kb_chunks": len(KNOWLEDGE_BASE),
        "is_live": status["is_live"],
        "provider": status["provider"],
        "rules_version": get_ruleset_version(),
        "verified_on": get_verified_on(),
    }), 200

@app.route("/")
def index():
    status = get_llm_status()
    return render_template(
        "index.html",
        live_mode=status["is_live"],
        provider_label=status["label"],
        kb_size=len(KNOWLEDGE_BASE),
    )

@app.route("/api/status")
def api_status():
    return jsonify(get_llm_status())

@app.route("/api/rules-version")
def api_rules_version():
    return jsonify({
        "ruleset_version": get_ruleset_version(),
        "verified_on": get_verified_on(),
        "status_summary": get_rules_status_summary(),
    })

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


@app.route("/api/audit/samples")
def api_audit_samples():
    """Returns sample manifests (Compliant, Warning, Penalized) for testing."""
    return jsonify(get_sample_manifests())


@app.route("/api/audit/evaluate", methods=["POST"])
def api_audit_evaluate():
    """
    Compliance & Penalty Resolution Engine:
    Evaluates manifest waste utilization against statutory thresholds.
    Calculates Green Credits or tier-based penalties + formal suspension notices.
    """
    data = request.get_json(force=True) or {}
    company_id = data.get("company_id", "CPCB-SAMPLE-01")
    company_name = data.get("company_name", "Enterprise Packaging Corp")
    try:
        manifest_tonnage = float(data.get("manifest_tonnage_introduced_mt", 100.0) or 0.0)
        waste_utilized = float(data.get("waste_utilized_mt", 70.0) or 0.0)
        mandated_pct = float(data.get("mandated_threshold_pct", 70.0) or 70.0)
        consecutive_years = int(data.get("consecutive_default_year", 1) or 1)
    except (ValueError, TypeError):
        manifest_tonnage, waste_utilized, mandated_pct, consecutive_years = 100.0, 70.0, 70.0, 1

    fiscal_year = data.get("fiscal_year", "2026-27")

    result = evaluate_manifest_compliance(
        company_id=company_id,
        company_name=company_name,
        manifest_tonnage_introduced_mt=manifest_tonnage,
        waste_utilized_mt=waste_utilized,
        mandated_threshold_pct=mandated_pct,
        fiscal_year=fiscal_year,
        consecutive_default_year=consecutive_years
    )
    return jsonify(result)


@app.route("/api/ask", methods=["POST"])
@limiter.limit("10 per minute")
def api_ask():
    data = request.get_json(force=True, silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Malformed JSON payload", "code": 400}), 400

    raw_question = data.get("question")
    if raw_question is None or not isinstance(raw_question, str):
        return jsonify({"error": "question is required", "code": 400}), 400

    question = raw_question.strip()
    if not question:
        return jsonify({"error": "question is required", "code": 400}), 400
    if len(question) < 3:
        return jsonify({"error": "question must be at least 3 characters", "code": 400}), 400
    if len(question) > 1000:
        return jsonify({"error": "question must not exceed 1000 characters", "code": 400}), 400

    as_of = data.get("as_of")
    start_t = time.time()
    result = ask(question=question, as_of=as_of)
    elapsed_ms = round((time.time() - start_t) * 1000, 1)

    question_hash = hashlib.sha256(question.encode("utf-8")).hexdigest()[:12]
    is_abstention = "insufficient" in result.get("answer", "").lower()
    verifier_passed = result.get("verifier", {}).get("verified", False)

    logger.info(
        "POST /api/ask - q_hash=%s q_len=%d citations=%d abstention=%s verifier_ok=%s mode=%s latency=%.1fms",
        question_hash,
        len(question),
        len(result.get("citations", [])),
        is_abstention,
        verifier_passed,
        result.get("mode", "unknown"),
        elapsed_ms,
    )
    return jsonify(result), 200

@app.route("/api/calculate", methods=["POST"])
@limiter.limit("60 per minute")
def api_calculate():
    data = request.get_json(force=True, silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Malformed JSON payload", "code": 400}), 400

    pibo_type = data.get("pibo_type", "Brand Owner")
    fiscal_year = data.get("fiscal_year", "2026-27")
    tonnages = data.get("tonnages", {})
    prior_year_tonnages = data.get("prior_year_tonnages")
    plastic_layer_weights = data.get("plastic_layer_weights")
    plastic_layer_weight_mt = data.get("plastic_layer_weight_mt")
    consecutive_year = data.get("consecutive_year_of_shortfall", 1)
    shortfalls = data.get("shortfalls")
    shortfall_mt = data.get("shortfall_mt")
    cert_price_override = data.get("cert_price_override_inr_per_mt")
    epr_target_basis = data.get("epr_target_basis")
    as_of = data.get("as_of")

    result = calculate_liability(
        pibo_type=pibo_type,
        fiscal_year=fiscal_year,
        tonnages=tonnages,
        prior_year_tonnages=prior_year_tonnages,
        plastic_layer_weights=plastic_layer_weights,
        plastic_layer_weight_mt=plastic_layer_weight_mt,
        consecutive_year_of_shortfall=consecutive_year,
        shortfalls=shortfalls,
        shortfall_mt=shortfall_mt,
        cert_price_override_inr_per_mt=cert_price_override,
        epr_target_basis=epr_target_basis,
        as_of=as_of,
    )

    logger.info(
        "POST /api/calculate - pibo_type=%s fy=%s total_mt=%.1f",
        pibo_type,
        fiscal_year,
        result.get("total_introduced_packaging_mt", 0.0),
    )
    return jsonify(result), 200

@app.route("/api/target/<fiscal_year>")
def api_target(fiscal_year):
    return jsonify(get_target(fiscal_year)), 200

@app.route("/api/deadline")
def api_deadline():
    return jsonify(get_annual_return_deadline()), 200

@app.route("/api/kb")
def api_kb():
    return jsonify([
        {k: v for k, v in chunk.items() if k != "text"} | {"text_preview": chunk["text"][:140] + "..."}
        for chunk in KNOWLEDGE_BASE
    ]), 200

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=debug, host="0.0.0.0", port=port)

