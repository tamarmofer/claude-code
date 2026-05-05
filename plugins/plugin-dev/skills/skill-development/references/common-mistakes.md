# Common Skill Authoring Mistakes

Four anti-patterns recur across skills. Each is shown with a bad example, why it fails, and a corrected version.

## Mistake 1: Weak Trigger Description

**Bad:**
```yaml
description: Provides guidance for working with hooks.
```

Vague, no specific trigger phrases, not third person. Claude has nothing concrete to match user requests against, so the skill loads inconsistently or not at all.

**Good:**
```yaml
description: This skill should be used when the user asks to "create a hook", "add a PreToolUse hook", "validate tool use", or mentions hook events. Provides comprehensive hooks API guidance.
```

Third person, specific quoted phrases, concrete scenarios.

## Mistake 2: Too Much in SKILL.md

**Bad:**
```
skill-name/
└── SKILL.md  (8,000 words — everything in one file)
```

Bloats context every time the skill loads. Detailed content gets pulled in even when not needed.

**Good:**
```
skill-name/
├── SKILL.md  (1,800 words — core essentials)
└── references/
    ├── patterns.md (2,500 words)
    └── advanced.md (3,700 words)
```

Progressive disclosure. References load only when Claude determines they are needed.

## Mistake 3: Second Person Writing

**Bad:**
```markdown
You should start by reading the configuration file.
You need to validate the input.
You can use the grep tool to search.
```

Second person breaks the imperative-form convention skills are built on and reads like prose advice rather than procedural instruction.

**Good:**
```markdown
Start by reading the configuration file.
Validate the input before processing.
Use the grep tool to search for patterns.
```

Imperative form, direct instructions.

## Mistake 4: Missing Resource References

**Bad:**
```markdown
# SKILL.md

[Core content]

[No mention of references/ or examples/]
```

Claude does not know references exist and never loads them, so progressive disclosure fails silently.

**Good:**
```markdown
# SKILL.md

[Core content]

## Additional Resources

- `references/patterns.md` — detailed patterns
- `references/advanced.md` — advanced techniques
- `examples/script.sh` — working example
```

Claude knows where to find supporting material and pulls it in on demand.

## Quick Self-Check

Before publishing a skill:

1. Read the description aloud. Would a user ask any of those quoted phrases?
2. Count words in SKILL.md. Over 3,000? Move detail to `references/`.
3. Search SKILL.md body for "you should", "you need", "you can". Replace with imperative.
4. Search SKILL.md for every file in `references/`, `examples/`, `scripts/`. Each must appear at least once.
