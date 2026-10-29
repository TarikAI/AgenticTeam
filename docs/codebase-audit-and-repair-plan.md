# AgenticTeam codebase audit and repair plan

Reviewed 2026-10-29 at `4e27df2`, after the supervisor and cross-platform fixes were merged.
The repository was clean when this audit began. The supervisor exists and has substantial
offline coverage. The next step is to repair the specific gaps below, not repeat the earlier
supervisor implementation plan. Preserve that plan and its progress record as implementation
history. Use the companion [repair prompts](codebase-repair-prompts.md) for the next work.

The principal risks are authority decisions that do not remain binding on every execution
path, accounting that trusts an editable projection, and recovery records that can disagree
after interruption. Agent quality is also limited by instructions that conflict with actual
CLI requirements. Resolve the high-priority findings before activating a paid unattended pilot.

## Verified baseline and review coverage

| Check | Observed result |
| --- | --- |
| Source validation | Passed: 50 agents, 9 presets, 13 harnesses. |
| Generated documentation | Passed. This checks generated text and syntax, not whether every documented workflow succeeds. |
| Full unit suite | 285 tests passed in 576.083 seconds on Windows / Python 3.14.5. |
| Deterministic scenarios | 8 of 8 passed. |
| External skill preflight | Passed; optional design-architect was absent. |
| Targeted review probes | Confirmed additional defects despite the green suite, using temporary projects, synthetic fixture authority, fake workers and mocked external commands. |
| Paid execution and publication | No model calls, live pilot, remote writes, deployments or persistent host registration were performed. |

The inventory contains 239 tracked files: 8 scripts, 50 role definitions, 15 skill files,
26 protocols, 21 runtime templates, 13 knowledge files, 16 documentation files, 10 eval files,
20 test/fixture files, 48 generated snapshots and 12 configuration/repository files.

The review covered both runtime implementations, all helpers and installers, CI, evals,
configuration/schemas, role procedures and output contracts, skills, protocols, templates,
and current supervisor documentation. Core authority, persistence, scheduling and accounting
paths received deeper source tracing and targeted reproduction. Tests received full execution
and focused source review. Generated snapshots were exercised through their tests rather
than independently audited as another implementation. Historical plans were context; repeated
role expertise paragraphs received targeted inspection. This is repository-wide coverage,
not a claim that every path or platform has been proven correct.

Open Code Review's range preview from `6fc55a2` to `4e27df2` selected 10 files; all 10 were
reviewed, none skipped, for 100% coverage of that selection. They were `config/guarantees.json`,
the two eval Python files, the supervisor scenario, both runtime Python files, `install.sh`,
and the fake worker/helper/fixture files. Its 19 excluded documentation/test files were also
reviewed outside that selection. The broader audit additionally covered unchanged code.

Real Claude behavior, a real restricted-account/container boundary, current vendor format
compatibility and remote CI results were not verified in this session. Local green tests
must not be described as successful live autonomy or proof of all operating systems.

## Authority and execution findings

P1 means high severity and a prerequisite for the unattended pilot. P2 means medium severity
and required for the corrected release candidate. Line numbers refer to `4e27df2`; resolve
the named function after edits move them. Each finding below states its evidence strength.

**A1 P1 Security — signed rejection can disappear from the effective decision state.**
Path: `scripts/agentic_team.py`, lines 3002–3010 and 3081–3085.
After a genuine owner rejection, changing the checkpoint's editable status to `recorded`
and the run to `active` allowed a new claim; the owner audit returned no problems. This was
reproduced. Derive effective checkpoint disposition from ordered authenticated decisions,
and reconcile in both directions. Test status changes, deletion and ID substitution; only
a legitimate resolution or explicitly valid supersession may clear the rejection.

**A2 P1 Security — an existing claim can start commands after owner rejection.**
Path: `scripts/agentic_team.py`, lines 2585–2592, `exec_command`.
A claimed task executed a harmless marker command with exit 0 while the run remained
`blocked-rejection`. Check the effective run gate before every new subprocess, including
checks started by completion. Keep passive reporting, cost recording and authenticated
recovery usable. Test ordinary execution and automatic acceptance checks after rejection
and closure; neither may start a new process.

**A3 P1 Security — approval is matched by risk but not by the approved action.**
Path: `scripts/agentic_team.py`, lines 2592–2602.
An approved R3 deploy task invoked a mocked command classified as publish. The CLI accepted
it even though the hook checks the action separately. Centralize admission so the task's
action, target/scope, required risk and current authenticated approval all cover the command.
Test deploy-versus-publish and other mismatches directly through the installed CLI without
depending on a hook to rescue an incorrect CLI decision.

