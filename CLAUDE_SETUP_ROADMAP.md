# Claude Code Setup Roadmap

A phased plan for taking a project from zero to a fully configured Claude Code
setup — covering installation, project memory, permissions, automation, and
team-wide and CI integration.

Work through the phases in order. Each phase is independently useful, so you can
stop at any point and still have a working setup. Treat the checklists as a
menu, not a mandate — adopt what fits your team.

---

## Phase 0 — Install & verify

**Goal:** Get Claude Code running locally and confirm it can see your repo.

- [ ] Install the CLI (see the [setup docs](https://code.claude.com/docs/en/setup)):
  - macOS/Linux: `curl -fsSL https://claude.ai/install.sh | bash`
  - Windows: `irm https://claude.ai/install.ps1 | iex`
- [ ] Run `claude` from your project root and complete authentication.
- [ ] Run a smoke test: ask Claude to summarize the repository.
- [ ] Confirm the IDE extension (VS Code / JetBrains) if your team uses one.

**Done when:** `claude` launches, authenticates, and can answer a question about
your codebase.

---

## Phase 1 — Project memory (`CLAUDE.md`)

**Goal:** Give Claude the durable context it needs to work like a teammate.

- [ ] Run `/init` to scaffold a `CLAUDE.md` at the repo root.
- [ ] Document the essentials:
  - How to build, test, lint, and run the project.
  - Project structure and where key code lives.
  - Conventions: naming, formatting, commit style, branch strategy.
  - "Gotchas" — non-obvious constraints a newcomer would trip on.
- [ ] Add nested `CLAUDE.md` files in subdirectories that have their own rules.
- [ ] Keep it lean — link out to longer docs rather than pasting them.

**Done when:** A fresh session can build and test the project without you
re-explaining the basics.

---

## Phase 2 — Permissions & settings

**Goal:** Reduce friction safely by pre-approving routine actions.

- [ ] Create `.claude/settings.json` for shared, checked-in team settings.
- [ ] Use `.claude/settings.local.json` for personal, git-ignored overrides.
- [ ] Allowlist common safe commands (build, test, lint, status) so they don't
      prompt every time.
- [ ] Keep destructive or outbound actions gated behind a prompt.
- [ ] Pin the default model and any environment variables the project needs.
- [ ] Tip: the `/fewer-permission-prompts` skill can scan past sessions and
      propose a sensible allowlist.

**Done when:** Routine work flows without prompt fatigue, and risky actions
still ask first.

---

## Phase 3 — Slash commands

**Goal:** Capture repeatable workflows as one-line commands.

- [ ] Add project commands under `.claude/commands/*.md` (this repo already ships
      `commit-push-pr`, `dedupe`, and `triage-issue`).
- [ ] Codify your team's frequent flows: "open a PR", "run the release checklist",
      "update the changelog", "review the current diff".
- [ ] Document available commands in `CLAUDE.md` so the team discovers them.

**Done when:** The 3–5 most common workflows are each a single command.

---

## Phase 4 — Hooks & automation

**Goal:** Enforce behavior that must happen every time — not just when Claude
remembers.

- [ ] Add a **SessionStart** hook so web/CI sessions can build, test, and lint
      reliably (see the `session-start-hook` skill).
- [ ] Add hooks for guardrails: formatting on save, blocking edits to generated
      files, or running a quick check before commits.
- [ ] Use the `update-config` skill to wire hooks into `settings.json`.

**Done when:** Critical pre/post actions run automatically, independent of the
prompt.

---

## Phase 5 — Subagents

**Goal:** Delegate specialized or parallelizable work to focused agents.

- [ ] Identify recurring narrow tasks (code review, exploration, planning,
      research) that benefit from a dedicated agent.
- [ ] Define custom subagents with scoped tools and tailored instructions.
- [ ] Prefer fan-out for independent work (e.g. searching many files, reviewing
      across dimensions) to keep the main session focused.

**Done when:** Heavy search/review/planning tasks are delegated rather than
clogging the main thread.

---

## Phase 6 — MCP servers & integrations

**Goal:** Connect Claude to the external systems your team already uses.

- [ ] Connect the services your workflow touches (issue trackers, docs, cloud
      providers, calendars).
- [ ] Scope credentials to least privilege; prefer read-only where possible.
- [ ] Document which servers are expected so teammates configure the same set.

**Done when:** Claude can act on your real tools without manual copy-paste.

---

## Phase 7 — Plugins

**Goal:** Package and share reusable capabilities across the team or org.

- [ ] Browse the [plugins directory](./plugins/README.md) for ready-made bundles
      (code review, feature dev, security guidance, plugin/SDK dev, and more).
- [ ] Install the plugins that match your stack via the marketplace.
- [ ] For org-specific needs, build a plugin with the `plugin-dev` plugin and
      publish it through a marketplace.

**Done when:** Common commands/agents are distributed as plugins, not copied by
hand.

---

## Phase 8 — GitHub & CI integration

**Goal:** Bring Claude into your pull-request and issue workflows.

- [ ] Add the `@claude` GitHub Action so Claude can respond on issues and PRs
      (this repo's `.github/workflows/claude.yml` is a reference).
- [ ] Automate triage and dedupe of incoming issues (see the existing
      `claude-issue-triage` and `claude-dedupe-issues` workflows).
- [ ] Wire up PR review automation with the `pr-review-toolkit` / `code-review`
      plugins.
- [ ] Scope tokens and repository access tightly.

**Done when:** Claude participates in CI — triaging issues and reviewing PRs —
within guardrails.

---

## Maintenance

A setup is a living thing. Revisit it on a cadence:

- **Weekly-ish:** Prune stale `CLAUDE.md` notes; promote repeated manual asks
  into slash commands.
- **Monthly-ish:** Review the permission allowlist; remove anything overly broad.
- **Per release:** Re-check hooks, plugins, and MCP scopes still match the
  project's needs.

---

## Quick reference

| Phase | Artifact | Lives in |
|-------|----------|----------|
| 1 | Project memory | `CLAUDE.md` (root + nested) |
| 2 | Permissions/settings | `.claude/settings.json`, `.claude/settings.local.json` |
| 3 | Slash commands | `.claude/commands/*.md` |
| 4 | Hooks | `settings.json` hooks |
| 5 | Subagents | agent definitions |
| 6 | MCP servers | MCP config |
| 7 | Plugins | `.claude-plugin/`, marketplace |
| 8 | CI integration | `.github/workflows/` |

For full documentation, see the [official docs](https://code.claude.com/docs/en/overview).
