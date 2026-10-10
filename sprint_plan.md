# EPR Copilot — 4-Person Sprint Plan (3–5 Hours)

## Team Roles

```
Person 1: DATA FIXER          → Fix all wrong statutory numbers + build rules.json
Person 2: BACKEND ENGINEER    → Verifier + calculator upgrades + API hardening
Person 3: FRONTEND + UX       → UI improvements + new features + print/PDF
Person 4: AI / RAG ENGINEER   → Retrieval upgrade + LLM prompt tuning + eval set
```

---

## Person 1 — DATA FIXER (The Lawyer)

> **Mission:** Make every number in the app legally correct. You are the source of truth.

### Hour 1: Research & Verify
- [ ] Open the actual Gazette PDFs / CPCB notifications (not blogs)
- [ ] Verify and correct these **known wrong values**:

| What's Wrong | Current (Wrong) | Likely Correct | Your Job |
|---|---|---|---|
| Cat IV recycling targets | 100% every year | 50→60→70→80% (same as Cat I) | Confirm from Gazette |
| Cat II recycled content | 10/20/30/30 | 10/10/20/20 | Confirm |
| Cat III recycled content | 5/10/10/10 | 5/5/10/10 | Confirm |
| EC refund schedule | 85/60/30% | 75/60/40% | Confirm from CPCB EC guideline |
| EC rate | Flat ₹5,000/MT | ₹5k/₹10k/₹20k (escalating) | Confirm |
| Filing deadlines | "Typical Sept/Oct" | FY 2025-26: PWP 31 Oct, PIBO 31 Dec 2026 | Find latest notice |

### Hour 2: Create rules.json
- [ ] Create `rules/rules.json` — single source of truth file:

```json
{
  "ruleset_version": "2026-10-10.1",
  "verified_on": "2026-10-10",
  "verified_by": "Person1-Name",
  "recycling_min_pct": { ... },
  "recycled_content_pct": { ... },
  "environmental_compensation": { ... },
  "deadlines": [ ... ],
  "cert_price_ranges": { ... }
}
```

- [ ] Every number must have a `source` field (Gazette notification number + clause)

### Hour 3: Update Knowledge Base
- [ ] Update `rag/knowledge_base.py` — fix the 5 wrong chunks (kb006, kb007, kb008, kb009, kb013)
- [ ] Add `effective_from` and `source_url` to each chunk's metadata
- [ ] Add any missing chunks: Cat V (biodegradable), reuse obligations, carry-forward rules
- [ ] Tag anything unverified as `needs_verify`

### Hour 4: Sync with Person 2
- [ ] Make sure `calculator.py` reads from your corrected values
- [ ] Write 10 golden test vectors (input → expected output) for Person 2's tests
- [ ] Review Person 4's eval questions for factual accuracy

**Delivers to team:** Corrected `rules.json`, updated `knowledge_base.py`, 10 golden test vectors.

---

## Person 2 — BACKEND ENGINEER (The Builder)

> **Mission:** Calculator fixes, numeric verifier, API hardening. Make the backend bulletproof.

### Hour 1: Fix Calculator
- [ ] Update `rag/calculator.py` to read from Person 1's corrected values:
  - Fix Cat IV recycling targets
  - Fix Cat II/III recycled content percentages
  - Add EC escalation (₹5k → ₹10k → ₹20k for year 1/2/3)
  - Fix refund schedule (75/60/40%)
- [ ] Add `_meta` to calculator response: `"rules_version": "2026-10-10.1"`, `"disclaimer": "simplified estimate"`
- [ ] Update `ANNUAL_RETURN_DEADLINE` with sourced, dated entries (from Person 1)

### Hour 2: Build Numeric Verifier
- [ ] Create `rag/verifier.py`:

```python
def verify_answer(answer: str, cited_chunks: list[dict]) -> dict:
    """
    Regex-extract every number, date, ₹ amount, clause ref from answer.
    Check each exists in the text of at least one cited chunk.
    Return {verified: bool, ungrounded: [...]}
    """
```

