# AgenticTeam codebase repair prompts

These prompts repair the implementation reviewed at `4e27df2`. They supersede the earlier
build-from-scratch supervisor prompts for future work. Read the
[audit and repair plan](codebase-audit-and-repair-plan.md) for evidence and finding IDs.
Use the master prompt for one continuing implementation; use individual phase prompts
when splitting the work. Keep one integrator for shared runtime files.

## Master repair prompt

```text
Repair the existing AgenticTeam implementation using docs/codebase-audit-and-repair-plan.md.
Do not rebuild the supervisor or repeat its completed P0-P7 implementation. This is a local
implementation and verification task through a reviewed offline release candidate.

Read repository instructions, git status/history, the audit plan, current supervisor contract,
and docs/codebase-repair-progress.md if present. The audit baseline is 4e27df2 with 285 local
unit tests and eight scenarios passing. Re-check current code: another session may already
have repaired an issue. Confirm each finding with a meaningful regression before changing it.
Record disconfirming evidence if a finding no longer applies; do not force the code to match
an outdated report.

Preserve unrelated and concurrent work. Use a suitable existing task checkout/branch or
create a codex/agenticteam-repairs branch without discarding changes. Do not push, merge
main, deploy, register persistent host tasks, send messages or spend model credits unless
the user separately authorized that action. Ordinary local repairs and offline tests are
part of this task and do not need repeated confirmation. Respect denials and human gates.

Create docs/codebase-repair-progress.md with one row per finding ID: current status, phase,
owner, regression, files, commit, test evidence and remaining decision. Track agent quality
improvements separately from reproduced defects. Preserve the older supervisor progress
file as history rather than rewriting it to suggest these cases were previously verified.

Implement F0-F7 in the plan's dependency order:
- F1: authenticated decision state, execution admission, exact action approval, fail-closed
  guards, trusted owner recovery paths, safe manifest mutations and complete isolation proof.
- F2: recoverable state/events, durable unique exec identities, bounded retries, complete
  contributor history and independence across remediation/reassignment.
- F3: canonical checkout ownership and accounting derived from verified owner evidence,
  including unknown cost and orphan reservations.
- F4: durable requeue, per-task failure reconciliation, accurate failed outcomes and source
  identity for polling watermarks.
- F5: access-aware/run-pinned packets, section-aware context, fresh specialist evidence,
  corrected agent command examples and clear result/decision contracts.
- F6: smoke scoring that rejects premature success and deterministic regressions for every
  finding, using installed copies and real state transitions.
- F7: independent review, full offline validation and a concrete optional pilot configuration.

Keep Python stdlib-only, compatible with 3.10+, and preserve Windows support. Do not reduce
human gates, weaken verification, ignore audit problems, fabricate usage, remove failing
acceptance cases or bless invalid fixtures to make tests green. Trusted owner operations
must never execute worker-writable runtime code or worker-authored tests with owner secrets.
Tests use temporary projects, synthetic fixture authority, harmless markers, fake workers
and mocked external actions. Never read real credentials or .env variants; never print tokens.

Use subagents for independent review, regression design or nonoverlapping documentation.
One integrator must own the main runtime (scripts/agentic_team.py) and shared policy changes. Do not allow
parallel edits to the same runtime files. Keep commits reviewable by invariant/fix group,
with matching protocol/template changes, rather than one opaque rewrite.

Run focused tests after each fix. After integration run source validation, generated docs,
the full unit suite, deterministic scenarios, preflight and affected installed/plugin/installer
smokes. Verify the declared OS/Python matrix where available and state unrun coverage.
Update progress before stopping or handing off, including the next exact step.

Finish with an independent review against every finding and the plan's acceptance cases.
Deliver the repaired offline candidate and actual evidence. A paid/live pilot is a separate
milestone: prepare exact isolation, budget, model, timeout and stop conditions; use existing
explicit authorization if it covers them, otherwise ask only at that final activation step.
Never claim model quality improved, a pilot passed, or a service was activated based only
on scripted workers.
```

## F0 reproduce and establish ownership

