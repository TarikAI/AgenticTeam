# Supervisor pilot plan

Prepared on 2026-10-31 against `main` at `b850178` (the codebase audit repairs merged and pushed;
CI run 41089313108 green on Ubuntu, macOS and Windows with Python 3.10, 3.12 and 3.14). The
supervisor is **implemented and offline-verified**. This plan takes it to **pilot-verified** and
puts the **activated** decision in front of the owner with evidence. The companion
[prompt pack](pilot-prompts.md) has a master prompt, one prompt per phase, a review prompt and
a resume prompt.

The states keep their meaning from [the progress record](supervisor-progress.md): offline-verified
means fake workers and no model calls; pilot-verified means one bounded paid run on a configured
host ended as the plan says it must; activated means a persistent host task the owner registered.
Nothing in this plan may describe a later state as reached because an earlier one is.

## Decisions fixed by this plan

| Decision | Value |
| --- | --- |
| Host | The pilot runs on a POSIX host: a Linux machine, or WSL2 (Ubuntu) with the project checkout, owner store, view and worker home all on the Linux filesystem. A Windows-native host is **not** used for the paid pilot (see "Corrections required": the probe receives Windows paths that mean nothing inside a `wsl` or container prefix, and `/mnt/c` is readable by every WSL user). The Windows host keeps running the offline suite. |
| Boundary | Preferred: a container (`docker run`) whose prefix mounts the checkout read-write, the view read-only and the worker home read-write at the **same absolute paths** as the host, mounts nothing else, runs as an unprivileged uid, and passes only the named environment variables. Fallback: a second Linux user `agentic-worker` reached through `sudo -n -u agentic-worker --`, with the owner store mode 0700, the view group-readable only, and the checkout shared through a setgid group. Either way the proof is `verify-isolation` **plus** the manual negative and positive checks in Q4; the probe alone is not the proof. |
| Credentials | The worker authenticates with a dedicated Anthropic API key created for the pilot, with a monthly spend limit set in the Anthropic console at or below the aggregate allowance. It reaches the worker only through `configure --env-passthrough ANTHROPIC_API_KEY` after correction Q1-b makes `ANTHROPIC_*` filtered by default, and only from a shell that holds no other Anthropic credential. The owner's own login and keys never enter the boundary. |
| Model | The owner's choice, recorded by `configure --model` and frozen into the job. Suggested for a 5 USD run ceiling: `claude-sonnet-5-5`; `claude-opus-5-5` for a harder brief with a larger ceiling. The agent executing this plan does not choose the model. |
| Pilot project | A fresh scratch repository outside AgenticTeam (not this checkout), with AgenticTeam installed for Claude Code, a tiny Python package with a unit test, one committed defect, and one fixture issue whose `AC-` lines a check can decide. Its path is recorded in the progress record. |
| Budgets and limits | `--budget usd=5`, `--attempt-usd 2`, `--headroom 1.25` (the harness cap is 1.60 USD per attempt), aggregate allowance 10 USD, `--retries 2`, `--timeout 1800`, `--turn-limit timeout-only` unless the installed CLI advertises `--max-turns`; `serve --until-idle --max-seconds 3600`. One job. |
| Stop conditions | Any hold (`needs-human` of any kind), any `serve` exit other than 0, the aggregate allowance spent, the owner's `pause --all`, or wall clock past `--max-seconds`. A stopped pilot is evaluated, never silently retried. |
| Authorization | Q0 to Q4 spend nothing and need no authorization beyond this plan. Q5 (the paid run) starts only after the owner has read the Q4 record and written an explicit authorization naming the budgets above; Q7 registers a host task only on a second explicit authorization. No push, merge or second paid run without the owner's words. |
| Branch and merge | Code and documentation changes land on a task branch (`pilot-prep`), verified with the canonical checks, merged into local `main` with a merge commit when the owner authorizes it. The pilot's own evidence (transcripts, digests, console figures) stays in the owner store and is summarised, not copied, into `docs/pilot-progress.md`. |
| Agents | One session owns the plan end to end. It may delegate reading and review to subagents; nothing else runs the pilot host concurrently. |

## Verified starting point

