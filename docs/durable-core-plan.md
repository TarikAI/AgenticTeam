# Six persistent core responsibilities

Prepared 1 November 2026 against the baseline named in [the autonomy implementation plan](autonomy-implementation-plan.md). This document specifies future implementation. It does not establish that the core has been implemented, pilot-verified, or activated.

The target is six persistent responsibilities, one deterministic owner-side supervisor, and fresh bounded role executions. Identity, pending work, approved knowledge and evidence survive restarts. A model session is disposable. Six permanently running or continuously billing sessions are neither required nor proposed.

## Integration contract

Read these documents together before implementation:

- [Autonomy implementation plan](autonomy-implementation-plan.md): program order, shared invariants and authorization boundaries.
- [Supervisor completion plan](supervisor-completion-plan.md): isolation, environment filtering, process ownership, metering, recovery and host activation.
- [Quality qualification plan](quality-qualification-plan.md): capability evidence, protected evaluations, qualified configuration identities, admission and promotion.
- [Durable-core implementation prompt](durable-core-prompt.md): a copy-ready execution brief for this workstream.

The plans share runtime files. Assign one integration owner for the supervisor, state CLI, policy, schemas and generated documentation. Parallelize read-only investigation and isolated tests; do not run competing edits or pilots against one checkout.

Every interface, field, command and new file proposed below is a design target, not an existing API. Resolve its exact spelling with the other workstreams in the implementation progress record before writing code. The quality workstream owns qualification records and decisions; the durable core consumes that contract rather than creating a second qualification database.

## What exists and what is missing

The source catalog has 50 roles and matching prompt files in `team.json` and `agents/`. The catalog's 13 harness targets are compiler targets, not 13 qualified supervisor adapters. The supervisor currently has `claude` and `command` adapters. Its documented status is offline-verified, without a verified paid pilot or registered host service.

Existing useful foundations include:

- One worker per checkout, durable attempt intent before launch, budget reservations, wrapper ownership, restart reconciliation and owner-side audit.
- A shared task graph, stage gates, path claims, leases, typed evidence, contribution history and revision-specific verification.
- Context packs and provenance rules, role playbooks, candidate lessons and human promotion.
- Canonical access classes, model tiers, risk rules and conditional specialist routing.

The missing core is not another collection of personas. It is authenticated role dispatch, bounded role-step completion, persistent responsibility obligations, trusted handoffs, and admission of only qualified execution configurations.

Current code anchors to recheck before edits:

| Existing seam | Location | Limitation or extension |
| --- | --- | --- |
| Role catalog and model tiers | `team.json` | Definitions are reusable; no persistent execution identity is declared. |
| Preset validation | `scripts/agentic_team.py`, `preset_problems` | A build needs QA and Code Reviewer coverage; six core roles alone are not a valid delivery roster. |
| Task claim | `scripts/agentic_team.py`, `claim_task` | Role identity comes from the caller's `--agent` string. |
| Historical contribution | `scripts/agentic_team.py`, `task_builders`, `note_contributor` | Preserves role names across task lifecycle changes; add authenticated principal history without removing these checks. |
| Verdict validation | `scripts/agentic_team.py`, `verdict_problems` | `Verifier:` identifies a role, not an authenticated process or fresh session. |
| Launch and reconciliation | `scripts/agentic_supervisor.py`, `launch`, `reconcile`, `classify` | One attempt currently drives a whole run. |
| Worker instructions | `scripts/agentic_supervisor.py`, `worker_prompt` | Tells the worker to continue until the run is complete or held. |
| Job configuration | `scripts/agentic_supervisor.py`, `new_job` | Freezes job settings; extend with execution mode and qualification references. |
| Final acceptance | `scripts/agentic_supervisor.py`, `completion_problems` | Keep owner-side full-run checks separate from step acceptance. |
| Trusted packaging | `scripts/agentic_supervisor.py`, `OWNER_COPY_FILES` | New trusted modules must be packaged and fingerprinted outside the writable checkout. |
| Knowledge | `scripts/agentic_team.py`, `learn`, `promote_check` | Reuse the candidate/promotion lifecycle; add versioned provenance and protected verification. |

