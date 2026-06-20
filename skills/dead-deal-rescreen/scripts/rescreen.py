#!/usr/bin/env python3
"""Dead-deal re-screening underwriting engine.

Re-underwrites passed-on / dead commercial real estate (CRE) deals against
today's financing rate and current comps, then emits a GO-BACK / WATCH /
STILL DEAD call per deal plus a ranked "call this week" shortlist.

This is a DETERMINISTIC math engine only. It does not fetch market data and
does not make investment decisions for you. Feed it a normalized deals file
(CSV or JSON) whose rate/cap/rent fields have ALREADY been refreshed to
today's market (see SKILL.md for how to gather those). Output is PRELIMINARY
and SUBJECT TO CHANGE. Not investment advice.

Usage:
    python3 rescreen.py deals.csv
    python3 rescreen.py deals.json --target-dscr 1.25 --target-coc 0.08
    python3 rescreen.py deals.csv --json        # machine-readable output

Normalized input columns (CSV header / JSON keys). Unknown columns are ignored;
missing optional fields degrade gracefully.

    deal              (str)   deal / property name              [required]
    reason_died       (str)   why it died (free text)
    date_died         (str)   ISO date the deal died/passed
    ask               (num)   seller's last ask price ($)       [required-ish]
    bid               (num)   our last bid / our value ($)
    noi               (num)   stabilized NOI ($/yr). If absent, derived from
                              rentable_sf * (market_rent_psf*(1-vacancy) - opex_psf)
    rentable_sf       (num)   rentable square feet
    market_rent_psf   (num)   CURRENT market rent, $/SF/yr
    prior_rent_psf    (num)   rent assumed when the deal died, $/SF/yr
    vacancy           (num)   stabilized vacancy as fraction (0.05 = 5%)
    opex_psf          (num)   operating expense, $/SF/yr
    prior_rate        (num)   all-in debt rate when deal died (0.065 = 6.5%)
    current_rate      (num)   all-in debt rate TODAY (0.060 = 6.0%)   [required-ish]
    ltv               (num)   loan-to-value fraction (default 0.65)
    amort_years       (num)   amortization in years; 0 = interest-only (default 30)
    prior_cap         (num)   market cap rate when deal died (0.060 = 6.0%)
    current_cap       (num)   market cap rate TODAY (0.065 = 6.5%)
"""

import argparse
import csv
import json
import sys

# Reasons that rates/comps cannot fix -> bias toward STILL DEAD.
FUNDAMENTAL_KEYWORDS = (
    "environmental", "contamination", "flood", "structural", "foundation",
    "zoning", "entitlement", "title", "easement", "litigation", "lawsuit",
    "location", "crime", "tenant credit", "anchor", "functional obsolesc",
    "seismic", "asbestos", "deferred maintenance", "earthout",
)

DEFAULTS = {
    "ltv": 0.65,
    "amort_years": 30.0,
    "target_dscr": 1.25,
    "target_coc": 0.08,
    "reengage_gap": 0.05,   # within 5% of buyer value -> re-openable
    "watch_gap": 0.10,      # within 10% AND trend favorable -> watch
}