| Item | Observed state (2026-10-31) |
| --- | --- |
| `main` | `b850178`, pushed; equal to `origin/main`. |
| Suite | 375 unit tests OK (Windows, Python 3.14); 8/8 scenarios including `supervisor_unattended`; `validate` and `docs --check` pass; CI matrix green. |
| Supervisor | `scripts/agentic_supervisor.py` (`supervise`): enqueue, configure, serve, status, pause, resume, cancel, release, acknowledge, recover-orphan, bind, allowance, verify-isolation, owner-copy, poll-github, host-example, prune. Guarantees G21–G25. |
| Isolation proof | `verify-isolation` runs a Python probe through the configured prefix with the worker's environment and passes when the probe prints that it could not read the sentinel and could not write the view. It has no positive control: a probe that cannot resolve the paths it was given prints the same two lines. Only mocked probes have been tested. |
| Worker environment | `SENSITIVE_ENV` strips `AGENTIC_TEAM_*`, GitHub, cloud, package-registry, `*SECRET*` and `*PASSWORD*` names. `ANTHROPIC_*` is not in the list, so the owner's key passes through unless the owner's shell lacks it. |
| Claude adapter | Refuses to launch without a verified boundary; inspects `claude --help` for `--print`, `--output-format`, `--max-budget-usd`, `--permission-mode`, `--allowedTools`; runs `-p` with `stream-json`, `acceptEdits`, the live-smoke allowlist plus `--allow-tool`, `--model` when set, `--max-turns` only when advertised. Claude Code 2.1.310 did not advertise it. |
| Paths | `worker_argv` and the probe pass host-native absolute paths (`str(Path)`), and the worker's environment carries host-native `AGENTIC_TEAM_HOME`, `AGENTIC_TEAM_VIEW` and `AGENTIC_TEAM_PROTECT`. A boundary that changes the filesystem namespace must present the same paths inside. |
| Pilot | Prepared in the operator guide and progress record; not run. No host task registered. |

## Scope and completion

**Pilot-verified** means all of the following hold for one job on the pilot project:

- The job went `queued → running → done` through `serve --until-idle` from the owner copy, with
  at most the configured retries, and the digest's Worker column says `claude (verified isolation; …)`.
- The run is `complete`: build, independent verification at the current HEAD, release under
  `unattended` with a rehearsed rollback, and the delivery report, all through the installed CLI.
- The fixture issue's `AC-` lines are satisfied by the change the worker committed in the pilot
  project, as judged by the owner running the project's tests at the run's verified SHA.
- The attempt's usage was metered from the frozen transcript, matches a usage record signed in
  the owner ledger, and is within 25 percent of the figure the Anthropic console shows for the
  pilot key over the same window (the console is the authority; the difference is recorded).
- `audit verify` for the run reports no unsigned gated step.
- The isolation record shows the probe passed **and** the manual checks of Q4 passed on the same
  configuration digest the job froze.
- The owner can read everything above from `status --json`, the store's log and the run folder,
  and the progress record names where.

A job that ends in a hold or a failure can still make the pilot **informative**: the hold is
diagnosed, defects get regression tests, and the record says "not pilot-verified" with the
reason. A second paid run is a new authorization.

Out of scope: more than one job, more than one checkout, GitHub polling against a real
repository (optional follow-on with its own authorization), webhooks, any push, deploy,
publish, comment or notification by the worker, and the activation itself (Q7 only prepares and
presents it).

## Corrections required before the paid run (Q1)

These were found while preparing this plan by reading `verify_isolation`, `worker_argv`,
`worker_environment` and `SENSITIVE_ENV`. Confirm each against the code before changing it, and
add the regression test named with it. None changes a frozen contract; each tightens a proof.