## The six responsibilities

These are existing role IDs with persistent duties. They do not gain broader permissions through persistence.

| Role | Durable duty | Invoke judgment when | Required result | Must never do |
| --- | --- | --- | --- | --- |
| `delivery-lead` | Preserve the accepted goal, task dependencies, ownership and next action. | A request needs decomposition, a dependency changes, or a blocker needs a bounded plan. | Valid task graph change, readiness evidence, dispatch proposal or escalation. | Approve human gates, broaden scope silently, certify its own implementation. |
| `context-engineer` | Preserve attributable context, packet versions and knowledge references. | Sources are too large, stale or ambiguous; a fresh session cannot orient. | Bounded snapshot with source hashes, omissions and freshness. | Rewrite accepted requirements, copy untrusted instructions into memory, self-promote lessons. |
| `qa-lead` | Preserve independent acceptance evidence and unresolved defects. | A candidate is ready for verification or remediation changes the candidate. | Authenticated verdict tied to the exact candidate and check evidence. | Build or remediate what it verifies; reuse a stale verdict. |
| `eval-engineer` | Preserve baselines, evaluation results and qualification proposals. | A model, harness, adapter, prompt, toolset or AI behavior changes, or drift is detected. | Protected evaluation result: pass, fail or inconclusive, with configuration identity. | Change protected thresholds after results, qualify its own promotion, expose holdout answers to workers. |
| `security-engineer` | Preserve risk findings, boundary assumptions and unresolved exceptions. | A change crosses a sensitive boundary or a security control needs interpretation. | Evidence-backed findings, required controls and explicit residual risks. | Grant credentials, bypass policy, weaken isolation, approve its own exception. |
| `sre-engineer` | Preserve incidents, recovery position and service health evidence. | A stall, repeated failure or recovery event needs diagnosis beyond deterministic checks. | Diagnosis and bounded recovery proposal or verified runbook evidence. | Restart an uncertain writer, clear a hold, expand spend or invent process ownership proof. |

Deterministic checks handle event polling, dependency readiness, ordinary packet assembly, heartbeat age, budget admission and known policy matches. They do not need six model calls on every tick. A quiet system should stay quiet and cheap.

## Required on-demand roles

Keep a valid existing build preset or an explicitly validated expanded roster. Add a separate responsibility set that references the six IDs; do not introduce a six-role-only build preset or count the supervisor as a seventh LLM agent.

| Work | Additional ownership that remains necessary |
| --- | --- |
| Idea and product definition | CEO, Product Manager, CTO, and UX/UI Designer when the experience matters. |
| Implementation | Fullstack Engineer or the appropriate frontend, backend, database, integration, mobile, data or AI implementer. |
| Independent code review | Code Reviewer; QA is not a substitute for this review. |
| Release and rollback | Release Manager or DevOps Engineer for the declared rollback rehearsal and release mechanics. Human approval remains required where policy says so. |
| Existing complex system | System Mapper before broad changes; Build Integrator when parallel worktrees are introduced separately. |
| Domain risks | Existing privacy, accessibility, compliance, fraud, performance and other conditional specialists. |

Missing required coverage is an admission error with a concrete remediation. It is not permission to let a core role impersonate a missing specialist. Scope-specific role demand comes from the task graph and specialist signals, not from a promise that all 50 must run.

## Execution and authority architecture

Use a single owner-side control plane. Its responsibilities are deterministic: accept triggers, maintain obligation state, select an eligible step, bind identity, admit a qualified route, reserve cost, launch, reconcile, accept receipts and expose actionable status. It neither invents product decisions nor grants human authority.

The worker boundary contains the working checkout, a read-only decision/context view, a limited writable home and only the credentials explicitly authorized for that attempt. The owner store, signing material, protected evaluations, trusted runtime and qualification promotion path stay outside it. Boundary proof and environment policy come from the supervisor completion workstream.

