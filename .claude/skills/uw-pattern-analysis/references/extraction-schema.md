# Extraction Schema — what to pull from every UW model

The goal is one normalized row per deal so deals become comparable. Models vary by shop and by analyst, so each field below lists the **canonical name** used in `deals.csv`, the **common labels** to match in the workbook, and the **outcome/actual** it must be paired with in Step 4. A field with no paired outcome can describe an input but can never prove a pattern.

Pull both the **base case** and the **downside case** value for any field that differs between cases (rent growth, exit cap, occupancy, returns). The gap between them is itself a signal (Lens 1).

## Identity & status
| canonical | common labels | notes |
|---|---|---|
| `deal_name` | tab name, header cell, file name | |
| `date` | "as of", "IC date", file mtime | underwriting date, not close date |
| `asset_type` | "property type", "product type" | multifamily / office / industrial / retail / hotel / etc. |
| `subtype_feature` | "vintage", "class", "construction type" | Class A/B/C, garden vs mid-rise, wood vs concrete, value-add vs core — the *feature* axis for Lens 2 |
| `market` / `submarket` | "MSA", "submarket" | needed to control for market vs skill |
| `status` | from notes | closed / passed / lost (lost bid) |

## Entry / basis
| canonical | common labels | outcome to pair |
|---|---|---|
| `purchase_price` | "purchase price", "total consideration" | actual close price (closed) or winning bid (passed/lost) |
| `price_per_unit` / `price_psf` | "$/unit", "$/SF", "$/key" | vs market comps at the time |
| `going_in_cap` | "going-in cap", "entry cap", "Y1 cap" | vs realized Y1 NOI / price |
| `entry_occupancy` | "in-place occ", "physical occ" | vs actual at takeover |

## Income growth assumptions (the recycled-assumption suspects)
| canonical | common labels | outcome to pair |
|---|---|---|
| `rent_growth_y1` … `rent_growth_yN` | "rent growth", "market rent growth", "trend rate" | realized rent growth per year |
| `loss_to_lease_capture` | "LTL", "mark-to-market" | realized capture pace |
| `other_income_growth` | "other income", "RUBS growth" | realized |
| `bad_debt` / `economic_vacancy` | "bad debt", "credit loss", "economic vacancy" | realized — chronically under-modeled |
| `stabilized_occupancy` | "stabilized occ", "vacancy" | realized stabilized |
| `lease_up_pace` | "absorption", "units/month", "months to stabilize" | realized lease-up speed |

## Expense & capital assumptions
| canonical | common labels | outcome to pair |
|---|---|---|
| `expense_growth` | "expense growth", "OpEx inflation" | realized |
| `tax_reassessment` | "tax growth", "reassessment", "millage" | realized post-sale taxes — frequent miss |
| `renovation_budget` | "reno/unit", "capex budget", "hard costs" | actual spend |
| `contingency` | "contingency %" | actual overrun |
| `capex_reserve` | "replacement reserve", "$/unit/yr" | actual |

## Exit assumptions
| canonical | common labels | outcome to pair |
|---|---|---|
| `hold_period` | "hold", "investment period" | actual hold |
| `exit_cap` | "exit cap", "terminal cap", "reversion cap" | market cap at actual/expected sale |
| `exit_cap_spread` | exit cap − entry cap | should usually be ≥ 0; persistent ≤ 0 is a tell |
| `terminal_value` | "reversion", "residual value", "net sale proceeds" | realized/current value |

## Financing
| canonical | common labels | notes |
|---|---|---|
| `ltv` / `ltc` | "leverage", "LTV", "LTC" | |
| `interest_rate` | "rate", "coupon", "all-in rate" | |
| `io_period` | "interest only", "IO" | |
| `dscr` / `debt_yield` | "DSCR", "debt yield" | |

## Returns (base AND downside)
| canonical | common labels | outcome to pair |
|---|---|---|
| `unlevered_irr` | "unlevered IRR", "property IRR" | realized (closed/sold) |
| `levered_irr` | "levered IRR", "equity IRR", "project IRR" | realized |
| `equity_multiple` | "EM", "MOIC", "equity multiple" | realized |
| `downside_levered_irr` | downside/bear case IRR | did realized breach it? |
| `coc_y1` | "cash-on-cash", "cash yield" | realized |

## Extraction mechanics
- Match labels case-insensitively, allowing punctuation/whitespace variation. Grab the **nearest numeric cell to the right, then below** the label.
- Percentages may be stored as `0.03` or `3.0` or `"3.0%"` — normalize to a number in percent. Flag ambiguous ones rather than guessing.
- When a field appears per-year (rent growth, occupancy), capture the **vector** and also a summary (`y1`, and the average or terminal).
- If a label matches multiple cells, prefer the one inside the labeled "Assumptions" / "Inputs" block; record the others as candidates for manual review.
- Never silently coerce a missing field to 0. Missing = `unknown`. A zero is a real assumption; absence is not.
