# Interface closure

The floor discipline for designing any user-facing interface — with or without the
`design-architect` skill installed. Closure means every affordance goes somewhere real.
`admin-surfaces.md` adds the control-plane contract for admin screens; this
protocol governs interface design itself.

## The contract

- Enumerate before designing. Areas, states, and depth come first; a screen list is an
  output of enumeration, never an input.
- Every affordance has a real destination. No dangling links, buttons, or menu items —
  including affordances shown from empty states and error paths.
- Component census before creation: reuse the design system's vocabulary and tokens
  before inventing new ones; the theme stays consistent across every surface.
- Read-only surfaces get no mutation controls; every mutation control declares its server
  operation.
- Hand off a page map, a component map, and a coverage summary. Audit closure in the
  rendered output, not in the plan.
- Every metric shown must declare its decision, source, freshness, and drill-down
  destination; remove metrics that support no action.

## Without the skill

Run the closure audit manually on the rendered result: walk every navigation item, button,
form, and empty state; record each affordance → destination pair. Any pair without a real,
implemented destination is a blocker, not a backlog item. Close the loop by re-auditing
after fixes, in the rendered output again.