The normal flow is:

1. Ingest a trigger as untrusted request data and identify its durable source key.
2. Derive or update obligations without duplicating the task graph.
3. Select a ready role step and freeze its task, input snapshot and requested output contract.
4. Ask the qualification subsystem to admit the exact execution configuration for its task class and risk.
5. Validate identity, isolation, policy, budget, checkout ownership and source state.
6. Persist dispatch intent and reservation before launching one fresh role execution.
7. Accept only requests and receipts authorized for that execution principal.
8. Reconcile the process tree, usage and evidence before accepting the step or choosing another one.
9. Continue the same job on verified step completion; use the existing full-run checks to decide final job completion.

No fallback, retry, changed role name or new session may expand autonomy. The existing R3/R4 human gates, stricter local policy, run budget, checkpoint decisions and release conditions remain in force.

## Proposed records and schema locations

Use versioned JSON contracts and the existing durable-write discipline. A small new module may own each concern, but do not create a second uncoordinated writer for run state.

| Proposed source file | Purpose |
| --- | --- |
| `config/durable-core.json` | Default responsibility set, event rules and bounded scheduling policy referencing canonical roles. |
| `schemas/durable-core.schema.json` | Responsibility definitions and persistent obligation projection. |
| `schemas/dispatch.schema.json` | Immutable dispatch, execution principal and allowed-operation contract. |
| `schemas/step-receipt.schema.json` | Trusted step acceptance record and evidence references. |
| `schemas/context-snapshot.schema.json` | Input provenance, hashes, omission list, retention class and scope. |
| `scripts/agentic_dispatch.py` | Proposed bounded-step scheduling helpers; no independent approval authority. |
| `scripts/agentic_broker.py` | Proposed owner-side request validation and receipt creation. |

These names are provisional integration choices. Prefer a small implementation over a new orchestration framework. Use standard-library facilities unless a justified dependency is approved under the existing policy.

Authoritative control records belong in the existing protected supervisor store. Proposed additions are `responsibilities.json`, `dispatches/<dispatch-id>.json`, `receipts/<dispatch-id>.json` and `contexts/<snapshot-id>/`. A project-side status page is a projection, never an authority source. The existing project task graph remains the task graph.

### Responsibility and obligation record

Required fields: schema version, role ID, enabled state, configuration revision, trigger rules, allowed duty kinds, memory references, and an event cursor for each source. A cursor binds `{run_uid, sequence, event_hash}`; a bare increasing number is insufficient across runs.

An obligation includes its ID, source event, role, duty kind, relevant run/task IDs, dependency references, status, due/expiry policy, attempt references and terminal reason. Suggested states are `pending`, `eligible`, `dispatched`, `satisfied`, `held` and `superseded`. They do not replace the run task states or human checkpoints.

Use a stable idempotency key derived from source identity, event hash, responsibility ID and trigger-policy revision. Event-cursor advancement and obligation/outbox insertion must be one durable transition, or a journaled transition recoverable without loss. A retry of intake must not create another paid obligation. Own-output events must not recursively wake a responsibility indefinitely.

### Dispatch record

Freeze at least:

- Dispatch, job, run and task IDs; execution mode; responsibility/role ID; distinct execution principal; step kind; parent dispatch when relevant.
- Expected source revision and relevant artifact hashes; owned/output paths; immutable context snapshot ID; exact prompt and canonical role revision hashes.
- Permitted broker operations; action/target/risk; policy and decision-view fingerprints; expiry and claim generation.
- Adapter identity/version; harness identity/version; requested and observed model identity; tool and isolation capability fingerprints; qualification ID and digest.
- Per-step USD/token/time limits where supported, reservation, run/aggregate ceiling references, retry counters and deadlines.
- Required evidence and step acceptance predicates; expected continuation; cancellation generation.

