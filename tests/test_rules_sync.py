import re
from rag.knowledge_base import KNOWLEDGE_BASE
from rag.rules import load_rules

def get_chunk(chunk_id: str) -> dict:
    for chunk in KNOWLEDGE_BASE:
        if chunk["id"] == chunk_id:
            return chunk
    raise KeyError(f"Chunk {chunk_id} not found in knowledge base")

def test_recycling_targets_sync():
    rules = load_rules()
    kb007 = get_chunk("kb007")
    text = kb007["text"]
    
    categories = ["I", "II", "III", "IV"]
    years = ["2024-25", "2025-26", "2026-27", "2027-28", "2028-29"]
    
    for cat in categories:
        for fy in years:
            expected_val = rules["recycling_min_pct"][fy][cat]
            pattern = rf"{expected_val}%\s+in\s+{re.escape(fy)}"
            match = re.search(pattern, text)
            assert match is not None, f"Drift: Category {cat} {fy} target {expected_val}% not found in kb007 text"

def test_recycled_content_targets_sync():
    rules = load_rules()
    kb008 = get_chunk("kb008")
    text = kb008["text"]
    
    categories = ["I", "II", "III"]
    years = ["2025-26", "2026-27", "2027-28", "2028-29"]
    
    for cat in categories:
        for fy in years:
            expected_val = rules["recycled_content_pct"][fy][cat]
            pattern = rf"{expected_val}%\s+in\s+{re.escape(fy)}"
            match = re.search(pattern, text)
            assert match is not None, f"Drift: Recycled content Category {cat} {fy} target {expected_val}% not found in kb008 text"

def test_environmental_compensation_sync():
    rules = load_rules()
    kb013 = get_chunk("kb013")
    text = kb013["text"]
    
    rates = rules["environmental_compensation"]["inr_per_mt_by_consecutive_year"]
    for year_str, amount in rates.items():
        if not str(amount).isdigit():
            continue
        formatted_amount = f"{int(amount):,}"
        pattern = rf"{re.escape(formatted_amount)}\s+per\s+MT\s+for\s+year\s+{year_str}"
        assert re.search(pattern, text) is not None, f"Drift: EC year {year_str} rate Rs {formatted_amount} not found in kb013 text"
    
    refunds = rules["environmental_compensation"]["refund_pct_by_year_of_fulfilment"]
    for year_str, pct in refunds.items():
        pattern = rf"{pct}%\s+refund\s+within\s+{year_str}\s+year"
        assert re.search(pattern, text) is not None, f"Drift: Refund year {year_str} percentage {pct}% not found in kb013 text"

def test_deadlines_sync():
    rules = load_rules()
    kb011 = get_chunk("kb011")
    text = kb011["text"]
    
    statutory_date = rules["statutory_annual_return_date"]
    assert statutory_date in text, f"Drift: Statutory return date {statutory_date} not found in kb011"
    
    for deadline in rules["deadlines"]:
        entity = deadline["entity"]
        date = deadline["date"]
        pattern = rf"{entity}.*?{date}"
        assert re.search(pattern, text) is not None, f"Drift: Deadline for {entity} ({date}) not found in kb011"

def test_cert_price_ranges_sync():
    rules = load_rules()
    kb009 = get_chunk("kb009")
    text = kb009["text"]
    
    for cat in ["I", "II", "III", "IV"]:
        low = rules["cert_price_ranges_inr_per_mt"][cat]["low"]
        high = rules["cert_price_ranges_inr_per_mt"][cat]["high"]
        low_fmt = f"{low:,}"
        high_fmt = f"{high:,}"
        pattern = rf"Category\s+{cat}:.*?{re.escape(low_fmt)}.*?{re.escape(high_fmt)}"
        assert re.search(pattern, text) is not None, f"Drift: Certificate prices for Category {cat} not found in kb009"
