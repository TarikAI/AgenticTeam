"""Documented agent workflows, executed as written against fresh installations (finding G5).

Each test reads the command or contract out of the shipped document, installs AgenticTeam
through the CLI into a new folder (no test-helper policy, so no injected budget), runs what the
document says, and checks the resulting state and artifacts, not the presence of a flag.
Placeholders (`<run-id>`, `<findings.json>`, ...) are the only substitutions.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

from helpers import ROOT, team
from test_regressions import PASSING_CHECK

TOKEN_HINT = "owner-tokens"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def code_lines(relative: str, needle: str) -> list[str]:
    """Lines inside fenced code blocks of a document that contain `needle`."""
    lines, inside = [], False
    for line in read(relative).splitlines():
        if line.strip().startswith("```"):
            inside = not inside
            continue
        if inside and needle in line:
            lines.append(line.strip())
    return lines


def inline_commands(relative: str, prefix: str) -> list[str]:
    """Backtick-quoted commands in prose that start with `prefix` (wrapped lines joined)."""
    found = re.findall(r"`(" + re.escape(prefix) + r"[^`]*)`", read(relative), flags=re.DOTALL)
    return [" ".join(item.split()) for item in found]


def argv_of(line: str, substitutions: dict[str, str] | None = None) -> list[str]:
    """A documented command line as argv, with the interpreter replaced by this one.

    Placeholders are replaced after splitting, word by word, so a substituted Windows path or
    a quoted check command reaches the CLI unchanged.
    """
    def token(text: str) -> str:  # `<owned path>` stays one word through shlex
        return re.sub(r"<([^<>]*)>", lambda match: "<" + match.group(1).replace(" ", "\x00") + ">", text)

    parts = shlex.split(token(line), posix=True)
    for old, new in (substitutions or {}).items():
        parts = [part.replace(token(old), new) for part in parts]
    parts = [part.replace("\x00", " ") for part in parts]
    if parts[0] == "py":
        parts = parts[2:] if parts[1].startswith("-") else parts[1:]
    elif parts[0] in {"python", "python3"}:
        parts = parts[1:]
    return [sys.executable, *parts]


class Fresh:
    """A project installed through the CLI, exactly as a user installs it."""

    def __init__(self, case: unittest.TestCase, preset: str = "platform-core", harness: str = "claude-code", git: bool = False) -> None:
        self.project = Path(tempfile.mkdtemp(prefix="doc-flow-"))
        case.addCleanup(shutil.rmtree, self.project, True)
        if git:
            for args in (("init", "-q"), ("config", "user.email", "doc@example.invalid"), ("config", "user.name", "Doc"),
                         ("commit", "-q", "--allow-empty", "-m", "base")):
                subprocess.run(["git", *args], cwd=self.project, check=True, capture_output=True)
        result = subprocess.run([sys.executable, str(ROOT / "scripts" / "agentic_team.py"), "install", str(self.project),
                                 "--harness", harness, "--preset", preset], capture_output=True, text=True)
        case.assertEqual(result.returncode, 0, result.stderr)
        self.bus = self.project / ".agentic-team"
        case.assertFalse((self.bus / "config" / "policies.local.json").exists(), "a fresh install has no local policy")
        self.cli = [sys.executable, str(self.bus / "bin" / "agentic_team.py")]

    def run(self, argv: list[str], stdin: str | None = None) -> subprocess.CompletedProcess:
        """Run a documented argv in the project folder (relative `.agentic-team/bin/...` resolves there)."""
        return subprocess.run(argv, cwd=self.project, capture_output=True, text=True, input=stdin, env=dict(os.environ))

    def cli_run(self, *args: str) -> subprocess.CompletedProcess:
        return self.run([*self.cli, *args])

    def ok(self, case: unittest.TestCase, *args: str) -> str:
        result = self.cli_run(*args)
        case.assertEqual(result.returncode, 0, f"{args}: {result.stderr}")
        return result.stdout

    def start(self, case: unittest.TestCase, autonomy: str = "autonomous", context: str = "adaptive", entry: str = "execute-only",
              run_id: str = "doc") -> Path:
        self.ok(case, "init-run", "--project", ".", "--name", "Doc", "--run-id", run_id, "--autonomy", autonomy,
                "--entry", entry, "--context", context, "--budget", "usd=5")
        return self.bus / "runs" / run_id

    def state(self, run: Path) -> dict:
        return team.load_state(run)

    def token_file(self, run: Path) -> Path:
        return team.owner_token_file(self.state(run))

    def build(self, case: unittest.TestCase, owner: str = "fullstack-engineer", task: str = "T1") -> None:
        (self.project / "src").mkdir(exist_ok=True)
        (self.project / "src" / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
        self.ok(case, "add-task", "--project", ".", "--id", task, "--title", "Build", "--owner", owner, "--action", "build",
                "--target", "local", "--path", "src", "--check", PASSING_CHECK)
        self.ok(case, "claim", "--project", ".", "--task", task, "--agent", owner)
        self.ok(case, "complete", "--project", ".", "--task", task, "--agent", owner, "--run-checks", "--evidence", "file:src/app.py")

    def to_verify(self, case: unittest.TestCase, run: Path) -> None:
        self.build(case)
        self.ok(case, "advance", "--project", ".")
        case.assertEqual(self.state(run)["stage"], "05_verify")

    def verdict(self, run: Path, verifier: str = "qa-lead") -> None:
        (run / "VERIFICATION.md").write_text(
            f"Verdict: PASS\nVerifier: {verifier}\nVerified-SHA: none\n\n# Verification\n\nAC-1 checked: T1-1\n", encoding="utf-8")


class StartupBudgetTests(unittest.TestCase):
    """README.md and skills/agentic-build/SKILL.md: the human starts a supervised run on a fresh install."""

    def test_documented_init_run_lines_start_a_run_on_a_fresh_install(self) -> None:
        cases = [(doc, line) for doc in ("README.md", "skills/agentic-build/SKILL.md")
                 for line in code_lines(doc, "agentic_team.py init-run")]
        self.assertGreaterEqual(len(cases), 4, cases)
        for doc, line in cases:
            with self.subTest(doc=doc, line=line):
                fresh = Fresh(self)
                result = fresh.run(argv_of(line))
                self.assertEqual(result.returncode, 0, result.stderr)
                run = team.find_run(fresh.project, None)
                state = fresh.state(run)
                self.assertEqual(state["autonomy"], "supervised")
                self.assertGreater(float(state["budgets"].get("usd", 0)), 0, "the documented line must set the ceiling")
                self.assertIn(TOKEN_HINT, result.stdout + result.stderr, "init-run tells the human where the token is")
                self.assertTrue(fresh.token_file(run).is_file())


class ArtifactInstructionTests(unittest.TestCase):
    """cto-architect and every `scaffold --artifact` the shipped docs tell an agent to run."""

    DOCS = ["README.md", *(str(path.relative_to(ROOT)).replace("\\", "/") for folder in ("agents", "skills", "protocols")
                           for path in sorted((ROOT / folder).rglob("*.md")))]

    def test_every_documented_scaffold_creates_its_artifact(self) -> None:
        named = {(doc, name) for doc in self.DOCS for name in re.findall(r"scaffold [^`\n]*--artifact ([A-Z][A-Z0-9-]*\.md)", read(doc))}
        self.assertIn(("agents/specialists/release-manager.md", "RELEASE.md"), named)
        fresh = Fresh(self, preset="full-company")
        run = fresh.start(self, autonomy="hitl", context="bmad-progressive", entry="idea")
        for doc, name in sorted(named):
            with self.subTest(doc=doc, artifact=name):
                (run / name).unlink(missing_ok=True)
                result = fresh.cli_run("scaffold", "--project", ".", "--artifact", name)
                self.assertEqual(result.returncode, 0, f"{doc} tells an agent to scaffold {name}: {result.stderr}")
                self.assertTrue((run / name).is_file())

    def test_cto_architect_writes_an_architecture_the_02_solution_exit_accepts(self) -> None:
        role = read("agents/leadership/cto-architect.md")
        step = re.search(r"\n4\. (.*?)\n5\. ", role, flags=re.DOTALL).group(1)
        self.assertNotIn("scaffold --artifact ARCHITECTURE.md", step, "ARCHITECTURE.md has no registered template")
        path = re.search(r"`(\.agentic-team/runs/<run-id>/ARCHITECTURE\.md)`", step).group(1)
        sections = [line.strip()[2:].split(":", 1)[0].split(" with ", 1)[0] for line in step.splitlines() if line.strip().startswith("- ")]
        self.assertGreaterEqual(len(sections), 6, sections)
        fresh = Fresh(self, preset="full-company")
        run = fresh.start(self, autonomy="hitl", context="bmad-progressive", entry="idea")
        problems = team.stage_exit_problems(fresh.project, run, fresh.state(run), "02_solution")
        self.assertIn("ARCHITECTURE.md is missing", " ".join(problems))
        target = fresh.project / path.replace("<run-id>", run.name)
        target.write_text("# Architecture\n\n" + "\n".join(f"## {title}\n\nDecided for AC-1.\n" for title in sections), encoding="utf-8")
        problems = team.stage_exit_problems(fresh.project, run, fresh.state(run), "02_solution")
        self.assertEqual([item for item in problems if "ARCHITECTURE" in item], [], problems)


class RemediationExampleTests(unittest.TestCase):
    """qa-lead and code-reviewer: filing remediation as the role documents yields runnable tasks."""

    FINDINGS = [{"severity": "major", "file": "src/app.py", "line": 1, "claim": "VALUE is wrong",
                 "scenario": "import app; app.VALUE == 1", "fix": "set VALUE to 2"}]

    def setUp(self) -> None:
        self.fresh = Fresh(self)
        self.run_dir = self.fresh.start(self)
        self.fresh.to_verify(self, self.run_dir)
        self.findings = self.run_dir / "05_verify" / "findings.json"
        self.findings.write_text(json.dumps(self.FINDINGS), encoding="utf-8")

    def assert_runnable(self, task_id: str) -> None:
        task = self.fresh.state(self.run_dir)["tasks"][task_id]
        access = team.installed_agents(self.fresh.project)[task["owner"]]["access"]
        self.assertIn(access, team.WRITE_ACCESS, task)
        self.assertEqual(task["stage"], "05_verify")
        self.assertEqual(task["checks"], [PASSING_CHECK])
        self.fresh.ok(self, "claim", "--project", ".", "--task", task_id, "--agent", task["owner"])
        self.fresh.ok(self, "complete", "--project", ".", "--task", task_id, "--agent", task["owner"], "--run-checks",
                      "--evidence", "file:src/app.py")
        self.assertEqual(self.fresh.state(self.run_dir)["tasks"][task_id]["status"], "completed")

    def test_findings_to_tasks_examples_file_a_runnable_task(self) -> None:
        for role in ("agents/engineering/qa-lead.md", "agents/engineering/code-reviewer.md"):
            examples = inline_commands(role, "findings-to-tasks ")
            self.assertTrue(examples, role)
            for example in examples:
                with self.subTest(role=role, example=example):
                    before = set(self.fresh.state(self.run_dir)["tasks"])
                    line = ".agentic-team/bin/agentic_team.py " + example
                    argv = argv_of(line, {"<findings.json>": str(self.findings), "<project test command>": PASSING_CHECK})
                    result = self.fresh.run(argv)
                    self.assertEqual(result.returncode, 1, f"findings exist, so exit 1 after adding: {result.stderr}")
                    added = sorted(set(self.fresh.state(self.run_dir)["tasks"]) - before)
                    self.assertEqual(len(added), 1, result.stdout + result.stderr)
                    self.assertIn(f"Added 1 remediation task(s) to stage 05_verify", result.stdout)
                    self.assert_runnable(added[0])

    def test_qa_lead_own_remediation_example_is_runnable(self) -> None:
        examples = [item for item in inline_commands("agents/engineering/qa-lead.md", "add-task ") if "<writer-role>" in item]
        self.assertEqual(len(examples), 1, examples)
        line = ".agentic-team/bin/agentic_team.py " + examples[0] + " --project ."
        argv = argv_of(line, {"<writer-role>": "fullstack-engineer", "<owned path>": "src", "<repro command>": PASSING_CHECK,
                              "<id>": "FIX-1", "<title>": "Fix VALUE", "<task>": "T1"})
        result = self.fresh.run(argv)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_runnable("FIX-1")


class ReleaseContractTests(unittest.TestCase):
    """release-manager's output contract, the release template, and the operating guide, per release profile."""

    def release_path(self, run: Path) -> Path:
        output = read("agents/specialists/release-manager.md").split("## Output", 1)[1].split("##", 1)[0]
        documented = re.search(r"`(\.agentic-team/runs/<run-id>/[^`]*RELEASE\.md)`", output).group(1)
        return run.parents[2] / documented.replace("<run-id>", run.name)

    def fill(self, text: str, approval: str) -> str:
        """Fill the release template as an agent would: every marker answered, the approval per the profile."""
        head = text.partition("## Approval")[0]
        return re.sub(r"\{\{[^}]*\}\}", "Recorded for this release.", head) + "## Approval\n\n" + approval + "\n"

    def to_release(self, fresh: Fresh, autonomy: str) -> Path:
        run = fresh.start(self, autonomy=autonomy, context="bmad-progressive")
        fresh.to_verify(self, run)
        fresh.verdict(run)
        fresh.ok(self, "advance", "--project", ".")
        self.assertEqual(fresh.state(run)["stage"], "06_release")
        fresh.ok(self, "scaffold", "--project", ".", "--artifact", "RELEASE.md")
        self.assertTrue(self.release_path(run).is_file(), "release-manager's output path is where scaffold writes")
        return run

    def approval_guidance(self) -> str:
        template = read("runtime/templates/release.md")
        return template.split("## Approval", 1)[1]

    def test_the_human_release_profile(self) -> None:
        guidance = self.approval_guidance()
        self.assertIn("human", guidance)
        fresh = Fresh(self, preset="full-company")
        run = self.to_release(fresh, "autonomous")
        # release-manager step 7: the approval question is a decision checkpoint whose id RELEASE.md records.
        out = fresh.ok(self, "checkpoint", "--project", ".", "--kind", "decision", "--question", "Release 1.0 to production?",
                       "--recommendation", "Release", "--risk", "R3", "--alternatives", "Hold", "--impact", "Users get 1.0",
                       "--evidence", "VERIFICATION.md", "--rollback", "Redeploy 0.9")
        checkpoint = out.strip().splitlines()[-1]
        path = self.release_path(run)
        path.write_text(self.fill(path.read_text(encoding="utf-8"), f"Human release checkpoint: {checkpoint}"), encoding="utf-8")
        self.assertEqual([item for item in team.stage_exit_problems(fresh.project, run, fresh.state(run), "06_release") if "RELEASE" in item], [])
        result = fresh.cli_run("advance", "--project", ".")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(fresh.state(run)["status"], "waiting-human")
        row = self.guide_row()
        self.assertIn("human", row)

    def test_the_executable_release_profile(self) -> None:
        guidance = self.approval_guidance()
        self.assertIn("unattended", guidance, "the template must say what the approval section holds without a human checkpoint")
        row = self.guide_row()
        self.assertNotIn("always human", row)
        self.assertIn("unattended", row)
        fresh = Fresh(self, preset="full-company")
        run = self.to_release(fresh, "unattended")
        # release-manager step 4: the rollback rehearsal, run exactly as documented.
        role = read("agents/specialists/release-manager.md")
        rehearsal = inline_commands("agents/specialists/release-manager.md", "add-task --id RB")
        self.assertEqual(len(rehearsal), 1, role)
        fresh.ok(self, *argv_of(".agentic-team/bin/agentic_team.py " + rehearsal[0] + " --project .",
                                {"<rollback command>": PASSING_CHECK})[2:])
        fresh.ok(self, "claim", "--project", ".", "--task", "RB", "--agent", "release-manager")
        fresh.ok(self, "complete", "--project", ".", "--task", "RB", "--agent", "release-manager", "--run-checks",
                 "--evidence", "note:rolled back and forward locally")
        path = self.release_path(run)
        path.write_text(self.fill(path.read_text(encoding="utf-8"), "Executable release (unattended, no task above R1); rollback rehearsal RB."),
                        encoding="utf-8")
        self.assertEqual(team.executable_release_problems(fresh.project, run, fresh.state(run)), [])
        fresh.ok(self, "advance", "--project", ".")
        state = fresh.state(run)
        self.assertEqual(state["stage"], "07_learn")
        self.assertFalse([item for item in state["checkpoints"] if item["kind"] == "stage"], "no human click under unattended")

    def guide_row(self) -> str:
        rows = [line for line in read("skills/agentic-build/references/operating-guide.md").splitlines() if line.startswith("| 06_release")]
        self.assertEqual(len(rows), 1)
        return rows[0]


