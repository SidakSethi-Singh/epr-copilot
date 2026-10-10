import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

def normalize_text_numbers(text: str) -> str:
    return re.sub(r"(?<=\d),(?=\d)", "", text)

def extract_percentages(text: str) -> List[str]:
    matches = re.findall(r"\b\d+(?:\.\d+)?%", text)
    return list(dict.fromkeys(matches))

def extract_currencies(text: str) -> List[str]:
    matches = re.findall(r"(?:₹|Rs\.?|INR)\s*[\d,]+(?:\.\d+)?", text, re.IGNORECASE)
    return list(dict.fromkeys(matches))

def extract_mt_quantities(text: str) -> List[str]:
    matches = re.findall(r"\b[\d,]+(?:\.\d+)?\s*(?:MT|metric tons?|tonnes?)\b", text, re.IGNORECASE)
    return list(dict.fromkeys(matches))

def extract_fy_strings(text: str) -> List[str]:
    matches = re.findall(r"\b(?:FY\s*)?\d{4}-\d{2,4}\b", text, re.IGNORECASE)
    return list(dict.fromkeys(matches))

def extract_clause_refs(text: str) -> List[str]:
    patterns = [
        r"\bRule\s+\d+(?:\.\d+)?\b",
        r"\bSection\s+\d+\b",
        r"\bSchedule\s+[IVXLCDM]+\b",
        r"\bG\.S\.R\.\s*\d+\([A-Za-z]\)\b",
        r"\bClause\s+\d+(?:\.\d+)?\b",
    ]
    results = []
    for pattern in patterns:
        found = re.findall(pattern, text, re.IGNORECASE)
        results.extend(found)
    return list(dict.fromkeys(results))

def extract_dates(text: str) -> List[str]:
    patterns = [
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,\s+\d{4})?\b",
        r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)(?:\s+\d{4})?\b",
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2}(?:,\s+\d{4})?\b",
        r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?(?:\s+\d{4})?\b",
    ]
    results = []
    for pattern in patterns:
        found = re.findall(pattern, text, re.IGNORECASE)
        results.extend(found)
    return list(dict.fromkeys(results))

def extract_citation_ids(text: str) -> List[str]:
    matches = re.findall(r"\[(kb\d+)\]", text, re.IGNORECASE)
    return [m.lower() for m in matches]

def parse_date_to_canonical(date_str: str) -> Optional[str]:
    cleaned = date_str.strip().replace(",", "")
    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%B %d %Y",
        "%d %B %Y",
        "%b %d %Y",
        "%d %b %Y",
        "%B %d",
        "%d %B",
        "%b %d",
        "%d %b",
    ]
    for fmt in formats:
        try:
            parsed = datetime.strptime(cleaned, fmt)
            if "%Y" in fmt:
                return parsed.strftime("%Y-%m-%d")
            return parsed.strftime("%m-%d")
        except ValueError:
            pass
    return None

def check_token_in_sources(token: str, sources_raw: List[str], sources_normalized: List[str]) -> bool:
    token_lower = token.lower()
    token_num_norm = normalize_text_numbers(token_lower)
    token_digits_only = re.sub(r"[^\d.]", "", token_num_norm)

    for src_raw, src_norm in zip(sources_raw, sources_normalized):
        src_raw_lower = src_raw.lower()
        src_norm_lower = src_norm.lower()

        if token_lower in src_raw_lower or token_num_norm in src_norm_lower:
            return True

        if token.endswith("%"):
            val = token[:-1].strip()
            if f"{val}%" in src_raw_lower or f"{val} percent" in src_raw_lower or f"{val} %" in src_raw_lower:
                return True

        if any(sym in token for sym in ["₹", "Rs", "INR", "rs"]):
            if token_digits_only and (token_digits_only in src_norm_lower or token_digits_only in src_raw_lower):
                return True

        canonical_date = parse_date_to_canonical(token)
        if canonical_date:
            if canonical_date in src_raw_lower or canonical_date in src_norm_lower:
                return True
            tokens_in_date = [part for part in re.split(r"[\s,-]+", token_lower) if len(part) >= 2]
            if tokens_in_date and all(part in src_raw_lower for part in tokens_in_date):
                return True

        if "mt" in token_lower or "ton" in token_lower:
            if token_digits_only and (token_digits_only in src_norm_lower or token_digits_only in src_raw_lower):
                return True

    return False

def check_needs_verify_flag(answer: str) -> bool:
    answer_lower = answer.lower()
    phrases = [
        "needs_verify",
        "needs verification",
        "need verification",
        "unverified",
        "requires verification",
        "pending verification",
        "provisional",
        "not confirmed",
    ]
    return any(phrase in answer_lower for phrase in phrases)

def verify_answer(answer: str, cited_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not answer or not answer.strip():
        return {
            "verified": False,
            "ungrounded": ["empty_answer"],
            "invalid_citations": [],
            "needs_verify_flagged": False,
        }

    valid_chunk_ids = {str(c.get("id", "")).lower() for c in cited_chunks if c.get("id")}
    cited_in_text = extract_citation_ids(answer)
    invalid_citations = [cid for cid in cited_in_text if cid not in valid_chunk_ids]

    sources_raw = []
    for c in cited_chunks:
        text_content = c.get("text", "") or ""
        citation_info = c.get("citation", "") or ""
        title_info = c.get("title", "") or ""
        clause_info = c.get("clause", "") or ""
        sources_raw.append(f"{title_info} {citation_info} {clause_info} {text_content}")

    sources_normalized = [normalize_text_numbers(s) for s in sources_raw]

    tokens_to_check = []
    tokens_to_check.extend(extract_percentages(answer))
    tokens_to_check.extend(extract_currencies(answer))
    tokens_to_check.extend(extract_dates(answer))
    tokens_to_check.extend(extract_fy_strings(answer))
    tokens_to_check.extend(extract_mt_quantities(answer))
    tokens_to_check.extend(extract_clause_refs(answer))

    ungrounded = []
    for token in tokens_to_check:
        if not check_token_in_sources(token, sources_raw, sources_normalized):
            ungrounded.append(token)

    requires_verification = any(
        c.get("confidence") == "needs_verify" or c.get("status") == "needs_verify"
        for c in cited_chunks
    )
    flag_present = check_needs_verify_flag(answer)
    needs_verify_flagged = flag_present if requires_verification else True

    has_invalid_citations = len(invalid_citations) > 0
    has_ungrounded = len(ungrounded) > 0
    verification_passed = (not has_invalid_citations) and (not has_ungrounded) and needs_verify_flagged

    return {
        "verified": verification_passed,
        "ungrounded": ungrounded,
        "invalid_citations": invalid_citations,
        "needs_verify_flagged": needs_verify_flagged,
    }
