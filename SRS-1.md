# Software Requirements Specification (SRS)

## EPR Compliance Copilot v1.0.0

**Document Version:** 1.0  
**Date:** October 2026  
**Status:** Implemented (v1.0.0 live)  

---

## 1. Introduction

### 1.1 Purpose

This document specifies the functional, non-functional, and system requirements for the **EPR Compliance Copilot** — an AI-powered research assistant and liability calculator for India's plastic waste Extended Producer Responsibility (EPR) regulations.

### 1.2 Scope

The system provides:
- A citation-grounded legal Q&A engine over Indian plastic waste EPR statutory rules
- A deterministic obligation and penalty calculator for Producers, Importers, Brand Owners (PIBOs), and Sellers
- A CPCB portal registration readiness checklist
- An audit-ready PDF/print report export

The system does **not**:
- Connect to or interact with the live CPCB portal
- File returns or submissions on behalf of users
- Provide legally binding advice
- Process payments or handle EPR certificate trading

### 1.3 Intended Users

| User Type | Description | Primary Use |
|-----------|------------|-------------|
| **Compliance Manager** | Corporate sustainability/legal teams at FMCG, pharma, e-commerce companies | Q&A, calculator, checklist |
| **Brand Owner / Producer** | Business owners introducing plastic packaging into market | Calculator, penalty estimation |
| **Importer** | Entities importing products with plastic packaging | Regulatory Q&A, registration checklist |
| **EPR Consultant** | Advisory professionals serving multiple PIBO clients | Client demos, quick reference |
| **Environmental Auditor** | CPCB-empanelled auditors verifying compliance | Knowledge base reference |

### 1.4 Definitions & Acronyms

| Term | Meaning |
|------|---------|
| **EPR** | Extended Producer Responsibility |
| **PIBO** | Producer, Importer, Brand Owner (obligated entities) |
| **CPCB** | Central Pollution Control Board |
| **SPCB/PCC** | State Pollution Control Board / Pollution Control Committee |
| **MoEFCC** | Ministry of Environment, Forest & Climate Change |
| **PWM Rules** | Plastic Waste Management Rules, 2016 (and amendments) |
| **EC** | Environmental Compensation (penalty) |
| **PRO** | Producer Responsibility Organisation |
| **PWP** | Plastic Waste Processor (recycler) |
| **MLP** | Multi-Layered Plastic packaging |
| **RAG** | Retrieval-Augmented Generation |
| **MT** | Metric Tonnes |
| **FY** | Financial Year (April–March) |

### 1.5 Regulatory References

| Reference | Relevance |
|-----------|-----------|
| Plastic Waste Management Rules, 2016 (MoEFCC) | Base framework |
| Schedule II — G.S.R. 133(E), 16 Feb 2022 | EPR targets, categories, penalties |
| PWM Amendment Rules, 2024 | Non-plastic EPR expansion |
| PWM Amendment Rules, 2025 (Rule 11) | QR code / barcode labeling mandate |
| PWM Amendment Rules, 2026 | Sellers, traceability, registered auditors |
| Environment (Protection) Act, 1986, Section 15 | Penalty and prosecution provisions |

---

## 2. Overall Description

### 2.1 System Context

```
┌─────────────────────────────────────────────────┐
│                    User (Browser)                │
│  Ask questions · Enter tonnages · View reports   │
└──────────────────────┬──────────────────────────┘
                       │ HTTP (port 5000)
                       ▼
┌─────────────────────────────────────────────────┐
│               Flask Web Server                   │
│  Routes: /api/ask, /api/calculate, /health, etc │
├──────────────┬──────────────────┬───────────────┤
│  RAG Pipeline│  Calculator      │  Knowledge    │
│  (LangGraph) │  Engine          │  Base         │
│              │  (deterministic) │  (22 chunks)  │
├──────────────┤                  │               │
│  TF-IDF      │                  │               │
│  Retriever   │                  │               │
├──────────────┘                  └───────────────┤
│                                                  │
│  LLM Provider (external API, optional)           │
│  Groq / OpenRouter / Gemini / Claude / OpenAI    │
└──────────────────────────────────────────────────┘
```

