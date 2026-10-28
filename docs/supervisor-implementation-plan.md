# Durable supervisor implementation plan

Prepared on 2026-10-28 against runtime baseline `d7714c2`. During review, the design-only
merge `6fc55a2` became local `main`; it changes the README and supervisor design, not code.

AgenticTeam already has evidence gates and an unattended release profile. The remaining
work is a durable supervisor that accepts a trigger, runs a bounded worker, reconciles
its outcome after interruption, and produces a verified local result or an actionable
human hold. Implement the supervisor in phases, beginning with authority and recovery
contracts. The current design has gaps that would otherwise permit duplicate workers,
unaccounted retries, and inconsistent approval checks.

This is an implementation plan, not a claim that the service exists. The companion
[prompt pack](supervisor-implementation-prompts.md) contains a master implementation
prompt, individual phase prompts, a documentation handoff, and an independent review prompt.

## Decisions fixed by this plan

These settle the points on which the design, this plan, and the prompt pack disagreed.

| Decision | Value |
| --- | --- |
| Module and command | `scripts/agentic_supervisor.py`, copied into `.agentic-team/bin/` on install and exposed as the `supervise` helper subcommand (`HELPER_SCRIPTS`, `HELPER_COMMANDS`, `SCRIPT_REFS`). Any module split stays beside it in `bin/`. |
| Branch and merge | One task branch per phase or phase group (for example `supervisor-p1-authority`), merged into local `main` with a merge commit (`--no-ff`) only when the owner authorizes the merge, as the evidence-gate and unattended-profile work were. No push without authorization. |
| Agents | One coding session owns the implementation; a second, documentation-only session is optional and never edits `scripts/`, `tests/`, this plan, or the prompt pack. |
| Milestones | The offline milestone (fake workers, no model calls) is gated by the cases marked "offline" in the acceptance table; "hardening" cases may follow in P7 or after the pilot without blocking it. |
| Entry mode | An owner decision per supervisor configuration, not a correctness rule: `execute-only` for triggers whose brief is already a plan (a triaged issue with `AC-` lines), `idea` for triggers that need product and architecture work. The configuration records the choice; triggers cannot change it. |

## Verified starting point

| Item | Observed state |
| --- | --- |
| Evidence gates | `16e4d70` merges `9e3a9d0`: executable completion checks, verification pinned to HEAD, budget ceilings and transcript metering, and live-smoke acceptance scoring. |
| Unattended profile | `d7714c2` merges `2f04554`: eligible R0/R1 runs can leave release through executable conditions; higher-risk work retains human gates. |
| Local history | At final inspection, `main` is `6fc55a2`, six commits ahead of the locally recorded `origin/main`; no remote fetch or push was performed during this review. |
| Concurrent documentation | The initial README modification and untracked design were committed as `6781b11` and merged in `6fc55a2` during review. They were not edited by this planning task. |
| Supervisor implementation | No supervisor helper, command registration, or supervisor tests exist in the inspected tree. |
| Current validation | Source validation passes: 50 agents, 9 presets, 13 harnesses. Generated documentation check passes. Seven deterministic scenarios pass. Full unit-suite result is recorded in the final verification section. |

The existing scorer in `evals/live_smoke.py` checks its particular smoke-test fixture.
It does not automatically turn arbitrary GitHub acceptance prose into trustworthy tests.
Workers must still create task-specific checks and obtain independent verification.

## Scope and completion

The first complete version supports one installed project checkout, one active worker,
manual events, explicitly configured GitHub issue polling, durable attempts, bounded
retries, transcript accounting, owner pause/resume/cancel controls, and local status output.
Python remains standard-library-only and compatible with 3.10+. Windows is a first-class
target for the supervisor and fake-worker tests.

“Complete” means the run has passed build, independent verification, release, and the
required learning/reporting stage; final usage has been reconciled; no required task or
checkpoint remains unresolved; and the owner can inspect the local change and evidence.
It does not include automatically pushing, merging, publishing, deploying, commenting on
issues, or sending notifications. Those actions retain their existing human gates.

