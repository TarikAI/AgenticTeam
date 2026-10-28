# Supervisor design (not yet implemented)

Status: design only, 2026-10-28. Nothing in this document exists in the code yet. It describes
the one layer AgenticTeam still lacks for unattended operation: a durable service that turns
triggers into runs, keeps workers alive, recovers from their failures, and reports to the owner.

## 1. Why

The CLI (`scripts/agentic_team.py`) is a deterministic state machine: tasks, leases, evidence,
gates, budgets, a signed decision ledger. Every command is one-shot, and nothing in the
repository invokes it on its own. `recover-leases` returns abandoned claims only when something
runs it; `usage --transcript` meters a session only when the owner side calls it; the
`unattended` profile lets a low-risk run leave the release stage without a click, but only if a
worker drives it there.

The supervisor is that something. It is deliberately small, dependency-free Python like the other
helpers in `scripts/`, keeps all of its state as files under the project's bus, and treats one
harness session as one worker. It does not replace a workflow engine; it is the minimum that
makes "issue in, verified change out" run without a prompt, and it is the seam where a managed
platform (Mission Control, Temporal, a cloud agent runtime) can later take over the loop.

## 2. Boundaries that must hold

- **Owner side.** The supervisor runs as the human's process: it holds `AGENTIC_TEAM_HOME`,
  issues runs, meters transcripts, and may read owner tokens. A worker is started without that
  variable and without any path to the tokens, so a worker can neither approve the gates that
  block it nor meter itself. This is the same split the live smoke eval already uses.
- **One worker per checkout.** Two sessions editing one working tree overwrite each other. The
  default worker cap is one per project; parallelism means several supervisors over several
  checkouts (or, later, one supervisor that provisions a worktree per job).
- **No new authority.** The supervisor adds no gate, waives nothing, and never calls `approve`,
  `reject`, `resolve`, or `waive`. A run that reaches a human checkpoint stays there, and the
  digest says so. R3/R4 actions keep their human checkpoints in every profile (guarantee G16).
- **Spend is capped before a worker starts.** Every run the supervisor creates carries a per-run
  ceiling (`init-run --budget`), and each finished session is metered from its transcript, so the
  ceiling counts what the harness reported, not what the agent claimed (guarantee G19).

## 3. Files

Everything lives under `.agentic-team/supervisor/` in the project. The CLI's guard hook should
deny agent writes to this folder the same way it protects `runs/*/state.json`.

| Path | Holds | Written by |
|---|---|---|
| `inbox/<event-id>.json` | one trigger waiting to become a run | `enqueue`, `poll-github`, any adapter |
| `jobs/<event-id>.json` | the job record: event, status, attempts, run id, worker pid, transcript path, notes | the tick |
| `transcripts/<event-id>-<attempt>.jsonl` | the worker's harness output for one attempt (stdout), plus a `.stderr` file | the worker process, via the supervisor's file handles |
| `log.jsonl` | append-only supervisor events (`enqueued`, `job-queued`, `run-initialized`, `worker-started`, `worker-exited`, `job-retrying`, `job-needs-human`, `job-done`, `job-failed`) | the tick |
| `STATUS.md` | the owner digest, regenerated every tick | the tick |

A job has one of six statuses: `queued`, `running`, `retrying`, `needs-human`, `done`, `failed`.
Status moves only inside a tick, and every move is logged, so the log replays the history.

### Event schema

```json
{
  "id": "gh-issue-42",
  "kind": "issue",
  "title": "Date parser drops the timezone",
  "brief": "Steps to reproduce ...",
  "acceptance": ["AC-1: parse_date keeps the offset", "AC-2: the regression test passes"],
  "source": {"repo": "owner/name", "number": 42, "url": "https://github.com/owner/name/issues/42"},
  "created_at": "2026-10-28T09:00:00Z"
}
```

`kind` is one of `issue`, `alert`, `schedule`, `manual`. The id is the idempotency key: an event
whose id already exists in the inbox or in `jobs/` is skipped, so a poller can run every minute.

## 4. Commands

All take `--project` (an installed project). Once the helper is registered the way
`findings-to-tasks` is, the bus CLI exposes them under a `supervise` subcommand; until then no
such command exists.

| Command | Does |
|---|---|
| `enqueue --kind K --title T (--brief TEXT \| --brief-file F) [--acceptance "AC-1: ..."]... [--id ID]` | Writes one inbox event. |
| `poll-github --repo owner/name [--label L] [--state open]` | Lists matching issues through the `gh` CLI and enqueues each unknown one as `gh-issue-<n>`; lines of the body containing an `AC-` id become the acceptance list. Pure parsing lives in its own function so it is unit-tested without the network. |
| `serve [--once \| --interval SECONDS \| --until-idle]` | Runs ticks. `--once` is one tick, for cron or a scheduled task; `--until-idle` keeps ticking until no job is running and the inbox is empty, then exits; `--interval` loops forever. |
| `status` | Prints the digest. |

