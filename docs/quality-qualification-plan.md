# Quality qualification across models and harnesses

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

Historical design baseline: 1 November 2026, source revision `f6153d3`. Refreshed 2 November 2026 against the worktree checkpoints below. The detailed requirements remain the acceptance contract; resume implemented components rather than recreating them. This document does not authorize new model spending, issue a qualification certificate or activate a service.

The governing integration contract is [Autonomy implementation plan](autonomy-implementation-plan.md). Read the [current progress review](autonomy-progress-review.md), coordinate with [Supervisor completion](supervisor-completion-plan.md) and [Durable core](durable-core-plan.md), and use the [focused resume prompt](quality-qualification-prompt.md).

## Earlier checkpoint — superseded by the latest refresh

These are inspected source checkpoints, not evidence that the main checkout contains all runtime work or that operational activation is complete. Recheck branch ancestry and dirty files before integrating further changes.

| Checkout or stream | Checkpoint | Implemented progress and remaining distinction |
| --- | --- | --- |
| Main checkout | `3aafe1b` before this documentation refresh | Planning and guide source; runtime implementation is in the worktrees below. |
| `autonomy-integration`, `.claude/worktrees/pensive-poincare-5e61a2` | `4949185` | Quality and durable-core libraries merged; supervisor S1–S3 and partial S4 host evidence merged. The later admission/role-step wiring is still a separate delta. |
| `claude/autonomy-integration-wiring-8046ea` | `c4794ec` | Admission, role-step dispatch, migration, packaging, G29–G32 and a command-shape rule exist. Review and integrate this implementation; do not start wiring again. |
| `claude/autonomy-quality-registry-22bb47` | `86e96b0` | Q0–Q2 library work is already merged into integration. Later commits `f90f6b8`, `2f9ce02` and `86e96b0` add a direct measurement adapter and sizing evidence; review that unmerged delta separately. |
| Durable-core stream | `1baed75` | D0–D2 library work is already merged. Integration and remaining trust-boundary work are the next steps. |

Evidence sources are the respective worktrees' `docs/autonomy-progress/quality.md`, `integration.md`, `durable-core.md` and `supervisor.md`, together with `docs/autonomy-contracts/`. Older summaries saying wiring has not started, S4 is entirely pending, or all qualification code is merely proposed are stale. The master progress review reconciles those records; a branch record alone is not current runtime activation evidence.

Recorded checks include 505 tests in the recorded full suite at `472d408`, 130 focused checks after `2f97cfc`, and wiring records of 632 Windows tests and 87 Ubuntu tests. These are historical reports, not reruns for this refresh. The later `c4794ec` command-rule change has focused evidence, not a fresh full-suite result. CI on the unpushed branches is not evidenced.

### Remaining gates that change the next implementation steps

| Gap at the inspected checkpoint | Required completion evidence |
| --- | --- |
| Owner-side broker `exec` and completion-triggered acceptance currently run worker-project checks outside the worker boundary. | Run both explicit and automatic checks inside an unprivileged container/VM grading boundary before live qualification or a pilot. Owner code validates evidence; worker-controlled code must never execute with owner credentials, signing keys, private registry/holdouts or inherited authority. |
| Admission returns `not-applicable` for the generic `command` adapter. Arbitrary command arguments do not prove there is no model call. | Explicit nonoperational fixtures remain usable, but every newly activated operational command route must pass admission. Test a command that invokes a model and a forged fixture label. |
| Bundle checks observe only part of the effective tuple: execution mode, adapter, requested model, runtime/CLI digests and separate boundary evidence. Other material is owner-declared. | Bind immutable artifacts and independent capability/identity probes to prompts, skills, tools, harness and actual resolved auxiliary/delegated models. Declared settings alone are not runtime attestation. |
| Dispatch checks exist; active revocation/expiry monitoring and cancellation are incomplete. | A revoked/expired active attempt stops through the tested lifecycle, preserves unknown-cost reservations, reconciles ownership and cannot start a second writer or another step. |
| The new direct CLI measurement adapter lacks supervised broker principal and receipt binding. | Implement a supervised assessment adapter that binds plan, task, attempt identity, artifacts, usage and independent grades to owner-verifiable receipts. Preserve direct sizing as a separate evidence type. |
| Local-process grader fixtures are not container/VM isolation evidence. Repository holdout-shaped fixtures are public. | Prove a real grader boundary and use protected immutable private holdouts. Test owner-secret/store access denial and grader child-process inheritance with safe canaries. |
| Linux role-step identity transport exists; admitted container role-step transport and Windows authentication remain incomplete. | Demonstrate the actual supported transport and negative identity cases. A monolithic-worker run cannot certify role-step dispatch. |
| `c4794ec` corrects a shell command-shape rule, but the skill's PowerShell `Out-File` path and allowed tool instructions still need alignment. | Align generated prompts, skills and narrow enforced permissions, then complete the authorized representative job. Do not broaden permissions to hide the mismatch. |
| Measurement includes auxiliary model usage and cached-token accounting. | Account for every actual `modelUsage` entry, including auxiliary Haiku and cache categories, with known cost provenance; unknown usage never means zero. |

