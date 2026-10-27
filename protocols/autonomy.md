# Autonomy and human control

Autonomy decides *when the team pauses*, never whether it follows guardrails. The human picks
one profile at `init-run --autonomy`. The values below are read by the runtime from
`config/policies.json` → `profiles`; if this table and the policy disagree, the policy wins and
the mismatch is a defect to report.

| | `autonomous` | `supervised` | `hitl` | `unattended` |
|---|---|---|---|---|
| 01_product exit (`product_gate`) | automatic (record assumptions in `ASSUMPTIONS.md`) | Fusion council closed in the stage, or a completed review task | human | as `autonomous` |
| 02_solution exit (`architecture_gate`) | completed review task by a read-only/research/review role | Fusion council or review task | human | as `autonomous` |
| 03_readiness exit (`readiness_gate`) | automatic | automatic | human | automatic |
| 06_release exit (`release_gate`) | human | human | human | executable: the five conditions below, for a run with no task above R1 |
| Claims that need an approved risk checkpoint (`pause_at`) | R3, R4 | R3, R4 | R2, R3, R4 | R3, R4 |
| `checkpoint --kind deviation` | recorded, no pause | pauses | pauses | recorded, no pause |
| Retries per task (`max_task_retries`) | 2 | 2 | 1 | 2 |
| Exhausted task | run continues | run continues | run is `blocked-failure` | run continues |
| Concurrent claims (`max_concurrent_agents`) | 8 | 6 | 6 | 8 |
| Spend ceiling at `init-run` (`require_budget_ceiling`) | required | required | optional | required |

R3 and R4 always need the human (`always_human_risk`) in every profile. The release stage exit
is a human checkpoint in every profile but `unattended`, which replaces that one click with
executable conditions for low-risk runs (below). The hard gates are listed once in
`guardrails.md`. A project may tighten the policy with `.agentic-team/config/policies.local.json`;
it can never loosen it: `{"profiles": {"unattended": {"release_gate": "human"}}}` puts the click
back, and `release_gate: "executable"` on any other profile is refused by `validate` and by every
command of an installed project.

## Risk classes

`config/policies.json` → `risk_levels` defines R0-R4; `risk.matrix` maps a task's `--action` and
`--target` to a level, `risk.path_rules` raise it for sensitive owned paths, and `risk.backstop`
raises it for wording that describes operating on the world. Risk only goes up automatically;
only the human lowers it (`waive --requirement risk:<task> --level R1`). If prose and policy
disagree, apply the safer requirement and raise the mismatch.

## Unattended release (`release_gate: executable`)

`unattended` is `autonomous` with one difference: for a run whose tasks are all R0 or R1,
`advance` leaves 06_release without a human checkpoint, so a supervisor can run issue-to-release
loops with nobody clicking. Production deploys, publishing, messaging real people, spending,
credentials, and destructive operations are R3/R4 tasks and still need the human's risk
checkpoint before `claim` and `exec`: the profile removes the click on the release *stage*, not
a gate on any action that touches the world. The CLI lets the stage exit only when all five
conditions hold, and refuses with the failing one otherwise:

1. **The exit contract passes**, including `verified-head`: HEAD still equals `Verified-SHA`
   (`workflow.md`). The human's `stage-exit:06_release:<check>` waivers apply here as everywhere.
2. **Every declared check passed.** Each completed 04_build and 05_verify task has a passing
   `exec` record for every `--check` it declared. A writing-role task that declared none counts
   only with the human's `checks:<task>` waiver.
3. **No task above R1.** If any task in the run, whatever its status, has an effective risk of
   R2 or more (a migration, a dependency, a staging deploy, a rehearsal against staging), the
   human release checkpoint comes back: `advance` returns `waiting-human` with a `stage`
   checkpoint that names the tasks, exactly as under `autonomous`.
4. **Release packet and rehearsed rollback.** `RELEASE.md` exists without template markers, and
   the run has a completed task with `--action rollback-test`, owned by `release-manager` or
   `devops-engineer`, that declared the rollback command as its `--check` and has a passing
   `exec` record for it by that role at the current HEAD (completion runs the check, so
   `complete` is the rehearsal; a commit after it needs a new rehearsal task, as it needs a new
   verdict). `rollback-test` is R1 on `local` and `ci`, R2 on `staging`, R3 on `production` and
   `external`.
5. **No budget question open.** A pending `budget` checkpoint is the human's to approve, or to
   waive with `waive --requirement budget:<metric>`, before the release.

The exit is recorded as a `release-conditions-met` event with the facts it rested on (the
checked tasks, the rehearsal task, the highest risk in the run, HEAD), so the ledger shows why
no human approved it. `unattended` needs a spend ceiling at `init-run`, as `autonomous` does.

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
