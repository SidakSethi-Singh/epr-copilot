# EPR Compliance Copilot — Production-Readiness, Usefulness & AWS Integration Report

| | |
|---|---|
| **Artifact judged** | `SRS-1.md` — EPR Compliance Copilot v1.0.0 (SRS v1.0, Oct 2026) |
| **Review date** | 10 Oct 2026 |
| **Reviewer mode** | LLM-as-judge (rubric-based, single pass) + web verification of regulatory claims |
| **Not inspected** | Source code, the 22 KB chunk texts, test files, the live deployment. This is a review of the *specification*. |

---

## 0. Verdict

| Question | Answer |
|---|---|
| Is the problem real and useful? | **Yes.** Rules change often, deadlines get extended repeatedly, and SMEs cannot afford a consultant for every question. |
| Is it production-ready for compliance decisions? | **No.** It is a strong **demo / pilot-grade MVP**. Verified data errors and static deadlines are disqualifying for a tool people may rely on to avoid penalties. |
| Is the architecture a good foundation? | **Yes.** Deterministic calculator + cited RAG + mock-mode fallback is the right shape for a legal-adjacent tool. |
| Should AWS be added? | **Yes, selectively** (Bedrock in India region, Guardrails, Lambda/ECS hosting, S3, EventBridge + Step Functions for a regulatory-update pipeline, Textract/Data Automation for the invoice parser). **Skip** the heavy managed stack (OpenSearch Serverless, SageMaker, AgentCore) for now. See §6. |
| Single highest-leverage fix | Make regulatory data **versioned, dated, source-linked and human-verified**, then gate every release on a golden test set. |

**Overall judge score: 56 / 100** (rubric in §2). Any score ≤ 2 on *Regulatory correctness* is a hard fail for production regardless of the total.

---

## 1. Method and limits (read this before trusting any ❌)

1. I read the full SRS and judged it against a rubric (§2).
2. I tried to verify its regulatory numbers against what is publicly available as of 10 Oct 2026.
3. **I could not pull the Gazette / CPCB PDFs themselves in this session.** Verification used consultancy and legal-update sites, which sometimes disagree with each other. So:
   - ✅ = consistent with ≥2 independent secondary sources
   - ❌ = conflicts with ≥2 secondary sources (strong signal, **not** proof; confirm against the Gazette/CPCB text)
   - ⚠️ = couldn't verify, or sources conflict
4. An LLM judge has self-preference and recency blind spots. For CI, use a *different* model family as judge and keep a human-verified subset (§8).
5. My web searching for competitors is not exhaustive.

---

## 2. LLM-as-judge scorecard

Scale 0–5. Weighted to 100.

| # | Dimension | Weight | Score | Evidence |
|---|---|---:|---:|---|
| 1 | Problem relevance / usefulness | 15 | **4** | Real pain; frequent amendments; deadline churn; SME under-service |
| 2 | Differentiation vs. existing tools | 10 | **3** | Free, cited, transparent confidence tags is distinctive; incumbents own fulfilment, not explainability |
| 3 | **Regulatory correctness** | 25 | **2** | Multiple table errors and stale deadlines (§3.1) |
| 4 | Architecture soundness | 10 | **4** | Deterministic math separated from LLM; fallback; stateless; data-driven tables |
| 5 | Hallucination / safety controls | 15 | **3** | Good *requirements* (FR-Q03–Q07) but nothing in the SRS *enforces* them programmatically |
| 6 | Evaluation rigor | 10 | **2** | Tests check internal consistency, not truth; no retrieval/faithfulness evals |
| 7 | Security / ops readiness | 10 | **2** | Payload cap and non-root good; no rate limiting, auth, observability, free-tier LLM dependency |
| 8 | Commercial viability | 5 | **3** | Strong as lead-gen / white-label; weak as standalone SaaS against Recykal-type incumbents |
| | **Weighted total** | 100 | **56** | (4·15 + 3·10 + 2·25 + 4·10 + 3·15 + 2·10 + 2·10 + 3·5) / 5 |

**Release bands used:** ≥ 80 production · 60–79 pilot with named customers · **40–59 demo / public beta with loud disclaimers (you are here)** · < 40 prototype.

---

## 3. Findings

### 3.1 Regulatory accuracy audit

