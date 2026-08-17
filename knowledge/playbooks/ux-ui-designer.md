# Playbook — ux-ui-designer

Personal checklist. Read before every task. Cap ~40 lines. Rules: `README.md` in this directory.

## Before starting
- [ ] Read my agent definition, this playbook, and the active run documents named in my task brief.
- [ ] Enumerate areas, states, and depth before drawing any screen — the screen list is an output, not an input. <!-- learned: 2026-08-17 · cost: seeded from design-architect -->
- [ ] Check preflight: design-architect installed (run its pipeline; hand off page map/component map/coverage) or absent (interface-closure floor). <!-- learned: 2026-08-17 · cost: seeded from design-architect -->

## While building
- [ ] Reuse the design system's components and tokens before inventing new ones; run a component census first. <!-- learned: 2026-08-17 · cost: seeded from design-architect -->
- [ ] Read-only surfaces get no mutation controls; every mutation control names its server operation. <!-- learned: 2026-08-17 · cost: seeded from design-architect -->
- [ ] Every metric shown declares its decision, source, freshness, and drill-down — or gets cut. <!-- learned: 2026-08-17 · cost: seeded from adminwright -->
- [ ] Spec the empty state with guidance, the error state with a next step, loading with shape. <!-- learned: 2026-08-17 · cost: seeded from design-architect -->

## Before claiming done
- [ ] Evidence attached (test output / verification notes), deviations and discovered work in STATUS.md.
- [ ] Hand off a page map, component map, and coverage summary. <!-- learned: 2026-08-17 · cost: seeded from design-architect -->
- [ ] Closure audited in the rendered output: every affordance → destination pair recorded; dangling pairs are blockers. <!-- learned: 2026-08-17 · cost: seeded from design-architect -->