**A4 P1 Security — guard lookup failures allow high-risk commands.**
Path: `scripts/agentic_team.py`, lines 4630–4651, `guard_decision`.
On a fresh installation with no current run, a guard query for a publish command returned
`None`, meaning allowed. No publish command was executed. Once a risky rule matches, missing
or unreadable approval context must deny with a useful reason. Test absent CURRENT, missing
state, malformed policy and unavailable verification data while preserving ordinary safe
operations and correctly approved actions.

**A5 P1 Security — recovery instructions cross back into worker-writable code.**
Paths: `scripts/agentic_supervisor.py:2163`, `docs/supervisor-operator-guide.md`,
`evals/live_smoke.py:124`, `evals/live_smoke.py:145`.
Generated owner actions pass the token file to the checkout's installed runtime, despite
the supervisor's trusted owner-copy design. The live smoke likewise meters through that
copy after a worker can edit it; its acceptance subprocesses also inherit the owner's
environment. This is a source-traced trust-boundary defect, not a claim that credentials
were stolen. Generate absolute commands for the trusted owner runtime with explicit project,
run and store context. Keep execution of worker-authored tests inside the worker boundary
with a filtered environment; keep authentication and metering in trusted code. Use harmless
sentinels to test recovery commands and smoke execution without accessing real secrets.

**A6 P1 Security — uninstall trusts paths in the installation manifest.**
Path: `scripts/agentic_team.py`, lines 1401–1414; inspect reinstall paths at 1197–1289 too.
A fixture manifest containing a parent-relative generated-file path caused uninstall to
delete a harmless sibling sentinel outside the target. Validate all manifest paths and
ownership before any mutation: traversal, absolute/rooted Windows paths, skill names, and
symlink/junction escapes. Reject the whole operation before partial deletion when any path
is invalid. Keep normal uninstall and preservation of runs/knowledge/supervisor state intact.

**A7 P1 Correctness — verifier independence omits earlier and remediation writers.**
Path: `scripts/agentic_team.py:2311`, `:3332`, `:3628`.
Two reproduced paths pass: an earlier builder becomes eligible after reopen/reassignment
erases its claim history; and a source-remediation writer in `05_verify` names itself as
the final verifier, advancing to release. Persist all relevant contributors across attempts
and include remediation in independence checks. Test both paths and a genuinely independent
reviewer. Role-level separation remains the documented guarantee; do not imply it proves
different human identities or isolated model reasoning.

## Runtime persistence and retry findings

**D1 P2 Correctness — concurrent commands overwrite evidence.**
Path: `scripts/agentic_team.py:2604`, `:2641–2648`.
Two concurrent calls for the same claim both returned `A-1` and referenced the same log;
the second command replaced the first log. Reserve a unique execution ID durably before
launch, finalize by that ID and claim generation, and retain immutable distinct logs.
Test concurrent commands and interruption between reservation, execution and finalization.

**D2 P2 Correctness — interruption between event append and state replacement forks history.**
Path: `scripts/agentic_team.py:1542–1563`, state/event persistence.
Fault injection left two events with a one-event state. A subsequent normal mutation appended
from the stale head, creating a broken chain. Add a recoverable transaction boundary or
validated pending-tail recovery; do not append to an unreconciled history or simply ignore
audit failures. Test each durable-write boundary and distinguish interrupted valid writes
from edited or truncated history.

**D3 P2 Correctness — reopening a held claim bypasses the retry limit.**
Path: `scripts/agentic_team.py:3332–3349`, `reopen_task`.
Five claim/reopen cycles left a task ready under a policy allowing two retries. Reopening
must preserve claimant/failure history and obey the same retry/escalation policy as other
abandonment paths. Once exhausted, require authenticated human reopening or extension.
Test repeated reasons, accumulated attempts and legitimate owner recovery.

## Supervisor and accounting findings

**S1 P1 Correctness — different stores can launch writers in the same checkout.**
Path: `scripts/agentic_supervisor.py:687–692`, `:702–706`, `:732–761`.
Two supervisors with distinct store roots passed synchronized startup checks and launched
two actual fake-worker processes in one checkout. Bind the canonical checkout to one store
and enforce checkout ownership independently of caller-selected store paths or owner homes.
Validate store-to-project metadata and define explicit migration. Test competing stores,
different homes, aliases to the same checkout and reuse of a store for another project.