### Measurement provenance and authority

Owner-authorized measurements recorded on 1 November used Claude Max. Their reported dollar amounts are harness-reported **API-equivalent estimates**, not a subscription invoice or proven incremental charge. The old quality record heading “Paid calls: None” describes its earlier offline stage and must not be used as a current summary of the entire branch.

| Recorded sizing evidence | Interpretation |
| --- | --- |
| One Sonnet double-dev measurement, approximately `$0.0146` | Followed an authentication failure with no model execution; it is a small direct-call measurement. |
| Five practice measurements, approximately `$0.0466` total | Limited sizing evidence, not a complete workflow. |
| First greet-worker attempt, approximately `$0.20` and 357k tokens | Stopped at a missing decision view. |
| Second greet-worker attempt, approximately `$0.34` and 962k tokens, mostly cached | Reached build/fix work, then stopped at a denied verification shell command. The token total uses `modelUsage`, not an incomplete top-level count. |

Those direct measurements ran outside the supervised `serve` path and do not establish isolated grading, complete-run cost, role-step qualification or a certificate. A previously discussed `$0.80–$1.50` full-run range is a projection, not a measured completed job. No completed live qualification or activated route is evidenced.

Prior measurement authorization does not authorize a new batch, pilot or activation. Check the actual existing session decision for scope, limits and expiry before any further spend; reuse matching authorization without asking twice, but never infer an expansion from a progress document or this plan.

## 1. Outcome and limits

Build a qualification system that lets AgenticTeam change a model or harness while preserving a declared, measured quality floor. Operational dispatch must refuse a configuration whose qualification is missing, stale, revoked, mismatched, outside its task scope, or statistically inconclusive. Candidate configurations may be assessed only through a separately authorized, isolated and budgeted experiment.

The six proposed persistent responsibilities are Delivery Lead, Context Engineer, QA Lead, Eval Engineer, Security Engineer and SRE Engineer. Their role identities, decisions and evidence persist; their model sessions may end. One deterministic owner-side supervisor handles admission, scheduling, state and accounting. Product Manager, CTO, builders, Code Reviewer, Release Manager and other specialists remain necessary when a task needs them. This work does not replace the existing build roster with six roles.

No number of agents and no finite evaluation can guarantee the best answer on every task or prove universal non-regression across arbitrary LLMs and harnesses. The enforceable promise is narrower: use only configurations qualified for the intended scope, reject observed regressions, hold when evidence is insufficient, preserve independent checks and permit measured, reversible promotion.

## 2. Historical baseline and retained acceptance requirements

The following table describes the original `f6153d3` design baseline, not the current worktrees. Its gaps motivated the requirements below; several now have implementations identified in the current checkpoint. Do not recreate Q0–Q2, the durable-core libraries or existing wiring. Reconfirm actual code and contracts before extending them; historical line numbers can move.

| Foundation at the historical baseline | Historical source anchor | Gap at that time |
| --- | --- | --- |
| Fifty role definitions and thirteen harness emitters | `team.json`; `docs/harnesses.md` | Emitted files are not evidence of equivalent runtime behavior or quality. |
| Supervisor adapters named `claude` and `command` | `scripts/agentic_supervisor.py:64` | No registry of qualified model/harness/tool/prompt combinations. |
| Configuration frozen into a job | `new_job`, approximately line 2650 | No signed qualification reference or trusted task-class assignment. |
| Configuration checks before launch | `Supervisor.launch`, approximately line 1274 | No quality admission before run creation, reservation or worker spawn. |
| Isolation proof bound to configuration | `boundary_digest`, approximately line 1384 | Does not identify the full effective model, tools, prompts, knowledge and grader configuration. |
| Owner-controlled refresh on resume | `Supervisor.resume`, approximately line 2147 | A refreshed model/harness configuration is not requalified. |
| Owner store, attempts, usage reservations, receipts and audit | `Store`, `launch`, `reconcile`, `meter` | No protected promotion, revocation or approved fallback registry. |
| Deterministic scenario suite | `evals/run_scenarios.py`; `tests/test_evals.py` | Tests workflow behavior, not model intelligence. |
| Claude live smoke and offline scorer fixtures | `evals/live_smoke.py`; `tests/test_live_smoke.py` | One small task and a specific human-release-gate contract; not a cross-harness qualification suite. |
| Behavioral-change evaluation protocol | `protocols/team-evaluation.md:71` | Three A/B runs are a smoke minimum, not statistical assurance; no executable admission gate or private holdout isolation. |
| Independent verifier roles and controlled lessons | `agents/engineering/qa-lead.md`; `agents/specialists/eval-engineer.md`; `protocols/evolution.md` | Different role names alone do not establish process identity or independent authority. |

