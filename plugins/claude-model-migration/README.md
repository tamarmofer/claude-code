# Claude Model Migration Plugin

Migrate your code and prompts to the current Claude generation — **Claude Opus 4.8** — from Sonnet 4.x or Opus 4.1/4.5/4.6/4.7.

## Overview

This skill updates your code and prompts to be compatible with Opus 4.8. It automates the migration process, handling model strings, removed parameters (`budget_tokens`, sampling params, assistant prefills), now-GA beta headers, and other configuration details. If you run into any issues with Opus 4.8 after migration, you can continue using this skill to adjust your prompts.

It targets `claude-opus-4-8` by default. It does not migrate Haiku models, and it only targets Claude Fable 5 if you explicitly ask for Fable.

## Usage

```
"Migrate my codebase to Opus 4.8"
```

## Learn More

Refer to our [prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices) for best practices on prompting Claude models.

## Authors

William Hu (whu@anthropic.com)
