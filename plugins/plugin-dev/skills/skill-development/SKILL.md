---
name: Skill Development
description: This skill should be used when the user asks to "create a skill", "add a skill to a plugin", "write a new SKILL.md", "improve a skill description", "audit a skill", or "organize skill content" for Claude Code plugins. Covers frontmatter triggers, progressive disclosure, and imperative writing style.
version: 0.1.0
---

# Skill Development for Claude Code Plugins

Create effective skills that load on the right triggers, stay lean in context, and provide procedural knowledge another Claude instance can act on.

## About Skills

Skills are modular, self-contained packages that extend Claude with specialized knowledge, workflows, and tools. Treat them as onboarding guides for specific domains—they transform a general-purpose agent into a specialized one with procedural knowledge no model can fully possess on its own.

Skills provide:
1. Specialized workflows — multi-step procedures for specific domains
2. Tool integrations — instructions for working with specific file formats or APIs
3. Domain expertise — company-specific knowledge, schemas, business logic
4. Bundled resources — scripts, references, and assets for repetitive tasks

## Anatomy of a Skill

```
skill-name/
├── SKILL.md                  (required)
│   ├── YAML frontmatter      (required: name, description)
│   └── Markdown instructions (required)
├── references/  (optional, loaded into context as needed)
├── examples/    (optional, working code Claude can copy)
├── scripts/     (optional, executable utilities)
└── assets/      (optional, files used in output, not loaded)
```

**Metadata quality matters most.** The `name` and `description` in frontmatter determine when Claude loads the skill. Be specific about what it does and when to use it.

## Progressive Disclosure

Skills use a three-level loading system:

1. **Metadata (name + description)** — always in context (~100 words)
2. **SKILL.md body** — loaded when skill triggers (target 1,500-2,000 words, max 3,000)
3. **Bundled resources** — loaded as Claude needs them (effectively unlimited)

Move detailed content to `references/` so SKILL.md stays lean. Information should live in either SKILL.md or a reference file, not both.

For full guidance on which content goes where, see `references/progressive-disclosure.md`.

## Skill Creation Process

### Step 1: Understand Use Cases

Identify concrete examples of how the skill will be used. Ask the user:

- "What functionality should this skill support?"
- "Give some examples of how this skill would be used."
- "What would a user say that should trigger this skill?"

Skip this step only when usage patterns are already clear.

### Step 2: Plan Reusable Contents

For each example, identify what `scripts/`, `references/`, or `assets/` would help. Concrete patterns:

- Repeated boilerplate code → `scripts/` (e.g., `scripts/rotate_pdf.py`)
- Repeated boilerplate output → `assets/` (e.g., `assets/hello-world/` template)
- Schemas, API docs, domain knowledge → `references/` (e.g., `references/schema.md`)

### Step 3: Create Structure

```bash
mkdir -p plugin-name/skills/skill-name/{references,examples,scripts}
touch plugin-name/skills/skill-name/SKILL.md
```

Create only the directories actually needed.

### Step 4: Write SKILL.md

The skill is being written for another Claude instance to read. Focus on procedural knowledge, domain-specific details, and reusable assets that help that instance execute tasks effectively.

**Frontmatter** — third-person, with quoted trigger phrases:

```yaml
---
name: Skill Name
description: This skill should be used when the user asks to "phrase 1", "phrase 2", "phrase 3". Be concrete about scenarios.
version: 0.1.0
---
```

**What makes a good description:**

- 3-7 quoted trigger phrases users would actually say. Mix exact verb forms ("create a hook") with topic keywords ("hooks.json").
- One concrete-scenarios sentence at the end ("Covers scenarios such as X, Y, Z") rather than a generic capability claim ("Provides comprehensive guidance").
- Disambiguate from sibling skills. If two skills share a phrase, narrow each description so Claude picks the right one. Example: agent-development vs. command-development both touch "frontmatter"—each description names its specific scope.
- Avoid generic verbs like "help with", "work with", "understand"—they trigger on everything.

