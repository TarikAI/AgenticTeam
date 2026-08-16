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

command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required." >&2; exit 1; }

if [ "$LIST" -eq 1 ]; then
  python3 "$CLI" --source "$ROOT" list agents
  printf '\nPresets:\n'
  python3 "$CLI" --source "$ROOT" list presets
  printf '\nHarnesses:\n'
  python3 "$CLI" --source "$ROOT" list harnesses
  exit 0
fi

[ -n "$TARGET" ] || { echo "Provide --target <project path>, or use --list." >&2; exit 2; }

if [ -n "$AGENTS" ]; then
  set --
  old_ifs=$IFS
  IFS=','
  for agent in $AGENTS; do set -- "$@" --only-agent "$agent"; done
  IFS=$old_ifs
  python3 "$CLI" --source "$ROOT" install "$TARGET" --harness "$HARNESS" "$@"
else
  python3 "$CLI" --source "$ROOT" install "$TARGET" --harness "$HARNESS" --preset "$PRESET"
fi
