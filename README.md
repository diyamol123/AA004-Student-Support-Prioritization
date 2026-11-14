# AA004 — Student Support Case Prioritization

**RealRails Agentic AI Batch 2 | Phase 3.2 — Final Demo & Portfolio Package**

## 1. Project Overview

Student Support Case Prioritization is a deterministic, multi-agent workflow designed to help academic support teams prioritize student support cases for timely outreach.

The system evaluates approved academic-support indicators, including:

- Attendance rate
- Missed submissions
- Student engagement status
- Days since last activity
- Unresolved support tickets
- Optional recent activity indicators

It generates an explainable recommendation, priority score, supporting evidence, and audit record.

**Primary objective:** Support transparent and consistent academic-support outreach decisions.

## 2. Business Problem

Academic support teams receive multiple student support requests and need a consistent way to identify cases that may require additional attention.

This MVP provides a structured prioritization workflow that helps coordinators identify cases for routine follow-up, priority outreach, tutor review, or additional information.

## 3. Agent Architecture

The application uses five specialized deterministic agents:

1. **Case Intake Agent** — validates and normalizes incoming case information.
2. **Attendance Agent** — evaluates attendance indicators.
3. **Engagement Agent** — evaluates engagement and recent activity.
4. **Support Load Agent** — evaluates missed submissions and unresolved support tickets.
5. **Student Support Decision Agent** — combines agent outputs and deterministic rules to generate the final recommendation.

The five agents are orchestrated through a compiled conditional LangGraph StateGraph with deterministic routing.

## 4. Phase 2.2 — LangGraph Conditional Routing

Phase 2.2 extends the Phase 2.1 sequential LangGraph workflow by introducing deterministic conditional routing after the Student Support Decision Agent. Existing agents, decision logic, and recommendation behavior remain unchanged.

### Eight-step conditional execution sequence

```text
START
  |
  v
1. Case Intake Agent
  |
  v
2. Attendance Agent
  |
  v
3. Engagement Agent
  |
  v
4. Support Load Agent
  |
  v
5. Student Support Decision Agent
  |
  v
6. Selected Route Node
   (LOW_RISK / HIGH_SUPPORT_NEED / INCOMPLETE /
    CONFLICTING / TUTOR_REVIEW)
  |
  v
7. Explanation Node
  |
  v
8. Audit Node
  |
  v
END
```

### Phase 2.2 implementation

- Replaced sequential orchestration with a compiled conditional LangGraph StateGraph.
- Mapped the existing run-scoped WorkflowContext into shared graph state.
- Reused all five existing deterministic agents.
- Preserved the existing decision logic and recommendation outcomes.
- Added eight-step conditional execution tracing.
- Integrated node trace information into workflow results and audit records.
- Displayed actual graph execution progress in the frontend dashboard.
- Preserved existing API endpoints and frontend functionality.

**Scope:** Deterministic conditional routing only. No LLM, RAG, vector database, or MCP was introduced in Phase 2.2.

### Route-to-recommendation mapping

| Conditional route | Recommendation |
|---|---|
| `LOW_RISK` | `NORMAL_FOLLOWUP` |
| `HIGH_SUPPORT_NEED` | `PRIORITY_OUTREACH` |
| `INCOMPLETE` | `REQUEST_MORE_INFO` |
| `CONFLICTING` | `TUTOR_REVIEW` |
| `TUTOR_REVIEW` | `TUTOR_REVIEW` |

All five routes converge on the shared Explanation Node and then the Audit Node. The selected route is included in execution tracing, explanation, and audit evidence.

## 5. Phase 2.3 — Controlled LLM Explanation

Phase 2.3 adds an optional Gemini explanation capability to the existing
conditional LangGraph workflow.

The deterministic workflow remains the sole authority for scoring,
prioritization, conditional routing, and recommendations. Gemini explains
the already-computed result using supplied workflow facts.

### LLM responsibilities and boundaries

- Gemini generates a human-readable explanation only.
- The deterministic decision agent remains authoritative.
- Gemini cannot modify priority scores, routes, or recommendations.
- The explanation service uses structured Pydantic output validation.
- The case ID and raw activity indicators are not sent to Gemini.
- Deterministic explanation fallback is used when Gemini is disabled,
  unavailable, times out, or returns invalid output.