Keep the current smoke contract intact: it succeeds by reaching the human release gate and stopping there. Add distinct evaluation cases for unattended completion and role-step dispatch. Do not make old smoke tests pass by changing their meaning.

## 3. Shared vocabulary and authority

Use these concepts consistently across the three workstreams:

| Term | Meaning |
| --- | --- |
| Execution bundle | Immutable identity of the effective runtime configuration, including all allowed delegated roles. |
| Task class | Owner-defined scope of work and required capabilities, independent of the candidate's self-description. |
| Assessment | A bounded experiment in an isolated fixture project; it produces evidence and cannot perform operational work. |
| Qualification result | Immutable pass, fail or inconclusive evaluation evidence for one bundle and scope. |
| Qualification certificate | Owner-authorized, signed admission authority referencing a passing result. |
| Operational route | Owner-approved selection of qualified bundles for a task class, with explicit fallback order. |
| Attempt | One bounded worker invocation with owner-bound identity, input/output hashes, qualification and usage evidence. |
| Step complete | A verified role-sized result that advances the same job; it is neither a retry failure nor whole-job completion. |
| Revocation | Owner decision that prevents future dispatch under a certificate and invokes the declared handling of active work. |

Only the owner-side broker may authorize admission or sign promotion. Workers may propose plans, produce candidate artifacts and read sanitized status. They cannot write the protected registry, choose a less restrictive task class, alter grading criteria, mint certificates, waive risk gates, increase budgets or approve their own work.

The [durable-core plan](durable-core-plan.md) owns authenticated attempt identities and result binding. Qualification must consume that identity contract. A worker-supplied `agent` or `verifier` string is never sufficient proof of separation.

## 4. Existing modules and historical interface proposals

Current implementation uses `scripts/agentic_qualification.py`, `scripts/agentic_evaluator.py`, generated `schemas/qualification/`, and tests named in the worktree records. The table below preserves the original provisional paths for traceability; do not create duplicates or assume these old names are current interfaces. Extend implemented contracts and migrate incompatible changes explicitly. G29 is quality admission; G26–G28 belong to supervisor safety and G30–G32 to core.

| Proposed path | Responsibility |
| --- | --- |
| `scripts/agentic_qualification.py` | Strict record validation, configuration fingerprinting, owner-side registry, admission decisions and certificate verification. |
| `evals/qualify.py` | Opt-in, budgeted assessment runner; frozen plans, repeated trials, scoring and result assembly. |
| `schemas/execution-bundle.schema.json` | Effective configuration identity. |
| `schemas/qualification-plan.schema.json` | Preregistered scope, experiment, metrics, budgets and stopping rule. |
| `schemas/qualification-result.schema.json` | Complete evidence and pass/fail/inconclusive decision. |
| `schemas/qualification-certificate.schema.json` | Owner-authorized scope, versions, expiry and result reference. |
| `schemas/qualification-event.schema.json` | Append-only promotion/revocation/route-change records. |
| `tests/test_qualification.py` | Black-box registry, admission and statistical fixture checks. |
| `tests/test_qualification_boundary.py` | Real process and selected sandbox-boundary tests, with explicit skip reporting where unavailable. |
| `docs/qualification-operator-guide.md` | Implemented command reference and operational procedures, written from the actual interface. |

Store executable authority and private raw evidence outside the checkout under the protected owner store. Repository files may hold schemas, source code, development fixtures and sanitized result summaries. Update install/package rules, owner-copy contents, generated CLI documentation and guarantee records when implementation adds runtime dependencies. A new helper must not cause the owner process to import worker-writable code.

## 5. Execution bundle and compatibility matrix

### 5.1 Exact effective identity

Canonicalize records deterministically and compute full SHA-256 digests. Declare canonical serialization and normalization rules; do not use ambiguous string concatenation. Reject duplicate keys, unsupported schema versions, unsafe paths, non-finite numbers and unknown authority fields. Reject path traversal and symlink escapes in any bundle materialization.

An execution bundle must identify:

| Field group | Required contents |
| --- | --- |
| Model | Provider, requested model, resolved version/snapshot when available, reasoning/inference settings, context limits and identity-verification method. |
| Per-role models | Effective model/settings for the supervisor's main role and every allowed delegated role; resolve inheritance explicitly. |
| Harness and adapter | Harness version, adapter implementation digest, resolved executable/launcher or immutable image digest, argument-template version and parser version. |
| Tools | Canonical names, input/output schema digests, trusted implementation/server identity, allowed operations, permission and network policy. |
| Instructions | Canonical and compiled role prompts, shared agent contract, protocols, skills, routing rules and policy digests. |
| Runtime | Owner supervisor/CLI digests, state/evidence schema versions, role-step protocol and cancellation/usage contracts. |
| Boundary | Sandbox recipe/image, immutable mount layout, environment-variable allowlist names, namespace mapping and isolation-proof digest. |
| Context and knowledge | Context assembly/retrieval versions, approved knowledge/playbook snapshot and provenance policy. |
| Delegation | Allowed role set, child-launch capability, effective permissions and model override restrictions. |

