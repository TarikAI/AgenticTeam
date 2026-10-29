"""Repair F5 (runtime half): packets fit the role, pin the run, keep required context (audit findings G1-G4)."""

from __future__ import annotations

import atexit
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

import helpers
from helpers import ROOT, fresh_project, team
from test_regressions import PASSING_CHECK, task_args

sys.path.insert(0, str(ROOT / "scripts"))
import findings_to_tasks  # noqa: E402

FINDING = [{"path": "src/app.py", "line": 3, "content": "crash on empty input", "severity": "blocker"}]


def spaced_project() -> Path:
    """An installed project whose path contains a space, as on many Windows profiles."""
    parent = Path(tempfile.mkdtemp(prefix="agentic packet "))
    atexit.register(shutil.rmtree, str(parent), True)
    target = parent / "my project"
    team.install_team(ROOT, target, "generic", "full-company", [], [])
    (target / ".agentic-team" / "config" / "policies.local.json").write_text(json.dumps(helpers.LOCAL_POLICY), encoding="utf-8")
    return target


def command_line(packet: str, verb: str) -> str:
    return next(line for line in packet.splitlines() if re.match(rf"python \S+ {verb} ", line))


def shells() -> dict[str, str]:
    """The documented shells available here: Bash (Git Bash on Windows, not the WSL launcher) and PowerShell."""
    found: dict[str, str] = {}
    if os.name == "nt":
        git = shutil.which("git")
        candidate = Path(git).resolve().parents[1] / "bin" / "bash.exe" if git else None
        if candidate and candidate.is_file():
            found["bash"] = str(candidate)
    elif shutil.which("bash"):
        found["bash"] = shutil.which("bash")
    powershell = shutil.which("pwsh") or shutil.which("powershell")
    if powershell:
        found["powershell"] = powershell
    return found


def run_line(project: Path, line: str, shell: str, program: str) -> subprocess.CompletedProcess:
    """Run a packet command line as written, with this interpreter standing in for `python`."""
    rest = line.split(" ", 2)[2]
    cli = project / ".agentic-team" / "bin" / "agentic_team.py"
    if shell == "bash":
        return subprocess.run([program, "-c", f"'{Path(sys.executable).as_posix()}' '{cli.as_posix()}' {rest}"],
                              capture_output=True, text=True, env=dict(os.environ))
    return subprocess.run([program, "-NoProfile", "-Command", f"& '{sys.executable}' '{cli}' {rest}"],
                          capture_output=True, text=True, env=dict(os.environ))


class AccessAwarePacketTests(unittest.TestCase):
    """G1: each access class gets instructions it can follow."""

    def test_every_access_class_gets_permitted_instructions(self) -> None:
        project = fresh_project()
        run = team.init_run(project, "Packets", "packets", "autonomous", "execute-only", "adaptive")
        roster = team.installed_agents(project)
        by_access: dict[str, str] = {}
        for agent in roster.values():
            by_access.setdefault(agent["access"], agent["id"])
        self.assertEqual(set(by_access), {"workspace-write", "review", "orchestrate", "read-only", "research"})
        for access, agent in sorted(by_access.items()):
            task_id = f"T-{access}"
            team.add_task(project, run, task_args(task_id, agent, action="research" if access in {"read-only", "research"} else "build",
                                                  path=[f"src/{access}"]))
            text = team.build_pack(project, run, task_id)[0].read_text(encoding="utf-8")
            brief = team.render_brief(project, run, task_id)
            with self.subTest(access=access):
                self.assertIn("Result envelope", text)
                if access in team.ACTIVE_ACCESS:
                    self.assertIn("## Commands (pinned to this project and run)", text)
                    self.assertIn("exec --task", text)
                else:
                    self.assertNotIn("exec --task", text)
                    self.assertIn("no shell", text)
                    self.assertIn("orchestrator records it", brief)
                    self.assertNotIn("Claim before writing", brief)


