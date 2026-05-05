# Progressive Disclosure in Skills

Skills load in three tiers. Place content at the right tier so context stays lean and detail remains discoverable.

## Tier 1: Metadata (always loaded)

The `name` and `description` in YAML frontmatter are always in context. This is roughly 100 words across all installed skills.

**Goal:** make the description specific enough that Claude can decide whether to load the skill on any given request, without loading the body.

## Tier 2: SKILL.md Body (loaded when skill triggers)

Loaded into context when the description matches the user's request. Target 1,500-2,000 words, hard cap 3,000.

**Include:**
- Core concepts and overview
- Essential procedures and workflows
- Most common use cases
- Quick reference tables
- Pointers to references/, examples/, scripts/

**Exclude:**
- Detailed pattern catalogs (move to references)
- Full API references (move to references)
- Long migration guides (move to references)
- Multiple working code samples (move to examples)
- Reusable utility code (move to scripts)

## Tier 3: Bundled Resources (loaded as needed)

### `references/` — Documentation

Loaded into context when Claude determines it is needed for the current task.

- Detailed patterns and advanced techniques
- Comprehensive API documentation
- Migration guides
- Edge cases and troubleshooting
- Schemas, domain knowledge, company policies

Each reference file can be large (2,000-5,000+ words). Files over 10k words should be searchable — include grep patterns in SKILL.md to point Claude at relevant sections.

### `examples/` — Working code

Complete, runnable code Claude can copy and adapt:

- Sample scripts
- Configuration files
- Template files
- Real-world usage examples

These are loaded into context like references but represent reusable artifacts rather than documentation.

### `scripts/` — Executable utilities

Code Claude runs without loading it into context:

- Validation tools
- Testing helpers
- Parsing utilities
- Automation scripts

Scripts can still be read into context when Claude needs to patch them or understand their behavior. Make them executable (`chmod +x`) and add a header comment.

### `assets/` — Output files

Files used in Claude's output, not loaded into context:

- Templates (HTML, PowerPoint, etc.)
- Brand assets (logos, fonts)
- Sample documents

Claude references these by path; they get copied or modified rather than read into the context window.

## Decision Tree

When deciding where new content goes:

```
Is it a complete runnable artifact Claude would copy?
  → examples/

Is it executable utility code Claude would run?
  → scripts/

Is it a file used in output but not read?
  → assets/

Is it long-form documentation (>500 words) on a sub-topic?
  → references/

Is it core procedural knowledge needed every time the skill loads?
  → SKILL.md body

Is it the trigger criteria for loading the skill?
  → SKILL.md frontmatter description
```

## Anti-pattern: Duplication

Content should live in exactly one place. If a pattern appears in both SKILL.md and `references/patterns.md`, the references file is canonical and SKILL.md should link to it with a one-line summary.