```text
Execute F0 of docs/codebase-audit-and-repair-plan.md. Read current instructions, git state,
the audit and existing supervisor contract. Create docs/codebase-repair-progress.md, mapping
A1-A7, D1-D3, S1-S9, G1-G5 and E1 to regression tests and responsible phase/owner.

Reproduce the high-priority cases in isolated temporary fixtures without real external
actions. Distinguish executed proofs from source-traced findings and optional improvements.
Capture baseline validation/unit/scenario results. Preserve existing work and all gates.
Do not rerun a paid smoke test or access real credentials.

Freeze the shared contracts needed for later phases: authoritative ordered decisions,
durable state transaction and execution identity, canonical project/store identity,
signed usage reconciliation, unknown-cost representation and contributor history. Keep
the design as small as possible and compatible with existing installed projects. Record
migration/recovery behavior explicitly. Finish with a concrete ordered repair backlog.
```

## F1 authority and trusted owner execution

```text
Implement F1 from docs/codebase-audit-and-repair-plan.md, findings A1-A6 and S5. Read the
progress record and relevant runtime/supervisor functions first. Reproduce each case before
repairing it; use available security-fix workflow instructions where applicable.

Derive checkpoint disposition from ordered authenticated decisions, detecting state
deletion/reclassification and unresolved rejection. Refuse new execution after rejection
or closure, including completion-triggered checks, while preserving status, accounting
and authorized recovery. Require action/scope/risk coverage for approval. Make high-risk
hook context failures deny with a useful reason instead of falling through to allow.

Generate owner recovery commands from the trusted owner-copy runtime with explicit
project/run/store context and correct shell quoting. Review the live-smoke owner path too:
worker-writable code must not receive owner credentials, and worker-authored tests must
execute inside the worker boundary with a filtered environment. Test with harmless sentinels.

Validate every installation-manifest mutation target before any changes: traversal,
absolute/rooted paths, escaping symlinks/junctions and malformed skill names must reject
the operation without partial deletion. Bind isolation proof to all relevant canonical
paths and effective boundary configuration, invalidating stale proof for existing jobs.

Add positive and negative installed-CLI tests for each case. Keep genuine owner approval,
resolution, normal installation/uninstall and unchanged verified configurations working.
Update affected guarantees/protocols and progress; no real credentials, paid workers,
deployments, pushes or permission bypasses.
```

## F2 durable runtime history and independent verification

```text
Implement F2 from docs/codebase-audit-and-repair-plan.md after the F1 authority contract
is stable. Address D1-D3 and A7 with one integrator for scripts/agentic_team.py.

Add fault injection around event append/flush and state replacement. A legitimate interrupted
write must recover into one coherent history; a subsequent mutation must never fork a stale
head. Reject actual edited/truncated history rather than broadly accepting any tail. Define
recovery/migration for existing interrupted runs and test owner audit after recovery.

Reserve unique exec IDs durably before releasing the state lock to launch a command. Keep
distinct immutable log/metadata records and finalize by execution identity plus claim
generation. Concurrent calls and restarts must never overwrite or reuse evidence IDs.

Unify claimed-task reopen with retry/failure accounting. Exhaustion or repeated failure
must require legitimate human recovery. Persist every relevant claimant/writer across
reopen, failure, reassignment and completion. Exclude earlier builders and 05_verify source
remediation writers from verifying their own output; allow a genuinely independent reviewer.

Exercise these cases with actual temporary CLI state and intercepted/harmless commands.
Do not keep a long-running subprocess inside a global state lock as the concurrency fix.
Run affected lifecycle/evidence/authority/unattended tests and update progress and protocols.
```

## F3 accounting and exclusive checkout ownership

```text
Implement F3 from docs/codebase-audit-and-repair-plan.md, findings S1-S4. Read the settled
runtime authority/transaction contracts and coordinate any ledger changes with their owner.

Bind one canonical checkout to its owner-controlled supervisor association. Alternate
--store values, owner homes or path aliases must not permit simultaneous writers. Validate
store metadata against the requested project and specify explicit migration. Reproduce
the competing-store interleaving with fake workers; never touch unrelated processes.

Use authenticated owner usage records as the source of idempotent ingestion. Compare digest,
source identity, amounts and cumulative projections before accepting an existing state record.
Forged or mismatched usage must hold rather than release reservations. Preserve legitimate
replay after usage was committed but the supervisor died before saving its job update.

Represent unknown cost distinctly from numeric zero. A USD-bounded adapter cannot settle
USD using only token counts. Cover missing/null/string/negative/nonfinite cost and valid zero
according to the adapter's documented contract. Keep unmatched reservations and checkout
claims when job records are missing/moved/corrupt; create an actionable orphan-recovery hold.

Test end to end through installed fake-worker runs, including a missing running job record,
unknown-cost completed attempt, signed replay, forged projection and alternate stores.
No accounting fix may refund uncertain usage or grant a new run to evade a ceiling. Record
the invariant and evidence in progress, budgets and operator guidance.
```