| # | SRS claim | What I found | Status | Action |
|---|---|---|---|---|
| 1 | Min. recycling Cat I/II/III: 50/30/30 → 60/40/40 → 70/50/50 → 80/60/60 (FY24-25 → FY27-28; flat after) | Matches multiple 2026 sources | ✅ | Keep; link Gazette clause |
| 2 | **Cat IV recycling = 100%** every year | Sources show **50 / 60 / 70 / 80%** (same ramp as Cat I) | ❌ | Fix table + test |
| 3 | Recycled content Cat I: 30/40/50/60 | Matches | ✅ | Keep |
| 4 | **Recycled content Cat II: 10/20/30/30** | Sources: **10/10/20/20** (one source shows 10/15/20/20). Nothing I found supports 30% | ❌ | Fix; resolve 2026-27 against Gazette |
| 5 | **Recycled content Cat III: 5/10/10/10** | Sources: **5/5/10/10**, and applies to **weight of plastic layers only** | ❌ | Fix; add the plastic-layer note to calculator |
| 6 | Obligation = tonnage × statutory % | Real base is the EPR target **Q = (A + B) − C**, using the **average of the previous two FYs** (virgin packaging purchased/introduced + pre-consumer waste, less quantity supplied to non-MSE brand owners). The recycling % is applied to *Q*, not to current-year tonnage | ⚠️ | Implement Q, or label output "simplified estimate" |
| 7 | EC = flat ₹5,000/MT | ₹5,000 is the **first-year** rate; most sources give ₹10,000 (2nd consecutive year) and ₹20,000 (3rd). Some sources list **category-specific** rates (e.g. ₹2,900 Cat I, ₹7,900 Cat III/IV). One source says CPCB revises EC every six months | ⚠️ | Read CPCB EC guideline (4 Apr 2024) and model escalation + category rates |
| 8 | **Refund schedule 85 / 60 / 30 %** | Three independent sources say **75 / 60 / 40 %** (within 1 / 2 / 3 years) | ❌ | Fix after checking the EC guideline |
| 9 | Statutory deadline June 30 | Correct baseline | ✅ | Keep |
| 10 | **"Typical extension windows Sept 30 / Oct 31"** | Extensions are ad hoc and long. FY 2025-26: PWPs **31 Oct 2026**, PIBOs **31 Dec 2026** (MoEFCC, 28 Aug 2026). FY 2024-25 was extended repeatedly (to Nov 2025, then 31 Jan 2026, then 31 Mar 2026). The guideline allows up to nine months of extension | ❌ | Replace with a dated, sourced **notice feed**; never hard-code "typical" |
| 11 | KB "reflects rules as of September 2026" | The 28 Aug 2026 deadline notice already contradicts the deadline chunk → drift within weeks | ❌ | Motivates the update pipeline (§6, Phase 3) |
| 12 | Checklist references "CPCB portal" | CPCB reportedly retired the standalone Plastic EPR portal from 28 Jun 2026 in favour of the **Common EPR Portal** (single source) | ⚠️ | Verify and update checklist text |
| 13 | kb015: non-plastic EPR (paper/glass/metal) "effective April 2026" | I found a **Dec 2024 draft** and secondary mentions of integration into "Solid Waste Management Rules, 2026". I could not confirm an April 2026 effective date | ⚠️ | Tag `needs_verify` until Gazette text is in hand |
| 14 | Rule 11 QR-code mandate (2025); Sellers / traceability / registered auditors (2026) | **Not checked** in this review | ⚠️ | Verify before the chunk ships as `verified` |
| 15 | Certificate prices ₹3.5k–₹20k/MT | Volatile and poorly sourced; secondary sources vary by an order of magnitude | ⚠️ | Make price an **input with date + source**, or drop the cost range |
| 16 | Categories I–IV only | Framework now recognises **Cat V (biodegradable)** | ⚠️ | Add or explicitly scope out |
| 17 | (absent) Reuse obligation | Cat I rigid reuse targets (from 2028-29, e.g. 25% / 85% / 15% by pack size) | gap | Add as a calculator module or scope note |
| 18 | (absent) Carry-forward | 2026 amendment: recycled-content shortfall can be carried forward 3 years if ≥ ⅓ cured per year; surplus is category-specific | gap | Add to Q&A KB; consider calculator support |
| 19 | (absent) End-of-life disposal share | Recycling % is a minimum; balance may go to prescribed EOL routes | gap | Calculator should not imply the remainder is "free" |

**Why this matters:** rows 2, 4, 5, 8 and 10 are *silent* wrong answers — the app returns a confident, cited, nicely formatted number that is wrong. In a compliance tool that is worse than no tool.

### 3.2 Design and engineering findings