class FusionSealingTests(unittest.TestCase):
    """The proposal examples seal each proposal: a proposal edited after its submission blocks the reveal."""

    SOURCES = [
        ("skills/fusion-council/SKILL.md", "fenced"),
        ("protocols/fusion.md", "fenced"),
        ("agents/specialists/fusion-moderator.md", "inline"),
    ]
    PROSE = {"<id>": "council-1", "<q>": "Which plan?", "<a>": "product-manager", "<b>": "cto-architect"}

    def commands(self, doc: str, style: str) -> tuple[str, str]:
        if style == "fenced":
            init = code_lines(doc, "fusion-init")[0]
            proposal = next(line for line in code_lines(doc, "fusion-submit") if "--kind proposal" in line)
            return init, proposal
        init = ".agentic-team/bin/agentic_team.py " + inline_commands(doc, "fusion-init ")[0] + " --project ."
        proposal = ".agentic-team/bin/agentic_team.py " + inline_commands(doc, "fusion-submit --fusion <id> --kind proposal")[0] + " --project ."
        for old, new in self.PROSE.items():
            init, proposal = init.replace(old, new), proposal.replace(old, new)
        return init, proposal

    def test_following_the_proposal_example_seals_the_proposal(self) -> None:
        for doc, style in self.SOURCES:
            with self.subTest(doc=doc):
                fresh = Fresh(self, preset="full-company")
                run = fresh.start(self, run_id="council-run")
                init, proposal = self.commands(doc, style)
                result = fresh.run(argv_of(init))
                self.assertEqual(result.returncode, 0, result.stderr)
                session = fresh.state(run)["fusion_sessions"][0]
                contributors = session["contributors"]
                first = re.search(r"--agent (\S+)", proposal).group(1)
                self.assertIn(first, contributors)
                order = [first] + [name for name in contributors if name != first]

                folder = f".agentic-team/runs/{run.name}/_fusion/{team.slug(session['id'])}/proposals"

                def argv(agent: str) -> list[str]:
                    # Only the moderator's prose leaves the path as <path>; its procedure names the file.
                    return argv_of(proposal.replace(first, agent).replace("<run-id>", run.name), {"<path>": f"{folder}/{agent}.md"})

                documented = argv(order[0])
                self.assertIn("--file", documented, f"{doc}: the proposal example does not pass --file, so nothing is sealed")
                path = documented[documented.index("--file") + 1]
                parent = fresh.project
                for part in Path(path).parts:  # exact case, so the path also works on case-sensitive filesystems
                    self.assertIn(part, os.listdir(parent), f"{doc}: documented path component {part!r} does not exist as written")
                    parent = parent / part
                result = fresh.run(documented)
                self.assertEqual(result.returncode, 0, result.stderr)
                record = fresh.state(run)["fusion_sessions"][0]["submissions"]["proposal"][order[0]]
                self.assertIn("sha256", record, f"{doc}: the documented proposal submission does not seal the file")
                sealed = fresh.project / record["file"]

                def submit(agent: str) -> subprocess.CompletedProcess:
                    return fresh.run(argv(agent))

                sealed.write_text(sealed.read_text(encoding="utf-8") + "\nRewritten after reading the others.\n", encoding="utf-8")
                for agent in order[1:-1]:
                    self.assertEqual(submit(agent).returncode, 0)
                refused = submit(order[-1])
                self.assertEqual(refused.returncode, 1, refused.stdout)
                self.assertIn("changed after submission", refused.stderr)
                self.assertEqual(fresh.state(run)["fusion_sessions"][0]["status"], "proposals", "the council must not reveal")


