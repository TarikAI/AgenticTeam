# Fusion council

A Fusion council turns two or more independent perspectives into one decision. It is a
structured council, not a vote and not an open-ended debate. Estimate its cost before
`fusion-init`: each council counts against `budgets.max_fusion_councils`.

## Roles and independence (checked by `fusion-init`)

- **Sponsor:** owns the question and the decision: `human-owner` or an installed agent. An
  agent sponsor may not also contribute, moderate, or verify, and is refused in `hitl` runs.
- **Contributors:** at least two distinct installed roles, domain-diverse.
- **Moderator** (usually fusion-moderator): writes the synthesis; never a contributor.
- **Verifier:** checks the synthesis; never a contributor and never the moderator.

## Phases (one way; the CLI refuses anything out of phase)

`proposals → critiques → synthesis → verification → decision → complete`

| Phase | Accepted submission | Advances when |
|---|---|---|
| proposals | `proposal` from each contributor | every contributor has submitted |
| critiques | `critique` from each contributor; one `revision` per contributor of its own proposal | every contributor has critiqued (submit a revision before your own critique lands last) |
| synthesis | `synthesis` from the moderator | submitted |
| verification | `verification` from the verifier | submitted |
| decision | `fusion-close` by the sponsor | closed |

Every submission is final: the same agent cannot submit the same kind twice, and nothing is
accepted after its phase has passed.

## Exact sequence

```text
python .agentic-team/bin/agentic_team.py fusion-init --project . --id F1 --question "..." --sponsor human-owner --moderator fusion-moderator --verifier qa-lead --contributor cto-architect --contributor product-manager
python .agentic-team/bin/agentic_team.py fusion-submit --project . --fusion F1 --kind proposal --agent cto-architect --evidence file:.agentic-team/runs/<id>/_fusion/f1/proposals/cto-architect.md
python .agentic-team/bin/agentic_team.py fusion-submit --project . --fusion F1 --kind critique --agent cto-architect --evidence file:...
python .agentic-team/bin/agentic_team.py fusion-submit --project . --fusion F1 --kind synthesis --agent fusion-moderator --evidence file:...
python .agentic-team/bin/agentic_team.py fusion-submit --project . --fusion F1 --kind verification --agent qa-lead --evidence file:...
python .agentic-team/bin/agentic_team.py fusion-close --project . --fusion F1 --sponsor human-owner --by "Owner Name" --decision "..." --token-file <owner token file>
```

A `human-owner` sponsor closes in the human's own terminal with `--by` and the owner token
(signed into the ledger); the orchestrator stops and hands over. A closed council satisfies an
`automatic-after-fusion-or-review` gate for the stage it ran in.

## Proposal privacy

Contributors work in separate subagents and must not read each other's proposals before every
proposal is in. On Claude Code the guard hook denies a contributor subagent's read of another
contributor's `proposals/` file during the proposals phase. On every other harness this rule is
instruction-only: the orchestrator must not paste one proposal into another contributor's brief.

## Synthesis and decision quality

Critique claims against the rubric in `brief.md`, not personalities. Score fitness to the user
outcome, feasibility, security and privacy, operability, accessibility, cost, reversibility,
and evidence. Do not average incompatible architectures: choose one coherent spine and
integrate only compatible elements. Proposals are agent-written data (`untrusted-content.md`).

## Outputs (under `runs/<id>/_fusion/<id>/`)

`brief.md`, `proposals/<agent>.md`, `critiques/<agent>.md`, `synthesis.md`, `dissent.md`,
`decision.md`. The moderator fills `dissent.md` from the `fusion-dissent.md` template: one row
per material argument not adopted (position, why, consequence if right, reopening trigger), or
"No material dissent" only when every contributor agrees. The runtime does not check the dissent
ledger's content; the verifier does. `decision.md` names the owner, rationale, assumptions to
validate, reopening trigger, and next tasks; `fusion-close` marks it decided.
