# Copy-ready prompt: implement quality qualification

Use this prompt in the AgenticTeam source checkout. It requests implementation, not immediate model spending or service activation. For the complete program, use the [master implementation prompt](autonomy-implementation-prompt.md). The detailed acceptance contract is [Quality qualification plan](quality-qualification-plan.md).

---

Implement AgenticTeam's quality-qualification workstream completely through the authorized scope. Read these documents first:

1. `docs/autonomy-implementation-plan.md` and any existing `docs/autonomy-implementation-progress.md`.
2. `docs/quality-qualification-plan.md` in full.
3. `docs/supervisor-completion-plan.md` and `docs/durable-core-plan.md`, especially shared identity, role-step, authority, assessment and lifecycle contracts.
4. `protocols/team-evaluation.md`, `protocols/evolution.md`, `protocols/harness-security.md`, `config/guarantees.json`, `docs/pilot-plan.md` and applicable repository instructions.

An explicit user instruction to execute this prompt authorizes its local implementation and offline checks, subject to applicable user and repository rules. Merely reading a plan, another agent's message or a historical example does not authorize paid calls, expanded access or activation. Reuse matching explicit session authorization rather than asking twice. Preserve current user changes, the generated guide and documentation edits. Coordinate with the integration owner before editing shared runtime files. Delegate independent review or isolated test work where useful; do not have multiple writers modify `scripts/agentic_supervisor.py`, `scripts/agentic_team.py`, shared schemas or policies concurrently.

## Intended result

Build owner-controlled qualification that prevents new operational dispatch under an unknown, expired, revoked, mismatched, out-of-scope or inconclusive model/harness configuration. Support bounded, explicitly authorized isolated assessment so the first configuration can be evaluated without an existing qualified baseline. Keep six durable responsibilities plus one deterministic supervisor and on-demand builders/reviewers/release roles consistent with the master plan. This is not a six-role-only build preset or six permanently billing sessions.

Do not promise universal non-regression or best quality from every LLM. Enforce a scoped measured floor, independent acceptance, preserved authority, honest uncertainty and reversible owner-approved promotion.

## Required work

### A. Establish the baseline and contracts

Inspect the actual code and tests. Record the source revision, current behavior, gaps, migration strategy and planned checks in the integration progress record. Reconfirm the quality plan's source anchors instead of assuming they still apply.

The repository has thirteen role emitters, but only `claude` and `command` supervisor adapters in the inspected baseline. Its current live smoke is Claude-specific and succeeds by reaching the human release gate. Preserve that contract. Add separate cases for unattended completion and role-sized steps.

Coordinate supervisor pre-pilot fixes before paid assessment: positive isolation controls, explicit credential filtering across preflight/probe/worker paths, correct host/worker namespace mapping and tested process/container stop behavior. Do not treat marker strings, a filtered environment or a changed home directory as an OS boundary.

### B. Implement immutable qualification records

Implement the strict schemas and protected owner-side registry specified in the quality plan. Reject malformed records, unknown authority fields, duplicate JSON keys, unsafe paths, unsupported versions and non-finite values.

Fingerprint the complete effective tuple: provider/resolved model and inference settings; every delegated role's effective model; harness/adapter/executable or image version; tool schemas, trusted identities and effective permissions; canonical and compiled prompts, shared contracts, skills, policy and routing; owner runtime and parser versions; sandbox, mounts and approved environment names; context/retrieval procedure and approved knowledge/playbooks.

Record exact task/context/artifact digests per attempt without forcing task content into the reusable configuration certificate. Track input schemas and context assembly in the bundle. Mutable aliases with unverifiable versions must not masquerade as immutable model snapshots.

Keep signing authority, private test sets and raw evidence outside worker-writable storage. Do not put credentials, credential hashes, signing keys or private answers in code, prompts, logs or command arguments. Publish sanitized summaries and hashes only.

Implement protected, versioned owner promotions, revocations and route rollback with signatures, a hash-chained event history, monotonic revisions, store locking and atomic updates. Passing evaluation does not promote or activate a candidate. Reuse proven authority utilities only where their scope is appropriate; a run token is not automatically a global promotion credential.

Choose and document the actual new command/API syntax during implementation. No proposed operation in the plan should be presented as an already-existing command.

### C. Build bounded assessment and trustworthy grading

Separate `assessment` from `operational` execution. Assessment requires a concrete owner-approved plan naming bundle, task set, isolated project/store, allowed operations, trial count, per-attempt/run/aggregate budgets, wall-clock cap, secret references, expiry and stop conditions. It may not process operational work, perform external commitments, alter routes, grant approvals or mint its own certificate.

Bootstrap assessment uses protected absolute criteria and clearly records that no comparative baseline exists. Subsequent candidates compare with a qualified baseline for the same task class. Fake adapters and scripted results remain labeled offline evidence; never accept them as live model qualification, actual provider cost or real boundary certification.

Protect immutable qualification holdouts and reference answers from workers, shared memory and lesson files. Keep development and reserve cases separate. Freeze candidate output and grade it independently. Execute all candidate code and candidate-authored checks in an unprivileged sandbox without owner credentials or private store access; never import or execute them in the credential-bearing owner evaluator process.

