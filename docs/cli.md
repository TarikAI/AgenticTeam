# Runtime CLI reference

There are two invocation forms, and they are not interchangeable.

**Run commands** operate on an installed project and take `--project`:

```text
python .agentic-team/bin/agentic_team.py <command> --project .
```

**Compiler commands** operate on the AgenticTeam source checkout and take no `--project`:

```text
python scripts/agentic_team.py <command>
```

Running a compiler command from an installed copy is refused with an explanatory error,
because the installed bus has no role source tree. To check an installation, use
`doctor --project .`.

The harness orchestrator normally invokes these. Humans can use them to inspect or recover a run.

## Compiler commands (run from the source checkout)

| Command | Purpose |
|---|---|
| `validate` | Check manifest, role files, presets, workflows, skills, and required contracts. |
| `list agents\|presets\|harnesses` | Inspect installable capabilities. |
| `install <target> --harness H --preset P [--model-profile M] [--force]` | Compile a native package and durable bus. Stops if a generated file was edited locally (`--force` backs it up). |
| `uninstall <target> [--purge]` | Remove generated files, managed blocks, skills, and installer-owned settings; keeps `knowledge/` and `runs/` unless `--purge`. |
| `guard [--harness H] [--scope review --agent A]` | Harness `PreToolUse` hook entry point (reads the tool call JSON on stdin). |

## Run commands (run against an installed project)

| Command | Required intent |
|---|---|
| `init-run` | Create numbered stages and atomic state with entry/context/autonomy choices. |
| `status [--json]` | Read current stage, task counts, checkpoints, rejections, failed tasks, and Fusion sessions. |
| `status --brief` | At most 20 lines for agents, including what is ready now and reported usage. |
| `next [--agent A] [--json]` | Tasks an agent can claim right now (ready, current stage, owned, no path conflict, under the cap). |
| `board [--format md\|mermaid\|json]` | The task graph by stage and status. |
| `pack --task T` | Build the task's context packet under `_context/` within `context_target_tokens` (2K-8K), listing what was truncated or omitted. |
| `brief --task T` | The delegation message an orchestrator hands the task's subagent (points at its packet). |
| `log [--type T] [--since N] [--json]` | Read `events.jsonl`, the run's append-only, hash-chained event log. |
| `metrics [--json] [--write]` | Per-role completion, first-pass rate, failures; checkpoint latency and rejection rate; commands; usage. `--write` saves `METRICS.md`. |
| `runs` / `switch-run --run R` / `close-run --reason` | List runs, point `CURRENT.md` at another run, or close one. Only `init-run` and `switch-run` move `CURRENT.md`. |
| `route-specialists` / `deactivate-specialist` | Match installed trigger rules and record bounded specialist participation. |
| `add-task` | Create a task envelope. The owner must be installed; the stage defaults to the current stage and may not be an earlier one; build and remediation tasks owned by a writing role need `--path` (or `--exclusive`) and at least one `--check CMD`, the acceptance command `complete` runs. `--verifies T` marks a verification task whose claimant may not have built T. |
| `claim` | Atomically claim a ready task of the current stage. The claiming agent must be installed and be the task owner; the profile's `max_concurrent_agents` caps open claims; owned paths may not overlap. |
| `renew` | Extend the lease on a task you hold (1-480 minutes). |
| `reassign` | Change the owner of an unclaimed open task, with a reason. |
| `complete [--run-checks] [--usage tokens=N,usd=N]` | Attach typed evidence (`file:`, `cmd:`, `commit:`, `url:`, `note:`) and unlock dependents. Runs every `--check` command that has no passing record at the current HEAD (all of them with `--run-checks`) and refuses while one fails. Write tasks need at least one `file:`/`cmd:`/`commit:`. |
| `supervise enqueue\|configure\|serve\|status\|pause\|resume\|cancel\|release\|allowance\|verify-isolation\|owner-copy\|poll-github\|host-example\|prune` | Owner side: the durable supervisor; `serve`, `resume`, `poll-github`, and `verify-isolation` run only from its owner copy outside the checkout. Turns triggers into runs with one bounded worker per checkout, meters and audits every attempt, and holds for the human instead of deciding ([operator guide](supervisor-operator-guide.md)). `serve` exits 0 ok, 1 error, 2 a job needs the human, 3 blocked. |
| `export-view --to DIR` | Owner side: copy the run's binding and ledger (no token) into `DIR`, the verification view a worker reads through `AGENTIC_TEAM_VIEW`; a `view.json` manifest records both digests. |
| `usage --transcript FILE [--task T] --by NAME --token-file PATH` | Owner side: record the tokens and USD the harness itself reported (Claude Code `json`/`stream-json` result message), hashed and signed into the ledger. The larger of reported and metered usage counts against the ceilings. |
| `exec --task T --agent A [--shell] -- CMD...` | Run a command for your claimed task; records exit code, duration, git HEAD, and output under `_evidence/`. Commands matching a policy command rule need an approved task of that action. Exit code mirrors the command (0/1). |
| `scaffold --artifact NAME` | Create `BRIEF.md`, `PRD.md`, `READINESS.md`, `VERIFICATION.md`, `RELEASE.md`, and the other run artifacts from their templates. |
| `fail` | Record an attempt and apply retry policy. Under a profile that stops on failure (hitl), an exhausted task blocks the run (`blocked-failure`). |
| `recover-leases` | Return expired claims to policy-controlled state. |
| `checkpoint` / `approve` / `reject` / `resolve` | Create and decide a human checkpoint. A rejection blocks the run (`blocked-rejection`) until the human `resolve`s it after the correction. Approving another checkpoint never clears a rejection. |
| `advance` | Exit the current stage only when every task of the stage is closed (completed or cancelled), no checkpoint is pending, the stage exit contract passes (`protocols/workflow.md`), and policy gates pass. |
| `fusion-init` | Create private proposal/critique/synthesis/dissent/decision artifacts. |
| `fusion-submit` | Record a proposal, critique, revision (one per contributor), synthesis, or verification. Each kind is accepted only in its phase and never twice. |
| `fusion-close` | Record the sponsor's decision after independent verification. A `human-owner` sponsor needs `--by` and the owner token. |
| `learn` | Record an evidence-scoped, non-promoted learning candidate. |
| `report` | Generate `DELIVERY-EVIDENCE.md` from state. It never overwrites the ceo's `DELIVERY-REPORT.md`. |
| `doctor` | Diagnose the installation (missing or locally modified generated files, version) and the active run (blocked, pending checkpoints, expired leases). Exits 1 when it finds anything. |
| `preflight [--require NAME]` | Report available external skills/tools; exit 1 when a required one is missing. |
| `findings-to-tasks FILE [--project P] [--apply] [--commands --shell bash\|powershell]` | Verdict plus remediation tasks owned by installed writable roles, in the current stage. |
| `design-to-admin` / `llm-check` | The design-architect bridge and the local-LLM endpoint check. |

