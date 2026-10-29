"""The durable supervisor: intake, store, launch recovery, checkout safety, authority, metering, lifecycle,
human interaction, evidence, packaging, operations, and GitHub polling (docs/supervisor-progress.md).

Every worker is the scripted fake worker driving the installed CLI; no test calls a model or the network.
"""

from __future__ import annotations

import errno
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

from helpers import ROOT, TEST_HOME, fresh_project, run_cli, team
from supervisor_fixtures import FAKE_WORKER, SupervisorBase, fast_config, git, git_project, scratch, sup


def kill(pid: int) -> None:
    try:
        os.kill(pid, signal.SIGTERM)
    except (OSError, ProcessLookupError):
        pass


def sleeper() -> subprocess.Popen:
    return subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])


class IntakeTests(SupervisorBase):
    def setUp(self) -> None:
        super().setUp()
        self.sup.pause(None, "intake tests launch nothing")

    def test_duplicate_event_is_harmless(self) -> None:
        self.assertEqual(self.enqueue(), "fix-1")
        self.assertEqual(self.sup.enqueue({"id": "fix-1", "kind": "manual", "title": "Fix fix-1", "brief": "Make feature() return 42.",
                                           "acceptance": ["AC-1: feature() returns 42"]})[0], "duplicate")
        self.sup.tick()
        self.assertEqual(self.sup.enqueue({"id": "fix-1", "kind": "manual", "title": "Fix fix-1", "brief": "Make feature() return 42.",
                                           "acceptance": ["AC-1: feature() returns 42"]})[0], "duplicate")
        jobs, problems = self.sup.store.jobs()
        self.assertEqual(([job["id"] for job in jobs], problems), (["fix-1"], []))
        self.assertEqual(list(self.sup.store.inbox.glob("*.json")), [])

    def test_conflicting_payload_is_reported(self) -> None:
        self.enqueue()
        with self.assertRaises(sup.SupervisorError) as raised:
            self.enqueue(brief="Something else entirely")
        self.assertIn("different event", str(raised.exception))
        self.sup.tick()
        with self.assertRaises(sup.SupervisorError) as raised:
            self.enqueue("other-id", source_key="manual:fix-1", brief="A different request")
        self.assertIn("different payload", str(raised.exception))
        dropped = sup.validate_event({"id": "fix-1-copy", "kind": "manual", "title": "Changed", "source_key": "manual:fix-1"})
        (self.sup.store.inbox / "dropped.json").write_text(json.dumps(dropped), encoding="utf-8")
        self.sup.tick()
        reasons = [path.read_text(encoding="utf-8") for path in self.sup.store.quarantine.glob("*.reason")]
        self.assertTrue(any("conflict" in reason for reason in reasons), reasons)
        self.assertEqual(self.job()["event"]["brief"], "Make feature() return 42.", "the accepted job is never replaced")

    def test_concurrent_enqueue_accepts_one_job(self) -> None:
        outcomes: list[str] = []
        errors: list[Exception] = []

        def submit() -> None:
            try:
                outcomes.append(sup.Supervisor(self.project).enqueue({"id": "race", "kind": "alert", "title": "Disk alert", "brief": "Disk at 91%"})[0])
            except Exception as exc:  # noqa: BLE001 - the test reports any failure
                errors.append(exc)

        threads = [threading.Thread(target=submit) for _ in range(6)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        self.assertEqual(sorted(outcomes), ["duplicate"] * 5 + ["queued"])
        self.sup.tick()
        self.assertEqual([job["id"] for job in self.sup.store.jobs()[0]], ["race"])

    def test_unsafe_ids_are_refused(self) -> None:
        for bad in ("../escape", "/abs/path", "C:\\win", "con", "NUL", "aux.txt", "a/b", "Upper", "", "x" * 81, "a..b"):
            with self.subTest(bad=bad), self.assertRaises(sup.EventError):
                sup.validate_event({"id": bad, "kind": "manual", "title": "t"})
        outside = self.sup.store.root.parent / "escape.json"
        (self.sup.store.inbox / "evil.json").write_text(json.dumps({"id": "../escape", "kind": "manual", "title": "t"}), encoding="utf-8")
        self.sup.tick()
        self.assertFalse(outside.exists())
        self.assertEqual(self.sup.store.jobs()[0], [])
        self.assertEqual(len(list(self.sup.store.quarantine.glob("*.reason"))), 1)

    def test_malformed_and_oversized_events_are_quarantined(self) -> None:
        inbox = self.sup.store.inbox
        (inbox / "torn.json").write_text('{"id": "torn", "kind": ', encoding="utf-8")
        (inbox / "huge.json").write_text(json.dumps({"id": "huge", "kind": "manual", "title": "t", "brief": "x" * 70000}), encoding="utf-8")
        (inbox / "extra.json").write_text(json.dumps({"id": "extra", "kind": "manual", "title": "t", "command": "rm -rf /"}), encoding="utf-8")
        (inbox / "kind.json").write_text(json.dumps({"id": "kind", "kind": "deploy", "title": "t"}), encoding="utf-8")
        self.enqueue("healthy")
        self.sup.tick()
        self.assertEqual([job["id"] for job in self.sup.store.jobs()[0]], ["healthy"], "bad events never block healthy intake")
        self.assertEqual(len(list(self.sup.store.quarantine.glob("*.reason"))), 4)
        self.assertEqual(list(inbox.glob("*.json")), [])

    def test_crash_between_job_record_and_inbox_removal(self) -> None:
        self.enqueue()
        waiting = (self.sup.store.inbox / "fix-1.json").read_text(encoding="utf-8")
        self.sup.tick()
        (self.sup.store.inbox / "fix-1.json").write_text(waiting, encoding="utf-8")  # the removal "never happened"
        self.sup.tick()
        self.assertEqual(len(self.sup.store.jobs()[0]), 1)
        self.assertFalse((self.sup.store.inbox / "fix-1.json").exists())
        index = self.sup.store.source_index("manual:fix-1")
        index.unlink()  # crash after the job record, before the index
        (self.sup.store.inbox / "fix-1.json").write_text(waiting, encoding="utf-8")
        self.sup.tick()
        self.assertTrue(index.is_file())
        self.assertEqual(len(self.sup.store.jobs()[0]), 1)


class StoreTests(SupervisorBase):
    def test_torn_record_blocks_launches(self) -> None:
        self.sup.pause(None, "set up")
        self.enqueue()
        self.sup.tick()
        (self.sup.store.jobs_dir / "broken.json").write_text('{"schema": 1, "id": "bro', encoding="utf-8")
        self.sup.resume(None)
        digest = self.sup.tick()
        self.assertEqual(digest["exit_code"], sup.EXIT_BLOCKED)
        self.assertTrue(any("broken.json" in item for item in digest["blockers"]), digest["blockers"])
        self.assertEqual(self.job()["status"], "queued", "nothing launches while a record is unreadable")
        self.enqueue("still-accepted")
        self.sup.tick()
        self.assertIn("still-accepted", [job["id"] for job in self.sup.store.jobs()[0]])
        self.assertEqual(self.sup.status()["exit_code"], sup.EXIT_BLOCKED)

    def test_lock_contention_is_blocked(self) -> None:
        other = sup.Supervisor(self.project)
        other.store.lock_timeout = 0.3
        with self.sup.store.lock():
            with self.assertRaises(sup.Blocked) as raised:
                other.tick()
            self.assertIn("locked", str(raised.exception))
        # Another process holds it; when that process dies, the OS releases it (no stale lock to break).
        holder = subprocess.Popen([sys.executable, "-c", (
            "import sys, time; from pathlib import Path; sys.path.insert(0, sys.argv[1]); import agentic_supervisor as s; "
            "store = s.Store(Path(sys.argv[2]), Path(sys.argv[3])); lock = store.lock(); lock.__enter__(); print('locked', flush=True); time.sleep(120)"),
            str(ROOT / "scripts"), str(self.project), str(self.sup.store.root)], stdout=subprocess.PIPE, text=True)
        self.addCleanup(holder.kill)
        self.assertEqual(holder.stdout.readline().strip(), "locked")
        with self.assertRaises(sup.Blocked):
            other.tick()
        holder.kill()
        holder.wait()
        other.tick()  # acquired at once

    def test_schema_mismatch_refuses_launches(self) -> None:
        self.enqueue()
        control = json.loads(self.sup.store.control_path.read_text(encoding="utf-8"))
        control["schema"] = 99
        self.sup.store.control_path.write_text(json.dumps(control), encoding="utf-8")
        with self.assertRaises(sup.Blocked):
            self.sup.tick()
        self.assertEqual(sup.main(["serve", "--once", "--project", str(self.project)]), sup.EXIT_BLOCKED)
        self.assertFalse(any(self.sup.store.attempts.glob("*/*")))

    def test_log_failure_keeps_the_transition(self) -> None:
        self.sup.pause(None, "set up")
        self.sup.store.log_path.unlink(missing_ok=True)
        self.sup.store.log_path.mkdir()
        self.enqueue()
        digest = self.sup.tick()
        self.assertEqual(self.job()["status"], "queued")
        self.assertGreater(digest["log_failures"], 0)

    def test_disk_full_stops_launches(self) -> None:
        self.enqueue()

        def always_full(path: Path, data: bytes) -> None:
            raise OSError(errno.ENOSPC, "No space left on device")

        with mock.patch.object(sup, "_write_bytes", always_full):
            with self.assertRaises(sup.Blocked) as raised:
                self.sup.tick()
        self.assertIn("disk is full", str(raised.exception))
        self.assertFalse(any(self.sup.store.attempts.glob("*/*/intent.json")))
        self.until_idle()
        self.assertEqual(self.job()["status"], "done", "after space returns the job runs normally")


class LaunchRecoveryTests(SupervisorBase):
    def test_crash_before_spawn_abandons_the_attempt(self) -> None:
        self.sup.configure(start_grace_seconds=0.3)
        self.enqueue()
        with mock.patch.object(sup, "spawn_detached", side_effect=OSError("simulated crash before spawn")):
            self.sup.tick()
        self.assertEqual(self.job()["status"], "starting")
        time.sleep(0.5)
        self.sup.tick()
        job = self.job()
        first = job["attempts"][0]
        self.assertEqual((first["status"], first["usage"]["state"]), ("abandoned", "not-started"))
        claim = json.loads((self.attempt_dir(index=0) / "claim").read_text(encoding="utf-8"))
        self.assertEqual(claim["by"], "supervisor")
        self.until_idle()
        job = self.job()
        self.assertEqual(job["status"], "done")
        self.assertEqual(len(job["attempts"]), 2)
        self.assertEqual(job["worker_retries"], 0, "a launch that never started is not a worker failure")

    def test_crash_after_spawn_adopts_the_wrapper(self) -> None:
        self.enqueue()
        self.sup.tick()
        job = self.job()
        job["attempts"][-1].pop("wrapper_pid", None)  # the parent died before saving the pid
        self.sup.store.save_job(job)
        fresh = sup.Supervisor(self.project)
        self.assertEqual(fresh.serve("until-idle", max_seconds=120), sup.EXIT_OK)
        job = self.job()
        self.assertEqual((job["status"], len(job["attempts"])), ("done", 1))

    def test_late_wrapper_cannot_claim_an_abandoned_attempt(self) -> None:
        self.sup.configure(start_grace_seconds=0.3)
        self.enqueue()
        with mock.patch.object(sup, "spawn_detached", side_effect=OSError("wrapper never ran")):
            self.sup.tick()
        time.sleep(0.5)
        self.sup.tick()
        folder = self.attempt_dir(index=0)
        self.assertEqual(sup.run_wrapper(folder), sup.EXIT_OK)  # a wrapper that wakes up too late
        self.assertFalse((folder / "start.json").exists())
        self.assertFalse((folder / "stdout.jsonl").exists(), "no worker ever started for the abandoned attempt")

    def test_exit_receipt_is_reconciled_once(self) -> None:
        self.mode("crash-once cost=0.05")
        self.enqueue()
        self.sup.tick()
        self.assertTrue(self.wait_for(lambda: (self.attempt_dir() / "exit.json").exists()))
        with mock.patch.object(sup.Supervisor, "classify", side_effect=RuntimeError("supervisor died mid-finalize")):
            with self.assertRaises(RuntimeError):
                self.sup.tick()
        fresh = sup.Supervisor(self.project)
        fresh.serve("until-idle", max_seconds=120)
        job = self.job()
        self.assertEqual(job["status"], "done")
        state = self.run_state()
        self.assertEqual(len(state["usage_sources"]), 2, "one record per attempt, never two for one transcript")
        failures = state["tasks"]["T1"].get("failures", [])
        self.assertEqual([item["signature"] for item in failures], [sup.FAIL_SIGNATURE], "the abandoned claim was recorded once")
        self.assertAlmostEqual(fresh.status()["allowance"]["usd_spent"], 0.10)

    def start_holding(self) -> dict:
        self.mode("claim-and-hang")
        self.enqueue()
        self.sup.tick()
        self.assertTrue(self.wait_for(lambda: (self.attempt_dir() / "worker.json").exists()))
        self.assertTrue(self.wait_for(lambda: self.run_state().get("tasks", {}).get("T1", {}).get("status") == "claimed", 60))
        self.sup.tick()
        self.assertEqual(self.job()["status"], "running")
        folder = self.attempt_dir()
        return {"start": json.loads((folder / "start.json").read_text(encoding="utf-8")),
                "worker": json.loads((folder / "worker.json").read_text(encoding="utf-8")), "folder": folder}

    def test_dead_wrapper_without_receipt_is_a_lost_attempt(self) -> None:
        held = self.start_holding()
        kill(held["worker"]["pid"])
        kill(held["start"]["pid"])
        self.assertTrue(self.wait_for(lambda: self.gone(held["start"]["pid"]) and self.gone(held["worker"]["pid"])))
        os.utime(held["folder"] / "heartbeat", (time.time() - 60, time.time() - 60))
        self.sup.tick()
        job = self.job()
        attempt = job["attempts"][-1]
        self.assertFalse((held["folder"] / "exit.json").exists())
        self.assertEqual(attempt["end_reason"], "wrapper-lost")
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "unknown-usage"), "a lost attempt's cost is unknown")
        self.assertEqual(self.run_state()["tasks"]["T1"]["status"], "ready", "the lost attempt's claim was recorded as a failure")
        self.mode("success")
        self.sup.resume("fix-1", charge_reservation=True)
        self.until_idle()
        self.assertEqual(self.job()["status"], "done")
        self.assertAlmostEqual(self.sup.status()["allowance"]["usd_spent"], 1.01)

    def test_reused_pid_holds_instead_of_relaunching(self) -> None:
        held = self.start_holding()
        kill(held["worker"]["pid"])
        kill(held["start"]["pid"])
        self.assertTrue(self.wait_for(lambda: self.gone(held["start"]["pid"]) and self.gone(held["worker"]["pid"])))
        stranger = sleeper()
        self.addCleanup(stranger.kill)
        start = dict(held["start"], pid=stranger.pid, identity=None)  # a live PID whose identity cannot be shown
        (held["folder"] / "start.json").write_text(json.dumps(start), encoding="utf-8")
        os.utime(held["folder"] / "heartbeat", (time.time() - 60, time.time() - 60))
        self.sup.tick()
        job = self.job()
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "ownership"))
        self.assertEqual(len(job["attempts"]), 1, "no replacement worker was launched")
        self.assertIsNone(stranger.poll(), "an unrelated process is never killed")
        start["identity"] = "win:1" if os.name == "nt" else "linux:1"  # now a known mismatch: the PID was reused
        self.assertEqual(sup.ownership(stranger.pid, start["identity"]), "dead")

    def test_a_reused_pid_with_another_identity_is_a_lost_attempt(self) -> None:
        held = self.start_holding()
        kill(held["worker"]["pid"])
        kill(held["start"]["pid"])
        self.assertTrue(self.wait_for(lambda: self.gone(held["start"]["pid"]) and self.gone(held["worker"]["pid"])))
        stranger = sleeper()
        self.addCleanup(stranger.kill)
        start = dict(held["start"], pid=stranger.pid, identity="win:1" if os.name == "nt" else "linux:1")
        (held["folder"] / "start.json").write_text(json.dumps(start), encoding="utf-8")
        os.utime(held["folder"] / "heartbeat", (time.time() - 60, time.time() - 60))
        self.sup.tick()
        job = self.job()
        self.assertEqual(job["attempts"][-1]["end_reason"], "wrapper-lost", "the PID belongs to another process now")
        self.assertEqual(job["hold"]["kind"], "unknown-usage")
        self.assertIsNone(stranger.poll(), "the process that reused the PID is never touched")

    def test_worker_outliving_its_wrapper_holds(self) -> None:
        held = self.start_holding()
        kill(held["worker"]["pid"])
        kill(held["start"]["pid"])
        self.assertTrue(self.wait_for(lambda: self.gone(held["start"]["pid"]) and self.gone(held["worker"]["pid"])))
        survivor = sleeper()
        self.addCleanup(survivor.kill)
        worker = {"pid": survivor.pid, "identity": sup.process_identity(survivor.pid), "tree": "test", "time": sup.now_iso()}
        (held["folder"] / "worker.json").write_text(json.dumps(worker), encoding="utf-8")
        os.utime(held["folder"] / "heartbeat", (time.time() - 60, time.time() - 60))
        self.sup.tick()
        job = self.job()
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "ownership"))
        self.assertEqual(self.run_state()["tasks"]["T1"]["status"], "claimed", "no lease is released while the old writer may act")
        with self.assertRaises(sup.SupervisorError) as raised:
            self.sup.resume("fix-1", confirm_stopped=True)
        self.assertIn("still running", str(raised.exception))
        self.assertIsNone(survivor.poll(), "the supervisor never kills it")
        survivor.kill()
        survivor.wait()
        with self.assertRaises(sup.SupervisorError):
            self.sup.resume("fix-1", confirm_stopped=True)  # now it proceeds, and the unknown cost holds it again
        self.assertEqual(self.job()["hold"]["kind"], "unknown-usage")
        self.assertEqual(self.run_state()["tasks"]["T1"]["status"], "ready")

    def test_two_supervisors_never_launch_twice(self) -> None:
        self.enqueue()
        errors: list[Exception] = []

        def spin() -> None:
            local = sup.Supervisor(self.project)
            for _ in range(15):
                try:
                    local.tick()
                except sup.Blocked:
                    pass
                except Exception as exc:  # noqa: BLE001
                    errors.append(exc)
                time.sleep(0.05)

        threads = [threading.Thread(target=spin) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        self.until_idle()
        job = self.job()
        self.assertEqual((job["status"], len(job["attempts"])), ("done", 1))

    def test_fresh_supervisor_reconciles_a_detached_worker(self) -> None:
        self.mode("slow sleep=2")
        self.enqueue()
        self.sup.tick()
        del self.sup  # the supervisor process is gone; the wrapper and worker are not
        restarted = sup.Supervisor(self.project)
        self.assertEqual(restarted._spawned, {})
        self.assertEqual(restarted.serve("until-idle", max_seconds=120), sup.EXIT_OK)
        self.sup = restarted
        self.assertEqual(self.job()["status"], "done")

    def test_live_writer_keeps_its_claims(self) -> None:
        held = self.start_holding()
        for _ in range(3):
            self.sup.tick()
            time.sleep(0.3)
        state = self.run_state()
        self.assertEqual(state["tasks"]["T1"]["status"], "claimed")
        self.assertFalse(state["tasks"]["T1"].get("failures"))
        self.assertFalse(any(event["type"] == "lease-recovered" for event in team.read_events(self.run_dir())))
        self.sup.cancel("fix-1", "end the test")
        self.assertTrue(self.wait_for(lambda: (held["folder"] / "exit.json").exists()))
        self.sup.tick()
        self.assertEqual(self.job()["status"], "cancelled")
        self.assertEqual(len(self.run_state()["tasks"]["T1"]["failures"]), 1)


class CheckoutTests(SupervisorBase):
    def test_dirty_tree_blocks_the_first_launch(self) -> None:
        (self.project / "notes.txt").write_text("my work in progress\n", encoding="utf-8")
        (self.project / ".gitignore").write_text((self.project / ".gitignore").read_text(encoding="utf-8") + "# edited\n", encoding="utf-8")
        self.enqueue()
        digest = self.sup.tick()
        self.assertEqual(digest["exit_code"], sup.EXIT_BLOCKED)
        self.assertTrue(any("uncommitted changes" in item and "notes.txt" in item for item in digest["blockers"]), digest["blockers"])
        self.assertEqual((self.job()["status"], self.job()["run_id"]), ("queued", None))
        self.assertEqual((self.project / "notes.txt").read_text(encoding="utf-8"), "my work in progress\n", "the supervisor never cleans")
        self.assertIn("# edited", (self.project / ".gitignore").read_text(encoding="utf-8"))
        git(self.project, "add", "-A")
        git(self.project, "commit", "-q", "-m", "owner work")
        self.until_idle()
        self.assertEqual(self.job()["status"], "done")

    def test_unrelated_active_run_blocks_launch(self) -> None:
        manual = team.init_run(self.project, "By hand", "by-hand", "autonomous", "execute-only", "adaptive")
        self.enqueue()
        digest = self.sup.tick()
        self.assertTrue(any("unrelated run by-hand" in item for item in digest["blockers"]), digest["blockers"])
        team.close_run(self.project, manual, "the supervisor takes over")
        self.until_idle()
        self.assertEqual(self.job()["status"], "done")

    def test_held_job_keeps_the_checkout(self) -> None:
        self.mode("r3")
        self.enqueue("held")
        self.until_idle()
        self.assertEqual(self.job("held")["status"], "needs-human")
        self.mode("success")
        self.enqueue("next")
        digest = self.sup.tick()
        self.assertEqual(self.job("next")["status"], "queued")
        self.assertTrue(any("reserved by job held" in item for item in digest["blockers"]), digest["blockers"])
        self.sup.pause("held", "owner is reviewing")
        self.sup.tick()
        self.assertEqual(self.sup.store.control()["checkout"]["job"], "held", "a paused, held job keeps the checkout")
        self.sup.cancel("held", "not shipping to production today")
        self.until_idle()
        self.assertEqual(self.job("next")["status"], "done")

    def test_parallel_workers_are_refused(self) -> None:
        with self.assertRaises(sup.UsageProblem) as raised:
            self.sup.configure(max_workers=2)
        self.assertIn("one writer per checkout", str(raised.exception))
        self.assertEqual(sup.main(["configure", "--project", str(self.project), "--max-workers", "3"]), sup.EXIT_USAGE)

    def test_current_run_pointer_change_holds(self) -> None:
        self.mode("stop-after-build")
        self.sup.configure(backoff_seconds=30.0, backoff_max_seconds=30.0)
        self.enqueue()
        self.sup.tick()
        self.assertTrue(self.wait_for(lambda: (self.attempt_dir() / "exit.json").exists()))
        self.sup.tick()
        self.assertEqual(self.job()["status"], "retrying")
        team.switch_run(self.project, "sup-fix-1")  # no-op, then a real move:
        other = team.init_run(self.project, "Elsewhere", "elsewhere", "hitl", "execute-only", "adaptive")
        self.assertEqual(team.current_run_id(self.project / ".agentic-team"), other.name)
        job = self.job()
        job["next_attempt_after"] = sup.now_iso()
        self.sup.store.save_job(job)
        self.sup.tick()
        job = self.job()
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "pointer"))
        self.assertEqual(len(job["attempts"]), 1)


