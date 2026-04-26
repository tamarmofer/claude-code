---
name: Inbox Command
description: This skill should be used when the user asks to "scan my inbox", "triage email", "process my inbox", "manage email", "draft replies for my inbox", "run inbox command", "check my inbox", or invokes any /inbox-command:* slash command. Operates against tamar@dundeeus.com (Outlook) and a personal Gmail account through a single Composio MCP server. Drafts-only by default; auto-send is opt-in.
version: 0.1.0
---

# Inbox Command

Triage Outlook + Gmail three times a day. Flag what needs the user, draft replies in the user's tone, classify senders into yes / pass / silence. Drafts-only by default.

## Operating principle

Every message gets exactly one of four verdicts:

- **needs_me** — requires the user's judgment. Draft a thoughtful reply; never auto-send.
- **yes** — user would say yes; sender is on the yes-list or LLM is highly confident. Short affirmative draft.
- **pass** — polite decline. Sender is on the pass-list or matches a pass-keyword (recruiting, sponsorship invites, partnership pitches).
- **silence** — newsletters, no-reply, automated. Log and move on. No draft.

Only verdicts in `auto_send` (from `references/sender-rules.md`) actually get sent. Default is `[]` — drafts only.

## Inputs

Two MCP-backed mailboxes accessed through one server:

- `composio` (SSE) — tools for both Outlook and Gmail.

