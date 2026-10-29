"""Rebuilt hat_financial_result (read-only) vs the secondary source for the A4-flagged rows.
Run from backend/: PGOPTIONS="-c default_transaction_read_only=on" DB_NAME=hat_live python rebuild_secondary.py
"""

from collections import Counter
from decimal import Decimal
from pathlib import Path

from sqlalchemy import create_engine, text

from app.database import postgres_url_from_env
from app.hat.data.results.raw import RawCache
from app.hat.data.results.secondary import page_url, parse_page

SEC = RawCache(Path("/data/workspace/hat-data-isin/raw/secondary-results"))


def page(symbol, basis):
    e = SEC.entry(page_url(symbol, basis))
    return {q.period_end: q for q in parse_page(SEC.body(e)) if q.basis == basis} if e and e.status == 200 else {}


def near(a, b):
    return a is not None and b not in (None, 0) and abs(a - b) / abs(b) <= Decimal("0.02")


with create_engine(postgres_url_from_env()).connect() as db:
    rows = db.execute(text(
        "select distinct on (symbol, period_end, basis) symbol, period_end, basis, revenue, net_profit, quality_flags"
        " from hat_financial_result where quality_flags is not null order by symbol, period_end, basis, version desc")).all()
pages, out, miss = {}, Counter(), []
for r in rows:
    s = pages.setdefault((r.symbol, r.basis), page(r.symbol, r.basis)).get(r.period_end)
    for flag, field in (("quarter_start_mislabelled", "revenue"), ("owners_profit_tag_swapped", "net_profit")):
        if flag not in r.quality_flags:
            continue
        out[(flag, "rows")] += 1
        if s and getattr(s, field) is not None:
            out[(flag, "on a secondary page")] += 1
            ok = near(getattr(r, field), getattr(s, field))
            out[(flag, f"{field} within 2%")] += ok
            if not ok:
                miss.append((flag, r.symbol, str(r.period_end), field, getattr(r, field), getattr(s, field)))
for k, v in sorted(out.items()):
    print(k, v)
for m in miss:
    print("  differs:", m)