## F4 queue and recovery outcomes

```text
Implement F4 from docs/codebase-audit-and-repair-plan.md, findings S6-S9, on the repaired
storage/accounting contract. Preserve unrelated runtime and documentation changes.

Make requeue durable across every source-index/inbox/job write boundary. A returned duplicate
must identify a real or recoverable accepted event. Repair dangling indexes without creating
two jobs. Record per-task failure reconciliation and retry only the uncommitted operations;
transient fail-command errors must not mark reconciliation complete or permit another worker.

Return the documented nonzero outcome for unresolved terminal failures. Define explicit
acknowledgement/history semantics and test mixed-state precedence so old failures neither
vanish silently nor permanently obscure successful later work.

Namespace GitHub polling cursors by canonical host/repository/label. Configuration changes
select the right cursor instead of copying another source's watermark. Test request arguments,
pagination and restart using fixtures and mocks only; no issue comments or network calls.

Add crash/interruption and transient-error regressions, update status/owner next actions,
and record actual focused test results in the progress file.
```

## F5 improve agent contracts and context

```text
Implement F5 from docs/codebase-audit-and-repair-plan.md, findings G1-G5 and the five agent
improvements. Keep useful role-specific expertise; do not replace all 50 roles with generic
boilerplate or expand their permissions to accommodate incorrect generated instructions.

Generate project/run/task/attempt identity, installed roster, access class, owned paths,
profile/stage, canonical artifact paths, required checks and stop conditions from runtime
data. Active roles receive authorized lifecycle commands. Read-only/research roles return
structured findings; separate orchestrator instructions handle state recording.

Pin all generated commands to project and run, including findings-to-tasks --commands and
saved task packets. Reproduce the two-run bug with duplicate task IDs and a changed CURRENT.
Test Bash and PowerShell rendering with paths containing spaces.

Extract requested #sections before applying context limits. Detect missing/ambiguous headings,
prioritize required acceptance/safety material, and report insufficient mandatory context
explicitly. Bind specialist completion to a fresh activation and relevant scope/evidence;
an old planning task must not automatically satisfy a new verification activation.

Repair all G5 examples and contracts: startup budgets on genuinely fresh installs,
ARCHITECTURE creation, remediation --check, run-root RELEASE.md, profile-aware release
guidance, and Fusion proposal sealing. Correct the stale base-SHA and harness-enforcement
statements. Test the actual documented workflows, not just flag-name existence.

Use a compact result envelope containing run/task, status, changes/findings, acceptance-to-
evidence mapping, executed checks, unresolved blockers/deviations and next owner. Make PASS,
CONDITIONAL and FAIL mutually exclusive. Silence cannot resolve a blocking decision. Scale
scaffolding, research and evaluation procedures to the assigned work and available capability.

Exercise platform-core, marketing-only, audit and custom rosters; absent specialists; read-only
research; a small brownfield fix; and interrupted handoff. Run deterministic tests only here.
Update generated snapshots only after inspecting the intended semantic diff. Record measured
contract behavior; do not claim live model-performance improvement without a benchmark.
```

## F6 strengthen evaluation and close regression gaps

```text
Implement F6 from docs/codebase-audit-and-repair-plan.md. Fix E1 and complete regression
coverage for all previous phases. Preserve the F1 trusted execution and owner boundaries.

The current live-smoke offline fixture passes at 04_build without VERIFICATION.md. Replace
that false-positive fixture with the intended valid journey through independent verification
to the legitimate pending human release gate. Keep the smoke's human-release contract distinct
from the unattended supervisor's full completion contract.

Add negative fixtures for stop-at-build, stale/self/missing verification, missing checks,
wrong checkpoint, nonzero worker exit, timeout and unresolved accounting. Main must consider
process outcome as well as scored files. Validate through the trusted runtime and run project
tests only within the worker boundary. Share capability and budget controls where appropriate
instead of allowing the smoke launcher and supervisor adapter to drift.

Expand deterministic scenarios to cover repaired authority, competing stores, interrupted
state/accounting, remediation ownership, run-pinned handoffs and context anchors. Ensure
every confirmed finding has a regression that would fail on 4e27df2 for the right reason.
Do not discard checks, mute exceptions or replace meaningful assertions with string snapshots.

Prepare an optional agent benchmark specification with fixed inputs, score definitions,
baseline/revised comparison, budget and stop conditions. Do not run models without explicit
authorization. Record offline evidence and remaining live/platform gaps in progress.
```