Use `--help` on any command for exact flags. All mutations take a run lock and atomically replace
state; do not edit `state.json` manually. Events are appended to `runs/<id>/events.jsonl`, each line
carrying the previous line's hash; `doctor` and `audit verify` report a broken chain.

Budgets (`config/policies.json` → `budgets`: `max_tasks`, `max_fusion_councils`, `max_lease_minutes`,
and `tokens`/`usd`, fed by `complete --usage` and by owner-side `usage --transcript` metering and
required before an autonomous, supervised, or unattended run starts) open a `budget` checkpoint at `warn_at`
(80 %) and stop the command that would exceed the limit until the human runs
`waive --requirement budget:<metric>`.

## Recovery commands

| Command | Use when |
|---|---|
| `unlock [--force]` | A command was killed mid-run and left `.state.lock` behind. Without `--force` a lock younger than 30s is kept, in case a command really is running. |
| `reopen --task T --reason R` | A claim wedged: return it to the queue (counts as an attempt). Reopening a failed, cancelled, or completed task, or `--extend-retries N`, is a human decision: add `--by` and the owner token. Attempt history is kept. |
| `cancel --task T --reason R --by NAME` | The human descoped the work (owner token required). Refuses while open dependents exist unless `--cascade`. Cancelled tasks no longer hold the stage gate. |

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Command succeeded. |
| `1` | Command failed (see stderr). |
| `2` | Stopped at a human gate (`advance` or `claim` needs a checkpoint decision). Scripts using `advance && next-step` stop instead of walking through the gate. |
| `3` | The run is blocked: an unresolved rejection or an exhausted task needs a human. |
| `64` | Usage error (unknown command or flag). |

