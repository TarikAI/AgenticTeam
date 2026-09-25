# Playbook — security-engineer

Personal checklist. Read before every task. Cap ~40 lines. Rules: `README.md` in this directory.

## Before starting
- [ ] Read my agent definition, this playbook, and the active run documents named in my task brief.  <!-- status: baseline -->
- [ ] Know the surface class before reviewing: admin/control surfaces get the admin-surfaces checklist, everything else the standard pass.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->

## While building
- [ ] Every endpoint: authenticated ≠ authorized for THIS resource — check per-object scope (IDOR) on every access.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->
- [ ] Query construction: parameterized only; trace any string-built query, filter, sort, or path.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->
- [ ] Render paths: find every place user/API content reaches the DOM and confirm encoding (XSS).  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->
- [ ] Admin surfaces: least privilege/default deny, tamper-evident audit (actor, target, time, reason, result), per-row authz in bulk ops, step-up or dual control for high-impact actions, safe impersonation, export controls.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->
- [ ] Concurrency: shared mutable state, check-then-act on permissions/quotas, idempotency on money/messaging/provisioning commands.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->
- [ ] With `ocr` present: pull per-file rule checklists (`ocr delegate rule`) and verify each item; findings normalized to file:line.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->

## Before claiming done
- [ ] Complete with typed evidence (`file:`, `cmd:<exec-id>`, `commit:`) through `complete`; record discovered work with `add-task`, deviations as a checkpoint.  <!-- status: baseline -->
- [ ] Findings carry attack scenario and fix, at true severity — no inflation, no courtesy downgrades.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->
- [ ] Denial paths tested, not assumed: 403/404 behavior verified for out-of-scope and cross-tenant targets.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->
