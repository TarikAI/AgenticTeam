# Agent Evolution Changelog

Applied Level-3 changes (see `.agentic-team/protocols/evolution.md`). This is the audit trail of how the
team's constitution changed and why. Append-only.

## Format

```
## YYYY-MM-DD
- **<agent-name>** — <what changed> (proposal P-00X, approved by <human>)
  evidence: <short>
```

---

## 2026-10-27 - unattended profile: an executable release gate for low-risk runs

A fourth autonomy profile, `unattended`, for supervisors that run issue-to-release loops with
nobody clicking (`config/guarantees.json`: G16 reworded, G19, new G20); approved by the human owner.

- **`unattended` is `autonomous` with `release_gate: executable`.** For a run with no task above
  R1, `advance` leaves 06_release without a human checkpoint when five executable conditions
  hold, each refused by name otherwise: the exit contract including `verified-head`; a passing
  `exec` record for every `--check` of every completed 04_build and 05_verify task (a check-less
  writing task only with the human's `checks:<task>` waiver); no task in the run above R1 (one
  R2+ task puts the human checkpoint back, as a `stage` checkpoint naming it); `RELEASE.md`
  without template markers plus a completed `--action rollback-test` task by `release-manager` or
  `devops-engineer` whose declared rollback command passed at the current HEAD; no `budget`
  checkpoint pending. The exit is logged as `release-conditions-met` with the facts it rested on.
- **What stays human.** R3/R4 actions (production deploys, publishing, messaging, spending,
  credentials, destructive operations) keep their risk checkpoints in every profile; `unattended`
  removes only the click on the release stage of R0-R1 work, needs a spend ceiling like
  `autonomous`, and `policies.local.json` can set its `release_gate` back to `human`.
  `release_gate: "executable"` on any other profile, or an unknown gate value, is refused by
  `validate` and by every command of an installed project (`policy_problems`).
- **New action `rollback-test`** (R1 on local and ci, R2 on staging, R3 on production and
  external) is the rehearsal convention; release-manager and devops-engineer document it.
- Tests: `tests/test_unattended.py` (every refusal, the passing path, the R2 fallback, the
  tightening), `test_authority.RiskModelTests.test_hard_gates_hold_under_unattended`, and the
  `unattended-release` eval scenario.

## 2026-10-27 - evidence gates for unattended runs

Four gaps a review of unattended operation found, each now refused by the CLI and covered by a
test (`config/guarantees.json` G10, G13, G18, G19); approved by the human owner.

- **Checks are no longer optional for build work.** `add-task` refuses a build or remediation
  task owned by a writing role without `--check` (`evidence.write_tasks_need_checks`), and
  `complete` runs every declared check that has no passing record at the current HEAD, so a
  file or a note alone no longer completes workspace-changing work. Tasks recorded before this
  rule complete only with the human's `waive --requirement checks:<task>`.
- **The verdict names the code being released.** `Verified-SHA` must equal the current HEAD at
  the 05_verify exit (the integration commit no longer counts once HEAD moved), and the new
  `verified-head` exit check refuses to leave 06_release if HEAD moved after the verdict.
- **Unattended runs need a ceiling, and the ceiling sees metered usage.** `autonomous` and
  `supervised` runs refuse to start without a `tokens` or `usd` ceiling
  (`profiles.<name>.require_budget_ceiling`; `init-run --budget` sets one per run). The new
  `usage --transcript` command records what the harness itself reported (Claude Code
  `stream-json`/`json` result message), hashed and signed into the ledger by the owner side;
  the larger of reported and metered usage counts against the ceiling.
- **The live smoke eval runs the acceptance criteria.** Its scorer executes `greet("World")`
  and `python -m unittest discover -s tests`, requiring at least one test to run, instead of
  checking that the files exist; it also meters the session's transcript against a 5 USD ceiling.

## 2026-09-25 - v3.0.0 upgrade

Applied from `docs/v3-upgrade-plan.md` (phases P0-P9; progress and deviations in
`docs/v3-progress.md`), approved by the human owner. Every defect row R-01..R-39 has a
regression test.

**Authority and safety**
- Human decisions are HMAC-signed into a ledger outside the project and bound to an owner key;
  gates read the ledger, so an edited `state.json` approves nothing (`audit verify` detects
  tampering). Tokens are passed by file, stdin, or prompt, never argv.
- Risk comes from `--action`/`--target`, raised by sensitive paths and a word-boundary
  backstop; only a human `waive` lowers it. Policy command rules feed `exec`, the harness guard
  hook, and OpenCode permission maps.
- Stage and risk checkpoints are CLI-authored; agent checkpoints must carry alternatives, impact,
  evidence, and rollback. `supervised` differs from `autonomous` (deviations pause).

