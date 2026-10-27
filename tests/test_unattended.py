"""The unattended profile: the release stage of an R0-R1 run exits on executable conditions, not a human click.

Guarantee G20. Every condition has its refusal path here, plus the passing path, the fallback
to the human checkpoint for R2+ work, and a project tightening the gate back to human.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import subprocess
import unittest

from helpers import fresh_project, run_cli, team
from test_evidence import PASS_HEADER, write
from test_regressions import PASSING_CHECK, task_args

RELEASE_TEXT = (
    "# Release\n\nArtifact: HEAD as verified. Rollout: local only. Data changes: none.\n"
    "Monitoring and rollback: rehearsed by task RB. Supply chain: no new dependencies.\n"
)


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self.project = fresh_project()

    def token(self, run_dir: Path) -> str:
        return team.owner_token_file(team.load_state(run_dir)).read_text(encoding="utf-8").strip()

    def local_policy(self, **data) -> None:
        path = self.project / ".agentic-team" / "config" / "policies.local.json"
        path.write_text(json.dumps({"budgets": {"usd": 50}, **data}), encoding="utf-8")

    def start(self, autonomy: str = "unattended") -> Path:
        return team.init_run(self.project, "Unattended", "ua", autonomy, "execute-only", "adaptive")

    def finish(self, run: Path, task_id: str, owner: str, note: str = "done", **overrides) -> None:
        """Add, claim, and complete a task; completion runs its declared check and records it."""
        team.add_task(self.project, run, task_args(task_id, owner, **overrides))
        team.claim_task(self.project, run, task_id, owner, 60)
        team.complete_task(self.project, run, task_id, owner, [f"note:{note}"])

    def to_release(self, run: Path, sha: str = "none") -> None:
        self.finish(run, "T1", "backend-engineer", "built")
        self.assertEqual(team.advance_stage(self.project, run), "05_verify")
        write(run, "VERIFICATION.md", PASS_HEADER.format(verifier="qa-lead", sha=sha))
        self.assertEqual(team.advance_stage(self.project, run), "06_release")

    def rehearse(self, run: Path, task_id: str = "RB", owner: str = "release-manager", check: str | None = PASSING_CHECK) -> None:
        self.finish(run, task_id, owner, "rolled back and forward on a local copy",
                    action="rollback-test", target="local", path=[], check=[check] if check else [])

    def refusal(self, run: Path) -> str:
        with self.assertRaises(team.TeamError) as raised:
            team.advance_stage(self.project, run)
        return str(raised.exception)

    def stage_checkpoints(self, run: Path) -> list[dict]:
        return [item for item in team.load_state(run)["checkpoints"] if item["kind"] == "stage"]


class ProfileTests(Base):
    def test_unattended_is_autonomous_with_an_executable_release_gate(self) -> None:
        profiles = team.load_policy(self.project)["profiles"]
        expected = dict(profiles["autonomous"], release_gate="executable", description=profiles["unattended"]["description"])
        self.assertEqual(profiles["unattended"], expected)
        self.assertTrue(profiles["unattended"]["require_budget_ceiling"])
        self.assertEqual(profiles["unattended"]["pause_at"], ["R3", "R4"])
        self.assertEqual(team.gate_value(profiles["unattended"], "06_release"), "executable")
        for name in ("autonomous", "supervised", "hitl"):
            self.assertEqual(team.gate_value(profiles[name], "06_release"), "human", name)
        for relative in ("schemas/run-state.schema.json", "schemas/team.schema.json"):
            self.assertIn("unattended", (self.project / ".agentic-team" / relative).read_text(encoding="utf-8"), relative)

    def test_unattended_runs_need_a_spend_ceiling(self) -> None:
        (self.project / ".agentic-team" / "config" / "policies.local.json").unlink()
        with self.assertRaises(team.TeamError) as raised:
            self.start()
        self.assertIn("spend ceiling", str(raised.exception))
        run = team.init_run(self.project, "U", "u", "unattended", "execute-only", "adaptive", {"usd": 3})
        self.assertEqual(team.load_state(run)["autonomy"], "unattended")

    def test_the_stage_contract_names_the_conditions(self) -> None:
        run = self.start()
        context = (run / "06_release" / "CONTEXT.md").read_text(encoding="utf-8")
        self.assertIn("gate: `executable`", context)
        self.assertIn("rollback-test", context)
        self.assertNotIn("Obtain explicit human approval", context)
        other = team.init_run(self.project, "A", "a", "autonomous", "execute-only", "adaptive")
        self.assertIn("Human approval required", (other / "06_release" / "CONTEXT.md").read_text(encoding="utf-8"))

    def test_executable_is_refused_on_every_other_profile(self) -> None:
        shipped = team.load_json(self.project / ".agentic-team" / "config" / "policies.json")
        self.assertEqual(team.policy_problems(shipped), [])
        for name in ("autonomous", "supervised", "hitl"):
            policy = copy.deepcopy(shipped)
            policy["profiles"][name]["release_gate"] = "executable"
            problems = team.policy_problems(policy)
            self.assertTrue(any("reserved" in problem for problem in problems), (name, problems))
        loosened = copy.deepcopy(shipped)
        loosened["profiles"]["unattended"]["require_budget_ceiling"] = False
        loosened["profiles"]["unattended"]["pause_at"] = ["R4"]
        problems = team.policy_problems(loosened)
        self.assertTrue(any("require_budget_ceiling" in problem for problem in problems), problems)
        self.assertTrue(any("R3" in problem for problem in problems), problems)
        typo = copy.deepcopy(shipped)
        typo["profiles"]["autonomous"]["readiness_gate"] = "automagic"
        self.assertTrue(any("gate_values" in problem for problem in team.policy_problems(typo)))
        # An installed policy edited by hand is refused by every command, not silently honored.
        installed = self.project / ".agentic-team" / "config" / "policies.json"
        edited = copy.deepcopy(shipped)
        edited["profiles"]["autonomous"]["release_gate"] = "executable"
        installed.write_text(json.dumps(edited), encoding="utf-8")
        with self.assertRaises(team.TeamError) as raised:
            team.load_policy(self.project)
        self.assertIn("reserved for unattended", str(raised.exception))
        code, _, err = run_cli(self.project, "init-run", "--project", str(self.project), "--name", "X", "--autonomy", "autonomous")
        self.assertEqual(code, 1)
        self.assertIn("reserved for unattended", err)
        installed.write_text(json.dumps(shipped, indent=2), encoding="utf-8")
        # A local overlay cannot grant the executable gate to another profile either.
        self.local_policy(profiles={"autonomous": {"release_gate": "executable"}})
        self.assertEqual(team.gate_value(team.load_policy(self.project)["profiles"]["autonomous"], "06_release"), "human")

    def test_hard_gates_hold_under_unattended(self) -> None:
        run = self.start()
        team.add_task(self.project, run, task_args("SHIP", "devops-engineer", action="deploy", target="production", path=["deploy"]))
        self.assertEqual(team.load_state(run)["tasks"]["SHIP"]["risk"], "R3")
        with self.assertRaises(team.GateError):
            team.claim_task(self.project, run, "SHIP", "devops-engineer", 60)
        self.assertTrue(any(item["kind"] == "risk" and item["task"] == "SHIP" for item in team.load_state(run)["checkpoints"]))
        team.add_task(self.project, run, task_args("WIPE", "database-engineer", action="data-destructive", target="local", path=["db"]))
        with self.assertRaises(team.GateError):
            team.claim_task(self.project, run, "WIPE", "database-engineer", 60)
        self.assertEqual(team.load_state(run)["tasks"]["WIPE"]["risk"], "R4")
        self.assertEqual(team.load_state(run)["status"], "waiting-human")


class UnattendedReleaseTests(Base):
    """The five conditions of protocols/autonomy.md, each with its own refusal, then the exit."""

    def test_release_exits_without_a_checkpoint_once_the_conditions_hold(self) -> None:
        run = self.start()
        self.to_release(run)
        # 4: the release packet
        message = self.refusal(run)
        self.assertIn("RELEASE.md is missing", message)
        self.assertIn("stays gated", message)
        team.scaffold_artifact(self.project, run, "RELEASE.md")
        self.assertIn("RELEASE.md still has unfilled", self.refusal(run))
        write(run, "RELEASE.md", RELEASE_TEXT)
        # 4: the rehearsed rollback
        self.assertIn("no rollback rehearsal", self.refusal(run))
        self.rehearse(run, "RB0", owner="backend-engineer")
        self.assertIn("RB0 is owned by backend-engineer; it must be devops-engineer or release-manager", self.refusal(run))
        self.rehearse(run, "RB1", check=None)
        self.assertIn("RB1 declares no --check", self.refusal(run))
        self.rehearse(run, "RB")
        self.assertEqual(self.stage_checkpoints(run), [])
        self.assertEqual(team.advance_stage(self.project, run), "07_learn")
        state = team.load_state(run)
        self.assertEqual(state["stage"], "07_learn")
        self.assertEqual(self.stage_checkpoints(run), [], "no human checkpoint was opened")
        events = [event for event in team.read_events(run) if event["type"] == "release-conditions-met"]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["rehearsal"], "RB")
        self.assertEqual(events[0]["checked_tasks"], ["T1"])
        self.assertEqual(events[0]["max_risk"], "R1")
        self.assertEqual(events[0]["autonomy"], "unattended")

    def test_the_rehearsal_is_a_record_by_the_release_role(self) -> None:
        run = self.start()
        self.to_release(run)
        write(run, "RELEASE.md", RELEASE_TEXT)
        team.add_task(self.project, run, task_args("RB", "release-manager", action="rollback-test", path=[], check=[PASSING_CHECK]))
        problems = team.executable_release_problems(self.project, run, team.load_state(run))
        self.assertIn("rollback rehearsal RB is ready, not completed", problems)
        team.claim_task(self.project, run, "RB", "release-manager", 60)
        problems = team.executable_release_problems(self.project, run, team.load_state(run))
        self.assertIn("rollback rehearsal RB is claimed, not completed", problems)
        # An open task already blocks advance before the conditions are read.
        with self.assertRaises(team.TeamError) as raised:
            team.advance_stage(self.project, run)
        self.assertIn("unfinished tasks: RB", str(raised.exception))
        team.complete_task(self.project, run, "RB", "release-manager", ["note:rehearsed"])
        record = team.load_state(run)["tasks"]["RB"]["execs"][-1]
        self.assertEqual((record["agent"], record["exit_code"], record["command"]), ("release-manager", 0, PASSING_CHECK))
        self.assertEqual(team.advance_stage(self.project, run), "07_learn")

    def test_every_build_and_verify_check_must_have_a_passing_record(self) -> None:
        run = self.start()
        self.to_release(run)
        write(run, "RELEASE.md", RELEASE_TEXT)
        self.rehearse(run)
        state = team.load_state(run)
        # A record that did not pass (a legacy or hand-edited run) is not evidence.
        state["tasks"]["T1"]["execs"][-1]["exit_code"] = 1
        team.save_state(self.project, run, state)
        self.assertIn("task T1 has no passing exec record for: " + PASSING_CHECK, self.refusal(run))
        # A writing-role task without any check counts only with the human's checks waiver (G10).
        state = team.load_state(run)
        state["tasks"]["T1"]["checks"] = []
        team.save_state(self.project, run, state)
        self.assertIn("T1 changed the workspace but declares no acceptance check", self.refusal(run))
        team.waive_requirement(self.project, run, "checks:T1", "pre-v3 task, reviewed by hand", "Owner", self.token(run))
        self.assertEqual(team.advance_stage(self.project, run), "07_learn")

    def test_an_r2_task_puts_the_human_release_checkpoint_back(self) -> None:
        run = self.start()
        self.to_release(run)
        write(run, "RELEASE.md", RELEASE_TEXT)
        self.rehearse(run)
        self.finish(run, "MIG", "database-engineer", "migrated a local copy", action="migrate", target="local", path=["db"])
        self.assertEqual(team.load_state(run)["tasks"]["MIG"]["risk"], "R2")
        self.assertEqual(team.advance_stage(self.project, run), "waiting-human")
        checkpoints = self.stage_checkpoints(run)
        self.assertEqual(len(checkpoints), 1)
        self.assertEqual(checkpoints[0]["stage"], "06_release")
        self.assertIn("MIG", checkpoints[0]["recommendation"])
        self.assertIn("above R1", checkpoints[0]["recommendation"])
        self.assertEqual(team.load_state(run)["status"], "waiting-human")
        team.approve_checkpoint(self.project, run, checkpoints[0]["id"], "Owner", "reviewed the migration", self.token(run))
        self.assertEqual(team.advance_stage(self.project, run), "07_learn")
        self.assertFalse(any(event["type"] == "release-conditions-met" for event in team.read_events(run)))

    def test_a_staging_rehearsal_is_r2_and_keeps_the_click(self) -> None:
        run = self.start()
        self.to_release(run)
        write(run, "RELEASE.md", RELEASE_TEXT)
        self.finish(run, "RB", "devops-engineer", "rolled staging back", action="rollback-test", target="staging", path=[], check=[PASSING_CHECK])
        self.assertEqual(team.load_state(run)["tasks"]["RB"]["risk"], "R2")
        self.assertEqual(team.advance_stage(self.project, run), "waiting-human")
        self.assertEqual(len(self.stage_checkpoints(run)), 1)

    def test_a_pending_budget_checkpoint_blocks_the_unattended_release(self) -> None:
        run = self.start()
        self.to_release(run)
        write(run, "RELEASE.md", RELEASE_TEXT)
        self.rehearse(run)
        self.local_policy(budgets={"max_tasks": 3})  # two tasks exist; the third crosses the 80 % warning
        self.finish(run, "NOTES", "research-agent", "read the release notes", action="research", path=[])
        state = team.load_state(run)
        budget = [item for item in state["checkpoints"] if item["kind"] == "budget"]
        self.assertEqual(len(budget), 1)
        message = self.refusal(run)
        self.assertIn(f"budget checkpoint {budget[0]['id']} ('max_tasks') is pending", message)
        self.assertIn("waives budget:max_tasks", message)
        team.approve_checkpoint(self.project, run, budget[0]["id"], "Owner", "finish within the budget", self.token(run))
        self.assertEqual(team.advance_stage(self.project, run), "07_learn")

    @unittest.skipIf(shutil.which("git") is None, "git not installed")
    def test_verified_head_and_the_rehearsal_are_pinned_to_the_released_commit(self) -> None:
        def git(*args: str) -> str:
            return subprocess.run(["git", *args], cwd=self.project, check=True, capture_output=True, text=True).stdout.strip()

        def commit(name: str) -> str:
            (self.project / "app.txt").write_text(f"{name}\n", encoding="utf-8")
            git("add", "app.txt")
            git("commit", "-q", "-m", name)
            return git("rev-parse", "HEAD")

        git("init", "-q")
        git("config", "user.email", "t@example.com")
        git("config", "user.name", "T")
        first = commit("v1")
        run = self.start()
        self.to_release(run, sha=first[:12])
        write(run, "RELEASE.md", RELEASE_TEXT)
        self.rehearse(run)
        second = commit("v2")  # a commit after verification: condition 1 (verified-head) refuses first
        with self.assertRaises(team.TeamError) as raised:
            team.advance_stage(self.project, run)
        self.assertIn("verified commit", str(raised.exception))
        write(run, "VERIFICATION.md", PASS_HEADER.format(verifier="qa-lead", sha=second[:12]))
        message = self.refusal(run)  # the verdict is current again; the rehearsal is not
        self.assertIn(f"RB has no passing exec record by devops-engineer or release-manager at the current HEAD {second[:12]}", message)
        self.rehearse(run, "RB2")
        self.assertEqual(team.advance_stage(self.project, run), "07_learn")
        events = [event for event in team.read_events(run) if event["type"] == "release-conditions-met"]
        self.assertEqual((events[0]["rehearsal"], events[0]["released_head"]), ("RB2", second))

    def test_a_project_can_tighten_the_release_gate_back_to_human(self) -> None:
        self.local_policy(profiles={"unattended": {"release_gate": "human"}})
        run = self.start()
        self.assertIn("Human approval required", (run / "06_release" / "CONTEXT.md").read_text(encoding="utf-8"))
        self.to_release(run)
        write(run, "RELEASE.md", RELEASE_TEXT)
        self.rehearse(run)
        self.assertEqual(team.advance_stage(self.project, run), "waiting-human")
        checkpoints = self.stage_checkpoints(run)
        self.assertEqual([item["stage"] for item in checkpoints], ["06_release"])
        team.approve_checkpoint(self.project, run, checkpoints[0]["id"], "Owner", "go", self.token(run))
        self.assertEqual(team.advance_stage(self.project, run), "07_learn")

    def test_the_other_profiles_still_stop_at_release(self) -> None:
        for autonomy in ("autonomous", "supervised"):
            with self.subTest(autonomy=autonomy):
                self.project = fresh_project()
                run = self.start(autonomy)
                self.to_release(run)
                write(run, "RELEASE.md", RELEASE_TEXT)
                self.rehearse(run)
                self.assertEqual(team.advance_stage(self.project, run), "waiting-human")
                self.assertEqual(len(self.stage_checkpoints(run)), 1)


if __name__ == "__main__":
    unittest.main()
