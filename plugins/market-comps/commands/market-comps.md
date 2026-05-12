---
description: Research comparable property sales and market data for a given address
allowed-tools: Read, Grep, Glob, WebFetch, WebSearch, Agent, TodoWrite
argument-hint: <address> [--type sale|rental|both] [--radius 0.25mi|0.5mi|1mi] [--period 6mo|12mo|24mo]
---

Research comparable property sales and market data for the specified address.

## Process

1. **Parse the request.** Extract:
   - Subject address (normalize to full street address, city, state, zip)
   - `--type`: `sale`, `rental`, `both`, or omitted (auto-detect after step 2). Default: auto.
   - `--radius`: `0.25mi`, `0.5mi`, `1mi`. Default: `0.5mi`.
   - `--period`: `6mo`, `12mo`, `24mo`. Applies to sale comps only; rental comps always use current/recent listings. Default: `12mo`.

   If the address cannot be parsed into a recognizable US property address, stop and ask the user to clarify.

   Use TodoWrite to track progress.

2. **Profile subject and neighborhood in parallel.** Launch two agents:

   **Agent A: property-profiler** — Research the subject property.
   **Agent B: neighborhood-analyst** — Research the surrounding market.

   When both return, determine comp type if user did not specify `--type`:
   - Multi-unit rental building with no individual units for sale → `rental`
   - Condo, co-op, single-family, or townhouse → `sale`
   - Active sale listing AND rental listings → `both`
   - Commercial or mixed-use → note in output, proceed with best-fit type

3. **Find comps.** Launch comp-finder agent with subject profile and comp type.

   If no comps are found (sparse market, unusual property), widen the radius by one tier (0.25→0.5→1mi) or the period (6→12→24mo) and retry once. If still no comps, report the data gap and produce a limited analysis using neighborhood medians only.

4. **Synthesize.** Launch comp-analyst agent with all data. Produce the report below.

5. **Output the report** directly to the terminal.

## Report Template

Adapt this template to the comp type. Omit sections that don't apply. Do not add sections not listed here.

---

## Comparative Market Analysis: [Address]
*Data retrieved [date]. This is not a formal appraisal.*

### Subject Property
| Detail | Value |
|--------|-------|
| Property Type | |
| Size | [sqft or unit sqft range] |
| Bed / Bath | [or "Studio–3BR" for multi-unit] |
| Year Built | |
| Last Sale | [date at price, or "N/A — rental building"] |
| Tax Assessed | |
| Automated Estimates | [Zestimate / Redfin est., or N/A] |
| Current Asking | [list price, or rent range for rentals] |
| Monthly Fees | [HOA/maintenance, or N/A for rentals] |

### Neighborhood: [Name]
| Metric | Value |
|--------|-------|
| Median Sale Price | |
| Median Rent | |
| YoY Change | |
| $/SqFt | |
| Days on Market | |
| Vacancy Rate | [if available] |
| Walk / Transit Score | |
| Market Direction | [Appreciating / Stable / Declining] |

### Comparables
[**Sale comps** — one table:]
| # | Address | Sale Date | Price | $/SqFt | Bd/Ba | SqFt | Year | DOM | Adj. Price |
|---|---------|-----------|-------|--------|-------|------|------|-----|------------|

[**Rental comps** — one table:]
| # | Building | Address | Year | Units | Studio | 1BR | 2BR | 3BR+ | Key Amenities | Dist. |
|---|---------|---------|------|-------|--------|-----|-----|------|---------------|-------|
| S | **Subject** | | | | | | | | | — |

For rental comps, show both gross rent and net effective (with concession noted) when concessions exist.

### Adjustments
[Sale: explain each adjustment and dollar amount.]
[Rental: compare amenity tiers. Note which comps have amenities the subject lacks (gym, pool, roof deck, in-unit W/D) and how those drive rent premiums.]

### Estimated Value
[Sale:]
| | Low | Mid | High |
|---|---|---|---|
| Value | | | |
| $/SqFt | | | |

[Rental — by unit type:]
| Unit Type | Low | Mid | High | $/SqFt/mo |
|-----------|-----|-----|------|-----------|

### Market Positioning (rental only)
| Unit Type | Subject | Area Median | vs. Market | Comp Range |
|-----------|---------|-------------|------------|------------|

### Key Findings
- [3-5 bullets: most decision-relevant insights, not repeating the tables]

### Market Trends
[2-3 sentences. Include: direction, YoY change, days-on-market trend, seasonal note if data is from an off-peak period.]

### Confidence: [High / Medium / Low]
[One sentence explaining: comp count, match quality, data freshness, market liquidity.]

### Sources
[Bulleted list of URLs]

---

## Guidelines

- Web search for current data. Do not rely on training data for prices, rents, or statistics.
- All dollar figures formatted with commas ($1,250,000). Rents as monthly amounts.
- $/sqft is mandatory for both sale and rental analysis.
- For rentals in concession-heavy markets (NYC, SF, etc.): always report **gross** and **net effective** rent. Net effective = (gross × lease_months - free_months × gross) / lease_months.
- Note the retrieval date for all data. Real estate data goes stale within weeks.
- Frame estimates as ranges, never point values. Wider range = lower confidence.
- If data is sparse, say so. A transparent "Low confidence — only 3 comps found, 2 require large adjustments" is better than a false-precision estimate.
- Seasonal context: note if the analysis period covers an off-peak season (winter in most US markets = lower rents/prices) and whether comps may be seasonally depressed.