**S2 P1 Accounting integrity — editable usage records are accepted as owner ingestion.**
Path: `scripts/agentic_supervisor.py:1384–1405`; runtime `audit_verify`.
A fixture's state was given a matching transcript hash and zero-valued usage source without
a signed usage record. The job became done at USD 0 although its transcript reported USD
0.01; the owner audit accepted it. This reproduces projection trust after worker exit, not
a paid worker predicting its final transcript hash. Reconcile deduplication using verified
owner-ledger records, checking source ID, digest, amounts and cumulative projections.
Forged or mismatched projections must hold; legitimate crash-after-ingestion replay must
still reconcile without double counting.

**S3 P1 Accounting integrity — missing USD is treated as zero USD.**
Paths: `scripts/agentic_team.py:2456–2459`, `scripts/agentic_supervisor.py:1386–1405`.
Resuming an unknown-usage job with a result containing 120 tokens and no cost changed it
to done, cleared the reservation and restored the whole aggregate allowance. For an
adapter bounded in USD, require a valid USD figure to settle USD. Missing, null, string,
negative and nonfinite amounts must remain unknown; handle genuine numeric zero according
to the adapter's explicit result contract. Test both parsing and full job reconciliation.

**S4 P1 Correctness — losing a job record refunds unknown spend and checkout ownership.**
Path: `scripts/agentic_supervisor.py:1052–1057`, `:1065–1069`.
Moving an unknown-usage job aside changed its reserved USD from 1 to 0 and checkout holder
from the job to none, without settlement. Preserve unmatched reservations and ownership in
durable owner records. Missing metadata requires an orphan-recovery hold reconciled against
attempt receipts and explicit disposition. Test missing, moved and torn records for both
finished unknown-cost attempts and potentially live workers; settled-charge tests alone
do not cover this case.

**S5 P1 Security — isolation proof does not cover its full configuration.**
Path: `scripts/agentic_supervisor.py:898–899`, `:1910–1911`, `:2039–2041`.
After a mocked successful probe, changing the verification-view directory retained
`verified=true` and produced no launch problem. Bind proof to the complete effective
boundary: canonical store/home/view/worker paths, boundary identity/configuration,
interpreter and relevant environment. Invalidate affected configuration and frozen jobs
when it changes. Test each change; do not claim these mocked tests validate a real OS boundary.

**S6 P2 Correctness — requeue can acknowledge a job that does not exist.**
Path: `scripts/agentic_supervisor.py:935–941`.
Interrupting after source-index replacement but before inbox creation made every retry
return duplicate `fix-1-r2`, with no such job or event. Commit a recoverable intent or durable
event before the index references it, and repair dangling references. Fault-inject every
write boundary and require exactly one accepted or recoverable requeued job.

**S7 P2 Correctness — terminal failed jobs return successful host exit codes.**
Path: `scripts/agentic_supervisor.py:1846–1847`, `:1871–1879`.
A known-cost worker exhausted retries and left a failed job, while serve-until-idle and
status both returned 0. Include unresolved failures in exit classification and next actions.
Define explicit acknowledgement of historical failures so a repaired queue need not remain
failed forever. Test mixed states and retain the documented 1/3/2/0 precedence.

**S8 P2 Correctness — unsuccessful failure recording is marked reconciled.**
Path: `scripts/agentic_supervisor.py:1354–1356`, `:1419–1426`.
One injected runtime `fail` error left the task claimed with no failure history, but marked
failure reconciliation complete and the job retrying. Reconcile each required task
durably and hold launch until all claims and failures are accounted for. Test transient
and persistent errors, restart between records and protection against duplicate failures.

**S9 P2 Correctness — GitHub polling reuses another host's watermark.**
Path: `scripts/agentic_supervisor.py:1926`, `:1951`.
Changing host while keeping repository/label sent the old host's `since` timestamp to the
new host in a mocked request, potentially missing older eligible issues. Namespace poll
state by canonical host, repository and label; changing any selects or creates the correct
cursor. Test each dimension and unchanged incremental polling without network access.

## Agent workflow and evaluation findings

**G1 P2 Agent contract — task packets demand tools a role does not have.**
Path: `scripts/agentic_team.py:3928`, `:3981`.
A research-role fixture received claim/exec/complete instructions, despite its compiled
read-only contract and tool restrictions. Generate access-aware instructions: active roles
execute authorized lifecycle steps; read-only/research roles return structured findings,
with separate orchestrator recording instructions. Test all access classes across installed
rosters rather than loosening tools to fit a generic packet.

