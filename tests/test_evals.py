"""P8: the deterministic team-evaluation scenarios run as part of the suite."""

from __future__ import annotations

import argparse
import importlib.util
import unittest

from helpers import ROOT, fresh_project, team

SPEC = importlib.util.spec_from_file_location("run_scenarios", ROOT / "evals" / "run_scenarios.py")
assert SPEC and SPEC.loader
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class ScenarioTests(unittest.TestCase):
    def test_every_scenario_passes(self) -> None:
        specs = runner.load_scenarios()
        self.assertGreaterEqual(len(specs), 6)
        for spec in specs:
            with self.subTest(scenario=spec["name"]):
                runner.run_scenario(spec)

    def test_scenarios_cover_the_required_situations(self) -> None:
        names = {spec["name"] for spec in runner.load_scenarios()}
        for required in ("greenfield", "plan-given", "brownfield", "fusion", "rejection", "self-approval"):
            self.assertTrue(any(required in name for name in names), required)


class FusionCommitRevealTests(unittest.TestCase):
    def test_a_proposal_edited_after_submission_blocks_the_reveal(self) -> None:
        project = fresh_project()
        run = team.init_run(project, "Council", "council", "autonomous", "execute-only", "adaptive")
        team.fusion_init(project, run, argparse.Namespace(
            id="f1", question="q", sponsor="human-owner", moderator="fusion-moderator", verifier="qa-lead",
            contributor=["product-manager", "cto-architect"]))
        base = run / "_fusion" / "f1" / "proposals"
        (base / "product-manager.md").write_text("Plan A\n", encoding="utf-8")
        (base / "cto-architect.md").write_text("Plan B\n", encoding="utf-8")
        # The run path is resolved (long Windows names, /private/var on macOS); the temp project may not be.
        relative = lambda name: (base / name).relative_to(project.resolve()).as_posix()  # noqa: E731
        team.fusion_submit(project, run, "f1", "proposal", "product-manager", "plan A", relative("product-manager.md"))
        (base / "product-manager.md").write_text("Plan A, rewritten after peeking\n", encoding="utf-8")
        with self.assertRaises(team.TeamError) as raised:
            team.fusion_submit(project, run, "f1", "proposal", "cto-architect", "plan B", relative("cto-architect.md"))
        self.assertIn("changed after submission", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
