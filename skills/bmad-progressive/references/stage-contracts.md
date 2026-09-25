# Stage exit contracts by context profile

Source of truth: `config/policies.json → stage_exits`. Each stage's `CONTEXT.md` prints its own
rules under **Exit criteria**. "Artifact" means the file exists in `<run>/` and has no unfilled
`{{...}}` markers or TODO.

| Stage | adaptive | bmad-progressive |
|---|---|---|
| 00_intake | BRIEF.md with `AC-` ids | BRIEF.md; ASSUMPTIONS.md |
| 01_product | — | PRD.md with `AC-` ids |
| 02_solution | — | ARCHITECTURE.md |
| 03_readiness | — | READINESS.md; it traces every `AC-` id in PRD.md/BRIEF.md |
| 04_build | typed evidence on every completed write task | same |
| 05_verify | VERIFICATION.md verdict header (PASS, or CONDITIONAL with the human's waiver) | same |
| 06_release | — | RELEASE.md |
| 07_learn | DELIVERY-REPORT.md | RETROSPECTIVE.md; DELIVERY-REPORT.md |

Both profiles add, for every stage: all tasks closed, no pending checkpoint, activated specialists
finished or deactivated, and the autonomy profile's gate (`product_gate`, `architecture_gate`,
`readiness_gate`, `release_gate`; see `.agentic-team/protocols/autonomy.md`). A human may waive one
named requirement with `waive --requirement stage-exit:<stage>:<check>`.

Readiness traces user outcomes and non-functional requirements to architecture, tasks, tests,
owners, and unresolved risks. A task packet contains only what one implementer needs.