## Human decisions: the owner token and the decision ledger

`init-run` issues an owner token and writes it **outside the project**, under
`~/.agentic-team/owner-tokens/<run-id>.<uid>.token` (override the folder with `AGENTIC_TEAM_HOME`).
It also binds the token's hash outside the project (`~/.agentic-team/runs/`). `approve`,
`reject`, `resolve`, `waive`, `cancel`, human `reopen`, `migrate`, and a human-sponsored
`fusion-close` require the token; each decision is appended to an HMAC-signed, hash-chained
ledger at `~/.agentic-team/ledger/`. Gates read the ledger, not `state.json`, so an edited state
file cannot approve anything, and a mismatched owner key makes every gated command refuse.

Never put the token in argv (shell history, process lists). In your own terminal:

```powershell
python .agentic-team/bin/agentic_team.py approve --project . --checkpoint CP-001 --by "Your Name" --decision "approved after review" --token-file "$HOME\.agentic-team\owner-tokens\<run-id>.<uid>.token"
```

```bash
python .agentic-team/bin/agentic_team.py approve --project . --checkpoint CP-001 --by "Your Name" --decision "approved after review" --token-file ~/.agentic-team/owner-tokens/<run-id>.<uid>.token
```

Omit `--token-file` in an interactive terminal and you are prompted without echo;
`--token-stdin` reads one line from stdin. `--token VALUE` still works but warns.

| Command | Use |
|---|---|
| `waive --requirement risk:<task> --level R1 --reason R --by NAME` | Lower one task's effective risk (only a human may). |
| `waive --requirement stage-exit:<stage>:<check> --reason R --by NAME` | Waive one named stage-exit requirement. |
| `audit verify --by NAME --token-file F` | Recompute every ledger signature and chain link and compare state with the ledger. |
| `migrate --by NAME --token-file F` | Upgrade a v2 run: bind the owner key and sign its past decisions. |

Rules that make the gate meaningful: `--by` may not name an installed agent, and an agent must
never be able to read `~/.agentic-team/`. The installer's harness rules (see
`docs/harnesses.md`) deny that path; this protects against shortcuts and prompt-injected
self-approval, not against deliberately malicious code running unsandboxed as your user.

## Risk: action and target

`add-task --action A --target T` declares what a task does and where. `config/policies.json`
maps the pair to R0-R4 (`risk.matrix`), owned paths such as CI definitions, migrations, and
dependency manifests raise the floor (`risk.path_rules`), and wording that describes operating
on the world ("--prod", "terraform apply") raises it further (`risk.backstop`). `--risk` is a
requested floor; the runtime never lowers below what it derives, and only a human `waive` can.
Agent checkpoints (`--kind decision|deviation|injection|budget`) must carry `--alternatives`,
`--impact`, `--evidence`, and `--rollback`; stage and risk gates are written by the CLI itself.

## Full command reference

<!-- CLI-REFERENCE:BEGIN -->
_Generated by `python scripts/agentic_team.py docs --write`; do not edit by hand._

### `add-task`

Add a task envelope to the run graph

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--id` | yes |  |  |
| `--title` | yes |  |  |
| `--objective` |  |  |  |
| `--owner` | yes |  |  |
| `--stage` (00_intake|01_product|02_solution|03_readiness|04_build|05_verify|06_release|07_learn) |  |  | Defaults to the run's current stage |
| `--risk` (R0|R1|R2|R3|R4) |  | `R1` | Requested floor; the runtime may raise it |
| `--action` |  | `build` | What the task does (see config/policies.json risk.actions) |
| `--target` |  | `local` | Where it acts: local, ci, staging, production, external |
| `--depends-on` |  |  |  |
| `--path` |  |  |  |
| `--exclusive` |  |  | Claim the whole workspace (conflicts with every other claim) |
| `--input` |  |  |  |
| `--acceptance` |  |  |  |
| `--evidence-contract` |  |  |  |
| `--check` |  |  | Acceptance command that must pass (repeatable) |
| `--verifies` |  |  | Task this one verifies; its builders cannot claim it |

### `advance`

Advance after task and policy gates pass

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |

### `approve`

Record explicit human checkpoint approval

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--checkpoint` | yes |  |  |
| `--decision` | yes |  |  |
| `--by` | yes |  | Name of the responsible human (never an agent id) |
| `--token-file` |  |  | Read the owner token from this file (never pass it in argv) |
| `--token-stdin` |  |  | Read the owner token from stdin |
| `--token` |  |  | Deprecated: owner token in argv (lands in shell history) |

