from pathlib import Path
import json
from typing import Any, Dict, List, Optional

_RULES_CACHE: Optional[Dict[str, Any]] = None

def get_rules_path() -> Path:
    return Path(__file__).resolve().parent.parent / "rules" / "rules.json"

def validate_rules_schema(data: Any) -> None:
    if not isinstance(data, dict):
        raise ValueError("Rules data must be a dictionary")
    
    required_top_level_keys = [
        "ruleset_version",
        "verified_on",
        "sources",
        "recycling_min_pct",
        "recycled_content_pct",
        "environmental_compensation",
        "deadlines",
        "statutory_annual_return_date",
        "cert_price_ranges_inr_per_mt",
    ]
    for key in required_top_level_keys:
        if key not in data:
            raise ValueError(f"Missing required top-level key: {key}")
    
    if not isinstance(data["sources"], list) or not data["sources"]:
        raise ValueError("sources must be a non-empty list")
    
    for source in data["sources"]:
        for src_key in ["id", "title", "url", "sha256", "retrieved_on"]:
            if src_key not in source:
                raise ValueError(f"Source missing required field: {src_key}")

    if not isinstance(data["recycling_min_pct"], dict):
        raise ValueError("recycling_min_pct must be a dictionary")
    
    if "_meta" not in data["recycling_min_pct"]:
        raise ValueError("recycling_min_pct must contain _meta")

    if not isinstance(data["recycled_content_pct"], dict):
        raise ValueError("recycled_content_pct must be a dictionary")

    if "_meta" not in data["recycled_content_pct"]:
        raise ValueError("recycled_content_pct must contain _meta")

    ec = data["environmental_compensation"]
    if not isinstance(ec, dict):
        raise ValueError("environmental_compensation must be a dictionary")
    
    for ec_key in ["inr_per_mt_by_consecutive_year", "refund_pct_by_year_of_fulfilment", "status"]:
        if ec_key not in ec:
            raise ValueError(f"environmental_compensation missing required field: {ec_key}")

    if not isinstance(data["deadlines"], list):
        raise ValueError("deadlines must be a list")

    for deadline in data["deadlines"]:
        for d_key in ["fy", "entity", "date", "basis", "source_id", "status"]:
            if d_key not in deadline:
                raise ValueError(f"Deadline missing required field: {d_key}")

    cert_prices = data["cert_price_ranges_inr_per_mt"]
    if not isinstance(cert_prices, dict) or "_meta" not in cert_prices:
        raise ValueError("cert_price_ranges_inr_per_mt must contain _meta")

def load_rules(force_reload: bool = False) -> Dict[str, Any]:
    global _RULES_CACHE
    if _RULES_CACHE is not None and not force_reload:
        return _RULES_CACHE
    
    path = get_rules_path()
    if not path.is_file():
        raise FileNotFoundError(f"Rules file not found at {path}")
    
    with open(path, "r", encoding="utf-8") as file_handle:
        try:
            data = json.load(file_handle)
        except json.JSONDecodeError as decode_error:
            raise ValueError(f"Malformed JSON in rules file: {decode_error}") from decode_error

    validate_rules_schema(data)
    _RULES_CACHE = data
    return _RULES_CACHE

def get_ruleset_version() -> str:
    return str(load_rules().get("ruleset_version", ""))

def get_verified_on() -> str:
    return str(load_rules().get("verified_on", ""))

def get_recycling_min_pct(fiscal_year: str, category: str) -> Optional[int]:
    rules = load_rules()
    table = rules.get("recycling_min_pct", {})
    year_table = table.get(fiscal_year)
    if isinstance(year_table, dict):
        return year_table.get(category)
    return None

def get_recycled_content_pct(fiscal_year: str, category: str) -> Optional[int]:
    rules = load_rules()
    table = rules.get("recycled_content_pct", {})
    year_table = table.get(fiscal_year)
    if isinstance(year_table, dict):
        return year_table.get(category)
    return None

def get_ec_rate(consecutive_year: int) -> int:
    rules = load_rules()
    rates = rules.get("environmental_compensation", {}).get("inr_per_mt_by_consecutive_year", {})
    str_key = str(min(max(consecutive_year, 1), 3))
    return int(rates.get(str_key, rates.get("3", 20000)))

def get_refund_pct(year_of_fulfilment: int) -> int:
    rules = load_rules()
    schedule = rules.get("environmental_compensation", {}).get("refund_pct_by_year_of_fulfilment", {})
    str_key = str(year_of_fulfilment)
    return int(schedule.get(str_key, 0))

def get_deadlines() -> List[Dict[str, Any]]:
    return list(load_rules().get("deadlines", []))

def get_statutory_annual_return_date() -> str:
    return str(load_rules().get("statutory_annual_return_date", "06-30"))

def get_cert_price_ranges() -> Dict[str, Any]:
    return dict(load_rules().get("cert_price_ranges_inr_per_mt", {}))

def count_status_tags(data: Any, counter: Dict[str, int]) -> None:
    if isinstance(data, dict):
        if "status" in data and isinstance(data["status"], str):
            status_value = data["status"]
            counter[status_value] = counter.get(status_value, 0) + 1
        for value in data.values():
            count_status_tags(value, counter)
    elif isinstance(data, list):
        for item in data:
            count_status_tags(item, counter)

def get_rules_status_summary() -> Dict[str, int]:
    rules = load_rules()
    counter = {"verified": 0, "reported": 0, "needs_verify": 0}
    count_status_tags(rules, counter)
    return counter