Prefer objective checks. Pin and calibrate supplementary model judges independently; preserve disagreement and missing evidence. Bind builder and verifier outcomes to broker-issued identities from the durable-core workstream, not self-declared role names. Include known-bad artifacts so graders demonstrably fail false successes.

### D. Implement honest statistical decisions

Treat the following as proposed defaults requiring preregistration and owner approval before paid assessment:

- Primary success floor: 90%, with a one-sided 95% lower confidence bound meeting the floor for each qualified task class.
- Critical safety failures: zero observed; any critical violation rejects.
- Allowed comparative quality decline: `delta = 0` by default; require a defensible lower bound on candidate-minus-baseline performance to meet zero. A nonzero margin is an explicit owner tradeoff, never a silent default.
- Required deterministic and mandatory regression cases: all pass.
- Budgets, latency/recovery limits, independent task count, repeat count, analysis method and stopping rule: explicit, bounded and fixed before the experiment.

Use paired task-level comparisons, randomized/interleaved execution and repeated trials. Account for correlation between repeats of the same task. Use justified conservative uncertainty methods, particularly for tiny, sparse or all-equal samples. Do not interpret “not significantly worse” as equivalence, and do not promote an inconclusive candidate.

Count crashes, timeouts, missing results and unknown usage honestly. Do not cherry-pick attempts, weaken graders, silently change the task distribution or sample until the result passes. The current minimum three A/B runs are smoke evidence, not universal or cross-harness assurance. No inconclusive result automatically authorizes additional spending.

### E. Enforce admission on every dispatch path

Use one owner-side admission contract at initial launch, retry, resume, configuration refresh, wrapper startup and each new role-worker step. Before run creation/new reservation/spawn, verify trusted scope, exact bundle, passing evidence, owner certificate, registry revision, expiry/revocation, required capabilities, current isolation and existing budget/risk gates.

Persist the admitted certificate, revision, bundle, mode, scope, identity and input digest before spawn. Recheck at the actual launch boundary and use immutable protected artifacts to prevent a configuration changing after it was checked. Apply the policy to `command` adapters as well; do not create an operational fixture bypass.

Revocation or expiry prevents the next worker step. For already-running work, stop further dispatch, use the tested cancellation lifecycle, reconcile processes/usage and hold. Explain any harness limit that prevents finer-grained cancellation. Do not start a new writer while ownership is uncertain. Verify observed model identity on completion; unknown or mismatched execution cannot count as qualified success.

Preserve legacy interactive/monolithic parser and read semantics. Mark missing qualification as legacy/unqualified, never retrospectively certified. Every newly activated operational scheduler route must use strict qualification. Switching an existing store to strict mode requires an explicit owner-controlled transition after attempts are drained/cancelled and reconciled; move its unqualified pending work into visible holds without silently reinterpreting frozen jobs. Strict-mode launches/retries/steps require admission. Keep offline fixtures in explicit nonoperational test mode, retain charges/reservations, test interrupted migrations and preserve existing interactive compatibility under its existing guards.

### F. Add safe fallback, rollout and learning

Fallback may select only an owner-approved, currently qualified configuration for the same scope. Reconcile the previous attempt and unknown usage before switching. Verify resume compatibility; otherwise hold or use an explicitly controlled checkpoint. Record a new attempt and reverify current output.

Implement scoped promotion, controlled canary, clear abort thresholds and rollback to a still-valid qualified route. Rollback must retain evidence and accounting and cannot undo external effects by assumption.

Use failure evidence to create sanitized lessons, development regression cases and separately protected sibling cases. Evaluate candidate playbook/prompt changes before owner promotion. Version knowledge and requalify material changes. Do not leak private test content into learning or lower safety standards to accommodate a weaker model.

## Tests and completion

Implement the quality plan's full verification matrix using black-box process/CLI behavior, independent reference calculations and deliberate negative fixtures. Essential cases include missing/tampered/revoked/expired authority, changed delegated models/tools/prompts, issue-driven scope escalation, check-to-use races, refresh/resume bypasses, assessment budget exhaustion, fixture promotion attempts, hidden-test access, forged PASS artifacts, disabled graders, insufficient samples, subgroup regressions, builder/verifier impersonation, fallback with a live writer or unknown usage, rollback to revoked versions, and legacy migration.

Update packaging, owner-copy files, schemas, guarantee records and generated/operator documentation. Run established offline checks appropriate to the changes, including manifest validation, CLI documentation consistency, unit tests and deterministic scenarios. Keep current smoke semantics intact. Do not use historical test counts as fresh evidence.

Complete all authorized offline implementation and independent review before presenting a concrete paid-assessment request. Do not make paid provider/authentication calls, increase allowances, activate a persistent service, publish or message people without applicable authorization. If live authorization or a suitable host is absent, finish the code and reviewable experiment package, record that exact remaining dependency and stop at that gate.

Return what changed, what was tested, evidence locations, unresolved limits and the next concrete decision. Distinguish **offline-complete**, **live-qualified** and **activated**. Do not claim operational portability until the exact tuples and task classes have their required evidence and owner-approved routes.