Deliver two milestones: an offline-tested implementation and an operational pilot on an
explicitly configured host. The pilot needs a supported worker isolation boundary and an
owner-authorized model budget. Do not call the service operational solely because fake
workers pass. Per-job worktrees, distributed scheduling, webhook servers, dashboards,
automatic PR creation, and additional model providers are later extensions.

## Corrections required before the main loop

| Concern | Current behavior or design gap | Required implementation decision |
| --- | --- | --- |
| Authority lookup | `agentic_home()` selects the binding and ledger root. Removing `AGENTIC_TEAM_HOME` changes that root; `VerifiedView` falls back to raw state when it cannot find a binding (`enforced = bound is not None`). Confirmed on 2026-10-29: a worker without the owner's home would pass gates on an edited `state.json`, with only the Claude Code guard hook in the way. | Separate secret storage from a trusted, worker-readable verification view. Concrete mechanism: the owner side exports a read-only directory (`AGENTIC_TEAM_VIEW`, say) holding the run's binding digest and ledger records and no tokens; `VerifiedView` reads the binding from the home first, then from the view; a run whose state carries `owner_token_sha256` (every v3 run) with neither source present is treated as bound-but-unreadable, so gated mutations are refused with a message naming the missing view. Preserve genuine approvals and rejections across owner and worker environments. |
| Owner isolation | Removing an environment variable does not stop the same OS user reading its files. | Keep tokens and authoritative supervisor records outside worker access; verify the chosen isolation boundary with a harmless sentinel. Hooks remain additional protection. |
| Spending | Runtime transcript metering happens after spending; `claim` and `exec` do not universally recheck previously spent USD. | Persist reservations and check remaining budgets before every launch. Add narrowly scoped runtime enforcement where required. Use a supported harness limit, timeout and turn limit; never describe estimated client-side limits as exact billing caps. |
| Unknown usage | The draft allows a missing result message to be logged without stopping retries. | Hold further paid attempts when usage is unknown. Retain the reservation and explain the recovery action. Never invent a zero-cost or successful result. |
| Completion | A final transcript can create a budget checkpoint after the run already says `complete`. | Meter and inspect pending checkpoints before setting the job to `done`. Run status alone is insufficient. |
| Crash recovery | The draft starts a process before durably recording ownership and relies on PID liveness. | Persist launch intent and a unique attempt identity first. Use durable start/exit receipts and validated process ownership. Ambiguity reserves the checkout and requires investigation. |
| Checkout ownership | A default worker cap of one does not reject larger caps or protect paused changes. | Reject parallel workers in one checkout. Keep its reservation while a job is paused, retrying, or has unresolved changes. |
| Lease recovery | Recovering leases while the old worker is alive can make its task available again. | Prove the old process tree has stopped before releasing claims; otherwise hold. A supervisor heartbeat is not proof that its worker is making progress. |
| Human continuation | The draft never revisits `needs-human`. | Provide owner resume that revalidates signed decisions, required tasks, usage and checkout ownership. The supervisor grants no approvals. |
| Retry accounting | Worker attempts and task retries are different; a failed noncritical task can leave the run `active`. | Persist both; inspect required failed tasks and repeated failure signatures before relaunch. Record each attempt failure once. |
| Input trust | Raw event IDs become paths; issue numbers collide across repositories. | Use validated IDs and namespaced source keys, containment checks, atomic deduplication, bounded inputs and quarantine. Trigger text cannot change launch settings. |

Source anchors in `scripts/agentic_team.py` at the reviewed commit: `init_run` at 1728,
`complete_task` at 2499, `ingest_usage` at 2449, `fail_task` at 2656,
`recover_leases` at 2680, `agentic_home` at 2794, `VerifiedView` at 2888,
`advance_stage` at 3237, and `executable_release_problems` at 3604.
Resolve by function name after edits move line numbers.

## Durable contract

Keep event intake and readable status under `.agentic-team/supervisor/`. Authoritative
job records, attempt receipts, accounting reservations and frozen transcripts must be
owner-controlled; they can live under an owner-only supervisor directory outside the
checkout, with a nonsecret project identifier linking the two. Do not place writable
authority beside files the worker can freely edit. The bus digest is a view, never proof.

Use versioned records with stable event, job, run and attempt IDs. Persist effective
configuration when the job is accepted: project identity, source key, payload digest,
autonomy, entry mode, context method, adapter, executable, budget, retry limit, timeouts
and base commit. Later command-line defaults must not silently alter existing jobs.

