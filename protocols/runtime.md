# Runtime and concurrency protocol

The harness provides model execution; `scripts/agentic_team.py` provides deterministic
project state. The filesystem is the durable coordination bus.

## Single-writer state

All task lifecycle changes go through the CLI. It writes atomically under a run lock. Agent
prose is never treated as state. A stale task lease may be recovered only after its expiry is
recorded as an event.

## Task lifecycle

`pending -> ready -> claimed -> completed`

Exceptional states are `blocked`, `failed`, and `cancelled`. A task becomes ready only when
all dependencies are complete. Claiming records agent, time, lease, and owned paths. Completion
requires evidence and refreshes dependent tasks.

## Parallel work

- Parallelize only tasks with satisfied dependencies and non-overlapping owned paths.
- Prefer native worktrees when the harness supports them; otherwise isolate by file ownership.
- One build integrator owns convergence of parallel branches or worktrees.
- Contract/schema changes are serialized through the architect or designated owner.
- Independent verification runs after integration, not on an obsolete branch.

## Recovery

Run state is resumable after process or context loss. On resume, read the router and state
summary, reconcile claimed leases, and continue the current stage. Never infer completion
from files alone; attach evidence through the CLI.