Never store credential values or credential hashes. Store approved secret-reference names and authorization scopes only. Sanitized registry views must not reveal private owner paths or holdout contents unnecessarily.

Dynamic task content is not part of a reusable certificate's bundle fingerprint. Its exact digest, trusted source classification, context-pack digest and accepted requirements version are recorded on each attempt. The input schema, context-generation procedure and source policy are part of the qualified bundle.

A change to any behavior-relevant identity creates a new candidate bundle. It may reuse still-applicable deterministic evidence, but it cannot silently inherit live quality qualification. Source-code edits that are the task's output are handled by job acceptance checks; changes to the executing agent's own prompt/configuration bundle are a separate configuration change.

Some providers expose mutable aliases without a verifiable snapshot. Record that uncertainty. Strict unattended admission must require an identity method adequate to the declared scope. An opaque alias is not an immutable version; if limited use is later authorized, make its restricted scope, short expiry, sentinel checks and residual uncertainty explicit. Never claim exact reproducibility from an unverifiable alias.

### 5.2 Per-configuration capability evidence

Maintain a matrix distinguishing four states: emitter available, adapter implemented, offline-conformant, and live-qualified for named task classes. Thirteen emitters must never become thirteen qualified runtimes through a default value.

For each candidate, probe or test tool schemas, enforced permissions, context handling, structured results, delegated-role model selection, cancellation, child-process termination, usage accounting, resume compatibility and independent review execution. Pin tool capabilities to observed schemas and effective permissions, not to marketing descriptions or untrusted tool annotations. MCP supports shared interfaces; it does not make implementations equivalent ([MCP tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)).

The second model/harness pair must qualify its whole effective tuple and task class. Reusing the same prompt does not qualify it. A top-level model certificate cannot cover untracked subagents using other models or permissions.

## 6. Registry records and owner-controlled decisions

Use strict schemas and bounded values for the following records. Prefer immutable content-addressed objects plus an append-only owner event log and a small atomic route pointer.

| Record | Minimum fields |
| --- | --- |
| Bundle | Schema version, ID/digest, component identities above, capabilities, creation provenance and explicit limitations. |
| Task class | Version, domain/language/repository constraints, risk ceiling, required capabilities, accepted entry/context modes, mandatory output contracts and exclusions. |
| Assessment authorization | Owner decision ID, plan/bundle/task-set digests, fixture project/store, named provider/model/harness and secret references, allowed operations, limits, expiry and stop conditions. |
| Plan | Baseline or explicit bootstrap status, candidate, scope, protected dataset split, grader versions, metrics, thresholds, sample count/repeats, analysis method, stopping rule and budget. |
| Trial | Plan/case/repeat ID, assigned bundle, trusted attempt identity, input/artifact/transcript hashes, process outcome, usage, duration, independent grades and failure reasons. |
| Result | All trial references, completeness checks, estimates/intervals, per-scope outcomes, decision `pass`, `fail` or `inconclusive`, contamination/exclusion notes and residual uncertainty. |
| Certificate | Bundle/result/plan digests, authorized task classes/capabilities, validity interval, limitations, owner decision/signature and revocation lookup. |
| Registry event | Monotonic sequence, previous-event hash, actor authority, event type, affected IDs, reason, timestamp and signature. |
| Route | Task class/version, active certificate, ordered qualified fallbacks, expected revision and owner authorization event. |

Evaluation success is not activation authority. Lifecycle: candidate, assessed, owner-approved certificate, then owner-selected route. Failed and inconclusive results remain visible. Expiry and revocation are checked independently of an old `active` pointer.

Use owner-side signing keys protected from workers by the real boundary. Do not put signing material in prompts, command arguments, worker environments or the project. Reuse proven signing/verification utilities where appropriate, but do not treat a run-specific token as an unrestricted cross-project promotion authority. Specify key rotation and verification of historical records. A hash without protected authority is only an integrity marker.

Promotion, revocation and rollback use the store lock, expected route revision, append-only event sequence and atomic replacement. Recovery must either complete the authorized transition or leave dispatch held; it must never guess an active certificate after torn writes. Log decisions without secrets. A worker cannot convert a fixture result or an unsigned JSON flag into authority.

## 7. Assessment mode solves the bootstrap problem

The first live configuration has no qualified predecessor. Do not create an operational bypass to evaluate it.

Implement an explicit `assessment` execution mode separate from `operational` mode. Assessment records/admission already exist; complete the supervised live adapter and protected grader using implemented contracts, and document any additional interface accurately.

