# Updating the shared roster

`docs/agent-team-guide/index.html` is the team roster, progress board and document library that Claude Code and
Codex both maintain for the owner. Open it in any browser; it works offline. This file is the one set of rules both
agents follow.

## When to update

Update the guide once a task is **fully done**, before you report back to the owner:

- implementation work committed or merged (name the branch and the commits);
- a plan, an implementation prompt, a progress record or a review written or changed;
- a host drill, a measurement or a live run finished, whatever its result (pass, fail or inconclusive);
- a long task started, stopped half-way or handed to another session or agent (the "active" list).

Do not update it mid-task with guesses. A task that stopped part-way gets an entry that says so and what is left.

## What lives where

| File | Edit it when | Rule |
| --- | --- | --- |
| `updates.json` | every finished task | Add one entry at the top. Never change or delete another agent's entry; correct it with a new one. |
| `progress.json` | a status, the next priority or the work in flight changed | Change only the rows your task changed. Set `asOf` and `updatedBy`. |
| `documents.json` | a plan or prompt was added, renamed or retired | Every `docs/*-plan.md`, `docs/*-prompt.md` and `docs/*-prompts.md` must be listed. |
| `roster.json`, `safety.json` | a role or a control changed | Audited data; keep roles in `team.json` order. |
| `guide.template.html` | the page layout changes | Keep dates, commits and status text out of it: they belong in `progress.json`. |
| `index.html`, `agent-roster.csv` | never by hand | `build.py` writes them. |

Plans and prompts are read from the main checkout's `docs/` folder. Progress records are read from the integration
branch named by `recordsRef` in `progress.json` (`docs/autonomy-implementation-progress.md` and every file in
`docs/autonomy-progress/`), so a record appears once it is committed there. Write records in the task's own branch as
usual; the guide does not replace them.

## Steps

1. Re-read `progress.json`, `updates.json` and `documents.json` right before you edit them: the other agent may
   have changed them since you last looked.
2. In `updates.json`, add your entry at the top of `entries` (format below).
3. In `progress.json`, set `asOf` to today and `updatedBy` to `claude` or `codex`. Update the `statuses` rows,
   `nextPriority`, `todaySummary` or `evidence` your task changed. If you reconciled the statuses against a newer
   integration commit, set `runtimeIntegration` to it. Add your task to `active` when you start long work, and remove
   it when you finish.
4. In `documents.json`, register any new plan or prompt pair (under `current`, or `earlier` for history).
5. Run the build, then the check, and fix every problem the check lists:

   ```text
   python docs/agent-team-guide/build.py
   python docs/agent-team-guide/build.py --check
   ```

6. Say in your report to the owner that the roster is updated.

Run both in the main checkout: last-changed dates come from file times there, so another clone builds different dates.
The check fails when `index.html` is stale, when a plan or prompt is not registered, when an entry is malformed, or
when the integration branch has moved past the commit the statuses were reconciled against. In that last case, read
the new records, update the statuses, then set `runtimeIntegration`.

## Entry format

```json
{
  "date": "2026-11-03",
  "agent": "claude",
  "task": "Short name of the task",
  "summary": "What is now true, in one to three sentences, including what was not done or not verified.",
  "documents": ["docs/autonomy-progress/example.md"],
  "refs": ["task-branch@1234567", "autonomy-integration@89abcde"]
}
```

`agent` is `claude` or `codex`. Dates are absolute (`YYYY-MM-DD`). Entries go newest first. `refs` may be empty for
work that is not committed; then say so, for example `"main checkout working tree, uncommitted"`.

## Rules for both agents

- **Facts only.** Write what a record, a commit or a check you ran shows. Say "not run" or "not verified" when that
  is the truth. A plan or a prompt is never evidence that the work passed.
- **No secrets.** Never write a token, key, credential, password, customer data or the contents of a `.env` file here.
- **The main checkout stays put.** Never reset, stash or switch branches in it: the plans and this guide live in its
  working tree. Commit to main, merge into main or push only when the owner says so.
- **One writer at a time.** Edit, then rebuild straight away. If the check shows a file changed under you, re-read it,
  reapply your entry and rebuild.
- **Keep it readable.** Plain sentences, no internal nicknames, and expand an acronym the first time it appears.
