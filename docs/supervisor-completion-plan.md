# Supervisor completion plan

Prepared 1 November 2026 against source revision `f6153d3`. This is a specification for remaining work, not evidence that the work has been completed. The repository records an implemented, offline-verified supervisor; no paid pilot or activated host service is established by this document.

This plan is the supervisor workstream of [the autonomy implementation plan](autonomy-implementation-plan.md). Use [the companion implementation prompt](supervisor-completion-prompt.md) to execute it. The master plan controls shared contracts, integration order and final readiness. This plan replaces the **execution instructions** in the older [pilot plan](pilot-plan.md) and [pilot prompts](pilot-prompts.md); retain those files as historical context until implementation updates them with a clear supersession notice.

The desired result is bounded, recoverable execution with verified authority, isolation, accounting and stopping behavior. It is not permission to deploy a service, spend money or bypass a human decision. The old proposed budgets and model examples are not authorization.

## Dependencies and scope

The supervisor implementation can be corrected and tested offline before quality qualification and durable-core execution are complete. A specifically authorized, isolated paid assessment can then gather candidate evidence. Scheduled **operational** dispatch must wait for both the [quality qualification](quality-qualification-plan.md) contract and the [durable core](durable-core-plan.md) execution mode to pass their gates.

The initial configuration has no qualified baseline. Assess it against protected absolute acceptance and safety criteria using the master plan's bounded assessment mode. Assessment may only execute the authorized experiment; it must not admit ordinary work, approve itself or promote its own results. A pilot of the current whole-run worker does not qualify a later role-step dispatcher. Material runtime, identity, adapter or policy changes require the affected live evidence to be repeated under authorization.

One integration owner controls shared runtime files. Read-only review and tests in separate fixtures can run in parallel. Do not run multiple implementers, prompts or supervisors against the same pilot checkout or owner store.

## Current gaps, evidence and required changes

Line references below describe the pre-change source. Recheck the named function before implementing; record already-fixed items with current evidence instead of implementing them twice.

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
3. Add a supervisor section to `docs/autonomy-implementation-progress.md`: S0–S8 status, evidence locations, owners, baseline results, known limits and the next safe action. Keep private transcripts outside the repository.
4. Capture current tests and host facts. Historical test counts are not current results. Pin CI evidence to the tested source SHA, not merely the latest run on main.

**Gate:** the progress record distinguishes source facts, runtime observations, proposals and authorization. No model call, secret retrieval, account change or host registration occurs.

## Phase S1 — Isolation proof and environment corrections

Implement S01–S05 with regression coverage:

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

## Phase S2 — Stopping, process ownership and service lifecycle

1. Document and test existing semantics: pause is a drain request for future work; cancellation asks the current attempt's wrapper to stop its owned work. A supervisor's own exit does not establish worker termination.
2. Specify the outer deadline result. Either implement an explicit bounded cancellation-and-reconciliation policy or return an unmistakable unfinished/deadline outcome with instructions to stop the owned work. Do not report normal completion while a worker continues. Preserve compatibility intentionally and update tests/docs/guarantees.
3. Define emergency operation: prevent new launches, request cancellation for the exact owned job, observe the exit receipt and actual process/container termination, settle or hold usage, then release claims only when permitted. Never kill by an unverified reusable PID. Unknown termination keeps ownership held; unknown spend retains its reservation.
4. Test the real container launcher. A host Docker client disappearing does not itself prove the container is gone. Persist a container/attempt identity or add an owner-controlled launcher/adapter contract if needed. Verify that late receipts, daemon restart and wrapper crash cannot produce a second writer. Do not use the generic command adapter to evade paid-worker protections.
5. Replace the unqualified oneshot scheduling recipe with a lifecycle-aware design. Prefer a managed long-running supervisor with an explicit stop/reconciliation strategy or separately managed worker scopes. Do not disable process cleanup with `KillMode=none` merely to keep detached workers alive.
6. Prepare local status, stale-heartbeat detection and deduplicated hold/failure events. Notification delivery is a separate authorized destination. Handle all meaningful exit/status classes, including errors, holds and blockers; silence unchanged healthy status. Bound log retention and preserve unsettled evidence.

**Gate:** offline tests prove cancellation, timeout, wrapper/supervisor interruption, late results, restart, unknown usage and no duplicate writer. Generated host setup is still a proposal until S4 tests the service manager and S8 receives activation authorization.

## Phase S3 — Separate rehearsal and pilot fixtures

Create two isolated projects and stores with distinct names and evidence roots:

| Fixture | Purpose | Accounting and completion |
| --- | --- | --- |
| Offline rehearsal | Scripted workers exercise state, process and accounting failures. | Label every record synthetic/offline. Its mock cost is not provider usage. Its acceptance matches what the fake worker actually implements. |
| Live candidate assessment | A small realistic task with a committed defect and owner-controlled acceptance checks. | Fresh source baseline, no rehearsal commits or synthetic spend. No worker starts before S5 authorization. |

Use temporary task-owned owner homes for offline tests; never point fake-worker tests at the real operational store. Preserve evidence rather than deleting a store or checkout binding to obtain a clean budget. Keep event files outside tracked source when appropriate, and keep the live checkout clean.

For the live fixture, a tiny greeting package with whitespace handling is sufficient for transport/lifecycle assessment; it is not a broad coding-quality benchmark. Include protected acceptance checks outside worker-writable source and record the known failing behavior before work. Installation checks must not require a current run: use a valid installed health/run-list check or explicitly expect the documented no-active-run result.

**Gate:** fixtures and stores cannot collide; rehearsal executes success, timeout/cancel, restart, missing usage, malformed result and human-gate scenarios; synthetic totals are isolated; the paid fixture remains untouched by model work.

