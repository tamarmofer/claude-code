# Skill Validation Checklist

Run through this list before considering a skill complete.

## Structure

- [ ] `SKILL.md` exists at the skill root
- [ ] YAML frontmatter present at top of SKILL.md
- [ ] Frontmatter has `name` field
- [ ] Frontmatter has `description` field
- [ ] Markdown body is present and substantial
- [ ] Every file mentioned in SKILL.md actually exists on disk
- [ ] Skill directory lives at `plugin-name/skills/skill-name/`

## Description Quality

- [ ] Uses third person ("This skill should be used when...")
- [ ] Includes specific trigger phrases users would actually say
- [ ] Trigger phrases are quoted in the description
- [ ] Lists concrete scenarios, not vague topics
- [ ] Does not start with "Use this skill when..." (second person)
- [ ] Does not start with "Provides guidance on..." (no triggers)

## Body Quality

- [ ] Uses imperative/infinitive form throughout
- [ ] No "You should", "You need to", "You can" in skill instructions
- [ ] Word count between 1,500 and 2,000 (acceptable up to 3,000)
- [ ] Detailed patterns moved to `references/`
- [ ] Working code moved to `examples/`
- [ ] Utility scripts moved to `scripts/`
- [ ] No information duplicated between SKILL.md and references/

## Resource References

- [ ] SKILL.md has an "Additional Resources" or equivalent section
- [ ] Each file in `references/` is referenced by name in SKILL.md
- [ ] Each file in `examples/` is referenced by name in SKILL.md
- [ ] Each file in `scripts/` is referenced by name in SKILL.md
- [ ] Reference paths use forward slashes and match actual filenames

## Resource Quality

- [ ] Reference files are detailed (2,000-5,000+ words is fine)
- [ ] Examples are complete and runnable
- [ ] Scripts are executable (`chmod +x`)
- [ ] Scripts have a brief comment header explaining purpose
- [ ] No broken internal links between files

## Loading Behavior

- [ ] Skill triggers on the phrases listed in the description
- [ ] Skill does NOT trigger on unrelated requests
- [ ] References load only when Claude needs them
- [ ] SKILL.md alone is sufficient for the most common use cases
