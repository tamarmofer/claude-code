# Tool Use

Claude's tool use is the foundation of agentic applications. The pattern: define tools, send messages, receive `tool_use` blocks, execute them, send `tool_result` blocks back, repeat until `stop_reason == "end_turn"`.

## Tool Definitions

Each tool needs `name`, `description`, and `input_schema` (JSON Schema):

```python
tools = [
    {
        "name": "search_web",
        "description": "Search the public web. Use when the user asks about current events or facts that may have changed since training.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        },
    },
]
```

The `description` is the most important field. It tells Claude *when* to use the tool. Be specific. Include negative examples ("Do not use for X").

## The Loop

```python
messages = [{"role": "user", "content": "What's the weather in Tokyo?"}]

while True:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        tools=tools,
        messages=messages,
    )
    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason == "end_turn":
        break
    if response.stop_reason != "tool_use":
        break  # unexpected; investigate

    tool_results = []
    for block in response.content:
        if block.type != "tool_use":
            continue
        try:
            result = dispatch_tool(block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })
        except Exception as e:
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(e),
                "is_error": True,
            })
    messages.append({"role": "user", "content": tool_results})
```

## Parallel Tool Calls

Claude can request multiple tools in one response. The loop above handles this naturally by iterating over all `tool_use` blocks before sending results. Always include a `tool_result` for **every** `tool_use` in the prior turn—missing results cause errors.

## `tool_choice`

Control whether/which tool Claude calls:

```python
# Default — Claude decides
tool_choice = {"type": "auto"}

# Force any tool call
tool_choice = {"type": "any"}

# Force a specific tool
tool_choice = {"type": "tool", "name": "search_web"}

# Disable tools for this turn
tool_choice = {"type": "none"}
```

Common patterns:
- `auto` + good descriptions for most agents.
- `tool` + specific tool for structured extraction (force `extract_entities` to always run).
- Disable parallel calls when tools have side effects you want serialized: `{"type": "auto", "disable_parallel_tool_use": true}`.

## Caching Tools

Tool definitions are excellent cache candidates—long, identical across requests. Add `cache_control` to the last tool:

```python
tools = [
    *first_n_tools,
    {**last_tool, "cache_control": {"type": "ephemeral"}},
]
```

## Streaming Tool Use

When streaming, tool input arrives as `input_json_delta` events. The SDK aggregates into the final `input` object automatically via `stream.get_final_message()`. For UIs that want to show partial tool input, parse `partial_json` from each delta.

## Tool-Result Errors

Pass `is_error: true` and put an error string in `content` to signal failure:

```python
{"type": "tool_result", "tool_use_id": "...", "content": "Connection refused", "is_error": true}
```

Claude will typically retry with adjusted inputs or explain the failure to the user.

## Anti-patterns

- **Hidden tools in system prompt**: don't describe tools in the system prompt instead of `tools`. The model sees them differently.
- **Imperative tool descriptions**: write descriptions about *when* the tool is appropriate, not *how* to call it. Schema covers the how.
- **Forgetting `is_error`**: returning an error string without `is_error: true` lets Claude treat it as a valid result.
- **Step explosion**: unbounded loops can burn through tokens. Always set a max-step counter.
- **Mutating tool order**: changing the order of tools across requests breaks prompt caching.

## Server Tools

Claude offers built-in server-side tools that execute on Anthropic's infrastructure (web search, code execution, computer use). These don't need client-side dispatch—Claude calls them, gets results, and you only see the final synthesis. See platform docs for current availability and pricing.