Required records include an inbox event, a job, a launch intent, per-attempt start and
exit receipts, immutable completed transcript metadata, usage reconciliation state,
failure-recording state, and structured lifecycle events. Use atomic writes with bounded
Windows replacement retries, a cross-process lock, and a documented flush policy. State
records are authoritative; logs and `STATUS.md` are derived diagnostics. Recover a crash
between a committed state change and its log entry without executing the action again.

Proposed job states are `queued`, `starting`, `running`, `reconciling`, `retrying`,
`needs-human`, `done`, `failed`, and `cancelled`. Every transition records a reason and
its triggering attempt or owner action. `starting` and `reconciling` expose crash windows
that the original six-state design hides. Equivalent internal substates are acceptable
if their durable behavior is tested.

The transition sequence is:

1. Validate and atomically accept the event. Repeating an identical source key and payload
   is harmless; a conflicting payload is reported rather than silently replacing a job.
2. Acquire the checkout reservation, verify the base tree and policy, initialize or
   reconcile the existing run, and persist the attempt and budget reservation.
3. Launch a wrapper which claims that exact attempt once, writes a start receipt, and
   starts the worker only after ownership is established. Parent death at this boundary
   must not permit a second active attempt.
4. Observe completion, timeout, denial, or interruption. Preserve stdout and stderr
   separately. Terminate only a verified owned process tree when cancellation requires it.
5. Reconcile final usage by transcript digest and the runtime's existing `usage_sources`.
   A crash after successful ingestion must not charge again. Exit 3 from ingestion may
   still mean usage was durably saved; inspect state before deciding what happened.
6. Reconcile task failures and claims once, then choose done, retry, failure, or human hold.
   An owner approval alone cannot cure unknown cost or uncertain process ownership.
7. Regenerate the digest. Release checkout ownership only when its changes have an explicit
   disposition and no previous writer can still act.

All run-scoped calls use explicit project and run selection. Keep the current-run pointer
aligned while a worker owns the checkout because existing hooks also consult it. Detect
an unexpected pointer change; do not silently operate on another run.

## Phases and acceptance gates

| Phase | Work and primary files | Acceptance gate |
| --- | --- | --- |
| P0 Contract and regression baseline | Reconcile this plan with `docs/supervisor-design.md`; record decisions and initialize `docs/supervisor-progress.md`. Define schemas, transitions, exit codes, authority view, isolation and budget policy. | Every correction above has a named test and implementation phase; existing failures are distinguished from new ones. |
| P1 Runtime prerequisites | `scripts/agentic_team.py`, authority/orchestration/evidence tests and affected protocols. Fix missing authority-view fallback for modern runs, preserve legitimate decision visibility, and implement required budget admission checks. | Worker cannot self-approve or silently lose authority enforcement; missing views refuse safely; authentic owner decisions remain usable; exhausted budget prevents new work while reporting and recovery remain possible. |
| P2 Storage and intake | New `scripts/agentic_supervisor.py`, schemas if useful, `tests/test_supervisor.py`. Implement locking, durable job/config records, enqueue, quarantine, status and checkout reservation. | Concurrent enqueue and competing supervisors do not duplicate a job or claim the checkout twice. Malformed records cannot escape the store or block healthy intake. Crash during intake loses neither event nor ownership. |
| P3 Attempt lifecycle | Worker wrapper plus fake worker, attempt receipts, owned-process checks, timeout, cancellation and crash reconciliation. Keep any module split within installed helper packaging. | Kill/restart at each launch boundary never creates overlapping workers. Reused/unknown PIDs never cause an unrelated process to be killed. Restart works without the old Python process handle. |
| P4 Runtime orchestration and accounting | Real run initialization, briefs, worker prompts, metering, failure and lease reconciliation, backoff, owner resume/cancel, terminal classification. | Installed fake worker completes through `07_learn` with recorded usage. Missing usage, pending human gates, repeated failure and ambiguous ownership hold correctly. Approval resumes the correct job without granting new authority. |
| P5 Harness and packaging | Claude adapter, guard coverage, helper registration, installer/plugin tests, generated CLI reference and protocols. | Installed and packaged entrypoints work outside this source tree. Adapter argv/environment tests require no model calls. Unsupported budget/isolation capability refuses a paid launch with a clear explanation. |
| P6 Triggers and host operation | GitHub polling adapter, status diagnostics, retention, operator guide, Windows and POSIX launch examples, deterministic eval scenario. | Paginated issue input deduplicates across polls/repositories; network failures do not lose jobs. Host stop/start/reboot tests preserve ownership and resume from records. Offline lifecycle checks remain network-free. |
| P7 Independent review and release candidate | Full test matrix, fault injection, doc updates, changelog, delivery report and optional bounded pilot. | All acceptance cases below pass with evidence. Pilot, remote publication and host activation are separately reported according to actual authorization and execution. |

