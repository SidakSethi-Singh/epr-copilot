import os
from unittest.mock import MagicMock, patch
import pytest
from botocore.stub import Stubber
import boto3
from rag.llm_bedrock import BedrockLLM
from rag.guardrail import grounded, is_guardrail_enabled
from rag.chain import ask, get_llm_status, generate_with_fallback

def test_bedrock_llm_invoke_success():
    client = boto3.client("bedrock-runtime", region_name="ap-south-1")
    stubber = Stubber(client)
    expected_params = {
        "modelId": "apac.anthropic.claude-3-haiku-20240307-v1:0",
        "messages": [{"role": "user", "content": [{"text": "Hello"}]}],
        "inferenceConfig": {"temperature": 0.0, "maxTokens": 700},
    }
    response = {
        "output": {
            "message": {
                "role": "assistant",
                "content": [{"text": "Hello from Bedrock"}],
            }
        },
        "stopReason": "end_turn",
        "usage": {"inputTokens": 10, "outputTokens": 5, "totalTokens": 15},
        "metrics": {"latencyMs": 150},
    }
    stubber.add_response("converse", response, expected_params)
    stubber.activate()

    llm = BedrockLLM(
        model_id="apac.anthropic.claude-3-haiku-20240307-v1:0",
        region_name="ap-south-1",
        client=client,
    )
    result = llm.invoke("Hello")
    assert result == "Hello from Bedrock"
    stubber.deactivate()

def test_guardrail_enabled_check(monkeypatch):
    monkeypatch.delenv("GUARDRAIL_ID", raising=False)
    monkeypatch.delenv("GUARDRAIL_VERSION", raising=False)
    assert is_guardrail_enabled() is False

    monkeypatch.setenv("GUARDRAIL_ID", "guardrail-123")
    monkeypatch.setenv("GUARDRAIL_VERSION", "1")
    assert is_guardrail_enabled() is True

def test_guardrail_intervened(monkeypatch):
    monkeypatch.setenv("GUARDRAIL_ID", "gr-123")
    monkeypatch.setenv("GUARDRAIL_VERSION", "DRAFT")

    mock_client = MagicMock()
    mock_client.apply_guardrail.return_value = {"action": "GUARDRAIL_INTERVENED"}

    is_grounded = grounded("context", "question", "hallucinated answer", client=mock_client)
    assert is_grounded is False

def test_guardrail_passes(monkeypatch):
    monkeypatch.setenv("GUARDRAIL_ID", "gr-123")
    monkeypatch.setenv("GUARDRAIL_VERSION", "DRAFT")

    mock_client = MagicMock()
    mock_client.apply_guardrail.return_value = {"action": "NONE"}

    is_grounded = grounded("context", "question", "valid answer", client=mock_client)
    assert is_grounded is True

def test_guardrail_error_safe_fallback(monkeypatch):
    monkeypatch.setenv("GUARDRAIL_ID", "gr-123")
    monkeypatch.setenv("GUARDRAIL_VERSION", "DRAFT")

    mock_client = MagicMock()
    mock_client.apply_guardrail.side_effect = RuntimeError("API failure")

    is_grounded = grounded("context", "question", "answer", client=mock_client)
    assert is_grounded is False

def test_fallback_chain_on_provider_error(monkeypatch):
    monkeypatch.setenv("BEDROCK_MODEL_ID", "apac.claude")
    monkeypatch.setenv("GROQ_API_KEY", "groq-key")

    mock_bedrock = MagicMock()
    mock_bedrock.invoke.side_effect = RuntimeError("Bedrock timeout")

    mock_groq = MagicMock()
    mock_groq_response = MagicMock()
    mock_groq_response.content = "FY: 2026-27\nApplies to: Brand Owner\nCategory I target is 70% [kb007]"
    mock_groq.invoke.return_value = mock_groq_response

    with patch("rag.chain.create_bedrock_llm", return_value=mock_bedrock), \
         patch("rag.chain.create_groq_llm", return_value=mock_groq):
        state = {
            "question": "What is the Category I target?",
            "retrieved_docs": [],
            "answer": "",
            "mode": "",
            "verifier": {},
            "as_of": None,
        }
        res = generate_with_fallback(state)
        assert res["mode"] == "live (Groq)"
        assert "70%" in res["answer"]