| Area | Finding | Severity |
|---|---|---|
| **Temporal modelling** | KB chunks have no `effective_from`, `superseded_by`, `retrieved_on`, or source URL/hash. Legal Q&A must answer "as of date X". | P0 |
| **Single source of truth** | Calculator tables (§5.3) and KB text (§5.2) are separate. They will diverge (they already conflict with reality in places). | P0 |
| **Enforcement of FR-Q07** | "Never state a number not in context" is a prompt rule. Add a post-generation **numeric + citation verifier** (regex all numbers/dates/clause refs in the answer → must appear in cited chunk text). | P0 |
| **Evals** | 18+ tests prove code works, not that answers are *true*. Need golden Q&A set, retrieval recall@k, faithfulness, abstention tests. | P0 |
| **Retrieval** | TF-IDF over 22 chunks is fine today and brittle tomorrow ("who has to register?" vs "PIBO obligated entity"). Corpus is also tiny: the real corpus (Schedule II, 2022/23/24/26 amendments, CPCB EC + annual return guidelines, extension notices, FAQs) is likely 300–1,500 clause-level chunks. | P1 |
| **Free-tier LLM dependency** | Assumption #4 ("providers maintain free tiers") is not a production assumption. | P1 |
| **Abuse / cost control** | Only a 64 KB payload cap. No per-IP rate limit, no concurrency cap. A public endpoint backed by a paid LLM needs both. | P0 (if public) |
| **Persistence trade-off** | "No data persisted" is a clean privacy story but blocks the features users pay for (saved calculations, audit trail, multi-year history). Offer *stateless mode* and *opt-in workspace mode*. | P1 |
| **Auth** | None. Fine for a demo; needed before any client data. | P1 |
| **Observability** | No metrics/tracing. You cannot improve what you cannot see (log retrieval hits, abstentions, verifier failures — not raw question text, if you keep the privacy promise). | P1 |
| **Legal exposure** | Disclaimer on every answer is good. Add ToS, a visible "last verified" date, and consider a lawyer glance before charging money. | P1 |
| **Dependencies / supply chain** | Pin and scan dependencies; you already have secret-scanning hooks (good). | P2 |
| **Language** | English only; Hindi next, but translating legal text adds risk — cite the English source alongside. | P2 |

### 3.3 What's genuinely good (keep these)

- Deterministic calculator separate from the LLM (NFR / design constraint).
- `confidence: verified | reported | needs_verify` on every chunk, surfaced to the user (FR-Q05). This is your best trust feature.
- Abstention requirement (FR-Q06) and automatic mock fallback (FR-Q11).
- Works with zero keys; stateless; non-root container; healthcheck; CI on 3.11/3.12.
- Data-driven tables (NFR-M03) — the right instinct; finish the job with versioned rules (§7).

---

## 4. Usefulness and prior art

### 4.1 Who actually benefits

| Segment | Fit | Why |
|---|---|---|
| **SME / D2C brands, importers, marketplace sellers** | ★★★★★ | Need to know "does this apply to me, how much, by when" without paying a consultant per question |
| **EPR consultants** | ★★★★ | Fast client demos, quick reference, white-label |
| Large FMCG compliance teams | ★★ | Already have consultants/platforms; will use it as a cross-check at best |
| Auditors | ★★ | Need primary-source traceability more than summaries |

### 4.2 Existing solutions I found (not exhaustive)

| Player | Type | What they do | Overlap with you | Your gap vs them |
|---|---|---|---|---|
| **Recykal** | Platform / marketplace | EPR fulfilment, 100+ verified recyclers, tracking, alerts; claims 650+ brands | Calculator-ish planning, deadline alerts | They actually *fulfil* (certificates, audits). You don't, by design |
| **Consultancies** (Kar Parivartan, Aleph India, PSR Compliance, Treelife, etc.) | Services + SEO content | Registration, returns, advisory | Same questions you answer | Human trust, filing support; slow/paid |
| **Sukra** | Self-service portal | PIBO registration prep and annual filing assistance | Registration/filing help | Workflow, not explainable Q&A |
| **Regilient** | "Agentic sustainability platform" | Multi-jurisdiction EPR workflow automation; lists India | Agentic compliance narrative | Enterprise/global, not India-plastic-deep |
| **Source Intelligence, Packgine, AlgoREP** | Global SaaS | EU PPWR / US state EPR, fee calculators | Concept only | Not Indian CPCB regime |
| **CircularChain** (hackathon repo) | Prototype | Circular-economy ledger with an EPR liability simulator | Calculator | Different product shape |
| **CPCB Common EPR Portal** | Official | Registration, certificates, returns | Authoritative data | No guidance layer |

**Finding:** I did not find a dedicated, citation-grounded, confidence-tagged Q&A + deterministic calculator specifically for Indian plastic EPR. That's an opening — but a thin one, because anyone with a RAG template can copy the *shape*. The moat is **data quality, freshness and trust**, not the architecture.

### 4.3 Positioning that makes sense for an AI-automation-agency business

1. **Lead magnet / top-of-funnel** for EPR consultants (white-label with their branding).
2. **"Annual return prep copilot"** for SMEs: upload invoices/BOM → classify into categories → compute Q → draft return worksheet → flag deadlines. This is where manual hours live; the Q&A is the on-ramp.
3. **Regulatory change radar**: dated notices, "what changed for me", email alerts. Deadlines were extended at least four times in the last year — people will pay to not miss one.
4. Do **not** compete head-on with fulfilment marketplaces.

---

