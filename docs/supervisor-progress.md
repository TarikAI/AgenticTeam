# Durable supervisor progress

The record the [implementation plan](supervisor-implementation-plan.md) asks for: phase status,
the frozen contract, decisions, the acceptance mapping, evidence, and the next step. States are
kept distinct: **planned**, **implemented**, **offline-verified** (fake workers, no model calls),
**pilot-verified** (a bounded paid run on a configured host), **activated** (a persistent host
task registered by the owner).

Branch: `claude/pensive-poincare-5e61a2` (one phase-group branch; one commit per phase or phase
group, merged into local `main` only when the owner authorizes it). Baseline: `main` at
`719aad0` (design `6781b11`, plan and prompts `6d4eb3f`, unattended profile `2f04554`).

## Phase status

| Phase | State | Commit | Notes |
|---|---|---|---|
| P0 Contract and baseline | implemented | see `git log` | This file; baseline checks green before any code change. |
| P1 Runtime prerequisites | planned | | |
| P2 Storage and intake | planned | | |
| P3 Attempt lifecycle | planned | | |
| P4 Orchestration and accounting | planned | | |
| P5 Adapter and packaging | planned | | |
| P6 Triggers and host operation | planned | | |
| P7 Review and release candidate | planned | | |

## Baseline (P0, 2026-10-29, Windows 11, Python 3.14.5)

| Check | Result |
|---|---|
| `python scripts/agentic_team.py validate` | OK: 50 agents, 9 presets, 13 harnesses |
| `python scripts/agentic_team.py docs --check` | Generated docs are current |
| `python -m unittest discover -s tests` | 200 tests, OK (1 skip: the opt-in live smoke) |
| `python evals/run_scenarios.py` | 7/7 scenarios passed |
| Claude Code CLI on this host | 2.1.310; `--help` lists `--print`, `--output-format`, `--max-budget-usd`, `--permission-mode`, `--allowedTools`, `--model`, `--bare`; it does **not** list `--max-turns` |

No existing failure is carried into P1.

## Frozen contract

Where this contract and `supervisor-design.md` differ, this contract wins; the design describes
the intent, the plan corrected it, and this section is what the code implements.

### Authority boundary

- **Two homes, one view.** The supervisor runs as the owner with `AGENTIC_TEAM_HOME` (tokens,
  bindings, ledger). A worker gets its own empty `AGENTIC_TEAM_HOME` (a scratch folder in the
  owner store with no tokens) and `AGENTIC_TEAM_VIEW`, a directory the owner side exports before
  every launch with the run's binding (`runs/<key>.json`) and ledger (`ledger/<key>.jsonl`), the
  same layout as the home, and no tokens.
- **Lookup order.** `VerifiedView` reads the binding and ledger from the home first, then from
  the view. A run whose state carries `owner_token_sha256` (every v3 run) with neither source is
  *bound but unreadable*: approvals in `state.json` count for nothing, and every gated command
  (`claim`, `advance`, human decisions) refuses with a message naming the missing view. Runs
  created before the owner binding (no `owner_token_sha256`) keep their explicit legacy path.
- **Integrity of the view.** The view is trusted only as far as the worker cannot write it: with
  the same OS user and no isolation it is defense in depth, exactly like the home ledger today.
  The supervisor therefore re-checks after every attempt, as the owner, with `audit verify`
  (ledger MACs, forged state approvals, event chain) and compares the view with the home ledger;
  either failure holds the job as `tamper`.
- **No new authority.** The supervisor never calls `approve`, `reject`, `resolve`, `waive`,
  `cancel` (runtime), or `reopen`. It records `fail` for tasks an ended attempt still held, meters
  usage as the owner (`usage --transcript`), and runs `audit verify`; nothing else.

### Storage

| Location | Holds | Writable by |
|---|---|---|
| `<project>/.agentic-team/supervisor/inbox/<event-id>.json` | triggers waiting for intake | `enqueue`, `poll-github`, file-drop adapters |
| `<project>/.agentic-team/supervisor/quarantine/` | refused inbox files plus a `.reason` file | the tick |
| `<project>/.agentic-team/supervisor/STATUS.md` | readable digest (a view, never proof) | the tick |
| `<owner home>/supervisor/<name>-<hash12>/` | the owner store: `store.json`, `config.json`, `control.json` (checkout reservation, pause, aggregate allowance and reservations), `jobs/`, `sources/`, `attempts/<job>/<attempt>/`, `view/`, `worker-home/`, `log.jsonl`, `.lock` | the supervisor only |

