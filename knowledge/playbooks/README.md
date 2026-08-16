# Role Playbooks

A playbook is one agent's personal, hard-won checklist — the things *that role* keeps
getting wrong (or right) in real builds. It is Level 2 of `protocols/evolution.md`.

## Why playbooks and not one big lessons file
`lessons.md` is shared and grows without bound; nobody can read 400 lines before every
task. A playbook is role-scoped and capped, so an agent can actually read it every time.
Lessons are the raw log; playbooks are the distilled reflexes.

## Rules

1. **File name = agent name.** `backend-engineer.md`, `cmo.md`, etc. Created lazily —
   if yours doesn't exist, create it from `_template.md` the first time you learn something.
2. **Read yours at the start of every task**, right after your agent definition. It takes
   seconds and it is the highest-yield reading you do.
3. **Write an entry when reality corrects you**: a review finding, a QA defect, a failed
   assumption, a human correction, or a pattern that clearly worked. Phrase every entry
   as an **imperative check**, not a story:
   - Bad: "We had a bug where the ORM did N+1 in the invoice loop."
   - Good: "Before finishing any list endpoint, log the emitted SQL and confirm one query."
4. **Cap at ~40 lines.** When you hit the cap, merge duplicates and delete checks that
   have become automatic. A playbook you skim past is worthless.
5. **Promote proven checks.** A check that has fired across multiple builds belongs in the
   agent definition itself — propose it via `knowledge/evolution/PROPOSALS.md` (Level 3).
   Once applied there, delete it from the playbook.
6. **Never put project secrets, customer data, or client-identifying details in a playbook.**
   These files travel between projects.

## Entry format

```markdown
- [ ] <imperative check>  <!-- learned: YYYY-MM-DD · cost: what it broke -->
```

Group under `## Before starting`, `## While building`, `## Before claiming done` so the
checks land where they're used.
