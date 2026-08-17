# Playbook — qa-lead

Personal checklist. Read before every task. Cap ~40 lines. Rules: `README.md` in this directory.

## Before starting
- [ ] Read my agent definition, this playbook, and the active run documents named in my task brief.
- [ ] Derive the risk map from acceptance criteria + architecture before writing strategy: what failure hurts most, what test catches it cheapest. <!-- learned: 2026-08-17 · cost: seeded from OCR -->

## While building
- [ ] Include the cases the PRD implies but doesn't spell out: error, empty, edge, abuse, concurrent edit, double-submit, slow network. <!-- learned: 2026-08-17 · cost: seeded from OCR -->
- [ ] Admin surfaces: test denial and per-row-scope paths, not just happy paths; verify audit events fire for privileged reads and mutations. <!-- learned: 2026-08-17 · cost: seeded from adminwright -->
- [ ] Seed production-shaped fixtures: every lifecycle state, long/localized text, missing optionals, conflicts, cross-tenant neighbours. <!-- learned: 2026-08-17 · cost: seeded from adminwright -->
- [ ] Treat review-gate and manifest findings as defect input with owners; a "fixed" finding without a regression test isn't fixed. <!-- learned: 2026-08-17 · cost: seeded from OCR/adminwright -->
- [ ] A test that can't fail is a lie — spot-check assertions actually bind to behavior. <!-- learned: 2026-08-17 · cost: seeded from OCR -->

## Before claiming done
- [ ] Evidence attached (test output / verification notes), deviations and discovered work in STATUS.md.
- [ ] Verdict table maps every acceptance criterion to an executed check; zero known must-fix defects or no ship. <!-- learned: 2026-08-17 · cost: seeded from adminwright -->
