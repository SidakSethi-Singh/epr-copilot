
"""
The RAG pipeline for EPR Compliance Copilot, built as a LangGraph graph:

    retrieve_node -> generate_node

Supports multiple generation modes, auto-selected based on environment keys.
Priority order (first key found wins, or set LLM_PROVIDER to force one):

  1. GROQ         -> GROQ_API_KEY      (free tier, ultra-fast LPU inference)
  2. OPENROUTER   -> OPENROUTER_API_KEY (free :free models via openrouter.ai)
  3. GEMINI       -> GEMINI_API_KEY or GOOGLE_API_KEY
  4. ANTHROPIC    -> ANTHROPIC_API_KEY
  5. OPENAI       -> OPENAI_API_KEY
  6. MOCK MODE    -> no key needed (returns raw retrieved chunks for free)

Current default free models (Sep 2026):
  Groq:       deepseek-r1-distill-llama-70b  (free tier)
  OpenRouter: deepseek/deepseek-r1:free       (zero cost :free endpoint)
"""

import os
from typing import TypedDict, List, Optional, Tuple, Any

from langchain_core.documents import Document
from rag.retriever import build_retriever

DISCLAIMER = (
    "This is a prototype research assistant, not a compliance authority. "
    "Every answer must be verified against official CPCB / MoEFCC "
    "notifications and reviewed by a qualified EPR consultant or "
    "environmental lawyer before you rely on it for an actual filing."
)

SYSTEM_PROMPT = """You are an authoritative legal research assistant for India's \
plastic waste Extended Producer Responsibility (EPR) regulations under the \
Plastic Waste Management Rules, 2016 (and MoEFCC / CPCB amendments).

Strict Rules You Must Obey (Zero Exceptions):
1. Scope & Source Grounding: Answer ONLY using the context chunks provided below. \
Do NOT assume or use outside knowledge, even if you believe you know the statutory rule.
2. Mandatory Citations: Cite the chunk ID (e.g. [kb007]) for every specific factual \
claim, definition, requirement, percentage, or rule.
3. Fiscal Year Precision: Always explicitly state the relevant Financial Year (FY) \
for every recycling target, recycled content threshold, or filing obligation you mention. \
If chunks show different targets across financial years, do not average or combine them -- \
list each FY separately.
4. Entity Scope: Explicitly state the entity type(s) (Producer, Importer, Brand Owner / PIBO, \
Seller, PWP) to which the rule applies.
5. Statutory Deadlines: If discussing deadlines or returns, always state the baseline rule \
clause (e.g. Rule 11.3) and any official circular/notification date mentioned in the context.
6. Confidence Tagging: If a chunk relied upon has confidence="needs_verify", you must \
explicitly warn the user with "⚠️ [NEEDS VERIFICATION]" alongside that claim.
7. Strict Abstention on Missing Info: If the provided chunks do not contain sufficient \
information to answer the question, state clearly: \
"The provided knowledge base does not contain sufficient statutory information to answer this question." \
Do NOT fill gaps with plausible guesses.
8. Verbatim Numeric Exactness: Never state a percentage, date, rupee figure, or clause \
number that does not appear verbatim in the provided context chunks.
9. Structured Format: Start your response with:
   **Applicable Scope:** [Entity Type(s) | Applicable FY(s)]
   Followed by clear, cited bullet points or paragraphs.

Context chunks:
{context}

Question: {question}

Structured Answer (with inline [chunk_id] citations):"""


class GraphState(TypedDict):
    question: str
    retrieved_docs: List[Document]
    answer: str
    mode: str


