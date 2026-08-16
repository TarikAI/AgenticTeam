# Evidence-gated delivery workflow

The authoritative runtime stages are numbered below. Entry mode may begin later, but every build
must preserve relevant safety inputs, independent verification, release controls, and learning.

## Entry

- `idea`: begin at `00_intake`.
- `plan-given`: preserve the supplied authority and begin at `03_readiness` unless a named gap
  requires a bounded earlier artifact.
- `execute-only`: create task envelopes and begin at `04_build`; never write a competing plan.

## Stages

1. **00 Intake — ceo:** normalize outcome, users, constraints, authority, entry/context/autonomy,
   risks, and unknowns. Output `BRIEF.md` and assumptions.
2. **01 Product — product-manager:** product outcomes, journeys, scope/non-goals, acceptance, and
   research only where it changes decisions. Human gate in HITL.
3. **02 Solution — architect + UX + triggered specialists:** architecture/data/API/experience,
   threat/privacy/operability/accessibility/cost requirements. Human gate in HITL; independent
   review in autonomous/supervised.
4. **03 Readiness — delivery-lead:** trace requirements to contracts, tasks, tests, owners, and
   risks. Nothing assignable lacks acceptance/evidence. Human gate in HITL.
5. **04 Build — leads/engineers/integrator:** claim dependency-ready, non-overlapping tasks;
   implement vertical evidence; integrate in order; repair within retry policy.
6. **05 Verify — QA/reviewers/specialists:** independent traceability and reproduced checks on the
   integrated result. Verdict is PASS, CONDITIONAL, or FAIL.
7. **06 Release — release/SRE/DevOps/docs:** artifact identity, migration, staged rollout,
   monitoring, support, and tested rollback. Production/public action always waits for human.
8. **07 Learn — delivery-lead/all:** retrospective, scoped lessons, evaluated playbook/team
   proposals, human-controlled promotion.

Marketing and customer-success work may run in parallel after product direction stabilizes, but
publishing, sending, advertising spend, and public commitments remain human-gated.

Each stage is governed by its `CONTEXT.md` and advanced through the state CLI. Do not infer a gate
from persuasive prose; attach objective outputs and evidence.
