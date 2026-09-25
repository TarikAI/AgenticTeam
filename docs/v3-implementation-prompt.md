# AgenticTeam v3 — implementation prompt

Paste everything below the line into a coding agent (Codex CLI, Claude Code, or similar) opened
at the repository root. It is written to be executed across several sessions; the progress file
makes it resumable.

---

You are the implementation engineer for the **AgenticTeam v3 upgrade** in this repository.
AgenticTeam is a portable AI delivery organization: 50 role files compiled into seven coding
harnesses' native formats, a deterministic stdlib-Python state CLI (`scripts/agentic_team.py`),
shared protocols, skills, templates, and tests. An audit on 2026-09-25 catalogued 39 runtime
and compiler defects (R-01…R-39, most of them reproduced) and found that the documentation
promises guarantees the code and harness do not enforce. Your job is to make every documented guarantee either enforced and tested, or
explicitly labelled "instruction only", and to deliver the role, protocol, skill, and harness
upgrades in the plan.

## 1. Authority and resumption

1. `docs/v3-upgrade-plan.md` is the authoritative scope and design. Section references below
   (§3.1, §5.4, Appendix B.2, …) point into it. If this prompt and the plan disagree, the plan
   wins. If the plan and the code you observe disagree, stop and report the difference before
   changing either.
2. Before any work, read `docs/v3-progress.md`. If it does not exist, create it with a table:
   `Phase | Branch | Status | Commits | Acceptance evidence | Deviations`. Update it at the end
   of every phase and whenever you stop. A fresh session must be able to resume from it alone.
3. Then read, in order: `docs/v3-upgrade-plan.md` (whole), `README.md`,
   `docs/architecture.md`, `docs/cli.md`, `scripts/agentic_team.py` (whole),
   `tests/test_runtime.py`, `tests/test_bridges.py`, `config/policies.json`, `team.json`,
   `protocols/agent-contract.md`, `protocols/autonomy.md`, `protocols/runtime.md`.

## 2. Non-negotiables

These invariants were defects once. Breaking any of them fails the upgrade:

- `scripts/install.sh` must probe for a Python that actually executes (the Windows `python3`
  Store stub passes `command -v`, then exits 49). Give `scripts/install.ps1` the same probe
  with a `py -3` fallback.
- Checkpoint decisions require the owner's authority (token), `--by` may never name an
  installed agent, and task risk is derived by the runtime, never trusted from the caller.
- Antigravity roles live at `.agents/agents/<id>.md` with frontmatter; the rule has
  `trigger: always_on`; a root `AGENTS.md` is written; `.agents/roles/` is not read by the
  tool. (Workflows become skills in P1 — R-38.)
- `.opencode/agents/` (plural) is correct. Do not change it.
- Compiled prompts rewrite `protocols/x.md` to `.agentic-team/protocols/x.md`; inside
  `protocols/` references use bare sibling filenames.
- `compact_agent_body` strips `## Standing orders`. Anything every agent must know belongs in
  `protocols/agent-contract.md`.
- Adapter and golden tests assert **literal** paths and values. Never derive expected values
  from `team.json` or from the code under test.
- v2 vocabulary only: stage dirs `00_intake`…`07_learn`, `DELIVERY-REPORT.md`,
  `VERIFICATION.md`, evidence through the state CLI. Never reintroduce `PLAN.md`, `STATUS.md`,
  `QA.md`, or "Phase N".
- The runtime is stdlib-only Python, supports 3.10+, makes no network or model API calls, and
  stores no secret other than the owner token. Tests may use 3.11+ modules only behind a skip.
- Windows is a first-class platform. Remember that `Path.home()` on Windows reads
  `USERPROFILE`, not `HOME`.
- Never weaken, skip, or delete a gate, check, or test to make something pass. Never make a
  human-only action performable by an agent.

## 3. How to work

- **Branches.** Create an integration branch `v3` from `main`. Do each phase on
  `v3/p<N>-<slug>` branched from `v3`, and merge it back into `v3` only when the phase is
  green. Do not push, open PRs, merge into `main`, or tag unless the human asks.
