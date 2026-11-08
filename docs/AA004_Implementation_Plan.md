# AA004 — Implementation Plan
## Student Support Case Prioritization
## Phase 1.2 — Workflow Visualization & Evidence

## 1. Source of Truth

1. Current RealRails Phase 1.1 GitHub post
2. AA004 Product Bible
3. RealRails generic feeder guides 01–04
4. Latest repository implementation / Repomix
5. ABIP as an architecture-learning reference only

The Product Bible controls domain responsibilities, business inputs,
outputs, rules, boundaries and acceptance criteria.

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

Data:
- Seeded JSON/Python data
- In-memory workflow audit for the MVP

## 3. Workflow Architecture

Business Input
    ↓
Input Validation / Adapter
    ↓
Context Builder
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

Agents execute sequentially in the Phase 1.2 workflow.

## 4. Required Agents

### Case Intake Agent
Input: student_case
Output: validated_case
Responsibility: validate and normalize the submitted support case.

### Attendance Agent
Input: validated_case and attendance evidence
Output: attendance_flag and score
Responsibility: evaluate attendance against configured thresholds.

### Engagement Agent
Input: validated_case and engagement evidence
Output: engagement_flag and score
Responsibility: evaluate participation and inactivity indicators.

### Support Load Agent
Input: validated_case, submission evidence and ticket evidence
Output: support_load_flag and score
Responsibility: evaluate missed submissions and unresolved support requests.

### Student Support Decision Agent
Input: all preceding agent outputs
Output: final_recommendation
Responsibility: combine approved academic-support evidence and apply
deterministic decision rules.

Each agent must return structured output and traceable evidence.

## 5. Run-Scoped Shared Workflow Context

The workflow context must contain at least:

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

## 6. Decision Configuration

The Product Bible requires configured thresholds and a fixed support-priority
score but does not prescribe numeric values.

Therefore, numeric defaults will be documented as configurable demonstration
assumptions, not official institutional policy.

Proposed initial configuration:

Attendance:
- Below 75%: high concern, 30 points
- 75% to below 85%: moderate concern, 15 points
- 85% or above: no attendance concern, 0 points

Missed submissions:
- Two or more: high concern, 30 points
- One: moderate concern, 15 points
- Zero: no submission concern, 0 points

Engagement:
- Inactive for 14 or more days: high concern, 20 points
- Inactive for 7–13 days: moderate concern, 10 points
- More recent activity: no inactivity concern, 0 points

Unresolved support tickets:
- Two or more: high concern, 20 points
- One: moderate concern, 10 points
- Zero: no ticket-load concern, 0 points

Maximum configured score: 100.

These values are editable configuration, not hard-coded policy claims.
They must be identified as demo assumptions in the application.

## 7. Decision Precedence

Apply decision conditions in this order:

1. Missing essential evidence:
   REQUEST_MORE_INFO.

2. Conflicting or inconsistent evidence:
   TUTOR_REVIEW.

3. High combination of low attendance and multiple missed submissions:
   PRIORITY_OUTREACH.

4. Configured high-priority score band:
   PRIORITY_OUTREACH.

5. Multiple support concerns requiring human assessment:
   TUTOR_REVIEW.

6. No major support concerns or only a single mild concern:
   NORMAL_FOLLOWUP.

All score bands and configurable conditions must be explicit,
deterministic and covered by tests.

## 8. Explanation and Evidence

Generate explanation from actual workflow execution.

Show:
- agents executed and execution order
- agent responsibilities and conclusions
- evidence used by each agent
- configured thresholds and triggered rules
- score calculation
- reason for the final recommendation
- missing data and limitations

Do not invent evidence or claim an agent executed when it did not.

## 9. Audit

Record:
- workflow_id
- input reference
- execution timestamp
- agent execution sequence
- major agent outputs
- triggered decision rules
- final recommendation
- errors or fallback state

An in-memory audit store is sufficient for this MVP.

## 10. Seeded Scenarios

1. Normal progress:
   Expected action: NORMAL_FOLLOWUP.

2. Low attendance and missed submissions:
   Expected action: PRIORITY_OUTREACH.

3. Attendance unavailable:
   Expected action: REQUEST_MORE_INFO.

All scenarios must be reproducible and testable.

## 11. Frontend Requirements

The React interface must display:
- student support case summary
- attendance, engagement and support indicators
- priority score
- actual agent execution trace
- agent inputs and outputs
- final recommended action
- explanation and decision evidence
- audit reference

The interface must not simulate agent activity.

## 12. MVP Boundaries

Do not implement:
- grading or academic penalties
- admissions decisions
- behavioral profiling
- sensitive personal characteristics
- external production integrations
- LangGraph
- LLMs
- RAG or vector databases
- MCP
- long-term agent memory
- Kubernetes

Conditional routing and controlled LLM enhancements belong to later phases.

## 13. Validation Checklist

- [ ] Backend and frontend start successfully.
- [ ] Health endpoint works.
- [ ] Student support input is validated.
- [ ] All five agents execute.
- [ ] Shared workflow context is populated.
- [ ] Configured rules affect the result.
- [ ] Recommendation is structured.
- [ ] Explanation uses actual evidence.
- [ ] Audit reference is available.
- [ ] All three seeded scenarios pass.
- [ ] Frontend displays the real workflow.
- [ ] Latest Repomix is generated after MVP validation.
