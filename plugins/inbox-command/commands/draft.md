---
description: Re-draft a reply for a single message by ID.
argument-hint: <message-id>
allowed-tools: ["mcp__plugin_inbox-command_composio__*", "Read"]
---

Re-draft the reply for message `$ARGUMENTS`.

Steps:

1. Fetch the message via `composio` (try Outlook first, fall back to Gmail).
2. Load `skills/inbox-command/references/tone-profile.md` and `draft-prompt.md`.
3. Re-classify the message using `sender-rules.md` + `classification-prompt.md`.
4. Compose a new draft body using the verdict's mode (`yes` / `pass` / `needs_me`).
5. Replace the existing draft on that thread (or create a new one).
6. Print the verdict, reason, and the new draft body. Do not send.
