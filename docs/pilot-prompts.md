# Supervisor pilot prompts

Use these prompts with the AgenticTeam repository open at its root on the **pilot host** (a Linux
machine or WSL2 Ubuntu with everything on the Linux filesystem). The [pilot plan](pilot-plan.md)
fixes the decisions, phases and acceptance cases; these prompts only direct an agent through
them. They never ask an agent to spend credits without the owner's written authorization,
approve its own work, weaken a check, or push.

For one session, paste the master prompt. The phase prompts let you assign or resume one phase;
each repeats its own starting instructions. Never run two prompts against the same pilot host
or owner store at the same time. Every prompt inherits the gotchas at the end of this file.

The agent that runs these prompts may be any capable coding model. The **worker's** model inside
the pilot is a separate owner decision recorded with `configure --model`; the prompts never pick it.

## Master prompt

```text
You are running the AgenticTeam supervisor pilot plan, docs/pilot-plan.md, phases Q0 to Q7,
from this repository on the pilot host. Read the plan, docs/supervisor-progress.md,
docs/supervisor-operator-guide.md sections 1, 3, 5 and 7, and docs/codebase-repair-progress.md
("Known limits and decisions for the owner") before you run anything. The supervisor is
implemented and offline-verified at main b850178 or later; nothing is pilot-verified or
activated, and your record must keep those three states distinct.

Fixed decisions (do not reopen them): POSIX pilot host; container boundary preferred, two-user
sudo fallback; a dedicated Anthropic API key passed only through --env-passthrough after the
Q1-b correction; the worker model is whatever the owner recorded with configure --model;
budgets usd=5 per run, 2 USD per attempt, headroom 1.25, aggregate 10 USD, 2 retries,
1800 s per attempt, turn limit timeout-only unless claude --help advertises --max-turns,
serve --until-idle --max-seconds 3600; one job; code on branch pilot-prep; merges and pushes
only on the owner's words.

Work in order. Q0 to Q4 spend nothing except the single authenticated claude -p check in Q4
(a few cents, inside the boundary, recorded). Stop before Q5 and present the Q4 record; Q5
starts only after the owner writes an authorization naming the project, model, budgets, time
limit and stop conditions, which you paste into docs/pilot-progress.md. Q7 presents a host
task and registers nothing.

For Q1, first read verify_isolation, worker_argv, worker_environment and SENSITIVE_ENV in
scripts/agentic_supervisor.py and confirm each of Q1-a, Q1-b, Q1-c is really open; record
line numbers. Implement only what is open, each with the named regression test, shown
failing once before the fix. Run the canonical checks (validate, docs --check, full unit
suite from the root with output redirected and the verdict grepped, evals/run_scenarios.py,
preflight_skills) before you call Q1 done.

Keep docs/pilot-progress.md current after every phase: what ran, where, versions, what came
back verbatim where the plan asks for verbatim, and what is open. Quote exit codes and
digests; never paraphrase a verdict. When a step fails, record it and stop at the gate;
do not retry a paid step, do not widen a budget, do not disable a check.

Never read or copy the owner's token files or the pilot key's value into any file or
message; name variables, not values. Never run owner commands from .agentic-team/bin inside
the checkout; use the owner copy. Never run serve from a shell holding any Anthropic
credential other than the pilot key.

Finish by writing the Q6 verdict in the plan's exact wording and the Q7 proposal verbatim,
then stop. Report: host facts, Q1 changes and test names, the pilot project path and commits,
the rehearsal digest, the boundary recipe and the six manual checks, the authorization text
(or that it is awaited), the paid run's figures, the verdict, and the activation proposal.
```

## Phase Q0 baseline and host readiness

```text
Execute Q0 of docs/pilot-plan.md on the pilot host. Create docs/pilot-progress.md with the
four states (offline-verified, pilot-verified, activated, plus "not run"), a phase table Q0
to Q7 with status and date columns, and a "Where it stands" paragraph that reads
"offline-verified; pilot not run".

Record on the host: uname -a, python3 --version, claude --version, whether claude --help
lists --max-turns, docker --version or "Docker absent, two-user fallback", git --version,
and git rev-parse HEAD of this checkout. Confirm main is b850178 or a descendant with green
CI (gh run list --branch main --limit 1). Run the full unit suite from the repository root
with output redirected to a file and quote the Ran/OK line. Spend nothing. Stop at the gate
and show the record.
```