- [ ] Wire into `chain.py` — after `generate_node`, run verifier
- [ ] If verifier fails → return mock-mode chunks + "could not verify answer against sources"

### Hour 3: API Hardening
- [ ] Add `flask-limiter` — 10 requests/minute per IP on `/api/ask`
- [ ] Add `/api/rules-version` endpoint — returns `rules.json` version + verified date
- [ ] Add `rules_version` and `verified_on` fields to every API response
- [ ] Add "Rules last verified: <date>" to `/health` response

### Hour 4: Tests
- [ ] Update `test_calculator.py` with Person 1's 10 golden test vectors
- [ ] Add `test_verifier.py` — test that ungrounded answers get caught
- [ ] Run full test suite — everything must pass
- [ ] Add test: `rules.json` values match `knowledge_base.py` claims (no drift)

**Delivers to team:** Fixed calculator, verifier module, hardened API, passing tests.

---

## Person 3 — FRONTEND + UX (The Designer)

> **Mission:** Make the UI trustworthy, polished, and demo-ready.

### Hour 1: Trust Indicators
- [ ] Add **"Rules last verified: 10 Oct 2026"** banner below header (fetch from `/api/rules-version`)
- [ ] Add confidence badge colors: `verified` = green, `reported` = yellow, `needs_verify` = red
- [ ] Add verifier status to Q&A response — show "✅ Answer verified against sources" or "⚠️ Showing raw sources (could not verify)"
- [ ] Add `rules_version` footer on every page

### Hour 2: Calculator UX Improvements
- [ ] Add "Simplified Estimate" label on calculator results
- [ ] Add EC escalation display — show Year 1/2/3 penalty rates (not just flat ₹5k)
- [ ] Add tooltip explanations on each category (what counts as Cat I vs II vs III)
- [ ] Improve mobile responsiveness (grid → stack on small screens)

### Hour 3: New Features
- [ ] Add **"Quick Compliance Check"** — user selects entity type → show which rules apply to them
- [ ] Add export to CSV button for calculator results (in addition to print/PDF)
- [ ] Add keyboard shortcut: Enter to submit question
- [ ] Add loading skeleton animation (replace plain "Searching..." text)

### Hour 4: Polish & Print
- [ ] Test print/PDF export — ensure it renders cleanly with all new elements
- [ ] Add project logo/branding if available
- [ ] Cross-browser test (Chrome, Firefox, Safari)
- [ ] Record a 2-minute demo video / screenshots for README

**Delivers to team:** Polished, trustworthy UI with verification indicators and improved UX.

---

## Person 4 — AI / RAG ENGINEER (The Brain)

> **Mission:** Better retrieval, better prompts, eval set. Make the AI actually reliable.

### Hour 1: Prompt Engineering
- [ ] Upgrade `SYSTEM_PROMPT` in `chain.py`:
  - Add rule: "State the fiscal year for every target you quote"
  - Add rule: "If chunks show different values for different FYs, do not average — list each"
  - Add rule: "Prefix your answer with the applicable FY and entity type"
  - Add: "If the question is about deadlines, always state the source notice date"
- [ ] Add a **structured output format** — answer starts with `FY:`, `Applies to:`, then the response
- [ ] Test with all 5 sample queries — verify citations are correct

### Hour 2: Retrieval Improvements
- [ ] Increase default `k` from 4 to 6 (more chunks = fewer misses with 22 chunks)
- [ ] Add **keyword boosting** — if question contains "deadline" or "filing", boost kb011; if "penalty" or "EC", boost kb013/kb014
- [ ] Add query preprocessing — expand abbreviations ("EC" → "Environmental Compensation", "MLP" → "Multi-Layered Plastic")
- [ ] Test retrieval on 20+ diverse questions — log which chunks are retrieved

### Hour 3: Build Golden Eval Set
- [ ] Create `tests/golden_eval.json` — 50 items:

```json
[
  {
    "question": "What is the recycling target for Cat I rigid plastics in FY 2026-27?",
    "expected_answer_contains": ["70%", "Category I"],
    "expected_chunks": ["kb007"],
    "type": "factual"
  },
  {
    "question": "What is the EPR target for electric vehicles?",
    "expected_answer_contains": ["not covered", "insufficient"],
    "expected_chunks": [],
    "type": "abstention"
  }
]
```

- [ ] Include: 20 factual, 10 paraphrase, 10 abstention (out of scope), 10 adversarial
- [ ] Write `tests/test_eval.py` — runs each question, checks expected chunks retrieved, checks answer contains/doesn't contain expected strings

### Hour 4: Multi-Provider Testing
- [ ] Test with Groq (free) — verify citations in answers
- [ ] Test with OpenRouter (free) — verify citations in answers
- [ ] Test mock mode — verify raw chunks are useful
- [ ] Compare answer quality across providers — document which gives best cited answers
- [ ] Write findings in `eval_results.md`

**Delivers to team:** Better prompts, smarter retrieval, 50-item eval set, provider comparison.

---

## Timeline (Clock View)

```
Hour    Person 1 (Data)    Person 2 (Backend)   Person 3 (Frontend)   Person 4 (AI/RAG)
─────   ──────────────     ─────────────────     ──────────────────    ────────────────
  1     Research &         Fix calculator        Trust indicators      Prompt engineering
        verify numbers     values                in UI                 improvements

  2     Create             Build numeric         Calculator UX         Retrieval
        rules.json         verifier              improvements          improvements

  3     Update KB          API hardening         New features          Build golden
        chunks             + rate limiting       (quick check, CSV)    eval set (50 Qs)

  4     Sync with P2       Tests (golden         Polish + print        Multi-provider
        Review P4 evals    vectors + verifier)   + demo recording      testing + eval

  5     ─── ALL TOGETHER: Integration test → fix breaks → final demo run ───
```

---

## Integration Points (Who Depends on Whom)

```
Person 1 ──(corrected values)──→ Person 2 (calculator)
Person 1 ──(updated KB)────────→ Person 4 (retrieval testing)
Person 1 ──(golden vectors)────→ Person 2 (tests)
Person 2 ──(verifier API)──────→ Person 3 (show verification status)
Person 2 ──(rules-version API)─→ Person 3 (display in UI)
Person 4 ──(eval questions)────→ Person 1 (factual review)
```

**Critical path:** Person 1 must deliver corrected values by end of Hour 2 → Person 2 is blocked until then on calculator fixes. Person 2 can build verifier independently in parallel.

---

## End-of-Sprint Checklist

- [ ] All 5 known wrong values fixed and verified
- [ ] `rules.json` exists with provenance
- [ ] Calculator matches `rules.json` values
- [ ] Numeric verifier catches ungrounded answers
- [ ] Rate limiting on `/api/ask`
- [ ] "Rules last verified" banner visible in UI
- [ ] Confidence badges color-coded
- [ ] 50-item golden eval set exists
- [ ] All tests pass
- [ ] Demo runs cleanly: ask 3 questions, run calculator, show print export

---

## What to Use for LLM / AI Work

| Task | Recommended Tool |
|------|-----------------|
| Person 1: Gazette research | Use Claude/GPT to help parse Gazette PDFs, but **verify every number yourself** |
| Person 4: Eval set generation | Use an LLM to generate question variants, but **manually verify expected answers** |
| Person 4: Prompt tuning | Test in the live app with Groq (free, fast) — iterate on system prompt |
| Person 2: Verifier regex | Write yourself — this is pure pattern matching, not AI |
| Person 3: CSS/HTML | Use LLM for code generation — straightforward |

---

## After the Sprint (Next Session)

With this sprint done, you'll have:
- ✅ Correct data (no more silent wrong answers)
- ✅ Verification layer (catches hallucinations)
- ✅ Eval framework (measures quality)
- ✅ Polished UI (looks trustworthy)

**Next sprint (another 3-5 hrs):** AWS deployment (Phase 2 from roadmap) — Bedrock + Lambda + budget caps.