Tool families used (exact names depend on Composio's tool naming, prefixed `mcp__plugin_inbox-command_composio__`):

- list / search messages (filtered by `unread:true` and `since:<timestamp>`)
- get message body + headers
- create draft on a thread
- send draft
- list sent items (used only by `bootstrap-tone.ps1`)

If `composio` is not connected, stop and tell the user to set `COMPOSIO_MCP_URL` and run `/mcp` to confirm.

## State

Outside the repo, at `%LOCALAPPDATA%\inbox-command\`:

- `state.json` — `{"outlook": {"last_scanned_ts": "..."}, "gmail": {"last_scanned_ts": "..."}}`
- `last-run.md` — human-readable summary written at end of each scan
- `last-run.log` — Task Scheduler captures stdout/stderr here

Create the directory if missing. On first run, default `last_scanned_ts` to 24 hours ago per account.

## Workflow

### 1. Load configuration

Read three files relative to this skill:

- `references/sender-rules.md` — YAML taxonomy (yes/pass/silence) and `auto_send` list
- `references/tone-profile.md` — distilled style invariants
- `references/classification-prompt.md` — few-shot exemplars for verdict
- `references/draft-prompt.md` — tone-anchored reply prompt

Read state from `%LOCALAPPDATA%\inbox-command\state.json`. If the file does not exist, treat `last_scanned_ts` as `now - 24h` for both accounts.

### 2. Pull messages

For each account in `[outlook, gmail]`:

```
msgs = composio.list_messages(
    account=<account>,
    filter={"unread": true, "since": state[<account>].last_scanned_ts}
)
```

If the list is empty, skip to the next account.

### 3. Classify (rules win, then LLM)

For each message, in order:

1. **Hard rules from `sender-rules.md`** — if a `yes:`, `pass:`, or `silence:` rule matches the sender domain, exact address, or subject keyword, that verdict wins immediately.
2. **LLM judgment** — if no rule matched, classify using the prompt in `references/classification-prompt.md`. The prompt returns one of `needs_me | yes | pass | silence` plus a one-line reason. Default to `needs_me` when uncertain — it is the safest verdict because it never auto-sends.

Hard rules always beat LLM verdicts. Never override `silence` from rules.

### 4. Compose drafts

- `silence` → no draft. Log `{message_id, verdict: silence, reason}` and move on.
- `yes` → 1–3 sentence affirmative draft using `references/draft-prompt.md` with `mode=yes`.
- `pass` → 2–4 sentence polite decline using `mode=pass`. Always thank, acknowledge, decline cleanly, no door-left-open. See `examples/pass-reply-example.md`.
- `needs_me` → longer draft (4–8 sentences) using `mode=needs_me`. Mark the subject `[needs you]` so the user can find it in Drafts.

Every draft is created via `composio.create_draft(account, thread_id, body, subject_prefix?)`.

### 5. (Opt-in) Send

After all drafts are created, for each draft whose verdict is in `rules.auto_send`:

```
composio.send_draft(account, draft_id)
```

Default `auto_send: []` means this loop is a no-op. `needs_me` is never auto-sent regardless of config — this is enforced in code, not just by convention.

### 6. Update state and write summary

- Update `state.json` `last_scanned_ts` per account to the current UTC timestamp.
- Write `last-run.md` with counts:

```
# Inbox Command — 2026-04-26 13:00 PT
- Outlook: 8 scanned · 2 needs you · 3 yes drafts · 1 pass draft · 2 silenced (0 sent)
- Gmail: 4 scanned · 1 needs you · 2 yes drafts · 0 pass drafts · 1 silenced (0 sent)

## Needs your attention
- Outlook · Sarah Chen · "Q2 board prep" · thread <id>
- Outlook · Mike Patel · "intro to founders fund" · thread <id>
- Gmail · Mom · "easter weekend" · thread <id>
```

Print this summary to stdout at the end of the run.

## Tone matching

`references/tone-profile.md` is the single source of truth for "the user's voice." It contains:

- Greeting patterns ("Hi {first}," vs. no greeting vs. "{first} —")
- Sign-off patterns ("Tamar" vs. "T" vs. none)
- Sentence length distribution (median + range)
- Hedging tics (e.g., "honestly," "to be frank," "happy to —")
- Em-dash, ellipsis, parenthetical usage
- Emoji policy (yes / no / which ones / when)

The draft prompt (`references/draft-prompt.md`) injects this profile into the system prefix on every compose call.

If `tone-profile.md` still says "PLACEHOLDER — run bootstrap-tone.ps1," compose drafts with a neutral professional voice and append a one-line note to the run summary asking the user to bootstrap.

## Sender classification taxonomy

`references/sender-rules.md` is YAML inside a fenced block:

```yaml
yes:
  - domain: stripe.com
  - sender: ceo@dundeeus.com
pass:
  - subject_keywords: [partnership, sponsorship, podcast invite, "guest post"]
  - domain_pattern: "*.recruiter.com"
silence:
  - domain_pattern: "noreply.*"
  - subject_keywords: [unsubscribe, newsletter, "view in browser"]
auto_send: []   # add `pass` first, then `yes`. needs_me never sends.
```

Match precedence: exact sender > exact domain > domain_pattern > subject_keywords. First match wins.

## Hard guarantees (do not break)

1. `needs_me` is **never** sent automatically, regardless of `auto_send`.
2. `silence` produces zero drafts and zero sends.
3. If `composio` MCP is not connected, abort cleanly and tell the user how to fix it. Do not write to state.
4. If any single message fails (parse error, draft API error), log it, increment a `failed` counter in the summary, and continue with the next message. Never let one bad message kill the run.
5. Message bodies are never written to disk. Only verdicts, message IDs, sender, subject, and timestamps appear in `state.json` / `last-run.md`.

## Headless invocation

The Windows scheduled task invokes:

```
claude -p "/inbox-command:scan" --permission-mode acceptEdits
```

The skill must succeed without any interactive prompts. If a clarification is needed, log it and skip — do not block.

## Manual commands

- `/inbox-command:scan` — full pipeline (this workflow)
- `/inbox-command:draft <message-id>` — re-draft a single message; useful when a draft was bad
- `/inbox-command:classify <sender>` — explain what verdict a sender would get and why
- `/inbox-command:rules` — open `references/sender-rules.md` for editing
- `/inbox-command:enable-auto-send <pass|all>` — flip the auto_send list

## Verification

To validate end-to-end:

1. `/mcp` lists `composio` connected with Outlook + Gmail tools visible.
2. Send a test email from a personal address to both inboxes; run `/inbox-command:scan`; one `needs_me` draft should appear in each Drafts folder; Sent should be unchanged.
3. Add the test sender to `pass:`; resend; a polite decline should appear in Drafts (not Sent until `auto_send` includes `pass`).
4. Task Scheduler History shows three runs at 08:00, 13:00, 17:00; `state.json` has three updated `last_scanned_ts` values per account by morning.
5. Diff three auto-drafts vs. three real historical replies for tone match (sign-off, sentence length, hedging tics).

## When to escalate to the user

- Composio is disconnected or returns auth errors → stop, do not write state, surface the error.
- More than 20% of messages in a single run hit the `failed` path → likely a tool schema drift; surface the error count and stop after this run.
- Tone profile is still the placeholder after seven days → remind the user in the next interactive session via the SessionStart hook.
