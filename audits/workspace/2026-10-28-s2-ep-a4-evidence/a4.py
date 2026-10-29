"""A4 validation numbers for the S2 EP results store. Prints markdown sections.

Run from backend/: DB_NAME=... HAT_DATA_ROOT=... python -I? no: python a4.py <filings.csv> <out.md>
Reads hat_financial_result / hat_financial_growth (read-only), the parse outcomes CSV and the
secondary-source page cache.
"""

from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

from sqlalchemy import create_engine, text

from app.database import postgres_url_from_env
from app.hat.data.results.raw import RawCache
from app.hat.data.results.secondary import page_url, parse_page

ROOT = Path("/data/workspace/hat-data-isin")
CR = Decimal(10) ** 7
out: list[str] = []


def p(line: str = "") -> None:
    out.append(line)


def table(head: list[str], rows: list[list[object]]) -> None:
    p("| " + " | ".join(head) + " |")
    p("| " + " | ".join("---" for _ in head) + " |")
    for r in rows:
        p("| " + " | ".join(str(x) for x in r) + " |")
    p()


def coverage(csv_path: Path, db) -> None:
    rows = list(csv.DictReader(csv_path.open()))
    p(f"Parse outcomes: `{csv_path}`, {len(rows):,} rows (one per filing and basis candidate).")
    p()
    by = defaultdict(Counter)
    reasons = Counter()
    reasons_year = defaultdict(Counter)
    for r in rows:
        if r["listing"] == "secondary":
            continue
        end = r["period_end"] or r["listing_period_end"]
        year = end[:4]
        fmt = r["format"] or "(unread)"
        res = r["result"]
        by[(year, fmt)]["found"] += 1
        by[(year, fmt)][res] += 1
        if res == "excluded":
            reasons[r["reason"]] += 1
            reasons_year[year][r["reason"]] += 1
    sec = db.execute(
        text(
            "select extract(year from period_end)::int, count(*) from hat_financial_result "
            "where source='secondary' group by 1"
        )
    ).all()
    sec_year = {str(y): n for y, n in sec}
    head = ["year", "format", "found", "stored", "already/same", "insurance", "excluded"]
    body = []
    for (year, fmt), c in sorted(by.items()):
        body.append(
            [
                year,
                fmt,
                c["found"],
                c["stored"],
                c["already_stored"] + c["same_figures"],
                c["insurance_skipped"],
                c["excluded"],
            ]
        )
    table(head, body)
    p("Excluded, by reason:")
    p()
    table(["reason", "count"], [[k or "(none)", v] for k, v in reasons.most_common()])
    p("Secondary-source rows backfilled, by period-end year (DB):")
    p()
    table(["year", "rows"], [[y, n] for y, n in sorted(sec_year.items())])


def counts(db) -> None:
    q = {
        "rows": "select count(*) from hat_financial_result",
        "nse rows": "select count(*) from hat_financial_result where source='nse'",
        "secondary rows": "select count(*) from hat_financial_result where source='secondary'",
        "insurance_skipped rows": "select count(*) from hat_financial_result where format='insurance_skipped'",
        "instruments": "select count(distinct instrument_id) from hat_financial_result",
        "q4_derived": "select count(*) from hat_financial_result where q4_derived",
        "period_mismatch": "select count(*) from hat_financial_result where period_mismatch",
        "revisions (version > 1)": "select count(*) from hat_financial_result where version > 1",
        "public_at_estimated": "select count(*) from hat_financial_result where public_at_estimated",
        "unit_suspect (growth)": "select count(*) from hat_financial_growth where unit_suspect",
        "growth rows": "select count(*) from hat_financial_growth",
        "growth with sales_yoy": "select count(*) from hat_financial_growth where sales_yoy is not null",
        "growth with eps_yoy": "select count(*) from hat_financial_growth where eps_yoy is not null",
    }
    table(["count", "rows", "query"], [[k, f"{db.execute(text(v)).scalar():,}", f"`{v}`"] for k, v in q.items()])
    src = db.execute(
        text(
            "select source, public_at_source, public_at_estimated, count(*) from hat_financial_result "
            "group by 1,2,3 order by 1,2,3"
        )
    ).all()
    table(["source", "public_at_source", "estimated", "rows"], [list(r) for r in src])