- **Test-first for defects.** For every defect ID in §3.1, first write a regression test that
  fails on the current code and names the ID (`test_R07_cancel_unblocks_stage`), then fix it.
  Put these in `tests/test_regressions.py`. Use `AGENTIC_TEAM_HOME` (after P0) or temporary
  `HOME` and `USERPROFILE` so no test touches the real home directory.
- **One home per fact.** A commit that changes behavior also updates, in the same commit, the
  protocol, skill, template, and doc text that describes that behavior. Run the doc↔CLI
  consistency test before every commit.
- **Harness formats.** Before changing an emitter, check the harness's current official
  documentation. Record the URL and verification date in `docs/harnesses.md` and in a comment
  on the emitter. If you cannot verify a field from a primary source, do not emit it, and list
  it in the phase report. If you have no web access, treat plan Appendix A (verified
  2026-09-25) as the baseline, add nothing beyond it, and say so in the report.
- **Scope.** Keep each diff inside its phase. Put adjacent problems in the progress file under
  "Follow-ups" rather than fixing them.
- **Verification after every phase.** Run and paste the results of:
  ```
  python scripts/agentic_team.py validate
  python -m unittest discover -s tests
  python scripts/agentic_team.py preflight        # scripts/preflight_skills.py until P1 lands
  ```
  plus the phase's acceptance commands. On Windows also run the `install.ps1` smoke install; on
  POSIX run the `install.sh` loop from `.github/workflows/ci.yml`.
- **Parallelism.** If your harness supports subagents (for example, Claude Code), you may
  split P6 by department and P7 by protocol file. Each subagent gets the relevant plan
  sections and must not touch files outside its slice. Review and integrate its output
  yourself. Otherwise, work sequentially.

## 4. Phases

Do the phases in order. P6 may start after P1 is merged. P7's runtime-describing text lands
with the runtime change; the rest of P7 starts after P3.

### P0 — Safety net
1. Add `AGENTIC_TEAM_HOME` (default `~/.agentic-team`) and use it for owner tokens and every
   future out-of-project file. Isolate all tests from the real home (fixes R-31).
2. Add `tests/helpers.py` with `fresh_project(preset, harness)` and `run_cli(*args)`, which
   runs the installed CLI as a subprocess and returns (exit code, stdout, stderr).
3. Add golden snapshots: compile the roster `ceo, fullstack-engineer, qa-lead, research-agent,
   sre-engineer` for every harness into `tests/golden/<harness>/…`, compare byte for byte, and
   regenerate with `UPDATE_GOLDEN=1`. Normalize timestamps.
4. Add a doc↔CLI consistency test: every `agentic_team.py <command>` and `--flag` mentioned in
   `README.md`, `docs/`, `skills/`, `protocols/`, and `agents/` must exist in `build_parser()`.
   Mark the currently broken mentions as known failures, each with its fix phase.
5. CI: add `macos-latest`; Python 3.10 (runtime subset), 3.12, 3.14; bump
   `actions/checkout`, `actions/setup-python`, and `actions/setup-node` to their current
   majors (look them up); use Node 22 or newer for the OCR job.
6. Accept when the suite is green, the golden files are committed, and a test proves nothing
   was written under the real home.

### P1 — Runtime correctness
Fix these, each test-first, with the behavior in §5.2, §5.7, §5.13, and §5.14:
- **Fusion.** R-01: each submission kind is accepted only in its phase. R-03: no resubmission;
  one `revision` per contributor during `critiques`. R-04: moderator ≠ verifier. R-02: a
  human-owner sponsor needs owner authority to close (use the existing token check now; the
  ledger comes in P2).
- **Rejections.** R-05: add `resolve --checkpoint --by --resolution` (human). Split
  `blocked-rejection` from `blocked-failure` (R-15).
- **Cancel and reopen.**
  - R-07: `cancel` is human-only. Cancelled tasks are closed for `advance`. Cancel refuses
    while dependents are open, unless `--cascade` is given.
  - R-08 and R-09: `reopen` works on failed, cancelled, or wedged tasks. Reopening a completed
    task, or extending the retry budget, is human-only. Keep the attempt history, and clear
    the claim fields correctly.
