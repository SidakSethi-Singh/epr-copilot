import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, Tuple
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rag.knowledge_base import KNOWLEDGE_BASE

ABBREVIATION_MAP: Dict[str, str] = {
    "EC": "Environmental Compensation",
    "MLP": "Multi-Layered Plastic",
    "PIBO": "Producer Importer Brand Owner",
    "PWP": "Plastic Waste Processor",
    "PRO": "Producer Responsibility Organisation",
    "CPCB": "Central Pollution Control Board",
    "SPCB": "State Pollution Control Board",
    "EOL": "End of Life",
}

KEYWORD_BOOSTS: List[Dict[str, Any]] = [
    {
        "pattern": r"\b(?:deadline|filing|extension|due)\b",
        "boost_chunk_ids": ["kb011"],
        "boost_score": 0.5,
    },
    {
        "pattern": r"\b(?:penalty|EC|compensation|refund)\b",
        "boost_chunk_ids": ["kb013", "kb014"],
        "boost_score": 0.5,
    },
    {
        "pattern": r"\b(?:QR|barcode|label|labeling|labelling)\b",
        "boost_chunk_ids": ["kb012"],
        "boost_score": 0.5,
    },
]

def expand_query(query: str) -> str:
    expanded_query = query
    for abbreviation, full_form in ABBREVIATION_MAP.items():
        pattern = rf"\b{re.escape(abbreviation)}\b"
        if re.search(pattern, query, flags=re.IGNORECASE):
            expanded_query = re.sub(pattern, f"{abbreviation} {full_form}", expanded_query, flags=re.IGNORECASE)
    return expanded_query

def tokenize_text(text: str) -> List[str]:
    return [token.lower() for token in re.findall(r"\w+", text) if len(token) > 1]

def filter_chunks_by_temporal_status(
    chunks: List[Dict[str, Any]],
    as_of: Optional[str] = None,
) -> List[Dict[str, Any]]:
    effective_as_of = as_of or datetime.now().strftime("%Y-%m-%d")
    filtered_chunks = []
    for chunk in chunks:
        effective_from = chunk.get("effective_from")
        if effective_from and effective_from > effective_as_of:
            continue
        superseded_by = chunk.get("superseded_by")
        superseded_on = chunk.get("superseded_on") or chunk.get("superseded_date")
        if superseded_by:
            if superseded_on and superseded_on <= effective_as_of:
                continue
            if not superseded_on:
                continue
        filtered_chunks.append(chunk)
    return filtered_chunks

class VectorSearcher(Protocol):
    def search(self, query: str, k: int) -> List[Tuple[str, float]]:
        ...

class HybridRetriever:
    def __init__(
        self,
        chunks: Optional[List[Dict[str, Any]]] = None,
        default_k: int = 6,
        vector_searcher: Optional[VectorSearcher] = None,
    ):
        self.raw_chunks = chunks if chunks is not None else KNOWLEDGE_BASE
        self.default_k = default_k
        self.vector_searcher = vector_searcher

    def _chunk_to_document(self, chunk: Dict[str, Any]) -> Document:
        return Document(
            page_content=chunk["text"],
            metadata={
                "id": chunk["id"],
                "title": chunk["title"],
                "citation": chunk["citation"],
                "confidence": chunk.get("confidence", "needs_verify"),
                "clause": chunk.get("clause", ""),
                "effective_from": chunk.get("effective_from"),
                "superseded_by": chunk.get("superseded_by"),
                "source_id": chunk.get("source_id"),
                "source_url": chunk.get("source_url"),
            },
        )

    def search(
        self,
        query: str,
        k: Optional[int] = None,
        as_of: Optional[str] = None,
    ) -> List[Document]:
        target_k = k if k is not None else int(os.environ.get("RETRIEVAL_K", str(self.default_k)))
        active_chunks = filter_chunks_by_temporal_status(self.raw_chunks, as_of=as_of)
        if not active_chunks:
            return []

        preprocessed_query = expand_query(query)
        chunk_texts = [f"{c['title']} {c['citation']} {c['text']}" for c in active_chunks]
        tokenized_corpus = [tokenize_text(text) for text in chunk_texts]
        tokenized_query = tokenize_text(preprocessed_query)

        bm25_model = BM25Okapi(tokenized_corpus)
        bm25_scores = bm25_model.get_scores(tokenized_query)
        bm25_ranked_indices = sorted(range(len(active_chunks)), key=lambda idx: bm25_scores[idx], reverse=True)

        tfidf_vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
        tfidf_matrix = tfidf_vectorizer.fit_transform(chunk_texts)
        query_vector = tfidf_vectorizer.transform([preprocessed_query])
        tfidf_scores = cosine_similarity(query_vector, tfidf_matrix).flatten()
        tfidf_ranked_indices = sorted(range(len(active_chunks)), key=lambda idx: tfidf_scores[idx], reverse=True)

        rrf_scores: Dict[int, float] = {idx: 0.0 for idx in range(len(active_chunks))}
        rrf_constant = 60.0

        for rank, idx in enumerate(bm25_ranked_indices, start=1):
            rrf_scores[idx] += 1.0 / (rrf_constant + rank)

        for rank, idx in enumerate(tfidf_ranked_indices, start=1):
            rrf_scores[idx] += 1.0 / (rrf_constant + rank)

        if self.vector_searcher is not None:
            vector_results = self.vector_searcher.search(preprocessed_query, target_k)
            id_to_idx = {c["id"]: idx for idx, c in enumerate(active_chunks)}
            for rank, (chunk_id, _) in enumerate(vector_results, start=1):
                if chunk_id in id_to_idx:
                    rrf_scores[id_to_idx[chunk_id]] += 1.0 / (rrf_constant + rank)

        for boost_entry in KEYWORD_BOOSTS:
            if re.search(boost_entry["pattern"], query, flags=re.IGNORECASE) or re.search(boost_entry["pattern"], preprocessed_query, flags=re.IGNORECASE):
                for boost_chunk_id in boost_entry["boost_chunk_ids"]:
                    for idx, c in enumerate(active_chunks):
                        if c["id"] == boost_chunk_id:
                            rrf_scores[idx] += boost_entry["boost_score"]

        final_ranked_indices = sorted(range(len(active_chunks)), key=lambda idx: rrf_scores[idx], reverse=True)
        selected_indices = final_ranked_indices[:target_k]
        return [self._chunk_to_document(active_chunks[idx]) for idx in selected_indices]

    def invoke(self, query: str) -> List[Document]:
        return self.search(query=query)

def build_retriever(
    k: Optional[int] = None,
    chunks: Optional[List[Dict[str, Any]]] = None,
    vector_searcher: Optional[VectorSearcher] = None,
) -> HybridRetriever:
    configured_k = k if k is not None else int(os.environ.get("RETRIEVAL_K", "6"))
    return HybridRetriever(chunks=chunks, default_k=configured_k, vector_searcher=vector_searcher)
