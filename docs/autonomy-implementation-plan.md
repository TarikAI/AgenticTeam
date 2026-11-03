# AgenticTeam autonomy implementation plan

Updated **2 November 2026**, including the final integration refresh to **`bf9d11a`**. Wiring `c4794ec`, quality measurement `86e96b0` and the review fixes are now merged into `autonomy-integration`. Main `3aafe1b` remains the documentation checkout. The [progress review](autonomy-progress-review.md) gives the latest implementation, exact evidence and residual acceptance for R01–R12; its earlier 4949185 pass is historical.

**Preserve the new fixes.** Broker executor routing, narrower fixture admission, broader bundle observation, active revocation, evaluated promotion and command/environment corrections now exist with recorded offline tests. They are not yet fully validated on the operational role-step boundary. Remaining work includes fixture capability confinement, missing-model evidence, complete effective configuration, timeout/revocation lifecycle proof, container transport, supervised assessment/grading, immutable context, four duty schedulers and retention.

The source-equivalent review-fixes candidate records **659 tests OK, 7 skipped**; this docs review did not rerun the full runtime suite. Real Docker drills and authorized direct sizing exist, but no complete live supervised role-step pilot, qualification certificate or activated service is evidenced.

## Plans and complete resume prompts

| Workstream | Detailed acceptance plan | Copy-ready prompt | Current checkpoint |
| --- | --- | --- | --- |
| Whole program | This plan and [progress review](autonomy-progress-review.md) | [Master prompt](autonomy-implementation-prompt.md) | Preserve merged changes, then close residual safety/quality gates. |
| Supervisor | [Supervisor completion](supervisor-completion-plan.md) | [Supervisor prompt](supervisor-completion-prompt.md) | S1–S3 offline-verified; S4 partly host-verified; role-step transport and lifecycle work remain. |
| Quality | [Quality qualification](quality-qualification-plan.md) | [Quality prompt](quality-qualification-prompt.md) | Registry/admission/review fixes merged; residual identity/fixture gaps and protected live assessment remain. |
| Persistent core | [Durable core](durable-core-plan.md) | [Core prompt](durable-core-prompt.md) | Core/role-step/promotion wiring merged; context, four advisory duties and retention remain incomplete. |
| Agent instructions | [Prompt improvements](agent-prompt-improvement-plan.md) | [Prompt-improvement prompt](agent-prompt-improvement-prompt.md) | Targeted shared/role/skill corrections needed; canonical role prompts unchanged by this review. |

One integration owner controls shared runtime, schema, policy and generated documentation changes. Focused prompts may run in isolated branches with agreed ownership; they must not concurrently overwrite shared runtime files or another session's progress record. Main's documentation update does not merge or activate those branches.

## Current phase assessment

| Original phase | Current evidence | Next gate |
| --- | --- | --- |
| 0 Baseline/contracts | Recorded; libraries exist; wiring contracts distinguish implemented from proposed. | Reconcile stale summaries and pins. No schema redesign without a concrete gap. |
| 1 Supervisor safety | Positive controls, consistent environment, bound proof, cancellation/container ownership and corrected recipes implemented. | Keep regressions; prove final integrated host lifecycle. |
| 2 Quality admission/core | Libraries merged; admission/role-step wiring and review fixes merged with recorded offline tests. | R01–R10: execution boundary, strict admission, full context and six-duty behavior. |
| 3 Offline/host recovery | Review fixes record 659 Windows tests (7 skipped); earlier 87 Ubuntu tests and S4 container drills remain historical. | Fresh combined-candidate verification after fixes; remaining host/transport drills. Historical counts are not new test results. |
| 4 Qualification/pilot | Authorized direct sizing only; build attempt stopped at QA. | Receipt-bound assessment, protected grader, complete supervised role-step validation and scoped qualification. |
| 5 Activation | Templates only; no activated service evidenced. | Qualified bundle, exact activation authority, readback, allowed/refused jobs and stop/restart proof. |
| 6 Improvement | Promotion/retention libraries and design are partial. | Wire evaluated knowledge promotion, dependency-aware retention, drift/revocation and qualified rollback. |