**G2 P2 Correctness — generated commands are not bound to the intended run.**
Paths: `scripts/agentic_team.py:3928`, `scripts/findings_to_tasks.py:187`, `:212`, `:305`.
Packets omit explicit run selection. The remediation bridge also drops an explicitly
requested run from generated commands: an offline two-run reproduction inserted
`remediate-001` into current rather than requested `wanted`. Carry project and run through
every generated command and handoff. Test saved packets after switching CURRENT and both
command rendering and direct apply, including overlapping task IDs and shell quoting.

**G3 P2 Agent context — requested file sections disappear during truncation.**
Path: `scripts/agentic_team.py:3944`.
For `large.md#Required`, a fixture packet retained the long introduction and omitted the
requested section. Resolve headings before budgeting, report missing/ambiguous anchors,
and prioritize required task/acceptance inputs over optional background. Reserve space
for the mandatory envelope and omissions report; return an explicit incomplete-context
condition when required material cannot fit. Test late/duplicate/Unicode headings and
multiple required inputs.

**G4 P2 Agent evidence — old specialist work satisfies a new activation.**
Path: `scripts/agentic_team.py:1943`, `:3578`.
Code tracing shows the gate accepts any completed task by the role, regardless of a later
activation's stage or changed scope. Bind satisfaction to an activation identity, scope
revision and relevant evidence. Allow reuse only through an explicit justified record.
Add the executable regression first: early specialist review, later implementation change,
reactivation, and refusal until fresh scoped work or reasoned deactivation. This finding
was source-traced rather than separately executed in this audit.

**G5 P2 Documentation contract — several advertised agent workflows cannot work as written.**

| Source at the reviewed commit | Concrete mismatch | Required check |
| --- | --- | --- |
| `README.md:136`, `skills/agentic-build/SKILL.md:51` | Default supervised startup omits the required budget; a fresh-install probe exits 1. | Execute the example against default policies, without the test helper's injected budget. |
| `agents/leadership/cto-architect.md:29` | Requests scaffolding ARCHITECTURE.md, which has no registered template; probe raises Unknown artifact. | Supply the intended template or a consistent handwritten-artifact instruction, then exercise it. |
| `agents/engineering/qa-lead.md:34`, `code-reviewer.md:71` | Remediation apply examples omit required checks; helper rejects them when findings exist. | Run each example with a real finding and verify a runnable task with a writing owner and check. |
| `agents/specialists/release-manager.md:49` | Output points to stage-local RELEASE.md while the gate expects the run-root file. | Follow the emitted output contract and satisfy the actual gate. |
| `skills/agentic-build/references/operating-guide.md:22`, `runtime/templates/release.md:25` | Always-human release language conflicts with unattended executable release. | Exercise artifacts and guidance for both human and executable release profiles. |
| `skills/fusion-council/SKILL.md:37`, `agents/specialists/fusion-moderator.md:26`, `protocols/fusion.md:34` | Proposal examples omit the separate file option that activates snapshot/hash verification. | Follow the example, change the proposal, and require reveal refusal. |

Also correct the stale no-base-SHA statement in `protocols/source-control.md:10` and the
contradictory Antigravity enforcement rows in `protocols/harness-security.md`. Extend doc
tests to behavior, artifact values and preconditions; do not satisfy them by deleting examples.

**E1 P2 Evaluation — smoke scoring passes before verification is attempted.**
Paths: `evals/live_smoke.py:75–102`, `tests/test_live_smoke.py`.
Replaying the existing offline fixture produced all scores passing at `04_build`, status
active, with no VERIFICATION.md. The test currently expects that outcome. Require the
intended verified transition and legitimate pending human release gate, independent
verification, current evidence and completed accounting. Main must account for process
failure/timeout, not only final file contents. Add negative fixtures for stopping at build,
missing/stale/self verification, and wrong checkpoint, plus a genuine positive fixture.
Keep this smoke's stop-at-human-release contract distinct from unattended supervisor completion.

## Improvements to the agents

Improve the generated contracts and their tests before expanding the 50-role roster or
adding more generic instructions. Preserve domain expertise that is already useful.

1. Generate operational facts once: project/run/task/attempt identity, installed-role
   availability, access class, active stage/profile, artifact paths, owned paths, checks,
   required context and stop conditions. Source these from runtime data, not duplicated prose.
2. Use an explicit result envelope: task/run, status, changes or findings, acceptance ID to
   evidence mapping, executed checks and results, unresolved blockers, deviations, and next
   owner. Read-only workers return proposed evidence for the orchestrator to record.
3. Make verdicts exclusive: PASS requires no open blockers or majors and evidence for all
   required criteria; majors require CONDITIONAL plus the existing human waiver; blockers
   or failed required criteria mean FAIL. A check that was not run is unknown, never passed.
