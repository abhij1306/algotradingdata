"""A4 diagnostics on hat_live (read-only) and the raw caches: the defects behind the cross-check
mismatches. Run from backend/:
PGOPTIONS="-c default_transaction_read_only=on" DB_NAME=hat_live python a4_diag.py <filings.csv>
"""

from __future__ import annotations

import csv
import random
import sys
from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path

from sqlalchemy import create_engine, text

from app.database import postgres_url_from_env
from app.hat.data.results import xbrl
from app.hat.data.results.raw import RawCache
from app.hat.data.results.secondary import page_url, parse_page

ROOT = Path("/data/workspace/hat-data-isin/raw")
NSE = RawCache(ROOT / "nse-results")
SEC = RawCache(ROOT / "secondary-results")
CR = Decimal(10) ** 7
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


def bad(a, b, tol):
    return a is not None and b is not None and b != 0 and abs(a - b) / abs(b) > Decimal("0.01") and abs(a - b) > tol


def num(fact):
    try:
        return Decimal(fact.text) if fact else None
    except Exception:  # noqa: BLE001
        return None


def contexts(url):
    facts, periods = xbrl.read_facts(NSE.body(NSE.entry(url)))
    one, four = facts.get(xbrl.QUARTER_CONTEXT, {}), facts.get(xbrl.YTD_CONTEXT, {})
    s, e = xbrl._period(one, periods.get(xbrl.QUARTER_CONTEXT))
    ys, ye = xbrl._period(four, periods.get(xbrl.YTD_CONTEXT))
    return facts, one, four, xbrl._span_days(s, e), xbrl._span_days(ys, ye)


