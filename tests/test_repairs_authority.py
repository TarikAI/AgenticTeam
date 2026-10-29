"""Repair F1: authority stays binding on every path (audit findings A1-A4, A6)."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile
import shutil
import unittest

from helpers import fresh_project, run_cli, team
from test_regressions import task_args

DETAILS = {"alternatives": "wait", "impact": "delay", "evidence": "notes", "rollback": "revert"}


def marker_command(marker: Path) -> str:
    """A harmless command that leaves a file behind, so a test can tell whether it ran."""
    return f'"{sys.executable}" -c "open(r\'{marker}\', \'w\').close()"'


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self.project = fresh_project()
        self.run = team.init_run(self.project, "Repairs", "repairs", "autonomous", "execute-only", "adaptive")
        self.scratch = Path(tempfile.mkdtemp(prefix="agentic-marker-"))
        self.addCleanup(shutil.rmtree, self.scratch, True)

    def token(self) -> str:
        return team.owner_token_file(team.load_state(self.run)).read_text(encoding="utf-8").strip()

    def reject_decision(self) -> str:
        checkpoint = team.create_checkpoint(self.project, self.run, "Vendor?", "A", "R2", "decision", details=DETAILS)
        team.reject_checkpoint(self.project, self.run, checkpoint, "Owner", "no", self.token())
        return checkpoint

    def edit_state(self, change) -> None:
        state = team.load_state(self.run)
        change(state)
        team.write_json_atomic(self.run / "state.json", state)

    def gated(self, task_id: str = "SHIP", action: str = "deploy", target: str = "production") -> str:
        team.add_task(self.project, self.run, task_args(task_id, "devops-engineer", action=action, target=target, path=[f"deploy/{task_id}"]))
        with self.assertRaises(team.GateError):
            team.claim_task(self.project, self.run, task_id, "devops-engineer", 60)
        return next(item["id"] for item in team.load_state(self.run)["checkpoints"] if item.get("task") == task_id)


class SignedRejectionTests(Base):
    """A1: the effective disposition comes from ordered signed decisions, not from state.json."""

    def test_reclassifying_a_rejected_checkpoint_does_not_reopen_the_run(self) -> None:
        checkpoint = self.reject_decision()
        team.add_task(self.project, self.run, task_args("A", "backend-engineer"))

        def forge(state):
            for item in state["checkpoints"]:
                if item["id"] == checkpoint:
                    item["status"] = "recorded"
            state["status"] = "active"
        self.edit_state(forge)
        with self.assertRaises(team.BlockedError):
            team.claim_task(self.project, self.run, "A", "backend-engineer", 60)
        problems = team.audit_verify(self.project, self.run, self.token())
        self.assertTrue(any(checkpoint in problem and "rejected" in problem for problem in problems), problems)

    def test_deleting_or_renumbering_the_rejection_does_not_reopen_the_run(self) -> None:
        checkpoint = self.reject_decision()
        team.add_task(self.project, self.run, task_args("A", "backend-engineer"))
        for forge in (
            lambda state: state.update(checkpoints=[item for item in state["checkpoints"] if item["id"] != checkpoint], status="active"),
            lambda state: [item.update(id="CP-099", status="recorded") for item in state["checkpoints"] if item["id"] == checkpoint],
        ):
            self.edit_state(forge)
            self.edit_state(lambda state: state.update(status="active"))
            with self.assertRaises(team.BlockedError):
                team.claim_task(self.project, self.run, "A", "backend-engineer", 60)
        problems = team.audit_verify(self.project, self.run, self.token())
        self.assertTrue(any("no longer lists" in problem for problem in problems), problems)

    def test_only_a_signed_resolution_clears_it_even_after_deletion(self) -> None:
        checkpoint = self.reject_decision()
        team.add_task(self.project, self.run, task_args("A", "backend-engineer"))
        self.edit_state(lambda state: state.update(checkpoints=[item for item in state["checkpoints"] if item["id"] != checkpoint]))
        with self.assertRaises(team.TeamError):
            team.resolve_checkpoint(self.project, self.run, checkpoint, "Owner", "fixed", "not-the-token")
        team.resolve_checkpoint(self.project, self.run, checkpoint, "Owner", "fixed", self.token())
        team.claim_task(self.project, self.run, "A", "backend-engineer", 60)

    def test_an_approval_does_not_follow_its_id_to_another_checkpoint(self) -> None:
        harmless = team.create_checkpoint(self.project, self.run, "Font?", "A", "R1", "decision", details=DETAILS)
        team.approve_checkpoint(self.project, self.run, harmless, "Owner", "fine", self.token())
        risky = self.gated()

        def swap(state):
            for item in state["checkpoints"]:
                if item["id"] == harmless:
                    item["id"] = "CP-090"
            for item in state["checkpoints"]:
                if item["id"] == risky:
                    item.update(id=harmless, status="approved")
        self.edit_state(swap)
        with self.assertRaises(team.GateError):
            team.claim_task(self.project, self.run, "SHIP", "devops-engineer", 60)

    def test_re_approving_an_edited_rejection_is_refused(self) -> None:
        checkpoint = self.reject_decision()
        self.edit_state(lambda state: [item.update(status="pending") for item in state["checkpoints"] if item["id"] == checkpoint])
        with self.assertRaises(team.TeamError) as raised:
            team.approve_checkpoint(self.project, self.run, checkpoint, "Owner", "ok", self.token())
        self.assertIn("resolve", str(raised.exception))
        self.assertEqual(team.rejected_checkpoints(team.load_state(self.run)), [checkpoint])

    def test_a_genuine_approval_still_admits_the_claim(self) -> None:
        risky = self.gated()
        team.approve_checkpoint(self.project, self.run, risky, "Owner", "ship", self.token())
        team.claim_task(self.project, self.run, "SHIP", "devops-engineer", 60)
        self.assertEqual(team.audit_verify(self.project, self.run, self.token()), [])


class ExecutionGateTests(Base):
    """A2: no new process after rejection or closure; recording stays possible."""

    def claimed(self, marker: Path) -> None:
        team.add_task(self.project, self.run, task_args("A", "backend-engineer", check=[marker_command(marker)]))
        team.claim_task(self.project, self.run, "A", "backend-engineer", 60)

    def test_exec_and_completion_checks_start_nothing_after_rejection(self) -> None:
        marker = self.scratch / "ran"
        self.claimed(marker)
        self.reject_decision()
        code, _, err = run_cli(self.project, "exec", "--project", str(self.project), "--task", "A", "--agent", "backend-engineer",
                               "--shell", "--", marker_command(marker))
        self.assertEqual(code, 3, err)
        with self.assertRaises(team.BlockedError):
            team.complete_task(self.project, self.run, "A", "backend-engineer", ["note:done"])
        self.assertFalse(marker.exists(), "a command ran while the run was rejected")
        # Passive reporting and authenticated recovery still work.
        self.assertEqual(run_cli(self.project, "status", "--project", str(self.project))[0], 0)

    def test_editing_the_status_back_does_not_restore_exec(self) -> None:
        marker = self.scratch / "ran"
        self.claimed(marker)
        checkpoint = self.reject_decision()
        self.edit_state(lambda state: [state.update(status="active")] + [item.update(status="recorded") for item in state["checkpoints"] if item["id"] == checkpoint])
        with self.assertRaises(team.BlockedError):
            team.exec_command(self.project, self.run, "A", "backend-engineer", [marker_command(marker)], shell=True)
        self.assertFalse(marker.exists())

    def test_exec_starts_nothing_after_closure(self) -> None:
        marker = self.scratch / "ran"
        self.claimed(marker)
        team.close_run(self.project, self.run, "stop")
        self.edit_state(lambda state: state.update(status="active"))
        with self.assertRaises(team.BlockedError):
            team.exec_command(self.project, self.run, "A", "backend-engineer", [marker_command(marker)], shell=True)
        self.assertFalse(marker.exists())

    def test_restoring_pre_close_state_and_events_does_not_reopen(self) -> None:
        marker = self.scratch / "ran"
        self.claimed(marker)
        saved = {name: (self.run / name).read_bytes() for name in ("state.json", "events.jsonl")}
        team.close_run(self.project, self.run, "stop")
        for name, data in saved.items():
            (self.run / name).write_bytes(data)
        with self.assertRaises(team.BlockedError):
            team.exec_command(self.project, self.run, "A", "backend-engineer", [marker_command(marker)], shell=True)
        self.assertFalse(marker.exists())
        problems = team.audit_verify(self.project, self.run, self.token())
        self.assertTrue(any("closed" in problem for problem in problems), problems)

    def test_a_torn_event_line_does_not_read_as_closure(self) -> None:
        team.add_task(self.project, self.run, task_args("A", "backend-engineer"))
        with team.events_path(self.run).open("ab") as handle:
            handle.write(b'{"seq": 99, "type": "task-ad')
        team.claim_task(self.project, self.run, "A", "backend-engineer", 60)
        self.assertEqual(team.audit_verify(self.project, self.run, self.token()), [])


class ActionApprovalTests(Base):
    """A3: an approval covers its task's action, target and risk, not just any R3 command."""

    def test_an_approved_deploy_cannot_publish_through_the_cli(self) -> None:
        checkpoint = self.gated()
        team.approve_checkpoint(self.project, self.run, checkpoint, "Owner", "ship", self.token())
        team.claim_task(self.project, self.run, "SHIP", "devops-engineer", 60)
        base = ["exec", "--project", str(self.project), "--task", "SHIP", "--agent", "devops-engineer", "--shell", "--"]
        code, _, err = run_cli(self.project, *base, "echo npm publish")
        self.assertEqual(code, 2, err)
        self.assertIn("publish", err)
        self.assertEqual(len(team.load_state(self.run)["tasks"]["SHIP"].get("execs", [])), 0)
        code, out, err = run_cli(self.project, *base, "echo fly deploy")
        self.assertEqual(code, 0, err)

    def test_an_approved_command_cannot_carry_a_chained_one(self) -> None:
        checkpoint = self.gated()
        team.approve_checkpoint(self.project, self.run, checkpoint, "Owner", "ship", self.token())
        team.claim_task(self.project, self.run, "SHIP", "devops-engineer", 60)
        for command in ("echo fly deploy && echo docker push evil/img", "echo fly deploy; echo gh release create v9",
                        "echo fly deploy && echo git push --force"):
            with self.subTest(command=command), self.assertRaises(team.GateError):
                team.exec_command(self.project, self.run, "SHIP", "devops-engineer", [command], shell=True)
            previous = os.environ.pop("CLAUDE_PROJECT_DIR", None)
            try:
                reason = team.guard_decision({"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(self.project)})
            finally:
                if previous is not None:
                    os.environ["CLAUDE_PROJECT_DIR"] = previous
            self.assertIsNotNone(reason, command)
        self.assertEqual(team.load_state(self.run)["tasks"]["SHIP"].get("execs", []), [])

    def test_changing_the_approved_scope_voids_the_approval(self) -> None:
        checkpoint = self.gated()
        team.approve_checkpoint(self.project, self.run, checkpoint, "Owner", "ship", self.token())
        team.claim_task(self.project, self.run, "SHIP", "devops-engineer", 60)
        self.edit_state(lambda state: [item.update(action="publish") for item in state["checkpoints"] if item["id"] == checkpoint]
                        + [state["tasks"]["SHIP"].update(action="publish")])
        with self.assertRaises(team.GateError):
            team.exec_command(self.project, self.run, "SHIP", "devops-engineer", ["echo npm publish"], shell=True)


class GuardFailClosedTests(Base):
    """A4: once a risky rule matches, missing or unreadable approval context denies."""

    def payload(self, command: str) -> dict:
        return {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(self.project)}

    def decide(self, command: str) -> str | None:
        previous = os.environ.pop("CLAUDE_PROJECT_DIR", None)
        try:
            return team.guard_decision(self.payload(command))
        finally:
            if previous is not None:
                os.environ["CLAUDE_PROJECT_DIR"] = previous

    def test_no_current_run_denies_a_publish_and_allows_safe_commands(self) -> None:
        bare = fresh_project()
        previous = os.environ.pop("CLAUDE_PROJECT_DIR", None)
        try:
            reason = team.guard_decision({"tool_name": "Bash", "tool_input": {"command": "npm publish"}, "cwd": str(bare)})
            self.assertIsNotNone(reason)
            self.assertIn("could not be checked", reason)
            self.assertIsNone(team.guard_decision({"tool_name": "Bash", "tool_input": {"command": "npm test"}, "cwd": str(bare)}))
        finally:
            if previous is not None:
                os.environ["CLAUDE_PROJECT_DIR"] = previous

    def test_missing_state_and_malformed_policy_deny(self) -> None:
        (self.run / "state.json").rename(self.run / "state.moved")
        self.assertIsNotNone(self.decide("git push origin main"))
        (self.run / "state.moved").rename(self.run / "state.json")
        (self.project / ".agentic-team" / "config" / "policies.local.json").write_text("{not json", encoding="utf-8")
        self.assertIsNotNone(self.decide("git push origin main"))
        self.assertIsNone(self.decide("git status"))

    def test_unverifiable_ledger_denies_and_a_real_approval_allows(self) -> None:
        checkpoint = self.gated("PUB", action="publish", target="external")
        team.approve_checkpoint(self.project, self.run, checkpoint, "Owner", "go", self.token())
        team.claim_task(self.project, self.run, "PUB", "devops-engineer", 60)
        self.assertIsNone(self.decide("npm publish"))
        self.assertIsNotNone(self.decide("fly deploy"), "a publish approval must not cover a deploy")
        binding = team.binding_path(team.home_key(team.load_state(self.run)))
        binding.rename(binding.with_suffix(".moved"))
        try:
            self.assertIsNotNone(self.decide("npm publish"))
        finally:
            binding.with_suffix(".moved").rename(binding)


class ManifestContainmentTests(unittest.TestCase):
    """A6: uninstall and reinstall touch only paths inside the project."""

    def setUp(self) -> None:
        self.parent = Path(tempfile.mkdtemp(prefix="agentic-uninstall-"))
        self.addCleanup(shutil.rmtree, self.parent, True)
        self.project = self.parent / "project"
        team.install_team(Path(__file__).resolve().parents[1], self.project, "generic", "full-company", [], [])
        self.sentinel = self.parent / "sentinel.txt"
        self.sentinel.write_text("keep", encoding="utf-8")
        self.record_path = self.project / ".agentic-team" / "install-manifest.json"

    def poison(self, **changes) -> None:
        record = json.loads(self.record_path.read_text(encoding="utf-8"))
        record.update(changes)
        self.record_path.write_text(json.dumps(record), encoding="utf-8")

    def assert_refused_without_change(self, action) -> None:
        before = sorted(str(path) for path in self.project.rglob("*"))
        with self.assertRaises(team.TeamError) as raised:
            action()
        self.assertIn("Unsafe", str(raised.exception))
        self.assertTrue(self.sentinel.exists())
        self.assertEqual(sorted(str(path) for path in self.project.rglob("*")), before, "a partial deletion happened")

    def test_escaping_paths_are_refused_before_any_deletion(self) -> None:
        record = json.loads(self.record_path.read_text(encoding="utf-8"))
        cases = [
            {"generated_files": record["generated_files"] + ["../sentinel.txt"]},
            {"generated_files": record["generated_files"] + [str(self.sentinel)]},
            {"generated_files": record["generated_files"] + ["/etc/hosts"]},
            {"owned_settings": {"../sentinel.txt": {}}},
            {"skill_dir": ".."},
            {"skills": record["skills"] + ["../../sentinel.txt"]},
        ]
        for case in cases:
            self.record_path.write_text(json.dumps({**record, **case}), encoding="utf-8")
            with self.subTest(case=case):
                self.assert_refused_without_change(lambda: team.uninstall_team(self.project))
                self.assert_refused_without_change(
                    lambda: team.install_team(Path(__file__).resolve().parents[1], self.project, "generic", "full-company", [], []))

    def test_a_symlinked_folder_cannot_carry_deletion_outside(self) -> None:
        outside = self.parent / "outside"
        outside.mkdir()
        (outside / "victim.md").write_text("keep", encoding="utf-8")
        link = self.project / "linked"
        try:
            os.symlink(outside, link, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks are not available to this user")
        record = json.loads(self.record_path.read_text(encoding="utf-8"))
        self.poison(generated_files=record["generated_files"] + ["linked/victim.md"])
        with self.assertRaises(team.TeamError):
            team.uninstall_team(self.project)
        self.assertTrue((outside / "victim.md").exists())

    def test_normal_uninstall_keeps_project_state(self) -> None:
        runs = self.project / ".agentic-team" / "runs" / "keep"
        runs.mkdir(parents=True)
        (runs / "state.json").write_text("{}", encoding="utf-8")
        team.uninstall_team(self.project)
        self.assertTrue((runs / "state.json").exists())
        self.assertTrue(self.sentinel.exists())


if __name__ == "__main__":
    unittest.main()