P0 through P4 are sequential. After P0, a read-only reviewer can build the acceptance
matrix, and Fable can draft the operator guide against the frozen contract. Keep one
integrator for `scripts/agentic_team.py`. P5 and P6 can proceed in parallel only after
P4's adapter/storage interfaces are stable and their file ownership does not overlap.

## Worker and budget policy

Use a fresh harness session per attempt while retaining the same AgenticTeam run. This
keeps each transcript attributable to one attempt and avoids accidentally re-metering a
conversation's cumulative history. Recovery context comes from the run's durable artifacts.

Require an explicit USD ceiling for the first paid Claude adapter, plus a finite turn
limit and wall-clock timeout. Token ceilings may tighten policy but cannot substitute for
a live token limit the adapter does not support. Reserve each attempt against the remaining
run allowance and a persisted supervisor aggregate allowance; a stream of individually
cheap jobs must not create unlimited total spending. The aggregate allowance is explicit,
does not reset on restart, and is replenished only by the owner.

Calculate remaining budget conservatively from the existing larger-of-reported-or-metered
rule and outstanding reservations. Unknown usage retains its reservation and holds the job.
No automatic budget waivers, retry extensions, new run IDs to evade a ceiling, or fabricated
metering records are allowed. A known-cost transient failure may retry with bounded backoff;
authentication errors, permission denials, safety refusals and repeated failures hold.

The adapter should use an argument vector and `shell=False`; prompt and issue text must
never become shell syntax. Inspect the installed CLI's help/version before relying on
flags, preserve installed hooks and deny rules, and restrict tools to the configured task.
Do not use permission-bypass flags or a startup mode that silently skips AgenticTeam hooks.
The permission baseline is the one `evals/live_smoke.py` already uses: the edit-accepting
permission mode plus an explicit tool allowlist (file tools, the agent and skill tools, and
Python invocations through the shell tool), extended per configuration with the project's
own build and test commands; the allowlist is part of the persisted job configuration.

