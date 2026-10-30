# AgenticTeam codebase repair progress

This record tracks the repairs to the findings in the
[audit and repair plan](codebase-audit-and-repair-plan.md), reviewed at `4e27df2`.
The earlier [supervisor progress](supervisor-progress.md) file is implementation
history. It does not show that the cases below were previously verified.

Branch `agenticteam-repairs`, built from `main` (`4e27df2`). Nothing has been pushed or merged
into `main`. No paid worker, live pilot, network call, or persistent host task was run.

## Where it stands

Every finding in the plan is reproduced by a regression that fails on `4e27df2` for the stated
reason and passes on this branch. No finding is still open. The repair is offline-verified on
Windows only:

- **Python 3.14:** full suite, validation, generated docs, scenarios, and preflight.
- **Python 3.11:** full suite.

It has not been run on macOS, Linux, or Python 3.10; CI covers those once the branch is pushed.
It is not pilot-verified.

The work was split by file ownership:

| Owner | Files and branch |
| --- | --- |
| Runtime integrator | `scripts/agentic_team.py` and `scripts/findings_to_tasks.py`, committed on this branch |
| Supervisor agent | `scripts/agentic_supervisor.py` and its tests, on branch `repairs-supervisor` |
| Docs/evals agent | `agents/`, `skills/`, `protocols/`, `runtime/templates/`, `README.md`, and `evals/live_smoke.py`, on branch `repairs-docs-evals` |

Both side branches are merged into this one.

## Findings

"Fails on 4e27df2" means the regression was run against a checkout of the baseline and failed
for the finding's reason.

| ID | Status | Phase | Regression | Files | Commit |
| --- | --- | --- | --- | --- | --- |
| A1 | fixed | F1 | `test_repairs_authority.SignedRejectionTests` (5) | runtime | `8f43da7` |
| A2 | fixed | F1 | `test_repairs_authority.ExecutionGateTests` (3) | runtime | `8f43da7` |
| A3 | fixed | F1 | `test_repairs_authority.ActionApprovalTests` (2, through the installed CLI) | runtime | `8f43da7` |
| A4 | fixed | F1 | `test_repairs_authority.GuardFailClosedTests` (3) | runtime | `8f43da7` |
| A5 | fixed | F1/F6 | Supervisor: `test_supervisor.OwnerCommandTests`; smoke: `test_live_smoke.OwnerBoundaryTests` | supervisor, `evals/live_smoke.py`, operator guide | `7966d28`, `af10bc6` |
| A6 | fixed | F1 | `test_repairs_authority.ManifestContainmentTests` (3; the symlink case is skipped where symlinks are unavailable) | runtime | `8f43da7` |
| A7 | fixed | F2 | `test_repairs_history.IndependenceTests` (2) | runtime | `8f43da7` |
| D1 | fixed | F2 | `test_repairs_history.ExecIdentityTests` (3) | runtime | `8f43da7` |
| D2 | fixed | F2 | `test_repairs_history.EventTransactionTests` (3) | runtime | `8f43da7` |
| D3 | fixed | F2 | `test_repairs_history.ReopenRetryTests` (2) | runtime | `8f43da7` |
| S1 | fixed | F3 | `test_supervisor.CheckoutBindingTests` (3) | supervisor | `1328378` |
| S2 | fixed | F3 | `test_supervisor.VerifiedUsageTests` (2); owner audit: `test_repairs_history.SignedUsageAuditTests` | supervisor, runtime `audit_verify` | `1328378`, this commit |
| S3 | fixed | F3 | `test_supervisor.UnknownUsdTests` (2) | supervisor, runtime `transcript_usage` | `1328378` |
| S4 | fixed | F3 | `test_supervisor.OrphanReservationTests` (2) | supervisor | `1328378` |
| S5 | fixed (mocked probes) | F1 | `test_supervisor.IsolationBindingTests` (2) | supervisor | `c2ff176` |
| S6 | fixed | F4 | `test_supervisor.DurableRequeueTests` (2) | supervisor | `647900f` |
| S7 | fixed | F4 | `test_supervisor.FailureOutcomeTests` (2) | supervisor | `647900f` |
| S8 | fixed | F4 | `test_supervisor.FailureReconciliationTests` (2) | supervisor | `647900f` |
| S9 | fixed | F4 | `test_supervisor.PollCursorTests` | supervisor | `647900f` |
| G1 | fixed | F5 | `test_repairs_packets.AccessAwarePacketTests` | runtime | `8f43da7` |
| G2 | fixed | F5 | `test_repairs_packets.RunPinningTests` (2: packets run through Git Bash and PowerShell in a path with spaces; findings-to-tasks `--commands` and `--apply`) | runtime, `findings_to_tasks.py` | `8f43da7` |
| G3 | fixed | F5 | `test_repairs_packets.SectionContextTests` (3) | runtime | `8f43da7` |
| G4 | fixed | F5 | `test_repairs_packets.SpecialistActivationTests` | runtime | `8f43da7` |
| G5 | fixed | F5 | `test_doc_workflows` (13 tests: each documented workflow run as written on a fresh install) | agents, skills, protocols, templates, README, quickstart | `91da741`, `187b27c` |
| E1 | fixed | F6 | `test_live_smoke.SmokeJourneyTests` and its negative cases | `evals/live_smoke.py` | `af10bc6` |