def latest_nse(db) -> dict:
    rows = db.execute(
        text(
            "select distinct on (instrument_id, period_end, basis) instrument_id, symbol, period_end,"
            " basis, revenue, net_profit, eps_basic, id from hat_financial_result where source='nse'"
            " and format <> 'insurance_skipped' order by instrument_id, period_end, basis, version desc"
        )
    ).all()
    return {(str(r[0]), r[2], r[3]): r for r in rows}


def rel(a: Decimal | None, b: Decimal | None) -> Decimal | None:
    if a is None or b is None:
        return None
    if b == 0:
        return None if a == 0 else Decimal(1)
    return abs(a - b) / abs(b)


def crosscheck(db, symbols: dict[str, str]) -> None:
    """Every NSE quarter the secondary page also shows: revenue, net profit, EPS."""
    cache = RawCache(ROOT / "raw" / "secondary-results")
    nse = latest_nse(db)
    pairs = []
    for iid, symbol in symbols.items():
        for basis in ("consolidated", "standalone"):
            entry = cache.entry(page_url(symbol, basis))
            if entry is None or entry.status != 200:
                continue
            for q in parse_page(cache.body(entry)):
                row = nse.get((iid, q.period_end, q.basis))
                if row is not None:
                    pairs.append((symbol, q, row))
    p(f"Pairs (NSE quarter also on the secondary page, same basis): {len(pairs):,}.")
    p()
    # the secondary source shows crores to 2 decimals for revenue/profit: tolerance 1% or 0.5 cr
    stats = {}
    worst = []
    fields = (("revenue", "revenue", 4), ("net_profit", "net_profit", 5), ("eps", "eps_basic", 6))
    for field, qa, ra in fields:
        for basis in ("consolidated", "standalone", "all"):
            n = mism = 0
            for symbol, q, row in pairs:
                if basis != "all" and q.basis != basis:
                    continue
                a, b = getattr(q, qa), row[ra]
                if a is None or b is None:
                    continue
                n += 1
                d = rel(a, b)
                tol_abs = CR / 2 if field != "eps" else Decimal("0.01")
                bad = d is not None and d > Decimal("0.01") and abs(a - b) > tol_abs
                if bad:
                    mism += 1
                    if basis != "all":
                        worst.append((d, field, symbol, q.period_end, q.basis, b, a))
            stats[(field, basis)] = (n, mism)
    table(
        ["field", "basis", "compared", "mismatched (>1% and > Rs 0.5 cr / Rs 0.01)", "rate"],
        [[f, bs, n, m, f"{(m / n * 100 if n else 0):.2f}%"] for (f, bs), (n, m) in stats.items()],
    )
    for field in ("revenue", "net_profit", "eps"):
        w = sorted((x for x in worst if x[1] == field), key=lambda x: x[0], reverse=True)[:20]
        p(f"Worst 20, {field}:")
        p()
        scale = (lambda v: f"{v / CR:,.2f} cr") if field != "eps" else (lambda v: f"{v:,.2f}")
        table(
            ["symbol", "period_end", "basis", "NSE", "secondary", "rel diff"],
            [[s, e, bs, scale(nv), scale(sv), f"{d * 100:.1f}%"] for d, _f, s, e, bs, nv, sv in w],
        )


def main() -> None:
    csv_path, target = Path(sys.argv[1]), Path(sys.argv[2])
    engine = create_engine(postgres_url_from_env())
    with engine.connect() as db:
        symbols = {
            str(i): s
            for i, s in db.execute(
                text("select distinct on (instrument_id) instrument_id, symbol from hat_financial_result order by instrument_id, period_end desc")
            )
        }
        p("## Coverage by year and format")
        p()
        coverage(csv_path, db)
        p("## Counts")
        p()
        counts(db)
        p("## Secondary-source cross-check")
        p()
        crosscheck(db, symbols)
    target.write_text("\n".join(out) + "\n")
    print(f"wrote {target}, {len(out)} lines")


if __name__ == "__main__":
    main()
