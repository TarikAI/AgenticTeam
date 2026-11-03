# AgenticTeam master implementation resume prompt

Updated 2 November 2026. Copy the complete block into the implementation session. It continues existing work; reading it does not authorize a new paid batch or activate anything. See the [progress review](autonomy-progress-review.md) and [master plan](autonomy-implementation-plan.md).

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

Continue the AgenticTeam autonomy implementation to a safely qualified, durable
role-step team. Deliver the remaining code, meaningful regression tests, migrations,
evidence and a concrete activation package. Reuse the existing implementation; do
not start over or stop at another plan. Limit readiness claims to actual evidence.

READ AND RECONCILE FIRST
Read applicable AGENTS.md/CLAUDE.md, then:
- docs/autonomy-progress-review.md
- docs/autonomy-implementation-plan.md
- docs/supervisor-completion-plan.md
- docs/quality-qualification-plan.md
- docs/durable-core-plan.md
- docs/agent-prompt-improvement-plan.md
Read the implementation checkout's docs/autonomy-implementation-progress.md,
docs/autonomy-progress/{supervisor,quality,durable-core,integration}.md and
contracts in docs/autonomy-contracts/. Inspect runtime, tests, schemas, guarantees,
policies, operator guide, host qualification and authorization/activation packages.

SCOPE AND AUTHORITY
This implementation invocation covers local code/docs and offline checks under the
current user's rules. It does not itself authorize new model calls, spending,
credentials, elevated host changes, service registration, external messages/polling,
publishing or production actions. Reuse exact existing authorization; do not ask
twice. Sizing or host-setup permission is not blanket assessment/activation authority.
Finish independent work and prepare a concrete packet before asking for missing
approval. Never read .env variants or owner token files, print secrets, weaken
permissions/guards, relax safety/quality gates or remove a refusal to make tests pass.

ONE INTEGRATION RECORD
Update the existing integration-owner record with dated corrections, current heads,
merged/unmerged state, ownership, contracts and evidence. Correct stale 'wiring not
started', 'S4 pending' and no-host/no-model claims by scope; retain historical results.
Do not repeat inconsistent test arithmetic. Keep G26-G28 supervisor, G29 admission,
G30-G32 core, with actual limitations. Parallelize disjoint work with one runtime owner.

PRIORITY 1: EXECUTION AND ADMISSION BEFORE MODEL ROLE STEPS
R01: Preserve COMMAND_EXECUTOR and step_executor now installed by the wrapper. Verify
explicit/implicit checks and their children actually stay contained, especially on timeout
and cancellation. Add safe regressions with dummy owner sentinels for residual gaps. Every candidate
code path, including implicit completion checks and indirect test imports, must run
inside the approved worker/grader boundary. Trusted broker code validates requests
and imports authenticated receipts; it must not run project commands with owner
filesystem/environment authority. Removing shell=True alone is insufficient. Preserve
command time/output bounds, cancellation, artifact identity and usage accounting.

R02: Preserve admission for credential-bearing generic routes and close the remaining
credential-less arbitrary-command fixture exemption through enforceable confinement. Fixture
mode must be enforceably scratch-only/nonoperational, with no model credentials or
network and no path to operational results. Command wrappers/children cannot become
a bypass. Operational generic adapters need the same capability/quality admission.

R03: Preserve expanded observation and verify the remaining effective bundle fields;
hold missing model identifiers instead of treating an empty reported set as success. Include resolved/auxiliary/delegated models, harness/adapter/parser/
launcher, tools/permissions, prompts/skills/policy, context/knowledge and boundary/image/
environment. Recheck at spawn and later steps; test tampering every material field.
Unknown identity holds or receives an explicit limited policy, never inherited approval.

R04: Preserve active watch_authority and complete direct role-step/container
revocation/expiry/invalidation tests with bounded detection and stop latency. Detect invalid
authority, safely stop, retain reservation/lease until reconciliation, reject late
results and hold. Test revoke/expire mid-attempt and restart during reconciliation.
Future-dispatch checks alone are insufficient.

R05: Keep container role-steps refused until real-engine endpoint confinement, peer
binding and owner-store/process isolation are proven. Same-UID Linux peer identity
is not strong isolation. Test per-dispatch mounts, trusted owner-copy identity, foreign
peer/replay refusal, lost wrapper, cancel and no second writer. Preserve explicit legacy
mode and fixture-only Windows IPC; never enable merely by deleting the refusal.

PRIORITY 2: COMPLETE EXISTING TEAM AND QUALITY PATHS
R06: Implement receipt-bound supervised assessment and a protected container/VM grader.
No candidate code receives registry/owner credentials. Trials bind authentic dispatch,
principal and receipt to exact source/artifacts/bundle and known reconciled usage.
The direct sizing adapter and local-process fixture grader cannot issue certificates.
Bootstrap assessment is an explicitly authorized experiment, never an operational bypass.

