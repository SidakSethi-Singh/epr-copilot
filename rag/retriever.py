"""
Retrieval layer for the EPR Compliance Copilot.

Uses LangChain's TFIDFRetriever (scikit-learn under the hood) enhanced with:
  1. Regulatory abbreviation expansion (e.g. EC -> Environmental Compensation,
     MLP -> Multilayered Plastic packaging) to bridge vocabulary gaps.
  2. Statutory keyword boosting for high-precision retrieval on critical
     compliance topics (deadlines, penalties, QR codes, MSME exemptions, etc.).
  3. Default top-k increased from 4 to 6 for broader clause coverage across
     the 22 statutory knowledge base chunks.
"""

import re
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_community.retrievers import TFIDFRetriever
from pydantic import Field, ConfigDict

from rag.knowledge_base import KNOWLEDGE_BASE

# Map common acronyms to their statutory expanded terms
ABBREVIATION_MAP: Dict[str, str] = {
    r"\bEC\b": "EC (Environmental Compensation penalties under EPA 1986 Section 15)",
    r"\bMLP\b": "MLP (Multilayered Plastic Packaging / Category III)",
    r"\bSUP\b": "SUP (Single-Use Plastics ban 120 microns)",
    r"\bPIBO\b": "PIBO (Producers, Importers, Brand Owners)",
    r"\bPIBOs\b": "PIBOs (Producers, Importers, Brand Owners)",
    r"\bPWP\b": "PWP (Plastic Waste Processors recyclers digital credits)",
    r"\bPWPs\b": "PWPs (Plastic Waste Processors recyclers digital credits)",
    r"\bBO\b": "Brand Owner (BO)",
    r"\bCTO\b": "CTO (Consent to Operate SPCB)",
    r"\bCTE\b": "CTE (Consent to Establish SPCB)",
    r"\bSPCB\b": "SPCB (State Pollution Control Board)",
    r"\bPCC\b": "PCC (Pollution Control Committee)",
    r"\bPRO\b": "PRO (Producer Responsibility Organisation Schedule II Clause 12)",
    r"\bMSME\b": "MSME (Micro and Small Enterprises exemption)",
    r"\bCat\s*1\b|\bCategory\s*1\b": "Category I (Rigid Plastics containers bottles)",
    r"\bCat\s*2\b|\bCategory\s*2\b": "Category II (Flexible Plastics pouches sachets)",
    r"\bCat\s*3\b|\bCategory\s*3\b": "Category III (Multilayered Plastic MLP non-plastic layer foil)",
    r"\bCat\s*4\b|\bCategory\s*4\b": "Category IV (Compostable Plastics IS/ISO 17088)",
}

# Domain keyword triggers mapped to specific statutory chunk IDs
KEYWORD_BOOSTS: Dict[tuple, List[str]] = {
    # Deadlines & extensions
    ("deadline", "due date", "annual return", "filing date", "extension", "june 30", "late return"): ["kb011"],
    # Penalties, EC & refund
    ("penalty", "penalties", "environmental compensation", "ec rate", "fine", "fines", "refund", "forfeiture", "section 15", "prosecution"): ["kb013", "kb014"],
    # Labeling & QR code
    ("qr", "qr code", "barcode", "label", "labeling", "labelling", "rule 11", "on-pack"): ["kb012"],
    # Boundaries Cat II vs Cat III
    ("cat ii vs cat iii", "category ii vs category iii", "flexible vs multilayer", "boundary", "aluminium foil", "aluminum foil", "paperboard", "layer composition"): ["kb004", "kb003"],
    # Recycled content
    ("recycled content", "recycled plastic content", "virgin plastic", "content mandate"): ["kb008"],
    # Recycling targets
    ("recycling target", "recycling targets", "recycling percentage", "minimum recycling"): ["kb007"],
    # Compostable
    ("compostable", "biodegradable", "is 17088", "iso 17088", "cat iv", "category iv"): ["kb005"],
    # MSME exemptions
    ("msme", "micro", "small enterprise", "small business", "turnover", "exempt", "exemption"): ["kb019"],
    # SPCB vs CPCB jurisdiction
    ("jurisdiction", "spcb", "pcc", "two states", "single window"): ["kb020"],
    # SUP ban & carry bag thickness
    ("single use", "single-use", "sup", "micron", "microns", "carry bag", "120 micron", "plastic cutlery"): ["kb017"],
    # PRO role
    ("pro", "producer responsibility organisation", "agency", "outsourcing"): ["kb010"],
    # PWP processor credits
    ("pwp", "processor", "recycler certificate", "digital credit", "double counting", "weighbridge"): ["kb018"],
    # Cross compliance
    ("battery", "bwmr", "e-waste", "ewaste", "cross-compliance", "offsetting"): ["kb022"],
    # Non plastic expansion
    ("paper", "glass", "metal", "non-plastic", "non plastic", "packaging rules 2024"): ["kb015"],
    # Registration & checklist
    ("registration", "register", "checklist", "portal", "iec", "form i"): ["kb016"],
    # Sellers
    ("seller", "sellers", "raw resin", "granules", "pellets"): ["kb002"],
    # EOL disposal
    ("end of life", "cement kiln", "waste to energy", "co-processing", "pyrolysis", "road", "irc sp"): ["kb021", "kb024"],
    # Energy recovery & Waste-to-Energy bridge
    ("energy", "waste to energy", "wte", "calorific", "calorific value", "thermal efficiency", "mwh", "alternative fuel", "afr"): ["kb024", "kb021"],
    # Biodegradable Category V
    ("biodegradable", "category v", "cat v", "is 17899", "iso 17556"): ["kb023"],
    # Collection formula
    ("collection obligation", "collection formula", "introduced packaging", "two preceding"): ["kb006"],
    # Credit prices & trading
    ("certificate price", "certificate cost", "epr certificate", "credit cost", "credit price", "trading portal", "market rate", "market price"): ["kb009"],
}


