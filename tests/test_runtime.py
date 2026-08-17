from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("agentic_team", ROOT / "scripts" / "agentic_team.py")
assert SPEC and SPEC.loader
team = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(team)


class SourceValidationTests(unittest.TestCase):
    def test_manifest_and_source_are_consistent(self) -> None:
        self.assertEqual(team.validate_source(ROOT), [])
        manifest = team.load_json(ROOT / "team.json")
        self.assertEqual(len(manifest["agents"]), 50)
        self.assertEqual(sum(agent["department"] == "specialists" for agent in manifest["agents"]), 18)
        self.assertEqual(len({agent["id"] for agent in manifest["agents"]}), 50)

    def test_skills_are_complete_and_invocable(self) -> None:
        for skill_dir in (ROOT / "skills").iterdir():
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            fields, body = team.parse_frontmatter(skill_file.read_text(encoding="utf-8"))
            self.assertEqual(fields["name"], skill_dir.name)
            self.assertGreater(len(fields["description"]), 80)
            self.assertNotIn("TODO", body)
            interface = (skill_dir / "agents" / "openai.yaml").read_text(encoding="utf-8")
            self.assertIn(f"${skill_dir.name}", interface)

    def test_documentation_local_links_resolve(self) -> None:
        checked = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
        for document in checked:
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "#")):
                    continue
                path = target.split("#", 1)[0]
                self.assertTrue((document.parent / path).resolve().exists(), f"Broken link in {document}: {target}")