## 5. Production-readiness gates

### P0 — before any external user relies on it
- [ ] Correct rows 2, 4, 5, 8, 10 of §3.1; confirm each number against Gazette/CPCB primary text; store the citation + page
- [ ] Add `effective_from`, `source_url`, `source_sha256`, `retrieved_on`, `verified_by`, `verified_on` to every KB chunk and rule value
- [ ] Move calculator tables + KB numbers to **one** versioned rules file; tests assert KB text ⇄ rules agree
- [ ] Implement EPR target **Q** (two-year average) or relabel the calculator output "simplified estimate"
- [ ] Replace "typical deadlines" with sourced, dated notices + a visible "rules last verified: <date>" banner
- [ ] Post-generation numeric/citation verifier; on failure → abstain or mock mode
- [ ] Golden eval set (≥ 100 Qs) + CI gate (§8)
- [ ] Rate limiting + concurrency cap + budget alarm if the endpoint is public

### P1 — before charging money
- [ ] Hybrid retrieval (BM25 + embeddings + rerank) over clause-level chunks
- [ ] Human-in-the-loop update workflow for rule changes (§6 Phase 3)
- [ ] Auth + optional workspace persistence (audit trail)
- [ ] Observability dashboard (retrieval hit rate, abstention rate, verifier-failure rate, latency, cost/query)
- [ ] Load test beyond the "~20 concurrent" assumption; ToS; legal review of disclaimer

### P2 — growth
- [ ] Invoice/BOM parser, agentic tool-calling, Hindi, multi-tenant dashboard, non-plastic EPR streams

---

## 6. AWS integration plan

### 6.1 Is AWS worth adding?

**Yes — for five specific jobs, not as a rewrite.**

| Reason AWS helps | Why it matters for this project |
|---|---|
| **In-country inference** | Claude models are now available on Bedrock with India geographic cross-Region inference (requests stay between Mumbai `ap-south-1` and Hyderabad `ap-south-2`). That is a concrete selling point for Indian enterprise clients and removes the free-tier dependency. |
| **No API keys in code** | Lambda/ECS IAM roles replace `.env` keys — aligns with NFR-S05. |
| **Guardrails with contextual grounding** | A managed grounding/relevance check on top of your own verifier. |
| **Scheduled, auditable ingestion** | EventBridge + Step Functions fit the "watch notices → extract → human approve → publish" pipeline. |
| **Document parsing** | Textract / Bedrock Data Automation (Data Automation endpoints exist in Mumbai) for the invoice/BOM feature. |

Be honest about the costs: AWS adds IAM, networking and billing complexity, and a surprise bill is the classic student-project failure mode. Phase 1 below is deliberately small and capped.

### 6.2 Adopt / Defer / Skip

| Service | Decision | Reason |
|---|---|---|
| **Amazon Bedrock (Claude, India geo inference profile)** | **Adopt — Phase 1** | New provider in `get_active_llm()` (NFR-M02). Keep Groq/mock as fallbacks |
| **Bedrock Guardrails (contextual grounding, `ApplyGuardrail`)** | **Adopt — Phase 1** | Independent API; can check output from *any* provider. Use alongside, not instead of, your numeric verifier |
| **AWS Lambda (container) + Lambda Web Adapter** | **Adopt — Phase 1** | Flask app runs unchanged; scale-to-zero; cheapest for spiky demo traffic |
| **S3 (+ versioning)** | **Adopt — Phase 1** | Raw notices, KB source docs, versioned `rules.json` |
| **CloudWatch + AWS Budgets** | **Adopt — Phase 1** | Logs, alarms, **spend cap alerts** |
| **CloudFront** | Adopt when public | HTTPS, caching of static UI, custom domain |
| **ECS Fargate / ECS Express Mode** | Alternative to Lambda | Use if you need long-lived workers. **Do not use App Runner** — it has been closed to new customers since 30 Apr 2026 |
| **EventBridge Scheduler + Step Functions + SNS/SES** | **Adopt — Phase 3** | Notice watcher, review queue, alerts |
| **Textract (AnalyzeExpense / tables) or Bedrock Data Automation** | **Adopt — Phase 3** | Invoice/BOM → line items. Confirm region availability of the exact API you pick |
| **DynamoDB + Cognito** | **Adopt — Phase 3** (opt-in workspace) | Saved calculations, audit trail, auth |
| **Bedrock Knowledge Bases + S3 Vectors (Mumbai)** | **Defer** | S3 Vectors is available in `ap-south-1`. But for ≤ a few thousand chunks, an in-container hybrid index (BM25 + small embedding index) is cheaper, simpler and keeps mock mode alive. Move to Knowledge Bases when you have user-uploaded corpora / multi-tenant docs |
| **Bedrock AgentCore / Agents** | **Defer** | Converse API tool-use (calculator + retriever as tools) is enough for the "agentic" roadmap item |
| **Amazon Translate** | Defer | Hindi later; always show English source |
| **AWS WAF** | Defer | Fixed monthly cost; use reserved concurrency + app rate limits first |
| **OpenSearch Serverless, Kendra, SageMaker, GPU instances** | **Skip** | Over-engineered / high always-on cost for this scale; and you don't need a local GPU — all inference is managed |

