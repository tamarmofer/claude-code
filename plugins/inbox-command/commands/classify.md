---
description: Show what verdict a sender or sample message would receive and why.
argument-hint: <sender-email-or-domain>
allowed-tools: ["Read"]
---

Explain how `$ARGUMENTS` would be classified.

Steps:

1. Load `skills/inbox-command/references/sender-rules.md`.
2. Walk through the rule precedence (exact sender → domain → domain_pattern → subject_keywords).
3. Report which rule would match (if any) and the resulting verdict.
4. If no rule matches, state that the LLM judge would classify based on message content and default to `needs_me` when uncertain.

Output format:

```
Sender: <input>
Matching rule: <rule or "none">
Verdict: <yes | pass | silence | needs_me (default)>
Auto-send: <yes | no, in drafts only>
```
