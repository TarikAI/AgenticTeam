# Playbook — platform-admin-engineer

Personal checklist. Read before every task. Cap ~40 lines. Rules: `README.md` in this directory.

## Before starting
- [ ] Read my agent definition, this playbook, and the active run documents named in my task brief.
- [ ] Enumerate actors, entities, lifecycle states, and risky actions before naming any screen. <!-- learned: 2026-08-17 · cost: seeded from adminwright -->
- [ ] Check preflight: adminwright installed (use its manifest CLI) or absent (hand-make the trace table, authz matrix, STATIC.md, state coverage). <!-- learned: 2026-08-17 · cost: seeded from adminwright -->

## While building
- [ ] Build the spine first: auth, roles/scopes, audit trail, one real read list, one low-risk command — before fan-out. <!-- learned: 2026-08-17 · cost: seeded from adminwright -->
- [ ] Every control connects to an authorized server operation; hidden nav or client checks are never authorization. <!-- learned: 2026-08-17 · cost: seeded from adminwright -->
- [ ] Bulk operations enforce authorization per target row, not once per request. <!-- learned: 2026-08-17 · cost: seeded from adminwright -->
- [ ] No mock, stub, or hard-coded value in the release path; static-by-design values registered with reason and approver. <!-- learned: 2026-08-17 · cost: seeded from adminwright -->
- [ ] Destructive actions get preview/confirm/reason/undo scaled to risk — prefer recovery over deletion. <!-- learned: 2026-08-17 · cost: seeded from adminwright -->

## Before claiming done
- [ ] Evidence attached (test output / verification notes), deviations and discovered work in STATUS.md.
- [ ] Every screen traced: capability → server operation → policy → data source → audit event → test → evidence; orphans written down as gaps. <!-- learned: 2026-08-17 · cost: seeded from adminwright -->
- [ ] State coverage list per screen: loading, empty, filtered-empty, validation, conflict, error, forbidden, success. <!-- learned: 2026-08-17 · cost: seeded from adminwright -->
- [ ] With adminwright: `validate --phase release` and `coverage` both exit 0 — pasted, not paraphrased. <!-- learned: 2026-08-17 · cost: seeded from adminwright -->
- [ ] I did not mark my own implementation reviewed. <!-- learned: 2026-08-17 · cost: seeded from adminwright -->
