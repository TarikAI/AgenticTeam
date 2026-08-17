# Specialist routing

Specialists are conditional lenses, not permanent ceremony. The orchestrator scans the
request, PRD, architecture, data classification, operational target, and current risks
against each `activate_when` entry in `team.json`.

Activate a specialist when a trigger is present, a relevant acceptance criterion exists, or
the cost of missing the specialty is materially higher than one bounded review. Record the
reason and task envelope. Deactivate after the output is accepted.

Required examples:

- Personal/sensitive data: privacy engineer and security engineer.
- User-facing interface: accessibility specialist; localization specialist when multilingual/RTL.
- Existing system or migration: system mapper before architecture changes.
- Production/availability target: SRE and release manager.
- High traffic or latency target: performance engineer.
- Admin/moderation/operations: platform admin engineer — through the `adminwright` skill
  when installed; `protocols/admin-surfaces.md` is the floor either way.
- UI system design or redesign: ux-ui-designer with the `design-architect` skill when
  installed; `protocols/interface-closure.md` is the floor either way.
- Any diff, PR, or pre-release review: code-reviewer using OCR delegation when the `ocr`
  CLI is installed; `protocols/review-discipline.md` is the floor either way.
- Regulated claim: compliance advisor, explicitly advisory and not legal counsel.
- Fusion request: fusion moderator plus at least two domain-diverse contributors.
- Progressive-context/BMAD request: context engineer.

Do not invoke every specialist by default. A review without a concrete question, input, output,
and acceptance test produces noise rather than safety.
