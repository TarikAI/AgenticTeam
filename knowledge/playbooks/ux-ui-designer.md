# Playbook — ux-ui-designer

Personal checklist. Read before every task. Cap ~40 lines. Rules: `README.md` in this directory.

## Before starting
- [ ] Read my agent definition, this playbook, and the active run documents named in my task brief.  <!-- status: baseline -->
- [ ] Enumerate areas, states, and depth before drawing any screen — the screen list is an output, not an input.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from design-architect -->
- [ ] Check preflight: design-architect installed (run its pipeline; hand off page map/component map/coverage) or absent (interface-closure floor).  <!-- status: baseline · learned: 2026-08-17 · source: seeded from design-architect -->

## While building
- [ ] Reuse the design system's components and tokens before inventing new ones; run a component census first.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from design-architect -->
- [ ] Read-only surfaces get no mutation controls; every mutation control names its server operation.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from design-architect -->
- [ ] Every metric shown declares its decision, source, freshness, and drill-down — or gets cut.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->
- [ ] Spec the empty state with guidance, the error state with a next step, loading with shape.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from design-architect -->

## Before claiming done
- [ ] Complete with typed evidence (`file:`, `cmd:<exec-id>`, `commit:`) through `complete`; record discovered work with `add-task`, deviations as a checkpoint.  <!-- status: baseline -->
- [ ] Hand off a page map, component map, and coverage summary.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from design-architect -->
- [ ] Closure audited in the rendered output: every affordance → destination pair recorded; dangling pairs are blockers.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from design-architect -->
