# Market Comps

Research comparable property sales and market data for a given address to support real estate valuation decisions.

## Usage

```
/market-comps <address> [--type sale|rental|both] [--radius 0.25mi|0.5mi|1mi] [--period 6mo|12mo|24mo]
```

### Examples

```
/market-comps 420 E 80th St, New York, NY
/market-comps 1234 Oak Ave, Austin, TX --type both
/market-comps 555 Market St, San Francisco --radius 0.25mi --period 6mo
```

## How It Works

1. **In parallel:** profiles the subject property AND analyzes the neighborhood market
2. **Finds comparable sales** - 5-8 recently sold properties matched on type, size, beds/baths, age, and proximity
3. **Applies adjustments** for differences between comps and subject (location, condition, size, features)
4. **Produces a CMA** (Comparative Market Analysis) with estimated market value range

## Output

The report includes:

- **Subject property summary** - type, size, beds/baths, last sale, tax assessment, automated estimates
- **Neighborhood snapshot** - median price, YoY trends, days on market, walk score
- **Comparable sales table** - each comp with raw and adjusted prices
- **Adjustment details** - what was adjusted and why
- **Estimated market value** - low / mid / high range with $/sqft
- **Rental analysis** - estimated rent and gross rent multiplier (if `--type rental` or `both`)
- **Market trends** - appreciating, stable, or declining
- **Confidence level** - based on comp quality and data availability
- **Disclaimer** - not a formal appraisal

## Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--type` | `sale`, `rental`, `both` | `sale` | Type of comps to search for |
| `--radius` | `0.25mi`, `0.5mi`, `1mi` | `0.5mi` | Search radius for comparables |
| `--period` | `6mo`, `12mo`, `24mo` | `12mo` | How far back to search for sales |

## Agents

| Agent | Model | Role |
|-------|-------|------|
| **property-profiler** | sonnet | Researches subject property details from public sources |
| **neighborhood-analyst** | sonnet | Gathers area-level market data and livability metrics |
| **comp-finder** | sonnet | Finds and ranks comparable recent sales/rentals |
| **comp-analyst** | sonnet | Synthesizes all data into a CMA with adjustments and valuation |

## Data Sources

The skill searches publicly available data from:
- Zillow (Zestimate, property details, recently sold)
- Redfin (estimates, market insights)
- Realtor.com (listings, sold data)
- County assessor records (tax assessed values)
- WalkScore.com (walkability, transit)
- GreatSchools (school ratings)

## Caveats

- This is an automated estimate, **not a formal appraisal**
- Accuracy depends on public data availability (varies by market)
- Rural or unusual properties may have few comps and wider estimate ranges
- Data freshness varies by source - dates are noted in the report
- Always consult a licensed appraiser or real estate professional for formal valuations
