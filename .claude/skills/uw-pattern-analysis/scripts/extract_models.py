#!/usr/bin/env python3
"""
extract_models.py — Build a normalized deal ledger from a folder of UW models.

Scans every .xlsx/.xlsm in a folder, locates assumption cells by matching the
text of adjacent label cells, and writes one row per workbook to deals.csv.

This is a *heuristic* starting point. UW templates differ per shop, so:
  1. Run it on ONE representative model first and eyeball the output.
  2. If a field is wrong/missing, add or fix synonyms in LABELS below, or
     correct the cell directly in deals.csv. The label map is meant to be edited.

Percentages are normalized to a number-in-percent (3.0 means 3%, not 0.03).
Missing fields are written as empty (treated as 'unknown' downstream), never 0.

Usage:
    python3 extract_models.py <folder> [-o deals.csv]

Requires: openpyxl  (pip install openpyxl)
"""
import argparse
import csv
import os
import re
import sys

try:
    from openpyxl import load_workbook
except ImportError:
    sys.exit("openpyxl is required: pip install openpyxl")

# canonical_field -> list of label regexes (matched case-insensitively against cell text)
LABELS = {
    "asset_type":        [r"property type", r"product type", r"asset type"],
    "subtype_feature":   [r"\bclass\b", r"vintage", r"construction type", r"value[- ]?add", r"core"],
    "market":            [r"submarket", r"\bmarket\b", r"\bMSA\b"],
    "purchase_price":    [r"purchase price", r"total consideration", r"acquisition price"],
    "price_per_unit":    [r"\$/?\s*unit", r"price per unit", r"per unit"],
    "price_psf":         [r"\$/?\s*(?:sf|psf)", r"price per (?:sf|foot)"],
    "going_in_cap":      [r"going[- ]?in cap", r"entry cap", r"yr?\s*1 cap", r"year 1 cap"],
    "entry_occupancy":   [r"in[- ]?place occ", r"physical occ", r"entry occ"],
    "rent_growth_y1":    [r"rent growth", r"market rent growth", r"trend(?:ed)? rate"],
    "bad_debt":          [r"bad debt", r"credit loss", r"economic vacancy"],
    "stabilized_occ":    [r"stabilized occ", r"vacancy"],
    "lease_up_pace":     [r"absorption", r"units?\s*/\s*month", r"months to stabiliz"],
    "expense_growth":    [r"expense growth", r"opex (?:growth|inflation)"],
    "tax_reassessment":  [r"reassessment", r"tax growth", r"millage"],
    "renovation_budget": [r"reno.*/?\s*unit", r"capex budget", r"hard costs?"],
    "contingency":       [r"contingency"],
    "hold_period":       [r"hold period", r"investment period", r"\bhold\b"],
    "exit_cap":          [r"exit cap", r"terminal cap", r"reversion cap"],
    "ltv":               [r"\bltv\b", r"\bltc\b", r"leverage"],
    "interest_rate":     [r"all[- ]?in rate", r"interest rate", r"\bcoupon\b"],
    "unlevered_irr":     [r"unlever(?:ed)? irr", r"property irr"],
    "levered_irr":       [r"lever(?:ed)? irr", r"equity irr", r"project irr"],
    "equity_multiple":   [r"equity multiple", r"\bMOIC\b", r"\bEM\b"],
    "downside_levered_irr": [r"downside.*irr", r"bear.*irr", r"stress.*irr"],
    "coc_y1":            [r"cash[- ]?on[- ]?cash", r"cash yield"],
}

# fields whose values are percentages (used to normalize 0.03 -> 3.0)
PERCENT_FIELDS = {
    "going_in_cap", "entry_occupancy", "rent_growth_y1", "bad_debt",
    "stabilized_occ", "expense_growth", "tax_reassessment", "contingency",
    "exit_cap", "ltv", "interest_rate", "unlevered_irr", "levered_irr",
    "downside_levered_irr", "coc_y1",
}

STATUS_HINTS = {
    "closed": [r"\bclosed\b", r"\bacquired\b", r"\bclosing\b", r"won"],
    "passed": [r"\bpassed\b", r"\bdeclined\b", r"\bno[- ]?bid\b"],
    "lost":   [r"\blost\b", r"lost bid", r"outbid", r"runner[- ]?up"],
}

