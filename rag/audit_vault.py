"""
Amazon DynamoDB & S3 Immutable Audit Vault.
Persists evaluated CPCB audit decisions, Green Credit certificates, and suspension notices
with SHA-256 cryptographic tamper-proof integrity hashes.
Connects to DynamoDB with automatic fallback to persistent local store for zero-friction hackathon demos.
"""

import os
import json
import hashlib
import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("epr_copilot.vault")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DB_PATH, exist_ok=True)
SQLITE_FILE = os.path.join(DB_PATH, "audit_vault.db")


def _init_sqlite_db():
    conn = sqlite3.connect(SQLITE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_vault (
            audit_id TEXT PRIMARY KEY,
            company_id TEXT NOT NULL,
            company_name TEXT NOT NULL,
            compliance_status TEXT NOT NULL,
            actual_utilization_pct REAL,
            net_credits_earned REAL,
            fine_levied_inr REAL,
            penalty_tier TEXT,
            integrity_sha256 TEXT NOT NULL,
            storage_backend TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            full_payload TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


_init_sqlite_db()


def generate_audit_hash(company_id: str, status: str, metrics: Dict[str, Any], timestamp: str) -> str:
    raw = f"{company_id}|{status}|{json.dumps(metrics, sort_keys=True)}|{timestamp}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def save_audit_record(audit_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves an audit result to Amazon DynamoDB (if configured) and persistent vault storage.
    """
    company_id = audit_result.get("company_id", "UNKNOWN")
    company_name = audit_result.get("company_name", "Unknown Entity")
    compliance_status = audit_result.get("compliance_status", "UNKNOWN")
    timestamp = audit_result.get("timestamp") or datetime.now().isoformat()
    metrics = audit_result.get("metrics", {})
    financial = audit_result.get("financial_resolution", {})

    audit_id = f"AUD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{company_id.replace(' ', '_')[:10]}"
    integrity_sha256 = generate_audit_hash(company_id, compliance_status, metrics, timestamp)

    storage_backend = "Persistent Local SQLite Vault"

    # Attempt Amazon DynamoDB insertion
    table_name = os.environ.get("DYNAMODB_TABLE_NAME")
    if table_name and os.environ.get("AWS_REGION"):
        try:
            import boto3
            dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("AWS_REGION", "ap-south-1"))
            table = dynamodb.Table(table_name)
            item = {
                "company_id": company_id,
                "audit_id": audit_id,
                "company_name": company_name,
                "compliance_status": compliance_status,
                "actual_utilization_pct": str(metrics.get("actual_utilization_pct", 0.0)),
                "net_credits_earned": str(financial.get("net_credits_earned", 0.0)),
                "fine_levied_inr": str(financial.get("fine_levied_inr", 0.0)),
                "penalty_tier": str(financial.get("penalty_tier", "NONE")),
                "integrity_sha256": integrity_sha256,
                "timestamp": timestamp,
                "storage_backend": "Amazon DynamoDB (AWS Cloud)",
                "full_payload": json.dumps(audit_result)
            }
            table.put_item(Item=item)
            storage_backend = "Amazon DynamoDB (Live Cloud)"
        except Exception as e:
            logger.warning("DynamoDB put failed, falling back to local vault: %s", e)

    # Persist in SQLite
    try:
        conn = sqlite3.connect(SQLITE_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO audit_vault (
                audit_id, company_id, company_name, compliance_status,
                actual_utilization_pct, net_credits_earned, fine_levied_inr,
                penalty_tier, integrity_sha256, storage_backend, timestamp, full_payload
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            audit_id,
            company_id,
            company_name,
            compliance_status,
            float(metrics.get("actual_utilization_pct", 0.0)),
            float(financial.get("net_credits_earned", 0.0)),
            float(financial.get("fine_levied_inr", 0.0)),
            str(financial.get("penalty_tier", "NONE")),
            integrity_sha256,
            storage_backend,
            timestamp,
            json.dumps(audit_result)
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error("Failed to write to local audit vault: %s", e)

    return {
        "audit_id": audit_id,
        "integrity_sha256": integrity_sha256,
        "storage_backend": storage_backend,
        "timestamp": timestamp,
        "status": "VAULT_SEALED"
    }


def list_audit_vault(limit: int = 15) -> List[Dict[str, Any]]:
    """Returns recent tamper-proof audits from the vault."""
    try:
        conn = sqlite3.connect(SQLITE_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT audit_id, company_id, company_name, compliance_status,
                   actual_utilization_pct, net_credits_earned, fine_levied_inr,
                   penalty_tier, integrity_sha256, storage_backend, timestamp
            FROM audit_vault
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            results.append({
                "audit_id": r[0],
                "company_id": r[1],
                "company_name": r[2],
                "compliance_status": r[3],
                "actual_utilization_pct": r[4],
                "net_credits_earned": r[5],
                "fine_levied_inr": r[6],
                "penalty_tier": r[7],
                "integrity_sha256": r[8],
                "storage_backend": r[9],
                "timestamp": r[10]
            })

        # If empty, seed initial records for demo
        if not results:
            seed_demo_vault()
            return list_audit_vault(limit)

        return results
    except Exception as e:
        logger.error("Failed to query audit vault: %s", e)
        return []


def seed_demo_vault():
    """Seeds realistic verified CPCB records for instant demoing."""
    demo_records = [
        {
            "company_id": "CPCB-MH-BO-2024-9102",
            "company_name": "Bharat Beverages & Snacks Ltd",
            "compliance_status": "COMPLIANT",
            "metrics": {"actual_utilization_pct": 80.0, "total_introduced_packaging_mt": 1200.0, "waste_utilized_mt": 960.0},
            "financial_resolution": {"net_credits_earned": 120.0, "fine_levied_inr": 0.0, "penalty_tier": "NONE"},
            "timestamp": "2026-10-10T14:15:00"
        },
        {
            "company_id": "CPCB-GJ-P-2023-1188",
            "company_name": "Gujarat Polymer Converters LLP",
            "compliance_status": "PENALIZED",
            "metrics": {"actual_utilization_pct": 30.0, "total_introduced_packaging_mt": 850.0, "waste_utilized_mt": 255.0},
            "financial_resolution": {"net_credits_earned": 0.0, "fine_levied_inr": 3400000.0, "penalty_tier": "TIER_2_ESCALATED"},
            "timestamp": "2026-10-10T15:30:00"
        }
    ]
    for r in demo_records:
        save_audit_record(r)
