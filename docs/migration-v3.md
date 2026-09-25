# Migrating from v2 to v3

v3 keeps the v2 architecture (portable roles compiled per harness, one state CLI, numbered
stages, hard human gates, Fusion) and makes its promises checkable: signed human decisions,
typed evidence, stage exit contracts, action/target risk, access classes, and harness guard
hooks. This page covers what changes for an existing v2 project and how to move a v2 run over.

## 1. Reinstall the team

Run the v3 installer against the project, with the same harness and preset as before:

```powershell
.\scripts\install.ps1 -Target C:\projects\app -Harness claude-code -Preset full-platform
```

```bash
python scripts/agentic_team.py install ~/projects/app --harness claude-code --preset full-platform
```

What to expect:

- **Local edits to generated files.** v3 records a sha256 for every generated file. From now on,
  reinstall stops and names any generated role, skill, protocol, or template you edited; rerun
  with `--force` to back those files up under `.agentic-team/backup/<timestamp>/` and continue.
  The v2 installer recorded no hashes, so the **first** v3 reinstall cannot detect your v2
  edits: copy any generated file you changed before reinstalling.
- **Project-owned files stay.** `knowledge/`, `runs/`, and text outside the managed AgenticTeam
  block in `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` are untouched. Generated files the new
  install no longer produces are removed.
- **Settings are merged, not overwritten.** On Claude Code the installer adds deny rules and a
  `PreToolUse` guard hook to `.claude/settings.json`; on Codex it adds the guard hook to
  `.codex/hooks.json`. Your own entries stay. The installer records the entries it owns in
  `install-manifest.json`, so reinstall and `uninstall` touch only those. Codex loads project
  hooks only in a trusted project after you review them with `/hooks`.
- **Access classes.** Every role now has one of `read-only`, `research`, `review`,
  `workspace-write`, or `orchestrate`, compiled into each harness's native tool or permission
  settings. Review roles (qa-lead, code-reviewer, security-engineer, …) can now run commands and
  record evidence but may write only under `.agentic-team/runs/`; orchestrators get the
  delegation tool. See [harnesses](harnesses.md).
- **Model profiles.** Roles now carry a tier, and the default profile `balanced` maps tiers to
  models and effort (on Claude Code: deep roles inherit your model with high effort, standard
  roles use `sonnet`, fast roles `haiku`). To keep v2 behaviour, where every role inherits the
  session model, install with `--model-profile inherit`:

  ```bash
  python scripts/agentic_team.py install ~/projects/app --harness claude-code --preset full-platform --model-profile inherit
  ```

- **Antigravity.** Antigravity retires `.agents/workflows/` on 2026-11-01. v3 no longer emits
  workflows; the same entry points are skills under `.agents/skills/` (`agentic-execute-plan`
  and `agentic-resume` included), which Antigravity exposes as commands. Reinstall before that
  date.
- **Helpers moved into the CLI.** Installed projects get `.agentic-team/bin/` with the state CLI
  and helpers; call them as `preflight`, `findings-to-tasks`, `design-to-admin`, and `llm-check`
  subcommands. Installed skills and protocols point at `.agentic-team/bin/agentic_team.py`.
- **Removing an install.** `uninstall` removes generated files, managed blocks, installed
  skills, and the installer's settings entries; it keeps `knowledge/` and `runs/` unless you
  add `--purge`.

## 2. Migrate a v2 run

Until you migrate it, v3 refuses to work on a v2 run: `status`, `doctor`, `runs`, `log`, and
`close-run` still work, and the other run commands (`add-task`, `claim`, `checkpoint`,
`approve`, `advance`, `next`, `board`, …) stop with "the human runs `migrate` … first".

The v2 owner token file is `~/.agentic-team/owner-tokens/<run-id>.token` (no `<uid>` part). In
your own terminal, in the project folder:

```powershell
py -3 .agentic-team/bin/agentic_team.py migrate --project . --run <run-id> --by "Your Name" --token-file "$HOME\.agentic-team\owner-tokens\<run-id>.token"
```

```bash
python3 .agentic-team/bin/agentic_team.py migrate --project . --run <run-id> --by "Your Name" --token-file ~/.agentic-team/owner-tokens/<run-id>.token
```

`migrate` is a human command (it needs the token) and:

1. binds the owner key outside the project (`~/.agentic-team/runs/<run-id>.json`);
2. signs the run's past decisions (approved, rejected, resolved checkpoints and cancellations)
   into the decision ledger `~/.agentic-team/ledger/<run-id>.jsonl`;
3. moves the events from `state.json` into the hash-chained `events.jsonl`;
4. replaces the legacy `blocked` status with the v3 run status, gives old tasks
   `action: build` / `target: local`, and upgrades the state version.

It prints each step. Afterwards `doctor` should print `OK`, and `audit verify` should report the
migrated decisions. The token file keeps its v2 name; keep using it for that run. New runs use
`<run-id>.<uid>.token`.

## 3. CLI changes