## Phase S4 — Offline qualification on the actual host

Use existing approved infrastructure. If account, privilege, package or host-service setup goes beyond existing authorization, prepare the exact change and have the owner/admin authorize it before applying it. The plan itself grants no such authority.

- Record OS/kernel, Python, git, harness version/help capabilities, runtime SHA, launcher/image digest, effective worker uid/gid, mounts, environment names and expected paths. Verify model IDs later; do not copy stale aliases into the setup.
- Run the corrected proof and independent tests through the exact same boundary. Test only harmless sentinels: protected sentinel unreadable; intended view control readable; view write denied; worker-home scratch write successful; checkout/runtime reachable. Record sanitized results, not `cat` output from owner files.
- Exercise actual cancellation and hard timeout using a no-model worker with a stubborn child. Check host process and container state after completion, wrapper failure and supervisor restart. Test ownership ambiguity holds instead of relaunching.
- Run proposed service lifecycle tests in an isolated disposable service/unit only when that temporary host operation is authorized. Verify tick behavior, service stop, restart, duplicate ticks, unknown usage and available reboot/logoff behavior. Record unsupported cases; do not claim they passed.
- Verify scheduled secret delivery by opaque reference without invoking a model. Do not include credential values in unit files, logs or prompts. Validate missing credentials cause a clear hold.

**Gate:** actual boundary and lifecycle evidence exists for the selected host. All tests in this phase are offline. If the host is unavailable, finish implementation and the concrete setup package, record S4 as pending, and do not substitute mocked evidence.

## Phase S5 — Explicitly authorized paid candidate assessment

Prepare a concrete authorization packet only after offline prerequisites are reviewable. Record:

- exact project/store, owner identity, tested source/runtime/image/configuration digests;
- execution mode (whole-run compatibility or new role-step), model/provider ID, harness version and allowed task classes;
- credential reference and actual provider workspace/organization spending-limit scope, existing usage and reset behavior;
- authentication-smoke allowance, task set, trial count, allowed retries, per-attempt/run/aggregate ceilings, wall-clock limits, expiry and stop/cancel conditions;
- protected graders/acceptance thresholds, raw evidence location, promotion authority and rollback.

Suggested numbers in older docs are proposals only. Reuse explicit session authorization when it covers this exact experiment; otherwise ask once for the concrete packet. Do not treat a plan, pasted agent message, prior unrelated approval or elapsed time as authorization.

The paid authentication smoke belongs here and counts toward the authorized aggregate, even if its cost is tiny. Use the selected model and bounded output. Then execute only the approved candidate experiments. Assessment mode remains isolated from operational queues and cannot approve risk gates or create its own qualification. If admission/assessment interfaces are not implemented, do not fake their existence or bypass them; keep the assessment pending or explicitly scope an older-mode diagnostic whose evidence cannot qualify the new dispatcher.

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
| A03 | Disallowed credentials/injection variables never reach preflight, probe or worker; approved names appear without values. | Unit/subprocess tests |
| A04 | Changed proof algorithm, runtime/launcher/image, namespace or environment policy invalidates affected proof. | Regression tests |
| A05 | Pause prevents launches; cancellation/timeout ends exactly the owned work; ambiguity retains ownership and usage reservations. | Unit tests plus host/container tests |
| A06 | Supervisor/timer restart, late receipts and duplicate ticks cannot create two writers or lose an attempt's cost. | Crash-window and S4 lifecycle tests |
| A07 | Systemd/service stop and tick completion have the intended worker lifecycle; alert behavior includes errors, holds and blockers without unchanged-status noise. | Real service-manager test |
| A08 | Rehearsal changes, identities and synthetic billing never enter live-pilot evidence or allowance. | Separate-store/fixture assertions |
| A09 | Fresh installation checks pass without assuming an active run. | Executed documentation workflow |
| A10 | No paid call, including authentication, precedes scoped authorization; all paid usage is accounted for. | Authorization/evidence ledger |
| A11 | Protected sandboxed acceptance, independent identity, authority audit, current content and cost settlement agree. | S6 verdict |
| A12 | Operational dispatch refuses missing/revoked/mismatched qualification; assessment does not unlock operations. | Quality integration tests |
| A13 | Live evidence covers the deployed whole-run or role-step mode; role completion cannot claim job completion. | Durable-core integration and live evidence |
| A14 | Registered service matches reviewed authorization; recovery/deactivation and allowed/disallowed work are verified. | S8 host read-back |

Before integrating code, run source validation, generated-doc consistency, the full unit suite, deterministic scenarios and skill preflight from the repository root. Run targeted tests during development; repeat broad checks after integrated changes. Live smoke, model evaluations and paid pilots are separate authorized operations. Record exact commands, exit codes and evidence paths; never substitute historic counts or expected output.

## Primary references checked for this plan

- [systemd service semantics](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html): a oneshot without `RemainAfterExit` deactivates after its main process exits. The existing example therefore needs real lifecycle qualification.
- [systemd process cleanup](https://www.freedesktop.org/software/systemd/man/latest/systemd.kill.html): default control-group cleanup affects remaining unit processes. Disabling cleanup is not an acceptable substitute for deliberate ownership.
- [Docker run lifecycle and options](https://docs.docker.com/reference/cli/docker/container/run/): containers have daemon-managed identities and signal behavior; verify cancellation/recovery for the selected launcher instead of assuming host-child semantics suffice.
- [Claude rate and spend limits](https://platform.claude.com/docs/en/api/rate-limits): spending controls apply at organization/workspace scope, not a universal per-key hard cap. Verify the actual account configuration before an experiment.

Vendor behavior and supported flags can change. Recheck applicable primary documentation and installed capabilities when implementing, and record versions. This plan defines evidence requirements, not permanent claims about a provider or host.