`<hash12>` is the SHA-256 of the normalized absolute project path, so the worker cannot redirect
the store. Records carry `"schema": 1`; an unknown schema or an unreadable record refuses new
launches and names the file. Writes are atomic (temporary file, fsync, `os.replace` with bounded
Windows retries). One cross-process lock (`.lock`, `O_EXCL`) serializes every store mutation; a
tick holds it from reconciliation to digest. State records are authoritative; `log.jsonl` and
`STATUS.md` are derived, and a failed log write never undoes a committed transition.

### Events and jobs

- Event: `id` (`[a-z0-9][a-z0-9._-]{0,79}`, no `..`, no Windows reserved stem), `kind`
  (`issue|alert|schedule|manual`), `title` (≤ 200), `brief` (≤ 20 000), `acceptance` (≤ 50 lines of
  ≤ 500), `source_key` (≤ 300, default `manual:<id>`), optional `source` object; ≤ 64 KiB; unknown
  keys refused. Text is untrusted brief material; it never selects settings, paths, or commands.
- Acceptance is atomic and idempotent: the source key's SHA-256 indexes `sources/`; the same key
  and payload digest is a harmless duplicate; a different payload is a reported conflict and
  never replaces the job. The job id is the event id.
- The job freezes the effective configuration at acceptance (profile, entry, context, adapter,
  executable or command template, tool allowlist, run budget, attempt reservation, retries,
  timeouts, isolation, accepted HEAD). Later `configure` changes affect only new jobs.

### Job states

`queued → starting → running → reconciling → (done | retrying | needs-human | failed | cancelled)`,
`retrying → starting`, `needs-human → retrying | done | cancelled` (owner `resume` or `cancel`
only). `paused` is a flag, not a state: a paused job is not launched; a running one finishes its
attempt. Every transition records `from`, `to`, `reason`, the attempt or owner action, and time.

### Launch handshake and process ownership

1. Under the lock: reserve the checkout, check the tree and policy, create or adopt the run,
   write `BRIEF.md`, export the view, record the attempt (unique id, nonce) and its budget
   reservation, write `intent.json`, set the job `starting`. Only then spawn.
2. The supervisor spawns a detached wrapper. The wrapper claims the attempt by creating
   `claim` with `O_EXCL` (exactly one wrapper per attempt), writes `start.json`, starts the
   worker (argv, `shell=False`, stdout and stderr to separate files) inside a process tree it
   controls (a Windows job object that kills the tree when the wrapper dies; a new POSIX session),
   writes `worker.json`, touches `heartbeat`, enforces the timeout, honors a `cancel` request, and
   writes `exit.json` (exit code, reason, transcript digest) before freezing the transcript.
3. Reconciliation never trusts a PID alone. No claim after the start grace: the supervisor creates
   `claim` itself (`O_EXCL`), so a late wrapper cannot start, and the attempt is `abandoned` at no
   cost. A claim with a fresh heartbeat is running. A stale heartbeat with a live wrapper (by PID
   and process start time where the platform exposes it), or a live worker without its wrapper,
   holds the job as `ownership`. Wrapper and worker both gone without an exit receipt is a lost
   attempt. The supervisor never kills by PID; only the wrapper ends the tree it started.
4. Leases are never recovered while an attempt can act; `fail` is recorded only after the attempt
   provably ended, with the stable signature `supervisor-attempt-ended`, so the runtime's
   repeated-failure rule applies and a replay records nothing twice (the task is no longer claimed).

### Checkout reservation

One writer per checkout: `max_workers` other than 1 is refused at `configure`. A job holds the
reservation from its first launch until it is terminal and the tree is clean (or the owner
records a disposition with `release`); paused, retrying, and held jobs keep it. The first launch
of a job refuses a dirty tree (excluding `.agentic-team/runs/`, `.agentic-team/supervisor/`,
`.agentic-team/CURRENT.md`, `.agentic-team/backup/`) and an unrelated active run in `CURRENT.md`.
The supervisor never resets, cleans, or checks out anything. A changed `CURRENT.md` while a job
owns the checkout holds the job as `pointer`.

### Budget policy

