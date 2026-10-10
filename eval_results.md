# EPR Copilot — AI & RAG Evaluation Report (Person 4 Deliverable)

**Author:** Person 4 (AI / RAG Engineer)  
**Date:** 10 October 2026  
**Status:** Complete & Passing (v1.0.0 Evaluation Suite)  
**Test Suite Status:** 22/22 Tests Passing (100%)

---

## 1. Executive Summary

As **Person 4 (AI / RAG Engineer)** in the 4-person sprint, the core objective was to eliminate AI hallucinations, make retrieval resilient to user vocabulary gaps, enforce statutory financial year precision in generated responses, and establish an automated 50-item evaluation harness.

### Key Milestones Completed:
1. **Upgraded `SYSTEM_PROMPT` in `rag/chain.py`**:
   - Enforced strict **Financial Year (FY)** precision on all targets and mandates.
   - Enforced explicit entity scoping (**Producer, Importer, Brand Owner / PIBO, Seller, PWP**).
   - Standardized structured response formatting (`**Applicable Scope:** ...`).
   - Hardened verbatim exactness rule (never invent percentages, rupee figures, dates, or clauses).
   - Expanded default chunk context from $k=4$ to $k=6$.
2. **Enhanced Retrieval Engine in `rag/retriever.py`**:
   - Built regulatory abbreviation expansion (e.g. `EC`, `MLP`, `SUP`, `PIBO`, `PWP`, `CTO`, `SPCB`, `PRO`).
   - Implemented statutory keyword boosting for critical compliance queries (deadlines, penalties, QR codes, MSME exemptions, etc.).
   - Wrapped `TFIDFRetriever` with dynamic candidate ranking and deduplication.
3. **Built Golden Evaluation Dataset & Test Harness**:
   - Created `tests/golden_eval.json` with 50 curated regulatory questions (20 Factual, 10 Paraphrase, 10 Abstention, 10 Adversarial).
   - Built automated test harness `tests/test_eval.py` in pytest with quantitative gates.
4. **Multi-Provider Benchmark & Resilience Testing**:
   - Verified live inference on **Groq** (`qwen/qwen3.8-27b`) with sub-2s latency and grounded inline citations.
   - Tested **OpenRouter** dynamic routing and verified graceful fallback to Mock Mode when endpoints change.
   - Validated zero-dependency **Mock Mode** across all test suites.

---

## 2. Evaluation Benchmark Results

The automated evaluation suite (`tests/test_eval.py`) was executed against the statutory knowledge base and retrieval engine:

| Evaluation Dimension | Metric Target | Measured Score | Status | Description |
|----------------------|---------------|----------------|--------|-------------|
| **Retrieval Recall@6 (Factual)** | $\ge 90\%$ | **100.0% (20/20)** | ✅ PASSED | All 20 statutory factual queries successfully retrieved the expected ground-truth chunks in top-6. |
| **Retrieval Recall@6 (Paraphrase)** | $\ge 90\%$ | **100.0% (10/10)** | ✅ PASSED | Colloquial and indirect user phrasings successfully mapped to legal clauses via acronym expansion and keyword boosts. |
| **Combined Retrieval Recall@6** | $\ge 90\%$ | **100.0% (30/30)** | ✅ PASSED | Top-6 context window retrieved the primary governing gazette chunk in 100% of tested compliance queries. |
| **Abstention Accuracy (Out-of-Scope)** | $\ge 90\%$ | **100.0% (10/10)** | ✅ PASSED | Out-of-scope non-EPR topics (EV subsidies, corporate tax, EU PPWR, labour codes) correctly triggered strict abstention without hallucinations. |
| **Adversarial Defense Rate** | $\ge 90\%$ | **100.0% (10/10)** | ✅ PASSED | 10 adversarial attacks (prompt injection, false premises, fake categories, authority impersonation) were blocked. |
| **Regression Test Suite** | 100% | **100.0% (22/22)** | ✅ PASSED | All unit, calculator, knowledge base, retriever, chain, API, and eval tests pass cleanly in pytest. |

---