- **Tasks and advance.**
  - R-11: `add-task` defaults to the current stage and refuses earlier stages.
  - R-14: any pending checkpoint blocks `advance`, and `advance` never overwrites
    `waiting-human`.
  - R-16: the claimant must be installed and must be the owner, unless a recorded `reassign`
    says otherwise. Enforce `max_concurrent_agents` from the profile.
  - R-18: write tasks in `04_build` need at least one `--path`, or `--exclusive`.
- **Runs and CURRENT.md.** R-19: only `init-run` and the new `switch-run` change
  `CURRENT.md`. Add `runs` and `close-run`.
- **Exit codes.** R-21: `0` ok, `1` error, `2` human gate, `3` blocked, `64` usage (override
  `ArgumentParser.error`). Introduce a `GateError`.
- **Windows.** R-22: retry `os.replace` on `PermissionError` with backoff, up to about 2 s.
- **Routing.** R-23: match words and phrases, not substrings. Apply the vocabulary in
  Appendix B.5 and add `tests/test_routing.py` with positive and negative phrases.
- **Doctor and reports.**
  - R-26: `doctor` reports blocked runs, pending checkpoints, expired leases, version
    mismatches, and generated-file drift.
  - R-27: record refused authority attempts as events.
  - R-28: `report` writes `DELIVERY-EVIDENCE.md` and never overwrites `DELIVERY-REPORT.md`.
- **Installed-copy detection.** R-29: detect an installed copy by its location
  (`.agentic-team/bin/`).
- **Defaults and presets.** R-30: set `team.json` `defaults.entry_mode` to a valid value.
  R-36: add a verifier to `fusion-product-council`.
- **Helpers.** R-32 and R-33: move `preflight_skills.py`, `findings_to_tasks.py`,
  `design_to_admin.py`, and `local_llm_check.py` into CLI subcommands (`preflight`,
  `findings-to-tasks [--apply] [--shell bash|powershell]`, `design-to-admin`, `llm-check`), and
  keep thin wrapper scripts.
  - `preflight` exits non-zero when a skill named as required is missing.
  - `findings-to-tasks` emits commands that actually run. It resolves owners to installed
    writable roles, never to `code-owner` or a read-only role, defaults to the current stage,
    and quotes correctly for the chosen shell.
  - Rewrite `scripts/…` references in installed skills, protocols, and roles to
    `.agentic-team/bin/agentic_team.py <subcommand>`.
- **Unread config.** R-25 (config part): read `max_concurrent_agents` now. Either use or delete
  every other unread manifest key; if emitters read harness dirs from `team.json`, tests still
  assert literal paths.
- **install.ps1.** R-34: add the interpreter probe.
- **Emitter fixes.**
  - R-37: make the Codex TOML string escaping safe, using `'''` literal strings or proper
    escaping, with a test that includes a backslash.
  - R-38: convert the six Antigravity `.agents/workflows/*.md` files into skills under
    `.agents/skills/<name>/SKILL.md`. Remove stale workflow files on reinstall.
  - R-39: set Antigravity `mainAgent: false` except for the lead roles, and give the rule a
    `description:`.
- **Also add:** `renew` (lease extension) and `reassign`.

**Deadline.** Antigravity retires workflows on **2026-11-01**. If P1 cannot be merged before
then, first ship R-38 alone as a `v2.0.2` hotfix branched from `main`, and tell the human.

**Accept when:**
- every listed ID has a passing regression test;
- a test executes `findings-to-tasks` output against a fresh install and all generated tasks
  exist;
- `doctor` fails on a blocked run.

### P2 — Authority, risk, audit
- **Ledger.** Implement §5.3.
  - Keep an append-only decision ledger at `$AGENTIC_TEAM_HOME/ledger/<run-id>.jsonl`. Each
    record carries an `HMAC-SHA256(owner_token, canonical JSON)` and the hash of the previous
    record.
  - `claim` and `advance` read approvals from the ledger, not from `state.json`.
  - Bind the owner key in `$AGENTIC_TEAM_HOME/runs/<run-id>.json`; on a mismatch, fail
    closed.
- **Token input.** Accept `--token-file`, `--token-stdin`, and a hidden interactive prompt.
  Keep `--token` with a deprecation warning. `init-run` never prints the token.