### `audit`

Human audit of the decision ledger

| Flag | Required | Default | Meaning |
|---|---|---|---|
| verify | yes |  | subcommand |

### `board`

Task graph by stage and status

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--format` (md|mermaid|json) |  | `md` |  |

### `brief`

Print the delegation message for a task's subagent

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--task` | yes |  |  |

### `cancel`

Human descopes a task so it stops blocking the stage gate

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--task` | yes |  |  |
| `--reason` | yes |  |  |
| `--cascade` |  |  | Also cancel every open dependent |
| `--by` | yes |  | Name of the responsible human (never an agent id) |
| `--token-file` |  |  | Read the owner token from this file (never pass it in argv) |
| `--token-stdin` |  |  | Read the owner token from stdin |
| `--token` |  |  | Deprecated: owner token in argv (lands in shell history) |

### `checkpoint`

Create a human decision checkpoint

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--question` | yes |  |  |
| `--recommendation` | yes |  |  |
| `--risk` (R0|R1|R2|R3|R4) |  | `R2` |  |
| `--kind` (budget|decision|deviation|injection) |  | `decision` |  |
| `--alternatives` | yes |  |  |
| `--impact` | yes |  |  |
| `--evidence` | yes |  |  |
| `--rollback` | yes |  |  |

### `claim`

Atomically claim a ready task

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--task` | yes |  |  |
| `--agent` | yes |  |  |
| `--lease-minutes` |  | `60` |  |

### `close-run`

Close a run (it stops accepting work)

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--reason` | yes |  |  |

### `complete`

Complete a claimed task with evidence

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--task` | yes |  |  |
| `--agent` | yes |  |  |
| `--evidence` |  |  | file:<path>, cmd:<exec-id>, commit:<sha>, url:<url>, or note:<text> |
| `--run-checks` |  |  | Run the task's --check commands through exec first |
| `--usage` |  |  | Reported cost, e.g. tokens=12000,usd=0.40 |

### `deactivate-specialist`

Close a bounded specialist activation with its result

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--agent` | yes |  |  |
| `--reason` | yes |  |  |

### `design-to-admin`

Draft an adminwright manifest from a design-architect handoff

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `helper_args` |  |  |  |

### `docs`

Regenerate (or check) the CLI reference and the guarantee ledger in docs/

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--write` |  |  | Write the generated sections |
| `--check` |  |  | Exit 1 if a generated section is stale |

### `doctor`

Check an installed team and active run

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` |  |

### `exec`

Run a command for a claimed task and record its exit code and output

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--task` | yes |  |  |
| `--agent` | yes |  |  |
| `--shell` |  |  | Run the command through the shell |
| `cmd` |  |  | -- <command...> |

### `export-view`

Owner side: export a run's binding and ledger (no tokens) as a worker's verification view

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--to` | yes |  | Directory the worker reads through AGENTIC_TEAM_VIEW |

### `fail`

Record a failed attempt and apply retry policy

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--task` | yes |  |  |
| `--agent` | yes |  |  |
| `--reason` | yes |  |  |
| `--signature` |  |  | Short failure fingerprint; the same one twice stops retrying (default: derived from --reason) |

### `findings-to-tasks`

Turn review findings into a verdict and runnable remediation tasks

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `helper_args` |  |  |  |

### `fusion-close`

Record the sponsor's final council decision

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--fusion` | yes |  |  |
| `--sponsor` | yes |  |  |
| `--decision` | yes |  |  |
| `--by` |  |  | Name of the responsible human (never an agent id) |
| `--token-file` |  |  | Read the owner token from this file (never pass it in argv) |
| `--token-stdin` |  |  | Read the owner token from stdin |
| `--token` |  |  | Deprecated: owner token in argv (lands in shell history) |

### `fusion-init`

