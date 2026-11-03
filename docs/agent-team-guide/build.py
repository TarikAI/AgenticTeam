"""Build the shared AgenticTeam roster and guide (index.html and agent-roster.csv).

Claude Code and Codex both maintain this guide; the update rules are in UPDATING.md next to this file.

    python docs/agent-team-guide/build.py           rebuild index.html and agent-roster.csv
    python docs/agent-team-guide/build.py --check   change nothing; exit 1 if either output is stale or the data is inconsistent
"""
import argparse
import csv
import datetime
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AGENTS = {"claude": "Claude Code", "codex": "Codex"}
CORE = ["delivery-lead", "context-engineer", "qa-lead", "eval-engineer", "security-engineer", "sre-engineer"]
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PLAN_OR_PROMPT = re.compile(r"^docs/[^/]+-(?:plan|prompt|prompts)\.md$")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")


def load(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def long_date(iso):
    day = datetime.date.fromisoformat(iso)
    return f"{day.day} {day.strftime('%B')} {day.year}"


def read_source(path, ref=None):
    """Return (text, origin, last-changed date) from the working tree, or from a git ref when one is named."""
    if ref:
        shown = git("show", f"{ref}:{path}")
        if shown.returncode != 0:
            raise SystemExit(f"cannot read {path} at {ref}: {shown.stderr.strip()}")
        changed = git("log", "-1", "--format=%cs", ref, "--", path).stdout.strip()
        return shown.stdout, f"{ref}:{path}", changed
    file = ROOT / path
    if not file.is_file():
        raise SystemExit(f"missing file: {path}")
    changed = datetime.date.fromtimestamp(file.stat().st_mtime).isoformat()
    return file.read_text(encoding="utf-8"), path, changed


def title_of(text, fallback):
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def copy_block(prompt):
    blocks = re.findall(r"```(?:text)?\n(.*?)```", prompt.replace("\r\n", "\n"), re.S)
    return max(blocks, key=len).strip() if blocks else (prompt.partition("\n---\n")[2] or prompt).strip()


def validate(progress, updates, documents):
    problems = []
    for key in ("asOf", "updatedBy", "recordsRef", "runtimeIntegration", "statuses", "todaySummary", "evidence",
                "nextPriority", "documentsNote", "active"):
        if key not in progress:
            problems.append(f"progress.json: missing '{key}'")
    if not DATE.match(str(progress.get("asOf", ""))):
        problems.append("progress.json: asOf must be YYYY-MM-DD")
    if progress.get("updatedBy") not in AGENTS:
        problems.append(f"progress.json: updatedBy must be one of {sorted(AGENTS)}")
    for row in progress.get("statuses", []):
        if set(row) != {"area", "state", "detail"}:
            problems.append(f"progress.json: status rows need exactly area, state and detail: {row}")
    for row in progress.get("active", []):
        if set(row) != {"task", "agent", "where", "since"} or row.get("agent") not in AGENTS or not DATE.match(str(row.get("since", ""))):
            problems.append(f"progress.json: active rows need task, agent (claude|codex), where and since (YYYY-MM-DD): {row}")
    previous = None
    for number, entry in enumerate(updates.get("entries", []), 1):
        if set(entry) != {"date", "agent", "task", "summary", "documents", "refs"}:
            problems.append(f"updates.json entry {number}: needs exactly date, agent, task, summary, documents, refs")
            continue
        if not DATE.match(entry["date"]):
            problems.append(f"updates.json entry {number}: date must be YYYY-MM-DD")
        if entry["agent"] not in AGENTS:
            problems.append(f"updates.json entry {number}: agent must be claude or codex")
        if not isinstance(entry["documents"], list) or not isinstance(entry["refs"], list):
            problems.append(f"updates.json entry {number}: documents and refs are lists")
        if previous and entry["date"] > previous:
            problems.append(f"updates.json entry {number}: entries go newest first ({entry['date']} after {previous})")
        previous = entry["date"]
    listed = set()
    for group in ("current", "earlier"):
        for doc in documents.get(group, []):
            for key in ("plan", "prompt"):
                if doc.get(key):
                    listed.add(doc[key])
    for doc in documents.get("records", []):
        listed.add(doc["path"])
    tracked = {p for p in git("ls-files", "--cached", "--others", "--exclude-standard", "docs").stdout.split("\n") if p}
    unlisted = sorted(p for p in tracked if PLAN_OR_PROMPT.match(p) and p not in listed)
    for path in unlisted:
        problems.append(f"documents.json: {path} is a plan or prompt that is not registered")
    reconciled = git("rev-parse", "--verify", "--quiet", f"{progress.get('runtimeIntegration', '')}^{{commit}}").stdout.strip()
    current = git("rev-parse", "--verify", "--quiet", f"{progress.get('recordsRef', '')}^{{commit}}").stdout.strip()
    if not current:
        problems.append(f"progress.json: recordsRef '{progress.get('recordsRef')}' is not a branch in this repository")
    elif reconciled != current:
        problems.append(f"progress.json: statuses were reconciled at {progress.get('runtimeIntegration')}, but "
                        f"{progress['recordsRef']} is now at {current[:7]}: review the statuses, then set runtimeIntegration")
    return problems


def build():
    manifest = json.loads((ROOT / "team.json").read_text(encoding="utf-8"))
    roster = load("roster.json")
    if isinstance(roster, dict):
        roster = roster["agents"]
    assert [r["id"] for r in roster] == [r["id"] for r in manifest["agents"]], "roster.json must follow team.json order"
    for role, canonical in zip(roster, manifest["agents"]):
        role.update({k: canonical[k] for k in ("id", "department", "tier", "access", "reports_to", "capabilities")})
        role["path"] = canonical["file"]
        role["prompt"] = (ROOT / canonical["file"]).read_text(encoding="utf-8")
    progress, updates, documents = load("progress.json"), load("updates.json"), load("documents.json")
    problems = validate(progress, updates, documents)
    ref = progress["recordsRef"]
    guarantees_text, guarantees_origin, _ = read_source("config/guarantees.json", ref)
    # No main-checkout commit is embedded: the page is committed to main itself, so it would be stale after every commit.
    data = {
        "date": progress["asOf"], "asOfLabel": long_date(progress["asOf"]), "timezone": "Asia/Riyadh",
        "version": manifest["version"],
        "recordsSha": git("rev-parse", "--short", ref).stdout.strip(),
        "agents": roster, "harnesses": manifest["harnesses"], "profiles": manifest["model_profiles"],
        "presets": manifest["presets"], "defaults": manifest["defaults"], "core": CORE,
        "agentNames": AGENTS,
        "safety": load("safety.json"),
        "guarantees": json.loads(guarantees_text), "guaranteesOrigin": guarantees_origin,
        "progress": progress, "updates": updates["entries"],
        "review": (ROOT / "docs/autonomy-progress-review.md").read_text(encoding="utf-8"),
        "updating": (HERE / "UPDATING.md").read_text(encoding="utf-8"),
    }
    docs = []
    for group in ("current", "earlier"):
        for doc in documents[group]:
            plan, plan_origin, plan_changed = read_source(doc["plan"], doc.get("ref"))
            entry = {"id": doc["id"], "title": doc["title"], "group": group,
                     "plan_name": doc["plan"].removeprefix("docs/"), "plan": plan, "plan_origin": plan_origin,
                     "plan_changed": plan_changed, "prompt_name": None, "prompt": "", "copy_prompt": ""}
            if doc.get("prompt"):
                prompt, prompt_origin, prompt_changed = read_source(doc["prompt"], doc.get("ref"))
                entry.update({"prompt_name": doc["prompt"].removeprefix("docs/"), "prompt": prompt,
                              "prompt_origin": prompt_origin, "prompt_changed": prompt_changed,
                              "copy_prompt": copy_block(prompt)})
            docs.append(entry)
    data["documents"] = docs
    record_paths = ["docs/autonomy-implementation-progress.md"]
    listing = git("ls-tree", "--name-only", ref, "docs/autonomy-progress/").stdout.split("\n")
    record_paths += sorted(p for p in listing if p.endswith(".md"))
    records = []
    for path in record_paths:
        text, origin, changed = read_source(path, ref)
        records.append({"id": path, "path": path, "title": title_of(text, path), "group": "integration",
                        "origin": origin, "changed": changed, "text": text})
    integration, rest = records[:1], sorted(records[1:], key=lambda r: (r["changed"], r["title"]), reverse=True)
    records = integration + rest
    for doc in documents.get("records", []):
        text, origin, changed = read_source(doc["path"], doc.get("ref"))
        records.append({"id": doc["path"], "path": doc["path"], "title": doc.get("title") or title_of(text, doc["path"]),
                        "group": "earlier", "origin": origin, "changed": changed, "text": text})
    data["records"] = records
    encoded = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    template = (HERE / "guide.template.html").read_text(encoding="utf-8")
    assert template.count("__GUIDE_DATA__") == 1
    page = template.replace("__GUIDE_DATA__", encoded)
    out = io.StringIO(newline="")
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["Order", "Agent", "Department", "Reports to", "Harness", "Typical tasks", "Specialty", "Description",
                     "Prompt file", "Access", "Model tier", "Activation", "Durable agent today / recommended target"])
    for i, role in enumerate(roster, 1):
        tasks = role["tasks"]
        if isinstance(tasks, list):
            tasks = "; ".join(tasks)
        durable = ("Persistent responsibility record and owner-enabled duty dispatch in integration; no activated service evidenced"
                   if role["id"] in CORE else "Saved role and shared durable work state; on-demand worker; no activated service evidenced")
        writer.writerow([i, role["id"], role["department"], role["reports_to"], "All 13 compiler targets; runtime support varies",
                         tasks, role["specialty"], role["description"], role["path"], role["access"], role["tier"],
                         role.get("activation", ""), durable])
    return page, out.getvalue(), problems, data


def write(path, text, encoding):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding=encoding)
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="change nothing; exit 1 when the outputs are stale or the data is inconsistent")
    args = parser.parse_args()
    page, table, problems, data = build()
    index, csv_file = HERE / "index.html", HERE / "agent-roster.csv"
    if args.check:
        if not index.is_file() or index.read_text(encoding="utf-8") != page:
            problems.append("index.html is stale: run build.py")
        if not csv_file.is_file() or csv_file.read_text(encoding="utf-8-sig") != table:
            problems.append("agent-roster.csv is stale: run build.py")
        for problem in problems:
            print("PROBLEM:", problem)
        print("Shared guide is current." if not problems else f"{len(problems)} problem(s); see UPDATING.md.")
        return 1 if problems else 0
    write(index, page, "utf-8")
    write(csv_file, table, "utf-8-sig")
    for problem in problems:
        print("WARNING:", problem)
    print(f"Built the shared guide: {len(data['agents'])} roles, {len(data['documents'])} plans, {len(data['records'])} records, "
          f"{len(data['updates'])} updates; records {data['progress']['recordsRef']}@{data['recordsSha']}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
