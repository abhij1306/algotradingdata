"""A4 spot check: 20 random company-quarters (fixed seed) against the results PDFs.

Run from backend/ with PYTHONPATH=. DB_NAME=... python spot.py <seed> <out.json>
For each sampled (instrument, period_end, basis) NSE row (latest version): the results
announcement's PDF (the announcement that dated the row, else the quarter's results announcement
naming it), downloaded once into the scratchpad's pdfcache/ (paced 2 s), its text extracted with pypdf,
and each stored figure searched for in rupees, thousands, lakhs, millions and crores.
"""

from __future__ import annotations

import io
import json
import random
import re
import sys
import time
from collections import defaultdict
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from pypdf import PdfReader
from sqlalchemy import create_engine, text

from app.database import postgres_url_from_env
from app.hat.data.bhavcopy import BROWSER_HEADERS
from app.hat.data.results.nse import is_results_announcement, nse_time
from app.hat.data.results.raw import RawCache
from app.hat.data.results.timing import named_quarter_ends

ROOT = Path("/data/workspace/hat-data-isin")
UNITS = {
    "rupees": Decimal(1),
    "thousands": Decimal(10**3),
    "lakhs": Decimal(10**5),
    "millions": Decimal(10**6),
    "crores": Decimal(10**7),
}


def announcements() -> dict[str, list[dict]]:
    cache = RawCache(ROOT / "raw" / "nse-results")
    by: dict[str, list[dict]] = defaultdict(list)
    for url, entry in cache.entries().items():
        if "corporate-announcements" not in url or entry.status != 200:
            continue
        for item in json.loads(cache.body(entry)):
            from app.hat.data.results.nse import Announcement

            a = Announcement(
                item.get("symbol") or "",
                nse_time(item.get("an_dt")),
                item.get("desc") or "",
                item.get("attchmntText") or "",
            )
            if a.at is None or not is_results_announcement(a):
                continue
            by[a.symbol].append({"at": a.at, "text": a.text, "pdf": item.get("attchmntFile")})
    for listed in by.values():
        listed.sort(key=lambda x: x["at"])
    return by


def pick_pdf(items: list[dict], row) -> dict | None:
    if row.public_at_source == "announcement":
        for it in items:
            if it["at"] == row.public_at:
                return it
    lo, hi = row.period_end, row.public_at + timedelta(days=3)
    for it in items:
        if row.period_end in named_quarter_ends(it["text"]) and lo < it["at"].date() <= hi.date():
            return it
    return None


def fetch_pdf(url: str) -> bytes | None:
    import requests

    old = RawCache(ROOT / "raw" / "nse-results-pdf")  # earlier dry run: read only
    entry = old.entry(url)
    if entry is not None and entry.status == 200:
        return old.body(entry)
    cache = RawCache(Path(__file__).resolve().parent / "pdfcache")  # never the shared raw cache
    entry = cache.entry(url)
    if entry is not None and entry.status == 200:
        return cache.body(entry)
    time.sleep(2)
    try:
        r = requests.get(url, headers=BROWSER_HEADERS, timeout=60)
    except requests.RequestException:
        return None
    if r.status_code != 200:
        return None
    cache.put(url, r.status_code, r.content)
    return r.content


def pdf_text(body: bytes) -> str:
    if body[:2] == b"PK":  # a zip of PDFs
        import zipfile

        with zipfile.ZipFile(io.BytesIO(body)) as z:
            parts = [pdf_text(z.read(n)) for n in z.namelist() if n.lower().endswith(".pdf")]
        return "\n".join(parts) or "<zip without pdf>"
    try:
        reader = PdfReader(io.BytesIO(body))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:  # noqa: BLE001 - a broken PDF is reported, not fatal
        return f"<unreadable: {type(exc).__name__}>"


def numbers(text_: str) -> set[Decimal]:
    out = set()
    for m in re.finditer(r"\(?-?[\d,]+\.?\d*\)?", text_):
        raw = m.group(0)
        neg = raw.startswith("(") or raw.startswith("-")
        digits = raw.strip("()-").replace(",", "")
        if not digits or digits == ".":
            continue
        try:
            v = Decimal(digits)
        except Exception:  # noqa: BLE001
            continue
        out.add(-v if neg else v)
    return out


def found_in(value: Decimal | None, nums: set[Decimal], eps: bool) -> str | None:
    """The unit in which `value` appears among `nums` (rounded as printed), else None."""
    if value is None:
        return None
    units = {"rupees/share": Decimal(1)} if eps else UNITS
    for unit, scale in units.items():
        scaled = value / scale
        for places in (2,) if eps else (2, 1, 0):
            q = scaled.quantize(Decimal(1).scaleb(-places), ROUND_HALF_UP)
            if q != 0 and (q in nums or -q in nums or abs(q) in nums):
                return f"{unit} ({places}dp)"
    return None


def main() -> None:
    seed, target = int(sys.argv[1]), Path(sys.argv[2])
    engine = create_engine(postgres_url_from_env())
    with engine.connect() as db:
        rows = db.execute(
            text(
                "select distinct on (instrument_id, period_end, basis) id, symbol, period_end, basis,"
                " format, revenue, net_profit, eps_basic, public_at, public_at_source, version,"
                " q4_derived, source_url from hat_financial_result where source='nse' and format <>"
                " 'insurance_skipped' order by instrument_id, period_end, basis, version desc"
            )
        ).all()
    rng = random.Random(seed)
    sample = rng.sample(rows, 20)
    index = announcements()
    results = []
    for row in sample:
        item = pick_pdf(index.get(row.symbol, []), row)
        rec = {
            "symbol": row.symbol,
            "period_end": str(row.period_end),
            "basis": row.basis,
            "format": row.format,
            "q4_derived": row.q4_derived,
            "version": row.version,
            "revenue": str(row.revenue),
            "net_profit": str(row.net_profit),
            "eps_basic": str(row.eps_basic),
            "xbrl": row.source_url,
            "pdf": item["pdf"] if item else None,
        }
        if item and item["pdf"]:
            body = fetch_pdf(item["pdf"])
            txt = pdf_text(body) if body else "<not fetched>"
            nums = numbers(txt)
            rec["pdf_chars"] = len(txt)
            rec["revenue_in_pdf"] = found_in(row.revenue, nums, False)
            rec["net_profit_in_pdf"] = found_in(row.net_profit, nums, False)
            rec["eps_in_pdf"] = found_in(row.eps_basic, nums, True)
            Path(target.parent / "pdf_text").mkdir(exist_ok=True)
            (target.parent / "pdf_text" / f"{row.symbol}_{row.period_end}_{row.basis}.txt").write_text(txt)
        results.append(rec)
        print(rec["symbol"], rec["period_end"], rec["basis"], rec.get("revenue_in_pdf"), rec.get("net_profit_in_pdf"), rec.get("eps_in_pdf"))
    target.write_text(json.dumps({"seed": seed, "population": len(rows), "sample": results}, indent=1))


if __name__ == "__main__":
    main()
