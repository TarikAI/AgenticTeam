"""P9: release integrity - generated docs current, guarantee ledger honest, presets covered, v2 runs migrate."""

from __future__ import annotations

import copy
import importlib
import re
import unittest

from helpers import ROOT, fresh_project, run_cli, team

OVERCLAIMS = (
    "enforced by the deterministic runtime",
    "cannot be bypassed",
    "tamper-proof",
    "guarantees a perfect",
    "immutable checkpoints",
    "fully enforced",
)


class GeneratedDocsTests(unittest.TestCase):
    def test_generated_sections_are_current(self) -> None:
        for path, text in team.generated_docs(ROOT).items():
            self.assertEqual(path.read_text(encoding="utf-8"), text, f"{path.name} is stale: run `python scripts/agentic_team.py docs --write`")

    def test_every_command_is_in_the_reference(self) -> None:
        reference = (ROOT / "docs" / "cli.md").read_text(encoding="utf-8")
        parser = team.build_parser()
        commands = next(action for action in parser._actions if isinstance(getattr(action, "choices", None), dict)).choices
        for name in commands:
            self.assertIn(f"### `{name}`", reference)


class GuaranteeLedgerTests(unittest.TestCase):
    def test_every_enforced_guarantee_names_a_real_test(self) -> None:
        data = team.load_json(ROOT / "config" / "guarantees.json")
        self.assertGreaterEqual(len(data["guarantees"]), 12)
        for row in data["guarantees"]:
            module_name, _, rest = row["test"].partition(".")
            module = importlib.import_module(module_name)
            target = module
            for part in rest.split("."):
                self.assertTrue(hasattr(target, part), f"{row['id']}: {row['test']} does not exist")
                target = getattr(target, part)

    def test_docs_do_not_overclaim(self) -> None:
        paths = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md")), *sorted((ROOT / "protocols").glob("*.md"))]
        problems = []
        for path in paths:
            if path.name.startswith("v3-"):
                continue  # the plan quotes the old claims it set out to fix
            text = path.read_text(encoding="utf-8").lower()
            for phrase in OVERCLAIMS:
                for match in re.finditer(re.escape(phrase), text):
                    if not text[max(0, match.start() - 4):match.start()].endswith("not "):
                        problems.append(f"{path.name}: '{phrase}'")
        self.assertEqual(problems, [], "\n".join(problems))


class PresetTests(unittest.TestCase):
    def test_presets_meet_their_coverage_invariants(self) -> None:
        self.assertEqual(team.preset_problems(team.load_json(ROOT / "team.json")), [])

    def test_a_build_preset_without_a_verifier_is_rejected(self) -> None:
        manifest = copy.deepcopy(team.load_json(ROOT / "team.json"))
        manifest["presets"]["platform-core"]["agents"].remove("qa-lead")
        self.assertTrue(any("verifier" in problem for problem in team.preset_problems(manifest)))

    def test_default_fusion_init_works_in_the_fusion_preset(self) -> None:
        project = fresh_project("fusion-product-council")
        run = team.init_run(project, "Council", "council", "autonomous", "execute-only", "adaptive")
        code, _, err = run_cli(project, "fusion-init", "--project", str(project), "--id", "x", "--question", "q",
                               "--contributor", "product-manager", "--contributor", "cto-architect")
        self.assertEqual(code, 0, err)


class VersionTests(unittest.TestCase):
    def test_versions_agree(self) -> None:
        self.assertEqual(team.VERSION, "3.0.0")
        for relative in ("team.json", "config/policies.json", "config/guarantees.json"):
            self.assertEqual(team.load_json(ROOT / relative)["version"], team.VERSION, relative)

    def test_a_v2_run_is_refused_until_migrated(self) -> None:
        project = fresh_project()
        run = team.init_run(project, "Old", "old", "autonomous", "execute-only", "adaptive")
        state = team.load_state(run)
        state["version"] = "2.0.0"
        team.write_json_atomic(run / "state.json", state)
        code, _, err = run_cli(project, "next", "--project", str(project))
        self.assertEqual(code, 1)
        self.assertIn("migrate", err)
        self.assertEqual(run_cli(project, "status", "--project", str(project))[0], 0)
        token = team.owner_token_file(state)
        code, _, err = run_cli(project, "migrate", "--project", str(project), "--by", "Owner", "--token-file", str(token))
        self.assertEqual(code, 0, err)
        self.assertEqual(run_cli(project, "next", "--project", str(project))[0], 0)

    def test_changelog_records_the_release(self) -> None:
        changelog = (ROOT / "knowledge" / "evolution" / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertRegex(changelog, r"v3\.0\.0")
        self.assertTrue((ROOT / "docs" / "migration-v3.md").is_file())


if __name__ == "__main__":
    unittest.main()
