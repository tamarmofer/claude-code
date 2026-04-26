#!/bin/bash
# Surface the most recent inbox-command run summary if the last scan was more
# than 8 hours ago, or if the tone profile is still the placeholder.
#
# Reads (Windows): %LOCALAPPDATA%\inbox-command\last-run.md and state.json
# Reads (POSIX, e.g. WSL): $LOCALAPPDATA or ~/.local/share/inbox-command/
#
# Output goes to stdout, which Claude Code surfaces in the session.

set -euo pipefail

if [ -n "${LOCALAPPDATA:-}" ]; then
  state_dir="${LOCALAPPDATA}/inbox-command"
else
  state_dir="${HOME}/.local/share/inbox-command"
fi

last_run="${state_dir}/last-run.md"
state="${state_dir}/state.json"

# Surface a stale run summary if the most recent scan is more than 8h old.
if [ -f "$last_run" ]; then
  now_epoch=$(date +%s)
  mtime_epoch=$(stat -c %Y "$last_run" 2>/dev/null || stat -f %m "$last_run" 2>/dev/null || echo 0)
  age_hours=$(( (now_epoch - mtime_epoch) / 3600 ))

  if [ "$age_hours" -ge 8 ]; then
    echo "## Inbox Command — last run was ${age_hours}h ago"
    echo ""
    cat "$last_run"
    echo ""
    echo "Run \`/inbox-command:scan\` to refresh, or wait for the next scheduled run."
  fi
fi

# Nudge if tone profile is still the placeholder.
plugin_root="${CLAUDE_PLUGIN_ROOT:-}"
if [ -n "$plugin_root" ]; then
  tone_file="${plugin_root}/skills/inbox-command/references/tone-profile.md"
  if [ -f "$tone_file" ] && grep -q "PLACEHOLDER" "$tone_file"; then
    echo ""
    echo "_Tone profile is still the placeholder. Run \`bootstrap-tone.ps1\` (or \`bootstrap-tone.sh\`) to capture your style._"
  fi
fi
