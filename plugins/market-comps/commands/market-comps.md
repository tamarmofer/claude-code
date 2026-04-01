---
description: Research comparable property sales and market data for a given address
allowed-tools: Read, Grep, Glob, WebFetch, WebSearch, Agent, TodoWrite
argument-hint: <address> [--type sale|rental|both] [--radius 0.25mi|0.5mi|1mi] [--period 6mo|12mo|24mo]
---

Research comparable property sales and market data for the specified address.

## Process

1. **Parse the request.** Identify:
   - The subject property address (normalize to full street address, city, state, zip if possible)
   - Type: `sale` (recent sales comps), `rental` (rental comps), or `both`. Default: `auto` (see step 2).
   - Search radius: `0.25mi`, `0.5mi`, or `1mi`. Default: `0.5mi`.
   - Time period: `6mo`, `12mo`, or `24mo` for how far back to look. Default: `12mo`.

   Use TodoWrite to track progress through each phase.

2. **Research the subject property.** Launch two agents in parallel:

   **Agent A: Property profiler** (property-profiler agent)
   Research the subject property itself:
   - Property type (single-family, condo, co-op, multi-family rental building, townhouse, commercial)
   - Approximate square footage, bedrooms, bathrooms
   - Lot size (if applicable)
   - Year built, recent renovations if known
   - Current Zestimate/Redfin estimate if available via web search
   - Last sale date and price
   - Tax assessed value
   - Any active listing status and asking price
   - Current rental listings and asking rents (if rental building)
   - HOA/co-op/condo/management fees

   **Agent B: Neighborhood analyst** (neighborhood-analyst agent)
   Research the surrounding area:
   - Neighborhood name and boundaries
   - Median home price and rent trends (YoY change)
   - Average price per square foot (sale and rental)
   - Days on market for recent listings
   - School district and ratings (if residential)
   - Walk Score, Transit Score if available
   - Notable nearby amenities or detractors
   - Vacancy rate if available
   - Zoning information if relevant

   **After step 2 completes, auto-detect comp type if user did not specify `--type`:**
   - If the subject is a **multi-unit rental building** (no individual units for sale), automatically switch to `rental` mode.
   - If the subject is a **condo, co-op, or single-family home**, default to `sale` mode.
   - If the subject has **both sale and rental activity**, default to `both`.

3. **Find comparable properties.** Launch a comp-finder agent. Tailor the search based on the comp type determined above:

   **For sale comps (`sale` or `both`):**
   - Search for properties sold within the specified time period and radius
   - Match on: property type, bedroom/bathroom count (within +/- 1), square footage (within +/- 20%), year built (within +/- 15 years)
   - For each comp, gather: address, sale date, sale price, price/sqft, bed/bath, sqft, year built, days on market
   - Note adjustments needed (e.g., comp has pool, is on a busy road, has been renovated)
   - Prioritize comps closest in size, condition, and proximity

   **For rental comps (`rental` or `both`):**
   - Search for comparable rental buildings and active/recent listings in the radius
   - Match on: property type, building class (doorman, elevator, walkup), unit types available, amenity tier, year built
   - For each comp building, gather: name, address, unit types and rent ranges by type, sqft, year built, stories/units, key amenities, distance
   - Note amenity differences that drive rent premiums (gym, pool, roof deck, in-unit W/D, concessions)
   - Also gather area median rents by unit type and YoY rent trends

   Target 5-8 comps.

4. **Synthesize the comparative market analysis.** Launch a comp-analyst agent with all gathered data to produce the final report:

   **For sale analysis:**
   - Calculate adjusted comp values (apply adjustments for differences from subject)
   - Derive estimated market value range (low/mid/high)
   - Calculate price per square foot range

   **For rental analysis:**
   - Compare subject rents to comp rents by unit type
   - Compare to neighborhood median rents (position as above/below/at market)
   - Assess amenity-tier positioning relative to comps
   - Estimate supportable rent range (low/mid/high) by unit type
   - Calculate implied rent per square foot
   - Note rent concession activity in the comp set

   For both types: identify market trends (appreciating, stable, declining) and confidence level.

