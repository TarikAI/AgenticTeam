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

## Stage exit contracts

`advance` refuses to leave a stage until its exit contract passes. The contract is policy data
(`config/policies.json` → `stage_exits`), chosen by the run's context method. Create each
artifact with `scaffold --artifact NAME`; a file that still contains a `{{...}}` marker or
`TODO` does not count.

| Stage | `bmad-progressive` | `adaptive` |
|---|---|---|
| 00_intake | `BRIEF.md`, `ASSUMPTIONS.md` | `BRIEF.md` with at least one `AC-` id |
| 01_product | `PRD.md` with `AC-` ids | — |
| 02_solution | `ARCHITECTURE.md` | — |
| 03_readiness | `READINESS.md` tracing every `AC-` id | — |
| 04_build | every task closed; write tasks carry typed evidence | same |
| 05_verify | `VERIFICATION.md` verdict lines, independent verifier, integration SHA | same |
| 06_release | `RELEASE.md` + human release checkpoint | human release checkpoint |
| 07_learn | `RETROSPECTIVE.md`, `DELIVERY-REPORT.md` | `DELIVERY-REPORT.md` |

In every stage `advance` also refuses while a checkpoint is pending or an activated specialist
has neither a completed task nor a deactivation reason. Remediation found in 05_verify is added
to 05_verify (the default stage is always the current one), so it gates the verify exit.

`VERIFICATION.md` starts with three machine-read lines: `Verdict: PASS|CONDITIONAL|FAIL`,
`Verifier: <role-id>` (installed, and never a 04_build claimant), and `Verified-SHA: <sha>`
(the integration commit recorded when 04_build exits, or `none` without git). FAIL blocks;
CONDITIONAL needs the human's waiver `stage-exit:05_verify:conditional`. Any named requirement
can be waived only by the human (`waive --requirement stage-exit:<stage>:<check>`).
