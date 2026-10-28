"""P5: harness compilers — access classes, model profiles, settings/hook merge, guard, new targets.

Assertions are literal paths and values on purpose (plan §2 invariant 7).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from helpers import ROOT, fresh_project, run_cli, team
from test_regressions import task_args

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    tomllib = None


def frontmatter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text.split("---", 2)[1]


def guard(payload: dict, scope: str | None = None, agent: str | None = None) -> str | None:
    return team.guard_decision(payload, scope, agent)


class ClaudeCodeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = fresh_project("full-company", "claude-code")

    def test_access_classes_compile_to_tool_sets(self) -> None:
        agents = self.project / ".claude" / "agents"
        self.assertIn("tools: Read, Grep, Glob\n", frontmatter(agents / "compliance-advisor.md"))
        self.assertIn("tools: Read, Grep, Glob, WebSearch, WebFetch\n", frontmatter(agents / "research-agent.md"))
        review = frontmatter(agents / "qa-lead.md")
        self.assertIn("tools: Read, Grep, Glob, Bash, Write, Edit, WebSearch, WebFetch\n", review)
        self.assertIn("--scope review --agent qa-lead", review)
        self.assertIn("skills:\n  - agentic-verify", review)
        self.assertIn("tools: Agent, Read, Write", frontmatter(agents / "ceo.md"))

    def test_balanced_profile_maps_tiers(self) -> None:
        agents = self.project / ".claude" / "agents"
        self.assertIn("model: inherit\neffort: high", frontmatter(agents / "security-engineer.md"))  # deep
        self.assertIn("model: sonnet", frontmatter(agents / "backend-engineer.md"))  # standard
        self.assertIn("model: haiku", frontmatter(agents / "content-marketer.md"))  # fast
        self.assertIn("color: pink", frontmatter(agents / "content-marketer.md"))

    def test_inherit_profile_reproduces_v2_models(self) -> None:
        target = Path(tempfile.mkdtemp())
        team.install_team(ROOT, target, "claude-code", "platform-core", [], [], "inherit")
        self.assertIn("model: inherit\ncolor", frontmatter(target / ".claude" / "agents" / "fullstack-engineer.md"))
        shutil.rmtree(target, ignore_errors=True)

    def test_router_is_imported_not_described(self) -> None:
        self.assertIn("\n@.agentic-team/AGENTS.md\n", (self.project / "CLAUDE.md").read_text(encoding="utf-8"))

    def test_settings_carry_deny_rules_and_guard_hook(self) -> None:
        settings = json.loads((self.project / ".claude" / "settings.json").read_text(encoding="utf-8"))
        self.assertIn("Read(~/.agentic-team/**)", settings["permissions"]["deny"])
        self.assertIn("Edit(/.agentic-team/runs/**/state.json)", settings["permissions"]["deny"])
        command = settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        self.assertIn("guard --harness claude-code", command)
        self.assertEqual(team.doctor(self.project), [])

    def test_settings_merge_keeps_user_entries_and_uninstall_removes_only_ours(self) -> None:
        target = Path(tempfile.mkdtemp())
        settings_path = target / ".claude" / "settings.json"
        settings_path.parent.mkdir(parents=True)
        settings_path.write_text(json.dumps({"model": "opus", "permissions": {"deny": ["Read(./.env)"]},
                                             "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "mine.sh"}]}]}}),
                                 encoding="utf-8")
        team.install_team(ROOT, target, "claude-code", "platform-core", [], [])
        team.install_team(ROOT, target, "claude-code", "platform-core", [], [])  # reinstall: no duplicates
        merged = json.loads(settings_path.read_text(encoding="utf-8"))
        self.assertEqual(merged["model"], "opus")
        self.assertEqual(merged["permissions"]["deny"].count("Read(~/.agentic-team/**)"), 1)
        self.assertIn("Read(./.env)", merged["permissions"]["deny"])
        commands = [hook["command"] for group in merged["hooks"]["PreToolUse"] for hook in group["hooks"]]
        self.assertEqual(sum("guard --harness" in command for command in commands), 1)
        self.assertIn("mine.sh", commands)
        team.uninstall_team(target)
        left = json.loads(settings_path.read_text(encoding="utf-8"))
        self.assertEqual(left["permissions"]["deny"], ["Read(./.env)"])
        self.assertEqual([hook["command"] for group in left["hooks"]["PreToolUse"] for hook in group["hooks"]], ["mine.sh"])
        self.assertFalse((target / ".claude" / "agents").exists())
        shutil.rmtree(target, ignore_errors=True)

    def test_invalid_user_settings_are_refused_not_rewritten(self) -> None:
        target = Path(tempfile.mkdtemp())
        settings_path = target / ".claude" / "settings.json"
        settings_path.parent.mkdir(parents=True)
        settings_path.write_text("{not json", encoding="utf-8")
        with self.assertRaises(team.TeamError):
            team.install_team(ROOT, target, "claude-code", "platform-core", [], [])
        self.assertEqual(settings_path.read_text(encoding="utf-8"), "{not json")
        shutil.rmtree(target, ignore_errors=True)

    def test_locally_modified_generated_files_need_force(self) -> None:
        target = Path(tempfile.mkdtemp())
        team.install_team(ROOT, target, "claude-code", "platform-core", [], [])
        agent = target / ".claude" / "agents" / "ceo.md"
        agent.write_text(agent.read_text(encoding="utf-8") + "\nMy local tweak.\n", encoding="utf-8")
        with self.assertRaises(team.TeamError) as raised:
            team.install_team(ROOT, target, "claude-code", "platform-core", [], [])
        self.assertIn(".claude", str(raised.exception))
        team.install_team(ROOT, target, "claude-code", "platform-core", [], [], force=True)
        backups = list((target / ".agentic-team" / "backup").rglob("ceo.md"))
        self.assertTrue(backups and "My local tweak." in backups[0].read_text(encoding="utf-8"))
        shutil.rmtree(target, ignore_errors=True)


class GuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project = fresh_project("full-company", "claude-code")
        self.run = team.init_run(self.project, "Guard", "guard", "autonomous", "execute-only", "adaptive")

    def payload(self, tool: str, **tool_input) -> dict:
        return {"tool_name": tool, "tool_input": tool_input, "cwd": str(self.project)}

    def test_owner_home_is_off_limits(self) -> None:
        self.assertIsNotNone(guard(self.payload("Read", file_path="~/.agentic-team/owner-tokens/x.token")))
        self.assertIsNotNone(guard(self.payload("Bash", command="cat $HOME/.agentic-team/ledger/x.jsonl")))
        self.assertIsNotNone(guard(self.payload("Bash", command=f"type {team.agentic_home()}\\runs\\x.json")))
        self.assertIsNone(guard(self.payload("Read", file_path=".agentic-team/CURRENT.md")))
        self.assertIsNone(guard(self.payload("Bash", command="python .agentic-team/bin/agentic_team.py status")))

    def test_supervisor_paths_and_commands_are_owner_only(self) -> None:
        self.assertIsNotNone(guard(self.payload("Write", file_path=".agentic-team/supervisor/inbox/x.json", content="{}")))
        self.assertIsNotNone(guard(self.payload("Bash", command="echo {} > .agentic-team/supervisor/inbox/x.json")))
        self.assertIsNotNone(guard(self.payload("Bash", command="python .agentic-team/bin/agentic_team.py supervise enqueue --title t")))
        self.assertIsNotNone(guard(self.payload("Bash", command="python .agentic-team/bin/agentic_team.py export-view --to v")))
        self.assertIsNone(guard(self.payload("Read", file_path=".agentic-team/supervisor/STATUS.md")), "the digest is readable")
        store = Path(tempfile.mkdtemp(prefix="owner-store-"))
        view = Path(tempfile.mkdtemp(prefix="view-"))
        with mock.patch.dict(os.environ, {"AGENTIC_TEAM_PROTECT": str(store), "AGENTIC_TEAM_VIEW": str(view)}):
            self.assertIsNotNone(guard(self.payload("Read", file_path=str(store / "control.json"))))
            self.assertIsNotNone(guard(self.payload("Bash", command=f"type {store}\\jobs\\x.json")))
            self.assertIsNotNone(guard(self.payload("Edit", file_path=str(view / "ledger" / "x.jsonl"), old_string="a", new_string="b")))
        shutil.rmtree(store, ignore_errors=True)
        shutil.rmtree(view, ignore_errors=True)
        self.assertIn("Edit(/.agentic-team/supervisor/**)", team.CLAUDE_DENY_RULES)

    def test_run_state_is_cli_only(self) -> None:
        self.assertIsNotNone(guard(self.payload("Write", file_path=".agentic-team/runs/guard/state.json", content="{}")))
        self.assertIsNotNone(guard(self.payload("Bash", command="echo {} > .agentic-team/runs/guard/state.json")))
        self.assertIsNone(guard(self.payload("Write", file_path=".agentic-team/runs/guard/VERIFICATION.md", content="x")))

    def test_external_commands_need_an_approved_task(self) -> None:
        denied = guard(self.payload("Bash", command="npx vercel deploy --prod"))
        self.assertIn("R3", denied)
        self.assertIsNone(guard(self.payload("Bash", command="python -m pytest -q")))
        team.add_task(self.project, self.run, task_args("SHIP", "devops-engineer", action="deploy", target="production", path=["deploy"]))
        with self.assertRaises(team.GateError):
            team.claim_task(self.project, self.run, "SHIP", "devops-engineer", 60)
        token = team.owner_token_file(team.load_state(self.run)).read_text(encoding="utf-8").strip()
        checkpoint = team.load_state(self.run)["checkpoints"][0]["id"]
        team.approve_checkpoint(self.project, self.run, checkpoint, "Owner", "ship", token)
        team.claim_task(self.project, self.run, "SHIP", "devops-engineer", 60)
        self.assertIsNone(guard(self.payload("Bash", command="npx vercel deploy --prod")))
        self.assertIsNotNone(guard(self.payload("Bash", command="git push --force origin main")), "R4 needs its own task")

    def test_review_scope_limits_writes(self) -> None:
        self.assertIsNotNone(guard(self.payload("Edit", file_path="src/app.py", old_string="a", new_string="b"), "review", "qa-lead"))
        self.assertIsNone(guard(self.payload("Write", file_path=".agentic-team/runs/guard/VERIFICATION.md", content="x"), "review", "qa-lead"))
        self.assertIsNone(guard(self.payload("Edit", file_path=".agentic-team/knowledge/playbooks/qa-lead.md", old_string="a", new_string="b"), "review", "qa-lead"))
        self.assertIsNotNone(guard(self.payload("Edit", file_path=".agentic-team/knowledge/playbooks/ceo.md", old_string="a", new_string="b"), "review", "qa-lead"))

    def test_fusion_proposals_stay_private_until_reveal(self) -> None:
        import argparse

        team.fusion_init(self.project, self.run, argparse.Namespace(
            id="f1", question="q", sponsor="human-owner", moderator="fusion-moderator", verifier="qa-lead",
            contributor=["product-manager", "cto-architect"]))
        peek = {**self.payload("Read", file_path=".agentic-team/runs/guard/_fusion/f1/proposals/cto-architect.md"), "agent_type": "product-manager"}
        self.assertIsNotNone(guard(peek))
        own = {**self.payload("Read", file_path=".agentic-team/runs/guard/_fusion/f1/proposals/product-manager.md"), "agent_type": "product-manager"}
        self.assertIsNone(guard(own))

    def test_guard_cli_emits_the_documented_deny_json(self) -> None:
        payload = json.dumps(self.payload("Read", file_path="~/.agentic-team/owner-tokens/x.token"))
        code, out, _ = run_cli(self.project, "guard", "--harness", "claude-code", stdin=payload)
        self.assertEqual(code, 0)
        decision = json.loads(out.splitlines()[0])["hookSpecificOutput"]
        self.assertEqual((decision["hookEventName"], decision["permissionDecision"]), ("PreToolUse", "deny"))
        code, out, _ = run_cli(self.project, "guard", "--harness", "claude-code", stdin=json.dumps(self.payload("Read", file_path="README.md")))
        self.assertEqual((code, out.strip()), (0, ""))


class OtherHarnessTests(unittest.TestCase):
    @unittest.skipIf(tomllib is None, "tomllib requires Python 3.11+")
    def test_codex_sandbox_effort_and_hooks(self) -> None:
        project = fresh_project("full-company", "codex")
        agents = project / ".codex" / "agents"
        self.assertEqual(tomllib.loads((agents / "compliance-advisor.toml").read_text(encoding="utf-8"))["sandbox_mode"], "read-only")
        qa = tomllib.loads((agents / "qa-lead.toml").read_text(encoding="utf-8"))
        self.assertEqual((qa["sandbox_mode"], qa["model_reasoning_effort"]), ("workspace-write", "high"))
        hooks = json.loads((project / ".codex" / "hooks.json").read_text(encoding="utf-8"))
        self.assertIn("guard --harness codex", hooks["hooks"]["PreToolUse"][0]["hooks"][0]["command"])

    def test_opencode_has_no_blanket_ask(self) -> None:
        project = fresh_project("full-company", "opencode")
        agents = project / ".opencode" / "agents"
        builder = frontmatter(agents / "backend-engineer.md")
        self.assertIn('    "*": allow\n', builder)
        self.assertIn('    "npm publish*": ask\n', builder)
        self.assertIn('    "git push --force*": deny\n', builder)
        self.assertNotIn("bash: ask", builder)
        self.assertIn('    "*": deny\n', frontmatter(agents / "research-agent.md"))
        self.assertIn("webfetch: allow", frontmatter(agents / "research-agent.md"))
        self.assertIn("task: allow", frontmatter(agents / "delivery-lead.md"))

    def test_gemini_frontmatter_uses_only_allowed_keys(self) -> None:
        project = fresh_project("full-company", "gemini-cli")
        for path in (project / ".gemini" / "agents").glob("*.md"):
            keys = {line.split(":", 1)[0] for line in frontmatter(path).strip().splitlines() if line and not line.startswith(" ")}
            self.assertLessEqual(keys, team.GEMINI_ALLOWED_KEYS, path.name)
        self.assertIn("  - google_web_search", frontmatter(project / ".gemini" / "agents" / "research-agent.md"))

    def test_pi_prompts_have_descriptions(self) -> None:
        project = fresh_project("platform-core", "pi")
        self.assertTrue((project / ".pi" / "prompts" / "agentic-build.md").read_text(encoding="utf-8").startswith("---\ndescription:"))

    def test_new_targets_write_their_native_files(self) -> None:
        expected = {
            "copilot": (".github/agents/qa-lead.agent.md", ".agents/skills"),
            "cursor": (".cursor/agents/qa-lead.md", ".agents/skills"),
            "factory": (".factory/droids/qa-lead.md", ".agents/skills"),
            "kiro": (".kiro/agents/qa-lead.json", ".kiro/skills"),
            "qwen-code": (".qwen/agents/qa-lead.md", ".qwen/skills"),
            "junie": (".junie/agents/qa-lead.md", ".junie/skills"),
        }
        for harness, (agent_file, skill_dir) in expected.items():
            with self.subTest(harness=harness):
                project = fresh_project("platform-core", harness)
                self.assertTrue((project / agent_file).is_file())
                self.assertTrue((project / skill_dir / "agentic-build" / "SKILL.md").is_file())
                self.assertIn(team.MANAGED_START, (project / "AGENTS.md").read_text(encoding="utf-8"))
        kiro = json.loads((fresh_project("platform-core", "kiro") / ".kiro" / "agents" / "qa-lead.json").read_text(encoding="utf-8"))
        self.assertEqual(kiro["prompt"], "file://./prompts/qa-lead.md")
        cursor = fresh_project("full-company", "cursor")
        self.assertIn("readonly: true", frontmatter(cursor / ".cursor" / "agents" / "research-agent.md"))
        copilot = fresh_project("full-company", "copilot")
        self.assertIn('tools: ["read", "search"]', frontmatter(copilot / ".github" / "agents" / "compliance-advisor.agent.md"))

    def test_installers_accept_every_harness(self) -> None:
        manifest = team.load_json(ROOT / "team.json")
        ps1 = (ROOT / "scripts" / "install.ps1").read_text(encoding="utf-8")
        ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        for harness in manifest["harnesses"]:
            self.assertIn(f"'{harness}'", ps1)
            self.assertIn(harness, ci)


class PolicyOverlayTests(unittest.TestCase):
    def test_local_policy_may_only_tighten(self) -> None:
        project = fresh_project()
        config = project / ".agentic-team" / "config"
        (config / "policies.local.json").write_text(json.dumps({
            "profiles": {"autonomous": {"pause_at": ["R2"], "max_concurrent_agents": 2, "release_gate": "automatic", "architecture_gate": "human"}},
            "budgets": {"max_tasks": 10},
        }), encoding="utf-8")
        policy = team.load_policy(project)
        auto = policy["profiles"]["autonomous"]
        self.assertIn("R2", auto["pause_at"])
        self.assertEqual(auto["max_concurrent_agents"], 2)
        self.assertEqual(auto["release_gate"], "human", "a local file cannot loosen a gate")
        self.assertEqual(auto["architecture_gate"], "human")
        self.assertEqual(policy["budgets"]["max_tasks"], 10)


if __name__ == "__main__":
    unittest.main()
