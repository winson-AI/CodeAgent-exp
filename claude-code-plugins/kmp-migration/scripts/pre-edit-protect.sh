#!/usr/bin/env bash
set -euo pipefail

paths="$(
  python3 -c '
import json
import sys

payload = json.load(sys.stdin)
tool_input = payload.get("tool_input") or {}
paths = []

for key in ("file_path", "path", "notebook_path"):
    value = tool_input.get(key)
    if isinstance(value, str) and value:
        paths.append(value)

for edit in tool_input.get("edits") or []:
    if isinstance(edit, dict):
        value = edit.get("file_path") or edit.get("path")
        if isinstance(value, str) and value:
            paths.append(value)

print("\n".join(paths))
' 
)"

while IFS= read -r file; do
  [[ -z "$file" ]] && continue

  normalized="${file#file://}"
  basename="${normalized##*/}"

  if [[ "$basename" == ".env" || "$basename" == .env.* ]]; then
    echo "Editing $file is blocked by policy: .env files are protected." 1>&2
    exit 2
  fi
done <<< "$paths"

exit 0