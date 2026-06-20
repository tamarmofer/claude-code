---
name: Dead Deal Re-screen
description: This skill should be used when the user wants to re-screen, revisit, or re-underwrite passed-on or dead commercial real estate deals against today's rates and current comps. Triggers include "re-screen the deals I passed on", "pull dead deals from the pipeline tracker", "which dead deals pencil now", "re-underwrite against today's rates", "GO-BACK / STILL DEAD / WATCH call", or "what's worth a call this week" for CRE acquisitions.
version: 0.1.0
---

# Dead Deal Re-screen

Pull every deal that was passed on or went dead in a CRE pipeline tracker over a
trailing window (default 18 months), re-underwrite each at **today's** financing
rate and current comps, and emit a tight triage table with a **GO-BACK /
STILL DEAD / WATCH** call per deal plus the top 3 worth a call this week.

The thesis: a deal that didn't pencil at last fall's rates may pencil now, and a
seller who held firm may have moved. This skill quantifies both.

All output is **PRELIMINARY and subject to change** — a screening triage, not an
underwriting memo or investment advice. Never fabricate deals, rates, or comps.

## Workflow

### 1. Locate and parse the tracker

The user names a path (or Google Sheet / Drive file). Parse by format — CSV/XLSX
directly, Sheets via the `mcp__Google_Drive__*` tools, PDF via the Read tool.
See `references/rescreening-methodology.md` for per-format handling.

### 2. Select the dead/passed set in the window

Find the status column and keep rows marked dead / passed / lost / dropped /
declined / closed-lost. Apply the trailing window (default 18 months) using the
date the deal died. Exclude anything still active or won. Exact match rules are
in `references/rescreening-methodology.md`.

### 3. Refresh each deal to "today"

For each deal fill the *current* fields — `current_rate`, `current_cap`,
`market_rent_psf` — while preserving the `prior_*` values captured when it died
so the engine can show what changed. **Prefer the user's own comps / CoStar /
broker data; use the web only as a fallback.** Rents are always **$/SF/yr**.
Batch lookups (one rate per asset type, one cap/rent per submarket). Sources and
where to find them: `references/data-sources.md`.

### 4. Normalize and run the engine

Map the deals onto the engine schema (`assets/tracker-template.csv` shows the
columns) and run the deterministic underwriting engine:

```bash
python3 scripts/rescreen.py deals.csv
# tune hurdles if the user's shop differs from the defaults:
python3 scripts/rescreen.py deals.csv --target-dscr 1.25 --target-coc 0.08 --ltv 0.65
python3 scripts/rescreen.py deals.csv --json   # machine-readable
```

The engine computes, per deal: NOI (or derives it from rents), value at market
cap, the max price that holds DSCR and cash-on-cash (the binding one is "buyer
value today"), the gap to ask, DSCR/CoC at the ask, and the signed deltas for
rate / cap / rent. It then applies the rubric to assign the call and rank the
top 3. Math details: `references/rescreening-methodology.md`.

### 5. Apply judgment and write the call

The engine's call is a strong default. Refine the one-liner with **seller-
motivation signals** (loan maturity, time on market, price cuts, fund-life
pressure) that the math can't see — these can upgrade a WATCH to a GO-BACK. The
full rubric, fundamental-killer overrides, and seller signals are in
`references/decision-rubric.md`.

### 6. Output

Produce exactly the format in `assets/output-template.md`:

- A lead disclaimer line: **PRELIMINARY — subject to change**, with the as-of
  date and source of rates and comps.
- A tight table: **Deal | Why it died | What's changed | Call | One line.**
  One line each; rents in $/SF/yr; "what's changed" shows the rate/cap/rent deltas.
- **Top 3 worth a call this week**, each with buyer-value-vs-ask, the gap, and
  the reason now (including the seller lever).

Keep it tight. The user wants a scannable triage, not prose.

## Decision calls (summary)

- **GO-BACK** — pencils at the ask today, or within the re-engage band (~5%) and
  the killer was price/financing that has since moved. Re-engage this week.
- **WATCH** — gap still open but modest (~10%) and trending favorable; name the
  trigger that flips it.
- **STILL DEAD** — wide gap with no favorable trend, or a fundamental killer
  (environmental, structural, zoning, title, location, tenant credit) that rates
  and comps cannot fix.

## Guardrails

- Refresh rates/comps live — they move daily; do not rely on memory.
- Cite the as-of date and source; flag any deal scored on missing inputs as
  lower-confidence rather than inventing numbers.
- If the environment's network policy blocks web access and the user has no
  internal comps, say which inputs are missing instead of guessing.

## Resources

- **`scripts/rescreen.py`** — deterministic underwriting + call engine (stdlib only).
- **`references/rescreening-methodology.md`** — tracker parsing, refresh steps, the math.
- **`references/decision-rubric.md`** — GO-BACK/WATCH/STILL DEAD rules, seller signals.
- **`references/data-sources.md`** — where to pull today's rates and comps.
- **`assets/tracker-template.csv`** — the normalized input schema.
- **`assets/output-template.md`** — the required output format.