def main() -> None:
    filings = Path(sys.argv[1])
    with create_engine(postgres_url_from_env()).connect() as db:
        latest = db.execute(text(
            "select distinct on (instrument_id, period_end, basis) symbol, period_end, basis, format,"
            " revenue, net_profit, eps_basic, q4_derived, source_url from hat_financial_result"
            " where source='nse' and format<>'insurance_skipped'"
            " order by instrument_id, period_end, basis, version desc")).all()
        derived = db.execute(text(
            "select symbol, period_end, basis, format, source_url, revenue from hat_financial_result"
            " where q4_derived")).all()
        mismatch = db.execute(text(
            "select symbol, period_end, basis, listing_period_end, version, revenue, public_at"
            " from hat_financial_result where period_mismatch")).all()
        impact = db.execute(text(
            "select count(*) filter (where c.q4_derived or p.q4_derived),"
            " count(*) filter (where (c.q4_derived or p.q4_derived) and g.sales_yoy is not null),"
            " count(*) filter (where c.period_mismatch or p.period_mismatch)"
            " from hat_financial_growth g left join hat_financial_result c on c.id=g.current_id"
            " left join hat_financial_result p on p.id=g.prior_id")).one()

    print("## D1 q4_derived rows:", len(derived), "negative revenue:", sum(r.revenue < 0 for r in derived))
    spans, near, have = Counter(), 0, 0
    for r in derived:
        facts, one, four, qs, ys = contexts(r.source_url)
        spans[(qs, ys)] += 1
        s = sec(r.symbol, r.basis, r.period_end)
        q = xbrl.figures(one, r.format, r.basis).revenue
        if s and s.revenue and q:
            have += 1
            near += abs(q - s.revenue) / s.revenue < Decimal("0.05")
    print("  OneD/FourD span days:", dict(spans))
    print("  on a secondary page:", have, "OneD revenue within 5% of the secondary quarter:", near)

    print("## D2 period_mismatch rows:")
    for r in mismatch:
        print("  ", tuple(r))

    print("## D3 consolidated net profit (owners' tag)")
    k, swaps = Counter(), []
    for r in latest:
        if r.basis != "consolidated" or r.q4_derived:
            continue
        _f, one, _four, _qs, _ys = contexts(r.source_url)
        owners = num(one.get("ProfitOrLossAttributableToOwnersOfParent"))
        period = num(one.get("ProfitLossForPeriod"))
        tci = num(one.get("ComprehensiveIncomeForThePeriod"))
        nci = num(one.get("ProfitOrLossAttributableToNonControllingInterests"))
        k["rows"] += 1
        if owners is None:
            k["owners tag absent"] += 1
        elif tci is not None and period is not None and owners == tci and owners != period and not nci:
            k["owners tag = total comprehensive income, NCI 0"] += 1
            swaps.append((r.symbol, str(r.period_end)))
    print("  ", dict(k), "examples:", swaps[:6])

    print("## D4 cross-check breakdown")
    rev, eps, npm, ratio = Counter(), Counter(), [], Counter()
    for r in latest:
        s = sec(r.symbol, r.basis, r.period_end)
        if not s:
            continue
        if bad(s.revenue, r.revenue, CR / 2):
            if r.q4_derived:
                rev["q4_derived"] += 1
            else:
                d = (s.revenue - r.revenue) / abs(r.revenue)
                rev["secondary 1-15% lower" if Decimal("-0.15") <= d < 0 else
                    "secondary 1-15% higher" if 0 < d <= Decimal("0.15") else "other >15%"] += 1
                q = s.revenue / r.revenue
                for lab, lo, hi in (("~100x", 90, 110), ("~10x", 9, 11), ("~1/100", Decimal("0.009"), Decimal("0.011"))):
                    if Decimal(lo) <= q <= Decimal(hi):
                        ratio[lab] += 1
        np_bad = bad(s.net_profit, r.net_profit, CR / 2)
        if r.basis == "consolidated" and np_bad:
            npm.append(r)
        if bad(s.eps_basic, r.eps_basic, Decimal("0.01")):
            if r.q4_derived:
                eps[(r.basis, "q4_derived")] += 1
            elif np_bad:
                eps[(r.basis, "net profit also differs")] += 1
            else:
                q = float(r.eps_basic / s.eps_basic) if s.eps_basic else 0
                split = any(abs(q - m) / m < 0.03 for m in (2, 3, 4, 5, 10, 1.5, 1.25))
                eps[(r.basis, "net profit agrees, integer ratio (split/bonus)" if split else
                     "net profit agrees, within 15%" if 0.85 < q < 1.15 else "net profit agrees, other")] += 1
    print("  revenue:", dict(rev), "scale ratios:", dict(ratio))
    print("  eps:", dict(eps))
    random.seed(1)
    sample = random.sample(npm, min(300, len(npm)))
    n = ok = 0
    for r in sample:
        _f, one, _four, _qs, _ys = contexts(r.source_url)
        total = num(one.get("ProfitLossForPeriod") or one.get("ProfitLoss"))
        if total is None:
            continue
        n += 1
        ok += not bad(sec(r.symbol, r.basis, r.period_end).net_profit, total, CR / 2)
    print("  consolidated net-profit mismatches:", len(npm), "sampled (seed 1):", n,
          "secondary agrees with total profit incl. NCI:", ok)

    print("## D5 q4_nine_month_missing exclusions")
    k, cmp = Counter(), Counter()
    for r in csv.DictReader(filings.open()):
        if r["reason"] != "q4_nine_month_missing":
            continue
        facts, one, _four, qs, ys = contexts(r["url"])
        k[(qs, ys, (r["period_end"] or r["listing_period_end"])[:7])] += 1
        basis = xbrl.basis_of_document(facts) or r["basis"]
        q = xbrl.figures(one, "integrated_indas", basis).revenue
        s = sec(r["symbol"], basis, date.fromisoformat(r["period_end"] or r["listing_period_end"]))
        if not s or not s.revenue or not q:
            cmp["no secondary quarter"] += 1
            continue
        x = float(q / s.revenue)
        cmp["~quarter" if 0.95 < x < 1.05 else "~half year" if 1.7 < x < 2.3 else "other"] += 1
    print("  (OneD days, FourD days, period):", dict(k))
    print("  OneD revenue vs secondary quarter:", dict(cmp))

    print("## D6 secondary pages")
    n, first, st = Counter(), Counter(), Counter()
    for _u, e in SEC.entries().items():
        st[e.status] += 1
        if e.status != 200:
            continue
        q = parse_page(SEC.body(e))
        n[len(q)] += 1
        if q:
            first[min(x.period_end for x in q).isoformat()] += 1
    print("  statuses:", dict(st), "quarters per page:", sorted(n.items()))
    print("  earliest quarter shown, most common:", first.most_common(4))

    print("## D7 growth rows touching q4_derived (with sales_yoy) / period_mismatch:", tuple(impact))


if __name__ == "__main__":
    main()
