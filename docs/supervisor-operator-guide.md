# Supervisor operator guide

The supervisor turns triggers (a manual request, a labelled GitHub issue, a dropped alert file)
into AgenticTeam runs, starts one worker at a time per checkout, and after every attempt decides
from the run's verified state whether the job is done, should retry, or needs you. It is an
owner-side process: it holds your owner home, meters what the harness reported, and audits the
decision ledger. It never approves, rejects, resolves, waives, or reopens anything.

**Status (2026-10-29): implemented and offline-verified** with scripted fake workers (no model
calls). It is **not pilot-verified** (no paid worker has run under it) and **not activated** (no
host task is registered). The contract it implements is in
[supervisor-progress.md](supervisor-progress.md); the design intent is in
[supervisor-design.md](supervisor-design.md).

## 1. Set it up

Install AgenticTeam in the project as usual, commit the project so the tree is clean, and ignore
runtime output so the supervisor's cleanliness check sees only source:

```text
.agentic-team/runs/
.agentic-team/CURRENT.md
.agentic-team/supervisor/
```

Every command below runs in **your own terminal**, as the owner, with the `AGENTIC_TEAM_HOME`
your runs use (the guard hook refuses `supervise` from an agent). The first command, run once on
a freshly installed checkout no worker has touched yet, copies the runtime and the supervisor into
the owner store (the **owner copy**), outside the checkout a worker can write, and prints its path;
`<owner copy>` below means `python "<that path>"`. Run every later owner command from that copy:
the checkout's `.agentic-team/bin/` is code a worker can edit. Work that uses your token or
credentials (`serve`, `resume`, `poll-github`, `verify-isolation`) runs only from the owner copy;
the copy inside the checkout refuses it (exit 3) and prints the command to use. `owner-copy
--refresh` copies again after you upgrade AgenticTeam. Configure once; every job freezes the
configuration it was accepted under, so later changes affect only new jobs (`resume
--refresh-config` re-freezes one held job on purpose):

```powershell
python .agentic-team/bin/agentic_team.py supervise owner-copy --project .
<owner copy> configure --project . --autonomy unattended --entry execute-only --budget usd=5 --attempt-usd 1
<owner copy> allowance --project . --add-usd 20 --reason "October pilot"
```

**One checkout, one store.** The first owner store that runs in a checkout binds it: the binding
(`.agentic-team/supervisor/binding.json`, inside the checkout so every spelling of its path reaches
it) names that store's identity. Any other store, whether chosen with `--store`, reached through a
different `AGENTIC_TEAM_HOME`, or opened through a symlink or junction, refuses with exit 3 and
starts no worker; a store whose own record names another project refuses as well. Moving to a new
store is explicit: run `bind --reason "..."` from the new store's owner copy. It is refused while the
bound store has any unfinished job, open reservation, checkout holder, orphan, or unreadable record;
if that store was deleted, `--old-store-missing` accepts losing its records. A store created before
binding existed binds the checkout the first time it runs.

| Setting | Meaning | Default |
|---|---|---|
| `--autonomy` | profile of every run (`unattended` lets R0–R1 runs leave release without a click) | `unattended` |
| `--entry` | `execute-only` treats the brief as the plan; `idea` pays for product, architecture with its independent review, and readiness on every trigger | `execute-only` |
| `--budget usd=N` | each run's ceiling (`init-run --budget`); required | none |
| `--attempt-usd N` | what one worker attempt reserves before it starts; required | none |
| `--headroom` | the Claude adapter passes `--max-budget-usd` = reservation ÷ headroom, because the harness limit is an estimate that can overshoot | 1.25 |
| `--retries N` | worker relaunches per job after the worker stopped early | 2 |
| `--timeout S` | wall-clock limit per attempt; the wrapper ends the worker's whole process tree | 3600 |
| `--max-workers` | must be 1: one writer per checkout | 1 |
| aggregate allowance | `allowance --add-usd`: the total every job together may spend; it never resets on its own | 0 (nothing launches) |

## 2. Queue work

```powershell
<owner copy> enqueue --project . --title "Date parser drops the timezone" --brief-file issue.md --acceptance "AC-1: parse_date keeps the offset"
```

The id is the idempotency key: the same id and payload again is a harmless duplicate; the same
source with a different payload is reported and never replaces the job. A source whose job was
cancelled or failed runs again only when you say so: `enqueue ... --requeue` creates a new job id. Any adapter may also drop
a JSON event into `.agentic-team/supervisor/inbox/`; a malformed, oversized, or conflicting file is
moved to `quarantine/` with a `.reason` file and never blocks the others.

