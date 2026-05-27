#!/usr/bin/env bash
set -euo pipefail
# Hook payload arrives on stdin as JSON; tool input includes the file path.
file=$(jq -r '.tool_input.file_path // empty')
[ -n "$file" ] && [[ "$file" == *.kt ]] && ktlint -F "$file" || true