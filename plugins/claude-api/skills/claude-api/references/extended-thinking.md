# Extended Thinking

Claude 4 Opus and Sonnet models support extended thinking—the model emits `thinking` blocks before producing its response. Thinking is internal reasoning the model uses to plan, verify, and structure complex outputs.

## When to Enable

Enable for:
- Multi-step math, logic, or analytical reasoning
- Complex code generation, refactoring, or debugging
- Agentic loops where decisions matter
- Long-form synthesis from many sources

Skip for:
- Simple Q&A, classification, extraction
- Latency-sensitive interactive UIs (thinking adds tokens and time)
- High-volume batch jobs where cost dominates

## Basic Usage

```python
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[{"role": "user", "content": "Plan a database migration: ..."}],
)

for block in response.content:
    if block.type == "thinking":
        print("[reasoning]", block.thinking)
    elif block.type == "text":
        print("[answer]", block.text)
```

Constraints:
- `budget_tokens` must be **less than** `max_tokens`.
- Thinking tokens count toward output billing at the standard output-token price.
- The model may use fewer thinking tokens than the budget; the budget is a cap.

## Sizing the Budget

| Task complexity | Suggested budget |
|---|---|
| Quick reasoning | 1,024 - 2,048 |
| Standard analysis | 4,096 - 8,000 |
| Complex multi-step | 10,000 - 16,000 |
| Hardest problems (research, long-context synthesis) | 20,000 - 32,000 |

Start small and increase only if answers feel underbaked. Larger budgets don't always improve output—they often just spend more.

## Thinking with Tool Use

Thinking interleaves naturally with tools. Claude can think, call a tool, see the result, think again, call another tool, etc.

```python
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    tools=tools,
    messages=messages,
)
```

When you send `tool_result` blocks back, preserve the original assistant `content` (including thinking blocks) in the conversation history. Removing thinking blocks breaks the model's chain.

## Streaming

Stream thinking alongside text:

```python
with client.messages.stream(
    model="claude-opus-4-7",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=messages,
) as stream:
    for event in stream:
        if event.type == "content_block_delta":
            if event.delta.type == "thinking_delta":
                print("[think]", event.delta.thinking, end="")
            elif event.delta.type == "text_delta":
                print(event.delta.text, end="")
```

For user-facing UIs, render thinking in a collapsed/dimmed region—users want to see *that* the model is reasoning without reading every step.

## "Think" Word Sensitivity

When thinking is **disabled** (no `thinking` parameter), recent Opus/Sonnet models are sensitive to the word "think" and its variants. The word can trigger implicit reasoning patterns that waste tokens or change behavior. Replace with "consider," "evaluate," "decide" in system prompts and user messages.

When thinking is **enabled**, this sensitivity disappears—the model uses thinking blocks for reasoning instead.

## Thinking + Caching

Thinking blocks are part of the assistant turn. When caching conversation history, treat the thinking blocks as cacheable content like any other assistant output. Don't strip thinking from cached prefixes—the model's continuity depends on it.

## Cost Awareness

Thinking is billed as output tokens. Budget conservatively:
- 10,000 thinking tokens on Opus 4.7 ≈ ~$0.15 per call
- Same budget on Sonnet 4.6 ≈ ~$0.03 per call

For agent loops, monitor cumulative `usage.output_tokens` across steps. A runaway loop with thinking enabled costs significantly more than one without.
