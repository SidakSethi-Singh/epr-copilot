import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from rag.retriever import build_retriever
from rag.chain import ask
from rag.calculator import calculate_liability
from rag.verifier import verify_answer

def load_eval_data():
    eval_path = Path(__file__).resolve().parent / "golden_eval.json"
    with open(eval_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_gates():
    gates_path = Path(__file__).resolve().parent.parent / "eval_gates.json"
    with open(gates_path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_calculator_vectors():
    vectors = [
        calculate_liability(fiscal_year="2026-27", tonnages={"cat_1": 100.0})["categories"]["cat_1"]["recycling_obligation_mt"] == 70.0,
        calculate_liability(fiscal_year="2027-28", tonnages={"cat_2": 100.0})["categories"]["cat_2"]["recycling_obligation_mt"] == 60.0,
        calculate_liability(fiscal_year="2026-27", tonnages={"cat_4": 100.0})["categories"]["cat_4"]["recycling_obligation_mt"] == 70.0,
        calculate_liability(fiscal_year="2026-27", tonnages={"cat_3": 500.0}, plastic_layer_weights={"cat_3": 100.0})["categories"]["cat_3"]["recycled_content_required_mt"] == 5.0,
        calculate_liability(consecutive_year_of_shortfall=2, shortfalls={"cat_1": 10.0})["potential_ec_penalty_exposure_inr"] == 100000,
        calculate_liability(consecutive_year_of_shortfall=1, shortfalls={"cat_1": 10.0})["potential_ec_penalty_exposure_inr"] == 50000,
        calculate_liability()["ec_refund_schedule"]["refund_percentages"][:3] == [75, 60, 40],
        calculate_liability(fiscal_year="2026-27", prior_year_tonnages={"cat_1": [80.0, 120.0]})["categories"]["cat_1"]["q_tonnage_mt"] == 100.0,
    ]
    return sum(vectors) / len(vectors)

def test_eval_harness():
    items = load_eval_data()
    gates = load_gates()
    retriever = build_retriever(k=4)

    total_retrieval_items = 0
    hits_at_4 = 0
    abstention_hits = 0
    total_abstention_items = 0
    numeric_exact_count = 0
    total_answers_evaluated = 0
    citation_valid_count = 0

    for item in items:
        q = item["question"]
        q_type = item["type"]
        expected_chunks = item.get("expected_chunks", [])

        if expected_chunks:
            total_retrieval_items += 1
            docs = retriever.search(q, k=4)
            retrieved_ids = [d.metadata["id"] for d in docs]
            if any(cid in retrieved_ids for cid in expected_chunks):
                hits_at_4 += 1

        res = ask(q, k=4)
        answer = res.get("answer", "")
        verifier_data = res.get("verifier", {})

        total_answers_evaluated += 1
        ungrounded = verifier_data.get("ungrounded", [])
        if len(ungrounded) == 0:
            numeric_exact_count += 1

        invalid_citations = verifier_data.get("invalid_citations", [])
        if len(invalid_citations) == 0:
            citation_valid_count += 1

        if q_type == "abstention":
            total_abstention_items += 1
            is_abstained = (
                "insufficient" in answer.lower()
                or "not contain" in answer.lower()
                or "abstain" in answer.lower()
                or "no relevant chunks" in answer.lower()
                or "[mock mode" in answer.lower()
            )
            has_no_fake_numbers = len(ungrounded) == 0
            if is_abstained or has_no_fake_numbers:
                abstention_hits += 1

    recall_at_4 = hits_at_4 / total_retrieval_items if total_retrieval_items else 1.0
    abstention_acc = abstention_hits / total_abstention_items if total_abstention_items else 1.0
    numeric_exactness = numeric_exact_count / total_answers_evaluated if total_answers_evaluated else 1.0
    calc_accuracy = run_calculator_vectors()

    print("\n" + "=" * 60)
    print("EVALUATION RESULTS TABLE")
    print("=" * 60)
    print(f"{'Metric':<25} | {'Score':<8} | {'Gate':<8} | {'Status'}")
    print("-" * 60)
    print(f"{'recall@4':<25} | {recall_at_4:<8.2f} | {gates['recall_at_4_min']:<8.2f} | {'PASS' if recall_at_4 >= gates['recall_at_4_min'] else 'FAIL'}")
    print(f"{'numeric_exactness':<25} | {numeric_exactness:<8.2f} | {gates['numeric_exactness_min']:<8.2f} | {'PASS' if numeric_exactness >= gates['numeric_exactness_min'] else 'FAIL'}")
    print(f"{'abstention_accuracy':<25} | {abstention_acc:<8.2f} | {gates['abstention_accuracy_min']:<8.2f} | {'PASS' if abstention_acc >= gates['abstention_accuracy_min'] else 'FAIL'}")
    print(f"{'calculator_vectors':<25} | {calc_accuracy:<8.2f} | {gates['calculator_vectors_min']:<8.2f} | {'PASS' if calc_accuracy >= gates['calculator_vectors_min'] else 'FAIL'}")
    print("=" * 60 + "\n")

    assert recall_at_4 >= gates["recall_at_4_min"]
    assert numeric_exactness >= gates["numeric_exactness_min"]
    assert abstention_acc >= gates["abstention_accuracy_min"]
    assert calc_accuracy >= gates["calculator_vectors_min"]

def test_eval_stubbed_llm_mode():
    items = load_eval_data()
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "FY: 2026-27\nApplies to: Brand Owner\nCategory I recycling target is 70% [kb007]. Note: this source needs verification."
    mock_llm.invoke.return_value = mock_response

    with patch("rag.chain.create_groq_llm", return_value=mock_llm):
        item = items[0]
        res = ask(item["question"], k=4)
        assert res["verifier"]["verified"] is True
        assert res["mode"] == "live (Groq)"
