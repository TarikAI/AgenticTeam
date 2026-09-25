---
name: bmad-progressive
description: Run an AgenticTeam build under the bmad-progressive context profile - compact stage CONTEXT.md contracts, BRIEF/PRD/ARCHITECTURE/READINESS artifacts as exit requirements, 2K-8K token task packets built by the CLI, and a cold walk test that proves a fresh agent can find its way from the router alone. Use when the user asks for BMAD, progressive context, full planning, or when a large, regulated, or long-running project needs staged context control. Not for small, well-specified changes (the adaptive profile is enough).
compatibility: Needs an AgenticTeam installation in the project (the bus at .agentic-team/, CLI at .agentic-team/bin/agentic_team.py), Python 3.10+, and a harness that can start a fresh subagent for the cold walk test. The run must be initialised with --context bmad-progressive.
---

# BMAD Progressive Context

An interoperable workflow inspired by BMAD patterns, not a bundled copy of BMAD. The load rule,
stages, and entry modes are in `.agentic-team/protocols/progressive-context.md`; exit contracts
in `.agentic-team/protocols/workflow.md`; the adaptive vs bmad-progressive table in
`references/stage-contracts.md`. Drive the stages with the agentic-build runbook; this skill adds
the context discipline. Exit codes: 0 ok, 1 error, 2 human gate → stop and present, 3 blocked →
stop and show the human's command, 64 usage.

## 1. Start

The human runs `init-run` (agentic-build step 2) with `--context bmad-progressive`. Confirm:

```text
python .agentic-team/bin/agentic_team.py status --project . --brief
```

`Context: bmad-progressive` must appear; otherwise stop and tell the human the run uses a
different profile (a new run is their decision). Entry `idea` starts at `00_intake`,
`plan-given` at `03_readiness`, `execute-only` at `04_build`; human-supplied artifacts stay
authoritative; never write a competing PRD.

## 2. Who edits which CONTEXT.md section

| Section | Written by | Rule |
|---|---|---|
| Header (Run, Stage, `Status:`) | CLI (`init-run`, refreshed by `advance`) | never edit |
| Purpose, Process, Outputs, Human check, Exit criteria | CLI from policy at `init-run` | never edit; editing does not change the gate |
| Working inputs | stage artifact owner (context-engineer when active) | current-run files this stage may change, with paths |
| Stable references | context-engineer, else the stage owner | authoritative sources with owner and freshness date |
| Next load | stage owner, before `advance` | the smallest set of inputs the next stage needs; links, not copies |

## 3. Task packets

Give each task its inputs with sections (`--input <project-relative path>#<section>`), then:

```text
python .agentic-team/bin/agentic_team.py pack --project . --task T-API-1
```

The packet lands in `<run>/_context/<task>.md` within `context_target_tokens` (2K–8K) and lists
what was truncated or omitted. If an omitted input is load-bearing (safety, data, contract, open
decision), the context-engineer writes a narrow attributable summary file, the task's `--input`
points at it, and `pack` runs again. `brief --task T` builds the same packet and prints the
delegation message.

## 4. Cold walk test

Run after every `advance` and before raising concurrency:

1. Start a fresh subagent with no conversation history. Give it only the project router (the
   AgenticTeam block in `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`) and allow at most two further
   reads.
2. Ask it for five answers: current stage, the task to do next, the next action, the required
   output (path), and the checkpoint that applies.
3. Compare with the CLI:

   ```text
   python .agentic-team/bin/agentic_team.py status --project . --json
   python .agentic-team/bin/agentic_team.py next --project . --json
   ```

   stage = `stage`; task ∈ `next`; action consistent with that task's envelope; output = the
   stage's Outputs / exit requirement; checkpoint = pending `checkpoints` or the stage's Human
   check.
4. Pass if all five match. On a miss, repair Working inputs / Next load (or the task's
   `--input`) and rerun; two consecutive misses → stop and raise a `deviation` checkpoint.

## 5. Advance

```text
python .agentic-team/bin/agentic_team.py advance --project .
```

Under bmad-progressive, exit 1 names the missing artifact (scaffold it with
`scaffold --artifact NAME`), unfilled `{{...}}` or to-do markers, or untraced `AC-` ids in
READINESS.md. Fix them in this stage; never `advance` around them.
