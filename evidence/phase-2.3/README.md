# Phase 2.3 — Controlled LLM Explanation

## 1. Overview

Phase 2.3 adds an optional Gemini-powered explanation capability to the
existing deterministic student-support workflow.

The LLM explains an already-computed recommendation. It does not make
prioritization or routing decisions.

## 2. Decision authority and boundaries

- The five existing deterministic agents continue to evaluate the case.
- The deterministic decision agent remains the sole decision authority.
- Conditional routing selects the route before the Explanation Node runs.
- Gemini generates a concise explanation from supplied workflow facts.
- Gemini cannot set or change scores, priorities, routes, or recommendations.
- The case ID and raw activity indicators are not sent to Gemini.
- Structured LLM output is validated using a Pydantic schema.

## 3. Conditional route explanation

| Route | Condition / purpose | Recommendation |
|---|---|---|
| `LOW_RISK` | No major support concerns identified | `NORMAL_FOLLOWUP` |
| `HIGH_SUPPORT_NEED` | Significant support concerns identified | `PRIORITY_OUTREACH` |
| `INCOMPLETE` | Essential information is missing | `REQUEST_MORE_INFO` |
| `CONFLICTING` | Evidence requires human review | `TUTOR_REVIEW` |
| `TUTOR_REVIEW` | Tutor or coordinator review is required | `TUTOR_REVIEW` |

All selected routes proceed through the shared Explanation Node and then
the Audit Node. The route is selected deterministically before Gemini runs.

## 4. Graph execution sequence

1. Case Intake Agent
2. Attendance Agent
3. Engagement Agent
4. Support Load Agent
5. Student Support Decision Agent
6. Selected conditional route
7. Explanation Node — Gemini with deterministic fallback
8. Audit Node

## 5. LLM validation and fallback

The Gemini service supports:

- Structured JSON output validation.
- Configurable provider, model, and timeout.
- Missing-key and unsupported-provider handling.
- Timeout, provider-error, and invalid-output fallback.
- Deterministic explanation when the LLM is disabled or unavailable.

LLM trace metadata records provider, model, status, whether the LLM was
used, whether fallback was used, validation status, and error category.

## 6. Verification results

### Live Gemini execution

- Provider: Gemini.
- Model: `gemini-3.5-flash-lite`.
- Status: `SUCCESS`.
- Validation: `VALID`.
- LLM used: `true`.
- Fallback used: `false`.
- Deterministic recommendation: `NORMAL_FOLLOWUP`.
- Priority score: `0`.
- Route: `LOW_RISK`.
- Audit record successfully retrieved with Gemini metadata.

### Timeout fallback

A simulated provider timeout was tested through the workflow.

- Status: `TIMEOUT`.
- LLM used: `false`.
- Fallback used: `true`.
- Deterministic recommendation remained unchanged.
- Audit record contained timeout and fallback metadata.
- Graph completed through the Audit Node.

### Automated validation

- Backend test suite: **53 passed**.
- Frontend ESLint: passed.
- TypeScript compilation: passed.
- Vite production build: passed.
- `git diff --check`: passed at the final evidence check.

## 7. Evidence inventory

The following six screenshots are included:

- `01-phase-2.3.png`
- `02-phase-2.3.png`
- `03-phase-2.3.png`
- `04-phase-2.3.png`
- `05-phase-2.3.png`
- `06-phase-2.3.png`

### Normal-path execution — LOW_RISK

- `01-phase-2.3.png` — Normal follow-up recommendation, priority score 0.
- `02-phase-2.3.png` — Eight-step LangGraph execution trace with `LOW_RISK`.
- `03-phase-2.3.png` — Gemini success and audit record.

### Conditional / alternate-path execution — HIGH_SUPPORT_NEED

- `04-phase-2.3.png` — Priority outreach recommendation, priority score 100.
- `05-phase-2.3.png` — Eight-step LangGraph execution trace with
  `HIGH_SUPPORT_NEED`.
- `06-phase-2.3.png` — Gemini success and audit record.

The latest project snapshot is:

- `repomix-output.xml`

## 8. Security and limitations

- `.env` contains local credentials and must remain untracked.
- `.env.example` contains placeholders only.
- API keys must not be committed or included in evidence snapshots.
- Automated tests do not require a live Gemini API call.
- The audit store is currently in-memory and is not durable across
  backend process restarts.
- The LLM is optional; deterministic explanations remain available
  when it is disabled or unavailable.

## 9. Submission checklist

- [ ] Attach a screenshot showing normal-path execution.
- [ ] Attach a screenshot showing conditional/alternate-path execution.
- [ ] Include the route table or the short route explanation above.
- [ ] Include the latest `repomix-output.xml`.
