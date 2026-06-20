# The Pattern Bar — separating signal from noise

A pattern analysis is only as honest as its threshold for calling something a pattern. The user asked for *their* pattern, not a deal review and not flattery. That means most candidates must be rejected. This file is the gate.

## A candidate is a pattern only if ALL three hold

1. **Frequency — appears in ≥3 independent deals.** Two is a coincidence. One is an anecdote. Independent means different deals, not the same deal counted across cases or years.
2. **Direction — the error has the same sign every time.** A rent-growth assumption that's too high on three deals and too low on three is *calibrated*, not biased. Same-signed misses are the only ones a default change can fix.
3. **Materiality — it moves dollars or bps that matter.** Quantify the impact: bps of IRR, dollars of value, or a clear effect on the buy/pass decision. A consistent but trivial miss is not worth one of the three slots.

If a candidate fails any one, it does not ship. Report fewer than three patterns before shipping a weak one.

## Control for market vs skill (do not skip)

The central confound: did the user err, or did the market move? An error that hit every reasonable underwriter is **beta**, not a personal pattern.

- For each candidate, ask: would a competent peer underwriting the same deal, with the same information *at that time*, have made the same call? If yes, it's not the user's pattern.
- Distinguish **input bias** (chose an assumption worse than the evidence supported) from **realized shock** (assumption was reasonable; the world moved). Only input bias is a personal pattern.
- Where possible, benchmark the user's assumption against the contemporaneous market consensus (comps, broker surveys, the actual clearing price). "Below where it cleared, repeatedly" is skill evidence; "below where it ended up after a macro surprise" is not.

## Hindsight bias (Lens 3 especially)

- Judge every past decision on the information set available **on the underwriting date**, never on outcomes known now.
- A passed deal that traded up is evidence only if the inputs the user got wrong were *knowable then*. If the upside came from an unforecastable event, the pass was correct given the information.
- State the information set explicitly when making a hindsight-sensitive claim.

## Survivorship bias (Lens 3 especially)

- Passed deals that later **underperformed** are part of the sample. Pull them too.
- Compute the pass **hit rate**: of all passes with knowable outcomes, what fraction would have made money vs lost money? If passes are right more often than not, conservatism is working — do not pathologize it.
- Never build the "you're too conservative" pattern from only the passes that stung.

## Base rates

- Compare the user's miss against the relevant base rate, not against zero. If rents broadly rose 4% and the user assumed 3% and got 4%, that's a 1% miss in a rising market — small. Context the magnitude.
- For passed-deal outperformance, compare to general market drift over the same window before calling it a personal miss.

## Sample-size honesty

- **8+ deals** with mixed status is a reasonable floor for any pattern claim. State the n for every pattern.
- With a thin sample, downgrade language from "you systematically do X" to "the available deals suggest X; confirm with more." Do not overclaim from 3 deals total.
- If outcomes are unknown for most deals (no actuals, no findable comps), say so — an inputs-only analysis can flag *suspicious* assumptions but cannot prove a *missing* one.

## Merge, don't pad

- One root cause that surfaces in multiple lenses is **one** pattern. Report it at the root-cause level.
- Forcing exactly three when only two clear the bar is itself a form of flattery (manufacturing rigor). Ship two strong patterns over three with a weak third, and say why.

## Final gate before writing

For each surviving pattern, confirm on paper:
- [ ] ≥3 named deals with underwritten-vs-actual/market numbers
- [ ] same sign across all cited deals
- [ ] dollar or bps impact stated
- [ ] market-vs-skill addressed
- [ ] hindsight/survivorship addressed if it's a passed-deal claim
- [ ] the fix is a single mechanical change, not "be more careful"
