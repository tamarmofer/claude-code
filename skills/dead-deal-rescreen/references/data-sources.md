# Data sources: today's rates and current comps

Where to pull the "what's changed since it died" inputs. Prefer the user's own
data; fall back to public sources. Always record the source and as-of date.

## Financing rate (`current_rate`)

Build an all-in rate = benchmark + spread, or take a direct quote.

- **Benchmarks** — 10-year U.S. Treasury (UST) and SOFR. Live values via
  WebSearch/WebFetch (Treasury daily par yields; CME/Fed SOFR). These move
  daily — fetch fresh, don't rely on memory.
- **Typical spreads (preliminary, confirm with the user's lenders):**
  - Agency multifamily (Freddie/Fannie): UST + ~150–250 bps.
  - CMBS / conduit (stabilized commercial): UST + ~250–400 bps.
  - Bank / life-co (low leverage, strong sponsor): tighter; bridge/debt-fund: wider.
- A single blended rate per asset type is fine for a preliminary screen. If the
  user has live lender quotes or a treasury feed, use those instead.

## Cap rates (`current_cap`, `prior_cap`)

- **Best:** the user's own comp set, CoStar / Green Street / RCA exports, or
  broker BOVs for the submarket and asset type.
- **Fallback:** WebSearch for recent broker market reports (CBRE, JLL, Cushman,
  Newmark, Marcus & Millichap) for the metro + asset type + quarter.
- Capture the cap rate *as of when the deal died* (`prior_cap`) so the engine
  can show the shift. If unavailable, estimate from the deal's original
  ask ÷ original NOI and note it as inferred.

## Rents (`market_rent_psf`, `prior_rent_psf`) — always $/SF/yr

- **Best:** the user's lease comps / rent roll comps / CoStar rent exports.
- **Fallback:** submarket reports and listing data via web search.
- Normalize everything to **$/SF/yr**. Convert if a source quotes monthly
  ($/SF/mo × 12) or annual gross vs. NNN — note which basis and keep it
  consistent with the `opex_psf` treatment.

## Gathering efficiently

- Batch the lookups: one rate read per asset type, one cap/rent read per
  submarket — not one per deal — then map onto deals.
- Cache the as-of date and cite it once in the output footer.
- If outbound web access is blocked by the environment's network policy and the
  user has no internal data, stop and tell the user which inputs are missing
  rather than guessing.
