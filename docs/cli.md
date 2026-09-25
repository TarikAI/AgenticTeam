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
| `add-task` | Create a task envelope. The owner must be installed; the stage defaults to the current stage and may not be an earlier one; build tasks owned by a writing role need `--path` (or `--exclusive`). `--check CMD` adds an acceptance command; `--verifies T` marks a verification task whose claimant may not have built T. |
| `claim` | Atomically claim a ready task of the current stage. The claiming agent must be installed and be the task owner; the profile's `max_concurrent_agents` caps open claims; owned paths may not overlap. |
| `renew` | Extend the lease on a task you hold (1-480 minutes). |
| `reassign` | Change the owner of an unclaimed open task, with a reason. |
| `complete [--run-checks] [--usage tokens=N,usd=N]` | Attach typed evidence (`file:`, `cmd:`, `commit:`, `url:`, `note:`) and unlock dependents. Write tasks need at least one `file:`/`cmd:`/`commit:`; `--check` commands must have passed. |
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
and optional `tokens`/`usd` fed by `complete --usage`) open a `budget` checkpoint at `warn_at`
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
