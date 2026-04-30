# CLAUDE.md

Guidance for AI assistants working in this repository.

## What this repo is (and isn't)

This is the **public-facing repository for Claude Code** (`anthropics/claude-code`). It is **not** the source code for the Claude Code CLI itself — that is closed-source. This repo hosts:

- A bundled plugin marketplace (`plugins/`) with 13 official plugins
- A devcontainer reference setup (`.devcontainer/`)
- Example settings and hooks (`examples/`)
- GitHub issue-automation workflows and scripts (`.github/workflows/`, `scripts/`)
- The user-facing `CHANGELOG.md` and `README.md`
- The issue tracker (bug reports, feature requests, etc.)

There is no application code to build, no test suite to run, no `package.json` at the root. Most "development" here is editing markdown, JSON, shell scripts, and TypeScript automation.

## Repository layout

```
.
├── .claude/commands/        # Repo-local slash commands (commit-push-pr, dedupe, triage-issue)
├── .claude-plugin/
│   └── marketplace.json     # Marketplace manifest — register every plugin here
├── .devcontainer/           # Reference Docker dev environment with firewall init
├── .github/
│   ├── ISSUE_TEMPLATE/      # bug, feature, docs, model behavior templates
│   └── workflows/           # Issue triage, dedupe, sweep, lifecycle automation
├── .vscode/extensions.json  # Recommended VS Code extensions
├── CHANGELOG.md             # User-facing CLI changelog (very large; updated by bot)
├── examples/
│   ├── hooks/               # Sample hook scripts (e.g. bash command validator)
│   └── settings/            # Reference settings.json for orgs (lax/strict/sandbox)
├── plugins/                 # 13 bundled plugins (see plugins/README.md)
├── scripts/                 # GitHub issue automation (Bun TS + bash)
├── Script/                  # PowerShell launcher for the devcontainer (Windows)
└── README.md
```

## Plugins

Each plugin under `plugins/<name>/` follows this structure:

```
plugins/<name>/
├── .claude-plugin/plugin.json   # Required metadata: name, description, version, author
├── README.md                    # Required user-facing docs
├── commands/*.md                # Slash commands (frontmatter: allowed-tools, description)
├── agents/*.md                  # Subagent definitions
├── skills/*/SKILL.md            # Agent Skills with progressive-disclosure structure
├── hooks/                       # Hook scripts + hooks.json registration
└── .mcp.json                    # Optional MCP server config
```

**When adding a new plugin:**
1. Create the directory under `plugins/`.
2. Add `plugins/<name>/.claude-plugin/plugin.json` (required) and `README.md`.
3. **Register it in `.claude-plugin/marketplace.json`** — without this entry, it won't be discoverable. Include `name`, `description`, `version`, `author`, `source` (`./plugins/<name>`), and `category` (`development`, `productivity`, `learning`, `security`).
4. Update the plugin table in `plugins/README.md`.
5. Use `${CLAUDE_PLUGIN_ROOT}` in hook commands so paths resolve regardless of install location (see `plugins/hookify/hooks/hooks.json` for the canonical pattern).

Note: `plugins/plugin-dev/` is the only plugin without a `.claude-plugin/plugin.json` — it's a skill/command bundle for plugin authors and is intentionally not in the marketplace manifest.

## Repo-local slash commands (`.claude/commands/`)

These run when working inside this repo:

- `/commit-push-pr` — branch off main, commit, push, open a PR (single-message tool batch).
- `/dedupe <issue-url>` — find up to 3 likely duplicates of a GitHub issue and post a comment via `scripts/comment-on-duplicates.sh`.
- `/triage-issue REPO: ... ISSUE_NUMBER: ... EVENT: ...` — analyze a new issue or comment and apply/remove labels via `scripts/edit-issue-labels.sh`. Never posts comments.

Both `/dedupe` and `/triage-issue` are also invoked from GitHub Actions (`.github/workflows/claude-dedupe-issues.yml`, `claude-issue-triage.yml`).

## Issue automation (`scripts/` + workflows)

The repo runs an automated issue lifecycle. Source of truth for labels and timeouts is `scripts/issue-lifecycle.ts`:

| Label | Days | Trigger |
|---|---|---|
| `invalid` | 3 | Not about Claude Code (CLI) |
| `needs-repro` | 7 | Bug without reproducible steps |
| `needs-info` | 7 | Bug missing version/env/error info |
| `stale` | 14 | No activity |
| `autoclose` | 14 | Marked for closure |

