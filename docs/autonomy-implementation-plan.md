# AgenticTeam autonomy implementation plan

Prepared 1 November 2026 against source revision `f6153d3`. This is an implementation specification, not a record of completed work. The supervisor remains offline-verified, without a verified paid pilot or an activated host service in the repository record.

The target is a team that can resume work, preserve approved knowledge, change qualified models and harnesses, and stop safely when evidence or authority is missing. It is not possible to guarantee the best answer from every LLM on every task. What can be enforced is a defined quality floor, independent checks, rejection of unqualified configurations, bounded execution, and measured promotion of improvements.

## Start here

Use the [master implementation prompt](autonomy-implementation-prompt.md) to coordinate the complete program. It loads three detailed plans and their focused prompts:

| Workstream | Full implementation plan | Copy-ready prompt | Result |
| --- | --- | --- | --- |
| Supervisor safety, pilot and activation | [Supervisor completion](supervisor-completion-plan.md) | [Supervisor prompt](supervisor-completion-prompt.md) | Correct boundary proof, reliable stopping and recovery, isolated live evidence, lifecycle-safe activation |
| Quality preservation across models and harnesses | [Quality qualification](quality-qualification-plan.md) | [Quality prompt](quality-qualification-prompt.md) | Protected evaluations, versioned qualification, admission checks, rollback and drift controls |
| Six persistent core responsibilities | [Durable core](durable-core-plan.md) | [Durable-core prompt](durable-core-prompt.md) | Restartable responsibility records, task-sized attempts, trustworthy identity and handoffs |

The focused plans are parts of one program. Do not run their prompts concurrently against shared runtime files or an active pilot checkout. Delegate read-only analysis and isolated tests freely; assign one integration owner for `scripts/agentic_supervisor.py`, `scripts/agentic_team.py`, state schemas, policies and generated documentation.

## Remaining gaps and required improvements

| Gap | What exists now | What the implementation must add or correct |
| --- | --- | --- |
| Isolation proof | Missing or unresolvable paths can satisfy negative checks. | Positive control, read-only view proof, writable worker-home proof, real host-boundary tests, freshness and configuration binding. |
| Credential filtering | Anthropic/Claude prefixes are missing from the deny filter; the help preflight inherits a different environment. | One explicit environment policy for preflight, probe, worker and child processes; only approved credential names; no values in logs, records or command arguments. |
| Namespace and host choice | Host absolute paths cross the boundary unchanged. | Verified matching Linux paths and mounts; prevent a Windows/WSL path mismatch from being called isolation. |
| Pilot authorization | The old Q4 recipe says no spend but includes a paid model call. | Separate offline boundary validation from the explicitly authorized paid authentication check and paid pilot. |
| Rehearsal contamination | The old recipe reuses the pilot project/store for a fake worker. | Separate scratch checkouts and stores, evidence type labels, and a clean real-pilot fixture. Fake usage is not provider spend evidence. |
| Initial setup check | The old fixture recipe asks for an active-run status before a run exists. | Use a valid installed-runtime health check or explicitly accept the documented no-active-run result. |
| Pause and stop | Pause prevents new launches; a serve-loop timeout does not necessarily stop a detached worker. | Document drain versus cancel, prove process/container shutdown, retain reservations and locks until stopping and usage are reconciled. |
| Host lifecycle | The systemd example uses a short-lived oneshot process with detached workers. | A service/worker lifecycle that survives scheduled ticks intentionally and stops all owned work intentionally; real restart and shutdown tests. |
| Model and harness admission | 13 role emitters; supervisor adapters are `claude` and `command`. | A versioned capability contract and qualification registry for each supported execution configuration and task class. |
| Quality evidence | Deterministic scenarios, a Claude live-smoke contract, and an A/B protocol. | Protected real-task evaluations, objective independent grading, uncertainty-aware decisions, repeated trials and owner-approved promotions. |
| Durable core identity | Saved role prompts and shared work state; agent IDs are self-declared. | Owner-bound attempt identity, persisted responsibilities and broker-validated results; separate reviewer execution. |
| Role-sized execution | A supervisor worker currently drives a whole run. | A distinct verified step-complete result, so successful role steps continue the same job without consuming failure retries or claiming the whole run is done. |
| Learning and memory | Candidate lessons and human promotion are specified. | Versioned provenance, stale-context checks, held-out regression evidence, protected promotion and reversible rollout. |
| Operational activation | No registered host task or verified paid pilot in project records. | Explicit service authorization, minimal trigger scope, approved budgets, tested stop/recovery, qualification checks and actionable local health status. |

