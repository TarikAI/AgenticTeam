# Playbook — code-reviewer

Personal checklist. Read before every task. Cap ~40 lines. Rules: `README.md` in this directory.

## Before starting
- [ ] Read my agent definition, this playbook, and the active run documents named in my task brief.
- [ ] Read the task brief and ARCHITECTURE.md contract before the diff — contract compliance is check #1. <!-- learned: 2026-08-17 · cost: seeded from OCR -->
- [ ] I am not the author of the diff I am reviewing. <!-- learned: 2026-08-17 · cost: seeded from adminwright/OCR -->
- [ ] Check preflight: `ocr` CLI present (delegate preview → rule → diff) or absent (manual file selection, same checklist). <!-- learned: 2026-08-17 · cost: seeded from OCR -->

## While building
- [ ] Review the diff AND its blast radius: callers and contract consumers, not just changed lines. <!-- learned: 2026-08-17 · cost: seeded from OCR -->
- [ ] Construct the failing scenario (input → wrong outcome) for every suspected bug; otherwise it's a question, not a finding. <!-- learned: 2026-08-17 · cost: seeded from OCR -->
- [ ] Security pass on every touched surface: injection, XSS rendering, per-resource authz (IDOR), validation, secrets, SSRF/traversal. <!-- learned: 2026-08-17 · cost: seeded from OCR -->
- [ ] Trace null/undefined flow, race and thread-safety, resource leaks, off-by-ones — the quiet defect classes. <!-- learned: 2026-08-17 · cost: seeded from OCR -->
- [ ] Ask of the tests: do they assert the acceptance criteria, and would they fail if the feature broke? <!-- learned: 2026-08-17 · cost: seeded from OCR -->
- [ ] Do not stop at the first blocker finding — finish the coverage list. <!-- learned: 2026-08-17 · cost: seeded from OCR -->

## Before claiming done
- [ ] Evidence attached (test output / verification notes), deviations and discovered work in STATUS.md.
- [ ] Every reviewable file ends reviewed or skipped-with-reason; totals and coverage rate reported. <!-- learned: 2026-08-17 · cost: seeded from OCR -->
- [ ] Every finding is line-anchored `[SEV] file:line` with scenario and fix; severity honest both ways. <!-- learned: 2026-08-17 · cost: seeded from OCR -->
- [ ] Likely false positives discarded silently — precision over noise. <!-- learned: 2026-08-17 · cost: seeded from OCR -->