### 2.2 Operating Environment

- **Runtime:** Python 3.11+
- **Server:** Flask (dev), Gunicorn (prod)
- **Container:** Docker (Python 3.12-slim base)
- **Client:** Any modern browser (Chrome, Firefox, Safari, Edge)
- **Deployment:** Local, Docker, or cloud VM
- **External Dependencies:** Optional LLM API (works without any)

### 2.3 Design Constraints

| Constraint | Rationale |
|-----------|-----------|
| Must work with zero API keys | Accessibility — users in India may lack paid API access |
| Knowledge base must be manually curated | Legal accuracy — no auto-scraping of statutory text |
| Calculator must be deterministic | Statutory math cannot have AI variability |
| All answers must carry citations | Auditability — every claim traceable to source |
| No user data persisted | Privacy — no database, no session storage, no logs of questions |

### 2.4 Assumptions

1. Users have basic understanding of EPR concepts (Producer, Importer, Brand Owner)
2. Users can estimate their plastic packaging tonnage by category
3. Knowledge base reflects rules as of September 2026
4. LLM providers maintain their current free-tier offerings
5. Statutory targets beyond FY 2028-29 follow the same trajectory (80%+ recycling)

---

## 3. Functional Requirements

### 3.1 Legal Q&A Assistant

| ID | Requirement | Priority |
|----|------------|----------|
| **FR-Q01** | System shall accept natural language questions (3–1000 characters) about EPR regulations | Must |
| **FR-Q02** | System shall retrieve top-k (default 4) relevant statutory chunks using TF-IDF similarity | Must |
| **FR-Q03** | System shall generate an answer grounded exclusively in retrieved chunks (no outside knowledge) | Must |
| **FR-Q04** | Every factual claim in the answer shall cite the source chunk ID (e.g. `[kb007]`) | Must |
| **FR-Q05** | If a cited chunk has `confidence=needs_verify`, the answer shall explicitly flag this | Must |
| **FR-Q06** | If retrieved chunks don't contain sufficient information, system shall say so rather than guess | Must |
| **FR-Q07** | System shall never state a percentage, date, amount, or clause number not present in the context | Must |
| **FR-Q08** | Response shall include: answer text, citation list, mode (live/mock), and disclaimer | Must |
| **FR-Q09** | System shall provide sample query pills for common questions | Should |
| **FR-Q10** | In mock mode (no API key), system shall return raw retrieved chunks with metadata | Must |
| **FR-Q11** | If live LLM call fails, system shall fall back to mock mode automatically | Must |

### 3.2 Liability & Penalty Calculator

| ID | Requirement | Priority |
|----|------------|----------|
| **FR-C01** | System shall accept PIBO entity type (Producer / Importer / Brand Owner / Seller) | Must |
| **FR-C02** | System shall accept fiscal year selection from supported range (FY 2024-25 to 2028-29) | Must |
| **FR-C03** | System shall accept packaging tonnage input per category (Cat I, II, III, IV) in MT | Must |
| **FR-C04** | System shall compute category-wise recycling obligation (tonnage × statutory %) | Must |
| **FR-C05** | System shall compute mandatory recycled content requirement (tonnage × content %) | Must |
| **FR-C06** | System shall estimate EPR certificate procurement cost range per category | Must |
| **FR-C07** | System shall compute Environmental Compensation (EC) penalty exposure at ₹5,000/MT | Must |
| **FR-C08** | System shall display EC 3-year refund schedule (85% / 60% / 30% / 0%) | Must |
| **FR-C09** | System shall sanitize inputs: reject NaN, Inf, negative values, and values > 1,000,000 MT | Must |
| **FR-C10** | System shall default unsupported fiscal years to FY 2026-27 | Should |
| **FR-C11** | System shall provide one-click PDF/print export of calculation results | Should |

### 3.3 Filing Deadlines & Checklist

