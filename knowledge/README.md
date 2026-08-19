# Knowledge Base — how the team learns

This directory is the team's persistent memory. The installer copies it into each
project at `.agentic-team/knowledge/`. It survives across builds: copy it back to this
master repo (or keep a shared location) so lessons compound.

## Files

- `lessons.md` — evidence-scoped lessons. Agents read only relevant entries and create
  candidates at retrospectives (or immediately after an expensive failure).
- `decisions.md` — cross-build decision patterns worth reusing (stack choices that
  worked, provider picks, etc.). Per-build decisions live in `.agentic-team/runs/<run-id>/DECISIONS.md`;
  promote the reusable ones here.
- `playbooks/` — one per-agent checklist. New checks remain candidates until evaluated;
  promoted checks become role-scoped reflexes. See `playbooks/README.md`.
- `evolution/` — `PROPOSALS.md` (candidate amendments to agent definitions) and
  `CHANGELOG.md` (what was actually changed and why). Human-approved only.

The evidence ladder from observation through human-approved promotion is defined in
`.agentic-team/protocols/evolution.md`. Read it before a retrospective.

## Rules for lessons

1. A lesson must change future behavior. "The build went well" is not a lesson.
   "Vitest + testcontainers flaked on Windows CI; pin testcontainers <X or use
   service containers" is a lesson.
2. Use the entry format below. Tag with roles so agents can filter to what's theirs.
3. Lessons are written by the agent who learned them, during retrospective (`07_learn`)
   or immediately when expensive.
4. The delivery-lead prunes: duplicates merged, stale entries (superseded versions,
   fixed bugs) deleted. A knowledge base nobody can read is not knowledge.

## Entry format

```
### [YYYY-MM-DD] [roles: backend-engineer, backend-lead] Short imperative title
- context: one line on the build/situation
- lesson: what to do differently and why
- evidence: what happened that taught this
```
