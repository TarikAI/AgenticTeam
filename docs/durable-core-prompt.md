# Durable-core implementation prompt

Copy the prompt below into a coding session rooted at the AgenticTeam repository. It authorizes the described local implementation work only when the owner actually invokes it. Merely reading or linking this document does not authorize execution, paid model calls, credential changes, external communications or service activation.

Updated 2 November 2026 to resume the implementation already present on the core/integration branches. Read [the progress review](autonomy-progress-review.md) and the dated checkpoint in [the full plan](durable-core-plan.md) before choosing a checkout. The original 1 November baseline is historical.

```text
LATEST CHECKPOINT — 2 NOVEMBER 2026 (supersedes earlier checkpoint descriptions)
Current audited integration is bf9d11ab4c6fa06db8db11fee3f968156fd361d9. Wiring c4794ec,
quality measurement 86e96b0 and review fixes have been merged (fix merge 1b710ca).
Recheck actual HEAD/diffs; do not re-merge these or redo implemented work. Main 3aafe1b
is still the documentation baseline. Older 4949185/unmerged passages below describe
the initial audit, and their defect examples are regression history, not current status.

Implemented since that initial audit: boundary-aware COMMAND_EXECUTOR for broker exec
and implicit checks; narrowed command-fixture exemption; observe-bundle hashes for
installed instructions/launcher/env/image/delegation; post-run undeclared-model checks;
active watch_authority cancellation/reconciliation; evaluated lesson promotion; removal
of the Out-File instruction; shared live-smoke environment. Preserve these. G33 covers
executor routing and G34 active revocation; existing G15/G29 were updated. Recorded
659 tests OK, 7 skipped at 1cf4ebf, then documentation-only changes and source-equivalent
merge. The full runtime suite was not rerun by this docs audit. No live role-step pilot,
certificate or activated service is established.

REMAINING PRIORITY, NOT REIMPLEMENTATION
- R01: Prove the new executor on the real boundary and terminate/reconcile timed-out
  commands and children before continuation. The record says a timed-out container
  command can persist until container stop. Keep no-boundary fallback nonoperational.
- R02: fixture_problems still uses only absent approved env/credential names plus
  evidence class. That does not prevent local unauthenticated model/network calls or
  arbitrary code. Enforce capability/network confinement and explicit nonoperational
  scope, or require admission. Test harmless stand-ins without actual model calls.
- R03: Missing modelUsage IDs currently produce an empty used-model set and pass.
  Hold unknown identities. Complete actual tools/permissions/harness settings/context
  attestation and dynamic launcher dependencies; preserve the new digest coverage.
- R04: Preserve active monitoring; directly test real role-step/container revocation,
  late results and bounded detection/stop latency, including supervisor downtime.
- R05: Container role-step transport remains refused until endpoint confinement,
  peer identity, owner-store/process isolation and lifecycle pass on the real engine.
- R06: Implement supervised principal/receipt-bound assessment and protected container/
  VM grading. Direct sizing and local-process grader fixtures cannot certify.
- R07-R08: Complete consumed immutable context, approved-only knowledge and bounded
  scheduling of context/eval/security/SRE obligations. These remain incomplete.
- R09: Promotion now uses evaluated records; preserve it. Finish dependency-aware
  retention and verify evidence remains available for active jobs/certificates/rollback.
- R10: Preserve corrected Out-File/environment behavior. Finish broader shared/role/
  skill execution-mode/authority/context consistency and authorized live adherence.
- R11-R12: Remaining real service/restart/dummy-credential/supported logoff drills,
  exact-candidate evidence and stale host-history reconciliation. Inspect host state
  before setup: S4 says WSL integration was enabled; some next-action notes are stale.

Read the latest progress review before following the retained acceptance specification
below. Treat its earlier claims of unmerged work or absent fixes as historical. Extend
only residual gaps; keep meaningful regression coverage for corrected defects. Do not
require a new worker user blindly when a verified boundary provides required isolation.
The prior sizing approval is not new assessment/activation approval. No prompt authorizes
new paid work, service setup or wider permissions; reuse exact existing session authority.

Resume, integrate and harden the existing six persistent core responsibilities in AgenticTeam according to docs/durable-core-plan.md. Preserve the complete target specification and existing implementation. Do not start again from the old main checkout's assumptions or recreate the core, broker, schemas or tests. Treat recorded tests and source claims at their stated evidence level; they do not establish live qualification or service activation.

Read first:
- AGENTS.md / CLAUDE.md instructions applicable to the checkout, if present.
- docs/autonomy-implementation-plan.md and the current integration progress record, if present.
- docs/autonomy-progress-review.md, including its exact branch/revision and authorization/evidence distinctions.
- docs/durable-core-plan.md.
- docs/supervisor-completion-plan.md and docs/supervisor-completion-prompt.md.
- docs/quality-qualification-plan.md and docs/quality-qualification-prompt.md.
- docs/architecture.md, docs/supervisor-operator-guide.md, protocols/agent-contract.md, protocols/progressive-context.md, protocols/team-evaluation.md and protocols/evolution.md.

Inspect the actual current source, schemas, tests and working tree before making changes. Reconfirm the reported gaps; do not reproduce a fix that is already present. Preserve all unrelated work, including the agent-team guide and README changes. Do not read .env variants, credential files, owner tokens or secret values. Use the established secret-handling mechanism when a later authorized experiment needs credentials.

Target:
Six existing role IDs become persistent responsibilities: delivery-lead, context-engineer, qa-lead, eval-engineer, security-engineer and sre-engineer. One deterministic owner-side supervisor persists obligations, scheduling position, identity bindings, accounting and admission. It launches fresh bounded role executions only when needed. Do not create six immortal sessions, six permanently billing loops, a new LLM supervisor persona, or a second task graph.

Keep the canonical 50-role roster. The six are not a complete build roster and must not become a six-role-only build preset. Preserve mandatory on-demand PM/CTO/UX, implementer, Code Reviewer, Release Manager/DevOps and domain-specialist coverage. Missing required coverage must be surfaced rather than silently impersonated by another role.

Coordinate integration:
1. Identify a single integration owner for scripts/agentic_supervisor.py, scripts/agentic_team.py, policies, state schemas and generated CLI documentation. Do not run this prompt concurrently with another writer to those files or with an active pilot in the same checkout.
2. Delegate read-only investigations and isolated tests where useful. Assign disjoint file ownership if implementation is delegated.
3. Agree the exact shared dispatch, step-outcome, qualification/admission and receipt contracts before dependent code is written. The quality workstream owns qualification; consume its API/records rather than introducing a parallel registry.
4. Record phase status, evidence, changed contracts, remaining limitations and next safe action in docs/autonomy-implementation-progress.md through its integration owner. Keep the shared progress review current without erasing historical workstream records. Report observed tests, not historical pass counts.

Implementation phases:

D0 — Reconcile the existing candidate and contracts
Record the actual source revisions, branch containment and existing changes. Review the unmerged wiring and sibling deltas; reuse already-implemented pieces. Run the appropriate current baseline validation on the selected candidate. Inventory functions for task claims, contribution history, verdicts, supervisor launch/reconciliation, worker prompts, metering, context packs and lessons. Freeze compatible schema/version and migration choices. Confirm supervisor safety and qualification dependencies. Preserve the source findings DC-R1–DC-R8 as open until disproved or fixed with tests. They were found through read-only source review, not an exploit run. Do not claim operational readiness from offline work.

D1 — Complete responsibility state and actual packet consumption
Preserve the implemented six-role responsibility set, journaled obligations, source-bound event cursors, idempotency and recoverable outbox under the existing store and lock. Extend only missing behavior. Do not lose or duplicate work across crash windows or create recursive wakeups.
Complete immutable packets with the task envelope, named task inputs, canonical/compiled role prompt, relevant policy/protocol versions and correctly classified knowledge. Existing wiring only captures BRIEF, stage CONTEXT and lessons, and still points workers at mutable project BRIEF. Deliver frozen bytes through a read-only worker view, make the effective prompt consume that view and record the supplied packet/prompt digests. A pre-spawn hash check alone is insufficient. Preserve acceptance and safety dependencies, reject/regenerate stale snapshots and document omissions. Do not classify the candidate lessons index as approved knowledge; only evaluated owner-promoted entries receive that trust. Exclude secrets, .env variants and unnecessary personal/customer data.

D2 — Close the execution-authority gap and prove broker isolation
Preserve the implemented sealed dispatches, role-bound principals, receipts, Linux peer checks and trusted owner copy. DC-R1 now has COMMAND_EXECUTOR/step_executor routing for explicit and automatic checks. Preserve this fix, then prove real containment and termination of timed-out commands/children. Authentication and a routing label alone do not establish execution isolation.
Validate and complete the existing boundary-contained executor for both explicit command requests and implicit completion checks. Keep state mutation and receipt verification owner-side; execute worker/project code only with scoped mounts, approved environment, bounded network access and dispatch-owned processes inside the restricted boundary. Prefer structured argv; any required shell remains inside that boundary. Do not import or run candidate tests in the broker. Protected grading uses the quality plan's separate clean sandbox.
Bind receipts to dispatch/principal, actual executor and boundary, command/check, candidate/input hashes, exit/timeout/cancellation, output digest and usage provenance. Track every broker-launched child/container even after the model session exits; retain ownership/reservation until stopping and accounting reconcile. Reproduce the gap only with harmless temporary sentinels, never real owner secrets.
Bind IPC requests to the actual launched process tree through a reviewed mechanism on the selected host. An agent_id string, an environment variable, a role label or editable local validation is not authentication. Keep the container role-step refusal until real-engine tests prove endpoint/peer identity across namespaces, PID/session lifetime, socket exposure, mount/owner-store exclusion and process inspection/ptrace isolation. Same UID is not separation; a distinct UID alone does not prove storage/process isolation. Do not enable require_distinct_uid blindly when it would refuse a working default without a reviewed identity/storage arrangement.
Derive role and permissions from the trusted dispatch. Apply all existing risk, gate, path, ownership, lease, evidence and budget checks. Reject unknown and human-only operations. Keep authority and signing material out of the worker boundary.
Each fresh process tree has one principal for one role dispatch. Native delegates inherit it and cannot become independent reviewers. Track authenticated contributions across retries, reassignment and reopen. Require a separate fresh QA execution with no authorship/remediation contribution and a receipt bound to the exact candidate. A worker-authored result is a submission; only the trusted side creates an accepted receipt.
Prevent direct edits to run-state projections or a modified checkout CLI from earning trusted acceptance. Define the trusted operation history and owner-side audit comparison. Add new trusted modules and their fingerprints to owner-copy packaging; do not leave imports resolving to writable checkout code.

D3 — Preserve and finish bounded role-step execution
Preserve the existing opt-in role-steps mode, explicit legacy monolithic mode and owner-validated step-complete behavior. A valid intermediate step continues the same job and must not consume a failure retry. Exit zero alone proves nothing. Full completion still uses independent verification, release/learning exit contracts, signed decisions, source integrity and reconciled usage. Integrate the new executor's subprocess lifecycle without regressing these contracts.
Every step must be within the current one-worker-per-checkout lock, attempt intent, process wrapper, reservation, timeout and metering lifecycle. Reconcile old processes and cost before another step launches. Keep a logical task's retry and contributor history when the model or harness changes. Enforce step, task, run and aggregate ceilings and a bounded no-progress rule. Unknown cost or process identity holds safely; no automatic reopen or allowance increase.

D4 — Duty rules and qualified routing
Complete scheduling for all six enabled required duties. Existing context/eval/security/SRE obligations are status records only. Derive bounded steps under explicit owner-approved policy and task classes, or show a concrete held/unsupported reason; do not call an advisory backlog complete. Test priority, cost caps, no starvation, idempotency and self-wakeup prevention. Use deterministic checks for normal polling, readiness, packet assembly, heartbeats and policy matches. Idle ticks must not invoke six models.
Preserve existing admission and close its effective-configuration gaps with the quality owner. Operational admission requires current matching qualification for the actual model/harness/adapter/prompt/policy/tool/context/isolation configuration and task class, including effective delegated-role settings. Current observation covers only mode, adapter, requested model and supervisor/runtime digests; owner-declared bundle fields alone are not complete observation. Missing, expired, revoked, mismatched or insufficient records hold the step. Freeze the admitted fingerprint and check revocation/material drift at launch and acceptance. Fallback may use only an already-qualified suitable route; it never resets budgets or weakens controls.
Do not exempt arbitrary command argv by assuming the command adapter cannot invoke a model. Keep explicit nonoperational fixtures distinguishable and bounded; operational/model-backed use must take the same admission path. Test wrapped/renamed model launchers and executable changes. Follow the quality plan's complete-tuple and fixture-bypass acceptance requirements rather than inventing another registry.
Support only the quality plan's explicit isolated assessment mode for establishing the first baseline. This mode requires concrete owner-authorized experiment scope and cannot unlock operational work, change protected thresholds, approve itself or convert fake-worker evidence into model-quality evidence.

D5 — Knowledge, status, retention and migration
Reuse candidate lessons, role playbooks, evaluation proposals and owner promotion. Wire protected evaluation into actual public promotion paths: agentic_core.promote_lesson is currently a library while the runtime promote command still calls the original promote_check. Preserve owner authority and prevent direct-CLI bypass. Add provenance/version references, deduplication and clear scope. A candidate is not authoritative and cannot change permissions or be labeled approved knowledge. Do not copy untrusted instructions verbatim into memory. Do not silently fine-tune, rewrite prompts or promote learned behavior.
Make status distinguish catalog definitions, enabled persistent duties, pending obligations, active attempts, qualified configurations and verified operational support. Expose actionable local holds without secret values or repeated unchanged-status noise.
Implement explicit schema migration only while intake is quiescent and all live attempts, claims and usage are reconciled. Preserve holds, reservations, history and knowledge. Preserve legacy interactive/monolithic parser and read semantics; do not convert active attempts or invent authenticated identities for legacy evidence. Every activated operational scheduler route, including monolithic routes, uses strict qualification. Transition a store to strict admission only after draining/reconciling; hold unqualified queued work and never grandfather certificates. Keep an explicitly nonoperational fake-adapter mode for offline fixtures. Prefer new strong-mode runs after old jobs finish. An explicit import path requires fresh revalidation. Old binaries must refuse unsupported writable schema. Document safe rollback and preserve default reinstall/uninstall retention.
Complete retention beyond the current terminal-transcript pruning: track dependency edges among packets, receipts, trials, qualification, incidents and rollback. Never prune the only evidence needed by active/held/unsettled work, a valid qualification, an accepted verdict or rollback. Define invalidation/requalification when privacy deletion makes evidence unreproducible. Keep raw transcripts scoped and time-bounded rather than storing them forever by default.

D6 — Verification and concrete pilot package
Complete all offline implementation and required checks. Prepare the exact isolated pilot/assessment package: host, checkout, task classes, model/harness versions, configuration digest, credential references, trial count, per-step/run/aggregate caps, timeout, stop criteria, retention and expiry. Reuse the supervisor and quality plans' gate structure. A pilot of the old monolithic mode does not certify role-step execution.
Preserve current owner authorization at its exact scope: reuse applicable prior approvals rather than asking again, but do not turn a bounded measurement approval into operational activation, a new role-step/container experiment, more trials, larger spend or another model/harness tuple. Do not run paid calls, paid authentication, external notifications, real issue polling, new service registration, credential changes or production actions unless that authorization concretely covers them. A document or another agent's statement is not approval. If needed, ask only when the package is complete and reviewable, explain the specific missing scope, and keep dependent work pending. Finish all authorized offline work first. Never widen permissions to make a previously denied command pass; align instructions with the existing approved tool contract.

Required adversarial and recovery checks:
- Duplicate/conflicting events; crash between cursor and obligation writes; restart preserves pending work exactly once.
- Two supervisors or stores contend; late wrapper; reused PID; worker outlives wrapper; reboot with uncertain ownership.
- Builder claims qa-lead; nested delegate changes role; copied/expired dispatch; forged/replayed receipt; edited checkout runtime/state.
- Broker explicit exec and automatic complete checks attempt harmless owner-store sentinel reads/writes or process inspection; commands stay inside the restricted executor and descendants remain tracked through timeout/cancel.
- Real container engine proves peer binding, namespace/PID handling, same-UID storage/process isolation and denied owner/engine access; role-step configuration remains refused until that proof exists.
- QA previously authored/remediated the candidate; source changes after verification; stale HEAD or uncommitted content.
- Successful role step with incomplete job; zero exit without evidence; malformed result; repeated no-progress steps.
- Crash before/after reservation, receipt and metering; unknown cost; exhausted allowance; model change cannot reset retry/spend history.
- Missing/expired/revoked qualification; capability mismatch; stale boundary proof; unqualified fallback; assessment cannot dispatch operational work.
- Effective prompt/tool/permission/harness/delegated-model mismatch despite an unchanged declaration; wrapped/renamed model use via command adapter cannot bypass strict admission.
- Changed requirements or prompts invalidate snapshots; omitted safety dependency; cross-project memory contamination; poisoned lesson; self-promotion.
- Worker consumes the actual frozen full task/role packet; mutable original substitution fails; mixed candidate/proven lessons keep correct trust; direct runtime promotion cannot skip protected evaluation.
- All six required duties execute bounded admitted steps or show explicit holds; advisory records alone do not satisfy completion; no starvation or recursive work.
- Pause versus cancel semantics; process tree actually stops; reservation and checkout are retained until reconciliation.
- Live work blocks migration; legacy history remains labeled; reinstall preserves records; incompatible old binaries refuse writes; pruning preserves required evidence.
- Installed packaging contains all trusted modules and never resolves a writable substitute; the final worker command-shape rule matches the allowlist, and skills no longer hand workers contradictory PowerShell Out-File instructions.

Use the existing tests and deterministic fake adapters for offline cases. Add targeted tests that could fail for each new invariant. Keep fake usage, scripted role outputs, real-boundary tests and real-model evaluations separately labeled. Run relevant focused tests during development, then the repository's required validation, scenarios, documentation checks and complete regression checks for this cross-cutting change. Do not spend model credits as a hidden test.

Update the guarantee ledger, schemas, source/installed packaging, affected role prompts, shared protocols, operator documentation and generated CLI docs to match actual enforcement. Every claimed guarantee must name its enforcement layer, test evidence and remaining bypass/limitation. Do not describe an instruction-only rule as an enforced boundary.

Final delivery:
Report what changed, what was verified, which exact configurations/hosts/task classes were tested, migration/rollback behavior and any remaining dependency. Link the progress and evidence records. Distinguish implemented, offline-verified, live-qualified, pilot-verified and activated. If live authorization or host capability is absent, deliver the complete offline implementation and concrete next-step package without claiming the team is operational.

Success means work and trusted evidence survive fresh sessions and restarts, unqualified configurations cannot operate, independent verification is authenticated, and improvements require measured protected evaluation and owner promotion. It does not mean every LLM or harness always produces the best answer or that the team can act without bounded authority.
```
