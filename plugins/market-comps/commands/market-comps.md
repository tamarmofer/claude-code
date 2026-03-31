---
description: Research and compare a tool, library, or product against market alternatives
allowed-tools: Bash(npm view:*), Bash(npm search:*), Bash(pip show:*), Bash(cargo search:*), Read, Grep, Glob, WebFetch, WebSearch, Agent, TodoWrite
argument-hint: <tool-or-product> [--depth shallow|deep] [--focus features|pricing|community|ecosystem|all]
---

Research and compare the specified tool, library, or product against its market alternatives.

## Process

1. **Parse the request and set up tracking.** Identify:
   - The subject (tool, library, framework, or product to evaluate)
   - Depth: `shallow` (quick overview, 3 alternatives) or `deep` (comprehensive, up to 6 alternatives). Default: `deep`.
   - Focus area: `features`, `pricing`, `community`, `ecosystem`, or `all`. Default: `all`.

   Use TodoWrite to create a task list tracking each phase of the comparison.

2. **Gather context.** Launch two agents in parallel:

   **Agent A: Subject researcher** (market-researcher agent)
   Research the subject itself:
   - What it is, what problem it solves, target audience
   - Current version, release cadence, maintenance status
   - Licensing and pricing model
   - Key features and capabilities
   - Known limitations and trade-offs

   **Agent B: Local project scanner** (haiku agent)
   Check the current project for context:
   - Scan package.json, requirements.txt, Cargo.toml, go.mod, or similar dependency files
   - Identify what the user already uses in this problem space
   - Note version constraints, related dependencies, and integration points
   - If no project files exist, return "no local project context"

3. **Identify alternatives.** Launch a sonnet agent to research the competitive landscape, informed by the subject research from step 2:
   - Direct competitors (same problem space, similar approach)
   - Indirect alternatives (different approach to the same problem)
   - Emerging options (newer entrants worth watching)
   - For libraries/frameworks: check package registries (npm, PyPI, crates.io) for popularity signals when available
   - Return a ranked list of the top alternatives (3 for `shallow`, up to 6 for `deep`)

4. **Research alternatives in parallel.** Launch one market-researcher agent per alternative identified in step 3. Each agent gathers the same data points collected for the subject in step 2.

   If a `--focus` was specified, tell each agent to prioritize that dimension but still gather baseline data for other dimensions.

5. **Synthesize comparison.** Launch a comparison-analyst agent with ALL research data (subject + alternatives + local project context). The analyst should:

   - Produce a comparison table. If `--focus` was specified, lead with that dimension and go deeper on it.
   - Highlight how findings relate to the user's current project setup (if local context was found).
   - Follow the output format below.

6. **Output the final report** to the terminal in this format:

---

## Market Comparison: [Subject]

### Overview
[1-2 sentence summary of what the subject is and the problem space]

### Your Project Context
[What the user currently uses in this space, based on local project scan. Omit this section if no project context was found.]

### Comparison
| | [Subject] | [Alt 1] | [Alt 2] | ... |
|---|---|---|---|---|
| Category | value | value | value | ... |
| ... | ... | ... | ... | ... |

### Key Findings
- [3-5 bullet points highlighting the most important insights]
- [If focus was specified, lead with findings in that area]

### When to Choose What
- **Choose [Subject] when:** [specific scenarios]
- **Choose [Alt 1] when:** [specific scenarios]
- ...

### Risks
- [Notable risks for each option: bus factor, license changes, breaking change history, vendor lock-in]

### Sources
[List URLs consulted, with dates of data retrieval]

---

Mark each todo item as complete as you finish each phase.

## Guidelines

- Be factual. Cite sources. Do not hallucinate features or statistics.
- If data is unavailable or unverifiable, say so explicitly rather than guessing.
- Present trade-offs honestly - every tool has strengths and weaknesses.
- Avoid marketing language. Use neutral, engineering-oriented descriptions.
- When comparing metrics (stars, downloads), note the date of observation.
- For open-source tools, check GitHub/GitLab for actual activity data rather than relying on general knowledge.
- Prioritize information that affects real engineering decisions: migration cost, breaking changes, bus factor, license compatibility.
- Do NOT make a single "best" recommendation. Provide scenario-based guidance instead.
