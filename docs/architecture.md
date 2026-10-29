# Architecture and runtime

AgenticTeam separates probabilistic work from deterministic coordination, and says which layer
backs each promise.

## Three layers

1. **Prompts decide.** Compiled role prompts, protocols, and skills tell each agent what to do,
   when to stop, and what evidence to produce. The harness (Claude Code, Codex, OpenCode, …)
   runs the models, tools, subagents, and worktrees. This layer is instruction: a model can
   ignore it.
2. **The CLI verifies.** `.agentic-team/bin/agentic_team.py` owns run state. It refuses
   transitions that break the rules: claims outside the current stage or owned paths, completion
   without typed evidence, leaving a stage whose exit contract fails, decisions without the owner
   token, high-risk tasks without an approved risk checkpoint. These checks apply on every
   harness, because every transition goes through the CLI. The CLI is stdlib-only Python, makes
   no network or model calls, and stores no credential other than the owner token.
3. **The harness enforces.** Where the harness offers it, the installer emits native permission
   settings (tool allowlists, sandbox modes, permission maps) and a `PreToolUse` guard hook that
   denies agent access to the owner's material, writes to run records, and R3/R4 commands without
   an approved task. Coverage differs by harness: see
   [harness security](../protocols/harness-security.md) and [harnesses](harnesses.md).

None of these layers is an OS boundary. Agents run as the same user as the owner; the runtime
makes shortcuts conspicuous and tampering evident (`doctor`, `audit verify`), and only OS
isolation (a sandbox, WSL2, a dev container, a separate account) makes it impossible. The
[guarantee ledger](#guarantee-ledger) below lists every guarantee with the layer that backs it.

## Policy is data

`config/policies.json` is the single source for autonomy profiles, the seven hard human gates,
the risk matrix (action × target → R0-R4), path rules and wording backstop, command rules shared
by `exec` and the guard hook, stage exit contracts, budgets, and specialist routing vocabulary.
A project-owned `config/policies.local.json` overlays it and may only tighten it (more pauses,
lower caps, extra human gates, extra command rules). `config/guarantees.json` is the guarantee
ledger's source.

## Installed layout

```text
<project>/
  .agentic-team/
    AGENTS.md                 compact router (imported or inlined by the harness root file)
    CURRENT.md                pointer to the active run and stage
    team.json                 installed manifest and roster
    install-manifest.json     generated files with sha256, installer-owned settings entries
    bin/
      agentic_team.py         the state CLI (also the guard hook entry point)
      preflight_skills.py     helpers, also exposed as CLI subcommands:
      findings_to_tasks.py      preflight, findings-to-tasks,
      design_to_admin.py        design-to-admin,
      local_llm_check.py        llm-check,
      agentic_supervisor.py     supervise (the owner-side supervisor)
    supervisor/               supervisor intake and digest (owner-written; agents read only)
      inbox/ quarantine/      trigger events waiting for intake; refused ones with a .reason
      STATUS.md               the digest, rewritten every tick
    config/
      policies.json           generated policy
      guarantees.json         guarantee ledger source
      policies.local.json     optional, project-owned; may only tighten policy
    schemas/                  team and run-state JSON schemas
    protocols/                shared operating law
    templates/                stage, artifact, task, Fusion, and report templates
    knowledge/                project-owned lessons, decisions, playbooks (kept on reinstall)
    backup/                   locally edited generated files saved by install --force
    runs/<run-id>/
      state.json              task, checkpoint, and run state; only the CLI writes it
      events.jsonl            append-only, hash-chained event log
      .state.lock             present only while a command holds the run lock
      00_intake/ … 07_learn/  one CONTEXT.md per stage (regenerated on each transition)
      04_build/tasks/         task envelopes
      BRIEF.md, PRD.md, …     run artifacts, created with `scaffold`
      _evidence/<task>/       exec records (.json) and captured output (.log)
      _context/               task context packets built by `pack`
      _decisions/             ADR-NNN.md architecture decisions
      _fusion/<council-id>/   proposals/, critiques/, synthesis.md, dissent.md, decision.md
      _marketing/             marketing track artifacts (MARKETING.md, owned by the cmo)
  .claude/ .codex/ .opencode/ …   harness-native roles, skills, and settings
```

The owner's material lives **outside the project**, in `~/.agentic-team/` (override with
`AGENTIC_TEAM_HOME`), keyed by `<run-id>.<uid>` so two projects with the same run name never mix:

