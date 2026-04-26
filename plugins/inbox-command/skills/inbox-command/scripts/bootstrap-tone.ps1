# One-time script to learn the user's tone from their last 50 sent items per
# account and write the result to references/tone-profile.md.
#
# Re-run any time the user's style drifts (new role, new audience, etc.).
#
# Usage:
#   powershell -File bootstrap-tone.ps1

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillRoot = Resolve-Path (Join-Path $scriptDir "..")
$toneFile = Join-Path $skillRoot "references\tone-profile.md"

Write-Host "Bootstrapping tone profile from your last 50 sent items per account..."
Write-Host "This will replace $toneFile"
Write-Host ""

$prompt = @"
Use the composio MCP to list the last 50 messages I sent from each connected account
(Outlook tamar@dundeeus.com and Gmail). Read the bodies. Write a tone profile to
$toneFile that replaces the placeholder content with concrete, specific observations
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
"@

claude -p $prompt --permission-mode acceptEdits

Write-Host ""
Write-Host "Done. Review $toneFile and edit anything that's off."
