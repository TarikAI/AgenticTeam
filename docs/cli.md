# Runtime CLI reference

The installed command is:

```text
python .agentic-team/bin/agentic_team.py <command> --project .
```

The harness orchestrator normally invokes it. Humans can use it to inspect or recover a run.

## Source/compiler commands

| Command | Purpose |
|---|---|
| `validate` | Check manifest, role files, presets, workflows, skills, and required contracts. |
| `list agents|presets|harnesses` | Inspect installable capabilities. |
| `install <target> --harness H --preset P` | Compile a native package and durable bus. |

## Run commands

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
