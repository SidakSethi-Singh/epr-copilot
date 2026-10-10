# EPR Copilot — Roadmap

> Current state: **Demo/MVP (score 56/100)**  
> Target: **Production-grade compliance tool with paying users**

---

## Phase 0 — Fix What's Broken (Days 1–7)

**Goal:** Stop the app from giving confident wrong answers.

| # | Task | Why | Status |
|---|------|-----|--------|
| 0.1 | Fix Cat IV recycling targets (currently 100%, should be 50→60→70→80%) | Silent wrong answer — users get penalized trusting this | ⬜ |
| 0.2 | Fix Cat II recycled content (currently 10/20/30/30, should be ~10/10/20/20) | Same — wrong number, wrong penalty calc | ⬜ |
| 0.3 | Fix Cat III recycled content (currently 5/10/10/10, should be ~5/5/10/10) + add "plastic layers only" note | Wrong basis for calculation | ⬜ |
| 0.4 | Fix EC refund schedule (currently 85/60/30%, should be 75/60/40%) | Penalty exposure estimate is wrong | ⬜ |
| 0.5 | Fix EC rate — add escalation (₹5k → ₹10k → ₹20k for consecutive years) | Currently assumes flat rate | ⬜ |
| 0.6 | Remove hardcoded "typical extension Sept/Oct" — replace with dated, sourced notice entries | Already stale — FY 2025-26 PIBO deadline is 31 Dec 2026 | ⬜ |
| 0.7 | Add `effective_from`, `source_url`, `retrieved_on`, `verified_by` to every KB chunk | No provenance = no trust | ⬜ |
| 0.8 | Add visible **"Rules last verified: <date>"** banner in UI | Users need to know data freshness | ⬜ |
| 0.9 | Label calculator output as "simplified estimate" (real formula uses 2-year avg EPR target Q) | Prevents false precision | ⬜ |

**Deliverable:** All statutory numbers verified against Gazette PDFs. Zero confident wrong answers.

---

## Phase 1 — Data Integrity & Safety Net (Days 8–21)

**Goal:** Single source of truth + automated verification.

| # | Task | Why |
|---|------|-----|
| 1.1 | Create `rules/rules.json` — all targets, rates, deadlines in one versioned file with source provenance | Calculator tables and KB text currently separate → will diverge |
| 1.2 | Make calculator + KB read from `rules.json` — tests assert they agree | Eliminates silent drift |
| 1.3 | Build post-generation **numeric/citation verifier** — regex-check every number, date, clause ref in LLM answer against cited chunk text | LLM prompt rules are suggestions; verifier is enforcement |
| 1.4 | On verifier failure → return mock-mode chunks + "could not verify answer" | Fail safe, not fail silent |
| 1.5 | Create golden eval set v1 (50 items: 20 factual, 10 paraphrase, 10 abstention, 10 adversarial) | Can't improve what you can't measure |
| 1.6 | Add CI gate — eval suite runs on every PR, blocks merge on failure | Prevents regression |
| 1.7 | Add per-IP rate limiting (Flask-Limiter) | Currently zero abuse protection |

**Deliverable:** `rules.json` is the single truth. Every answer is machine-verified. CI catches regressions.

---

## Phase 2 — AWS Deployment & Bedrock (Days 22–35)

**Goal:** Production hosting with in-country inference, no API keys in code.

| # | Task | Why |
|---|------|-----|
| 2.1 | AWS account setup — IAM Identity Center, MFA, budget alarm (small USD cap) | Safety first |
| 2.2 | Enable Bedrock Claude (India geographic inference profile — Mumbai/Hyderabad) | In-country inference, no free-tier dependency |
| 2.3 | Add Bedrock provider to `get_active_llm()` — IAM role auth, no `.env` keys | Clean credential management |
| 2.4 | Create Bedrock Guardrail with contextual grounding check | Independent hallucination guard alongside your verifier |
| 2.5 | Package Flask app for Lambda (container + Lambda Web Adapter) | Scale-to-zero, cheap for spiky traffic |
| 2.6 | Deploy via SAM — reserved concurrency = 5 (hard cost ceiling) | Prevents surprise bills |
| 2.7 | Add CloudWatch logging + spend alerts at 50/80/100% of budget | Observability from day 1 |
| 2.8 | Keep Groq/OpenRouter/mock as fallbacks — Bedrock down → auto-fallback | Reliability |

**Deliverable:** App live on AWS. Bedrock inference. Budget-capped. Mock fallback preserved.

---

## Phase 3 — Retrieval Upgrade (Days 36–55)

**Goal:** Handle real-world question variety, not just keyword matches.

| # | Task | Why |
|---|------|-----|
| 3.1 | Re-chunk KB to clause level (one section/sub-rule per chunk, 150–400 tokens) → 300+ chunks | Current 22 chunks too coarse — misses specific sub-rules |
| 3.2 | Add missing regulatory content — Cat V (biodegradable), reuse obligations, carry-forward rules, Common EPR Portal | Gaps identified in report |
| 3.3 | Implement hybrid retrieval: BM25 + embeddings (compute at build time, ship vectors with image) | TF-IDF misses semantic matches ("who must register?" vs "PIBO obligated entity") |
| 3.4 | Add reranker — top 20 → top 4 | Better precision on retrieved chunks |
| 3.5 | Add temporal filtering — default to rules effective today, allow "as of <date>" param | Legal answers are time-dependent |
| 3.6 | Expand golden eval set to 100+ items (add 15 temporal, 15 paraphrase, 10 adversarial) | Validates retrieval upgrade |
| 3.7 | Add retrieval metrics to observability — hit rate, recall@k, abstention rate | Measure retrieval quality |

**Deliverable:** Semantic search over 300+ chunks. Time-aware answers. Measurable retrieval quality.

