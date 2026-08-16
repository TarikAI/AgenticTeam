# Architecture and runtime

AgenticTeam separates probabilistic work from deterministic coordination.

## Four layers

1. **Harness execution:** the selected coding harness invokes models, tools, native subagents,
   worktrees, or sequential roles.
2. **Portable organization:** `team.json`, source agent contracts, presets, capabilities,
   access classifications, and conditional specialist triggers.
3. **Progressive project context:** a small router, `CURRENT.md`, numbered stage `CONTEXT.md`
   contracts, task packets, decisions, Fusion records, and product artifacts.
4. **State manager:** `.agentic-team/bin/agentic_team.py` atomically manages task/checkpoint/run
   state. It makes no model API calls and stores no credentials.

This split is deliberate: prompts decide and create; code protects lifecycle invariants.

## Installed layout

```text
.agentic-team/
  AGENTS.md                 compact stable router
  CURRENT.md                generated active-run pointer
  team.json                 installed manifest and roster
  install-manifest.json     compiler record
  bin/agentic_team.py       deterministic state manager
  config/policies.json      risk and autonomy policy
  protocols/                shared operating law
  knowledge/                project-owned lessons/playbooks
  templates/                stage, task, Fusion, report templates
  runs/<run-id>/
    state.json              atomic generated state; do not hand-edit
    00_intake/CONTEXT.md
    01_product/CONTEXT.md
    02_solution/CONTEXT.md
    03_readiness/CONTEXT.md
    04_build/CONTEXT.md
    04_build/tasks/
    05_verify/CONTEXT.md
    06_release/CONTEXT.md
    07_learn/CONTEXT.md
    _context/
    _decisions/
    _fusion/<council-id>/
```

Harness-native files live beside this bus (`.claude/agents`, `.codex/agents`, and so on).

## State invariants

- Only the CLI writes `state.json`; writes use a run lock, temporary file, and atomic replace.
- Dependencies control `pending` → `ready`.
- Claims include an agent, timestamp, lease, and owned paths.
- Concurrent claimed paths may not be equal or parent/child overlaps.
- Failed attempts follow profile retry limits; expired leases can be recovered explicitly.
- R3/R4 tasks always create human checkpoints; HITL also pauses for R2.
- Product/architecture/readiness gates follow the selected profile; release is always human.
- Builders cannot satisfy Fusion moderation/verification roles in the same council.

## Model/runtime boundary

AgenticTeam does not bundle a universal model scheduler. Native multi-agent harnesses perform real
delegation; Antigravity and Pi receive workflows/role contracts and can execute them sequentially
or through their available orchestration facilities. The same durable state enables a run to move
between harnesses without pretending every provider has identical APIs.

## Extending the roster

Add a concise source role under `agents/`, register its ID/file/department/tier/access/manager/
capabilities in `team.json`, add conditional `activate_when` triggers when appropriate, update a
preset only when the role should be installable there, and run validation/tests. Shared standing
orders belong in protocols, not copied into new prompts.
