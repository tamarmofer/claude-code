---
description: Research comparable property sales and market data for a given address
allowed-tools: Read, Grep, Glob, WebFetch, WebSearch, Agent, TodoWrite
argument-hint: <address> [--type sale|rental|both] [--radius 0.25mi|0.5mi|1mi] [--period 6mo|12mo|24mo]
---

Research comparable property sales and market data for the specified address.

## Process

1. **Parse the request.** Identify:
   - The subject property address (normalize to full street address, city, state, zip if possible)
   - Type: `sale` (recent sales comps), `rental` (rental comps), or `both`. Default: `sale`.
   - Search radius: `0.25mi`, `0.5mi`, or `1mi`. Default: `0.5mi`.
   - Time period: `6mo`, `12mo`, or `24mo` for how far back to look. Default: `12mo`.

   Use TodoWrite to track progress through each phase.

2. **Research the subject property.** Launch two agents in parallel:

   **Agent A: Property profiler** (property-profiler agent)
   Research the subject property itself:
   - Property type (single-family, condo, co-op, multi-family, townhouse, commercial)
   - Approximate square footage, bedrooms, bathrooms
   - Lot size (if applicable)
   - Year built, recent renovations if known
   - Current Zestimate/Redfin estimate if available via web search
   - Last sale date and price
   - Tax assessed value
   - Any active listing status and asking price

   **Agent B: Neighborhood analyst** (neighborhood-analyst agent)
   Research the surrounding area:
   - Neighborhood name and boundaries
   - Median home price and price trends (YoY change)
   - Average price per square foot
   - Days on market for recent listings
   - School district and ratings (if residential)
   - Walk Score, Transit Score if available
   - Notable nearby amenities or detractors
   - Zoning information if relevant

3. **Find comparable properties.** Launch a comp-finder agent to identify 5-8 comparable recent transactions:
   - Search for properties sold within the specified time period and radius
   - Match on: property type, bedroom/bathroom count (within +/- 1), square footage (within +/- 20%), year built (within +/- 15 years)
   - For each comp, gather: address, sale date, sale price, price/sqft, bed/bath, sqft, year built, days on market
   - Also note any adjustments needed (e.g., comp has pool, comp is on a busy road, comp has been renovated)
   - Prioritize comps closest in size, condition, and proximity

   If `--type` includes `rental`, also search for comparable rental listings:
   - Active and recently leased units in the radius
   - Monthly rent, bed/bath, sqft, amenities included

4. **Synthesize the comparative market analysis.** Launch a comp-analyst agent with all gathered data to produce the final report:

   - Calculate adjusted comp values (apply adjustments for differences from subject)
   - Derive an estimated market value range (low/mid/high) based on adjusted comps
   - Calculate price per square foot range
   - If rental comps gathered, estimate monthly rent range and gross rent multiplier
   - Identify market trends (appreciating, stable, declining)

5. **Output the final report** to the terminal:

---

## Comparative Market Analysis: [Address]

### Subject Property
| Detail | Value |
|--------|-------|
| Property Type | [type] |
| Bed / Bath | [X bd / Y ba] |
| Sq Ft | [sqft] |
| Year Built | [year] |
| Last Sale | [date] at [price] |
| Tax Assessed | [value] |
| Current Estimate | [Zestimate/Redfin estimate range] |

### Neighborhood Snapshot
| Metric | Value |
|--------|-------|
| Median Home Price | [price] |
| YoY Price Change | [+/- %] |
| Avg $/Sq Ft | [price] |
| Median Days on Market | [days] |
| Walk Score | [score] |

### Comparable Sales
| # | Address | Sale Date | Price | $/SqFt | Bed/Bath | SqFt | Year | DOM | Adj. Price |
|---|---------|-----------|-------|--------|----------|------|------|-----|------------|
| 1 | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

### Adjustments Applied
[Explain adjustments: "Comp 2 adjusted -$15K for inferior condition", etc.]

### Estimated Market Value
| | Low | Mid | High |
|---|---|---|---|
| Value | $X | $Y | $Z |
| $/SqFt | $X | $Y | $Z |

[If rental comps included:]
### Rental Analysis
| Metric | Range |
|--------|-------|
| Estimated Monthly Rent | $X - $Y |
| Gross Rent Multiplier | X - Y |

### Market Trends
[2-3 sentences on whether the local market is appreciating, stable, or declining, with supporting data]

### Data Sources & Caveats
- [List URLs consulted]
- **Disclaimer:** This is an automated estimate based on publicly available data. It is not a formal appraisal. Actual property values depend on condition, features, and market factors not captured here. Consult a licensed appraiser or real estate professional for formal valuations.

---

Mark each todo item as complete as you finish each phase.

## Guidelines

- Use web search to find current property data from Zillow, Redfin, Realtor.com, county assessor records, and similar public sources.
- Be explicit when data is estimated vs. verified from a source.
- All dollar figures should be formatted with commas (e.g., $1,250,000).
- Price per square foot is a key metric - always include it.
- Note the date data was retrieved, as real estate data changes frequently.
- Adjustments should be directional and reasonable (typically $5K-$50K per feature difference for residential).
- Do NOT present the estimate as a definitive valuation. Always frame it as a data-driven estimate range.
- If public data is sparse (e.g., rural area, unusual property type), say so and widen the estimate range accordingly.
