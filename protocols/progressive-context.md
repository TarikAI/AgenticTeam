# Progressive context protocol

AgenticTeam adapts ICM's compact router and stage-contract ideas and BMAD's progressive
planning/build flow. Use this mode when requested, for large or regulated work, or when a
single context would become noisy. Small, well-specified tasks may use direct execution.

## Context architecture

- The root router is stable and short; it points, it does not teach the whole system.
- Numbered folders encode stage order.
- Every active stage owns a `CONTEXT.md` contract with **Inputs**, **Process**, **Outputs**,
  **Human check**, and **Exit criteria**.
- Each fact has one authoritative home. Other documents link to it rather than copying it.
- Stable knowledge lives outside per-run artifacts.
- State and indexes are generated from files; agents never hand-edit generated state views.

## Load rule

Start with the router and current stage contract. Read at most two additional documents
before acting unless the contract explicitly names more. Target 2,000–8,000 tokens for a
task context pack. If more is necessary, the context engineer writes a narrow summary that
links to evidence and records what was omitted.

## Standard stages

1. `00_intake` — normalize the request, constraints, entry mode, and open questions.
2. `01_product` — brief/PRD, journeys, scope, measurable acceptance.
3. `02_solution` — architecture, UX direction, risks, contracts, specialist reviews.
4. `03_readiness` — traceability, sequencing, ownership, and unresolved blockers.
5. `04_build` — small task packets, implementation, integration, continuously updated evidence.
6. `05_verify` — independent review, tests, security/accessibility/performance as applicable.
7. `06_release` — release plan, human approval, rollback, and operational handoff.
8. `07_learn` — retrospective, evidence-backed lessons, evaluated playbook proposals.

## Entry modes

- `idea`: start at intake and progressively create product/solution artifacts.
- `plan-given`: adopt the supplied plan, validate only what is needed for safe execution,
  then enter readiness or build.
- `execute-only`: do not generate a competing plan; create task envelopes from the supplied
  authority and start at build.

## Cold walk test

A fresh agent must be able to identify the current stage, its task, the next action, the
required output, and the checkpoint using the router plus no more than two reads. Failure
means the context design must be repaired before scaling concurrency.
