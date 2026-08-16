# Communication and handoff protocol

Files are the durable bus; the CLI is the state authority. The active run is named in
`.agentic-team/CURRENT.md`. Start with the router, current stage contract, and assigned task
packet—not every document in the run.

## Task envelope

Every task records ID, title/objective, owner, stage, risk, dependencies, owned paths, named inputs,
acceptance checks, and completion evidence. A task becomes ready only when the state manager proves
its dependencies complete. One agent owns one claim; parallel claims may not overlap paths.

## Updates

Progress messages are concise and evidence-labelled:

```text
T-014 — completed by backend-engineer
Artifacts: src/api/auth/*, tests/api/auth/*
Observed: 14 integration tests passed (command/run link)
Deviation: rate limiting split into T-021; architecture contract unchanged
Risk/follow-up: password reset remains outside supplied scope
```

Distinguish observed evidence from reported and inferred information. Never mark complete from an
unexecuted command or file existence alone.

## Handoffs and escalation

A handoff names produced artifacts, authoritative decisions, checks/results, limitations, and the
next task. Escalation follows worker → lead → delivery-lead → ceo → human and contains question,
recommendation, alternatives, impact, and smallest needed answer.

Create a new task for discovered scope. Do not quietly expand the current envelope or edit another
claimed task's paths.
