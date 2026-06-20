#!/usr/bin/env python3
"""
analyze_patterns.py — Run the four diagnostic lenses over a deal ledger.

Reads deals.csv (from extract_models.py, with Step-4 outcomes filled in) and
prints ranked CANDIDATE patterns with the stats the pattern bar needs:
frequency, sign consistency, mean miss, and a rough impact proxy.

It does NOT decide the final patterns or write prose — that's the analyst's
judgment (see references/pattern-bar.md). It surfaces the candidates and the
numbers so the judgment is grounded, not vibes.

CSV convention:
  - underwritten value in column  <field>
  - realized/market outcome in column  <field>_actual
  - status in 'status' (closed/passed/lost)
  - passed-deal outcome in 'later_traded_value' (and the UW value to compare
    against is 'purchase_price' or a value field)

Usage:
    python3 analyze_patterns.py deals.csv
"""
import argparse
import csv
import statistics
import sys

PCT = "%"

# fields where "underwritten minus actual" being consistently one sign is a bias
RECYCLED = [
    ("rent_growth_y1", "lower",  "rent growth straight-lined above realized"),
    ("exit_cap",       "higher", "exit cap underwritten tighter (lower) than realized"),
    ("lease_up_pace",  "lower",  "lease-up modeled faster than realized"),
    ("bad_debt",       "higher", "bad debt / economic vacancy under-modeled"),
    ("expense_growth", "higher", "expense growth under-modeled"),
    ("tax_reassessment","higher","tax reassessment under-modeled"),
    ("contingency",    "higher", "contingency below actual overruns"),
    ("renovation_budget","higher","renovation budget below actual spend"),
]


def f(v):
    """Parse a cell to float or None."""
    if v is None or str(v).strip() == "":
        return None
    try:
        return float(str(v).replace(",", "").replace("%", "").replace("$", ""))
    except ValueError:
        return None


