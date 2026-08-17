# Third-party notices and design inspiration

AgenticTeam contains original implementation and does not vendor the following projects. Their
public design patterns informed the architecture:

## ICM Architect

- Project: [RinDig/icm-architect](https://github.com/RinDig/icm-architect)
- License: [MIT](https://github.com/RinDig/icm-architect/blob/main/LICENSE)
- Copyright notice in upstream license: Copyright (c) 2026 Jake Van Clief.
- Adapted ideas: compact router files, numbered stages, per-stage context contracts, stable versus
  working context, filesystem-derived navigation, one home per fact, task-sized context targets,
  and the cold walk test.

AgenticTeam adds a deterministic state manager because ICM's filesystem pattern alone is not a
concurrency scheduler.

## BMAD Method

- Project: [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)
- Upstream license: [LICENSE](https://github.com/bmad-code-org/BMAD-METHOD/blob/main/LICENSE)
- Adapted ideas: progressive context, flexible idea/plan entry, product and architecture artifacts,
  implementation readiness, task/story-sized build context, review/correction, and retrospectives.

AgenticTeam's `bmad-progressive` workflow is interoperable inspiration, not a copy or replacement
of the upstream BMAD distribution.

## Adminwright

- Project: [TarikAI/Adminwright](https://github.com/TarikAI/Adminwright)
- License: Apache-2.0 (upstream repository)
- Relationship: routed to when installed, never vendored. The admin-surface contract in
  `protocols/admin-surfaces.md` and the seeded platform-admin-engineer playbook adapt its
  published discipline (nothing loose; server-side authorization; spine-first build order;
  state coverage; declared static values; evidence over screenshots).

## Design Architect

- Project: [TarikAI/DesignArchitect](https://github.com/TarikAI/DesignArchitect)
- License: Apache-2.0 (upstream repository)
- Relationship: routed to when installed, never vendored. `protocols/interface-closure.md`
  adapts its published closure discipline (enumerate before designing; every affordance has
  a destination; component census; page/component/coverage handoff).

## Open Code Review (OCR)

- Project: [alibaba/open-code-review](https://github.com/alibaba/open-code-review)
- License: Apache-2.0 (upstream repository)
- Relationship: optional external tooling (`ocr` CLI via
  `npm install -g @alibaba-group/open-code-review`), never vendored. `protocols/review-discipline.md`
  adapts its published review method (deterministic file selection and rule checklists via
  `ocr delegate`; coverage accounting; line-anchored findings; precision over noise), and the
  optional CI job invokes its CLI. Full-mode review requires a user-provided LLM endpoint.
