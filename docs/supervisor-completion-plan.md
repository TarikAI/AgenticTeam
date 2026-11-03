# Supervisor completion plan

## Latest verified checkpoint — 2 November 2026

**Integration advanced during this review to `bf9d11ab4c6fa06db8db11fee3f968156fd361d9` (`autonomy-integration`).** The wiring `c4794ec`, quality measurement `86e96b0` and review-fixes branch are now merged. `main` remains `3aafe1b` plus these documentation edits. This checkpoint supersedes the earlier `4949185` / unmerged status below; retain that earlier pass only as historical evidence. Recheck current HEAD before implementation; do not reset or re-merge work already incorporated.

The review-fixes record reports **659 tests OK, 7 skipped** at `1cf4ebf`, followed by a documentation-only commit and merge `1b710ca` with the same source tree. The integration owner recorded manifest/docs/scenario/preflight checks on the merge. Later `72ef067`/`bf9d11a` clarify promotion documentation. This review inspected the new source and records; it did not rerun that full runtime suite. No new live role-step pilot, qualification or service activation is recorded.

| Correction | Latest implementation | Remaining acceptance |
| --- | --- | --- |
| R01 | `step_executor` now routes explicit and completion checks through container/prefix execution; records boundary; owner-side git hooks/fsmonitor are constrained. | Real boundary proof for these new execution paths, guaranteed termination of timed-out commands/children before continuing, and no-boundary fallback confined to genuine nonoperational fixtures. Fake-boundary tests prove routing/environment, not OS containment. |
| R02 | Credential/approved-environment-bearing command adapters now require admission; offline-rehearsal refuses those names. | The residual fixture exemption still checks only environment/credential names and evidence class. Arbitrary argv can reach local unauthenticated models or other network/services without such names. Enforce fixture capabilities/network and nonoperational scope; do not equate “no credentials passed” with “cannot call a model.” |
| R03 | Installed prompt/skill/policy, launcher, environment/image and delegation digests are observed; undeclared models reported in `modelUsage` hold results. | Missing model IDs currently yield an empty set and pass this check. Hold unknown model evidence. Complete actual tool schemas/permissions, harness version/settings/context identity and dynamically loaded launcher code coverage. A post-run reported subset is not complete pre-run attestation. |
| R04 | `watch_authority` rechecks admitted attempts each tick, records withdrawal, stops and reconciles; revoked outcomes cannot advance. | Preserve this implementation; prove actual role-step/container revocation, late-result refusal and bounded detection/stop latency, including supervisor downtime. Do not rebuild the monitor. |
| R05 | Container role-step refusal remains. | Endpoint-confined transport and real-engine negative identity/lifecycle tests. Same-UID process binding alone is not isolation. |
| R06 | Direct live sizing adapter exists. | Supervised principal/receipt-bound assessment and protected container/VM grading; first certificate-quality trials. |
| R07–R08 | Earlier snapshot/obligation wiring remains. | Complete frozen context actually consumed, approved-only knowledge, and bounded scheduling for the four currently advisory duties. |
| R09 | Runtime promotion now requires an evaluation record and invokes `promote_lesson`; G15 updated. | Preserve and verify the promotion path; dependency-aware retention is still open. Do not label all R09 complete merely because promotion is wired. |
| R10 | Conflicting `Out-File` advice is removed; live smoke uses shared environment policy. | Live command-rule adherence and broader shared/role/skill mode/context/authority consistency from the prompt-improvement plan. |
| R11–R12 | Merge/status/contract reconciliation has advanced; G33 executor and G34 active revocation were added. | Remaining real service/restart/dummy-credential/supported logoff drills, source-specific qualification and a few stale host/history statements. |

Source: current integration `docs/autonomy-progress/review-fixes.md` and `docs/autonomy-implementation-progress.md`; `scripts/agentic_supervisor.py` (`step_executor`, `observed_bundle`, `fixture_problems`, `transcript_models`, `watch_authority`), runtime executor/promotion hooks, updated skill and live-smoke files. Residual findings above are source review, not exploit demonstrations. The record itself notes that timed-out container commands can continue until the container stops, launcher-loaded external code is not fully digested, missing model IDs pass, and real role-step revocation is not yet directly tested.

**Resume order:** preserve merged fixes; finish residual R01–R04 acceptance alongside R05 transport; implement R06 assessment/grader, R07 context, R08 scheduling and R09 retention; align broader agent instructions; then finish host drills, authorized live qualification/pilot and narrow activation. A distinct worker user is one possible isolation mechanism, not an unconditional extra requirement when a verified boundary provides the required separation. Read actual host state before repeating setup: S4 records WSL integration enabled, while some next-action notes still say to enable it.