class ProtocolStatementTests(unittest.TestCase):
    """Protocol statements about what the runtime and harness enforce, checked against what they do."""

    def test_source_control_base_sha_statement_matches_the_runtime(self) -> None:
        text = read("protocols/source-control.md")
        base = text.split("## Base", 1)[1].split("##", 1)[0]
        self.assertNotIn("does not store a base", base)
        fresh = Fresh(self, git=True)
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=fresh.project, capture_output=True, text=True, check=True).stdout.strip()
        fresh.start(self)
        status = json.loads(fresh.ok(self, "status", "--project", ".", "--json"))
        self.assertEqual(status["base_sha"], head)
        bullets = [" ".join(item.split()) for item in re.split(r"\n- ", base)]
        recorded = next((item for item in bullets if "base_sha" in item), "")
        self.assertTrue(recorded.startswith("[runtime]"), f"the protocol must say the runtime records base_sha: {bullets}")

    def test_harness_enforcement_table_matches_installed_hooks(self) -> None:
        rows = [line for line in read("protocols/harness-security.md").splitlines() if line.startswith("| `")]
        seen: dict[str, str] = {}
        for row in rows:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            for harness in re.findall(r"`([a-z-]+)`", cells[0]):
                self.assertNotIn(harness, seen, f"{harness} has two contradictory rows")
                seen[harness] = cells[1]
        self.assertEqual(set(seen), set(json.loads(read("team.json"))["harnesses"]))
        for harness, enforced in sorted(seen.items()):
            with self.subTest(harness=harness):
                claims_hook = "guard hook" in enforced
                self.assertEqual(claims_hook, harness in team.HOOKED_HARNESSES, enforced)
                if not claims_hook:
                    continue
                fresh = Fresh(self, harness=harness)
                settings = fresh.project / team.OWNED_SETTINGS[harness]
                self.assertIn(f"guard --harness {harness}", settings.read_text(encoding="utf-8"))
                self.assertEqual(team.hook_self_test(fresh.project), [])
        hooked = read("protocols/harness-security.md").split("## What the guard denies", 1)[1].split("\n\n", 2)[1]
        for name in ("Claude Code", "Codex", "Antigravity", "Gemini CLI"):
            self.assertIn(name, hooked)