| Id | Problem | Change | Test |
| --- | --- | --- | --- |
| Q1-a | **No positive control in the isolation probe.** The probe prints `AGENTIC-ISOLATION-DENIED` on any `OSError`, including "no such file" when the boundary cannot see the host path at all, and `AGENTIC-VIEW-READONLY` when the view directory does not exist inside it. A `wsl` or container prefix given host paths therefore passes without proving anything, and the worker then fails to find its view. | Before the sentinel test, the probe must read a control file the owner writes into the view directory and print its random content; the boundary passes only if the control content comes back, the sentinel is denied, the view is read-only, and a write into the worker home succeeds. Refusal messages name which of the four checks failed. | `test_supervisor.py`: a scripted prefix that cannot resolve host paths is refused with "control file unreadable"; a prefix that sees the view but not the store passes; a prefix that can write the view is refused. |
| Q1-b | **Credentials pass through implicitly.** `ANTHROPIC_*` is not filtered, so whatever Anthropic key or token the owner's shell holds reaches every worker, unrecorded. | Add `ANTHROPIC_.*` and `CLAUDE_.*` to `SENSITIVE_ENV`; the pilot passes the dedicated key with `--env-passthrough ANTHROPIC_API_KEY`, which the job freezes and the digest's Worker column lists by name (never by value). The operator guide's isolation section documents the passthrough as the only way a credential reaches a worker. | `test_supervisor.py`: `worker_environment` drops `ANTHROPIC_API_KEY` by default and keeps it when passed through; the status digest names passed-through variables. |
| Q1-c | **Boundary namespace is undocumented.** Nothing tells the owner that the prefix must present the checkout, view and worker home at the host's absolute paths. | Operator guide section 7 states it, gives the container prefix shape (`-v <path>:<path>` three times, `:ro` on the view, `-e` for each `AGENTIC_TEAM_*` variable and the passthrough list, `-w <checkout>`, `-u <uid>:<gid>`), and the two-user shape; `configure --isolation-prefix-json` warns (not refuses) when the prefix starts with `wsl` or `wsl.exe` on Windows. | `test_supervisor.py`: the warning text appears for a `wsl` prefix; `test_safety_net` doc checks still pass. |

If reading the code shows one of these already handled, record that in the progress record
with the line numbers and skip the change; do not re-implement what exists.

## Phases and acceptance gates

Each phase ends with its evidence appended to `docs/pilot-progress.md` (created in Q0): what was
run, on which host and versions, what came back, and what is still open. A phase is complete
only when its gate holds; the next phase may start before the record is merged but never before
the gate.

### Q0 baseline and host readiness (no spend)

- Create `docs/pilot-progress.md` with the four states, a phase table, and a "Where it stands"
  paragraph that says "offline-verified; pilot not run".
- On the pilot host record: OS and kernel, `python3 --version`, `claude --version`, whether
  `claude --help` advertises `--max-turns`, `docker --version` (or that Docker is absent and the
  two-user fallback applies), `git --version`, and the AgenticTeam commit the host checkout is at.
- Confirm `main` is `b850178` or later with green CI; confirm the suite passes on the pilot host
  (full suite, redirected to a file).
- Gate: the record exists, the host facts are in it, the suite's verdict line is quoted.

### Q1 corrections (no spend)

Implement the table above on branch `pilot-prep`, with tests, `docs --write` if any parser text
changed, the operator guide updates, and a changelog line. Gate: the unit suite, `validate`,
`docs --check`, the scenarios and `preflight_skills` pass; the three tests exist and fail
without the change (show the failing run once).

### Q2 the pilot project (no spend)

- Create the scratch repository on the pilot host's Linux filesystem (not under `/mnt/c`), with
  a package `greet/` (`greet/__init__.py` exposing `greet(name)`), `tests/test_greet.py`, a
  `README.md`, a `.gitignore` covering `.agentic-team/runs/`, `.agentic-team/CURRENT.md`,
  `.agentic-team/supervisor/`, `__pycache__/`. Commit as `fixture: greet package`.
- Introduce the defect the issue describes, with a passing suite that does not cover it: for
  example `greet("  Ada ")` returns `Hello,   Ada !`; the issue asks for trimmed whitespace and
  a regression test. Commit as `fixture: defect under test`.
- Install AgenticTeam into it for Claude Code with `platform-core`, commit the install.
- Write the fixture event as `pilot-event.json` next to the repository (not inside it):
  `kind: manual`, a title, a brief of five to ten lines that reads like a triaged issue, and
  acceptance lines `AC-1: greet trims surrounding whitespace from the name` and
  `AC-2: tests/test_greet.py has a regression test for AC-1 and the whole suite passes`.
- Gate: `git status` clean; the project's own tests pass; `agentic_team.py validate` is not
  needed here (it is the AgenticTeam source check), but `.agentic-team/bin/agentic_team.py
  status --project .` runs; the event file parses.

### Q3 dress rehearsal with the command adapter (no spend)

On the pilot host, in the pilot project, with the owner store under the owner's real
`AGENTIC_TEAM_HOME`:

- `owner-copy`, then `configure` with the pilot budgets, `--adapter command` and the scripted
  worker from `tests/fake_worker.py` as `--worker-command-json` (see
  `evals/scenarios/supervisor_unattended.json` for the exact argv shape), `allowance --add-usd 10`.
