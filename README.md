# EPR Compliance Copilot (v1.1.0)

[![Release](https://img.shields.io/badge/release-v1.1.0-2d6a4f.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](pyproject.toml)
[![Tests Passing](https://img.shields.io/badge/tests-31%2F31%20passing-brightgreen.svg)](tests/)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock%20(India%20Geo)-FF9900.svg)](proper_roadmap.md)
[![Single Source of Truth](https://img.shields.io/badge/rules.json-verified-2d6a4f.svg)](rules/rules.json)

A citation-grounded compliance copilot, deterministic liability engine, and waste-to-energy circularity bridge for India's plastic waste **Extended Producer Responsibility (EPR)** regulations (Schedule II of the Plastic Waste Management Rules, 2016, and subsequent MoEFCC & CPCB amendments).

---

## Key Features

- **Statutory Legal Q&A Assistant**: Grounded in official CPCB Gazette notifications with citation badges (`[kb007]`), provenance metadata (`effective_from`, `source_url`), and confidence ratings (`verified`, `reported`, `needs_verify`).
- **Post-Generation Numeric & Citation Verifier (`rag/verifier.py`)**: Programmatically validates all generated figures (percentages, dates, rupee amounts, clause references) against cited gazette chunks, preventing silent hallucinations.
- **Single Source of Truth (`rules/rules.json`)**: Versioned, audited statutory database powering both the deterministic calculator and RAG knowledge base to prevent rules drift.
- **Interactive EPR Liability & Penalty Calculator**:
  - Computes Category I–IV statutory recycling targets and mandatory recycled-content thresholds.
  - Models **Environmental Compensation (EC) penalty escalation** (Year 1: ₹5,000/MT, Year 2: ₹10,000/MT, Year 3: ₹20,000/MT) under EPA 1986 Section 15.
  - Implements statutory **75% / 60% / 40% 3-year refund schedule**.
- **Waste-to-Energy & Circularity Bridge**:
  - Models diversion of non-recycled plastic packaging to authorized End-of-Life (EOL) routes per Schedule II Clause 8.
  - Estimates thermal energy yield (MWh) and coal substitution in cement kiln co-processing (~35 MJ/kg, 85% thermal efficiency).
  - Estimates electrical energy yield (MWh) via Waste-to-Energy (WtE) combustion boilers (~25% electrical efficiency).
- **Multi-Model LLM Routing with AWS Bedrock**:
  - **AWS Bedrock**: In-country inference via India geographic cross-Region inference profile (`ap-south-1` Mumbai / `ap-south-2` Hyderabad) using Claude 3.5 Sonnet / Haiku.
  - **Groq**: Free tier ultra-fast LPU inference (`qwen/qwen3.8-27b`).
  - **OpenRouter**: Free-tier gateway (`deepseek/deepseek-r1:free`).
  - **Google Gemini** (`gemini-2.5-flash`), **Anthropic Claude**, **OpenAI**.
  - **Mock Mode**: Zero-dependency offline fallback serving raw statutory clauses.
- **Filing Deadlines & Portal Checklist**: Includes latest MoEFCC extension notices (FY 2025-26 returns: PWPs by 31 Oct 2026, PIBOs by 31 Dec 2026) and Form I registration checklist.
- **Audit-Ready PDF / Print Export**: One-click printable compliance reports with dedicated `@media print` stylesheets.
- **Automated Test & Evaluation Suite**: 31 passing unit, integration, verifier, and golden benchmark tests with 100% Retrieval Recall@6 and 100% Abstention accuracy.

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        User Browser (SPA)                              │
│   Legal Q&A  ·  Liability & EC Calculator  ·  Energy Bridge  ·  PDF    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTPS (Port 5000)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         Flask Application (app.py)                     │
│  - 64 KB Payload Ceiling & Per-IP Rate Limiter                         │
│  - Routes: /api/ask, /api/calculate, /api/rules-version, /health, ... │
└───────────┬───────────────────────────────┬────────────────────────────┘
            │                               │
            ▼                               ▼
┌───────────────────────────────┐ ┌──────────────────────────────────────┐
│     LangGraph RAG Workflow    │ │     Deterministic Calculator Engine  │
│         (rag/chain.py)        │ │           (rag/calculator.py)        │
│                               │ │                                      │
│ 1. retrieve_node:             │ │ - Reads rules/rules.json             │
│    Enhanced TF-IDF Retriever  │ │ - Cat I–IV Recycling Targets         │
│    + Acronym Expansion        │ │ - Recycled Content Mandates          │
│    + Keyword Statutory Boosts │ │ - EC Escalation (₹5k/₹10k/₹20k)      │
│    (top-k = 6 chunks)         │ │ - 75/60/40% Refund Schedule          │
│                               │ │ - Energy Recovery Scenario (MWh)     │
│ 2. generate_node:             │ │ - Coal Displacement Estimate         │
│    Dynamic Provider Switch    │ └──────────────────┬───────────────────┘
│                               │                    │
│ 3. verifier_node:             │                    │
│    rag/verifier.py            │                    │
│    Regex Numeric & Citation   │                    │
│    Grounding Verifier         │                    │
└───────────┬───────────────────┘                    │
            │                                        │
            ▼                                        ▼
┌───────────────────────────────┐ ┌──────────────────────────────────────┐
│      LLM Provider Layer       │ │      Single Source of Truth          │
│  - AWS Bedrock (India Geo)    │ │         (rules/rules.json)           │
│  - Groq (qwen3.8-27b)         │ │  Versioned, audited gazette clauses  │
│  - OpenRouter / Gemini        │ │  with statutory source provenance    │
│  - Offline Mock Mode          │ └──────────────────────────────────────┘
└───────────────────────────────┘
```

---

## AWS Services Integration Architecture

The copilot is architected to deploy natively on AWS serverless infrastructure:

```
                                  ┌──────────────────────────────┐
                                  │      Amazon CloudFront       │
                                  │   HTTPS, Edge Cache & WAF    │
                                  └──────────────┬───────────────┘
                                                 │
                                                 ▼
                                  ┌──────────────────────────────┐
                                  │      AWS Lambda (Docker)     │
                                  │  Flask + Lambda Web Adapter  │
                                  │  Reserved Concurrency = 5    │
                                  │  (Strict Abuse/Cost Ceiling) │
                                  └──────┬───────────────┬───────┘
                                         │               │
                     ┌───────────────────▼───┐   ┌───────▼──────────────────────┐
                     │ Amazon Bedrock Runtime│   │ Amazon S3                    │
                     │ Claude 3.5 Sonnet     │   │ - rules/rules.json (version) │
                     │ India Geo Profile     │   │ - Gazette PDFs & Circulars   │
                     │ (ap-south-1 / -2)     │   │ - Audit Logs                 │
                     │ + Bedrock Guardrails  │   └───────▲──────────────────────┘
                     └───────────────────────┘           │
                                                         │
  ┌────────────────── Regulatory Update Pipeline (Scheduled) ────────────────────┐
  │ Amazon EventBridge ──► Lambda Poller ──► Hash Diff ──► AWS Step Functions   │
  │   ──► Bedrock Rule Diff Extraction ──► Amazon SNS Email Alert to Reviewer    │
  │   ──► Human Approves ──► Publish New rules.json ──► CI Eval Gate Deploys     │
  └──────────────────────────────────────────────────────────────────────────────┘
```

### AWS Services Utilized:
1. **Amazon Bedrock (In-Country Inference)**:
   - Uses the **India Geographic cross-Region inference profile** keeping inference data within India (`ap-south-1` Mumbai and `ap-south-2` Hyderabad).
   - Removes third-party API key exposure via IAM Execution Role authentication.
2. **Amazon Bedrock Guardrails**:
   - `ApplyGuardrail` contextual grounding check validates answer fidelity against retrieved context chunks alongside our deterministic verifier.
3. **AWS Lambda with AWS Lambda Web Adapter (LWA)**:
   - Runs the containerized Flask application with scale-to-zero economics.
   - Hard cost ceiling enforced via `ReservedConcurrentExecutions = 5`.
4. **Amazon S3**:
   - Versioned storage bucket for `rules.json`, official Gazette source PDFs, and report exports.
5. **Amazon EventBridge & AWS Step Functions**:
   - Automated daily watch on CPCB/MoEFCC circular pages to detect amendments, calculate cryptographic hash diffs, and queue diff proposals for human sign-off before publishing.
6. **Amazon Textract (AnalyzeExpense / Tables)**:
   - Automated document parsing of supplier packaging invoices and Bills of Materials (BOM) to extract plastic packaging weights for automated Category I–IV categorization.
7. **Amazon CloudWatch & AWS Budgets**:
   - End-to-end telemetry and cost threshold alarms configured at 50%, 80%, and 100% of spending limits.

---

## Quickstart

### 1. Setup Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt pytest
```

### 2. Configure Environment (Optional for Live Mode)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Choose your preferred provider:
```ini
# Option A: AWS Bedrock (Recommended for Enterprise / In-Country Inference)
AWS_BEDROCK_ENABLED=true
AWS_REGION=ap-south-1
BEDROCK_MODEL_ID=apac.anthropic.claude-3-5-sonnet-20241022-v2:0

# Option B: Groq (Recommended for FREE & Fast Dev)
GROQ_API_KEY=gsk_your_groq_api_key
GROQ_MODEL=qwen/qwen3.8-27b

# Option C: OpenRouter (FREE models)
OPENROUTER_API_KEY=sk-or-your_key
OPENROUTER_MODEL=deepseek/deepseek-r1:free

# Option D: Google Gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

*(If no API key is provided, the copilot runs automatically in **Mock Mode**, displaying raw retrieved legal chunks with zero external dependencies).*

### 3. Start the Application
```bash
.venv/bin/python app.py
```
Open **http://localhost:5000** in your browser.

---

## Docker Deployment

To build and run via Docker Compose:
```bash
docker compose up --build
```
Healthcheck probe runs automatically at `/health`.

---

## Running the Automated Test & Eval Suite

Execute all 31 unit, integration, verifier, and golden benchmark tests:
```bash
.venv/bin/pytest tests/ -v
```

### Evaluation Benchmark Results:
- **Retrieval Recall@6 (Factual)**: 100.0% (20/20)
- **Retrieval Recall@6 (Paraphrase)**: 100.0% (10/10)
- **Abstention Accuracy (Out-of-Scope)**: 100.0% (10/10)
- **Adversarial Defense Rate**: 100.0% (10/10)
- **Rules Consistency Check**: 100.0% agreement between `rules.json` and `knowledge_base.py`

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `GET /health` | GET | Liveness & readiness probe returning KB chunk count, ruleset version, and active provider |
| `GET /api/status` | GET | Returns active LLM provider label and live/mock state |
| `GET /api/rules-version` | GET | Returns current ruleset version, verification date, and statutory source list |
| `POST /api/ask` | POST | Submits compliance question; returns answer with grounded citations and numeric verification status |
| `POST /api/calculate` | POST | Calculates Category I–IV recycling targets, recycled content, EC escalation, and energy recovery |
| `GET /api/target/<fy>` | GET | Returns statutory recycling and recycled-content targets for a financial year (e.g. `2026-27`) |
| `GET /api/deadline` | GET | Returns official CPCB annual return filing deadline and active extension circulars |
| `GET /api/kb` | GET | Returns all knowledge base chunks with citations and confidence ratings |

---

## Project Structure

```
epr-copilot/
├── app.py                      # Flask web server, rate limiting, and REST API
├── rules/
│   └── rules.json              # Single source of truth: targets, EC rates, deadlines, energy parameters
├── rag/
│   ├── __init__.py
│   ├── knowledge_base.py       # 24 ground-truth statutory chunks with provenance metadata
│   ├── retriever.py            # Enhanced TF-IDF retriever with acronym expansion & statutory boosts
│   ├── chain.py                # LangGraph multi-provider workflow (Bedrock, Groq, OpenRouter, Mock)
│   ├── verifier.py             # Post-generation numeric & citation grounding verifier
│   └── calculator.py           # Deterministic liability, EC escalation & energy recovery engine
├── static/
│   ├── css/app.css             # Dark theme stylesheet with print styles for PDF export
│   └── js/app.js               # Frontend tabs, API integration, and report rendering
├── templates/
│   └── index.html              # Tabbed UI (Legal Q&A, Liability & Energy Calculator, Deadlines, KB)
├── tests/
│   ├── test_api.py             # Flask API integration tests
│   ├── test_calculator.py      # Unit tests for liability calculations & input sanitization
│   ├── test_chain.py           # Tests for LangGraph singleton & mock generation
│   ├── test_eval.py            # Automated eval harness (Recall@6, Abstention, Adversarial)
│   ├── golden_eval.json        # 50-item golden evaluation dataset
│   ├── test_knowledge_base.py  # Integrity tests for statutory chunks
│   ├── test_retriever.py       # Unit tests for enhanced retriever
│   ├── test_rules_consistency.py # Drift-prevention tests asserting rules.json ⇄ KB agreement
│   └── test_verifier.py        # Unit tests for numeric & citation verifier
├── Dockerfile                  # Production containerfile with non-root user & healthcheck
├── docker-compose.yml          # Container orchestration with environment variable passthrough
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Modern package metadata & pytest configuration
└── README.md                   # Documentation, architecture, and AWS deployment guide
```

---

## Regulatory Basis & Citations

- **Schedule II of the Plastic Waste Management Rules, 2016** (notified under MoEFCC G.S.R. 133(E) dated 16 February 2022).
- **CPCB Environmental Compensation Guidelines** (renewed 4 April 2024).
- **MoEFCC Annual Return Extension Circular** (dated 28 August 2026).
- **PWM (Amendment) Rules, 2025** (Rule 11 on-pack QR code & barcode labeling mandates).
- **PWM (Amendment) Rules, 2026** (Virgin raw material Sellers registration & registered environmental auditors).
- **Environment (Protection) Act, 1986** (Section 15 penalty & prosecution regime).
- **CPCB Technical Guidelines for Co-Processing in Cement Kilns & Waste-to-Energy** (Alternative Fuel & Raw Material benchmarks).