### 6.3 Target architecture

```
                         ┌────────────── Browser (SPA, 4 tabs) ──────────────┐
                         └───────────────────────┬────────────────────────────┘
                                                 │ HTTPS
                                       ┌─────────▼─────────┐
                                       │    CloudFront     │  (static UI + API path)
                                       └─────────┬─────────┘
                                                 │
                             ┌───────────────────▼───────────────────┐
                             │ Lambda (container, Flask via Web      │  reserved concurrency = cap
                             │ Adapter)  /api/ask  /api/calculate …  │
                             │  ├─ Retriever (BM25+embeddings in-proc)│
                             │  ├─ Calculator (reads rules.json)     │
                             │  ├─ Verifier (numbers/citations)      │
                             │  └─ LLM provider switch               │
                             └───────┬──────────────┬────────────────┘
                                     │              │
                  ┌──────────────────▼───┐   ┌──────▼──────────────────────┐
                  │ Bedrock Runtime      │   │ S3: rules.json (versioned), │
                  │ Claude via India geo │   │ KB chunks, source PDFs      │
                  │ inference profile    │   └──────▲──────────────────────┘
                  │ + Guardrails         │          │ publish (after approval)
                  └──────────────────────┘          │
                                                    │
 ┌─────────────── Regulatory update pipeline (Phase 3) ─────────────────────────┐
 │ EventBridge Scheduler ─► Lambda fetch (CPCB / MoEFCC pages, hash diff)       │
 │        ─► S3 raw ─► Step Functions ─► Bedrock (small model) "what changed"   │
 │        ─► SNS/SES email to YOU ─► human approves in a tiny review page       │
 │        ─► publish new rules.json + KB version ─► eval suite runs in CI       │
 └──────────────────────────────────────────────────────────────────────────────┘

 Phase 3 optional:  Cognito + DynamoDB (workspaces, audit trail)
                    Textract / Data Automation (invoice → line items → category → Q)
```

### 6.4 How to implement it

#### Phase 0 — account hygiene (30 min, do first)
1. Create the account with MFA; use **IAM Identity Center** (SSO) for daily use; no root access keys.
2. Set a **Budget alarm** (e.g. a small monthly USD cap with email at 50/80/100%).
3. Work in `ap-south-1` (Mumbai). Both `ap-south-1` and `ap-south-2` must be allowed in IAM for the India geographic profile.
4. On your Mac (no GPU needed): `aws configure sso` → `aws sso login --profile epr` → `export AWS_PROFILE=epr`. boto3 picks this up; there are no keys in `.env`.

#### Phase 1 — Bedrock provider + Guardrails + Lambda (≈ 1 weekend)