Assessment requires a protected, owner-authorized plan naming the exact candidate, task set, isolated fixture project/store, trial count, per-attempt/run/aggregate spend caps, wall-clock cap, credential reference, permitted operations, expiry and stop conditions. It permits only the plan's experiment work. It cannot consume operational issues, deploy, publish, message real people, alter routes, grant approvals, or mint certificates. The existing hard human gates still apply.

Offline assessment uses explicitly labeled scripted fixtures with no model calls. Those results establish state-machine behavior only. They cannot be promoted as live model quality, true provider cost or real sandbox certification. Reject certificates whose required evidence types are satisfied only by fixture records.

Bootstrap assessment compares the candidate against protected absolute acceptance, safety and operational criteria. Label the resulting baseline as an absolute-scope qualification, not evidence of improvement over an absent predecessor. Subsequent candidates compare against a currently qualified baseline for the same scope. A baseline becoming unavailable does not automatically qualify its replacement.

Authentication checks that call a model are paid assessment operations and count against the authorized budget. No flag, document, subagent message, or elapsed time substitutes for owner authorization. Reuse existing conversation authorization only when it actually covers the concrete experiment. Stop when the budget or trial cap is exhausted; an inconclusive result never triggers automatic extra paid trials.

## 8. Protected datasets and independent grading

### 8.1 Split and protect the evidence

Maintain development cases, a qualification holdout and fresh reserve cases separately. A production regression set may contain sanitized real failures. Record case IDs, provenance, contamination status, split version and digests. Holdout tasks and expected outcomes must be immutable for the comparison and inaccessible to candidate workers before their authorized case input is released.

The worker receives a case brief and public fixtures, not hidden assertions, reference answers, private rubrics, evaluator code or the remainder of the task set. Keep hidden assets out of shared context, lessons, role memory and verbose error logs. A case exposed for debugging becomes development material; replace it from a controlled reserve before future qualification. Repeated adaptive tuning against the same holdout is contamination, even when only aggregate scores are returned.

Freeze candidate output, then grade it from an owner-controlled evaluator against protected checks. Run any candidate-authored tests and candidate code in a separate unprivileged sandbox with bounded resources and no owner credentials, signing keys, tokens, private store mounts or uncontrolled network access. Never import a worker's module or run its check command in the credential-bearing owner process. Environment filtering alone is not an OS boundary.

Independently authored hidden checks must be capable of failing. Include deliberately degraded artifacts, missing functionality and attempts to tamper with results. Verify the grader's failure behavior before its scores can qualify a candidate.

### 8.2 Who evaluates whom

| Role | Assessment responsibility | Separation requirement |
| --- | --- | --- |
| Delivery Lead | Scope and trial orchestration | Cannot choose easier thresholds or an unqualified operational route. |
| Context Engineer | Case context assembly and provenance | Cannot access private answers or silently modify requirements. |
| QA Lead | Independent outcome acceptance | Separate authenticated attempt from builder/remediation writer. |
| Eval Engineer | Plan, dataset and scorer proposals | Cannot alter frozen grading after results or promote its own candidate. |
| Security Engineer | Boundary and adversarial checks | Cannot waive violations or grant sensitive access. |
| SRE Engineer | Recovery, cancellation and accounting evidence | Cannot conceal unknown usage or extend experiments. |
| Human owner | Threshold approval, assessment authorization and promotion | Final authority is explicit and recorded. |

Prefer deterministic outcome tests, executed-state checks and human-calibrated rubrics. Model judges are supplementary: pin their own model, prompt and version independently from the candidate; blind candidate identities/order where practical; treat candidate content as untrusted; report disagreement. An independent role name using the same context and self-report is not independent grading.

Retain the Eval Engineer prompt's minimum calibration requirement of 50 human labels, but label it a minimum, not universal adequacy. Specify acceptable judge agreement before running. Grader disagreement, failed calibration, missing outcomes or contaminated cases cause an inconclusive or failed assessment according to the preregistered rule.

## 9. Proposed metrics and statistically honest admission

The following defaults are **proposals for owner approval before assessment**, not existing policy or universal standards. Product Manager supplies task meaning; QA/Eval supply measurement; the owner approves the preregistered plan. A more demanding domain may require stricter floors.

| Measure | Proposed default | Interpretation |
| --- | --- | --- |
| Primary task success | At least 90% success, with a one-sided 95% lower confidence bound meeting 90%, in each qualified task class | Every mandatory outcome for a case must pass; the floor applies to the declared distribution, not every future task. |
| Critical safety failures | Zero observed failures; any critical failure rejects | No statistical averaging can offset a credential leak, unauthorized action or broken authority boundary. Zero observed failures is not proof of zero risk. |
| Comparative quality decline | Allowed decline `delta = 0` by default | Require a defensible lower confidence bound on candidate-minus-baseline quality to meet zero. A nonzero margin needs explicit owner approval and revised claims. |
| Deterministic regressions | All required workflow/authority scenarios and must-pass cases succeed | Do not trade off safety or known mandatory failures against a higher average. |
| Evidence and accounting | Complete provenance, independent grades and known usage | Missing or unverifiable evidence cannot pass. |
| Latency, spend and recovery | Explicit per-scope limits declared before trials | No invented universal percentage; unknown limits block assessment approval. |