Do not substitute a whole-run pilot: the recorded owner target is **role-steps** on Linux with a proven container boundary. Whole-run remains explicit legacy compatibility. Windows fixture transport and same-UID Linux test processes do not establish the required model-worker isolation.

## Priority corrections

The [review](autonomy-progress-review.md) gives source paths and concrete acceptance cases for each row.

| Order | Work | Why it gates progress |
| --- | --- | --- |
| 1 | R01: validate executor isolation and timeout/child termination. | Executor routing is implemented; real containment and command-lifetime evidence remain incomplete. |
| 2 | R02–R04: finish fixture confinement/full observed identity and validate active revocation. | No passed credentials does not prove no model access; missing model IDs currently pass; real role-step revocation still needs proof. |
| 3 | R05: prove container role-step transport. | The chosen operational mode is correctly refused until confinement and peer identity work on the real engine. |
| 4 | R06–R10: supervised assessment/grading, complete consumed snapshots, all duties, protected learning/retention and coherent tools. | These turn existing libraries into the promised team and valid quality evidence. |
| 5 | R11–R12: remaining lifecycle drills, integration verification and truthful records. | Stale summaries and sibling-branch tests do not qualify the final runtime. |

## Implementation order

### A. Reconcile and pin the candidate

Inspect current branch heads, dirty files, changes relative to integration and ongoing ownership. Preserve all user work and historical evidence. Wiring, quality, core, safety and review-fix changes are incorporated at bf9d11a. Review later deltas only; do not re-merge these branches. Follow actual merge authority; this documentation request does not merge or push anything.

Carry updated plans into the chosen implementation checkout with a reviewed diff. Update the integration owner's existing progress record instead of creating a second competing runtime status log. Record source revisions, contracts, migrations, test provenance and open risks. Correct stale “wiring not started,” “no host evidence,” and “no model calls” claims with dated, scope-specific amendments.

Gate: one identifiable candidate and integration owner; no lost work, duplicate libraries, conflicting schema ownership or unsupported readiness claim.

### B. Close authority and admission gaps

Close the residual R01–R05 acceptance before model-backed role-step dispatch; preserve the newly implemented executor, observation and monitor. Every path executing candidate code, including implicit checks at completion, must use the bounded worker or grader executor. Trusted owner code validates state and authenticated receipts; it does not execute candidate code with owner privileges. Preserve usage reconciliation, leases, cancellation, safe paths and output limits.

Fixture status must be explicit and enforceable, with no operational route, credentials or model/network access. Verify or immutably materialize the effective model/harness/tool/prompt/policy/context/boundary bundle. Detect running-attempt revocation, expiry and invalidation, stop safely and reject late results. Keep container-role-step refusal until real-engine tests prove transport and owner-data/process isolation.

Gate: meaningful before/after regressions pass; operational generic commands cannot bypass the contracts; uncertain ownership, cost or isolation remains held.

### C. Complete the six-duty and quality path

Finish R06–R10 using existing modules. Assemble and consume immutable complete packets with actual role prompts, task inputs, acceptance, source versions and approved knowledge. Candidate lessons stay candidates. Schedule context, evaluation, security and reliability duties under bounded owner-configured triggers, alongside delivery and independent QA. Avoid recursion, duplicate dispatch and unbounded advisory work.

Preserve the newly wired evaluated lesson promotion; finish rollback and reference-aware retention. Implement supervised assessment with broker principal/receipt evidence and a protected grader sandbox without owner credentials. Direct CLI sizing stays diagnostic only. Follow the prompt-improvement plan to align shared contracts, canonical roles, generated mode/authority instructions and skills; preserve the corrected command-rule/PowerShell and shared live-smoke environment behavior, then validate remaining role/mode consistency. Version prompt changes in the effective bundle and measure adherence before promotion.

Gate: core and quality acceptance matrices pass in fixtures; step completion differs from job completion; successful steps consume no failure retry; builder children cannot gain independent QA authority by naming a role.

### D. Verify the exact combined candidate

Run affected regressions, schema checks, manifest validation, generated docs, scenarios, skills preflight and one coherent full unit suite on the final candidate. Include installed/owner-copy packaging. Repeat affected checks after later fixes; do not cite a pre-change full suite as covering a later edit. Independent review must assess execution authority and admission as well as behavior.