5. **Output the final report** to the terminal:

---

## Comparative Market Analysis: [Address]

### Subject Property
| Detail | Value |
|--------|-------|
| Property Type | [type] |
| Bed / Bath (or Unit Types) | [details] |
| Sq Ft | [sqft or range] |
| Year Built | [year] |
| Last Sale / Current Rents | [details] |
| Tax Assessed | [value] |
| Current Estimate | [Zestimate/Redfin estimate range, if applicable] |

### Neighborhood Snapshot
| Metric | Value |
|--------|-------|
| Median Home Price | [price] |
| Median Rent | [rent, if applicable] |
| YoY Price Change | [+/- %] |
| Avg $/Sq Ft | [price] |
| Median Days on Market | [days] |
| Vacancy Rate | [rate, if available] |
| Walk Score | [score] |

[For sale comps:]
### Comparable Sales
| # | Address | Sale Date | Price | $/SqFt | Bed/Bath | SqFt | Year | DOM | Adj. Price |
|---|---------|-----------|-------|--------|----------|------|------|-----|------------|
| 1 | ... | ... | ... | ... | ... | ... | ... | ... | ... |

### Adjustments Applied
[Explain adjustments: "Comp 2 adjusted -$15K for inferior condition", etc.]

### Estimated Market Value
| | Low | Mid | High |
|---|---|---|---|
| Value | $X | $Y | $Z |
| $/SqFt | $X | $Y | $Z |

[For rental comps:]
### Comparable Rentals
| # | Building | Address | Year | Units | Studio | 1BR | 2BR | 3BR | Key Amenities | Dist. |
|---|---------|---------|------|-------|--------|-----|-----|-----|---------------|-------|
| S | **Subject** | ... | ... | ... | ... | ... | ... | ... | ... | — |
| 1 | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

### Market Positioning
| Unit Type | Subject Rent | Area Median | vs. Market | Comp Range |
|-----------|-------------|-------------|------------|------------|
| Studio | $X | $Y | +/-Z% | $A - $B |
| ... | ... | ... | ... | ... |

### Estimated Rent Ranges
| Unit Type | Low | Mid | High | $/SqFt |
|-----------|-----|-----|------|--------|
| Studio | $X | $Y | $Z | $A |
| ... | ... | ... | ... | ... |

### Key Findings
- [3-5 bullet points highlighting the most important insights]

### Market Trends
[2-3 sentences on whether the local market is appreciating, stable, or declining, with supporting data]

### Confidence Level
[High/Medium/Low with explanation: comp quality, data freshness, market liquidity]

### Data Sources & Caveats
- [List URLs consulted, with retrieval date]
- **Disclaimer:** This is an automated estimate based on publicly available data. It is not a formal appraisal. Actual property values depend on condition, features, and market factors not captured here. Consult a licensed appraiser or real estate professional for formal valuations.

---

Mark each todo item as complete as you finish each phase.

## Guidelines

- Use web search to find current property data from Zillow, Redfin, StreetEasy, Realtor.com, county assessor records, and similar public sources.
- Be explicit when data is estimated vs. verified from a source.
- All dollar figures should be formatted with commas (e.g., $1,250,000).
- Price per square foot is a key metric - always include it (both sale $/sqft and rent $/sqft as applicable).
- Note the date data was retrieved, as real estate data changes frequently.
- For sale comps: adjustments should be directional and reasonable (typically $5K-$50K per feature difference for residential).
- For rental comps: compare by amenity tier and unit type rather than dollar adjustments. Note concessions (free months, reduced deposits) as they affect net effective rent.
- Do NOT present the estimate as a definitive valuation. Always frame it as a data-driven estimate range.
- If public data is sparse (e.g., rural area, unusual property type), say so and widen the estimate range accordingly.