class DecisionContractTests(unittest.TestCase):
    """Agent improvement 4: silence never resolves a blocking decision."""

    def test_an_unanswered_decision_stays_unresolved_while_independent_work_continues(self) -> None:
        for doc in ("protocols/agent-contract.md", "protocols/plan-modes.md"):
            text = read(doc)
            self.assertNotRegex(text, r"(?i)silence (can be read as|means)", doc)
            self.assertIn("unresolved", text, doc)
        fresh = Fresh(self)
        run = fresh.start(self)
        for doc in ("protocols/agent-contract.md", "protocols/plan-modes.md"):
            self.assertEqual((fresh.bus / doc).read_text(encoding="utf-8"),
                             read(doc), "the installed protocol is the shipped one")
        out = fresh.ok(self, "checkpoint", "--project", ".", "--kind", "decision", "--question", "Which database?",
                       "--recommendation", "PostgreSQL (default)", "--risk", "R2", "--alternatives", "SQLite", "--impact", "Schema",
                       "--evidence", "BRIEF.md", "--rollback", "Migrate")
        checkpoint = out.strip().splitlines()[-1]
        fresh.build(self)  # work the question does not block continues
        result = fresh.cli_run("advance", "--project", ".")
        self.assertEqual(result.returncode, 2, "an unanswered decision holds the stage")
        state = fresh.state(run)
        self.assertEqual(state["stage"], "04_build")
        self.assertEqual(next(item for item in state["checkpoints"] if item["id"] == checkpoint)["status"], "pending")


