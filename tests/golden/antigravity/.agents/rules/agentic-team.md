---
trigger: always_on
description: AgenticTeam coordination - router, run state CLI, and human gates
---

# AgenticTeam coordination

Read `.agentic-team/AGENTS.md`, then `.agentic-team/CURRENT.md` and the active stage
`CONTEXT.md`. Role contracts are installed as named agents in `.agents/agents/`; dispatch
bounded work to them instead of performing every role yourself. Durable state changes go
through `.agentic-team/bin/agentic_team.py`.

A human-supplied plan is authoritative. When this harness generates an implementation
plan artifact, that artifact must be a faithful transcription of the supplied plan - same
scope, same sequence, nothing invented - and execution starts immediately. Do not pause to
re-approve a plan the human already wrote; pause only at the hard human gates.
