---
name: claude-model-migration
description: Migrate prompts and code to the current Claude generation (Claude Opus 4.8). Use when the user wants to update their codebase, prompts, or API calls to a newer Claude model — e.g. "migrate to Opus 4.8", "upgrade my model", "move off Sonnet 4.5/Opus 4.1/4.5/4.6/4.7". Handles model string updates and prompt adjustments for known Opus 4.8 behavioral differences. Does NOT migrate Haiku, and does NOT target Claude Fable 5 unless the user explicitly asks for Fable.
---

# Claude Model Migration Guide

One-shot migration to the current Opus-tier model, **Claude Opus 4.8**, from Sonnet 4.x, Opus 4.0/4.1/4.5/4.6, or Opus 4.7. Opus 4.8 keeps the same request surface as Opus 4.7 (no new breaking changes) — coming from 4.7 it is essentially a model-string swap plus optional prompt re-tuning; coming from 4.6 or older you also apply the 4.7 breaking changes below.

> **Scope first.** If the user didn't name a specific file, directory, or file list, ask which scope to migrate before editing anything. Phrases like "my codebase", "my project", or "everywhere" are ambiguous about *where* — confirm first.

> **Target model.** Default to `claude-opus-4-8`. Only target Claude Fable 5 (`claude-fable-5`) if the user explicitly asks for Fable — it has a different API surface and above-Opus pricing. Do **not** migrate Haiku models.

## Migration Workflow

1. Confirm the migration scope with the user (see note above).
2. Search the codebase for model strings and API calls.
3. Update model strings to Opus 4.8 (see platform-specific strings below).
4. Apply the breaking-change checklist below (some items 400 if missed).
5. Remove GA-now beta headers (`effort-2025-11-24`, `interleaved-thinking-2025-05-14`, etc.).
6. Summarize all changes made.
7. Tell the user: "If you encounter any issues with Opus 4.8, let me know and I can help adjust your prompts."

## Model String Updates

Identify which platform the codebase uses, then replace model strings accordingly.

### Target Model Strings (Opus 4.8)

| Platform | Opus 4.8 Model String |
|----------|----------------------|
| Anthropic API (1P) | `claude-opus-4-8` |
| Claude Platform on AWS | `claude-opus-4-8` |
| AWS Bedrock | `anthropic.claude-opus-4-8` |
| Google Vertex AI | `claude-opus-4-8` |
| Azure / Microsoft Foundry | `claude-opus-4-8` |

Use the **bare** alias — do **not** append a date suffix (`claude-opus-4-8-20251101` and similar will 404). Bedrock keeps the `anthropic.` prefix; Vertex/Foundry/1P/Claude-Platform-on-AWS use the bare ID.

### Source Model Strings to Replace

| Source Model | Anthropic API (1P) | AWS Bedrock | Google Vertex AI |
|--------------|-------------------|-------------|------------------|
| Sonnet 4.0 | `claude-sonnet-4-20250514` | `anthropic.claude-sonnet-4-20250514-v1:0` | `claude-sonnet-4@20250514` |
| Sonnet 4.5 | `claude-sonnet-4-5` | `anthropic.claude-sonnet-4-5` | `claude-sonnet-4-5` |
| Opus 4.1 | `claude-opus-4-1` | `anthropic.claude-opus-4-1` | `claude-opus-4-1` |
| Opus 4.5 | `claude-opus-4-5` | `anthropic.claude-opus-4-5` | `claude-opus-4-5` |
| Opus 4.6 | `claude-opus-4-6` | `anthropic.claude-opus-4-6` | `claude-opus-4-6` |
| Opus 4.7 | `claude-opus-4-7` | `anthropic.claude-opus-4-7` | `claude-opus-4-7` |

**Do NOT migrate**: any Haiku models (e.g., `claude-haiku-4-5`), or Sonnet code the user wants to keep on Sonnet — Opus 4.8 is the Opus-tier target, not a Sonnet replacement.

## Breaking Changes (apply as code edits — these 400 if missed)

