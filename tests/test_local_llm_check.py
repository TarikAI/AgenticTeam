"""Tests for the local LLM endpoint checker (docs/local-llms.md)."""

import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import local_llm_check  # noqa: E402


class TestParsers(unittest.TestCase):
    def test_openai_models_payload(self):
        payload = {"data": [{"id": "qwen-team"}, {"id": "llama-role"}, {"object": "model"}]}
        self.assertEqual(
            local_llm_check.parse_openai_models(payload), ["qwen-team", "llama-role"]
        )

    def test_openai_empty_and_invalid(self):
        self.assertEqual(local_llm_check.parse_openai_models({"data": []}), [])
        self.assertIsNone(local_llm_check.parse_openai_models({"nope": 1}))
        self.assertIsNone(local_llm_check.parse_openai_models(["not", "a", "dict"]))

    def test_ollama_models_payload(self):
        payload = {"models": [{"name": "llama3.1:8b"}, {"size": 123}]}
        self.assertEqual(local_llm_check.parse_ollama_models(payload), ["llama3.1:8b"])

    def test_ollama_invalid(self):
        self.assertIsNone(local_llm_check.parse_ollama_models({"models": "nope"}))
        self.assertIsNone(local_llm_check.parse_ollama_models(None))


class TestProbe(unittest.TestCase):
    def test_unreachable_endpoint_reports_absent(self):
        # A closed port on localhost must return None quickly, not raise.
        payload = local_llm_check.fetch_json("http://127.0.0.1:1/v1/models")
        self.assertIsNone(payload)

    def test_build_report_tolerates_absent_servers(self):
        report = local_llm_check.build_report()
        for name in ("lm_studio", "ollama"):
            self.assertIn(name, report)
            self.assertIsInstance(report[name]["reachable"], bool)
            self.assertIsInstance(report[name]["models"], list)

    def test_human_summary_mentions_guidance(self):
        summary = local_llm_check.human_summary(local_llm_check.build_report())
        self.assertIn("docs/local-llms.md", summary)
        self.assertIn("not a blocked run", summary)

    def test_main_always_exits_zero(self):
        self.assertEqual(local_llm_check.main(["--format", "json"]), 0)


if __name__ == "__main__":
    unittest.main()
