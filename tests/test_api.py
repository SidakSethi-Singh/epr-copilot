import logging
import pytest
from app import app, limiter

@pytest.fixture
def client():
    app.config["TESTING"] = True
    limiter.reset()
    with app.test_client() as test_client:
        yield test_client

def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert data["kb_chunks"] >= 16
    assert "is_live" in data
    assert "provider" in data
    assert "rules_version" in data
    assert "verified_on" in data

def test_rules_version_endpoint(client):
    res = client.get("/api/rules-version")
    assert res.status_code == 200
    data = res.get_json()
    assert "ruleset_version" in data
    assert "verified_on" in data
    assert "status_summary" in data
    assert "needs_verify" in data["status_summary"]

def test_status_endpoint(client):
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.get_json()
    assert "is_live" in data
    assert "provider" in data
    assert "label" in data

def test_ask_endpoint_schema_and_response(client):
    res = client.post("/api/ask", json={"question": "What is Category I plastic packaging?", "as_of": "2026-10-10"})
    assert res.status_code == 200
    data = res.get_json()
    required_keys = [
        "question",
        "answer",
        "citations",
        "mode",
        "verifier",
        "rules_version",
        "verified_on",
        "disclaimer",
    ]
    for key in required_keys:
        assert key in data
    assert len(data["citations"]) > 0

def test_ask_endpoint_validation_errors(client):
    res_empty = client.post("/api/ask", json={"question": ""})
    assert res_empty.status_code == 400
    assert "required" in res_empty.get_json()["error"]
    assert res_empty.get_json()["code"] == 400

    res_short = client.post("/api/ask", json={"question": "hi"})
    assert res_short.status_code == 400
    assert "at least 3 characters" in res_short.get_json()["error"]
    assert res_short.get_json()["code"] == 400

    res_long = client.post("/api/ask", json={"question": "a" * 1001})
    assert res_long.status_code == 400
    assert "must not exceed 1000 characters" in res_long.get_json()["error"]
    assert res_long.get_json()["code"] == 400

    res_non_dict = client.post("/api/ask", data="invalid non json", content_type="application/json")
    assert res_non_dict.status_code == 400

def test_calculate_endpoint(client):
    res = client.post("/api/calculate", json={
        "pibo_type": "Brand Owner",
        "fiscal_year": "2026-27",
        "tonnages": {"cat_1": 100, "cat_2": 200},
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["total_introduced_packaging_mt"] == 300.0
    assert data["potential_ec_penalty_exposure_inr"] > 0
    assert "_meta" in data
    assert "rules_version" in data["_meta"]
    assert "verified_on" in data["_meta"]
    assert "disclaimer" in data["_meta"]

def test_target_endpoint(client):
    res = client.get("/api/target/2026-27")
    assert res.status_code == 200
    data = res.get_json()
    assert data["found"] is True
    assert data["recycling_targets_pct"]["cat_1"] == 70
    assert "rules_version" in data
    assert "verified_on" in data

def test_deadline_endpoint(client):
    res = client.get("/api/deadline")
    assert res.status_code == 200
    data = res.get_json()
    assert "statutory_date" in data
    assert "deadlines" in data
    assert len(data["deadlines"]) >= 2
    for d in data["deadlines"]:
        assert "fy" in d
        assert "entity" in d
        assert "date" in d
        assert "source_id" in d

def test_kb_endpoint(client):
    res = client.get("/api/kb")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) >= 16
    for item in data:
        assert "id" in item
        assert "title" in item
        assert "text_preview" in item


def test_audit_samples_endpoint(client):
    res = client.get("/api/audit/samples")
    assert res.status_code == 200
    data = res.get_json()
    assert "fmcg_compliant" in data
    assert "retail_warning" in data
    assert "msme_penalized" in data


def test_audit_evaluate_endpoint_compliant(client):
    res = client.post("/api/audit/evaluate", json={
        "company_id": "TEST-001",
        "company_name": "Test Clean Foods Ltd",
        "manifest_tonnage_introduced_mt": 1000.0,
        "waste_utilized_mt": 800.0,
        "mandated_threshold_pct": 70.0
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["compliance_status"] == "COMPLIANT"
    assert data["metrics"]["actual_utilization_pct"] == 80.0
    assert data["financial_resolution"]["net_credits_earned"] == 100.0
    assert data["financial_resolution"]["green_credit_monetary_value_inr"] == 250000.0
    assert "statutory_guideline_summary" in data


def test_audit_evaluate_endpoint_penalized(client):
    res = client.post("/api/audit/evaluate", json={
        "company_id": "TEST-002",
        "company_name": "Defaulting Packagers Ltd",
        "manifest_tonnage_introduced_mt": 1000.0,
        "waste_utilized_mt": 200.0,
        "mandated_threshold_pct": 70.0,
        "consecutive_default_year": 3
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["compliance_status"] == "PENALIZED"
    assert data["financial_resolution"]["penalty_tier"] == "TIER_3_SEVERE_SUSPENSION"
    assert data["financial_resolution"]["fine_levied_inr"] > 0
    assert data["suspension_notice_payload"] is not None
    assert "notice_id" in data["suspension_notice_payload"]


def test_payload_too_large_413(client):
    large_payload = {"question": "x" * (65 * 1024)}
    res = client.post("/api/ask", json=large_payload)
    assert res.status_code in [400, 413]
    assert res.get_json()["code"] in [400, 413]


def test_rate_limiting_429(client):
    limiter.reset()
    responses = [
        client.post("/api/ask", json={"question": f"Question number {i}"})
        for i in range(12)
    ]
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes
    rate_limited_response = next(r for r in responses if r.status_code == 429)
    assert rate_limited_response.get_json()["code"] == 429
    assert "Retry-After" in rate_limited_response.headers


def test_no_question_text_in_logs(client, caplog):
    secret_text = "SECRET_TOKEN_FIND_ME_998877"
    with caplog.at_level(logging.INFO, logger="epr_copilot"):
        res = client.post("/api/ask", json={"question": f"Tell me about {secret_text}"})
        assert res.status_code == 200
    for record in caplog.records:
        assert secret_text not in record.message


def test_textract_samples_and_parse_endpoints(client):
    res = client.get("/api/textract/samples")
    assert res.status_code == 200
    data = res.get_json()
    assert "vapi_weighbridge" in data

    vapi_text = data["vapi_weighbridge"]["raw_text"]
    parse_res = client.post("/api/textract/parse", json={"raw_text": vapi_text})
    assert parse_res.status_code == 200
    parse_data = parse_res.get_json()
    assert parse_data["status"] == "SUCCESS"
    assert parse_data["extracted_manifest"]["vehicle_number"] == "GJ-15-XY-4401"


def test_vault_records_endpoint(client):
    res = client.get("/api/vault/records")
    assert res.status_code == 200
    records = res.get_json()
    assert isinstance(records, list)
    assert len(records) > 0
    assert "integrity_sha256" in records[0]


