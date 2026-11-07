# AA004 — Student Support Case Prioritization
## RealRails Agentic AI Batch 2 — Product Bible

> **Role of this file:** This Product Bible is the domain source of truth for this case study.
> **Architecture rule:** Implement this case using the standard RealRails deterministic Agentic AI architecture.
> **Phase rule:** Do not introduce LangGraph or LLM features before the relevant later phase.

| Field | Value |
|---|---|
| Case ID | `AA004` |
| Domain | Education Operations |
| Complexity | Easy |
| Core Pattern | Business Input → Context → Domain Agents → Deterministic Rules → Decision → Explanation → Audit |

---

## 1. Product / Case Name

**Student Support Case Prioritization**

## 2. Business Problem

Academic support teams often receive many student support requests and need a transparent way to prioritize follow-up based on attendance, missed submissions, engagement, and open support issues.

## 3. Primary Users / Actors

- Student support coordinator
- Academic operations lead
- Tutor coordinator

## 4. MVP Objective

Prioritize academic-support cases for outreach without making grading, disciplinary, or admission decisions.

## 5. Business Input

Student support case with attendance rate, missed submissions, engagement status, unresolved support tickets, and recent activity indicators.

## 6. Expected Final Output / Recommendation

Recommended action: NORMAL_FOLLOWUP / PRIORITY_OUTREACH / TUTOR_REVIEW / REQUEST_MORE_INFO, with priority score and reasons.

## 7. Domain Data Required

- Seeded attendance summary
- Submission status
- Engagement indicators
- Open support cases
- Configured priority rules

Use seeded/sample data for the internship MVP unless the current GitHub post explicitly allows an external integration.

## 8. Agent Definitions

The case should use the following agent responsibilities. Agent names may be adapted slightly in code, but their business responsibility must remain clear.

| Agent | Responsibility | Main Input | Main Output |
|---|---|---|---|
| Case Intake Agent | Validates and normalizes the support case. | `student_case` | `validated_case` |
| Attendance Agent | Evaluates attendance against configured support thresholds. | `validated_case + attendance` | `attendance_flag, score` |
| Engagement Agent | Evaluates recent participation and inactivity signals. | `validated_case + engagement` | `engagement_flag, score` |
| Support Load Agent | Evaluates missed work and unresolved support requests. | `validated_case + submissions + tickets` | `support_load_flag, score` |
| Student Support Decision Agent | Combines non-sensitive academic support evidence into an outreach priority. | `all agent outputs` | `final_recommendation` |

## 9. Agent Responsibilities

Each specialized agent must:

- perform one clear business responsibility
- consume structured input from the current workflow context
- produce a structured output
- avoid making decisions outside its boundary
- expose enough evidence for later explanation and audit

The **Decision Agent** combines prior agent outputs into the final structured recommendation.

## 10. Agent Inputs and Outputs

Use explicit structured models for:

- original business input
- validated/normalized input
- each agent output
- decision result
- explanation/evidence
- audit reference

Do not pass unstructured blobs between agents when a small structured contract is practical.

## 11. Run-Scoped Shared Workflow Context

The workflow context should contain at least:

- `workflow_id`
- `student_case`
- `validated_case`
- `attendance_flag`
- `engagement_flag`
- `support_load_flag`
- `scores`
- `agent_outputs`
- `final_recommendation`
- `explanation`
- `audit_reference`
- `errors`

This is **run-scoped shared workflow context**, not long-term AI memory.

## 12. Deterministic Rules / Validation / Scoring

1. Use only approved support indicators; do not infer protected or personal characteristics.
2. High combination of missed submissions + low attendance → PRIORITY_OUTREACH.
3. Single mild flag → NORMAL_FOLLOWUP.
4. Conflicting or incomplete evidence → TUTOR_REVIEW or REQUEST_MORE_INFO.
5. No automated grading, disciplinary, or admission outcome.

