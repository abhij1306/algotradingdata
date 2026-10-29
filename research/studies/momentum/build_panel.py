"""Build a stocks-only daily panel (EQ/BE) 2014-06-01..2024-12-31 from raw bars. Hold-out (2025+) never read."""
import glob, os, duckdb
OUT = "/data/workspace/research/momentum/data/bars.parquet"
files = []
for d in sorted(glob.glob("/data/workspace/hat-data-isin/bars_daily_raw/date=*")):
    day = d.split("=")[1]
    if "2014-06-01" <= day <= "2024-12-31":
        files += [(f, day) for f in glob.glob(d + "/*.parquet")]
con = duckdb.connect()
q = " UNION ALL ".join(
    f"SELECT DATE '{day}' AS date, instrument_id, isin, symbol, series, CAST(open AS DOUBLE) AS open, CAST(high AS DOUBLE) AS high, "
    f"CAST(low AS DOUBLE) AS low, CAST(close AS DOUBLE) AS close, CAST(prev_close AS DOUBLE) AS prev_close, volume, CAST(traded_value AS DOUBLE) AS traded_value "
    f"FROM read_parquet('{f}') WHERE series IN ('EQ','BE')" for f, day in files)
con.execute(f"COPY ({q}) TO '{OUT}' (FORMAT parquet)")
print(con.execute(f"SELECT count(*), min(date), max(date), count(distinct instrument_id) FROM '{OUT}'").fetchall())
