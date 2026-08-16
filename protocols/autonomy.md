# Autonomy and human control

Autonomy controls *when the team pauses*, not whether it follows guardrails. Select one
profile when a run is created; changes are recorded as decisions.

| Profile | Normal behavior | Required pauses |
|---|---|---|
| `autonomous` | Plan, implement, test, repair, and continue without routine confirmation. | High/critical risk and every hard human gate. Release approval remains human. |
| `supervised` | Continue through reversible work and checkpoint material deviations. | Structural deviations, high/critical risk, hard gates. |
| `hitl` | Present decisions at product, architecture, readiness, and release boundaries. | Stage gates, medium+ risk, hard gates. |

## Risk classes

- **R0 — inspect:** read, search, analyze, or locally calculate.
- **R1 — reversible workspace:** edit project files, run tests, create local artifacts.
- **R2 — consequential workspace:** migrations, dependency upgrades, broad refactors, or
  changes with non-obvious rollback.
- **R3 — external/consequential:** deploy, message, publish, purchase, change live data, or
  alter shared infrastructure.
- **R4 — irreversible/sensitive:** destructive operations, credentials, payment movement,
  legal commitments, or safety-critical actions.

`config/policies.json` is the machine-readable authority. If prose and policy disagree, use
the safer requirement and raise the mismatch.

## Checkpoint format

Every pause states: decision, recommendation, alternatives, impact of delay, evidence, and
the smallest response needed from the human. Approved checkpoints are immutable events in
run state.

## Failure behavior

Retry only within the configured budget and only when new evidence changes the attempt.
After that, record the failure, preserve artifacts, release the task lease, and escalate.
Never loop, hide a degraded result, or weaken a check to make it pass.
