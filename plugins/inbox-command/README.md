# Inbox Command

Triage Outlook + Gmail three times a day. Flags what needs you, drafts replies in your tone, classifies senders into **yes / pass / silence**.

**Day-one safety:** drafts-only. Nothing is sent automatically until you opt in via `/inbox-command:enable-auto-send`.

## What it does

```
/inbox-command:scan
  → 12 scanned · 3 needs you · 5 yes drafts · 2 pass drafts · 2 silenced (0 sent)
```

- **Scan**: pulls unread mail from both inboxes since the last run.
- **Classify**: rules in `skills/inbox-command/references/sender-rules.md` win on exact match; the LLM judges the rest. Verdicts: `needs_me`, `yes`, `pass`, `silence`.
- **Draft**: composes replies using your learned tone (`references/tone-profile.md`).
- **Send (opt-in)**: only verdicts listed in `auto_send` are sent. Default `[]`.

## Mailboxes

- **Outlook**: `tamar@dundeeus.com` (Microsoft 365)
- **Gmail**: your personal account

Both go through one MCP server (Composio), so there is one OAuth flow and one trust boundary.

## Why Composio

You don't have admin rights on the dundeeus.com Microsoft 365 tenant, so a self-owned Azure app registration is blocked. Composio brings its own consented Azure app and Google OAuth client; you grant delegated access through their standard consent screen. Trade-off: tokens are custodied by Composio. Drafts-only mode keeps blast radius small while you evaluate that.

If you later get tenant admin and want to swap to a self-owned MCP (`@softeria/ms-365-mcp-server`), it is a one-file change to `.mcp.json`.

## Setup

### 1. Install the plugin

```
/plugin marketplace add ./
/plugin install inbox-command@claude-code-plugins
```

### 2. Create your Composio MCP server

1. Sign up at https://app.composio.dev (free tier is fine).
2. Create a new MCP server and add two integrations: **Outlook** and **Gmail**.
3. Connect each: sign in to `tamar@dundeeus.com` (Outlook) and your Gmail account; grant the read/send/draft scopes.
4. Copy the SSE URL Composio gives you (looks like `https://mcp.composio.dev/<server-id>/sse`).
5. Set the env var so this plugin picks it up:

   **Windows (PowerShell, persistent):**
   ```powershell
   [Environment]::SetEnvironmentVariable("COMPOSIO_MCP_URL", "https://mcp.composio.dev/<your-server-id>/sse", "User")
   ```

   Restart Claude Code so the env var is picked up.

### 3. First-run check

```
/mcp
```

Confirm `composio` is listed and shows tools for both Outlook and Gmail.

```
/inbox-command:scan
```

Should write drafts to both Drafts folders. Nothing in Sent.

### 4. Bootstrap your tone (one-time)

```powershell
powershell -File plugins\inbox-command\skills\inbox-command\scripts\bootstrap-tone.ps1
```

Reads your last 50 sent items per account, distills your style, writes `references/tone-profile.md`. Re-run any time your style drifts.

### 5. Seed your sender rules

```
/inbox-command:rules
```

Edit `references/sender-rules.md` to add senders / domains / subject keywords under `yes:`, `pass:`, `silence:`. Leave `auto_send: []` for now.

### 6. Install the Windows scheduled task (3x/day)

```powershell
powershell -File plugins\inbox-command\schedulers\install-task.ps1
```

Registers "Inbox Command — 3x daily" with triggers at 08:00, 13:00, 17:00 local time. Survives reboot, runs without an open terminal.

Verify:

```powershell
Get-ScheduledTask -TaskName "Inbox Command - 3x daily"
```

### 7. (Later) Enable auto-send

Once you trust the drafts:

```
/inbox-command:enable-auto-send pass    # auto-sends polite declines only
/inbox-command:enable-auto-send all     # auto-sends yes + pass; needs_me always waits
```

## Commands

| Command | What it does |
|---------|---|
| `/inbox-command:scan` | Full pipeline: scan → classify → draft → (opt-in) send |
| `/inbox-command:draft <message-id>` | Draft a reply for a single message |
| `/inbox-command:classify <sender>` | Show what verdict the rules give for a sender |
| `/inbox-command:rules` | Open the sender taxonomy for editing |
| `/inbox-command:enable-auto-send <pass\|all>` | Flip auto-send on |

## File map

```
plugins/inbox-command/
  .claude-plugin/plugin.json
  .mcp.json                     # Composio SSE server
  skills/inbox-command/
    SKILL.md                    # the workflow
    references/
      sender-rules.md           # YAML taxonomy (you edit this)
      tone-profile.md           # learned, written by bootstrap-tone.ps1
      classification-prompt.md  # few-shot exemplars
      draft-prompt.md           # tone-anchored reply prompt
    examples/
      yes-reply-example.md
      pass-reply-example.md
    scripts/
      bootstrap-tone.ps1
      bootstrap-tone.sh         # WSL/Git Bash variant
  commands/
    scan.md  draft.md  classify.md  rules.md  enable-auto-send.md
  hooks/
    session-start.sh  hooks.json
  schedulers/
    inbox-command.xml           # Task Scheduler definition
    install-task.ps1            # registers the task
    run-scan.ps1                # wrapper that the task runs
```

## State

Runtime state lives outside the repo at `%LOCALAPPDATA%\inbox-command\`:

- `state.json` — `last_scanned_ts` per account
- `last-run.md` — most recent scan summary (surfaced on next session via the SessionStart hook)
- `last-run.log` — Task Scheduler stdout/stderr

## Privacy notes

- Tokens are stored by Composio (cloud). Read their data handling docs before connecting accounts you consider sensitive.
- The plugin never logs message bodies to disk; only verdict + message ID + timestamp goes into `state.json`.
- Drafts-only mode is the default. Auto-send requires an explicit toggle.