Do not include secret values. Record credential references or allowed variable names only. Observed identity cannot be fabricated from a requested alias. When the provider cannot reveal a stable underlying model version, qualification must state that limitation and use the quality plan's freshness/drift policy.

### Receipt and accepted state

A receipt is produced by the trusted side after validation. Include dispatch/principal identity, observed launch and termination identity, accepted operation sequence, input/output hashes, evidence references, source revision, usage provenance, stop reason, qualification reference, acceptance decision and timestamp. Bind its integrity to the protected owner-side ledger or equivalent trusted record.

Worker-authored prose, JSON or a process exit code is a submission, not an authenticated receipt. Missing, conflicting, stale or replayed submissions are rejected or held. Never accept a receipt twice or meter it twice after a restart.

## Identity and broker requirements

The present role-name checks are useful but do not authenticate an actor. A worker can supply another installed role ID. Fixing this requires a boundary; adding an `agent_id` field or signed file that an editable local CLI chooses to trust is insufficient.

The proposed broker is the only path by which a strong-mode worker earns accepted state transitions or verification evidence. It runs from the protected owner copy and exposes a narrowly scoped local transport. Bind the caller to the launched process tree using a reviewed OS-supported mechanism, such as a per-attempt restricted IPC endpoint and process credentials. Validate this on the chosen host. An environment variable alone is not authentication.

Each fresh process tree receives one execution principal bound to one role and dispatch. Its descendants inherit that identity. Native subagents do not become independent reviewers by adopting different labels; a separate authenticated role requires a separate supervisor dispatch after reconciliation.

The broker must:

1. Validate dispatch existence, freshness, caller binding, operation sequence, claim generation and cancellation state.
2. Derive role and scope from trusted dispatch state; ignore or verify any caller-provided role name.
3. Allow only the operations and paths required by that role step. Delivery can propose/record its authorized task-graph changes, not claim a builder or verifier identity.
4. Apply the canonical runtime's existing risk, gate, ownership, evidence and budget checks without adding an alternate approval path.
5. Invoke trusted runtime code outside the writable checkout and create trusted receipts for accepted operations.
6. Preserve contributor identity across failure, reassignment, reopening and session replacement.
7. Deny unknown operations and human-only actions. Human credentials and promotion authority never pass to workers.

Initially, serialize strong-mode mutations through this broker and the existing run lock. Worker-readable state may remain in the project bus, but a worker-edited projection cannot satisfy trusted acceptance. Define how broker-accepted history is replayed or compared during owner audit; otherwise direct edits could still counterfeit completion.

For QA, independent identity requires a fresh session with no prior authoring/remediation contribution to the candidate, protected inputs and an exact candidate fingerprint. Same model is permitted only if qualified; same role label is not proof of independence. Avoid passing the builder's private reasoning to the verifier. Pass the specification, diff, artifacts and reproduced evidence needed for review.

## Role step versus complete job

Keep the existing monolithic execution mode as an explicit compatibility mode. Introduce an opt-in `role-steps` mode with an owner-validated outcome contract.

| Proposed step outcome | Meaning | Next action |
| --- | --- | --- |
| `step-complete` | This dispatch's acceptance predicates passed and its receipt is trusted. | Continue the same job; do not consume failure retry budget. |
| `needs-human` | A canonical checkpoint or unresolved authority decision blocks progress. | Preserve hold, reservation rules and next owner action. |
| `retryable-failure` | An allowed transient failure occurred; old processes and usage are reconciled. | Retry only within step, task, run and aggregate limits. |
| `terminal-failure` | Repeated failure, exhausted retry allowance, invalid evidence or a terminal task condition. | Hold or fail according to existing policy; no automatic reopen. |
| `cancelled` | Cancellation was requested and owned processes have been proven stopped. | Reconcile cost and claims before releasing the checkout. |

The outcome vocabulary must be integrated with existing states rather than overloading `done`. Full job completion still requires the run's verification, release, learning, signed decisions, metering and source integrity checks. A hundred successful steps do not make an incomplete job complete.