**GitHub issues.** Only the repository and opt-in label you configure are polled, through the
`gh` CLI you are logged into:

```powershell
<owner copy> configure --project . --github-repo acme/app --github-label agentic
<owner copy> poll-github --project .
```

Pull requests are skipped; each issue becomes `gh-<repo>-<number>-<hash>` keyed by host,
repository, and number; lines with an `AC-` id become the acceptance list. The issue text is
untrusted brief material: it is written into the run's `BRIEF.md` under an untrusted-data banner
and can never choose a budget, a permission, a path, or a command. The watermark advances only
after every fetched issue was durably accepted; a rate limit (exit 3) or an authentication error
(exit 1) accepts nothing and leaves it alone, and so does any failure to accept an issue (a busy or
full store): an issue that was not accepted is never skipped by the next poll. An issue edited after acceptance is reported as a
conflict; queue it again under a new id if the change matters. Each source keeps its own watermark,
keyed by host, repository (both case-insensitive), and label: changing any of them polls the new
source from the beginning instead of sending another source's `since`, and switching back resumes
the original cursor. A watermark file from before keyed cursors is not reused (a full poll is
harmless, because intake is idempotent).

**Requeue.** `enqueue --requeue` records the new job id in the source index only after the
previous job's record holds everything needed to recreate the event, then writes the event. If the
supervisor is interrupted between those writes, the next `enqueue` or tick recreates the waiting
event, so the id a requeue or duplicate reports is always a real or recoverable job, and a retry
never creates a second one.

## 3. Run it

| Command | Does | Exit |
|---|---|---|
| `<owner copy> serve --once` | one tick: reconcile attempts, take in events, launch at most one worker, write the digest | 0 ok · 1 error · 2 a job needs you · 3 blocked |
| `<owner copy> serve --until-idle [--max-seconds N]` | ticks until nothing is starting, running, reconciling, launchable, or waiting out a retry backoff | same |
| `<owner copy> serve --interval 60` | ticks forever; Ctrl+C stops intake and exits, leaving running workers with their wrappers | 0 |
| `<owner copy> status [--json]` | the digest; also written to `.agentic-team/supervisor/STATUS.md` | same as the last tick |

When several conditions hold, the exit code follows 1 > 3 > 2 > 0. A failed job (retries exhausted,
or a run that stopped short with no retry left) counts as "a job needs you" (2) until you
acknowledge it: `<owner copy> acknowledge --job J --reason "..."` keeps the job `failed` in the
history and records your reason, after which it no longer affects the exit code; a later successful
job never hides an unacknowledged failure. `enqueue --requeue` of a failed job's source records the
acknowledgement for you ("requeued as J-r2"). A cron job can mail you on any non-zero exit. A worker outlives the tick that launched it (its wrapper is detached), so the
simplest durable host form is `serve --once` on a schedule, run from the owner copy. Print a
ready example with absolute paths; printing it registers nothing, and registering it is your step:

```powershell
<owner copy> host-example --project . --platform windows
<owner copy> host-example --project . --platform systemd
<owner copy> host-example --project . --platform cron
```

Overlapping ticks wait for the store lock, so a slow tick never starts a second worker.

## 4. When a job needs you

