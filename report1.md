# LLM-as-Judge Report — EPR Compliance Copilot

| Field | Value |
|---|---|
| **Judge role** | Independent LLM evaluator (judge mode) |
| **Date** | 10 Oct 2026 |
| **Repo** | `epr-copilot` @ commit `fede678` (+ uncommitted working tree) |
| **Scope** | Full project: backend, RAG pipeline, calculator, parser, validator, marketplace, frontend, tests, Docker, CI, docs |
| **Verification performed** | Not just code reading — test suite executed, live server booted, and flagged bugs **reproduced by running the code** |

---

## 1. Executive Summary

**Overall score: 6.8 / 10 — Strong, honest, well-engineered prototype. Not yet production-grade.**

This is a genuinely well-thought-out project: a Flask + LangGraph RAG assistant for India's plastic EPR rules with a deterministic compliance calculator, multi-provider LLM routing (Bedrock → Groq → OpenRouter → Gemini → Claude → OpenAI → mock fallback), a curated 22-chunk statutory knowledge base with confidence tiers, and 18 passing tests. The engineering culture is visibly good — disclaimers everywhere, `needs_verify` discipline, singleton graph caching, NaN/Inf sanitization, non-root Docker.

However, judging is evidence-based, and I found **two confirmed functional bugs in the brand-new Invoice Parser on its own bundled sample data**, an **unreachable UI tab**, a **false-positive compliance check**, zero test coverage on 3 of 7 `rag/` modules, and an **LLM-output XSS vector**. The newest features (parser, validator, marketplace) are uncommitted, untested, and below the quality bar of the older core.

> **One-line verdict:** *Excellent skeleton and core (calculator, RAG, infra); the last mile (new modules) was built faster than it was verified.*

---

## 2. Scoring Rubric

| # | Dimension | Score | Weight | Notes |
|---|---|---|---|---|
| 1 | Architecture & Code Quality | 8.0 | 12% | Clean layering, typed, documented |
| 2 | RAG / AI Engineering | 7.0 | 15% | Honest TF-IDF tradeoff, strict anti-hallucination prompt; no eval harness |
| 3 | Domain Correctness (verified) | 6.0 | 15% | Calculator solid; parser bugs confirmed |
| 4 | Security | 5.5 | 13% | Good container hygiene; XSS vector, no rate limiting |
| 5 | Testing & QA | 5.0 | 13% | 18/18 pass, but ~43% of rag modules uncovered |
| 6 | Documentation Accuracy | 7.5 | 10% | README mostly accurate; drift on new modules |
| 7 | DevOps & Deployment | 7.0 | 8% | Non-root Docker + healthcheck + CI matrix; unpinned deps |
| 8 | Regulatory Grounding | 8.5 | 6% | Confidence tiers + citations is the right design |
| 9 | Frontend / UX | 7.0 | 5% | Clean tabs, presets, exports; orphaned tab |
| 10 | Repo Hygiene | 6.0 | 3% | Uncommitted feature modules at "v1.0.0" |
| | **Weighted overall** | **6.8 / 10** | | |

---

## 3. Verified Findings (Evidence, Not Opinion)

### BUG-1 (High) — Invoice Parser double-counts grand totals on its own sample
`rag/parser.py:130` only skips total lines containing "quantity", "weight", or "invoiced". The bundled sample `snack_food` ends with `TOTAL ANNUAL ESTIMATE: 395.0 MT`, which is **not** skipped and gets ingested as a Category I line item.

Reproduced by running the code:
```
total_mt: 790.0                      ← should be 395.0
{'cat_1': 395.0, 'cat_2': 120.0, 'cat_3': 275.0, 'cat_4': 0.0}
TOTAL ANNUAL ESTIMATE: 395.0 MT -> cat_1 395.0   ← phantom entry
```
Impact: any liability computed from this parse is 2× overstated. There is no test for `parser.py`, so CI cannot catch it.

### BUG-2 (High) — Rigid Cat I item misclassified as Flexible Cat II
Same run, same sample: `"Rigid Polypropylene (PP) Sweet Boxes & Trays with Lid (Category I Rigid)"` → **cat_2**. Root cause: keyword scoring double-counts `"pp"` (matches inside "polypropylene") so Cat II scores 2 vs Cat I's 1 (`"rigid"`), while `"tray"`, `"box"`, `"lid"` are absent from the Cat I keyword list.

Impact: Category I carries a **70%** recycling target in FY 2026-27 vs **50%** for Cat II — this misclassification directly understates statutory obligation. That is exactly the kind of error this product exists to prevent.

