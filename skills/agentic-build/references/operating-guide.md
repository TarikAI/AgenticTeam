# Operating guide

Lookup tables for the agentic-build runbook. Exit contracts come from `config/policies.json →
stage_exits` and are printed in each stage's `CONTEXT.md` under **Exit criteria**; the protocol
is `.agentic-team/protocols/workflow.md`.

## Stage artifacts

`scaffold --artifact NAME` creates the file in `<run>/` from `.agentic-team/templates/`. Items
marked (bmad) are exit requirements only under `--context bmad-progressive`; under `adaptive`
they are optional.

| Stage | Artifact | Owner (fallback) | Exit requirement |
|---|---|---|---|
| 00_intake | BRIEF.md | ceo (fullstack-engineer) | exists, no `{{...}}`/TODO; adaptive: contains `AC-` ids |
| 00_intake | ASSUMPTIONS.md | ceo | (bmad) exists |
| 01_product | PRD.md | product-manager (ceo) | (bmad) contains `AC-` ids |
| 02_solution | ARCHITECTURE.md, `_decisions/ADR-NNN.md` (hand-written; ADR from `adr.md`) | cto-architect (fullstack-engineer) | (bmad) ARCHITECTURE.md exists |
| 03_readiness | READINESS.md | delivery-lead (ceo) | (bmad) exists and traces every `AC-` id |
| 04_build | code and tests | owners of build tasks | every completed write task has `file:`/`cmd:`/`commit:` evidence |
| 05_verify | VERIFICATION.md | qa-lead (code-reviewer) | `Verdict:` / `Verifier:` / `Verified-SHA:` header; see agentic-verify |
| 06_release | RELEASE.md | release-manager (devops-engineer) | (bmad) exists; human release checkpoint, except `unattended` with no task above R1: exits on the executable conditions of `protocols/autonomy.md` (RELEASE.md complete under every context, rehearsed rollback) |
| 07_learn | RETROSPECTIVE.md, DELIVERY-REPORT.md | delivery-lead; ceo | DELIVERY-REPORT.md exists (both under bmad) |

Every stage also needs: all its tasks closed, no pending checkpoint, activated specialists
finished or deactivated, and its policy gate passed.

## add-task flags

| Flag | Use |
|---|---|
| `--id`, `--title`, `--owner` | required; owner must be installed |
| `--stage` | defaults to the current stage; never an earlier one |
| `--action`, `--target` | what and where (`risk.actions` in `config/policies.json`; target local, ci, staging, production, external); the runtime derives the risk |
| `--risk` | a requested floor only |
| `--path` (repeatable) or `--exclusive` | owned paths; required for 04_build tasks of writing roles |
| `--depends-on` (repeatable) | task ids that must complete first |
| `--input` (repeatable) | project-relative file, optionally `#section`; `pack` inlines it |
| `--acceptance`, `--evidence-contract` (repeatable) | the done criteria and expected evidence |
| `--check` (repeatable) | acceptance command; must pass through `exec` (`complete --run-checks`) |
| `--verifies` (repeatable) | marks a verification task; builders of the named tasks cannot claim it |

## Evidence types

`file:<project-relative path>` (hashed), `cmd:<exec-id>` (from `exec`), `commit:<sha>`,
`url:<url>`, `note:<text>`. A note never suffices for a write task.
