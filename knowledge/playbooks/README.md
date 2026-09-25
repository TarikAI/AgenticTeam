# Role playbooks

A playbook is one role's short checklist of checks that reality taught it. It is the playbook
candidate step of `.agentic-team/protocols/evolution.md`. `pack` puts the owner's playbook into
every task packet, so keep it short enough to read every time.

## Entry format

```markdown
- [ ] <imperative check>  <!-- status: candidate · learned: YYYY-MM-DD · source: <run>/<task> · cost: <what it broke> -->
```

Group checks under `## Before starting`, `## While building`, `## Before claiming done`.

| Status | Meaning | Set by |
|---|---|---|
| `candidate` | observed once or twice; not yet evaluated | the role, when it adds the line |
| `proven` | evaluated against a baseline; `promoted: <date> by <human>` is appended | the human, with `promote --role <id> --match "<text>" --by <human>` (owner token) |
| `baseline` | seeded with the team from reviewed sources | the source repository |

## Rules

1. **File name = role id** (`backend-engineer.md`). Create it from `_template.md` the first time
   the role learns something.
2. **Agents add candidates only.** Never write `proven` or `baseline`, never edit a check you did
   not add, never edit another role's playbook.
3. **Write a check when reality corrects you:** a review finding, a failed check, a wrong
   assumption, a human correction. Phrase it as an imperative check, not a story:
   - Bad: "We had a bug where the ORM did N+1 in the invoice loop."
   - Good: "Before finishing any list endpoint, log the emitted SQL and confirm one query."
4. **Cap at ~40 lines.** At the cap, the retrospective owner merges duplicates and removes checks
   that became automatic or were refuted.
5. **Proven checks that keep firing** may become a proposal in
   `knowledge/evolution/PROPOSALS.md` to change the role definition; once the human applies it,
   delete the check here.
6. **No secrets, customer data, client-identifying details, or text copied from untrusted
   content.** Playbooks travel between projects (sanitisation checklist: `../README.md`).
