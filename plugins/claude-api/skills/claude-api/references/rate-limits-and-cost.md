# Rate Limits and Cost

## Rate Limit Dimensions

Anthropic API enforces three dimensions:

- **RPM** — requests per minute
- **ITPM** — input tokens per minute (includes cache reads at full count toward this limit)
- **OTPM** — output tokens per minute (includes thinking tokens)

Limits scale with usage tier. Tier 1 (default) is low; verified deployment with usage history moves to higher tiers automatically. For enterprise volumes, contact sales.

When throttled, response is `429` with `Retry-After`. The SDKs honor this automatically up to `max_retries`.

## Optimizing Within Limits

If hitting ITPM:
- Enable prompt caching—cached input does count toward ITPM, but if you're throttled on first-time input, caching doesn't help. Reduce prompt size.
- Move high-volume work to Batch API (no rate-limit pressure on synchronous tier).
- Split traffic across multiple workspace API keys if you have separate workloads.

If hitting OTPM:
- Reduce `max_tokens` ceilings—lower bound limits expected output and frees headroom.
- Use smaller models (Haiku) for tasks that don't need Opus/Sonnet.
- Disable extended thinking where it isn't needed.

If hitting RPM:
- Batch multiple user queries into single requests where logic allows.
- Use the Batch API for jobs that can wait.

## Cost Math

Approximate prices per million tokens (verify current pricing on the Anthropic site):

| Model | Input | Output |
|---|---|---|
| Opus 4.7 | $15 | $75 |
| Sonnet 4.6 | $3 | $15 |
| Haiku 4.5 | $0.80 | $4 |

Multipliers:
- Cache write (5m TTL): 1.25× input price
- Cache write (1h TTL): 2× input price
- Cache read: 0.1× input price
- Batch API: 0.5× both input and output
- Thinking tokens: billed at output price

## Prompt Caching Cost Math

For a 10,000-token system prompt on Sonnet 4.6:
- Uncached: 10k × $3/M = $0.03 per call
- Cache write (5m): 10k × $3.75/M = $0.0375 (single write)
- Cache read: 10k × $0.30/M = $0.003 per call

Break-even = (cache write premium) / (savings per read) = $0.0075 / $0.027 ≈ 0.28 calls. So caching pays off on the **first cache hit** (i.e., second total call) at this prompt size.

For 1-hour TTL: break-even = $0.03 / $0.027 ≈ 1.1, so caching pays off on the **second** cache hit. Use 1h only for prefixes hit many times within an hour.

## Batch API Pricing

- 50% off input and output
- Up to 24-hour processing window (most jobs complete in under 1 hour)
- No effect on synchronous RPM/ITPM/OTPM limits
- 100,000 requests max per batch

When to batch:
- Background classification, summarization, extraction
- Bulk data processing
- Eval runs
- Anything where the user isn't waiting

When NOT to batch:
- Interactive UIs
- Conversational agents
- Anything with strict SLA on response time

## Cost Monitoring

Always read `response.usage` and log it. For agent loops, accumulate across steps:

```python
total = {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}
# inside loop:
total["input"] += response.usage.input_tokens
total["output"] += response.usage.output_tokens
total["cache_read"] += response.usage.cache_read_input_tokens or 0
total["cache_write"] += response.usage.cache_creation_input_tokens or 0
```

Set hard cost ceilings on agent loops—a runaway loop with Opus and extended thinking can spend hundreds of dollars per session.
