---
name: claude-api
description: This skill should be used when the user asks to "build a Claude app", "call the Claude API", "use the Anthropic SDK", "add prompt caching", "use Claude tool use", "enable extended thinking", "stream Claude responses", "implement Claude with vision", or any task involving the Anthropic Python/TypeScript SDK or direct HTTP calls to api.anthropic.com. Covers model selection, prompt caching, tool use, extended thinking, streaming, batch, files, vision, citations, and migration between Claude model versions.
version: 0.1.0
---

# Claude API Development

Build, debug, and optimize applications using the Claude API. This skill targets the Anthropic Python SDK (`anthropic`), the TypeScript SDK (`@anthropic-ai/sdk`), and direct REST calls to `https://api.anthropic.com/v1/messages`.

When working in an existing codebase, follow the patterns and SDK version already in use—do not rewrite working code to match templates in this skill.

## Model Selection

Default to the latest models in the Claude 4 family. Model IDs:

| Family | Latest | Use for |
|---|---|---|
| Opus | `claude-opus-4-7` | Hardest reasoning, agentic loops, complex coding, long-context analysis |
| Sonnet | `claude-sonnet-4-6` | Default workhorse: balanced speed, cost, and quality |
| Haiku | `claude-haiku-4-5-20251001` | High-volume, low-latency classification, extraction, routing |

For migrations between specific model versions (e.g., 4.5 → 4.7), see `references/migrations.md`.

## Minimal Call

**Python (anthropic SDK):**
```python
from anthropic import Anthropic

client = Anthropic()  # reads ANTHROPIC_API_KEY
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude."}],
)
print(response.content[0].text)
```

**TypeScript:**
```ts
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();  // reads ANTHROPIC_API_KEY
const response = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello, Claude." }],
});
console.log(response.content[0].text);
```

## Prompt Caching (Always Enable for Repeated Context)

Prompt caching cuts cost ~90% and latency significantly when the same prefix is reused across requests. **Default to enabling it on every system prompt, tool definition block, or long document used more than once.**

Add `cache_control: {type: "ephemeral"}` to the last block of any cached prefix:

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": LONG_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }
    ],
    messages=[{"role": "user", "content": user_query}],
)
print(response.usage)  # cache_creation_input_tokens, cache_read_input_tokens
```

Rules:
- Cache breakpoints are added at the END of blocks; up to 4 breakpoints per request.
- Default TTL is 5 minutes; pass `"ttl": "1h"` for one-hour caching (beta header required—see `references/prompt-caching.md`).
- Cached prefixes must be **identical byte-for-byte**. Don't interpolate user input into a cached block.

For detailed patterns (system + tools + document caching, multi-turn conversation caching), see `references/prompt-caching.md`.

## Tool Use

Define tools with JSON Schema input, receive `tool_use` blocks in responses, send `tool_result` blocks back:

```python
tools = [{
    "name": "get_weather",
    "description": "Get current weather for a location.",
    "input_schema": {
        "type": "object",
        "properties": {"location": {"type": "string"}},
        "required": ["location"],
    },
}]

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "Weather in Tokyo?"}],
)

if response.stop_reason == "tool_use":
    tool_use = next(b for b in response.content if b.type == "tool_use")
    result = call_my_tool(tool_use.name, tool_use.input)
    followup = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=tools,
        messages=[
            {"role": "user", "content": "Weather in Tokyo?"},
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": result,
            }]},
        ],
    )
```

Tool definitions are excellent caching candidates—add `cache_control` to the last tool. See `references/tool-use.md` for parallel tool calls, `tool_choice` control, error handling, and the loop pattern.

## Extended Thinking

Opus and Sonnet 4.x support extended thinking—the model produces a `thinking` block before the response. Enable it for complex reasoning, math, multi-step coding:

```python
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[{"role": "user", "content": "Plan a refactor of this codebase: ..."}],
)
# response.content includes ThinkingBlock items followed by TextBlock items
```

Notes:
- `budget_tokens` must be less than `max_tokens`.
- Thinking tokens count toward output token billing.
- When thinking is enabled, the model is **less sensitive** to the word "think" in prompts. When disabled, replace "think" with "consider"/"evaluate" to avoid triggering implicit reasoning.

For interleaved thinking with tool use and streaming-during-thinking, see `references/extended-thinking.md`.

## Streaming

Stream responses for interactive UIs:

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Tell me a story."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    final = stream.get_final_message()
```

Event types include `message_start`, `content_block_start`, `content_block_delta` (with `text_delta`, `thinking_delta`, `input_json_delta`), `content_block_stop`, `message_delta`, `message_stop`. The SDK handles event parsing; only drop to raw events for partial-tool-call streaming or custom UIs.

## Vision

Pass images as base64-encoded blocks or URLs:

```python
import base64
with open("chart.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": image_data,
            }},
            {"type": "text", "text": "Describe this chart."},
        ],
    }],
)
```

Supported: `image/jpeg`, `image/png`, `image/gif`, `image/webp`. Max 20 images per request; resize to ≤1568px on the longest edge for cost efficiency.

## Files

For PDFs and large documents, use the Files API to upload once and reference by `file_id` across many requests:

```python
file = client.beta.files.upload(file=("report.pdf", open("report.pdf", "rb"), "application/pdf"))
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    betas=["files-api-2025-04-14"],
    messages=[{
        "role": "user",
        "content": [
            {"type": "document", "source": {"type": "file", "file_id": file.id}},
            {"type": "text", "text": "Summarize this report."},
        ],
    }],
)
```

Pair with prompt caching on the document block for repeated queries against the same file.

## Batch

For workloads where latency doesn't matter, the Message Batches API offers 50% off and processes up to 100,000 requests per batch:

```python
batch = client.messages.batches.create(
    requests=[
        {"custom_id": f"req_{i}", "params": {
            "model": "claude-sonnet-4-6",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }} for i, prompt in enumerate(prompts)
    ]
)
# Poll batch.id, then retrieve results.
```

## Errors and Retries

The SDKs handle retries with exponential backoff by default for 429 and 5xx. Common error classes:

- `RateLimitError` (429): respect `Retry-After`; consider raising tier or using batch.
- `OverloadedError` (529): retry with backoff; consider failover to a different model.
- `APIStatusError` (400): inspect `body.error.message`; usually a malformed request.
- `APIConnectionError`: network; retry.

Set `max_retries=3` and a sensible timeout on the client.

## Security

- **Never embed `ANTHROPIC_API_KEY` in client-side code.** Proxy through your backend.
- Validate and sanitize tool inputs before executing—`tool_use` blocks are model output, not trusted.
- For agent loops, set hard step limits and watch `usage.input_tokens` cumulatively to bound cost.

## Migrations

When upgrading model versions: change the model ID, re-test representative prompts, soften aggressive imperatives (`MUST`/`ALWAYS`) if tool overtriggering appears, and verify caching breakpoints still match byte-for-byte. See `references/migrations.md` for version-by-version notes.

## Additional Resources

- `references/prompt-caching.md` — system + tools + document caching, multi-turn caching, 1h TTL, breakpoint strategy
- `references/tool-use.md` — parallel tool calls, `tool_choice`, error handling, the agentic loop pattern
- `references/extended-thinking.md` — interleaved thinking with tool use, thinking with streaming, budget sizing
- `references/migrations.md` — version-by-version migration notes (Sonnet 4.5 → 4.6, Opus 4.5 → 4.6 → 4.7, retired model replacements)
- `references/rate-limits-and-cost.md` — ITPM/OTPM tiers, batch pricing, prompt caching cost math