```text
~/.agentic-team/
  owner-tokens/<run-id>.<uid>.token   the owner token (written by init-run, mode 0600 where supported)
  runs/<run-id>.<uid>.json            the bound owner-key hash
  ledger/<run-id>.<uid>.jsonl         HMAC-signed, hash-chained human decisions
```

Agents must never read this folder; the Claude Code deny rules and the guard hook refuse it.

The supervisor keeps its authoritative records there too, one store per project checkout:

```text
~/.agentic-team/supervisor/<project>-<hash12>/
  config.json, control.json           configuration; checkout reservation, pause, aggregate allowance, reservations
  jobs/<job>.json                     one job: frozen event and configuration, status, attempts, transitions
  sources/<sha256>.json               the idempotency index (one accepted payload per source key)
  attempts/<job>/<attempt>/           intent.json, claim, start.json, worker.json, heartbeat, exit.json,
                                      stdout.jsonl (the frozen transcript), stderr.txt, wrapper.log
  view/                               the verification view a worker reads (binding and ledger, no token)
  worker-home/                        the worker's empty AGENTIC_TEAM_HOME
  log.jsonl, digest.json, .lock       derived log and digest; the cross-process store lock
```

A worker runs with `AGENTIC_TEAM_HOME=worker-home` and `AGENTIC_TEAM_VIEW=view`: it sees the
human's decisions without any token, and the CLI refuses its gated commands if the view is
missing. See the [supervisor operator guide](supervisor-operator-guide.md).

## State invariants the CLI enforces

- **Atomic, locked writes.** Every mutation takes the run lock (`.state.lock`), writes a
  temporary file, and replaces `state.json` atomically. Events go to `events.jsonl`, each line
  carrying the previous line's hash; `state.json` keeps only the head and count.
- **Lifecycle.** Tasks move `pending → ready → claimed → completed`, plus `failed` and
  `cancelled`. A task is `ready` only when every dependency is `completed`.
- **Claims.** The claimant must be installed and be the task owner; the task must belong to the
  current stage; the profile's `max_concurrent_agents` caps open claims; owned paths may not
  overlap (equal or parent/child), and `--exclusive` conflicts with every claim. Build tasks of
  writing roles in `04_build` must declare `--path` or `--exclusive`. A `--verifies` task refuses
  claimants who built the task it verifies.
- **Evidence.** `complete` accepts typed evidence (`file:` hashed, `cmd:` an `exec` record,
  `commit:` resolved with git, `url:`, `note:`). Write tasks need at least one `file:`, `cmd:`, or
  `commit:`; declared `--check` commands must have a passing `exec` record.
- **Risk.** Effective risk is derived from `--action`/`--target`, owned-path rules, and the
  wording backstop; `--risk` can only raise it, and only a human `waive` lowers it. R-levels in
  the profile's `pause_at` (R3/R4 always; hitl also R2) need an approved, CLI-written risk
  checkpoint before `claim`.
- **Human authority.** `approve`, `reject`, `resolve`, `waive`, `cancel`, human `reopen`,
  `promote`, `migrate`, `audit verify`, and a human-sponsored `fusion-close` require the owner
  token; `--by` may not name an installed agent. Decisions are appended to the signed ledger,
  and gates read the ledger, not `state.json`. A mismatch between the state's owner key and the
  bound key makes every gated command refuse. Refused attempts are recorded as
  `authority-refused` events.
- **Checkpoints.** Only the CLI writes `stage` and `risk` checkpoints. Agent checkpoints
  (`decision`, `deviation`, `injection`, `budget`) must carry alternatives, impact, evidence,
  and rollback. Any pending checkpoint blocks `advance`.
- **Blocking.** A rejection sets `blocked-rejection` until the human `resolve`s it; approving
  another checkpoint never clears it. An exhausted task under a stop-on-failure profile sets
  `blocked-failure` until the human reopens with more retries or cancels. Blocked commands exit 3.
- **Stage exits.** `advance` leaves a stage only when every task of the stage is closed, no
  checkpoint is pending, activated specialists are closed out, and the stage exit contract in
  `policies.json` passes (required artifacts without template markers, `AC-` traceability,
  `VERIFICATION.md` verdict lines from a non-builder verifier on the current HEAD, HEAD still
  equal to that verified commit at release, a human release checkpoint, or under `unattended`
  the five executable release conditions for a run with no task above R1). Details:
  [workflow](../protocols/workflow.md).
- **Fusion.** Councils move one way through proposals → critiques → synthesis → verification →
  decision; each submission kind is accepted only in its phase and never twice; moderator,
  verifier, and contributors are distinct. Proposals submitted with `--file` are hashed and
  re-checked at reveal.