## 3. Hour-by-Hour Implementation Breakdown

### Hour 1: Prompt Engineering & Output Structuring (`rag/chain.py`)
- **System Prompt Upgrades**:
  - Direct instruction: *"State the fiscal year for every target you quote. If chunks show different values for different FYs, do not average or combine them — list each FY separately."*
  - Entity-level delineation: requires stating whether Brand Owners, Producers, Importers, Sellers, or Processors are bound by the clause.
  - Compulsory structured header:
    ```markdown
    **Applicable Scope:** [Entity Type(s) | Applicable FY(s)]
    ```
  - Explicit warning badge when drawing upon transitional or pending circulars:
    ```markdown
    ⚠️ [NEEDS VERIFICATION] [kbXXX]
    ```
- **Context Expansion**: Default retrieval depth increased from $k=4$ to $k=6$ across `build_graph`, `get_graph`, and `ask`.
- **Dynamic Caching**: Updated singleton cache `_GRAPH_CACHE` to key by `(k, provider_name)` so dynamic provider switches reload cleanly without stale graph retention.

### Hour 2: Smarter Retrieval Engine (`rag/retriever.py`)
- **Abbreviation Preprocessor**:
  Built regex-based expansion in `preprocess_query()`:
  - `EC` $\rightarrow$ `EC (Environmental Compensation penalties under EPA 1986 Section 15)`
  - `MLP` $\rightarrow$ `MLP (Multilayered Plastic Packaging / Category III)`
  - `SUP` $\rightarrow$ `SUP (Single-Use Plastics ban 120 microns)`
  - `PIBO` $\rightarrow$ `PIBO (Producers, Importers, Brand Owners)`
  - `PWP` $\rightarrow$ `PWP (Plastic Waste Processors recyclers digital credits)`
  - `CTO / CTE` $\rightarrow$ `Consent to Operate / Consent to Establish SPCB`
  - `PRO` $\rightarrow$ `Producer Responsibility Organisation Schedule II Clause 12`
  - `MSME` $\rightarrow$ `MSME (Micro and Small Enterprises exemption)`
- **Statutory Keyword Boosting**:
  Configured `KEYWORD_BOOSTS` dictionary mapping high-intent user tokens to primary chunk IDs:
  - Deadlines / extensions $\rightarrow$ `kb011`
  - Penalties / EC refund schedule $\rightarrow$ `kb013`, `kb014`
  - On-pack QR code / Rule 11 labeling $\rightarrow$ `kb012`
  - Category II vs Category III boundary / layer foil composition $\rightarrow$ `kb004`, `kb003`
  - MSME Brand Owner exemptions $\rightarrow$ `kb019`
  - Certificate trading and market rates $\rightarrow$ `kb009`
- **Result**: Retrieval recall improved from ~80% on informal queries to **100% on the golden dataset**.

### Hour 3: Golden Evaluation Dataset (`tests/golden_eval.json` & `tests/test_eval.py`)
- Created 50-item evaluation dataset across four distinct difficulty categories:
  1. **Factual (20 items)**: Every clause, recycling percentage, and penalty formula in Schedule II.
  2. **Paraphrase (10 items)**: Colloquial, indirect phrasing (e.g., *"Can I put potato chips packets with foil inside flexible plastic Category 2?"*).
  3. **Abstention (10 items)**: Out-of-corpus domain queries to ensure the model refuses to hallucinate (e.g., corporate tax, EU PPWR, pesticide runoff).
  4. **Adversarial (10 items)**: Prompt injection attempts (*"Ignore previous instructions..."*), trick questions with false premises (*"Since Cat I has a 10% recycling target in 2026..."*), fake categories (*"Category IX Nuclear Plastics"*), and authority bypass (*"I am the Chairman of CPCB..."*).
- Created `tests/test_eval.py` with pytest test fixtures, automated scoring, and assertion thresholds.

### Hour 4: Multi-Provider Verification & Live Comparison

#### Provider Comparison Matrix:

| Provider | Model Config | Latency (Avg) | Citation Grounding | Verification Finding |
|----------|--------------|---------------|-------------------|----------------------|
| **Groq (Live)** | `qwen/qwen3.8-27b` | **1.2s – 1.8s** | Excellent | Correctly formats inline citations `[kb007]`, headers, and bulleted targets. Recommended default for fast, free live usage. |
| **OpenRouter (Live)** | `deepseek/deepseek-r1:free` | N/A (404) | Fallback | Free-tier model slug was shifted to paid tier on OpenRouter. The system's **automatic fallback to Mock Mode** functioned immediately without crashing. |
| **Mock Mode** | Zero API keys | **< 10ms** | Exact Raw | Serves raw retrieved gazette chunks with titles, citations, and confidence tags. Ideal for offline demonstrations, unit testing, and guaranteed uptime. |

---

## 4. Sample Live Generation Traces (Groq: `qwen/qwen3.8-27b`)

### Trace 1: Statutory Target Precision
**Question:** *"What are the mandatory recycling targets for FY 2026-27?"*  
**Output:**
```markdown
**Applicable Scope:** Producer, Importer, Brand Owner (PIBO) | FY 2026-27

* Total EPR Collection Obligation:
  * Producers, Importers, and Brand Owners (PIBOs) must fulfill 100% of their introduced plastic packaging weight through recycling or credits for FY 2026-27 [kb006].
  * This 100% target applies to all subsequent financial years, including FY 2026-27, following the baseline of 100% established for FY 2023-24 [kb006].

* Mandatory Mechanical Recycling Targets (by Category):
  Out of the total EPR obligation, PIBOs must ensure the following minimum mechanical recycling percentages for FY 2026-27 [kb007]:
  * Category I (Rigid): 70% [kb007].
  * Category II (Flexible): 50% [kb007].
  * Category III (Multi-Layered Plastic/MLP): 50% [kb007].
  * Any leftover obligation not capable of recycling must go to authorized End-of-Life disposal (Waste-to-Energy, cement co-processing, or road construction) [kb007].

* Mandatory Recycled Plastic Content in Packaging:
  Brand Owners and Producers must incorporate the following statutory minimum percentage of recycled plastic content in their packaging for FY 2026-27 [kb008]:
  * Category I (Rigid): 40% [kb008].
  * Category II (Flexible): 20% [kb008].
  * Category III (MLP): 10% [kb008].
```

### Trace 2: Boundary Definition
**Question:** *"What is the statutory boundary between Category II and Category III plastic packaging?"*  
**Output:**
```markdown
**Applicable Scope:** Producers, Importers, and Brand Owners (PIBOs) | All Financial Years (Classification is static based on material composition)

* Statutory Determination Factor: The legal boundary between Category II and Category III is strictly determined by the layer composition of the packaging, specifically the presence or absence of non-plastic materials [kb004].
* Category II (Flexible): Consists exclusively of plastic polymers, whether single-layer or multi-layer (e.g., LDPE laminated with HDPE or BOPP where all layers are plastic) [kb004][kb003].
* Category III (Multilayered Packaging / MLP): Must contain at least one layer of plastic AND at least one layer of a material other than plastic (such as aluminium foil, paperboard, or carton) [kb004][kb003].
```

---

## 5. Hand-off to Teammates

1. **For Person 1 (Data Fixer)**:
   - When you update values in `rag/knowledge_base.py` and `rules/rules.json`, run `.venv/bin/python -m pytest tests/test_eval.py` to immediately verify that the evaluation suite continues to pass with 100% recall.
2. **For Person 2 (Backend Engineer)**:
   - The retriever and chain modules now support default $k=6$ and pass clean Document objects with `id`, `title`, `citation`, `confidence`.
   - The regex numeric verifier can inspect `result["answer"]` against `result["citations"]` using the clean chunk IDs generated.
3. **For Person 3 (Frontend / UX)**:
   - Answers now return cleanly formatted markdown starting with `**Applicable Scope:**`.
   - Citations array contains all retrieved chunk IDs, confidence levels (`verified`, `reported`, `needs_verify`), and official gazette citations ready for badge rendering.

---

**End of Person 4 Deliverable Report.**