- **Audit.** Add `audit verify` (human; recompute the MACs and the chain) and `waive` (human;
  a named stage-exit requirement or risk floor, with a reason). Make fusion-close for a human
  sponsor go through the ledger.
- **Checkpoints.** Only the CLI creates `stage` and `risk` checkpoints, with CLI-generated
  factual content. Agent checkpoints (`decision`, `deviation`, `injection`, `budget`) require
  `--alternatives --impact --evidence --rollback` (R-13).
- **Supervised profile.** R-12: `supervised` pauses on `deviation` checkpoints. Read every
  `*_gate` key from policy, and remove the hard-coded gate tables at lines 652-656, 939, and
  1231-1232.
- **Risk model.** Implement §5.4 (R-20):
  - `--action` and `--target`, `risk.matrix`, `risk.path_rules`, a word-boundary backstop that
    only raises risk, and `command_rules`;
  - lowering risk only through a human `waive`;
  - one R0–R4 definition, in `policies.json`; global installs are R4.
- **Token docs.** R-35: update docs so the token never appears in argv examples.
- **Migration.** `migrate` bootstraps a ledger for v2 runs, carrying pending decisions only.

**Accept when:**
- tests show that swapping the stored hash and injecting an approval into `state.json` both
  fail closed;
- `audit verify` flags an edited ledger line;
- the risk corpus classifies as expected. From the audit: "Write consumer contract tests for
  orders API", "Build payment form UI with client-side validation", "Truncate long product
  titles in card component", "Purge unused CSS", "Publish domain event to in-process bus",
  "Screen reader should announce form errors", "Add billing page skeleton", and "POST to
  /api/users handler" are all ≤ R2 as `build/local`; `deploy/production` and any text
  containing `vercel --prod`, `terraform apply`, `kubectl apply`, or `git push --force` are
  ≥ R3;
- a test shows `supervised` and `autonomous` behaving differently.

### P3 — Evidence and stage exits
- **Stage exits.** Implement §5.5 with `policies.json.stage_exits`: artifact checks, verdict
  lines, template-placeholder detection, `skipped_by_entry` / `no-work` records, and pending
  specialist obligations (R-10).
- **Evidence.** Implement §5.6: typed evidence, `exec` capture, `add-task --check`,
  `complete --run-checks`, and `commit:` resolution when git is present (R-17).
- **Verification independence.**
  - `add-task --verifies T…`;
  - a builder cannot claim a task that verifies its own work;
  - the verifier is not among the 04_build claimants;
  - `Verified-SHA` must equal the recorded integration SHA.
- **Templates.** Add VERIFICATION, READINESS, RELEASE, ADR, RISKS, checkpoint, handoff,
  RETROSPECTIVE, BRIEF, PRD, and fusion-dissent templates. Regenerate CONTEXT.md status on
  every transition, and render exit criteria from the policy rows.

**Accept when:**
- the "00→06 with nothing" scenario is refused at the 00 exit;
- a missing or invalid `Verdict:` line blocks the 05 exit;
- a builder self-verification is refused;
- `complete --run-checks` records exit codes and refuses on failure.

### P4 — Events, budgets, ergonomics
- **Events.** Implement §5.8: `events.jsonl` with a hash chain, `log`, `metrics`, and
  `budgets` (checkpoint at 80 %, stop at 100 %).
- **Ergonomics.** Implement §5.9: `next`, `board`, `pack`, `brief`, and `status --brief`.
  `migrate` moves v2 events.

**Accept when:**
- a 200-task run keeps `state.json` under 40 KiB;
- `pack` for a fixture task lands within 2K–8K tokens;
- an edited event breaks the chain check.

### P5 — Harness compilers
Implement §5.10–§5.12 and Appendix A:
- **Access and models.** The access model (`read-only`, `research`, `review`,
  `workspace-write`, `orchestrate`) mapped per harness, and model profiles (`inherit`,
  `balanced` default, `max-quality`, `economy`).
