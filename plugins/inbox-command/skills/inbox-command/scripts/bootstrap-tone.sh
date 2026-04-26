#!/bin/bash
# Bash variant of bootstrap-tone.ps1 for WSL / Git Bash users.
# Re-run any time the user's style drifts.

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_root="$(cd "$script_dir/.." && pwd)"
tone_file="$skill_root/references/tone-profile.md"

echo "Bootstrapping tone profile from your last 50 sent items per account..."
echo "This will replace $tone_file"
echo

prompt=$(cat <<EOF
Use the composio MCP to list the last 50 messages I sent from each connected account
(Outlook tamar@dundeeus.com and Gmail). Read the bodies. Write a tone profile to
$tone_file that replaces the placeholder content with concrete, specific observations
drawn from my actual sent mail. Fill these sections with specifics, not generic advice:

  - Greeting (with examples of the exact form I use)
  - Sign-off (with the exact strings I use)
  - Sentence length (median + range, count one-sentence paragraphs)
  - Hedging tics (the actual phrases I use)
  - Punctuation tics (em-dashes, parentheticals, ellipses, lowercase starts)
  - Emoji policy (which ones I actually use, in which contexts)
  - Closing patterns by reply length (short/medium/long)

Quote 2-3 short sentences from my actual sent mail per section to anchor the
observations. Do not invent style I don't use.

When done, print 'Tone profile written.' to stdout.
EOF
)

claude -p "$prompt" --permission-mode acceptEdits

echo
echo "Done. Review $tone_file and edit anything that's off."