`status` lists every held job with the reason and the exact next commands. Every generated
command runs the **owner copy** by absolute path (`<owner store>/bin/agentic_team.py` for the
runtime's human operations, `<owner store>/bin/agentic_supervisor.py` for the supervisor), never
the checkout's `.agentic-team/bin/`, which a worker can edit. Each one carries its context
explicitly: `AGENTIC_TEAM_HOME`, `--project`, and `--run` (runtime) or `--store` (supervisor), plus
`--by <owner name> --token-file <your token file>` for a human decision, so it does the same thing
from any directory. `status --json` gives each job's `next_commands` for both shells, quoted for
paths with spaces; `next_action` and `STATUS.md` show the form for this host's shell. For example,
in PowerShell (Bash gets `AGENTIC_TEAM_HOME='...' '<python>' ...`):

```powershell
$env:AGENTIC_TEAM_HOME = 'C:\Users\me\.agentic-team'; & C:\Python314\python.exe 'C:\Users\me\.agentic-team\supervisor\app-1a2b\bin\agentic_team.py' approve --checkpoint CP-001 --decision '...' --project 'C:\work\my app' --run sup-fix-1 --by Owner --token-file 'C:\Users\me\.agentic-team\owner-tokens\sup-fix-1.<uid>.token'
```

Approvals stay the runtime's authenticated human operations; `resume` then revalidates the hold and
relaunches only if it cleared. Below, `<rt>` and `<sup>` stand for those two owner-copy commands
with their context.

| Hold | What happened | What you do |
|---|---|---|
| `checkpoint` | the run waits for a human decision: an R2+ release, an R3/R4 action, a deviation, a budget warning, or a rejection | `<rt> approve --checkpoint CP-00N --decision "..."` (or `reject`; after a rejection, correct the work and `resolve`), then `<sup> resume --job J` |
| `evidence` | the run says `complete`, but the owner-side re-check disagrees: the event log does not show the run reaching 07_learn and completing, or the verification, release (including the executable release conditions when no human approved it), or learning exit contract fails as you see it | inspect the run folder and its event log; a worker can write `state.json`, so a status field proves nothing on its own |
| `failed-task` | a task failed the same way twice or ran out of retries | `<rt> reopen --task T --reason "new approach" --extend-retries 1`, then resume |
| `unknown-usage` | the attempt's cost cannot be settled: no readable cost (killed, timed out, malformed output), no numeric `total_cost_usd`, or a usage record in the run state that the signed owner ledger does not confirm; its reservation stays counted | `<sup> resume --job J --usage-transcript FILE` to meter a recovered transcript, or `--charge-reservation` to count the whole reservation as spent |
| `failure-record` | the ended attempt still held tasks and the runtime refused to record their `fail` three ticks in a row (the reason says which and why); nothing relaunches while a claim is unaccounted for | fix what the runtime reports, then `<sup> resume --job J`, which records the failures first and refuses while any claim is still open |
| `ownership` | a wrapper or worker cannot be shown to have stopped (stale heartbeat, a worker outliving its wrapper, an unreadable process identity) | check the processes yourself, then `<sup> resume --job J --confirm-stopped`; it refuses while a process is provably still the attempt's |
| `budget` | the run's remaining allowance is below one attempt, or an attempt took the run past its ceiling | review; `<rt> waive --requirement budget:usd --reason "..."` lifts the run's ceiling (the aggregate allowance still applies), then resume |
| `tamper` | `audit verify` failed (an unsigned ledger record, a state approval with no signature) or the exported view changed during the attempt | investigate before anything else; resume only re-runs the audit |
| `source` | the run completed but the tree has uncommitted changes, or HEAD moved past the verified commit with source changes | inspect `git status` and `git log`; the supervisor never resets or cleans; restore the verified tree, then resume |
| `pointer` | `CURRENT.md` names another run | `<rt> switch-run --run sup-<job>`, then resume |
| `config`, `adapter` | the configuration cannot launch (no budget, no current isolation proof for paid workers, a worker command that does not start, a harness login failure), or the launch failed before any worker started | fix it with `<sup> configure ...`, then `<sup> resume --job J --refresh-config` |

Two more conditions block every launch (exit 3) rather than holding one job:

- **Orphan-recovery hold.** A job record that is missing, moved aside, or torn never releases what
  `control.json` holds for it: its reservations stay counted and, if it held the checkout, the
  checkout stays reserved, because its attempt may have spent money and its worker may still be
  writing. The blocker lists what is held and which attempts have no exit receipt. Restore the
  record and serve again (the job is then reconciled normally, including metering), or run
  `<sup> recover-orphan --job J --disposition "..."`: it refuses while an attempt's process is
  provably the attempt's and still running, asks for `--confirm-stopped` when that cannot be shown,
  charges every reservation the orphan held in full (uncertain spend is never refunded), and
  releases the checkout with your disposition. The orphan's run stays the checkout's current run;
  the next job launches only after you close it (`<rt> close-run --reason "..."`), because the
  supervisor never closes a run itself.
- **Checkout bound to another store** (section 1).

`<owner copy> pause --job J` (or `--all`) stops launching; a running attempt finishes first.
`<owner copy> cancel --job J --reason "..."` asks the attempt's wrapper to end its own worker tree;
nothing else is ever signalled, and every change in the tree is kept. While an attempt is not yet
reconciled (including one held because its processes cannot be shown to have stopped), the job
stays as it is and keeps the checkout; it becomes `cancelled` only after a tick reconciles that
attempt, and `release` refuses until then. A job that leaves uncommitted changes keeps the
checkout reserved until you deal with them and run
`<owner copy> release --job J --disposition "kept on branch x"`. An attempt whose cost stayed unknown
can still be settled on a finished job with `resume --job J --charge-reservation`.

## 5. Money

Before each attempt the supervisor reserves `--attempt-usd` against both the run's remaining
allowance (its ceiling minus the larger of reported and metered usage, minus open reservations)
and the aggregate allowance. After the attempt it meters the frozen transcript exactly once (by
digest, so a crash and restart never charges twice) and replaces the reservation with the real
figure. Unknown cost keeps the reservation and holds the job: nothing is ever recorded as free.

What counts as a cost: every adapter is bounded in USD, so the result line must report
`total_cost_usd` as a JSON number. A missing, `null`, string, boolean, negative, or non-finite
value is unknown, even when token counts are present; a numeric `0` is a genuine zero and settles at
zero. The figure that settles an attempt comes from the owner ledger, not from the run state a
worker can write: the run's usage record for the transcript must match a usage record in the
ledger signed with your token (same source id, transcript digest, USD and tokens, also equal to
what the transcript says), and the run's metered totals must equal the signed cumulative sum. A
supervisor that crashed after metering finds that signed record and settles without metering
twice; an edited or forged projection holds as `unknown-usage`.
The runtime refuses `claim` and `exec` once a run's ceiling is spent, so a worker cannot start new
work past it. All figures are the harness's client-side estimate.

## 6. Restart and recovery

Everything is on disk, so a restarted supervisor, a reboot, or a cron tick with no memory behaves
the same as a long-running one. Each attempt is recorded (with its reservation) before its wrapper
starts; exactly one wrapper can claim it; a late wrapper finds the attempt abandoned and starts
nothing. A wrapper that died without its exit receipt is a lost attempt when both it and its worker
are provably gone (process ID plus process start time), and a hold when that cannot be shown. A
task the ended attempt still held gets one `fail` with the signature `supervisor-attempt-ended`,
so the runtime's repeated-failure rule applies; leases are never recovered while the old writer
might act. Each recorded failure is saved as it is recorded, and reconciliation counts as complete
only when the run state, read again, shows no claimed task left: a `fail` the runtime refuses
leaves the job reconciling (retried next tick, never relaunched), and after three refusals it holds
as `failure-record`; a replay never records a failure twice. On Windows the worker runs in a job object that ends with its wrapper.

Records live in the owner store, printed at the bottom of `status`
(`<AGENTIC_TEAM_HOME>/supervisor/<project>-<hash>/`): `config.json`, `control.json` (checkout,
pause, aggregate allowance and reservations), `jobs/`, `attempts/<job>/<attempt>/` (intent, claim,
start and exit receipts, heartbeat, transcript, stderr), `bin/` (the owner copy), `view/`,
`worker-home/`, `log.jsonl`. The store lock is an operating-system file lock, released when its
holder dies, so a crashed tick never leaves a lock to break. An unreadable record or an unknown
schema stops launches and names the file; a full disk stops launches and says so. Neither loses
queued work, and spend already recorded stays counted even if you move a broken record aside; a
reservation or checkout claim of a missing record becomes the orphan-recovery hold (section 4).

The tree counts as clean only when `git diff HEAD` is empty, no file is flagged skip-worktree or
assume-unchanged, and no untracked file exists outside the committed `.gitignore` files
(`.git/info/exclude` and global excludes are not honored); runtime output (`.agentic-team/runs/`,
`supervisor/`, `knowledge/`, `CURRENT.md`, `backup/`) is excluded. A tree git cannot read is never
treated as clean.

## 7. Isolation and paid workers

A worker gets an empty `AGENTIC_TEAM_HOME` and reads your decisions through the exported
verification view (`AGENTIC_TEAM_VIEW`), never through its own home; without the view the CLI
refuses its gated commands. Those gates run inside the worker's own process, so a worker that can
run arbitrary commands could point the CLI at a view it wrote itself or edit `state.json`. They are
defense in depth. The check that holds is yours: after every attempt the supervisor runs
`audit verify` with your token, which replays every stage exit through a human gate, every claim
of a task that needed a risk approval, and every waiver against the signed ledger in your home,
and holds the job as `tamper` on any step without a signature. Keep production credentials out of
the worker's reach, so an R3/R4 action cannot succeed even before that audit.
Unrelated credentials (`GH_*`, `AWS_*`, `*SECRET*`, …) are filtered from its environment. None of
that stops a process of the same OS user from reading your files, so the Claude adapter refuses to
launch until a boundary is verified:

```powershell
<owner copy> configure --project . --adapter claude --isolation-prefix-json "[\"wsl\", \"-u\", \"agentic-worker\", \"--\"]" --view-dir <worker-readable dir> --worker-home <worker-writable dir>
<owner copy> verify-isolation --project .
```

`verify-isolation` writes a harmless sentinel into the owner store and runs a probe through the
prefix, with the same filtered environment a worker gets; the boundary passes only if the probe
cannot read the sentinel and cannot write into the view directory. The proof is bound to the whole
effective boundary: the owner store and `AGENTIC_TEAM_HOME`, the view directory, the worker home,
the prefix and the Python inside it, the Claude executable, the environment passthrough list, and
the interpreter that runs the supervisor (all as canonical paths). Changing any of them with
`configure` clears the proof, and a launch from another owner home or interpreter finds none. A
job freezes the proof with its configuration; when the store's current proof no longer matches it,
the job holds as `config` until you verify the current configuration and resume it with
`--refresh-config`. A proof recorded before this binding existed counts as unverified, so verify
once after upgrading. These are offline checks with a probe; they do not prove a real OS boundary
beyond what the probe observed. The adapter inspects `claude --help` before every launch and refuses if
`--print`, `--output-format`, `--max-budget-usd`, `--permission-mode`, or `--allowedTools` is
missing. Claude Code 2.1.310 does not advertise `--max-turns`; the adapter then refuses unless you
accept the wall-clock timeout and the budget cap as the only live bounds with
`--turn-limit timeout-only`. The worker runs in print mode with `stream-json` output, the
edit-accepting permission mode, and the tool allowlist the live smoke uses plus what you add with
`--allow-tool`; project hooks stay on (no `--bare`, no permission bypass).

**Pilot setup (not yet run).** One project with a clean tree and a fixture issue; a verified
boundary (a restricted local account or a container with the view mounted read-only); the
installed Claude CLI version recorded; `--budget usd=5`, `--attempt-usd 2`, an aggregate allowance
of 10; `--timeout 1800`; `--turn-limit timeout-only` unless the CLI advertises `--max-turns`;
`serve --until-idle --max-seconds 3600`; stop conditions: any hold, any exit other than 0, or the
allowance spent. It needs your explicit authorization for the spend.

## 8. The command adapter

`--adapter command --worker-command-json '[...]'` runs an argv you supply instead of Claude Code
(`{python}`, `{project}`, `{run}`, `{run_dir}`, `{brief}`, `{attempt}`, `{job}` are substituted
per argument; nothing passes through a shell). The tests and the eval scenario use it with a
scripted worker. Its cost is whatever its output's `result` line reports, it is not isolated, and
the digest's Worker column says so for every job; do not point it at a paid harness to avoid the
isolation check.

## 9. Upgrade, retention, uninstall

Reinstalling AgenticTeam keeps `.agentic-team/supervisor/` and the owner store. `uninstall`
keeps `supervisor/` with `knowledge/` and `runs/`; `uninstall --purge` removes the project's
files only, never the owner store, which you delete yourself when you are done with it.
`<owner copy> prune --older-than-days 30 [--dry-run]` deletes transcripts of finished jobs whose
cost was accounted; it never touches unfinished jobs, unknown-cost attempts, job records, or
receipts.

## 10. Known limits

- One checkout, one worker; parallelism means more checkouts, which this version does not provision.
- No webhooks: GitHub is polled; other sources drop files.
- Process identity uses the process start time on Windows and Linux (and `ps` elsewhere); where
  it cannot be read, the supervisor holds and asks you rather than guessing.
- The view and the owner store are protected only by the boundary you provide; on the same OS
  user, `audit verify` and the view digests detect tampering after the fact.
- Cost figures are the harness's estimate, and the harness's own spend limit can overshoot.
- Owner controls carry no separate credential: anything that can write the owner store can change
  the allowance or resume a job, which is why the store must sit behind the isolation boundary.
- A worker's gates are defense in depth (above); forgery is found by your audit after the attempt.
- The checkout binding lives in the checkout so that every path alias finds it; it guards against a
  second owner store by mistake, not against a worker that deletes it (another store could then bind
  the checkout only when the owner runs one).