- Every job runs under an explicit run ceiling (`init-run --budget usd=N`), an attempt reservation
  (`attempt_usd`), and the persisted aggregate allowance in `control.json`, which only the owner
  replenishes (`allowance --add-usd`) and which does not reset on restart.
- Before a launch: reservation ≤ run ceiling − max(runtime usage, supervisor charges) − open
  reservations, and ≤ aggregate allowance − spent − open reservations. Otherwise the job holds
  (`budget`) or the queue blocks (aggregate exhausted).
- The Claude adapter passes `--max-budget-usd` = reservation ÷ headroom (default 1.25), because the
  harness limit is an estimate that can overshoot; the wall-clock timeout always applies. The turn
  limit is required unless the owner configures `turn_limit: timeout-only`, which the digest shows,
  because this CLI version does not advertise `--max-turns`.
- After an attempt the frozen transcript is metered once (digest checked against the run's
  `usage_sources` first; exit 3 from `usage` still means the usage was saved). Unknown usage keeps
  the reservation as spent and holds the job; only the owner clears it by metering a transcript
  (`resume --usage-transcript`) or charging the reservation (`resume --charge-reservation`).
- Runtime admission (P1): `claim` and `exec` refuse once a token or USD ceiling is spent, unless the
  human waived `budget:<metric>`; status, metering, `fail`, `recover-leases`, and human decisions
  keep working. Usage figures that are negative or not finite are refused.

### Completion

`done` requires: run `complete` (07_learn exited, so the delivery report exists); the attempt's
usage metered; no pending checkpoint after metering; `audit verify` clean; the tree clean
outside runtime paths; and HEAD equal to the run's verified commit when git exists. A project
without git is held (`source`), because source integrity cannot be shown.

### Owner controls and exit codes

`enqueue`, `configure`, `serve`, `status`, `pause`, `resume`, `cancel`, `release`, `allowance`,
`verify-isolation`, `poll-github`, `host-example`, `prune`. They change scheduling only.
`serve --once` is one tick; `--until-idle` ticks until nothing is starting, running, reconciling,
queued and launchable, or retrying (backoff included), then prints the hold summary; `--interval`
ticks forever and, on interrupt, stops intake and exits, leaving wrapped workers running (the next
start reconciles them). Exit codes: 0 ok, 1 operational failure, 2 a job needs the human, 3 blocked
(lock busy, store refuses launches, queue blocked), 64 usage error; precedence 1 > 3 > 2 > 0.
`resume` revalidates the hold: signed decisions in the ledger, no failed task, usage known,
ownership proven, pointer and tree as required. `cancel` stops only the attempt's own tree through
its wrapper and preserves every change.

## Acceptance mapping

Milestone column: **offline** gates the offline milestone; **hardening** must pass before the
pilot is called operational. Test ids are `module.Class.method` under `tests/`.

