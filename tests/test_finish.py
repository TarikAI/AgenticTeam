"""Remaining build items: Antigravity/Gemini guard hooks, Claude Code plugin package, v2 reinstall backup."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from helpers import ROOT, fresh_project, run_cli, team


class AntigravityHookTests(unittest.TestCase):
    def test_hooks_file_is_merged_and_guard_speaks_antigravity(self) -> None:
        target = Path(tempfile.mkdtemp())
        hooks = target / ".agents" / "hooks.json"
        hooks.parent.mkdir(parents=True)
        hooks.write_text(json.dumps({"my-linter": {"PostToolUse": [{"matcher": "run_command", "hooks": [{"type": "command", "command": "lint"}]}]}}), encoding="utf-8")
        team.install_team(ROOT, target, "antigravity", "platform-core", [], [])
        data = json.loads(hooks.read_text(encoding="utf-8"))
        self.assertIn("my-linter", data)
        self.assertIn("guard --harness antigravity", data["agentic-team-guard"]["PreToolUse"][0]["hooks"][0]["command"])
        self.assertEqual(team.doctor(target), [])
        payload = {"toolCall": {"name": "run_command", "args": {"CommandLine": "cat ~/.agentic-team/owner-tokens/x.token", "Cwd": str(target)}},
                   "workspacePaths": [str(target)]}
        code, out, _ = run_cli(target, "guard", "--harness", "antigravity", stdin=json.dumps(payload))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.splitlines()[0])["decision"], "deny")
        team.uninstall_team(target)
        self.assertEqual(set(json.loads(hooks.read_text(encoding="utf-8"))), {"my-linter"})
        shutil.rmtree(target, ignore_errors=True)


class GeminiHookTests(unittest.TestCase):
    def test_settings_get_a_before_tool_guard(self) -> None:
        project = fresh_project("platform-core", "gemini-cli")
        settings = json.loads((project / ".gemini" / "settings.json").read_text(encoding="utf-8"))
        hook = settings["hooks"]["BeforeTool"][0]
        self.assertIn("run_shell_command", hook["matcher"])
        self.assertIn("guard --harness gemini-cli", hook["hooks"][0]["command"])
        self.assertEqual(team.doctor(project), [])
        payload = {"tool_name": "write_file", "tool_input": {"file_path": ".agentic-team/runs/x/state.json", "content": "{}"}, "cwd": str(project)}
        code, out, _ = run_cli(project, "guard", "--harness", "gemini-cli", stdin=json.dumps(payload))
        self.assertEqual((code, json.loads(out.splitlines()[0])["decision"]), (0, "deny"))


class PluginPackageTests(unittest.TestCase):
    def test_package_builds_a_valid_plugin_and_marketplace(self) -> None:
        out = Path(tempfile.mkdtemp())
        plugin = team.package_claude_plugin(ROOT, out)
        manifest = json.loads((plugin / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual((manifest["name"], manifest["version"]), ("agentic-team", team.VERSION))
        market = json.loads((out / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(market["plugins"][0]["source"], "./plugins/agentic-team")
        self.assertEqual(len(list((plugin / "agents").glob("*.md"))), 50)
        for agent in (plugin / "agents").glob("*.md"):
            frontmatter = agent.read_text(encoding="utf-8").split("---", 2)[1]
            for ignored in ("hooks:", "permissionMode:", "mcpServers:"):
                self.assertNotIn(ignored, frontmatter, f"{agent.name}: plugin agents ignore {ignored}")
        self.assertTrue((plugin / "skills" / "agentic-build" / "SKILL.md").is_file())
        hooks = json.loads((plugin / "hooks" / "hooks.json").read_text(encoding="utf-8"))
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/bin/agentic_team.py", hooks["hooks"]["PreToolUse"][0]["hooks"][0]["command"])
        self.assertTrue((plugin / "bin" / "agentic_team.py").is_file())
        shutil.rmtree(out, ignore_errors=True)


class LegacyReinstallTests(unittest.TestCase):
    def test_reinstall_over_a_v2_install_backs_up_every_generated_file(self) -> None:
        target = Path(tempfile.mkdtemp())
        team.install_team(ROOT, target, "claude-code", "platform-core", [], [])
        record_path = target / ".agentic-team" / "install-manifest.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        record.pop("generated_hashes")  # what a v2 installer wrote
        record["version"] = "2.0.0"
        record_path.write_text(json.dumps(record), encoding="utf-8")
        agent = target / ".claude" / "agents" / "ceo.md"
        agent.write_text("my hand-edited v2 prompt\n", encoding="utf-8")
        team.install_team(ROOT, target, "claude-code", "platform-core", [], [])
        backups = list((target / ".agentic-team" / "backup").glob("*-v2"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / ".claude" / "agents" / "ceo.md").read_text(encoding="utf-8"), "my hand-edited v2 prompt\n")
        shutil.rmtree(target, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
