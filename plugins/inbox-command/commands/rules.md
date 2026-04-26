---
description: Open the sender taxonomy for editing.
allowed-tools: ["Read", "Edit"]
---

Open `skills/inbox-command/references/sender-rules.md` for editing.

Walk the user through:

1. The current contents — list which entries are under `yes:`, `pass:`, `silence:`.
2. Ask what they want to add, change, or remove.
3. Make the edit. Preserve the YAML structure inside the fenced block.
4. Remind them: `auto_send: []` means drafts only. `needs_me` is never auto-sent.

Match precedence the user should know about: `sender` > `domain` > `domain_pattern` > `subject_keywords`. First match wins.
