# Working on this repository (Claude Code and Codex)

This file is for coding agents working on AgenticTeam itself. It is not part of what AgenticTeam installs into
other projects.

## Shared roster: update it when a task is fully done

The team roster, progress board and document library at `docs/agent-team-guide/index.html` is shared by Claude
Code and Codex. When you finish a task (work committed or merged; a plan, prompt, record or review written or
changed; a drill or live run finished), update it before you report back, following
`docs/agent-team-guide/UPDATING.md`:

1. Re-read `progress.json`, `updates.json` and `documents.json` in `docs/agent-team-guide/`.
2. Add one entry at the top of `updates.json`, update the `progress.json` rows your task changed, and register any
   new plan or prompt in `documents.json`.
3. Run `python docs/agent-team-guide/build.py`, then `python docs/agent-team-guide/build.py --check`.

## Ground rules

- Commit to main, merge into main or push only when the owner says so.
- Never reset, stash or switch branches in the main checkout: the plans and the shared guide live in its working tree.
- Implementation work goes on task branches merged into `autonomy-integration`; its records live in
  `docs/autonomy-implementation-progress.md` and `docs/autonomy-progress/` on that branch.
- Never read `.env` files, owner tokens or credential files, and never write a secret into the repository.
