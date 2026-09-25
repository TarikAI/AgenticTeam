# Source control

Git history is evidence: it shows who changed what, for which task, and which commit was
verified and released. Each rule is marked **[runtime]** (checked by the CLI or the guard hook)
or **[instruction]** (the team follows it; nothing refuses a violation).

## Base

- [instruction] Right after `init-run`, the orchestrator records the starting commit
  (`git rev-parse HEAD`) as `Base-SHA: <sha>` in BRIEF.md. The runtime does not store a base
  SHA; every task branch and every verification diff starts from this line.
- [instruction] Start from a clean tree (`git status --porcelain` empty) or commit/stash first.

## One branch per write task

- [instruction] Each claimed write task works on its own branch `at/<run>/<task>` (optionally
  in its own worktree), created from `Base-SHA` or from a merge the integrator already verified:
  `git worktree add -b at/<run>/<task> ../<repo>-<task> <base-sha>`.
- [instruction] Commits touch only the task's owned paths (`add-task --path`); a needed edit
  outside them is a new task or a `checkpoint --kind deviation`, not a quiet widening.
- [runtime] Overlapping `--path` claims (or any claim beside an `--exclusive` task) are refused
  at `claim`. The runtime checks the declared paths, not the diff.
- [instruction] Claude Code subagent `isolation: worktree` branches from the repository's
  default branch, not from the current HEAD. When the run's base is not the default branch,
  create the worktree yourself as above, and check `git merge-base HEAD <base-sha>` before work.
- [runtime] Every `exec` record stores the git HEAD it ran at, so a `cmd:` evidence line names
  the commit it tested; `commit:<sha>` evidence must resolve in the repository.

## Commits

- [instruction] Every commit carries two trailers so authorship and verifier independence are
  checkable from history:
  `git commit -m "<summary>" --trailer "Agentic-Task: <task-id>" --trailer "Agentic-Agent: <role-id>"`
- [instruction] Check: `git log --format="%(trailers:key=Agentic-Agent,valueonly)" <base>..<sha>`
  lists every author role; the `Verifier:` in VERIFICATION.md must not appear in it.
- [instruction] One logical change per commit; no generated secrets, `.env`, or
  `runs/**/_evidence/` in commits (`secrets-and-sensitive-data.md`).

## Integration

- [instruction] Only build-integrator merges task branches, one at a time, in `--depends-on`
  order, and runs the checks through `exec` after each risky boundary.
- [instruction] A conflict that needs a design choice becomes a task for the owning role
  (`add-task`) or a `checkpoint --kind decision`; the integrator never redesigns while merging.
- [instruction] The integrated result is checked out in the project root before `advance`
  leaves `04_build`; merged task branches may then be deleted locally (`git branch -d`).
- [runtime] When `advance` exits `04_build`, the CLI records the project root's HEAD as the
  run's integration SHA (`stage-advanced` event, `status --json`).
- [runtime] The `05_verify` exit requires `Verified-SHA:` in VERIFICATION.md to match that
  recorded SHA (`none` only when the project has no git history).
- [instruction] The runtime records the integration SHA once. Code changed after `04_build`
  exits is not covered by that match: raise `checkpoint --kind deviation` naming the new SHA and
  the checks re-run on it, and let the human decide.

## Release identity

- [instruction] A release is identified by commit SHA + build digest (sha256 of the artifact,
  or the image digest) + version, written in RELEASE.md. Rebuilding from the same SHA must
  reproduce the digest, or RELEASE.md says why not.

## Destructive history operations (R4)

- [runtime] Force pushes (`git push --force`, `-f`, `--force-with-lease`) match an R4 command
  rule: the guard hook (where installed) and `exec` refuse them unless a claimed
  `--action data-destructive` task has a human-approved risk checkpoint. Pushes to
  `main`/`master` and `gh pr merge` are R3 under the same rule.
- [instruction] History rewrites (`rebase`, `reset --hard`, `filter-repo` on a shared branch)
  and deleting a shared branch (`git push --delete`, `git push <remote> :<branch>`) are R4
  too, but no default command rule matches them. Declare them as `--action data-destructive`
  tasks; a project may add rules for them in `policies.local.json`.

## Revert

1. Find the change: `git log --grep "Agentic-Task: <task-id>" --format="%H %s"`.
2. `add-task --action build` in the current stage with the reason; its owner reverts on a
   fresh `at/<run>/<task>` branch: `git revert <sha>` (a merge commit: `git revert -m 1 <sha>`).
   Never reset or force-push a shared branch to undo work.
3. build-integrator merges the revert and re-runs the checks via `exec`; record the new SHA.
4. Before `04_build` exits, the new HEAD becomes the integration SHA. After it, follow the
   deviation rule above. After release, the rollback in RELEASE.md applies and a production
   rollback is a hard gate (`guardrails.md`).