class AuthorityTests(SupervisorBase):
    def test_worker_gets_a_scratch_home_and_a_view(self) -> None:
        with mock.patch.dict(os.environ, {"GH_TOKEN": "ghp_not_for_workers"}):
            self.enqueue()
            self.until_idle()
        self.assertEqual(self.job()["status"], "done")
        env = next(item for item in self.transcript_lines() if item.get("subtype") == "fake-env")
        self.assertEqual(Path(env["home"]), self.sup.store.root / "worker-home")
        self.assertNotEqual(Path(env["home"]).resolve(), TEST_HOME.resolve())
        self.assertFalse(env["home_has_tokens"])
        self.assertEqual(Path(env["view"]), self.sup.store.root / "view")
        self.assertFalse(env["gh_token_visible"], "unrelated credentials are filtered out")
        intent = json.loads((self.attempt_dir() / "intent.json").read_text(encoding="utf-8"))
        self.assertNotIn("GH_TOKEN", intent["env_names"])
        self.assertNotIn("ghp_not_for_workers", json.dumps(intent))
        # Without a boundary the same OS user reads the owner store, so paid launches are refused.
        self.sup.configure(isolation={"python": sys.executable})
        result = self.sup.verify_isolation()
        self.assertFalse(result["verified"])
        self.sup.configure(adapter="claude", executable=[sys.executable, "-c", "print('--help')"])
        self.enqueue("paid")
        self.until_idle()
        job = self.job("paid")
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "config"))
        self.assertIn("isolation boundary", job["hold"]["reason"])
        self.assertIsNone(job["run_id"], "nothing was spent or created")


