# Team observability

How the team, and the human, see what a run did. Counts come from the CLI's own records, never
from agent summaries.

## The event log

- Every state change the CLI makes appends one line to `.agentic-team/runs/<run-id>/events.jsonl`
  (`task-claimed`, `task-completed`, `task-failed`, `command-executed`, `checkpoint-created`,
  `checkpoint-approved`, `checkpoint-rejected`, `requirement-waived`, `stage-advanced`,
  `authority-refused`, `fusion-submission`, `lesson-recorded`, ...).
- Each line carries a sequence number and the hash of the previous line; `state.json` keeps
  `events_head` and `event_count`. Editing, removing, or reordering a line breaks the chain.
  This makes tampering evident, not impossible (see `harness-security.md`).
- Only the CLI writes the log. The guard hook denies agent writes to it where installed.
- Read it: `agentic_team.py log --type task-failed --since 120 --json`
  (`--since` takes a sequence number).

## Metrics

`agentic_team.py metrics --json` derives these from state and events:

| Metric | Definition |
|---|---|
| tasks per role | tasks owned by the role |
| completed | tasks in `completed` |
| first-pass | completed tasks with no recorded failed attempt |
| failed attempts | `fail` records across the role's tasks (retries included) |
| failed tasks | tasks currently in `failed` |
| checkpoint latency | median seconds from `checkpoint-created` to the human's approve/reject |
| rejection rate | rejected or resolved checkpoints ÷ all decided checkpoints |
| authority refusals | `authority-refused` events (a human-only command ran without valid owner authority: missing or wrong token, or an agent id as `--by`) |
| commands executed / failed | `command-executed` events / those with a non-zero exit code |
| usage | tokens and USD summed from `complete --usage` (self-reported) |

First-pass rate = first-pass ÷ completed, per role. Read a rising failure count or refusal count
as a process signal for the retrospective, not as a score of one agent.

## METRICS.md

- `agentic_team.py metrics --write` also writes `runs/<run-id>/METRICS.md`.
- The orchestrator writes it before `07_learn` closes; RETROSPECTIVE.md and DELIVERY-REPORT.md
  cite its numbers.

## Cross-run rollups

- Rollups across runs or projects are built from `metrics --json` output: counts, rates,
  durations, and role ids only.
- No content leaves the run: no task titles, objectives, evidence strings, command output,
  checkpoint questions, file paths, or lesson text. Project-identifying names are replaced by an
  opaque id before any rollup is shared.
- A rollup is an input to `knowledge/evolution/PROPOSALS.md`; it never edits roles or protocols
  by itself.

## Integrity checks

- `agentic_team.py doctor` re-walks the active run's hash chain and reports broken links, a head
  that does not match state, or a wrong event count. No token needed; run it at session start.
- `agentic_team.py audit verify --by <name> --token-file <path>` (human) additionally recomputes
  every ledger signature and reports forged, missing, or reordered decisions.
- A broken chain or a failed audit stops the run: raise it to the human, preserve the files,
  and do not repair them by hand.
