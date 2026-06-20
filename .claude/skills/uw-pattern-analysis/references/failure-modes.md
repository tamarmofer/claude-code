# Failure Modes — the four lenses

Each lens has: the **test** (what to compute), the **pattern signal** (what qualifies it as systematic vs noise), the **trap** (the analytical mistake that produces a false pattern), and **common manifestations** in real-estate underwriting. `scripts/analyze_patterns.py` computes the raw test; this file is the judgment layer.

---

## Lens 1 — Downside cases that ran too generous

**Test.** For each deal, compute the *downside spread* = (base-case return − downside-case return) and the *downside delta on key inputs* (how much rent growth / exit cap / occupancy actually moves in the downside). Then compare the downside case to the **realized** outcome for closed deals. Tabulate: (a) is the downside spread roughly constant across deals? (b) for closed deals, did the realized outcome land *below* the modeled downside?

**Pattern signal.** A real pattern looks like one of:
- The downside is a near-constant haircut (e.g. always ~10% IRR shaved, exit cap always +25–50 bps) regardless of the deal's actual risk — i.e. the downside is decorative, not analytic.
- Realized outcomes breached the modeled downside in **≥3 deals** → the "worst case" wasn't a worst case.
- The downside never moves the inputs that actually sink RE deals together (rent growth *and* exit cap *and* lease-up slipping at once) — single-variable stresses only.

**Trap.** A downside breached by a genuine macro shock that hit everyone (rate spike, 2022-style cap decompression) is not a personal pattern unless the user's downsides were systematically thinner than a reasonable analyst's. Control for market: if peers' downsides also broke, it's beta, not the user.

**Common manifestations.**
- Downside = "base minus 10%" applied mechanically.
- Exit cap in downside only +25 bps when entry-to-exit history says +75–100 is plausible.
- Downside holds rent growth flat but never negative; never models concession wars or a lease-up that stalls.
- Bad debt / economic vacancy not stressed at all in the downside.
- No correlation modeled: the downside moves one lever while holding the correlated ones at base.

---

## Lens 2 — A building type or feature consistently overpaid for

**Test.** Group deals by `asset_type` and by `subtype_feature` (Class, vintage, construction type, value-add vs core, submarket). For each group compute average `going_in_cap` and `price_per_unit`/`price_psf` paid, and the **realized** return or value vs underwriting. Look for a group where the user reliably pays a richer price (tighter cap / higher PSF) *and* the realized performance underdelivers relative to other groups.

**Pattern signal.** Same-signed underperformance across **≥3 deals in the same type/feature bucket**: the user pays up for a characteristic that doesn't pay off. Classic shapes: overpaying for "amenity-rich Class A" that never commands the modeled premium; paying core-like caps for value-add execution risk; a pet submarket where the user's basis is always 5–10% above where it clears.

**Trap.** Don't confuse *paying more* with *overpaying*. Higher price is only overpayment if realized returns lag. Also separate selection from skill: if the user only ever *wins* the overheated deals in a hot bucket (winner's curse), the bucket — not the user's valuation — may be the issue. Both are actionable but the fix differs.

**Common manifestations.**
- Pays a premium for new/Class-A vintage on the thesis of "lower capex," then the realized capex/turn gap vs Class B doesn't justify the cap spread.
- Overpays for a specific feature (covered parking, in-unit W/D, "walkability") modeled as a rent premium the comps never confirm.
- A favored submarket where the user's basis is consistently above clearing — emotional anchor.
- Value-add deals underwritten at near-core entry caps because the renovation premium is double-counted (in both NOI growth and cap compression).

---

## Lens 3 — Deals passed that later traded up

**Test.** For each `passed`/`lost` deal, pull the later trade price / current value (web/comps, cited) and compute the delta vs the user's underwritten value and vs the asking price at the time. Record the **stated reason for passing** from notes. Then look for a common reason across the misses.

**Pattern signal.** Not "some passed deals went up" — *most things go up over a long enough window*. The pattern is a **common, repeated reason** for passing on deals that then outperformed: e.g. always knocked rent growth too low in a specific submarket, always over-penalized a feature, always required a downside that no winning bidder required. **≥3 passes with the same root cause** and a real positive delta.

**Trap — this is the most bias-prone lens.**
- **Hindsight:** judge the pass on *information available then*, not what's known now. If the asset traded up only because of an unforecastable rate cut, the pass wasn't wrong.
- **Survivorship:** passed deals that *went down* must be counted too. Pull a sample of passes that underperformed; if passes are right more often than wrong, conservatism isn't a defect. Quantify the hit rate, don't cherry-pick the ones that stung.
- **Base rate:** compare the user's passed-deal outperformance rate to the general market drift over the same window. Beating the user's own number isn't impressive if everything beat it.

**Common manifestations.**
- Systematically under-modeling rent growth in a tightening submarket → priced out every time.
- A blanket exit-cap conservatism that no competitive bidder shared → never clears.
- Over-weighting a single risk (one soft comp, deferred maintenance) into a full pass.

---

## Lens 4 — Reused assumptions that keep missing

**Test.** For each recycled input (`rent_growth`, `exit_cap`, `lease_up_pace`, `bad_debt`, `expense_growth`, `tax_reassessment`, `contingency`), build the distribution of **underwritten minus actual** across all closed deals. Report mean miss, sign consistency, and dollar/bps impact.

**Pattern signal.** A **consistently signed** miss is a pattern; a symmetric scatter around zero is calibrated noise. The dangerous ones:
- `exit_cap` underwritten tighter than realized in most deals (optimistic reversion).
- `rent_growth` straight-lined above realized (the most common and most expensive miss).
- `lease_up_pace` faster than realized (stabilization always slips a quarter or two).
- `tax_reassessment` under-modeled (taxes reset on sale and the model lags).
- `contingency` / `renovation_budget` under actual spend every time.
- `bad_debt` / economic vacancy below realized.

**Trap.** A miss that is *unbiased on average* but high-variance is a different problem (precision, not bias) and gets a different fix (wider ranges, not a shifted default). Only a mean miss with consistent sign justifies moving the default. Also weight by dollars: a 50 bps exit-cap bias on a long-hold deal dwarfs a rent-growth rounding error.

**Common manifestations.**
- Exit cap = entry cap (no decompression cushion) used as a house default.
- Year-1 rent growth set to the brochure number, not the trailing realized.
- "Stabilize in 12 months" copied between deals regardless of unit count or market depth.
- Contingency fixed at 5% while actual overruns run 10–15%.

---

## Cross-lens discipline

- The same root cause can surface in several lenses (e.g. optimistic exit cap shows up in Lens 1 and Lens 4). Merge them into one pattern stated at the root-cause level; don't report the same error three times to pad to three.
- Always translate to **dollars or bps**, not just frequency. "Misses rent growth" is weak; "rent-growth optimism cost ~110 bps of levered IRR across 6 closed deals, ~$Xm of value" is a finding.
- If a candidate can't be tied to ≥3 specific deals with numbers, it does not ship.
