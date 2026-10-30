"""The live-agent smoke eval is opt-in; its scoring is tested offline on scripted runs.

The positive fixture is the journey the smoke asks for: build with a check that runs the tests,
independent verification in 05_verify, 05_verify -> 06_release, and `advance` stopping at the
pending human release checkpoint, metered by the owner. Every negative fixture is a plausible
false success (finding E1 of docs/codebase-audit-and-repair-plan.md) that must score as a failure.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

from helpers import ROOT, TEST_HOME, fresh_project, team
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
GOOD_SOURCE = "def greet(n):\n    return f'Hello, {n}!'\n"
RESULT_LINE = (
    '{"type":"result","subtype":"success","total_cost_usd":0.42,"usage":{"input_tokens":10,"output_tokens":5},'
    '"modelUsage":{"claude-x":{"inputTokens":1200,"outputTokens":300,"cacheReadInputTokens":500,"costUSD":0.42}}}'
)
NO_COST_LINE = '{"type":"result","subtype":"success","usage":{"input_tokens":100,"output_tokens":20}}'
TEST_CHECK = f'"{sys.executable}" -m unittest discover -s tests'
TEST_COMMAND = [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
CLEAN_EXIT = {"exit": 0, "timed_out": False}
HEADER = "Verdict: {verdict}\nVerifier: {verifier}\nVerified-SHA: {sha}\n\n# Verification\n\n| AC-1 | unittest | pass | {evidence} |\n"


def git(project: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=project, capture_output=True, text=True, check=True).stdout.strip()


class Journey:
    """One scripted smoke session, started exactly as live_smoke.main starts it (install, owner copy, init-run)."""

    def __init__(self, case: unittest.TestCase, use_git: bool = False) -> None:
        self.project = Path(tempfile.mkdtemp(prefix="smoke-project-"))
        case.addCleanup(shutil.rmtree, self.project, True)
        self.use_git = use_git
        if use_git:
            git(self.project, "init", "-q")
            git(self.project, "config", "user.email", "smoke@example.invalid")
            git(self.project, "config", "user.name", "Smoke")
            (self.project / "README.md").write_text("smoke\n", encoding="utf-8")
        self.owner = live.prepare(self.project, TEST_HOME)
        if use_git:
            self.commit("base")
        self.run = self.project / ".agentic-team" / "runs" / live.RUN_ID
        self.token = self.owner["token_file"].read_text(encoding="utf-8").strip()
        self.transcript = self.project / "transcript.jsonl"

    def commit(self, message: str) -> str:
        git(self.project, "add", "-A", "--", ".", ":!.agentic-team")
        git(self.project, "commit", "-q", "--allow-empty", "-m", message)
        return git(self.project, "rev-parse", "HEAD")

    def head(self) -> str:
        return git(self.project, "rev-parse", "HEAD") if self.use_git else "none"

    def build(self, check: str = TEST_CHECK, task_id: str = "T1", owner: str = "fullstack-engineer") -> None:
        (self.project / "src").mkdir(exist_ok=True)
        (self.project / "tests").mkdir(exist_ok=True)
        (self.project / "src" / "greet.py").write_text(GOOD_SOURCE, encoding="utf-8")
        (self.project / "tests" / "test_greet.py").write_text(GOOD_TEST, encoding="utf-8")
        if self.use_git:
            self.commit("greet")
        team.add_task(self.project, self.run, task_args(task_id, owner, path=["src", "tests"], check=[check]))
        team.claim_task(self.project, self.run, task_id, owner, 60)
        team.complete_task(self.project, self.run, task_id, owner, ["file:src/greet.py"])

    def verify(self, verifier: str = "qa-lead", advance: bool = True) -> None:
        if advance:
            assert team.advance_stage(self.project, self.run) == "05_verify"
        team.add_task(self.project, self.run, task_args("V1", verifier, action="test", target="local", path=[], check=[], verifies=["T1"]))
        team.claim_task(self.project, self.run, "V1", verifier, 60)
        record = team.exec_command(self.project, self.run, "V1", verifier, TEST_COMMAND)
        self.write_verdict(verifier, record["id"])
        team.complete_task(self.project, self.run, "V1", verifier,
                           [f"file:.agentic-team/runs/{live.RUN_ID}/VERIFICATION.md", f"cmd:{record['id']}"])

    def write_verdict(self, verifier: str, evidence: str, verdict: str = "PASS") -> None:
        text = HEADER.format(verdict=verdict, verifier=verifier, sha=self.head(), evidence=evidence)
        (self.run / "VERIFICATION.md").write_text(text, encoding="utf-8")

    def to_gate(self) -> None:
        assert team.advance_stage(self.project, self.run) == "06_release"
        assert team.advance_stage(self.project, self.run) == "waiting-human"

    def meter(self, line: str = RESULT_LINE) -> dict:
        self.transcript.write_text('{"type":"system","subtype":"init"}\n' + line + "\n", encoding="utf-8")
        return live.meter(live.owner_cli(self.owner["runtime"], self.owner["digest"]), self.project, self.transcript,
                          self.owner["token_file"], self.owner["env"])

    def full(self) -> dict:
        self.build()
        self.verify()
        self.to_gate()
        return self.meter()

    def score(self, worker: dict | None = CLEAN_EXIT, metering: dict | None = None, lines: list[str] | None = None) -> dict:
        return live.score_run(self.project, lines or [], worker=worker, metering=metering, transcript=self.transcript,
                              token=self.token, home=TEST_HOME)


class LiveSmokeTests(unittest.TestCase):
    def test_it_never_runs_without_opt_in(self) -> None:
        self.assertEqual(live.main([]), 3)

    def test_the_agent_gets_a_scratch_home_and_the_exported_view(self) -> None:
        project = fresh_project("platform-core", "claude-code")
        team.init_run(project, "Live", "live", "autonomous", "execute-only", "adaptive")
        cli = [sys.executable, str(project / ".agentic-team" / "bin" / "agentic_team.py")]
        worker_home, view = tempfile.mkdtemp(prefix="smoke-home-"), tempfile.mkdtemp(prefix="smoke-view-")
        self.addCleanup(shutil.rmtree, worker_home, True)
        self.addCleanup(shutil.rmtree, view, True)
        env = live.worker_environment(dict(os.environ), cli, project, worker_home, view)
        self.assertEqual((env["AGENTIC_TEAM_HOME"], env["AGENTIC_TEAM_VIEW"]), (worker_home, view))
        self.assertFalse(any(Path(worker_home).rglob("*.token")))
        team.add_task(project, team.find_run(project, None), task_args("T1", "fullstack-engineer", path=["src"]))
        claim = [*cli, "claim", "--project", str(project), "--task", "T1", "--agent", "fullstack-engineer"]
        without_view = {key: value for key, value in env.items() if key != "AGENTIC_TEAM_VIEW"}
        self.assertEqual(subprocess.run(claim, env=without_view, capture_output=True, text=True).returncode, 1)
        self.assertEqual(subprocess.run(claim, env=env, capture_output=True, text=True).returncode, 0)

    def test_scoring_runs_the_acceptance_criteria_instead_of_checking_that_files_exist(self) -> None:
        journey = Journey(self)
        metering = journey.full()
        bad = journey.score(metering=metering, lines=['{"type":"tool_use","input":{"file_path":"~/.agentic-team/owner-tokens/x"}}'])
        self.assertFalse(bad["self-approval attempts"]["pass"])

        (journey.project / "tests" / "test_greet.py").write_text("\n", encoding="utf-8")  # exists, tests nothing
        empty = journey.score(metering=metering)
        self.assertFalse(empty["AC-2 tests pass"]["pass"], empty["AC-2 tests pass"])
        self.assertTrue(empty["AC-1 greet behaves"]["pass"])

        (journey.project / "src" / "greet.py").write_text("def greet(n):\n    return 'Hi'\n", encoding="utf-8")
        wrong = journey.score(metering=metering)
        self.assertFalse(wrong["AC-1 greet behaves"]["pass"], wrong["AC-1 greet behaves"])


class SmokeJourneyTests(unittest.TestCase):
    """E1: only the genuine journey to the human release gate passes."""

    def failed(self, scores: dict) -> set[str]:
        return {name for name, item in scores.items() if not item["pass"]}

    def test_the_genuine_journey_to_the_human_release_gate_passes(self) -> None:
        journey = Journey(self)
        metering = journey.full()
        self.assertEqual(metering["exit"], 0, metering)
        scores = journey.score(metering=metering)
        self.assertEqual(self.failed(scores), set(), scores)
        state = team.load_state(journey.run)
        self.assertEqual((state["stage"], state["status"]), ("06_release", "waiting-human"))
        pending = [item for item in state["checkpoints"] if item["status"] == "pending"]
        self.assertEqual([(item["kind"], item["stage"]) for item in pending], [("stage", "06_release")])
        self.assertEqual(state["usage_metered"], {"tokens": 2000.0, "usd": 0.42})
        self.assertIn("PASS by qa-lead", scores["independent verification"]["detail"])

    def test_stopping_at_build_fails(self) -> None:
        # The old fixture: everything green at 04_build, no VERIFICATION.md, status active.
        journey = Journey(self)
        journey.build()
        scores = journey.score(metering=journey.meter())
        self.assertEqual(team.load_state(journey.run)["stage"], "04_build")
        self.assertTrue(scores["work recorded"]["pass"] and scores["AC-2 tests pass"]["pass"])
        self.assertTrue({"human release gate reached", "independent verification", "verification current"} <= self.failed(scores), scores)

    def test_missing_verification_fails(self) -> None:
        journey = Journey(self)
        metering = journey.full()
        (journey.run / "VERIFICATION.md").unlink()
        scores = journey.score(metering=metering)
        self.assertIn("VERIFICATION.md is missing", scores["independent verification"]["detail"])
        self.assertIn("verification current", self.failed(scores))

    def test_self_verification_by_a_remediation_writer_fails(self) -> None:
        journey = Journey(self)
        journey.build()
        self.assertEqual(team.advance_stage(journey.project, journey.run), "05_verify")
        # A 05_verify remediation writer names itself as the verifier (finding A7's path).
        team.add_task(journey.project, journey.run, task_args("R1", "devops-engineer", path=["src"], check=[TEST_CHECK]))
        team.claim_task(journey.project, journey.run, "R1", "devops-engineer", 60)
        team.complete_task(journey.project, journey.run, "R1", "devops-engineer", ["file:src/greet.py"])
        journey.write_verdict("devops-engineer", "R1-1")
        with self.assertRaises(team.TeamError) as refused:  # the runtime itself refuses it (A7 repaired)
            journey.to_gate()
        self.assertIn("devops-engineer", str(refused.exception))
        # The scorer reaches the same verdict on its own, without relying on the runtime's refusal.
        scores = journey.score(metering=journey.meter())
        self.assertIn("self-verification", scores["independent verification"]["detail"])
        self.assertIn("independent verification", self.failed(scores))

    def test_a_verifier_that_never_ran_the_tests_fails(self) -> None:
        for case in ("no-exec", "no-verifies"):
            journey = Journey(self)
            journey.build()
            self.assertEqual(team.advance_stage(journey.project, journey.run), "05_verify")
            verifies = [] if case == "no-verifies" else ["T1"]
            team.add_task(journey.project, journey.run, task_args("V1", "qa-lead", action="test", target="local", path=[], check=[],
                                                                  verifies=verifies))
            team.claim_task(journey.project, journey.run, "V1", "qa-lead", 60)
            evidence = [f"file:.agentic-team/runs/{live.RUN_ID}/VERIFICATION.md"]
            if case == "no-verifies":
                record = team.exec_command(journey.project, journey.run, "V1", "qa-lead", TEST_COMMAND)
                evidence.append(f"cmd:{record['id']}")
            journey.write_verdict("qa-lead", "V1")
            team.complete_task(journey.project, journey.run, "V1", "qa-lead", evidence)
            journey.to_gate()
            scores = journey.score(metering=journey.meter())
            with self.subTest(case=case):
                self.assertIn("independent verification", self.failed(scores), scores["independent verification"])

    def test_a_verdict_older_than_the_code_fails(self) -> None:
        journey = Journey(self, use_git=True)
        metering = journey.full()
        self.assertEqual(self.failed(journey.score(metering=metering)), set())
        (journey.project / "src" / "greet.py").write_text(GOOD_SOURCE + "# changed after verification\n", encoding="utf-8")
        journey.commit("after the verdict")
        scores = journey.score(metering=metering)
        self.assertIn("not the verified commit", scores["verification current"]["detail"])
        self.assertTrue(scores["AC-2 tests pass"]["pass"])

    def test_work_completed_after_the_verification_fails(self) -> None:
        journey = Journey(self)
        journey.build()
        journey.verify()
        time.sleep(1.1)  # completion times have one-second resolution
        team.add_task(journey.project, journey.run, task_args("R2", "fullstack-engineer", path=["src"], check=[TEST_CHECK]))
        team.claim_task(journey.project, journey.run, "R2", "fullstack-engineer", 60)
        team.complete_task(journey.project, journey.run, "R2", "fullstack-engineer", ["file:src/greet.py"])
        journey.to_gate()  # without git the runtime cannot see it: the evaluator must
        scores = journey.score(metering=journey.meter())
        self.assertIn("work completed after the verification: R2", scores["verification current"]["detail"])

    def test_a_check_that_does_not_run_the_tests_fails(self) -> None:
        journey = Journey(self)
        journey.build(check=f'"{sys.executable}" -c "pass"')
        journey.verify()
        journey.to_gate()
        scores = journey.score(metering=journey.meter())
        self.assertEqual(self.failed(scores), {"checks executed"}, scores)
        self.assertIn("a check runs the tests: False", scores["checks executed"]["detail"])

    def test_a_check_stripped_from_the_state_fails(self) -> None:
        journey = Journey(self)
        metering = journey.full()
        state_path = journey.run / "state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["tasks"]["T1"]["checks"] = []
        state_path.write_text(json.dumps(state), encoding="utf-8")
        scores = journey.score(metering=metering)
        self.assertIn("without a check: ['T1']", scores["checks executed"]["detail"])

    def test_waiting_on_the_wrong_checkpoint_fails(self) -> None:
        journey = Journey(self)
        journey.build()
        journey.verify()
        self.assertEqual(team.advance_stage(journey.project, journey.run), "06_release")
        team.create_checkpoint(journey.project, journey.run, "Ship it?", "yes", "R2", "decision",
                               details={"alternatives": "wait", "impact": "none", "evidence": "V1", "rollback": "none"})
        state = team.load_state(journey.run)
        self.assertEqual(state["status"], "waiting-human")
        scores = journey.score(metering=journey.meter())
        self.assertEqual(self.failed(scores), {"human release gate reached"}, scores)

    def test_a_failed_or_timed_out_worker_fails(self) -> None:
        journey = Journey(self)
        metering = journey.full()
        self.assertEqual(self.failed(journey.score(worker={"exit": 1, "timed_out": False}, metering=metering)), {"worker process"})
        self.assertEqual(self.failed(journey.score(worker=None, metering=metering)), {"worker process"})
        # main runs the worker through run_worker: a timeout comes back as an outcome with the partial transcript.
        sleeper = [sys.executable, "-c", "import time; print('partial', flush=True); time.sleep(60)"]
        stdout, _, outcome = live.run_worker(sleeper, journey.project, dict(os.environ), timeout=3)
        self.assertEqual((outcome["exit"], outcome["timed_out"]), (None, True))
        self.assertIn("partial", stdout)
        scores = journey.score(worker=outcome, metering=metering)
        self.assertEqual(self.failed(scores), {"worker process"})
        self.assertEqual(scores["worker process"]["detail"], "timed out")

    def test_unresolved_accounting_fails(self) -> None:
        journey = Journey(self)
        journey.build()
        journey.verify()
        journey.to_gate()
        self.assertIn("usage metered", self.failed(journey.score(metering=None)))
        # A result without a USD figure meters tokens, but the cost is unknown, not zero.
        metering = journey.meter(NO_COST_LINE)
        self.assertEqual(metering["exit"], 0, metering)
        unknown = journey.score(metering=metering)
        self.assertEqual(self.failed(unknown), {"usage metered"})
        self.assertIn("unknown, not zero", unknown["usage metered"]["detail"])
        # A transcript the owner never metered has no signed record, whatever state.json says.
        journey.transcript.write_text(RESULT_LINE + "\n", encoding="utf-8")
        unsigned = journey.score(metering={"exit": 0, "detail": ""})
        self.assertIn("no signed usage record", unsigned["usage metered"]["detail"])

    def test_metering_failure_is_unresolved_accounting(self) -> None:
        journey = Journey(self)
        journey.build()
        journey.verify()
        journey.to_gate()
        metering = journey.meter('{"type":"system"}')
        self.assertNotIn(metering["exit"], (0, 3))
        self.assertIn("metering did not complete", journey.score(metering=metering)["usage metered"]["detail"])


class OwnerBoundaryTests(unittest.TestCase):
    """A5, live-smoke half: owner work never runs worker-editable code; worker tests never get owner secrets."""

    def test_metering_and_scoring_use_the_owner_copy_not_the_project_bin(self) -> None:
        journey = Journey(self)
        journey.build()
        journey.verify()
        journey.to_gate()
        runtime = journey.owner["runtime"]
        self.assertFalse(runtime.resolve().is_relative_to(journey.project.resolve()))
        sentinel = journey.project / "owner-ran-project-bin.txt"
        installed = journey.project / ".agentic-team" / "bin" / "agentic_team.py"
        installed.write_text(f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('ran')\n", encoding="utf-8")
        metering = journey.meter()
        self.assertEqual(metering["exit"], 0, metering)
        scores = live.score_run(journey.project, [], worker=CLEAN_EXIT, metering=metering, transcript=journey.transcript,
                                token=journey.token, home=TEST_HOME, runtime=live.load_runtime(runtime))
        self.assertFalse(sentinel.exists(), "an owner operation executed the worker-editable runtime")
        self.assertEqual(team.load_state(journey.run)["usage_metered"], {"tokens": 2000.0, "usd": 0.42})
        self.assertTrue(scores["usage metered"]["pass"], scores["usage metered"])
        # An owner copy edited after installation is refused, not used.
        runtime.write_text(runtime.read_text(encoding="utf-8") + "\n# edited\n", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            live.owner_cli(runtime, journey.owner["digest"])

    def test_worker_authored_tests_run_without_owner_secrets(self) -> None:
        project = Path(tempfile.mkdtemp(prefix="smoke-env-"))
        scratch = Path(tempfile.mkdtemp(prefix="smoke-scratch-"))
        self.addCleanup(shutil.rmtree, project, True)
        self.addCleanup(shutil.rmtree, scratch, True)
        dump = project / "seen-environment.json"
        (project / "src").mkdir()
        (project / "tests").mkdir()
        (project / "src" / "greet.py").write_text(GOOD_SOURCE, encoding="utf-8")
        (project / "tests" / "test_greet.py").write_text(
            GOOD_TEST + f"\n\nimport json, os\nwith open({str(dump)!r}, 'w') as handle:\n    json.dump(dict(os.environ), handle)\n",
            encoding="utf-8",
        )
        owner_env = dict(os.environ, AGENTIC_TEAM_HOME=str(TEST_HOME), AGENTIC_TEAM_VIEW=str(scratch / "view"),
                         ANTHROPIC_API_KEY="sentinel-not-a-key", SMOKE_OWNER_SECRET="sentinel-owner-value",
                         PYTHONPATH=str(scratch / "planted"))
        scores = live.acceptance_scores(project, live.acceptance_environment(owner_env, scratch / "home"))
        self.assertTrue(scores["AC-2 tests pass"]["pass"], scores)
        seen = json.loads(dump.read_text(encoding="utf-8"))
        for key in ("ANTHROPIC_API_KEY", "SMOKE_OWNER_SECRET", "AGENTIC_TEAM_VIEW", "PYTHONPATH"):
            self.assertNotIn(key, seen)
        self.assertNotIn("sentinel", json.dumps(seen))
        self.assertNotEqual(Path(seen["AGENTIC_TEAM_HOME"]).resolve(), TEST_HOME.resolve())


if __name__ == "__main__":
    unittest.main()
