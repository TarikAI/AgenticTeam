# Durable supervisor progress

The record the [implementation plan](supervisor-implementation-plan.md) asks for: phase status,
the frozen contract, decisions, the acceptance mapping, evidence, and the next step. States are
kept distinct: **planned**, **implemented**, **offline-verified** (fake workers, no model calls),
**pilot-verified** (a bounded paid run on a configured host), **activated** (a persistent host
task registered by the owner).

**Where it stands (2026-10-29): implemented and offline-verified on Windows 11 / Python 3.14.**
Not pilot-verified, not activated, not run on macOS, Linux, or Python 3.10 (those come from the
CI matrix once the branch is pushed, which has not happened). Nothing was pushed or merged.

Branch: `claude/pensive-poincare-5e61a2`, one phase-group branch based on `main` at `719aad0`
(design `6781b11`, plan and prompts `6d4eb3f`, unattended profile `2f04554`). P0 and P1 have one
commit each; P2 to P7 landed as one commit, because the review fixes rewrote the same functions
the earlier phases introduced and an honest split was not possible.

## Phase status

| Phase | State | Evidence |
|---|---|---|
| P0 Contract and baseline | done | This file; baseline green (below). |
| P1 Runtime prerequisites | offline-verified | Verification view, fail-closed authority, budget admission, finite usage; G21, G22. |
| P2 Storage and intake | offline-verified | `IntakeTests`, `StoreTests`. |
| P3 Attempt lifecycle | offline-verified | `LaunchRecoveryTests`, wrapper and `ProcessTree`. |
| P4 Orchestration and accounting | offline-verified | `LifecycleTests`, `MeteringTests`, `HumanTests`, `EvidenceTests`, `TamperTests`, `CheckoutTests`, `OperationsTests`. |
| P5 Adapter and packaging | offline-verified (adapter not run against a real CLI session) | `PackagingTests`, `AuthorityTests`, `IsolationProbeTests`, guard test. |
| P6 Triggers and host operation | offline-verified | `GithubPollTests`, host examples, operator guide, `supervisor-unattended` scenario. |
| P7 Review and release candidate | offline release candidate | Independent review below; every finding fixed with a regression test. Pilot not run (no authorization for spend). |

## Baseline (P0, 2026-10-29, Windows 11, Python 3.14.5)

| Check | Result |
|---|---|
| `python scripts/agentic_team.py validate` | OK: 50 agents, 9 presets, 13 harnesses |
| `python scripts/agentic_team.py docs --check` | Generated docs are current |
| `python -m unittest discover -s tests` | 200 tests, OK (1 skip: the opt-in live smoke) |
| `python evals/run_scenarios.py` | 7/7 scenarios passed |
| Claude Code CLI on this host | 2.1.310; `--help` lists `--print`, `--output-format`, `--max-budget-usd`, `--permission-mode`, `--allowedTools`, `--model`, `--bare`; it does **not** list `--max-turns` |

## Final verification (P7)

