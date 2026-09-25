# Autonomy and human control

Autonomy controls *when the team pauses*, not whether it follows guardrails. Select one
profile when a run is created; changes are recorded as decisions.

| Profile | Normal behavior | Required pauses |
|---|---|---|
| `autonomous` | Plan, implement, test, repair, and continue without routine confirmation. Deviations are recorded, not paused on. Architecture exits after an independent review. | R3/R4 tasks and every hard human gate. Release approval remains human. |
| `supervised` | Continue through reversible work. Product and architecture exit after a Fusion council or an independent review. | Deviation checkpoints, R3/R4 tasks, hard gates. |
| `hitl` | Present decisions at product, architecture, readiness, and release boundaries. | Stage gates, R2+ tasks, hard gates. |

The exact gate values live in `config/policies.json` (`product_gate`, `architecture_gate`,
`readiness_gate`, `release_gate`, `deviation`, `pause_at`); the runtime reads them and nothing
else.

## Risk classes

- **R0 — inspect:** read, search, analyze, or locally calculate.
- **R1 — reversible workspace:** edit project files, run tests, create local artifacts.
- **R2 — consequential workspace:** migrations, dependency upgrades, broad refactors, or
  changes with non-obvious rollback.
- **R3 — external/consequential:** deploy, message, publish, purchase, change live data, or
  alter shared infrastructure.
- **R4 — irreversible/sensitive:** destructive operations, credentials, payment movement,
  legal commitments, or safety-critical actions.

`config/policies.json` is the machine-readable authority (`risk_levels`, and `risk.matrix` for
how an action and target map to a level). If prose and policy disagree, use the safer
requirement and raise the mismatch.

## Checkpoint format

Every agent-raised pause states the question, recommendation, alternatives, impact, evidence,
and rollback; the CLI refuses a checkpoint without them. Stage and risk gates are created by
the CLI with the facts it can see (artifacts and their hashes, task states, evidence). Human
decisions are appended to an HMAC-signed, hash-chained ledger outside the project; they are
tamper-evident (`audit verify`), and gates read them from the ledger rather than from state.

## Failure behavior

Retry only within the configured budget and only when new evidence changes the attempt.
After that, record the failure, preserve artifacts, release the task lease, and escalate.
Never loop, hide a degraded result, or weaken a check to make it pass.