## How each repair works

Each finding below has a short note on the enforced contract and how existing runs migrate.

- **Authority (A1–A4):**
  - The effective state of a decided checkpoint is the last signed decision about it.
  - New approvals carry a fingerprint of the checkpoint's kind, task, stage, risk, action, target, and question. An approval does not follow its ID to another checkpoint, and it does not survive an edit to what it covers. Approvals signed before this change carry no fingerprint and keep counting.
  - The run gate (rejection or closure) applies to every new process, including the checks that `complete` runs. It is derived from the ledger and the `run-closed` event, not from `status`.
  - `exec` and the guard hook share one admission function. Its rules:
    - A command that matches a rule needs a task declared for that rule's action.
    - The task's risk must be at least the rule's.
    - From R3 up, the command also needs a signed approval covering that action, target, and risk.
  - Once a risky rule matches, the guard denies whenever the approval context cannot be read.
- **Manifest containment (A6):** every path that install or uninstall would touch is validated before the first change. That covers generated files, owned settings, the skill folder, and skill names. The whole operation is refused on the first unsafe path.
- **History (D1–D3):**
  - **Exec IDs:** reserved in state, with an event, before the command starts. Evidence files are created exclusively. A result that arrives after its claim ended is kept and marked `stale_claim`, and it never counts as a passing check.
  - **Interrupted appends:** a tail written by an interrupted append is moved to `events.interrupted.jsonl`, and the recovery is recorded as an event. History that does not chain up to the head recorded in state is refused, whether it was edited or truncated.
  - **Reopen:** reopening a claim is a failed attempt. It keeps the claimant, spends the retry budget, and escalates on a repeated reason.
- **Independence (A7):** each task keeps `contributors`, which survive reopen, reassignment, and completion. Writers of source remediation in `05_verify` count as builders for the final verdict.
- **Packets (G1–G4):**
  - Packets carry project, run, task, and attempt identity, the owner's access class, and a result envelope.
  - Roles without a shell get report-only instructions; the orchestrator records their result.
  - Commands are pinned with `--project` and `--run`, quoted for both Bash and PowerShell.
  - Requested `#sections` are extracted before budgeting, and required inputs are budgeted before background material. Missing or cut required material produces a `Context condition: INCOMPLETE` notice.
  - Specialist work satisfies only the activation it was added for.
- **Supervisor and accounting (S1–S9, A5 owner side):** these are described in the [operator guide](supervisor-operator-guide.md) and guarantees G23/G24. New owner commands are `bind`, `recover-orphan`, and `acknowledge`. The checkout's store binding lives in `.agentic-team/supervisor/binding.json`.
- **Owner usage audit (S2):** `audit verify` also checks every metered usage source and the running totals against the signed `usage` ledger records.

## Independent review (F7)

A read-only reviewer checked the integrated diff against every finding. It ran its probes in
temporary copies. It confirmed ten defects that remained after the first repair pass. Each one is
now fixed, and each has a regression that fails without its fix:

