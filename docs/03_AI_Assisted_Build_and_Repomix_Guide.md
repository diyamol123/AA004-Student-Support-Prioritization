# RealRails Batch 2 — AI-Assisted Build & Repomix Guide
## Purpose

Use AI as a development mentor while keeping the Product Bible and repository as the source of truth.

---

## Standard AI Working Set

For build/review tasks, give the AI:

```text
Current GitHub Post
+
Selected Product Bible
+
Relevant Generic Feeder Guides
+
Latest Repomix
```

ABIP may be attached only when architecture comparison is useful.

---

## Source Priority

```text
GitHub Post
   ↓
Product Bible
   ↓
Generic Feeder Documents
   ↓
Repomix
   ↓
ABIP Reference
   ↓
AI General Knowledge
```

AI must not override higher-priority sources.

---

## Recommended AI Workflow

Ask AI to:

1. read all inputs first
2. summarize the exact task boundary
3. inspect current repository before changing it
4. map Product Bible requirements to existing code
5. propose the smallest implementation plan
6. implement incrementally
7. provide run/test commands
8. validate actual behavior
9. identify remaining gaps
10. end with a completion checklist

Do not ask AI to "build everything" without context.

---

## Repomix Purpose

Repomix is the AI-readable snapshot of the current repository.

Use it to:

- understand code structure
- identify actual agents/services
- inspect workflow context
- confirm endpoints
- review rule logic
- verify frontend/backend integration
- guide Docker changes
- guide later LangGraph evolution

Repomix is read-only reference material.

Make edits in the repository.

---

## Generate Repomix

From the repository root, a typical command is:

```bash
npx repomix . --output repomix-output.xml
```

If Repomix is installed or configured differently, use the repository's approved command.

Regenerate after meaningful changes.

---

## AI Troubleshooting Prompt Pattern

When blocked, provide:

```text
1. Current GitHub Post
2. Product Bible
3. Latest Repomix
4. Exact command used
5. Exact error output
6. What was expected
```

Ask AI to diagnose the **existing implementation** rather than redesigning the product.

---

## AI Safety / Quality Rules

Do not allow AI to:

- invent domain rules
- silently change acceptance criteria
- add future-phase technology
- introduce secrets into source control
- remove audit/explanation just to simplify code
- claim tests passed when they were not run
- treat generated code as validated evidence

The student must run the application and capture evidence.

---

## Completion Evidence

A good AI-assisted cycle ends with:

```text
Implement
  ↓
Run
  ↓
Observe
  ↓
Correct
  ↓
Validate
  ↓
Generate Repomix
  ↓
Submit Evidence
```
