# Playbook — code-reviewer

Personal checklist. Read before every task. Cap ~40 lines. Rules: `README.md` in this directory.

## Before starting
- [ ] Read my agent definition, this playbook, and the active run documents named in my task brief.  <!-- status: baseline -->
- [ ] Read the task brief and ARCHITECTURE.md contract before the diff — contract compliance is check #1.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->
- [ ] I am not the author of the diff I am reviewing.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright/OCR -->
- [ ] Check preflight: `ocr` CLI present (delegate preview → rule → diff) or absent (manual file selection, same checklist).  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->

## While building
- [ ] Review the diff AND its blast radius: callers and contract consumers, not just changed lines.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->
- [ ] Construct the failing scenario (input → wrong outcome) for every suspected bug; otherwise it's a question, not a finding.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->
- [ ] Security pass on every touched surface: injection, XSS rendering, per-resource authz (IDOR), validation, secrets, SSRF/traversal.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->
- [ ] Trace null/undefined flow, race and thread-safety, resource leaks, off-by-ones — the quiet defect classes.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->
- [ ] Ask of the tests: do they assert the acceptance criteria, and would they fail if the feature broke?  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->
- [ ] Do not stop at the first blocker finding — finish the coverage list.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->

## Before claiming done
- [ ] Complete with typed evidence (`file:`, `cmd:<exec-id>`, `commit:`) through `complete`; record discovered work with `add-task`, deviations as a checkpoint.  <!-- status: baseline -->
- [ ] Every reviewable file ends reviewed or skipped-with-reason; totals and coverage rate reported.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->
- [ ] Every finding is line-anchored `[SEV] file:line` with scenario and fix; severity honest both ways.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->
- [ ] Likely false positives discarded silently — precision over noise.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->
