"""Slim float panel from bars_tr.parquet: date, chain id, symbol, adj open/close, raw close, traded value."""
import duckdb
con = duckdb.connect(); con.execute("SET enable_progress_bar=false")
con.execute("""COPY (SELECT date, instrument_id AS iid, symbol, CAST(open AS DOUBLE) AS o, CAST(close AS DOUBLE) AS c,
  CAST(prev_close AS DOUBLE) AS pc, CAST(raw_close AS DOUBLE) AS rc, CAST(traded_value AS DOUBLE) AS tv
  FROM 'data/bars_tr.parquet') TO 'data/slim.parquet' (FORMAT parquet)""")