Do not charge a successful role handoff as a worker failure. Conversely, do not allow an endless chain of successful but non-progressing steps: enforce a run step ceiling, meaningful state/evidence progress, bounded orchestration turns and a repeated-no-progress hold. Record these proposed bounds as owner-configurable policy before the pilot.

## Budgets, retries and ordering

Every role step reserves its maximum admitted cost before launch, including planning, context, review and evaluation steps. Count subprocess/provider usage under the same attempt when the harness reports it; unknown usage preserves the reservation and holds further paid work. Do not call a local or command adapter free without an explicit accounting classification.

Apply four independent limits: step attempt, task retry, run allowance and supervisor aggregate allowance. Replacing a role, harness or model must not reset any of them. Qualification assessments have their own explicitly authorized experiment budgets and remain separate from operational work.

Successful step completion allows a new reservation only after prior process ownership and metering are reconciled. A retry uses a new dispatch/attempt ID linked to the prior one and a fresh identity; it preserves the logical task's failure history. Keep the current repeated-failure rule and owner-only reopen.

Use task dependency order and deterministic priority rules. Prioritize pending safety/authority holds and required verification before optional improvements. Never allow health polling or optional learning to starve delivery, nor let delivery skip mandatory review to meet a deadline. Preserve one worker per checkout throughout the initial version.

## Context snapshots and memory

Create a read-only snapshot for each dispatch from the task envelope, accepted requirements, stage contract, canonical role prompt, permitted protocols and relevant approved knowledge. Use the existing packet budget as the starting point; record omissions and required follow-up reads. Context Engineer judgment is needed for difficult summarization, not every packet assembly.

A snapshot manifest records source paths/identities, source hashes or immutable Git revisions, capture time, scope, author, trust classification, omissions, required facts, and the task/dispatch allowed to consume it. Freeze the actual packet bytes. A path to an editable file alone is not an immutable snapshot. The worker's output directory is separate.

Before dispatch, compare required sources to the snapshot. A changed requirement, policy, prompt or relevant source invalidates the snapshot; regenerate or hold. Never silently compress away a safety condition, unresolved decision or acceptance criterion. When a summary disagrees with an authoritative source, the source wins and the discrepancy is recorded.

Scope memory by project, role and purpose. Reuse `knowledge/lessons.md`, role playbooks and proposal records rather than creating six unreviewed memory stores. Candidate observations are labeled, attributable and non-authoritative. Approved checks may guide behavior but cannot change permissions or override the accepted task. Cross-project reuse requires sanitization and explicit promotion under the existing evolution process.

Retention must be part of the deployment configuration: distinguish immutable manifests/hashes, required acceptance evidence, input packets and raw transcripts. Preserve records needed by active jobs, holds, unsettled usage, disputes, qualification validity and rollback. Pruning never removes the only reproducible source for an accepted verdict. Raw content gets a declared retention period and access policy; no indefinite transcript collection by default. A privacy deletion request may require invalidating dependent evidence or qualification rather than pretending retained hashes still reproduce deleted material.

Never snapshot `.env` variants, credential files, owner tokens, secrets or unnecessary personal/customer data. Record exclusion rules and verify them. External issues, web pages, tool output and other agents' submissions remain untrusted data in snapshots and lessons. Do not copy their instructions verbatim into an authoritative playbook.

## Quality admission dependency

Operational dispatch must ask the quality subsystem to validate the exact route/configuration fingerprint for the step's task class, role duty, risk and required capabilities. Admission rejects missing, expired, revoked or mismatched qualification, insufficient isolation, unknown required capability and unapproved fallback.

The first configuration cannot require a previously qualified baseline. Use the quality plan's explicitly authorized, isolated assessment mode against protected absolute criteria. Assessment authorization is bounded to its experiment project, configurations, task set, trial counts, budgets and expiry; it cannot unlock operational dispatch or promote itself.