| ID | Requirement | Priority |
|----|------------|----------|
| **FR-F01** | System shall display statutory annual return deadline (June 30) | Must |
| **FR-F02** | System shall display typical CPCB extension windows (Sept 30 / Oct 31) | Must |
| **FR-F03** | System shall provide interactive CPCB registration readiness checklist | Must |
| **FR-F04** | Checklist shall cover: CTE/CTO, PAN/GST/CIN, IEC, packaging specs, certificates, QR code, audit | Must |

### 3.4 Knowledge Base Browser

| ID | Requirement | Priority |
|----|------------|----------|
| **FR-K01** | System shall expose all 22 statutory chunks via UI and API | Must |
| **FR-K02** | Each chunk shall display: ID, title, citation source, confidence tag, text preview | Must |
| **FR-K03** | Confidence tags shall be visually distinct (color-coded badges) | Should |

### 3.5 System Health & Status

| ID | Requirement | Priority |
|----|------------|----------|
| **FR-H01** | `/health` endpoint shall return KB chunk count and LLM status | Must |
| **FR-H02** | `/api/status` shall return active provider name and live/mock state | Must |
| **FR-H03** | UI shall display live/mock badge in header | Must |

---

## 4. Non-Functional Requirements

### 4.1 Performance

| ID | Requirement | Target |
|----|------------|--------|
| **NFR-P01** | TF-IDF retrieval latency | < 50ms for 22 chunks |
| **NFR-P02** | Mock mode full response time | < 200ms |
| **NFR-P03** | Live mode response time (depends on LLM provider) | < 10s |
| **NFR-P04** | Calculator computation time | < 10ms |
| **NFR-P05** | Concurrent user support (gunicorn, 2 workers) | ~20 simultaneous |

### 4.2 Security

| ID | Requirement |
|----|------------|
| **NFR-S01** | Request payload capped at 64 KB to prevent DoS |
| **NFR-S02** | Question length validated (min 3, max 1000 chars) |
| **NFR-S03** | Calculator inputs sanitized against NaN, Inf, overflow |
| **NFR-S04** | Docker container runs as non-root user (`appuser`) |
| **NFR-S05** | API keys loaded from environment variables, never hardcoded |
| **NFR-S06** | Pre-commit hooks detect accidental secret commits |
| **NFR-S07** | No user data stored — stateless request/response model |

### 4.3 Reliability

| ID | Requirement |
|----|------------|
| **NFR-R01** | System must function fully in mock mode without any external dependency |
| **NFR-R02** | Live LLM failure must auto-fallback to mock mode, not crash |
| **NFR-R03** | Docker healthcheck probes `/health` every 30s with 3 retries |
| **NFR-R04** | LangGraph pipeline compiled once and cached (singleton) to prevent re-init per request |

### 4.4 Maintainability

| ID | Requirement |
|----|------------|
| **NFR-M01** | Knowledge base chunks must be editable by non-developers (plain Python dicts) |
| **NFR-M02** | Adding a new LLM provider requires only adding a new block in `get_active_llm()` |
| **NFR-M03** | Statutory target tables must be updatable without code logic changes (data-driven) |
| **NFR-M04** | Test suite must cover calculator math, KB integrity, retrieval, chain, and API routes |

### 4.5 Portability

| ID | Requirement |
|----|------------|
| **NFR-PO1** | Must run on macOS, Linux, and Windows (Python 3.11+) |
| **NFR-PO2** | Must be deployable via `docker compose up --build` with zero additional setup |
| **NFR-PO3** | CI must validate on Python 3.11 and 3.12 |

### 4.6 Usability

| ID | Requirement |
|----|------------|
| **NFR-U01** | Single-page UI with tab navigation — no page reloads |
| **NFR-U02** | Sample query pills for one-click common questions |
| **NFR-U03** | Calculator pre-populated with example values for immediate demo |
| **NFR-U04** | Print-optimized CSS for audit-ready PDF export via browser |
| **NFR-U05** | Every answer carries a regulatory disclaimer |

---

## 5. Data Requirements

### 5.1 Knowledge Base Schema

Each statutory chunk follows this structure:

