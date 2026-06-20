# Effort Parameter

**The effort parameter is GA on Opus 4.8 — no beta header required.** It lives inside `output_config`, not at the top level. Default to `high` during migration; use `xhigh` for coding and agentic work.

## Overview

Effort controls how eagerly Claude spends tokens. It affects all tokens: thinking, text responses, and tool calls. On Opus 4.8, lower effort means fewer, more-consolidated tool calls, less preamble, and terser confirmations.

| Effort | Use Case |
|--------|----------|
| `max` | Hardest, latency-insensitive tasks where correctness dominates cost; can overthink |
| `xhigh` | Best for most coding and agentic use cases (the default in Claude Code) |
| `high` | Recommended default and minimum for most intelligence-sensitive work |
| `medium` | Cost/latency-sensitive work that can trade off some intelligence |
| `low` | Short, scoped, latency-sensitive tasks; significant token savings |

`xhigh` and `max` are available on Opus 4.6 and later (and Sonnet 4.6); they error on Sonnet 4.5 / Haiku 4.5.

## Implementation

No beta header. Combine with adaptive thinking for the best cost/quality tradeoff.

**Python SDK:**
```python
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    thinking={"type": "adaptive"},
    output_config={
        "effort": "high"  # low | medium | high | xhigh | max
    },
    messages=[...]
)
```

**TypeScript SDK:**
```typescript
const response = await client.messages.create({
  model: "claude-opus-4-8",
  max_tokens: 16000,
  thinking: { type: "adaptive" },
  output_config: {
    effort: "high"  // low | medium | high | xhigh | max
  },
  messages: [...]
});
```

**Raw API:**
```json
{
  "model": "claude-opus-4-8",
  "max_tokens": 16000,
  "thinking": { "type": "adaptive" },
  "output_config": {
    "effort": "high"
  },
  "messages": [...]
}
```

## Effort replaces the thinking budget

On Opus 4.8 there is no `budget_tokens` — `thinking: {"type": "enabled", "budget_tokens": N}` returns a 400. Control thinking depth with `effort` plus adaptive thinking (`thinking: {"type": "adaptive"}`). There is no exact 1:1 mapping from an old token budget to an effort level; pick by use case from the table above and tune.

## Recommendations

1. Start at `high` and sweep `medium` / `high` / `xhigh` on your own eval set — the intelligence ↔ latency ↔ cost relationship isn't monotonic, and higher effort up front often reduces total turns and cost on agentic work.
2. Use `xhigh` for coding and agentic loops; pair with a generous `max_tokens` (start at 64K with streaming).
3. Use `medium` or `low` for routine, high-volume, or latency-sensitive queries.
4. Reserve `max` for extremely hard, latency-insensitive tasks.
