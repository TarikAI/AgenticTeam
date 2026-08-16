# Owner guide — no coding required

You are the product owner. Your job is to describe the result, correct misunderstandings early,
and approve consequential actions. The team handles technical execution and must show evidence.

## Install once

Choose a project folder and a harness. On Windows, from this repository:

```powershell
.\scripts\install.ps1 -Target "C:\Users\YOU\Documents\my-platform" -Harness claude-code -Preset full-platform
```

`full-platform` installs the whole delivery organization. Specialists do not all speak at once;
the orchestrator activates them when the product triggers their expertise.

## Start

Open the project in your harness and say:

> Use `agentic-build`. Build my complete platform in autonomous mode with BMAD progressive
> context. My idea is: [describe users, problem, desired result, must-haves, constraints].

If you already have a plan, say:

> Use my plan as the source of truth. Entry mode is plan-given. Do not re-plan; validate what is
> necessary, then build, verify, and prepare the release.

## What you will see

`.agentic-team/CURRENT.md` points to the active run and stage. Each numbered stage has a readable
`CONTEXT.md`, and the final work includes requirement/product/architecture/build/verification/
release/learning evidence as applicable. The generated `state.json` is the task machine; you do
not need to edit it.

## Decisions that always come back to you

- putting a product into production;
- publishing publicly or messaging real people;
- spending money or creating paid resources;
- using real credentials or payment methods;
- destructive or irreversible operations;
- legal or contractual commitments.

Ask for the recommendation, alternatives, evidence, rollback, and consequence of waiting. The
checkpoint must contain those facts.

## Useful instructions

- “Give me evidence-backed status: complete, unfinished, blocked, at risk, and decisions needed.”
- “Run Fusion mode with product, architecture, UX, security, and cost perspectives.”
- “Show the integrated product and reproduce the critical tests.”
- “Do not publish or deploy; prepare everything up to the approval gate.”
- “Use execute-only mode; my supplied plan is authoritative.”
- “Run independent verification. The builder cannot be the sole reviewer.”

If the team loops or becomes vague, ask it to read `CURRENT.md`, run the status/doctor commands,
recover expired leases, and report the exact blocking state.
