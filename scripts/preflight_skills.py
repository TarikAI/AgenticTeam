#!/usr/bin/env python3
"""Preflight: detect installed skills and review tooling; print a capability report.

Checks project-local and user-global skill directories for the known skills listed in
protocols/skill-acquisition.md, plus the `ocr` CLI on PATH. This is a report, not a
gate: exit code is always 0, and every absent capability is paired with the floor
protocol that covers it (see docs/skills-integration-plan.md).

Usage:
    python scripts/preflight_skills.py                # human summary
    python scripts/preflight_skills.py --format json  # machine-readable
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

# skill name -> (relative marker files, floor protocol, what it unlocks)
KNOWN_SKILLS = {
    "adminwright": (
        ["adminwright/SKILL.md"],
        "protocols/admin-surfaces.md",
        "admin consoles / control surfaces: manifest-driven build and release gates",
    ),
    "design-architect": (
        ["design-architect/SKILL.md", "design-architect/README.md"],
        "protocols/interface-closure.md",
        "complete UI system design: enumeration, closure fixpoint, page/component maps",
    ),
    "open-code-review-delegate": (
        ["open-code-review-delegate/SKILL.md"],
        "protocols/review-discipline.md",
        "diff review: deterministic file selection and per-file rule checklists",
    ),
}

# skill-dir candidates, relative to the project root and to the user home,
# mirroring the harness map in team.json plus user-global installs.
PROJECT_SKILL_DIRS = [
    ".claude/skills",
    ".agents/skills",
    ".pi/skills",
    "skills",
]
HOME_SKILL_DIRS = [
    ".claude/skills",
    ".agents/skills",
    ".pi/skills",
]


def find_skill(markers, roots):
    for root in roots:
        for marker in markers:
            candidate = root / marker
            if candidate.is_file():
                return str(candidate)
    return None


def build_report(project_root):
    roots = []
    for rel in PROJECT_SKILL_DIRS:
        path = project_root / rel
        if path.is_dir():
            roots.append(path)
    home = Path.home()
    for rel in HOME_SKILL_DIRS:
        path = home / rel
        if path.is_dir():
            roots.append(path)

    report = {
        "project_root": str(project_root),
        "skill_roots": [str(r) for r in roots],
        "skills": {},
        "tools": {"ocr": shutil.which("ocr")},
        "floors": {
            "admin-surfaces": "protocols/admin-surfaces.md",
            "interface-closure": "protocols/interface-closure.md",
            "review-discipline": "protocols/review-discipline.md",
        },
    }
    for name, (markers, floor, unlocks) in KNOWN_SKILLS.items():
        report["skills"][name] = {
            "path": find_skill(markers, roots),
            "floor": floor,
            "unlocks": unlocks,
        }
    return report


def human_summary(report):
    lines = ["Preflight capability report", "=" * 40]
    for name, info in report["skills"].items():
        if info["path"]:
            lines.append(f"[present] {name}: {info['path']}")
            lines.append(f"          unlocks: {info['unlocks']}")
        else:
            lines.append(f"[absent ] {name}")
            lines.append(f"          floor:   {info['floor']} (applies regardless)")
    ocr = report["tools"]["ocr"]
    if ocr:
        lines.append(f"[present] ocr CLI: {ocr}")
        lines.append("          use delegation mode in-session (no endpoint needed):")
        lines.append("          ocr delegate preview --format json, then ocr delegate rule")
    else:
        lines.append("[absent ] ocr CLI")
        lines.append("          install: npm install -g @alibaba-group/open-code-review (R2)")
        lines.append("          floor:   protocols/review-discipline.md")
    lines.append("Full-mode ocr review/scan requires an LLM endpoint: CI secret only.")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--project-root",
        default=str(Path(__file__).resolve().parent.parent),
        help="project root to scan (default: this repository)",
    )
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    report = build_report(Path(args.project_root))
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(human_summary(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