Claude's current documentation describes `--max-budget-usd` as an estimated spend limit
that can overshoot, with subagent spending included; previous conversation totals are not
part of a resumed invocation's cap. Thus reservations need headroom and the actual cost
must still be reconciled. [Claude CLI reference](https://code.claude.com/docs/en/cli-reference)

Print mode loads project hooks by default; `--bare` skips discovery. Streaming output can
include the final result and session cost. Verify the actual transcript format against
fixtures captured from the supported CLI version. [Programmatic Claude usage](https://code.claude.com/docs/en/headless)

Native Windows lacks Claude's built-in shell sandbox, and that sandbox on supported systems
covers shell commands rather than every tool. The live pilot therefore needs a tested
whole-worker boundary, such as a suitably restricted account or container; merely selecting
WSL2 or removing an environment variable is insufficient. Keep host/container provisioning
outside the core Python service. [Claude sandbox scope](https://code.claude.com/docs/en/sandboxing)

## Owner controls and trigger policy

Proposed helper operations are `enqueue`, `serve`, `status`, `pause`, `resume`, `cancel`
and `poll-github`; these are future interfaces, not commands available at the review baseline.
Owner controls change supervisor scheduling only. Runtime approval, rejection, resolution,
waiver and reopening remain the runtime's authenticated human operations.

Define `serve --once` as one bounded reconciliation/intake/launch tick. A running process
survives through its wrapper and durable identity. Define `--until-idle` to wait for all
eligible queued, starting, running, reconciling and retrying work, including retry backoff.
Held jobs produce a final hold summary rather than an infinite wait. Forever mode handles
shutdown by stopping intake and applying its documented drain/cancel policy. Keep
0 = successful operation, 1 = operational failure, 2 = human attention, 3 = blocked,
and 64 = invalid usage; specify mixed-job precedence and expose full detail in JSON status.

The digest includes job/run/attempt IDs, source, stage, status, age, verified commit,
known usage, outstanding reservations, budget remaining, retry reason, checkpoint question,
and the exact next owner action. It must never print secrets or entire transcripts by default.

Poll only an owner-configured repository and opt-in label. Use a source identity including
host, repository and issue number; exclude PRs, handle pagination/rate limits, and retain
watermarks only after durable acceptance. Issue bodies are untrusted brief material,
including their acceptance lines. They cannot choose executable paths, budgets or permissions.
Entry mode is the owner's configured choice (see "Decisions fixed by this plan"): `idea`
pays for the product, architecture (with its independent review), and readiness stages on
every trigger; `execute-only` treats the brief as the plan. Record the choice in the job
configuration and never let trigger text select it.

Provide retention rules that preserve unfinished jobs, pending accounting and audit evidence.
Disk-full, malformed-state and schema-version errors must prevent new launches and explain
recovery. Generate host launch examples and test them in scratch environments. Registering
a persistent task, enabling paid execution, or posting notifications is a separate activation
step; generating a runbook does not claim those actions happened.

## Required acceptance cases

| Area | Cases that must be exercised |
| --- | --- |
| Event integrity | Duplicate event; same key with conflicting payload; concurrent enqueue; cross-repository issue number; traversal/absolute path/Windows reserved-name attempts; oversized and malformed event. |
| Store durability | Torn write; crash before/after inbox handoff; lock contention; schema mismatch; log-write failure after committed transition; disk full. |
| Launch recovery | Crash before spawn, after spawn before parent save, after start receipt, after exit receipt; stale PID and PID reuse; worker outliving parent; two supervisors on one checkout. |
| Checkout safety | Pre-existing dirty tree; unrelated active run; paused job with changes; max-workers greater than one; unexpected current-run pointer change; no destructive reset or cleanup. |
| Authority | Different owner/worker homes; unavailable verification view; fabricated approval in state; real approval/rejection visible; worker cannot read owner sentinel or mutate control records. |
| Metering | Valid result; malformed/truncated/missing result; nonfinite/negative cost fields; duplicate digest; crash after ingestion before job save; over-budget exit 3; completed run followed by final budget checkpoint. |
| Retry and leases | Recoverable known-cost crash; unknown-cost hold; repeated failure; required task exhausted while run remains active; no double-recorded failure; no lease release while old writer lives. |
| Human interaction | R2 release pause; R3/R4 action pause; owner approves/resolves then resumes; rejection stays blocked; exhausted task needs legitimate reopen; cancel stops only owned processes and preserves changes. |
| Evidence | Passing command with failing acceptance; stale HEAD; tracked/untracked source changed after verification; missing rollback rehearsal; missing learning/report artifact; zero process exit with incomplete run. |
| Packaging | Direct helper and installed alias; missing helper; plugin export; reinstall preserves supervisor state; uninstall/purge semantics documented and tested; Python 3.10 and Windows paths with spaces. |
| Operations | Once/idle/forever exit semantics; bounded backoff; host restart with detached worker; graceful shutdown; polling pagination/auth failure/rate limit; status without secrets. |

Milestone gating: the offline milestone requires the Event integrity cases through
"cross-repository issue number", every Launch recovery case except PID reuse, every
Authority case, the Metering cases through "duplicate digest" plus "over-budget exit 3",
every Retry and leases case, every Human interaction case, every Evidence case, the
Packaging cases through "plugin export", and the once/idle/forever and host-restart
Operations cases. The rest (traversal and reserved-name inputs, oversized events, torn
writes, lock contention, schema mismatch, log-write failure, disk full, PID reuse,
nonfinite cost fields, reinstall and uninstall semantics, Python 3.10 and spaces in paths,
backoff, graceful shutdown, polling pagination and rate limits, retention) is hardening:
required before the pilot is called operational, not before the offline milestone.

Use fake workers for every automated case. Include fake modes for success, known-cost crash,
missing usage, hang, human gate, repeated failure and malformed output. The fake worker drives
the installed CLI, creates real fixture commits and declared checks, records an independent
verification role, rehearses rollback, and finishes learning. It must not write runtime state
directly just to produce a green test. Dedicated tamper tests may deliberately corrupt fixtures.

For source integrity, require a clean relevant source tree at verification and finalization,
including untracked deliverable files; exclude only known runtime output paths. Existing
HEAD checks alone do not detect uncommitted edits. A legitimate source change after verification
requires checks and verification again. Local fixture/worker commits do not authorize a push.

## Verification and delivery

Canonical existing checks are:

```text
python scripts/agentic_team.py validate
python scripts/agentic_team.py docs --check
python -m unittest discover -s tests -v
python evals/run_scenarios.py
python scripts/preflight_skills.py
```

Also run the new focused supervisor tests, installed-helper/plugin tests, and installer
smokes. CI currently covers Windows, macOS and Ubuntu with Python 3.10, 3.12 and 3.14.
Record actual platform coverage; a local Windows pass is not proof of the full matrix.
Run the live smoke only with explicit budget authorization, after offline acceptance passes.

Repository gotchas that cost time before:

- Run the suite from the repository root; a `cd tests` in a shell tool call persists for
  later calls and makes `discover -s tests` fail. Unittest's verdict prints mid-stream when
  stdout is piped, so redirect the whole run to a file and grep `^(Ran |OK|FAILED)`.
- `tests/test_safety_net.py` regenerates golden snapshots with `UPDATE_GOLDEN=1`; any change
  to a golden-roster role (`ceo`, `fullstack-engineer`, `qa-lead`, `research-agent`,
  `sre-engineer`) needs it, and the diff is reviewed, not assumed.
- `python scripts/agentic_team.py docs --write` regenerates the CLI reference and the
  guarantee ledger after parser or `config/guarantees.json` changes; the command table near
  the top of `docs/cli.md` and the tree in `docs/architecture.md` are hand-written.
- `DocCliConsistencyTests` reads every `agentic_team.py <command>` phrase in the docs as an
  invocation; describe future commands in prose until they exist.
- Scenario JSON expands `PYTHON` to the running interpreter; the fake worker builds its
  check commands from `sys.executable` the same way, quoted, because `python3` on Windows
  may be the Store stub.
- Autonomous, supervised, and unattended runs need a spend ceiling: tests get it from
  `tests/helpers.fresh_project` (`policies.local.json`) or `init-run --budget`.
- Windows: stdin redirected to NUL reports `isatty()`; never prompt without the real-console
  check. Shell heredocs mangle backslashes; write files with a file tool.

Register every shipped module through the existing helper copy/package mechanisms. Update
`SCRIPT_REFS`, `HELPER_SCRIPTS` and `HELPER_COMMANDS` as appropriate; generated top-level help
alone will not document nested helper options. Keep future-interface prose from being parsed
as an invocation of a command that does not exist yet; do not weaken documentation checks.

At each phase, update `docs/supervisor-progress.md` with status, branch/commit, changed files,
test results, remaining blockers and the exact next step. Keep planned, implemented,
offline-verified, pilot-verified and activated states distinct. The final delivery includes
source, tests, docs, operator examples, an independent review, and truthful remaining limits.

### Review session results

- Local source validation: passed, 50 agents, 9 presets, 13 harnesses.
- Generated documentation check: passed.
- Deterministic scenarios: 7 of 7 passed.
- Preflight: passed; optional `design-architect` integration is absent.
- Full unit suite on Windows / Python 3.14.5: 199 passed, 1 failed; 200 tests in
  123.814 seconds. The sole failure was `DocCliConsistencyTests`: the draft design at
  line 73 presented the proposed `supervise` helper as an existing command. The runtime
  tests passed. Resolved on 2026-10-29 by rewording the design; the safety-net module
  and the generated-docs check pass again. The check was not weakened.
- No paid worker, live smoke, remote push, merge, deployment or host service activation
  was performed for this planning task.
