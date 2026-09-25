# Progressive context

AgenticTeam adapts ICM's compact router and stage contracts and BMAD's progressive planning.
The goal: any agent finds its stage, task, next action, and output with a handful of reads.

## Three layers

1. **Router** (`.agentic-team/AGENTS.md`, imported or inlined by the harness): short and stable.
   It points; it does not teach the whole system.
2. **`CURRENT.md`**: names the active run and stage. Only `init-run` and `switch-run` move it.
3. **Stage `CONTEXT.md`** (`runs/<id>/<stage>/CONTEXT.md`): Inputs, Process, Outputs, Human
   check, and Exit criteria. The CLI regenerates its `Status:` line on every transition and
   renders the exit criteria from the same policy rows `advance` checks; agents edit the other
   sections, and the stage owner keeps them current.

Each fact has one home; other documents link to it. Stable knowledge lives in
`.agentic-team/knowledge/`, not in run artifacts. Agents never hand-edit generated state.

## Load rule

Read the router, `CURRENT.md`, and the current stage `CONTEXT.md`; then at most two more
documents before acting, unless the contract names more. For a task, use its packet:

```text
python .agentic-team/bin/agentic_team.py pack --project . --task T-014
```

`pack` writes `runs/<id>/_context/<task>.md` within `context_target_tokens` (2K-8K): the
envelope, named inputs, the stage contract excerpt, the role's playbook checks, and the exact
claim/exec/complete commands. It lists what it truncated or omitted; read an omitted source only
if the task actually needs it. If a task truly needs more, the context-engineer writes a narrow
summary that links to evidence and records what it left out.

## Context methods (`init-run --context`)

The two methods differ in their exit contracts (`config/policies.json` → `stage_exits`, table in
`workflow.md`):

- **`bmad-progressive`:** every stage has its own artifact: `BRIEF.md` + `ASSUMPTIONS.md`,
  `PRD.md` with `AC-` ids, `ARCHITECTURE.md`, `READINESS.md` tracing every `AC-` id,
  `VERIFICATION.md`, `RELEASE.md`, `RETROSPECTIVE.md` + `DELIVERY-REPORT.md`. Use it for large,
  regulated, or multi-team work, or when asked.
- **`adaptive`:** 00-03 collapse into one `BRIEF.md` carrying the `AC-` ids and the task list;
  05_verify still needs the verdict lines, 06_release still needs the human release checkpoint,
  and 07_learn needs `DELIVERY-REPORT.md`. Use it for small, well-specified work.

Entry modes (`idea`, `plan-given`, `execute-only`) are orthogonal: `plan-modes.md`.

## Cold walk test

Run it after setting up a run and before raising concurrency:

1. Start a fresh subagent that is given only the router (no chat history, no packet).
2. Ask it to state: the current stage, its next task, the next action (exact command), the
   required output, and any pending checkpoint.
3. Run `status --json` and compare.
4. Pass: all five answers match state within two reads beyond the router. Fail: fix the router
   pointer or the stage `CONTEXT.md` (not the subagent's prompt) and rerun.

Record the result as `cmd:` or `note:` evidence on the setup task.
