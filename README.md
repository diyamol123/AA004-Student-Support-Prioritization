# AA004 — Student Support Case Prioritization

**RealRails Agentic AI Batch 2 | Phase 2.1 — LangGraph Linear Orchestration**

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

The five agents are orchestrated through a compiled LangGraph linear StateGraph.

## 4. Phase 2.1 — LangGraph Linear Orchestration

The original sequential workflow orchestration has been migrated to LangGraph while preserving the existing deterministic business rules, agent responsibilities, decision logic, and recommendation behavior.

### Seven-node execution sequence

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
6. Explanation Node
  |
  v
7. Audit Node
  |
  v
END
```

### Phase 2.1 implementation

- Replaced sequential orchestration with a compiled LangGraph StateGraph.
- Mapped the existing run-scoped WorkflowContext into shared graph state.
- Reused all five existing deterministic agents.
- Preserved the existing decision logic and recommendation outcomes.
- Added seven-node execution tracing.
- Integrated node trace information into workflow results and audit records.
- Displayed actual graph execution progress in the frontend dashboard.
- Preserved existing API endpoints and frontend functionality.

**Scope:** Linear orchestration only. No conditional routing, LLM, RAG, vector database, or MCP was introduced in Phase 2.1.

## 5. Recommendation Types

The workflow supports four recommendations:

| Recommendation | Meaning |
|---|---|
| NORMAL_FOLLOWUP | Routine support follow-up |
| PRIORITY_OUTREACH | Priority academic-support outreach |
| TUTOR_REVIEW | Human tutor or coordinator review |
| REQUEST_MORE_INFO | Additional information is required |

The system calculates a priority score and provides reasons, triggered rules, and evidence for its recommendation.

## 6. Technology Stack

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
- LangGraph linear StateGraph
- Shared workflow context
- Rule-based prioritization
- Node execution tracing
- Audit logging

## 7. Project Structure

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
│   ├── Phase-1.4/
│   └── Phase-2.1/
│       ├── README.md
│       ├── repomix-output.xml
│       └── screenshots/
├── frontend/
│   ├── src/
│   └── package.json
├── .gitignore
└── README.md
```

## 8. Setup and Execution

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

## 9. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Backend health check |
| POST | `/api/workflows/run` | Execute prioritization workflow |
| GET | `/api/audit/{audit_reference}` | Retrieve workflow audit record |

## 10. Phase 2.1 Validation Results

Latest local validation:

- Backend tests: **46 passed**
- Frontend production build: passed
- Frontend ESLint: passed
- Four Product Bible scenarios: tested successfully
- LangGraph graph compilation and seven-node execution: verified
- Expected node execution order: verified
- Workflow state and node trace: verified
- Recommendation and deterministic decision behavior: preserved
- Explanation and audit integration: verified
- API workflow and audit integration: verified

## 11. Submission Evidence

Phase 2.1 evidence is available in `evidence/Phase-2.1/`:

- `README.md` — Component mapping, execution order, changes, and validation.
- `01-working-dashboard.png` — Working application.
- `02-langgraph-execution.png` — Seven-node execution trace.
- `03-workflow-state.png` — Workflow state.
- `04-explanation-audit.png` — Explanation and audit results.
- `repomix-output.xml` — Latest regenerated project snapshot.

## 12. MVP Scope and Limitations

This MVP is designed for academic-support prioritization only.

- It does not make grading, disciplinary, admission, or academic penalty decisions.
- It does not use protected or sensitive personal characteristics for prioritization.
- Scoring thresholds are initial MVP assumptions and should be reviewed and approved by the institution before operational use.
- Recommendations support human academic-support staff and do not replace their judgment.
- Audit records are currently held in backend memory and are not retained after a backend restart.

## 13. Future Improvements

Potential future enhancements include:

- Deterministic conditional workflow routing.
- Configurable institutional prioritization thresholds.
- Expanded audit and reporting capabilities.
- Integration with approved student-support systems.
- Further workflow orchestration capabilities.

## 14. Project Information

**Case ID:** AA004  
**Product:** Student Support Case Prioritization  
**Domain:** Education Operations  
**Current implementation:** Phase 2.1 — LangGraph Linear Orchestration

### Existing Phase 1.4 Deployment

The following deployment remains the Phase 1.4 cloud version. Phase 2.1 has been committed and pushed to GitHub but has not been deployed.

- Frontend: https://aa-004-student-support-prioritizati.vercel.app/
- Backend health: https://aa004-student-support-prioritization.onrender.com/health

The Render free instance may take time to wake after inactivity.

---

**Current Status:** Phase 2.1 implementation and local validation completed. Awaiting reviewer acceptance.