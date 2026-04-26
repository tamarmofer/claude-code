---
description: Scan Outlook + Gmail, classify, and draft replies. Drafts only unless auto_send is enabled.
allowed-tools: ["mcp__plugin_inbox-command_composio__*", "Read", "Write", "Bash"]
---

Run the full Inbox Command pipeline as documented in `skills/inbox-command/SKILL.md`.

Steps:

1. Verify the `composio` MCP is connected. If not, stop and tell the user to set `COMPOSIO_MCP_URL` and restart Claude Code.
2. Load `skills/inbox-command/references/sender-rules.md`, `tone-profile.md`, `classification-prompt.md`, `draft-prompt.md`.
3. Read `%LOCALAPPDATA%\inbox-command\state.json` (or default both `last_scanned_ts` to `now - 24h` if missing).
4. For each account in `[outlook, gmail]`: pull unread messages since the last scan, classify each, create a draft if the verdict is anything other than `silence`, and send only if the verdict is in `auto_send`.
5. `needs_me` is **never** auto-sent regardless of `auto_send`.
6. Update `state.json` and write a summary to `last-run.md`.
7. Print the summary to stdout.

If running headlessly (Task Scheduler), do not prompt for clarification. On any per-message failure, log it and continue.
