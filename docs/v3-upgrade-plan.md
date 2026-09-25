# AgenticTeam v3 upgrade plan

Status: **implemented** in v3.0.0 (progress, evidence, and deviations: `docs/v3-progress.md`) · planned 2026-09-25 · baseline `main` @ `d0fb6cf` (v2.0.1: 50 roles, 7 harness
targets, 50 tests green on Python 3.14).

Evidence base: four independent audits run on 2026-09-25 (runtime probe, full roster review,
shared-law review, harness-format research) plus the official Claude Code docs. Every row
marked *reproduced* was executed against a scratch install with `HOME`/`USERPROFILE`
redirected. The companion implementation prompt is `docs/v3-implementation-prompt.md`.

---

## 1. Summary

The v2 architecture is right and stays: portable role source compiled to native harness
formats, one deterministic state CLI, numbered stages, path claims, hard human gates, Fusion
councils, and "floor + escalation" for external skills.

The problem is that **the shared law promises more than the code and the harness deliver**:

- **Guarantees that are documented but not enforced:** Fusion ordering and privacy,
  independent verification, evidence-backed completion, stage exit criteria, the
  `supervised` profile, concurrency caps, "single writer" state, risk classification.
- **Human authority can be forged or bypassed:** replacing `owner_token_sha256` in
  `state.json` lets an agent approve its own R3 gate; `fusion-close --sponsor human-owner`
  needs no token; the installer emits no harness rule that stops agents reading the token file.
- **Liveness defects:** one rejection blocks a run forever; `cancel` never unblocks a stage;
  `reopen` resurrects completed tasks and resets the retry budget.
- **The risk classifier is inverted:** 11 of 11 ordinary build tasks were raised to R3/R4
  ("Write consumer contract tests" → R4, "Purge unused CSS" → R4) while 3 of 3 real deploys
  ("vercel --prod", "Ship it") stayed R0.
- **Compiled roles cannot do their jobs:** in Claude Code all 13 read-only roles (qa-lead,
  code-reviewer, security-engineer, research-agent, …) get only `Read, Grep, Glob` — no test
  runs, no `git diff`, no web. Orchestrators get no delegation tool. `tier` is ignored
  (`model: inherit` everywhere). OpenCode asks before every shell command, so autonomy is
  impossible there.
- **Broken tooling:** installed skills tell agents to run `scripts/agentic_team.py` and
  `scripts/preflight_skills.py`, which do not exist in installed projects; the
  findings→remediation bridge emits `add-task` commands that always fail.
- **Roster quality:** the 18 specialists are ~200-token prose stubs; five lifecycle artifacts
  (ASSUMPTIONS, READINESS, RELEASE, RETROSPECTIVE, DELIVERY-REPORT) have no owning role; no
  role uses the PASS/CONDITIONAL/FAIL verdict; search-and-replace residue from the v1→v2
  migration remains in 30+ files; specialist routing is raw substring matching.

**v3 theme: prompts decide, the CLI verifies, the harness enforces — and the docs say exactly
which one backs each guarantee.**

Target outcome: **v3.0.0**, in which every documented guarantee is either enforced by code or
harness configuration and covered by a regression test, or explicitly labelled
"instruction only" in one guarantee ledger.

---

## 2. Keep — invariants that must not regress

These were defects once. The v3 work must keep every one of them true:

1. `scripts/install.sh` probes for a Python that **executes** (the Windows `python3` Store stub
   passes `command -v` and then exits 49). v3 extends the same probe to `install.ps1`.
2. Checkpoint decisions require the owner token; `--by` may not name an installed agent; task
   risk is derived by the runtime, never trusted from `--risk` alone.
3. Antigravity: agents at `.agents/agents/<id>.md` with frontmatter, rule has
   `trigger: always_on`, root `AGENTS.md` required; `.agents/roles/` is not read. (v3 replaces
   the workflows with skills because Antigravity retires workflows on 2026-11-01 — R-38.)
4. `.opencode/agents/` (plural) is correct. Do not "fix" it.
5. Compiled prompts resolve protocol references to `.agentic-team/protocols/...`; inside
   `protocols/` use bare sibling filenames.
6. `compact_agent_body` strips `## Standing orders`; anything every agent must know lives in
   `protocols/agent-contract.md`.
7. Adapter tests assert **literal** paths and values, never values read back from `team.json`.
8. v2 vocabulary: stage dirs `00_intake`…`07_learn`, `DELIVERY-REPORT.md` (ceo),
   `VERIFICATION.md`, task evidence via the state CLI. Never reintroduce `PLAN.md`,
   `STATUS.md`, `QA.md`, or "Phase N".
9. The runtime stays stdlib-only Python, makes no network or model calls, stores no
   credentials other than the owner token, and Windows remains a first-class platform.

---

## 3. Audit findings

### 3.1 Runtime defects

Line numbers refer to `scripts/agentic_team.py` at `d0fb6cf`.