**1. Enable the model.** In the Bedrock console, open model access / inference profiles and copy the **India geographic inference profile ID** for the Claude model you choose (don't type it from memory — copy it). Anthropic models may ask for first-time use-case details.

**2. Add a provider** (`rag/llm_bedrock.py`):

```python
import os
import boto3
from botocore.config import Config

REGION = os.getenv("AWS_REGION", "ap-south-1")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID")  # paste India geographic inference profile ID

_client = None
def _bedrock():
    global _client
    if _client is None:
        _client = boto3.client(
            "bedrock-runtime",
            region_name=REGION,
            config=Config(read_timeout=20, retries={"max_attempts": 2, "mode": "standard"}),
        )
    return _client

def generate(system_prompt: str, context: str, question: str) -> str:
    resp = _bedrock().converse(
        modelId=MODEL_ID,
        system=[{"text": system_prompt}],
        messages=[{
            "role": "user",
            "content": [{"text": f"<context>\n{context}\n</context>\n\nQuestion: {question}"}],
        }],
        inferenceConfig={"maxTokens": 700, "temperature": 0},  # drop any param the chosen model rejects
    )
    return resp["output"]["message"]["content"][0]["text"]
```

Wire it into `get_active_llm()`:

```python
if os.getenv("BEDROCK_MODEL_ID"):
    return ("bedrock", bedrock_generate)
# …existing Groq / OpenRouter / Gemini / OpenAI blocks…
# no provider → mock mode (unchanged)
```

Any exception → your existing FR-Q11 fallback to mock mode.

**3. Create a Guardrail** (console → Bedrock → Guardrails): enable **contextual grounding check** (grounding + relevance thresholds; start moderate, tune on your golden set). Then call it on every answer:

```python
gr = boto3.client("bedrock-runtime", region_name=REGION)

def grounded(context: str, question: str, answer: str) -> bool:
    r = gr.apply_guardrail(
        guardrailIdentifier=os.environ["GUARDRAIL_ID"],
        guardrailVersion=os.environ["GUARDRAIL_VERSION"],
        source="OUTPUT",
        content=[
            {"text": {"text": context,  "qualifiers": ["grounding_source"]}},
            {"text": {"text": question, "qualifiers": ["query"]}},
            {"text": {"text": answer,   "qualifiers": ["guard_content"]}},
        ],
    )
    return r["action"] != "GUARDRAIL_INTERVENED"
```

If `False` → return mock-mode chunks + "could not verify answer against sources". **Keep your own numeric verifier too**: the managed check is an ML classifier, not a proof.

**4. Package for Lambda.** Keep your Dockerfile; add the Lambda Web Adapter so Flask runs unchanged:

```dockerfile
FROM python:3.12-slim
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:<PIN_A_RELEASED_VERSION> /lambda-adapter /opt/extensions/lambda-adapter
ENV PORT=5000 AWS_LWA_PORT=5000
WORKDIR /app
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m appuser && chown -R appuser /app
USER appuser
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "1", "app:app"]
```

Minimal AWS SAM template (`template.yaml`):

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: AWS::Serverless-2016-10-31
Resources:
  EprApi:
    Type: AWS::Serverless::Function
    Metadata: { Dockerfile: Dockerfile, DockerContext: . }
    Properties:
      PackageType: Image
      MemorySize: 1024
      Timeout: 30
      ReservedConcurrentExecutions: 5        # hard cost/abuse ceiling
      FunctionUrlConfig: { AuthType: NONE }  # put CloudFront in front when public
      Environment:
        Variables:
          BEDROCK_MODEL_ID: "<india-geo-inference-profile-id>"
          GUARDRAIL_ID: "<id>"
          GUARDRAIL_VERSION: "1"
      Policies:
        - Statement:
            - Effect: Allow
              Action: [bedrock:InvokeModel, bedrock:ApplyGuardrail]
              Resource: "*"   # tighten to the inference-profile + foundation-model ARNs in BOTH ap-south-1 and ap-south-2
```

Deploy: `sam build && sam deploy --guided`. Do **not** put the function in a VPC (avoids NAT-gateway charges you don't need).

**5. Rate-limit in-app** (e.g. Flask-Limiter, per-IP) in addition to reserved concurrency.

**Definition of done for Phase 1:** `/health` reports `provider: bedrock`; killing Bedrock access makes the app fall back to mock mode; a deliberately ungrounded answer is blocked by the guardrail *and* by your verifier; the budget alarm is firing in a test.

#### Phase 2 — retrieval upgrade (no new AWS service required)
1. Re-chunk to clause level (one section/sub-rule per chunk, 150–400 tokens) with metadata from §7.
2. Hybrid search: BM25 + embeddings (compute embeddings **offline at build time** — Bedrock embedding model or a small local model on your CPU-only Mac — and ship the vectors with the image so runtime retrieval stays key-free), then rerank top 20 → top 4.
3. Add **temporal filtering**: default to rules effective on today's date; allow an "as of" parameter.
4. Only move to **Bedrock Knowledge Bases + S3 Vectors** when you need user-uploaded documents or many tenants.

#### Phase 3 — update pipeline, invoice parser, workspaces
**Notice watcher (highest value):**
1. EventBridge Scheduler (daily) → Lambda fetches the official notice pages you choose; hash page content; if changed, store raw HTML/PDF in S3 (`raw/<date>/…`). Check each site's terms/robots before scraping; fall back to manual upload if disallowed.
2. Step Functions: extract text → Bedrock (a small/cheap model) produces a *structured diff proposal* (`{rule_id, old, new, effective_from, source_quote_locator}`).
3. SNS/SES emails **you** a link to a minimal review page; you approve/reject. **No auto-publish.**
4. On approve: write new `rules.json` + KB version to S3, trigger CI evals, then deploy.

**Invoice/BOM parser:** Textract `AnalyzeExpense` (or Bedrock Data Automation) → line items → Claude classifies each into Cat I–V with a confidence score and the reasoning shown → **user confirms** → tonnage per category feeds the calculator.

**Workspaces:** Cognito (sign-in) + DynamoDB (saved calculations keyed by tenant, with the `ruleset_version` used so old results stay reproducible). Keep stateless mode as the default; workspaces are opt-in. If you store accounts/emails of Indian users, check obligations under India's DPDP Act with someone qualified.

### 6.5 Cost and safety controls (non-negotiable)
- Budget alarms on day 1; reserved concurrency cap on the function.
- Estimate per-query cost = `(input tokens × input price + output tokens × output price)` using the current Bedrock pricing page for your chosen model; a RAG query is roughly "4 chunks + prompt" in, a short answer out. Use a small model for the judge and for pipeline extraction.
- Avoid always-on fixed-cost components (NAT gateway, WAF, OpenSearch Serverless) until revenue justifies them.
- Check **AWS Activate / student credits** eligibility.
- Never log raw question text if you keep the "no user data stored" promise; log counters and hashes.
- Data handling: confirm Bedrock's data-protection terms in AWS docs before telling clients "your prompts aren't stored or used for training."

---

## 7. Proposed data model (single source of truth)

`rules/rules.json` — every number carries provenance. Values below are **working corrections, `needs_verify` until you confirm against the Gazette/CPCB text**.

```json
{
  "ruleset_version": "2026-10-10.1",
  "sources": [
    {"id": "gsr133e-2022", "title": "PWM Amendment Rules 2022 – Schedule II EPR guidelines", "url": "<gazette url>", "sha256": "<hash>", "retrieved_on": "2026-10-10"},
    {"id": "cpcb-ec-2024-04-04", "title": "CPCB EC guidelines (renewed 4 Apr 2024)", "url": "<cpcb url>", "sha256": "<hash>", "retrieved_on": "<date>"}
  ],
  "recycling_min_pct": {
    "2024-25": {"I": 50, "II": 30, "III": 30, "IV": 50},
    "2025-26": {"I": 60, "II": 40, "III": 40, "IV": 60},
    "2026-27": {"I": 70, "II": 50, "III": 50, "IV": 70},
    "2027-28": {"I": 80, "II": 60, "III": 60, "IV": 80},
    "2028-29": {"I": 80, "II": 60, "III": 60, "IV": 80},
    "_meta": {"applies_to": "EPR target Q", "status": "needs_verify", "source_ids": ["gsr133e-2022"]}
  },
  "recycled_content_pct": {
    "2025-26": {"I": 30, "II": 10, "III": 5},
    "2026-27": {"I": 40, "II": 10, "III": 5},
    "2027-28": {"I": 50, "II": 20, "III": 10},
    "2028-29": {"I": 60, "II": 20, "III": 10},
    "_meta": {"III_basis": "weight of plastic layers only", "status": "needs_verify"}
  },
  "environmental_compensation": {
    "inr_per_mt_by_consecutive_year": {"1": 5000, "2": 10000, "3": 20000},
    "category_specific_rates": "UNRESOLVED – check guideline",
    "refund_pct_by_year_of_fulfilment": {"1": 75, "2": 60, "3": 40},
    "status": "needs_verify"
  },
  "deadlines": [
    {"fy": "2025-26", "entity": "PWP",  "date": "2026-10-31", "basis": "MoEFCC extension 2026-08-28", "source_id": "<notice>"},
    {"fy": "2025-26", "entity": "PIBO", "date": "2026-12-31", "basis": "MoEFCC extension 2026-08-28", "source_id": "<notice>"}
  ]
}
```

Every KB chunk gets: `id, title, citation, source_id, page/clause, effective_from, superseded_by, retrieved_on, verified_by, verified_on, confidence, text`.

**Golden calculator vectors (add to `test_calculator.py` once verified):**

| Input | Expected |
|---|---|
| Cat II, EPR target 100 MT, FY 2027-28 | min. recycling = 60 MT |
| Cat I, EPR target 100 MT, FY 2026-27 | min. recycling = 70 MT |
| Cat IV, EPR target 100 MT, FY 2026-27 | min. recycling = 70 MT (**currently 100 in SRS**) |
| Cat III, 100 MT plastic-layer weight, FY 2026-27 | recycled content = 5 MT (**currently 10 in SRS**) |
| Shortfall 10 MT, 2nd consecutive year | EC = ₹1,00,000 (not ₹50,000) |

---

## 8. Evaluation harness (LLM-as-judge in CI)

**Golden set (≥ 100 items), human-verified:**
- 40 factual (numbers, dates, definitions) with expected value + expected chunk IDs
- 20 paraphrase variants of the above (retrieval robustness)
- 15 **temporal** ("what was the PIBO deadline for FY 2024-25?", "as of today…")
- 15 **abstention** (out-of-corpus; must say it doesn't know)
- 10 adversarial (prompt injection in the question, "ignore context and guess", leading questions with wrong premises)

**Metrics and gates:**

| Metric | Method | Release gate |
|---|---|---|
| Retrieval recall@4 | gold chunk IDs in top-4 | ≥ 0.90 |
| Citation validity | every `[kbXXX]` exists and supports the sentence | 100% exist; ≥ 95% support |
| **Numeric exactness** | every number/date/clause in answer ⊂ cited chunk text (regex, no LLM) | **100%** |
| Faithfulness | judge LLM (different model family) scores claims vs. context, rubric 1–5 | mean ≥ 4.5, no claim < 3 |
| Abstention accuracy | correct "insufficient information" on OOC set | ≥ 90% |
| Calculator golden vectors | exact match | 100% |
| Latency / cost | p95 < 10 s; cost/query tracked | alert on regression |

**Judge prompt skeleton:**

```
You are a strict auditor. Given CONTEXT, QUESTION, ANSWER:
1. List every factual claim in ANSWER (numbers, dates, entities, obligations).
2. For each claim, quote the supporting span from CONTEXT or mark UNSUPPORTED.
3. Flag any claim that states something about a different fiscal year than asked.
Output JSON: {"claims":[{"text":..,"support":..|null}],"score":1-5,"fatal":bool}
Fatal = any unsupported number, date, amount or clause reference.
```

Run on every PR; block merge on gate failure. Re-run the full set whenever `rules.json` or KB changes.

---

## 9. Roadmap

| Window | Deliverables |
|---|---|
| **Days 1–14** | Fix §3.1 errors · rules.json + provenance · numeric verifier · golden set v1 (50 items) · CI gate · "rules last verified" banner |
| **Days 15–30** | AWS Phase 0 + Phase 1 (Bedrock, Guardrails, Lambda, budgets) · rate limits · public beta with explicit disclaimers |
| **Days 31–60** | Clause-level KB (300+ chunks) · hybrid retrieval · temporal filtering · golden set 100+ · observability |
| **Days 61–90** | Notice watcher + review queue · email alerts · pilot with 2–3 EPR consultants/SMEs · decide on workspaces vs. white-label |

---

## 10. Things I could not verify (resolve before marking anything `verified`)

1. Exact Gazette wording for Cat II/III recycled-content values in 2026-27 (sources disagree: 10 vs 15 vs 20 for Cat II; 5 vs 7 vs 10 for Cat III).
2. Whether EC rates are flat or category-specific, and the current refund percentages.
3. The 2026 amendment details: Rule 11 QR/barcode mandate, Sellers, traceability, registered auditors.
4. Effective date and legal home of non-plastic EPR (paper/glass/metal).
5. Portal migration date and any new registration steps for the Common EPR Portal.
6. Current certificate price ranges per category.
7. Exact Bedrock model IDs / pricing in your account and region (copy from console; check the pricing page).

---

## 11. Sources consulted

**Regulatory (secondary — confirm with primary text)**
- https://www.karparivartan.com/plastic-epr-in-india-a-complete-guide-to-packaging-categories-targets-and-compliance/
- https://greensutra.in/news/plastic-epr-explained-2026/
- https://beaconfiling.com/glossary/extended-producer-responsibility
- https://treelife.in/compliance/epr-registration-for-plastic-packaging/
- https://afleo.com/epr-registration-for-plastic-waste-management/
- https://recircle.in/epr-penalties-in-india-what-happens-if-companies-fail-to-meet-plastic-recycling-targets/
- https://sigmaearth.com/extended-producer-responsibility-epr-for-plastic-waste/
- https://teamleaseregtech.com/updates/article/59143/moefcc-issued-extension-in-timeline-for-filing-of-annual-returns-of-pwps-and-pibos/
- https://teamleaseregtech.com/updates/article/53906/cpcb-notified-the-extension-of-annual-return-filing-by-registered-pibos-for-fy-2024-25/
- https://lexplosion.in/?p=152383
- https://alephindia.in/environmental-protection-extended-producer-responsibility-rules-for-packaging-and-sanitary-waste-2024.php
- https://www.recykal.com/articles/draft-epr-rules-2025-for-paper-glass-and-metal-packaging-explained

**Competitors / prior art**
- https://www.recykal.com/epr-plastic · https://www.recykal.com/epr
- https://sukra.net/ · https://www.regilient.ai/environmental-compliance/epr-compliance-software
- https://www.sourceintelligence.com/solution/epr · https://packgine.ai/ · https://algorep.ai/blog/epr-compliance-software-2026
- https://github.com/CodewithEvilxd/Automate-lndia
- https://github.com/dhruvsharma-0001/epr-copilot (this project's public repo)

**AWS**
- https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-expands-claude-model-availability-to-india-cross-region-inference/
- https://aws.amazon.com/blogs/machine-learning/introducing-openai-models-on-amazon-bedrock-for-in-country-inferencing-in-india/
- https://aws.amazon.com/bedrock/faqs/
- https://docs.aws.amazon.com/general/latest/gr/bedrock.html
- https://aws.amazon.com/about-aws/whats-new/2026/03/s3-vectors-expands-17-regions
- https://docs.aws.amazon.com/apprunner/latest/dg/apprunner-availability-change.html (App Runner closed to new customers)

---

*Next step I'd suggest: share the repo's `knowledge_base.py` and `calculator.py` and I can run the same audit against the actual code and KB text (the SRS review above can't see implementation bugs).*
