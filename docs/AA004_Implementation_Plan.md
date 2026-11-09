# AA004 — Implementation Plan
## Student Support Case Prioritization
## Phase 1.4 — Cloud Deployment, Workflow Evidence & Regression Validation

## 1. Source of Truth

1. AA004 Product Bible
2. Current repository implementation and tests
3. RealRails generic feeder guides
4. Latest Phase 1.4 evidence
5. ABIP as an architecture-learning reference only

The Product Bible controls domain responsibilities, business inputs, outputs, rules, boundaries and acceptance criteria. The implementation and tests establish the currently delivered behaviour.

## 2. Technology

Backend:
- Python 3.11+
- FastAPI
- Pydantic
- Uvicorn
- pytest

Frontend:
- React
- Vite
- TypeScript
- CSS

Workflow:
- Five deterministic agents
- Sequential execution
- Run-scoped shared workflow context
- Rule-based prioritization
- In-memory audit records

Deployment:
- Render backend
- Vercel frontend
- Frontend API proxy to the deployed backend

## 3. Workflow Architecture

Business Input
    ↓
Input Validation / Adapter
    ↓
Run-Scoped Shared Workflow Context
    ↓
Case Intake Agent
    ↓
Attendance Agent
    ↓
Engagement Agent
    ↓
Support Load Agent
    ↓
Student Support Decision Agent
    ↓
Deterministic Recommendation
    ↓
Explanation and Evidence
    ↓
Audit Trail
    ↓
Business UI

The five agents execute sequentially within the same workflow run.

## 4. Required Agents

1. Case Intake Agent — validates and normalizes the submitted case.
2. Attendance Agent — evaluates attendance indicators.
3. Engagement Agent — evaluates engagement status and inactivity.
4. Support Load Agent — evaluates missed submissions and unresolved support tickets.
5. Student Support Decision Agent — combines upstream outputs and applies deterministic decision rules.

Each agent returns structured output and traceable evidence.

## 5. Run-Scoped Shared Workflow Context

The context includes:
- workflow_id
- student_case
- validated_case
- attendance_flag
- engagement_flag
- support_load_flag
- scores
- agent_outputs
- final_recommendation
- explanation
- audit_reference
- errors

The context belongs to one workflow execution. It is not long-term memory.

## 6. Input Fields

The case input supports:
- case_id
- attendance_rate
- missed_submissions
- engagement_status
- days_since_last_activity
- unresolved_support_tickets
- recent_activity_indicators

Numeric fields remain numeric in the submitted JSON. Empty optional numeric fields are submitted as null.

Recent activity indicators are optional strings. The intake agent normalizes whitespace and removes case-insensitive duplicates. The indicators are included in the validated case as evidence; the current Engagement Agent does not use them to change scores or recommendations.

## 7. Implemented Decision Precedence

The current deterministic decision agent applies these conditions in order:

1. If a specialist agent cannot complete because essential evidence is missing, return REQUEST_MORE_INFO using RULE-01-INCOMPLETE-EVIDENCE.
2. If supplied evidence is inconsistent, return TUTOR_REVIEW using RULE-02-INCONSISTENT-EVIDENCE.
3. If attendance is below 75% and missed submissions are at least two, return PRIORITY_OUTREACH using RULE-03-LOW-ATTENDANCE-AND-MISSED-WORK.
4. If multiple concerns or any high concern remain, return TUTOR_REVIEW using RULE-04-MULTIPLE-OR-HIGH-CONCERNS.
5. Otherwise, return NORMAL_FOLLOWUP using RULE-05-NORMAL-FOLLOWUP.

A high priority score by itself does not trigger PRIORITY_OUTREACH. The specific decision conditions above control the recommendation.

## 8. Demonstration Thresholds

Attendance:
- Below 75%: high concern, 30 points
- 75% to below 85%: moderate concern, 15 points
- 85% or above: no attendance concern

Missed submissions:
- Two or more: high concern, 30 points
- One: moderate concern, 15 points
- Zero: no submission concern

Engagement:
- 14 or more days since activity: high concern, 20 points
- 7–13 days: moderate concern, 10 points
- Fewer than 7 days: no inactivity concern

Unresolved support tickets:
- Two or more: high concern, 20 points
- One: moderate concern, 10 points
- Zero: no ticket-load concern

These are MVP demonstration thresholds, not official institutional policy.

## 9. Seeded Regression Scenarios

| Scenario | Expected action | Expected rule |
|---|---|---|
| Normal progress | NORMAL_FOLLOWUP | RULE-05-NORMAL-FOLLOWUP |
| Priority outreach | PRIORITY_OUTREACH | RULE-03-LOW-ATTENDANCE-AND-MISSED-WORK |
| Conflicting evidence | TUTOR_REVIEW | RULE-02-INCONSISTENT-EVIDENCE |
| Incomplete information | REQUEST_MORE_INFO | RULE-01-INCOMPLETE-EVIDENCE |

Each scenario should be executed through the deployed frontend and checked against the returned workflow context, five agent outputs, scores, flags, explanation, recommendation and audit reference.

## 10. Frontend Requirements

The interface displays:
- student support case input
- numeric attendance and support indicators
- optional recent activity indicators
- four demo scenarios
- priority score and recommendation
- actual agent execution trace
- shared workflow context
- decision explanation and triggered rules
- audit reference and retrieved audit record

Sidebar navigation links to Case Prioritization, Agent Workflow and Audit Evidence. Navigation remains visible on mobile.

The interface must not simulate agent activity.

## 11. Audit

Audit records include:
- workflow_id
- input reference
- execution timestamp
- agent execution sequence
- agent outputs
- triggered rules
- final recommendation
- errors

The MVP audit store is in memory. Records are not retained after a backend process restart or replacement.

## 12. MVP Boundaries

Do not implement:
- grading or academic penalties
- admissions decisions
- behavioral profiling
- sensitive personal characteristics
- LangGraph
- LLMs
- RAG or vector databases
- MCP
- long-term agent memory
- Kubernetes

These are outside the current Phase 1.4 scope.

## 13. Validation Checklist

- [ ] Backend health endpoint responds.
- [ ] Frontend reaches the deployed backend through its API proxy.
- [ ] Numeric inputs are submitted as numbers or null.
- [ ] Recent activity indicators are submitted as a string array.
- [ ] All five agents execute in sequence.
- [ ] Shared workflow context is populated.
- [ ] Normal progress returns NORMAL_FOLLOWUP.
- [ ] Priority outreach returns PRIORITY_OUTREACH.
- [ ] Conflicting evidence returns TUTOR_REVIEW.
- [ ] Incomplete information returns REQUEST_MORE_INFO.
- [ ] Explanations and evidence match actual execution.
- [ ] Audit records can be retrieved during the same backend process.
- [ ] Sidebar navigation works on desktop and mobile.
- [ ] Backend tests pass.
- [ ] Frontend build and lint pass.
- [ ] Latest Repomix and Phase 1.4 screenshots are captured.