Create an independent fusion council workspace

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--id` | yes |  |  |
| `--question` | yes |  |  |
| `--sponsor` |  | `human-owner` |  |
| `--moderator` |  | `fusion-moderator` |  |
| `--verifier` |  | `qa-lead` |  |
| `--contributor` | yes |  |  |

### `fusion-submit`

Record a council proposal, critique, revision, synthesis, or verification

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--fusion` | yes |  |  |
| `--kind` (proposal|critique|revision|synthesis|verification) | yes |  |  |
| `--agent` | yes |  |  |
| `--evidence` | yes |  |  |
| `--file` |  |  | Submitted file; its hash is recorded and re-checked at reveal (commit-reveal) |

### `guard`

Harness PreToolUse hook: read the tool call as JSON on stdin; deny unsafe calls

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--harness` |  | `claude-code` |  |
| `--scope` (review) |  |  |  |
| `--agent` |  |  |  |

### `init-run`

Create a resumable progressive run

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` |  |
| `--name` | yes |  |  |
| `--run-id` |  |  |  |
| `--autonomy` (autonomous|supervised|hitl|unattended) |  | `hitl` |  |
| `--entry` (idea|plan-given|execute-only) |  | `idea` |  |
| `--context` (adaptive|bmad-progressive) |  | `adaptive` |  |
| `--budget` |  |  | Spend ceiling for this run, e.g. usd=40 or tokens=3000000; only tightens the policy's. Autonomous, supervised, and unattended runs refuse to start without one |

### `install`

Compile and install native definitions into a project

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `target` | yes |  |  |
| `--harness` | yes |  |  |
| `--preset` |  | `full-company` |  |
| `--agent` |  |  | Add an agent beyond the preset |
| `--only-agent` |  |  | Install an exact custom selection; repeat per agent |
| `--model-profile` |  |  | Tier-to-model mapping: inherit, balanced (default), max-quality, economy |
| `--force` |  |  | Overwrite locally modified generated files (backed up first) |

### `learn`

Record an evidence-scoped learning candidate

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--title` | yes |  |  |
| `--evidence` | yes |  |  |
| `--lesson` | yes |  |  |
| `--scope` | yes |  |  |
| `--counterexample` | yes |  |  |
| `--roles` |  | `` | Comma-separated role ids the lesson applies to (default: all) |
| `--trigger` |  | `` | The situation that should bring this lesson to mind |
| `--confidence` (low|medium|high) |  | `medium` |  |
| `--task` |  |  | Task the evidence comes from |

### `list`

List available agents, presets, or harnesses

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `kind` (agents|presets|harnesses) | yes |  |  |

### `llm-check`

Report reachable local LLM endpoints

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `helper_args` |  |  |  |

### `log`

Read the run's event log

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--type` |  |  |  |
| `--since` |  |  | Only events after this sequence number |
| `--json` |  |  |  |

### `metrics`

Run metrics per role, checkpoints, commands, usage

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--json` |  |  |  |
| `--write` |  |  | Also write METRICS.md in the run folder |

### `migrate`

Upgrade a run to this version (binds the owner key, signs past decisions)

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--by` | yes |  | Name of the responsible human (never an agent id) |
| `--token-file` |  |  | Read the owner token from this file (never pass it in argv) |
| `--token-stdin` |  |  | Read the owner token from stdin |
| `--token` |  |  | Deprecated: owner token in argv (lands in shell history) |

### `next`

Tasks an agent can claim right now

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--agent` |  |  |  |
| `--json` |  |  |  |

### `pack`

Build the task context packet (2K-8K tokens) under _context/

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--task` | yes |  |  |

### `package-claude-plugin`

Build a Claude Code plugin and marketplace from the full roster

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `out_dir` | yes |  | Marketplace folder to create (e.g. dist/claude-plugin) |
| `--model-profile` |  |  | Tier-to-model mapping (default from team.json) |

### `preflight`

Report which external skills/tools are available (non-zero when --require is missing)

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `helper_args` |  |  |  |

### `promote`

Human marks a candidate playbook check as proven

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--role` | yes |  |  |
| `--match` | yes |  | Unique text of the candidate check |
| `--by` | yes |  | Name of the responsible human (never an agent id) |
| `--token-file` |  |  | Read the owner token from this file (never pass it in argv) |
| `--token-stdin` |  |  | Read the owner token from stdin |
| `--token` |  |  | Deprecated: owner token in argv (lands in shell history) |

### `reassign`

Change the owner of an unclaimed open task

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--task` | yes |  |  |
| `--owner` | yes |  |  |
| `--reason` | yes |  |  |