### BUG-3 (Medium) — Validator passes a product barcode as a "Traceability QR Code"
`rag/validator.py:46` regex accepts `barcode`, so the `borderline_ldpe` sample's retail barcode `8901234567890` passes the Rule 11(1)(e) traceability check. Reproduced: check status `PASS` on a label that has no QR at all. A compliance tool should fail closed on ambiguous evidence, not pass open.

### BUG-4 (Medium) — Orphaned UI tab
`templates/index.html:222` defines a `complianceTab` (Quick Statutory Compliance Check), but the tab bar (`index.html:28-33`) has no button for it. The feature is unreachable by users, while `app.js:6` still eagerly fetches its data on every page load. Dead feature shipping live API calls.

### BUG-5 (Medium) — Fabricated provenance claim in API response
`rag/parser.py:177` hardcodes `"aws_service_used": "Amazon Textract (OCR) + Amazon Bedrock (Polymer Categorization)"` — but the parser is pure local regex; no AWS service is invoked. For a compliance product, claiming an AWS pipeline that doesn't exist is a credibility defect, especially in a hackathon judged on AWS alignment.

### SEC-1 (High) — LLM output rendered via `innerHTML` (stored-XSS-shaped vector)
`static/js/app.js:77-87` injects `data.answer` and citation metadata straight into `innerHTML` after only `\n → <br>` replacement. In live mode the answer is LLM-generated text; in any future setup where KB text or LLM output contains HTML, it executes in the user's browser. Use `textContent` / a sanitizer.

### SEC-2 (Medium) — No rate limiting on `/api/ask`
`app.py:180` forwards every request to a potentially paid LLM with no throttling, no auth, and a 64 KB body cap as the only guard. One user can burn the Groq/OpenAI quota. Fine for localhost; a real risk on any public deploy.

### QA-1 (High) — New modules have zero test coverage
`rag/parser.py`, `rag/validator.py`, `rag/marketplace.py` — the three newest, buggiest modules — are covered by **0 of 18 tests**. The 18 passing tests all cover the older, more mature modules. Test suite passes ≠ test suite is adequate.

### DOC-1 (Medium) — README structure drift
`README.md:122-153` "Project Structure" omits `rag/parser.py`, `rag/validator.py`, `rag/marketplace.py` and the new API endpoints (`/api/parse_invoice`, `/api/validate_artwork`, `/api/marketplace*`, `/api/rules-version`, `/api/compliance-check`). README is v1.0.0-frozen while the working tree moved on.

### HYG-1 (Medium) — Uncommitted feature code at a released version
Git status shows `parser.py`, `validator.py`, `marketplace.py`, `SRS-1.md`, `report.md`, `roadmap-1.md`, `sprint_plan.md` untracked, and `app.py`, `app.js`, `app.css` modified. The repo claims a stable v1.0.0 release, but a third of the functionality exists only as loose working-tree state — unreproducible from the tag.

### Minor issues
- `rag/chain.py:118` & `140`: comment numbering drifts (two sections labeled "── 2.").
- `app.py:137`: unknown entity falls back to Brand Owner silently instead of 404 — masks client errors.
- `chain.py:114` etc.: provider failures logged with `print()`, not the configured `logger`.
- `calculator.py`: UI advertises escalating EC rates (₹5k → ₹10k → ₹20k/MT, `index.html:195-198`) but the calculator models a flat ₹5,000/MT with hardcoded refund fractions — presentation and engine disagree.
- `requirements.txt`: unpinned `>=` ranges (CI built on whatever is latest today); `pytest` ships in the production image.
- `validator.py:118`: empty-text branch reports `failed_count = 5` while normal path uses `total_checks = 4`.
- KB confidence distribution is 21 × `verified`, 1 × `reported`, **0 × `needs_verify`** — the tier system is designed but effectively unused, which slightly weakens the honesty story.

---

## 4. What Is Genuinely Good