def get_active_llm() -> Tuple[str, Optional[Any]]:
    """
    Auto-detects and initialises the best available LLM provider.

    Priority:
      1. Groq          (GROQ_API_KEY)       -- free tier, extremely fast
      2. OpenRouter    (OPENROUTER_API_KEY) -- routes to free :free models
      3. Google Gemini (GEMINI_API_KEY / GOOGLE_API_KEY)
      4. Anthropic     (ANTHROPIC_API_KEY)
      5. OpenAI        (OPENAI_API_KEY)
      6. Mock mode     (no key needed)

    Override priority with LLM_PROVIDER=groq|openrouter|gemini|anthropic|openai
    """
    selected = (os.environ.get("LLM_PROVIDER") or "").strip().lower()

    # ── 1. Groq ────────────────────────────────────────────────────────────────
    # Free-tier models confirmed active Sep 2026:
    #   qwen/qwen3.8-27b       ← default (active, fast, free)
    #   openai/gpt-oss-20b     ← active lightweight, free
    #   openai/gpt-oss-120b    ← active large model, free
    groq_key = os.environ.get("GROQ_API_KEY")
    if (selected == "groq" or not selected) and groq_key:
        try:
            from langchain_groq import ChatGroq
            model_name = os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b")
            llm = ChatGroq(
                model_name=model_name,
                groq_api_key=groq_key,
                temperature=0,
                max_tokens=1024,
            )
            return f"live (Groq: {model_name})", llm
        except Exception as e:
            print(f"[warning] Groq init failed: {e}")
            if selected == "groq":
                return "mock", None

    # ── 2. OpenRouter ──────────────────────────────────────────────────────────
    # Free models (add :free suffix, zero cost, Sep 2026 confirmed active):
    #   deepseek/deepseek-r1:free         ← default (strong reasoning, free)
    #   qwen/qwq-32b:free                 ← Qwen reasoning model, free
    #   google/gemma-3-27b-it:free        ← Google Gemma 3, free
    #   deepseek/deepseek-chat:free       ← DeepSeek V3 chat, free
    #   mistralai/mistral-7b-instruct:free ← lightweight, very fast, free
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if (selected == "openrouter" or not selected) and openrouter_key:
        try:
            from langchain_openai import ChatOpenAI
            model_name = os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-r1:free")
            llm = ChatOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_key,
                model=model_name,
                temperature=0,
                max_tokens=1024,
                default_headers={
                    "HTTP-Referer": "https://epr-copilot.local",
                    "X-Title": "EPR Compliance Copilot",
                },
            )
            return f"live (OpenRouter: {model_name})", llm
        except Exception as e:
            print(f"[warning] OpenRouter init failed: {e}")
            if selected == "openrouter":
                return "mock", None

    # ── 3. Google Gemini ────────────────────────────────────────────────────────
    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if (selected == "gemini" or not selected) and gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=gemini_key,
                temperature=0,
                max_output_tokens=1024,
            )
            return f"live (Gemini: {model_name})", llm
        except Exception as e:
            print(f"[warning] Gemini init failed: {e}")
            if selected == "gemini":
                return "mock", None

    # ── 4. Anthropic Claude ─────────────────────────────────────────────────────
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if (selected == "anthropic" or not selected) and anthropic_key:
        try:
            from langchain_anthropic import ChatAnthropic
            model_name = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
            llm = ChatAnthropic(
                model=model_name,
                api_key=anthropic_key,
                temperature=0,
                max_tokens=1000,
            )
            return f"live (Claude: {model_name})", llm
        except Exception as e:
            print(f"[warning] Claude init failed: {e}")
            if selected == "anthropic":
                return "mock", None

    # ── 5. OpenAI ───────────────────────────────────────────────────────────────
    openai_key = os.environ.get("OPENAI_API_KEY")
    if (selected == "openai" or not selected) and openai_key:
        try:
            from langchain_openai import ChatOpenAI
            model_name = os.environ.get("OPENAI_MODEL", "gpt-4o")
            llm = ChatOpenAI(
                model=model_name,
                api_key=openai_key,
                temperature=0,
                max_tokens=1000,
            )
            return f"live (OpenAI: {model_name})", llm
        except Exception as e:
            print(f"[warning] OpenAI init failed: {e}")
            if selected == "openai":
                return "mock", None

    # ── 6. Fallback: Mock Mode ──────────────────────────────────────────────────
    return "mock", None


_GRAPH_CACHE: dict = {}
_ACTIVE_LLM_CACHE: Optional[Tuple[str, Optional[Any]]] = None


def get_cached_llm(force_reload: bool = False) -> Tuple[str, Optional[Any]]:
    """Returns cached (provider_label, llm) or initializes it once."""
    global _ACTIVE_LLM_CACHE
    if _ACTIVE_LLM_CACHE is None or force_reload:
        _ACTIVE_LLM_CACHE = get_active_llm()
    return _ACTIVE_LLM_CACHE