Updated 2 November 2026. The original specification was prepared against `f6153d3`; that baseline is **historical**. Main at `3aafe1b` contains these plans but has not incorporated the runtime work below. Resume from reviewed implementation worktrees rather than reimplementing their completed fixes in main.

This plan is the supervisor workstream of [the autonomy implementation plan](autonomy-implementation-plan.md). Use [the companion implementation prompt](supervisor-completion-prompt.md) to execute it. The master plan controls shared contracts, integration order and final readiness. This plan replaces the **execution instructions** in the older [pilot plan](pilot-plan.md) and [pilot prompts](pilot-prompts.md); retain those files as historical context until implementation updates them with a clear supersession notice.

The desired result is bounded, recoverable execution with verified authority, isolation, accounting and stopping behavior. It is not permission to deploy a service, spend money or bypass a human decision. The old proposed budgets and model examples are not authorization. A separate owner-approved cost measurement has been recorded; it is neither a full qualification assessment nor service authorization.

## Checkpoint — 2 November 2026

Read [the current cross-workstream review](autonomy-progress-review.md) before resuming. This checkpoint compares committed source and project progress records; it does not claim fresh tests, access to the private evidence stores or a new live run. Source paths in this section refer to the **pinned checkout named in the table**, not to main's older copy. Recheck HEAD and working-tree changes before acting; other sessions own those worktrees and progress files.

| Pinned source | Checkout relative to the repository root | Recorded state and limits |
| --- | --- | --- |
| Integration `4949185` | `.claude/worktrees/pensive-poincare-5e61a2` | S01–S05 corrections, deadline/cancel semantics, container ownership, fixture separation and generated lifecycle setup are implemented. Ubuntu/WSL2 plus Docker boundary and stubborn-worker drills are recorded as passing; systemd and restart qualification remain incomplete. |
| Wiring `c4794ec` | `.claude/worktrees/autonomy-integration-wiring-8046ea` | Includes the integration safety changes plus admission at launch/wrapper/resume/role steps, installed owner-copy modules, brokered role steps and context checks. Recorded offline results include 632 tests with 6 skipped and Linux role-step/process-binding coverage. Container role-step transport is explicitly refused. The command-rule prompt correction is not live-retested. |
| Quality `86e96b0` | `.claude/worktrees/autonomy-quality-registry-22bb47` | Records separately owner-approved cost measurements and improved token aggregation. A direct whole-run worker built a small fix but stopped at verification because tool calls were denied. This unisolated measurement is sizing evidence, not certification, a complete job or qualification of role steps. |

The selected qualification target is **role-steps**. Whole-run remains compatibility behavior; do not substitute it to get around a role-step refusal. No qualified role-step certificate or activated service is established by these records. The three SHAs are separate snapshots, not one tested combined release. Workstream records contain stale earlier statements and next actions; reconcile them with their owners rather than overwriting files owned by another active session.

| Area | Current classification | Required next action |
| --- | --- | --- |
| S01–S05 | Implemented with offline regressions; supported-host boundary partly verified | Retain the fixes. Revalidate after material integration changes and extend their contract to every new execution path. |
| S06–S08 | Stop/ownership/service generation implemented; host coverage incomplete | Finish the actual service-manager, engine/supervisor restart and supported logoff/reboot drills. |
| S09–S12 | Safer recipes, separate fixtures and accounting labels implemented; assessment/activation packets remain proposals | Preserve separate evidence classes and approval scope. Apply sandboxing to broker-triggered checks as well as graders. |
| S13 | Role-step/admission wiring offline-verified; full live qualification pending | Close the priority blockers below, qualify the selected transport, then prepare a scoped assessment. |

### Priority blockers before further paid use

1. **Owner-side command execution through the broker.** At wiring `c4794ec`, `scripts/agentic_broker.py:306` calls `TeamRuntime.exec` through `team.exec_command(..., shell=True)`; `:310` calls `complete_task`, which can execute project checks. `scripts/agentic_team.py:2841` starts the command in the project with no explicit sanitized environment or OS boundary. `scripts/agentic_supervisor.py:781`–`:810` constructs that runtime in the owner-side wrapper. Authenticated role identity and command-risk rules do not sandbox project code. Route every worker-requested command and completion check through a verified least-privilege executor; retain trusted state/receipts in the owner broker. Do not merely strip one secret or trust a command's spelling.
2. **Command-adapter admission bypass.** Wiring `scripts/agentic_supervisor.py:1756` returns `not-applicable` for every non-Claude adapter, assuming a configured arbitrary command is a no-model fixture. Synthetic labeling does not prevent a command from invoking a model or network. Restrict the exemption to enforceably offline, owner-defined fixtures with no provider credentials or unauthorized egress, or subject executable adapters to the applicable admission contract. Refuse unknown classifications; do not repair this by silently certifying fixture evidence.
3. **Unqualified role-step container transport.** Wiring `scripts/agentic_supervisor.py:3662` refuses this combination pending endpoint confinement and real-engine proof. Keep that refusal until the durable-core owner supplies the transport and its negative tests. Linux process binding and the earlier container isolation drill are distinct evidence; neither establishes the missing combination. A separately qualified Linux prefix boundary is an option only if it meets the same role-step and owner-isolation requirements.
4. **Execution-path and prompt consistency.** Align `evals/live_smoke.py` and other live launchers with the controlled environment and boundary policy; verify the actual caller, not just a shared helper. Wiring's `COMMAND_RULE` has offline tests but no live retest. `skills/agentic-build/SKILL.md` still suggests PowerShell `Out-File`, contradicting the allowed repo-relative Bash/python/git forms. Correct the recipe and test every emitted prompt/skill without broadening permissions just to pass a measurement.