1. **Deterministic calculator is the best module in the repo.** `_safe_tonnage` guards NaN/Inf/negatives/strings (`calculator.py:96-105`), and `test_calculator.py` asserts exact statutory math (195 MT obligation → ₹975,000 EC exposure). This is audit-grade code.
2. **Honest AI engineering posture.** TF-IDF is chosen with the tradeoff *written down* (`retriever.py:1-18`), mock mode is a first-class citizen, and the system prompt (`chain.py:36-57`) forbids outside knowledge and invented numbers. The `verified / reported / needs_verify` citation badges are the correct design for legal RAG.
3. **Resilient provider routing with real fallback.** Every provider init is try/except with graceful degradation to mock (`chain.py:287-299` falls back to mock generator on live-call failure). I booted the app: `/health` returned `ok`, 22 chunks, mock mode; `/api/ask` returned 4 citations.
4. **Verified README claims.** "18 passing tests" — I ran them: **18 passed in 8.6s** on Python 3.12. Health endpoint, KB count of 22, print stylesheet (`app.css:343`) all check out.
5. **Ops hygiene above prototype average.** Non-root Docker user, healthcheck, gunicorn, 64 KB payload cap, `detect-secrets` pre-commit, CI matrix (3.11/3.12).
6. **Domain authenticity.** Correct Cat II vs Cat III layer-composition boundary, IS/ISO 17088 for Cat IV, June 30 filing deadline, MSE exemption nuance — this reads like someone actually studied the Gazette.

---

## 5. Risk Assessment

| Risk | Severity | Likelihood | Commentary |
|---|---|---|---|
| Parser misclassification inflates/deflates statutory obligation | **High** | Certain (reproduced) | Core use case of the feature |
| XSS via LLM/KB content | High | Low–Med | Requires hostile content; innerHTML makes it possible |
| Quota exhaustion on public deploy | Med | High | No throttling |
| Users act on validator false-positives | Med | Med | Barcode ≠ QR |
| Unreproducible release (uncommitted code) | Med | Certain | Working tree ≠ v1.0.0 tag |

---

## 6. Prioritized Recommendations

**P0 — before anyone relies on this**
1. Fix parser total-line skip (match `total` + any of `quantity|weight|invoiced|estimate|annual`) and de-duplicate `"pp"`/`"polypropylene"` scoring; add `tray`, `box`, `lid`, `closure` to Cat I keywords.
2. Add `tests/test_parser.py`, `tests/test_validator.py`, `tests/test_marketplace.py` — starting with the two repro'd bugs as regression tests.
3. Replace `innerHTML` rendering with `textContent`-based building or DOMPurify.
4. Commit the working tree; make the release tag match reality.

**P1 — production readiness**
5. Add rate limiting (`flask-limiter`) and a 440/404 for unknown entities on `/api/compliance-check`.
6. Change the barcode regex to require QR specifically (`qr|QR code|traceability`), failing closed otherwise.
7. Pin dependencies (compile a lock file); move `pytest` to dev extras only.
8. Model the escalating EC schedule (₹5k/₹10k/₹20k) in `calculator.py` so UI and engine agree.

**P2 — polish**
9. Update README project structure & API table; unify chain.py numbering; route provider warnings through `logger`.
10. Add a small RAG eval set (10–20 Q→expected-chunk pairs) and wire it into CI; use `needs_verify` tier for the genuinely uncertain chunks.
11. Wire the orphaned `complianceTab` into the tab bar or delete it.

---

## 7. Score Justification (Why 6.8, Not 7.5 or 6.0)

- **Not higher** because a judge cannot award "production-ready" to a compliance product whose newest flagship feature (invoice parsing) demonstrably doubles tonnage and flips statutory categories on its own demo data — with no tests guarding it — and whose frontend executes LLM output as HTML.
- **Not lower** because the core engine (calculator + retrieval + routing + ops) is solid, honestly documented, verified by an actually-passing test suite, and the failures found are localized, reproducible, and cheap to fix. The project also self-discloses its limitations (disclaimers, prototype framing) rather than overselling — minus the one fabricated `aws_service_used` claim.

**Grade band: B (strong prototype / pre-production).** Fix P0 items and re-run judge: realistic ceiling 8.0–8.3.

---

## 8. Verification Log

| Check | Command | Result |
|---|---|---|
| Test suite | `py -3.12 -m pytest tests/ -v` | **18 passed**, 1 deprecation warning (`langchain-community` sunset) |
| Live boot | `app.py` on :5001, `GET /health` | `{"status":"ok","kb_chunks":22,"provider":"mock"}` |
| Live Q&A | `POST /api/ask` | mode=mock, 4 citations, answer 2869 chars |
| Parser bug | `parse_packaging_text(SAMPLE_INVOICES['snack_food'])` | total 790 MT (expected 395); rigid item → cat_2 |
| Validator bug | `validate_packaging_artwork(borderline_ldpe)` | Barcode passed as traceability QR |
| Print styles claim | grep `@media print` in `static/css/app.css` | Found (line 343) |
| CI workflow exists | file inspection | `.github/workflows/ci.yml` present (README accurate) |

*End of report1.md — generated by LLM-as-Judge, evidence-based.*
