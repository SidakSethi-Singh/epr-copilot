import pytest
from rag.verifier import verify_answer

def test_grounded_answer_passes():
    chunks = [
        {
            "id": "kb007",
            "title": "Recycling Targets",
            "citation": "Schedule II, Clause 7",
            "clause": "Clause 7.2",
            "text": "For FY 2026-27, recycling target for Category I is 70% under Schedule II.",
            "confidence": "verified",
        }
    ]
    answer = "Under Schedule II, Category I has a recycling target of 70% for 2026-27 [kb007]."
    res = verify_answer(answer, chunks)
    assert res["verified"] is True
    assert res["ungrounded"] == []
    assert res["invalid_citations"] == []
    assert res["needs_verify_flagged"] is True

def test_invented_percentage_fails():
    chunks = [
        {
            "id": "kb007",
            "title": "Recycling Targets",
            "citation": "Schedule II",
            "text": "Target is 70%.",
            "confidence": "verified",
        }
    ]
    answer = "The target is 95% [kb007]."
    res = verify_answer(answer, chunks)
    assert res["verified"] is False
    assert any("95%" in u for u in res["ungrounded"])

def test_invented_date_fails():
    chunks = [
        {
            "id": "kb014",
            "title": "Deadlines",
            "citation": "MoEFCC Order",
            "text": "The deadline is 2026-10-31.",
            "confidence": "verified",
        }
    ]
    answer = "The deadline is 2030-12-31 [kb014]."
    res = verify_answer(answer, chunks)
    assert res["verified"] is False
    assert any("2030-12-31" in u for u in res["ungrounded"])

def test_fake_citation_fails():
    chunks = [
        {
            "id": "kb001",
            "title": "General Scope",
            "citation": "Rules",
            "text": "Scope includes producers.",
            "confidence": "verified",
        }
    ]
    answer = "Scope includes producers [kb999]."
    res = verify_answer(answer, chunks)
    assert res["verified"] is False
    assert "kb999" in res["invalid_citations"]

def test_indian_format_amount_matches():
    chunks = [
        {
            "id": "kb013",
            "title": "EC Rates",
            "citation": "CPCB Guidelines",
            "text": "The penalty for year 2 is Rs 100000 per MT.",
            "confidence": "verified",
        }
    ]
    answer = "The penalty is ₹1,00,000 per MT [kb013]."
    res = verify_answer(answer, chunks)
    assert res["verified"] is True
    assert res["ungrounded"] == []

def test_missing_needs_verify_flag_fails():
    chunks = [
        {
            "id": "kb015",
            "title": "Market Prices",
            "citation": "CPCB Report",
            "text": "Credit prices range between 3500 and 8000.",
            "confidence": "needs_verify",
        }
    ]
    answer_without_flag = "Credit prices are 3500 [kb015]."
    res_fail = verify_answer(answer_without_flag, chunks)
    assert res_fail["verified"] is False
    assert res_fail["needs_verify_flagged"] is False

    answer_with_flag = "Credit prices are 3500 [kb015]. Note: this source is unverified and needs verification."
    res_pass = verify_answer(answer_with_flag, chunks)
    assert res_pass["verified"] is True
    assert res_pass["needs_verify_flagged"] is True

def test_empty_answer_fails():
    chunks = [{"id": "kb001", "text": "Some text", "confidence": "verified"}]
    res = verify_answer("", chunks)
    assert res["verified"] is False
    assert res["ungrounded"] == ["empty_answer"]

    res_spaces = verify_answer("   ", chunks)
    assert res_spaces["verified"] is False