These are required extensions of S02/S03, S07/S12 and S13, not a reason to redo S01–S05. Quality certificate/evaluator details and core identity/transport details remain assigned to their respective plans and owners.

## Dependencies and scope

The supervisor implementation can be corrected and tested offline before quality qualification and durable-core execution are complete. A specifically authorized, isolated paid assessment can then gather candidate evidence. Scheduled **operational** dispatch must wait for both the [quality qualification](quality-qualification-plan.md) contract and the [durable core](durable-core-plan.md) execution mode to pass their gates.

The initial configuration has no qualified baseline. Assess it against protected absolute acceptance and safety criteria using the master plan's bounded assessment mode. Assessment may only execute the authorized experiment; it must not admit ordinary work, approve itself or promote its own results. A whole-run measurement does not qualify the selected role-step dispatcher. Material runtime, identity, adapter or policy changes require the affected live evidence to be repeated under authorization.

One integration owner controls shared runtime files. Read-only review and tests in separate fixtures can run in parallel. Do not run multiple implementers, prompts or supervisors against the same pilot checkout or owner store.

## Historical gap specification — retain as regression requirements

The table below describes `f6153d3`, not the current worktrees. S01–S05 and much of S06–S12 have since been implemented as summarized above. Keep these required outcomes as acceptance criteria; use the current checkpoint and review to decide what remains. These historical line references are not current implementation locations.

| ID | Observed gap | Source evidence | Required outcome |
| --- | --- | --- | --- |
| S01 | The isolation probe accepts negative markers without proving the intended paths are reachable. Missing paths can look like access denial. Existing tests deliberately substitute missing paths and expect success. | `scripts/agentic_supervisor.py:2387`, `:2397`, `:2411`; `tests/test_supervisor.py:1135`; old Q1-a at `docs/pilot-plan.md:79` | Positive view control, protected owner sentinel, denied view write, successful worker-home write, correct namespace and a structured, successful probe response. Replace the misleading success fixture. |
| S02 | Credential filtering omits Anthropic/Claude prefixes and otherwise copies unrecognized environment variables. The digest does not list approved passthrough names. | `scripts/agentic_supervisor.py:70`, `:2599`, `:2610`; old Q1-b at `docs/pilot-plan.md:80` | Explicit environment policy with a minimal host/platform baseline, approved passthrough names, reserved-variable protection and names-only diagnostics. No credential or interpreter-injection variable passes by accident. |
| S03 | The help preflight inherits the owner's raw environment and working directory; the probe and worker use a different path. | `scripts/agentic_supervisor.py:2573` compared with `:1341`, `:2402` | The same controlled boundary environment and working directory apply to version/help checks, probes and workers. Owner-side trusted operations remain separate. |
| S04 | Host-native absolute paths are passed unchanged. The old Windows/WSL recipe can refer to nonexistent worker paths. | `scripts/agentic_supervisor.py:1450`, `:2401`; old Q1-c at `docs/pilot-plan.md:81` | A declared, verified namespace contract. Start with a supported POSIX host and matching absolute paths. Do not call an incompatible Windows-prefix configuration verified. |
| S05 | The proof digest covers path/configuration strings, not necessarily the current contents or identity of a mutable launcher/image or the proof algorithm version. | `scripts/agentic_supervisor.py:1384` | Versioned proof envelope bound to the actual boundary, launcher/image identity, environment policy and relevant code version; stale or changed proof refuses paid launch. |
| S06 | Pause stops future launches, while outer serve timeout or interruption can leave a detached worker running. Timeout may return zero with work still active. | `scripts/agentic_supervisor.py:2128`, `:2247`, `:2289`; old pilot stop recipe at `docs/pilot-plan.md:180` | Explicit drain versus cancel semantics, truthful deadline outcome and a tested emergency procedure. Do not release ownership or reservations until work is reconciled. |
| S07 | Process ownership records identify the host process/group; a Docker prefix also involves a daemon-managed container. Its lifetime is not explicitly persisted. | `scripts/agentic_supervisor.py:403`, `:533` | Qualify the actual boundary's lifecycle, including stubborn children, cancellation and crash recovery. Persist/reconcile container identity or use a proven lifecycle-aware launcher if host process identity is insufficient. |
| S08 | The generated systemd example is a oneshot tick with detached workers. Exit 2/3 are treated as success, without an alert mechanism. | `scripts/agentic_supervisor.py:2740`, `:2763` | A lifecycle-aware service or managed worker scope, tested under the real service manager, with explicit health/hold handling and secret injection. |
| S09 | The old boundary phase says no spend but runs a paid authentication prompt before paid authorization. It also proposes broad passwordless sudo. | `docs/pilot-plan.md:26`, `:148`, `:152`, `:163`; `docs/pilot-prompts.md:34`, `:164` | Fully offline boundary phase; all paid checks inside explicit experiment authorization. No automatic account/sudoers provisioning or broad privilege grants. |
| S10 | Rehearsal reuses the real pilot project/store. The fake worker writes a different feature and reports synthetic cost. | `docs/pilot-plan.md:131`, `:174`; `tests/fake_worker.py:41`, `:108`, `:162` | Separate rehearsal and paid fixtures, stores, event IDs, accounting and evidence labels. Never promote fake usage or fake acceptance into live evidence. |
| S11 | The fixture asks for successful active-run status before any run exists. | `docs/pilot-plan.md:125`; `scripts/agentic_team.py:1582`, `:5766` | Use installed health/roster/run-list checks; explicitly expect the no-active-run result where appropriate. |
| S12 | The old plan treats a key as having its own hard spend cap, and executes worker-authored tests as the owner. | `docs/pilot-plan.md:21`, `:51`, `:190`, `:217` | Verify the actual provider organization/workspace limit and accounting scope; run acceptance in a clean sandbox without owner credentials. Avoid absolute spend guarantees. |
| S13 | The old pilot proves only a whole-run happy path. | `docs/pilot-plan.md:258`; `scripts/agentic_supervisor.py:2581` | Keep a qualification matrix for recovery, usage, authority, host lifecycle and the actual execution mode. Do not infer operational or cross-harness readiness from one successful task. |

