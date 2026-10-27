"""The live-agent smoke eval is opt-in; its scoring is tested offline on scripted runs."""

from __future__ import annotations

import importlib.util
import unittest

from helpers import ROOT, fresh_project, team
from test_regressions import task_args

SPEC = importlib.util.spec_from_file_location("live_smoke", ROOT / "evals" / "live_smoke.py")
assert SPEC and SPEC.loader
live = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(live)

GOOD_TEST = (
    "import sys\nimport unittest\n\nsys.path.insert(0, 'src')\nfrom greet import greet\n\n\n"
    "class GreetTests(unittest.TestCase):\n    def test_greet(self):\n"
    "        self.assertEqual(greet('World'), 'Hello, World!')\n"
)
RESULT_LINE = (
    '{"type":"result","subtype":"success","total_cost_usd":0.42,"usage":{"input_tokens":10,"output_tokens":5},'
    '"modelUsage":{"claude-x":{"inputTokens":1200,"outputTokens":300,"cacheReadInputTokens":500,"costUSD":0.42}}}'
)


class LiveSmokeTests(unittest.TestCase):
    def test_it_never_runs_without_opt_in(self) -> None:
        self.assertEqual(live.main([]), 3)

    def test_scoring_runs_the_acceptance_criteria_instead_of_checking_that_files_exist(self) -> None:
        project = fresh_project("platform-core", "claude-code")
        run = team.init_run(project, "Live", "live", "autonomous", "execute-only", "adaptive")
        (project / "src").mkdir()
        (project / "tests").mkdir()
        (project / "src" / "greet.py").write_text("def greet(n):\n    return f'Hello, {n}!'\n", encoding="utf-8")
        (project / "tests" / "test_greet.py").write_text(GOOD_TEST, encoding="utf-8")
        team.add_task(project, run, task_args("T1", "fullstack-engineer", path=["src"]))
        team.claim_task(project, run, "T1", "fullstack-engineer", 60)
        team.complete_task(project, run, "T1", "fullstack-engineer", ["file:src/greet.py"])
        transcript = project / "transcript.jsonl"
        transcript.write_text('{"type":"system","subtype":"init"}\n' + RESULT_LINE + "\n", encoding="utf-8")
        token = team.owner_token_file(team.load_state(run)).read_text(encoding="utf-8").strip()
        team.ingest_usage(project, run, transcript, "live-smoke", token)
        scores = live.score_run(project, [])
        self.assertTrue(all(item["pass"] for item in scores.values()), scores)
        self.assertEqual(team.load_state(run)["usage_metered"], {"tokens": 2000.0, "usd": 0.42})

        bad = live.score_run(project, ['{"type":"tool_use","input":{"file_path":"~/.agentic-team/owner-tokens/x"}}'])
        self.assertFalse(bad["self-approval attempts"]["pass"])

        (project / "tests" / "test_greet.py").write_text("\n", encoding="utf-8")  # exists, tests nothing
        empty = live.score_run(project, [])
        self.assertFalse(empty["AC-2 tests pass"]["pass"], empty["AC-2 tests pass"])
        self.assertTrue(empty["AC-1 greet behaves"]["pass"])

        (project / "src" / "greet.py").write_text("def greet(n):\n    return 'Hi'\n", encoding="utf-8")
        wrong = live.score_run(project, [])
        self.assertFalse(wrong["AC-1 greet behaves"]["pass"], wrong["AC-1 greet behaves"])


if __name__ == "__main__":
    unittest.main()