Issues with ≥10 👍 reactions (`STALE_UPVOTE_THRESHOLD`) are exempt from stale/autoclose.

**Scripts (Bun TypeScript + bash):**
- `scripts/sweep.ts` — daily cron; marks stale, closes expired (workflow: `sweep.yml`, runs 10:00 & 22:00 UTC).
- `scripts/auto-close-duplicates.ts` — closes issues 3 days after a duplicate-detection comment with no rebuttal (workflow: `auto-close-duplicates.yml`).
- `scripts/lifecycle-comment.ts` — posts the heads-up comment when a lifecycle label is applied (workflow: `issue-lifecycle-comment.yml`).
- `scripts/backfill-duplicate-comments.ts` — manual backfill via `workflow_dispatch`.
- `scripts/gh.sh` — **restricted** `gh` wrapper used by Claude in workflows. Only allows `issue view`, `issue list`, `search issues`, `label list` with a small flag allowlist. **Always use this over raw `gh`** in slash commands and workflow prompts.
- `scripts/comment-on-duplicates.sh` — posts a duplicate-candidates comment (max 3 candidates, hardcoded to `anthropics/claude-code`).
- `scripts/edit-issue-labels.sh` — adds/removes labels, validating each against the repo's actual label list before applying.

All TS scripts run under Bun (workflows use `oven-sh/setup-bun@v2`); shell scripts use `set -euo pipefail`.

**Conventions to preserve when editing automation:**
- Pass user-controlled values (issue titles, etc.) via env vars in workflows, never via direct templating — see `log-issue-events.yml` for the pattern.
- Keep `scripts/gh.sh`'s allowlist tight; expanding it widens the attack surface for prompt-injection-via-issue.
- The `non-write-users-check.yml` workflow guards `allowed_non_write_users` additions in `.github/**` PRs — don't disable it.

## GitHub Actions integration

`.github/workflows/claude.yml` responds to `@claude` mentions in issues, PRs, and review comments using `anthropics/claude-code-action@v1`. Issue triage and dedupe workflows invoke slash commands directly via the action's `prompt` input. Models in use: `claude-opus-4-6` (triage), `claude-sonnet-4-5-20250929` (dedupe, default `@claude`).

## Working conventions

- **Don't add files to the repo root.** Place new plugins under `plugins/`, automation under `scripts/`, examples under `examples/`.
- **Don't edit `CHANGELOG.md`.** It's generated/updated by an external bot — see the dominant commit history (`chore: Update CHANGELOG.md`).
- **Prefer editing existing files.** No build step exists; check that JSON files are still valid (especially `marketplace.json` and any `plugin.json`).
- **Plugin command frontmatter:** scope `allowed-tools` narrowly. Existing examples use `Bash(./scripts/gh.sh:*)` rather than open `Bash` access.
- **Line endings:** `.gitattributes` enforces LF for text files and `*.sh`. Don't commit CRLF.
- **Branch names for new work:** descriptive kebab-case (e.g., `claude/add-claude-documentation-LyKWV`).
- **Commits:** short imperative subject; recent style is plain (`feat(code-review): ...`, `chore: ...`). The user-facing changelog is separate, so commit messages don't need to be marketing-grade.
- **PRs:** open with `/commit-push-pr` or via `gh pr create`. Don't open PRs unless the user asks.

## Testing changes

There is no test runner. Validation is manual:

- **Plugin changes:** install the plugin locally with `claude` and exercise the command/agent/hook. For JSON changes, run `python -m json.tool < file.json` (or `jq .`) to confirm validity.
- **Workflow changes:** if you can't trigger them, at least run `actionlint` mentally — verify env-var quoting, especially for any field interpolating user input.
- **Script changes:** the TS scripts run under Bun; quick smoke-test with `bun run scripts/<name>.ts --dry-run` where supported (`sweep.ts` and `lifecycle-comment.ts` honor `--dry-run`).

## Issue templates

Five templates in `.github/ISSUE_TEMPLATE/`: `bug_report.yml`, `feature_request.yml`, `documentation.yml`, `model_behavior.yml`, and `config.yml` (chooser config). Updates to triage logic in `.claude/commands/triage-issue.md` should match what these templates collect.

## Out of scope

If asked to fix a bug in the Claude Code CLI itself, debug `claude` runtime behavior, or modify the agent loop — the source is not in this repo. Direct the user to file a bug via `/bug` or the issue templates here.