### Conditional workflow routes

| Route | Recommendation |
|---|---|
| `LOW_RISK` | `NORMAL_FOLLOWUP` |
| `HIGH_SUPPORT_NEED` | `PRIORITY_OUTREACH` |
| `INCOMPLETE` | `REQUEST_MORE_INFO` |
| `CONFLICTING` | `TUTOR_REVIEW` |
| `TUTOR_REVIEW` | `TUTOR_REVIEW` |

The selected route is determined before the Explanation Node. All routes
continue through explanation and audit processing.

### Phase 2.3 verification

- Live Gemini execution completed successfully.
- Provider: Gemini.
- Model: `gemini-3.5-flash-lite`.
- Live response status: `SUCCESS`.
- Structured response validation: `VALID`.
- Simulated timeout and deterministic fallback tested.
- Backend test suite: **53 passed**.
- Frontend lint and production build results are documented in the
  Phase 2.3 evidence README.

The LLM is an optional explanation layer. The workflow remains capable of
producing deterministic explanations without a successful LLM response.

## 6. Phase 3.1 — Productized Business Experience

Phase 3.1 improves the application experience for academic support teams while preserving the existing Phase 2.3 agentic AI backend.

### Business-facing workspace

- Introduced Student Support Workspace as the primary user experience.
- Improved navigation and labels to use clear business terminology.
- Presented recommendations with priority scores, reasons, and supporting evidence.
- Added suggested next steps based on the existing recommendation.
- Made human review explicit before support actions are taken.
- Improved evidence labels and descriptions for easier understanding.
- Improved the interface for responsive, narrow-screen use.

### Technical review access

Explainability & Audit remains available through a separate advanced review area. It provides access to workflow execution, agent outputs, technical evidence, and audit details without making these internal details part of the normal business workflow.

### Preserved architecture

- Existing deterministic decision rules and recommendation logic remain unchanged.
- Existing five-agent LangGraph workflow and conditional routing are preserved.
- Gemini remains an explanation layer, not the decision authority.
- No new backend decision logic was introduced for this productization phase.

### Phase 3.1 evidence

- Application screenshots: `evidence/phase-3.1/screenshots/`
- Latest repository snapshot: `evidence/phase-3.1/repomix-output.xml`

---

## 7. Recommendation Types

The workflow supports four recommendations:

| Recommendation | Meaning |
|---|---|
| NORMAL_FOLLOWUP | Routine support follow-up |
| PRIORITY_OUTREACH | Priority academic-support outreach |
| TUTOR_REVIEW | Human tutor or coordinator review |
| REQUEST_MORE_INFO | Additional information is required |

The system calculates a priority score and provides reasons, triggered rules, and evidence for its recommendation.

## 8. Technology Stack

**Backend**
- Python 3.11+
- FastAPI
- Pydantic
- Pytest
- LangGraph

**Frontend**
- React
- TypeScript
- Vite
- CSS

**Workflow**
- Deterministic multi-agent execution
- Conditional LangGraph StateGraph
- Shared workflow context
- Rule-based prioritization
- Conditional node execution tracing
- Audit logging

## 9. Project Structure

```text
AA004-Student-Support-Prioritization/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── graphs/
│   │   │   └── student_support_graph.py
│   │   ├── models/
│   │   └── services/
│   ├── tests/
│   └── main.py
├── docs/
├── evidence/
│   ├── phase-2.2/
│   ├── phase-2.3/
│   │   ├── README.md
│   │   ├── repomix-output.xml
│   │   └── Screenshot files (9)
│   └── phase-3.1/
│       ├── repomix-output.xml
│       └── screenshots/
├── frontend/
│   ├── src/
│   └── package.json
├── .gitignore
└── README.md
```

## 10. Setup and Execution

### Backend

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python3 -m uvicorn backend.main:app --reload --port 8000
```

Backend health endpoint:

`http://127.0.0.1:8000/health`

### Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite development URL printed in the terminal, usually:

`http://localhost:5173`

### Production build and lint

```bash
cd frontend
npm run build
npm run lint
```

