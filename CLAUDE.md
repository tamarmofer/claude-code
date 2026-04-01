# CLAUDE.md

This file provides guidance for AI assistants working in this repository.

## Repository Overview

This is the official **Claude Code** repository -- an agentic coding tool that lives in the terminal, IDE, and web. The repo contains the plugin ecosystem, CI/CD automation, examples, and community infrastructure. The core CLI source is published separately via npm (`@anthropic-ai/claude-code`).

## Repository Structure

```
.claude/commands/       # Root-level slash commands (commit-push-pr, dedupe, triage-issue)
.claude-plugin/         # Plugin marketplace registry (marketplace.json)
.devcontainer/          # Dev container setup (Dockerfile, devcontainer.json)
.github/workflows/      # 12 CI/CD workflows for issue triage, deduplication, lifecycle
examples/
  hooks/                # Hook implementation examples (e.g., bash_command_validator_example.py)
  settings/             # Settings templates (lax, strict, bash-sandbox)
plugins/                # 14 official plugins (see Plugin Architecture below)
scripts/                # Automation scripts (TypeScript + Shell)
```

## Plugin Architecture

Each plugin lives under `plugins/<name>/` and follows a standard layout:

```
plugin-name/
  .claude-plugin/plugin.json   # Plugin metadata (name, version, description)
  commands/                    # Slash commands (*.md with YAML frontmatter)
  agents/                      # Autonomous agents (*.md with YAML frontmatter)
  skills/                      # Reusable skill definitions
  hooks/                       # Event handlers (PreToolUse, Stop, SessionStart, etc.)
  README.md                    # Plugin documentation
```

### Official Plugins

| Plugin | Purpose |
|---|---|
| `feature-dev` | Structured 7-phase feature development workflow |
| `code-review` | Automated PR review with parallel agents and confidence scoring |
| `agent-sdk-dev` | Claude Agent SDK application creation and verification |
| `plugin-dev` | Toolkit for developing Claude Code plugins |
| `pr-review-toolkit` | 6 specialized review agents (comments, tests, errors, types, quality, simplification) |
| `commit-commands` | Git workflow automation (/commit, /commit-push-pr, /clean_gone) |
| `hookify` | Markdown-based hook creation without code |
| `security-guidance` | PreToolUse hooks for security pattern detection |
| `frontend-design` | Guides for polished, non-generic UI design |
| `ralph-wiggum` | Self-referential AI loops for iterative development |
| `explanatory-output-style` | Educational insights hook |
| `learning-output-style` | Interactive learning mode hook |
| `claude-opus-4-5-migration` | Model migration automation |

## Command & Agent File Format

### Commands (Slash Commands)

```yaml
---
description: User-facing description
argument-hint: Optional argument description
allowed-tools: Bash(*), Grep(*), Read(*)   # Permission restrictions
---

# Markdown body with instructions for Claude
```

### Agents

```yaml
---
name: agent-name
description: What the agent does
tools: Glob, Grep, Read, Bash, WebFetch
model: haiku|sonnet|opus
color: yellow
---

# Agent system prompt and instructions
```

## CI/CD Workflows

Located in `.github/workflows/`:

| Workflow | Trigger | Purpose |
|---|---|---|
| `claude.yml` | @claude mentions | Main Claude Code integration |
| `claude-dedupe-issues.yml` | Issue events | Auto-deduplicate issues |
| `claude-issue-triage.yml` | Issue events | Auto-label and triage issues |
| `auto-close-duplicates.yml` | Label changes | Close confirmed duplicates |
| `lock-closed-issues.yml` | Scheduled | Lock inactive closed issues |
| `non-write-users-check.yml` | Workflow dispatch | Prevent unauthorized access |
| `issue-opened-dispatch.yml` | Issue opened | Route new issues |
| `log-issue-events.yml` | Issue events | Track issue lifecycle |
| `sweep.yml` | Scheduled | Code cleanup automation |

## Scripts

Located in `scripts/`:

- `auto-close-duplicates.ts` -- Duplicate issue closure automation
- `backfill-duplicate-comments.ts` -- Backfill missing duplicate comments
- `comment-on-duplicates.sh` -- Shell wrapper for duplicate commenting
- `edit-issue-labels.sh` -- Label management utility
- `gh.sh` -- Restricted GitHub CLI wrapper
- `issue-lifecycle.ts` -- Issue state management
- `lifecycle-comment.ts` -- Lifecycle comment automation
- `sweep.ts` -- Code cleanup automation

## Development Environment

### DevContainer

The `.devcontainer/` provides a ready-to-use environment:
- **Base**: Node.js 20 with ZSH (Powerlevel10k)
- **Tools**: git, gh (GitHub CLI), jq, fzf, vim, delta
- **Networking**: iptables/ipset support (NET_ADMIN, NET_RAW)
- **Memory**: `NODE_OPTIONS=--max-old-space-size=4096`

### VS Code Extensions (DevContainer)

- `anthropic.claude-code` -- Claude Code extension
- `dbaeumer.vscode-eslint` -- ESLint
- `esbenp.prettier-vscode` -- Prettier (default formatter, format on save)
- `eamodio.gitlens` -- GitLens

## Settings Configuration

Three-level hierarchy (most specific wins):
1. **Project**: `.claude/settings.json`
2. **Organization**: `managed-settings.json` (enterprise)
3. **Global**: User home directory

Example configurations in `examples/settings/`:
- `settings-lax.json` -- Minimal restrictions
- `settings-strict.json` -- Enterprise-grade security
- `settings-bash-sandbox.json` -- Sandboxed bash execution

## Key Conventions

### When Adding a New Plugin

1. Create the plugin directory under `plugins/<name>/`
2. Include `.claude-plugin/plugin.json` with metadata
3. Add commands, agents, skills, and hooks as needed using YAML frontmatter format
4. Write a `README.md` with overview, features, usage, and troubleshooting
5. Register the plugin in `.claude-plugin/marketplace.json`

### When Writing Commands or Agents

- Use YAML frontmatter for metadata (description, tools, model, etc.)
- Specify `allowed-tools` to restrict permissions appropriately
- Choose the right model tier: `haiku` for fast/simple, `sonnet` for balanced, `opus` for complex
- Use `color` in agents for terminal output differentiation

### When Writing Hooks

- Hooks respond to events: `PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`
- Keep hooks simple and focused on pattern matching
- Test hooks before deployment
- Use the `hookify` plugin for markdown-based hook creation

### Architectural Patterns

- **Parallel agent execution**: Launch multiple independent agents simultaneously
- **Confidence scoring**: Filter issues by confidence threshold (typically 80+) to reduce false positives
- **Progressive disclosure**: Lean core docs, detailed references, working examples
- **Frontmatter-driven config**: All commands, agents, and skills use YAML frontmatter in markdown

## Git Workflow

- **Main branch**: `main` (protected)
- **Flow**: Feature branches -> PR -> Review -> Merge
- **Commit messages**: Clear, descriptive, focusing on "why" not "what"

## Security

- Report vulnerabilities via [HackerOne](https://hackerone.com/anthropic-vdp)
- The `security-guidance` plugin provides PreToolUse hooks that warn about common vulnerabilities (command injection, XSS, eval, pickle deserialization, os.system)
- Never commit secrets or credentials; the settings system supports `deniedMcpServers` and fine-grained permission rules