## Phase S0 — Baseline and shared contract

1. Preserve all existing work, including guide and README edits. Use a suitable current checkout; create a `codex/` branch only when needed. Record source SHA, branch, working-tree changes and existing instructions.
2. Read the master, quality and durable-core plans. Agree the admission/assessment interface, qualification digest, identity/result envelope, role-step completion vocabulary and evidence references before changing shared code. Proposed interfaces are specifications until implemented and documented; do not invent commands that the current parser lacks.
3. Read existing supervisor/integration/quality progress records in their owning checkouts. Coordinate reconciliation with those owners; do not overwrite their active files. Update the assigned shared review with S0–S8 status, evidence locations, source SHA, known limits and next action. Keep private transcripts outside the repository.
4. Capture current tests and host facts. Historical test counts are not current results. Pin CI evidence to the tested source SHA, not merely the latest run on main.
5. Reconcile integration `4949185`, wiring `c4794ec` and quality `86e96b0` with current branch heads and dirty work before any edits. Agree the integration base and shared-file owner. Do not merge or run paid work merely because this document names a branch. Preserve completed safety changes, role-step wiring and the command-rule correction.
6. First close the owner-side broker command/check execution path and the command-adapter exemption. Establish negative tests with harmless sentinels and fake credential values before widening any live activity. Complete the remaining transport/environment work with the quality/core owners. The host and paid phases remain gated on these results.

**Gate:** the progress record distinguishes source facts, runtime observations, proposals and authorization. No model call, secret retrieval, account change or host registration occurs.

## Phase S1 — Isolation proof and environment corrections

S01–S05 are implemented in the recorded integration; preserve their regression coverage. The requirements below remain the contract. Implement only confirmed remaining defects, including environment parity for the broker executor, completion checks, live-smoke launcher and evaluator paths:

- The owner writes harmless test artifacts: a nonce-bearing view control and a protected sentinel. These are test data, not credentials. Confirm the sentinel exists on the owner side; do not read real tokens or use owner configuration as a negative-control target.
- The worker probe must establish the expected view identity, deny access to the owner sentinel, deny a write to the existing view, and successfully create/read/remove a scratch file in the worker home. Also confirm the expected checkout and runtime are reachable. A deliberately unmounted owner path may be absent; that alone is insufficient without the positive controls.
- Parse one bounded structured response bound to the nonce/configuration. Require exit zero and every required result. Reject absent paths, wrong nonce, omitted/duplicate fields, malformed output, partial execution, nonzero exit and timeouts. Clean up only the exact harmless files created for this probe, after checking their resolved paths.
- Define an environment allowlist appropriate to each supported host. Deliberately preserve necessary platform variables and explicit, approved passthrough names; block inherited provider credentials, unrelated tokens, interpreter/loader injection and reserved authority variables. Set worker HOME/config/cache locations deliberately. Do not print values or persist them in argv, intent, digests or documentation.
- Use the approved secret mechanism for the dedicated worker credential. Supervisor configuration stores only its reference/name. No `.env` reading, token inspection, credential copying into chat or credential values in command-line arguments.
- Make preflight, probe and worker agree on environment policy and working directory. Add names-only diagnostics for the effective passthrough contract. Keep owner-side metering/auditing on the trusted owner copy.
- Bind proof to schema/algorithm version, canonical paths, owner identity, effective uid/gid, launcher identity, pinned container image digest where applicable, environment-policy version, interpreter/runtime versions and required configuration. Define expiry/revalidation. Existing unversioned proofs cannot silently remain valid.
- Document the initial supported namespace. Prefer matching Linux absolute paths in a reviewed container with only checkout read-write, view read-only and worker home read-write mounts. No owner home, credential directory or container-engine socket mount. No privileged mode. Other boundaries require their own proof and review.
- Replace the broad sudo fallback with a separate, explicit owner/admin setup proposal if a container is unavailable. A future restricted launcher must have fixed validated paths/arguments and controlled environment; do not grant arbitrary commands or embed secrets in argv.

**Gate:** each original failure has a regression that failed before its fix; clean and hostile environment fixtures are covered; invalid/stale boundaries refuse launch. Independent review finds no credential-value exposure. The actual host boundary still requires S4.

### S1 extension — broker execution and adapter classification

- Split trusted state changes from project-code execution. The owner broker validates dispatch/role/claim/expiry and records receipts; a bounded executor runs project commands and all checks triggered by completion inside the verified worker or grader boundary. No owner key, token store, credential directory, host home or engine socket is exposed to that executor. Unknown executor/boundary identity refuses the operation.
- Use one explicit environment policy, controlled cwd, time/output ceilings and owned process/container lifecycle for these commands. Cancellation and stale dispatches stop or refuse work and cannot produce an accepted completion. Check the same generation and content before recording the result; a worker-written log alone is not trusted evidence.
- Test harmless nested commands and imported test code, not only command strings: a valid-looking test runner may execute arbitrary project code. Show the protected sentinel and fake inherited credentials are unavailable, allowed checkout scratch work succeeds, and owner state cannot be changed through a test/check subprocess. Test both broker `exec` and `complete`.
- Define the command adapter's offline exemption by a constrained fixture execution contract. Arbitrary owner-configured argv must not be considered offline solely because `adapter=command`. Test a scripted child attempting a model executable, credential use or network access; it must be refused or contained without a real call. Every executable non-fixture path must undergo admission before reservation/spawn, at wrapper start and on resume/new steps. Do not present a proposed option as an existing CLI interface.

**Gate:** no project-authored code runs with broker/owner authority; fixture selection cannot bypass paid/admission safeguards; independent adversarial tests pass before any further paid worker run.

## Phase S2 — Stopping, process ownership and service lifecycle

The recorded integration already implements explicit unfinished exit code 4, leave/cancel policies, container identity/reconciliation and a long-running service example. Review and extend these paths for broker executors and the selected role-step transport; do not replace them with the historical implementation.

1. Document and test existing semantics: pause is a drain request for future work; cancellation asks the current attempt's wrapper to stop its owned work. A supervisor's own exit does not establish worker termination.
2. Specify the outer deadline result. Either implement an explicit bounded cancellation-and-reconciliation policy or return an unmistakable unfinished/deadline outcome with instructions to stop the owned work. Do not report normal completion while a worker continues. Preserve compatibility intentionally and update tests/docs/guarantees.
3. Define emergency operation: prevent new launches, request cancellation for the exact owned job, observe the exit receipt and actual process/container termination, settle or hold usage, then release claims only when permitted. Never kill by an unverified reusable PID. Unknown termination keeps ownership held; unknown spend retains its reservation.
4. Test the real container launcher. A host Docker client disappearing does not itself prove the container is gone. Persist a container/attempt identity or add an owner-controlled launcher/adapter contract if needed. Verify that late receipts, daemon restart and wrapper crash cannot produce a second writer. Do not use the generic command adapter to evade paid-worker protections.
5. Replace the unqualified oneshot scheduling recipe with a lifecycle-aware design. Prefer a managed long-running supervisor with an explicit stop/reconciliation strategy or separately managed worker scopes. Do not disable process cleanup with `KillMode=none` merely to keep detached workers alive.
6. Prepare local status, stale-heartbeat detection and deduplicated hold/failure events. Notification delivery is a separate authorized destination. Handle all meaningful exit/status classes, including errors, holds and blockers; silence unchanged healthy status. Bound log retention and preserve unsettled evidence.