```python
{
    "id": "kb001",                    # Unique identifier
    "title": "...",                   # Human-readable title
    "citation": "...",               # Official source reference
    "confidence": "verified",        # verified | reported | needs_verify
    "text": "..."                    # Full statutory text content
}
```

### 5.2 Current Knowledge Base Coverage (22 chunks)

| ID Range | Topic Area |
|----------|-----------|
| kb001–kb002 | EPR framework origin, obligated entity definitions |
| kb003–kb005 | Packaging categories I–IV (definitions, boundaries, compostable) |
| kb006–kb008 | Collection targets, recycling targets, recycled content mandates |
| kb009 | EPR certificate trading and market pricing |
| kb010 | PRO role and legal liability limits |
| kb011 | Filing deadlines and extension circulars |
| kb012 | QR code / barcode labeling mandate (Rule 11) |
| kb013–kb014 | Environmental Compensation regime, penalties, criminal prosecution |
| kb015 | Non-plastic EPR expansion (paper, glass, metal — effective April 2026) |
| kb016 | CPCB portal registration checklist |
| kb017 | Single-use plastics ban and 120-micron carry bag threshold |
| kb018 | Plastic Waste Processor protocols and digital credit generation |
| kb019 | MSME exemptions and small entity thresholds |
| kb020 | CPCB vs SPCB jurisdictional boundaries |
| kb021 | End-of-life disposal mandates (cement kilns, WtE, roads) |
| kb022 | Cross-compliance: battery waste and e-waste EPR boundaries |

### 5.3 Calculator Data Tables

**Recycling Targets (% of introduced packaging)**

| FY | Cat I | Cat II | Cat III | Cat IV |
|----|-------|--------|---------|--------|
| 2024-25 | 50% | 30% | 30% | 100% |
| 2025-26 | 60% | 40% | 40% | 100% |
| 2026-27 | 70% | 50% | 50% | 100% |
| 2027-28 | 80% | 60% | 60% | 100% |
| 2028-29 | 80% | 60% | 60% | 100% |

**Recycled Content Mandates (%)**

| FY | Cat I | Cat II | Cat III | Cat IV |
|----|-------|--------|---------|--------|
| 2025-26 | 30% | 10% | 5% | 0% |
| 2026-27 | 40% | 20% | 10% | 0% |
| 2027-28 | 50% | 30% | 10% | 0% |
| 2028-29 | 60% | 30% | 10% | 0% |

**EPR Certificate Market Price Ranges (₹/MT)**

| Category | Low | High |
|----------|-----|------|
| Cat I (Rigid) | ₹3,500 | ₹8,000 |
| Cat II (Flexible) | ₹6,000 | ₹14,000 |
| Cat III (MLP) | ₹8,000 | ₹20,000 |
| Cat IV (Compostable) | ₹4,000 | ₹10,000 |

---

## 6. Interface Requirements

### 6.1 API Endpoints

| Endpoint | Method | Request Body | Response |
|----------|--------|-------------|----------|
| `/health` | GET | — | `{status, kb_chunks, is_live, provider}` |
| `/api/status` | GET | — | `{is_live, provider, label}` |
| `/api/ask` | POST | `{question: string}` | `{question, answer, citations[], mode, disclaimer}` |
| `/api/calculate` | POST | `{pibo_type, fiscal_year, tonnages: {cat_1..4}}` | Full obligation breakdown (see 6.2) |
| `/api/target/<fy>` | GET | — | `{fiscal_year, found, recycling_targets_pct, recycled_content_pct}` |
| `/api/deadline` | GET | — | `{statutory_date, typical_extended_date, note}` |
| `/api/kb` | GET | — | Array of chunk objects with text previews |

### 6.2 Calculator Response Schema