- **Exit codes.** `0` success, `1` error, `2` stopped at a human gate, `3` run blocked (an
  unresolved rejection or an exhausted task), `64` usage error. In v2 every error exited 2.
- **Owner token.** Pass it with `--token-file PATH`, `--token-stdin`, or the hidden prompt.
  `--token VALUE` still works but warns, because it lands in shell history. Tokens are keyed by
  `<run-id>.<uid>`.
- **`add-task`.** `--action` (for example `build`, `test`, `docs`, `migrate`, `deploy`,
  `publish`) and `--target` (`local`, `ci`, `staging`, `production`, `external`) declare what the
  task does and where; risk is derived from them (default `build`/`local`), and `--risk` can only
  raise it. The stage defaults to the current stage and may not be an earlier one. Build tasks
  owned by a writing role in `04_build` need at least one `--path` (or `--exclusive`). `--check
  CMD` adds an acceptance command; `--verifies T` marks a verification task that T's builders
  may not claim.
- **`complete`.** Evidence is typed: `file:<path>` (must exist; hashed), `cmd:<exec-id>` (an
  `exec` record), `commit:<sha>`, `url:<url>`, `note:<text>`. Write tasks need at least one
  `file:`, `cmd:`, or `commit:`; `--run-checks` runs the task's `--check` commands first.
  Untyped text counts as a note.
- **`claim`.** The claimant must be installed and be the task's owner, and the task must be in
  the current stage; `max_concurrent_agents` is enforced.
- **Human-only.** `cancel` and reopening a failed, cancelled, or completed task (or
  `--extend-retries`) now need `--by` and the owner token. An orchestrator may still `reopen` a
  wedged claim.
- **Rejections.** A rejection blocks the run until the human runs `resolve --checkpoint CP
  --resolution ...`; approving another checkpoint no longer clears it.
- **New commands:** `resolve`, `waive`, `renew`, `reassign`, `exec`, `next`, `board`, `pack`,
  `brief`, `runs`, `switch-run`, `close-run`, `log`, `metrics`, `audit verify`, `migrate`,
  `promote`, `uninstall`, `guard`, `docs`, `preflight`, `findings-to-tasks`, `design-to-admin`,
  `llm-check`. Full reference: [CLI](cli.md).
- **`report`** writes `DELIVERY-EVIDENCE.md` and never overwrites the ceo's `DELIVERY-REPORT.md`.
- **`--run`** operates on another run without repointing `CURRENT.md`; use `switch-run` for that.

## 4. Checkpoint changes

- Agents create `decision`, `deviation`, `injection`, and `budget` checkpoints only, and each
  needs `--alternatives`, `--impact`, `--evidence`, and `--rollback` besides the question and
  recommendation.
- `stage` and `risk` checkpoints are written by the CLI itself, with factual content, when
  `advance` or `claim` reaches a human gate. An agent can no longer author the text of the gate
  that blocks it.
- Any pending checkpoint blocks `advance`.
- Decisions are appended to the signed ledger; gates read the ledger, not `state.json`.

## 5. Stages now have exit contracts

`advance` checks each stage's required artifacts (policy data in `config/policies.json` →
`stage_exits`): for example `BRIEF.md` and `ASSUMPTIONS.md` for intake, `PRD.md` with `AC-` ids,
a `READINESS.md` that traces every `AC-` id, and `VERIFICATION.md` headed by `Verdict:`,
`Verifier:`, and `Verified-SHA:` lines from a verifier who did not build. Files still containing
template markers do not count. Create artifacts with `scaffold --artifact NAME`; the human can
waive one named requirement with `waive --requirement stage-exit:<stage>:<check>`. Details:
[workflow](../protocols/workflow.md).

## 6. Known limitations

- Hooks and deny rules are not a sandbox: code running unsandboxed as your user can still read
  `~/.agentic-team`. The ledger and event chain make tampering evident, not impossible. Claude
  Code's sandbox runs on macOS, Linux, and WSL2, not native Windows
  ([harness security](../protocols/harness-security.md)).
- Antigravity hooks and Gemini CLI `policy.toml` rules are not emitted (their formats are not
  verified). Antigravity, Pi, and generic installs have no harness enforcement.
- On OpenCode, `edit: deny` does not stop writes through `bash`; review-role source protection
  is instruction only there.
- Fusion proposal privacy is enforced by the guard hook on Claude Code only; elsewhere it is an
  instruction, and rewrites are detected at reveal only for proposals submitted with `--file`.
- `fail` takes a `--reason`; repeated-failure fingerprints that escalate instead of retrying are
  not implemented.
- Tasks still live in `state.json` (about 0.7 KiB each); only events moved out.
- Token and USD budgets see only the usage agents report with `complete --usage`.
- `adaptive` runs need no `RELEASE.md`; the human release checkpoint still applies.
- Agent identity is self-declared: the CLI checks that a claimant is the installed owner, not
  which model is actually calling.
- The live-agent smoke evaluation is documented but not automated; it needs model credentials.
  `evals/run_scenarios.py` runs the deterministic scenarios.
