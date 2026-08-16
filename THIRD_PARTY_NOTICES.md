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