- **Claude Code agent files.**
  - `skills` preload per role (qa-lead → agentic-verify; fusion-moderator → fusion-council;
    ceo and delivery-lead → agentic-build; context-engineer → bmad-progressive);
  - the `Agent` tool for orchestrate roles;
  - tool sets per access from Appendix A.3. Review roles get Read, Grep, Glob, Bash, Write,
    Edit, WebSearch, and WebFetch, plus a subagent-scoped `PreToolUse` hook that denies
    Write/Edit outside `.agentic-team/runs/**` and the role's own playbook. Research roles get
    WebSearch and WebFetch;
  - `color` by department;
  - the router imported with `@.agentic-team/AGENTS.md` in the CLAUDE.md managed block, and
    inlined (≤ 25 lines) for harnesses without imports.
- **Settings and guard.** Merge `.claude/settings.json` (deny rules plus the `PreToolUse`
  guard hook) without clobbering user settings; track the installer-owned entries in
  `install-manifest.json`; keep a backup. Add the `guard` subcommand.
- **Other harnesses** (§5.12, Appendix A):
  - OpenCode: permission pattern maps instead of a blanket `bash: ask`.
  - Codex: `model_reasoning_effort` and `sandbox_mode` per access, plus the guard in
    `.codex/hooks.json`. Say in the install output that project hooks need trust and a
    `/hooks` review.
  - Gemini CLI: `tools` allowlists. Its frontmatter schema is strict, so emit only allowed
    keys.
  - Pi: prompt frontmatter.
- **P5b new targets**, only after P5 is green, each with golden snapshots and literal-path
  tests: GitHub Copilot and Cursor first, then Factory Droid, Kiro (which also copies skills to
  `.kiro/skills/`), Qwen Code, and Junie. Verify each against Appendix A.2 and current docs.
- **Skills.** In `agents/openai.yaml`, set `policy.allow_implicit_invocation: false` for
  fusion-council, agentic-learn, and agentic-build.
- **Accept when:**
  - golden diffs are reviewed and committed;
  - every emitted field is backed by Appendix A;
  - in a Claude Code install:
    - the guard denies `Read` of `~/.agentic-team/owner-tokens/x.token` (fed a synthetic hook
      payload);
    - a review role's frontmatter allows Bash but denies edits outside the run folder;
    - `doctor` runs a hook self-test.

### P6 — Roster
Apply Appendix B.1–B.6, B.8, and §3.4:
- **Specialists.** Rebuild all 18 specialists on the B.3 skeleton, at 450–800 tokens each.
  Add the concrete procedures in B.8.
- **Ownership.** Give every artifact and verdict the owner in B.2, with one verdict
  vocabulary.
- **Descriptions.** Rewrite them with trigger and exclusion clauses, starting from the drafts
  in B.4.
- **Vocabulary.** Purge the B.1 terms from roles, protocols, knowledge, and playbooks, and
  replace the `lessons.md` learning path.
- **Standing orders.** Delete them from all 50 sources. Move the rules that would otherwise be
  lost ("never improvise a path", the plan-modes pointer, the bounded-question-list format, the
  three-line deviation format, the "Closing a build" duties) into
  `protocols/agent-contract.md` and the relevant Output contracts.
- **Overlaps and reporting.** Split growth vs analytics, eval vs ai-ml, and the runbook owner.
  Fix reporting lines and re-tier per B.6.
- **Security and supply chain.** Fold AI/agent security (OWASP Top 10 for LLM Applications,
  injection suites) and supply-chain duties into security-engineer, eval-engineer,
  devops-engineer, and compliance-advisor.
- **Cleanup.** Cut persona filler; update WCAG to 2.2.
- **Roster size.** Keep all 50 ids. Shrink context-engineer and fusion-moderator to pointers
  plus a skill preload.
- **Tests.** Add `tests/test_roster.py`, covering banned vocabulary, specialist headings,
  description rules, role-id references, single artifact ownership, compiled size 400–2,500
  tokens, and no Standing orders.
- **Accept when:** roster lint and routing tests are green and the golden diffs are reviewed.