Every accepted operational job must still pass all of its mandatory acceptance criteria. The proposed 90% evaluation floor describes a configuration's performance on a declared task distribution; it is not permission to deliver failed jobs or ignore the remaining failures.

For the primary binary metric, preregister what constitutes an independent case and whether success means one assigned attempt or success across the fixed repeat policy. Do not switch the denominator after seeing results. Production retries, if allowed, must be the same declared policy in both arms; record first-attempt and final-job outcomes, total cost and retry counts separately.

Use paired baseline/candidate tasks, randomized or interleaved order, the same accepted requirements, and equal declared resources. Run at least three repeats per case unless a justified alternative is preregistered. Set the number of distinct task families, total attempts and maximum spend explicitly; there is no unlimited sampling default. Choose sample size from task diversity, expected variance, effect/margin, confidence/power requirements and budget. A budget too small to establish the floor produces a useful pilot or an inconclusive qualification, not a weaker hidden standard.

Repeated trials of the same task are correlated. Aggregate or resample at the independent task/family level; do not count every repeat as a new independent population example. Use a justified paired interval method and one-sided confidence level fixed in the plan. For clustered scores, a preregistered task-cluster procedure may be appropriate; for sparse binary outcomes use a conservative justified interval rather than a naive normal approximation. Degenerate bootstrap intervals from all-equal tiny samples are not automatic proof of equality. Test the statistical implementation against independently computed reference cases.

Strict `delta = 0` can leave an equally capable but noisy candidate inconclusive. That is an honest outcome. Failure to find a statistically significant difference does not prove equivalence. A candidate meeting the absolute floor but failing or not establishing the comparison cannot replace the qualified baseline under the strict route.

Record all scheduled trials: crashes, timeouts, invalid outputs and unavailable required tools are outcomes. Exclude only cases allowed by the preregistered infrastructure-failure rule, preserve their records, report both raw and adjusted counts, and require independent approval where the rule calls for it. Do not cherry-pick favorable runs or keep retrying until a pass appears. Missing trials, post-hoc threshold changes, unplanned multiple comparisons or unbounded sequential peeking prevent qualification.

Use per-task-class and critical-subgroup floors. A gain on easy work must not conceal a loss on difficult or sensitive work. Predeclare multiple-comparison handling. Report counts, estimates, uncertainty, distributions and residual limitations, not only a single composite score.

The existing three baseline/three candidate A/B rule in `protocols/team-evaluation.md` remains a minimum behavioral smoke requirement. It does not establish cross-harness quality, statistical equivalence or universal safety. Extend that protocol explicitly without weakening its human-promotion rule.

For perspective, under independent Bernoulli assumptions zero failures in 299 trials yields an approximately 1% one-sided 95% upper failure-rate bound; it does not demonstrate zero failure probability. Correlated tasks do not satisfy that assumption. Use suitable one-sided or exact intervals, especially for sparse outcomes ([NIST confidence-interval guidance](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm)).

Evaluate the model and harness together and maintain both capability and regression cases; they answer different questions ([Anthropic agent-evaluation guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)).

## 10. Fail-closed operational admission

Implement a single owner-side admission decision used by initial launch, retry, resume, wrapper startup and role-step dispatch. It returns an explicit admit/hold decision, reasons and exact authority references; it must not mutate quality standards to obtain admission.

Before creating a run, reserving new model spend or starting a worker, require:

1. A trusted task-class assignment and capability/risk requirements.
2. Valid record schemas, signatures and event-chain/route revision.
3. A passing result of the required evidence type and an owner-approved certificate.
4. Exact observed effective bundle identity, including allowed delegated roles and tools.
5. Matching scope, valid time window, no revocation and sufficient freshness.
6. Current isolation evidence, existing hard gates and available authorized budget.
7. A compatible resume/role-step contract when continuing existing state.

Persist certificate ID, registry revision, bundle digest, mode, scope, identity ticket, input digest and admission reason in the job/attempt intent before spawn. Integrate at `Supervisor.launch`, `new_job`, `resume`, wrapper execution and the new role-step dispatcher. `resume --refresh-config` must not transfer a certificate to a new bundle.

Recheck immediately before the wrapper starts the actual worker, and before every subsequent worker/role step. Use immutable owner-protected artifacts or read-only image/mount identities to prevent check-to-use replacement; a checksum check alone cannot stop a file changing afterward. Revalidate current revocation and expiry at each new dispatch, including after restart or a crash between intent and spawn.

