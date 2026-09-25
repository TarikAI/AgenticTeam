# Runtime and concurrency protocol

The harness provides model execution; `scripts/agentic_team.py` provides deterministic
project state. The filesystem is the durable coordination bus.

## Single-writer state

All task lifecycle changes go through the CLI. It writes atomically under a run lock. Agent
prose is never treated as state. A stale task lease may be recovered only after its expiry is
recorded as an event.

## Task lifecycle

`pending -> ready -> claimed -> completed`

Exceptional states are `failed` and `cancelled`; `completed` and `cancelled` are closed for the
stage gate. A task becomes ready only when all dependencies are complete. Only the task owner
claims it, in the current stage, within the profile's concurrency cap; claiming records agent,
time, lease, and owned paths (`renew` extends a lease). Completion requires evidence and
refreshes dependent tasks.

Authority: agents create, claim, renew, complete, and fail tasks; the orchestrator may
`reassign` an unclaimed task and `reopen` a wedged claim. Only the human (owner token) may
`cancel` work, reopen a failed, cancelled, or completed task, extend a retry budget, decide a
checkpoint, or `resolve` a rejection. The run is `blocked-rejection` while a rejection is
unresolved and `blocked-failure` when a profile that stops on failure has an exhausted task.

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
