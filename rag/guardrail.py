import os
import boto3
from typing import Any, Optional

def is_guardrail_enabled() -> bool:
    guardrail_id = os.environ.get("GUARDRAIL_ID")
    guardrail_version = os.environ.get("GUARDRAIL_VERSION")
    return bool(guardrail_id and guardrail_version)

def grounded(
    context: str,
    question: str,
    answer: str,
    client: Optional[Any] = None,
) -> bool:
    guardrail_id = os.environ.get("GUARDRAIL_ID")
    guardrail_version = os.environ.get("GUARDRAIL_VERSION")
    if not (guardrail_id and guardrail_version):
        return True

    region_name = os.environ.get("AWS_REGION", "ap-south-1")
    try:
        bedrock_client = client or boto3.client("bedrock-runtime", region_name=region_name)
        response = bedrock_client.apply_guardrail(
            guardrailIdentifier=guardrail_id,
            guardrailVersion=guardrail_version,
            source="OUTPUT",
            content=[{"text": {"text": answer}}],
        )
        action = response.get("action")
        if action == "GUARDRAIL_INTERVENED":
            return False
        return True
    except Exception:
        return False