class AdapterTests(unittest.TestCase):
    def test_every_harness_compiles_native_package(self) -> None:
        expected = {
            "claude-code": ".claude/agents/ceo.md",
            "codex": ".codex/agents/ceo.toml",
            "opencode": ".opencode/agents/ceo.md",
            "antigravity": ".agents/roles/ceo.md",
            "gemini-cli": ".gemini/agents/ceo.md",
            "pi": ".pi/prompts/agentic-build.md",
            "generic": ".agentic-team/agents/ceo.md",
        }
        for harness, relative in expected.items():
            with self.subTest(harness=harness), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary)
                record = team.install_team(ROOT, target, harness, "platform-core", [], [])
                self.assertEqual(len(record["agents"]), 11)
                self.assertTrue((target / relative).is_file())
                self.assertTrue((target / ".agentic-team" / "bin" / "agentic_team.py").is_file())
                self.assertTrue((target / ".agentic-team" / "protocols" / "fusion.md").is_file())
                self.assertTrue((target / team.load_json(ROOT / "team.json")["harnesses"][harness]["skill_dir"] / "agentic-build" / "SKILL.md").is_file())
                for router in (target / "AGENTS.md", target / "CLAUDE.md", target / "GEMINI.md"):
                    if router.exists():
                        self.assertLess(router.stat().st_size, 32 * 1024)

    def test_codex_toml_is_valid_and_read_only_is_constrained(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            team.install_team(ROOT, target, "codex", "audit", [], [])
            definition = tomllib.loads((target / ".codex" / "agents" / "security-engineer.toml").read_text(encoding="utf-8"))
            self.assertEqual(definition["name"], "security-engineer")
            self.assertEqual(definition["sandbox_mode"], "read-only")

    def test_full_company_codex_package_parses_all_roles(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            record = team.install_team(ROOT, target, "codex", "full-company", [], [])
            files = list((target / ".codex" / "agents").glob("*.toml"))
            self.assertEqual(len(record["agents"]), 50)
            self.assertEqual(len(files), 50)
            parsed_names = {tomllib.loads(path.read_text(encoding="utf-8"))["name"] for path in files}
            self.assertEqual(parsed_names, set(record["agents"]))
            self.assertLess((target / "AGENTS.md").stat().st_size, 32 * 1024)

    def test_custom_selection_installs_only_requested_agents(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            record = team.install_team(ROOT, target, "generic", "full-company", [], ["ceo", "fusion-moderator"])
            self.assertEqual(record["agents"], ["ceo", "fusion-moderator"])
            self.assertEqual(len(list((target / ".agentic-team" / "agents").glob("*.md"))), 2)

    def test_installed_cli_is_self_contained(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            team.install_team(ROOT, target, "generic", "platform-core", [], [])
            cli = target / ".agentic-team" / "bin" / "agentic_team.py"
            version = subprocess.run([sys.executable, str(cli), "--version"], check=True, capture_output=True, text=True)
            self.assertIn(team.VERSION, version.stdout)
            created = subprocess.run(
                [sys.executable, str(cli), "init-run", "--project", str(target), "--name", "Installed runtime", "--run-id", "portable"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("portable", created.stdout)
            self.assertTrue((target / ".agentic-team" / "runs" / "portable" / "state.json").is_file())

    def test_reinstall_prunes_managed_roles_and_preserves_user_router_text(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            (target / "AGENTS.md").write_text("# User instructions\n\nKeep this.\n", encoding="utf-8")
            team.install_team(ROOT, target, "codex", "platform-core", [], [])
            self.assertTrue((target / ".codex" / "agents" / "fullstack-engineer.toml").is_file())
            team.install_team(ROOT, target, "codex", "full-company", [], ["ceo"])
            self.assertFalse((target / ".codex" / "agents" / "fullstack-engineer.toml").exists())
            router = (target / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("Keep this.", router)
            self.assertEqual(router.count(team.MANAGED_START), 1)


class RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.project = Path(self.temporary.name)
        team.install_team(ROOT, self.project, "generic", "full-company", [], [])

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def new_run(self, autonomy: str = "autonomous", entry: str = "idea") -> Path:
        return team.init_run(self.project, "Test project", "test-run", autonomy, entry, "bmad-progressive")

    @staticmethod
    def task_args(task_id: str, owner: str, depends: list[str] | None = None, risk: str = "R1", path: list[str] | None = None) -> argparse.Namespace:
        return argparse.Namespace(
            id=task_id,
            title=f"Task {task_id}",
            objective=f"Deliver {task_id}",
            owner=owner,
            stage="04_build",
            risk=risk,
            depends_on=depends or [],
            path=path or [f"src/{task_id.lower()}"],
            input=["authoritative plan"],
            acceptance=["checks pass"],
            evidence_contract=["test output"],
        )

    def test_task_graph_claim_completion_and_dependency_refresh(self) -> None:
        run = self.new_run()
        team.add_task(self.project, run, self.task_args("T1", "backend-engineer"))
        team.add_task(self.project, run, self.task_args("T2", "frontend-engineer", ["T1"]))
        state = team.load_state(run)
        self.assertEqual(state["tasks"]["T1"]["status"], "ready")
        self.assertEqual(state["tasks"]["T2"]["status"], "pending")
        team.claim_task(self.project, run, "T1", "backend-engineer", 60)
        team.complete_task(self.project, run, "T1", "backend-engineer", ["12 tests passed"])
        self.assertEqual(team.load_state(run)["tasks"]["T2"]["status"], "ready")

    def test_specialist_routing_activates_only_matching_installed_roles(self) -> None:
        run = self.new_run()
        matches = team.route_specialists(self.project, run, ["large-project bmad", "pii", "rtl multilingual"])
        activated = {item["agent"] for item in matches}
        self.assertTrue({"context-engineer", "privacy-engineer", "localization-specialist"}.issubset(activated))
        state = team.load_state(run)
        self.assertEqual(state["active_specialists"]["context-engineer"]["status"], "active")
        team.deactivate_specialist(self.project, run, "context-engineer", "Context contracts created")
        self.assertEqual(team.load_state(run)["active_specialists"]["context-engineer"]["status"], "complete")

    def test_claim_rejects_overlapping_active_paths(self) -> None:
        run = self.new_run()
        team.add_task(self.project, run, self.task_args("T1", "backend-engineer", path=["src/api"]))
        team.add_task(self.project, run, self.task_args("T2", "frontend-engineer", path=["src/api/routes.py"]))
        team.claim_task(self.project, run, "T1", "backend-engineer", 60)
        with self.assertRaises(team.TeamError):
            team.claim_task(self.project, run, "T2", "frontend-engineer", 60)

    def test_concurrent_overlapping_claims_have_exactly_one_winner(self) -> None:
        run = self.new_run()
        team.add_task(self.project, run, self.task_args("T1", "backend-engineer", path=["src/shared"]))
        team.add_task(self.project, run, self.task_args("T2", "frontend-engineer", path=["src/shared/view.ts"]))

        def attempt(task_id: str, agent: str) -> str:
            try:
                team.claim_task(self.project, run, task_id, agent, 60)
                return "claimed"
            except team.TeamError:
                return "rejected"

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda pair: attempt(*pair), [("T1", "backend-engineer"), ("T2", "frontend-engineer")]))
        self.assertEqual(sorted(results), ["claimed", "rejected"])

    def test_expired_lease_is_recovered_with_retry_evidence(self) -> None:
        run = self.new_run()
        team.add_task(self.project, run, self.task_args("T1", "backend-engineer"))
        team.claim_task(self.project, run, "T1", "backend-engineer", 60)
        state = team.load_state(run)
        state["tasks"]["T1"]["lease_expires"] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=1)).isoformat().replace("+00:00", "Z")
        team.write_json_atomic(run / "state.json", state)
        self.assertEqual(team.recover_leases(self.project, run), 1)
        recovered = team.load_state(run)["tasks"]["T1"]
        self.assertEqual(recovered["status"], "ready")
        self.assertEqual(recovered["last_failure"]["reason"], "claim lease expired")

    def test_high_risk_task_requires_human_approval_even_autonomous(self) -> None:
        run = self.new_run("autonomous")
        team.add_task(self.project, run, self.task_args("DEPLOY", "devops-engineer", risk="R3"))
        with self.assertRaises(team.TeamError):
            team.claim_task(self.project, run, "DEPLOY", "devops-engineer", 60)
        state = team.load_state(run)
        checkpoint = state["checkpoints"][0]
        self.assertEqual(state["status"], "waiting-human")
        team.approve_checkpoint(self.project, run, checkpoint["id"], "human-owner", "Approved staged action")
        team.claim_task(self.project, run, "DEPLOY", "devops-engineer", 60)
        self.assertEqual(team.load_state(run)["tasks"]["DEPLOY"]["status"], "claimed")

    def test_hitl_stage_gate_waits_and_resumes(self) -> None:
        run = self.new_run("hitl", "plan-given")
        self.assertEqual(team.load_state(run)["stage"], "03_readiness")
        self.assertEqual(team.advance_stage(self.project, run), "waiting-human")
        state = team.load_state(run)
        team.approve_checkpoint(self.project, run, state["checkpoints"][0]["id"], "human-owner", "Ready")
        self.assertEqual(team.advance_stage(self.project, run), "04_build")

    def test_human_can_reject_checkpoint_and_block_run(self) -> None:
        run = self.new_run("supervised")
        checkpoint = team.create_checkpoint(self.project, run, "Accept migration?", "Use reversible migration", "R2", "decision")
        team.reject_checkpoint(self.project, run, checkpoint, "human-owner", "Revise rollback plan")
        state = team.load_state(run)
        self.assertEqual(state["status"], "blocked")
        self.assertEqual(state["checkpoints"][0]["status"], "rejected")

    def test_fusion_enforces_independence_and_full_sequence(self) -> None:
        run = self.new_run()
        args = argparse.Namespace(
            id="product-plan",
            question="What should we build?",
            sponsor="human-owner",
            moderator="fusion-moderator",
            verifier="qa-lead",
            contributor=["product-manager", "cto-architect"],
        )
        team.fusion_init(self.project, run, args)
        self.assertEqual(team.fusion_submit(self.project, run, "product-plan", "proposal", "product-manager", "proposal path"), "proposals")
        self.assertEqual(team.fusion_submit(self.project, run, "product-plan", "proposal", "cto-architect", "proposal path"), "critiques")
        team.fusion_submit(self.project, run, "product-plan", "critique", "product-manager", "critique path")
        self.assertEqual(team.fusion_submit(self.project, run, "product-plan", "critique", "cto-architect", "critique path"), "synthesis")
        self.assertEqual(team.fusion_submit(self.project, run, "product-plan", "synthesis", "fusion-moderator", "synthesis path"), "verification")
        self.assertEqual(team.fusion_submit(self.project, run, "product-plan", "verification", "qa-lead", "verified"), "decision")
        team.fusion_close(self.project, run, "product-plan", "human-owner", "Choose coherent plan A")
        self.assertEqual(team.load_state(run)["fusion_sessions"][0]["status"], "complete")
        self.assertTrue((run / "_fusion" / "product-plan" / "dissent.md").is_file())

    def test_learning_and_report_are_evidence_derived(self) -> None:
        run = self.new_run()
        lesson = team.learn(self.project, run, "Contract drift", "Integration failed at API boundary", "Freeze schema first", "parallel APIs", "single-file prototype")
        report = team.generate_report(self.project, run)
        self.assertTrue(lesson.is_file())
        self.assertIn("Candidate only", lesson.read_text(encoding="utf-8"))
        self.assertTrue(report.is_file())


if __name__ == "__main__":
    unittest.main()