- `enqueue` the fixture event; `serve --until-idle --max-seconds 600`; expect `done`, a metered
  attempt (the fake worker's result line), `audit verify` clean, exit 0.
- Exercise the owner controls once each on a second event: `pause --all`, `resume --all`,
  `cancel --job` on a queued job, `acknowledge` is not needed unless something failed; confirm
  the exit codes match the operator guide table.
- Reset: `release --job` for the done job, delete the owner store **and** the checkout binding
  (`.agentic-team/supervisor/binding.json`) only if the owner says so, otherwise `bind` is not
  needed because the same store continues into Q4.
- Gate: the digest and log show the lifecycle the operator guide describes, with no hold; the
  record quotes the final digest.

### Q4 the boundary (no spend, but the worker identity authenticates once)

- Build the boundary chosen in the decisions table. Container: an image with Python 3, git,
  Node and Claude Code installed; `claude --version` inside it recorded. Two-user: the user,
  the sudoers rule (`<owner> ALL=(agentic-worker) NOPASSWD: ALL`), the shared group on the
  checkout, umask 002 for both users.
- `configure --adapter claude --isolation-prefix-json '[…]' --isolation-python <python inside>
  --view-dir <path> --worker-home <path> --env-passthrough ANTHROPIC_API_KEY --model <owner's
  choice> --turn-limit timeout-only` (drop the last flag if `--max-turns` is advertised), with the
  pilot budgets and timeout. The `ANTHROPIC_API_KEY` in the owner's shell for this and every
  later owner command is the pilot key and nothing else.
- `verify-isolation`; expect `verified: true` naming all four checks.
- Manual checks through the **same prefix**, recorded verbatim: `cat <owner store>/config.json`
  is denied; `touch <view>/x` is denied; `cat <view>/<a view file>` succeeds; `touch <worker
  home>/x` succeeds; `git -C <checkout> status` succeeds; `claude --version` succeeds;
  `claude -p "Reply with the single word ready" --output-format json --max-budget-usd 0.05` returns
  a result with a numeric `total_cost_usd` (this is the one authenticated call before Q5, a few
  cents, and it is what proves the key works inside the boundary; record its cost).
- Gate: all of the above, plus the store's `isolation.boundary_sha256` recorded in the progress
  record so Q5 can show the job froze the same digest.

### Q5 the paid run (owner authorization required)

Start only after the owner has written an authorization that names the pilot project, the model,
`usd=5` / `2` / `10`, `1800` seconds and the stop conditions. Paste it into the progress record.

- `allowance` already holds 10 USD from Q3; confirm with `status --json` that nothing is open
  from the rehearsal and that the configuration digest equals Q4's.
- `enqueue` the fixture event (a new id if Q3 used the same source key; `--requeue` is for failed
  or cancelled sources, not done ones).
- `serve --until-idle --max-seconds 3600` from the owner copy, output captured to a file. Do not
  run anything else against the checkout meanwhile.
- While it runs, the only owner actions are `status` and, on a stop condition, `pause --all`.
- On exit: record the exit code, the digest, the job's attempts with their usage state and USD,
  the run's stage and status, `audit verify` output, and the Anthropic console's figure for the
  pilot key.
- Gate: the exit code and digest are recorded truthfully. Whether the pilot is "verified" is
  decided in Q6, not here.

### Q6 evaluation (no spend)

- Check every bullet of "Scope and completion" and mark each held or not.
- Read the pilot project's diff at the run's `Verified-SHA`; run its tests there; confirm the
  regression test exists and the defect is fixed; confirm nothing was pushed from the project.
- Read the transcript's result message: cost, turns, model actually used, stop reason. Compare
  cost to the console. Read `stderr.txt` and `wrapper.log` for warnings.
- For a hold or failure: diagnose from the log and the run state, write a regression test when
  the cause is in AgenticTeam, and record the fix on `pilot-prep`. Do not start another paid run.
- Gate: the progress record's "Where it stands" says exactly one of "pilot-verified on <host>
  with <model> at <USD>" or "not pilot-verified: <reason>", with the evidence paths.

### Q7 activation decision (no spend; registration needs authorization)

- Print `host-example --platform systemd` (or `cron`) from the owner copy; include it in the
  record with the tick interval, the allowance policy (how much, replenished how), the exit-code
  handling (what mails or pages the owner on 2 and 3), and the retention (`prune`).
- If GitHub polling is wanted: the repository, the opt-in label and `gh auth status` as the owner,
  presented, not configured.
- Register nothing. Present the setup and stop; the owner registers it, or authorizes the agent
  to, in their own words.
- Gate: the record has the proposed unit or crontab verbatim and the words "not activated".

## Worker and budget policy for the pilot

| Item | Value | Where it is enforced |
| --- | --- | --- |
| Run ceiling | `usd=5` | `init-run --budget` by the supervisor; `claim`/`exec` refuse once spent (G22) |
| Attempt reservation | 2 USD; harness cap 1.60 USD (`--max-budget-usd`) | supervisor reservation; the harness's own estimate |
| Aggregate allowance | 10 USD | `allowance`; nothing launches past it |
| Console limit | at or below 10 USD per month on the pilot key | Anthropic console (the only hard stop on provider spend) |
| Retries | 2 relaunches | supervisor |
| Time | 1800 s per attempt; 3600 s for the whole `serve` | wrapper kills the process tree; `--max-seconds` |
| Turns | `timeout-only` unless `--max-turns` is advertised | adapter refuses otherwise |
| Permissions | `acceptEdits`, live-smoke allowlist plus `--allow-tool` for the project's test command | adapter; project hooks stay on |
| Authority | empty worker home, read-only view, no tokens; `audit verify` after the attempt with the owner token | runtime (G21), supervisor (G25) |
| Credentials | pilot key by passthrough only; nothing else in the shell | Q1-b plus the owner's discipline, recorded |

## Required acceptance cases

| Id | Case | Phase | Blocks |
| --- | --- | --- | --- |
| A1 | Probe without positive control is refused; with it, passes only when all four checks hold | Q1 | pilot |
| A2 | `ANTHROPIC_API_KEY` dropped by default, kept by passthrough, named in the digest | Q1 | pilot |
| A3 | `wsl` prefix on Windows warns; guide documents namespace rule | Q1 | pilot |
| A4 | Pilot project: clean tree, failing behaviour, passing suite, event file with two `AC-` lines | Q2 | pilot |
| A5 | Rehearsal job `done`, metered, audit clean, exit 0; pause/resume/cancel exit codes as documented | Q3 | pilot |
| A6 | `verify-isolation` true; six manual checks recorded; one authenticated `claude -p` inside the boundary with numeric cost | Q4 | pilot |
| A7 | Owner authorization text recorded before any paid `serve` | Q5 | pilot |
| A8 | Paid job recorded truthfully: exit code, digest, attempts, usage, run state, audit, console figure | Q5 | evaluation |
| A9 | Every "Scope and completion" bullet marked held or not, with evidence paths | Q6 | verdict |
| A10 | Defects found by the pilot have regression tests on `pilot-prep` | Q6 | merge |
| A11 | Activation setup presented verbatim; nothing registered | Q7 | none |

## Verification and delivery

- Canonical checks before any merge: `validate`, `docs --check`, the full unit suite from the
  repository root with output redirected and the verdict line grepped, `evals/run_scenarios.py`,
  `preflight_skills`. On the pilot host the suite runs under the host's Python; the Windows host
  keeps its own run.
- `docs/pilot-progress.md` carries: phase table with dates; host facts; the Q1 diff summary and
  test names; the pilot project path and commits; the rehearsal digest; the boundary recipe,
  digest and manual checks; the authorization text; the paid run's figures; the Q6 verdict; the
  Q7 proposal; known limits. It never describes a state as reached without the evidence line.
- README gets one bullet under Documentation pointing at the plan, prompts and progress record;
  the operator guide's pilot paragraph points at the progress record once Q6 is written.
- Merge of `pilot-prep` into local `main` with a merge commit only when the owner authorizes;
  no push without the owner's words.

## Known limits of the pilot

- One job proves the loop once; it does not prove the retry path, the config hold, or the
  unknown-usage hold against a real harness. Those stay offline-verified.
- The container or second user is a boundary for files; it does not stop a worker from using the
  network, so production credentials must be absent from the host the worker can reach, not
  merely filtered from its environment.
- Cost comparison against the console is approximate (the console aggregates by key and time).
- The pilot key's console limit is the only hard stop on provider spend; everything the
  supervisor enforces is after-the-fact metering or a client-side estimate.
- Nothing here provisions more checkouts or workers; activation runs the same one-checkout loop
  on a schedule.
