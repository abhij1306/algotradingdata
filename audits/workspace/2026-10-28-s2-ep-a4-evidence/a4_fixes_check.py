"""PR check for the A4 fixes (D1-D3): parse every cached NSE XBRL in filings.csv with main's parser
and this branch's, offline (raw cache read-only, no database writes), and compare.
Run from backend/: python a4_fixes_check.py <filings.csv> <xbrl_main.py>
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path

from app.hat.data.results import xbrl as new
from app.hat.data.results.ingest import year_before_listing
from app.hat.data.results.raw import RawCache
from app.hat.data.results.secondary import page_url, parse_page

ROOT = Path("/data/workspace/hat-data-isin/raw")
NSE = RawCache(ROOT / "nse-results")
SEC = RawCache(ROOT / "secondary-results")
_pages: dict = {}


def sec(symbol, basis, period_end):
    key = (symbol, basis)
    if key not in _pages:
        e = SEC.entry(page_url(symbol, basis))
        _pages[key] = (
            {q.period_end: q for q in parse_page(SEC.body(e)) if q.basis == basis}
            if e and e.status == 200
            else {}
        )
    return _pages[key].get(period_end)


def run(mod, body):
    try:
        return mod.parse(body), ""
    except mod.XbrlError as e:
        return None, str(e) or "xbrl_error"


def near(a, b, pct="0.02"):
    return a is not None and b not in (None, 0) and abs(a - b) / abs(b) <= Decimal(pct)


def main() -> None:
    spec = importlib.util.spec_from_file_location("xbrl_main", sys.argv[2])
    old = importlib.util.module_from_spec(spec)
    sys.modules["xbrl_main"] = old
    spec.loader.exec_module(old)
    rows = [r for r in csv.DictReader(open(sys.argv[1])) if r["url"].endswith(".xml")]
    seen, change, flags, d1, d3, d2, d5 = set(), Counter(), Counter(), Counter(), Counter(), [], Counter()
    for r in rows:
        if r["url"] in seen:
            continue
        seen.add(r["url"])
        e = NSE.entry(r["url"])
        if not e or e.status != 200:
            continue
        body = NSE.body(e)
        (po, eo), (pn, en) = run(old, body), run(new, body)
        listing_end = date.fromisoformat(r["listing_period_end"])
        if pn and year_before_listing(pn.period_end, listing_end):
            d2.append((r["symbol"], r["listing_period_end"], str(pn.period_end), r["result"], r["url"].rsplit("/", 1)[1]))
        for f in pn.flags if pn else ():
            flags[f] += 1
        basis = (pn.basis if pn else "") or r["basis"]
        if eo != en:
            change[f"error {eo or 'ok'} -> {en or 'ok'}"] += 1
        elif po and pn:
            fig = lambda f: f and (f.revenue, f.total_income, f.net_profit, f.eps_basic, f.eps_diluted)  # noqa: E731
            q = lambda p: (p.period_start, p.period_end, fig(p.quarter), fig(p.annual))  # noqa: E731
            if q(po) != q(pn):
                kind = "quarter_start_mislabelled" if new.FLAG_QUARTER_START_MISLABELLED in pn.flags else (
                    "owners_profit_tag_swapped" if new.FLAG_OWNERS_TAG_SWAPPED in pn.flags else "other")
                change[f"figures changed ({kind})"] += 1
            else:
                change["unchanged"] += 1
        else:
            change[f"unchanged error {en}"] += 1
        end = pn.period_end if pn else None
        s = sec(r["symbol"], basis, end) if end else None
        if r["q4_derived"] == "True":
            d1["rows"] += 1
            if not pn:
                d1[f"now excluded {en}"] += 1
            elif pn.quarter and new.FLAG_QUARTER_START_MISLABELLED in pn.flags:
                d1["now read as the quarter (flagged)"] += 1
                if s and s.revenue:
                    d1["  on a secondary page"] += 1
                    d1["  revenue within 2% of the secondary quarter"] += near(pn.quarter.revenue, s.revenue)
            else:
                d1["other"] += 1
        if r["reason"] == "q4_nine_month_missing":
            d5[en or ("ok, flagged" if pn and pn.flags else "ok")] += 1
        if pn and pn.quarter and new.FLAG_OWNERS_TAG_SWAPPED in pn.flags and po and po.quarter:
            d3["flagged"] += 1
            if s and s.net_profit is not None:
                d3["  on a secondary page"] += 1
                d3["  old net profit within 2% of the secondary"] += near(po.quarter.net_profit, s.net_profit)
                d3["  new net profit within 2% of the secondary"] += near(pn.quarter.net_profit, s.net_profit)
    print("documents parsed:", len(seen))
    print("## main -> branch:", dict(change.most_common()))
    print("## flags:", dict(flags))
    print("## D1 (q4_derived rows on main):", dict(d1))
    print("## D5 (q4_nine_month_missing on main) now:", dict(d5))
    print("## D3 owners' tag swapped:", dict(d3))
    print("## D2 documents a year before their listing:", len(d2))
    for x in d2:
        print("  ", x)


if __name__ == "__main__":
    main()