## F7 final review and release candidate

```text
Execute F7 from docs/codebase-audit-and-repair-plan.md. Read the repair progress and current
diff. Assign an independent review using the prompt below and fix confirmed findings with
regressions before declaring the candidate ready.

Run validation, generated-doc checks, the full unit suite, deterministic scenarios, preflight,
installed helper/plugin and installer smokes. Exercise the declared OS/Python matrix where
available and record exact results; do not infer remote CI or platform success from one host.
Inspect snapshot updates and verify the documented commands behave on fresh installations.

Reconcile every finding ID: fixed with evidence, no longer applicable with proof, or still
open. No P1 may remain before the unattended pilot; any deferred P2 needs an explicit rationale
and user acceptance rather than being silently relabeled complete. Update guarantees,
operator guide, README and changelog to describe actual enforcement and limitations.

Deliver the offline release candidate with reviewed commits/diff, tests, unresolved gaps and
the exact next step. Prepare a concrete pilot using a verified whole-worker boundary, chosen
model, run/attempt/aggregate budgets, timeout and stop conditions. Run or activate it only
when the user's existing explicit authorization covers those actions. Do not automatically
push, merge, deploy, schedule a persistent host service or send notifications.
```

## Independent reviewer prompt

```text
Independently review the AgenticTeam repair diff and docs/codebase-repair-progress.md against
every finding in docs/codebase-audit-and-repair-plan.md. Begin read-only; use temporary fixtures
and no paid/model/network calls or real credentials. Do not trust phase labels as evidence.

Trace the authority decision projection and rejection lifecycle; approval action/scope;
fail-closed guard errors; trusted owner runtime paths; manifest containment; state/event
transactions; unique exec identities; retry accounting and complete writer history; project-
wide checkout locking; signed usage replay, unknown USD and orphan reservations; atomic
requeue; task-failure reconciliation; exit outcomes; and source-specific polling cursors.

Inspect generated agent packets for access mode, explicit run identity, required context,
fresh specialist evidence and a usable result contract. Execute representative documented
workflows. Ensure the smoke scorer rejects a plausible incomplete run and accepts a genuinely
verified one. Look for regressions hidden by fixture changes or weakened assertions.

For each actionable finding report priority/severity, exact file/line, trigger, impact,
reproduction or source trace, smallest repair and missing regression. Discard cosmetic noise
and unverified assumptions. Report coverage and live/platform limits. If no actionable
findings remain, state that plainly without claiming a security certification or a live pilot.
```

## Fable documentation handoff prompt

```text
Update AgenticTeam's current documentation and agent-facing examples to support the repair
work, using docs/codebase-audit-and-repair-plan.md and docs/codebase-repair-progress.md.
Coordinate file ownership with the coding integrator; do not edit runtime code or claim
unimplemented fixes have shipped.

Own the G5 example/contract corrections and the human-decision wording identified in the
agent improvements. Keep canonical paths, budgets, required checks, access constraints,
Fusion sealing and release profiles consistent with the repaired runtime. Generate a compact
cross-reference of each changed example and its executable acceptance test. Preserve role
expertise and keep operational facts sourced from the generator.

Make the operator guide use trusted owner-copy commands with explicit project/run/store
context. Explain unknown cost, orphan ownership, failure acknowledgement and recovery according
to the implemented contract. Keep historical design documents clearly historical; one current
operator contract should describe current behavior. Report unresolved design questions instead
of silently choosing a weaker guarantee. Run relevant documentation/workflow checks and
record actual evidence. No paid pilot, remote publication or persistent activation.
```

## Resume after interruption

```text
Resume the AgenticTeam repair work. Read repository instructions, git status/history,
docs/codebase-audit-and-repair-plan.md and docs/codebase-repair-progress.md. Inspect current
changes and test evidence before deciding which phase is next. Preserve other contributors'
work, and continue the first incomplete authorized phase using docs/codebase-repair-prompts.md.

Do not rebuild completed functionality, discard a dirty tree, erase failed evidence or launch
a replacement worker without reconciling the previous attempt's ownership. Keep tests offline
and preserve human gates. Update progress with what actually finished and the exact next step.
```
