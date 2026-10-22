#!/usr/bin/env bash
# Stop hook: block the turn when checks fail so Claude fixes them before finishing.
# A second consecutive failure is reported without blocking, to avoid a loop.
input=$(cat)
if output=$("$CLAUDE_PROJECT_DIR/scripts/check.sh" 2>&1); then exit 0; fi
if [ "$(jq -r '.stop_hook_active // false' <<<"$input")" = true ]; then
  jq -n --arg out "$output" '{systemMessage: ("Repository checks still failing:\n" + ($out | .[-1500:]))}'
  exit 0
fi
printf 'Repository checks failed. Fix them before finishing:\n%s\n' "$output" | tail -c 4000 >&2
exit 2
