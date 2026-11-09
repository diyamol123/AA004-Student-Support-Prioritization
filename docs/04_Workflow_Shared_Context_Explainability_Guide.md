# RealRails Batch 2 — Workflow, Shared Context & Explainability Guide
## Purpose

Use this guide in Phase 1.4 to make the working application explain its own Agentic AI flow.

---

## What the Reviewer Must Understand

The application should make it possible to answer:

1. What business input started the workflow?
2. Which agents executed?
3. What does each agent do?
4. What did each agent read?
5. What did each agent produce?
6. How did the shared context change?
7. Which deterministic rules influenced the result?
8. Where was the final recommendation made?
9. Why was that recommendation produced?
10. Where is the audit evidence?

---

## Required Concept

Use the term:

> **Run-scoped shared workflow context**

It is the structured state used during one workflow execution.

It is not automatically:

- long-term memory
- semantic memory
- persistent agent memory
- an AI brain

---

## Recommended Context View

A case may expose:

```text
workflow_id
business_input
validated_input

shared_context
  ├─ reference/domain data
  ├─ calculated fields
  └─ current workflow status

agent_outputs
  ├─ agent_a
  ├─ agent_b
  ├─ agent_c
  └─ ...

final_recommendation
explanation
audit_reference
errors
```

Only show fields that actually exist.

---

## Recommended UI Patterns

Use one simple pattern or combination:

- agent execution timeline
- workflow console
- expandable agent cards
- shared-context panel
- decision-evidence panel
- audit panel

The UI should be functional, not theatrical.

Avoid creating a separate animated HTML learning assignment.

---

## Agent Card Minimum

A reviewer should be able to see:

```text
Agent Name
Responsibility
Input Used
Output Produced
Status
Evidence / Rule Result
```

Do not pretend agents are natural-language chat participants unless that is actually implemented.

---

## Explanation Rules

Explanation should be derived from:

- agent outputs
- triggered rules
- scores
- matched evidence
- missing-data flags
- decision result

In Phase 1, deterministic explanation templates are sufficient.

Do not invent evidence.

---

## Audit Rules

Audit should allow a reviewer to trace:

```text
Input
→ Execution
→ Agent Outputs
→ Rule Triggers
→ Final Recommendation
```

An in-memory audit is acceptable for the MVP if clearly stated.

---

## Product Bible Alignment

The Product Bible controls:

- agent names/responsibilities
- domain fields
- rule meaning
- decision output
- evidence requirements

The generic workflow view must adapt to the selected case.

Do not force every project to display identical domain content.

---

## Completion Check

- [ ] actual agents are visible
- [ ] execution order is accurate
- [ ] shared context is visible or inspectable
- [ ] rule/evidence is visible
- [ ] final recommendation is visible
- [ ] explanation is evidence-based
- [ ] audit reference exists
- [ ] UI does not claim nonexistent functionality