**Runtime correctness**
- Rejections resolve (`resolve`); cancel/reopen are human decisions that actually unblock;
  Fusion phases, independence, and commit-reveal are enforced; claims need the installed owner,
  the current stage, owned paths, and the concurrency cap; `--run` no longer repoints
  CURRENT.md; exit codes 0/1/2/3/64; Windows replace retries; word-based specialist routing.
- Stage exit contracts, typed evidence with `exec` capture, `--check` acceptance commands,
  verifier independence, integration SHA.
- `events.jsonl` hash chain, `log`, `metrics`, budgets, `next`, `board`, `pack`, `brief`.

**Finishing items (2026-09-26)**
- A task that fails the same way twice stops retrying (`failure-repeated`); only the human reopens it.
- Guard hooks for Antigravity (`.agents/hooks.json`) and Gemini CLI (`.gemini/settings.json`).
- `package-claude-plugin` builds a validated Claude Code plugin and marketplace.
- First reinstall over a v2 install backs up every previously generated file.
- Opt-in live-agent smoke eval (`evals/live_smoke.py`) with offline-tested scoring.

**Harnesses and roster**
- Access classes (read-only, research, review, workspace-write, orchestrate), model profiles,
  skill preloads, settings/hook merge, guard hook, `uninstall`, local-edit protection; six new
  targets (Copilot, Cursor, Factory, Kiro, Qwen Code, Junie); Antigravity workflows became
  skills ahead of their 2026-11-01 retirement.
- All 50 roles rewritten: specialist skeleton, single artifact/verdict ownership, descriptions
  with trigger and exclusion clauses, v1 vocabulary removed, Standing orders removed.
- Shared law aligned with the runtime; eight new protocols; skills are runbooks; learning loop
  with candidate/proven/baseline and a human `promote`; six deterministic eval scenarios in CI.

## 2026-08-19 - Audit remediation (v2.0.1)

Applied after a full repository audit. Every item below was reproduced before the fix and
re-verified after it.

**Safety**
- Checkpoint decisions now require the run's owner token, issued by `init-run` and stored
  outside the project at `~/.agentic-team/owner-tokens/<run-id>.token`. `--by` may not name an
  installed agent. Previously any agent could approve the R4 gate that was blocking it.
- Task risk is derived from what the task says it does; the declared `--risk` is a floor
  request, not a promise. A task titled "deploy to production" labelled R1 is raised to R3.
- A human rejection now actually blocks: claims and stage advances are refused while a run is
  `blocked`, and approving one checkpoint no longer clears an unrelated rejection.
- `advance` exits 2 at a human gate, so `advance && next-step` stops instead of walking through.

**Harness compilation**
- Antigravity: roles moved to `.agents/agents/<id>.md` with required frontmatter, rule gained
  `trigger: always_on`, workflows gained `description:`, and a root `AGENTS.md` is written.
  The previous `.agents/roles/` layout was never loaded by the tool.
- Protocol references in compiled prompts are rewritten to `.agentic-team/protocols/...`.
- Read-only roles carry an explicit ACCESS CONSTRAINT paragraph for harnesses without a
  pinned tool vocabulary (Antigravity, Gemini CLI, generic).
- `generic` writes a root `AGENTS.md`; switching harnesses removes the previous skill tree.

**Installer**
- `install.sh` probes for a Python that actually runs. On Windows `python3` resolves to the
  Microsoft Store stub, so every install failed with exit 49.

**Role definitions**
- All 50 roles moved to v2 vocabulary: state CLI instead of PLAN.md, task evidence records
  instead of STATUS.md, VERIFICATION.md instead of QA.md, stage names instead of "Phase N",
  DELIVERY-REPORT.md instead of FINAL-REPORT.md, with a single owner for the report.
- The per-role playbook loop now lives in `agent-contract.md`, which every compiled agent
  points at, so it survives compilation. It was previously stripped and reached no agent.
- The 18 specialists gained the standing-orders block the other 32 already had.

**Tests and CI**
- 42 -> 50 tests. Adapter expectations are literals rather than being read back out of
  `team.json`, plus new tests for native conventions, gate self-approval, risk derivation,
  blocked runs, protocol reference resolution, documented role counts, and gate coverage.
- CI runs on Windows and Ubuntu across two Python versions and performs real installs of all
  seven harnesses. It previously only syntax-checked the installer, which is why the Windows
  bug shipped.

**Documentation**
- Corrected the role count, split the CLI reference into compiler vs run invocations, fixed
  the generic router path and the local-LLM tier table, and documented that unlisted harnesses
  (zcode, Cursor, Windsurf, in-house runners) use `--harness generic`.

Not changed: `.opencode/agents/` is correct as-is. An audit pass claimed it should be
singular; the current OpenCode documentation specifies the plural form.

## 2026-08-14
- **system** — Baseline: 31 agents, 10 protocols, evolution + playbook system established.
  evidence: initial build of the AgenticTeam system.
