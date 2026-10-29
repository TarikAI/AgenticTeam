# Runtime and concurrency

The harness runs the models; `.agentic-team/bin/agentic_team.py` owns project state. Every
mutation takes a run lock and atomically replaces `state.json`; agent prose is never state.
Flags and examples: `docs/cli.md` (the source checkout's copy); `--help` on any command.

## Task lifecycle

`pending → ready → claimed → completed`, plus `failed` and `cancelled`. Closed for the stage
gate: `completed` and `cancelled`. A task is `ready` when every dependency is `completed`.

| Transition | Command | Who | Runtime checks |
|---|---|---|---|
| create | `add-task` | orchestrator | owner installed; stage = current or later; `--action`/`--target` derive risk; build tasks of writing roles need `--path` or `--exclusive` |
| claim | `claim` | owner agent | current stage; claimant is the owner; `max_concurrent_agents`; no owned-path overlap; not a builder of the task it `--verifies`; R-level in `pause_at` needs an approved risk checkpoint |
| renew | `renew` | claimant | 1-480 minutes |
| run a check | `exec` | claimant | records exit code, duration, git HEAD, output; refuses unapproved command-rule matches |
| complete | `complete` | claimant | typed evidence; `--run-checks` must pass |
| fail | `fail --reason` | claimant | counts an attempt; `failed` when retries are exhausted |
| reassign | `reassign` | orchestrator | unclaimed open task; reason recorded |
| reopen a wedged claim | `reopen` | orchestrator | counts as an attempt |
| reopen failed/cancelled/completed, `--extend-retries` | `reopen --by` | **human** | owner token |
| cancel | `cancel --by` | **human** | owner token; refuses open dependents unless `--cascade` |
| decide | `approve` / `reject` / `resolve` | **human** | owner token |
| waive | `waive` | **human** | owner token; the only way to lower risk or skip a named exit check |
| advance | `advance` | orchestrator | `workflow.md` → Stage exit contracts |
| promote, migrate, audit | `promote`, `migrate`, `audit verify` | **human** | owner token |

Read-only and research roles never claim or complete; the orchestrator records for them.

## Run states

`active`, `waiting-human` (a checkpoint is pending), `verifying` (in 05_verify),
`blocked-rejection`, `blocked-failure`, `complete`, `closed`.

- **blocked-rejection:** the human rejected a checkpoint. Fix the work, then the human runs
  `resolve` with a corrective note. Approving some other checkpoint never clears it.
- **blocked-failure:** a profile that stops on failure (`hitl`) has an exhausted task. The human
  either `reopen --extend-retries N` or `cancel`s it.

## Exit codes

`0` ok · `1` error (stderr says why) · `2` stopped at a human gate · `3` run blocked · `64` usage
error. On `2`, show the pending checkpoint and wait; on `3`, show the rejection or failed task and
stop. Never loop on `advance`.

## Events and the ledger

- `runs/<id>/events.jsonl` is append-only and hash-chained (each line carries the previous
  line's hash); read it with `log`, summarize with `metrics`. Only the CLI writes it.
- A worker started by a supervisor gets its own, empty `AGENTIC_TEAM_HOME` and an
  `AGENTIC_TEAM_VIEW`: a directory the owner side exports (`export-view --to <dir>`) holding the
  run's binding and ledger and no token. Gates read the binding and ledger from the home first,
  then from the view; a v3 run with neither refuses gated commands rather than trusting
  `state.json`.
- Human decisions go to an HMAC-signed, hash-chained ledger under `~/.agentic-team/ledger/`.
  Gates read the ledger, not `state.json`, so editing state approves nothing. `audit verify`
  recomputes both chains. Agents never read `~/.agentic-team/`.
- This is tamper-evident, not tamper-proof: code running unsandboxed as the same OS user can
  still do damage. Unattended runs belong in an OS sandbox, WSL2, a container, or a separate
  account.

## Parallel work

- Parallelize only dependency-ready tasks with non-overlapping owned paths.
- Prefer native worktrees when the harness has them; one build-integrator merges in dependency
  order. Contract and schema changes go through the cto-architect.
- Verification starts from the integration commit recorded when 04_build exits and ends with a
  verdict on the current HEAD; release refuses to exit if HEAD moved after that verdict.

## Recovery

State survives process and context loss. On resume: read `CURRENT.md`, run `status --brief`,
run `recover-leases` for expired claims, continue the current stage. A killed command can leave
`.state.lock`; `unlock` clears it. Never infer completion from files; attach evidence through the
CLI.
