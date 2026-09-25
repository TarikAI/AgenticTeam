# Playbook — platform-admin-engineer

Personal checklist. Read before every task. Cap ~40 lines. Rules: `README.md` in this directory.

## Before starting
- [ ] Read my agent definition, this playbook, and the active run documents named in my task brief.  <!-- status: baseline -->
- [ ] Enumerate actors, entities, lifecycle states, and risky actions before naming any screen.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->
- [ ] Check preflight: adminwright installed (use its manifest CLI) or absent (hand-make the trace table, authz matrix, STATIC.md, state coverage).  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->

## While building
- [ ] Build the spine first: auth, roles/scopes, audit trail, one real read list, one low-risk command — before fan-out.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->
- [ ] Every control connects to an authorized server operation; hidden nav or client checks are never authorization.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->
- [ ] Bulk operations enforce authorization per target row, not once per request.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->
- [ ] No mock, stub, or hard-coded value in the release path; static-by-design values registered with reason and approver.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->
- [ ] Destructive actions get preview/confirm/reason/undo scaled to risk — prefer recovery over deletion.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->

## Before claiming done
- [ ] Complete with typed evidence (`file:`, `cmd:<exec-id>`, `commit:`) through `complete`; record discovered work with `add-task`, deviations as a checkpoint.  <!-- status: baseline -->
- [ ] Every screen traced: capability → server operation → policy → data source → audit event → test → evidence; orphans written down as gaps.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->
- [ ] State coverage list per screen: loading, empty, filtered-empty, validation, conflict, error, forbidden, success.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->
- [ ] With adminwright: `validate --phase release` and `coverage` both exit 0 — pasted, not paraphrased.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->
- [ ] I did not mark my own implementation reviewed.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->