---

## Phase 4 — Regulatory Update Pipeline (Days 56–75)

**Goal:** Rules stay current without manual monitoring.

| # | Task | Why |
|---|------|-----|
| 4.1 | EventBridge Scheduler (daily) → Lambda fetches CPCB/MoEFCC notice pages → hash diff → store in S3 | Deadlines were extended 4+ times last year — users can't afford to miss one |
| 4.2 | Step Functions: extract text → Bedrock (cheap model) produces structured diff proposal | Automated change detection |
| 4.3 | SNS/SES emails you a review link → you approve/reject on a minimal review page | **No auto-publish** — human gate for legal data |
| 4.4 | On approve: write new `rules.json` + KB version to S3 → CI evals run → deploy | Versioned, tested updates |
| 4.5 | Add "What Changed" section in UI — dated changelog of rule updates | Users see freshness at a glance |
| 4.6 | Email/webhook alerts for subscribed users when deadlines change | This is what people will pay for |

**Deliverable:** Semi-automated regulatory update pipeline. Human-approved. Users get deadline alerts.

---

## Phase 5 — Invoice Parser & Agentic Flow (Days 76–100)

**Goal:** Eliminate manual tonnage entry — upload docs, get obligations.

| # | Task | Why |
|---|------|-----|
| 5.1 | Invoice/BOM upload endpoint (PDF, image) | Users have invoices, not category-wise tonnage breakdowns |
| 5.2 | Textract `AnalyzeExpense` or Bedrock Data Automation → extract line items | Structured extraction from unstructured docs |
| 5.3 | LLM classifies each line item into Cat I–V with confidence + reasoning shown | Transparent classification |
| 5.4 | User confirms/corrects classification → feeds calculator | Human-in-the-loop for accuracy |
| 5.5 | Implement agentic tool-calling — LLM decides when to call calculator vs retriever vs parser | Converse API tool-use, not a full agent framework |
| 5.6 | Implement real EPR target Q formula (2-year average of introduced packaging) | Replace "simplified estimate" with accurate calc |

**Deliverable:** Upload invoice → get categorized obligations. Agent orchestrates tools.

---

## Phase 6 — Multi-Tenant & Monetization (Days 101–130)

**Goal:** Paying users. Saved state. Audit trails.

| # | Task | Why |
|---|------|-----|
| 6.1 | Cognito auth (sign-in/sign-up) | Gate access, identify users |
| 6.2 | DynamoDB — saved calculations keyed by tenant + `ruleset_version` | Audit trail, reproducibility |
| 6.3 | Multi-year compliance history dashboard | "Show me my obligations for the last 3 FYs" |
| 6.4 | White-label mode for EPR consultants (custom branding, client management) | Best go-to-market for this product |
| 6.5 | CloudFront + custom domain + HTTPS | Production-grade frontend |
| 6.6 | DPDP Act compliance check (if storing Indian user data) | Legal requirement |
| 6.7 | ToS + legal review of disclaimer | Before charging money |
| 6.8 | Load test beyond 20 concurrent users | Validate scaling |

**Deliverable:** SaaS-ready. Auth. Saved state. White-label. Revenue.

---

## Phase 7 — Expansion (Days 130+)

| # | Task | Why |
|---|------|-----|
| 7.1 | Hindi language support (translate answers, always show English source alongside) | India's most spoken language |
| 7.2 | Non-plastic EPR streams — paper, glass, metal (EPR for Packaging Rules, 2024) | Same user base, adjacent regulation |
| 7.3 | Battery waste + e-waste EPR modules | Cross-compliance — same companies face all three |
| 7.4 | Slack/Teams bot for compliance teams | Where people already work |
| 7.5 | Annual return worksheet generator — pre-filled from saved calculations | The real workflow end-point |
| 7.6 | CPCB portal integration (when API available) | Auto-fill registration forms |

---

## Milestone Summary

```
                          YOU ARE HERE
                               ↓
Phase 0 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  Fix wrong numbers
Phase 1  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  Single source of truth + verifier
Phase 2   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  AWS deploy + Bedrock
Phase 3    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  Semantic retrieval
Phase 4      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  Update pipeline
Phase 5        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  Invoice parser + agentic
Phase 6           ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  Multi-tenant SaaS
Phase 7              ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  Hindi, non-plastic, integrations
```

---

## What NOT to Build (Yet)

| Tempting Idea | Why Skip It |
|---------------|-------------|
| OpenSearch Serverless / Kendra | Overkill for <1000 chunks. High always-on cost. |
| SageMaker / GPU instances | All inference is managed (Bedrock). No custom models needed. |
| Full agent framework (AgentCore) | Converse API tool-use is enough. Keep it simple. |
| Competing with Recykal on certificate fulfilment | They own the marketplace. You own the explanation + calculation layer. |
| Mobile app | Web works fine. No user demand signal yet. |
| Real-time CPCB portal scraping | Legal risk. Use manual upload + daily hash checks with human review. |

---

## Success Metrics

| Phase | Metric | Target |
|-------|--------|--------|
| 0–1 | Regulatory accuracy (golden set) | 100% on verified claims |
| 1 | Numeric verifier pass rate | 100% (block on fail) |
| 2 | Uptime on AWS | 99.5% |
| 2 | Cost per query | < ₹2 |
| 3 | Retrieval recall@4 | ≥ 0.90 |
| 3 | Abstention accuracy (out-of-scope questions) | ≥ 90% |
| 4 | Rule update latency (notice → live) | < 48 hours |
| 5 | Invoice classification accuracy | ≥ 85% (with user confirmation) |
| 6 | Paying users (consultants or SMEs) | 5+ in first quarter |
| 6 | Monthly active users | 50+ |