### `recover-leases`

Recover expired task claims according to retry policy

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |

### `reject`

Record explicit human rejection and block the run for correction

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--checkpoint` | yes |  |  |
| `--decision` | yes |  |  |
| `--by` | yes |  | Name of the responsible human (never an agent id) |
| `--token-file` |  |  | Read the owner token from this file (never pass it in argv) |
| `--token-stdin` |  |  | Read the owner token from stdin |
| `--token` |  |  | Deprecated: owner token in argv (lands in shell history) |

### `renew`

Extend the lease on a task you hold

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--task` | yes |  |  |
| `--agent` | yes |  |  |
| `--lease-minutes` |  | `60` |  |

### `reopen`

Return a wedged claim to the queue; failed/cancelled/completed tasks need a human

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--task` | yes |  |  |
| `--reason` | yes |  |  |
| `--extend-retries` |  |  | Human only: extra attempts for this task |
| `--by` |  |  | Name of the responsible human (never an agent id) |
| `--token-file` |  |  | Read the owner token from this file (never pass it in argv) |
| `--token-stdin` |  |  | Read the owner token from stdin |
| `--token` |  |  | Deprecated: owner token in argv (lands in shell history) |

### `report`

Generate DELIVERY-EVIDENCE.md from durable state

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |

### `resolve`

Human closes a rejection after the correction; unblocks the run

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--checkpoint` | yes |  |  |
| `--resolution` | yes |  |  |
| `--by` | yes |  | Name of the responsible human (never an agent id) |
| `--token-file` |  |  | Read the owner token from this file (never pass it in argv) |
| `--token-stdin` |  |  | Read the owner token from stdin |
| `--token` |  |  | Deprecated: owner token in argv (lands in shell history) |

### `route-specialists`

Activate installed specialists whose triggers match project signals

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--signal` | yes |  |  |
| `--json` |  |  |  |

### `runs`

List runs in this project

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` |  |
| `--json` |  |  |  |

### `scaffold`

Create a run artifact from its template

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--artifact` | yes |  |  |

### `status`

Show durable run status

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--json` |  |  |  |
| `--brief` |  |  | At most 20 lines, with what is ready now (for agents) |

### `supervise`

Owner side: turn triggers into runs with one bounded worker per checkout (enqueue, serve, status, resume, cancel)

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `helper_args` |  |  |  |

### `switch-run`

Point CURRENT.md at another run

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` |  |
| `--run` | yes |  |  |

### `uninstall`

Remove an installation (keeps knowledge/ and runs/ unless --purge)

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `target` | yes |  |  |
| `--purge` |  |  |  |

### `unlock`

Clear a state lock left by a process that died

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--force` |  |  | Clear even a recently touched lock |

### `usage`

Record usage metered from a harness transcript (owner side; it counts against the ceilings)

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--transcript` | yes |  | Claude Code --output-format json or stream-json output; its last result message is read |
| `--task` |  |  | Also attribute the figures to this task |
| `--by` | yes |  | Name of the responsible human (never an agent id) |
| `--token-file` |  |  | Read the owner token from this file (never pass it in argv) |
| `--token-stdin` |  |  | Read the owner token from stdin |
| `--token` |  |  | Deprecated: owner token in argv (lands in shell history) |

### `validate`

Validate the source manifest, agents, skills, and required contracts

### `waive`

Human waives one named requirement (risk:<task> or stage-exit:<stage>:<check>)

| Flag | Required | Default | Meaning |
|---|---|---|---|
| `--project` |  | `.` | Installed project root |
| `--run` |  |  | Run id; defaults to CURRENT.md |
| `--requirement` | yes |  |  |
| `--reason` | yes |  |  |
| `--level` (R0|R1|R2|R3|R4) |  |  | For risk waivers: the risk level to apply |
| `--by` | yes |  | Name of the responsible human (never an agent id) |
| `--token-file` |  |  | Read the owner token from this file (never pass it in argv) |
| `--token-stdin` |  |  | Read the owner token from stdin |
| `--token` |  |  | Deprecated: owner token in argv (lands in shell history) |
<!-- CLI-REFERENCE:END -->