class RunPinningTests(unittest.TestCase):
    """G2: saved commands address the run they were made for, after CURRENT moves."""

    def setUp(self) -> None:
        self.project = spaced_project()
        self.wanted = team.init_run(self.project, "Wanted", "wanted", "autonomous", "execute-only", "adaptive")
        self.other = team.init_run(self.project, "Other", "other", "autonomous", "execute-only", "adaptive")
        for run in (self.wanted, self.other):
            team.add_task(self.project, run, task_args("A", "backend-engineer"))  # overlapping task IDs

    def test_saved_packet_commands_survive_a_current_switch_in_both_shells(self) -> None:
        packet = team.build_pack(self.project, self.wanted, "A")[0].read_text(encoding="utf-8")
        line = command_line(packet, "claim")
        self.assertIn("--run wanted", line)
        self.assertEqual(team.current_run_id(team.project_bus(self.project)), "other")
        available = list(shells().items())
        if not available:
            self.skipTest("neither bash nor PowerShell is available")
        result = run_line(self.project, line, *available[0])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(team.load_state(self.wanted)["tasks"]["A"]["status"], "claimed")
        self.assertEqual(team.load_state(self.other)["tasks"]["A"]["status"], "ready")
        for shell, program in available[1:]:
            fail = command_line(packet, "fail").replace('"<what failed>"', "'checked from another shell'")
            result = run_line(self.project, fail, shell, program)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(team.load_state(self.other)["tasks"]["A"]["status"], "ready")

    def test_remediation_commands_and_apply_use_the_requested_run(self) -> None:
        findings = Path(tempfile.mkdtemp(prefix="agentic-findings-")) / "findings.json"
        findings.write_text(json.dumps(FINDING), encoding="utf-8")
        captured = []
        original_print = print

        def capture(*args, **kwargs):
            captured.append(" ".join(str(arg) for arg in args))
        import builtins
        builtins.print = capture
        try:
            findings_to_tasks.main([str(findings), "--project", str(self.project), "--run", "wanted", "--commands",
                                    "--check", PASSING_CHECK])
        finally:
            builtins.print = original_print
        lines = [line.strip() for line in "\n".join(captured).splitlines() if line.strip().startswith("python ")]
        self.assertTrue(lines)
        self.assertTrue(all("--run wanted" in line for line in lines), lines)
        argv = findings_to_tasks.add_task_argv(findings_to_tasks.build_tasks(
            [findings_to_tasks.normalize(item) for item in FINDING], findings_to_tasks.load_context(str(self.project), "wanted"),
            "04_build", [PASSING_CHECK])[0], str(self.project), "wanted")
        code, _, err = helpers.run_cli(self.project, *argv)
        self.assertEqual(code, 0, err)
        self.assertEqual(len(team.load_state(self.wanted)["tasks"]), 2)
        self.assertEqual(len(team.load_state(self.other)["tasks"]), 1)
        findings_to_tasks.main([str(findings), "--project", str(self.project), "--run", "wanted", "--apply", "--check", PASSING_CHECK])
        self.assertEqual(len(team.load_state(self.other)["tasks"]), 1, "apply wrote into the current run")


class RemediationShellTests(unittest.TestCase):
    """G2: printed remediation commands run as written in each documented shell, quotes and spaces included."""

    def printed(self, project: Path, shell: str) -> list[str]:
        findings = Path(tempfile.mkdtemp(prefix="agentic-findings-")) / "findings.json"
        findings.write_text(json.dumps([{"path": "src/app.py", "line": 3, "content": 'crash on "empty" input', "severity": "blocker"}]),
                            encoding="utf-8")
        import builtins
        captured: list[str] = []
        original = builtins.print
        builtins.print = lambda *args, **kwargs: captured.append(" ".join(str(arg) for arg in args))
        try:
            findings_to_tasks.main([str(findings), "--project", str(project), "--run", "wanted", "--commands", "--shell", shell,
                                    "--check", PASSING_CHECK])
        finally:
            builtins.print = original
        lines = [line.strip() for line in "\n".join(captured).splitlines()]
        start = next(index for index, line in enumerate(lines) if line.startswith("Runnable add-task"))
        return [line for line in lines[start + 1:] if line.startswith(("python ", "function Q"))]

    def test_powershell_lines_add_the_task_in_every_available_powershell(self) -> None:
        programs = [program for program in (shutil.which("powershell"), shutil.which("pwsh")) if program]
        if not programs:
            self.skipTest("PowerShell is not available")
        for program in programs:
            project = spaced_project()
            wanted = team.init_run(project, "Wanted", "wanted", "autonomous", "execute-only", "adaptive")
            team.init_run(project, "Other", "other", "autonomous", "execute-only", "adaptive")
            lines = self.printed(project, "powershell")
            cli = project / ".agentic-team" / "bin" / "agentic_team.py"
            script = "\n".join(line if line.startswith("function") else f"& '{sys.executable}' '{cli}' " + line.split(" ", 2)[2]
                               for line in lines)
            result = subprocess.run([program, "-NoProfile", "-NonInteractive", "-Command", script + "\nexit $LASTEXITCODE"],
                                    capture_output=True, text=True, env=dict(os.environ))
            with self.subTest(shell=program):
                self.assertEqual(result.returncode, 0, (script, result.stderr[-600:]))
                tasks = team.load_state(wanted)["tasks"]
                self.assertEqual(len(tasks), 1)
                self.assertIn('"empty"', next(iter(tasks.values()))["title"])


