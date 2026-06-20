# Decision rubric: GO-BACK / WATCH / STILL DEAD

How to translate the re-underwriting into a call. The engine applies this
automatically; use this file to sanity-check edge cases and to write the
one-line rationale in plain deal language.

## The three calls

**GO-BACK** — Re-engage the seller this week.
- Pencils at the ask today (gap ≤ 0), **or**
- Within the re-engage band (default ≤ 5% of buyer value) — close enough that a
  seller who has moved, or a small concession, bridges it.
- The original killer was *price/financing*, which has since moved our way.

**WATCH** — Not yet, but trending into range. Set a trigger.
- Gap is open but modest (default ≤ 10%) **and** the trend is favorable (rate
  down, cap expanded, or rents up since it died).
- Name the trigger that flips it: "one more 25bp cut," "another $1/SF comp,"
  "if the seller's loan matures in Q3." Put the trigger in the one-liner.

**STILL DEAD** — Don't spend time on it.
- Gap remains wide (default > 10%) with no favorable trend, **or**
- The killer was *fundamental* — something rates and comps cannot fix.

## Fundamental killers (rates/comps can't fix these)

Bias to STILL DEAD regardless of the math when the reason involves: environmental
/ contamination / flood, structural / foundation / seismic / asbestos, zoning /
entitlement, title / easement / litigation, location / crime, tenant-credit /
anchor-rollover risk, or functional obsolescence. The engine flags these from
the `reason_died` text. A favorable rate move does **not** rescue a deal whose
problem was the dirt, the structure, or the law. The exception: if the
fundamental issue has been independently *resolved* (remediation done, rezoned,
anchor re-leased), drop the flag and re-run.

## Seller-motivation signals (can upgrade WATCH → GO-BACK)

The math says what *we* can pay; these say whether the *seller* will finally
take it. Weigh them in the one-liner and, when strong, justify a GO-BACK even at
a slightly wider gap:

- **Loan maturity / maturity wall** — a maturing loan into higher rates forces a
  sale. Check when their debt comes due.
- **Time on / off market** — months of no trade erodes "held firm."
- **Failed re-trades or fallen-out buyers** — prior deal died in DD.
- **Changed broker / price cut / new whisper** — public signs of softening.
- **Fund life / 1031 clock / partnership dispute** — structural pressure to transact.

When recommending a GO-BACK, pair the number with the lever: *"come back at our
$38.5M; their acquisition loan matures in Q4 and they've cut once already."*

## Ranking the "call this week" top 3

Prefer GO-BACK deals, ranked by smallest gap (closest to a clean yes) and
favorable trend. If there are fewer than three GO-BACKs, fill from the WATCH /
closest-to-flip list so the user always sees the three highest-probability
conversations — but label honestly (a near-miss WATCH is "worth a call to test
the seller," not "this pencils").

## Honesty and disclaimers

- Lead the output with **"PRELIMINARY — subject to change."**
- State the as-of date and source for rates and comps.
- Never fabricate a deal, a comp, or a rate. If a field is missing, say so and
  mark the call lower-confidence rather than inventing inputs.
- This is a screening triage, not an underwriting committee memo or investment
  advice.