## Phase Q1 corrections before the paid run

```text
Execute Q1 of docs/pilot-plan.md on branch pilot-prep. Read verify_isolation, worker_argv,
worker_environment and SENSITIVE_ENV in scripts/agentic_supervisor.py and the isolation
section of docs/supervisor-operator-guide.md. For each of Q1-a (positive control in the
isolation probe), Q1-b (ANTHROPIC_* and CLAUDE_* filtered by default, passthrough named in
the digest) and Q1-c (namespace rule documented; wsl prefix warns on Windows), state with
line numbers whether it is open. Implement only the open ones.

Q1-a: the probe reads a random control file the owner writes into the view directory and
prints its content; the boundary passes only when the control content comes back, the
sentinel is denied, the view is read-only and a write into the worker home succeeds. The
refusal names which check failed. Tests: a scripted prefix that cannot resolve host paths is
refused with "control file unreadable"; a prefix that sees the view but not the store passes;
a prefix that can write the view is refused.

Q1-b: extend SENSITIVE_ENV; worker_environment drops ANTHROPIC_API_KEY unless passed
through; the digest's Worker column lists passed-through variable names. Tests for both.

Q1-c: operator guide section 7 states that the prefix must present the checkout, view and
worker home at the host's absolute paths, with the container and two-user shapes;
configure warns (does not refuse) for a prefix starting with wsl or wsl.exe on Windows.
Test the warning text.

Show each new test failing once before its fix. Add a changelog line under a dated heading.
Run validate, docs --check (docs --write first if parser text changed), the full suite from
the root with output redirected, evals/run_scenarios.py and preflight_skills. Commit on
pilot-prep with a message that names Q1-a, Q1-b, Q1-c. Do not merge or push.
```

## Phase Q2 the pilot project

```text
Execute Q2 of docs/pilot-plan.md on the pilot host. Create a scratch git repository on the
Linux filesystem, outside this checkout and not under /mnt/c. Add greet/__init__.py with
greet(name) returning "Hello, <name>!", tests/test_greet.py with a passing test, README.md,
and .gitignore covering .agentic-team/runs/, .agentic-team/CURRENT.md,
.agentic-team/supervisor/ and __pycache__/. Commit "fixture: greet package".

Introduce the defect: greet does not trim surrounding whitespace, and the suite still
passes because no test covers it. Commit "fixture: defect under test". Install AgenticTeam
into the project for claude-code with the platform-core preset using this checkout's
scripts/agentic_team.py install, and commit the install.

Write pilot-event.json next to the repository (not inside it): kind manual, a title, a brief
of five to ten lines written like a triaged issue, and exactly two acceptance lines:
"AC-1: greet trims surrounding whitespace from the name" and "AC-2: tests/test_greet.py has
a regression test for AC-1 and the whole suite passes". Confirm the project's tests pass,
git status is clean, and .agentic-team/bin/agentic_team.py status --project . runs. Record
the path and the three commit hashes in docs/pilot-progress.md. Spend nothing.
```

## Phase Q3 dress rehearsal with the command adapter

```text
Execute Q3 of docs/pilot-plan.md on the pilot host in the pilot project, with the owner
store under your real AGENTIC_TEAM_HOME. Read evals/scenarios/supervisor_unattended.json
for the command-adapter argv that drives tests/fake_worker.py, and docs/supervisor-operator-
guide.md sections 1 and 3.

Run owner-copy from the checkout's bin once, then every later command from the owner copy:
configure with autonomy unattended, entry execute-only, budget usd=5, attempt-usd 2,
headroom 1.25, retries 2, timeout 1800, adapter command and the fake worker as the command;
allowance --add-usd 10 --reason "pilot rehearsal". Enqueue pilot-event.json's content with
enqueue (title, brief, both acceptance lines), then serve --until-idle --max-seconds 600
with output to a file. Expect the job done, the attempt metered from the fake result line,
audit clean in the log, exit 0.

On a second enqueued event exercise pause --all, resume --all and cancel --job, and confirm
the exit codes of status against the operator guide's table. Then release --job for the
done job. Leave the store and the checkout binding in place for Q4 unless the owner says
otherwise. Record the final digest verbatim and the exit codes in docs/pilot-progress.md.
Spend nothing.
```

