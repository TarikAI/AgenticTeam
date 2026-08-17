# Playbook — frontend-engineer

Personal checklist. Read before every task. Cap ~40 lines. Rules: `README.md` in this directory.

## Before starting
- [ ] Read my agent definition, this playbook, and the active run documents named in my task brief.
- [ ] Read the design spec section AND the API contract for every endpoint the screen consumes. <!-- learned: 2026-08-17 · cost: seeded from OCR/design-architect -->

## While building
- [ ] Build happy path + loading + empty + error + edge (long text, many items, tiny viewport) in the same task. <!-- learned: 2026-08-17 · cost: seeded from adminwright -->
- [ ] Every link, button, and menu item routes to a real implemented destination — including from empty and error states. <!-- learned: 2026-08-17 · cost: seeded from design-architect -->
- [ ] Treat API data as untrusted at the UI boundary: encode on render, never `innerHTML` raw content. <!-- learned: 2026-08-17 · cost: seeded from OCR -->
- [ ] Use design tokens only — no local magic colors, spacing, or z-indexes. <!-- learned: 2026-08-17 · cost: seeded from design-architect -->
- [ ] On admin screens: no control without its server operation; no client-side-only authorization. <!-- learned: 2026-08-17 · cost: seeded from adminwright -->

## Before claiming done
- [ ] Evidence attached (test output / verification notes), deviations and discovered work in STATUS.md.
- [ ] Keyboard-walk the screen: focus order, labels, traps. <!-- learned: 2026-08-17 · cost: seeded from adminwright -->
- [ ] Self-review the diff per review-discipline.md before handoff; state coverage listed per screen. <!-- learned: 2026-08-17 · cost: seeded from OCR -->
