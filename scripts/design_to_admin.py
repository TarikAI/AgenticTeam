#!/usr/bin/env python3
"""Bridge: translate a design-architect handoff into a DRAFT adminwright manifest.

A design-architect Phase-14 handoff (page map, component map, coverage) closes the UI
graph: every affordance has a destination. That guarantees no dangling links — it does
NOT guarantee the right capabilities exist. This bridge therefore emits a draft only:
screens and navigation as starting points, statuses "planned", capabilities empty on
purpose. Adminwright Phases 1-3 (discovery, control-plane modeling, capability
derivation) still must run before any implementation claim.

Input (JSON file): {"project", "profile"?, "areas"?, "pages": [{"id", "title"?, "route",
"purpose"?, "roles"?, "affordances": [{"label", "destination", "mutation"?}]}]}

Modes:
- adminwright installed: initializes <project>/.admin-console/manifest.json via the
  skill's own CLI (init + add screen), so entries are validated at write time.
- adminwright absent: writes <project>/.admin-console/ADMIN-DRAFT.md — the same draft
  as a hand-fillable trace table per protocols/admin-surfaces.md.

Exit 0 on success, 2 on usage/IO errors. A draft is never a release claim.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preflight_skills import KNOWN_SKILLS, PROJECT_SKILL_DIRS, HOME_SKILL_DIRS  # noqa: E402

REQUIRED_STATES = ["loading", "populated", "error", "forbidden"]

ID_PATTERN = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")


def find_adminwright(project_root):
    markers = KNOWN_SKILLS["adminwright"][0]
    roots = []
    for rel in PROJECT_SKILL_DIRS:
        p = project_root / rel
        if p.is_dir():
            roots.append(p)
    for rel in HOME_SKILL_DIRS:
        p = Path.home() / rel
        if p.is_dir():
            roots.append(p)
    for root in roots:
        for marker in markers:
            candidate = root / marker
            if candidate.is_file():
                return candidate.parent
    return None


def slugify(value, fallback):
    slug = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    if not slug:
        slug = fallback
    if not ID_PATTERN.match(slug):
        slug = fallback
    return slug


def build_screen(page):
    """Map one handoff page to one schema-conforming draft screen entry."""
    page_id = slugify(page.get("id") or page.get("title"), "screen")
    affordances = page.get("affordances") or []
    mutations = [a for a in affordances if a.get("mutation")]
    states = list(REQUIRED_STATES)
    if mutations:
        states.append("success")
    return {
        "id": page_id,
        "route": page.get("route") or f"/{page_id}",
        "purpose": page.get("purpose") or page.get("title") or page_id,
        "roles": page.get("roles") or [],
        "dataSources": [],  # authoritative sources are discovered in Phase 1, not designed
        "capabilities": [],  # derived in Phase 3 from domain evidence, not UI topology
        "actions": [slugify(a.get("label"), "action") for a in mutations],
        "states": states,
        "responsive": True,
        "accessibilityStatus": "planned",
        "status": "planned",
        "rationale": "Draft from design-architect handoff; requires Phases 1-3 derivation.",
        "tests": [],
    }


def build_draft(handoff):
    pages = handoff.get("pages") or []
    if not pages:
        raise ValueError("handoff contains no pages")
    seen = set()
    screens = []
    for page in pages:
        screen = build_screen(page)
        base = screen["id"]
        n = 2
        while screen["id"] in seen:
            screen["id"] = f"{base}-{n}"
            n += 1
        seen.add(screen["id"])
        screens.append(screen)
    return {
        "project": handoff.get("project") or "Untitled Platform",
        "profile": handoff.get("profile") or "standard",
        "areas": handoff.get("areas") or [],
        "screens": screens,
    }


def render_markdown(draft):
    lines = [
        "# Admin console draft (from design-architect handoff)",
        "",
        "DRAFT ONLY. A closed UI graph is not capability completeness. Run the",
        "admin-surface contract (protocols/admin-surfaces.md) — or adminwright Phases",
        "1-3 when installed — before any implementation claim.",
        "",
        f"- Project: {draft['project']}  ·  Profile: {draft['profile']}",
        f"- Areas: {', '.join(draft['areas']) or '(unspecified)'}",
        "",
        "| Screen | Route | Purpose | Roles | Actions | States |",
        "|---|---|---|---|---|---|",
    ]
    for s in draft["screens"]:
        lines.append(
            f"| {s['id']} | {s['route']} | {s['purpose']} | "
            f"{', '.join(s['roles']) or '?'} | {', '.join(s['actions']) or '(read-only)'} | "
            f"{', '.join(s['states'])} |"
        )
    lines += [
        "",
        "For each screen, complete by hand: capability -> server operation -> policy ->",
        "data source -> audit event -> test -> evidence. Orphans on either side are defects.",
        "",
    ]
    return "\n".join(lines)


def run(argv, executable=None):
    executable = executable or sys.executable
    return subprocess.run(
        [executable, *argv], capture_output=True, text=True, check=False
    )


def write_via_adminwright(draft, project_root, skill_dir, runner=None):
    runner = runner or run
    manifest = project_root / ".admin-console" / "manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    cli = str(Path(skill_dir) / "scripts" / "admin_console_manifest.py")
    result = runner([
        cli, "init",
        "--project-root", str(project_root),
        "--name", draft["project"],
        "--profile", draft["profile"],
    ])
    if result.returncode != 0:
        sys.stderr.write(result.stdout + result.stderr)
        raise RuntimeError("adminwright manifest init failed")
    waved = []
    for screen in draft["screens"]:
        # Drafts lack discovered data sources and formally declared roles by design;
        # --allow-invalid writes them through, reports what it waved past, and the
        # release gate still refuses until Phases 1-3 fill the gaps with evidence.
        result = runner([
            cli, "add",
            "--manifest", str(manifest),
            "--kind", "screen",
            "--json", json.dumps(screen),
            "--allow-invalid",
        ])
        if result.returncode != 0:
            sys.stderr.write(result.stdout + result.stderr)
            raise RuntimeError(f"add screen {screen['id']} failed (refused write)")
        waved.append(result.stdout.strip())
    if any(waved):
        print("Written through --allow-invalid; the release gate still blocks on:")
        print("\n".join(w for w in waved if w))
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("handoff", help="design-architect Phase-14 handoff JSON file")
    parser.add_argument("--project-root", default=".", help="target project root")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    try:
        handoff = json.loads(Path(args.handoff).read_text(encoding="utf-8"))
        draft = build_draft(handoff)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(f"cannot read handoff: {exc}")

    skill_dir = find_adminwright(project_root)
    if skill_dir:
        manifest = write_via_adminwright(draft, project_root, skill_dir)
        print(f"Draft manifest written via adminwright: {manifest}")
        print("Screens planned:", ", ".join(s["id"] for s in draft["screens"]))
        print("Phases 1-3 (discovery, modeling, capability derivation) still required.")
        return 0
    out = project_root / ".admin-console" / "ADMIN-DRAFT.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_markdown(draft), encoding="utf-8")
    print(f"adminwright not found; draft trace table written: {out}")
    print("Fill capabilities, operations, policies, audit, and evidence by hand per")
    print("protocols/admin-surfaces.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
