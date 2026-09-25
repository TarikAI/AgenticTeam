# Owner guide — no coding required

You are the product owner. You describe the result, correct misunderstandings early, and make
the decisions that can hurt you if they go wrong: releasing, publishing, spending, credentials,
destructive changes, and legal commitments. The team does the technical work and must show
evidence for it.

You type a handful of commands yourself, in your own terminal. Everything else happens in your
coding tool (Claude Code, Codex, and so on), which this guide calls the *harness*.

## 1. What you need

- **Python 3.10 or newer that actually runs.** Check it:
  - Windows: open PowerShell and run `py -3 --version`. If that fails, install Python from
    python.org (tick "Add python.exe to PATH"). The `python` that Windows offers from the
    Microsoft Store is often only a stub that opens the Store; do not rely on it. In this guide,
    use `py -3` wherever a command says `python`.
  - macOS/Linux: `python3 --version`.
- **This repository** on your computer (download or `git clone`).
- **A project folder** for the product (it can be empty).
- **Git** in the project folder is recommended: the team records the exact commit it verified.

## 2. Install the team into your project

Windows (PowerShell, from the AgenticTeam folder). PowerShell blocks downloaded scripts by
default; the first line allows scripts for this window only:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install.ps1 -Target "C:\Users\YOU\Documents\my-platform" -Harness claude-code -Preset platform-core
```

macOS/Linux:

```bash
./scripts/install.sh --target ~/my-platform --harness claude-code --preset platform-core
```

`platform-core` is a compact delivery team; `full-platform` installs every engineering role and
specialist. Specialists do not all speak at once: the orchestrator activates them when your
product needs them. The README lists all presets and harnesses.

## 3. You start the run, in your own terminal

Starting a run creates your **owner token**, the secret that proves a decision came from you.
The token must never reach an agent, so you start the run yourself, in a normal terminal window,
not inside the harness chat.

Open a terminal in your project folder and run one of these (change the name):

```powershell
py -3 .agentic-team/bin/agentic_team.py init-run --project . --name "My Platform" --autonomy supervised --entry idea --context adaptive
```

```bash
python3 .agentic-team/bin/agentic_team.py init-run --project . --name "My Platform" --autonomy supervised --entry idea --context adaptive
```

Choices:

- `--autonomy`: `hitl` (you approve product, architecture, readiness, and release; the
  default), `supervised` (the team proceeds and pauses for deviations and external actions),
  or `autonomous` (the team continues through all reversible, in-scope work).
- `--entry`: `idea` (start from a description), `plan-given` (you already have a plan), or
  `execute-only` (build exactly the plan you supply).
- `--context`: `adaptive` (lighter paperwork for clear, bounded work) or `bmad-progressive`
  (a full document for every stage).

The command prints where it wrote your token, for example:

```text
Owner token written to C:\Users\YOU\.agentic-team\owner-tokens\20260925-101500-my-platform.3f9a1c2b7d4e.token
```

The file is `~/.agentic-team/owner-tokens/<run-id>.<uid>.token` in your home folder, outside
the project. Copy that **path** somewhere handy; you use it for every decision. Never open the
file to copy the token, never paste the token into the harness chat, a ticket, or a document,
and never put it on a command line. If an agent ever asks for it, say no.

## 4. Tell the team what to build

Open the project in your harness and say:

> Use `agentic-build`. The run is already started. My idea is: [users, problem, desired result,
> must-haves, constraints].

If you already have a plan (start the run with `--entry plan-given`):

> Use `agentic-build`. My plan is the source of truth: do not re-plan; validate what is
> necessary, then build, verify, and prepare the release.

`.agentic-team/CURRENT.md` points to the active run and stage. Each stage folder under
`.agentic-team/runs/<run-id>/` has a readable `CONTEXT.md`, and the stage documents (brief,
product requirements, architecture, verification, release plan, delivery report) appear there.
You never need to edit `state.json`.

## 5. See what is waiting for you

In your own terminal, in the project folder:

```powershell
py -3 .agentic-team/bin/agentic_team.py status --project .
py -3 .agentic-team/bin/agentic_team.py doctor --project .
```

(`python3` instead of `py -3` on macOS/Linux.)

- `status` shows the stage, the run status, and "Pending checkpoints: CP-001, …": decisions
  waiting for you. The team also shows each one in the chat with a recommendation,
  alternatives, impact, evidence, and a rollback plan. Ask for whichever is missing.
- `doctor` checks the installation and the run, and lists anything that needs attention
  (pending decisions, a blocked run, expired work, a broken record). It prints `OK` when there
  is nothing.

## 6. Decide: approve, reject, resolve, waive

Every decision command takes your name (`--by`) and the path of your token file
(`--token-file`). The token is read from the file, so it never appears on screen, in your shell
history, or in the process list.

PowerShell — set the path once per window, then decide:

```powershell
$TokenFile = "$HOME\.agentic-team\owner-tokens\<run-id>.<uid>.token"
py -3 .agentic-team/bin/agentic_team.py approve --project . --checkpoint CP-001 --by "Your Name" --decision "approved: go ahead" --token-file $TokenFile
py -3 .agentic-team/bin/agentic_team.py reject --project . --checkpoint CP-002 --by "Your Name" --decision "no: keep the free plan only" --token-file $TokenFile
py -3 .agentic-team/bin/agentic_team.py resolve --project . --checkpoint CP-002 --by "Your Name" --resolution "free plan only; pricing page removed" --token-file $TokenFile
```

bash:

```bash
TOKEN_FILE=~/.agentic-team/owner-tokens/<run-id>.<uid>.token
python3 .agentic-team/bin/agentic_team.py approve --project . --checkpoint CP-001 --by "Your Name" --decision "approved: go ahead" --token-file "$TOKEN_FILE"
python3 .agentic-team/bin/agentic_team.py reject --project . --checkpoint CP-002 --by "Your Name" --decision "no: keep the free plan only" --token-file "$TOKEN_FILE"
python3 .agentic-team/bin/agentic_team.py resolve --project . --checkpoint CP-002 --by "Your Name" --resolution "free plan only; pricing page removed" --token-file "$TOKEN_FILE"
```

If you leave out `--token-file` in an interactive terminal, you are asked for the token without
it being shown.

**Waive** skips one named requirement, with a reason. The team tells you the exact requirement
name when it needs one:

```powershell
py -3 .agentic-team/bin/agentic_team.py waive --project . --requirement stage-exit:00_intake:artifact:ASSUMPTIONS.md --reason "no open assumptions" --by "Your Name" --token-file $TokenFile
```

The same command lowers one task's risk level (`--requirement risk:<task-id> --level R1`) or lets
the team continue past a budget limit (`--requirement budget:<metric>`). Only you can do either.

`--by` must be your name; the command refuses the name of an installed agent.

## 7. What "blocked" means

- **Waiting for you** (`waiting-human`): a checkpoint is pending. The team stops at it (the
  command returns exit code 2) and waits for your approve or reject.
- **Blocked** (`blocked-rejection` or `blocked-failure`): the command returns exit code 3 and
  the team stops.
  - After a **rejection**, the run stays blocked until you `resolve` that checkpoint. Let the
    team fix the work first, check it, then run `resolve` with a short note on what changed.
    Approving some other checkpoint does not clear a rejection.
  - After **repeated failures** under `hitl`, a task has used its retries. Give it more
    (`reopen --task T --reason R --extend-retries 1 --by "Your Name" --token-file ...`) or
    drop it (`cancel --task T --reason R --by "Your Name" --token-file ...`).

## 8. How to stop the team

- To pause: do not approve. Nothing behind a pending checkpoint can proceed, and you can tell
  the team in the chat to stop.
- To end the run for good:

  ```powershell
  py -3 .agentic-team/bin/agentic_team.py close-run --project . --reason "stopping here"
  ```

  A closed run stops accepting work. Your files and the run's records stay.
- To stop the harness itself, use its own stop or cancel control.

## 9. Decisions that always come back to you

These seven hard gates hold in every autonomy profile, including `autonomous`:

1. production deployment;
2. public publishing or messaging real people;
3. spending money or creating paid resources;
4. handling real credentials or payment methods;
5. destructive or irreversible data operations;
6. installing software with broad system access or modifying system settings;
7. legal or contractual commitments.

Autonomy only changes how often the team asks you about everything else. It never removes these
gates. Before you approve one, ask for the recommendation, alternatives, evidence, rollback, and
the consequence of waiting.

## 10. What protects you, honestly

- **The CLI** refuses decisions without your token, refuses to leave a stage whose required
  documents or evidence are missing, and refuses to start a high-risk task until you approve its
  risk checkpoint. It runs on every harness.
- **Your decisions are signed.** Each one is appended to a signed, chained ledger in
  `~/.agentic-team/ledger/`. Editing files inside the project cannot fake an approval.
- **Harness rules and the guard hook** (Claude Code and Codex; other harnesses get narrower
  permission settings) stop agents from reading your token folder, editing the run's records,
  and running deploy/publish-style commands without your approval. On Codex, the hook loads only
  after you trust the project and review it with `/hooks`. On Pi, generic, and Antigravity
  installs these rules are instructions only.
- **Not a sandbox.** Agents run as your user. A determined or malicious program could still read
  your home folder. Hooks stop shortcuts and tricked agents; they do not stop hostile code. For
  unattended or autonomous runs, use real isolation: on Windows, run the harness in WSL2 (where
  Claude Code's sandbox works), a dev container, or a separate Windows account that cannot read
  your home folder. Keep production passwords and keys out of the project and its environment.

Details: [harness security](../protocols/harness-security.md).

## 11. Check that nobody forged a decision

Any time, and before a release:

```powershell
py -3 .agentic-team/bin/agentic_team.py audit verify --project . --by "Your Name" --token-file $TokenFile
```

```bash
python3 .agentic-team/bin/agentic_team.py audit verify --project . --by "Your Name" --token-file "$TOKEN_FILE"
```

It re-checks the signature on every decision and the chain of run events, and compares them with
the project's state. `OK: N signed decision(s); state matches the ledger` means everything lines
up. Anything else means stop the team and investigate before approving more.

## Useful instructions for the team

- "Give me evidence-backed status: complete, unfinished, blocked, at risk, and decisions needed."
- "Run Fusion mode with product, architecture, UX, security, and cost perspectives."
- "Show the integrated product and reproduce the critical tests."
- "Do not publish or deploy; prepare everything up to the approval gate."
- "Run independent verification. The builder cannot be the verifier."

If the team loops or becomes vague, ask it to read `CURRENT.md`, run `status --brief` and
`doctor`, recover expired leases, and report the exact blocking state.