These are the changes that turn into a 400 error on Opus 4.8. Apply only the ones the source code actually uses; coming straight from Opus 4.7, the code is usually already clean.

1. **Manual extended thinking is removed.** `thinking: {"type": "enabled", "budget_tokens": N}` returns a 400 on Opus 4.7 and 4.8. Replace with `thinking: {"type": "adaptive"}` and control depth with the effort parameter (see `references/effort.md`). Adaptive thinking is **off** when the `thinking` field is omitted — set it explicitly to enable. Delete all `budget_tokens` plumbing.

2. **Sampling parameters are removed.** `temperature`, `top_p`, and `top_k` return a 400 on Opus 4.7 and 4.8. Remove them; steer behavior with prompting instead.

3. **Last-assistant-turn prefills are removed.** A `messages` array ending in `role: "assistant"` returns a 400. Replace with structured outputs (`output_config.format` with a `json_schema`) or a system-prompt instruction. (Few-shot assistant turns *earlier* in the conversation are still fine.)

4. **`output_format` → `output_config.format`.** The top-level `output_format` parameter is deprecated API-wide; use `output_config.format`.

5. **Stream for large `max_tokens`.** Non-streaming requests risk SDK HTTP timeouts above ~16K output; Opus 4.8 supports up to 128K output via streaming. Use `messages.stream()` / `.get_final_message()` for large outputs.

## Silent default change to check

**Thinking content is omitted by default.** On Opus 4.7/4.8, `thinking` blocks are returned with an empty `thinking` field unless you opt in. If the code surfaces reasoning to a UI or log, add `thinking: {"type": "adaptive", "display": "summarized"}`. The block-field name is unchanged (`block.thinking`).

## Beta headers to remove (now GA)

Remove these and switch `client.beta.messages.create(...)` back to `client.messages.create(...)`:

- `effort-2025-11-24` — the effort parameter is GA (no header needed).
- `interleaved-thinking-2025-05-14` — adaptive thinking interleaves automatically.
- `fine-grained-tool-streaming-2025-05-14`, `token-efficient-tools-2025-02-19`, `output-128k-2025-02-19` — built in to Claude 4+.

## Effort & token re-baselining

- Opus 4.8 supports `output_config.effort` of `low` | `medium` | `high` | `xhigh` | `max` (GA, no beta header). Default to `high`; use `xhigh` for coding/agentic work; reserve `max` for the hardest latency-insensitive tasks. See `references/effort.md`.
- Opus 4.7/4.8 count tokens differently from Opus 4.6 and earlier — re-run `count_tokens()` on representative prompts and give `max_tokens` / compaction triggers extra headroom. Do not apply a blanket multiplier. (Coming from Opus 4.7, token counts are roughly unchanged.)
- Opus 4.8 provides a 1M context window at standard API pricing — no long-context premium.

## Prompt Adjustments

Opus 4.8 has known behavioral differences from earlier models. **Only apply these fixes if the user explicitly requests them or reports a specific issue.** By default, just update model strings and the breaking-change items above.

**Integration guidelines**: When adding snippets, integrate them thoughtfully — use XML tags, match the existing prompt's style and structure, and place additions in logical locations. See `references/prompt-snippets.md` for the full text of each snippet, covering:

1. **Tool overtriggering / undertriggering** — 4.8's tool triggering is surface-dependent; soften aggressive language, or add explicit "call this when…" triggers (in tool descriptions too) if it under-reaches for search, subagents, memory, or custom tools.
2. **Over-engineering prevention** — 4.8 may add unrequested files/abstractions, especially at higher effort.
3. **Code exploration** — encourage reading files before proposing fixes.
4. **Narration & autonomy** — 4.8 narrates more than 4.7 and asks more often on minor decisions; add a silence-default and small-decisions-don't-ask guidance if needed.
5. **Frontend design quality** — anti-"AI slop" snippet.

## Reference

- `references/effort.md` — the effort parameter (GA), levels, and recommended settings.
- `references/prompt-snippets.md` — full text of each prompt snippet to add.