**Gate:** offline tests prove cancellation, timeout, wrapper/supervisor interruption, late results, restart, unknown usage and no duplicate writer. Generated host setup is still a proposal until S4 tests the service manager and S8 receives activation authorization.

## Phase S3 — Separate rehearsal and pilot fixtures

The integration includes separate fixture generation and evidence labels. Reuse and verify that implementation; create new isolated instances when needed, with distinct names and evidence roots:

| Fixture | Purpose | Accounting and completion |
| --- | --- | --- |
| Offline rehearsal | Scripted workers exercise state, process and accounting failures. | Label every record synthetic/offline. Its mock cost is not provider usage. Its acceptance matches what the fake worker actually implements. |
| Live candidate assessment | A small realistic task with a committed defect and owner-controlled acceptance checks. | Fresh source baseline, no rehearsal commits or synthetic spend. No worker starts before S5 authorization. |

Use temporary task-owned owner homes for offline tests; never point fake-worker tests at the real operational store. Preserve evidence rather than deleting a store or checkout binding to obtain a clean budget. Keep event files outside tracked source when appropriate, and keep the live checkout clean.

For the live fixture, a tiny greeting package with whitespace handling is sufficient for transport/lifecycle assessment; it is not a broad coding-quality benchmark. Include protected acceptance checks outside worker-writable source and record the known failing behavior before work. Installation checks must not require a current run: use a valid installed health/run-list check or explicitly expect the documented no-active-run result.

**Gate:** fixtures and stores cannot collide; rehearsal executes success, timeout/cancel, restart, missing usage, malformed result and human-gate scenarios; synthetic totals are isolated; the paid fixture remains untouched by model work.

## Phase S4 — Offline qualification on the actual host

**Recorded partial pass:** integration `4949185`, `docs/autonomy-progress/supervisor.md`, records Ubuntu 24.04/WSL2 plus Docker 29.9.2, proof-v2 positive/negative controls, cancellation, timeout with unknown-usage hold, and a wrapper/client crash where a surviving container prevented replacement. This was recorded on prior source; it was not rerun for this document update and does not prove brokered container role steps. Do not repeat it merely to obtain a new date; rerun affected checks after relevant source/boundary changes.

**Still required:** authorized disposable systemd lifecycle tests; engine restart; supervisor restart during an active/ambiguous attempt; dummy-credential delivery/missing-credential tests; supported host logoff/reboot and recovery behavior. Record unsupported cases and narrow the supported deployment claim accordingly. Endpoint-confined role-step transport requires its own real-engine tests after implementation. Never remove its current refusal to reuse the older whole-run drill.

Use existing approved infrastructure. If account, privilege, package or host-service setup goes beyond existing authorization, prepare the exact change and have the owner/admin authorize it before applying it. The plan itself grants no such authority.

- Record OS/kernel, Python, git, harness version/help capabilities, runtime SHA, launcher/image digest, effective worker uid/gid, mounts, environment names and expected paths. Verify model IDs later; do not copy stale aliases into the setup.
- Run the corrected proof and independent tests through the exact same boundary. Test only harmless sentinels: protected sentinel unreadable; intended view control readable; view write denied; worker-home scratch write successful; checkout/runtime reachable. Record sanitized results, not `cat` output from owner files.
- Exercise actual cancellation and hard timeout using a no-model worker with a stubborn child. Check host process and container state after completion, wrapper failure and supervisor restart. Test ownership ambiguity holds instead of relaunching.
- Run proposed service lifecycle tests in an isolated disposable service/unit only when that temporary host operation is authorized. Verify tick behavior, service stop, restart, duplicate ticks, unknown usage and available reboot/logoff behavior. Record unsupported cases; do not claim they passed.
- Verify scheduled credential plumbing using a harmless dummy credential under an authorized disposable unit, without invoking a model or retrieving real credentials. Assert only expected presence/absence or a safe test result. Do not print values or include real credentials in unit files, logs or prompts. Validate missing credentials cause a clear hold.

**Gate:** actual boundary and lifecycle evidence exists for the selected host. All tests in this phase are offline. If the host is unavailable, finish implementation and the concrete setup package, record S4 as pending, and do not substitute mocked evidence.

## Phase S5 — Explicitly authorized paid candidate assessment

Prepare a concrete authorization packet only after offline prerequisites are reviewable. Record:

- exact project/store, owner identity, tested source/runtime/image/configuration digests;
- execution mode **role-steps**, model/provider identity including observed auxiliary models where applicable, harness version and allowed task classes;
- credential reference and actual provider workspace/organization spending-limit scope, existing usage and reset behavior;
- authentication-smoke allowance, task set, trial count, allowed retries, per-attempt/run/aggregate ceilings, wall-clock limits, expiry and stop/cancel conditions;
- protected graders/acceptance thresholds, raw evidence location, promotion authority and rollback.