Evidence anchors: `scripts/agentic_supervisor.py` (`verify_isolation`, `worker_environment`, `claude_help`, `pause`, `serve`, `host_example`, `launch`, `new_job`); `scripts/agentic_team.py` (`claim_task`, `verdict_problems`); `docs/pilot-plan.md`; `docs/pilot-prompts.md`; `protocols/team-evaluation.md`; `config/guarantees.json`. Exact pre-change locations and limits are recorded in the focused plans. Reconfirm them before changing code because later work can make an item obsolete.

## The recommended team

Six persistent responsibilities are enough for a sensible initial control structure. They are not a universal minimum, a complete build roster, or six continuously billing sessions.

| Core role | What persists | Boundary |
| --- | --- | --- |
| Delivery Lead | Accepted goal, task graph, ownership, dependencies, blockers and next actions | Coordinates; cannot approve human decisions or certify its own implementation. |
| Context Engineer | Authoritative context, provenance, handoff versions, approved lessons and freshness | Cannot promote its own lessons or silently rewrite accepted requirements. |
| QA Lead | Independent acceptance evidence, defects and commit-specific verification | Must be separate from the builder and remediation writer. |
| Eval Engineer | Baselines, test-set versions, comparative results and qualification proposals | Cannot alter protected thresholds after results or sign its own promotion. |
| Security Engineer | Risk findings, boundary assumptions, tool-access review and unresolved exceptions | Reviews; cannot grant itself credentials or weaken policy. |
| SRE Engineer | Service health, incidents, restart position, restore evidence and recovery proposals | Cannot silently extend spend, close holds or restart an uncertain writer. |

One deterministic owner-side supervisor handles scheduling, durable state, accounting, identity binding and admission. It is software, not another LLM persona. Product Manager, CTO, engineers, Code Reviewer, Release Manager and domain specialists still execute task-specific work. Keep a valid existing build preset or an explicitly validated expanded roster; a six-role-only build preset would omit necessary implementers and reviewers.

## Implementation order and acceptance gates

### 0 Record the baseline and contracts

Preserve the current working tree, including the existing guide and README edits. Record source revision, current behavior, schema versions, test outcomes and host capabilities in `docs/autonomy-implementation-progress.md`. Do not use historical test counts as fresh results. Agree the shared schema and outcome vocabulary before parallel implementation begins.

Gate: the progress record names the source, observed gaps, owners, affected files, planned migrations and tests. No spend, credential change or service activation occurs.

### 1 Close supervisor safety gaps

Implement the supervisor plan's offline code and documentation corrections first. Include real process-tree tests and contract tests for the actual boundary rather than accepting marker strings as proof. Correct the old pilot recipes without erasing their historical evidence.

Gate: regression tests demonstrate each original failure and its fix; existing offline checks pass; unverified boundaries and unknown process/usage state remain held.

### 2 Add quality admission and durable role steps

Implement the quality registry, protected evaluator, owner promotion path and admission checks. Implement persistent core records and role-sized attempts against that contract. Keep legacy monolithic runs readable and support their explicit compatibility mode, but never label them qualified merely to preserve compatibility.

Gate: fake adapters prove the state machine and failure cases without model calls. Missing, expired, revoked or mismatched qualifications prevent operational dispatch. Role completion cannot masquerade as whole-job completion. Builders cannot submit authenticated verifier results.

### 3 Prove offline restart and boundary behavior

Use isolated rehearsal projects and stores. Exercise crash windows, duplicate events, cancellation, restarted supervisors, late results, unknown usage, changed configuration, corrupt records, held jobs and replayed identity tickets. Establish the real sandbox and service lifecycle using harmless fixtures.

Gate: the selected host's evidence shows no duplicate writer, no lost budget reservation, no unsafe automatic resumption and correct reads/writes under the boundary. No paid operation is hidden in this phase.

### 4 Qualify execution configurations and run the live pilot