class LifecycleTests(SupervisorBase):
    def test_job_runs_to_done_with_metered_usage(self) -> None:
        self.enqueue()
        self.assertEqual(self.until_idle(), sup.EXIT_OK)
        job = self.job()
        self.assertEqual(job["status"], "done")
        attempt = job["attempts"][0]
        self.assertEqual((attempt["usage"]["state"], attempt["usage"]["usd"]), ("metered", 0.01))
        state = self.run_state()
        self.assertEqual((state["status"], state["usage_metered"]["usd"]), ("complete", 0.01))
        self.assertEqual(state["usage_sources"][0]["sha256"], attempt["usage"]["sha256"])
        self.assertTrue(any(event["type"] == "release-conditions-met" for event in team.read_events(self.run_dir())))
        self.assertIn("AC-1: feature() returns 42", (self.run_dir() / "BRIEF.md").read_text(encoding="utf-8"))
        status = self.sup.status()
        self.assertEqual((status["checkout"]["job"], status["allowance"]["usd_spent"], status["allowance"]["usd_reserved"]), (None, 0.01, 0))
        self.assertIn("| `fix-1` | manual | done |", self.sup.store.status_md.read_text(encoding="utf-8"))
        receipt = json.loads((self.attempt_dir() / "exit.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["stdout_sha256"], attempt["usage"]["sha256"])

    def test_known_cost_crash_is_retried_and_finishes(self) -> None:
        self.mode("crash-once cost=0.05")
        self.enqueue()
        self.until_idle()
        job = self.job()
        self.assertEqual((job["status"], len(job["attempts"]), job["worker_retries"]), ("done", 2, 1))
        self.assertEqual(job["attempts"][0]["exit_code"], 3)
        self.assertEqual(job["attempts"][0]["failures_recorded"], ["T1"])
        failures = self.run_state()["tasks"]["T1"]["failures"]
        self.assertEqual([item["signature"] for item in failures], [sup.FAIL_SIGNATURE])
        self.assertAlmostEqual(self.sup.status()["allowance"]["usd_spent"], 0.10)

    def test_repeated_failure_holds_until_the_human_reopens(self) -> None:
        self.mode("repeated-failure")
        self.enqueue()
        self.assertEqual(self.until_idle(), sup.EXIT_HUMAN)
        job = self.job()
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "failed-task"))
        self.assertEqual(self.run_state()["status"], "active", "autonomous profiles keep the run active; the job still holds")
        with self.assertRaises(sup.SupervisorError):
            self.sup.resume("fix-1")  # nothing changed: still failed
        team.reopen_task(self.project, self.run_dir(), "T1", "try again with more retries", "Owner", self.token(), 1)
        self.sup.resume("fix-1")
        self.until_idle()
        job = self.job()
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "failed-task"), "the same failure again: only the human decides")
        self.assertEqual(len(job["attempts"]), 2)


