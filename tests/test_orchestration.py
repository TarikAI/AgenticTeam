"""P4: event log, metrics, budgets, and orchestrator ergonomics (next, board, pack, brief)."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

from helpers import fresh_project, run_cli, team
from test_regressions import task_args


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self.project = fresh_project()
        self.run = team.init_run(self.project, "Orchestration", "orc", "autonomous", "execute-only", "adaptive")

    def token(self) -> str:
        return team.owner_token_file(team.load_state(self.run)).read_text(encoding="utf-8").strip()


class EventLogTests(Base):
    def test_R24_events_live_outside_state_and_state_does_not_grow_with_them(self) -> None:
        team.add_task(self.project, self.run, task_args("A", "backend-engineer"))
        team.claim_task(self.project, self.run, "A", "backend-engineer", 60)
        before = (self.run / "state.json").stat().st_size
        for _ in range(60):
            team.renew_lease(self.project, self.run, "A", "backend-engineer", 60)
        after = (self.run / "state.json").stat().st_size
        self.assertNotIn("events", team.load_state(self.run))
        self.assertLess(after - before, 300, "state.json must not accumulate event history")
        self.assertGreaterEqual(len(team.read_events(self.run)), 62)

    def test_event_chain_detects_edits(self) -> None:
        team.add_task(self.project, self.run, task_args("A", "backend-engineer"))
        self.assertEqual(team.verify_events(self.run), [])
        path = self.run / "events.jsonl"
        lines = path.read_text(encoding="utf-8").splitlines()
        first = json.loads(lines[0])
        first["type"] = "rewritten-history"
        lines[0] = json.dumps(first)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.assertTrue(team.verify_events(self.run))
        self.assertTrue(any("chain" in item or "head" in item for item in team.doctor(self.project)))

    def test_log_command_filters(self) -> None:
        team.add_task(self.project, self.run, task_args("A", "backend-engineer"))
        code, out, err = run_cli(self.project, "log", "--project", str(self.project), "--type", "task-added", "--json")
        self.assertEqual(code, 0, err)
        events = json.loads(out)
        self.assertEqual([event["task"] for event in events], ["A"])


class ErgonomicsTests(Base):
    def test_next_lists_only_claimable_work(self) -> None:
        team.add_task(self.project, self.run, task_args("A", "backend-engineer", path=["src/api"]))
        team.add_task(self.project, self.run, task_args("B", "frontend-engineer", path=["src/api/views"]))
        team.add_task(self.project, self.run, task_args("C", "backend-engineer", depends_on=["A"]))
        self.assertEqual([item["task"] for item in team.next_tasks(self.project, self.run, "backend-engineer")], ["A"])
        team.claim_task(self.project, self.run, "A", "backend-engineer", 60)
        self.assertEqual(team.next_tasks(self.project, self.run, "frontend-engineer"), [], "B overlaps A's claim")

    def test_board_formats(self) -> None:
        team.add_task(self.project, self.run, task_args("A", "backend-engineer"))
        team.add_task(self.project, self.run, task_args("B", "backend-engineer", depends_on=["A"]))
        state = team.load_state(self.run)
        self.assertIn("| A | backend-engineer | ready", team.render_board(state, "md"))
        self.assertIn("a --> b", team.render_board(state, "mermaid"))
        self.assertEqual(len(json.loads(team.render_board(state, "json"))["04_build"]), 2)

    def test_pack_respects_the_token_budget_and_lists_omissions(self) -> None:
        spec = self.project / "docs" / "spec.md"
        spec.parent.mkdir(parents=True)
        spec.write_text("# Spec\n\n" + ("The order service must be idempotent. " * 1200), encoding="utf-8")
        team.add_task(self.project, self.run, task_args("A", "backend-engineer", input=["docs/spec.md"], check=["python -m pytest -q"]))
        path, tokens, omissions = team.build_pack(self.project, self.run, "A")
        self.assertLessEqual(tokens, 8000)
        self.assertGreaterEqual(tokens, 2000)
        text = path.read_text(encoding="utf-8")
        self.assertIn("claim --task A --agent backend-engineer", text)
        self.assertIn("--run-checks", text)
        self.assertTrue(omissions, "the oversized input must be reported as truncated")

    def test_brief_points_at_the_pack(self) -> None:
        team.add_task(self.project, self.run, task_args("A", "backend-engineer"))
        brief = team.render_brief(self.project, self.run, "A")
        self.assertIn("You are `backend-engineer`", brief)
        self.assertIn("_context", brief)

    def test_status_brief_is_short(self) -> None:
        for index in range(30):
            team.add_task(self.project, self.run, task_args(f"T{index}", "backend-engineer"))
        text = team.render_status(team.load_state(self.run), brief=True)
        self.assertLessEqual(len(text.splitlines()), 20)
        self.assertIn("Ready now:", text)


class MetricsAndBudgetTests(Base):
    def test_metrics_per_role(self) -> None:
        team.add_task(self.project, self.run, task_args("A", "backend-engineer"))
        team.claim_task(self.project, self.run, "A", "backend-engineer", 60)
        team.fail_task(self.project, self.run, "A", "backend-engineer", "flaky")
        team.claim_task(self.project, self.run, "A", "backend-engineer", 60)
        record = team.exec_command(self.project, self.run, "A", "backend-engineer", [sys.executable, "-c", "pass"])
        team.complete_task(self.project, self.run, "A", "backend-engineer", [f"cmd:{record['id']}"], usage={"tokens": 1500.0})
        data = team.compute_metrics(self.run)
        role = data["roles"]["backend-engineer"]
        self.assertEqual((role["completed"], role["first_pass"], role["failures"]), (1, 0, 1))
        self.assertEqual(data["usage"], {"tokens": 1500.0})
        self.assertEqual(data["commands_executed"], 1)

    def test_budget_warns_then_stops_until_the_human_waives(self) -> None:
        policy_path = self.project / ".agentic-team" / "config" / "policies.json"
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["budgets"]["max_tasks"] = 3
        policy_path.write_text(json.dumps(policy), encoding="utf-8")
        team.add_task(self.project, self.run, task_args("A", "backend-engineer"))
        team.add_task(self.project, self.run, task_args("B", "backend-engineer"))
        team.add_task(self.project, self.run, task_args("C", "backend-engineer"))  # 3 >= 0.8*3: warning checkpoint
        state = team.load_state(self.run)
        self.assertTrue(any(item["kind"] == "budget" for item in state["checkpoints"]))
        with self.assertRaises(team.BlockedError):
            team.add_task(self.project, self.run, task_args("D", "backend-engineer"))  # 4 > 3
        team.waive_requirement(self.project, self.run, "budget:max_tasks", "scope grew", "Owner", self.token())
        team.add_task(self.project, self.run, task_args("D", "backend-engineer"))

    def test_usage_flag_parsing(self) -> None:
        self.assertEqual(team.parse_usage(["tokens=100,usd=0.5", "tokens=50"]), {"tokens": 150.0, "usd": 0.5})
        with self.assertRaises(team.TeamError):
            team.parse_usage(["dollars=3"])


class MigrationTests(unittest.TestCase):
    def test_migrate_moves_legacy_events_into_the_chain(self) -> None:
        project = fresh_project()
        run = team.init_run(project, "Legacy", "legacy", "autonomous", "execute-only", "adaptive")
        state = team.load_state(run)
        state["events"] = [{"time": team.utcnow(), "type": "run-created"}, {"time": team.utcnow(), "type": "task-added", "task": "X"}]
        team.write_json_atomic(run / "state.json", state)
        token = team.owner_token_file(state).read_text(encoding="utf-8").strip()
        steps = team.migrate_run(project, run, "Owner", token)
        self.assertTrue(any("moved 2 events" in step for step in steps))
        self.assertNotIn("events", team.load_state(run))
        self.assertEqual(team.verify_events(run), [])


if __name__ == "__main__":
    unittest.main()