Freeze admitted configuration identity in the dispatch. Recheck revocation and material configuration drift before launch and before accepting a result. Define how an in-flight revocation stops or quarantines the result without losing cost/process ownership. A result may be kept as experimental evidence while being refused for operational completion.

Fallback selects only a route already qualified for the same required capability and workload. Record why it changed, preserve task and spend history, and start a fresh bounded step. If no admitted alternative exists, hold. A compiler emitter, model size, brand name or high reasoning setting is not quality evidence.

## Migration and backward compatibility

Version the supervisor store, dispatch records and strong-mode run extensions explicitly. Older code must refuse unsupported writable state rather than silently ignoring new authority fields.

Migration is owner-side, recorded and recoverable. First quiesce intake and reconcile all live attempts, reservations and claims. Back up the store and binding metadata without exposing credentials. Refuse migration while process ownership or usage is unknown. Do not abandon locks or rewrite current records to appear terminal.

Preserve legacy interactive and monolithic parser/read semantics. Do not convert an active attempt into several role steps. Existing role-name contribution history remains useful but is labeled legacy/self-declared; migration cannot manufacture authenticated historical principals. Require a fresh strong-mode verification step before claiming the stronger guarantee.

Compatibility does not exempt an activated operational scheduler from qualification. Move a store into strict admission only after draining and reconciling existing attempts; then hold queued monolithic or role-step work whose exact configuration lacks qualification. Do not grandfather old jobs or issue certificates to keep fixtures passing. Keep an explicit nonoperational fake-adapter test mode for deterministic offline fixtures, with evidence labeled accordingly. Historical records stay readable even when their old configuration is no longer admitted to execute.

Prefer enabling role steps for a new run after old jobs finish. When resuming an old incomplete run is necessary, define an explicit import/revalidation path: preserve all history, holds and budget totals; bind current source and artifacts; revalidate mandatory evidence; and never auto-approve a checkpoint. A separate migration test must prove that path before use.

Reinstall/uninstall must preserve knowledge and protected control state by default. Add all trusted new modules, schemas and policy versions to owner-copy packaging and integrity checks. Rollback to older software is allowed only when it understands the current store or restores an idle compatible backup; never point old code at incompatible active state.

## Delivery phases and acceptance gates

Follow the master program's sequencing. These are the durable-core work packages, not permission to run a paid experiment or register a service.

### D0 Baseline and shared contracts

Record the source revision, current test outcomes, existing working-tree changes, proposed schemas, step vocabulary, broker trust boundary and ownership of shared files. Confirm supervisor safety fixes and qualification interfaces before dependent work. Keep guide and unrelated changes intact.

Gate: reviewed contracts and migration strategy exist in the integration progress record; no runtime changes are claimed as live evidence.

### D1 Durable obligations and snapshots

Implement responsibility references, event cursors/outbox, bounded obligations and immutable context manifests. Use fake events and fixtures; no model calls.

Gate: duplicate/reordered/replayed events, crash windows, stale sources and malformed snapshots are handled deterministically. Restart resumes the same pending work without duplication. The canonical roster count and valid preset coverage remain correct.

### D2 Trusted identity and broker

Implement protected owner-side operation validation, role-bound principals and receipts. Integrate with canonical runtime gates and owner-copy packaging. Keep strong mode disabled until the selected host's identity/isolation boundary is proven.

Gate: role spoofing, expired grants, replayed operations, direct state edits, modified checkout runtime, cross-role calls and forged receipts cannot earn trusted acceptance. A builder and its children cannot submit authenticated QA verification.

### D3 Role-sized scheduling and recovery

Implement step selection, reservation, launch, receipt acceptance, handoff, no-progress detection and process/usage reconciliation. Preserve monolithic fixtures and semantics.

Gate: successful intermediate steps continue the job without consuming failure retries; zero exit with missing step evidence fails acceptance; completion of a step never marks the full job done. Existing one-writer, metering, gate and cancellation invariants still pass.

### D4 Six duty rules and qualified admission

