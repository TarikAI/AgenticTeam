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
| `install <target> --harness H --preset P` | Compile a native package and durable bus. |

## Run commands (run against an installed project)

| Command | Required intent |
|---|---|
| `init-run` | Create numbered stages and atomic state with entry/context/autonomy choices. |
| `status [--json]` | Read current stage, task counts, checkpoints, rejections, failed tasks, and Fusion sessions. |
| `runs` / `switch-run --run R` / `close-run --reason` | List runs, point `CURRENT.md` at another run, or close one. Only `init-run` and `switch-run` move `CURRENT.md`. |
| `route-specialists` / `deactivate-specialist` | Match installed trigger rules and record bounded specialist participation. |
| `add-task` | Create a task envelope. The owner must be installed; the stage defaults to the current stage and may not be an earlier one; build tasks owned by a writing role need `--path` (or `--exclusive`). |
| `claim` | Atomically claim a ready task of the current stage. The claiming agent must be installed and be the task owner; the profile's `max_concurrent_agents` caps open claims; owned paths may not overlap. |
| `renew` | Extend the lease on a task you hold (1-480 minutes). |
| `reassign` | Change the owner of an unclaimed open task, with a reason. |
| `complete` | Attach evidence and unlock dependents. |
| `fail` | Record an attempt and apply retry policy. Under a profile that stops on failure (hitl), an exhausted task blocks the run (`blocked-failure`). |
| `recover-leases` | Return expired claims to policy-controlled state. |
| `checkpoint` / `approve` / `reject` / `resolve` | Create and decide a human checkpoint. A rejection blocks the run (`blocked-rejection`) until the human `resolve`s it after the correction. Approving another checkpoint never clears a rejection. |
| `advance` | Exit the current stage only when every task of the stage is closed (completed or cancelled), no checkpoint is pending, and policy gates pass. |
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
state; do not edit `state.json` manually.

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

## Checkpoint decisions require the owner token

`init-run` issues an owner token and writes it **outside the project**, under
`~/.agentic-team/owner-tokens/<run-id>.token` (override the folder with `AGENTIC_TEAM_HOME`).
`approve`, `reject`, `resolve`, `cancel`, human `reopen`, and a human-sponsored `fusion-close` require it:

```text
python .agentic-team/bin/agentic_team.py approve --project . --checkpoint CP-001 \
  --by "Your Name" --decision "approved after review" --token "$(cat ~/.agentic-team/owner-tokens/<run-id>.token)"
```

Two rules make the gate meaningful: `--by` may not name an installed agent, and an agent must
never be granted read access to the token path. Configure your harness permissions accordingly.
