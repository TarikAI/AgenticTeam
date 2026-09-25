---
name: fusion-council
description: Run an AgenticTeam Fusion council - two or more contributors write sealed independent proposals, cross-critique on explicit assignments, revise once, then a moderator synthesizes one coherent plan with dissent preserved, an independent verifier checks it, and the sponsor records the decision through the CLI. Use when the user asks for fusion mode, council mode, a debate, multiple independent opinions, red-team planning, or a multi-specialist decision on architecture, risk, or product direction. Not for routine task review (use agentic-verify).
compatibility: Needs an AgenticTeam installation in the project (the bus at .agentic-team/, CLI at .agentic-team/bin/agentic_team.py), Python 3.10+, and a harness that can start isolated subagents. A human-owner sponsor closes the council in their own terminal with the owner token.
---

# Fusion Council

Runbook for the orchestrator. The protocol (roles, sequence, decision quality) is
`.agentic-team/protocols/fusion.md`; file contents per artifact: `references/council-artifacts.md`.
Every command below takes `--project .`; exit codes: 0 ok, 1 error (a submission out of phase or
twice is refused), 2 human gate, 3 blocked (e.g. `max_fusion_councils` budget), 64 usage.

## 1. Create the council

Pick at least two contributors with different specialties, a moderator (usually
`fusion-moderator`), and a verifier; the three sets must not overlap and moderator ≠ verifier.
The sponsor is `human-owner` or an installed agent that takes no other part; a `hitl` run needs
`human-owner`.

```text
python .agentic-team/bin/agentic_team.py fusion-init --project . --id F-ARCH --question "Which persistence model for orders?" --sponsor human-owner --moderator fusion-moderator --verifier code-reviewer --contributor backend-lead --contributor database-engineer --contributor security-engineer
```

It creates `<run>/_fusion/F-ARCH/` with `brief.md`, `proposals/<agent>.md`, `critiques/<agent>.md`,
`synthesis.md`, `dissent.md`, `decision.md`. The moderator completes `brief.md` (facts, unknowns,
constraints, rubric) and freezes it before any proposal starts.

## 2. Proposals (sealed)

Start one isolated subagent per contributor. Give it only `brief.md` and the path of its own
`proposals/<agent>.md`. It must not open any other file under `proposals/` until the phase is
`critiques` (on Claude Code the guard hook hides them; on other harnesses this is instruction
only, so do not paste one proposal into another's prompt). Each contributor, when done:

```text
python .agentic-team/bin/agentic_team.py fusion-submit --project . --fusion F-ARCH --kind proposal --agent backend-lead --evidence file:.agentic-team/runs/<run-id>/_fusion/F-ARCH/proposals/backend-lead.md
```

The phase moves to `critiques` when the last contributor submits. Submissions are final.

## 3. Critiques and one revision

The moderator writes explicit assignments into `brief.md` (who critiques which proposal, every
proposal critiqued at least once, against the frozen rubric). Each contributor writes its
`critiques/<agent>.md` and may submit one `revision` of its own proposal. Revisions must be
submitted before the last critique, because the last critique closes the phase:

```text
python .agentic-team/bin/agentic_team.py fusion-submit --project . --fusion F-ARCH --kind revision --agent database-engineer --evidence "revised section 2 after security-engineer's critique"
python .agentic-team/bin/agentic_team.py fusion-submit --project . --fusion F-ARCH --kind critique --agent database-engineer --evidence file:.agentic-team/runs/<run-id>/_fusion/F-ARCH/critiques/database-engineer.md
```

## 4. Synthesis, dissent, verification

The moderator writes `synthesis.md` (one coherent spine; incompatible foundations are not
averaged) and fills `dissent.md` with the columns of `.agentic-team/templates/fusion-dissent.md`,
then submits. A fresh verifier subagent checks traceability, evidence, and dissent, then submits:

```text
python .agentic-team/bin/agentic_team.py fusion-submit --project . --fusion F-ARCH --kind synthesis --agent fusion-moderator --evidence file:.agentic-team/runs/<run-id>/_fusion/F-ARCH/synthesis.md
python .agentic-team/bin/agentic_team.py fusion-submit --project . --fusion F-ARCH --kind verification --agent code-reviewer --evidence "verified: every rubric item traced; dissent complete"
```

A verification that finds a gap is a finding, not a pass: raise a checkpoint and stop.

## 5. Decision

- **Agent sponsor** (not allowed in `hitl`):

  ```text
  python .agentic-team/bin/agentic_team.py fusion-close --project . --fusion F-ARCH --sponsor cto-architect --decision "Adopt synthesis v1; reopen if write volume exceeds 5k/s"
  ```

- **`human-owner` sponsor:** stop. Show the human the synthesis, dissent, and verification, and
  hand over the line they run in their own terminal:

  ```powershell
  python .agentic-team/bin/agentic_team.py fusion-close --project . --fusion F-ARCH --sponsor human-owner --decision "..." --by "Your Name" --token-file "$HOME\.agentic-team\owner-tokens\<run-id>.<uid>.token"
  ```

  ```bash
  python3 .agentic-team/bin/agentic_team.py fusion-close --project . --fusion F-ARCH --sponsor human-owner --decision "..." --by "Your Name" --token-file ~/.agentic-team/owner-tokens/<run-id>.<uid>.token
  ```

`fusion-close` appends the recorded decision to `decision.md`. A council closed in a stage
satisfies an `automatic-after-fusion-or-review` gate for that stage. Turn the decision's next
tasks into `add-task` entries.

## Stop conditions

- a contributor saw another proposal before `critiques`: record it in `dissent.md` and tell the
  human; do not silently continue;
- exit 2 or 3; a human-owner sponsor; the verifier reports a gap;
- a vote count is offered in place of evidence.