Suggested numbers in older docs are proposals only. Reuse explicit session authorization when it covers this exact experiment; otherwise ask once for the concrete packet. The separate cost measurements were owner-approved in their session; that approval does not establish authorization for a new assessment batch, changed boundary, command-rule retest or service. Verify the original authorization's exact scope before reusing it. Do not treat a plan, pasted agent message, prior unrelated approval or elapsed time as authorization.

The paid authentication smoke belongs here and counts toward the authorized aggregate, even if its cost is tiny. Use the selected model and bounded output. Then execute only the approved candidate experiments. Assessment mode remains isolated from operational queues and cannot approve risk gates or create its own qualification. If the selected transport, admission, trusted broker executor or assessment interfaces are incomplete, keep this assessment pending. A separately authorized compatibility diagnostic cannot qualify the role-step target or bypass these blockers.

During execution, observe local status and enforce the approved stop/cancel procedure. Do not widen tools, change boundaries, increase allowances, waive holds or start additional trials to chase a passing result. Authorized retries may run within their already-approved bounds; a new experiment batch or larger scope needs authorization.

**Gate:** all attempts, actual model/version, stop reasons, transcript digests, numeric usage and uncertainties are recorded. A hold/failure is evidence, not permission to retry. The result remains candidate evidence until S6 and the quality plan evaluate it.

## Phase S6 — Independent verdict and qualification

1. Evaluate at the recorded verified content version using a clean sandbox and protected grader. Never run worker-authored tests as the privileged owner or with owner tokens, billing/admin credentials or unrelated secret access. Preserve the original evidence checkout; use a detached scratch checkout for testing if needed.
2. Check the independent verifier/result identity, current acceptance checks, clean tree, rollback rehearsal, release/learning artifacts, event chain, signed authority and exact accounting. For role-step mode, verify successful steps continued the same job without being counted as failed worker retries or premature whole-job completion.
3. Reconcile provider billing for the dedicated scope/time window with attempt metering, separating authentication and other authorized trials. Declare tolerance before running; account for reporting delay, rounding and scope. A material unexplained mismatch or unknown usage holds qualification.
4. Record pass, fail or inconclusive for each qualification row. One success cannot establish untested retry, unknown-usage, scheduler or new-harness behavior. Feed this evidence into the quality plan's protected qualification and owner promotion path.
5. Fix diagnosed repository defects with regressions. Material changes invalidate affected evidence. Further paid trials require coverage by existing authorization or a new explicit experiment packet.

**Gate:** the actual execution mode/configuration/task classes have independent live evidence and owner-approved qualification. The required durable-core identity and handoff gates pass. No service is yet activated by this verdict.

## Phase S7 — Reviewable operational activation package

Prepare, but do not register, the exact startup/service configuration and operational runbook. Include:

| Topic | Required content |
| --- | --- |
| Scope | One host/checkout first; approved queue sources and task classes; no automatic expansion to repositories or external actions. |
| Admission | Exact qualified configuration and actual durable execution mode; missing, expired, revoked or mismatched qualification blocks dispatch. No silent model fallback. |
| Service | Account, working paths, startup schedule/lifecycle, restart behavior, process/container ownership and maximum active workers. |
| Secrets | Approved opaque references and tested injection; owner credentials unavailable to workers; missing secrets hold safely. |
| Spend | Attempt/run/aggregate and provider-scope limits; named replenishment authority; no automatic refill without explicit policy. |
| Health | Local status, stale heartbeat and meaningful-change alerts. External recipients/channels only if explicitly authorized. |
| Recovery | Pause/drain, cancel, evidence reconciliation, unknown usage, orphan hold, restart, backup/restore and rollback to the previous qualified configuration. |
| Retention | Keep unsettled/held evidence; sanitize summaries; bounded logs; backup access and restore test. |
| Deactivation | Exact service disable/stop procedure, active-attempt handling and read-back verification. |

**Gate:** independent review checks the package against actual S4/S6 evidence. The progress record says **qualified; not activated**. Operational activation is blocked if quality/core work is incomplete, even if a bounded pilot succeeded.

## Phase S8 — Authorized activation and observation

Use existing explicit authorization only if it covers the concrete S7 configuration; otherwise request authorization after presenting it. Register one narrow service and read back the actual installed settings. Do not enable real GitHub polling, webhooks, external notifications, extra repositories or paid resource creation unless their scope is included.

Verify an allowed task completes, a deliberately unqualified/disallowed task holds without launching, repeated ticks do not duplicate work, scheduled credentials work, allowance exhaustion blocks new work, and the proven stop/recovery procedure works. Observe service restart and reboot/logoff only where supported and authorized. Keep operations within the approved budget and workload.

