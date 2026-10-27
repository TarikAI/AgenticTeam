"""P3: stage exit contracts, typed evidence, exec capture, independent verification."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

from helpers import fresh_project, run_cli, team
from test_regressions import FAILING_CHECK, PASSING_CHECK, task_args

PASS_HEADER = "Verdict: PASS\nVerifier: {verifier}\nVerified-SHA: {sha}\n\n# Verification\n\n| AC-1 | tests | pass | cmd |\n"


def write(run_dir: Path, name: str, text: str) -> None:
    (run_dir / name).write_text(text, encoding="utf-8")


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self.project = fresh_project()

    def token(self, run_dir: Path) -> str:
        return team.owner_token_file(team.load_state(run_dir)).read_text(encoding="utf-8").strip()

    def build_and_finish(self, run: Path, task_id: str = "T1", owner: str = "backend-engineer") -> None:
        team.add_task(self.project, run, task_args(task_id, owner))
        team.claim_task(self.project, run, task_id, owner, 60)
        record = team.exec_command(self.project, run, task_id, owner, [sys.executable, "-c", "print('ok')"])
        team.complete_task(self.project, run, task_id, owner, [f"cmd:{record['id']}"])


class StageExitTests(Base):
    def test_R10_an_empty_run_cannot_walk_to_release(self) -> None:
        run = team.init_run(self.project, "Empty", "empty", "autonomous", "idea", "bmad-progressive")
        with self.assertRaises(team.TeamError) as raised:
            team.advance_stage(self.project, run)
        self.assertIn("BRIEF.md is missing", str(raised.exception))
        self.assertEqual(team.load_state(run)["stage"], "00_intake")

    def test_scaffolded_templates_are_not_accepted_until_filled(self) -> None:
        run = team.init_run(self.project, "Scaffold", "sc", "autonomous", "idea", "bmad-progressive")
        team.scaffold_artifact(self.project, run, "BRIEF.md")
        team.scaffold_artifact(self.project, run, "ASSUMPTIONS.md")
        with self.assertRaises(team.TeamError) as raised:
            team.advance_stage(self.project, run)
        self.assertIn("unfilled", str(raised.exception))
        write(run, "BRIEF.md", "# Brief\n\n- AC-1: sign in\n")
        write(run, "ASSUMPTIONS.md", "# Assumptions\n\n| A-1 | email login | common | ask | rework |\n")
        self.assertEqual(team.advance_stage(self.project, run), "01_product")
        context = (run / "00_intake" / "CONTEXT.md").read_text(encoding="utf-8")
        self.assertIn("Status: `complete`", context)
        self.assertIn("Status: `active`", (run / "01_product" / "CONTEXT.md").read_text(encoding="utf-8"))

    def test_readiness_must_trace_every_acceptance_id(self) -> None:
        run = team.init_run(self.project, "Trace", "trace", "autonomous", "plan-given", "bmad-progressive")
        write(run, "PRD.md", "# PRD\n\n- AC-1: a\n- AC-2: b\n")
        write(run, "READINESS.md", "# Readiness\n\n| AC-1 | T1 | test |\n")
        with self.assertRaises(team.TeamError) as raised:
            team.advance_stage(self.project, run)
        self.assertIn("does not trace AC-2", str(raised.exception))
        write(run, "READINESS.md", "# Readiness\n\n| AC-1 | T1 | test |\n| AC-2 | T2 | test |\n")
        self.assertEqual(team.advance_stage(self.project, run), "04_build")

    def test_active_specialist_must_finish_or_be_deactivated(self) -> None:
        run = team.init_run(self.project, "Spec", "spec", "autonomous", "execute-only", "adaptive")
        team.route_specialists(self.project, run, ["personal data"])
        with self.assertRaises(team.TeamError) as raised:
            team.advance_stage(self.project, run)
        self.assertIn("privacy-engineer", str(raised.exception))
        team.deactivate_specialist(self.project, run, "privacy-engineer", "no personal data after all")
        self.assertEqual(team.advance_stage(self.project, run), "05_verify")

    def test_waiver_is_human_only_and_named(self) -> None:
        run = team.init_run(self.project, "Waive", "waive", "autonomous", "idea", "bmad-progressive")
        write(run, "BRIEF.md", "# Brief\n")
        with self.assertRaises(team.TeamError):
            team.waive_requirement(self.project, run, "stage-exit:00_intake:artifact:ASSUMPTIONS.md", "n/a", "ceo", self.token(run))
        team.waive_requirement(self.project, run, "stage-exit:00_intake:artifact:ASSUMPTIONS.md", "no assumptions", "Owner", self.token(run))
        self.assertEqual(team.advance_stage(self.project, run), "01_product")


class EvidenceTests(Base):
    def run_(self) -> Path:
        return team.init_run(self.project, "Evidence", "ev", "autonomous", "execute-only", "adaptive")

    def test_R17_evidence_must_be_real(self) -> None:
        run = self.run_()
        team.add_task(self.project, run, task_args("A", "backend-engineer"))
        team.claim_task(self.project, run, "A", "backend-engineer", 60)
        with self.assertRaises(team.TeamError):
            team.complete_task(self.project, run, "A", "backend-engineer", ["file:does/not/exist.txt"])
        with self.assertRaises(team.TeamError):
            team.complete_task(self.project, run, "A", "backend-engineer", ["all tests pass (trust me)"])
        with self.assertRaises(team.TeamError):
            team.complete_task(self.project, run, "A", "backend-engineer", ["cmd:A-99"])
        with self.assertRaises(team.TeamError):
            team.complete_task(self.project, run, "A", "backend-engineer", ["file:../outside.txt"])
        (self.project / "src" / "a").mkdir(parents=True)
        (self.project / "src" / "a" / "main.py").write_text("print(1)\n", encoding="utf-8")
        team.complete_task(self.project, run, "A", "backend-engineer", ["file:src/a/main.py"])
        record = team.load_state(run)["tasks"]["A"]["evidence_records"][0]
        self.assertEqual(record["type"], "file")
        self.assertEqual(len(record["sha256"]), 64)

    def test_docs_tasks_may_complete_with_notes(self) -> None:
        run = self.run_()
        team.add_task(self.project, run, task_args("DOC", "tech-writer", action="docs"))
        team.claim_task(self.project, run, "DOC", "tech-writer", 60)
        team.complete_task(self.project, run, "DOC", "tech-writer", ["note:README updated"])

    def test_exec_records_and_checks_gate_completion(self) -> None:
        run = self.run_()
        failing = f'"{sys.executable}" -c "import sys; sys.exit(3)"'
        team.add_task(self.project, run, task_args("A", "backend-engineer", check=[failing]))
        team.claim_task(self.project, run, "A", "backend-engineer", 60)
        with self.assertRaises(team.TeamError):
            team.complete_task(self.project, run, "A", "backend-engineer", [], run_checks=True)
        task = team.load_state(run)["tasks"]["A"]
        self.assertEqual(task["execs"][0]["exit_code"], 3)
        log = run / task["execs"][0]["log"]
        self.assertIn("exit 3", log.read_text(encoding="utf-8"))

    def test_passing_checks_complete_the_task(self) -> None:
        run = self.run_()
        passing = f'"{sys.executable}" -c "print(42)"'
        team.add_task(self.project, run, task_args("A", "backend-engineer", check=[passing]))
        team.claim_task(self.project, run, "A", "backend-engineer", 60)
        team.complete_task(self.project, run, "A", "backend-engineer", [], run_checks=True)
        self.assertEqual(team.load_state(run)["tasks"]["A"]["status"], "completed")

    def test_build_tasks_must_declare_an_acceptance_check(self) -> None:
        run = self.run_()
        with self.assertRaises(team.TeamError) as raised:
            team.add_task(self.project, run, task_args("A", "backend-engineer", check=[]))
        self.assertIn("--check", str(raised.exception))
        team.add_task(self.project, run, task_args("DOC", "tech-writer", action="docs", check=[]))  # not workspace-changing work
        team.add_task(self.project, run, task_args("R", "code-reviewer", action="inspect", path=[], check=[]))
        policy_path = self.project / ".agentic-team" / "config" / "policies.json"
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["evidence"]["write_tasks_need_checks"] = False
        policy_path.write_text(json.dumps(policy), encoding="utf-8")
        team.add_task(self.project, run, task_args("B", "backend-engineer", check=[]))

    def test_completion_runs_the_checks_and_a_file_alone_cannot_finish_build_work(self) -> None:
        run = self.run_()
        team.add_task(self.project, run, task_args("A", "backend-engineer", check=[FAILING_CHECK]))
        team.claim_task(self.project, run, "A", "backend-engineer", 60)
        (self.project / "src" / "a").mkdir(parents=True)
        (self.project / "src" / "a" / "main.py").write_text("print(1)\n", encoding="utf-8")
        with self.assertRaises(team.TeamError) as raised:
            team.complete_task(self.project, run, "A", "backend-engineer", ["file:src/a/main.py"])
        self.assertIn("no passing exec record", str(raised.exception))
        task = team.load_state(run)["tasks"]["A"]
        self.assertEqual([item["exit_code"] for item in task["execs"]], [3], "complete ran the declared check itself")
        self.assertEqual(task["status"], "claimed")

    def test_a_task_recorded_without_checks_completes_only_with_the_human_waiver(self) -> None:
        run = self.run_()
        team.add_task(self.project, run, task_args("A", "backend-engineer"))
        state = team.load_state(run)
        state["tasks"]["A"]["checks"] = []  # recorded before checks were required
        team.write_json_atomic(run / "state.json", state)
        team.claim_task(self.project, run, "A", "backend-engineer", 60)
        record = team.exec_command(self.project, run, "A", "backend-engineer", [sys.executable, "-c", "pass"])
        with self.assertRaises(team.TeamError) as raised:
            team.complete_task(self.project, run, "A", "backend-engineer", [f"cmd:{record['id']}"])
        self.assertIn("checks:A", str(raised.exception))
        with self.assertRaises(team.TeamError):
            team.waive_requirement(self.project, run, "checks:A", "legacy", "backend-engineer", self.token(run))
        team.waive_requirement(self.project, run, "checks:A", "legacy task, checked by hand", "Owner", self.token(run))
        team.complete_task(self.project, run, "A", "backend-engineer", [f"cmd:{record['id']}"])
        self.assertEqual(team.load_state(run)["tasks"]["A"]["status"], "completed")

    def test_exec_refuses_external_commands_without_an_approved_task(self) -> None:
        run = self.run_()
        team.add_task(self.project, run, task_args("A", "backend-engineer"))
        team.claim_task(self.project, run, "A", "backend-engineer", 60)
        with self.assertRaises(team.GateError):
            team.exec_command(self.project, run, "A", "backend-engineer", ["git push --force origin main"], shell=True)
        with self.assertRaises(team.GateError):
            team.exec_command(self.project, run, "A", "backend-engineer", ["npx vercel deploy --prod"], shell=True)

    def test_exec_through_the_cli(self) -> None:
        run = self.run_()
        team.add_task(self.project, run, task_args("A", "backend-engineer"))
        team.claim_task(self.project, run, "A", "backend-engineer", 60)
        code, out, err = run_cli(self.project, "exec", "--project", str(self.project), "--task", "A",
                                 "--agent", "backend-engineer", "--", sys.executable, "-c", "print('hi')")
        self.assertEqual(code, 0, err)
        self.assertIn("A-1: exit 0", out)


class VerificationTests(Base):
    def verify_stage(self, run: Path) -> None:
        self.build_and_finish(run)
        self.assertEqual(team.advance_stage(self.project, run), "05_verify")

    def test_builder_cannot_claim_its_own_verification(self) -> None:
        run = team.init_run(self.project, "V", "v", "autonomous", "execute-only", "adaptive")
        self.build_and_finish(run)
        team.add_task(self.project, run, task_args("V1", "backend-engineer", verifies=["T1"], action="test"))
        with self.assertRaises(team.TeamError) as raised:
            team.claim_task(self.project, run, "V1", "backend-engineer", 60)
        self.assertIn("independent", str(raised.exception))

    def test_verdict_contract(self) -> None:
        run = team.init_run(self.project, "V", "v", "autonomous", "execute-only", "adaptive")
        self.verify_stage(run)
        with self.assertRaises(team.TeamError):
            team.advance_stage(self.project, run)  # no VERIFICATION.md
        write(run, "VERIFICATION.md", PASS_HEADER.format(verifier="backend-engineer", sha="none"))
        with self.assertRaises(team.TeamError) as raised:
            team.advance_stage(self.project, run)
        self.assertIn("independent", str(raised.exception))
        write(run, "VERIFICATION.md", PASS_HEADER.replace("PASS", "FAIL").format(verifier="qa-lead", sha="none"))
        with self.assertRaises(team.TeamError):
            team.advance_stage(self.project, run)
        write(run, "VERIFICATION.md", PASS_HEADER.replace("PASS", "CONDITIONAL").format(verifier="qa-lead", sha="none"))
        with self.assertRaises(team.TeamError) as raised:
            team.advance_stage(self.project, run)
        self.assertIn("waiver", str(raised.exception))
        write(run, "VERIFICATION.md", PASS_HEADER.format(verifier="qa-lead", sha="none"))
        self.assertEqual(team.advance_stage(self.project, run), "06_release")

    @unittest.skipIf(shutil.which("git") is None, "git not installed")
    def test_verified_sha_must_be_the_current_head_through_release(self) -> None:
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
        commit("v1")
        run = team.init_run(self.project, "V", "v", "autonomous", "execute-only", "adaptive")
        team.add_task(self.project, run, task_args("T1", "backend-engineer"))
        team.claim_task(self.project, run, "T1", "backend-engineer", 60)
        team.exec_command(self.project, run, "T1", "backend-engineer", [PASSING_CHECK], shell=True)
        commit("v2")  # the check passed at v1; the task completes at v2, so completion runs it again
        team.complete_task(self.project, run, "T1", "backend-engineer", ["note:built"])
        execs = team.load_state(run)["tasks"]["T1"]["execs"]
        self.assertEqual(len(execs), 2)
        self.assertEqual(execs[-1]["git_head"], git("rev-parse", "HEAD"))
        self.assertEqual(team.advance_stage(self.project, run), "05_verify")
        integration = team.load_state(run)["integration_sha"]
        self.assertEqual(integration, git("rev-parse", "HEAD"))

        write(run, "VERIFICATION.md", PASS_HEADER.format(verifier="qa-lead", sha="deadbeef"))
        with self.assertRaises(team.TeamError) as raised:
            team.advance_stage(self.project, run)
        self.assertIn("not the current HEAD", str(raised.exception))
        write(run, "VERIFICATION.md", PASS_HEADER.format(verifier="qa-lead", sha=integration[:12]))
        remediated = commit("v3")  # remediation inside 05_verify moved HEAD: the verdict is stale
        with self.assertRaises(team.TeamError) as raised:
            team.advance_stage(self.project, run)
        self.assertIn("changed after", str(raised.exception))
        write(run, "VERIFICATION.md", PASS_HEADER.format(verifier="qa-lead", sha=remediated[:12]))
        self.assertEqual(team.advance_stage(self.project, run), "06_release")
        self.assertEqual(team.load_state(run)["verified_sha"], remediated)

        commit("v4")  # a commit after verification cannot ride the old verdict into production
        with self.assertRaises(team.TeamError) as raised:
            team.advance_stage(self.project, run)
        self.assertIn("verified commit", str(raised.exception))
        write(run, "VERIFICATION.md", PASS_HEADER.format(verifier="qa-lead", sha=git("rev-parse", "HEAD")[:12]))
        self.assertEqual(team.advance_stage(self.project, run), "waiting-human")  # only the human release gate remains


if __name__ == "__main__":
    unittest.main()
