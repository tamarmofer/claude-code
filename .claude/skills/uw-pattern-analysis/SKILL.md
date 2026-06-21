---
name: UW Pattern Analysis
description: This skill should be used when a real-estate investor asks to find their own systematic underwriting biases across a folder of historical UW models and deal notes — e.g. "where am I systematically wrong in my underwriting", "read my UW models from the last 12 months and find my pattern", "what building type or feature do I overpay for", "which assumptions do I keep missing", "did deals I passed later trade up", "analyze my downside cases", "my own pattern, not a deal review". Produces a small number of evidence-backed personal patterns plus one corrective adjustment each. Not for reviewing a single deal.
version: 0.1.0
---

# UW Pattern Analysis

Find an underwriter's *own* repeated, systematic errors across many deals — not a review of any single deal. The output is a short, blunt list of patterns, each proven with deal-level evidence and dollar magnitude, each paired with one mechanical adjustment that prevents it next time.

## The one rule that makes this hard

A **deal review** asks "was this deal underwritten well?" A **pattern analysis** asks "what does this person get wrong *every time*?" These are different work. A pattern requires the same error, in the same direction, across multiple independent deals. One bad call is noise. Treat everything as noise until it clears the pattern bar (see `references/pattern-bar.md`).

Two failure modes to actively resist:
- **Flattery / sign-flipping.** Do not soften findings, do not pad with strengths, do not report "areas of opportunity." The user explicitly asked not to be flattered. State the error, the cost, the fix.
- **Hindsight & survivorship bias.** "Deal X went up after they passed" is only evidence if the *information available at underwriting* should have changed the call. Controlling for this is the analyst's job, not the user's. See `references/pattern-bar.md`.

## Inputs and assumptions

- **Models:** Excel `.xlsx`/`.xlsm`. Models vary; extraction is label-driven and must be calibrated against one real model before trusting it (Step 2).
- **Deal calls / notes:** any accompanying text (`.md`, `.txt`, `.docx`, PDF) — used for deal status (closed / passed / lost), stated thesis, and the price actually paid or bid.
- **Passed-deal ground truth:** what a passed deal *later traded at* is pulled from the web / comps (WebSearch, then WebFetch) — see Step 4. Without it, the "passed" lens is just opinion.

## Workflow

Run these in order. Do not jump to conclusions before Step 5; the diagnostics, not intuition, decide the patterns.

### Step 1 — Inventory the folder

Walk the folder. Build a deal list: one entry per deal with name, file path(s), date, asset/building type, and status (closed, passed, lost). Read accompanying notes for status and price. Report the count by status — a credible pattern analysis needs roughly **8+ deals**, with a mix of closed and passed. If there are fewer, say so plainly and scope the claims down.

### Step 2 — Calibrate extraction on ONE model first

UW templates differ per shop. Before bulk extraction, open one representative model and confirm where each canonical assumption lives (entry cap, rent growth, exit cap, capex, IRR, etc. — full list in `references/extraction-schema.md`). Adjust the label map in `scripts/extract_models.py` if the labels don't match. Only then run it across the folder.

### Step 3 — Build the normalized deal ledger

Run `scripts/extract_models.py <folder> -o deals.csv`. It scans each workbook, locates assumption cells by matching adjacent labels, and emits one row per deal with the canonical fields. **Read the CSV and sanity-check it** against the real models — flag any field the heuristic missed rather than silently dropping it. The ledger is the spine of the whole analysis; garbage here invalidates everything downstream.

### Step 4 — Get ground truth (the step everyone skips)

A pattern needs *outcomes*, not just inputs.
- **Closed deals:** pair each underwritten assumption with what actually happened (actual rent growth, actual capex, actual exit/current value, realized vs pro-forma IRR). Pull actuals from any asset-management / actuals files in the folder; where missing, mark the field unknown rather than guessing.
- **Passed / lost deals:** for each, use **WebSearch** then **WebFetch** to find what it later traded at, the winning bid, or current valuation/comps. Record the delta vs the user's underwritten value and *why* they passed (from notes). Cite the source. If nothing is findable, mark unknown — never fabricate a trade.

Record outcomes in `deals.csv` (or a paired `outcomes.csv`).

### Step 5 — Run the four diagnostic lenses

For each lens, run the test in `references/failure-modes.md` (also automated in `scripts/analyze_patterns.py deals.csv`). Each lens emits *candidate* patterns with frequency, average miss, and dollar impact:

1. **Downside cases that ran too generous** — across deals, how far below base does the "downside" actually go, and did realized outcomes breach it? A downside that's a 10% haircut every time, never stress-testing the real risks, is a pattern.
2. **Building type / feature overpaid for** — group deals by type and feature; where does the user consistently pay a richer going-in cap / price-per-unit than warranted by realized performance? Same sign across the group = pattern.
3. **Passed deals that later traded up** — among passed deals, how often did the asset trade above the user's number, and is there a common reason for the pass (e.g. always too conservative on a specific submarket or feature)?
4. **Recycled assumptions that keep missing** — for each reused input (rent growth, exit cap, lease-up speed, bad debt, capex/contingency), the distribution of underwritten vs actual. A consistently signed miss is a pattern; a symmetric scatter is not.

### Step 6 — Qualify and rank

Apply the pattern bar (`references/pattern-bar.md`): a candidate is a pattern only if it (a) appears in **≥3 deals**, (b) misses in the **same direction**, and (c) is **material** in dollars or bps. Drop one-offs and market-wide effects the user couldn't have controlled. Rank survivors by *evidence strength × dollar impact*. Keep the **top 3** — no more, even if more qualify; force the prioritization.

### Step 7 — Write the output

Use `assets/pattern-report-template.md`. For each of the 3 patterns:
- **Name it** in one blunt line.
- **Evidence:** name the specific deals, with the numbers (underwritten vs actual/market, the miss, the dollars). Minimum three deals.
- **The cost:** aggregate dollar or bps impact.
- **The one adjustment:** a single, mechanical, checkable change to the process or model — a hard input cap, a required stress, a default flip — not "be more careful."

Close with what was checked and what couldn't be (unknown outcomes, thin samples). No summary of strengths. No encouragement.

## Anti-flattery checklist (apply before sending)

- Every pattern names ≥3 specific deals with real numbers. If not, it's an opinion — cut it or downgrade it.
- No strengths section, no hedging adjectives, no "great instincts." The deliverable is the 3 errors and 3 fixes.
- Each adjustment is mechanical enough that a junior analyst could enforce it without judgment.
- Hindsight/survivorship explicitly addressed for any passed-deal claim.
- If the data can't support 3 real patterns, report fewer and say why — do not manufacture a third.

## Resources

- **`references/extraction-schema.md`** — canonical assumption fields to pull from every model, their common labels, and the actual/outcome each pairs with.
- **`references/failure-modes.md`** — the four lenses in detail: the exact test, the trap, and how each error typically shows up in RE underwriting.
- **`references/pattern-bar.md`** — thresholds for pattern vs noise; controlling for market vs skill; handling hindsight, survivorship, and passed-deal ground truth honestly.
- **`scripts/extract_models.py`** — label-driven extractor: folder of workbooks → `deals.csv`.
- **`scripts/analyze_patterns.py`** — runs the four lenses over `deals.csv` and prints ranked candidate patterns with stats.
- **`assets/pattern-report-template.md`** — the output format for the final 3-pattern report.
- **`examples/example-report.md`** — a fully populated report on synthetic data showing the expected depth, evidence standard, and blunt tone.