| Check | Result |
|---|---|
| `python scripts/agentic_team.py validate` | OK: 50 agents, 9 presets, 13 harnesses |
| `python scripts/agentic_team.py docs --check` | Generated docs are current |
| `python -m unittest discover -s tests` | 284 tests in 515 s, OK (1 skip: the opt-in live smoke); `test_supervisor.py` alone: 73 tests |
| `python evals/run_scenarios.py` | 8/8 scenarios passed (adds `supervisor-unattended`) |
| `python scripts/preflight_skills.py` | passed |
| Live smoke, paid pilot | not run (needs the owner's authorization for model spend) |

## Frozen contract

Where this contract and `supervisor-design.md` differ, this contract wins. Changes made in P7
after the independent review are marked **(P7)**.

### Authority boundary

- **Two homes, one view.** The supervisor runs as the owner with `AGENTIC_TEAM_HOME` (tokens,
  bindings, ledger). A worker gets its own empty `AGENTIC_TEAM_HOME` and `AGENTIC_TEAM_VIEW`, a
  directory the owner side exports before every launch with the run's binding and ledger, no token.
- **Lookup.** With `AGENTIC_TEAM_VIEW` set, `VerifiedView` reads only the view, never the worker's
  writable home **(P7)**; without it, the home. A v3 run with neither is *bound but unreadable*:
  no decision in `state.json` counts and gated commands refuse, naming the missing view. v2 runs
  awaiting `migrate` keep the explicit legacy path.
- **Where the real check is (P7).** The CLI's gates run in the worker's process, which can point
  the CLI at a view it wrote or edit `state.json`; they are defense in depth. After every attempt
  the owner runs `audit verify` with the token, which now replays every stage exit through a human
  (or executable) gate, every claim of a risk-gated task, and every waiver against the signed home
  ledger, and compares the view with its export digests (a deleted file counts). Any gap holds the
  job as `tamper`. Production credentials stay out of the worker's reach.
- **Owner copy (P7).** Owner-side work (metering with the token, audits, launching wrappers) runs
  from `<store>/bin/` (a copy of the runtime and the supervisor taken when the store is created,
  refreshed with `supervise owner-copy --refresh`), never from the checkout's `bin/`. `serve`,
  `resume`, `poll-github`, and `verify-isolation` refuse (exit 3) when the running supervisor's own
  code lives inside the checkout.
- **No new authority.** The supervisor never approves, rejects, resolves, waives, cancels runtime
  tasks, or reopens. It records `fail` for tasks an ended attempt still held, meters usage as the
  owner, and runs `audit verify`.

### Storage

| Location | Holds | Written by |
|---|---|---|
| `<project>/.agentic-team/supervisor/inbox/`, `quarantine/`, `STATUS.md` | intake, refused files with a `.reason`, the digest | `enqueue`, `poll-github`, file drops; the tick |
| `<owner home>/supervisor/<name>-<hash12>/` | `store.json`, `config.json`, `control.json` (checkout, pause, aggregate allowance, reservations, keyed charges), `jobs/`, `sources/`, `attempts/<job>/<attempt>/`, `bin/` (owner copy), `view/`, `worker-home/`, `log.jsonl`, `digest.json`, `.lock` | the supervisor only |

`<hash12>` is the SHA-256 of the normalized project path. Records carry `"schema": 1`; an unknown
schema or an unreadable record refuses launches and names the file, while intake continues. Writes
are atomic with an fsync and bounded Windows retries. The store lock is an operating-system file
lock (`msvcrt` / `flock`), released when the holder dies **(P7)**; a tick holds it from
reconciliation to digest. Spend is a keyed record (`charges`, one entry per attempt) merged with
the job records, so a crash between two writes neither loses nor doubles it and a record moved
aside never refunds it **(P7)**.

### Events and jobs

- Event: `id` (`[a-z0-9][a-z0-9._-]{0,79}`, no `..`, no reserved device stem), `kind`
  (`issue|alert|schedule|manual`), `title` ≤ 200, `brief` ≤ 20 000, `acceptance` ≤ 50 × 500,
  `source_key` ≤ 300, small `source`; ≤ 64 KiB; unknown keys refused; text is untrusted.
- Same source key and digest: duplicate. Different payload: `ConflictError`, never replacing the
  job. A cancelled or failed source runs again only with the owner's `enqueue --requeue` (new id)
  **(P7)**.
- The job freezes its configuration at acceptance; `resume --refresh-config` re-freezes one held
  job on the owner's request **(P7)**. Command templates are validated against the known
  placeholders at `configure` **(P7)**.

### Job states

`queued → starting → running → reconciling → (done | retrying | needs-human | failed | cancelled)`,
`retrying → starting`, `needs-human → retrying | done | cancelled`. `paused` is a flag. Hold kinds:
`checkpoint`, `failed-task`, `unknown-usage`, `ownership`, `budget`, `tamper`, `evidence` **(P7)**,
`source`, `pointer`, `config`, `adapter`. A held job whose last attempt is not reconciled keeps
being reconciled every tick **(P7)**.

### Launch handshake and process ownership

1. Under the lock: reserve the checkout; create or adopt the run (`init-run --name=<title>` so a
   title cannot be read as a flag, **(P7)**); write `BRIEF.md`; export the view; record the attempt
   and its reservation; write `intent.json`; set `starting`; then spawn. Any failure before the
   wrapper is a visible `config` hold, and a launch interrupted after the reservation resumes on the
   next tick **(P7)**.
2. The wrapper claims the attempt with `O_EXCL`, writes `start.json`, marks `spawning.json`
   **(P7)**, starts the worker in a tree it controls (a Windows job object that ends with the
   wrapper; a POSIX session), writes `worker.json`, heartbeats, enforces the timeout, honors
   `cancel` (also before the worker starts), and writes `exit.json` before freezing the transcript.
3. Reconciliation never trusts a PID alone. A live wrapper this supervisor started is never
   abandoned while it starts **(P7)**; otherwise an unclaimed attempt past the grace is abandoned by
   taking its claim. A claim with a fresh heartbeat is running. A stale heartbeat with a live or
   unidentifiable wrapper, a live worker without its wrapper, a wrapper that died while spawning,
   a POSIX process group that still has members, or a Windows tree without a job object holds the
   job as `ownership` **(P7)**. The supervisor never kills by PID.
4. `fail` is recorded only after the attempt provably ended, with the signature
   `supervisor-attempt-ended`; a replay records nothing twice.

### Checkout reservation

One writer per checkout (`max_workers` must be 1). A job holds the reservation from its first
launch until it is terminal, its last attempt is reconciled, and the tree is clean, or until the
owner's `release`, which also refuses an unreconciled attempt **(P7)**. `cancel` of a job whose
last attempt is unreconciled only asks the wrapper to stop and keeps everything until a tick
reconciles the attempt **(P7)**. The tree is clean only when `git diff HEAD` is empty, nothing is
flagged skip-worktree or assume-unchanged, and no untracked file exists outside the committed
`.gitignore` files; runtime output is excluded (`.agentic-team/runs/`, `supervisor/`,
`knowledge/`, `CURRENT.md`, `backup/`; `knowledge/` because 07_learn writes lessons after
verification); an unreadable tree is never clean **(P7)**. The supervisor never resets or cleans.

### Budget policy

Explicit run ceiling, attempt reservation, and an aggregate allowance only the owner replenishes.
Launch needs the reservation within the run's remaining allowance (ceiling minus the larger of
runtime and supervisor-known spend, minus open reservations; lifted by the human's `budget:usd`
waiver **(P7)**) and within the aggregate. The Claude adapter passes `--max-budget-usd` =
reservation ÷ headroom and requires a turn limit unless `--turn-limit timeout-only`. Metering is
once per transcript digest; exit 3 from `usage` still counts; unknown usage keeps its reservation
and holds, and may be settled even on a finished job **(P7)**. Runtime admission refuses `claim`
and `exec` once a ceiling is spent.