NUM_RE = re.compile(r"-?\d[\d,]*\.?\d*")


def to_number(val, is_percent):
    """Coerce a cell value to a float; normalize percents to number-in-percent."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        n = float(val)
    else:
        m = NUM_RE.search(str(val))
        if not m:
            return None
        n = float(m.group(0).replace(",", ""))
        if "%" in str(val):           # "3.0%" already in percent units
            return round(n, 4)
    if is_percent and -0.0 <= n <= 1.0 and n != 0:
        # stored as fraction (0.03) -> 3.0 ; leave values >1 as already-percent
        n = n * 100
    return round(n, 4)


def scan_cells(ws, max_rows=400, max_cols=60):
    """Return {(row,col): value} for the populated top-left region of a sheet."""
    grid = {}
    for r, row in enumerate(ws.iter_rows(max_row=max_rows, max_col=max_cols, values_only=True), 1):
        for c, v in enumerate(row, 1):
            if v is not None and v != "":
                grid[(r, c)] = v
    return grid


def nearest_numeric(grid, r, c, is_percent):
    """Find the value just right of, then just below, a label cell."""
    for cc in range(c + 1, c + 6):          # scan right
        if (r, cc) in grid:
            n = to_number(grid[(r, cc)], is_percent)
            if n is not None:
                return n
    for rr in range(r + 1, r + 4):          # then scan down
        if (rr, c) in grid:
            n = to_number(grid[(rr, c)], is_percent)
            if n is not None:
                return n
    return None


def extract_workbook(path):
    row = {"deal_name": os.path.splitext(os.path.basename(path))[0], "file": path}
    try:
        wb = load_workbook(path, read_only=True, data_only=True)
    except Exception as e:
        row["_error"] = f"could not open: {e}"
        return row

    # merge the populated region of every sheet into one grid keyed by sheet
    grids = {ws.title: scan_cells(ws) for ws in wb.worksheets}
    wb.close()

    for field, patterns in LABELS.items():
        is_pct = field in PERCENT_FIELDS
        found = None
        for compiled in (re.compile(p, re.I) for p in patterns):
            for grid in grids.values():
                for (r, c), v in grid.items():
                    if isinstance(v, str) and compiled.search(v):
                        if field in ("asset_type", "subtype_feature", "market"):
                            # text fields: take the neighboring text cell
                            for cc in range(c + 1, c + 4):
                                nb = grid.get((r, cc))
                                if isinstance(nb, str) and nb.strip():
                                    found = nb.strip()
                                    break
                            if found is None and isinstance(v, str):
                                found = v.strip()
                        else:
                            found = nearest_numeric(grid, r, c, is_pct)
                        if found is not None:
                            break
                if found is not None:
                    break
            if found is not None:
                break
        row[field] = found if found is not None else ""
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", help="folder containing UW models")
    ap.add_argument("-o", "--out", default="deals.csv")
    args = ap.parse_args()

    models = []
    for dirpath, _, files in os.walk(args.folder):
        for f in files:
            if f.lower().endswith((".xlsx", ".xlsm")) and not f.startswith("~$"):
                models.append(os.path.join(dirpath, f))
    if not models:
        sys.exit(f"No .xlsx/.xlsm models found under {args.folder}")

    rows = []
    for path in sorted(models):
        print(f"  reading {os.path.basename(path)}", file=sys.stderr)
        rows.append(extract_workbook(path))

    # add empty *_actual columns for the outcome fields so Step 4 can fill them
    outcome_fields = [f for f in LABELS if f not in ("asset_type", "subtype_feature", "market")]
    headers = ["deal_name", "file", "status"] + list(LABELS.keys()) \
        + [f"{f}_actual" for f in outcome_fields] + ["pass_reason", "later_traded_value", "source", "_error"]

    with open(args.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=headers, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            r.setdefault("status", "")
            w.writerow(r)

    print(f"\nWrote {len(rows)} deals -> {args.out}", file=sys.stderr)
    print("Next: open it, sanity-check against the real models, fill status + *_actual "
          "outcomes (Step 4), then run analyze_patterns.py.", file=sys.stderr)


if __name__ == "__main__":
    main()