class MeteringTests(SupervisorBase):
    def test_missing_usage_holds_and_keeps_the_reservation(self) -> None:
        self.mode("missing-usage")
        self.enqueue()
        self.assertEqual(self.until_idle(), sup.EXIT_HUMAN)
        job = self.job()
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "unknown-usage"))
        self.assertEqual(self.run_state()["status"], "complete")
        self.assertEqual(self.sup.status()["allowance"]["usd_reserved"], 1.0, "the reservation stays counted")
        with self.assertRaises(sup.SupervisorError) as raised:
            self.sup.resume("fix-1")
        self.assertIn("--charge-reservation", str(raised.exception))
        self.assertEqual(self.sup.resume("fix-1", charge_reservation=True), "job fix-1 is done")
        status = self.sup.status()
        self.assertEqual((status["allowance"]["usd_spent"], status["allowance"]["usd_reserved"]), (1.0, 0))

    def test_malformed_result_holds(self) -> None:
        self.mode("malformed")
        self.enqueue()
        self.until_idle()
        self.assertEqual(self.job()["hold"]["kind"], "unknown-usage")
        recovered = Path(tempfile.mkdtemp(prefix="recovered-")) / "session.jsonl"
        self.addCleanup(shutil.rmtree, str(recovered.parent), True)
        recovered.write_text(json.dumps({"type": "result", "total_cost_usd": 0.2, "usage": {"output_tokens": 9}}) + "\n", encoding="utf-8")
        self.assertEqual(self.sup.resume("fix-1", usage_transcript=recovered), "job fix-1 is done")
        self.assertEqual(self.run_state()["usage_metered"]["usd"], 0.2)

    def test_metering_is_idempotent_after_a_crash(self) -> None:
        self.enqueue()
        self.sup.tick()
        self.assertTrue(self.wait_for(lambda: (self.attempt_dir() / "exit.json").exists(), 60))
        real = sup.Supervisor.cli

        def crash_after_usage(instance, *args):
            result = real(instance, *args)
            if args and args[0] == "usage":
                raise RuntimeError("supervisor died right after the usage command")
            return result

        with mock.patch.object(sup.Supervisor, "cli", crash_after_usage):
            with self.assertRaises(RuntimeError):
                self.sup.tick()
        self.assertEqual(self.job()["attempts"][0]["usage"]["state"], "pending")
        sup.Supervisor(self.project).serve("until-idle", max_seconds=60)
        state = self.run_state()
        self.assertEqual(len(state["usage_sources"]), 1)
        self.assertEqual(sum(1 for record in team.read_ledger(team.home_key(state)) if record["action"] == "usage"), 1)
        self.assertEqual((self.job()["status"], self.sup.status()["allowance"]["usd_spent"]), ("done", 0.01))

    def test_over_budget_ingestion_still_counts(self) -> None:
        self.sup.configure(run_budget={"usd": 0.5}, attempt_usd=0.5)
        self.mode("success cost=0.6")
        self.enqueue()
        self.until_idle()
        job = self.job()
        self.assertEqual(job["attempts"][0]["usage"]["note"], "the run crossed its ceiling")
        self.assertEqual(self.run_state()["usage_metered"]["usd"], 0.6, "exit 3 from usage still saved the spend")
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "budget"))
        self.assertEqual(self.sup.status()["allowance"]["usd_spent"], 0.6)

    def test_final_budget_checkpoint_keeps_a_complete_run_from_done(self) -> None:
        self.sup.configure(run_budget={"usd": 1.0}, attempt_usd=1.0)
        self.mode("success cost=0.9")
        self.enqueue()
        self.until_idle()
        job = self.job()
        state = self.run_state()
        self.assertEqual(state["status"], "complete")
        budget = [item for item in state["checkpoints"] if item["kind"] == "budget"]
        self.assertEqual(len(budget), 1)
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "checkpoint"))
        team.approve_checkpoint(self.project, self.run_dir(), budget[0]["id"], "Owner", "within reason", self.token())
        self.assertEqual(self.sup.resume("fix-1"), "job fix-1 is done")


