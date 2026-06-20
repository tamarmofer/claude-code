# Re-screening methodology

Detailed procedure for re-underwriting dead / passed-on CRE deals. Load this
when extracting deals from a tracker or when explaining the math behind a call.

## 1. Extract the dead/passed deals (last 18 months)

The pipeline tracker can be any format. Detect and parse accordingly:

| Format | How to read |
|---|---|
| `.csv` / `.tsv` | Read directly. |
| `.xlsx` / `.xls` | `python3 -c "import openpyxl"` to check; else convert with `libreoffice --headless --convert-to csv`, or read cells via openpyxl. |
| Google Sheet (URL or Drive) | Use the `mcp__Google_Drive__*` tools (`search_files`, `read_file_content`). |
| Numbers / Notion / Airtable export | Ask the user to export to CSV, or parse the exported file. |
| `.pdf` | Read with the Read tool (it extracts tables). |

**Identify the "dead/passed" set.** Look for a status/stage column. Treat as
dead/passed any value matching (case-insensitive): `dead`, `passed`, `pass`,
`lost`, `no`, `dropped`, `killed`, `declined`, `walked`, `re-trade failed`,
`expired`, `closed-lost`. Exclude anything still `active`, `LOI`, `under
contract`, `won`, `closed-won`.

**Apply the 18-month window.** Use the date the deal died/was passed (a
"date died", "last activity", "stage date", or "lost date" column). Keep rows
where that date is within 18 months of today. If no date exists, keep the row
but note the date is unknown and confirm with the user.

**Normalize into the engine schema.** Map tracker columns onto the columns
`scripts/rescreen.py` expects (see its docstring / `assets/tracker-template.csv`).
Carry over whatever underwriting fields exist (ask, our bid, NOI or rents, the
financing rate assumed at the time, the cap rate at the time). Leave unknown
fields blank — the engine degrades gracefully.

## 2. Refresh to "today" — rates and comps

For each deal, fill the *current* fields before scoring. See
`references/data-sources.md` for where to pull these.

- `current_rate` — today's all-in debt rate for this asset type / leverage.
  Build it from the benchmark (SOFR or the 10-yr UST) + a typical spread, or
  use an agency/CMBS quote. One blended rate per asset type is fine for a
  preliminary screen.
- `current_cap` — today's market cap rate for the submarket/asset type.
- `market_rent_psf` — current asking/effective market rent in **$/SF/yr**.
- Keep the `prior_*` fields (rate, cap, rent) as captured when the deal died so
  the engine can show *what changed*.

Prefer the user's own comp set / CoStar / broker exports over public web data.
Only reach for the web when the user has no internal comps. Always note the
source and as-of date of the rate and comp data in the final output.

## 3. The underwriting math (what the engine computes)

For each deal, at **today's** rate and comps:

- **NOI** — use stabilized NOI if given; else derive:
  `NOI = SF × (market_rent_psf × (1 − vacancy) − opex_psf)`.
- **Value at market cap** — `NOI ÷ current_cap`. The market clearing price.
- **Mortgage constant `k`** — annual debt service per $1 of loan, from
  `current_rate` and amortization (interest-only ⇒ `k = rate`).
- **Max price that holds DSCR** — `max_loan = NOI ÷ (target_DSCR × k)`,
  `price = max_loan ÷ LTV`. Default `target_DSCR = 1.25×`.
- **Max price that holds cash-on-cash** —
  `price = NOI ÷ (LTV×k + target_CoC×(1−LTV))`. Default `target_CoC = 8%`.
- **Buyer value today** — the *binding* (minimum) of the DSCR and CoC prices.
  This is the most a disciplined buyer pays now.
- **Gap to ask** — `(ask − buyer_value) ÷ ask`. The number that drives the call.
- **DSCR / CoC at the ask** — diagnostics: would it even finance at the ask?

## 4. Quantify "what changed"

Report the deltas a buyer cares about (signed so positive = more favorable):

- **Rate delta** = `prior_rate − current_rate` (rates *down* helps).
- **Cap delta** = `current_cap − prior_cap` (cap *expansion* = lower price helps a buyer).
- **Rent delta** = `current_rent − prior_rent` in $/SF/yr (rents *up* lifts NOI).

A deal is "trend favorable" if any of these moved in the buyer's favor — this
is what separates a WATCH from a STILL DEAD when the gap is still open.

## 5. Tuning the targets

The defaults (`LTV 65%`, `DSCR 1.25×`, `CoC 8%`, 30-yr amort) are generic.
If the user's shop runs a different hurdle (e.g. unlevered yield-on-cost,
levered IRR, a different DSCR floor), override via CLI flags or pre-compute the
buyer value externally and pass it as `bid`. Confirm hurdles with the user when
they're unknown rather than silently assuming the defaults.
