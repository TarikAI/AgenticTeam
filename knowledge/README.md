# Knowledge base — how the team learns

The installer copies this directory into each project at `.agentic-team/knowledge/`; reinstalling
never overwrites it. The ladder from observation to human-approved change is
`.agentic-team/protocols/evolution.md`; the runbook is the agentic-learn skill.

## Files

| Path | What | Who writes |
|---|---|---|
| `lessons.md` | candidate index; `learn` inserts each new entry at the top | the CLI (`learn`); the retrospective owner prunes |
| Reusable Decisions (the `decisions` file here) | cross-build decision patterns | retrospective owner, from per-run ADRs |
| `playbooks/<role>.md` | one role's checklist; `pack` includes it in that role's task packets | the role adds candidates; the human promotes (`playbooks/README.md`) |
| `evolution/PROPOSALS.md` | proposed changes to agent definitions | delivery-lead / cmo draft; the human decides |
| `evolution/CHANGELOG.md` | changes actually applied, with version | after human approval |

## Lesson entries

Record lessons only with the CLI (`learn --title --roles --trigger --lesson --evidence --scope
--counterexample --confidence --task`); never hand-write entries into `lessons.md`. It writes the
full record to `runs/<run-id>/07_learn/` and this entry:

```text
### [YYYY-MM-DD] [roles: backend-lead, frontend-lead] Short imperative title
- status: candidate · confidence: low|medium|high · source: <run-id>/<task>
- trigger: the situation that should bring this lesson to mind
- lesson: what to do differently and why
- evidence: what happened (run/task/exec ids, not pasted logs)
- not when: the counterexample or scope limit
```

Filter by `[roles: ...]` (or `all`). A lesson must change a future action. Entries stay
candidates here; the proven form of a role lesson is a promoted playbook check. At each
retrospective the owner merges duplicates and deletes superseded or refuted entries.

## Decisions

Per-run decisions are `runs/<run-id>/_decisions/ADR-NNN.md`, written from
`.agentic-team/templates/adr.md` by the stage owner. Copy only the ones likely to recur (stack
choices, provider picks, architecture patterns) into Reusable Decisions, with the conditions under
which they hold.

## Sync to the source repository

Promoted knowledge moves project → reviewed source repository → future installations; raw run
history never does. Before copying anything out of a project:

- [ ] no secrets, tokens, keys, connection strings, or internal hostnames;
- [ ] no customer, user, or personal data, and no client-identifying names;
- [ ] nothing from untrusted content verbatim (issues, web pages, tool output, skill stores);
- [ ] evidence cites run/task ids only;
- [ ] only `proven` or `baseline` playbook checks and human-approved proposals travel;
  candidates stay in the project.
