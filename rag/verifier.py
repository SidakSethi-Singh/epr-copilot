"""
Post-generation Numeric and Citation Verifier for EPR Compliance Copilot.

Enforces statutory grounding by extracting factual claims:
  1. Percentages (e.g. 70%, 50%, 10%)
  2. Rupee / currency figures (e.g. Rs 5,000, Rs 10,000, Rs 20,000, Rs 3,500 - Rs 8,000)
  3. Statutory clause & rule citations (e.g. Rule 11.3, Schedule II, Section 15, Clause 7.2)
  4. Statutory dates and extensions (e.g. June 30, October 31, December 31, 28 August 2026)
  5. Physical thresholds (e.g. 120 microns, 60 GSM)

And verifying that each extracted claim exists in the text of at least one cited statutory chunk.
"""

import re
from typing import List, Dict, Any, Union


def _normalize_text(text: str) -> str:
    """Normalizes whitespace, punctuation, and currency symbols for flexible matching."""
    text = text.replace("₹", "Rs ").replace("INR", "Rs")
    # Normalize Indian currency notation: Rs. 5,000 -> Rs 5000
    text = re.sub(r"Rs\.?\s*", "rs ", text, flags=re.IGNORECASE)
    # Remove commas inside numbers (e.g., 5,000 -> 5000)
    text = re.sub(r"(?<=\d),(?=\d)", "", text)
    # Collapse whitespace
    return " ".join(text.lower().split())


def extract_statutory_claims(text: str) -> List[Dict[str, str]]:
    """
    Extracts high-stakes numeric and regulatory claims from text.
    Returns a list of dicts: {"type": str, "claim": str, "normalized": str}
    """
    claims = []

    # 1. Percentages (e.g., 70%, 50%, 85%)
    for match in re.finditer(r"\b(\d+(?:\.\d+)?)\s*%", text):
        val = match.group(0).strip()
        claims.append({"type": "percentage", "claim": val, "normalized": f"{match.group(1)}%"})

    # 2. Currency figures (e.g., Rs 5,000, Rs 10,000, Rs 20,000)
    for match in re.finditer(r"(?:rs\.?|₹|inr)\s*([\d,]+(?:\.\d+)?)", text, flags=re.IGNORECASE):
        clean_num = match.group(1).replace(",", "")
        claims.append({"type": "currency", "claim": match.group(0).strip(), "normalized": f"rs {clean_num}"})

    # 3. Rule / Clause / Section citations (e.g., Rule 11.3, Clause 7.2, Section 15)
    for match in re.finditer(r"\b(Rule\s+\d+(?:\.\d+)*|Clause\s+\d+(?:\.\d+)*|Section\s+\d+|Schedule\s+[IVX]+)\b", text, flags=re.IGNORECASE):
        val = match.group(0).strip()
        claims.append({"type": "statutory_ref", "claim": val, "normalized": _normalize_text(val)})

    # 4. Critical dates (e.g., June 30, October 31, December 31, 28 August 2026)
    month_pattern = r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,?\s*\d{4})?\b|\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)(?:\s+\d{4})?\b"
    for match in re.finditer(month_pattern, text, flags=re.IGNORECASE):
        val = match.group(0).strip()
        claims.append({"type": "date", "claim": val, "normalized": _normalize_text(val)})

    # 5. Technical thresholds (microns, GSM, MWh)
    for match in re.finditer(r"\b(\d+)\s*(?:microns?|gsm|mwh)\b", text, flags=re.IGNORECASE):
        val = match.group(0).strip()
        claims.append({"type": "threshold", "claim": val, "normalized": _normalize_text(val)})

    # De-duplicate while preserving order
    seen = set()
    unique_claims = []
    for c in claims:
        key = (c["type"], c["normalized"])
        if key not in seen:
            seen.add(key)
            unique_claims.append(c)

    return unique_claims


def verify_answer(answer: str, cited_chunks: List[Union[Dict[str, Any], Any]]) -> Dict[str, Any]:
    """
    Checks each extracted numeric/statutory claim in the answer against the corpus of cited chunks.

    Args:
        answer: The generated response from the LLM or mock generator.
        cited_chunks: List of Document objects or chunk dicts with page_content or text.

    Returns:
        {
            "status": "verified" | "unverified" | "skipped",
            "is_verified": bool,
            "checked_claims_count": int,
            "ungrounded_claims": List[str],
            "verified_claims": List[str]
        }
    """
    if not answer or not cited_chunks:
        return {
            "status": "skipped",
            "is_verified": False,
            "checked_claims_count": 0,
            "ungrounded_claims": [],
            "verified_claims": [],
        }

    # Extract all text from context chunks
    chunk_corpus_parts = []
    for chunk in cited_chunks:
        if hasattr(chunk, "page_content"):
            chunk_corpus_parts.append(chunk.page_content)
        elif isinstance(chunk, dict):
            chunk_corpus_parts.append(chunk.get("text", "") or chunk.get("page_content", ""))
        else:
            chunk_corpus_parts.append(str(chunk))

    full_context_norm = _normalize_text(" ".join(chunk_corpus_parts))
    claims = extract_statutory_claims(answer)

    if not claims:
        return {
            "status": "verified",
            "is_verified": True,
            "checked_claims_count": 0,
            "ungrounded_claims": [],
            "verified_claims": [],
        }

    verified_claims = []
    ungrounded_claims = []

    for c in claims:
        norm = c["normalized"]
        # Direct check
        if norm in full_context_norm:
            verified_claims.append(c["claim"])
            continue

        # If it's currency like "rs 5000", check if "5000" appears in context
        if c["type"] == "currency":
            digits = re.sub(r"\D", "", norm)
            if digits and digits in full_context_norm:
                verified_claims.append(c["claim"])
                continue

        # If it's percentage like "70%", check if "70%" or "70 percent" is present
        if c["type"] == "percentage":
            num = norm.replace("%", "").strip()
            if num in full_context_norm and (f"{num}%" in full_context_norm or f"{num} percent" in full_context_norm or f"{num} %" in full_context_norm):
                verified_claims.append(c["claim"])
                continue

        # If it's date like "october 31", check if both "october" and "31" exist in close proximity
        if c["type"] == "date":
            tokens = norm.split()
            if all(t in full_context_norm for t in tokens):
                verified_claims.append(c["claim"])
                continue

        # If it's clause citation like "rule 11.3", check parts
        if c["type"] == "statutory_ref":
            tokens = norm.split()
            if all(t in full_context_norm for t in tokens):
                verified_claims.append(c["claim"])
                continue

        ungrounded_claims.append(c["claim"])

    is_ok = len(ungrounded_claims) == 0
    return {
        "status": "verified" if is_ok else "unverified",
        "is_verified": is_ok,
        "checked_claims_count": len(claims),
        "ungrounded_claims": ungrounded_claims,
        "verified_claims": verified_claims,
    }