def preprocess_query(query: str) -> str:
    """Expands regulatory acronyms and synonyms to enhance vocabulary overlap."""
    expanded = query
    for pattern, replacement in ABBREVIATION_MAP.items():
        expanded = re.sub(pattern, replacement, expanded, flags=re.IGNORECASE)
    return expanded


def get_boosted_chunk_ids(query: str) -> List[str]:
    """Identifies chunk IDs that should receive priority boosting for query keywords."""
    query_lower = query.lower()
    boosted = []
    for keywords, chunk_ids in KEYWORD_BOOSTS.items():
        if any(kw in query_lower for kw in keywords):
            for cid in chunk_ids:
                if cid not in boosted:
                    boosted.append(cid)
    return boosted


class EnhancedTFIDFRetriever(BaseRetriever):
    """
    Enhanced TF-IDF retriever combining scikit-learn term frequencies with
    regulatory domain query expansion and keyword boosting.
    """
    base_retriever: TFIDFRetriever = Field(description="Underlying TF-IDF retriever")
    documents_by_id: Dict[str, Document] = Field(description="Map of chunk id to Document")
    k: int = Field(default=6, description="Number of documents to return")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _get_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
        expanded_query = preprocess_query(query)
        # Fetch more candidates from TF-IDF for reranking/boosting
        candidate_count = min(len(self.documents_by_id), max(self.k * 2, 10))
        self.base_retriever.k = candidate_count
        raw_docs = self.base_retriever.invoke(expanded_query)

        boosted_ids = get_boosted_chunk_ids(query)
        result_docs: List[Document] = []
        seen_ids = set()

        # 1. Place boosted matching chunks first
        for cid in boosted_ids:
            if cid in self.documents_by_id and cid not in seen_ids:
                result_docs.append(self.documents_by_id[cid])
                seen_ids.add(cid)

        # 2. Add candidates retrieved by TF-IDF
        for doc in raw_docs:
            cid = doc.metadata.get("id")
            if cid and cid not in seen_ids:
                result_docs.append(doc)
                seen_ids.add(cid)
            if len(result_docs) >= self.k:
                break

        return result_docs[:self.k]


def build_retriever(k: int = 6) -> EnhancedTFIDFRetriever:
    """
    Builds an enhanced TF-IDF retriever over the statutory knowledge base.

    Args:
        k: number of chunks to retrieve per query (default 6).
    """
    documents = [
        Document(
            page_content=chunk["text"],
            metadata={
                "id": chunk["id"],
                "title": chunk["title"],
                "citation": chunk["citation"],
                "confidence": chunk["confidence"],
                "effective_from": chunk.get("effective_from"),
                "source_url": chunk.get("source_url"),
                "retrieved_on": chunk.get("retrieved_on"),
                "verified_by": chunk.get("verified_by"),
            },
        )
        for chunk in KNOWLEDGE_BASE
    ]
    documents_by_id = {doc.metadata["id"]: doc for doc in documents}

    base_tfidf = TFIDFRetriever.from_documents(documents, k=k)
    return EnhancedTFIDFRetriever(
        base_retriever=base_tfidf,
        documents_by_id=documents_by_id,
        k=k,
    )


if __name__ == "__main__":
    retriever = build_retriever(k=4)
    sample_questions = [
        "What are the QR code labeling requirements?",
        "What happens if I miss my annual EPR filing deadline?",
        "How much does an EPR certificate cost?",
        "Can I use aluminium foil under flexible plastic Category II?",
    ]
    for q in sample_questions:
        print(f"\nQuery: {q}")
        results = retriever.invoke(q)
        for r in results:
            print(f"  [{r.metadata['id']}] {r.metadata['title']} "
                  f"(confidence={r.metadata['confidence']})")

