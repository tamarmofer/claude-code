# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is (and is not)

This is **not** the source code for the Claude Code CLI. It is a public-facing distribution repository for the [`@anthropic-ai/claude-code`](https://www.npmjs.com/package/@anthropic-ai/claude-code) product, containing:

1. **A plugin marketplace** (`plugins/` + `.claude-plugin/marketplace.json`) — official Claude Code plugins distributed via the `/plugin` command.
2. **GitHub issue-triage automation** (`scripts/` + `.github/workflows/`) — Bun-executed TypeScript and shell scripts driven by Claude itself via `anthropics/claude-code-action@v1`.
3. **Configuration examples and a devcontainer** (`examples/`, `.devcontainer/`) for end-users adopting Claude Code.

There is no top-level `package.json`, no build step, and no test suite at the repo root. Don't add one without a strong reason. README.md is targeted at end-users installing Claude Code, not contributors.

## Repository layout (orientation)

- `plugins/<name>/` — one directory per plugin, each with `.claude-plugin/plugin.json` and some combination of `commands/`, `agents/`, `skills/`, `hooks/`. The marketplace at `.claude-plugin/marketplace.json` lists every plugin with its `source` path; **adding or renaming a plugin requires updating that file.**
- `scripts/` — Bun TypeScript (`*.ts`) and bash scripts. The `*.ts` files are run by GitHub Actions via `bun run scripts/<file>.ts`; they hit the GitHub REST API directly via `fetch` rather than `gh`.
- `.claude/commands/` — repo-level slash commands (`/commit-push-pr`, `/dedupe`, `/triage-issue`) that the CI workflows invoke via `prompt: "/triage-issue ..."`.
- `.github/workflows/` — Claude-driven workflows (`claude-issue-triage.yml`, `claude-dedupe-issues.yml`, `claude.yml`) and pure Bun workflows (`sweep.yml`, `auto-close-duplicates.yml`).
- `examples/settings/` — `settings-lax.json`, `settings-strict.json`, `settings-bash-sandbox.json` reference configs for org-wide deployments.
- `CHANGELOG.md` — large, frequently auto-updated. Don't reformat it.

## Issue-triage architecture

The triage system has three layers that act on the same set of labels:

1. **Real-time labelling on issue events** — `claude-issue-triage.yml` invokes the `/triage-issue` slash command (`.claude/commands/triage-issue.md`) on `issues.opened` and `issue_comment.created`. The command applies/removes lifecycle labels.
2. **Duplicate detection on issue open** — `claude-dedupe-issues.yml` invokes `/dedupe`, which uses 5 parallel agents to search for duplicates and posts a comment via `scripts/comment-on-duplicates.sh`.
3. **Scheduled enforcement** — `sweep.yml` (twice daily) runs `scripts/sweep.ts` to mark stale and close expired issues; `auto-close-duplicates.yml` (daily) runs `scripts/auto-close-duplicates.ts` to close issues whose duplicate comment is >3 days old without further activity.

**`scripts/issue-lifecycle.ts` is the single source of truth** for lifecycle label names, timeout days, and close messages: `invalid` (3d), `needs-repro` (7d), `needs-info` (7d), `stale` (14d), `autoclose` (14d), with `STALE_UPVOTE_THRESHOLD = 10` (issues with ≥10 thumbs-up are exempt from staling/closing). Both `sweep.ts` and lifecycle-comment workflows import from this file — change it here, not in copies.

### `scripts/gh.sh` is a restricted wrapper, not full `gh`

The slash commands `/dedupe` and `/triage-issue` are run by Claude in CI under `allowed-tools: Bash(./scripts/gh.sh:*)`. The wrapper only allows these subcommands: `issue view`, `issue list`, `search issues`, `label list`, with only the flags `--comments --state --limit --label`. The `search issues` query is rejected if it contains `repo:`, `org:`, or `user:` qualifiers — scope is enforced via the `GH_REPO`/`GITHUB_REPOSITORY` env var. **Don't add new subcommands to triage prompts without first extending `gh.sh`.**

## Plugin conventions

Each plugin under `plugins/` is independently authored and self-contained. When adding to or modifying a plugin:

- Every plugin has `.claude-plugin/plugin.json` with `name`, `version`, `description`, `author`. The `name` must match the directory name and the marketplace entry.
- **The marketplace entry in `.claude-plugin/marketplace.json` must be kept in sync** — name, version, description, author, `source` path, and `category`.
- Hook scripts reference `${CLAUDE_PLUGIN_ROOT}` (set by the harness) for plugin-relative paths — don't hardcode `plugins/<name>/...`.
- Plugins use whatever components they need: `commands/*.md`, `agents/*.md`, `skills/*/SKILL.md`, `hooks/hooks.json` + handler scripts, `.mcp.json` for MCP servers. Not every plugin has every component.

## Running scripts locally

- TypeScript scripts use [Bun](https://bun.sh) — invoke as `bun run scripts/<file>.ts`. They expect `GITHUB_TOKEN`, `GITHUB_REPOSITORY_OWNER`, `GITHUB_REPOSITORY_NAME` env vars. `sweep.ts` accepts `--dry-run`.
- Bash scripts in `scripts/` (`gh.sh`, `comment-on-duplicates.sh`, `edit-issue-labels.sh`) are designed to be invoked by Claude under restricted `allowed-tools` permissions — they intentionally validate and reject inputs outside their narrow contract.

## Conventions when modifying this repo

- **Don't bump versions casually.** Plugin versions live in two files (`plugins/<name>/.claude-plugin/plugin.json` and the matching marketplace entry); only bump when shipping a real change to that plugin.
- **`CHANGELOG.md` is the upstream Claude Code changelog**, not a changelog for this repo. It's appended to by automation (`chore: Update CHANGELOG.md` commits). Don't edit it manually unless explicitly asked.
- Slash command frontmatter (`allowed-tools:`) is enforced — when a command grows new behavior, expand `allowed-tools` rather than relying on broad permissions.
- Workflows pin `anthropics/claude-code-action@v1` and pass `--model` via `claude_args`. Triage uses `claude-opus-4-6`; the @claude responder uses `claude-sonnet-4-5-20250929`. Match the existing model choice unless changing it deliberately.