class HumanTests(SupervisorBase):
    def test_r2_work_pauses_at_release_and_resumes_after_approval(self) -> None:
        self.mode("r2")
        self.enqueue()
        self.assertEqual(self.until_idle(), sup.EXIT_HUMAN)
        job = self.job()
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "checkpoint"))
        state = self.run_state()
        stage = next(item for item in state["checkpoints"] if item["kind"] == "stage" and item["status"] == "pending")
        self.assertIn("MIG", stage["recommendation"])
        self.assertEqual(sup.main(["status", "--project", str(self.project)]), sup.EXIT_HUMAN)
        self.assertIn("approve --checkpoint", self.sup.status()["jobs"][0]["next_action"])
        team.approve_checkpoint(self.project, self.run_dir(), stage["id"], "Owner", "migration reviewed", self.token())
        self.sup.resume("fix-1")
        self.until_idle()
        job = self.job()
        self.assertEqual((job["status"], len(job["attempts"])), ("done", 2))

    def test_r3_action_holds_for_the_human(self) -> None:
        self.mode("r3")
        self.enqueue()
        self.until_idle()
        job = self.job()
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "checkpoint"))
        self.assertIn("SHIP", job["hold"]["reason"])
        state = self.run_state()
        self.assertTrue(any(item["kind"] == "risk" and item["task"] == "SHIP" and item["status"] == "pending" for item in state["checkpoints"]))
        self.assertNotEqual(state["tasks"]["SHIP"]["status"], "claimed")

    def test_rejection_stays_held(self) -> None:
        self.sup.configure(autonomy="autonomous")
        self.enqueue()
        self.until_idle()
        stage = next(item for item in self.run_state()["checkpoints"] if item["kind"] == "stage" and item["status"] == "pending")
        team.reject_checkpoint(self.project, self.run_dir(), stage["id"], "Owner", "not this week", self.token())
        with self.assertRaises(sup.SupervisorError) as raised:
            self.sup.resume("fix-1")
        self.assertIn("rejected", str(raised.exception))
        self.assertEqual(self.job()["status"], "needs-human")

    def test_cancel_stops_the_owned_worker_and_keeps_changes(self) -> None:
        bystander = sleeper()
        self.addCleanup(bystander.kill)
        self.mode("claim-and-hang")
        self.enqueue()
        self.sup.tick()
        folder = self.attempt_dir()
        self.assertTrue(self.wait_for(lambda: (folder / "worker.json").exists()))
        self.assertTrue(self.wait_for(lambda: (self.project / "src").is_dir() and any((self.project / "src").glob("feature_*.py")), 60))
        worker = json.loads((folder / "worker.json").read_text(encoding="utf-8"))
        self.assertIn("cancel requested", self.sup.cancel("fix-1", "wrong priority"))
        self.assertTrue(self.wait_for(lambda: (folder / "exit.json").exists(), 30))
        self.assertEqual(json.loads((folder / "exit.json").read_text(encoding="utf-8"))["reason"], "cancelled")
        self.assertTrue(self.wait_for(lambda: not sup.process_alive(worker["pid"]), 15), "the wrapper ended its own worker")
        self.sup.tick()
        self.assertEqual(self.job()["status"], "cancelled")
        self.assertIsNone(bystander.poll(), "nothing else was touched")
        self.assertTrue(any((self.project / "src").glob("feature_*.py")), "the worker's changes are kept")
        self.assertEqual(self.sup.store.control()["checkout"]["job"], "fix-1", "uncommitted changes keep the checkout reserved")
        self.sup.release("fix-1", "kept the draft on a branch")
        self.assertIsNone(self.sup.store.control()["checkout"]["job"])


class EvidenceTests(SupervisorBase):
    def finish_with(self, mode: str, retries: int = 0) -> dict:
        self.sup.configure(retries=retries)
        self.mode(mode)
        self.enqueue()
        self.until_idle()
        return self.job()

    def test_failing_verdict_is_not_done(self) -> None:
        job = self.finish_with("verdict-fail")
        self.assertEqual(job["status"], "failed")
        self.assertEqual(self.run_state()["stage"], "05_verify")

    def test_commit_after_verification_is_not_done(self) -> None:
        job = self.finish_with("commit-after-verify")
        self.assertEqual(job["status"], "failed")
        self.assertEqual(self.run_state()["stage"], "06_release", "verified-head kept the release stage closed")

    def test_change_after_verification_holds(self) -> None:
        job = self.finish_with("dirty-after-verify")
        self.assertEqual(self.run_state()["status"], "complete")
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "source"))
        self.assertIn("stray_", job["hold"]["reason"])
        for stray in (self.project / "src").glob("stray_*.txt"):
            stray.unlink()
        self.assertEqual(self.sup.resume("fix-1"), "job fix-1 is done")

    def test_missing_rollback_rehearsal_is_not_done(self) -> None:
        job = self.finish_with("no-rollback")
        self.assertEqual((job["status"], self.run_state()["stage"]), ("failed", "06_release"))

    def test_missing_delivery_report_is_not_done(self) -> None:
        job = self.finish_with("no-report")
        self.assertEqual((job["status"], self.run_state()["stage"]), ("failed", "07_learn"))

    def test_zero_exit_with_an_incomplete_run_retries(self) -> None:
        job = self.finish_with("stop-after-build", retries=1)
        self.assertEqual((job["status"], len(job["attempts"]), job["worker_retries"]), ("failed", 2, 1))
        self.assertEqual([attempt["exit_code"] for attempt in job["attempts"]], [0, 0])


class TamperTests(SupervisorBase):
    autonomy = "autonomous"

    def test_forged_state_approval_holds_as_tamper(self) -> None:
        self.mode("forge")
        self.enqueue()
        self.until_idle()
        job = self.job()
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "tamper"))
        self.assertIn("no signed approval", job["hold"]["reason"])

    def test_self_approval_is_refused_and_held(self) -> None:
        self.mode("self-approve")
        self.enqueue()
        self.until_idle()
        job = self.job()
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "checkpoint"))
        self.assertTrue(any(event["type"] == "authority-refused" for event in team.read_events(self.run_dir())))


