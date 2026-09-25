# Playbook — frontend-engineer

Personal checklist. Read before every task. Cap ~40 lines. Rules: `README.md` in this directory.

## Before starting
- [ ] Read my agent definition, this playbook, and the active run documents named in my task brief.  <!-- status: baseline -->
- [ ] Read the design spec section AND the API contract for every endpoint the screen consumes.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR/design-architect -->

## While building
- [ ] Build happy path + loading + empty + error + edge (long text, many items, tiny viewport) in the same task.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->
- [ ] Every link, button, and menu item routes to a real implemented destination — including from empty and error states.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from design-architect -->
- [ ] Treat API data as untrusted at the UI boundary: encode on render, never `innerHTML` raw content.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->
- [ ] Use design tokens only — no local magic colors, spacing, or z-indexes.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from design-architect -->
- [ ] On admin screens: no control without its server operation; no client-side-only authorization.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->

## Before claiming done
- [ ] Complete with typed evidence (`file:`, `cmd:<exec-id>`, `commit:`) through `complete`; record discovered work with `add-task`, deviations as a checkpoint.  <!-- status: baseline -->
- [ ] Keyboard-walk the screen: focus order, labels, traps.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from adminwright -->
- [ ] Self-review the diff per review-discipline.md before handoff; state coverage listed per screen.  <!-- status: baseline · learned: 2026-08-17 · source: seeded from OCR -->
