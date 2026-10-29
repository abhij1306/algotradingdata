"""Export HAT's total-return adjusted daily bars (bars_daily view: splits/bonuses/rights/demergers +
dividends, ISIN chains linked) for EQ/BE, 2014-06-01..2024-12-31 only, plus PIT NIFTY 500 membership.
Read-only: hat_live opened with default_transaction_read_only."""
import os
os.environ["PGOPTIONS"] = "-c default_transaction_read_only=on"
os.environ["DB_NAME"] = "hat_live"
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import engine
from app.hat.data.store import DataStore
from app.hat.data.chains import stored_adjustment

OUT = Path("/data/workspace/research/momentum/data")
with Session(engine) as s:
    adj = stored_adjustment(s)
    mem = s.execute(text("select instrument_id::text, effective_from, effective_to, symbol from hat_index_member "
                         "where index_name='NIFTY 500' and effective_from <= '2024-12-31'")).fetchall()
lineage = dict(adj.lineage)
import pandas as pd
m = pd.DataFrame(mem, columns=["instrument_id", "effective_from", "effective_to", "symbol"])
m["chain_id"] = m.instrument_id.map(lambda i: lineage.get(i, i))
m.to_parquet(OUT / "nifty500_members.parquet")
con = DataStore(Path("/data/workspace/hat-data-isin"), memory_limit="4GB",
                temp_dir=Path("/tmp/claude-1000/momentum-spill")).connect(adj)
print(con.execute("describe bars_daily").fetchall())
con.execute(f"""COPY (SELECT * FROM bars_daily WHERE date BETWEEN DATE '2014-06-01' AND DATE '2024-12-31'
  AND series IN ('EQ','BE')) TO '{OUT}/bars_tr.parquet' (FORMAT parquet)""")
print(con.execute(f"select count(*), min(date), max(date), count(distinct instrument_id) from '{OUT}/bars_tr.parquet'").fetchall())
print(len(m), m.chain_id.nunique())