The same valid input and the same configured rules should produce the same result.

## 13. Decision / Recommendation Logic

Calculate a fixed support-priority score from approved indicators, then map it to a support action band.

The final response should contain:

- `status` / recommended action
- score or priority where relevant
- short reasons
- triggered rules / evidence
- agent output references where useful
- audit reference

## 14. Execution Flow

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
Deterministic Rules / Scoring
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

The implementation may run agents sequentially in Phase 1. Later phases will evolve orchestration using LangGraph.

## 15. Explanation and Evidence Requirements

The application must make it possible to understand:

- which agents executed
- what each agent concluded
- which rules or thresholds triggered
- why the final recommendation was selected
- what important limitations or missing data affected the result

The explanation must not invent evidence that is not present in the workflow state.

## 16. Audit Requirements

Record at minimum:

- `workflow_id`
- request/input reference
- execution timestamp
- agent execution sequence
- major agent outputs
- triggered decision rules
- final recommendation
- errors or fallback state

An in-memory audit store is acceptable for the internship MVP unless a later phase explicitly requires persistence.

## 17. Sample Scenarios

| Scenario | Input / Condition | Expected Behaviour |
|---|---|---|
| Normal progress | No major support flags | NORMAL_FOLLOWUP |
| Multiple support flags | Low attendance + missed work | PRIORITY_OUTREACH |
| Incomplete data | Attendance unavailable | REQUEST_MORE_INFO |

These scenarios should be implemented as seeded/demo data or reproducible test inputs.

## 18. Expected MVP UI

The basic Phase 1 UI should make the business workflow usable and explainable.

- Case summary
- Indicator cards
- Agent trace
- Priority score
- Recommended next action
- Audit evidence

Keep the UI functional and clear. Heavy product polish belongs to optional Phase 3.

## 19. MVP Boundaries / Non-Goals

- No grading or academic penalty decisions
- No admissions decisions
- No behavioral profiling
- No use of sensitive personal attributes

Also:

- no production credentials
- no hidden external dependencies
- no unsupported claims of production readiness
- no future-phase technology added early

## 20. Future Conditional-Routing Opportunity

LOW_RISK → normal follow-up; HIGH_SUPPORT_NEED → priority outreach; INCOMPLETE → request information; CONFLICTING → tutor review.

This should be used later in **Phase 2.2 — LangGraph Conditional Routing**.

## 21. Future Controlled LLM Opportunity

Optional summarization of support notes into non-sensitive structured categories or explanation generation, with deterministic scoring unchanged.

The LLM is an enhancement layer. It must not replace deterministic authority where deterministic rules already provide the business decision.

## 22. Acceptance Criteria

The case is ready for core internship progression when:

- [ ] The supplied business input can be submitted through the application.
- [ ] Input is validated and normalized.
- [ ] 3–5 meaningful agent responsibilities are implemented.
- [ ] Agents use structured inputs and outputs.
- [ ] Run-scoped shared workflow context is visible in code and/or UI.
- [ ] Deterministic rules/scoring are implemented and testable.
- [ ] A structured recommendation is produced.
- [ ] Explanation/evidence is available.
- [ ] Audit information is recorded.
- [ ] At least the three sample scenarios can be demonstrated.
- [ ] The case can later map existing agents to LangGraph nodes without redesigning the domain.
- [ ] The Product Bible remains the domain source of truth through later phases.

---

## AI Execution Reminder

When this Product Bible is given to an AI assistant together with a RealRails GitHub post and generic feeder documents:

1. Treat the **current GitHub post** as the immediate task boundary.
2. Treat this **Product Bible** as the domain/product source of truth.
3. Use the **generic RealRails feeder documents** as the engineering method.
4. Use the latest **Repomix** as the implementation truth.
5. Use **ABIP only as an architecture-learning reference**.
6. Do not invent unrelated features, agents, data, or future-phase technologies.