## 10. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Backend health check |
| POST | `/api/workflows/run` | Execute prioritization workflow |
| GET | `/api/audit/{audit_reference}` | Retrieve workflow audit record |

## 11. Phase 2.2 Validation Results

Latest local validation:

- Backend tests: **48 passed**
- Frontend production build: passed
- Frontend ESLint: passed
- Five conditional routing scenarios — normal, priority, incomplete, conflicting, and tutor review — tested successfully
- LangGraph graph compilation and eight-step conditional execution: verified
- Expected node execution order: verified
- Workflow state and node trace: verified
- Recommendation and deterministic decision behavior: preserved
- Explanation and audit integration: verified
- API workflow and audit integration: verified

## 12. Submission Evidence

Phase 2.2 evidence is available in `evidence/phase-2.2/`. Phase 2.3 evidence is available in `evidence/phase-2.3/`.

See `evidence/phase-2.2/README.md` for the Phase 2.2 evidence inventory.

See `evidence/phase-2.3/README.md` for the Phase 2.3 route explanation, screenshot inventory, validation results, and latest Repomix snapshot (`repomix-output.xml`).

## 13. MVP Scope and Limitations

This MVP is designed for academic-support prioritization only.

- It does not make grading, disciplinary, admission, or academic penalty decisions.
- It does not use protected or sensitive personal characteristics for prioritization.
- Scoring thresholds are initial MVP assumptions and should be reviewed and approved by the institution before operational use.
- Recommendations support human academic-support staff and do not replace their judgment.
- Audit records are currently held in backend memory and are not retained after a backend restart.

## 14. Future Improvements

Potential future enhancements include:

- Configurable institutional prioritization thresholds.
- Expanded audit and reporting capabilities.
- Integration with approved student-support systems.
- Further workflow orchestration capabilities.

## 15. Project Information

**Case ID:** AA004
**Product:** Student Support Case Prioritization
**Domain:** Education Operations
**Current implementation:** Phase 3.2 — Final Demo & Portfolio Package

### Cloud Deployment

The deployed application provides the Student Support Case Prioritization experience. Verify the live URLs before demonstration.

- Frontend — Vercel: https://aa-004-student-support-prioritizati.vercel.app/
- Backend health — Render: https://aa004-student-support-prioritization.onrender.com/health

The production deployment was verified with a successful Gemini explanation, valid structured output, and deterministic decision control.

The Render free instance may take time to wake after inactivity.

---

**Current Status:** Phase 3.2 — Final Demo & Portfolio Package. The productized application is complete, production frontend and backend health endpoints have been verified, and 16 organised Phase 3.2 screenshots are included in the repository.


## Phase 3.2 — Final Demo & Portfolio Package

### Demo scenarios

1. **Normal follow-up:** `DEMO-NORMAL-01` — expected `NORMAL_FOLLOWUP` via `LOW_RISK`.
2. **Incomplete evidence:** `DEMO-INCOMPLETE-01` — expected `REQUEST_MORE_INFO` via `INCOMPLETE`.
3. **Priority outreach and explanation:** `DEMO-PRIORITY-01` — expected `PRIORITY_OUTREACH` via `HIGH_SUPPORT_NEED`; Gemini explains the deterministic result without changing it.

A conflicting-evidence scenario is also available: `DEMO-CONFLICT-01` — expected `TUTOR_REVIEW` via `CONFLICTING`.

### Architecture evolution

The project evolved from deterministic multi-agent prioritization, to sequential LangGraph orchestration, conditional routing, controlled Gemini explanations with deterministic fallback, and a business-facing workspace. Phase 3.2 packages the existing implementation for demonstration and review; it does not introduce a new decision engine.

### Phase 3.2 screenshots

Sixteen Phase 3.2 screenshots are organised as follows: `main-application/` (4), `scenario-1/` (4), `scenario-2/` (4), and `scenario-3/` (4). The original raw captures are kept separately in `evidence/phase-3.2/raw-captures/` and are not part of the organised screenshot submission. Earlier-phase screenshots remain in their original folders.

### Demo limitations

This is an academic-support MVP. Recommendations require human review. Thresholds are demo assumptions, audit records are held in backend memory and are lost after restart, and no live institutional integration is claimed. Gemini is an optional explanation layer and does not control decisions.
