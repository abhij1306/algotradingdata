"""Cache the engine's cap-adjusted daily bars (bars_daily_cap_adj, the view the backtest reads)
for 2015-01-01..2024-12-31, using only corporate-action factors with ex_date <= 2024-12-31 (no
hold-out information). Run with DB_NAME=hat_live PGOPTIONS='-c default_transaction_read_only=on'."""
import dataclasses, datetime as dt, sys
sys.path.insert(0, '/data/workspace/algotrading/backend')
from app.database import db_session_scope
from app.hat.settings import operator_settings
from app.hat.data.store import DataStore
from app.hat.data.chains import stored_adjustment
CUT = dt.date(2024, 12, 31)
OUT = '/data/workspace/research/vcp-leaks/cache'
s = operator_settings()
with db_session_scope() as session:
    adj = stored_adjustment(session)
adj = dataclasses.replace(adj, factors=tuple(f for f in adj.factors if f.ex_date <= CUT),
                          dividends=tuple(d for d in adj.dividends if d.ex_date <= CUT))
store = DataStore('/data/workspace/hat-data-isin', memory_limit='3GB')
with store.connect(adj) as con:
    con.execute(f"""COPY (SELECT instrument_id::VARCHAR instrument_id, date, series, symbol,
      CAST(open AS DOUBLE) o, CAST(high AS DOUBLE) h, CAST(low AS DOUBLE) l, CAST(close AS DOUBLE) c,
      CAST(raw_close AS DOUBLE) raw_c, CAST(volume AS DOUBLE) v, CAST(traded_value AS DOUBLE) tv
      FROM bars_daily_cap_adj WHERE date BETWEEN DATE '2015-01-01' AND DATE '2024-12-31')
      TO '{OUT}/adj.parquet' (FORMAT parquet)""")
    print(con.execute(f"select count(*), count(distinct instrument_id), max(date) from '{OUT}/adj.parquet'").fetchall())
