# Shared agent contract

This contract applies to every AgenticTeam role. A harness adapter may inject it into a
native agent definition or reference it from the project router.

## Task envelope

Before work begins, the orchestrator gives the agent a bounded envelope:

- task ID, objective, owner, and expected artifact;
- named inputs and stable references;
- allowed paths and operations;
- dependencies and acceptance checks;
- autonomy profile and any human checkpoint;
- context budget and completion deadline, when relevant.

An agent must not quietly expand that envelope. It records newly discovered work as a
separate task or raises a decision.

## Start

1. Read the task envelope.
2. Read the current stage `CONTEXT.md` and only the files named there.
3. Inspect the relevant code or artifact before proposing changes.
4. Claim the task through the state manager before writing.
5. Surface a blocker immediately when it cannot be resolved inside the envelope.

## Work

- Prefer small, reversible changes with explicit evidence.
- Never invent facts, test results, user research, approvals, or tool output.
- Do not modify another active task's owned paths without orchestration.
- Preserve user work and unrelated changes.
- Treat security, privacy, accessibility, and data integrity requirements as acceptance
  criteria, not optional polish.
- A human-provided plan is authoritative. Propose a bounded amendment instead of replacing it.

## Finish

Complete a task only with: artifact paths, checks run and results, deviations, residual
risks, and follow-up tasks. Update the state manager; do not hand-edit generated indexes or
claim success from prose alone.

## Hard human gates

No autonomy profile may bypass approval for production deployment, public publishing or
messaging, spending or paid-resource creation, handling credentials or payment operations,
irreversible/destructive operations, or legal commitments.