def load(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def sign_consistency(diffs):
    """Fraction of values sharing the majority sign (1.0 = perfectly consistent)."""
    pos = sum(1 for d in diffs if d > 0)
    neg = sum(1 for d in diffs if d < 0)
    if not diffs:
        return 0.0
    return max(pos, neg) / len(diffs)


def lens4_recycled(rows):
    print("\n=== Lens 4: recycled assumptions that keep missing ===")
    print("(underwritten - actual; bias only counts if same-signed across >=3 deals)\n")
    candidates = []
    for field, _bad_dir, desc in RECYCLED:
        pairs = []
        for r in rows:
            uw, ac = f(r.get(field)), f(r.get(f"{field}_actual"))
            if uw is not None and ac is not None:
                pairs.append((r.get("deal_name", "?"), uw - ac))
        if len(pairs) < 3:
            print(f"  {field:18s} n={len(pairs)} — too few outcomes to judge")
            continue
        diffs = [d for _, d in pairs]
        cons = sign_consistency(diffs)
        mean = statistics.mean(diffs)
        flag = "PATTERN" if cons >= 0.8 and abs(mean) > 1e-9 else "noise"
        print(f"  {field:18s} n={len(pairs)}  mean_miss={mean:+.2f}  sign_consistency={cons:.0%}  -> {flag}")
        if flag == "PATTERN":
            deals = ", ".join(f"{d}({v:+.1f})" for d, v in pairs)
            candidates.append((abs(mean) * len(pairs), field,
                               f"{desc}: mean {mean:+.2f} across {len(pairs)} deals [{deals}]"))
    return candidates


def lens1_downside(rows):
    print("\n=== Lens 1: downside cases that ran too generous ===")
    spreads, breaches = [], []
    for r in rows:
        base, down = f(r.get("levered_irr")), f(r.get("downside_levered_irr"))
        if base is not None and down is not None:
            spreads.append((r.get("deal_name", "?"), base - down))
        real, down2 = f(r.get("levered_irr_actual")), f(r.get("downside_levered_irr"))
        if real is not None and down2 is not None and real < down2:
            breaches.append((r.get("deal_name", "?"), down2, real))
    cands = []
    if spreads:
        vals = [s for _, s in spreads]
        cv = (statistics.pstdev(vals) / statistics.mean(vals)) if statistics.mean(vals) else 0
        print(f"  downside spread: n={len(spreads)} mean={statistics.mean(vals):.1f}pp "
              f"coeff_var={cv:.2f}  ({'mechanical/constant haircut' if cv < 0.25 else 'varies by deal'})")
        if cv < 0.25 and len(spreads) >= 3:
            cands.append((statistics.mean(vals) * len(spreads), "downside_spread",
                          f"downside is a near-constant ~{statistics.mean(vals):.0f}pp haircut "
                          f"across {len(spreads)} deals — decorative, not analytic"))
    else:
        print("  no base/downside IRR pairs found")
    if breaches:
        deals = ", ".join(f"{d}(down {dn:.1f} vs real {rl:.1f})" for d, dn, rl in breaches)
        print(f"  *** realized breached the modeled downside in {len(breaches)} deals: {deals}")
        if len(breaches) >= 3:
            cands.append((len(breaches) * 5, "downside_breach",
                          f"realized return fell below the 'worst case' in {len(breaches)} deals [{deals}]"))
    return cands


def lens2_overpay(rows):
    print("\n=== Lens 2: building type / feature consistently overpaid for ===")
    print("(group avg going-in cap & realized IRR miss by type/feature)\n")
    groups = {}
    for r in rows:
        key = (r.get("asset_type") or "?", r.get("subtype_feature") or "?")
        cap = f(r.get("going_in_cap"))
        miss = None
        uw, ac = f(r.get("levered_irr")), f(r.get("levered_irr_actual"))
        if uw is not None and ac is not None:
            miss = uw - ac
        groups.setdefault(key, []).append((r.get("deal_name", "?"), cap, miss))
    cands = []
    for (atype, feat), items in sorted(groups.items()):
        caps = [c for _, c, _ in items if c is not None]
        misses = [m for _, _, m in items if m is not None]
        if not items:
            continue
        avg_cap = f"{statistics.mean(caps):.2f}" if caps else "n/a"
        avg_miss = statistics.mean(misses) if misses else None
        tag = ""
        if len(items) >= 3 and avg_miss is not None and avg_miss > 0:
            tag = "  -> PATTERN (pays in, underdelivers)"
            cands.append((avg_miss * len(items), f"{atype}/{feat}",
                          f"{atype}/{feat}: {len(items)} deals, avg going-in cap {avg_cap}, "
                          f"avg IRR shortfall {avg_miss:+.1f}pp"))
        print(f"  {atype:14s} {feat:14s} n={len(items):2d} avg_cap={avg_cap:>6s} "
              f"avg_IRR_miss={avg_miss:+.1f}{tag}" if avg_miss is not None
              else f"  {atype:14s} {feat:14s} n={len(items):2d} avg_cap={avg_cap:>6s} (no realized IRR)")
    return cands


def lens3_passed(rows):
    print("\n=== Lens 3: deals passed that later traded up ===")
    print("(requires later_traded_value from web/comps; survivorship & hindsight in pattern-bar.md)\n")
    passed = [r for r in rows if (r.get("status") or "").lower() in ("passed", "lost")]
    if not passed:
        print("  no passed/lost deals tagged")
        return []
    up, down, unknown = [], [], 0
    for r in rows:
        if (r.get("status") or "").lower() not in ("passed", "lost"):
            continue
        uw = f(r.get("purchase_price"))
        later = f(r.get("later_traded_value"))
        name = r.get("deal_name", "?")
        if uw is None or later is None:
            unknown += 1
            continue
        delta = (later - uw) / uw * 100 if uw else 0
        (up if delta > 0 else down).append((name, delta, r.get("pass_reason", "")))
    n_known = len(up) + len(down)
    print(f"  passed/lost: {len(passed)}  with outcome: {n_known}  unknown: {unknown}")
    if n_known:
        hit = len(down) / n_known  # 'down' = passes that did NOT trade up = correct passes
        print(f"  correct-pass rate: {hit:.0%}  (if high, conservatism is working — not a defect)")
    for d, delta, why in sorted(up, key=lambda x: -x[1]):
        print(f"    UP   {d:18s} {delta:+.0f}% vs your number   reason passed: {why}")
    for d, delta, why in sorted(down, key=lambda x: x[1]):
        print(f"    DOWN {d:18s} {delta:+.0f}% vs your number   reason passed: {why}")
    cands = []
    if len(up) >= 3:
        reasons = [w for _, _, w in up if w]
        cands.append((sum(d for _, d, _ in up), "passed_traded_up",
                      f"{len(up)} passed deals later traded above your number; "
                      f"check for a common reason: {reasons}"))
    return cands


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", help="deals.csv with Step-4 outcomes filled in")
    args = ap.parse_args()
    rows = load(args.csv)
    print(f"Loaded {len(rows)} deals from {args.csv}")
    by_status = {}
    for r in rows:
        by_status[(r.get("status") or "untagged").lower()] = by_status.get((r.get("status") or "untagged").lower(), 0) + 1
    print("Status mix:", ", ".join(f"{k}={v}" for k, v in by_status.items()))
    if len(rows) < 8:
        print("\n!! Fewer than 8 deals — downgrade all pattern claims; state the small n. (pattern-bar.md)")

    cands = []
    cands += lens1_downside(rows)
    cands += lens2_overpay(rows)
    cands += lens3_passed(rows)
    cands += lens4_recycled(rows)

    print("\n\n=== RANKED CANDIDATE PATTERNS (impact proxy x frequency) ===")
    if not cands:
        print("  None cleared the rough bar. Do NOT manufacture three — report what's real.")
    for score, key, desc in sorted(cands, key=lambda x: -x[0]):
        print(f"  [{score:7.1f}] {key}: {desc}")
    print("\nThese are CANDIDATES. Apply the full pattern bar (market-vs-skill, hindsight, "
          "survivorship, dollars) before writing the final 3. See references/pattern-bar.md.")


if __name__ == "__main__":
    main()
