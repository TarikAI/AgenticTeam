# Admin and control surfaces

The floor discipline for any admin console, back office, ops tool, or internal control
surface — with or without the `adminwright` skill installed. When the skill is present,
route to it and follow its manifest machinery (`skill-acquisition.md`); this
protocol is the always-on contract either way.

## The contract

- Nothing loose. Every screen traces to a capability; every capability traces to a server
  operation, a server-side policy, an authoritative data source, an audit event where
  required, a test, and resolvable evidence. An orphan on either side is a defect.
- No mock, placeholder, stub, random, or hard-coded value in the release path. A value
  that is genuinely static by design is registered — `declaredStatic[]` under the skill,
  otherwise a `STATIC.md` table — with a reason and an approver. That registry is the only
  sanctioned exception.
- Authorization is enforced server-side, per resource, and per target row in bulk
  operations. Hidden navigation and client-side checks are never authorization.
- Build the spine first: authentication, role and scope model, audit trail, one real
  read-only list, one low-risk command end to end — before fanning out to many screens.
  Retrofitting these onto twenty finished screens is a rewrite, not a patch.
- Cover every state per screen: loading, empty, filtered-empty, validation, conflict,
  error, forbidden, partial/stale, and success.
- Prefer safe recovery over irreversible deletion — preview, confirmation, reason capture,
  step-up authentication, or undo, scaled to risk.
- Evidence over screenshots. The implementer never marks their own work reviewed.
- Profiles scale gate severity (internal / standard / regulated), never honesty. Money,
  health, minors, or audited data means the regulated bar: separation of duties,
  privileged-read audit, and no unresolved assumptions.

## Without the skill

Produce the same artifacts by hand: a capability→operation→policy→audit trace table, an
authorization matrix (role × capability × scope), the static-value registry, a
state-coverage list per screen, and evidence links recorded in task state. Vertical
slices only — never a screen without its server operation and policy.
