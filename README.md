# EPR Compliance Copilot (v1.0.0)

[![Release](https://img.shields.io/badge/release-v1.0.0-2d6a4f.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](pyproject.toml)
[![Future Upgrades](https://img.shields.io/badge/roadmap-UPGRADES.md-52b788.svg)](UPGRADES.md)

A citation-grounded compliance copilot and obligation calculation engine for India's plastic waste Extended Producer Responsibility (EPR) regulations (Schedule II of the Plastic Waste Management Rules, 2016 and subsequent MoEFCC & CPCB amendments).

Built on **Flask + LangChain + LangGraph**, architected for **Amazon Web Services (AWS)**:
- **Statutory Legal Q&A Assistant**: Grounded in official CPCB notifications, with citation badges and confidence ratings (`verified`, `reported`, `needs_verify`).
- **Amazon Bedrock & Multi-Model Dynamic LLM Routing**: Native support for **Amazon Bedrock** (`anthropic.claude-3-5-sonnet`, `amazon.titan-text-express-v1`, `meta.llama3-70b-instruct`) hosted in `ap-south-1` (Mumbai), plus **Groq**, **OpenRouter**, **Google Gemini**, **Anthropic Claude**, **OpenAI**, with automated fallback to zero-dependency **Mock Mode**.
- **Interactive EPR Liability & Penalty Calculator**: Computes Category I–IV statutory recycling targets, mandatory recycled-content requirements, certificate procurement budgets, and Environmental Compensation (EC) penalty exposures with a 3-year refund schedule.
- **Audit-Ready PDF / Print Report Export**: One-click printable compliance reports with dedicated `@media print` layout.
- **CPCB Portal Registration Readiness Checklist**: Practical compliance guide for Producers, Importers, Brand Owners (PIBOs), and Sellers.
- **Automated Test Suite**: 18 passing unit and integration tests across calculation math, RAG retrieval, and API routes.
- **Future Roadmap**: See [UPGRADES.md](UPGRADES.md) for planned features (Amazon OpenSearch Hybrid RAG, Textract Invoice/BOM Vision Parser, Agentic Tool-Calling).

---

## Architecture (AWS Cloud-Native Alignment)

```
Browser  -->  Flask API (ECS Fargate / App Runner)  -->  LangGraph Pipeline (rag/chain.py)
                                                              │
                                                              ├─► retrieve_node: TF-IDF / Amazon OpenSearch
                                                              │   (rag/retriever.py) over rag/knowledge_base.py (22 statutory chunks)
                                                              │
                                                              └─► generate_node:
                                                                  ├── Enterprise: Amazon Bedrock (Claude 3.5 Sonnet / Titan)
                                                                  ├── Dev: Groq (qwen/qwen3.8-27b - Free & Fast)
                                                                  ├── Dev: OpenRouter (deepseek/deepseek-r1:free)
                                                                  ├── Live: Google Gemini / Claude / OpenAI
                                                                  └── Mock Mode: (zero API key fallback)
```

- **Retrieval**: `langchain_community.retrievers.TFIDFRetriever` over 22 statutory knowledge chunks with exact legal clause citations.
- **Generation**: Strict system prompt enforcing zero hallucinations, explicit citation tags (e.g. `[kb004]`), and distinction between verified gazette rules vs reported market estimates.
- **Deterministic Calculator** (`rag/calculator.py`): Mathematical computation engine covering Category I (Rigid), Category II (Flexible), Category III (Multi-layered MLP), and Category IV (Compostable) obligations, market certificate prices, and Section 15 EPA 1986 penalty exposures with sanitization against `NaN` and `Inf`.

---

## Quickstart

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate environment:
# On Linux / macOS:
source .venv/bin/activate
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt pytest
```

### 2. Configure API Key (Optional for Live Mode)
Copy `.env.example` to `.env`:
```bash
# On Linux / macOS:
cp .env.example .env
# On Windows (PowerShell):
Copy-Item .env.example .env
```

Add your preferred key:
```ini
# Option A: Groq (Recommended - FREE & Fast)
GROQ_API_KEY=gsk_your_groq_api_key
GROQ_MODEL=qwen/qwen3.8-27b

# Option B: OpenRouter (FREE models)
OPENROUTER_API_KEY=sk-or-your_key
OPENROUTER_MODEL=deepseek/deepseek-r1:free

# Option C: Google Gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

# Option D: Anthropic Claude
# ANTHROPIC_API_KEY=your_anthropic_api_key

# Option E: OpenAI
# OPENAI_API_KEY=your_openai_api_key
```
*(If no API key is provided, the copilot runs automatically in **Mock Mode**, displaying raw retrieved legal chunks with zero setup).*

### 3. Start the Application
```bash
.venv/bin/python app.py
```
Open **http://localhost:5000** in your browser.

---

## Docker Deployment

To run via Docker Compose:
```bash
docker compose up --build
```
Open **http://localhost:5000**. Healthcheck runs automatically at `/health`.

---

## Running Tests

Execute the comprehensive test suite:
```bash
.venv/bin/pytest tests/ -v
```

---

## Project Structure

```
epr-copilot/
├── app.py                      # Flask web server & REST API endpoints
├── rag/
│   ├── __init__.py
│   ├── knowledge_base.py       # 22 ground-truth statutory CPCB knowledge chunks
│   ├── retriever.py            # Keyword/TF-IDF retrieval engine
│   ├── chain.py                # LangGraph multi-model RAG workflow & singleton cache
│   └── calculator.py           # Deterministic EPR liability & penalty engine
├── static/
│   ├── css/
│   │   └── app.css             # Stylesheet with print styles for PDF export
│   └── js/
│       └── app.js              # Client-side UI logic and API communication
├── templates/
│   └── index.html              # Clean semantic tabbed UI
├── tests/
│   ├── test_calculator.py      # Unit tests for liability calculations & input sanitization
│   ├── test_knowledge_base.py  # Integrity tests for statutory chunks
│   ├── test_retriever.py       # Unit tests for retrieval engine
│   ├── test_chain.py           # Tests for LangGraph singleton & mock generation
│   └── test_api.py             # Flask API integration tests
├── .github/
│   └── workflows/
│       └── ci.yml              # CI workflow testing across Python 3.11 & 3.12
├── .pre-commit-config.yaml     # Secret detection and syntax hooks
├── Dockerfile                  # Production containerfile with non-root user
├── docker-compose.yml          # Container orchestration
├── CHANGELOG.md                # Semantic versioning changelog
├── pyproject.toml              # Modern package metadata
├── requirements.txt            # Python dependencies
└── README.md                   # Documentation & technical guide
```

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `GET /health` | GET | Liveness and readiness probe returning chunk count and active LLM status |
| `GET /api/status` | GET | Returns active LLM provider label and live/mock state |
| `POST /api/ask` | POST | Submits compliance question; returns answer with grounded chunk citations |
| `POST /api/calculate` | POST | Calculates Category I–IV recycling targets, recycled content, and EC penalties |
| `GET /api/target/<fy>` | GET | Returns statutory targets for a specific fiscal year (e.g. `2026-27`) |
| `GET /api/deadline` | GET | Returns official CPCB annual return filing deadline |
| `GET /api/kb` | GET | Returns all knowledge base chunks with citations and confidence ratings |