Record **activated** only with installed-host evidence, the qualified configuration digest, execution mode and supported task classes. If registration or a required check fails, stop new launches, reconcile active work, restore the prior safe configuration and record the hold. At first activation without a prior qualified route, the safe rollback is paused intake and no dispatch. The system cannot operate while its required host or dependencies are unavailable.

## Acceptance matrix

| ID | Falsifiable requirement | Evidence type |
| --- | --- | --- |
| A01 | Missing view/home paths, wrong control, partial/nonzero probe and writable view cannot produce a valid proof. | Regression tests plus real S4 boundary |
| A02 | Approved boundary passes all independent positive/negative controls; real owner material is never used as test output. | S4 sanitized report |
| A03 | Disallowed credentials/injection variables never reach preflight, probe, worker, broker project-code executor, completion checks or live launcher; approved names appear without values. | Unit/subprocess tests plus boundary checks |
| A04 | Changed proof algorithm, runtime/launcher/image, namespace or environment policy invalidates affected proof. | Regression tests |
| A05 | Pause prevents launches; cancellation/timeout ends exactly the owned work; ambiguity retains ownership and usage reservations. | Unit tests plus host/container tests |
| A06 | Supervisor/timer restart, late receipts and duplicate ticks cannot create two writers or lose an attempt's cost. | Crash-window and S4 lifecycle tests |
| A07 | Systemd/service stop and tick completion have the intended worker lifecycle; alert behavior includes errors, holds and blockers without unchanged-status noise. | Real service-manager test |
| A08 | Rehearsal changes, identities and synthetic billing never enter live-pilot evidence or allowance. | Separate-store/fixture assertions |
| A09 | Fresh installation checks pass without assuming an active run. | Executed documentation workflow |
| A10 | No paid call, including authentication, precedes scoped authorization; all paid usage is accounted for. | Authorization/evidence ledger |
| A11 | Protected sandboxed acceptance, independent identity, authority audit, current content and cost settlement agree. | S6 verdict |
| A12 | Operational dispatch refuses missing/revoked/mismatched qualification; assessment does not unlock operations. | Quality integration tests |
| A13 | Live evidence covers the selected role-step mode and exact transport; role completion cannot claim job completion. Whole-run sizing cannot qualify it. | Durable-core integration and live evidence |
| A14 | Registered service matches reviewed authorization; recovery/deactivation and allowed/disallowed work are verified. | S8 host read-back |
| A15 | Broker `exec` and every completion-triggered project check run behind the verified boundary, cannot read harmless owner sentinels/fake credentials or mutate owner authority, and have bounded cancellation and generation-aware receipts. | Adversarial subprocess tests and real-boundary qualification |
| A16 | A configured command cannot obtain an offline exemption merely by its adapter name. Fixture model/network attempts are contained/refused; all other execution paths require admission. | Negative fixtures without paid/network calls |
| A17 | Container role steps remain refused until endpoint confinement, cross-dispatch/owner impersonation refusal and crash/restart ownership pass on the actual engine. | Core transport tests plus S4 host evidence |
| A18 | All emitted prompts and skills obey the same permitted command forms; the `Out-File` contradiction is removed. A separately authorized live retest reports whether verification and the remaining job actually complete. | Offline prompt/skill checks; scoped live evidence |
| A19 | Dummy credential delivery, absence, service stop/restart, engine/supervisor restart and supported logoff/reboot are recorded for the actual deployment; unsupported cases are excluded from claims. | Disposable host qualification, no model calls |

Before integrating code, run source validation, generated-doc consistency, the full unit suite, deterministic scenarios and skill preflight from the repository root. Run targeted tests during development; repeat broad checks after integrated changes. Live smoke, model evaluations and paid pilots are separate authorized operations. Record exact commands, exit codes and evidence paths; never substitute historic counts or expected output.

## Primary references checked for this plan

- [systemd service semantics](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html): a oneshot without `RemainAfterExit` deactivates after its main process exits. The existing example therefore needs real lifecycle qualification.
- [systemd process cleanup](https://www.freedesktop.org/software/systemd/man/latest/systemd.kill.html): default control-group cleanup affects remaining unit processes. Disabling cleanup is not an acceptable substitute for deliberate ownership.
- [Docker run lifecycle and options](https://docs.docker.com/reference/cli/docker/container/run/): containers have daemon-managed identities and signal behavior; verify cancellation/recovery for the selected launcher instead of assuming host-child semantics suffice.
- [Claude rate and spend limits](https://platform.claude.com/docs/en/api/rate-limits): spending controls apply at organization/workspace scope, not a universal per-key hard cap. Verify the actual account configuration before an experiment.

Vendor behavior and supported flags can change. Recheck applicable primary documentation and installed capabilities when implementing, and record versions. This plan defines evidence requirements, not permanent claims about a provider or host.
