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
| `status [--json]` | Read current stage, task counts, checkpoints, and Fusion sessions. |
| `route-specialists` / `deactivate-specialist` | Match installed trigger rules and record bounded specialist participation. |
| `add-task` | Create a task envelope with owner, risk, dependencies, paths, acceptance, evidence. |
| `claim` | Atomically claim a ready non-overlapping task with a lease. |
| `complete` | Attach evidence and unlock dependents. |
| `fail` | Record an attempt and apply retry/blocking policy. |
| `recover-leases` | Return expired claims to policy-controlled state. |
| `checkpoint` / `approve` / `reject` | Create and explicitly resolve a human decision. Rejection blocks correction work. |
| `advance` | Exit the current stage only after tasks and policy gates pass. |
| `fusion-init` | Create private proposal/critique/synthesis/dissent/decision artifacts. |
| `fusion-submit` | Record proposals, critiques, synthesis, and verification in order. |
| `fusion-close` | Record the sponsor's decision after independent verification. |
| `learn` | Record an evidence-scoped, non-promoted learning candidate. |
| `report` | Generate an evidence-indexed delivery report. |
| `doctor` | Diagnose installation and active-run consistency. |

Use `--help` on any command for exact flags. All mutations take a run lock and atomically replace
state; do not edit `state.json` manually.

## Recovery commands

| Command | Use when |
|---|---|
| `unlock [--force]` | A command was killed mid-run and left `.state.lock` behind. Without `--force` a lock younger than 30s is kept, in case a command really is running. |
| `reopen --task T --reason R` | A task exhausted its retries or wedged; return it to the queue so the stage can finish. |
| `cancel --task T --reason R` | The human descoped the work; stop it holding the stage gate closed. |

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Command succeeded. |
| `1` | Command failed (see stderr). |
| `2` | `advance` stopped at a human gate. Scripts using `advance && next-step` therefore stop too, instead of walking through the gate. |

## Checkpoint decisions require the owner token

`init-run` issues an owner token and writes it **outside the project**, under
`~/.agentic-team/owner-tokens/<run-id>.token`. `approve` and `reject` require it:

```text
python .agentic-team/bin/agentic_team.py approve --project . --checkpoint CP-001 \
  --by "Your Name" --decision "approved after review" --token "$(cat ~/.agentic-team/owner-tokens/<run-id>.token)"
```

Two rules make the gate meaningful: `--by` may not name an installed agent, and an agent must
never be granted read access to the token path. Configure your harness permissions accordingly.
