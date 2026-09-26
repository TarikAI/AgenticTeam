"""Regression tests for the defects catalogued in docs/v3-upgrade-plan.md §3.1.

Each test is named after its defect ID and failed on d0fb6cf.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest

from helpers import ROOT, fresh_project, run_cli, team

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    tomllib = None


def task_args(task_id: str, owner: str, **overrides) -> argparse.Namespace:
    values = dict(
        id=task_id,
        title=f"Task {task_id}",
        objective=None,
        owner=owner,
        stage=None,
        risk="R1",
        depends_on=[],
        path=[f"src/{task_id.lower()}"],
        exclusive=False,
        input=[],
        acceptance=[],
        evidence_contract=[],
    )
    values.update(overrides)
    return argparse.Namespace(**values)


class Base(unittest.TestCase):
    preset = "full-company"

    def setUp(self) -> None:
        self.project = fresh_project(self.preset)

    def run_(self, autonomy: str = "autonomous", entry: str = "execute-only", run_id: str = "reg") -> Path:
        return team.init_run(self.project, "Regression", run_id, autonomy, entry, "adaptive")

    @staticmethod
    def token(run_dir: Path) -> str:
        return team.owner_token_file(team.load_state(run_dir)).read_text(encoding="utf-8").strip()

    def fusion(self, run_dir: Path, **overrides) -> None:
        values = dict(
            id="f1",
            question="Which plan?",
            sponsor="human-owner",
            moderator="fusion-moderator",
            verifier="qa-lead",
            contributor=["product-manager", "cto-architect"],
        )
        values.update(overrides)
        team.fusion_init(self.project, run_dir, argparse.Namespace(**values))


class FusionRegressions(Base):
    def test_R01_submissions_only_in_their_phase(self) -> None:
        run = self.run_()
        self.fusion(run)
        with self.assertRaises(team.TeamError):
            team.fusion_submit(self.project, run, "f1", "synthesis", "fusion-moderator", "skip all")
        with self.assertRaises(team.TeamError):
            team.fusion_submit(self.project, run, "f1", "critique", "product-manager", "before reveal")
        self.assertEqual(team.load_state(run)["fusion_sessions"][0]["status"], "proposals")

    def test_R02_human_sponsor_close_needs_owner_token(self) -> None:
        run = self.run_()
        self.fusion(run)
        for kind, agents in (
            ("proposal", ["product-manager", "cto-architect"]),
            ("critique", ["product-manager", "cto-architect"]),
            ("synthesis", ["fusion-moderator"]),
            ("verification", ["qa-lead"]),
        ):
            for agent in agents:
                team.fusion_submit(self.project, run, "f1", kind, agent, f"{kind} evidence")
        with self.assertRaises(team.TeamError):
            team.fusion_close(self.project, run, "f1", "human-owner", "closed by an agent")
        with self.assertRaises(team.TeamError):
            team.fusion_close(self.project, run, "f1", "human-owner", "closed by an agent", "Owner", "wrong")
        team.fusion_close(self.project, run, "f1", "human-owner", "plan A", "Owner", self.token(run))
        self.assertEqual(team.load_state(run)["fusion_sessions"][0]["status"], "complete")
        decision = (run / "_fusion" / "f1" / "decision.md").read_text(encoding="utf-8")
        self.assertIn("plan A", decision)

    def test_R03_no_resubmission_and_one_revision(self) -> None:
        run = self.run_()
        self.fusion(run)
        team.fusion_submit(self.project, run, "f1", "proposal", "product-manager", "v1")
        with self.assertRaises(team.TeamError):
            team.fusion_submit(self.project, run, "f1", "proposal", "product-manager", "v2 after peeking")
        team.fusion_submit(self.project, run, "f1", "proposal", "cto-architect", "v1")
        team.fusion_submit(self.project, run, "f1", "revision", "product-manager", "revised with evidence")
        with self.assertRaises(team.TeamError):
            team.fusion_submit(self.project, run, "f1", "revision", "product-manager", "second revision")

    def test_R04_moderator_cannot_verify_own_synthesis(self) -> None:
        run = self.run_()
        with self.assertRaises(team.TeamError):
            self.fusion(run, verifier="fusion-moderator")


class LifecycleRegressions(Base):
    def test_R05_rejection_can_be_resolved_by_the_human(self) -> None:
        run = self.run_("supervised")
        checkpoint = team.create_checkpoint(self.project, run, "Q?", "rec", "R2", "decision", details={"alternatives": "wait", "impact": "delay", "evidence": "notes", "rollback": "revert"})
        team.reject_checkpoint(self.project, run, checkpoint, "Owner", "no", self.token(run))
        self.assertEqual(team.load_state(run)["status"], "blocked-rejection")
        follow_up = team.create_checkpoint(self.project, run, "Fixed?", "rec", "R2", "decision", details={"alternatives": "wait", "impact": "delay", "evidence": "notes", "rollback": "revert"})
        team.approve_checkpoint(self.project, run, follow_up, "Owner", "yes", self.token(run))
        self.assertEqual(team.load_state(run)["status"], "blocked-rejection", "approval must not clear a rejection")
        with self.assertRaises(team.TeamError):
            team.resolve_checkpoint(self.project, run, checkpoint, "Owner", "fixed", None)
        self.assertEqual(team.resolve_checkpoint(self.project, run, checkpoint, "Owner", "fixed", self.token(run)), "active")

    def test_R07_cancel_closes_the_task_for_the_stage_gate(self) -> None:
        run = self.run_()
        team.add_task(self.project, run, task_args("A", "backend-engineer"))
        team.add_task(self.project, run, task_args("B", "backend-engineer", depends_on=["A"]))
        with self.assertRaises(team.TeamError):
            team.cancel_task(self.project, run, "A", "descoped", "Owner", self.token(run))  # open dependent
        cancelled = team.cancel_task(self.project, run, "A", "descoped", "Owner", self.token(run), cascade=True)
        self.assertEqual(cancelled, ["A", "B"])
        self.assertEqual(team.advance_stage(self.project, run), "05_verify")

    def test_R08_completed_task_is_not_reopened_by_an_agent(self) -> None:
        run = self.run_()
        team.add_task(self.project, run, task_args("A", "backend-engineer"))
        team.claim_task(self.project, run, "A", "backend-engineer", 60)
        (self.project / "src").mkdir(exist_ok=True)
        (self.project / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
        team.complete_task(self.project, run, "A", "backend-engineer", ["file:src/a.py", "note:tests: 3 passed"])
        with self.assertRaises(team.TeamError):
            team.reopen_task(self.project, run, "A", "agent wants another go")
        team.reopen_task(self.project, run, "A", "human asked for rework", "Owner", self.token(run))
        task = team.load_state(run)["tasks"]["A"]
        self.assertEqual(task["status"], "ready")
        self.assertNotIn("lease_expires_at", task)
        self.assertEqual(task["previous_evidence"], [["file:src/a.py", "note:tests: 3 passed"]])

    def test_R09_reopen_keeps_attempts_and_budget_extension_is_human(self) -> None:
        run = self.run_()
        team.add_task(self.project, run, task_args("A", "backend-engineer"))
        for reason in ("import error", "timeout in fixture", "wrong column"):  # 2 retries: the third is final
            team.claim_task(self.project, run, "A", "backend-engineer", 60)
            team.fail_task(self.project, run, "A", "backend-engineer", reason)
        self.assertEqual(team.load_state(run)["tasks"]["A"]["status"], "failed")
        with self.assertRaises(team.TeamError):
            team.reopen_task(self.project, run, "A", "loop", extend_retries=5)
        team.reopen_task(self.project, run, "A", "new approach", "Owner", self.token(run), extend_retries=1)
        task = team.load_state(run)["tasks"]["A"]
        self.assertEqual(task["attempts"], 3)
        self.assertEqual(task["retry_extension"], 1)
        with self.assertRaises(team.TeamError):
            team.cancel_task(self.project, run, "A", "agent descopes", "backend-engineer", self.token(run))

    def test_repeated_failure_signature_stops_retrying(self) -> None:
        run = self.run_()
        team.add_task(self.project, run, task_args("A", "backend-engineer"))
        team.claim_task(self.project, run, "A", "backend-engineer", 60)
        team.fail_task(self.project, run, "A", "backend-engineer", "AssertionError at line 42 in C:/src/a.py")
        self.assertEqual(team.load_state(run)["tasks"]["A"]["status"], "ready")
        team.claim_task(self.project, run, "A", "backend-engineer", 60)
        team.fail_task(self.project, run, "A", "backend-engineer", "AssertionError at line 57 in C:/src/b.py")
        task = team.load_state(run)["tasks"]["A"]
        self.assertEqual(task["status"], "failed", "the same failure twice must escalate, not retry")
        self.assertIn("failure-repeated", [event["type"] for event in team.read_events(run)])

    def test_R11_remediation_defaults_to_the_current_stage(self) -> None:
        run = self.run_()
        team.advance_stage(self.project, run)  # 04 -> 05
        team.add_task(self.project, run, task_args("FIX", "backend-engineer"))
        self.assertEqual(team.load_state(run)["tasks"]["FIX"]["stage"], "05_verify")
        with self.assertRaises(team.TeamError):
            team.add_task(self.project, run, task_args("OLD", "backend-engineer", stage="04_build"))
        with self.assertRaises(team.TeamError):
            team.advance_stage(self.project, run)  # FIX now gates the 05 exit

    def test_R14_pending_checkpoint_blocks_advance(self) -> None:
        run = self.run_()
        team.create_checkpoint(self.project, run, "Which vendor?", "Vendor A", "R2", "decision", details={"alternatives": "wait", "impact": "delay", "evidence": "notes", "rollback": "revert"})
        self.assertEqual(team.advance_stage(self.project, run), "waiting-human")
        self.assertEqual(team.load_state(run)["stage"], "04_build")
        self.assertEqual(team.load_state(run)["status"], "waiting-human")

    def test_R15_failure_block_is_distinct_and_not_cleared_by_unrelated_approval(self) -> None:
        run = self.run_("hitl")
        team.add_task(self.project, run, task_args("A", "backend-engineer"))
        for reason in ("import error", "wrong column"):  # hitl: 1 retry
            team.claim_task(self.project, run, "A", "backend-engineer", 60)
            team.fail_task(self.project, run, "A", "backend-engineer", reason)
        self.assertEqual(team.load_state(run)["status"], "blocked-failure")
        checkpoint = team.create_checkpoint(self.project, run, "Unrelated?", "yes", "R1", "decision", details={"alternatives": "wait", "impact": "delay", "evidence": "notes", "rollback": "revert"})
        team.approve_checkpoint(self.project, run, checkpoint, "Owner", "ok", self.token(run))
        self.assertEqual(team.load_state(run)["status"], "blocked-failure")
        with self.assertRaises(team.BlockedError) as raised:
            team.advance_stage(self.project, run)
        self.assertIn("exhausted", str(raised.exception))

    def test_R16_claim_requires_installed_owner_and_respects_cap(self) -> None:
        run = self.run_()
        team.add_task(self.project, run, task_args("A", "backend-engineer"))
        with self.assertRaises(team.TeamError):
            team.claim_task(self.project, run, "A", "totally-made-up-agent", 60)
        with self.assertRaises(team.TeamError):
            team.claim_task(self.project, run, "A", "frontend-engineer", 60)
        team.reassign_task(self.project, run, "A", "frontend-engineer", "frontend owns the view")
        team.claim_task(self.project, run, "A", "frontend-engineer", 60)
        for index in range(8):
            team.add_task(self.project, run, task_args(f"C{index}", "backend-engineer"))
        for index in range(7):  # autonomous cap is 8 in total
            team.claim_task(self.project, run, f"C{index}", "backend-engineer", 60)
        with self.assertRaises(team.TeamError) as raised:
            team.claim_task(self.project, run, "C7", "backend-engineer", 60)
        self.assertIn("Concurrency cap", str(raised.exception))

    def test_R18_build_tasks_need_paths_or_exclusive(self) -> None:
        run = self.run_()
        with self.assertRaises(team.TeamError):
            team.add_task(self.project, run, task_args("A", "backend-engineer", path=[]))
        team.add_task(self.project, run, task_args("X", "backend-engineer", path=[], exclusive=True))
        team.add_task(self.project, run, task_args("B", "frontend-engineer", path=["src/ui"]))
        team.claim_task(self.project, run, "X", "backend-engineer", 60)
        with self.assertRaises(team.TeamError):
            team.claim_task(self.project, run, "B", "frontend-engineer", 60)

    def test_R19_touching_an_older_run_does_not_repoint_current(self) -> None:
        first = self.run_(run_id="first")
        team.init_run(self.project, "Second", "second", "autonomous", "execute-only", "adaptive")
        team.add_task(self.project, first, task_args("A", "backend-engineer"))
        current = (self.project / ".agentic-team" / "CURRENT.md").read_text(encoding="utf-8")
        self.assertIn("`second`", current)
        team.switch_run(self.project, "first")
        self.assertIn("`first`", (self.project / ".agentic-team" / "CURRENT.md").read_text(encoding="utf-8"))
        self.assertEqual({item["run"] for item in team.list_runs(self.project)}, {"first", "second"})

    def test_R21_exit_codes_distinguish_error_gate_blocked_usage(self) -> None:
        self.run_()
        project = str(self.project)
        self.assertEqual(run_cli(self.project, "claim", "--project", project, "--task", "NOPE", "--agent", "ceo")[0], 1)
        self.assertEqual(run_cli(self.project, "claim", "--project", project)[0], 64)
        run_cli(self.project, "add-task", "--project", project, "--id", "D", "--title", "deploy to production",
                "--owner", "devops-engineer", "--path", "infra")
        self.assertEqual(run_cli(self.project, "claim", "--project", project, "--task", "D", "--agent", "devops-engineer")[0], 2)
        code, _, err = run_cli(self.project, "checkpoint", "--project", project, "--question", "q", "--recommendation", "r",
                               "--alternatives", "a", "--impact", "i", "--evidence", "e", "--rollback", "r")
        checkpoint = _.strip()
        token = team.owner_token_file(team.load_state(team.find_run(self.project, None))).read_text(encoding="utf-8").strip()
        run_cli(self.project, "reject", "--project", project, "--checkpoint", checkpoint, "--by", "Owner",
                "--decision", "no", "--token-stdin", stdin=token + "\n")
        self.assertEqual(run_cli(self.project, "advance", "--project", project)[0], 3)

    def test_R22_atomic_write_survives_a_concurrent_reader(self) -> None:
        run = self.run_()
        path = run / "state.json"
        handle = open(path, "r", encoding="utf-8")
        releaser = threading.Timer(0.1, handle.close)
        releaser.start()
        try:
            team.write_json_atomic(path, team.load_state(run))
        finally:
            releaser.join()
            handle.close()
        self.assertEqual(team.load_state(run)["run_id"], "reg")

    def test_R23_routing_matches_words_not_substrings(self) -> None:
        run = self.run_()
        hits = team.route_specialists(self.project, run, ["deploy a soundcloud clone", "administrator docs", "bug reproduction steps"])
        self.assertEqual(hits, [])

    def test_R26_doctor_reports_blocked_runs_and_drift(self) -> None:
        run = self.run_("supervised")
        checkpoint = team.create_checkpoint(self.project, run, "Q?", "rec", "R2", "decision", details={"alternatives": "wait", "impact": "delay", "evidence": "notes", "rollback": "revert"})
        team.reject_checkpoint(self.project, run, checkpoint, "Owner", "no", self.token(run))
        router = self.project / "AGENTS.md"
        router.write_text(router.read_text(encoding="utf-8").replace("AgenticTeam", "Tampered"), encoding="utf-8")
        findings = "\n".join(team.doctor(self.project))
        self.assertIn("blocked-rejection", findings)
        self.assertIn("modified locally: AGENTS.md", findings)

    def test_R27_refused_authority_is_recorded(self) -> None:
        run = self.run_()
        checkpoint = team.create_checkpoint(self.project, run, "Q?", "rec", "R2", "decision", details={"alternatives": "wait", "impact": "delay", "evidence": "notes", "rollback": "revert"})
        with self.assertRaises(team.TeamError):
            team.approve_checkpoint(self.project, run, checkpoint, "Owner", "self-approval", "forged")
        events = [event["type"] for event in team.read_events(run)]
        self.assertIn("authority-refused", events)

    def test_R28_report_never_overwrites_the_delivery_report(self) -> None:
        run = self.run_()
        (run / "DELIVERY-REPORT.md").write_text("# Written by the ceo\n", encoding="utf-8")
        path = team.generate_report(self.project, run)
        self.assertEqual(path.name, "DELIVERY-EVIDENCE.md")
        self.assertEqual((run / "DELIVERY-REPORT.md").read_text(encoding="utf-8"), "# Written by the ceo\n")


class InstallRegressions(unittest.TestCase):
    def test_R29_installed_copy_refuses_validate_for_every_harness(self) -> None:
        for harness in ("generic", "pi"):
            with self.subTest(harness=harness):
                project = fresh_project("platform-core", harness)
                code, _, err = run_cli(project, "validate")
                self.assertEqual(code, 1)
                self.assertIn("installed copy", err)

    def test_R30_manifest_defaults_are_valid_choices(self) -> None:
        defaults = team.load_json(ROOT / "team.json")["defaults"]
        self.assertIn(defaults["entry_mode"], {"idea", "plan-given", "execute-only"})

    def test_R33_helpers_are_installed_and_paths_rewritten(self) -> None:
        project = fresh_project("platform-core", "claude-code")
        code, out, err = run_cli(project, "preflight", "--format", "json")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out)["project_root"], str(project.resolve()))
        self.assertEqual(run_cli(project, "preflight", "--require", "definitely-missing")[0], 64)
        self.assertEqual(run_cli(project, "preflight", "--require", "design-architect")[0] in {0, 1}, True)
        for folder in (project / ".claude" / "skills", project / ".agentic-team" / "protocols", project / ".claude" / "agents"):
            for path in folder.rglob("*.md"):
                text = path.read_text(encoding="utf-8")
                self.assertNotRegex(text, r"(?<![\w./-])scripts/(agentic_team|preflight_skills)\.py", str(path))

    def test_R34_install_ps1_probes_an_executing_interpreter(self) -> None:
        script = (ROOT / "scripts" / "install.ps1").read_text(encoding="utf-8")
        self.assertIn("sys.version_info[:2] >= (3, 10)", script)
        self.assertIn("'py', '-3'", script)
        self.assertNotIn("Get-Command python -ErrorAction SilentlyContinue)) {\n  throw", script)

    def test_R36_fusion_preset_has_its_default_verifier(self) -> None:
        manifest = team.load_json(ROOT / "team.json")
        self.assertIn("qa-lead", manifest["presets"]["fusion-product-council"]["agents"])

    @unittest.skipIf(tomllib is None, "tomllib requires Python 3.11+")
    def test_R37_codex_toml_survives_backslashes_and_quotes(self) -> None:
        for text in ('path C:\\new\\table and "quotes"', "ends with a quote '", "has ''' fences"):
            with self.subTest(text=text):
                parsed = tomllib.loads("x = " + team.toml_literal(text) + "\n")["x"]
                self.assertEqual(parsed.lstrip("\n") if parsed.startswith("\n") else parsed, text)

    def test_R38_R39_antigravity_ships_skills_not_workflows(self) -> None:
        project = fresh_project("platform-core", "antigravity")
        self.assertFalse((project / ".agents" / "workflows").exists())
        self.assertTrue((project / ".agents" / "skills" / "agentic-resume" / "SKILL.md").is_file())
        self.assertIn("mainAgent: false", (project / ".agents" / "agents" / "qa-lead.md").read_text(encoding="utf-8"))

    def test_R38_reinstall_removes_stale_workflows(self) -> None:
        project = Path(tempfile.mkdtemp())
        stale = project / ".agents" / "workflows" / "resume.md"
        stale.parent.mkdir(parents=True)
        stale.write_text("---\ndescription: old\n---\n", encoding="utf-8")
        record_path = project / ".agentic-team" / "install-manifest.json"
        record_path.parent.mkdir(parents=True)
        record_path.write_text(json.dumps({"generated_files": [os.path.join(".agents", "workflows", "resume.md")]}), encoding="utf-8")
        team.install_team(ROOT, project, "antigravity", "platform-core", [], [])
        self.assertFalse(stale.exists())


if __name__ == "__main__":
    unittest.main()