`serve` options, fixed for the life of the process: `--autonomy` (default `unattended`),
`--budget usd=N[,tokens=N]` (default a small USD ceiling; a run cannot start without one),
`--entry` (default `execute-only`), `--context`, `--max-workers` (default 1), `--retries`
(default 2 worker relaunches per job), and how to start a worker: either the Claude Code headless
session the supervisor builds itself (`--max-turns`, `--model`), or a user-supplied command
template (`--worker-arg` repeated; `{project}`, `{run}`, `{run_dir}`, and `{brief}` are
substituted), which is also how the tests inject a scripted worker.

Exit codes: 0; 1 on error; 2 from `serve --once` and `status` when any job waits for a human, so
a cron job can mail the owner on a non-zero exit.

## 5. The tick

Each tick is idempotent and reads everything it needs from disk, so a restarted supervisor (or a
cron tick with no memory of the last one) behaves the same as a long-running one. Only the
process handles of workers it started itself live in memory.

1. **Reconcile running jobs.** For each job in `running`:
   - If the supervisor holds the process handle, poll it; otherwise test the recorded pid for
     liveness (a reused pid can fool this test; the run state below settles it). Alive: run
     `recover-leases` for the job's run and move on.
   - Exited: record the exit code when known. Meter the attempt's transcript with the owner
     token (`usage --transcript`, attributed to the run). A transcript with no result message
     is logged, not fatal. If the ceiling refuses (the run crossed its budget), the job becomes
     `needs-human` with that note, because the ceiling will refuse the next command anyway.
   - Read the run state. `complete` → `done`. `waiting-human` or any `blocked-*` status →
     `needs-human`, with the pending checkpoint's question in the note. Otherwise the worker
     stopped before finishing: every task it still holds gets a recorded failure through
     `fail` with a stable reason (so the runtime's repeated-failure rule applies), and the job
     becomes `retrying` if attempts remain, else `failed`.
2. **Relaunch.** Each `retrying` job with capacity available is relaunched on the same run (the
   run keeps its evidence and its ceiling; only the worker process is new).
3. **Intake.** Inbox events move into `jobs/` as `queued`, oldest first, and their inbox files
   are deleted.
4. **Launch.** While running workers are below the cap: take the oldest `queued` job, create its
   run (`init-run` with the configured profile, entry, context, and ceiling; run id derived from
   the event id), write `BRIEF.md` in the run from the event (title, trigger, source, brief,
   acceptance lines with `AC-` ids), start the worker with its stdout and stderr redirected to
   the attempt's transcript files, and record pid, attempt, and start time.
5. **Digest.** Rewrite `STATUS.md`: counts per status; one line per job with id, kind, title,
   status, attempts, run stage and status, metered USD, and the note; the pending checkpoint
   question for every `needs-human` job; the path of each run folder.

The worker prompt tells the session which run it drives, where its brief is, that work is
recorded through the installed CLI with declared checks, that verification is independent and at
the current HEAD, that it continues through release as the profile allows (rehearsing the
rollback as a `rollback-test` task under `unattended`), and that it must stop at any human
checkpoint. The prompt grants nothing the policy does not.

## 6. What "done" means for the first implementation

- The helper exists in `scripts/`, is copied into `.agentic-team/bin/` on install, and is
  registered as the `supervise` subcommand (`HELPER_SCRIPTS`, `HELPER_COMMANDS`, `SCRIPT_REFS`).
- A scripted fake worker under `tests/` drives the installed CLI exactly as an agent would:
  adds a build task with a check, claims it, completes it, advances to verify, writes
  `VERIFICATION.md`, and under `unattended` writes `RELEASE.md`, rehearses the rollback, and
  advances to completion. It prints one harness-style result line so metering has something to
  read, and it records whether it could see the owner's home variable (it must not). A mode
  file in the project switches it between a clean finish, a crash after claiming, and stopping
  at the release checkpoint.
- Tests cover: enqueue and idempotent ids; a full tick → wait → tick cycle that ends `done` with
  metered usage and a complete run; a crash that is retried once, with the abandoned claim
  released and the second attempt finishing; an `autonomous` run that ends `needs-human` and
  makes `serve --once` exit 2; a fresh supervisor object reconciling a job started by another
  (restart durability); GitHub issue parsing into events; and the worker environment check.
- `validate`, the unit suite, the scenarios, and `docs --check` pass; the CLI reference and the
  architecture tree list the new helper; the changelog has a dated entry.

## 7. Known limits of this version

- No isolation: the worker edits the project checkout directly. Containers or per-job worktrees
  are the next step and change nothing in the tick's contract.
- No inbound webhooks: adapters poll (GitHub) or drop files (alerts, schedules). A small
  receiver that writes inbox files is a separate, optional piece.
- Pid liveness is a heuristic; the run state is the source of truth.
- The harness's cost figures are its client-side estimate, as the budgets protocol already says.
- The supervisor itself must be kept alive by the host: cron, a systemd unit, or Windows Task
  Scheduler calling `serve --once` (or `--until-idle`) on a schedule is the simplest durable form.
