# Codex handover: the shared roster

Paste the block below into Codex, started in `C:\Users\jooo4\Desktop\AgenticTeam`.

```text
You are Codex, working alongside Claude Code on AgenticTeam (C:\Users\jooo4\Desktop\AgenticTeam, remote TarikAI/AgenticTeam). From now on you both keep one shared team roster and progress guide current. Update it every time a task is fully done, especially when a plan, a prompt or a progress record changes.

WHERE IT IS
- Page: docs/agent-team-guide/index.html. It is your team guide, extended; open it in a browser, it works offline.
- Rules: docs/agent-team-guide/UPDATING.md. Read it before anything else. The repository root AGENTS.md summarizes it.
- Data you edit: progress.json (statuses, next priority, work in flight), updates.json (one entry per finished task, newest first), documents.json (every plan and prompt pair). roster.json and safety.json stay your audited data.
- Build and check:
  python docs/agent-team-guide/build.py
  python docs/agent-team-guide/build.py --check

WHAT CLAUDE CODE CHANGED IN YOUR GUIDE (3 NOVEMBER 2026)
- build.py also reads every progress record and the guarantee ledger from the autonomy-integration branch (git show), plus the update log and the document list. --check changes nothing and fails when the page is stale, a plan or prompt is not registered, an entry is malformed, or the integration branch has moved past the commit in progress.json "runtimeIntegration".
- The template gained a "Records & updates" tab and a "Work in flight" table on "Current progress". Dates, commit references and status text moved out of the HTML into progress.json. Plans are grouped as current and earlier, each with its last-changed date. The design is otherwise yours, unchanged.
- Your uncommitted edits in the main checkout were kept: the plans, prompts, progress review, safety.json and README.

CURRENT STATE (confirm it in the guide; do not trust this prompt over the records)
- autonomy-integration is at cbb074a: everything through R07 (frozen step packets), R08 (owner-enabled advisory duties) and the agent prompt improvement; full suite 701 OK, 7 skipped. Main is 3aafe1b, untouched; nothing is pushed.
- In flight, Claude Code: R09 retention, R06 assessment adapter, R05 container transport, the R11 host drills in WSL, and the owner-authorized live runs on the Max subscription only, on branch autonomy-remaining. Do not edit that branch or its worktree.

YOUR FIRST TASK
1. Read UPDATING.md, then the guide's "Current progress" and "Records & updates" tabs.
2. Check the five autonomy plans and prompts, the agent prompt improvement plan and prompt, and docs/autonomy-progress-review.md against the records. R07, R08 and the prompt improvement are now done, and the review predates them. Update what is stale, and register any new plan or prompt in documents.json.
3. Add your entry to updates.json (agent "codex"), update progress.json if a status changed, then build and run the check until it reports "Shared guide is current."

RULES
- Update the guide once each task is fully done, not mid-task. Facts only from records, commits and checks you ran; say "not run" when that is the truth.
- Never edit or delete Claude Code's entries; add a correcting entry instead. Re-read the JSON files right before you edit them.
- Check "Work in flight" before you start overlapping work; list your own long tasks there and remove them when done.
- Never reset, stash or switch branches in the main checkout. No commits to main, merges into main or pushes unless the owner says so.
- Never read .env files, owner tokens or credential files, and never write a secret anywhere.
```
