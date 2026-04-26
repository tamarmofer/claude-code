---
description: Flip auto-send on for `pass` (recommended first) or `all` (yes + pass). needs_me never auto-sends.
argument-hint: <pass | all>
allowed-tools: ["Read", "Edit"]
---

Update `auto_send` in `skills/inbox-command/references/sender-rules.md` based on `$ARGUMENTS`.

Valid values:

- `pass` → `auto_send: [pass]`
- `all` → `auto_send: [yes, pass]`
- `off` → `auto_send: []`

Anything else: stop and explain valid values.

Steps:

1. Read `sender-rules.md`.
2. If the user is jumping straight to `all` and the current value is `[]`, warn that the recommended path is `pass` first for one to two weeks. Ask for confirmation. If they confirm, proceed.
3. Edit the `auto_send:` line in the YAML block.
4. Confirm the new value and remind them: `needs_me` is never auto-sent regardless of this list.