**Trigger test** before shipping: draft 3 queries the skill *should* load on and 3 queries it should *not* load on. Read the description and predict the result for each. Adjust the description until predictions match intent.

**Versioning:** bump patch on description tweaks, minor on body changes, major on workflow-breaking changes.

**Body** — imperative/infinitive form, target 1,500-2,000 words. Reference supporting files explicitly:

```markdown
## Additional Resources

- `references/patterns.md` — common patterns
- `examples/script.sh` — working example
- `scripts/validate.sh` — validation utility
```

### Step 5: Validate

Check the skill against `references/validation-checklist.md` before finalizing.

### Step 6: Iterate

After using the skill on real tasks, update SKILL.md and resources based on observed gaps. Common improvements:

- Strengthen trigger phrases
- Move long sections to `references/`
- Add missing examples or scripts
- Clarify ambiguous instructions

## Writing Style

Write the skill body in **imperative/infinitive form** (verb-first), not second person:

| Correct (imperative)                  | Incorrect (second person)                   |
|---------------------------------------|---------------------------------------------|
| Parse the frontmatter using sed.      | You should parse the frontmatter using sed. |
| Validate input before processing.     | You need to validate input.                 |
| Use grep to search for patterns.      | You can use grep to search.                 |

The frontmatter description must use **third person**:

| Correct                                                | Incorrect                                  |
|--------------------------------------------------------|--------------------------------------------|
| This skill should be used when the user asks to "..." | Use this skill when you want to ...        |
| This skill should be used when ...                    | Load this skill when user asks ...         |

For detailed style guidance and edge cases, see `references/writing-style.md`.

## Validation Checklist

Before finalizing a skill, verify:

- [ ] SKILL.md exists with valid YAML frontmatter (`name`, `description`)
- [ ] Description uses third person and includes specific quoted trigger phrases
- [ ] Body uses imperative form throughout
- [ ] Body is 1,500-2,000 words (max 3,000)
- [ ] Detailed content lives in `references/`, not SKILL.md
- [ ] All referenced files actually exist
- [ ] Examples are complete and runnable
- [ ] Scripts are executable

For a more detailed checklist, see `references/validation-checklist.md`.

## Quick Reference: Skill Structures

**Minimal** — simple knowledge, no resources:
```
skill-name/
└── SKILL.md
```

**Standard (recommended)** — most plugin skills:
```
skill-name/
├── SKILL.md
├── references/detailed-guide.md
└── examples/working-example.sh
```

**Complete** — complex domains with utilities:
```
skill-name/
├── SKILL.md
├── references/{patterns.md, advanced.md}
├── examples/{example1.sh, example2.json}
└── scripts/validate.sh
```

## Plugin-Specific Notes

### Location

Plugin skills live in `plugin-name/skills/skill-name/`. Claude Code auto-discovers them—no packaging or registration needed. Users get skills when they install the plugin.

### Testing

Install the plugin locally and ask questions that should trigger the skill:

```bash
cc --plugin-dir /path/to/plugin
```

Verify the skill loads on expected queries and not on unrelated ones.

### Reference Implementations

Study the sibling skills in this plugin as templates:

- `../hook-development/` — strong triggers, lean SKILL.md, three references and three examples
- `../agent-development/` — AI-assisted creation guidance, complete examples
- `../plugin-settings/` — real-world references and working scripts
- `../command-development/` — clear critical concepts, multiple references
- `../plugin-structure/` — clean organization

## Common Mistakes

The four most common failure modes are vague trigger descriptions, putting everything in SKILL.md, second-person writing, and unreferenced resources. For full examples and fixes, see `references/common-mistakes.md`.

## Additional Resources

- `references/progressive-disclosure.md` — what goes in SKILL.md vs references/ vs examples/ vs scripts/
- `references/writing-style.md` — detailed style guidance
- `references/validation-checklist.md` — extended validation
- `references/common-mistakes.md` — anti-patterns with fixes
- `references/skill-creator-original.md` — full original skill-creator methodology
