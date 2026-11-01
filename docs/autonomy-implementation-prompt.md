# AgenticTeam master implementation prompt

Copy the block below into a capable coding harness with the AgenticTeam repository open. The focused prompts linked in the plan can also be used for one workstream at a time. This prompt directs implementation; creating or reading this file does not itself run the implementation or authorize paid work.

```text
Implement the AgenticTeam autonomy program in this repository. Take the existing
offline-verified supervisor to a correctly bounded, evidence-tested system with
quality qualification and six durable core responsibilities. Deliver working code,
tests, migrations, documentation and a concrete activation package; do not stop at
another plan. Complete authorized work and keep status truthful at live/owner gates.

READ FIRST
Read applicable AGENTS.md/CLAUDE.md instructions and these files in order:
1. docs/autonomy-implementation-plan.md
2. docs/supervisor-completion-plan.md
3. docs/quality-qualification-plan.md
4. docs/durable-core-plan.md
5. docs/supervisor-operator-guide.md, docs/pilot-plan.md, docs/pilot-prompts.md,
   protocols/harness-security.md, protocols/team-evaluation.md,
   protocols/evolution.md, config/guarantees.json and config/policies.json.
Then inspect the actual implementation and tests referenced by those plans.
The new plans identify corrections to older pilot recipes. Reconfirm every gap in
the current code; skip already-fixed items with evidence. Never execute an old
recipe that contradicts the safety/authorization requirements of this task.
If a required plan is absent, locate it before proceeding; do not invent its contents.

SCOPE AND AUTHORITY
This invocation authorizes the local implementation and offline checks described
by the plans, subject to the user's and harness's applicable rules. It does not by
itself authorize paid model calls, spending, credential provisioning, elevated host
changes, external messages, remote GitHub polling, publishing, production actions,
push/merge, or service registration. Reuse explicit authorization already present
in the conversation when it covers the exact action; do not ask for it twice.
Before a missing paid or activation authorization, finish all independent local
work and present the exact reviewable setup, limits, checks and stop criteria.
No secret values in chat, files, process arguments or logs. Do not read .env files
or owner token files. Use the approved secret mechanism and owner-side operations.
Never weaken a guard, permission prompt, hard human gate or isolation boundary.

WORKING METHOD
Inspect git status and preserve all existing work, including the team guide and
README changes. Reuse a suitable checkout; use the codex/ branch prefix if a new
branch is needed. Do not discard indexes, user changes or historical run records.
Create docs/autonomy-implementation-progress.md with baseline revision, current
behavior, evidence, phases, owners, unresolved decisions and next safe action.
One integration owner controls shared runtime/schema/policy files. Parallelize
read-only audits and disjoint edits when safe, but never launch two writers in the
same active pilot checkout or run overlapping full test suites unnecessarily.
Reproduce confirmed defects with meaningful regression tests before fixing them.
Do not create tests that only echo implementation details or silently update
golden snapshots to make failures disappear.

IMPLEMENTATION ORDER
A. Baseline and contracts.
   Record the actual host/tool versions without exposing credentials. Inspect the
   current manifest, supervisor, state CLI, tests, schemas and generated docs.
   Agree the shared identity, job/step outcome, qualification and evidence contracts
   before editing cross-cutting code. Mark proposed interfaces as proposed until
   implemented. Preserve existing exit-code and legacy read/migration contracts.

B. Supervisor safety and pilot readiness.
   Implement every confirmed correction in supervisor-completion-plan.md: positive
   boundary controls; explicit consistent environments including help preflight;
   Linux namespace/mount proof; paid-auth separation; separate fake and real stores;
   correct no-active-run checks; drain versus cancellation; whole process/container
   termination; lifecycle-safe scheduling; bounded usage/recovery and safe recipes.
   Do not call a marker-only mocked probe a verified OS boundary. Do not claim
   pause or the serve-loop deadline has stopped a running worker unless verified.

C. Quality qualification.
   Implement the protected versioned evidence/qualification registry and owner-only
   promotion path. Evaluate the complete model+harness+tools+prompts+policy+context+
   boundary configuration for explicit task classes, not a model display name.
   Add fail-closed operational admission at enqueue/launch as applicable, immediately
   before process spawn, on resume/config refresh and every new role attempt.
   Missing, unknown, mismatched, expired or revoked qualification must hold work.
   Keep schema/config changes, results and qualification status auditable.
   Run untrusted candidate code only in a separate grading sandbox without owner
   credentials. Keep holdouts/graders/thresholds outside the candidate's write access.
   Provide a tightly scoped owner-authorized assessment mode for the first baseline
   and candidates; it cannot admit operational jobs or mark itself qualified.
   Do not promise guaranteed best quality. Fail/inconclusive is a valid outcome.

D. Durable core.
   Implement persistent responsibility records for delivery-lead, context-engineer,
   qa-lead, eval-engineer, security-engineer and sre-engineer. Keep one deterministic
   owner-side supervisor, not six immortal model sessions. Preserve required on-demand
   Product Manager, CTO, builders, Code Reviewer, Release Manager and specialists.
   Bind authoritative claims/results to owner-launched role attempts through the
   trusted identity/broker contract. A self-declared agent or Verifier string is not
   authentication. An untrusted subagent result can be advisory, not an authenticated
   independent verdict. Enforce fresh reviewer identity and immutable source snapshot.
   Add a verified role-step completion outcome distinct from whole-job completion;
   successful continuation must not consume failure retries. Every step still owns
   a budget reservation, bounded attempt, transcript/evidence record and safe lease.
   Preserve the single-writer checkout rule and explicit legacy monolithic mode.
   Persist context/provenance/freshness and promote only evaluated approved lessons.

E. Offline validation and independent review.
   Exercise each focused plan's acceptance matrix with fake adapters and harmless
   fixtures. Include crash windows, replay, impersonation, stale verification,
   context truncation, denied tools, missing cost, exhausted budgets, corruption,
   cancellation, container children, stale qualifications and promotion tampering.
   Run the repository's manifest validation, generated-doc check, relevant focused
   tests, full unit suite, scenario suite and skills preflight from repository root.
   Keep outputs and verdicts. Run real-host boundary/lifecycle checks when an
   authorized capable host exists. Do not silently install elevated services.
   Have an independent reviewer verify the implementation and evidence. Fix material
   findings, repeat affected checks, and update docs/guarantee ledger honestly.

F. Authorized assessment and live pilot.
   Prepare the exact scratch project, provider/model and harness version, frozen
   configuration digest, credential reference, test-set version, trial count,
   per-attempt/run/aggregate budgets, deadline, expiry and stop rules. If matching
   authorization is missing, present it and wait before paid work. The first paid
   authentication check also requires coverage and counts toward the budget.
   Freeze metrics and grading thresholds before results. Keep fake-worker evidence
   separate. Qualify the first pair against absolute floors, then compare candidates
   against the same baseline/task distribution with repeated trials and uncertainty.
   Run the live supervisor pilot for the actual new execution mode. Keep the
   existing smoke eval's human-release-gate outcome distinct from unattended pilot
   completion. Meter/reconcile provider usage, audit decisions, independently run
   acceptance checks in the grading boundary and record pass/fail/inconclusive.
   No unapproved extra trials, retry batches, automatic budget increase or fallback.

G. Controlled activation and improvement.
   Prepare exact service files and the approved task/trigger scope; use a qualified
   configuration. Present schedule, limits, owner account, secret references, stop,
   recovery, local status, retention and rollback. Register only when the owner's
   activation authorization covers it. Verify registration, an allowed run, a refused
   run, restart behavior, stopping and accounting. External notifications need their
   own authorized recipient/destination. Do not notify on unchanged status by default.
   Add observation->lesson->evaluation->proposal->human promotion->changelog handling.
   Requalify material changes and retain a tested qualified fallback. If first
   activation has no earlier qualified route, rollback to paused/no dispatch after
   reconciling active work; never substitute an unqualified configuration. Never silently
   relax thresholds, replace the baseline or self-promote a new model/lesson.

DONE MEANS
All offline acceptance cases pass; documentation and migrations match the actual
interfaces; independent review has no unresolved release-blocking finding; and
any claimed live/activated state has configuration-specific authorized evidence.
If paid approval, host access or activation permission is absent, complete and
deliver the offline implementation plus the concrete pending package. Report the
dependency exactly; do not call the system live-verified or activated.

FINAL REPORT
State what changed, files/commits, tests actually run, remaining risks, which
model+harness+task classes are qualified, which identities are durably dispatched,
pilot and service status, actual usage versus ceilings, how to stop/rollback, and
the next required owner decision. Link the progress record. Avoid perfect-quality
claims and distinguish inferred safety from tested enforcement.

ON RESUME
Read the progress record, working-tree changes, owner-side job/attempt status and
existing authorizations. Reconcile them before doing anything. Never relaunch while
the previous writer may still act. Evidence, frozen configuration and live state
override an optimistic progress note. Continue at the earliest unsatisfied gate;
do not repeat paid work just because context was lost.
```
