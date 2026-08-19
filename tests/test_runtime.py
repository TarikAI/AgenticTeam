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

    def test_documented_role_counts_match_the_manifest(self) -> None:
        """A count written by hand drifts the moment the roster changes."""
        manifest = team.load_json(ROOT / "team.json")
        total = len(manifest["agents"])
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for claimed in re.findall(r"All (\d+) roles", readme):
            self.assertEqual(int(claimed), total, f"README claims {claimed} roles, manifest has {total}")
        for claimed in re.findall(r"\*\*(\d+) roles\*\*", readme):
            self.assertEqual(int(claimed), total, f"README claims {claimed} roles, manifest has {total}")
        departments = {}
        for agent in manifest["agents"]:
            departments[agent["department"]] = departments.get(agent["department"], 0) + 1
        specialists = departments.get("specialists", 0)
        for claimed in re.findall(r"\*\*(\d+) conditional specialists", readme):
            self.assertEqual(int(claimed), specialists)

    def test_agent_contract_covers_every_absolute_human_gate(self) -> None:
        """The floor agents actually read must not be shorter than the floor in policy."""
        policy = team.load_json(ROOT / "config" / "policies.json")
        contract = (ROOT / "protocols" / "agent-contract.md").read_text(encoding="utf-8").lower()
        keywords = {
            "production deployment": "production deployment",
            "public publishing or messaging real people": "publishing",
            "spending money or creating paid resources": "spending",
            "handling real credentials or payment methods": "credential",
            "destructive or irreversible data operations": "irreversible",
            "installing software with broad system access or modifying system settings": "broad system access",
            "legal or contractual commitments": "legal",
        }
        for gate in policy["absolute_human_gates"]:
            needle = keywords.get(gate)
            self.assertIsNotNone(needle, f"policy gate '{gate}' has no contract keyword mapping")
            self.assertIn(needle, contract, f"agent-contract.md does not cover the '{gate}' gate")

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
            "antigravity": ".agents/agents/ceo.md",
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
                # Skill dir is asserted as a literal per harness, not read back out of
                # team.json - reading the manifest would make this assertion a tautology.
                skill_dirs = {
                    "claude-code": ".claude/skills",
                    "codex": ".agents/skills",
                    "opencode": ".agents/skills",
                    "antigravity": ".agents/skills",
                    "gemini-cli": ".agents/skills",
                    "pi": ".pi/skills",
                    "generic": ".agents/skills",
                }
                self.assertTrue((target / skill_dirs[harness] / "agentic-build" / "SKILL.md").is_file())
                # Every harness must end up with at least one root instruction file.
                self.assertTrue(
                    any((target / name).is_file() for name in ("AGENTS.md", "CLAUDE.md", "GEMINI.md")),
                    f"{harness} wrote no root instruction file",
                )
                for router in (target / "AGENTS.md", target / "CLAUDE.md", target / "GEMINI.md"):
                    if router.exists():
                        self.assertLess(router.stat().st_size, 32 * 1024)

    def test_harness_native_conventions_hold(self) -> None:
        """Each harness only loads files that match its own conventions.

        These assertions are literals on purpose: a compiler that writes to the wrong
        directory or omits required frontmatter installs cleanly and then does nothing.
        """
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            team.install_team(ROOT, target, "antigravity", "platform-core", [], [])
            agent = (target / ".agents" / "agents" / "ceo.md").read_text(encoding="utf-8")
            self.assertTrue(agent.startswith("---"), "antigravity agent needs YAML frontmatter")
            self.assertIn("name: ceo", agent)
            self.assertIn("description:", agent)
            rule = (target / ".agents" / "rules" / "agentic-team.md").read_text(encoding="utf-8")
            self.assertIn("trigger:", rule, "an antigravity rule without a trigger may never load")
            self.assertLessEqual(len(rule), 12000, "antigravity rules are capped at 12000 characters")
            for workflow in (target / ".agents" / "workflows").glob("*.md"):
                body = workflow.read_text(encoding="utf-8")
                self.assertIn("description:", body, f"{workflow.name} would not register as a command")
                self.assertLessEqual(len(body), 12000)
            self.assertFalse((target / ".agents" / "roles").exists(), "stale role directory")

        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            team.install_team(ROOT, target, "opencode", "platform-core", [], [])
            body = (target / ".opencode" / "agents" / "code-reviewer.md").read_text(encoding="utf-8")
            self.assertIn("mode:", body, "opencode needs a mode to know this is a subagent")
            self.assertIn("edit: deny", body, "read-only role lost its opencode sandbox")

    def test_read_only_roles_state_their_constraint_in_the_prompt(self) -> None:
        """Not every harness can express a tool allowlist, so the constraint travels in text."""
        for harness, relative in (
            ("gemini-cli", ".gemini/agents/code-reviewer.md"),
            ("antigravity", ".agents/agents/code-reviewer.md"),
            ("generic", ".agentic-team/agents/code-reviewer.md"),
        ):
            with self.subTest(harness=harness), tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary)
                team.install_team(ROOT, target, harness, "platform-core", [], [])
                self.assertIn("ACCESS CONSTRAINT", (target / relative).read_text(encoding="utf-8"))

    def test_compiled_protocol_references_resolve_in_the_target(self) -> None:
        """A compiled agent must not point at a protocol path that does not exist."""
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            team.install_team(ROOT, target, "claude-code", "platform-core", [], [])
            referenced = set()
            for definition in (target / ".claude" / "agents").glob("*.md"):
                body = definition.read_text(encoding="utf-8")
                referenced.update(re.findall(r"\.agentic-team/protocols/[a-z0-9-]+\.md", body))
                self.assertNotRegex(
                    body,
                    r"(?<![\w./-])protocols/[a-z0-9-]+\.md",
                    f"{definition.name} has an unresolved protocol path",
                )
            self.assertTrue(referenced, "expected compiled agents to reference protocols")
            for reference in sorted(referenced):
                self.assertTrue((target / reference).is_file(), f"dangling protocol reference: {reference}")

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
    def owner_token(run_dir: Path) -> str:
        """The token a real human would hold; it lives outside the project by design."""
        return team.owner_token_path(run_dir.name).read_text(encoding="utf-8").strip()

    @staticmethod
    def task_args(task_id: str, owner: str, depends: list[str] | None = None, risk: str = "R1", path: list[str] | None = None, title: str | None = None) -> argparse.Namespace:
        return argparse.Namespace(
            id=task_id,
            title=title or f"Task {task_id}",
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
        team.approve_checkpoint(
            self.project, run, checkpoint["id"], "human-owner", "Approved staged action", self.owner_token(run)
        )
        team.claim_task(self.project, run, "DEPLOY", "devops-engineer", 60)
        self.assertEqual(team.load_state(run)["tasks"]["DEPLOY"]["status"], "claimed")

    def test_hitl_stage_gate_waits_and_resumes(self) -> None:
        run = self.new_run("hitl", "plan-given")
        self.assertEqual(team.load_state(run)["stage"], "03_readiness")
        self.assertEqual(team.advance_stage(self.project, run), "waiting-human")
        state = team.load_state(run)
        team.approve_checkpoint(
            self.project, run, state["checkpoints"][0]["id"], "human-owner", "Ready", self.owner_token(run)
        )
        self.assertEqual(team.advance_stage(self.project, run), "04_build")

    def test_human_can_reject_checkpoint_and_block_run(self) -> None:
        run = self.new_run("supervised")
        checkpoint = team.create_checkpoint(self.project, run, "Accept migration?", "Use reversible migration", "R2", "decision")
        team.reject_checkpoint(
            self.project, run, checkpoint, "human-owner", "Revise rollback plan", self.owner_token(run)
        )
        state = team.load_state(run)
        self.assertEqual(state["status"], "blocked")
        self.assertEqual(state["checkpoints"][0]["status"], "rejected")

    def test_agent_cannot_approve_the_gate_that_blocks_it(self) -> None:
        run = self.new_run("autonomous")
        team.add_task(self.project, run, self.task_args("DEPLOY", "devops-engineer", risk="R3"))
        with self.assertRaises(team.TeamError):
            team.claim_task(self.project, run, "DEPLOY", "devops-engineer", 60)
        checkpoint = team.load_state(run)["checkpoints"][0]["id"]
        token = self.owner_token(run)
        # named as the agent: refused even holding the token
        with self.assertRaises(team.TeamError):
            team.approve_checkpoint(self.project, run, checkpoint, "devops-engineer", "self", token)
        # posing as a human without the token: refused
        with self.assertRaises(team.TeamError):
            team.approve_checkpoint(self.project, run, checkpoint, "human-owner", "self", None)
        # wrong token: refused
        with self.assertRaises(team.TeamError):
            team.approve_checkpoint(self.project, run, checkpoint, "human-owner", "self", "not-the-token")
        self.assertEqual(team.load_state(run)["checkpoints"][0]["status"], "pending")

    def test_declared_risk_cannot_hide_an_external_action(self) -> None:
        run = self.new_run("autonomous")
        team.add_task(self.project, run, self.task_args("SHIP", "devops-engineer", risk="R1", title="deploy to production"))
        task = team.load_state(run)["tasks"]["SHIP"]
        self.assertEqual(task["declared_risk"], "R1")
        self.assertEqual(task["risk"], "R3", "a deploy labelled R1 must still be gated")
        with self.assertRaises(team.TeamError):
            team.claim_task(self.project, run, "SHIP", "devops-engineer", 60)

    def test_rejected_run_blocks_further_claims(self) -> None:
        run = self.new_run("supervised")
        team.add_task(self.project, run, self.task_args("WORK", "fullstack-engineer", risk="R1"))
        checkpoint = team.create_checkpoint(self.project, run, "Proceed?", "Hold", "R2", "decision")
        team.reject_checkpoint(self.project, run, checkpoint, "human-owner", "Stop", self.owner_token(run))
        self.assertEqual(team.load_state(run)["status"], "blocked")
        with self.assertRaises(team.TeamError):
            team.claim_task(self.project, run, "WORK", "fullstack-engineer", 60)

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
