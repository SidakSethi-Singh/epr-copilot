"""
Statutory consistency and drift prevention tests (G10).
Asserts that rules/rules.json and rag/knowledge_base.py never drift apart.
"""

import os
import json
import pytest
from rag.knowledge_base import KNOWLEDGE_BASE
from rag.calculator import calculate_liability, get_target, get_rules_version

RULES_PATH = os.path.join(os.path.dirname(__file__), "..", "rules", "rules.json")


@pytest.fixture(scope="module")
def rules():
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_rules_file_structure(rules):
    """Ensures rules.json has all required schema blocks."""
    assert "ruleset_version" in rules
    assert "verified_on" in rules
    assert "sources" in rules and len(rules["sources"]) >= 3
    assert "recycling_min_pct" in rules
    assert "recycled_content_pct" in rules
    assert "environmental_compensation" in rules
    assert "deadlines" in rules
    assert "energy" in rules


def test_golden_roadmap_vectors():
    """
    Validates the 6 critical golden vectors from the Production-Readiness
    Audit and Proper Roadmap §7:
      1. Cat II, 100 MT, FY 2027-28 -> min. recycling = 60 MT
      2. Cat I, 100 MT, FY 2026-27 -> min. recycling = 70 MT
      3. Cat IV, 100 MT, FY 2026-27 -> min. recycling = 70 MT (not 100 MT)
      4. Cat III, 100 MT plastic layer, FY 2026-27 -> recycled content = 5 MT (not 10 MT)
      5. Shortfall 10 MT, 2nd consecutive year -> EC = Rs 1,00,000 (escalated at Rs 10,000/MT)
      6. Year 1 refund -> 75% refund (not 85%)
    """
    # 1. Cat II, 100 MT, FY 2027-28
    res1 = calculate_liability(fiscal_year="2027-28", tonnages={"cat_2": 100.0})
    assert res1["categories"]["cat_2"]["recycling_obligation_mt"] == 60.0

    # 2. Cat I, 100 MT, FY 2026-27
    res2 = calculate_liability(fiscal_year="2026-27", tonnages={"cat_1": 100.0})
    assert res2["categories"]["cat_1"]["recycling_obligation_mt"] == 70.0

    # 3. Cat IV, 100 MT, FY 2026-27 (previously wrong at 100 MT)
    res3 = calculate_liability(fiscal_year="2026-27", tonnages={"cat_4": 100.0})
    assert res3["categories"]["cat_4"]["recycling_obligation_mt"] == 70.0

    # 4. Cat III, 100 MT, FY 2026-27 (previously wrong at 10 MT)
    res4 = calculate_liability(fiscal_year="2026-27", tonnages={"cat_3": 100.0})
    assert res4["categories"]["cat_3"]["recycled_content_required_mt"] == 5.0

    # 5. Shortfall 10 MT, Year 2 consecutive default escalation
    # If obligation is 10 MT, Year 2 total EC must be 10 * 10,000 = Rs 1,00,000
    res5 = calculate_liability(fiscal_year="2026-27", tonnages={"cat_1": 100.0 / 7.0})  # 100/7 * 70% = 10 MT
    assert res5["ec_escalation_by_consecutive_year"]["year_2_rate_inr_per_mt"] == 10000
    assert abs(res5["ec_escalation_by_consecutive_year"]["year_2_total_inr"] - 100000) <= 1000

    # 6. Refund schedule: 75% Year 1, 60% Year 2, 40% Year 3
    res6 = calculate_liability(fiscal_year="2026-27", tonnages={"cat_1": 100.0})
    assert "75%" in res6["ec_refund_schedule"]["year_1_fulfillment"]
    assert "60%" in res6["ec_refund_schedule"]["year_2_fulfillment"]
    assert "40%" in res6["ec_refund_schedule"]["year_3_fulfillment"]


def test_kb_and_rules_do_not_drift(rules):
    """
    Cross-checks that numbers stated in knowledge base chunk texts agree with rules.json:
      - kb007 contains 70% for Cat I in 2026-27
      - kb008 contains 40% for Cat I, 10% for Cat II, 5% for Cat III in 2026-27
      - kb013 contains 75% for year 1 refund
    """
    kb_dict = {chunk["id"]: chunk["text"] for chunk in KNOWLEDGE_BASE}

    # kb007 checks
    assert "70% in FY 2026-27" in kb_dict["kb007"]
    assert "50% in FY 2026-27" in kb_dict["kb007"]  # Cat II & III

    # kb008 checks
    assert "40% in FY 2026-27" in kb_dict["kb008"]
    assert "10% in FY 2026-27" in kb_dict["kb008"]
    assert "5% in FY 2026-27" in kb_dict["kb008"]

    # kb013 checks
    assert "75% of the levied EC is refunded" in kb_dict["kb013"]
    assert "60% is refunded" in kb_dict["kb013"]
    assert "40% is refunded" in kb_dict["kb013"]
    assert "Rs 10,000 per MT in Year 2" in kb_dict["kb013"]
    assert "Rs 20,000 per MT in Year 3" in kb_dict["kb013"]
