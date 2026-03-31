# Market Comps

Research and compare software tools, libraries, frameworks, and products against their market alternatives to inform technical decisions.

## Usage

```
/market-comps <tool-or-product> [--depth shallow|deep] [--focus features|pricing|community|ecosystem|all]
```

### Examples

```
/market-comps Redis
/market-comps React --depth shallow
/market-comps PostgreSQL --focus ecosystem
/market-comps Tailwind CSS --depth deep --focus all
```

## How It Works

1. **Parses the request** and sets up progress tracking via TodoWrite
2. **In parallel:** researches the subject tool AND scans your local project (package.json, requirements.txt, etc.) for existing usage context
3. **Identifies alternatives** - direct competitors, indirect alternatives, emerging options
4. **Researches each alternative in parallel** using dedicated market-researcher agents
5. **Synthesizes findings** into a structured comparison with tables, scenario-based guidance, and risk assessment

## Output

The report includes:

- **Your Project Context** - what you currently use in this problem space (if detected)
- **Comparison table** - dense, scannable, focused on dimensions where tools differ
- **Key findings** - non-obvious insights not already visible in the table
- **Scenario-based guidance** - "Choose X when..." format for each option
- **Risks** - bus factor, license concerns, breaking change history, lock-in
- **Sources** - URLs consulted with retrieval dates

## Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--depth` | `shallow`, `deep` | `deep` | `shallow` compares 3 alternatives; `deep` compares up to 6 |
| `--focus` | `features`, `pricing`, `community`, `ecosystem`, `all` | `all` | Prioritize a specific comparison dimension |

## Agents

| Agent | Model | Role |
|-------|-------|------|
| **market-researcher** | sonnet | Gathers structured factual data about a single tool via web search |
| **comparison-analyst** | sonnet | Synthesizes pre-gathered research into actionable comparison reports |

## Design Principles

- **Factual and sourced** - uses web search for current data; marks unverifiable claims
- **Balanced** - every tool has trade-offs; no single "best" recommendation
- **Context-aware** - considers your existing project dependencies and stack
- **Decision-oriented** - scenario-based guidance, not opinions
- **Honest about gaps** - missing data shown as N/A, not guessed