Connect the six duty rules, on-demand role coverage, stale-context recovery, evidence-based QA, evaluation triggers, security review and reliability diagnosis. Consume the quality workstream's registry and admission API.

Gate: operational dispatch cannot start without current matching qualification. Fake adapters cover absent capabilities, revocation, fallback, role coverage and changing configurations. Idle ticks invoke no model. Assessment mode remains restricted and distinct from operational work.

### D5 Knowledge, observability and migration

Add sanitized status, role-step metrics, incident/lesson provenance, retention, schema migration, compatibility and documented rollback. Status distinguishes installed roles, enabled responsibilities, queued obligations, active executions and verified durable support.

Gate: active/held evidence survives pruning and reinstall; old jobs are not silently reinterpreted; knowledge candidates cannot self-promote; status never exposes secrets or claims a model is continuously awake.

### D6 Isolated qualification and pilot

Use the supervisor and quality plans' authorized live procedure after all offline gates pass. The pilot must exercise the new role-step mode, fresh verifier identity, restart, cancellation, a required hold and at least one meaningful recovery. A pilot of the old monolithic worker does not certify this dispatcher.

Gate: independent owner-side evidence supports the exact tested configuration and task classes; usage reconciles; safety and quality thresholds pass. Failed or inconclusive results remain unqualified. Service activation is a later concrete owner decision under the master plan.

## Acceptance matrix

| Area | Required failure or recovery test |
| --- | --- |
| Event durability | Crash between obligation and cursor writes; duplicate source IDs; altered payload under the same ID; unknown run cursor. |
| Writer exclusion | Two supervisors/ticks compete; old wrapper starts late; previous writer outlives wrapper; reboot with uncertain identity. |
| Role identity | Builder supplies `qa-lead`; child process claims another role; copied/expired dispatch; forged receipt; altered checkout CLI. |
| Independence | QA contributed before reassignment/reopen; QA remediates source; verdict references old HEAD or uncommitted changes. |
| Step outcomes | Exit zero without output; valid step with incomplete run; repeated no-progress steps; malformed continuation. |
| Accounting | Crash after reservation, after receipt and during metering; missing/NaN/unknown cost; changed model tries to reset allowance. |
| Qualification | Missing/expired/revoked record; tuple mismatch; weak adapter; stale proof; unqualified fallback; first-baseline assessment cannot operate. |
| Context | Requirement or prompt changes after snapshot; omitted safety dependency; mutable file reference; cross-project memory contamination. |
| Knowledge | Poisoned external instructions; duplicate lesson; unsupported `proven` label; candidate changes a permission; invalid promotion. |
| Stop and recovery | Pause drains as documented; cancel proves tree stopped; uncertain stop preserves lock/reservation; restart resumes exact pending obligation. |
| Migration | Live attempt blocks migration; legacy evidence stays labeled; compatible reinstall preserves state; old binary refuses new schema. |
| Retention | Prune cannot remove active/held/unsettled or required qualification evidence; raw sensitive content is excluded. |

Extend existing `tests/test_supervisor.py`, `tests/test_authority.py`, `tests/test_evidence.py`, `tests/test_orchestration.py`, `tests/test_harness.py`, `tests/test_evals.py`, `tests/test_release.py` and packaging tests. Add focused tests for broker authentication, dispatch contracts, snapshots and migration. Keep deterministic offline fixtures separate from real-model and real-boundary evidence.

## Completion and honest limits

Offline completion means implemented contracts, green relevant regression checks, demonstrated negative cases, reviewed migration and accurate operator documentation. It does not mean qualified or activated.

Operational completion additionally requires the supervisor safety gates, matching live quality qualification, a role-step pilot, independent review and explicit activation authorization for the concrete service scope. Record evidence and unresolved limits in `docs/autonomy-implementation-progress.md`.

The six-role design is a practical initial control structure, not a universal minimum. Persistence preserves work; qualification restricts admissible configurations; verification checks each result. These mechanisms reduce regressions and recover from failure. They cannot guarantee the best answer from every model or prove that all future tasks will succeed.
