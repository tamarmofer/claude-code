# Prompt Caching

Prompt caching is the highest-impact optimization for almost any Claude application. **Enable it by default** when a prefix is reused across more than one request. Typical savings: 90% cost reduction on cached tokens, 50-80% latency reduction on time-to-first-token.

## How It Works

Add `cache_control: {"type": "ephemeral"}` to the **last block** of any cacheable prefix. Up to 4 cache breakpoints per request. Each breakpoint marks the end of a cacheable prefix; everything before it (including earlier breakpoints) is part of that prefix.

The cache is keyed by exact prefix content. **One byte different = cache miss.** Don't interpolate user input or timestamps into cached blocks.

## Default TTL: 5 Minutes

Default cache TTL is 5 minutes from last hit. Each cache hit refreshes the TTL.

## 1-Hour TTL (Beta)

Pass the beta header and `ttl` parameter for longer caching:

```python
response = client.beta.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    betas=["extended-cache-ttl-2025-04-11"],
    system=[
        {
            "type": "text",
            "text": LONG_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral", "ttl": "1h"},
        }
    ],
    messages=[{"role": "user", "content": query}],
)
```

1-hour cache writes cost more than 5-minute writes but save on rewrite traffic for very long-lived prefixes (e.g., daily-refresh document caches).

## What's Cacheable

In order of typical reuse value:

1. **System prompts** (especially long ones with rules, examples, schemas)
2. **Tool definitions** (`tools` array)
3. **Long documents** in the first user message (`document` or `text` blocks)
4. **Few-shot examples** in messages

## Breakpoint Strategy

The 4 breakpoints belong on the boundaries of independently-reused content. Common layout:

```python
client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system=[
        {"type": "text", "text": STABLE_RULES,
         "cache_control": {"type": "ephemeral"}},          # breakpoint 1
        {"type": "text", "text": DAILY_REFRESHED_CONTEXT,
         "cache_control": {"type": "ephemeral"}},          # breakpoint 2
    ],
    tools=[
        *TOOL_DEFINITIONS,
        # cache_control on the last tool definition
    ],
    messages=[
        {"role": "user", "content": [
            {"type": "document", "source": ..., 
             "cache_control": {"type": "ephemeral"}},      # breakpoint 3
            {"type": "text", "text": user_query},
        ]},
    ],
)
```

## Multi-Turn Conversation Caching

Conversation history caches well if you cache **the last user/assistant turn** of the prior conversation:

```python
messages = [
    *prior_turns,
    {"role": "assistant", "content": [
        {"type": "text", "text": last_assistant_text,
         "cache_control": {"type": "ephemeral"}},
    ]},
    {"role": "user", "content": new_user_message},
]
```

Each new turn writes a fresh breakpoint at the new end-of-conversation, and reads the previous prefix from cache.

## Verifying It Works

Inspect `response.usage`:

```python
print(response.usage.cache_creation_input_tokens)  # tokens written to cache this request
print(response.usage.cache_read_input_tokens)      # tokens read from cache (90% cheaper)
print(response.usage.input_tokens)                  # non-cached input tokens
```

On a successful cache hit, `cache_read_input_tokens` will equal your cached-prefix size and `input_tokens` will be small. If you see writes on every request, your prefix has drift—a header, timestamp, or user input is varying.

## Cost Math

| Token type | Cost vs. base input |
|---|---|
| Regular input | 1× |
| Cache write (5m TTL) | 1.25× |
| Cache write (1h TTL) | 2× |
| Cache read | 0.1× |

Break-even: cache pays off on the second hit at 5m TTL, on the third hit at 1h TTL.

## Pitfalls

- **Cache misses from drift**: a single varying byte (clock, request ID, user name) invalidates the cache.
- **Cache before user input**: never put `cache_control` *after* a user-input block within a turn—the user input changes per request and breaks the cache.
- **Tool reordering**: changing the order of tool definitions breaks the cache. Sort tools deterministically.
- **System prompt injection**: don't dynamically build the system prompt per request. Build it once at startup.