An already-running model call cannot be retroactively prevented. Declare active-attempt behavior: on revocation or expiry, stop further dispatch, signal cancellation of owned work through the supervisor's tested lifecycle, reconcile its process and usage, and hold the job. If the harness cannot stop at individual tool/model steps, disclose that coarser boundary and do not claim per-tool enforcement. Never start a replacement while the old writer may still be active. A safety revocation must not silently drain into another unqualified step.

At completion, verify the observed model/tool/result identity and provenance against the admitted bundle. A mismatch or unknown identity cannot yield certified completion; preserve evidence, account for usage and hold. A zero process exit is not a quality verdict.

Apply the same rule to `command` adapters. Offline fixtures use explicit test-only evidence and isolated test configuration, never a production flag that bypasses qualification. Do not let a fabricated `fixture` label authorize an arbitrary command in operational mode.

### Compatibility and migration

Continue to read and report legacy monolithic runs, states and transcripts, and preserve existing interactive/monolithic parser semantics. Preserve history, charges, reservations and unresolved holds. Missing qualification fields mean `legacy/unqualified`, not an inferred pass. Existing interactive compatibility remains governed by its existing authority and safety rules; it is not evidence of qualified unattended operation.

Every newly activated operational scheduler route uses strict qualification. Moving an existing store to strict admission is an explicit owner-controlled migration: drain or cancel and reconcile its attempts first, record the mode transition, then put unqualified pending work into visible qualification holds. Do not silently reinterpret frozen jobs, invent certificates or switch an active store's semantics during an attempt. Offline fixtures retain explicit nonoperational test mode.

Once a route/store uses strict operational admission, its new launches, retries and role steps require a qualified bundle. An explicit compatibility mode may preserve old interpretation, reporting and supported monolithic execution shape, but it cannot bypass qualification for a newly activated operational scheduler route or call a legacy run live-qualified. The owner must select an appropriate qualified configuration for held work or authorize a separate assessment. Reconcile old running processes safely before migration; never launch a replacement or erase their state merely to make migration convenient.

Use versioned migration records and test interrupted migration. Unknown future schemas fail closed for execution while read-only diagnosis explains the incompatibility. Never rewrite past evidence as if the new gate had existed at the time.

## 11. Fallback, rollout, rollback and learning

Fallback is an owner-approved list of still-qualified bundles for the same task class and capabilities. Availability alone is not qualification. An exhausted budget, missing provider response or invalid model identity must not trigger an unapproved cheaper model.

Before switching, stop/reconcile the prior attempt, preserve unknown-cost reservations, verify source/task state, check resume compatibility, and start a new bound attempt. If safe cross-harness continuation is unproven, hold or use an explicitly planned clean checkpoint/checkout. Reconcile externally consequential actions before replay; use idempotency where the action supports it. Re-run independent acceptance at the resulting content version.

Promotion is scoped and gradual: an isolated assessment, owner approval, a narrow authorized canary, observation against declared abort conditions, then an explicit route change. Canary actions and costs need the same authorization discipline as assessments. Material runtime/identity/adapter changes require a new live pilot; a monolithic-worker pilot does not certify role-step dispatch.

Rollback restores a previously qualified route only if its certificate remains valid under current policy. It does not undo external actions, discard source changes, refund usage or delete audit history. Preserve the previous route and run compatibility/rollback drills before activation.

Learning sequence: observed failure with provenance, sanitized scoped lesson, development regression case plus a separately held-out sibling case, candidate prompt/playbook change, fixed-plan evaluation, owner promotion, versioned bundle and reversible rollout. Do not call a disclosed failure example a secret holdout. Context Engineer maintains freshness and provenance; Eval Engineer measures; QA/Security verify; only owner authority promotes. Do not leak private case contents into lessons or reduce a threshold because a new model performs worse.

## 12. Phases and acceptance gates

| Phase | Deliverable | Required gate |
| --- | --- | --- |
| Q0 Baseline and boundaries | Source/evidence inventory; agreed schema and identity contracts; supervisor pre-pilot corrections | No paid calls; real boundary requirements understood; existing working tree preserved. |
| Q1 Immutable schemas and registry | Strict records, fingerprinting, protected store and append-only decisions | Tampering, unknown versions, path escapes and partial writes fail safely. |
| Q2 Independent evaluator | Protected splits, sandbox graders, complete trial results and tested statistics | Degraded fixtures fail; no owner-context execution of candidate code; missing evidence cannot pass. |
| Q3 Admission integration | Launch/resume/wrapper/role-step checks, revocation and migration | No new operational worker without valid scoped authority; legacy records remain readable. |
| Q4 Offline system rehearsal | Crash, replay, lifecycle, cancellation, duplicate and fake-model scenarios | State-machine tests pass and remain explicitly offline; no fixture becomes live-qualified. |
| Q5 Authorized bootstrap assessment | First live bundle assessed against absolute criteria | Fixed owner-authorized experiment; pass/fail/inconclusive with usage and boundary evidence. |
| Q6 Second pair and comparative admission | Whole-tuple/task-class comparison with a qualified baseline | All absolute and comparative gates pass; owner approves before changing any route. |
| Q7 Narrow rollout and sustained checks | Authorized canary, tested rollback, drift/expiry handling and local health | Service activation follows the master/supervisor plan; only evidenced scope is called activated. |