class PackagingTests(unittest.TestCase):
    def test_installed_alias_and_direct_helper(self) -> None:
        project = git_project()
        code, out, err = run_cli(project, "supervise", "status", "--project", str(project))
        self.assertEqual(code, 0, err)
        self.assertIn("Supervisor status", out)
        self.assertTrue((project / ".agentic-team" / "bin" / "agentic_supervisor.py").is_file())
        direct = subprocess.run([sys.executable, str(ROOT / "scripts" / "agentic_supervisor.py"), "status", "--project", str(project)],
                                capture_output=True, text=True)
        self.assertEqual(direct.returncode, 0, direct.stderr)
        code, out, _ = run_cli(project, "supervise", "--help")
        self.assertEqual(code, 0)
        for op in ("enqueue", "serve", "resume", "cancel", "poll-github"):
            self.assertIn(op, out)
        self.assertEqual(run_cli(project, "supervise", "serve", "--project", str(project))[0], sup.EXIT_USAGE, "a mode is required")

    def test_missing_helper_is_reported(self) -> None:
        project = fresh_project()
        (project / ".agentic-team" / "bin" / "agentic_supervisor.py").unlink()
        code, _, err = run_cli(project, "supervise", "status", "--project", str(project))
        self.assertEqual(code, 1)
        self.assertIn("reinstall AgenticTeam", err)
        self.assertNotIn("Traceback", err)

    def test_plugin_ships_the_supervisor(self) -> None:
        out = scratch("plugin-")
        plugin = team.package_claude_plugin(ROOT, out)
        self.assertTrue((plugin / "bin" / "agentic_supervisor.py").is_file())
        self.assertIn("supervise", team.HELPER_COMMANDS)

    def test_reinstall_and_uninstall_keep_supervisor_state(self) -> None:
        project = git_project()
        supervisor = sup.Supervisor(project)
        supervisor.configure(**fast_config())
        supervisor.pause(None, "keep it queued")
        supervisor.enqueue({"id": "kept", "kind": "manual", "title": "Kept"})
        store = supervisor.store.root
        team.install_team(ROOT, project, "generic", "full-company", [], [], force=True)
        self.assertTrue((project / ".agentic-team" / "supervisor" / "inbox" / "kept.json").is_file(), "reinstall preserves intake")
        team.uninstall_team(project)
        self.assertTrue((project / ".agentic-team" / "supervisor" / "inbox" / "kept.json").is_file(), "uninstall keeps supervisor/")
        self.assertTrue((store / "config.json").is_file(), "the owner store lives outside the project")
        team.install_team(ROOT, project, "generic", "full-company", [], [])
        team.uninstall_team(project, purge=True)
        self.assertFalse((project / ".agentic-team").exists())
        self.assertTrue((store / "config.json").is_file(), "purge removes the project's files only; the owner deletes the store")

    def test_paths_with_spaces(self) -> None:
        parent = scratch("space parent ")
        project = parent / "my project"
        source = git_project()
        shutil.copytree(source, project)
        supervisor = sup.Supervisor(project, parent / "owner store")
        supervisor.configure(**fast_config())
        supervisor.add_allowance(5.0, "spaces")
        supervisor.enqueue({"id": "spaced", "kind": "manual", "title": "Spaces", "acceptance": ["AC-1: works"]})
        supervisor.serve("until-idle", max_seconds=120)
        self.assertEqual(supervisor.store.job("spaced")["status"], "done")


class OperationsTests(SupervisorBase):
    def test_once_until_idle_and_forever(self) -> None:
        self.enqueue()
        self.assertEqual(self.sup.serve("once"), sup.EXIT_OK)
        self.assertIn(self.job()["status"], {"starting", "running"})
        self.assertEqual(self.sup.serve("until-idle", max_seconds=120), sup.EXIT_OK)
        self.assertEqual(self.job()["status"], "done")
        ticks = []

        def interrupt(_seconds: float) -> None:
            ticks.append(1)
            if len(ticks) >= 2:
                raise KeyboardInterrupt

        self.assertEqual(self.sup.serve("forever", 0.01, sleep=interrupt), sup.EXIT_OK)
        digest = json.loads(self.sup.store.digest_path.read_text(encoding="utf-8"))
        self.assertTrue(any("supervisor stopped" in item for item in digest["blockers"]))
        self.assertEqual(self.sup.status()["exit_code"], sup.EXIT_OK, "a clean stop is not a blocker")

    def test_retry_backoff_is_bounded(self) -> None:
        cfg = {"backoff_seconds": 30.0, "backoff_max_seconds": 900.0}
        self.assertEqual([sup.backoff_delay(cfg, retry) for retry in range(1, 8)], [30, 60, 120, 240, 480, 900, 900])

    def test_status_shows_no_secrets(self) -> None:
        self.enqueue(brief="SECRET-BRIEF-TEXT that should not be in the digest")
        self.until_idle()
        token = self.token()
        rendered = self.sup.store.status_md.read_text(encoding="utf-8")
        dumped = json.dumps(self.sup.status())
        for text in (rendered, dumped):
            self.assertNotIn(token, text)
            self.assertNotIn("fake-env", text, "transcripts are never shown")
            self.assertNotIn("SECRET-BRIEF-TEXT", text, "brief bodies stay in the run folder")
            self.assertNotIn("owner-tokens", text)

    def test_prune_keeps_unfinished_and_unmetered_work(self) -> None:
        self.enqueue("finished")
        self.until_idle()
        self.mode("missing-usage")
        self.enqueue("unmetered")
        self.until_idle()
        removed = self.sup.prune(0, dry_run=False)
        finished = self.sup.store.attempt_dir("finished", self.job("finished")["attempts"][0]["id"])
        unmetered = self.sup.store.attempt_dir("unmetered", self.job("unmetered")["attempts"][0]["id"])
        self.assertTrue(any(str(finished) in path for path in removed))
        self.assertFalse((finished / "stdout.jsonl").exists())
        self.assertTrue((finished / "exit.json").is_file(), "receipts are audit evidence and stay")
        self.assertTrue((unmetered / "stdout.jsonl").is_file(), "a transcript whose cost is unknown stays")
        self.assertTrue(self.sup.store.job_path("finished").is_file())

    def test_host_examples_use_absolute_paths_and_register_nothing(self) -> None:
        for platform in ("windows", "cron", "systemd"):
            text = sup.host_example(self.project, platform, 5)
            self.assertIn(str(self.project.resolve()), text)
            self.assertIn("serve --once", text)
            self.assertIn(str(team.agentic_home()), text)
            self.assertIn(str(self.sup.store.bin / "agentic_supervisor.py"), text, "the host runs the owner copy")
        scheduled = subprocess.run([sys.executable, str(self.sup.store.bin / "agentic_supervisor.py"), "serve", "--once", "--project", str(self.project)],
                                   cwd=tempfile.gettempdir(), capture_output=True, text=True)
        self.assertEqual(scheduled.returncode, 0, scheduled.stderr)
        alias = self.project / ".agentic-team" / "bin" / "agentic_team.py"
        refused = subprocess.run([sys.executable, str(alias), "supervise", "serve", "--once", "--project", str(self.project)],
                                 capture_output=True, text=True)
        self.assertEqual(refused.returncode, sup.EXIT_BLOCKED)
        self.assertIn("owner copy", refused.stderr)


