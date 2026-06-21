# Example output — filled report (synthetic data)

This is an illustrative run of the skill against a fabricated 11-deal portfolio.
All deals, numbers, and outcomes are invented to demonstrate the format and the
evidentiary standard. Real runs must cite the user's actual deals and sourced outcomes.

---

# Underwriting Pattern Analysis — your models, Jun 2025 – Jun 2026

**Scope:** 11 deals (6 closed, 5 passed/lost). Outcomes available for 9 (2 closed deals too recent to have realized data).
**Method:** normalized assumption ledger across all 11 models; four diagnostic lenses; pattern bar = ≥3 deals, same-signed, material. This is a self-pattern read, not a deal review.

---

## Pattern 1 — Your exit cap is your entry cap. You bank reversion you never earn.

**What you do:** Across the book, you set the exit cap at or below the going-in cap, so the model prices in cap compression as a default rather than a thesis. Realized/market exit caps came in 40–85 bps wider every time. This is the single most expensive habit in the portfolio because it compounds on the largest cash flow in the model.

**Evidence (6 deals):**

| Deal | Exit cap UW | Exit cap actual/market | Miss | Value impact |
|---|---|---|---|---|
| Maple Court (closed) | 5.00% | 5.75% | −75 bps | −$4.1M reversion |
| Harbor 9 (closed) | 4.75% | 5.50% | −75 bps | −$3.3M reversion |
| Vista del Sol (closed) | 5.25% | 5.65% | −40 bps | −$1.8M reversion |
| Brick & Vine (closed) | 4.50% | 5.35% | −85 bps | −$5.2M reversion |
| Cedar Yards (closed) | 5.00% | 5.50% | −50 bps | −$2.0M reversion |
| Lowell Mills (closed) | 4.85% | 5.50% | −65 bps | −$2.6M reversion |

**Aggregate cost:** ~−65 bps mean exit-cap miss, ~−110 bps of levered IRR per deal, roughly **−$19M of modeled value** across the six closed deals. Sign consistency: 6/6.

**Why it's a pattern, not noise:** Same sign on all six, across two asset types and three submarkets — this is a house default, not a market call. Controlled for market: contemporaneous broker surveys at each underwriting date already showed terminal caps ≥ entry caps; you chose tighter anyway, so this is input bias, not an unforecastable shock. (Lens 1 and Lens 4 surfaced this as the same root cause; merged into one pattern.)

**The one adjustment:** Hard-code exit cap = going-in cap + 50 bps as the model default, and require written justification in the IC memo to set it tighter. Removes the silent compression assumption; makes optimism a deliberate, defended choice.

---

## Pattern 2 — You overpay for "amenity-rich Class A" on a rent premium the comps never confirm.

**What you do:** In Class A multifamily you underwrite a $150–225/unit amenity rent premium (package rooms, co-working, dog spa) and pay a 40–60 bps tighter going-in cap to win them. Realized achieved rents landed at roughly half the modeled premium; the Class B value-add deals in the same book beat their pro forma.

**Evidence (4 Class A deals vs book):**

| Deal | Modeled amenity premium | Achieved | Going-in cap paid | Realized vs UW IRR |
|---|---|---|---|---|
| Harbor 9 | +$210/unit | +$95/unit | 4.75% | −2.4 pp |
| Brick & Vine | +$185/unit | +$80/unit | 4.50% | −3.1 pp |
| The Magnolia (closed) | +$150/unit | +$70/unit | 4.90% | −1.9 pp |
| Riverband (closed) | +$225/unit | +$110/unit | 4.80% | −2.2 pp |
| *Class B value-add cohort (n=2)* | — | — | 5.40% avg | **+0.8 pp avg** |

**Aggregate cost:** Class A cohort averaged a −2.4 pp levered IRR shortfall on a ~50 bps richer entry basis; the cheaper Class B cohort outperformed. You are paying up for a feature set that returns less.

**Why it's a pattern, not noise:** 4/4 same-signed underperformance, isolated to one feature bucket, with a same-window control cohort that went the other way — so it's the amenity-premium assumption, not the market. Note the selection risk: in hot Class A processes you only win when you're the high bid (winner's curse), which compounds the overpay.

**The one adjustment:** Cap the underwritten amenity premium at 50% of the broker/comp-quoted figure until a deal-specific rent comp proves more, and stop crossing below a 5.0% going-in cap on Class A without a signed rent-comp set. Forces the premium to be earned in comps, not assumed.

---

## Pattern 3 — You pass on the tightening submarket because your rent growth is always a year behind it.

**What you do:** In your core target submarket (Riverside/East Bank corridor) you straight-line rent growth at ~3.0% while the market ran 5–6%. That one input prices you out, so you pass, and the asset trades 12–16% above your number to a buyer who simply used the trailing trend.

**Evidence (4 passed deals — outcomes sourced from CoStar/Real Capital comps, cited):**

| Deal (passed) | Your rent growth | Realized | Your value | Later traded | Delta | Reason you passed |
|---|---|---|---|---|---|---|
| Eastline 200 | 3.0% | 5.5% | $48.0M | $55.6M | +16% | "rent growth too aggressive" |
| Quarry Flats | 3.0% | 5.0% | $31.0M | $35.1M | +13% | "rent growth too aggressive" |
| The Beacon | 2.5% | 6.0% | $42.0M | $47.5M | +13% | "underwriting didn't pencil" |
| Stationhouse | 3.0% | 4.5% | $27.5M | $30.8M | +12% | "submarket caution" |

**Aggregate cost:** Four passes in one submarket that each traded +12–16% within ~12 months; ~$30M of acquisition volume and the associated spread, forgone. Correct-pass rate in this submarket: 0/4.

**Why it's a pattern, not noise (bias controls applied):**
- **Survivorship:** pulled all 5 passes, not just winners — 4 of the 5 were in this submarket and all 4 traded up; the one pass outside it (suburban office) correctly went down. So conservatism isn't broadly wrong — it's specifically miscalibrated here.
- **Hindsight:** at each underwriting date, trailing-12-month rent prints in this submarket were already 5%+ and absorption was positive; the higher growth was knowable then, not just in retrospect.
- **Base rate:** the wider market drifted ~4% over the window; these assets beat that *and* your number, so this is a real personal miss, not general drift.

**The one adjustment:** In any submarket where trailing-12-month rent growth exceeds your assumption by more than 150 bps, the model must default to the trailing rate (not a flat house number), and any downward override requires a one-line written reason. Stops you from importing a stale 3% into a 5% market.

---

## What this analysis could NOT establish

- **Downside-stress adequacy as a standalone pattern:** the downside-too-generous signal (a near-constant ~10 pp IRR haircut applied mechanically) was real but largely a symptom of the exit-cap default in Pattern 1 — folded in rather than double-counted. Only 4 closed deals had enough realized data to test downside breach directly; flagged, not yet a standalone claim.
- **Tax reassessment and contingency misses:** directionally under-modeled but outcome data existed for only 2 deals each — below the 3-deal bar. Watch list, not a pattern.
- **One passed deal (Granary office)** had no findable later trade; excluded from Lens 3 rather than assumed.

*No strengths section by design. The deliverable is the errors and the fixes.*
