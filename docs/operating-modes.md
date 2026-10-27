# Autonomy, Fusion, and progressive context

## Autonomy

`autonomous` continues through reversible local work, repairs within retry budget, records
assumptions and deviations, and exits architecture after an independent review. `supervised`
additionally pauses on deviation checkpoints and exits product/architecture only after a Fusion
council or independent review. `hitl` pauses at product, architecture, readiness, R2+ tasks,
and release. `unattended` is `autonomous` without the release click: for a run with no task
above R1, 06_release exits when five executable conditions hold (the exit contract with
`verified-head`; a passing record for every declared build and verify check; no task above R1;
`RELEASE.md` complete with a rollback rehearsed by `release-manager` or `devops-engineer` as a
`rollback-test` task at the released HEAD; no budget checkpoint pending), see
[autonomy](../protocols/autonomy.md). `autonomous`, `supervised`, and `unattended` runs start
only with a spend ceiling (`init-run --budget`, or `budgets` in `policies.local.json`), since
nobody watches the meter while they run. The values are data in `config/policies.json`.

Use `unattended` for the loops nobody should have to click through: dependency-free fixes,
documentation, tests, internal tooling, a supervisor working an issue queue to a releasable
commit, where the rollback is a command that can be rehearsed locally or in CI. Do not use it
when the work will be R2 or above (a migration, a new dependency, CI or infrastructure
definitions, anything on staging): the human checkpoint returns on the first such task, so
`autonomous` is the honest choice there; when the rollback cannot be exercised by a command; or
when the release itself is the production deploy, which stays an R3 task with its own human risk
checkpoint in every profile. A project that wants the click back under `unattended` sets
`{"profiles": {"unattended": {"release_gate": "human"}}}` in `policies.local.json`.

All profiles stop for production deploys, public publishing/messaging, spending or paid resources,
real credentials/payment methods, destructive/irreversible operations, and legal commitments.
Changing the word “autonomous” cannot remove these gates.

## Fusion councils

Fusion prevents two common multi-agent failures: anchoring on the first answer and smoothing away
important dissent. First proposals remain private until all are submitted; critiques use one frozen
rubric; a moderator produces a single coherent design; an independent verifier checks traceability.

Use Fusion when a choice is ambiguous, expensive, high-risk, or benefits from genuinely different
expertise. Skip it for mechanical implementation with an authoritative design.

Council artifacts are durable under `_fusion/<id>/`: brief, proposals, critiques, synthesis,
dissent, and decision. The final decision includes validation experiments and reopening triggers.

## BMAD-inspired progressive context

Progressive mode borrows the useful flow—product definition, architecture, readiness, task-sized
implementation, review/correction, release, and retrospective—without forcing every project
through unnecessary documents.

ICM-style context contracts make the flow navigable:

- a router stays under roughly 60 lines;
- numbered folders encode order;
- each stage declares working inputs, stable references, process, outputs, human check, exit
  criteria, and next load;
- each fact has one home;
- a fresh agent must orient with the router plus at most two reads;
- task packs target 2,000–8,000 tokens and retain provenance/omissions.

Use `bmad-progressive` when requested or for large, regulated, long-lived, multi-agent, or
context-fragile work. Use `adaptive` for a precise bounded task. Safety and independent
verification are never dropped by either context method.