def get_llm_status() -> dict:
    """Returns provider status dict for the Flask frontend badge."""
    provider_name, _ = get_cached_llm()
    is_live = provider_name != "mock"
    return {
        "is_live": is_live,
        "provider": provider_name,
        "label": f"LIVE -- {provider_name.split('(')[1].rstrip(')')}" if is_live else "MOCK MODE -- no API key set",
    }


def retrieve_node(state: GraphState, retriever) -> GraphState:
    docs = retriever.invoke(state["question"])
    return {**state, "retrieved_docs": docs}


def _format_context(docs: List[Document]) -> str:
    lines = []
    for d in docs:
        m = d.metadata
        flag = " (NEEDS VERIFICATION)" if m.get("confidence") == "needs_verify" else ""
        lines.append(
            f"[{m['id']}] {m['title']}{flag}\nSource: {m['citation']}\n{d.page_content}"
        )
    return "\n\n".join(lines)


def generate_node_mock(state: GraphState) -> GraphState:
    """Mock mode: returns raw retrieved chunks with no API call."""
    docs = state["retrieved_docs"]
    if not docs:
        answer = "No relevant chunks found in the knowledge base for this question."
    else:
        parts = ["[MOCK MODE -- no API key configured, showing raw retrieved chunks]\n"]
        for d in docs:
            m = d.metadata
            flag = (
                "  <-- NEEDS VERIFICATION, do not treat as confirmed"
                if m.get("confidence") == "needs_verify"
                else ""
            )
            parts.append(
                f"[{m['id']}] {m['title']}{flag}\nSource: {m['citation']}\n{d.page_content}\n"
            )
        answer = "\n".join(parts)
    return {**state, "answer": answer, "mode": "mock"}


def generate_node_live(state: GraphState, llm, provider_name: str) -> GraphState:
    """Live mode: generates a cited, grounded answer via the configured LLM."""
    context = _format_context(state["retrieved_docs"])
    prompt = SYSTEM_PROMPT.format(context=context, question=state["question"])
    try:
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, "content") else str(response)
        return {**state, "answer": content, "mode": provider_name}
    except Exception as e:
        print(f"[warning] Live LLM call failed ({provider_name}): {e}. Falling back to mock generator.")
        mock_result = generate_node_mock(state)
        mock_result["mode"] = f"fallback_mock (error: {type(e).__name__})"
        return mock_result


def build_graph(k: int = 6):
    """Builds and compiles the LangGraph pipeline with dynamic model routing."""
    from langgraph.graph import StateGraph, END

    retriever = build_retriever(k=k)
    provider_name, llm = get_cached_llm()

    graph = StateGraph(GraphState)
    graph.add_node("retrieve", lambda s: retrieve_node(s, retriever))

    if llm is not None:
        graph.add_node("generate", lambda s: generate_node_live(s, llm, provider_name))
    else:
        graph.add_node("generate", generate_node_mock)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    return graph.compile()


def get_graph(k: int = 6, force_reload: bool = False):
    """Singleton getter for compiled LangGraph instance to prevent re-compilation per request."""
    global _GRAPH_CACHE
    if k not in _GRAPH_CACHE or force_reload:
        _GRAPH_CACHE[k] = build_graph(k=k)
    return _GRAPH_CACHE[k]


def ask(question: str, k: int = 6) -> dict:
    """Entry point: run the RAG pipeline once and return structured response."""
    app = get_graph(k=k)
    result = app.invoke({"question": question, "retrieved_docs": [], "answer": "", "mode": ""})

    citations = [
        {
            "id": d.metadata["id"],
            "title": d.metadata["title"],
            "citation": d.metadata["citation"],
            "confidence": d.metadata["confidence"],
        }
        for d in result["retrieved_docs"]
    ]

    return {
        "question": question,
        "answer": result["answer"],
        "citations": citations,
        "mode": result["mode"],
        "disclaimer": DISCLAIMER,
    }


if __name__ == "__main__":
    status = get_llm_status()
    print(f"Status: {status}")
    out = ask("What are the QR code labeling requirements for plastic packaging?")
    print(f"Mode: {out['mode']}\n")
    print(out["answer"])
    print("\nCitations:", [c["id"] for c in out["citations"]])
