# Operating guide

## Minimum task envelope

Every task requires: ID, objective, owner/capability, artifact, named inputs, dependencies,
owned paths, risk class, acceptance checks, and evidence required for completion.

## Lifecycle

`pending -> ready -> claimed -> completed`; exceptional states are `blocked`, `failed`, and
`cancelled`. Use the installed CLI (`python .agentic-team/bin/agentic_team.py --help`) for the exact
commands. The CLI is the single writer for run state.

## Stage order

`00_intake`, `01_product`, `02_solution`, `03_readiness`, `04_build`, `05_verify`,
`06_release`, `07_learn`. Entry modes may start later but may not omit a safety-relevant input.

## Completion evidence

Record changed artifact paths, checks and outcomes, acceptance mapping, deviations, residual
risks, and follow-ups. Generated files, unrun test commands, and self-review are not proof.
