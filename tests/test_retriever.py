import pytest
from rag.retriever import (
    build_retriever,
    expand_query,
    filter_chunks_by_temporal_status,
    HybridRetriever,
)

def test_abbreviation_expansion():
    query = "What is EC obligation for MLP packaging under PIBO rules?"
    expanded = expand_query(query)
    assert "Environmental Compensation" in expanded
    assert "Multi-Layered Plastic" in expanded
    assert "Producer Importer Brand Owner" in expanded

def test_as_of_filtering():
    chunks = [
        {"id": "c1", "text": "Old rule", "effective_from": "2022-01-01", "superseded_by": None},
        {"id": "c2", "text": "Future rule", "effective_from": "2027-01-01", "superseded_by": None},
        {"id": "c3", "text": "Superseded rule", "effective_from": "2022-01-01", "superseded_by": "c4", "superseded_on": "2024-01-01"},
    ]
    active = filter_chunks_by_temporal_status(chunks, as_of="2025-06-01")
    active_ids = [c["id"] for c in active]
    assert "c1" in active_ids
    assert "c2" not in active_ids
    assert "c3" not in active_ids

def test_keyword_boosting():
    retriever = build_retriever(k=6)
    results = retriever.search("What is the annual filing deadline?")
    result_ids = [doc.metadata["id"] for doc in results]
    assert "kb011" in result_ids

def test_sample_query_1_qr_code_labeling():
    retriever = build_retriever(k=6)
    results = retriever.search("What are the QR code and barcode labeling mandates?")
    result_ids = [doc.metadata["id"] for doc in results]
    assert "kb012" in result_ids

def test_sample_query_2_filing_deadline():
    retriever = build_retriever(k=6)
    results = retriever.search("What happens if I miss my annual EPR filing deadline?")
    result_ids = [doc.metadata["id"] for doc in results]
    assert "kb011" in result_ids

def test_sample_query_3_ec_penalty_rates():
    retriever = build_retriever(k=6)
    results = retriever.search("What are the environmental compensation EC penalty rates?")
    result_ids = [doc.metadata["id"] for doc in results]
    assert "kb013" in result_ids

def test_sample_query_4_recycling_targets():
    retriever = build_retriever(k=6)
    results = retriever.search("What are the recycling targets for Category I rigid plastics?")
    result_ids = [doc.metadata["id"] for doc in results]
    assert "kb007" in result_ids

def test_sample_query_5_category_iv_compostable():
    retriever = build_retriever(k=6)
    results = retriever.search("What are the rules for Category IV compostable plastics?")
    result_ids = [doc.metadata["id"] for doc in results]
    assert "kb005" in result_ids