### P7 — Protocols, skills, templates, knowledge
- **New protocols.** `untrusted-content.md`, `source-control.md`, `supply-chain.md`,
  `secrets-and-sensitive-data.md`, `budgets.md`, `team-observability.md`,
  `team-evaluation.md`, and `harness-security.md` (threat model, per-harness enforcement
  table, and sandbox guidance: Claude Code's sandbox supports macOS, Linux, and WSL2, not
  native Windows). Their required contents are in Appendix B.7. Wire `untrusted-content.md`
  into `agent-contract.md` and the router.
- **Rewrites.** Rewrite `autonomy.md`, `runtime.md`, `workflow.md`, `fusion.md`,
  `evolution.md`, `guardrails.md`, `final-report.md`, and `specialist-routing.md` to match
  P1–P4. Keep one hard-gate list and include it by reference.
- **Skills.** Turn the five skills into runbooks per Appendix B.9: exact CLI sequences,
  exit-code branches, stop conditions, bundled scripts, and `compatibility:` frontmatter,
  with no restated protocol prose.
- **Knowledge loop.**
  - Playbook entries get a status (`candidate|proven|baseline`) and a source run; agents add
    candidates only.
  - `learn` gains `--roles --trigger --confidence --task`, and a human `promote` step is added.
  - Relabel the seeded playbooks as `baseline`, and remove the fabricated evidence line in
    `knowledge/lessons.md`.
- **Accept when:**
  - the drift tests pass (hard-gate lists match policy; every template is referenced and
    present; no v1 terms);
  - each skill's command sequence runs in a test against a fresh install.

### P8 — Team evaluation
- **Scenarios.** Add `evals/scenarios/*.json`: deterministic scripted runs for greenfield,
  plan-given, execute-only, brownfield fix, Fusion, and rejection/recovery, each asserting
  gates, artifacts, and authority refusals. Run them in CI.
- **Live smoke eval.** Document an optional, opt-in live-agent smoke eval that runs a harness
  headless (for Claude Code: `claude -p … --output-format stream-json`), with credentials only
  in CI secrets.
- **Accept when** the scenarios are green in CI.

### P9 — Docs, migration, release
- **Docs.**
  - The guarantee ledger (`config/guarantees.json` → `docs/architecture.md`), with a test that
    docs never overclaim.
  - `docs/cli.md` generated by `agentic_team.py docs --cli`, with a staleness test.
  - `docs/harnesses.md` with verification dates.
  - A rewritten `docs/quickstart-non-dev.md` covering: prerequisites; the human starts the run
    in their own terminal; where the token lives; PowerShell and bash
    approve/reject/resolve commands that never put the token in argv; "never paste the token
    into chat"; how to stop the team.
  - The README preset table with coverage columns, and `docs/migration-v3.md`.
- **Presets.** Enforce the preset coverage invariants (B.6) in `validate`.
- **Version.** Set 3.0.0 in `VERSION` (in `scripts/agentic_team.py`), `team.json`,
  `policies.json`, and the schemas. Add a CHANGELOG entry, and mark
  `docs/skills-integration-plan.md` as historical.
- **Accept** on the plan's §10 definition of done.

## 5. Stop and ask the human when

- a change would loosen any human gate, hard gate, or risk floor, or let an agent perform a
  human-only action;
- a harness field or path cannot be verified from primary documentation;
- a phase's acceptance criteria cannot be met without changing the plan's design;
- a migration would drop or rewrite existing run data, knowledge, or user settings;
- an existing test would have to be deleted rather than updated;
- you find a defect that is not in §3.1 and is severity High or Critical. Record it, then ask
  whether to fix it in the current phase.

State deviations in three lines: what fails, the smallest fix, and the cost of doing it as
written.

## 6. Report format

At the end of each phase, append to `docs/v3-progress.md` and reply with:

1. **Result:** phase, branch, and commits (hash plus subject).
2. **Fixed:** defect IDs with their regression test names.
3. **Evidence:** the exact commands run and their final output lines (validate, unittest,
   preflight, acceptance commands, install smoke).
4. **Golden diffs:** which snapshots changed and why.
5. **Deviations** (three-line format) and **follow-ups**.
6. **Unverified:** anything you could not verify, especially harness fields.

When P9 is done, finish with a release summary for the human: what changed, the migration
steps for existing installs, which guarantees are now enforced (by layer), and which remain
instruction-only.
