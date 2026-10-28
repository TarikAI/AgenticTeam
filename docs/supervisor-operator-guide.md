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
your runs use (the guard hook refuses `supervise` from an agent). The first command copies the
runtime and the supervisor into the owner store (the **owner copy**), outside the checkout a
worker can write. Work that uses your token or credentials (`serve`, `resume`, `poll-github`,
`verify-isolation`) runs only from that copy; the copy inside the checkout refuses it (exit 3) and
prints the command to use. `supervise owner-copy` prints the path, and `owner-copy --refresh`
copies again after you upgrade AgenticTeam. Configure once; every job freezes the configuration
it was accepted under, so later changes affect only new jobs (`resume --refresh-config` re-freezes
one held job on purpose):

```powershell
python .agentic-team/bin/agentic_team.py supervise configure --project . --autonomy unattended --entry execute-only --budget usd=5 --attempt-usd 1
python .agentic-team/bin/agentic_team.py supervise allowance --project . --add-usd 20 --reason "October pilot"
```

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
python .agentic-team/bin/agentic_team.py supervise enqueue --project . --title "Date parser drops the timezone" --brief-file issue.md --acceptance "AC-1: parse_date keeps the offset"
```

The id is the idempotency key: the same id and payload again is a harmless duplicate; the same
source with a different payload is reported and never replaces the job. A source whose job was
cancelled or failed runs again only when you say so: `enqueue ... --requeue` creates a new job id. Any adapter may also drop
a JSON event into `.agentic-team/supervisor/inbox/`; a malformed, oversized, or conflicting file is
moved to `quarantine/` with a `.reason` file and never blocks the others.

**GitHub issues.** Only the repository and opt-in label you configure are polled, through the
`gh` CLI you are logged into:

```powershell
python .agentic-team/bin/agentic_team.py supervise configure --project . --github-repo acme/app --github-label agentic
python "<owner copy>" poll-github --project .          # <owner copy>: the path `supervise owner-copy` prints
```

Pull requests are skipped; each issue becomes `gh-<repo>-<number>-<hash>` keyed by host,
repository, and number; lines with an `AC-` id become the acceptance list. The issue text is
untrusted brief material: it is written into the run's `BRIEF.md` under an untrusted-data banner
and can never choose a budget, a permission, a path, or a command. The watermark advances only
after every fetched issue was durably accepted; a rate limit (exit 3) or an authentication error
(exit 1) accepts nothing and leaves it alone, and so does any failure to accept an issue (a busy or
full store): an issue that was not accepted is never skipped by the next poll. An issue edited after acceptance is reported as a
conflict; queue it again under a new id if the change matters.

## 3. Run it

| Command | Does | Exit |
|---|---|---|
| `<owner copy> serve --once` | one tick: reconcile attempts, take in events, launch at most one worker, write the digest | 0 ok · 1 error · 2 a job needs you · 3 blocked |
| `<owner copy> serve --until-idle [--max-seconds N]` | ticks until nothing is starting, running, reconciling, launchable, or waiting out a retry backoff | same |
| `<owner copy> serve --interval 60` | ticks forever; Ctrl+C stops intake and exits, leaving running workers with their wrappers | 0 |
| `supervise status [--json]` | the digest; also written to `.agentic-team/supervisor/STATUS.md` | same as the last tick |

When several conditions hold, the exit code follows 1 > 3 > 2 > 0. A cron job can mail you on any
non-zero exit. A worker outlives the tick that launched it (its wrapper is detached), so the
simplest durable host form is `serve --once` on a schedule, run from the owner copy. Print a
ready example with absolute paths; printing it registers nothing, and registering it is your step:

```powershell
python .agentic-team/bin/agentic_team.py supervise host-example --project . --platform windows
python .agentic-team/bin/agentic_team.py supervise host-example --project . --platform systemd
python .agentic-team/bin/agentic_team.py supervise host-example --project . --platform cron
```

Overlapping ticks wait for the store lock, so a slow tick never starts a second worker.

## 4. When a job needs you

`status` lists every held job with the reason and the exact next command. Approvals stay the
runtime's authenticated human operations; `supervise resume` then revalidates the hold and
relaunches only if it cleared.

| Hold | What happened | What you do |
|---|---|---|
| `checkpoint` | the run waits for a human decision: an R2+ release, an R3/R4 action, a deviation, a budget warning, or a rejection | `agentic_team.py approve --checkpoint CP-00N --decision "..." --by <you> --token-file <token>` (or `reject`; after a rejection, correct the work and `resolve`), then resume the job |
| `evidence` | the run says `complete`, but the owner-side re-check disagrees: the event log does not show the run reaching 07_learn and completing, or the verification, release (including the executable release conditions when no human approved it), or learning exit contract fails as you see it | inspect the run folder and its event log; a worker can write `state.json`, so a status field proves nothing on its own |
| `failed-task` | a task failed the same way twice or ran out of retries | `agentic_team.py reopen --task T --reason "new approach" --extend-retries 1 --by <you> --token-file <token>`, then resume |
| `unknown-usage` | the attempt left no readable cost (killed, timed out, malformed output); its reservation stays counted | `supervise resume --job J --usage-transcript FILE` to meter a recovered transcript, or `--charge-reservation` to count the whole reservation as spent |
| `ownership` | a wrapper or worker cannot be shown to have stopped (stale heartbeat, a worker outliving its wrapper, an unreadable process identity) | check the processes yourself, then `supervise resume --job J --confirm-stopped`; it refuses while a process is provably still the attempt's |
| `budget` | the run's remaining allowance is below one attempt, or an attempt took the run past its ceiling | review; `agentic_team.py waive --requirement budget:usd ...` lifts the run's ceiling (the aggregate allowance still applies), then resume |
| `tamper` | `audit verify` failed (an unsigned ledger record, a state approval with no signature) or the exported view changed during the attempt | investigate before anything else; resume only re-runs the audit |
| `source` | the run completed but the tree has uncommitted changes, or HEAD moved past the verified commit with source changes | inspect `git status` and `git log`; the supervisor never resets or cleans; restore the verified tree, then resume |
| `pointer` | `CURRENT.md` names another run | `agentic_team.py switch-run --run sup-<job>`, then resume |
| `config`, `adapter` | the configuration cannot launch (no budget, no verified isolation for paid workers, a worker command that does not start, a harness login failure), or the launch failed before any worker started | fix it with `supervise configure`, then `resume --job J --refresh-config` |

`supervise pause --job J` (or `--all`) stops launching; a running attempt finishes first.
`supervise cancel --job J --reason "..."` asks the attempt's wrapper to end its own worker tree;
nothing else is ever signalled, and every change in the tree is kept. While an attempt is not yet
reconciled (including one held because its processes cannot be shown to have stopped), the job
stays as it is and keeps the checkout; it becomes `cancelled` only after a tick reconciles that
attempt, and `release` refuses until then. A job that leaves uncommitted changes keeps the
checkout reserved until you deal with them and run
`supervise release --job J --disposition "kept on branch x"`. An attempt whose cost stayed unknown
can still be settled on a finished job with `resume --job J --charge-reservation`.

## 5. Money

Before each attempt the supervisor reserves `--attempt-usd` against both the run's remaining
allowance (its ceiling minus the larger of reported and metered usage, minus open reservations)
and the aggregate allowance. After the attempt it meters the frozen transcript exactly once (by
digest, so a crash and restart never charges twice) and replaces the reservation with the real
figure. Unknown cost keeps the reservation and holds the job: nothing is ever recorded as free.
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
might act. On Windows the worker runs in a job object that ends with its wrapper.

Records live in the owner store, printed at the bottom of `status`
(`<AGENTIC_TEAM_HOME>/supervisor/<project>-<hash>/`): `config.json`, `control.json` (checkout,
pause, aggregate allowance and reservations), `jobs/`, `attempts/<job>/<attempt>/` (intent, claim,
start and exit receipts, heartbeat, transcript, stderr), `bin/` (the owner copy), `view/`,
`worker-home/`, `log.jsonl`. The store lock is an operating-system file lock, released when its
holder dies, so a crashed tick never leaves a lock to break. An unreadable record or an unknown
schema stops launches and names the file; a full disk stops launches and says so. Neither loses
queued work, and spend already recorded stays counted even if you move a broken record aside.

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
python .agentic-team/bin/agentic_team.py supervise configure --project . --adapter claude --isolation-prefix-json "[\"wsl\", \"-u\", \"agentic-worker\", \"--\"]" --view-dir <worker-readable dir> --worker-home <worker-writable dir>
python "<owner copy>" verify-isolation --project .
```

`verify-isolation` writes a harmless sentinel into the owner store and runs a probe through the
prefix; the boundary passes only if the probe cannot read the sentinel and cannot write into the
view directory. Changing the prefix resets the
verification. The adapter inspects `claude --help` before every launch and refuses if
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
`supervise prune --older-than-days 30 [--dry-run]` deletes transcripts of finished jobs whose
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
