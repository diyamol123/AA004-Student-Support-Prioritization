# RealRails Batch 2 — Deterministic Agentic AI Architecture Guide
## Purpose

This is the standard Phase 1 engineering contract for all approved case studies.

The domain changes.
The architecture remains consistent.

---

## Standard Architecture

```text
Business Input
    ↓
Input Validation / Adapter
    ↓
Context Builder
    ↓
Run-Scoped Shared Workflow Context
    ↓
Specialized Domain Agents
    ↓
Deterministic Rules / Scoring / Matching
    ↓
Decision / Recommendation Agent
    ↓
Structured Recommendation
    ↓
Explanation + Evidence
    ↓
Audit Trail
    ↓
Business UI
```

---

## 1. Business Input

Use a structured request model.

Examples:

- appointment request
- vendor offer set
- ticket
- work order
- invoice
- project snapshot

Validate required fields before agent execution.

---

## 2. Context Builder

The Context Builder prepares the information required for one workflow run.

Responsibilities may include:

- normalize input
- load seeded/reference data
- derive safe calculated fields
- initialize workflow ID
- initialize agent-output container
- initialize errors/status

Do not put final business decision logic in the Context Builder.

---

## 3. Run-Scoped Shared Workflow Context

Recommended high-level shape:

```text
workflow_id
business_input
validated_input
shared_context
agent_outputs
final_recommendation
explanation
audit_reference
errors
```

Case-specific fields may live inside `shared_context` and `agent_outputs`.

This context exists for the current workflow run.

Do not call it long-term memory.

---

## 4. Specialized Domain Agents

Each agent must have:

- one clear responsibility
- defined input
- defined output
- limited decision boundary
- traceable execution

Avoid agents that merely rename data.

A useful agent should perform meaningful domain analysis, validation, scoring, matching, or classification.

---

## 5. Deterministic Rules

Rules should be:

- explicit
- repeatable
- testable
- explainable
- represented in code or configuration

Examples:

```text
IF required information missing
THEN REQUEST_MORE_INFO

IF risk_score >= configured threshold
THEN REVIEW

IF candidate violates hard constraint
THEN remove candidate
```

The same valid input + same rules should produce the same result.

---

## 6. Decision / Recommendation Agent

The Decision Agent:

- reads prior agent outputs
- applies final precedence/weighting
- produces one structured recommendation
- returns reasons/evidence

Recommended output pattern:

```json
{
  "status": "RECOMMENDED_ACTION",
  "score": 82,
  "reasons": ["..."],
  "evidence": ["..."],
  "review_required": false
}
```

The exact fields should fit the Product Bible.

---

## 7. Explanation

Explanation must be derived from actual execution evidence.

It may use deterministic templates in Phase 1.

It must not invent facts.

---

## 8. Audit

Minimum audit information:

```text
workflow_id
timestamp
input reference
agent execution order
major agent outputs
triggered rules
final recommendation
error/fallback status
```

An in-memory audit store is acceptable for Phase 1.

---

## 9. Default Technical Stack

Preferred common stack:

### Backend
- Python 3.11+
- FastAPI
- Pydantic
- pytest

### Frontend
- React
- Vite
- TypeScript

### Data
- seeded JSON/Python data for simple cases
- SQLite only when simple persistence materially helps the Product Bible

The objective is consistency and learning, not infrastructure complexity.

---

## 10. Required Boundary

Phase 1 does **not** require:

- LangGraph
- LLMs
- RAG
- vector DB
- MCP
- knowledge graph
- long-term memory
- Kubernetes
- production enterprise integration

Those are not signs of quality when the Product Bible does not require them.