class GithubPollTests(SupervisorBase):
    PAGE_ONE = [
        {"number": 1, "title": "Date parser drops the timezone", "body": "Steps\n- AC-1: parse_date keeps the offset\n- AC-2: regression test passes",
         "html_url": "https://github.com/acme/app/issues/1", "updated_at": "2026-10-28T09:00:00Z", "created_at": "2026-10-28T08:00:00Z"},
        {"number": 2, "title": "A pull request", "body": "", "pull_request": {"url": "x"}, "updated_at": "2026-10-28T09:30:00Z"},
    ]
    PAGE_TWO = [{"number": 3, "title": "Retry on 503", "body": "AC-1: retries twice", "updated_at": "2026-10-28T10:00:00Z"}]

    def setUp(self) -> None:
        super().setUp()
        self.sup.pause(None, "polling tests launch nothing")

    def test_issue_numbers_are_namespaced_by_repository(self) -> None:
        first, _ = sup.parse_issue_pages(json.dumps([{"number": 1, "title": "A", "body": ""}]), "github.com", "acme/app")
        second, _ = sup.parse_issue_pages(json.dumps([{"number": 1, "title": "B", "body": ""}]), "github.com", "acme/other")
        self.assertNotEqual(first[0]["id"], second[0]["id"])
        self.assertEqual((first[0]["source_key"], second[0]["source_key"]), ("github.com/acme/app#1", "github.com/acme/other#1"))
        events, newest = sup.parse_issue_pages(json.dumps(self.PAGE_ONE) + json.dumps(self.PAGE_TWO), "github.com", "acme/app")
        self.assertEqual([event["source"]["number"] for event in events], [1, 3], "pull requests are not issues")
        self.assertEqual(events[0]["acceptance"], ["- AC-1: parse_date keeps the offset", "- AC-2: regression test passes"])
        self.assertEqual(newest, "2026-10-28T10:00:00Z")

    def test_pagination_auth_and_rate_limits(self) -> None:
        with self.assertRaises(sup.UsageProblem):
            self.sup.poll_github(lambda argv: (0, "[]", ""))
        self.sup.configure(github={"repo": "acme/app", "label": "agentic"})
        calls: list[list[str]] = []

        def pages(argv: list[str]) -> tuple[int, str, str]:
            calls.append(argv)
            return 0, json.dumps(self.PAGE_ONE) + "\n" + json.dumps(self.PAGE_TWO), ""

        report = self.sup.poll_github(pages)
        self.assertEqual(len(report["accepted"]), 2)
        self.assertIn("--paginate", calls[0])
        self.assertIn("labels=agentic", calls[0][-1])
        report = self.sup.poll_github(pages)
        self.assertEqual((report["accepted"], len(report["duplicates"])), ([], 2))
        self.assertIn("since=2026-10-28T10%3A00%3A00Z", calls[1][-1], "the watermark is used after durable acceptance")
        watermark = json.loads(self.sup.store.poll_path.read_text(encoding="utf-8"))
        with self.assertRaises(sup.Blocked):
            self.sup.poll_github(lambda argv: (1, "", "gh: API rate limit exceeded for user"))
        with self.assertRaises(sup.SupervisorError) as raised:
            self.sup.poll_github(lambda argv: (1, "", "HTTP 401: Bad credentials"))
        self.assertIn("authentication", str(raised.exception))
        self.assertEqual(json.loads(self.sup.store.poll_path.read_text(encoding="utf-8")), watermark, "failures leave the watermark alone")
        fresh = [{"number": 9, "title": "New", "body": "AC-1: x", "updated_at": "2026-10-29T07:00:00Z"}]
        with mock.patch.object(sup.Supervisor, "enqueue", side_effect=sup.Blocked("store locked")):
            with self.assertRaises(sup.Blocked):
                self.sup.poll_github(lambda argv: (0, json.dumps(fresh), ""))
        self.assertEqual(json.loads(self.sup.store.poll_path.read_text(encoding="utf-8")), watermark, "an issue that was not accepted is not skipped")
        edited = [dict(self.PAGE_TWO[0], body="AC-1: retries five times", updated_at="2026-10-29T08:00:00Z")]
        report = self.sup.poll_github(lambda argv: (0, json.dumps(edited), ""))
        self.assertEqual(len(report["conflicts"]), 1, "an edited issue is reported, never silently replacing its job")
        self.sup.tick()
        self.assertEqual(len(self.sup.store.jobs()[0]), 2)


