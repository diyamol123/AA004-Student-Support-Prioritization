# RealRails Batch 2 — Product Bible Execution Guide
## Purpose

This guide explains **how to use any approved Product Bible** during Phase 1.

The Product Bible defines **WHAT the application must do**.
The generic RealRails guides define **HOW the application should be engineered**.

---

## Source-of-Truth Order

Always use this order:

1. Current GitHub post — immediate task boundary
2. Selected Product Bible — domain/product truth
3. Generic RealRails feeder documents — engineering method
4. Latest Repomix — actual implementation truth
5. ABIP — architecture-learning reference only
6. AI general knowledge — implementation assistance only

Do not let AI replace a Product Bible requirement with a generic assumption.

---

## Product Bible → Implementation Mapping

| Product Bible Section | Implementation Meaning |
|---|---|
| Business Problem | Defines why the product exists |
| Business Input | Request/API/UI input model |
| Domain Data Required | Seeded/sample data or simple persistence |
| Agent Definitions | Specialized domain agent/services |
| Agent Inputs/Outputs | Structured contracts/models |
| Shared Workflow Context | Run-scoped workflow state |
| Deterministic Rules | Rule/scoring/validation services |
| Decision Logic | Decision/Recommendation Agent |
| Explanation/Evidence | Explainability layer/UI |
| Audit Requirements | Audit event/store/reference |
| Sample Scenarios | Demo/test cases |
| Expected MVP UI | Minimum usable frontend |
| Conditional Opportunity | Reserved for Phase 2.2 |
| LLM Opportunity | Reserved for Phase 2.3 |
| Acceptance Criteria | Definition of done |

---

## Standard Execution Pattern

```text
Read Product Bible
      ↓
Extract Domain Contract
      ↓
Map to RealRails Architecture
      ↓
Implement Small Working MVP
      ↓
Validate Product Bible Scenarios
      ↓
Generate Repomix
      ↓
Use Repomix for Next Post
```

---

## What AI May Decide

AI may help decide:

- file/folder structure
- class/function names
- clean API design
- component design
- implementation sequence
- test organization
- simple data representation
- small technical details

AI must preserve the Product Bible.

---

## What AI Must Not Invent

Do not add:

- new business actors
- new decision authority
- extra agents without a real need
- unsupported data fields
- unrequested external integrations
- LLM/RAG/LangGraph in Phase 1
- production claims
- sensitive profiling
- business rules that contradict the Product Bible

If a requirement is ambiguous, choose the **smallest reasonable MVP interpretation** and document the assumption.

---

## Standard MVP Quality

The implementation should be:

- runnable
- deterministic
- structured
- explainable
- auditable
- easy to demonstrate
- easy to evolve later

Do not optimize for enterprise scale in Phase 1.

---

## Completion Check

Before claiming Product Bible coverage, confirm:

- [ ] business input implemented
- [ ] required domain data represented
- [ ] 3–5 meaningful agents implemented
- [ ] structured outputs exist
- [ ] shared workflow context exists
- [ ] deterministic rules implemented
- [ ] decision logic implemented
- [ ] explanation/evidence available
- [ ] audit available
- [ ] sample scenarios demonstrable
- [ ] MVP boundaries respected
