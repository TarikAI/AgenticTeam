"""Tests for the skill-integration bridge scripts (Phase 6 of the integration plan)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import design_to_admin  # noqa: E402
import findings_to_tasks  # noqa: E402

HANDOFF = {
    "project": "Moddesk",
    "profile": "standard",
    "areas": ["moderation", "users"],
    "pages": [
        {
            "id": "queue",
            "title": "Moderation queue",
            "route": "/admin/moderation/queue",
            "purpose": "Triage flagged content",
            "roles": ["moderator"],
            "affordances": [
                {"label": "Approve item", "destination": "action:approve", "mutation": True},
                {"label": "Open record", "destination": "/admin/records/:id"},
            ],
        },
        {
            "id": "Metrics Overview",
            "route": "/admin/metrics",
            "purpose": "Read-only platform metrics",
            "roles": ["admin"],
            "affordances": [],
        },
    ],
}

FINDINGS_OCR = [
    {
        "path": "src/components/Table.tsx",
        "content": "User content rendered without encoding (XSS)",
        "start_line": 42,
        "end_line": 42,
        "category": "security",
        "severity": "critical",
    },
    {
        "path": "src/api/list.py",
        "content": "Unpaginated list endpoint",
        "category": "performance",
        "severity": "medium",
    },
    {"path": "src/util.ts", "content": "Misspelled variable", "category": "style", "severity": "low"},
]


class TestDesignToAdmin(unittest.TestCase):
    def test_build_draft_maps_pages(self):
        draft = design_to_admin.build_draft(HANDOFF)
        self.assertEqual(len(draft["screens"]), 2)
        queue, metrics = draft["screens"]
        self.assertEqual(queue["actions"], ["approve-item"])
        self.assertIn("success", queue["states"])
        self.assertEqual(metrics["actions"], [])
        self.assertNotIn("success", metrics["states"])
        self.assertEqual(metrics["id"], "metrics-overview")  # slugified
        for screen in draft["screens"]:
            self.assertEqual(screen["status"], "planned")
            self.assertEqual(screen["capabilities"], [])  # derived later, by design

    def test_empty_handoff_rejected(self):
        with self.assertRaises(ValueError):
            design_to_admin.build_draft({"pages": []})

    def test_markdown_fallback_is_a_draft(self):
        markdown = design_to_admin.render_markdown(design_to_admin.build_draft(HANDOFF))
        self.assertIn("DRAFT ONLY", markdown)
        self.assertIn("(read-only)", markdown)
        self.assertIn("capability -> server operation", markdown)

    def test_duplicate_ids_disambiguated(self):
        handoff = {"pages": [{"id": "queue"}, {"id": "queue"}]}
        draft = design_to_admin.build_draft(handoff)
        self.assertEqual([s["id"] for s in draft["screens"]], ["queue", "queue-2"])

    def test_write_via_adminwright_cli_sequence(self):
        calls = []

        def fake_runner(argv, executable=None):
            calls.append(argv)
            return mock.Mock(returncode=0, stdout="", stderr="")

        with tempfile.TemporaryDirectory() as tmp:
            design_to_admin.write_via_adminwright(
                design_to_admin.build_draft(HANDOFF), Path(tmp), "/fake/skill",
                runner=fake_runner,
            )
        self.assertIn("init", calls[0])
        adds = [c for c in calls if "add" in c]
        self.assertEqual(len(adds), 2)
        screen_json = json.loads(adds[0][adds[0].index("--json") + 1])
        self.assertEqual(screen_json["status"], "planned")

    def test_cli_refused_write_raises(self):
        def fake_runner(argv, executable=None):
            return mock.Mock(returncode=2, stdout="", stderr="refused")

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(RuntimeError):
                design_to_admin.write_via_adminwright(
                    design_to_admin.build_draft(HANDOFF), Path(tmp), "/fake/skill",
                    runner=fake_runner,
                )

    def test_main_fallback_without_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            handoff_file = Path(tmp) / "handoff.json"
            handoff_file.write_text(json.dumps(HANDOFF), encoding="utf-8")
            with mock.patch.object(design_to_admin, "find_adminwright", return_value=None):
                rc = design_to_admin.main([str(handoff_file), "--project-root", tmp])
            self.assertEqual(rc, 0)
            draft = Path(tmp) / ".admin-console" / "ADMIN-DRAFT.md"
            self.assertTrue(draft.is_file())

    @unittest.skipUnless(
        design_to_admin.find_adminwright(Path.cwd()),
        "adminwright skill not installed on this machine",
    )
    def test_integration_real_manifest_write(self):
        skill = design_to_admin.find_adminwright(Path.cwd())
        with tempfile.TemporaryDirectory() as tmp:
            manifest = design_to_admin.write_via_adminwright(
                design_to_admin.build_draft(HANDOFF), Path(tmp), skill,
            )
            data = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(len(data["screens"]), 2)
            self.assertTrue(all(s["status"] == "planned" for s in data["screens"]))


class TestFindingsToTasks(unittest.TestCase):
    def test_ocr_schema_normalized(self):
        findings = [findings_to_tasks.normalize(f) for f in FINDINGS_OCR]
        self.assertEqual([f["severity"] for f in findings], ["blocker", "major", "minor"])
        self.assertEqual(findings[0]["line"], 42)

    def test_verdicts(self):
        self.assertEqual(findings_to_tasks.verdict([{"severity": "blocker"}]), "FAIL")
        self.assertEqual(findings_to_tasks.verdict([{"severity": "major"}]), "CONDITIONAL")
        self.assertEqual(findings_to_tasks.verdict([{"severity": "minor"}]), "PASS")
        self.assertEqual(findings_to_tasks.verdict([]), "PASS")

    def test_security_finding_routes_to_security_engineer(self):
        findings = [findings_to_tasks.normalize(f) for f in FINDINGS_OCR]
        tasks = findings_to_tasks.build_tasks(findings)
        owners = {t["owner"] for t in tasks}
        self.assertIn("security-engineer", owners)
        # blocker + major get individual tasks; the low one is batched
        summaries = [t["summary"] for t in tasks]
        self.assertTrue(any(s.startswith("[BLOCKER]") for s in summaries))
        self.assertTrue(any("Batched minor/nit" in s for s in summaries))

    def test_line_anchored_summaries(self):
        finding = findings_to_tasks.normalize(FINDINGS_OCR[0])
        task = findings_to_tasks.build_tasks([finding])[0]
        self.assertIn("src/components/Table.tsx:42", task["summary"])

    def test_unknown_severity_rejected(self):
        with self.assertRaises(ValueError):
            findings_to_tasks.normalize({"path": "a", "content": "x", "severity": "huge"})

    def test_add_task_command_shape(self):
        finding = findings_to_tasks.normalize(FINDINGS_OCR[0])
        command = findings_to_tasks.add_task_command(findings_to_tasks.build_tasks([finding])[0])
        self.assertIn("add-task", command)
        self.assertIn("--owner security-engineer", command)

    def test_main_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "findings.json"
            path.write_text(json.dumps(FINDINGS_OCR), encoding="utf-8")
            rc = findings_to_tasks.main([str(path)])
            self.assertEqual(rc, 1)  # blocker present -> not PASS
            path.write_text(json.dumps([]), encoding="utf-8")
            rc = findings_to_tasks.main([str(path)])
            self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
