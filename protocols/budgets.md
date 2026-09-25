# Budgets

A run spends tasks, councils, time, tokens, and money. The human sets the ceilings; the CLI
counts and stops; agents report what they used.

## Where budgets live

`config/policies.json → budgets` (defaults) and the project-owned
`.agentic-team/config/policies.local.json → budgets` (may only lower a ceiling or set one that
was unset):

| Key | Meaning | Checked at | Default |
|---|---|---|---|
| `max_tasks` | tasks in the run | `add-task` | 400 |
| `max_fusion_councils` | Fusion councils in the run | `fusion-init` | 12 |
| `max_lease_minutes` | longest lease one `renew --lease-minutes` may set | `renew` | 480 |
| `tokens` | total tokens reported via `complete --usage` | `complete` | unset (not checked) |
| `usd` | total USD reported via `complete --usage` | `complete` | unset (not checked) |
| `warn_at` | fraction of a ceiling that opens the checkpoint | all of the above | 0.8 |

Set a token or money ceiling before the run starts, for example
`{"budgets": {"tokens": 3000000, "usd": 40}}` in `policies.local.json`.

## What the runtime does

- At `warn_at` (80 % by default) of `max_tasks`, `max_fusion_councils`, `tokens`, or `usd`, the
  CLI opens one `budget` checkpoint per metric. Like any pending checkpoint it blocks `advance`
  until the human approves (continue) or rejects (stop and re-plan).
- A command that would take a metric past its ceiling is refused with exit 3 (blocked). For
  `complete`, the completion is refused and the task stays claimed.
- Only the human lifts a ceiling for the rest of the run:
  `agentic_team.py waive --requirement budget:<metric> --reason "<why>" --by <name> --token-file <path>`
  (`<metric>` is the key, e.g. `budget:usd`).
- `status --brief` and `metrics` show the running usage totals.

## What agents do (instruction)

- Report usage on every completion, from the harness's own usage or cost report:
  `complete --task <id> --agent <role> --evidence <...> --usage tokens=48000,usd=0.62`.
  The runtime does not meter models; unreported usage is invisible to the ceiling.
- Stop at a budget refusal (exit 3). Do not split, rename, or re-add tasks to get under a cap,
  and do not under-report usage; either is a deviation.
- When a `budget` checkpoint is pending, finish claimed work but claim nothing new that the
  checkpoint would decide.

## Before a Fusion council

Estimate its cost before `fusion-init` and put it in the council brief:

- tokens ≈ contributors × (proposal + critique + one revision) + moderator synthesis +
  verifier pass, each at the tokens a comparable task used in this run (`metrics` usage per task)
  or a stated guess;
- USD = tokens × the price of the model tier each role runs at.

If the estimate would pass `warn_at` of the `tokens` or `usd` ceiling, raise
`checkpoint --kind budget` with the estimate as `--impact` before starting.

## The main cost lever: model profiles

Model choice dominates spend. `install --model-profile` maps each role's tier (deep, standard,
fast) to models: `economy`, `balanced` (default), `max-quality`, or `inherit` (see
`docs/harnesses.md`). Reinstall with `economy` for exploratory or low-risk runs; keep deep-tier
roles for architecture, verification, and release decisions. Fewer activated specialists and
fewer councils are the next levers.

## Reporting

- DELIVERY-REPORT.md, section "Cost and learning", states actual spend against each ceiling
  (tasks, councils, tokens, USD), budget checkpoints and waivers, and the model profile used,
  taken from `metrics --json`, not from memory.
- A metric with no reported usage is written as "not reported", never as zero.
