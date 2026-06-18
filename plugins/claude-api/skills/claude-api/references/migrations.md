# Model Migrations

Version-by-version guidance for moving Claude API code between model versions. **Default playbook:** update the model ID, re-run a representative test set, watch for the behaviors listed below, and adjust prompts only if observed.

## Sonnet 4.5 → 4.6

- Model string: `claude-sonnet-4-5-20250929` → `claude-sonnet-4-6`
- Tool descriptions matter more in 4.6—weak descriptions trigger fewer/wrong tool calls. Audit `description` fields.
- Slightly less verbose by default. Prompts that previously needed "be concise" can drop that instruction.

## Sonnet 4.6 → Opus 4.7

- Model string: `claude-sonnet-4-6` → `claude-opus-4-7`
- Opus is more agentic; loops will run longer if not bounded. Set hard step limits.
- Cost is higher—route only complex requests to Opus, keep classification/extraction on Sonnet or Haiku.

## Opus 4.5 → 4.6 → 4.7

- 4.5 → 4.6: Sensitivity to imperative language (`MUST`, `ALWAYS`, `CRITICAL`) increased. Aggressive system prompts can cause tool over-triggering. Soften to `should`, `do`, `prefer`.
- 4.6 → 4.7: Improved long-context utilization. Prompts that paginated context manually can pass full documents directly. Extended thinking budgets can typically be reduced 20-30% for equivalent quality.

## General Cross-Version Pattern

For any version bump:

1. **Update model string** in client code and any config.
2. **Soften imperatives** in system prompts only if you observe over-triggering on tools or unnecessary verbosity.
3. **Verify prompt cache hits**—the prefix bytes (system, tools, documents) must be identical. Cache will rebuild on first call after a model change.
4. **Re-test representative prompts**: 10-20 prompts covering the app's use cases. Look for tool misuse, refusals on previously-OK content, length changes, format drift.
5. **Bound agent loops**—newer Opus models will run more steps if allowed.

## Retired Model Replacements

When a model is retired, replace with the recommended successor:

| Retired | Replacement |
|---|---|
| `claude-3-opus-*` | `claude-opus-4-7` |
| `claude-3-5-sonnet-*` | `claude-sonnet-4-6` |
| `claude-3-5-haiku-*` | `claude-haiku-4-5-20251001` |
| `claude-3-haiku-*` | `claude-haiku-4-5-20251001` |
| `claude-sonnet-4-20250514` | `claude-sonnet-4-6` |
| `claude-opus-4-1-20250805` | `claude-opus-4-7` |

After a retirement migration, expect quality improvements but also behavior shifts (refusal patterns, output style, tool-calling). Re-test before deploying.

## Platform-Specific Model Strings

Anthropic API uses bare model IDs. Bedrock and Vertex use platform-specific formats.

| Family | Anthropic API | AWS Bedrock | Google Vertex AI |
|---|---|---|---|
| Opus 4.7 | `claude-opus-4-7` | `anthropic.claude-opus-4-7-v1:0` | `claude-opus-4-7@latest` |
| Sonnet 4.6 | `claude-sonnet-4-6` | `anthropic.claude-sonnet-4-6-v1:0` | `claude-sonnet-4-6@latest` |
| Haiku 4.5 | `claude-haiku-4-5-20251001` | `anthropic.claude-haiku-4-5-20251001-v1:0` | `claude-haiku-4-5@20251001` |

**Bedrock:** recent Claude models on Bedrock require an inference-profile prefix (`us.`, `eu.`, `apac.`), e.g., `us.anthropic.claude-opus-4-7-v1:0`.

**Vertex:** publisher path required in some SDKs: `publishers/anthropic/models/claude-opus-4-7`.

**Azure AI Foundry:** uses user-chosen deployment names mapped to underlying models.

For migrations specifically targeting Opus 4.5 (legacy), see the sibling `claude-opus-4-5-migration` plugin.