Update `docs/autonomy-implementation-progress.md` with phase status, exact source, affected files, checks actually run, sanitized evidence hashes, limitations, owner decisions and next safe action. Offline-complete and awaiting live authorization is a valid honest intermediate state; it is not full completion.

## 13. Verification matrix

Prefer black-box CLI/subprocess tests and independently specified fixtures. Observe launch markers, processes, registry revisions, reservations, artifacts and outcomes. Do not build tests by copying the implementation's predicates or recomputing a hash with the same faulty helper and calling equality proof.

| Case | Expected evidence |
| --- | --- |
| Missing/malformed certificate | No launch marker or new model spend; explicit qualification hold. |
| Edited result/certificate/chain | Rejection without losing audit history. |
| Model snapshot, tool schema, prompt, playbook or delegated-role model changed | Old certificate cannot admit the modified tuple. |
| Unknown task class; issue nominates its own certificate | Hold; untrusted text grants no authority. |
| Expired/revoked certificate on retry, resume or restart | No subsequent worker step starts. |
| Revocation between intent and wrapper spawn | Wrapper refuses; reservation reconciled correctly. |
| Revocation while running | Owned work is stopped/reconciled; no duplicate writer or next step. |
| Promotion races with dispatch | One explicit admitted revision; no unrecorded stale selection. |
| Bundle replaced after hash check | Immutable boundary prevents replacement or startup refuses. |
| Config refresh to unqualified tuple | Resume remains held; no silent certificate transfer. |
| Command adapter or fake fixture seeks bypass | Operational admission still applies; fixture cannot mint live authority. |
| Assessment authorization missing, expired or out of scope | No trial starts; no automatic operational fallback. |
| Assessment reaches attempt/time/spend ceiling | Stops with complete records; no automatic extra sample. |
| Baseline absent | Only authorized bootstrap absolute assessment; no fabricated comparison. |
| Hidden-test leakage, symlink escape or candidate imports | Worker/grader boundary denies access to owner authority and unreleased holdouts. |
| Candidate writes PASS files or disables its tests | Independent acceptance still detects the seeded failure. |
| Constant-success or tampered grader | Known bad artifact fails qualification of the grader. |
| Too few trials, missing outcomes, failed judge calibration | Inconclusive or fail by the frozen rule; no promotion. |
| Improved aggregate but failed critical subgroup | Admission rejects. |
| Statistical edge cases: all successes, all failures, ties, correlation, sparse discordance | Independently calculated expected intervals/decisions; no divide-by-zero or false confidence. |
| Checkpoint recovery and a new harness session | Exact accepted requirements and context provenance survive; current acceptance reverified. |
| Builder submits a verifier result or replayed identity ticket | Broker rejects; no quality verdict forged by role name. |
| Unknown cost or surviving prior worker during fallback | Reservations/ownership retained; no new worker. |
| Owner rollback to expired/revoked route | Refused; rollback is not a safety downgrade. |
| Valid rollback | Atomic route change, preserved history and accounting, correct next-attempt bundle. |
| Legacy and future schema records | Legacy readable but unqualified; unknown execution schema held. |
| Package/install/owner-copy | Installed and protected runtimes include the new module/schema dependencies. |
| Existing smoke and deterministic scenarios | Their original authority, evidence, release and recovery meanings remain intact. |

Run the established offline checks appropriate to the changes: manifest validation, generated CLI documentation consistency, the unit suite and deterministic scenarios. Test the new scenarios once their implementation is complete. Do not run opt-in live evaluation, model authentication, provider calls or persistent activation during offline verification. Real boundary and paid evidence are separate, explicitly recorded gates.

## 14. Completion definition

This workstream is offline-complete when schemas, registry, isolated grading, statistics, migration and admission behavior are implemented, packaged, documented and independently reviewed, with failure tests demonstrating that the gate can refuse plausible false successes.

It is live-qualified only when the exact deployed tuple and task classes have genuine authorized assessment evidence, owner-approved certificates and tested operational lifecycle behavior. It is activated only after the separate service authorization and read-back verification in the master plan. Do not collapse those three states.

The delivered system must be able to explain: what configuration is allowed, for which tasks, based on which evidence, who authorized it, when it expires, what changed, why a run is held, and which qualified rollback remains available. It must never claim guaranteed best quality.
