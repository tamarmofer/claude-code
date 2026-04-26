# Sender Rules

The `inbox-command` skill reads the YAML below as its classification taxonomy. Hard rules win over the LLM judge.

Match precedence (first match wins):
1. `sender:` — exact email address
2. `domain:` — exact domain
3. `domain_pattern:` — glob pattern (e.g. `*.recruiter.com`)
4. `subject_keywords:` — case-insensitive substring match against the subject

`auto_send` controls which verdicts get sent without human review. Default `[]` means drafts only. `needs_me` is never auto-sent regardless of this list.

Note: keys are quoted because `yes` is a YAML 1.1 boolean. Always read this block as YAML 1.1 with the `safe_load` parser; verdict names live as quoted string keys.

```yaml
"yes":
  # Senders the user wants to say yes to. Short affirmative drafts.
  # - sender: ceo@dundeeus.com
  # - domain: stripe.com

"pass":
  # Senders / topics the user wants to politely decline.
  # - subject_keywords: [partnership, sponsorship, "podcast invite", "guest post"]
  # - domain_pattern: "*.recruiter.com"

"silence":
  # Newsletters, no-reply, automated. No draft created.
  - domain_pattern: "noreply.*"
  - domain_pattern: "no-reply.*"
  - subject_keywords: [unsubscribe, "view in browser", "view this email in your browser"]
  - sender_pattern: "*+noreply@*"

auto_send: []   # start at []. After 1-2 weeks: ["pass"]. Later: ["yes", "pass"]. needs_me NEVER sends.
```