def _num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace("$", "").replace(",", "").replace("%", "")
    if s == "" or s.lower() in ("na", "n/a", "none", "-"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def mortgage_constant(rate, amort_years):
    """Annualized mortgage constant (annual debt service / loan balance)."""
    if rate is None:
        return None
    if not amort_years or amort_years <= 0:
        return rate  # interest-only
    i = rate / 12.0
    n = amort_years * 12.0
    if i == 0:
        return 1.0 / amort_years
    pmt = i / (1.0 - (1.0 + i) ** (-n))
    return pmt * 12.0


def derive_noi(row):
    sf = _num(row.get("rentable_sf"))
    rent = _num(row.get("market_rent_psf"))
    if sf is None or rent is None:
        return None
    vac = _num(row.get("vacancy")) or 0.0
    opex = _num(row.get("opex_psf")) or 0.0
    return sf * (rent * (1.0 - vac) - opex)


def max_price_for_dscr(noi, k, ltv, target_dscr):
    if not all(v not in (None, 0) for v in (noi, k, ltv)):
        return None
    max_loan = noi / (target_dscr * k)
    return max_loan / ltv


def max_price_for_coc(noi, k, ltv, target_coc):
    # CoC = (NOI - loan*k) / equity >= target, loan = ltv*price, equity=(1-ltv)*price
    # NOI >= price * (ltv*k + target*(1-ltv))
    denom = ltv * k + target_coc * (1.0 - ltv)
    if noi is None or denom <= 0:
        return None
    return noi / denom


def screen(row, opts):
    name = (row.get("deal") or "Unnamed").strip()
    reason = (row.get("reason_died") or "").strip()
    ask = _num(row.get("ask"))
    bid = _num(row.get("bid"))
    noi = _num(row.get("noi"))
    if noi is None:
        noi = derive_noi(row)

    ltv = _num(row.get("ltv")) or opts["ltv"]
    amort = _num(row.get("amort_years"))
    amort = opts["amort_years"] if amort is None else amort
    cur_rate = _num(row.get("current_rate"))
    pri_rate = _num(row.get("prior_rate"))
    cur_cap = _num(row.get("current_cap"))
    pri_cap = _num(row.get("prior_cap"))
    cur_rent = _num(row.get("market_rent_psf"))
    pri_rent = _num(row.get("prior_rent_psf"))

    k = mortgage_constant(cur_rate, amort)

    value_cap = noi / cur_cap if (noi and cur_cap) else None
    price_dscr = max_price_for_dscr(noi, k, ltv, opts["target_dscr"]) if k else None
    price_coc = max_price_for_coc(noi, k, ltv, opts["target_coc"]) if k else None

    # The most a disciplined buyer pays today (binding constraint).
    candidates = [p for p in (price_dscr, price_coc) if p]
    buyer_max = min(candidates) if candidates else (value_cap if value_cap else bid)

    gap = None
    if ask and buyer_max:
        gap = (ask - buyer_max) / ask

    # DSCR / CoC at the ask, today's rate.
    dscr_at_ask = coc_at_ask = None
    if ask and noi and k:
        loan = ltv * ask
        ds = loan * k
        dscr_at_ask = noi / ds if ds else None
        equity = ask - loan
        coc_at_ask = (noi - ds) / equity if equity else None

    # What changed (signed; positive = more favorable to a buyer).
    rate_delta = (pri_rate - cur_rate) if (pri_rate is not None and cur_rate is not None) else None
    cap_delta = (cur_cap - pri_cap) if (pri_cap is not None and cur_cap is not None) else None  # expansion helps buyer
    rent_delta = (cur_rent - pri_rent) if (pri_rent is not None and cur_rent is not None) else None
    trend_favorable = any(d is not None and d > 0 for d in (rate_delta, cap_delta, rent_delta))

    fundamental = any(kw in reason.lower() for kw in FUNDAMENTAL_KEYWORDS)

    call, why = decide(gap, trend_favorable, fundamental, opts)

    return {
        "deal": name,
        "reason_died": reason,
        "noi": noi,
        "ask": ask,
        "bid": bid,
        "buyer_value_today": buyer_max,
        "value_at_market_cap": value_cap,
        "gap_to_ask": gap,
        "dscr_at_ask": dscr_at_ask,
        "coc_at_ask": coc_at_ask,
        "rate_delta": rate_delta,
        "cap_delta": cap_delta,
        "rent_delta_psf": rent_delta,
        "trend_favorable": trend_favorable,
        "fundamental_flag": fundamental,
        "call": call,
        "one_liner": why,
        "_score": rank_score(call, gap, trend_favorable),
    }


def decide(gap, trend_favorable, fundamental, opts):
    if fundamental and (gap is None or gap > 0):
        return "STILL DEAD", "Killer was structural/locational, not priced by rates or comps."
    if gap is None:
        return "WATCH", "Insufficient inputs to re-underwrite; refresh NOI/ask to confirm."
    if gap <= 0:
        return "GO-BACK", "Pencils at the ask today; re-engage before the market re-rates."
    if gap <= opts["reengage_gap"]:
        return "GO-BACK", f"Within {gap*100:.0f}% of our value; gap is bridgeable if the seller has moved."
    if gap <= opts["watch_gap"] and trend_favorable:
        return "WATCH", f"{gap*100:.0f}% gap but trend is moving our way; one more rate/comp print flips it."
    return "STILL DEAD", f"Still {gap*100:.0f}% over what it supports today; no path without a big price cut."


def rank_score(call, gap, trend_favorable):
    base = {"GO-BACK": 100, "WATCH": 50, "STILL DEAD": 0}[call]
    if gap is not None:
        base -= gap * 100          # smaller gap ranks higher
    if trend_favorable:
        base += 5
    return base


def load(path):
    if path.lower().endswith(".json"):
        with open(path) as f:
            data = json.load(f)
        return data if isinstance(data, list) else data.get("deals", [])
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def fmt_money(v):
    return f"${v/1e6:.2f}M" if (v and abs(v) >= 1e6) else (f"${v:,.0f}" if v else "—")


def fmt_pct(v, signed=False):
    if v is None:
        return "—"
    return (f"{v*100:+.1f}%" if signed else f"{v*100:.1f}%")


def main():
    ap = argparse.ArgumentParser(description="Re-screen dead CRE deals.")
    ap.add_argument("deals", help="deals CSV or JSON (rate/cap/rent fields refreshed to today)")
    ap.add_argument("--ltv", type=float, default=DEFAULTS["ltv"])
    ap.add_argument("--amort-years", type=float, default=DEFAULTS["amort_years"])
    ap.add_argument("--target-dscr", type=float, default=DEFAULTS["target_dscr"])
    ap.add_argument("--target-coc", type=float, default=DEFAULTS["target_coc"])
    ap.add_argument("--reengage-gap", type=float, default=DEFAULTS["reengage_gap"])
    ap.add_argument("--watch-gap", type=float, default=DEFAULTS["watch_gap"])
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    args = ap.parse_args()

    opts = {
        "ltv": args.ltv, "amort_years": args.amort_years,
        "target_dscr": args.target_dscr, "target_coc": args.target_coc,
        "reengage_gap": args.reengage_gap, "watch_gap": args.watch_gap,
    }

    rows = load(args.deals)
    results = [screen(r, opts) for r in rows]

    if args.json:
        json.dump(results, sys.stdout, indent=2)
        print()
        return

    print("> **PRELIMINARY — subject to change. Not investment advice.** "
          "Rents in $/SF/yr. Re-screened at today's financing rate and current comps.\n")
    print("| Deal | Why it died | What's changed | Call | One line |")
    print("|---|---|---|---|---|")
    for r in results:
        changed = []
        if r["rate_delta"] is not None:
            changed.append(f"rate {fmt_pct(-r['rate_delta'], signed=True)}")
        if r["rent_delta_psf"] is not None:
            changed.append(f"rent {r['rent_delta_psf']:+.2f}/SF")
        if r["cap_delta"] is not None:
            changed.append(f"cap {fmt_pct(r['cap_delta'], signed=True)}")
        changed_str = ", ".join(changed) if changed else "—"
        print(f"| {r['deal']} | {r['reason_died'] or '—'} | {changed_str} "
              f"| **{r['call']}** | {r['one_liner']} |")

    go = [r for r in results if r["call"] == "GO-BACK"]
    shortlist = sorted(results, key=lambda r: r["_score"], reverse=True)
    top3 = (go or shortlist)[:3] if not go else sorted(go, key=lambda r: r["_score"], reverse=True)[:3]
    print("\n### Top 3 worth a call this week")
    for i, r in enumerate(top3, 1):
        print(f"{i}. **{r['deal']}** — buyer value today {fmt_money(r['buyer_value_today'])} "
              f"vs ask {fmt_money(r['ask'])} (gap {fmt_pct(r['gap_to_ask'])}). {r['one_liner']}")


if __name__ == "__main__":
    main()