## Phase Q4 the boundary

```text
Execute Q4 of docs/pilot-plan.md on the pilot host. Build the boundary the plan fixes:
preferably a container image with Python 3, git, Node and Claude Code, run with the
checkout, the view directory and the worker home bind-mounted at the same absolute paths
as the host (the view read-only), nothing else mounted, an unprivileged uid, -w set to the
checkout, and -e for AGENTIC_TEAM_HOME, AGENTIC_TEAM_VIEW, AGENTIC_TEAM_WORKER,
AGENTIC_TEAM_PROTECT, PYTHONIOENCODING and ANTHROPIC_API_KEY. If Docker is absent, create
the agentic-worker user, the NOPASSWD sudoers rule for your user to run as it, a shared
setgid group on the checkout, umask 002, owner store mode 0700, view group-readable only.

From the owner copy, configure --adapter claude --isolation-prefix-json with that prefix,
--isolation-python for the Python inside it, --view-dir and --worker-home on paths the
boundary presents unchanged, --env-passthrough ANTHROPIC_API_KEY, --model as the owner
recorded, --turn-limit timeout-only unless claude --help advertises --max-turns, and the
pilot budgets and timeout. The only Anthropic credential in your shell is the pilot key.

Run verify-isolation; expect verified true naming all four checks. Then run through the
same prefix and record verbatim: cat of the owner store's config.json (denied), touch in
the view (denied), cat of a file in the view (succeeds), touch in the worker home
(succeeds), git -C <checkout> status (succeeds), claude --version (succeeds), and one
claude -p "Reply with the single word ready" --output-format json --max-budget-usd 0.05
(returns a numeric total_cost_usd; record the cost). This last call is the only spend
before Q5. Record the store's isolation boundary digest. Stop at the gate and present the
record; do not enqueue anything for the Claude adapter yet.
```

## Phase Q5 the paid run

```text
Execute Q5 of docs/pilot-plan.md only if docs/pilot-progress.md contains the owner's
authorization naming the pilot project, the model, usd=5 per run, 2 USD per attempt, 10 USD
aggregate, 1800 seconds and the stop conditions. If it does not, stop and ask for it in
those words; do not proceed on an earlier approval of anything else.

Confirm with status --json that no job is open from Q3 and that the current configuration
digest equals the one recorded in Q4. Enqueue the fixture event with a new id. From the
owner copy run serve --until-idle --max-seconds 3600 with output to a file and touch
nothing else in the checkout while it runs. The only owner actions meanwhile are status
and, on a stop condition, pause --all.

When serve exits, record verbatim: exit code, the digest, each attempt's usage state and
USD, the run's stage and status, audit verify output, and the Anthropic console figure for
the pilot key. Do not interpret yet, do not retry, do not change any budget. Stop at the gate.
```

## Phase Q6 evaluation

```text
Execute Q6 of docs/pilot-plan.md. Check every bullet of the plan's "Scope and completion"
and mark each held or not with the evidence path. Check out the pilot project at the run's
Verified-SHA, run its tests, confirm the regression test exists and the defect is fixed,
and confirm nothing was pushed. Read the transcript's result message (cost, model, stop
reason) and the attempt's stderr and wrapper log; compare the cost to the console.

If the job held or failed, diagnose from the store log and the run state. For a cause in
AgenticTeam write a regression test and the fix on pilot-prep; for a cause in the fixture
or the host record it as such. Start no second paid run. Write "Where it stands" in the
plan's exact form: "pilot-verified on <host> with <model> at <USD>" or "not pilot-verified:
<reason>". Run the canonical checks if code changed. Commit on pilot-prep; do not merge or push.
```

## Phase Q7 activation decision

```text
Execute Q7 of docs/pilot-plan.md. From the owner copy print host-example --platform
systemd (or cron) and paste it verbatim into docs/pilot-progress.md with: the tick interval,
the allowance policy (amount and how it is replenished), what the owner does on exit codes
2 and 3, and the prune schedule. If GitHub polling is wanted, present the repository, the
opt-in label and gh auth status as the owner; configure nothing. Register nothing. Write
"not activated" in the record, present the setup, and stop.
```