### Completion

`done` requires: the attempt metered; no pending checkpoint after metering; `audit verify` clean
(including the decision replay); the owner-side re-check of the 05_verify, 06_release (with the
executable release conditions when no human approved it), and 07_learn exit contracts; an event log
that shows the run reaching 07_learn and `run-completed`; a recorded verified commit; and a clean
tree at it (a later commit may touch only runtime output) **(P7)**. A forged `complete` status
holds as `evidence`.

### Owner controls and exit codes

`enqueue [--requeue]`, `configure`, `serve`, `status`, `pause`, `resume [--confirm-stopped]
[--usage-transcript F | --charge-reservation] [--refresh-config]`, `cancel`, `release`,
`allowance`, `verify-isolation` (sentinel unreadable **and** view unwritable **(P7)**),
`owner-copy [--refresh]` **(P7)**, `poll-github`, `host-example` (prints the owner copy's command),
`prune`. Exit codes 0 / 1 / 2 (a job needs the human) / 3 (blocked) / 64, precedence 1 > 3 > 2 > 0.
The digest shows how each job's worker is bounded **(P7)**.

## Independent review (P7)

A read-only reviewer traced the code against this contract and reproduced each finding offline.
It did not approve a pilot. Disposition of every finding:

| # | Severity | Finding | Fix | Regression test |
|---|---|---|---|---|
| 1 | critical | a worker's own writable home outranked the view; forged unsigned records passed gates, invisible to the owner's audit | view-exclusive lookup; `audit verify` replays stage exits, risk-gated claims, and waivers; deleted view files count | `test_authority.VerificationViewTests.test_a_binding_planted_in_the_worker_home_is_ignored`, `..._replays_gated_steps_a_forged_view_allowed`, `..._finds_a_stage_exit_without_a_signed_approval` |
| 2 | high | `done` rested on the worker-written status field | owner-side completion re-check of exit contracts and the event log; missing verified commit is a problem | `test_supervisor.ReviewFindingTests.test_forged_completion_is_not_done`, `..._compares_head_with_the_verified_commit` |
| 3 | high | cancelling a held job freed the checkout while its worker lived | cancel and release wait for the last attempt to be reconciled; held unreconciled attempts keep being reconciled | `..._cancelling_an_ownership_hold_keeps_the_checkout_until_the_writer_ends` |
| 4 | high | the owner side ran the checkout's `bin/` with the token | owner copy in the store; credential ops refuse from inside the checkout; `verify-isolation` also requires a read-only view | `test_supervisor.IsolationProbeTests`, `OperationsTests.test_host_examples_use_absolute_paths_and_register_nothing` |
| 5 | medium-high | breaking a stale lock could let two contenders hold it | OS file lock, released on holder death; nothing stale to break | `StoreTests.test_lock_contention_is_blocked` (a killed holder process) |
| 6 | medium | a failure between run creation and `starting` stranded the job | launch failures become visible holds; an interrupted first launch resumes; template placeholders validated | `..._a_launch_failure_before_the_wrapper_is_a_visible_hold`, `..._an_interrupted_first_launch_resumes` |
| 7 | medium | `poll-github` advanced the watermark past an issue it failed to accept | only `ConflictError` is reported; any other failure propagates and keeps the watermark | `GithubPollTests.test_pagination_auth_and_rate_limits` |
| 8 | medium | moving a torn record aside refunded its spend | keyed `charges` merged with job records | `..._moving_a_record_aside_keeps_its_spend` |
| 9 | low-medium | config holds, budget holds, and cancelled sources had no way out | `--refresh-config`, the human's `budget:usd` waiver honored, `enqueue --requeue`; config resume re-checks and refuses at once | `..._config_and_budget_holds_have_a_way_out`, `..._a_cancelled_source_can_be_requeued_by_the_owner` |
| 10 | low | skip-worktree, `.git/info/exclude`, and git failures hid changes | new `dirty_paths`; unreadable is never clean | `..._hidden_changes_and_unreadable_trees_are_not_clean` |
| 11 | low | the digest did not show unisolated or timeout-only workers; this file was stale | Worker column in the digest; this file rewritten | `..._the_digest_says_how_the_worker_is_bounded` |
| — | unverified (POSIX) | a wrapper dying while spawning, or descendants outliving the worker, looked dead | `spawning.json` marker; process-group liveness; Windows trees without a job object hold | covered by the reconcile rules; POSIX runs only in CI |

The reviewer's reproduction scripts were re-run against the fixed code: the planted-home waiver
is refused, the cancelled-hold scenario keeps the second job queued, the polling script now sees
the failure instead of a silent skip, the template typo is refused at `configure`, and hidden
changes are reported.

## Acceptance mapping

Milestone column: **offline** gates the offline milestone; **hardening** must pass before the
pilot is called operational; **pilot** needs the configured host. Test ids are under `tests/`.

| Area | Case | Test | Milestone |
|---|---|---|---|
| Event integrity | duplicate event | `test_supervisor.IntakeTests.test_duplicate_event_is_harmless` | offline |
| | conflicting payload | `test_supervisor.IntakeTests.test_conflicting_payload_is_reported` | offline |
| | concurrent enqueue | `test_supervisor.IntakeTests.test_concurrent_enqueue_accepts_one_job` | offline |
| | cross-repository issue number | `test_supervisor.GithubPollTests.test_issue_numbers_are_namespaced_by_repository` | offline |
| | traversal, absolute, reserved names | `test_supervisor.IntakeTests.test_unsafe_ids_are_refused` | hardening |
| | oversized and malformed event | `test_supervisor.IntakeTests.test_malformed_and_oversized_events_are_quarantined` | hardening |
| Store durability | torn write | `test_supervisor.StoreTests.test_torn_record_blocks_launches` | hardening |
| | crash before/after inbox handoff | `test_supervisor.IntakeTests.test_crash_between_job_record_and_inbox_removal` | offline |
| | lock contention, dead holder | `test_supervisor.StoreTests.test_lock_contention_is_blocked` | hardening |
| | schema mismatch | `test_supervisor.StoreTests.test_schema_mismatch_refuses_launches` | hardening |
| | log-write failure | `test_supervisor.StoreTests.test_log_failure_keeps_the_transition` | hardening |
| | disk full | `test_supervisor.StoreTests.test_disk_full_stops_launches` | hardening |
| | record moved aside keeps spend | `test_supervisor.ReviewFindingTests.test_moving_a_record_aside_keeps_its_spend` | hardening |
| Launch recovery | crash before spawn | `test_supervisor.LaunchRecoveryTests.test_crash_before_spawn_abandons_the_attempt` | offline |
| | after spawn, before parent save | `test_supervisor.LaunchRecoveryTests.test_crash_after_spawn_adopts_the_wrapper` | offline |
| | late wrapper after abandonment | `test_supervisor.LaunchRecoveryTests.test_late_wrapper_cannot_claim_an_abandoned_attempt` | offline |
| | after exit receipt | `test_supervisor.LaunchRecoveryTests.test_exit_receipt_is_reconciled_once` | offline |
| | stale PID, lost wrapper | `test_supervisor.LaunchRecoveryTests.test_dead_wrapper_without_receipt_is_a_lost_attempt` | offline |
| | PID reuse (unreadable identity, mismatched identity) | `test_supervisor.LaunchRecoveryTests.test_reused_pid_holds_instead_of_relaunching`, `..._a_reused_pid_with_another_identity_is_a_lost_attempt` | hardening |
| | worker outliving its wrapper | `test_supervisor.LaunchRecoveryTests.test_worker_outliving_its_wrapper_holds` | offline |
| | two supervisors on one checkout | `test_supervisor.LaunchRecoveryTests.test_two_supervisors_never_launch_twice` (threads), `StoreTests.test_lock_contention_is_blocked` (processes) | offline |
| | interrupted first launch; launch failure | `test_supervisor.ReviewFindingTests.test_an_interrupted_first_launch_resumes`, `..._a_launch_failure_before_the_wrapper_is_a_visible_hold` | offline |
| Checkout safety | dirty tree, no destructive cleanup | `test_supervisor.CheckoutTests.test_dirty_tree_blocks_the_first_launch` | offline |
| | hidden or unreadable tree state | `test_supervisor.ReviewFindingTests.test_hidden_changes_and_unreadable_trees_are_not_clean` | offline |
| | unrelated active run | `test_supervisor.CheckoutTests.test_unrelated_active_run_blocks_launch` | offline |
| | paused or held job keeps the checkout | `test_supervisor.CheckoutTests.test_held_job_keeps_the_checkout`, `ReviewFindingTests.test_cancelling_an_ownership_hold_keeps_the_checkout_until_the_writer_ends` | offline |
| | max-workers above one | `test_supervisor.CheckoutTests.test_parallel_workers_are_refused` | offline |
| | current-run pointer change | `test_supervisor.CheckoutTests.test_current_run_pointer_change_holds` | offline |
| Authority | different homes, missing view | `test_authority.VerificationViewTests.test_worker_home_without_a_view_refuses_gated_commands` | offline |
| | planted home, forged view | `test_authority.VerificationViewTests.test_a_binding_planted_in_the_worker_home_is_ignored`, `..._replays_gated_steps_a_forged_view_allowed`, `..._finds_a_stage_exit_without_a_signed_approval` | offline |
| | fabricated state approval | `test_authority.VerificationViewTests.test_fabricated_state_approval_is_ignored_through_the_view`, `test_supervisor.TamperTests` | offline |
| | real approval and rejection visible | `test_authority.VerificationViewTests.test_real_decisions_are_visible_through_the_view` | offline |
| | worker environment; owner copy | `test_supervisor.AuthorityTests.test_worker_gets_a_scratch_home_and_a_view`, `IsolationProbeTests.test_owner_work_runs_from_the_owner_copy`, `test_harness.GuardTests.test_supervisor_paths_and_commands_are_owner_only` | offline |
| | worker cannot read owner material or write the view | `test_supervisor.IsolationProbeTests.test_the_boundary_must_hide_the_store_and_protect_the_view` (the probe's logic with a stand-in boundary); a real boundary is not testable offline on one OS user | pilot |
| Metering | valid result | `test_supervisor.LifecycleTests.test_job_runs_to_done_with_metered_usage` | offline |
| | malformed, truncated, missing result | `test_supervisor.MeteringTests.test_missing_usage_holds_and_keeps_the_reservation`, `..._malformed_result_holds` | offline |
| | non-finite or negative cost | `test_orchestration.MetricsAndBudgetTests.test_nonfinite_or_negative_usage_is_refused` | hardening |
| | duplicate digest, crash after ingestion | `test_supervisor.MeteringTests.test_metering_is_idempotent_after_a_crash` | offline |
| | over-budget exit 3 | `test_supervisor.MeteringTests.test_over_budget_ingestion_still_counts` | offline |
| | complete run, then a final budget checkpoint | `test_supervisor.MeteringTests.test_final_budget_checkpoint_keeps_a_complete_run_from_done` | offline |
| Retry and leases | known-cost crash retried | `test_supervisor.LifecycleTests.test_known_cost_crash_is_retried_and_finishes` | offline |
| | repeated failure, exhausted task, reopen | `test_supervisor.LifecycleTests.test_repeated_failure_holds_until_the_human_reopens` | offline |
| | no double-recorded failure | `test_supervisor.LaunchRecoveryTests.test_exit_receipt_is_reconciled_once` | offline |
| | no lease release while the old writer lives | `test_supervisor.LaunchRecoveryTests.test_live_writer_keeps_its_claims`, `..._worker_outliving_its_wrapper_holds` | offline |
| Human interaction | R2 release pause, approve, resume | `test_supervisor.HumanTests.test_r2_work_pauses_at_release_and_resumes_after_approval` | offline |
| | R3/R4 action pause | `test_supervisor.HumanTests.test_r3_action_holds_for_the_human` | offline |
| | rejection stays blocked | `test_supervisor.HumanTests.test_rejection_stays_held` | offline |
| | cancel stops only owned processes, keeps changes | `test_supervisor.HumanTests.test_cancel_stops_the_owned_worker_and_keeps_changes` | offline |
| | holds with a way out; requeue | `test_supervisor.ReviewFindingTests.test_config_and_budget_holds_have_a_way_out`, `..._a_cancelled_source_can_be_requeued_by_the_owner` | offline |
| Evidence | passing command, failing verdict | `test_supervisor.EvidenceTests.test_failing_verdict_is_not_done` | offline |
| | stale HEAD (runtime gate and supervisor comparison) | `test_supervisor.EvidenceTests.test_commit_after_verification_is_not_done`, `ReviewFindingTests.test_the_supervisor_compares_head_with_the_verified_commit` | offline |
| | change after verification | `test_supervisor.EvidenceTests.test_change_after_verification_holds` | offline |
| | missing rollback rehearsal | `test_supervisor.EvidenceTests.test_missing_rollback_rehearsal_is_not_done` | offline |
| | missing report; forged completion | `test_supervisor.EvidenceTests.test_missing_delivery_report_is_not_done`, `ReviewFindingTests.test_forged_completion_is_not_done` | offline |
| | zero exit with an incomplete run | `test_supervisor.EvidenceTests.test_zero_exit_with_an_incomplete_run_retries` | offline |
| Packaging | direct helper and installed alias | `test_supervisor.PackagingTests.test_installed_alias_and_direct_helper` | offline |
| | missing helper | `test_supervisor.PackagingTests.test_missing_helper_is_reported` | offline |
| | plugin export | `test_supervisor.PackagingTests.test_plugin_ships_the_supervisor` | offline |
| | reinstall and uninstall keep supervisor state | `test_supervisor.PackagingTests.test_reinstall_and_uninstall_keep_supervisor_state` | hardening |
| | Windows paths with spaces | `test_supervisor.PackagingTests.test_paths_with_spaces` | hardening |
| | Python 3.10, macOS, Linux | the CI matrix (not run: the branch is not pushed) | hardening |
| Operations | once, until-idle, forever | `test_supervisor.OperationsTests.test_once_until_idle_and_forever` | offline |
| | graceful shutdown with a running attempt | `test_supervisor.ReviewFindingTests.test_an_interrupt_leaves_a_running_attempt_with_its_wrapper` | hardening |
| | bounded backoff | `test_supervisor.OperationsTests.test_retry_backoff_is_bounded` | hardening |
| | host restart with a detached worker | `test_supervisor.LaunchRecoveryTests.test_fresh_supervisor_reconciles_a_detached_worker` | offline |
| | polling pagination, auth failure, rate limit, failed acceptance | `test_supervisor.GithubPollTests.test_pagination_auth_and_rate_limits` | hardening |
| | status without secrets; worker bounds shown | `test_supervisor.OperationsTests.test_status_shows_no_secrets`, `ReviewFindingTests.test_the_digest_says_how_the_worker_is_bounded` | offline |
| | retention | `test_supervisor.OperationsTests.test_prune_keeps_unfinished_and_unmetered_work` | hardening |
| | host examples run the owner copy | `test_supervisor.OperationsTests.test_host_examples_use_absolute_paths_and_register_nothing` | hardening |

## Pilot setup (prepared, not run)

The pilot needs the owner's explicit authorization for model spend and a configured host.

| Item | Value |
|---|---|
| Project | one scratch project with a clean, committed tree and a fixture issue (`AC-` lines) |
| Isolation | a restricted local account (`runas` or WSL user) or a container: owner home unreadable, view mounted read-only, worker home writable; `verify-isolation` must pass |
| CLI | the installed Claude Code version recorded with `claude --version` before the run (2.1.310 on this host) |
| Model | the owner's choice (`configure --model`), recorded in the job |
| Budgets | `--budget usd=5`, `--attempt-usd 2`, `--headroom 1.25`, aggregate allowance 10 USD |
| Limits | `--timeout 1800`; `--turn-limit timeout-only` (this CLI does not advertise `--max-turns`) |
| Run | `<owner copy> serve --until-idle --max-seconds 3600` |
| Stop conditions | any hold, any exit other than 0, the aggregate allowance spent |
| Owner controls | `status`, `pause --all`, `cancel --job`, the runtime's `approve`/`reject` for checkpoints |

## Remaining limits

- The CLI's gates inside a worker are defense in depth; forgery is found by the owner's audit
  after the attempt. A worker that can write the run folder could forge a consistent set of
  artifacts and events; independent verification and owner review address that, not the code.
- Owner controls carry no separate credential; the store must sit behind the isolation boundary.
- One checkout, one worker; no webhooks; the Claude adapter has not run against a real session.
- Cost figures are the harness's estimate; the harness's spend limit can overshoot.
- Not run here: macOS, Linux, Python 3.10, the paid pilot, a registered host task.

## Next step

The owner's decision: review and merge the branch into local `main` (and push to run the CI
matrix), then authorize the pilot above if desired.