class ReviewFindingTests(SupervisorBase):
    """Regression tests for the independent review's findings (docs/supervisor-progress.md, P7)."""

    def test_forged_completion_is_not_done(self) -> None:
        self.mode("forge-complete")
        self.enqueue()
        self.until_idle()
        job = self.job()
        self.assertEqual(self.run_state()["status"], "complete", "the worker forged the status field")
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "evidence"))
        self.assertIn("run-completed", job["hold"]["reason"])

    def test_cancelling_an_ownership_hold_keeps_the_checkout_until_the_writer_ends(self) -> None:
        self.sup.configure(heartbeat_seconds=30.0)
        self.mode("claim-and-hang")
        self.enqueue("hung")
        self.sup.tick()
        folder = self.attempt_dir("hung")
        self.assertTrue(self.wait_for(lambda: (folder / "worker.json").exists()))
        self.assertTrue(self.wait_for(lambda: self.run_state("hung")["tasks"].get("T1", {}).get("status") == "claimed", 60),
                        "the worker holds its task and has written uncommitted files")
        self.sup.tick()
        os.utime(folder / "heartbeat", (time.time() - 600, time.time() - 600))
        self.sup.tick()
        job = self.job("hung")
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "ownership"))
        self.mode("success")
        self.enqueue("next")
        self.assertIn("reconciles that attempt", self.sup.cancel("hung", "stop it"))
        self.assertTrue((folder / "cancel").exists(), "the wrapper is asked to end its own tree")
        with self.assertRaises(sup.SupervisorError):
            self.sup.release("hung", "too early")
        self.sup.tick()
        self.assertEqual(self.sup.store.control()["checkout"]["job"], "hung")
        self.assertEqual(self.job("next")["status"], "queued", "no second writer while the first may act")
        self.assertTrue(self.wait_for(lambda: (folder / "exit.json").exists(), 30))
        self.sup.tick()
        self.assertEqual(self.job("hung")["status"], "cancelled")
        self.assertEqual(self.job("hung")["attempts"][-1]["usage"]["state"], "unknown", "its cost stays visible, not dropped")
        self.assertEqual(self.sup.status()["allowance"]["usd_reserved"], 1.0)
        self.sup.resume("hung", charge_reservation=True)
        self.sup.release("hung", "draft discarded by the owner")
        self.assertEqual(self.sup.status()["allowance"]["usd_reserved"], 0)

    def test_a_launch_failure_before_the_wrapper_is_a_visible_hold(self) -> None:
        self.enqueue()
        with mock.patch.object(sup.Supervisor, "worker_argv", side_effect=KeyError("runid")):
            self.sup.tick()
        job = self.job()
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "config"))
        self.assertIn("KeyError", job["hold"]["reason"])
        self.assertEqual(self.sup.resume("fix-1"), "job fix-1 is retrying")
        self.until_idle()
        self.assertEqual(self.job()["status"], "done")
        with self.assertRaises(sup.UsageProblem) as raised:
            self.sup.configure(command=[sys.executable, str(FAKE_WORKER), "--run", "{runid}"])
        self.assertIn("unknown placeholder", str(raised.exception))

    def test_an_interrupted_first_launch_resumes(self) -> None:
        self.enqueue()
        self.sup.pause(None, "set up")
        self.sup.tick()
        self.sup.resume(None)
        job = self.job()
        job.update(run_id="sup-fix-1", holds_checkout=True)  # killed after the reservation, before init-run finished
        self.sup.store.save_job(job)
        self.until_idle()
        job = self.job()
        self.assertEqual((job["status"], len(job["attempts"])), ("done", 1))

    def test_moving_a_record_aside_keeps_its_spend(self) -> None:
        self.enqueue()
        self.until_idle()
        self.assertEqual(self.sup.status()["allowance"]["usd_spent"], 0.01)
        aside = scratch("aside-")
        shutil.move(str(self.sup.store.job_path("fix-1")), str(aside / "fix-1.json"))
        self.sup.tick()
        self.assertEqual(self.sup.status()["allowance"]["usd_spent"], 0.01, "the spend is kept by key, not recomputed away")

    def test_config_and_budget_holds_have_a_way_out(self) -> None:
        self.sup.configure(adapter="claude")
        self.enqueue("paid")
        self.sup.tick()
        self.assertEqual(self.job("paid")["hold"]["kind"], "config")
        self.sup.configure(**fast_config())
        with self.assertRaises(sup.SupervisorError):
            self.sup.resume("paid")  # still frozen at acceptance
        self.sup.resume("paid", refresh_config=True)
        self.until_idle()
        self.assertEqual(self.job("paid")["status"], "done")
        self.sup.configure(run_budget={"usd": 1.0}, attempt_usd=1.0)
        self.mode("stop-after-build cost=0.5")
        self.enqueue("budgeted")
        self.until_idle()
        job = self.job("budgeted")
        self.assertEqual((job["status"], job["hold"]["kind"]), ("needs-human", "budget"))
        team.waive_requirement(self.project, self.run_dir("budgeted"), "budget:usd", "one more attempt", "Owner", self.token("budgeted"))
        self.mode("success")
        self.sup.resume("budgeted")
        self.until_idle()
        self.assertEqual(self.job("budgeted")["status"], "done")

    def test_a_cancelled_source_can_be_requeued_by_the_owner(self) -> None:
        self.sup.pause(None, "no launches")
        self.enqueue()
        self.sup.tick()
        self.sup.cancel("fix-1", "not now")
        event = {"id": "fix-1", "kind": "manual", "title": "Fix fix-1", "brief": "Make feature() return 42.", "acceptance": ["AC-1: feature() returns 42"]}
        self.assertEqual(self.sup.enqueue(event), ("duplicate", "fix-1"))
        outcome, job_id = self.sup.enqueue(event, requeue=True)
        self.assertEqual((outcome, job_id), ("requeued", "fix-1-r2"))
        self.sup.tick()
        self.assertEqual(self.job("fix-1-r2")["status"], "queued")
        self.assertEqual(self.job("fix-1")["status"], "cancelled")

    def test_hidden_changes_and_unreadable_trees_are_not_clean(self) -> None:
        tracked = self.project / ".gitignore"
        tracked.write_text(tracked.read_text(encoding="utf-8") + "# changed\n", encoding="utf-8")
        git(self.project, "update-index", "--skip-worktree", ".gitignore")
        (self.project / ".git" / "info").mkdir(exist_ok=True)
        (self.project / ".git" / "info" / "exclude").write_text("secret-notes.txt\n", encoding="utf-8")
        (self.project / "secret-notes.txt").write_text("hidden from status\n", encoding="utf-8")
        self.assertEqual(git(self.project, "status", "--porcelain"), "", "git status alone sees nothing")
        found = sup.dirty_paths(self.project)
        self.assertIn(".gitignore (hidden from git status)", found)
        self.assertIn("secret-notes.txt", found)
        broken = git_project()
        (broken / ".git" / "HEAD").write_text("ref: refs/heads/does-not-exist\n", encoding="utf-8")
        self.assertIsNone(sup.dirty_paths(broken), "an unreadable tree is unknown, never clean")

    def test_the_supervisor_compares_head_with_the_verified_commit(self) -> None:
        head = git(self.project, "rev-parse", "HEAD")
        self.assertEqual(self.sup.source_problems({"verified_sha": head}), [])
        self.assertIn("no verified commit", self.sup.source_problems({})[0])
        (self.project / ".agentic-team" / "knowledge" / "lessons-extra.md").write_text("learned\n", encoding="utf-8")
        git(self.project, "add", "-A")
        git(self.project, "commit", "-q", "-m", "knowledge only")
        self.assertEqual(self.sup.source_problems({"verified_sha": head}), [], "a later commit of runtime output keeps the verdict")
        (self.project / "src.py").write_text("x = 1\n", encoding="utf-8")
        git(self.project, "add", "-A")
        git(self.project, "commit", "-q", "-m", "source after verification")
        self.assertIn("change source", self.sup.source_problems({"verified_sha": head})[0])

    def test_the_digest_says_how_the_worker_is_bounded(self) -> None:
        self.sup.pause(None, "no launches")
        self.enqueue()
        self.sup.tick()
        row = self.sup.status()["jobs"][0]
        self.assertIn("unisolated", row["worker"])
        self.assertIn("unisolated", self.sup.store.status_md.read_text(encoding="utf-8"))
        self.assertIn("timeout-only", sup.worker_label({"adapter": "claude", "turn_limit": "timeout-only", "isolation": {}}))

    def test_an_interrupt_leaves_a_running_attempt_with_its_wrapper(self) -> None:
        self.mode("claim-and-hang")
        self.enqueue()

        def stop(_seconds: float) -> None:
            raise KeyboardInterrupt

        self.assertEqual(self.sup.serve("forever", 0.01, sleep=stop), sup.EXIT_OK)
        folder = self.attempt_dir()
        self.assertTrue(self.wait_for(lambda: (folder / "start.json").exists()))
        start = json.loads((folder / "start.json").read_text(encoding="utf-8"))
        self.assertTrue(sup.process_alive(start["pid"]), "shutdown stops intake, not the worker")
        restarted = sup.Supervisor(self.project)
        restarted.tick()
        self.assertEqual(self.job()["status"], "running")
        restarted.cancel("fix-1", "end of test")


class IsolationProbeTests(SupervisorBase):
    def stub(self, read: bool, view_writable: bool) -> list[str]:
        """A stand-in boundary that runs the probe after hiding what a real boundary would hide."""
        script = scratch("boundary-") / "boundary.py"
        script.write_text(
            "import subprocess, sys\nargs = sys.argv[1:]\n"
            f"if {not read!r} and len(args) > 3: args[3] = args[3] + '.hidden'\n"
            f"if {not view_writable!r} and len(args) > 5: args[5] = args[5] + '-not-there'\n"
            "raise SystemExit(subprocess.call(args))\n", encoding="utf-8")
        return [sys.executable, str(script)]

    def test_the_boundary_must_hide_the_store_and_protect_the_view(self) -> None:
        for read, writable, expected in ((True, True, False), (False, True, False), (False, False, True)):
            with self.subTest(read=read, view_writable=writable):
                self.sup.configure(isolation={"prefix": self.stub(read, writable), "python": sys.executable})
                self.assertEqual(self.sup.verify_isolation()["verified"], expected)
        self.sup.configure(isolation={"prefix": [sys.executable, "-c", "pass"]})
        self.assertFalse(self.sup.store.config()["isolation"]["verified"], "a new prefix must be verified again")

    def test_owner_work_runs_from_the_owner_copy(self) -> None:
        copy = self.sup.store.bin
        self.assertTrue((copy / "agentic_team.py").is_file() and (copy / "agentic_supervisor.py").is_file())
        self.assertFalse(sup.running_inside(self.project))
        recorded = json.loads(self.sup.store.meta_path.read_text(encoding="utf-8"))["owner_copy"]["sha256"]
        self.assertEqual(recorded["agentic_team.py"], sup.sha256_file(copy / "agentic_team.py"))
        bin_cli = self.project / ".agentic-team" / "bin" / "agentic_team.py"
        with mock.patch.object(sup.subprocess, "run", wraps=subprocess.run) as spy:
            self.sup.cli("status")
        self.assertEqual(Path(spy.call_args.args[0][1]), copy / "agentic_team.py")
        self.assertNotEqual(Path(spy.call_args.args[0][1]), bin_cli, "never the checkout's bin/, which a worker can edit")


if __name__ == "__main__":
    unittest.main()
