#!/usr/bin/env python3
"""Check local LLM servers (LM Studio, Ollama) and report loaded models.

Probes the common OpenAI-compatible endpoints and prints what is reachable and which
models are loaded. This is a report, not a gate: exit code is always 0, and an absent
server means sequential or cloud-backed execution, not a blocked run. Companion to
scripts/preflight_skills.py capability report (see docs/local-llms.md).

Usage:
    python scripts/local_llm_check.py                # human summary
    python scripts/local_llm_check.py --format json  # machine-readable
"""

import argparse
import json
import sys
import urllib.error
import urllib.request

TIMEOUT_SECONDS = 2.5

LM_STUDIO_URL = "http://localhost:1234/v1/models"
OLLAMA_URL = "http://localhost:11434/api/tags"


def fetch_json(url):
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError):
        return None


def parse_openai_models(payload):
    """OpenAI-compatible /v1/models: {"data": [{"id": ...}]}"""
    if not isinstance(payload, dict):
        return None
    models = payload.get("data")
    if not isinstance(models, list):
        return None
    return [m.get("id") for m in models if isinstance(m, dict) and m.get("id")]


def parse_ollama_models(payload):
    """Ollama /api/tags: {"models": [{"name": ...}]}"""
    if not isinstance(payload, dict):
        return None
    models = payload.get("models")
    if not isinstance(models, list):
        return None
    return [m.get("name") for m in models if isinstance(m, dict) and m.get("name")]


def build_report():
    report = {
        "lm_studio": {"endpoint": LM_STUDIO_URL, "reachable": False, "models": []},
        "ollama": {"endpoint": OLLAMA_URL, "reachable": False, "models": []},
    }
    payload = fetch_json(LM_STUDIO_URL)
    models = parse_openai_models(payload) if payload is not None else None
    if models is not None:
        report["lm_studio"].update(reachable=True, models=models)
    payload = fetch_json(OLLAMA_URL)
    models = parse_ollama_models(payload) if payload is not None else None
    if models is not None:
        report["ollama"].update(reachable=True, models=models)
    return report


def human_summary(report):
    lines = ["Local LLM report", "=" * 30]
    for name in ("lm_studio", "ollama"):
        entry = report[name]
        if entry["reachable"]:
            listed = ", ".join(entry["models"]) or "(server reachable, no models loaded)"
            lines.append(f"[reachable] {name}: {entry['endpoint']}")
            lines.append(f"            models: {listed}")
        else:
            lines.append(f"[absent  ] {name}: {entry['endpoint']} not reachable")
    lines.append("Absent servers mean sequential or cloud-backed execution, not a blocked run.")
    lines.append("Guidance: docs/local-llms.md")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    report = build_report()
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(human_summary(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
