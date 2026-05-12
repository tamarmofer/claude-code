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
2. **Auto-detects comp type** if `--type` is not specified (rental building → rental comps, condo/house → sale comps)
3. **Finds 5-8 comparables** matched on type, size, beds/baths, age, amenity tier, and proximity
4. **Synthesizes a CMA** (Comparative Market Analysis) with estimated value/rent ranges

## Output

- **Subject property summary** - type, size, beds/baths, last sale, tax assessment, automated estimates
- **Neighborhood snapshot** - median price, median rent, YoY trends, days on market, walk score
- **Comparables table** - sale comps with adjusted prices, or rental comps with gross and net effective rents
- **Adjustments** - sale: dollar adjustments per feature; rental: amenity tier comparison
- **Estimated value/rent range** - low / mid / high with $/sqft
- **Key findings** - 3-5 non-obvious insights
- **Market trends and confidence level**

## Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--type` | `sale`, `rental`, `both` | auto-detect | Comp type. Auto-detects from property profile if omitted. |
| `--radius` | `0.25mi`, `0.5mi`, `1mi` | `0.5mi` | Search radius for comparables |
| `--period` | `6mo`, `12mo`, `24mo` | `12mo` | How far back to search (sale comps only; rentals use current listings) |

## Agents

| Agent | Model | Role |
|-------|-------|------|
| **property-profiler** | sonnet | Researches subject property details from public sources |
| **neighborhood-analyst** | sonnet | Gathers area-level market data (sale and rental) and livability metrics |
| **comp-finder** | sonnet | Finds and ranks comparable recent sales or rental buildings |
| **comp-analyst** | sonnet | Synthesizes all data into a CMA with adjustments and valuation |

## Data Sources

The skill searches publicly available data from:
- Zillow, Redfin, Realtor.com, StreetEasy (NYC)
- County assessor records (tax assessed values)
- Apartments.com, Zumper (rental comps)
- WalkScore.com (walkability, transit)
- GreatSchools (school ratings)

## Caveats

- This is an automated estimate, **not a formal appraisal**
- For rentals: tracks gross and net effective rents (concessions noted)
- Seasonal context is noted when data spans off-peak periods
- Accuracy depends on public data availability (varies by market)
- Rural or unusual properties may have few comps and wider estimate ranges
- Always consult a licensed appraiser or real estate professional for formal valuations
