# AA004 — Student Support Case Prioritization

**RealRails Agentic AI Batch 2 | Phase 1.4 — Cloud Deployment, Workflow Evidence & Regression Validation**

## 1. Project Overview

Student Support Case Prioritization is a deterministic, multi-agent workflow designed to help academic support teams prioritize student support cases for timely outreach.

The system evaluates approved academic-support indicators, including:

- Attendance rate
- Missed submissions
- Student engagement status
- Days since last activity
- Unresolved support tickets
- Optional recent activity indicators (included as case evidence; not independently scored)

It generates an explainable recommendation, priority score, supporting evidence, and audit record.

**Primary objective:** Support transparent and consistent academic-support outreach decisions.

## 2. Business Problem

Academic support teams receive multiple student support requests and need a consistent way to identify cases that may require additional attention.

This MVP provides a structured prioritization workflow that helps coordinators identify cases for follow-up, priority outreach, tutor review, or additional information.

## 3. Agent Architecture

The application uses five specialized agents:

1. **Case Intake Agent** — validates and normalizes incoming case information.
2. **Attendance Agent** — evaluates attendance indicators.
3. **Engagement Agent** — evaluates engagement and recent activity.
4. **Support Load Agent** — evaluates missed submissions and unresolved support tickets.
5. **Student Support Decision Agent** — combines agent outputs and deterministic rules to generate the final recommendation.

Each agent has a defined responsibility and produces structured, traceable outputs.

## 4. Recommendation Types

The workflow supports four recommendations:

| Recommendation | Meaning |
|---|---|
| `NORMAL_FOLLOWUP` | Routine support follow-up |
| `PRIORITY_OUTREACH` | Priority academic-support outreach |
| `TUTOR_REVIEW` | Human tutor or coordinator review |
| `REQUEST_MORE_INFO` | Additional information is required |

The system calculates a priority score and provides reasons, triggered rules, and evidence for its recommendation.

## 5. Technology Stack

**Backend**
- Python 3.11+
- FastAPI
- Pydantic
- Pytest

**Frontend**
- React
- TypeScript
- Vite
- CSS

**Workflow**
- Deterministic agent execution
- Shared workflow context
- Rule-based prioritization
- Audit logging

## 6. Project Structure

```text
AA004-Student-Support-Prioritization/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── models/
│   │   └── services/
│   ├── tests/
│   └── main.py
├── docs/
│   ├── Product_Bible.md
│   ├── 01_Product_Bible_Execution_Guide.md
│   ├── 02_Deterministic_AgenticAI_Architecture_Guide.md
│   ├── 03_AI_Assisted_Build_and_Repomix_Guide.md
│   ├── 04_Workflow_Shared_Context_Explainability_Guide.md
│   └── AA004_Implementation_Plan.md
├── frontend/
│   ├── src/
│   └── package.json
├── .gitignore
└── README.md
```

## 7. Setup and Execution

### Backend

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python3 -m uvicorn backend.main:app --reload --port 8000
```

Backend health endpoint:

```text
http://127.0.0.1:8000/health
```

### Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite development URL printed in the terminal, usually:

```text
http://localhost:5173
```

### Production build

```bash
cd frontend
npm run build
npm run lint
```


## 8. Dockerized Local Deployment

The application can be built and run locally using Docker Compose.

### Prerequisites

- Docker Desktop installed and running
- Docker Compose V2

### Build the containers

Run from the project root:

    docker compose build

### Start the application

    docker compose up -d

### Access the application

- Frontend: http://localhost:8080
- Backend health: http://localhost:8000/health
- Frontend health proxy: http://localhost:8080/health
- API documentation: http://localhost:8000/docs

### Check container health

    docker compose ps

Both backend and frontend containers should report healthy status.

### View application logs

    docker compose logs

For individual services:

    docker compose logs backend
    docker compose logs frontend

### Stop the containers

    docker compose down

### Troubleshooting

- If a port is already in use, stop the conflicting application or configure BACKEND_PORT and FRONTEND_PORT.
- If the backend is not healthy, inspect it using docker compose logs backend.
- If the frontend cannot reach the backend, check BACKEND_URL and backend container health.
- Rebuild after changing application code or Docker configuration using docker compose up -d --build.

The audit service currently uses in-memory storage. Audit records are available while the backend process is running and are not persisted across backend restarts.

## 9. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Backend health check |
| POST | `/api/workflows/run` | Execute prioritization workflow |
| GET | `/api/audit/{audit_reference}` | Retrieve workflow audit record |

## 10. Validation Results

Latest local validation:

- Backend tests: **45 passed**
- Frontend TypeScript compilation: passed
- Vite production build: passed
- Frontend ESLint: passed
- Four demo scenarios tested successfully
- Five-agent workflow execution verified
- Audit record retrieval verified
- Backend Docker image built successfully
- Frontend Docker image built successfully
- Backend and frontend containers started successfully
- Both container health checks passed
- Nginx reverse proxy validated
- End-to-end workflow and audit retrieval validated through the Dockerized frontend
- Backend tests inside Docker: 45 passed
- Docker Compose configuration validation passed

## 11. MVP Scope and Limitations

This MVP is designed for academic-support prioritization only.

It does not make grading, disciplinary, admission, or academic penalty decisions.

It does not use protected or sensitive personal characteristics for prioritization.

The scoring thresholds are initial MVP assumptions and should be reviewed and approved by the institution before operational use.

Recommendations are intended to support human academic-support staff, not replace their judgment.

## 12. Future Improvements

Potential future enhancements include:

- Configurable institutional prioritization thresholds
- Expanded audit and reporting capabilities
- Integration with approved student-support systems
- Further workflow orchestration capabilities

---

**Case ID:** AA004
**Product:** Student Support Case Prioritization
**Domain:** Education Operations
**Phase:** 1.4 — Cloud Deployment, Workflow Evidence & Regression Validation


## Phase 1.4 Deployment

- Frontend: https://aa-004-student-support-prioritizati.vercel.app/
- Backend health: https://aa004-student-support-prioritization.onrender.com/health

The Render free instance may take time to wake after inactivity.
Audit records are held in backend memory and are not retained after a backend restart.