- **Budgets.** At the warning threshold the CLI opens a `budget` checkpoint; a command that would
  exceed a limit stops until the human waives it. Autonomous, supervised, and unattended runs start
  only with a token or USD ceiling, and the ceiling counts the larger of what agents report and what the
  owner side meters from the harness transcript (`usage`).
- **Runs.** Only `init-run` and `switch-run` move `CURRENT.md`; `--run` never repoints it.

What the CLI cannot see: actions an agent takes without declaring a task, files edited outside a
task's claimed paths, and whether a document's content is good. Those rest on the harness layer,
reviewers, and the human.

## Model/runtime boundary

The harness runs the models; AgenticTeam does not bundle a model scheduler and never calls a
model. Each role has a `tier` (deep, standard, fast); `install --model-profile` (`inherit`,
`balanced` default, `max-quality`, `economy`) maps tiers to the harness's own model and effort
settings where the harness supports them ([harnesses](harnesses.md)). Native multi-agent
harnesses delegate for real; harnesses without delegation execute role contracts sequentially
against the same task graph. Because all coordination lives in files and the CLI, a run can move
between harnesses without pretending every provider has the same API. Local models work too:
[local LLMs](local-llms.md).

## Extending the roster

1. Write the source role under `agents/<department>/<id>.md`. Specialists follow the skeleton
   `## When`, `## Inputs`, `## Procedure`, `## Output`, `## Done when`, `## Hand-offs`,
   `## Access`, in that order.
2. Register it in `team.json`: `id`, `file`, `department`, `tier`, `access` (`read-only`,
   `research`, `review`, `workspace-write`, `orchestrate`), `reports_to`, `capabilities`, and,
   for conditional specialists, `activate_when` triggers.
3. Add it to a preset only when it belongs there; presets keep their coverage (build presets need
   an orchestrator, `qa-lead`, and `code-reviewer`; Fusion presets need `fusion-moderator` and
   `qa-lead`; audit presets an orchestrator; marketing presets `cmo`).
4. Run `python scripts/agentic_team.py validate` and the tests.

`validate` runs the roster lint: the description (at most 300 characters) needs a trigger clause
("Use when …") and an exclusion clause ("Not for … (use <id>)"); retired v1/v2 vocabulary is
refused; the specialist skeleton is checked; every role id mentioned must exist; each lifecycle
artifact (BRIEF, ASSUMPTIONS, PRD, ARCHITECTURE, DESIGN, READINESS, VERIFICATION, RELEASE,
RETROSPECTIVE, DELIVERY-REPORT, MARKETING) has exactly one `**Owns:**` role; and the compiled
prompt must be 400-2500 tokens. Standing orders every agent needs belong in
`protocols/agent-contract.md`, not in role files.

## Guarantee ledger

<!-- GUARANTEES:BEGIN -->
_Generated from `config/guarantees.json` by `python scripts/agentic_team.py docs --write`._

| Layer | Meaning |
|---|---|
| `cli` | The state CLI refuses the transition (exit 1/2/3). |
| `harness` | Harness configuration or the guard hook refuses the tool call (Claude Code, Codex; OpenCode/Gemini/Copilot/Cursor/Factory/Kiro/Qwen/Junie where their permission fields apply). |
| `tamper-evident` | Not prevented, but detected afterwards by doctor or audit verify. |
| `instruction` | Only the role prompts and protocols ask for it. |