class VerdictVocabularyTests(unittest.TestCase):
    """Agent improvement 3: PASS, CONDITIONAL and FAIL are exclusive and say the same thing everywhere."""

    PLACES = ["protocols/definition-of-done.md", "runtime/templates/verification.md", "skills/agentic-verify/SKILL.md",
              "agents/engineering/qa-lead.md"]

    def test_every_definition_is_exclusive(self) -> None:
        for doc in self.PLACES:
            text = " ".join(read(doc).split())
            with self.subTest(doc=doc):
                self.assertIn("PASS = no open blocker or major", text)
                self.assertIn("CONDITIONAL = no open blocker", text)
                self.assertIn("FAIL = any open blocker or failed required criterion", text)
                self.assertIn("not run is unknown", text)

    def test_the_runtime_gate_agrees(self) -> None:
        fresh = Fresh(self)
        run = fresh.start(self)
        fresh.to_verify(self, run)
        for verdict, passes in (("FAIL", False), ("CONDITIONAL", False), ("PASS", True)):
            (run / "VERIFICATION.md").write_text(f"Verdict: {verdict}\nVerifier: qa-lead\nVerified-SHA: none\n", encoding="utf-8")
            problems = team.verdict_problems(fresh.project, run, fresh.state(run), "VERIFICATION.md", lambda check: False)
            self.assertEqual(not problems, passes, (verdict, problems))


if __name__ == "__main__":
    unittest.main()