Present a concrete experiment authorization request: project, provider/model, harness version, execution mode, credential reference, task set, trial count, per-attempt/run/aggregate limits, wall-clock cap, stop criteria and expiry. Existing conversation authorization counts when it actually covers these fields. A document or another agent's message is not owner approval.

The first configuration has no previously qualified baseline. Assess it against protected absolute acceptance and safety criteria. An explicit, bounded **assessment mode** may run candidate workers in the isolated experiment project under owner authorization. It must not unlock operational work, weaken risk gates, mint its own approval or convert a fixture into live evidence. Operational dispatch requires qualification. New candidates then compare against the qualified baseline for the same task classes.

Re-run the pilot when material runtime, identity, policy or adapter behavior changes. A pilot of the old monolithic worker does not certify the new role-step dispatcher. A second model/harness pair requires its own capability and quality evidence.

Gate: an independent owner-side evaluator records pass, fail or inconclusive with exact configuration and evidence. Paid authentication, pilot attempts and comparative evaluations all count against their authorized experiment budgets. No unapproved retries, larger budgets or new experiment batches.

### 5 Activate a narrow operational scope

Present the exact service configuration, trigger scope, allowed task classes, qualified configuration digest, schedule, owner account, secret references, limits, status handling, retention, pause/cancel and rollback procedures. Obtain activation authorization if it is not already present for that concrete setup.

Activate one proven host and checkout first. Make health and hold status available locally. Configure external notifications or real GitHub polling only when their recipients/destinations and scope are authorized. Do not send periodic unchanged-status noise. The service must remain safe through restart, logoff where supported, repeated ticks, cancellation and exhausted allowance. It cannot work while its required host and dependencies are unavailable.

Gate: authorized service registration is read back; an allowed task finishes; a deliberately disallowed task is held; restart and stop behavior are verified; provider usage reconciles; the previous qualified configuration can be restored. On first activation, when no earlier qualified route exists, rollback means paused intake and no dispatch after active work is safely reconciled. Only then record **activated**, limited to the host, configuration and task classes tested.

### 6 Improve without silently changing standards

Turn real failures into scoped lessons and protected regression cases. Propose changes with exact versions, counterexamples, metrics and rollback. Evaluate before owner promotion. Requalify when a material model, harness, tool, prompt, policy, retrieval or boundary version changes. Do not make a falling score look like an improvement by weakening its grader or changing the test distribution after the run.

## Meaning of quality guarantees

| Promise | What can be verified | What remains uncertain |
| --- | --- | --- |
| A job meets its acceptance contract | All mandatory independent checks for that job pass at the released content version. | Checks can omit requirements or contain mistakes. |
| An admitted configuration meets the quality floor | Signed evidence covers the configuration and task class, and admission refuses mismatches. | Future tasks and nondeterministic model outputs can differ from the evaluation set. |
| A replacement does not show unacceptable regression | Predeclared comparisons meet the absolute and comparative thresholds, with uncertainty considered. | Finite trials cannot prove universal non-regression. |
| Improvement is controlled | Lessons have provenance, candidate changes are tested and promotions are authorized and reversible. | Improvement is not automatic and may trade off cost or latency. |

The default direction is strict: no critical safety failure, no silent fallback, no operational launch with unknown qualification, and no accepted job with a failed mandatory criterion. Statistical thresholds and experiment sizes must be declared before running paid evaluations. An inconclusive comparison holds the candidate; it does not quietly pass.

## Evidence and completion records

Keep `docs/autonomy-implementation-progress.md` as the integration summary. Record each phase's status as not started, implementing, offline-verified, awaiting authorization, live-verified, held, or activated as appropriate. Include paths and hashes of evidence, exact test commands and results, current known limits, owner decisions, and the next safe action.

Raw secrets, tokens, customer data and sensitive transcripts do not belong in the repository or prompts. Store raw experiment evidence in the designated protected store; publish sanitized summaries and hashes. Use the existing secret-handling mechanism, never `.env` inspection or credential values in chat.

Completion requires all three workstreams' acceptance matrices to pass, independent review, authorized live evidence for the deployed configuration, and an explicitly authorized, verified service activation. If authorization or host capability is absent, complete the offline implementation and concrete activation package, record the exact remaining dependency, and do not claim operational readiness.