| ID | Defect | Where | Evidence | Severity |
|---|---|---|---|---|
| R-01 | Fusion phase order not enforced: synthesis accepted with zero proposals; status jumps to `verification`; statuses can move backwards | `fusion_submit` 1328-1353 | reproduced | Critical |
| R-02 | `fusion-close --sponsor human-owner` accepted from anyone, no token; `decision.md` stays "draft" | `fusion_close` 1356-1368 | reproduced | Critical |
| R-03 | Fusion proposals overwritable after reveal; critiques accepted before reveal | 1342 | reproduced | High |
| R-04 | Moderator may equal verifier (self-verified synthesis) | `fusion_init` 1281 | reproduced | High |
| R-05 | A rejection is terminal: no command resolves it; approving a follow-up leaves the run `blocked` | 1150-1152 | reproduced | Critical |
| R-06 | Owner approval forgeable: replacing `owner_token_sha256` in `state.json` lets any writer approve and claim an R3 task | 1088, 1118-1130 | reproduced | Critical |
| R-07 | `cancel` never unblocks: `advance` treats every non-`completed` task as open; dependents never become ready | 1227, 756-762 | reproduced | High |
| R-08 | `reopen` accepts completed tasks (checks for status `done`, which never exists), resets `attempts`, writes bogus `lease_expires_at` | 1189-1202 | reproduced | High |
| R-09 | `cancel`/`reopen` unauthenticated although they are human decisions (descoping, retry budget) | 1189, 1205 | reproduced (fail→reopen loop: 5 failures, attempts 0) | High |
| R-10 | Stages with zero tasks and zero artifacts exit: an autonomous run went 00→06 with nothing | `advance_stage` 1219-1270 | reproduced | Critical |
| R-11 | Remediation added during 05_verify defaults to `04_build` and never blocks 05→06 | `add-task --stage` default 1520 | reproduced | High |
| R-12 | `supervised` behaves exactly like `autonomous`: `structural-deviation` and all `*_gate` keys are never read | 652-656, 939, 1231 | code read | High |
| R-13 | Agents can author the stage-gate checkpoint text (`checkpoint --kind stage --question "Approve minor copy tweak?"`); approving it satisfies `advance` | `create_checkpoint` 1060-1078 | reproduced | High |
| R-14 | Pending non-stage checkpoints do not block `advance`, which flips `waiting-human` back to `active` | 1267 | reproduced | Medium |
| R-15 | hitl task exhaustion blocks the run with the *rejection* message; approving any unrelated checkpoint clears it | 935-938, 1021, 1150 | reproduced | Medium |
| R-16 | `claim` accepts any agent id (not installed, not the owner); one agent can hold unlimited claims | 919-989 | reproduced | Medium |
| R-17 | `complete` accepts unverifiable evidence (`"trust me"`, nonexistent files) | 992-1006 | reproduced | High |
| R-18 | Tasks without `--path` bypass overlap detection and run beside any writer | 974-980 | reproduced | Medium |
| R-19 | Operating on a non-current run via `--run` silently repoints `CURRENT.md` (`is_current_run` is dead code) | 743, 750-753 | reproduced | Medium |
| R-20 | Risk floor is keyword substrings: 11/11 benign tasks → R3/R4, 3/3 real deploys → R0; task file prints the declared, not effective, risk | 856, 869-908 | reproduced | Critical |
| R-21 | Every error exits 2, the documented "human gate" code; argparse usage errors also exit 2 | 1712-1718, 1742-1744 | reproduced | Medium |
| R-22 | Windows: `os.replace` raises `PermissionError` while any reader holds `state.json` (status reads are unlocked) | 76-80 | reproduced | Medium |
| R-23 | Specialist routing is raw substring matching ("soundcloud"→finops, "reproduction"→sre, "storage"→eval via `rag`, React `children`→privacy); misses "personal data", "Stripe checkout", "p95", "99.9% uptime" | 768-773 | reproduced | Medium |
| R-24 | Events are appended inside `state.json` forever (200 tasks → 133 KiB rewritten on every mutation); `status --json` dumps it into agent context | 619 | reproduced | Medium |
| R-25 | `max_concurrent_agents`, `context_target_tokens`, `tier`, `native_subagents`, harness dir keys, `workflows.fusion.modes` are never read | whole file | code read | Medium |
| R-26 | `doctor` prints OK on a permanently blocked run; checks no generated-file drift | 1427-1467 | reproduced | Medium |
| R-27 | A refused approval is not recorded (the contract says it is) | 1140-1143 | code read | Low |
| R-28 | `report` overwrites a `DELIVERY-REPORT.md` the ceo wrote | 1406-1424 | reproduced | Medium |
| R-29 | `validate` from a `generic`/`pi` install is not refused (`.agentic-team/agents/` defeats `is_installed_bus`) | 153-155 | reproduced | Low |
| R-30 | `team.json` default `entry_mode: "adaptive"` is not a valid `--entry` value | team.json:10 | code read | Low |
| R-31 | Tests write owner tokens into the developer's real `~/.agentic-team/owner-tokens/` | tests/test_runtime.py | reproduced | Low |
| R-32 | `findings_to_tasks.py` emits `add-task` lines that cannot run: no `--id/--title`, nonexistent `--summary/--evidence`, broken quoting, owner `code-owner` not installed, blocker fixes routed to the read-only `security-engineer` | findings_to_tasks.py:76-128 | reproduced | High |
| R-33 | Installed projects only receive `bin/agentic_team.py`; skills and protocols reference `scripts/agentic_team.py` and `scripts/preflight_skills.py` | 528-531; skills/agentic-build/SKILL.md:21,25; protocols/skill-acquisition.md:10 | reproduced | High |
| R-34 | `install.ps1` checks only `Get-Command python` (the Store stub passes), no version probe, no `py -3` fallback | install.ps1:22-24 | code read | Medium |
| R-35 | The token travels in argv (`--token`, shell history, process list); docs model `--token "$(cat …)"`, which is exactly what an agent would run | 1561, 1567; docs/cli.md:77-78 | code read | High |
| R-36 | `fusion-product-council` preset lacks the default verifier (`qa-lead`): `fusion-init` with defaults fails | team.json:78 | reproduced | Low |
| R-37 | `toml_literal` writes a *basic* multi-line TOML string: any backslash in a future prompt makes the Codex agent file invalid and Codex silently skips it | 318-320 | code read (no current prompt contains `\`) | Medium |
| R-38 | Antigravity workflows (`.agents/workflows/*.md`) are deprecated and **stop working on 2026-11-01**; the replacement is skills (`.agents/skills/<name>/SKILL.md`, which become `/name` commands) | `emit_antigravity` 414-448 | vendor docs | High (time-bound) |
| R-39 | Antigravity: `mainAgent: true` on all 50 roles puts every role in the agent picker; the rule lacks `description:` (used as its pointer when rules exceed their budget) | 389-390, 397-400 | vendor docs | Low |

### 3.2 Claims vs enforcement (highest impact)

| Claim (where) | Reality |
|---|---|
| "human gates are enforced by the deterministic runtime" (docs/local-llms.md:106) | The runtime gates only `claim` of declared tasks. It sees no commands; an agent can deploy, send, or spend without any task. |
| "checkpoint decisions require the human owner's token" (agent-contract.md:52) | Three bypasses: edit the stored hash (R-06), read the unprotected token file, copy the documented `$(cat …)` pattern. |
| "Approved checkpoints are immutable events" (autonomy.md:29; README) | Plain JSON inside the project; no signature, no chain. |
| "The builder of an artifact cannot be its sole verifier" (fusion.md, definition-of-done.md, agentic-verify) | Nothing links tasks, commits, and agents; a builder claimed and completed a 05_verify task. |
| "Proposals remain private until all are submitted" (operating-modes.md:16) | All proposal files sit side by side, readable and writable by every agent. |
| "Declared outputs exist" — exit criteria in every generated CONTEXT.md | Never checked (R-10). |
| supervised "pauses for structural deviations" (autonomy.md:9) | Never evaluated (R-12). |
| "`bmad-progressive` activates … fresh context per step" (README:112) | `adaptive` gets the same eight contracts; `context_method` is only printed. |
| "Only the CLI writes `state.json`" (architecture.md:51) | Convention only: no permission rule, no hook, no schema validation. |
| Skills are "checked by `scripts/preflight_skills.py` at run start" (skills-integration-plan.md:22) | The script is not installed and always exits 0. |

### 3.3 Harness compilation gaps

| Gap | Where |
|---|---|
| Read-only roles get `Read, Grep, Glob` in Claude Code: they cannot run tests, `git diff`, `ocr delegate`, the state CLI, or any web lookup — yet their compiled prompts tell them to do all of that. | `emit_claude` 302 |
| No compiled role gets `WebSearch`/`WebFetch`, MCP tools, or `Agent`; `ceo`, `delivery-lead`, `cmo`, `fusion-moderator` are delegation roles that cannot delegate. (Current Claude Code lets a subagent spawn subagents up to three levels deep when it has the `Agent` tool.) | 302 |
| `tier` never compiled; `model: inherit` or nothing everywhere. | 308, 391 |
| OpenCode: `bash: ask` for every role, including tests and the state CLI. | 355 |
| The managed router block tells agents *in words* to read `.agentic-team/AGENTS.md`. Claude Code only loads what is imported (`@path`); prose pointers are followed only if the model decides to. | `managed_router` 257-267 |
| No permission rules, hooks, or settings are emitted for any harness, although the docs rely on them ("configure your harness permissions accordingly"). | install_team |
| Unused native features that fit this system: Claude Code `disallowedTools`, `skills` preload, `effort`, `maxTurns`, `color`, subagent-scoped `hooks`, `isolation: worktree`, the `agent` main-session setting; `agents/openai.yaml` `policy.allow_implicit_invocation`; Codex `model_reasoning_effort` and hooks; Gemini CLI `tools` allowlists; Pi prompt frontmatter. | emitters, skills |
| Cross-harness collisions: `.claude/agents/` is also read by Cursor (which ignores `tools`, so read-only roles lose their restriction there) and GitHub Copilot; `.agents/agents/` is also read by Devin Desktop (formerly Windsurf). | installs next to other tools |
| Gemini CLI agent frontmatter is a strict schema: one unknown key stops the agent loading. Never share frontmatter builders between emitters. | `emit_gemini` |
| Docs drift: `docs/harnesses.md` cites Windsurf (now Devin Desktop), Pi's old repo (now `earendil-works/pi`), and Codex URLs that now redirect to `learn.chatgpt.com/docs/*`. | docs/harnesses.md |

### 3.4 Roster (50 roles)

- **Thin specialists:** 18 specialists average 204 body tokens and 0.1 of the 8 standard
  sections; 13 lack at least three of: named inputs, ordered procedure, output location,
  "done" bar. None names its stage, artifact, verdict vocabulary, or manager.
- **Impossible jobs under compile:** research-agent, skill-scout, qa-lead, and
  performance-engineer cannot do their core job; accessibility-specialist and growth-analyst
  mostly cannot; security-engineer, code-reviewer, finops-engineer, privacy-engineer, and
  system-mapper only partly.
- **Unowned artifacts:** ASSUMPTIONS, READINESS, RELEASE, RETROSPECTIVE, DELIVERY-REPORT.
  Ownership of DELIVERY-REPORT existed only in four Standing-orders paragraphs, which the
  compiler strips. Verdicts use three vocabularies (`ship recommendation`,
  `approve | approve-with-fixes | request-changes`, none).
- **Residue:** "the run's task board" (14 lines; `delivery-lead.md:32` tells the role to
  write a file literally named `…/the run's task board`), "task evidence record" used as a
  mid-task message channel the CLI does not have (16), "hardening" (16), lifecycle "phase"
  (10), `lessons.md` (51 references in 31 roles), `DECISIONS.md` (6), WCAG 2.1 (3).
- **Overlaps:** growth-analyst vs analytics-engineer (worst), eval-engineer vs ai-ml-engineer
  (same manager as the builder it evaluates), fullstack vs backend/frontend engineers, sre vs
  devops vs release-manager on runbooks and rollback.
- **Descriptions:** all ≤ 300 characters with a trigger clause; none has an exclusion
  ("Not for X — use Y"), the most effective separator for auto-delegation.
- **Standing orders:** byte-identical in 46 of 50 files (~390 tokens × 50) and stripped at
  compile. Lost at compile: "never improvise a path", the plan-modes pointer, the bounded
  question-list format, and the four "Closing a build" duties (who owns DELIVERY-REPORT).
- **No new roles are needed.** Every coverage gap (API contracts, supply chain, LLM/agent
  security, MLOps, app-store release, OSS licensing) folds into an existing role.

### 3.5 Shared law: protocols, skills, templates, knowledge, docs

- **Drift:** autonomy gates defined differently in `autonomy.md`, `operating-modes.md`,
  `policies.json`, and code; three different hard-gate lists; three risk definitions plus the
  undocumented `RISK_SIGNALS`; four verdict rules; three delivery-report structures; two homes
  for decisions (`DECISIONS.md` vs `_decisions/`); STATUS.md/QA.md still in `guardrails.md`,
  `final-report.md`, and every playbook.
- **Skills are pointers, not runbooks:** none of the five contains the CLI command sequence,
  decision points on exit codes, or stop conditions; each restates protocol prose.
- **Missing protocols:** untrusted content / prompt injection, source control (branches,
  worktrees, commit trailers), supply chain, secrets and sensitive data, budgets, team
  observability, team evaluation, MCP/tool trust.
- **Templates:** no VERIFICATION (with a machine-readable verdict), READINESS matrix,
  RELEASE checklist, ADR, RISKS, checkpoint, handoff, or RETROSPECTIVE template; the code
  never reads `runtime/templates/final-report.md`; CONTEXT.md `Status:` is never refreshed.
- **Learning loop:** `learn` writes to the run folder in a format the knowledge index cannot
  filter; nothing promotes lessons into playbooks; agents write straight into playbooks that
  travel between projects (a persistent prompt-injection path); read-only roles cannot write
  playbooks; the seeded playbooks restate protocols and one cites evidence nobody gathered.
- **Owner guide:** a non-developer cannot succeed: prerequisites missing, the token never
  mentioned, approval only shown as a bash `$(cat …)` one-liner, rejection permanence not
  mentioned, `doctor` hides blocks.

### 3.6 Tests and CI

- No tests for `reopen`, `cancel`, `unlock`, `doctor`, `recover-leases` edge cases, exit codes,
  or bridge commands actually executing; `test_fusion_enforces_independence_and_full_sequence`
  tests only the happy path; `test_add_task_command_shape` asserts the broken command.
- No golden snapshots of compiled output, no schema validation of state, no doc↔CLI consistency
  check, no HOME isolation.
- CI: Python 3.11/3.13 on Ubuntu and Windows only. Missing macOS (install.sh targets it),
  Python 3.10 (claimed runtime minimum), and 3.14 (the maintainer's interpreter). The optional
  OCR job pins Node 20, which reached end of life in April 2026; action majors should be bumped.

---

## 4. Design principles for v3

1. **Three layers, labelled.** Prompts decide; the CLI verifies state transitions; the
   harness enforces tool use. Every guarantee is listed once in a *guarantee ledger*
   (§5.1) with its enforcing layer and known bypasses. Docs link to the ledger instead of
   asserting enforcement.
2. **Policy is data.** `config/policies.json` (plus a project-owned
   `policies.local.json` overlay that may only tighten) is the single source for gates, risk,
   stage exits, command rules, budgets, and routing vocabulary. Code reads it; prose links to it.
3. **Every transition has an authority.** Each CLI mutation declares whether an agent, the
   orchestrator, or the human may perform it (§5.2).
4. **Evidence is typed and checked.** Files are hashed, commands are captured with exit codes,
   commits are resolved. Free text remains allowed but never satisfies a gate on its own.
5. **Honest threat model.** Agents run as the same OS user. The runtime makes shortcuts
   conspicuous and tamper-*evident*; OS isolation (sandbox, WSL2, container) is what makes
   them tamper-*proof*. Docs say so.
6. **One home per fact; inline what must load.** Router text is imported or inlined, never
   referenced by prose. Standing orders leave the role files.
7. **Verified emitters.** Every harness emitter cites the official doc URL and verification
   date; unverifiable fields are not emitted.
8. **Compatible upgrade.** v2 runs migrate with `migrate`; reinstall preserves project-owned
   files and refuses to overwrite locally modified generated files without `--force`.

---

## 5. Target design

### 5.1 Guarantee ledger

A new section in `docs/architecture.md`, generated from `config/guarantees.json` (one row per
guarantee: id, statement, enforced_by ∈ {cli, harness, instruction}, test id, known bypass).
A test fails if any doc asserts "enforced", "immutable", "private", "in order", or "cannot"
about a guarantee whose ledger row says `instruction`.

### 5.2 Task lifecycle and authority

States: `pending → ready → claimed → completed`, plus `failed`, `cancelled`, and
`blocked` (dependency cancelled or failed). Closed states: `completed`, `cancelled`.

| Transition | Command | Authority | Rules |
|---|---|---|---|
| create | `add-task` | orchestrator | Default stage = current stage; tasks for earlier stages refused. Write tasks in `04_build` require ≥ 1 `--path` (or `--exclusive`, which conflicts with every other claim). `--action`/`--target` required (§5.4). |
| claim | `claim` | owner agent | Agent must be installed and equal the owner (or hold a recorded `reassign`); task must be in the current stage; concurrency cap `max_concurrent_agents` enforced; verification tasks refuse builders of the tasks they `--verifies`. |
| renew | `renew` | claimant | Extends the lease; lease max from policy. |
| complete | `complete` | claimant | Typed evidence validated (§5.6); `--check` commands must have a passing `exec` record. |
| fail | `fail` | claimant | Requires `--signature` (short failure fingerprint); the same signature twice escalates instead of retrying. |
| reassign | `reassign` | orchestrator | Records reason; owner must be installed. |
| cancel | `cancel` | **human** | Refuses when non-closed dependents exist unless `--cascade`. |
| reopen | `reopen` | orchestrator for `failed`/wedged `claimed`; **human** for `completed` | Keeps attempt history; extending the retry budget is human-only. |
| decide | `approve` / `reject` / `resolve` | **human** | `resolve` closes a rejection with a corrective note; run unblocks when no unresolved rejection remains. |
| waive | `waive` | **human** | Waives one named stage-exit requirement with a reason. |
| advance | `advance` | orchestrator | §5.5. |

Run states: `active`, `waiting-human` (pending checkpoint), `blocked-rejection`,
`blocked-failure`, `verifying`, `complete`, `closed`. The two blocked states carry different
messages and different unblock paths.

Only the CLI creates `stage` and `risk` checkpoints, with factual CLI-generated content
(artifacts and hashes, verdict line, open risks, evidence links). Agents may create
`decision`, `deviation`, `injection`, and `budget` checkpoints, which require
`--alternatives`, `--impact`, `--evidence`, and `--rollback` in addition to question and
recommendation. Any pending checkpoint blocks `advance`.

### 5.3 Human authority v3

- **Decision ledger outside the project.** `approve`, `reject`, `resolve`, `waive`,
  human `cancel`/`reopen`, and human-sponsored `fusion-close` append a record to
  `$AGENTIC_TEAM_HOME/ledger/<run-id>.jsonl` (default `~/.agentic-team`). Each record
  carries `HMAC-SHA256(owner_token, canonical_json(record))` and the previous record's hash.
  `state.json` mirrors decisions for display; `claim` and `advance` read the ledger, not
  `state.json`, when they check approvals. Editing `state.json` therefore gains nothing.
- **Owner key binding.** `init-run` records `sha256(token)` both in state and in
  `$AGENTIC_TEAM_HOME/runs/<run-id>.json`. A mismatch fails every gated command closed
  ("owner key mismatch — run `audit verify`").
- **Token handling.** Accepted as `--token-file PATH`, `--token-stdin`, or an interactive
  hidden prompt. `--token VALUE` is accepted with a deprecation warning. `init-run` never
  prints the token. Docs show PowerShell and bash commands that never put the token in argv.
- **`audit verify`** (human, needs the token) recomputes every ledger MAC and the event hash
  chain (§5.8), and reports forged, missing, or reordered decisions.
- **Refused attempts are recorded** as `authority-refused` events (fixes R-27).
- **Harness layer** (§5.12) denies agent access to `$AGENTIC_TEAM_HOME` and agent writes to
  run state and the ledger.
- **Threat model (documented).** Protects against cooperative agents taking shortcuts,
  prompt-injected attempts to self-approve, and accidental edits. It does not protect against
  deliberately malicious code running unsandboxed as the same user. For that, run autonomous
  sessions in an OS sandbox (Claude Code's sandbox runs on macOS, Linux, and WSL2 — not native
  Windows), WSL2, a dev container, or a separate OS account.
- `AGENTIC_TEAM_HOME` also isolates tests (fixes R-31).

### 5.4 Risk model v3

Risk comes from **what the task does and where**, not from words in its title.

- `add-task --action` ∈ `inspect, build, test, docs, research, add-dependency, migrate,
  infra-change, deploy, publish, send-message, spend, credential, data-destructive, legal`
  and `--target` ∈ `local, ci, staging, production, external`.
- `policies.json.risk.matrix` maps (action, target) → R-level. Examples: build/local → R1;
  add-dependency/local → R2; migrate/local → R2; migrate/production → R4; deploy/staging →
  R2 (hitl pauses) ; deploy/production → R3; send-message/external → R3;
  data-destructive/anything → R4; credential → R4.
- `policies.json.risk.path_rules` raise floors by owned path:
  `.github/workflows/**`, `**/migrations/**`, `infra/**`, `terraform/**`, `k8s/**`,
  `Dockerfile*`, lockfiles and dependency manifests → R2.
- A **word-boundary keyword backstop** only *raises* risk and only for phrases that describe
  operating on the world (e.g., `\b(deploy|release|publish|push)\b.{0,40}\b(prod|production|live)\b`,
  `--prod\b`, `\bterraform apply\b`, `\bkubectl (apply|delete)\b`, `\bdrop (table|database)\b`,
  `\bnpm publish\b`, `\bgit push\b.*--force`). Remove `contract`, `truncate`, `purge`,
  `billing`, `payment`, `post to`, `announce`, `credential` (as a bare word), `legal` (bare).
- Lowering an effective risk requires a human `waive` of that task's risk floor.
- **Command rules** (`policies.json.command_rules`: regex, risk, reason) are shared by the
  harness guard hook (§5.12), the OpenCode permission map, and `exec`. A matching command is
  allowed only while a claimed task with an approved checkpoint covers it.
- Resolve the drift: one R0–R4 definition (policies.json), `autonomy.md` links to it,
  global installs and "broad system access" are hard gates (R4) consistently.

### 5.5 Stage exit contracts

`policies.json.stage_exits` declares, per stage, the required artifacts and machine-checkable
lines. `advance` checks them, and refuses while any pending checkpoint, open task, or active
specialist without a closing task/reason exists.

| Stage | Exit requirement (default policy) |
|---|---|
| 00_intake | `BRIEF.md` and `ASSUMPTIONS.md` exist and differ from templates |
| 01_product | `PRD.md` with ≥ 1 `AC-` acceptance id |
| 02_solution | `ARCHITECTURE.md` with an ADR index; `DESIGN.md` when UI signals routed; threat model section when security triggered |
| 03_readiness | `READINESS.md` traceability matrix: every `AC-` id maps to ≥ 1 task and ≥ 1 check |
| 04_build | every task closed; every write task has typed evidence; integration commit recorded when git is present |
| 05_verify | `VERIFICATION.md` first lines `Verdict: PASS` (or `CONDITIONAL` with an approved checkpoint), `Verifier: <id>`, `Verified-SHA: <sha>`; verifier ∉ 04_build claimants; `Verified-SHA` = recorded integration SHA |
| 06_release | `RELEASE.md` (artifact identity, rollout, monitoring, rollback evidence) + human release checkpoint |
| 07_learn | `RETROSPECTIVE.md` and `DELIVERY-REPORT.md` |

The table is the `bmad-progressive` profile. `adaptive` runs use a lighter policy profile
(00–03 collapse into one `BRIEF.md` with inline `AC-` ids and a task list; 05 still needs the
verdict lines; 06 still needs the human release checkpoint), which finally gives
`context_method` a behavioral meaning.

A stage skipped by the entry mode records `skipped_by_entry`. A stage with no work records an
explicit `no-work` note from the orchestrator, which requires the stage's artifacts anyway.
Placeholder detection: files that still contain template markers (`{…}` or `TODO`) fail.
`CONTEXT.md` status lines are regenerated on every transition; exit criteria text is rendered
from the same policy rows.

### 5.6 Evidence v3

- Typed evidence strings: `file:<path>` (must exist; sha256 + size recorded),
  `cmd:<exec-id>` (an `exec` record), `commit:<sha>` (resolved with `git cat-file -e` when the
  project is a git repo), `url:<https-url>` (recorded, not fetched), `note:<text>` (allowed,
  never sufficient alone for a write task).
- `exec --task T --agent A -- <argv…>` runs a command without a shell (unless `--shell`),
  captures exit code, duration, git HEAD, and the first/last 64 KiB of output into
  `runs/<id>/_evidence/<task>/<n>.json|.log`, refuses commands that match an unapproved
  `command_rules` entry, and returns an `exec-id`.
- `add-task --check "<command>"` (repeatable) declares acceptance commands;
  `complete --run-checks` executes them through `exec` and refuses completion unless all
  pass. This turns "tests pass" from a claim into a record.

### 5.7 Fusion v3

- One-way state machine: `proposals → critiques → synthesis → verification → decision →
  complete`. Each submission kind is accepted only in its phase; no resubmission after the
  phase advances; one `revision` per contributor during `critiques`.
- `fusion-submit --file <path>` records the file's sha256 (commit). At reveal
  (`proposals → critiques`) the CLI re-hashes every proposal and refuses to reveal if any
  changed, then copies them to `revealed/`. Proposals are written under `sealed/<agent>.md`.
- Moderator ≠ verifier ≠ contributors. Critique assignments (critic → target) are explicit.
- `fusion-close`: human-owner sponsor needs human authority (§5.3); an agent sponsor is only
  valid when the profile's gate policy allows automatic decisions for that decision class.
  Close writes `decision.md` status and requires `dissent.md` to be non-empty or to state
  "No material dissent".
- Harness layer: during `proposals`, the guard hook denies a contributor subagent reads of
  other contributors' `sealed/` files (Claude Code passes `agent_type` to hooks). Elsewhere
  privacy stays instruction-only and the ledger says so.

### 5.8 Events, metrics, budgets

- Events move to `runs/<id>/events.jsonl`, append-only, each line carrying the previous line's
  hash; `state.json` keeps `events_head` and `event_count`. `log [--since] [--type]` reads it.
- `metrics` derives first-pass completion rate, retries, and failure signatures per role,
  checkpoint latency and rejection rate, verification FAIL rate, gate refusals; writes
  `runs/<id>/METRICS.md` on demand.
- `policies.json.budgets`: max tasks per run, max attempts per task, max lease minutes, max
  Fusion councils per run, optional token/USD ceilings recorded via `complete --usage`.
  At 80 % the CLI opens a `budget` checkpoint; at 100 % gated commands stop.

### 5.9 Orchestrator ergonomics

| Command | Purpose |
|---|---|
| `next --agent A [--json]` | Claimable tasks for A: ready, owned by A, no path conflict, under the cap. |
| `board [--format md\|mermaid\|json]` | Task graph by stage and status. |
| `pack --task T` | Builds the 2K–8K-token context packet (envelope, named inputs, stage contract excerpt, role playbook checks, exact claim/exec/complete commands), writes `_context/<task>.md`, prints a token estimate and omissions. |
| `brief --task T` | The delegation message an orchestrator hands a subagent. |
| `status --brief` | ≤ 20 lines for agents; `--json` keeps full detail. |
| `runs`, `switch-run`, `close-run` | Multiple runs without silently repointing `CURRENT.md` (fixes R-19). |
| `migrate` | Upgrades v2 state (events → jsonl, new fields, ledger bootstrap). |

### 5.10 Access model v3

| Access | Meaning | Roles (default) |
|---|---|---|
| `read-only` | Inspect files; return findings in the final message. | compliance-advisor, fraud-risk-analyst, finops-engineer |
| `research` | read-only + web search/fetch. | research-agent, skill-scout |
| `review` | Inspect + execute commands + web; may write only under `.agentic-team/runs/**` and its own playbook; never edits source. | qa-lead, code-reviewer, security-engineer, performance-engineer, accessibility-specialist, privacy-engineer, system-mapper, growth-analyst |
| `workspace-write` | Edit the project within owned paths. | builders |
| `orchestrate` | workspace-write + delegation. | ceo, delivery-lead, cmo, fusion-moderator |

`release-manager` becomes `workspace-write` (nothing uses `orchestrate` for it). Harness
mapping is in Appendix A. The compiled stub differs by access: `read-only`/`research` roles
are told the orchestrator records their results; `review` roles record their own evidence.

### 5.11 Model tiers

`team.json.model_profiles` maps tier → per-harness settings; `install --model-profile`
chooses one (default `balanced`; `inherit` reproduces v2).

| Profile | deep | standard | fast |
|---|---|---|---|
| `inherit` | inherit | inherit | inherit |
| `balanced` (default) | inherit + high effort | `sonnet` | `haiku` |
| `max-quality` | `opus` + high effort | `opus` | `sonnet` |
| `economy` | `sonnet` | `haiku` | `haiku` |

Codex uses `model_reasoning_effort` per tier and leaves `model` unset unless the profile names
one; OpenCode and Gemini CLI emit `model` only when the profile provides a provider-qualified
id; Pi/generic record the tier in the prompt header. Re-tier: skill-scout and tech-writer
fast→standard; release-manager and eval-engineer standard→deep.

### 5.12 Harness enforcement layer

- **Guard entrypoint:** `python .agentic-team/bin/agentic_team.py guard --event pretooluse`
  reads the harness hook JSON on stdin and denies: any access to `$AGENTIC_TEAM_HOME`
  (owner tokens, ledger); Write/Edit of `.agentic-team/runs/**/state.json`,
  `events.jsonl`, `_evidence/**`; commands matching `command_rules` without an approved
  covering task; during Fusion `proposals`, contributor reads of other contributors' sealed
  files. Deny output uses the harness's documented JSON; exit 2 as fallback. The guard must
  distinguish `$AGENTIC_TEAM_HOME` (default `~/.agentic-team`, the owner's material) from the
  project bus `.agentic-team/` (which agents must keep using): resolve `~`, `$HOME`,
  `%USERPROFILE%`, and absolute paths before matching, and match command text for
  `owner-tokens` and `ledger` references. The guard never blocks the CLI's own reads of the
  ledger (those happen inside the `agentic_team.py` subprocess, not in an agent tool call).
- **Claude Code:** merge (never clobber) `.claude/settings.json`: `permissions.deny` for
  `Read(~/.agentic-team/**)`, `Edit(~/.agentic-team/**)`, and
  `Edit(/.agentic-team/runs/**/state.json)`; a `PreToolUse` hook running the guard; optional
  `sandbox.filesystem.denyRead: ["~/.agentic-team"]` on platforms that support the sandbox.
  Entries the installer owns are recorded in `install-manifest.json` so reinstall/uninstall
  remove only them. The hook command uses the interpreter the installer probed, with a
  portable fallback.
- **Review access in Claude Code:** subagent-scoped `hooks` in the role frontmatter deny
  Write/Edit outside `.agentic-team/runs/**` and the role's playbook.
- **OpenCode:** `permission.bash` becomes a pattern map (`"*": "allow"` for workspace and
  review roles, then `ask`/`deny` entries generated from `command_rules`; the last matching
  rule wins, so specific patterns come after `*`). Research roles get `webfetch`/`websearch:
  allow`; orchestrate roles get `task: allow`; read-only roles `edit: deny, bash: deny`.
  `edit: deny` does not stop writes through bash — the ledger marks review-role source
  protection "instruction only" on OpenCode.
- **Codex:** project hooks (`.codex/hooks.json`, `PreToolUse`) run the same guard; they load
  only in trusted projects after a `/hooks` review, which the install output and docs must say.
  `sandbox_mode` per access (`read-only` for read-only/research, `workspace-write` otherwise);
  `model_reasoning_effort` per tier. No per-agent tool allowlist exists.
- **Gemini CLI:** `tools` allowlists per access using Gemini tool names (read-only:
  `read_file, list_directory, glob, grep_search`; research adds `google_web_search, web_fetch`;
  review adds `run_shell_command`), plus `policy.toml` deny rules generated from
  `command_rules` if the current docs confirm the rule syntax.
- **Antigravity:** keep the ACCESS CONSTRAINT text (no reliable per-agent read-only switch);
  emit `.agents/hooks.json` only after its format is verified.
- **Pi / generic:** no native enforcement; the ledger marks these rules "instruction only".
- **New targets** (P5b): Copilot `tools: ["read","search"]` allowlists, Cursor
  `readonly: true`, Factory `tools: read-only`, Kiro `tools` + permissions, Qwen and Junie
  native tool names — each only as verified in Appendix A.

### 5.13 Installer v3

- Helper tools become CLI subcommands installed with the bus: `preflight` (non-zero exit when
  a required skill is missing), `findings-to-tasks` (emits runnable commands, `--apply` to add
  tasks directly), `design-to-admin`, `llm-check`. `scripts/*.py` stay as thin wrappers.
- Installed skills and protocols have `scripts/agentic_team.py` and `scripts/preflight_skills.py`
  rewritten to `.agentic-team/bin/agentic_team.py …` (same mechanism as protocol refs).
- Generated files are recorded with sha256; reinstall refuses to overwrite a locally
  modified generated file without `--force` (then backs it up under `.agentic-team/backup/`).
- `uninstall` removes generated files, managed blocks, and installer-owned settings entries;
  keeps `knowledge/` and `runs/` unless `--purge`.
- `policies.local.json` (project-owned) overlays policy and may only tighten.
- `install.ps1` gets the executing-interpreter probe and `py -3` fallback.
- `.gitignore` guidance for `runs/**/_evidence` and owner material is written to the managed
  block; nothing sensitive is committed by default.
- Optional: `package-claude-plugin` generates a Claude Code plugin + marketplace entry
  (skills, hooks, a full-roster agent set) as a second distribution channel. Per-project
  roster selection remains the installer's job.

### 5.14 CLI surface and exit codes

Exit codes: `0` success · `1` error · `2` stopped at a human gate (unchanged) · `3` run
blocked (rejection or exhausted failure) · `64` usage error. `docs/cli.md` is generated by
`agentic_team.py docs --cli`, and a test fails when it is stale.

New commands: `resolve`, `waive`, `renew`, `reassign`, `exec`, `next`, `board`, `pack`,
`brief`, `runs`, `switch-run`, `close-run`, `log`, `metrics`, `audit verify`, `migrate`,
`uninstall`, `preflight`, `findings-to-tasks`, `design-to-admin`, `llm-check`, `guard`,
`docs`.

---

## 6. Phases

Each phase is one branch (`v3/p<N>-<slug>`), ends green, and updates the protocols and docs
that describe the behavior it changes **in the same commit**.

### P0 — Safety net (size S)

- `AGENTIC_TEAM_HOME` override; tests set it plus `HOME`/`USERPROFILE` to temp dirs (R-31).
- `tests/helpers.py` (`fresh_project()`, `run_cli()` subprocess helper with exit codes).
- Golden snapshots: compile a fixed 5-role roster (`ceo, fullstack-engineer, qa-lead,
  research-agent, sre-engineer`) for every harness into `tests/golden/<harness>/…`;
  `UPDATE_GOLDEN=1` regenerates. Later phases review snapshot diffs.
- Doc↔CLI consistency test: every `agentic_team.py <command> --flag` mentioned in `docs/`,
  `skills/`, `protocols/`, `agents/`, and `README.md` exists in `build_parser()`.
- CI: add `macos-latest`; Python 3.10 (runtime tests; skip tomllib-dependent tests), 3.12,
  3.14; bump `actions/checkout`, `actions/setup-python`, `actions/setup-node` to current majors;
  Node 22+ for the OCR job.
- **Accept:** suite green on Ubuntu, Windows, macOS; golden files committed; no files written
  to the real home during tests.

### P1 — Runtime correctness (size M)

Fix R-01, R-02 (token check now; ledger in P2), R-03, R-04, R-05, R-07, R-08, R-09, R-11,
R-14, R-15, R-16, R-18, R-19, R-21, R-22, R-23, R-25 (`max_concurrent_agents`; delete or use
the other unread keys), R-26, R-27, R-28, R-29, R-30, R-32, R-33, R-34, R-36, R-37, R-38,
R-39, following §5.2, §5.7, §5.9 (`renew`, `runs`/`switch-run`/`close-run`), §5.13 (helpers
as subcommands, path rewriting, ps1 probe), §5.14 (exit codes). Word-boundary routing plus
the new trigger vocabulary (Appendix B.5).

**Time-bound:** R-38 (Antigravity workflows → skills) must ship before **2026-11-01**. If P1
will not be merged by then, cut it as a standalone `v2.0.2` hotfix from `main` first.

- **Test-first:** each defect ID gets a regression test that fails on `d0fb6cf` and passes
  after the fix (`tests/test_regressions.py`, test names carry the ID).
- **Accept:** every ID above has a passing regression test; the bridge's generated commands
  execute against a fresh install; `doctor` reports blocked runs, pending checkpoints, expired
  leases.

### P2 — Authority, risk, and audit (size L)

§5.3 (ledger, HMAC, token handling, `audit verify`, human-only commands), §5.4 (action
classes, matrix, path rules, backstop, command rules, `waive`), §5.2 checkpoint content rules,
R-06, R-10 (authority parts), R-12 (supervised = `deviation` checkpoints + gate keys read from
policy), R-13, R-20, R-35. `migrate` bootstraps a ledger for v2 runs (pending decisions only).
- **Accept:** forging `state.json` (hash swap, injected approval) fails closed; `audit verify`
  detects a tampered ledger line; the risk corpus classifies as expected — the eleven benign
  titles in §3.1 R-20 stay ≤ R2 as `build/local`, `deploy/production` is ≥ R3 whatever the
  title says, and titles containing `vercel --prod`, `terraform apply`, `kubectl apply`, or
  `git push --force` are raised to ≥ R3 by the backstop (free text such as "Ship it" is caught
  by the action class and the command guard, not by keywords); `supervised` differs from
  `autonomous` in a test.

### P3 — Evidence and stage exits (size L)

§5.5, §5.6, verification independence, remediation-stage rule, specialist obligations, new
templates (Appendix B.2 owners), CONTEXT.md refresh, `report` → `DELIVERY-EVIDENCE.md`.
- **Accept:** the "00→06 with nothing" scenario is refused at 00 exit; a builder cannot claim a
  task that verifies its own work; `complete --run-checks` records exit codes; a
  `VERIFICATION.md` without a valid verdict line blocks 05 exit.

### P4 — Orchestration ergonomics, events, budgets (size M)

§5.8, §5.9. `events.jsonl` with hash chain, `log`, `metrics`, budgets, `next`, `board`,
`pack`, `brief`, `status --brief`, `migrate` for event relocation.
- **Accept:** 200-task run keeps `state.json` < 40 KiB; `pack` output within 2K–8K tokens for
  a fixture task; chain verification detects an edited event.

### P5 — Harness compilers v3 (size L)

§5.10, §5.11, §5.12 and Appendix A: access mapping, model profiles, `skills` preload per role
(qa-lead → agentic-verify; fusion-moderator → fusion-council; delivery-lead, ceo →
agentic-build; context-engineer → bmad-progressive), `Agent` tool for orchestrate roles,
tool sets per Appendix A.3 (review roles: Bash plus Write/Edit limited to the run folder by
subagent-scoped hooks), `color` by department, router imported (`@…`) for Claude
Code and inlined (≤ 25 lines) elsewhere, settings/hook merge, OpenCode permission maps,
`openai.yaml` `policy.allow_implicit_invocation: false` for fusion-council, agentic-learn, and
agentic-build. Each emitter carries its doc URL and verification date.
- **P5b — new targets** (Appendix A.2), in this order: GitHub Copilot
  (`.github/agents/<id>.agent.md`) and Cursor (`.cursor/agents/<id>.md`, `readonly`), then
  Factory Droid, Kiro (also copies skills to `.kiro/skills/`), Qwen Code, and Junie. Each new
  target gets golden snapshots and literal-path adapter tests. Cursor's docs call 50+
  subagents an anti-pattern, so its emitter should warn above ~15 roles and recommend a preset.
- **Accept:** golden snapshots updated and reviewed; every emitted field appears in Appendix A
  with a source; a Claude Code install contains the guard hook and deny rules and a review
  role that can run `python -m unittest` but cannot edit `src/`.

### P6 — Roster v3 (size L)

Appendix B.1–B.6: specialist skeleton for all 18 specialists (450–800 tokens), artifact and
verdict ownership, description rewrites with exclusion clauses, vocabulary purge, learning-path
rewrite, Standing orders removed from all 50 sources (lost duties moved to
`agent-contract.md` and the Output contracts), overlaps split, reporting lines fixed, AI/agent
security and supply-chain duties folded into existing roles, marketing track artifacts under
`runs/<id>/_marketing/`, persona filler cut, WCAG 2.2. Keep all 50 ids (no merges in v3;
context-engineer and fusion-moderator shrink to pointers plus skill preload).
- New `tests/test_roster.py`: banned vocabulary; specialist headings; description length,
  trigger, and exclusion clauses; every role id in a body exists; each lifecycle artifact has
  exactly one owner; compiled size 400–2,500 tokens; no Standing orders block.
- **Accept:** roster lint green; routing corpus (Appendix B.5) passes positive and negative
  cases.

### P7 — Protocols, skills, templates, knowledge (size L)

- New protocols: `untrusted-content.md`, `source-control.md`, `supply-chain.md`,
  `secrets-and-sensitive-data.md`, `budgets.md`, `team-observability.md`,
  `team-evaluation.md`, `harness-security.md` (threat model, per-harness enforcement table,
  sandbox/WSL2/container guidance). Contents per Appendix B.7.
- Rewrite `autonomy.md`, `runtime.md`, `workflow.md`, `fusion.md`, `evolution.md`,
  `agent-contract.md` (absorbs the lost standing-order rules), `guardrails.md`,
  `final-report.md` (one 7-section report), `specialist-routing.md` to match P1–P4 behavior;
  one hard-gate list included by reference.
- Skills become runbooks: exact command sequences, exit-code branches, stop conditions,
  bundled scripts, `compatibility:` frontmatter, no restated protocol prose.
- Templates: VERIFICATION, READINESS, RELEASE, ADR (`_decisions/ADR-NNN.md` replaces
  `DECISIONS.md`), RISKS, checkpoint, handoff, RETROSPECTIVE, BRIEF, PRD (with `AC-` ids),
  fusion-dissent, marketing CONTEXT.
- Knowledge loop: playbook entries carry `status: candidate|proven|baseline` and a source run;
  agents add candidates only; `learn` gains `--roles --trigger --confidence --task` and writes
  the knowledge index format; a `promote` path (human) moves candidates to proven; seeded
  playbooks relabelled `baseline`; the fabricated evidence line in `knowledge/lessons.md`
  removed; sanitisation checklist for project→source sync.
- **Accept:** no drift test failures (hard-gate lists equal policy; every template referenced
  and present; no v1 terms); each skill's command sequence executes in a test against a fresh
  install.

### P8 — Team evaluation (size M)

- `evals/scenarios/*.json`: scripted, deterministic runs of the state machine for greenfield,
  plan-given, execute-only, brownfield fix, Fusion, and rejection/recovery, each asserting
  gates, artifacts, and authority refusals. Run in CI.
- Optional live-agent smoke eval (opt-in, secrets in CI only): drive one small scenario through
  a real harness in headless mode (for Claude Code, `claude -p` with `--output-format
  stream-json`) and score gate adherence, evidence presence, artifact creation, and
  self-approval attempts.
- Evolution rule: a protocol or role change that lowers the scenario pass rate is rejected.
- **Accept:** scenario suite green in CI; live smoke documented and runnable manually.

### P9 — Docs, migration, release (size S/M)

- Guarantee ledger in `docs/architecture.md`; `docs/cli.md` generated; `docs/harnesses.md`
  with verification dates; `docs/quickstart-non-dev.md` rewritten (prerequisites, the human
  starts the run, where the token lives, PowerShell and bash approve/reject/resolve commands,
  never paste the token into chat, how to stop the team); README preset table with coverage
  columns; `docs/migration-v3.md`.
- Presets satisfy coverage invariants (Appendix B.6), enforced by `validate`.
- Version 3.0.0 in the `VERSION` constant (`scripts/agentic_team.py`), `team.json`,
  `policies.json`, and schemas; CHANGELOG entry; the skills-integration plan marked historical.
- **Accept:** §10.

---

## 7. Sequencing and effort

```
P0 → P1 → P2 → P3 → P4 ─┐
            └──→ P5 ─────┼─→ P8 → P9
P1 ──→ P6 (roster) ──────┤
P3 ──→ P7 (law/skills) ──┘
```

- P6 can start after P1 (it touches `agents/**`, `team.json` roster fields, `tests/test_roster.py`).
- P7 protocol text that describes runtime behavior lands with the runtime change; the
  remaining P7 work starts after P3.
- P5 needs P2's command rules and P1's access-independent fixes.
- Rough size: S ≈ one focused session, M ≈ 2–3, L ≈ 4–6. Total ≈ 25–35 agent sessions.

---

## 8. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Over-gating kills autonomy (stage exits, action classes) | Defaults tuned against the P8 scenarios; `waive`; `policies.local.json` may only tighten, but the shipped defaults for `autonomous` stay permissive for R0–R2. |
| Harness formats change or are misread | Verify against official docs at implementation time; record URL + date; golden snapshots; unverifiable fields not emitted. |
| Hooks on Windows fail to find Python | Installer records the probed interpreter; hook falls back to `py -3`; `doctor` runs a hook self-test. |
| `.claude/settings.json` merge corrupts user settings | Parse-merge-write with backup; installer-owned entries tracked; refuse on invalid JSON. |
| Breaking existing v2 runs | `migrate`; commands refuse on v2 state (except `status`, `migrate`, `doctor`) with a clear message. |
| Scope creep across 10 phases | Phase acceptance gates; deviations reported in three lines; progress file (`docs/v3-progress.md`). |
| False sense of security | Guarantee ledger + threat model + sandbox guidance; tests assert docs do not overclaim. |

---

## 9. Deliberately out of scope for v3

- A model scheduler or direct model API calls from the runtime.
- New roles, role merges, or removals (ids stay stable; revisit after P8 metrics).
- A web dashboard (the `board`/`metrics` outputs are the interface).
- Replacing HMAC with asymmetric signatures (needs a non-stdlib dependency).

---

## 10. v3 definition of done

1. `python scripts/agentic_team.py validate` → OK (including roster lint, preset coverage,
   policy schema, guarantee ledger).
2. `python -m unittest discover -s tests` → green on Windows, Ubuntu, macOS; Python 3.10–3.14
   (3.10 runtime subset).
3. Every R-ID in §3.1 has a regression test; every guarantee ledger row marked `cli` or
   `harness` has a test id.
4. `python scripts/agentic_team.py install <tmp> --harness H --preset platform-core` works for
   all harnesses, and `doctor --project <tmp>` passes including the hook self-test where
   applicable.
5. `evals/` scenario suite green.
6. `docs/cli.md` regenerated and unchanged by the generator; no doc overclaims.
7. `docs/migration-v3.md` and CHANGELOG entry present; a v2 fixture run migrates cleanly.

---

## Appendix A — Harness verification (primary sources, checked 2026-09-25)

Re-verify every row at implementation time; formats move monthly. "UNVERIFIED" items must not
be emitted until confirmed.

### A.1 Current targets

| Harness | v2 output | Verdict | v3 changes | Sources |
|---|---|---|---|---|
| Claude Code | `.claude/agents/<id>.md` (`name`, `description`, `tools`, `model: inherit`); managed block in `CLAUDE.md`; `.claude/skills/` | Correct but minimal | Frontmatter also supports `disallowedTools`, `model` (`sonnet`, `opus`, `haiku`, `fable`, full id, `inherit`), `permissionMode`, `maxTurns`, `skills` (full content preloaded), `mcpServers`, `hooks` (subagent-scoped PreToolUse/PostToolUse/Stop), `memory`, `background`, `omitClaudeMd`, `effort` (`low`…`max`), `isolation: worktree` (branches from the default branch, not HEAD), `color`, `initialPrompt`. Delegation tool is `Agent` (`Task` alias); subagents may spawn subagents up to three levels deep. `CLAUDE.md` loads `@path` imports (four hops); a prose pointer to another file is followed only if the model chooses to. Project `.claude/settings.json`: `permissions.deny` (`Read(~/…)` home-relative, `//abs`, `/project-relative`), hooks (`PreToolUse` deny via `hookSpecificOutput.permissionDecision: "deny"` or exit 2). Read/Edit deny rules also cover recognised Bash file commands and redirects, but not arbitrary subprocesses — use a hook or the sandbox. Sandbox (`sandbox.filesystem.denyRead` etc.): macOS, Linux, WSL2 only. Plugins: `.claude-plugin/plugin.json` + root `agents/ skills/ hooks/hooks.json .mcp.json`; plugin agents ignore `hooks`, `mcpServers`, `permissionMode`. Agent teams: experimental (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`), hooks `TaskCreated`/`TaskCompleted`/`TeammateIdle`. | code.claude.com/docs/en/sub-agents, /hooks, /permissions, /sandboxing, /memory, /plugins-reference, /agent-teams |
| Codex | `.codex/agents/<id>.toml` (`name`, `description`, `developer_instructions`, `sandbox_mode = "read-only"`); `.agents/skills/` + `agents/openai.yaml`; root `AGENTS.md` | Correct | Add `model_reasoning_effort` per tier (`low`…`max`); `sandbox_mode` per access; fix TOML string escaping (R-37). Project `.codex/` loads only in trusted projects. Hooks: `.codex/hooks.json` (`PreToolUse`, `SubagentStart/Stop`, …; project hooks need trust + `/hooks` review). No per-agent tool allowlist. Delegation via `spawn_agent` etc.; default 6 threads, depth 1 (`[agents] max_concurrent_threads_per_session`). `agents/openai.yaml` supports `policy.allow_implicit_invocation`. AGENTS.md combined cap 32 KiB. Per-agent `approval_policy` effect: UNVERIFIED. | learn.chatgpt.com/docs/agent-configuration/subagents, /agents-md, /hooks, /build-skills; codex-rs source (rust-v0.157.0) |
| OpenCode | `.opencode/agents/<id>.md` (`description`, `mode`, `permission: {edit, bash: ask}`); `.agents/skills/`; `AGENTS.md` | Correct (V1); V2 (2.0.0, 2026-09-11) translates V1 frontmatter | Replace blanket `bash: ask` with pattern maps; use `webfetch`, `websearch`, `task` permission keys; optional `steps`, `color` (6-digit hex for V2), `model` only when provider-qualified. Keep V1 syntax until V2 is the majority; V2 native form is an ordered `permissions` list. | opencode.ai/docs/agents, /docs/permissions, /v2/docs/migrate-v1 |
| Gemini CLI | `.gemini/agents/<id>.md` (`name`, `description`); `GEMINI.md` block; `.agents/skills/` | Correct (minimal) | Strict schema — allowed keys only: `name`, `description`, `kind`, `display_name`, `tools`, `mcp_servers` (not `mcpServers`), `model`, `temperature`, `max_turns`, `timeout_mins`. Add `tools` allowlists per access; `max_turns` optional. Project agents load only in trusted folders when folder trust is on. Extensions (`gemini-extension.json`) are a possible distribution channel. | github.com/google-gemini/gemini-cli `docs/core/subagents.md`, `packages/core/src/agents/agentLoader.ts` (v0.61.0) |
| Antigravity | `.agents/agents/<id>.md` (`name`, `description`, `subagent`, `mainAgent`, `model`); rule `.agents/rules/agentic-team.md` (`trigger: always_on`); `.agents/workflows/*.md`; `.agents/skills/`; `AGENTS.md` | Agents/rule/skills correct for Antigravity 2.0 and CLI; **workflows retire 2026-11-01**; IDE support for custom subagents not documented | Convert the six workflows to skills (R-38); `mainAgent: false` except lead roles; add `description:` to the rule (rule files ≤ 24,000 bytes). Keys seen only in changelogs (`inheritCustomizations`, `excludeDefaultComponents`, `hooks`, `hidden`): verify before use; the default of `inheritCustomizations` is UNVERIFIED and matters (roles might not see the rule/skills). | antigravity.google/docs/subagents, /docs/rules, /docs/ide/workflows, /docs/migration/workflows-to-skills; antigravity-cli CHANGELOG |
| Pi | Root `AGENTS.md`; `.pi/skills/`; `.pi/prompts/*.md` (plain text); roles in `.agentic-team/agents/` | Correct | Add prompt frontmatter (`description`, `argument-hint`). Pi also reads `.agents/skills/`. Optional: emit `.pi/agents/*.md` for the official subagent example extension (`name`, `description`, `tools`, `model`; project scope must be enabled). Repo moved to `earendil-works/pi`. | github.com/earendil-works/pi `packages/coding-agent/docs/*` (0.87.1) |
| Generic | `.agentic-team/agents/*.md`; `.agents/skills/`; `AGENTS.md` | Correct | Inline the router (≤ 25 lines) into the managed block. | agents.md |

### A.2 Candidate targets (P5b)

| Harness | Agent file and keys | Read-only mechanism | Skills | Recommendation |
|---|---|---|---|---|
| GitHub Copilot | `.github/agents/<id>.agent.md`: `name`, `description`, `tools`, `model`, `mcp-servers`, `target`, `disable-model-invocation`, `user-invocable`; body ≤ 30,000 chars. Also reads `.claude/agents/`. | `tools: ["read","search"]` | `.github/skills`, `.agents/skills`, `.claude/skills` | Add (widest reach) |
| Cursor | `.cursor/agents/<id>.md`: `name`, `description`, `model`, `readonly`, `is_background`; no `tools` key. Also reads `.claude/agents/` and scans `.codex/agents/`. Rules `.cursor/rules/*.mdc`. | `readonly: true` | `.agents/skills`, `.cursor/skills` | Add; emit presets, not 50 roles |
| Factory Droid | `.factory/droids/<id>.md`: `name`, `description`, `model`, `reasoningEffort`, `tools`, `mcpServers` | `tools: read-only` | `.factory/skills`, `.agents/skills` | Add (near 1:1 with Claude) |
| Kiro | `.kiro/agents/<id>.json`: `name`, `description`, `prompt` (`file://…`), `model`, `tools`, `allowedTools`, `permissions`, `mcpServers`, `resources` | `tools: ["read"]` + deny `fs_write` | **only** `.kiro/skills/` | Add; copy skills |
| Qwen Code | `.qwen/agents/<id>.md`: `name`, `description`, `tools`, `disallowedTools`, `model`, `approvalMode`, `permissionMode`, `maxTurns`, `mcpServers`, `hooks`; Qwen tool names only (Claude names are silently dropped) | `tools` allowlist | `.qwen/skills`, `.agents/skills` | Add |
| JetBrains Junie | `.junie/agents/<id>.md`: `name`, `description`, `tools`/`disallowedTools`, `model`, `permissionMode`, `reasoningLevel`, `maxTurns`, `skills`, `mcpServers`. Also loads top-level `.agents/*.md` as subagents. | `tools: [Read, Grep, Glob]` or `permissionMode: plan` | `.junie/skills`, `.agents/skills` | Add |
| Augment/Auggie | `.augment/agents/<id>.md`: `name`, `description`, `color`, `model`, `tools`/`disabled_tools` | `disabled_tools` | `.augment/skills`, `.agents/skills` | Optional |
| Amp, Cline, Crush, Zed, Devin Desktop | No stable native agent file (or none needed) | — | `.agents/skills` | `generic` is enough; document collisions |
| Roo Code, Windsurf | Shut down / renamed (Windsurf → Devin Desktop) | — | — | Remove mentions |

### A.3 Access mapping (v3)

| Access | Claude Code | Codex | OpenCode | Gemini CLI | Antigravity |
|---|---|---|---|---|---|
| read-only | `tools: Read, Grep, Glob` | `sandbox_mode = "read-only"` | `edit: deny`, `bash: deny` | `tools: [read_file, list_directory, glob, grep_search]` | ACCESS CONSTRAINT text |
| research | + `WebSearch, WebFetch` | `read-only` (+ web search only if verified) | + `webfetch: allow`, `websearch: allow` | + `google_web_search, web_fetch` | text |
| review | `Read, Grep, Glob, Bash, Write, Edit, WebSearch, WebFetch` + subagent `hooks` limiting Write/Edit to `.agentic-team/runs/**` and the role's playbook | `workspace-write` + text + guard hook | `edit: deny`; bash pattern map (source protection is instruction-only) | + `run_shell_command` (no `write_file`/`replace`) | text |
| workspace-write | `Read, Write, Edit, Grep, Glob, Bash, WebSearch, WebFetch` | `workspace-write` | `edit: allow`; bash pattern map | omit `tools` | default |
| orchestrate | workspace-write + `Agent`; `skills` preload | workspace-write; delegation instructions in AGENTS.md | + `task: allow`; `mode: primary` | default | `mainAgent: true` |

Guard hooks and deny rules come on top of this per §5.12.

### A.4 Standards

- **Agent Skills:** `name` 1–64 chars, lowercase letters/digits/hyphens, matching the folder;
  `description` 1–1024 chars; optional `license`, `compatibility` (≤ 500), `metadata`,
  `allowed-tools` (experimental). `.agents/skills/` is read by nearly every harness except
  Kiro. The five skill names are valid.
- **AGENTS.md:** no required fields; nearest file wins; Gemini CLI needs
  `context.fileName`; Codex caps combined size at 32 KiB; Claude Code reads it only when no
  `CLAUDE.md` exists (an `@AGENTS.md` import works everywhere).
- **Subagent definitions:** no cross-tool standard. Agent Plugins 1.0.0 (2026-08-06) covers
  skills and MCP only. `.claude/agents/` is the most widely read compatibility folder.

### A.5 Still unverified (resolve before emitting)

Antigravity `inheritCustomizations` default and IDE support for `.agents/agents/`; Antigravity
`tools` semantics without `excludeDefaultComponents`; Codex per-agent `approval_policy` and web
search configuration; Cursor parsing of TOML in `.codex/agents/`; Copilot CLI nesting default;
Gemini `policy.toml` rule syntax for command patterns.

---

## Appendix B — Reference tables

### B.1 Vocabulary replacement map (roles, protocols, knowledge, playbooks)

| Banned | Replace with |
|---|---|
| "the run's task board" | the task graph: `add-task`, `status`, `board` |
| "task evidence record" used for questions/notes | `checkpoint --kind decision` for decisions; `add-task` for discovered work; `complete --evidence` for completion |
| "hardening", "hardening gate/phase" | `05_verify` |
| lifecycle "phase", "Ship phase", "at ship" | stage (`06_release` for ship) |
| `lessons.md` as a role's write target | playbook candidate line in `.agentic-team/knowledge/playbooks/<id>.md`; cross-role: `agentic_team.py learn …` |
| `DECISIONS.md` | `_decisions/ADR-NNN.md` (ADR template); approvals are checkpoints |
| `STATUS.md`, `QA.md`, `PLAN.md` | removed (state CLI, `VERIFICATION.md`, task graph) |
| `knowledge/lessons.md`, bare `team.json` paths in roles | `.agentic-team/knowledge/…`, `.agentic-team/team.json` |
| WCAG 2.1 | WCAG 2.2 AA |

### B.2 Artifact and verdict ownership

| Artifact | Stage | Owner | Fallback when not installed |
|---|---|---|---|
| BRIEF.md, ASSUMPTIONS.md | 00 | ceo | fullstack-engineer (solo) |
| PRD.md (`AC-` ids) | 01 | product-manager | ceo |
| ARCHITECTURE.md + `_decisions/ADR-*.md` | 02 | cto-architect | fullstack-engineer |
| DESIGN.md | 02 | ux-ui-designer | frontend-lead |
| Threat model section | 02 | security-engineer (returns content; cto-architect persists if access forbids) | cto-architect |
| READINESS.md, task graph | 03 | delivery-lead | ceo |
| VERIFICATION.md (`Verdict:` PASS/CONDITIONAL/FAIL) | 05 | qa-lead | code-reviewer |
| Blocker findings feeding the verdict | 05 | code-reviewer, security-engineer, triggered specialists | — |
| RELEASE.md | 06 | release-manager | devops-engineer |
| RETROSPECTIVE.md | 07 | delivery-lead (+ cmo section) | ceo |
| DELIVERY-REPORT.md | 07 | ceo (sections from delivery-lead, cmo) | fullstack-engineer |
| MARKETING/BRAND/SEO/SOCIAL/EMAIL/ADS/CREATIVE/METRICS | parallel track, `runs/<id>/_marketing/` | cmo and the named marketing roles | cmo |

One verdict vocabulary everywhere: findings are `blocker | major | minor | nit`; PASS = zero open
blockers; CONDITIONAL = zero blockers, open majors each with an owner and an approved
checkpoint; FAIL = any open blocker.

### B.3 Specialist skeleton (450–800 tokens)

```markdown
---
name: <id>
description: <≤300 chars: what it does. Use when <trigger>. Not for <X> (use <id>).>
---

# <Title>

<One or two sentences of mission.>

## When
Stages and triggers (link specialist-routing vocabulary).

## Inputs
Named artifacts and paths.

## Procedure
1. … (4–7 concrete, checkable steps; named tools/standards)

## Output
Artifact name, location, format; verdict vocabulary if it gates.

## Done when
A checkable bar.

## Hand-offs
Role ids only (manager first).

## Access
What this role may change, and what it returns for others to persist.
```

### B.4 Description rules (enforced by `validate`)

≤ 300 characters; contains a trigger clause ("Use when/to/for", "Activate when") and an
exclusion clause ("Not for … (use <id>)"); no banned vocabulary; orchestrate roles say
"main-session orchestrator". Starting drafts (adjust after the P6 rewrite of each body):

| Role | Draft description |
|---|---|
| ceo | Main-session orchestrator for AgenticTeam runs, not a delegated worker. Use at run start (00_intake) to write BRIEF.md and ASSUMPTIONS.md and pick the roster, at stage gates to accept or reject work against the brief, to arbitrate unresolved disputes, and to write DELIVERY-REPORT.md. |
| fullstack-engineer | Solo builder for small scopes. Use when one agent should take a feature or MVP from schema to API to UI, or when no backend/frontend leads are installed. On team builds, use only for tasks whose owned paths span database, API, and UI; otherwise use backend- or frontend-engineer. |
| qa-lead | Owns the 05_verify verdict. Use to turn PRD acceptance criteria into a risk-based test strategy and traceability matrix, and to issue PASS, CONDITIONAL, or FAIL in VERIFICATION.md from reproduced evidence. Not for writing tests (test-engineer) or reviewing diffs (code-reviewer). |
| code-reviewer | Independent reviewer of a diff, PR, or file set it did not author. Use after a task's tests pass and before merge, for line-anchored correctness, contract, and maintainability findings plus a verdict. Not for threat models, dependency audits, or security sign-off (security-engineer). |
| analytics-engineer | Product measurement owner. Use when a feature needs defined metrics, versioned event schemas, tracking implementation, or experiment design and statistics (sample size, stopping rules). Not for campaign or attribution readouts (growth-analyst) or ETL/warehouse pipelines (data-engineer). |
| growth-analyst | Marketing readouts owner. Use to report campaign and channel performance (spend, CAC, ROAS, funnel conversion) with attribution caveats and to recommend budget reallocation. Consumes analytics-engineer's event contracts and experiment designs; does not define tracking. |
| sre-engineer | Reliability design for systems with an explicit uptime, SLO, or on-call requirement. Use to define SLIs/SLOs and error budgets, alerts, backup/restore tests with RPO/RTO, and incident runbooks. Not for CI/CD or environments (devops-engineer) or the release go/no-go (release-manager). |
| devops-engineer | Build and deploy mechanics. Use for CI pipelines, one-command dev environments, containers, IaC, secret-store wiring, and scripted staging deploy and rollback. Not for SLOs, alert design, or incident runbooks (sre-engineer) or the production release decision (release-manager). |
| eval-engineer | Independent evaluator for LLM, RAG, and agent features. Use when an AI quality claim needs evidence: golden sets with provenance, adversarial and prompt-injection suites, calibrated LLM judges, and a CI regression gate. Not for building the AI feature itself (ai-ml-engineer). |
| platform-admin-engineer | Builds admin, back-office, and internal ops consoles: server-side operations, role and scope authorization, audit events, and safe bulk actions. Use when a task adds or changes a privileged control surface. Moderation policy comes from trust-and-safety-specialist; this role builds the tooling. |
| customer-success-strategist | Post-signup journey designer. Use when a product needs onboarding milestones, a support taxonomy with escalation paths, or retention and customer-health signals. Not for lifecycle email copy (email-marketing-specialist) or developer docs (tech-writer). |
| research-agent | Use when a decision depends on current external facts (library versions, provider APIs, pricing, competitors) that must be cited with dates; state the decision it feeds. Needs web tools. Not for questions the repository itself can answer. |

Also change ai-ml-engineer's "…prompt design, evals, and cost/latency engineering" to
"…prompt design and smoke checks; formal evals go to eval-engineer".

### B.5 Routing vocabulary (word/phrase match, not substring)

| Role | Remove | Add |
|---|---|---|
| eval-engineer | `rag` | `retrieval-augmented`, `chatbot`, `embeddings`, `llm-feature`, `prompt` |
| fusion-moderator | `fusion`, `council` | `fusion-mode`, `council-mode` |
| sre-engineer | `production`, `availability`, `on-call` (substring) | `uptime`, `slo`, `sla`, `on-call rotation` |
| privacy-engineer | `children` | `child-data`, `minors`, `personal-data`, `gdpr` |
| localization-specialist | `rtl` | `right-to-left`, `i18n`, `l10n`, `locale` |
| platform-admin-engineer | `admin`, `operations` | `admin-console`, `back-office`, `ops-console` |
| finops-engineer | `cloud`, `budget` | `cloud-cost`, `cost-ceiling` |
| customer-success-strategist | `saas` | `customer-onboarding`, `support-desk` |
| fraud-risk-analyst | — | `checkout`, `refunds`, `payouts` |
| performance-engineer | — | `p95`, `throughput`, `load-test` |
| trust-and-safety-specialist | — | `comments`, `uploads`, `report-abuse` |
| accessibility-specialist | — | `web-ui`, `forms`, `dashboard` |

Signals are a controlled vocabulary; matching normalizes hyphens and spaces and compares whole
words or phrases. `tests/test_routing.py` must include:

- **Must not activate** (role that v2 wrongly activated): "file storage for test coverage
  reports", "drag-and-drop board", "average order value" (eval-engineer); "confusion matrix",
  "Stable Diffusion images", "city council meetings" (fusion-moderator); "room availability
  calendar", "function calling for the chatbot", "bug reproduction steps" (sre-engineer); "React
  children inside the modal" (privacy-engineer); "recruiters shortlist candidates"
  (localization-specialist); "CRUD operations for invoices" (platform-admin-engineer);
  "performance budget for LCP" (finops-engineer); "migration to add a nullable column"
  (system-mapper); "a simple SaaS to-do app", "developer onboarding section of the README"
  (customer-success-strategist); "deploy a soundcloud clone" (finops-engineer).
- **Must activate:** `personal data` / `gdpr` → privacy-engineer (and compliance-advisor for
  `gdpr`); `checkout refunds payouts` → fraud-risk-analyst; `chatbot embeddings` →
  eval-engineer; `web-ui forms` → accessibility-specialist; `i18n`, `right-to-left` →
  localization-specialist; `p95 throughput` → performance-engineer; `uptime slo` →
  sre-engineer; `comments uploads report-abuse` → trust-and-safety-specialist.

### B.6 Tiers, reporting lines, presets

- Tiers: skill-scout, tech-writer fast→standard; release-manager, eval-engineer
  standard→deep.
- Reporting: eval-engineer → qa-lead (independence from ai-ml-engineer); ux-ui-designer →
  product-manager (or change `frontend-lead.md` to own it — pick one); managers name all their
  reports in their bodies; optionally finops-engineer → cto-architect and
  analytics-engineer → product-manager to cut delivery-lead's 20 direct reports.
- Preset coverage invariants (`validate`): every build preset contains an orchestrator
  (ceo or delivery-lead), a verifier (qa-lead), and a reviewer (code-reviewer); presets with
  parallel writers contain build-integrator; Fusion presets contain a moderator and a verifier
  distinct from contributors; audit presets contain an orchestrator. Fix platform-core,
  regulated-platform, launch, fusion-product-council, audit, scale-readiness accordingly.

### B.7 New protocol contents (P7)

| Protocol | Must say |
|---|---|
| `untrusted-content.md` | Trust tiers: human authority > repository code > agent-written run artifacts > third-party content (web pages, issues, PR comments, dependency READMEs, package metadata, MCP/tool output, fixtures, other agents' proposals). Task inputs carry provenance (`untrusted:<url>`). Untrusted text never creates an R2+ task or a checkpoint question without human confirmation. Nothing untrusted enters playbooks, lessons, or proposals verbatim (playbooks travel between projects). On a suspected injection: stop, preserve the content, `checkpoint --kind injection`. MCP/tool trust: project allowlist of pinned servers, each tool classed read / local-write / external (R3) / destructive (R4); a changed tool description triggers re-review; no credentials to remote servers without a hard-gate checkpoint. |
| `secrets-and-sensitive-data.md` | Humans provision dev secrets via `.env` (never read into prompts; `.env.example` kept current). Secret-scan gate at 05 (e.g., gitleaks) with the command and a zero-findings bar. Redact evidence, events, and reports. Leak response: stop → R4 checkpoint → human rotates → history rewrite only under an approved R4. Synthetic fixtures by default; production-derived data only with an R3 checkpoint and documented anonymisation; no real PII in prompts, evidence, lessons, or screenshots. Owner-token lifecycle: deleted when the run closes. |
| `source-control.md` | Record `base_sha` at `init-run`; one branch/worktree per claimed write task (`at/<run>/<task>`) matching its owned paths; commit trailers `Agentic-Task:` and `Agentic-Agent:` (make authorship and verifier independence checkable); only build-integrator merges, in dependency order; conflicts become integrator tasks; verify at a recorded `integration_sha`; release identity = SHA + build digest; force-push, history rewrite, and shared-branch deletion are R4. Note that Claude Code `isolation: worktree` branches from the default branch, not HEAD. |
| `supply-chain.md` | Before adding a package, confirm it exists and is not a typosquat or hallucinated name (registry age, downloads, repository, maintainer). Commit lockfiles; install with `npm ci` / `uv sync --locked` / hashed pip; `--ignore-scripts` by default. License allowlist (MIT, Apache-2.0, BSD, ISC, MPL); copyleft needs an ADR. SBOM (CycloneDX/syft) and a vulnerability-scan threshold at 05/06. `add-dependency` is one action class (R2). |
| `budgets.md` | The human sets a run budget (tasks, attempts, wall clock, optional tokens/USD) recorded in state; per-task and per-council caps; estimate a Fusion's cost before `fusion-init`; checkpoint at 80 %, stop at 100 %; report actual spend in DELIVERY-REPORT. |
| `team-observability.md` | Events in `events.jsonl`; `metrics` definitions (first-pass completion and retries per role, findings by severity, escapes by stage of origin, checkpoint latency and rejection rate, verification FAIL rate, cost per task); `METRICS.md` per run; no content, only counts, in cross-run rollups. |
| `team-evaluation.md` | Reference scenarios (P8) with seeded defects; score acceptance rate, seeded-defect catch rate, gate violations, human interventions, cost, and time; any protocol or playbook change is A/B tested (≥ 3 runs each, pre-registered threshold) and recorded in PROPOSALS; run before each AgenticTeam release. |
| `harness-security.md` | Threat model (§5.3); the per-harness enforcement table (Appendix A.3 + §5.12) with which rules are enforced vs instruction-only; sandbox guidance (Claude Code sandbox on macOS/Linux/WSL2; WSL2 or a dev container on native Windows); never grant agents read access to `$AGENTIC_TEAM_HOME`; keep production credentials out of agent environments entirely. |

Also: context handoff (trigger at ~70 % context; handoff note with goal, done, evidence, next
command, files touched, what not to retry; `renew` or release the lease) goes into
`communication.md` with a `handoff.md` template; failure signatures and loop detection go into
`autonomy.md`.

### B.8 Role procedure additions (P6)

| Role | Add |
|---|---|
| qa-lead | PASS/CONDITIONAL/FAIL rules (B.2); traceability matrix columns; S1–S4 defect scale with a release rule; defects filed as remediation tasks in the current stage; which checks it re-runs itself via `exec`. |
| security-engineer | OWASP ASVS level choice (L1 default; L2 for PII, payments, admin); STRIDE per trust boundary; scan commands (`osv-scanner`, `pip-audit`, `npm audit`, `gitleaks`, `syft`); OWASP Top 10 for LLM Applications checklist; severity-to-ship rule. |
| delivery-lead | The actual CLI sequence (`add-task` with action/target/paths/checks, `next`, `board`, `recover-leases`, `advance`); READINESS.md contents; RETROSPECTIVE.md answering the evolution questions. |
| accessibility-specialist | WCAG 2.2 AA; axe-core via Playwright and Lighthouse; manual script (keyboard-only, NVDA/VoiceOver, 200 %/400 % reflow, reduced motion); findings as criterion, severity, impact, repro, fix. |
| performance-engineer | Budget table (p50/p95/p99, throughput, error rate, LCP/INP/CLS); load-model template; k6 or Locust plus profilers; ≥ 3 runs with variance; report template. |
| eval-engineer | Eval plan per capability (metric, dataset size and provenance, threshold, baseline); judge calibration against human labels; repeats/temperature for variance; regression gate; prompt-injection suite. |
| sre-engineer | SLO table (SLI, target, window, budget, burn-rate alerts); alert fields (runbook, owner, user impact); restore drill with measured RPO/RTO; production-readiness checklist. |
| release-manager | RELEASE.md as the output; go/no-go checklist (artifact digest, migration forward/back tested, flags, canary percentage and abort thresholds, observation window, comms); consumes the VERIFICATION.md verdict; app-store submission as a release. |
| privacy-engineer | Data inventory columns (element, category, purpose, lawful basis, source, store, access, processors, region, retention, deletion path); DPIA triggers; access/delete/export test cases handed to test-engineer; log-redaction check. |
| analytics-engineer | Metric dictionary (formula, grain, owner, source, freshness); event-schema versioning; experiment pre-registration (hypothesis, primary metric, MDE, sample size, stopping rule, guardrails); data-quality thresholds. |

### B.9 Skill runbook requirements (P7)

- **agentic-build:** precondition `doctor`; branch on `status --brief`/`--json` (blocked →
  stop and show the checkpoint; waiting-human → show pending checkpoints; else continue); the
  human runs `init-run` in their own terminal (exact PowerShell and bash lines); run
  `preflight --format json` into `_context/capabilities.json`; `route-specialists` with the
  controlled vocabulary; per stage: `add-task` (stage, action, target, paths, checks, inputs
  with source sections) → `next` → `claim` → `exec`/`complete --run-checks` → `advance`;
  handle exit codes 2/3; stop on budget exhaustion, a repeated failure signature, or any hard
  gate outside an approved task.
- **agentic-verify:** inputs (PRD `AC-` ids, ARCHITECTURE contracts, `status --json`, base and
  integration SHAs); commands (`git diff --stat <base>..<integration>`, the `ocr delegate`
  sequence when present, the project's test command via `exec`); output VERIFICATION.md from
  the template with the verdict lines; remediation via `findings-to-tasks --apply` in the
  current stage; stop if the verifier claimed any 04_build task.
- **fusion-council:** exact `fusion-init` / `fusion-submit --file` / `fusion-close` sequence;
  contributors work in isolated subagents and do not read `sealed/` before reveal; explicit
  critique assignments; moderator ≠ verifier; human-owner sponsor → stop and hand over.
- **bmad-progressive:** the cold walk test as a procedure (a fresh subagent with only the router
  answers stage, task, next action, output, checkpoint; pass if they match `status --json`);
  who edits which CONTEXT.md sections; `pack` for task packets.
- **agentic-learn:** `learn` with roles, trigger, confidence, and task; candidate → evaluation
  record → PROPOSALS entry → human approval → CHANGELOG; sanitisation checklist.
- All five: `compatibility:` frontmatter, paths under `.agentic-team/bin/`, no restated
  protocol prose; `agents/openai.yaml` sets `policy.allow_implicit_invocation: false` for
  agentic-build, fusion-council, and agentic-learn.

---

## Appendix C — Reproducing the audit

The probes behind §3.1 become the regression tests of P1–P3; each row's "Defect" column is the
scenario to encode. To reproduce a row before fixing it:

1. In Python, set `os.environ["HOME"]` and `os.environ["USERPROFILE"]` to a temp directory
   **before** importing `scripts/agentic_team.py` (after P0, set `AGENTIC_TEAM_HOME`
   instead). On Windows, `Path.home()` reads `USERPROFILE`; exporting a POSIX-style path from
   Git Bash does not isolate it, and a token file lands in the real home directory.
2. `install_team(ROOT, tmp, "generic", "full-company", [], [])`, then `init_run(...)`.
3. Call the function named in the row (`fusion_submit`, `cancel_task`, `advance_stage`, …)
   and assert the defective outcome; after the fix, invert the assertion.

Risk corpus for R-20 (P2): the eleven benign titles — "Write consumer contract tests for
orders API", "Build payment form UI with client-side validation", "Truncate long product
titles in card component", "Purge unused CSS", "Publish domain event to in-process bus",
"Screen reader should announce form errors", "Add billing page skeleton", "POST to /api/users
handler", "Document deployment steps in README", "Credential form field validation", "Add
legal disclaimer footer text" — and the deploy phrasings "Make it live on the prod cluster",
"Ship it", "vercel --prod".