Complete harmless host drills within actual authorization: systemd lifecycle, supervisor and engine restarts, dummy credential delivery, supported logoff/reboot, container transport, cancellation/unknown usage and no second writer. Pin host, image, paths and hashes. Material runtime changes invalidate earlier proof as its contract requires.

Gate: no unresolved release-blocking finding; exact passed/failed/skipped cases; unsupported hosts remain unqualified. No paid operation hidden in offline validation.

### E. Qualify and run the selected live pilot

Freeze a concrete experiment packet: role-step project/store, provider and all effective models, harness version, bundle/task-class digests, secret references, holdouts, graders, trial count, absolute/comparative thresholds, per-attempt/run/aggregate allowance, wall-clock limit, expiry and stop rules. Reuse actual prior authorization only when it covers that packet. Earlier Max-subscription sizing approval does not authorize new assessment batches or activation.

First qualification uses protected absolute acceptance and safety floors under bounded assessment authority; it cannot unlock operational jobs or sign its own promotion. A complete live role-step pilot must demonstrate independent QA, usage, recovery and final delivery. One happy pilot does not replace task-class quality trials. Failed or inconclusive results hold; do not add trials, relax graders or increase retries without covered authority.

Gate: independent evaluator records pass/fail/inconclusive with exact source/configuration and receipt-linked evidence, usage reconciled, owner promotion scoped to accepted capabilities/task classes. No certificate from fixtures or direct sizing.

### F. Activate and improve within scope

Prepare final service configuration, trigger/schedule and task classes, qualified route, account and secret references, limits, local health/hold handling, retention, stop/recovery and rollback. Activate within concrete existing authority, or request missing authorization after the package is reviewable.

Read back registration; demonstrate an allowed task, denied task, restart, cancellation and reconciled usage. First activation without an earlier qualified route rolls back to paused intake and no dispatch after reconciliation. External notifications need destination authorization; unchanged status stays quiet.

Add real failures as regression evidence, preserve provenance and evaluate improvements before owner promotion. Requalify material changes. Qualify a second model/harness for the same task classes before claiming tested portability; arbitrary future models remain unqualified. Work requires its host and dependencies to be available.

## Recommended operating core

| Persistent responsibility | Owns | Authority limit |
| --- | --- | --- |
| Delivery Lead | Goal, graph, ownership, dependencies and recovery coordination. | Cannot authorize human gates or approve its own implementation. |
| Context Engineer | Frozen context, provenance, freshness and approved lessons. | Cannot promote candidates or alter accepted requirements. |
| QA Lead | Independent acceptance and commit-specific verdict. | Separate execution principal from builder/remediator. |
| Eval Engineer | Evaluation plans, baselines, trials and qualification proposals. | Cannot weaken thresholds after results or promote itself. |
| Security Engineer | Boundaries, tool permissions, findings and exceptions. | Cannot grant itself credentials or weaken policy. |
| SRE Engineer | Health, incidents, restart position and recovery proposals. | Cannot extend spend or restart an uncertain writer. |

These are **six persistent responsibilities**, not six continuously billing sessions or a universal minimum. One deterministic supervisor owns dispatch, state, accounting, identity and admission. The 50-role catalog remains; Product Manager, CTO, builders, Code Reviewer, Release Manager and specialists execute on demand. Keep a valid build preset; six control roles alone cannot deliver every project.

## Quality commitments and completion

An accepted job must pass every mandatory criterion at the released content version. Admission requires valid evidence for the exact effective bundle and task class. A replacement meets predeclared absolute and comparative thresholds; unknown/inconclusive evidence holds it. Learning promotion is evaluated, authorized and reversible.

These controls enforce a quality floor and reject measured regressions. They cannot guarantee universally best output or zero future degradation after any LLM/harness replacement. Retain the focused plan's uncertainty-aware criteria, including its proposed 90% lower-bound floor and zero-regression comparison; freeze approved policy before trials, not after results.

Completion requires focused acceptance matrices, independent review, scoped live qualification and explicit verified activation. Report implemented, offline-verified, host-verified, live-measured, qualified and activated separately. A source finding is not a reproduced exploit; a proposed correction is not a fix. Keep secrets and sensitive transcripts outside repository docs, prompts and chat.