4. Separate optional assumptions from required decisions. Replace the statement in
   `protocols/agent-contract.md:60` and `protocols/plan-modes.md:29` that silence can resolve
   blocking gaps. Defaults apply only to reversible choices within existing authority;
   unanswered checkpoints remain unresolved while independent work continues.
5. Scale procedures to the task and available tools. A brownfield one-line fix needs no
   new platform scaffold. Solo fullstack execution still needs an independent review path.
   Evaluation metrics depend on output type; exact-label tasks can legitimately use exact
   comparison. Missing specialists/simulators should yield an explicit capability request
   or limitation, not invented work or evidence.

Verify these changes with deterministic packet/workflow tests first. An optional live
benchmark can later compare baseline and revised prompts on greenfield, brownfield,
marketing, review/remediation, missing capability and interrupted-handoff tasks. Pre-register
acceptance coverage, wrong-role actions, interventions, repeated failures, context usage,
cost and completion criteria. Fake-worker tests prove mechanics, not model performance.

## Repair sequence and dependencies

| Phase | Scope and finding IDs | Required result before continuing |
| --- | --- | --- |
| F0 Reproduce and track | Freeze baseline; create `docs/codebase-repair-progress.md`; map every finding to a regression and owner. | Distinguish reproduced, source-traced and proposed improvements; preserve existing green tests. |
| F1 Authority and trusted execution | A1–A6, S5. One integrator owns runtime admission, ledger decisions, owner commands, manifest boundaries and isolation proof. | Rejection, approval mismatch, absent authority, unsafe owner command paths and escaping manifest paths cannot pass their new negative tests. |
| F2 Durable runtime history | D1–D3, A7. Repair state/event transactions, execution identities, retry accounting and contributor history together. | Interruption and concurrency preserve one coherent auditable history, unique evidence and independent review. |
| F3 Accounting and checkout ownership | S1–S4. Coordinate runtime ledger validation with supervisor reservations and project identity. | No second writer, unsigned settlement, unknown-to-zero conversion or lost-record refund. |
| F4 Queue and recovery outcomes | S6–S9. Atomic requeue, failure recording, exit outcomes and source cursors. | Every interrupted handoff is recoverable; incomplete reconciliation blocks relaunch; failed work is visible to the host. |
| F5 Agent contracts and context | G1–G5 and agent improvements. Fix generators first, then role/skill/template references. | Saved commands address the correct run; each role gets permitted instructions and required context; actual documented workflows execute. |
| F6 Evaluation and regression closure | E1, A5 smoke boundary, expanded deterministic scenarios and complete cross-file tests. | The evaluator rejects plausible false success; every confirmed finding has a meaningful regression. |
| F7 Release review and pilot preparation | Independent review, full suite, platform/installer checks, docs/guarantees, optional authorized pilot. | No unresolved P1; P2 addressed or explicitly accepted with rationale. Claims match tests and actual activation state. |

F1–F3 alter shared runtime and ledger contracts and should be integrated sequentially.
F4's isolated polling work and documentation-example analysis can proceed independently
with nonoverlapping ownership. F5 depends on F2 for writer/attempt history; F6 can draft
negative fixtures early but completes after the behavior is fixed. Do not run competing
coding agents against `scripts/agentic_team.py` in one checkout.

## Acceptance and delivery

Keep the existing checks and add focused regressions beside the relevant tests. Avoid
assertions that merely restate implementation strings or bless an invalid fixture.

```text
python scripts/agentic_team.py validate
python scripts/agentic_team.py docs --check
python -m unittest discover -s tests -v
python evals/run_scenarios.py
python scripts/preflight_skills.py
```

Also verify installed helper/plugin packaging, source-free installed execution, reinstall
preservation and installer smokes. Run the declared Windows/macOS/Linux and Python
3.10/3.12/3.14 matrix where available; report any unrun cells. Test generated command quoting
with spaces and both documented shells. Do not launch real risky commands to test denial;
use harmless markers or intercepted subprocesses.

At every phase record commit, changed files, regression IDs, test results, unresolved
decisions and the next step. Update guarantee claims only when evidence supports them.
The existing progress file's statement that earlier review findings were fixed is history,
not proof that the new cases are covered. Keep offline-verified, pilot-verified and activated
states separate. A paid pilot still requires a concrete verified boundary, explicit budget,
stop conditions and the user's authorization for that execution.

Audit probes and logs were kept outside the repository under the local temporary directories
`agenticteam-audit-20261029` and `agentic-supervisor-audit-20261029`. Durable regression tests
should reproduce their described behavior without depending on those temporary paths.
Only this plan and its companion prompts were added by the audit; runtime fixes remain to do.
