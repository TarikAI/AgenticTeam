---
name: agentic-learn
description: Convert completed-run evidence into scoped lessons, agent playbook improvements, evaluated team proposals, and versioned human-approved evolution. Use after delivery, incidents, repeated failures, retrospectives, or when the user asks the agent team to learn and improve itself safely.
---

# Agentic Learn

Read `references/learning-ladder.md`. Learning is evidence governance, not permission for agents
to rewrite their own guardrails.

## Learn safely

1. Gather observed outcomes, task events, verification results, failures, recoveries, and human
   feedback. Include external skill stores when present — adminwright's cross-project store
   (`~/.adminwright`), design-architect's learning registry, and review-gate findings — so
   learning converges here instead of fragmenting per tool. Separate facts from
   interpretation.
2. Write a scoped lesson with trigger, impact, evidence, and when it should *not* apply.
3. Convert an agent-specific lesson into a reversible playbook candidate.
4. Define an evaluation that could disprove the candidate; compare against baseline on relevant
   tasks and inspect regressions.
5. Promote repeated, positive results to a team/agent proposal with version, migration, rollback,
   and affected files.
6. Require human approval before changing agent definitions, autonomy policy, permissions,
   guardrails, or release rules. Record the decision and version.

Never learn from fabricated feedback, one lucky outcome, or a metric optimized at the expense of
security, correctness, accessibility, privacy, or user intent.
