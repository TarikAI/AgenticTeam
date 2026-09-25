# Specialist routing

Specialists are conditional lenses, not permanent ceremony. Each installed role's
`activate_when` list in `.agentic-team/team.json` is a controlled signal vocabulary
(`personal-data`, `gdpr`, `checkout`, `uptime`, `slo`, `web-ui`, `i18n`, `right-to-left`,
`chatbot`, `admin-console`, ...).

## Matching (what the runtime does)

```text
python .agentic-team/bin/agentic_team.py route-specialists --project . --signal "personal-data" --signal "checkout refunds"
```

`route-specialists` compares each signal against every trigger by whole words and phrases,
treating hyphens, underscores, and spaces alike: `personal data` matches `personal-data`, but
`React children` does not match `child-data` and `city council` does not match `council-mode`.
There is no substring or synonym matching, so pass signals in the vocabulary's own terms: the
orchestrator reads the request, PRD, architecture, data classification, operational targets, and
open risks, and translates them into those terms.

Every match is recorded (`specialist-activated` event, `active_specialists` in state) with the
matched triggers and the stage.

## Closing an activation (checked by `advance`)

An activated specialist blocks the stage exit until either:

- a task owned by that specialist is `completed`, with a concrete question, input, output, and
  acceptance test in its envelope; or
- the orchestrator records why it is not needed:
  `deactivate-specialist --agent <id> --reason "<why>"`.

Do not activate every specialist by default; an unscoped review produces noise, not safety.

## Judgment on top of matching

Add a specialist without a trigger match when an acceptance criterion needs it or missing the
specialty costs more than one bounded review; route it with the matching signal so the
activation is recorded. Typical pairings:

- Personal or sensitive data: privacy-engineer with security-engineer.
- User-facing interface: accessibility-specialist; localization-specialist when multilingual
  or right-to-left.
- Existing system or migration: system-mapper before architecture changes.
- Uptime or SLO target: sre-engineer and release-manager.
- Latency or throughput target: performance-engineer.
- Admin or ops console: platform-admin-engineer, through the `adminwright` skill when present;
  `admin-surfaces.md` is the floor either way.
- User-generated content: trust-and-safety-specialist designs policy; platform-admin-engineer
  builds the tooling.
- Payments, refunds, payouts: fraud-risk-analyst with security-engineer.
- LLM, retrieval, or chatbot features: eval-engineer alongside ai-ml-engineer.
- UI system design: ux-ui-designer with the `design-architect` skill when present;
  `interface-closure.md` is the floor.
- Any diff or PR: code-reviewer, with OCR delegation when `ocr` is installed;
  `review-discipline.md` is the floor.
- Regulated claims: compliance-advisor, advisory and not legal counsel.
- Fusion request: fusion-moderator plus at least two domain-diverse contributors (`fusion.md`).
- Progressive-context request: context-engineer (`progressive-context.md`).
