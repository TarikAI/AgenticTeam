# Autonomy and human control

Autonomy decides *when the team pauses*, never whether it follows guardrails. The human picks
one profile at `init-run --autonomy`. The values below are read by the runtime from
`config/policies.json` → `profiles`; if this table and the policy disagree, the policy wins and
the mismatch is a defect to report.

| | `autonomous` | `supervised` | `hitl` |
|---|---|---|---|
| 01_product exit (`product_gate`) | automatic (record assumptions in `ASSUMPTIONS.md`) | Fusion council closed in the stage, or a completed review task | human |
| 02_solution exit (`architecture_gate`) | completed review task by a read-only/research/review role | Fusion council or review task | human |
| 03_readiness exit (`readiness_gate`) | automatic | automatic | human |
| 06_release exit (`release_gate`) | human | human | human |
| Claims that need an approved risk checkpoint (`pause_at`) | R3, R4 | R3, R4 | R2, R3, R4 |
| `checkpoint --kind deviation` | recorded, no pause | pauses | pauses |
| Retries per task (`max_task_retries`) | 2 | 2 | 1 |
| Exhausted task | run continues | run continues | run is `blocked-failure` |
| Concurrent claims (`max_concurrent_agents`) | 8 | 6 | 6 |
| Spend ceiling at `init-run` (`require_budget_ceiling`) | required | required | optional |

R3 and R4 always need the human (`always_human_risk`), and the release gate is human in every
profile. The hard gates are listed once in `guardrails.md`. A project may tighten the policy with
`.agentic-team/config/policies.local.json`; it can never loosen it.

## Risk classes

`config/policies.json` → `risk_levels` defines R0-R4; `risk.matrix` maps a task's `--action` and
`--target` to a level, `risk.path_rules` raise it for sensitive owned paths, and `risk.backstop`
raises it for wording that describes operating on the world. Risk only goes up automatically;
only the human lowers it (`waive --requirement risk:<task> --level R1`). If prose and policy
disagree, apply the safer requirement and raise the mismatch.

## Checkpoints

- Agents raise `decision`, `deviation`, `injection`, and `budget` checkpoints; the CLI refuses
  one without `--alternatives`, `--impact`, `--evidence`, and `--rollback`.
- Only the CLI creates `stage` and `risk` checkpoints, with facts it can see (artifact hashes,
  task states, evidence), so no agent words the question the human approves.
- Decisions need the owner token and are HMAC-signed into the ledger outside the project; gates
  read the ledger, not `state.json` (`runtime.md`).

## Failure behavior and loop detection

- Retry only when new evidence changes the attempt, and only within `max_task_retries`.
- Record every attempt with `fail --reason` (the failing check and the error, not a story).
  The runtime fingerprints the reason (numbers and paths normalized), or takes `--signature`.
- The same signature twice means you are looping: the runtime marks the task `failed` instead
  of retrying and logs `failure-repeated`. Only the human reopens it (`reopen --extend-retries`),
  so bring a changed approach and escalate with a `checkpoint --kind decision`.
- Never hide a degraded result or weaken a check to make it pass.
- Budgets (`policies.json` → `budgets`, tightened per run by `init-run --budget`) open a `budget`
  checkpoint at 80 % and stop the command that would exceed the limit until the human waives it.
  The larger of what agents report (`complete --usage`) and what the owner side meters from the
  harness transcript (`usage --transcript`) counts (`budgets.md`).
