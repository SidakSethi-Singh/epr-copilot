import pytest
from rag.textract_manifest import parse_manifest_with_textract, get_sample_textract_manifests
from rag.audit_vault import save_audit_record, list_audit_vault, generate_audit_hash


def test_sample_textract_manifests():
    samples = get_sample_textract_manifests()
    assert "vapi_weighbridge" in samples
    assert "bhiwandi_eway" in samples
    assert "manesar_mlp_bilty" in samples


def test_parse_vapi_weighbridge():
    samples = get_sample_textract_manifests()
    vapi_text = samples["vapi_weighbridge"]["raw_text"]
    parsed = parse_manifest_with_textract(raw_text=vapi_text)

    assert parsed["status"] == "SUCCESS"
    assert parsed["confidence_score"] >= 0.90
    extracted = parsed["extracted_manifest"]
    assert extracted["vehicle_number"] == "GJ-15-XY-4401"
    assert extracted["consignor_gstin"] == "27AABCB9102K1ZP"
    assert extracted["weights"]["net_plastic_weight_mt"] == 24.50
    assert extracted["pwm_category"] == "Category I (Rigid Plastics)"

    # Audit bridge payload
    bridge = parsed["audit_bridge_payload"]
    assert bridge["manifest_tonnage_introduced_mt"] == 24.50


def test_parse_bhiwandi_eway():
    samples = get_sample_textract_manifests()
    bhiwandi_text = samples["bhiwandi_eway"]["raw_text"]
    parsed = parse_manifest_with_textract(raw_text=bhiwandi_text)

    assert parsed["status"] == "SUCCESS"
    extracted = parsed["extracted_manifest"]
    assert extracted["vehicle_number"] == "MH-04-GP-8821"
    assert extracted["weights"]["net_plastic_weight_mt"] == 18.20
    assert extracted["pwm_category"] == "Category II (Flexible Plastics)"


from datetime import datetime


def test_audit_vault_integrity_and_persistence():
    audit_payload = {
        "company_id": "TEST-VAULT-CO",
        "company_name": "Test Vault Entity",
        "compliance_status": "COMPLIANT",
        "metrics": {"actual_utilization_pct": 75.0},
        "financial_resolution": {"net_credits_earned": 50.0, "fine_levied_inr": 0.0},
        "timestamp": datetime.now().isoformat()
    }
    receipt = save_audit_record(audit_payload)
    assert "audit_id" in receipt
    assert "integrity_sha256" in receipt
    assert receipt["status"] == "VAULT_SEALED"

    records = list_audit_vault(limit=50)
    assert len(records) > 0
    found = any(r["company_id"] == "TEST-VAULT-CO" for r in records)
    assert found is True