```json
{
  "pibo_type": "Brand Owner",
  "fiscal_year": "2026-27",
  "total_introduced_packaging_mt": 410.0,
  "total_recycling_obligation_mt": 245.0,
  "total_recycled_content_required_mt": 95.0,
  "estimated_cert_procurement_cost_range_inr": {
    "min": 1525000,
    "max": 3560000,
    "formatted": "Rs 15,25,000 - Rs 35,60,000"
  },
  "potential_ec_penalty_exposure_inr": 1225000,
  "ec_refund_schedule": {
    "year_1_fulfillment": "85% refund",
    "year_2_fulfillment": "60% refund",
    "year_3_fulfillment": "30% refund",
    "after_year_3": "0% refund (forfeited)"
  },
  "categories": { ... },
  "governing_rules": "Schedule II of PWM Rules, 2016"
}
```

### 6.3 UI Tabs

| Tab | Content |
|-----|---------|
| **Legal Q&A Assistant** | Question input, sample pills, answer with citations |
| **Liability & Penalty Calculator** | PIBO type selector, FY selector, tonnage inputs, results dashboard |
| **CPCB Filing & Deadlines** | Deadline cards, 6-item registration checklist |
| **Knowledge Base Browser** | Scrollable list of all 22 chunks with confidence badges |

---

## 7. Test Requirements

| Test Suite | File | What It Validates |
|-----------|------|-------------------|
| Calculator Unit Tests | `test_calculator.py` | All FY targets, input sanitization (NaN, Inf, negative, overflow), EC penalty math, refund schedule |
| Knowledge Base Tests | `test_knowledge_base.py` | All 22 chunks have required fields (`id`, `title`, `citation`, `confidence`, `text`), no duplicates |
| Retriever Tests | `test_retriever.py` | TF-IDF returns relevant chunks for sample queries, correct metadata structure |
| Chain Tests | `test_chain.py` | Graph singleton caching, mock generation output format, fallback behavior |
| API Integration Tests | `test_api.py` | All endpoints return correct status codes, validation rejects bad input, response schema matches |

**CI:** GitHub Actions runs full suite on Python 3.11 and 3.12 on every push/PR to `main`.

---

## 8. Constraints & Limitations

| # | Limitation | Impact | Mitigation Path |
|---|-----------|--------|-----------------|
| 1 | TF-IDF retrieval is keyword-based, not semantic | Misses semantically similar questions that don't share vocabulary | Upgrade to embedding-based retriever (planned in UPGRADES.md) |
| 2 | Knowledge base is static (22 chunks) | New amendments require manual updates | Future: auto-ingest from Gazette RSS/API |
| 3 | No user authentication | Anyone with URL access can use the tool | Add auth layer if deployed publicly |
| 4 | No multi-language support | India has 22 official languages; tool is English-only | Future: Hindi/regional language support |
| 5 | Certificate prices are market estimates | Actual portal trading prices may differ | Tagged as `confidence: reported` |
| 6 | No database | No query history, no saved calculations | Future: optional PostgreSQL for audit trails |
| 7 | Single-server architecture | No horizontal scaling | Future: Redis cache + load balancer |

---

## 9. Future Enhancements (from UPGRADES.md roadmap)

| Feature | Description |
|---------|-------------|
| Hybrid RAG | Combine TF-IDF with embedding-based retrieval (FAISS/Chroma) |
| Invoice/BOM Vision Parser | Upload invoice images → auto-extract packaging tonnages |
| Agentic Tool-Calling | LLM autonomously decides when to call calculator vs retriever |
| Multi-tenant Dashboard | Company accounts with saved calculations and compliance history |
| CPCB Portal Integration | Auto-fill registration forms (pending API availability) |
| Gazette Auto-Ingestion | Monitor MoEFCC notifications and auto-update knowledge base |

---

## 10. Acceptance Criteria

The system is considered complete when:

1. ✅ All 18+ tests pass on Python 3.11 and 3.12
2. ✅ Q&A returns cited answers for all 5 sample queries
3. ✅ Calculator produces correct outputs for all 5 supported fiscal years
4. ✅ Mock mode works with zero API keys
5. ✅ At least one free-tier LLM provider works in live mode
6. ✅ Docker build and `docker compose up` succeeds
7. ✅ PDF/print export renders cleanly
8. ✅ `/health` endpoint returns 200 with correct metadata
9. ✅ No hardcoded API keys in codebase
10. ✅ Every answer carries a regulatory disclaimer