## Independent review prompt

```text
Review the AgenticTeam pilot work on branch pilot-prep against docs/pilot-plan.md without
trusting docs/pilot-progress.md. For Q1, read the diff and run the three named tests; check
that each fails on main b850178 and passes on the branch; check that the probe now requires
the control content and that an unresolvable path is refused, not passed. For Q2 to Q4,
check that the recorded commands could produce the recorded output (paths, digests, exit
codes consistent across the record, the store log and the run folder). For Q5 and Q6,
check that the verdict follows from the evidence and that no state is claimed beyond it.
Report defects with file and line, and what the record overclaims, if anything. Change
nothing.
```

## Resume prompt after interruption

```text
Resume the AgenticTeam pilot plan from docs/pilot-progress.md. Read its phase table and the
last gate recorded, then git status and git log -5 on pilot-prep, and status --json from the
owner copy on the pilot project. Reconcile the three: if a phase is marked complete without
its gate's evidence, mark it open. If a job is running or held, do not launch anything;
record what the supervisor says and continue with the phase the record names, under the
same authorization rules: Q5 needs the owner's written authorization in the record, Q7
registers nothing.
```

## Repository and pilot gotchas (every prompt inherits these)

```text
- Run the suite from the repository root: python -m unittest discover -s tests, with
  output redirected to a file, then grep ^(Ran |OK|FAILED). A cd in a shell tool call can
  persist and break discovery; unittest prints its verdict mid-stream when piped.
- Golden snapshots: UPDATE_GOLDEN=1 on test_safety_net.py after any change to a golden
  role; review the diff. Generated docs: docs --write after parser or guarantees changes;
  docs --check must pass. DocCliConsistencyTests treats every "agentic_team.py <command>"
  phrase in README, docs and protocols as an invocation; describe future commands in prose.
- Owner commands run from the owner copy printed by owner-copy, never from the checkout's
  .agentic-team/bin; the in-checkout copy refuses serve, resume, poll-github and
  verify-isolation with exit 3.
- status and serve exit 2 when a job needs you and 3 when blocked; 1 > 3 > 2 > 0 when
  several hold. A failed job keeps 2 until acknowledge.
- Every job freezes the configuration and the isolation proof it was accepted under; any
  configure after verify-isolation clears the proof, so configure first, verify last, and
  resume --refresh-config only when you mean to re-freeze a held job.
- Paths cross the boundary unchanged: the probe and the worker get host-native absolute
  paths and environment values. A wsl prefix from Windows, or a container that mounts at
  different paths, makes the probe's "denied" lines meaningless (Q1-a adds the positive
  control) and leaves the worker unable to find its view. Mount at identical paths; keep
  the project, store, view and worker home on the Linux filesystem, not /mnt/c, which every
  WSL user can read.
- Docker passes environment only with -e NAME for each variable; sudo -n -u <user> -- drops
  the environment unless the sudoers rule keeps it (env_keep) or the prefix is
  sudo -n -u <user> env NAME=... which the supervisor does not build. Prefer the container.
- The worker environment filter keeps ANTHROPIC_* until Q1-b lands; until then the owner's
  shell must hold only the pilot key when it runs serve. After Q1-b the key reaches the
  worker only by --env-passthrough ANTHROPIC_API_KEY. Never write a key's value anywhere.
- The Anthropic console limit on the pilot key is the only hard stop on provider spend; the
  harness's --max-budget-usd is an estimate and the supervisor meters after the attempt.
- Claude Code 2.1.310 did not advertise --max-turns; check claude --help on the pilot host
  and record it. Without it, --turn-limit timeout-only is required and the timeout and the
  budget cap are the only live bounds.
- Autonomous, supervised and unattended runs refuse to start without a spend ceiling; the
  supervisor passes init-run --budget from configure --budget.
- Windows: stdin redirected to NUL reports isatty(); shell heredocs mangle backslashes, so
  write files with a file tool; Path.home() reads USERPROFILE. The Windows host runs the
  offline suite, not the paid pilot.
- Canonical checks before any merge: validate, docs --check, the unit suite, run_scenarios,
  preflight_skills. The live smoke and the pilot spend model credits and run only when the
  owner says so, in writing, in the progress record.
```
