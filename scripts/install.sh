#!/usr/bin/env bash
# Thin POSIX wrapper around the cross-platform AgenticTeam compiler.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLI="$ROOT/scripts/agentic_team.py"
PRESET="full-company"
TARGET=""
HARNESS="claude-code"
AGENTS=""
LIST=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --preset) PRESET="$2"; shift 2 ;;
    --target) TARGET="$2"; shift 2 ;;
    --harness) HARNESS="$2"; shift 2 ;;
    --agents) AGENTS="$2"; shift 2 ;;
    --list) LIST=1; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

# Resolve a Python that actually RUNS. On Windows, `python3` resolves to the Microsoft
# Store alias stub: `command -v` finds it, every invocation then fails with exit 49.
# So probe candidates by executing one, not by checking that the name exists.
PY_BIN=""
for candidate in python3 python py; do
  command -v "$candidate" >/dev/null 2>&1 || continue
  if [ "$candidate" = "py" ]; then
    if py -3 -c "import sys; sys.exit(0 if sys.version_info[:2] >= (3, 10) else 1)" >/dev/null 2>&1; then
      PY_BIN="py -3"; break
    fi
    continue
  fi
  if "$candidate" -c "import sys; sys.exit(0 if sys.version_info[:2] >= (3, 10) else 1)" >/dev/null 2>&1; then
    PY_BIN="$candidate"; break
  fi
done
if [ -z "$PY_BIN" ]; then
  echo "Python 3.10+ is required but no working interpreter was found (tried python3, python, py -3)." >&2
  exit 1
fi

if [ "$LIST" -eq 1 ]; then
  $PY_BIN "$CLI" --source "$ROOT" list agents
  printf '\nPresets:\n'
  $PY_BIN "$CLI" --source "$ROOT" list presets
  printf '\nHarnesses:\n'
  $PY_BIN "$CLI" --source "$ROOT" list harnesses
  exit 0
fi

[ -n "$TARGET" ] || { echo "Provide --target <project path>, or use --list." >&2; exit 2; }

if [ -n "$AGENTS" ]; then
  set --
  old_ifs=$IFS
  IFS=','
  for agent in $AGENTS; do set -- "$@" --only-agent "$agent"; done
  IFS=$old_ifs
  $PY_BIN "$CLI" --source "$ROOT" install "$TARGET" --harness "$HARNESS" "$@"
else
  $PY_BIN "$CLI" --source "$ROOT" install "$TARGET" --harness "$HARNESS" --preset "$PRESET"
fi
