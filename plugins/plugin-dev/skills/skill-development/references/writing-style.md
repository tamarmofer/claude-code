# Skill Writing Style

Skills target another Claude instance as the reader. The style optimizes for that reader: terse, instructional, free of authorial voice.

## Imperative / Infinitive Form (Body)

Write skill bodies as direct procedural instructions. Lead with verbs.

**Correct:**
```
Create the directory structure.
Parse the frontmatter using sed.
Validate settings before use.
Run the script with --dry-run first.
```

**Incorrect (second person):**
```
You should create the directory structure.
You need to parse the frontmatter.
You must validate settings.
You can run the script with --dry-run.
```

**Incorrect (third-person about Claude):**
```
Claude should parse the frontmatter.
The assistant must validate settings.
```

The skill reader is Claude. Speaking about Claude in the third person while Claude reads the text is awkward. Speak directly to the action.

## Third Person (Description)

The frontmatter description is read by Claude before the skill loads. It must describe when to load the skill in third person.

**Correct:**
```yaml
description: This skill should be used when the user asks to "create X", "configure Y", or mentions Z.
```

**Incorrect:**
```yaml
description: Use this skill when you want to create X.        # second person
description: Load this skill when user asks about X.           # imperative — wrong for description
description: Provides guidance on X.                            # no trigger criteria
```

## Objective, Instructional Language

Focus on the action, not the actor.

**Correct:**
```
Parse the frontmatter using sed.
Extract fields with grep.
Validate values before use.
```

**Incorrect:**
```
You can parse the frontmatter...           # second person
Claude should extract fields...             # third-person about reader
The user might validate values...           # mislabels the actor
```

## Acceptable Exceptions

Some "you" usage is acceptable when it appears inside quoted example content (e.g., a hook message, an agent prompt, or a sample user-facing string). The convention applies to skill instructions, not to literal text the skill is producing as output.

Example — acceptable inside a sample hook message body:
```markdown
Example rule message:
> "You're adding console.log to production code. Consider removing it."
```

The quoted message addresses the user being intercepted, not the skill reader.

## Tone

- Short sentences over long ones.
- Concrete steps over abstract advice.
- Active voice. Lead with the verb.
- No filler ("In order to...", "It is important to note that...").
- No motivational framing ("Remember that...", "It's worth mentioning...").
