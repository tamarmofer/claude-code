# claude-api

Build, debug, and optimize applications using the Claude API and Anthropic SDKs (Python `anthropic`, TypeScript `@anthropic-ai/sdk`, or direct HTTP).

## What this plugin provides

A single skill, `claude-api`, that covers:

- Model selection (Opus 4.7, Sonnet 4.6, Haiku 4.5)
- Minimal-call patterns in Python and TypeScript
- **Prompt caching** (enabled by default for repeated prefixes)
- Tool use and the agentic loop
- Extended thinking
- Streaming, vision, files, batch
- Error handling and retries
- Migrations between Claude model versions
- Rate limits and cost optimization

## Triggers

This skill loads when the user asks to build a Claude app, call the Claude API, use the Anthropic SDK, add prompt caching, use tool use, enable extended thinking, stream Claude responses, or migrate between Claude model versions.

## Related plugins

- `claude-opus-4-5-migration` — narrow skill specifically for migrating to Opus 4.5