R07: Freeze and consume complete role/task/acceptance/source/context packets. Include
canonical prompts and needed inputs; do not read mutable BRIEF as authority after a
snapshot. Candidate lessons are not approved knowledge. Preserve approved provenance;
reject stale/missing/tampered inputs; test recovery, truncation and post-snapshot edits.

R08: Finish all six duties: delivery-lead, context-engineer, qa-lead, eval-engineer,
security-engineer and sre-engineer. Four advisory obligations currently display without
dispatch. Add bounded owner-configured triggers/dependencies, idempotent wake-ups,
budgets and no-recursion/no-progress holds. Every attempt needs a principal, reservation,
lease and receipt. Builders/product/architecture/review/release specialists remain on
demand. Builder children cannot become independent QA by changing their role name.
Step-complete continues the job without failure retry consumption or whole-job success.
Preserve paused/reconciled legacy migration and one writer per checkout.

R09: Preserve integrated evaluated lesson promotion, verify revocation semantics and
finish reference-aware retention. Preserve evidence needed by active jobs, certificates,
incidents or rollback. Models cannot silently promote lessons or loosen policy.

R10: Align COMMAND_RULE, skills and actual permitted tools/working directory. Replace
any remaining unsupported examples with a genuinely supported narrow method; the
known PowerShell Out-File contradiction has already been removed. Share environment policy across live smoke/measurement where applicable.
Use offline denied-tool tests before authorized live adherence measurement.
Apply the prompt-improvement plan across the shared contract, role specialties,
generated execution-mode/authority instructions and immutable task packet. Keep
legacy and broker-mediated examples distinct. Native children cannot self-declare
independent QA; repository content cannot grant authority. Version all changed
instructions in the effective bundle and qualify them, rather than merely testing text.

PRIORITY 3: VERIFY ONE FINAL CANDIDATE
Run focused before/after regressions, schema checks, manifest validation, generated
docs, scenarios, skills preflight, installed/owner-copy packaging and one coherent
full suite. Cover crash/replay/impersonation, stale verdict/context, unknown cost,
budget exhaustion, cancellation, registry corruption, revoked/expired qualification,
forbidden fixture use and migration. Historical sibling tests are not current evidence.
Get independent review; close release-blocking findings and rerun affected checks.
Record exact candidate revisions, commands, results, skips and remaining limitations.

Complete harmless remaining S4 drills under actual host authorization: disposable
systemd service, engine restart, supervisor restart, scheduled dummy-credential
reference, supported logoff/reboot, role-step transport and cancellation. The prior
whole-worker boundary does not prove broker transport. Refresh proof after material
code changes. Report unsupported cases. No paid call hidden in this phase.

PRIORITY 4: AUTHORIZED QUALIFICATION AND COMPLETE ROLE-STEP PILOT
Prepare exact host/image/project/store, full effective bundle and task classes,
secret references, protected dataset/graders, trial count/repeated-case rules,
absolute floor/comparative thresholds, per-attempt/run/aggregate allowance, deadline,
expiry and stop criteria. Follow the detailed plan's predeclared statistics and
inconclusive rules. Reconcile previous usage/authority before any call, including auth
smoke. If scope is missing, present this packet and wait for the dependent action.

Assess the first baseline against protected absolute floors, independently grade it,
and run a complete supervised role-step job with real independent QA/final delivery.
A build-only sizing result is not a pilot; one happy pilot is not full task-class
qualification. Record pass/fail/inconclusive. No automatic extra trials, larger budget,
weaker checks or unqualified fallback. Reconcile auxiliary-model and failed-attempt
usage. Only owner promotion changes routes. A second model/harness needs its own evidence.

PRIORITY 5: NARROW ACTIVATION AND CONTROLLED IMPROVEMENT
Prepare service files, triggers/task classes, qualified route, schedule, account,
secret references, limits, health/hold status, retention, stop/recovery and rollback.
Register only within actual activation authority. Read back registration; verify
allowed/refused jobs, restart/stop and accounting. External notifications need their
own destination scope; stay quiet on unchanged state. No earlier qualified route
means rollback to paused intake/no dispatch after active-work reconciliation.
Requalify material changes; promote lessons after protected evaluation and owner
approval with reversible versions. Never silently lower the quality floor.

DONE AND REPORT
Deliver code and evidence for all authorized scope. Distinguish implemented, offline-
verified, host-verified, live-measured, qualified and activated. If authority/host
capability is missing, finish independent work and deliver the exact pending package;
do not claim readiness. Report candidate refs, changes, tests actually run, open IDs,
six-duty status, qualified task classes, pilot/service state, usage, stop/rollback and
next owner decision. Link progress. Never promise best output or universal non-degradation.

ON RESUME
Read current code/diffs, redacted owner-side job status, authorization and evidence.
Reconcile prior workers/usage; never duplicate an uncertain writer or paid trial because
context was lost. Continue at the earliest unsatisfied gate.
```
