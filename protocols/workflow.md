# Evidence-gated delivery workflow

Runs move through numbered stages `00_intake` … `07_learn`. The entry mode may start later, but
every build keeps independent verification, release controls, and learning. Each stage is
governed by its `CONTEXT.md` and left only through `advance`; persuasive prose never opens a gate.

## Entry (`init-run --entry`)

- `idea`: begin at `00_intake`.
- `plan-given`: adopt the supplied plan and begin at `03_readiness` unless a named gap needs a
  bounded earlier artifact (`plan-modes.md`).
- `execute-only`: create task envelopes and begin at `04_build`; never write a competing plan.

## Stages and owners

| Stage | Owner → artifact | Work |
|---|---|---|
| 00_intake | ceo → `BRIEF.md`, `ASSUMPTIONS.md` | outcome, users, constraints, authority, entry/context/autonomy choices, risks, unknowns |
| 01_product | product-manager → `PRD.md` (`AC-` ids) | journeys, scope and non-goals, measurable acceptance; research only where it changes a decision |
| 02_solution | cto-architect → `ARCHITECTURE.md` + `_decisions/ADR-NNN.md`; ux-ui-designer → `DESIGN.md` | architecture, data, API, experience; triggered specialists add threat, privacy, operability, accessibility, and cost requirements |
| 03_readiness | delivery-lead → `READINESS.md` and the task graph | trace every `AC-` id to tasks and checks; nothing assignable lacks acceptance and evidence |
| 04_build | leads, engineers, build-integrator | claim ready, non-overlapping tasks; vertical slices with evidence; integrate in dependency order |
| 05_verify | qa-lead → `VERIFICATION.md` | independent, reproduced checks on the integration commit; code-reviewer, security-engineer, and triggered specialists supply findings |
| 06_release | release-manager → `RELEASE.md` | artifact identity, migrations, staged rollout, monitoring, tested rollback; production and public actions always wait for the human |
| 07_learn | delivery-lead → `RETROSPECTIVE.md`; ceo → `DELIVERY-REPORT.md` | retrospective, scoped lessons, evaluated proposals (`evolution.md`), the final report (`final-report.md`) |

Marketing runs as a parallel track once product direction is stable: artifacts live under
`runs/<id>/_marketing/`, the cmo owns `MARKETING.md`, and publishing, sending, ad spend, and
public commitments stay behind the hard gates (`guardrails.md`).

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
| 04_build | every task closed; write tasks carry typed evidence and passed their declared checks | same |
| 05_verify | remediation tasks closed with evidence; `VERIFICATION.md` verdict lines, independent verifier, `Verified-SHA` = HEAD | same |
| 06_release | `RELEASE.md`; HEAD still equals the verified commit; human release checkpoint | HEAD still equals the verified commit; human release checkpoint |
| 07_learn | `RETROSPECTIVE.md`, `DELIVERY-REPORT.md` | `DELIVERY-REPORT.md` |

In every stage `advance` also refuses while a task of the stage is open, a checkpoint is
pending, or an activated specialist has neither a completed task nor a deactivation reason; then
the profile's gate applies (`autonomy.md`), and a human gate returns exit code 2 with a new stage
checkpoint. Remediation found in 05_verify is added
to 05_verify (the default stage is always the current one), so it gates the verify exit.

`VERIFICATION.md` starts with three machine-read lines: `Verdict: PASS|CONDITIONAL|FAIL`,
`Verifier: <role-id>` (installed, and never a 04_build claimant), and `Verified-SHA: <sha>`
(the project's current HEAD, or `none` without git). The verdict names the code as it is now:
when remediation inside 05_verify moves HEAD, the verifier verifies again at the new HEAD and
updates the line, and the integration commit recorded at the 04_build exit is only the review's
starting point. The 06_release exit checks the same line against HEAD once more, so a commit
made after verification (a version bump, a hotfix) cannot ride an older verdict into production;
re-verify at HEAD, or the human waives `stage-exit:06_release:verified-head` with a reason.
FAIL blocks; CONDITIONAL needs the human's waiver `stage-exit:05_verify:conditional`. Any named
requirement can be waived only by the human (`waive --requirement stage-exit:<stage>:<check>`).