| Review finding | Severity | Fix | Regression |
| --- | --- | --- | --- |
| A chained command (`fly deploy && docker push ...`) rode one approval | P1 | `command_refusal` checks every matching rule, in both `exec` and the guard | `ActionApprovalTests.test_an_approved_command_cannot_carry_a_chained_one` |
| A requeued job that had run was recreated when its record went missing, refunding its spend and freeing the checkout | P1 | `repair_requeue` does not recreate a job with receipts, a reservation, the checkout, or an orphan hold | `OrphanReservationTests.test_a_requeued_job_that_ran_is_not_recreated_when_its_record_goes` |
| A rejected checkpoint whose status was edited back to pending could be approved | P2 | `approve` and `reject` check the effective status | `SignedRejectionTests.test_re_approving_an_edited_rejection_is_refused` |
| Restoring the pre-close state and events reopened a closed run | P2 | `close-run` also records an unsigned `close` entry in the owner ledger; the audit reports a state that ignores it | `ExecutionGateTests.test_restoring_pre_close_state_and_events_does_not_reopen` |
| A torn last event line read as a closure, and the audit crashed on it | P2 | Only positive evidence closes a run; `verify_events` reports a torn tail | `ExecutionGateTests.test_a_torn_event_line_does_not_read_as_closure` |
| A usage ID could be reused after state was cleared, hiding the earlier spend | P2 | IDs are numbered from the signed ledger; the audit flags duplicate subjects and totals every signed record | `SignedUsageAuditTests` |
| A `# comment` in a fenced code block ended the requested section | P2 | Lines inside code fences are not headings | `SectionContextTests.test_a_comment_in_a_code_block_does_not_end_the_section` |
| PowerShell owner commands did not set `AGENTIC_TEAM_HOME` when the path had no spaces | P2 | The assigned value is always a string literal | `OwnerCommandTests.test_the_powershell_home_assignment_takes_effect` |
| The smoke scorer passed a verifier that never ran the tests | P2 | It requires a passing test run by the verifier, and `--verifies` covering the build tasks | `test_live_smoke.SmokeJourneyTests.test_a_verifier_that_never_ran_the_tests_fails` |
| `findings-to-tasks --shell powershell` lines failed in Windows PowerShell 5.1 when values contained double quotes | P2 | A printed `Q` helper escapes embedded quotes only where the running PowerShell needs it | `RemediationShellTests` (executed in `powershell.exe` 5.1) |

The reviewer also raised several P3 items:

- **Fixed:** `shell_word` refuses a path that contains `'` instead of falling back to expanding double quotes.
- **Fixed:** the self-verification smoke test now scores the run instead of returning early.
- **Accepted as limits, not fixed:**
  - The smoke scorer compares completion times at one-second resolution.
  - The scorer reads worker-writable state, with authority cross-checked through the owner ledger.
  - The smoke worker timeout does not kill grandchild processes.

## Agent quality improvements

These are tracked separately from reproduced defects.

| Item | Status | Evidence |
| --- | --- | --- |
| 1. Operational facts generated once | done for task packets | `AccessAwarePacketTests`, `RunPinningTests` |
| 2. Explicit result envelope | done in packets; read-only roles return it to the orchestrator | `AccessAwarePacketTests` |
| 3. Exclusive verdicts | done (definition of done, verification template, agentic-verify, qa-lead) | `test_doc_workflows.VerdictVocabularyTests` |
| 4. Silence never resolves a blocking decision | done (`agent-contract.md`, `plan-modes.md`, packet stop conditions) | `test_doc_workflows.DecisionContractTests` |
| 5. Procedures scaled to the task and capability | partial: packets name the access class and the stop conditions for missing capability; role texts were not rewritten | none beyond the packet tests |

None of this shows that model behavior improved. That would need the optional benchmark the plan
describes, run with explicit authorization.

## Known limits and decisions for the owner

- **Supervisor checkout binding:** the binding lives in the checkout so every path alias finds it, which means a worker can delete it. After that, a second store the owner runs could bind the checkout. This is documented as G23's bypass. A binding outside the checkout cannot be found from every alias.
- **Orphan recovery:** after `recover-orphan`, the orphan's run stays current, so the next job launches only once the owner closes that run. The supervisor never closes runs.
- **Isolation proof (S5):** only tested with mocked probes. No real OS or container boundary was verified.
- **Live-smoke owner copy (A5):** this is not an OS boundary. A worker running as the same user can still reach the owner home.
- **`usage --require-usd`:** not added to the CLI. The supervisor checks the transcript itself before metering.

## Test evidence

Recorded on Windows 11, at the integration commit:

| Check | Result |
| --- | --- |
| `validate` | OK: 50 agents, 9 presets, 13 harnesses |
| `docs --check` | current |
| Full unit suite, Python 3.14 | 375 tests OK, 1 skip (symlink creation needs privileges on this host), 750 s |
| Full unit suite, Python 3.11 | 375 tests OK, 1 skip, 725 s |
| `evals/run_scenarios.py` | 8/8 passed |
| `scripts/preflight_skills.py` | exit 0 (the optional `design-architect` skill is absent) |

## Next step

1. With the owner's authorization, push the branch so CI runs on macOS, Linux, and Python 3.10, then merge into `main`.
2. The paid pilot remains a separate decision. It needs a verified whole-worker boundary, a chosen model, run, attempt and aggregate budgets, a timeout, and stop conditions.
