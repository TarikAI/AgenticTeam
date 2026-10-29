"""Repair F2: one coherent history under interruption and concurrency (audit findings D1-D3, A7)."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import threading
import unittest
from unittest import mock

from helpers import fresh_project, run_cli, team
from test_regressions import PASSING_CHECK, task_args

PASS_HEADER = "Verdict: PASS\nVerifier: {verifier}\nVerified-SHA: none\n\n# Verification\n\n| AC-1 | tests | pass | cmd |\n"


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self.project = fresh_project()
        self.run = team.init_run(self.project, "History", "history", "autonomous", "execute-only", "adaptive")

    def token(self) -> str:
        return team.owner_token_file(team.load_state(self.run)).read_text(encoding="utf-8").strip()

    def task(self) -> dict:
        return team.load_state(self.run)["tasks"]["A"]


class ExecIdentityTests(Base):
    """D1: concurrent and interrupted commands never share an ID or overwrite evidence."""

    def setUp(self) -> None:
        super().setUp()
        team.add_task(self.project, self.run, task_args("A", "backend-engineer"))
        team.claim_task(self.project, self.run, "A", "backend-engineer", 60)

    def test_concurrent_commands_get_distinct_ids_and_logs(self) -> None:
        results: list[tuple[int, str, str]] = []

        def call(word: str) -> None:
            results.append(run_cli(self.project, "exec", "--project", str(self.project), "--task", "A", "--agent", "backend-engineer",
                                   "--", sys.executable, "-c", f"import time; time.sleep(1); print('{word}')"))
        threads = [threading.Thread(target=call, args=(word,)) for word in ("first", "second")]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual([code for code, _, _ in results], [0, 0], results)
        execs = self.task()["execs"]
        self.assertEqual(sorted(item["id"] for item in execs), ["A-1", "A-2"])
        logs = {item["log"] for item in execs}
        self.assertEqual(len(logs), 2)
        outputs = sorted((self.run / log).read_text(encoding="utf-8") for log in logs)
        self.assertTrue(any("first" in text for text in outputs) and any("second" in text for text in outputs), outputs)
        self.assertEqual(self.task().get("exec_pending"), [])

    def test_an_interrupted_execution_keeps_its_reservation(self) -> None:
        with mock.patch.object(team.subprocess, "run", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                team.exec_command(self.project, self.run, "A", "backend-engineer", [sys.executable, "-c", "pass"])
        self.assertEqual(self.task()["exec_pending"], ["A-1"])
        record = team.exec_command(self.project, self.run, "A", "backend-engineer", [sys.executable, "-c", "pass"])
        self.assertEqual(record["id"], "A-2")
        self.assertEqual(team.verify_events(self.run), [])

    def test_a_result_for_an_ended_claim_is_kept_but_not_counted(self) -> None:
        original = team.subprocess.run

        def reopen_during_run(*args, **kwargs):
            team.reopen_task(self.project, self.run, "A", "wedged")
            return original(*args, **kwargs)
        with mock.patch.object(team.subprocess, "run", side_effect=reopen_during_run):
            team.exec_command(self.project, self.run, "A", "backend-engineer", [PASSING_CHECK], shell=True)
        record = self.task()["execs"][-1]
        self.assertTrue(record["stale_claim"])
        self.assertIsNone(team.check_record(self.task(), PASSING_CHECK))


class EventTransactionTests(Base):
    """D2: an interrupted write never forks the event chain; edited history is refused."""

    def interrupt_next_state_write(self) -> None:
        original = team.write_json_atomic

        def fail_on_state(path, data):
            if Path(path).name == "state.json":
                raise OSError("simulated crash after the event append")
            return original(path, data)
        with mock.patch.object(team, "write_json_atomic", side_effect=fail_on_state):
            with self.assertRaises(OSError):
                team.add_task(self.project, self.run, task_args("LOST", "backend-engineer"))

    def test_an_interrupted_write_recovers_into_one_chain(self) -> None:
        self.interrupt_next_state_write()
        self.assertNotIn("LOST", team.load_state(self.run)["tasks"])
        team.add_task(self.project, self.run, task_args("B", "backend-engineer"))
        self.assertEqual(team.verify_events(self.run), [])
        self.assertTrue((self.run / "events.interrupted.jsonl").is_file())
        types = [event["type"] for event in team.read_events(self.run)]
        self.assertIn("interrupted-write-recovered", types)
        self.assertEqual(team.audit_verify(self.project, self.run, self.token()), [])

    def test_a_torn_final_line_recovers(self) -> None:
        with team.events_path(self.run).open("ab") as handle:
            handle.write(b'{"seq": 99, "type": "task-ad')
        team.add_task(self.project, self.run, task_args("B", "backend-engineer"))
        self.assertEqual(team.verify_events(self.run), [])

    def test_edited_or_truncated_history_is_refused(self) -> None:
        team.add_task(self.project, self.run, task_args("B", "backend-engineer"))
        path = team.events_path(self.run)
        original = path.read_bytes()
        lines = original.decode("utf-8").splitlines()
        edited = json.loads(lines[0])
        edited["type"] = "rewritten"
        for content in ("\n".join([json.dumps(edited), *lines[1:]]) + "\n", "\n".join(lines[:-1]) + "\n"):
            path.write_text(content, encoding="utf-8")
            with self.assertRaises(team.TeamError):
                team.add_task(self.project, self.run, task_args("C", "backend-engineer"))
        path.write_bytes(original)
        team.add_task(self.project, self.run, task_args("C", "backend-engineer"))


class ReopenRetryTests(Base):
    """D3: reopening a claim spends the retry budget and keeps the claimant on record."""

    def cycle(self, reason: str) -> None:
        team.claim_task(self.project, self.run, "A", "backend-engineer", 60)
        team.reopen_task(self.project, self.run, "A", reason)

    def test_claim_reopen_cycles_stop_at_the_retry_limit(self) -> None:
        team.add_task(self.project, self.run, task_args("A", "backend-engineer"))
        limit = team.profile_policy(self.project, team.load_state(self.run))["max_task_retries"]
        for number in range(limit):
            self.cycle(f"wedged differently {'x' * number}")
            self.assertEqual(self.task()["status"], "ready")
        self.cycle("wedged once more, a new way")
        self.assertEqual(self.task()["status"], "failed")
        self.assertEqual(len(self.task()["failures"]), limit + 1)
        with self.assertRaises(team.TeamError):
            team.claim_task(self.project, self.run, "A", "backend-engineer", 60)
        with self.assertRaises(team.TeamError):
            team.reopen_task(self.project, self.run, "A", "try again")
        team.reopen_task(self.project, self.run, "A", "owner extends", by="Owner", token=self.token(), extend_retries=1)
        self.assertEqual(self.task()["status"], "ready")

    def test_the_same_reason_twice_escalates(self) -> None:
        team.add_task(self.project, self.run, task_args("A", "backend-engineer"))
        self.cycle("stuck on the build")
        self.cycle("stuck on the build")
        self.assertEqual(self.task()["status"], "failed")


class SignedUsageAuditTests(Base):
    """S2, owner audit side: metered usage in state must match the signed usage records."""

    def test_forged_usage_projections_fail_the_owner_audit(self) -> None:
        transcript = self.run / "transcript.jsonl"
        transcript.write_text(json.dumps({"type": "result", "subtype": "success", "total_cost_usd": 0.01,
                                          "usage": {"input_tokens": 100, "output_tokens": 20}}) + "\n", encoding="utf-8")
        team.ingest_usage(self.project, self.run, transcript, "Owner", self.token())
        self.assertEqual(team.audit_verify(self.project, self.run, self.token()), [])
        forgeries = [
            lambda state: state["usage_sources"][0].update(usd=0.0),
            lambda state: state["usage_metered"].update(usd=0.0),
            lambda state: state["usage_sources"].append({"id": "U-002", "sha256": "0" * 64, "usd": 0.0}),
            lambda state: state.update(usage_sources=[], usage_metered={}),
        ]
        original = (self.run / "state.json").read_bytes()
        cleared = team.load_state(self.run)
        cleared.update(usage_sources=[], usage_metered={})
        team.write_json_atomic(self.run / "state.json", cleared)
        cheaper = self.run / "cheaper.jsonl"
        cheaper.write_text(json.dumps({"type": "result", "subtype": "success", "total_cost_usd": 0.001,
                                       "usage": {"input_tokens": 1}}) + "\n", encoding="utf-8")
        record = team.ingest_usage(self.project, self.run, cheaper, "Owner", self.token())
        self.assertEqual(record["id"], "U-002", "a usage ID is never reused after state was cleared")
        self.assertTrue(any("usage" in problem for problem in team.audit_verify(self.project, self.run, self.token())))
        (self.run / "state.json").write_bytes(original)
        for forge in forgeries:
            state = team.load_state(self.run)
            forge(state)
            team.write_json_atomic(self.run / "state.json", state)
            with self.subTest(forge=forge):
                self.assertTrue(any("usage" in problem for problem in team.audit_verify(self.project, self.run, self.token())))
            (self.run / "state.json").write_bytes(original)


class IndependenceTests(Base):
    """A7: earlier builders and 05_verify remediation writers cannot verify their own work."""

    def test_an_earlier_builder_stays_ineligible_after_reopen_and_reassignment(self) -> None:
        team.add_task(self.project, self.run, task_args("A", "backend-engineer"))
        team.claim_task(self.project, self.run, "A", "backend-engineer", 60)
        team.reopen_task(self.project, self.run, "A", "handing over")
        team.reassign_task(self.project, self.run, "A", "fullstack-engineer", "capacity")
        team.claim_task(self.project, self.run, "A", "fullstack-engineer", 60)
        team.complete_task(self.project, self.run, "A", "fullstack-engineer", ["note:built"])
        team.add_task(self.project, self.run, task_args("V", "backend-engineer", verifies=["A"], action="test", path=["tests/v"]))
        with self.assertRaises(team.TeamError) as raised:
            team.claim_task(self.project, self.run, "V", "backend-engineer", 60)
        self.assertIn("independent", str(raised.exception))
        team.reassign_task(self.project, self.run, "V", "qa-lead", "independent reviewer")
        team.claim_task(self.project, self.run, "V", "qa-lead", 60)

    def test_a_remediation_writer_cannot_be_the_final_verifier(self) -> None:
        team.add_task(self.project, self.run, task_args("A", "backend-engineer"))
        team.claim_task(self.project, self.run, "A", "backend-engineer", 60)
        team.complete_task(self.project, self.run, "A", "backend-engineer", ["note:built"])
        self.assertEqual(team.advance_stage(self.project, self.run), "05_verify")
        team.add_task(self.project, self.run, task_args("FIX", "fullstack-engineer", stage="05_verify", path=["src/fix"]))
        team.claim_task(self.project, self.run, "FIX", "fullstack-engineer", 60)
        team.complete_task(self.project, self.run, "FIX", "fullstack-engineer", ["note:remediated"])
        (self.run / "VERIFICATION.md").write_text(PASS_HEADER.format(verifier="fullstack-engineer"), encoding="utf-8")
        with self.assertRaises(team.TeamError) as raised:
            team.advance_stage(self.project, self.run)
        self.assertIn("independent", str(raised.exception))
        (self.run / "VERIFICATION.md").write_text(PASS_HEADER.format(verifier="qa-lead"), encoding="utf-8")
        self.assertEqual(team.advance_stage(self.project, self.run), "06_release")


if __name__ == "__main__":
    unittest.main()