| Area | Case | Phase | Test | Milestone |
|---|---|---|---|---|
| Event integrity | duplicate event | P2 | `test_supervisor.IntakeTests.test_duplicate_event_is_harmless` | offline |
| | same key, conflicting payload | P2 | `test_supervisor.IntakeTests.test_conflicting_payload_is_reported` | offline |
| | concurrent enqueue | P2 | `test_supervisor.IntakeTests.test_concurrent_enqueue_accepts_one_job` | offline |
| | cross-repository issue number | P6 | `test_supervisor.GithubPollTests.test_issue_numbers_are_namespaced_by_repository` | offline |
| | traversal, absolute, reserved names | P2 | `test_supervisor.IntakeTests.test_unsafe_ids_are_refused` | hardening |
| | oversized and malformed event | P2 | `test_supervisor.IntakeTests.test_malformed_and_oversized_events_are_quarantined` | hardening |
| Store durability | torn write | P2 | `test_supervisor.StoreTests.test_torn_record_blocks_launches` | hardening |
| | crash before/after inbox handoff | P2 | `test_supervisor.IntakeTests.test_crash_between_job_record_and_inbox_removal` | offline |
| | lock contention | P2 | `test_supervisor.StoreTests.test_lock_contention_is_blocked` | hardening |
| | schema mismatch | P2 | `test_supervisor.StoreTests.test_schema_mismatch_refuses_launches` | hardening |
| | log-write failure after a transition | P2 | `test_supervisor.StoreTests.test_log_failure_keeps_the_transition` | hardening |
| | disk full | P2 | `test_supervisor.StoreTests.test_disk_full_stops_launches` | hardening |
| Launch recovery | crash before spawn | P3 | `test_supervisor.LaunchRecoveryTests.test_crash_before_spawn_abandons_the_attempt` | offline |
| | after spawn, before parent save | P3 | `test_supervisor.LaunchRecoveryTests.test_crash_after_spawn_adopts_the_wrapper` | offline |
| | after start receipt | P3 | `test_supervisor.LaunchRecoveryTests.test_late_wrapper_cannot_claim_an_abandoned_attempt` | offline |
| | after exit receipt | P3 | `test_supervisor.LaunchRecoveryTests.test_exit_receipt_is_reconciled_once` | offline |
| | stale PID | P3 | `test_supervisor.LaunchRecoveryTests.test_dead_wrapper_without_receipt_is_a_lost_attempt` | offline |
| | PID reuse | P3 | `test_supervisor.LaunchRecoveryTests.test_reused_pid_holds_instead_of_relaunching` | hardening |
| | worker outliving its parent | P3 | `test_supervisor.LaunchRecoveryTests.test_worker_outliving_its_wrapper_holds` | offline |
| | two supervisors on one checkout | P3 | `test_supervisor.LaunchRecoveryTests.test_two_supervisors_never_launch_twice` | offline |
| Checkout safety | pre-existing dirty tree | P4 | `test_supervisor.CheckoutTests.test_dirty_tree_blocks_the_first_launch` | offline |
| | unrelated active run | P4 | `test_supervisor.CheckoutTests.test_unrelated_active_run_blocks_launch` | offline |
| | paused job with changes | P4 | `test_supervisor.CheckoutTests.test_held_job_keeps_the_checkout` | offline |
| | max-workers above one | P2 | `test_supervisor.CheckoutTests.test_parallel_workers_are_refused` | offline |
| | current-run pointer change | P4 | `test_supervisor.CheckoutTests.test_current_run_pointer_change_holds` | offline |
| | no destructive reset or cleanup | P4 | `test_supervisor.CheckoutTests.test_dirty_tree_blocks_the_first_launch` (files untouched) | offline |
| Authority | different owner and worker homes | P1 | `test_authority.VerificationViewTests.test_worker_home_without_a_view_refuses_gated_commands` | offline |
| | unavailable verification view | P1 | `test_authority.VerificationViewTests.test_worker_home_without_a_view_refuses_gated_commands` | offline |
| | fabricated approval in state | P1 | `test_authority.VerificationViewTests.test_fabricated_state_approval_is_ignored_through_the_view` | offline |
| | real approval and rejection visible | P1 | `test_authority.VerificationViewTests.test_real_decisions_are_visible_through_the_view` | offline |
| | worker cannot read owner material or mutate control records | P4/P5 | `test_supervisor.AuthorityTests.test_worker_gets_a_scratch_home_and_a_view`, `test_harness.GuardTests.test_supervisor_paths_and_commands_are_owner_only` | offline |
| Metering | valid result | P4 | `test_supervisor.LifecycleTests.test_job_runs_to_done_with_metered_usage` | offline |
| | malformed, truncated, missing result | P4 | `test_supervisor.MeteringTests.test_missing_usage_holds_and_keeps_the_reservation`, `test_supervisor.MeteringTests.test_malformed_result_holds` | offline |
| | non-finite or negative cost | P1 | `test_orchestration.MetricsAndBudgetTests.test_nonfinite_or_negative_usage_is_refused` | hardening |
| | duplicate digest, crash after ingestion | P4 | `test_supervisor.MeteringTests.test_metering_is_idempotent_after_a_crash` | offline |
| | over-budget exit 3 | P4 | `test_supervisor.MeteringTests.test_over_budget_ingestion_still_counts` | offline |
| | complete run, then a final budget checkpoint | P4 | `test_supervisor.MeteringTests.test_final_budget_checkpoint_keeps_a_complete_run_from_done` | offline |
| Retry and leases | recoverable known-cost crash | P4 | `test_supervisor.LifecycleTests.test_known_cost_crash_is_retried_and_finishes` | offline |
| | unknown-cost hold | P4 | `test_supervisor.MeteringTests.test_missing_usage_holds_and_keeps_the_reservation` | offline |
| | repeated failure; required task exhausted while the run is active | P4 | `test_supervisor.LifecycleTests.test_repeated_failure_holds_until_the_human_reopens` | offline |
| | no double-recorded failure | P3/P4 | `test_supervisor.LaunchRecoveryTests.test_exit_receipt_is_reconciled_once` | offline |
| | no lease release while the old writer lives | P3 | `test_supervisor.LaunchRecoveryTests.test_live_writer_keeps_its_claims` | offline |
| Human interaction | R2 release pause, approve, resume | P4 | `test_supervisor.HumanTests.test_r2_work_pauses_at_release_and_resumes_after_approval` | offline |
| | R3/R4 action pause | P4 | `test_supervisor.HumanTests.test_r3_action_holds_for_the_human` | offline |
| | rejection stays blocked | P4 | `test_supervisor.HumanTests.test_rejection_stays_held` | offline |
| | exhausted task needs a legitimate reopen | P4 | `test_supervisor.LifecycleTests.test_repeated_failure_holds_until_the_human_reopens` | offline |
| | cancel stops only owned processes, keeps changes | P3/P4 | `test_supervisor.HumanTests.test_cancel_stops_the_owned_worker_and_keeps_changes` | offline |
| Evidence | passing command, failing acceptance | P4 | `test_supervisor.EvidenceTests.test_failing_verdict_is_not_done` | offline |
| | stale HEAD | P4 | `test_supervisor.EvidenceTests.test_commit_after_verification_is_not_done` | offline |
| | tracked or untracked change after verification | P4 | `test_supervisor.EvidenceTests.test_change_after_verification_holds` | offline |
| | missing rollback rehearsal | P4 | `test_supervisor.EvidenceTests.test_missing_rollback_rehearsal_is_not_done` | offline |
| | missing learning or report artifact | P4 | `test_supervisor.EvidenceTests.test_missing_delivery_report_is_not_done` | offline |
| | zero exit with an incomplete run | P4 | `test_supervisor.EvidenceTests.test_zero_exit_with_an_incomplete_run_retries` | offline |
| Packaging | direct helper and installed alias | P5 | `test_supervisor.PackagingTests.test_installed_alias_and_direct_helper` | offline |
| | missing helper | P5 | `test_supervisor.PackagingTests.test_missing_helper_is_reported` | offline |
| | plugin export | P5 | `test_supervisor.PackagingTests.test_plugin_ships_the_supervisor` | offline |
| | reinstall preserves supervisor state | P5 | `test_supervisor.PackagingTests.test_reinstall_and_uninstall_keep_supervisor_state` | hardening |
| | uninstall and purge semantics | P5 | `test_supervisor.PackagingTests.test_reinstall_and_uninstall_keep_supervisor_state` | hardening |
| | Python 3.10, Windows paths with spaces | P5 | `test_supervisor.PackagingTests.test_paths_with_spaces`; 3.10 through the CI matrix | hardening |
| Operations | once, until-idle, forever | P4 | `test_supervisor.OperationsTests.test_once_until_idle_and_forever` | offline |
| | bounded backoff | P4 | `test_supervisor.OperationsTests.test_retry_backoff_is_bounded` | hardening |
| | host restart with a detached worker | P3 | `test_supervisor.LaunchRecoveryTests.test_fresh_supervisor_reconciles_a_detached_worker` | offline |
| | graceful shutdown | P4 | `test_supervisor.OperationsTests.test_once_until_idle_and_forever` (interrupt) | hardening |
| | polling pagination, auth failure, rate limit | P6 | `test_supervisor.GithubPollTests.test_pagination_auth_and_rate_limits` | hardening |
| | status without secrets | P4 | `test_supervisor.OperationsTests.test_status_shows_no_secrets` | offline |
| | retention | P6 | `test_supervisor.OperationsTests.test_prune_keeps_unfinished_and_unmetered_work` | hardening |

## Decisions

- One phase-group branch (this worktree's) with one commit per phase or phase group; no merge,
  push, release, paid run, or host registration without the owner's authorization.
- The runtime is read through its module (state, verified view, transcript parsing) and changed
  only through the installed CLI (`init-run`, `usage`, `fail`, `audit verify`, `export-view`),
  with explicit `--project` and `--run`.
- Paid launches (the Claude adapter) require a verified isolation boundary
  (`verify-isolation` with a harmless sentinel). The command adapter runs an owner-supplied argv
  (scripted workers, tests) and is shown as unisolated in the digest.

## Next step

P1: the verification view and budget admission in `scripts/agentic_team.py`, with their tests.
