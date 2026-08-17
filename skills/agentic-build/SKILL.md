---
name: agentic-build
description: Orchestrate a complete software or platform build with AgenticTeam, from idea or supplied plan through architecture, parallel implementation, integration, independent verification, release readiness, and learning. Use when the user asks the team to build, continue, resume, execute a plan, work autonomously, or work with human checkpoints.
---

# Agentic Build

Use the project router and deterministic state manager; do not simulate a team in one long
prompt. Read `references/operating-guide.md` before starting or resuming a run.

## Start or resume

1. If `.agentic-team/runs/` contains an active run, resume it unless the user clearly asks for
   a new one. Reconcile claimed tasks and read only the current stage context.
2. Otherwise classify entry as `idea`, `plan-given`, or `execute-only`. A supplied plan is
   authoritative; do not manufacture a replacement.
3. Select `autonomous`, `supervised`, or `hitl`. Default to the installed policy. Autonomy never
   bypasses hard human gates.
4. Use progressive context when explicitly requested, for large/regulated work, or when the
   cold walk test would otherwise fail.
5. Initialize the run through `scripts/agentic_team.py`; never hand-edit state JSON.

## Orchestrate

- Run `scripts/preflight_skills.py` at run start and record the capability report. Route
  admin/control-surface work through `adminwright`, UI system design through
  `design-architect`, and diff reviews through OCR delegation when preflight finds them;
  the floor protocols (`admin-surfaces.md`, `interface-closure.md`, `review-discipline.md`)
  apply either way. See `protocols/skill-acquisition.md`.
- Route work by capability and activate conditional specialists from `team.json` only with a
  concrete question and output.
- Create tasks with dependencies, acceptance checks, owned paths, risk, and evidence contract.
- Parallelize ready tasks with non-overlapping ownership. Claim them through the state manager.
- Keep product, interface, and data contracts stable. Record deviations as decisions.
- Use a build integrator for parallel writers and a different agent for independent verification.
- At checkpoints, present recommendation, alternatives, impact, evidence, and the smallest human
  response needed.

## Finish

Do not stop at code generation. Integrate, run applicable checks, repair within retry policy,
perform independent verification, prepare release/rollback evidence, and generate the final
report. A production deployment or public action always waits for explicit human approval.