class SectionContextTests(unittest.TestCase):
    """G3: a requested #section survives budgeting; missing or ambiguous anchors are reported."""

    def setUp(self) -> None:
        self.project = fresh_project()
        self.run = team.init_run(self.project, "Context", "context", "autonomous", "execute-only", "adaptive")
        doc = self.project / "docs" / "large.md"
        doc.parent.mkdir(parents=True)
        intro = "Background that does not matter for this task. " * 2500
        doc.write_text(f"# Large\n\n{intro}\n\n## Required\n\nREQUIRED-MARKER: the API returns 409 on conflict.\n\n"
                       "## Café Ñandú\n\nUNICODE-MARKER\n\n## Twice\n\nFIRST\n\n## Twice\n\nSECOND\n\n## After\n\nAFTER-MARKER\n",
                       encoding="utf-8")

    def pack(self, *inputs: str) -> tuple[str, list[str]]:
        task_id = f"T{len(team.load_state(self.run)['tasks'])}"
        team.add_task(self.project, self.run, task_args(task_id, "backend-engineer", input=list(inputs)))
        path, _, omissions = team.build_pack(self.project, self.run, task_id)
        return path.read_text(encoding="utf-8"), omissions

    def test_a_late_section_is_kept_and_the_intro_is_not(self) -> None:
        text, omissions = self.pack("docs/large.md#Required")
        self.assertIn("REQUIRED-MARKER", text)
        self.assertNotIn("Background that does not matter", text)
        self.assertNotIn("AFTER-MARKER", text)
        self.assertNotIn("INCOMPLETE", text)

    def test_a_comment_in_a_code_block_does_not_end_the_section(self) -> None:
        doc = self.project / "docs" / "setup.md"
        doc.write_text("# Setup\n\n## Required\n\nBefore.\n\n```bash\n# install deps\npip install x\n```\n\n"
                       "AFTER-FENCE-MARKER\n\n## Next\n\nNEXT-MARKER\n", encoding="utf-8")
        text, _ = self.pack("docs/setup.md#Required")
        self.assertIn("# install deps", text)
        self.assertIn("AFTER-FENCE-MARKER", text)
        self.assertNotIn("NEXT-MARKER", text)

    def test_unicode_duplicate_and_missing_anchors(self) -> None:
        text, _ = self.pack("docs/large.md#café ñandú")
        self.assertIn("UNICODE-MARKER", text)
        text, omissions = self.pack("docs/large.md#Twice")
        self.assertIn("FIRST", text)
        self.assertIn("SECOND", text)
        self.assertTrue(any("ambiguous" in item for item in omissions), omissions)
        text, omissions = self.pack("docs/large.md#Nowhere")
        self.assertIn("Context condition: INCOMPLETE", text)
        self.assertTrue(any("not found" in item for item in omissions), omissions)

    def test_required_inputs_outrank_background_and_overflow_is_reported(self) -> None:
        text, omissions = self.pack("docs/large.md#Required", "docs/large.md")
        self.assertIn("REQUIRED-MARKER", text)
        self.assertIn("Context condition: INCOMPLETE", text)
        self.assertLessEqual(team.estimate_tokens(text), 8000)


class SpecialistActivationTests(unittest.TestCase):
    """G4: work done for an earlier activation does not satisfy a new one."""

    def test_reactivation_needs_fresh_scoped_work_or_a_reasoned_deactivation(self) -> None:
        project = fresh_project()
        run = team.init_run(project, "Spec", "spec", "autonomous", "execute-only", "adaptive")
        matches = team.route_specialists(project, run, ["admin-console"])
        self.assertIn("platform-admin-engineer", [item["agent"] for item in matches])
        team.add_task(project, run, task_args("EARLY", "platform-admin-engineer", path=["admin/early"]))
        team.claim_task(project, run, "EARLY", "platform-admin-engineer", 60)
        team.complete_task(project, run, "EARLY", "platform-admin-engineer", ["note:reviewed the early plan"])

        def blocked() -> bool:
            state = team.load_state(run)
            return any("platform-admin-engineer" in item for item in team.stage_exit_problems(project, run, state, state["stage"]))
        self.assertFalse(blocked())
        team.route_specialists(project, run, ["admin-console"])  # the implementation changed: activate again
        self.assertTrue(blocked(), "the early task must not satisfy the new activation")
        team.add_task(project, run, task_args("FRESH", "platform-admin-engineer", path=["admin/fresh"]))
        team.claim_task(project, run, "FRESH", "platform-admin-engineer", 60)
        team.complete_task(project, run, "FRESH", "platform-admin-engineer", ["note:reviewed the change"])
        self.assertFalse(blocked())
        team.route_specialists(project, run, ["admin-console"])
        team.deactivate_specialist(project, run, "platform-admin-engineer", "nothing in scope changed since FRESH")
        self.assertFalse(blocked())


if __name__ == "__main__":
    unittest.main()
