"""
Unit tests for the post-generation numeric and statutory verifier (rag/verifier.py).
"""

import pytest
from rag.verifier import extract_statutory_claims, verify_answer
from rag.knowledge_base import KNOWLEDGE_BASE


def test_extract_statutory_claims():
    text = (
        "Category I rigid plastics have a 70% recycling target in FY 2026-27 under Rule 11.3. "
        "The penalty under Section 15 of EPA 1986 is Rs 5,000 per MT. "
        "Carry bags must be at least 120 microns. Deadline is October 31, 2026."
    )
    claims = extract_statutory_claims(text)
    claim_texts = [c["claim"] for c in claims]

    assert any("70%" in c for c in claim_texts)
    assert any("Rs 5,000" in c or "5,000" in c for c in claim_texts)
    assert any("Rule 11.3" in c for c in claim_texts)
    assert any("Section 15" in c for c in claim_texts)
    assert any("120 microns" in c for c in claim_texts)
    assert any("October 31" in c for c in claim_texts)


def test_verify_answer_grounded_pass():
    # Use chunk kb007 text as cited context
    kb007 = next(c for c in KNOWLEDGE_BASE if c["id"] == "kb007")

    grounded_answer = (
        "For Category I rigid plastics, the mandatory recycling target is 70% in FY 2026-27 [kb007]. "
        "In FY 2027-28 onwards, it rises to 80%."
    )
    res = verify_answer(grounded_answer, [kb007])
    assert res["is_verified"] is True
    assert res["status"] == "verified"
    assert len(res["ungrounded_claims"]) == 0


def test_verify_answer_ungrounded_caught():
    kb007 = next(c for c in KNOWLEDGE_BASE if c["id"] == "kb007")

    # Fabricate an ungrounded target (e.g. 99% or Rs 99,999)
    hallucinated_answer = (
        "Under Schedule II, Category I rigid plastics have a 99% target in 2026-27 [kb007], "
        "and non-compliance fine is Rs 99,000 per MT."
    )
    res = verify_answer(hallucinated_answer, [kb007])
    assert res["is_verified"] is False
    assert res["status"] == "unverified"
    assert len(res["ungrounded_claims"]) > 0
    assert any("99%" in u for u in res["ungrounded_claims"])


def test_verify_empty_or_no_claims():
    res = verify_answer("This is a general statement without specific figures.", [KNOWLEDGE_BASE[0]])
    assert res["is_verified"] is True
    assert res["checked_claims_count"] == 0
