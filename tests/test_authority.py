"""P2: human authority, decision ledger, risk model, policy gates (plan §5.2-§5.4)."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from helpers import fresh_project, run_cli, team
from test_regressions import task_args

DETAILS = {"alternatives": "wait", "impact": "delay", "evidence": "notes", "rollback": "revert"}

BENIGN = [
    "Write consumer contract tests for orders API",
    "Build payment form UI with client-side validation",
    "Truncate long product titles in card component",
    "Purge unused CSS",
    "Publish domain event to in-process bus",
    "Screen reader should announce form errors",
    "Add billing page skeleton",
    "POST to /api/users handler",
    "Document deployment steps in README",
    "Credential form field validation",
    "Add legal disclaimer footer text",
]
DANGEROUS = [
    "Run vercel --prod after merge",
    "terraform apply the new VPC",
    "kubectl apply the manifests",
    "git push --force to clean up",
    "Deploy the API to production",
    "Make it live on the prod cluster",
]


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self.project = fresh_project()

    def run_(self, autonomy: str = "autonomous", entry: str = "execute-only") -> Path:
        return team.init_run(self.project, "Authority", "auth", autonomy, entry, "adaptive")

    @staticmethod
    def token(run_dir: Path) -> str:
        return team.owner_token_file(team.load_state(run_dir)).read_text(encoding="utf-8").strip()

    def gated_task(self, run_dir: Path) -> str:
        team.add_task(self.project, run_dir, task_args("SHIP", "devops-engineer", action="deploy", target="production", path=["deploy"]))
        with self.assertRaises(team.GateError):
            team.claim_task(self.project, run_dir, "SHIP", "devops-engineer", 60)
        return next(item["id"] for item in team.load_state(run_dir)["checkpoints"] if item["kind"] == "risk")


class ForgeryTests(Base):
    def test_R06_swapping_the_state_hash_fails_closed(self) -> None:
        run = self.run_()
        checkpoint = self.gated_task(run)
        state = team.load_state(run)
        forged_token = "agent-made-this"
        import hashlib

        state["owner_token_sha256"] = hashlib.sha256(forged_token.encode()).hexdigest()
        team.write_json_atomic(run / "state.json", state)
        with self.assertRaises(team.TeamError) as raised:
            team.approve_checkpoint(self.project, run, checkpoint, "Owner", "self", forged_token)
        self.assertIn("Owner key mismatch", str(raised.exception))
        with self.assertRaises(team.TeamError):
            team.claim_task(self.project, run, "SHIP", "devops-engineer", 60)

    def test_R06_an_approval_injected_into_state_is_not_honoured(self) -> None:
        run = self.run_()
        checkpoint = self.gated_task(run)
        state = team.load_state(run)
        for item in state["checkpoints"]:
            if item["id"] == checkpoint:
                item.update(status="approved", approved_by="Owner")
        state["status"] = "active"
        team.write_json_atomic(run / "state.json", state)
        with self.assertRaises(team.GateError):
            team.claim_task(self.project, run, "SHIP", "devops-engineer", 60)

    def test_real_approval_goes_through_the_ledger(self) -> None:
        run = self.run_()
        checkpoint = self.gated_task(run)
        team.approve_checkpoint(self.project, run, checkpoint, "Owner", "ship it", self.token(run))
        team.claim_task(self.project, run, "SHIP", "devops-engineer", 60)
        self.assertEqual(team.audit_verify(self.project, run, self.token(run)), [])

    def test_audit_verify_detects_a_tampered_ledger_line(self) -> None:
        run = self.run_()
        checkpoint = self.gated_task(run)
        team.approve_checkpoint(self.project, run, checkpoint, "Owner", "ship it", self.token(run))
        ledger = team.ledger_path(team.home_key(team.load_state(run)))
        records = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
        records[0]["decision"] = "edited after the fact"
        ledger.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
        problems = team.audit_verify(self.project, run, self.token(run))
        self.assertTrue(any("not signed by the owner" in problem for problem in problems), problems)

    def test_audit_verify_detects_a_state_only_approval(self) -> None:
        run = self.run_()
        checkpoint = self.gated_task(run)
        state = team.load_state(run)
        state["checkpoints"][0]["status"] = "approved"
        team.write_json_atomic(run / "state.json", state)
        problems = team.audit_verify(self.project, run, self.token(run))
        self.assertTrue(any(checkpoint in problem for problem in problems))

    def test_cancel_forged_in_state_does_not_open_the_gate(self) -> None:
        run = self.run_()
        team.add_task(self.project, run, task_args("A", "backend-engineer"))
        state = team.load_state(run)
        state["tasks"]["A"]["status"] = "cancelled"
        team.write_json_atomic(run / "state.json", state)
        with self.assertRaises(team.TeamError):
            team.advance_stage(self.project, run)

    def test_owner_material_is_unique_per_run_not_per_name(self) -> None:
        other = fresh_project()
        first = self.run_()
        second = team.init_run(other, "Other", "auth", "autonomous", "execute-only", "adaptive")
        self.assertNotEqual(team.home_key(team.load_state(first)), team.home_key(team.load_state(second)))


class CheckpointRules(Base):
    def test_R13_agents_cannot_author_gate_checkpoints(self) -> None:
        run = self.run_()
        for kind in ("stage", "risk", "waiver"):
            with self.assertRaises(team.TeamError):
                team.create_checkpoint(self.project, run, "Approve minor copy tweak?", "yes", "R1", kind, details=DETAILS)
        with self.assertRaises(team.TeamError):
            team.create_checkpoint(self.project, run, "Vendor?", "A", "R2", "decision")  # no facts

    def test_stage_gate_checkpoint_carries_cli_facts(self) -> None:
        run = team.init_run(self.project, "Gate", "gate", "hitl", "plan-given", "adaptive")
        self.assertEqual(team.advance_stage(self.project, run), "waiting-human")
        gate = team.load_state(run)["checkpoints"][0]
        self.assertEqual(gate["kind"], "stage")
        self.assertIn("facts", gate)
        self.assertIn("tasks", gate["facts"])

    def test_R12_supervised_pauses_on_deviation_autonomous_records_it(self) -> None:
        supervised = self.run_("supervised")
        team.create_checkpoint(self.project, supervised, "Switch ORM?", "Keep", "R2", "deviation", details=DETAILS)
        self.assertEqual(team.load_state(supervised)["status"], "waiting-human")
        other = fresh_project()
        autonomous = team.init_run(other, "Auto", "auto", "autonomous", "execute-only", "adaptive")
        team.create_checkpoint(other, autonomous, "Switch ORM?", "Keep", "R2", "deviation", details=DETAILS)
        state = team.load_state(autonomous)
        self.assertEqual(state["status"], "active")
        self.assertEqual(state["checkpoints"][0]["status"], "recorded")

    def test_autonomous_architecture_gate_needs_an_independent_review(self) -> None:
        run = team.init_run(self.project, "Arch", "arch", "autonomous", "idea", "adaptive")
        (run / "BRIEF.md").write_text("# Brief\n\n- AC-1: users can sign in\n", encoding="utf-8")
        team.advance_stage(self.project, run)  # 00 -> 01
        team.advance_stage(self.project, run)  # 01 -> 02 (recorded assumptions)
        with self.assertRaises(team.TeamError) as raised:
            team.advance_stage(self.project, run)
        self.assertIn("independent-review", str(raised.exception))
        team.add_task(self.project, run, task_args("REVIEW", "code-reviewer", action="inspect", path=[]))
        team.claim_task(self.project, run, "REVIEW", "code-reviewer", 60)
        team.complete_task(self.project, run, "REVIEW", "code-reviewer", ["review notes"])
        self.assertEqual(team.advance_stage(self.project, run), "03_readiness")


class RiskModelTests(Base):
    def test_R20_benign_build_tasks_stay_below_external_risk(self) -> None:
        policy = team.load_policy(self.project)
        for title in BENIGN:
            with self.subTest(title=title):
                level, reasons = team.derive_risk(policy, "build", "local", title, title, [])
                self.assertLessEqual(team.RISK_ORDER[level], 2, reasons)

    def test_R20_operating_on_the_world_is_raised(self) -> None:
        policy = team.load_policy(self.project)
        for title in DANGEROUS:
            with self.subTest(title=title):
                level, _ = team.derive_risk(policy, "build", "local", title, title, [])
                self.assertGreaterEqual(team.RISK_ORDER[level], 3)
        self.assertEqual(team.derive_risk(policy, "deploy", "production", "Ship it", "", [])[0], "R3")
        self.assertEqual(team.derive_risk(policy, "data-destructive", "local", "clean", "", [])[0], "R4")

    def test_paths_raise_the_floor(self) -> None:
        policy = team.load_policy(self.project)
        self.assertEqual(team.derive_risk(policy, "build", "local", "ci", "", [".github/workflows/ci.yml"])[0], "R2")
        self.assertEqual(team.derive_risk(policy, "build", "local", "db", "", ["src/db/migrations"])[0], "R2")
        self.assertEqual(team.derive_risk(policy, "build", "local", "ui", "", ["src/ui"])[0], "R1")

    def test_command_rules(self) -> None:
        policy = team.load_policy(self.project)
        self.assertEqual(team.command_risk(policy, "git push --force origin main")[0], "R4")
        self.assertEqual(team.command_risk(policy, "npx vercel deploy --prod")[0], "R3")
        self.assertEqual(team.command_risk(policy, "python -m pytest -q")[0], "R0")

    def test_only_a_human_waiver_lowers_risk(self) -> None:
        run = self.run_()
        team.add_task(self.project, run, task_args("MIG", "database-engineer", action="migrate", target="local", path=["db"]))
        team.claim_task(self.project, run, "MIG", "database-engineer", 60)  # R2 is fine in autonomous
        other = fresh_project()
        hitl = team.init_run(other, "H", "h", "hitl", "execute-only", "adaptive")
        team.add_task(other, hitl, task_args("MIG", "database-engineer", action="migrate", target="local", path=["db"]))
        with self.assertRaises(team.GateError):
            team.claim_task(other, hitl, "MIG", "database-engineer", 60)
        with self.assertRaises(team.TeamError):
            team.waive_requirement(other, hitl, "risk:MIG", "local sqlite only", "database-engineer", self.token(hitl), "R1")
        team.waive_requirement(other, hitl, "risk:MIG", "local sqlite only", "Owner", self.token(hitl), "R1")
        state = team.load_state(hitl)
        self.assertEqual(state["checkpoints"][0]["status"], "superseded")
        self.assertEqual(state["status"], "active")
        team.claim_task(other, hitl, "MIG", "database-engineer", 60)
        self.assertEqual(team.load_state(hitl)["tasks"]["MIG"]["risk"], "R1")

    def test_hard_gates_hold_under_unattended(self) -> None:
        """G16: the executable release gate removes a click on the stage, never a gate on an action."""
        other = fresh_project()
        run = team.init_run(other, "U", "u", "unattended", "execute-only", "adaptive")
        for task_id, owner, action in (("SHIP", "devops-engineer", "deploy"), ("PUB", "release-manager", "publish"),
                                       ("PAY", "ceo", "spend"), ("WIPE", "database-engineer", "data-destructive")):
            team.add_task(other, run, task_args(task_id, owner, action=action, target="production", path=[task_id.lower()]))
            self.assertGreaterEqual(team.RISK_ORDER[team.load_state(run)["tasks"][task_id]["risk"]], 3, task_id)
            with self.assertRaises(team.GateError):
                team.claim_task(other, run, task_id, owner, 60)
        checkpoints = team.load_state(run)["checkpoints"]
        self.assertEqual(sorted(item["task"] for item in checkpoints if item["kind"] == "risk"), ["PAY", "PUB", "SHIP", "WIPE"])
        self.assertEqual(team.load_state(run)["status"], "waiting-human")


class TokenInputTests(Base):
    def test_R35_token_file_and_stdin_work_and_argv_warns(self) -> None:
        run = self.run_()
        checkpoint = self.gated_task(run)
        token_file = team.owner_token_file(team.load_state(run))
        project = str(self.project)
        code, _, err = run_cli(self.project, "approve", "--project", project, "--checkpoint", checkpoint,
                               "--by", "Owner", "--decision", "ok", "--token-file", str(token_file))
        self.assertEqual(code, 0, err)
        second = team.create_checkpoint(self.project, run, "Vendor?", "A", "R2", "decision", details=DETAILS)
        code, _, err = run_cli(self.project, "reject", "--project", project, "--checkpoint", second,
                               "--by", "Owner", "--decision", "no", "--token", self.token(run))
        self.assertEqual(code, 0, err)
        self.assertIn("shell history", err)
        code, _, err = run_cli(self.project, "resolve", "--project", project, "--checkpoint", second,
                               "--by", "Owner", "--resolution", "fixed", "--token-stdin", stdin=self.token(run) + "\n")
        self.assertEqual(code, 0, err)
        code, out, err = run_cli(self.project, "audit", "verify", "--project", project, "--by", "Owner",
                                 "--token-file", str(token_file))
        self.assertEqual(code, 0, err)
        self.assertIn("signed decision", out)


class MigrationTests(Base):
    def test_v2_run_migrates_and_keeps_its_decisions(self) -> None:
        run = self.run_()
        state = team.load_state(run)
        key = team.home_key(state)
        token = self.token(run)
        # Simulate a v2 run: no uid-keyed binding, no ledger, one approval in state.
        team.binding_path(key).unlink()
        state.pop("run_uid")
        state["version"] = "2.0.0"
        state["status"] = "blocked"
        state["checkpoints"].append({"id": "CP-001", "status": "approved", "kind": "decision", "stage": "04_build",
                                     "risk": "R2", "question": "q", "recommendation": "r", "created_at": team.utcnow()})
        team.write_json_atomic(run / "state.json", state)
        team.owner_token_path(state["run_id"]).write_text(token + "\n", encoding="utf-8")
        steps = team.migrate_run(self.project, run, "Owner", token)
        self.assertTrue(any("bound the owner key" in step for step in steps))
        migrated = team.load_state(run)
        self.assertEqual(migrated["version"], team.VERSION)
        self.assertEqual(team.audit_verify(self.project, run, token), [])


if __name__ == "__main__":
    unittest.main()