| ID | Guarantee | Backed by | Test | Known bypass |
|---|---|---|---|---|
| G01 | Human decisions (approve, reject, resolve, waive, cancel, reopen, promote, human fusion-close) need the owner token; an edited state.json approves nothing. | cli, tamper-evident | `test_authority.ForgeryTests` | An agent that reads the token from ~/.agentic-team (blocked by harness rules; only an OS sandbox makes it impossible). |
| G02 | A stage exits only with its exit contract met (artifacts without template markers, AC traceability, typed evidence, VERIFICATION verdict lines), no pending checkpoint, and finished specialists. | cli | `test_evidence.StageExitTests` | A human waiver (stage-exit:<stage>:<check>); artifact content quality is judged by reviewers, not the CLI. |
| G03 | The verifier is not a builder: --verifies tasks refuse their builders and VERIFICATION.md's Verifier may not be a 04_build claimant. | cli | `test_evidence.VerificationTests` | Agent identity is self-declared: an agent could claim under another role id. |
| G04 | Task risk comes from the declared action and target, raised by sensitive paths and operating-on-the-world wording; only the human lowers it. | cli | `test_authority.RiskModelTests` | A task declared as a benign action that later runs a deploy command; G05 catches the command where hooks exist. |
| G05 | Commands matching an R3/R4 command rule (deploys, publishes, force pushes, infrastructure apply, global installs) run only inside a claimed task of that action with a human-approved risk checkpoint. | harness, cli | `test_harness.GuardTests.test_external_commands_need_an_approved_task` | Harnesses without a hook (Pi, generic, and the six newer targets) and deliberately obfuscated commands. |
| G06 | Agents never read or write ~/.agentic-team (owner tokens, key bindings, ledger). | harness, instruction | `test_harness.GuardTests.test_owner_home_is_off_limits` | A subprocess that opens the file indirectly without naming the path, and harnesses without the guard hook; only an OS sandbox (macOS/Linux/WSL2) prevents it. |
| G07 | Only the CLI writes state.json, events.jsonl, and _evidence/. | harness, tamper-evident | `test_orchestration.EventLogTests.test_event_chain_detects_edits` | Edits in harnesses without hooks; detected by doctor/audit verify (event hash chain, owner-key binding). |
| G08 | Fusion councils run in phase order, without resubmission, with moderator, verifier, and contributors independent. | cli | `test_regressions.FusionRegressions` | None within the CLI. |
| G09 | Fusion proposals stay private until every contributor has submitted, and cannot be rewritten after submission. | harness, tamper-evident, instruction | `test_harness.GuardTests.test_fusion_proposals_stay_private_until_reveal` | Reading other proposals in harnesses without the guard hook; rewrites are caught at reveal only when submitted with --file. |
| G10 | Completion evidence is typed and checked: files exist and are hashed, exec records carry exit codes, commits resolve; build and remediation tasks by writing roles must declare an acceptance check, and complete runs every check lacking a passing record at the current HEAD and refuses while one fails. | cli | `test_evidence.EvidenceTests` | Note-only evidence remains allowed for inspection and documentation tasks; a task recorded before checks were required completes only with the human's checks:<task> waiver; the check command itself is what the task author declared. |
| G11 | Claims respect ownership, the current stage, owned-path overlap, and the concurrency cap. | cli | `test_regressions.LifecycleRegressions.test_R16_claim_requires_installed_owner_and_respects_cap` | Editing files outside the claimed paths is not detected (instruction). |
| G12 | Review roles never edit project source. | harness, instruction | `test_harness.GuardTests.test_review_scope_limits_writes` | Shell commands that write files, and every harness other than Claude Code. |
| G13 | Budgets open a checkpoint at the warning threshold and stop the command that would exceed them; a per-run --budget only tightens the policy's ceiling. | cli | `test_orchestration.MetricsAndBudgetTests.test_budget_warns_then_stops_until_the_human_waives` | Token and USD ceilings see what agents report and what the owner side meters from harness transcripts (G19); a harness that writes no transcript is unmetered. |
| G14 | A rejection blocks the run until the human resolves it; exhausted retries in hitl block until the human reopens or cancels. | cli | `test_regressions.LifecycleRegressions.test_R05_rejection_can_be_resolved_by_the_human` | None within the CLI. |
| G15 | Playbook checks become proven only through the human's promote. | cli, instruction | `test_law.LearningLoopTests.test_only_the_human_promotes_a_playbook_check` | Playbooks are ordinary files: an agent can edit the status text directly (visible in review and the ledger has no record). |
| G16 | The seven hard human gates (R3/R4 actions) hold in every autonomy profile, unattended included; the release-stage exit is a human checkpoint in autonomous, supervised, and hitl, and executable only under unattended for a run with no task above R1. | cli, harness, instruction | `test_authority.RiskModelTests.test_hard_gates_hold_under_unattended` | An action taken without any declared task in a harness without hooks; keep production credentials out of agent environments. |
| G17 | A task that fails the same way twice stops retrying; only the human reopens it. | cli | `test_regressions.LifecycleRegressions.test_repeated_failure_signature_stops_retrying` | Failure reasons worded differently each time produce different signatures. |
| G18 | Verification is pinned to the code being released: Verified-SHA must equal the current HEAD when 05_verify exits, and 06_release cannot exit while HEAD differs from the verified commit. | cli | `test_evidence.VerificationTests.test_verified_sha_must_be_the_current_head_through_release` | Projects without git history (Verified-SHA: none); uncommitted edits do not move HEAD; the human's stage-exit:06_release:verified-head waiver. |
| G19 | Autonomous, supervised, and unattended runs start only with a token or USD ceiling, and the ceiling counts the larger of agent-reported usage and usage metered from the harness transcript by the owner side (usage --transcript, signed into the ledger). | cli | `test_orchestration.MetricsAndBudgetTests.test_metered_usage_comes_from_the_harness_transcript_and_counts_against_the_ceiling` | Metering depends on whoever launched the session running usage with the transcript; the figures are the harness's client-side estimate. |
| G20 | Under unattended, 06_release exits without a human checkpoint only when the exit contract passes (verified-head included), every completed build and verify task has a passing exec record for each declared check, no task in the run is above R1 (one R2+ task puts the human checkpoint back), RELEASE.md is complete and a rollback-test task by release-manager or devops-engineer passed its declared rollback command at the current HEAD, and no budget checkpoint is pending; release_gate executable is refused on every other profile, and policies.local.json can set it back to human. | cli | `test_unattended.UnattendedReleaseTests` | The checks and the rollback command are what the task authors declared; work declared as a benign action (G04's bypass) looks low-risk; the human's stage-exit:06_release:<check> waivers cover the exit contract; actions taken without a task are invisible, as everywhere. |
| G21 | A worker started with AGENTIC_TEAM_VIEW reads human decisions only from that owner-exported view (binding and ledger, no token), never from its own writable home; a v3 run with neither the home binding nor a view counts no decision in state.json and refuses gated commands; the owner's audit verify replays every stage exit through a human gate, every claim of a risk-gated task, and every waiver against the signed home ledger. | cli | `test_authority.VerificationViewTests` | The gates run in the worker's own process, which can point the CLI at a view it wrote or edit state.json; that is found by the owner's audit after the attempt, not prevented, so production credentials must stay out of the worker's reach. |
| G22 | Once a token or USD ceiling is spent, claim and exec refuse new work until the human waives budget:<metric>, while status, metering, fail, recover-leases and human decisions keep working; usage figures that are not finite or are negative are refused. | cli | `test_orchestration.MetricsAndBudgetTests.test_spent_budget_stops_new_work_but_not_recovery` | Spend inside a running harness session is metered only after the session ends; the ceiling stops the next command, not the session. |
| G23 | The supervisor keeps one writer per checkout: the checkout is bound to one owner store, so another store (another --store, owner home, or path alias) or a store recorded for another project launches nothing until the owner moves the binding from an idle store; each attempt and its budget reservation are recorded before its wrapper starts, exactly one wrapper can claim an attempt, a late wrapper finds it abandoned, an attempt whose processes cannot be shown to have stopped holds instead of relaunching, task leases are never released while the previous writer may act, a cancelled or held job keeps the checkout until its last attempt is reconciled, and a missing, moved, or torn job record keeps its reservations and checkout claim under an orphan-recovery hold; the store lock is an operating-system lock released when its holder dies. | cli | `test_supervisor.LaunchRecoveryTests` | Process identity relies on the platform's process start time; where it cannot be read the supervisor holds for the owner. The checkout binding is a file in the checkout: a worker that deletes it lets a second store the owner runs bind the checkout. |
| G24 | A supervised job is done only when the attempt's frozen transcript was metered exactly once from a numeric USD figure and the run's usage record matches a usage record signed into the owner ledger (missing, null, or non-numeric USD and unsigned or edited projections stay unknown), no checkpoint is pending, audit verify passes, the owner-side re-check of the verification, release, and learning exit contracts and of the event log agrees the run completed, and the tree (with no hidden or unreadable state) is clean at the verified commit; unknown usage keeps its reservation counted and holds further paid work until the owner resolves it. | cli | `test_supervisor.MeteringTests` | Cost figures are the harness's client-side estimate; a command-adapter worker reports whatever its output's result line says; a worker that can write the run folder could forge a consistent set of artifacts and events, which independent verification and owner review address. |
| G25 | The supervisor holds rather than decides: it never approves, rejects, resolves, waives, or reopens; it runs its owner-side work from an owner copy outside the checkout, never from the project's bin/; a forged state approval, a step without a signed decision, or an edited or deleted view file holds the job as tampering. | cli, harness | `test_supervisor.TamperTests` | On the same OS user without an isolation boundary a worker could edit the owner store; audit verify and the view digests detect forgery after the attempt, not before. Paid workers therefore require a verified boundary that hides the store and keeps the view read-only. |
<!-- GUARANTEES:END -->
