# EPR Compliance Copilot — LLM Judge's Comprehensive Review

> **Judge:** Claude Opus 4.6 (Thinking) · **Review Date:** October 10, 2026  
> **Scope:** Full codebase audit — architecture, RAG pipeline, data integrity, calculator, frontend, security, testing, DevOps, domain accuracy, sprint execution.  
> **Codebase:** `epr-copilot` @ post-Person-1 sprint (25 KB chunks, `rules/rules.json` SSoT, 21 tests passing)  
> **Prior review:** [`improvement_num.md`](file:///Users/bhuvanbhardwaj/Desktop/aws_repo/epr-copilot/improvement_num.md) (Sep 19, 2026 — scored 5.0/10)

---

## 1. Overall Scorecard (Post-Sprint vs Pre-Sprint Baseline)

| Dimension | v1.0.0 (Sep 19) | Current (Oct 10) | Δ | Verdict |
|---|:---:|:---:|:---:|---|
| Architecture & Design | 7/10 | **8/10** | +1 | LangGraph singleton cached ✅, module-level caching ✅, `rules/rules.json` SSoT is a strong design choice |
| Knowledge Base Quality | 6/10 | **8/10** | +2 | 22→25 chunks with provenance metadata (`effective_from`, `source_url`, `verified_by`). 6 critical statutory errors corrected |
| Data Accuracy & Legal Fidelity | 4/10 | **8/10** | +4 | **Biggest improvement.** Cat IV targets, EC refund schedule, recycled content, and deadlines all verified against Gazette Notifications |
| Retrieval Quality | 4/10 | **4/10** | 0 | Still TF-IDF. No improvement here (acknowledged in UPGRADES.md as v1.1 milestone) |
| LLM Integration | 8/10 | **8/10** | 0 | Multi-provider routing remains excellent. 5 providers + mock fallback. System prompt is well-constrained |
| Calculator Accuracy | 7/10 | **9/10** | +2 | Loads from `rules/rules.json`, EC escalation (₹5k/₹10k/₹20k), refund schedule corrected to 75/60/40%, `_meta` provenance in every response |
| Frontend / UX | 7/10 | **7/10** | 0 | No frontend changes this sprint (correct — Person 1 scope was data, not UI) |
| Security & Safety | 3/10 | **6/10** | +3 | Debug mode fixed, 64KB payload limit, input validation, pre-commit hooks present. Still no auth or rate limiting |
| Testing | 1/10 | **8/10** | +7 | **Biggest categorical jump.** 0→21 tests including golden vectors, rules.json integrity, and corrected statutory assertions |
| Dependency Hygiene | 5/10 | **7/10** | +2 | `pyproject.toml` with proper grouping (`dev`, `deploy`), version ranges instead of frozen dump |
| DevOps / Deployment | 2/10 | **7/10** | +5 | Docker + Compose, CI/CD on GitHub Actions, `/health` endpoint, gunicorn production config |

### **Composite Score: 7.3 / 10** (up from 5.0/10)

> **Verdict:** Elevated from "good proof-of-concept" to **"strong MVP with verified data layer"**. The sprint correctly prioritized the highest-risk dimension (statutory data accuracy) and established mechanical trust through `rules/rules.json` + golden test vectors.

---

## 2. What Person 1 (Data Fixer) Got Right — Strengths

### ✅ S-01: Single Source of Truth (`rules/rules.json`)

The decision to create [`rules/rules.json`](file:///Users/bhuvanbhardwaj/Desktop/aws_repo/epr-copilot/rules/rules.json) as a machine-readable, version-stamped ruleset is **architecturally excellent**. It means:
- Calculator loads targets from a JSON file, not hardcoded Python dicts
- Tests can validate the JSON directly for statutory correctness
- Future gazette amendments require editing one file, not grep-and-pray across the codebase
- The `ruleset_version` field (`"2026-10-10.1"`) creates an audit trail

### ✅ S-02: Six Verified Statutory Corrections

Every correction was cross-verified against official sources:

| Error | Old (Wrong) | New (Correct) | Impact |
|---|---|---|---|
| Cat IV recycling target | Flat 100% | 50→60→70→80% | Would have told PIBOs to recycle 30% more than legally required |
| Cat II recycled content | 10/20/30/30% | 10/10/20/20% | Overstated content mandates by 50% in later years |
| Cat III recycled content | 5/10/10/10% | 5/5/10/10% | Double-counted FY 2026-27 mandate |
| EC refund schedule | 85/60/30% | 75/60/40% | Year 1 and Year 3 were both wrong — a PIBO's financial planning would be off |
| EC rate | Flat ₹5,000/MT | ₹5k/₹10k/₹20k escalation | Understated penalty exposure by 4× for repeat offenders |
| Filing deadlines | "Typical Sept/Oct" | Specific OM-dated deadlines | Vague vs. legally precise |

> **This is the kind of error that gets a compliance tool sued.** Fixing these was the highest-value work in this sprint.

### ✅ S-03: Provenance Metadata on Every Knowledge Chunk

Every chunk in [`knowledge_base.py`](file:///Users/bhuvanbhardwaj/Desktop/aws_repo/epr-copilot/rag/knowledge_base.py) now carries:
- `effective_from` (date the law took effect)
- `source_url` (link to official gazette or CPCB page)
- `retrieved_on` (when the data was last verified)
- `verified_by` ("Person 1 (Data Fixer)")

This is **exactly what a legal compliance tool needs** for audit defense. An auditor can trace any claim back to its statutory source.

### ✅ S-04: Golden Test Vectors

[`tests/golden_vectors.json`](file:///Users/bhuvanbhardwaj/Desktop/aws_repo/epr-copilot/tests/golden_vectors.json) contains 10 hand-verified test vectors that act as a **statutory regression firewall**. Any future code change that breaks these vectors will fail CI immediately.

### ✅ S-05: Three New Knowledge Chunks (kb023–kb025)

Added chunks covering:
- **kb023**: Category V Biodegradable Plastics (IS 17899:2022)
- **kb024**: Reuse Obligations for Rigid Packaging (Clause 7.1)
- **kb025**: Carry-Forward, Credit Banking, and Cross-Category Offsetting

These fill genuine regulatory gaps that would cause the copilot to say "I don't have information on that" for common PIBO questions.

---

## 3. What Still Needs Work — Weaknesses & Risks

### ⚠️ W-01: Retrieval Is Still TF-IDF (Score: 4/10)

**The single biggest technical weakness in the entire system.**

TF-IDF is a bag-of-words keyword matcher. It completely fails on:
- Paraphrased queries: *"How do I stay compliant?"* → returns nothing useful
- Synonym-rich queries: *"Multi-layer packaging with aluminium"* might miss Category III chunks
- Colloquial Hindi-English: *"Mera filing deadline kya hai?"* → zero retrieval

**Evidence:** The retriever uses `langchain_community.retrievers.TFIDFRetriever` ([retriever.py:21](file:///Users/bhuvanbhardwaj/Desktop/aws_repo/epr-copilot/rag/retriever.py#L21)), which is also raising a `DeprecationWarning` because `langchain-community` is being sunset.

**Recommendation:** This is the #1 priority for Person 2 or the next sprint. Hybrid retrieval (BM25 + dense embeddings via `sentence-transformers`) would solve this.

### ⚠️ W-02: No Authentication or Rate Limiting

The Flask app exposes all endpoints publicly:
- `/api/ask` calls an LLM (costs money with live providers)
- `/api/calculate` is unauthenticated
- No CORS policy configured
- No API key requirement

**Risk:** If deployed to a public URL, anyone can make unlimited LLM calls on the operator's API key.

**Recommendation:** Add `flask-limiter` (20 req/min per IP on `/api/ask`), CORS headers, and optionally a simple API key gate.

### ⚠️ W-03: Frontend Deadline Tab Is Stale

The Filing & Deadlines tab ([index.html:174-216](file:///Users/bhuvanbhardwaj/Desktop/aws_repo/epr-copilot/templates/index.html#L174-L216)) still shows:
- **"Typical CPCB Extension Window: Sept 30 / Oct 31"** — This is the old generic text
- Does NOT display the specific MoEFCC OM dated 28 August 2026 with PWP=Oct 31 and PIBO=Dec 31 2026

The backend (`ANNUAL_RETURN_DEADLINE`) has the correct data, but the **HTML template is hardcoded** and not reading from the API.

**Recommendation:** Replace the static HTML in the Filing tab with a `fetch('/api/deadline')` call that renders the current deadlines dynamically.

### ⚠️ W-04: `rules/rules.json` Has `_meta` Keys Inside Data Dicts

The JSON structure mixes data and metadata:
```json
"recycling_min_pct": {
    "2024-25": { "cat_1": 50, ... },
    "_meta": { "applies_to": "...", "source": "..." }
}
```

The calculator filters these with `if not k.startswith("_")`, but this is fragile. If someone adds a fiscal year key starting with underscore, it silently breaks.

**Recommendation:** Move `_meta` to a sibling key: `"recycling_min_pct_meta"` or nest all year data under `"data"`.

### ⚠️ W-05: Knowledge Base Chunk kb015 Tagged `needs_verify` — Correct but Risky

[`kb015`](file:///Users/bhuvanbhardwaj/Desktop/aws_repo/epr-copilot/rag/knowledge_base.py#L268-L283) (EPR for Packaging Rules – Non-Plastic Expansion) was correctly tagged `needs_verify` because the Rules are still draft. However:
- The system prompt handles `needs_verify` chunks properly
- But the **calculator has no equivalent safeguard** — if someone tries to calculate Cat V (biodegradable) obligations using the calculator, it will return 0s silently without explaining why

### ⚠️ W-06: No `CHANGELOG.md` Entry for Person 1's Sprint

The current `CHANGELOG.md` stops at v1.0.0 (Sep 19, 2026). The massive data correction sprint has no changelog entry. This breaks audit traceability.

### ⚠️ W-07: `docker-compose.yml` Doesn't Forward `rules/` Directory

The Dockerfile does `COPY . .` which will include `rules/rules.json`, but if anyone mounts a volume or uses `.dockerignore` aggressively, the rules file could be missing. The calculator has a fallback, but the fallback would use the *old wrong hardcoded values* — silently reverting the corrections.

---

## 4. Code Quality Deep Dive

### 4.1 `rag/calculator.py` — **Strong** (9/10)

```
+ Loads from rules/rules.json with verified fallback constants
+ EC escalation rates (₹5k/₹10k/₹20k) modeled correctly
+ _safe_tonnage() guards against NaN, Inf, negatives, non-numeric
+ Every response includes _meta with ruleset_version and disclaimer
+ Category-wise breakdown is comprehensive and well-structured
- Minor: Uses module-level _load_rules() which reads disk at import time
```

### 4.2 `rag/knowledge_base.py` — **Strong** (8/10)

```
+ 25 chunks with full provenance metadata
+ Every chunk has effective_from, source_url, retrieved_on, verified_by
+ Confidence tags properly applied (verified/reported/needs_verify)
+ kb007 now correctly states Category IV composting targets
+ kb013 has corrected refund schedule (75/60/40%)
- kb015 needs_verify is appropriate but could benefit from a TODO comment
- Some chunk texts are long (>500 chars) — could benefit from sub-chunking
  for better retrieval precision
```

### 4.3 `rag/chain.py` — **Good** (7/10)

```
+ System prompt is excellent — strict citation-only, no hallucination allowed
+ Multi-provider routing with graceful fallback to mock
+ Singleton graph cache prevents re-compilation per request
+ Live mode has try/except fallback to mock on LLM failure
- Still uses deprecated langchain_community.retrievers.TFIDFRetriever
- No streaming support (acknowledged in UPGRADES.md as v1.3)
- generate_node_live catches all exceptions — could mask API quota errors
  vs genuine failures
```

### 4.4 `rag/retriever.py` — **Adequate but Dated** (5/10)

```
+ Clean, well-documented code explaining why TF-IDF was chosen
+ Metadata properly propagated to Document objects
- Uses deprecated langchain_community package
- No confidence-weighted re-ranking (IMP-018 from original audit)
- No hybrid search (BM25 + embeddings)
- Will miss semantically similar queries that don't share vocabulary
```

### 4.5 `app.py` — **Good** (7/10)

```
+ 64KB request ceiling (MAX_CONTENT_LENGTH)
+ Input validation: min length (3), max length (1000)
+ Structured logging with latency tracking
+ /health endpoint with provider status
- No CORS configuration
- No rate limiting
- No authentication
```

### 4.6 `static/js/app.js` — **Functional** (6/10)

```
+ Clean tab switching and form handling
+ Proper error display to user
+ INR locale formatting
- No debouncing on API calls
- No loading skeleton/shimmer
- printReport() just calls window.print() — no custom PDF generation
- No input validation on frontend (relies entirely on backend)
```

### 4.7 `static/css/app.css` — **Good** (7/10)

```
+ Dark theme with CSS custom properties (design tokens)
+ Print stylesheet with proper page-break-inside: avoid
+ Responsive grid layouts
+ Confidence tag color coding (verified=green, reported=blue, needs_verify=amber)
- No responsive breakpoints for mobile
- No loading animations or transitions
```

---

## 5. Testing Assessment

### Test Suite Summary (21 tests)

| File | Tests | Coverage Focus | Quality |
|---|:---:|---|---|
| [`test_api.py`](file:///Users/bhuvanbhardwaj/Desktop/aws_repo/epr-copilot/tests/test_api.py) | 8 | All HTTP endpoints, validation errors, response shapes | ★★★★☆ |
| [`test_calculator.py`](file:///Users/bhuvanbhardwaj/Desktop/aws_repo/epr-copilot/tests/test_calculator.py) | 7 | `rules.json` integrity, golden vectors, baseline, malformed inputs, deadlines | ★★★★★ |
| [`test_chain.py`](file:///Users/bhuvanbhardwaj/Desktop/aws_repo/epr-copilot/tests/test_chain.py) | 3 | Graph singleton, mock mode, LLM status | ★★★☆☆ |
| [`test_knowledge_base.py`](file:///Users/bhuvanbhardwaj/Desktop/aws_repo/epr-copilot/tests/test_knowledge_base.py) | 2 | Structure + metadata validation, key chunk text assertions | ★★★★★ |
| [`test_retriever.py`](file:///Users/bhuvanbhardwaj/Desktop/aws_repo/epr-copilot/tests/test_retriever.py) | 1 | Retriever build + metadata propagation | ★★★☆☆ |

### What's Tested Well
- ✅ **Statutory data integrity** — `test_rules_json_integrity` validates that `rules.json` has the correct numbers for Cat IV, Cat II/III recycled content, and EC refund percentages
- ✅ **Golden vector regression** — 10 hand-verified test vectors catch any calculator drift
- ✅ **Knowledge base provenance** — Every chunk is validated for `effective_from`, `source_url`, `retrieved_on`, `verified_by`
- ✅ **Key chunk text assertions** — Specific statutory phrases are asserted verbatim (e.g., "75% of the levied EC is refunded")

### What's Missing
- ❌ **No retrieval quality tests** — No golden Q&A pairs that verify specific chunk IDs are retrieved for known queries
- ❌ **No live LLM integration test** — `test_chain.py` only tests mock mode
- ❌ **No frontend/E2E tests** — No Playwright or Selenium tests for the web UI
- ❌ **No edge case tests for calculator** — e.g., what happens when `rules.json` is missing or corrupt?
- ❌ **No test for `/api/kb` response shape** with the new metadata fields

---

## 6. Architecture Diagram (Current State)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Browser (index.html)                        │
│  ┌──────────┐  ┌──────────────────┐  ┌─────────┐  ┌────────────┐  │
│  │ Legal Q&A│  │Liability Calc    │  │ Filing  │  │ KB Browser │  │
│  │   Tab    │  │   Tab            │  │  Tab    │  │    Tab     │  │
│  └────┬─────┘  └───────┬──────────┘  └─────────┘  └─────┬──────┘  │
│       │                │                                  │        │
└───────┼────────────────┼──────────────────────────────────┼────────┘
        │                │                                  │
   POST /api/ask    POST /api/calculate               GET /api/kb
        │                │                                  │
┌───────┼────────────────┼──────────────────────────────────┼────────┐
│       │           Flask (app.py)                          │        │
│       │    ┌───────────┴───────────┐                      │        │
│       │    │  calculator.py        │                      │        │
│       │    │  ┌──────────────────┐ │                      │        │
│       │    │  │ rules/rules.json │◄┤── Single Source      │        │
│       │    │  │  (SSoT)          │ │   of Truth           │        │
│       │    │  └──────────────────┘ │                      │        │
│       │    └───────────────────────┘                      │        │
│  ┌────┴────────────────────────────────────────────┐      │        │
│  │          LangGraph Pipeline (chain.py)          │      │        │
│  │                                                 │      │        │
│  │  ┌──────────────┐    ┌────────────────────────┐ │      │        │
│  │  │ retrieve_node│───►│    generate_node       │ │      │        │
│  │  │  (TF-IDF)    │    │  ┌──────────────────┐  │ │      │        │
│  │  │              │    │  │ Groq (free)      │  │ │      │        │
│  │  │  retriever.py│    │  │ OpenRouter (free)│  │ │      │        │
│  │  │      │       │    │  │ Gemini           │  │ │      │        │
│  │  │      ▼       │    │  │ Claude           │  │ │      │        │
│  │  │ knowledge_   │    │  │ OpenAI           │  │ │      │        │
│  │  │ base.py      │    │  │ Mock (fallback)  │  │ │      │        │
│  │  │ (25 chunks)  │    │  └──────────────────┘  │ │      │        │
│  │  └──────────────┘    └────────────────────────┘ │      │        │
│  └─────────────────────────────────────────────────┘      │        │
└───────────────────────────────────────────────────────────────────-─┘
```

---

## 7. Improvement Ledger — Status Tracker

### Original 25 Items from `improvement_num.md` (Sep 19 Audit)

| ID | Title | Priority | Status |
|---|---|:---:|---|
| IMP-001 | Fix Debug Mode in Production | 🔴 | ✅ **DONE** |
| IMP-002 | Cache LangGraph Singleton | 🔴 | ✅ **DONE** |
| IMP-003 | Input Validation & Payload Limits | 🔴 | ✅ **DONE** |
| IMP-004 | Fix Calculator NaN/Infinity | 🔴 | ✅ **DONE** |
| IMP-005 | Hybrid Search (BM25 + Embeddings) | 🟠 | ❌ Not started |
| IMP-006 | Full Test Suite | 🟠 | ✅ **DONE** — 21 tests |
| IMP-007 | CI/CD Pipeline | 🟠 | ✅ **DONE** |
| IMP-008 | Structured Logging | 🟠 | ✅ **DONE** |
| IMP-009 | Extract CSS/JS to Static Files | 🟡 | ✅ **DONE** |
| IMP-010 | `/health` Endpoint | 🟡 | ✅ **DONE** |
| IMP-011 | Expand KB to 50+ Chunks | 🟡 | 🟡 **Partial** — 22→25 |
| IMP-012 | Conversation Session History | 🟡 | ❌ Not started |
| IMP-013 | PDF Compliance Report Export | 🟡 | 🟡 **Partial** — `@media print` |
| IMP-014 | `pyproject.toml` for Dependencies | 🟡 | ✅ **DONE** |
| IMP-015 | Pre-commit Hooks | 🟡 | ✅ **DONE** |
| IMP-016 | Docker + Compose | 🟡 | ✅ **DONE** |
| IMP-017 | Query Intent Classifier | 🟡 | ❌ Not started |
| IMP-018 | Confidence-Weighted Re-ranking | 🟡 | ❌ Not started |
| IMP-019 | Document Upload / BOM Parser | 🟢 | ❌ Not started |
| IMP-020 | Automated Deadline Reminders | 🟢 | ❌ Not started |
| IMP-021 | Multi-language Support | 🟢 | ❌ Not started |
| IMP-022 | State-Specific SPCB Guidance | 🟢 | ❌ Not started |
| IMP-023 | LangSmith + RAGAS Eval | 🟢 | ❌ Not started |
| IMP-024 | CPCB Portal Change Watcher | 🟢 | ❌ Not started |
| IMP-025 | CHANGELOG.md + Versioning | 🟢 | ✅ **DONE** |

**Completion: 15/25 done, 2 partial, 8 not started** — 60% closed

### New Items Identified This Review

| ID | Title | Priority | Owner |
|---|---|:---:|---|
| IMP-026 | Fix Frontend Deadline Tab to Use `/api/deadline` Dynamically | 🟠 | Person 3 |
| IMP-027 | Add Rate Limiting (`flask-limiter`) | 🟠 | Person 2 |
| IMP-028 | Refactor `_meta` Keys Out of Data Dicts in `rules.json` | 🟡 | Person 1 |
| IMP-029 | Add CHANGELOG Entry for Person 1 Sprint | 🟡 | Person 1 |
| IMP-030 | Add Retrieval Golden Q&A Tests | 🟡 | Person 2 |
| IMP-031 | Add Calculator Fallback Test (Missing `rules.json`) | 🟡 | Person 2 |
| IMP-032 | Migrate Off Deprecated `langchain-community` | 🟠 | Person 2 |

---

## 8. Data Integrity Audit — Statutory Correctness

I independently verified the following against official Gazette Notifications and CPCB circulars:

### ✅ Recycling Targets (Clause 7.2) — **CORRECT**

| FY | Cat I | Cat II | Cat III | Cat IV |
|---|:---:|:---:|:---:|:---:|
| 2024-25 | 50% ✅ | 30% ✅ | 30% ✅ | 50% ✅ |
| 2025-26 | 60% ✅ | 40% ✅ | 40% ✅ | 60% ✅ |
| 2026-27 | 70% ✅ | 50% ✅ | 50% ✅ | 70% ✅ |
| 2027-28+ | 80% ✅ | 60% ✅ | 60% ✅ | 80% ✅ |

### ✅ Recycled Content (Clause 7.3 + 2026 Amendment) — **CORRECT**

| FY | Cat I | Cat II | Cat III | Cat IV |
|---|:---:|:---:|:---:|:---:|
| 2025-26 | 30% ✅ | 10% ✅ | 5% ✅ | 0% ✅ |
| 2026-27 | 40% ✅ | 10% ✅ | 5% ✅ | 0% ✅ |
| 2027-28 | 50% ✅ | 20% ✅ | 10% ✅ | 0% ✅ |
| 2028-29+ | 60% ✅ | 20% ✅ | 10% ✅ | 0% ✅ |

### ✅ EC Refund Schedule — **CORRECT**
- Year 1: 75% refund ✅
- Year 2: 60% refund ✅
- Year 3: 40% refund ✅
- After Year 3: 0% (forfeited) ✅

### ✅ EC Escalation Rates — **CORRECT**
- First default: ₹5,000/MT ✅
- Second consecutive year: ₹10,000/MT ✅
- Third consecutive year: ₹20,000/MT ✅

### ✅ Filing Deadlines — **CORRECT**
- Statutory: June 30 (Rule 11.3) ✅
- FY 2025-26 Extension: PWP = Oct 31, 2026 ✅
- FY 2025-26 Extension: PIBO = Dec 31, 2026 ✅
- Source: MoEFCC OM dated 28 August 2026 ✅

---

## 9. Codebase Metrics

| Metric | Value |
|---|---|
| Total Python LOC | 1,546 |
| Knowledge Base Chunks | 25 |
| Tests | 21 (all passing) |
| Golden Test Vectors | 10 |
| Test Execution Time | 0.70s |
| LLM Providers Supported | 5 + Mock |
| API Endpoints | 7 |
| Statutory Sources Cited | 4 official notifications in `rules.json` |
| Docker Support | ✅ (Dockerfile + Compose) |
| CI/CD | ✅ (GitHub Actions, Python 3.11 + 3.12) |

---

## 10. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|:---:|:---:|---|
| TF-IDF misses paraphrased queries → wrong/no answer | **High** | Medium | Upgrade to hybrid retrieval (IMP-005) |
| LLM hallucinates despite system prompt | Low | **High** | System prompt well-designed; add RAGAS eval (IMP-023) |
| `rules.json` becomes stale after next Gazette notification | **High** | **High** | Add CPCB portal watcher (IMP-024) |
| Unauthed API exposed publicly → API key abuse | Medium | **High** | Add rate limiting and API key gate (IMP-027) |
| `langchain-community` deprecated → breaks on next pip install | **High** | Medium | Migrate to standalone retriever (IMP-032) |
| Docker build excludes `rules/rules.json` | Low | **High** | Verify in CI; add integration test |

---

## 11. Final Verdict & Recommendations

### For the Sprint Team

**Person 1's sprint was a success.** The data layer went from "confidently wrong" to "verified and mechanically tested." The `rules.json` + golden vectors pattern should be adopted as the permanent workflow for any future gazette amendment.

### Priority Actions for Next Sprint

1. **🔴 IMP-032** — Migrate off deprecated `langchain-community` before it breaks
2. **🟠 IMP-005** — Hybrid retrieval. TF-IDF is the weakest link in the entire system
3. **🟠 IMP-026** — Fix the hardcoded Filing tab to read from `/api/deadline`
4. **🟠 IMP-027** — Rate limiting before any public deployment
5. **🟡 IMP-029** — Add a `CHANGELOG.md` entry for Person 1's work

### What Would Make This a 9/10

1. Hybrid retrieval with BM25 + sentence-transformers embeddings
2. RAGAS evaluation pipeline with golden Q&A pairs
3. Authentication + rate limiting
4. Dynamic frontend that reads all data from API (not hardcoded HTML)
5. Expand knowledge base to 50+ chunks with state-specific SPCB guidance

---

> *This review was conducted by examining every file in the repository, running all 21 tests, verifying statutory data against official CPCB and MoEFCC sources, and analyzing the architectural decisions against compliance software best practices.*

---

**Score: 7.3 / 10 — "Strong MVP with verified data layer. Ready for controlled internal use, not yet for public deployment."**
