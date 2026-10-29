"""Build the daily panel (2015-01-01..2024-12-31, hold-out excluded) with adjusted prices,
PIT NIFTY 500 membership, earnings flag, NIFTY 500 regime. Read-only."""
import os, sys, duckdb, pandas as pd, numpy as np
os.environ['DB_NAME'] = 'hat_live'; os.environ['PGOPTIONS'] = '-c default_transaction_read_only=on'
sys.path.insert(0, '/data/workspace/algotrading/backend')
from sqlalchemy import text
from app.database import engine

D = '/data/workspace/hat-data-isin'
OUT = '/data/workspace/research/ep-study/cache'
END = '2024-12-31'
con = duckdb.connect()
bars = con.execute(f"""
  select cast(date as date) d, instrument_id iid, isin, symbol, series,
         cast(open as double) o, cast(high as double) h, cast(low as double) l,
         cast(close as double) c, cast(prev_close as double) pc, volume v,
         cast(traded_value as double) tv
  from read_parquet('{D}/bars_daily_raw/date=*/*.parquet', hive_partitioning=1)
  where cast(date as date) between '2015-01-01' and '{END}' and series in ('EQ','BE')
""").df()
assert pd.Timestamp(bars.d.max()) <= pd.Timestamp(END)
with engine.connect() as c:
    mem = pd.read_sql(text("select instrument_id::text iid, effective_from f, effective_to t from hat_index_member where index_name='NIFTY 500'"), c)
    res = pd.read_sql(text("""select instrument_id::text iid, public_at, public_at_source src from hat_financial_result
                              where public_at <= '2024-12-31' and coalesce(public_at_estimated,false)=false"""), c)
bars['d'] = pd.to_datetime(bars.d)
bars = bars.sort_values(['iid', 'd']).drop_duplicates(['iid', 'd'], keep='last').reset_index(drop=True)
# NSE prev_close is the previous RAW close on ex-dates, so it cannot adjust anything. Prices for gaps and
# forward returns come from HAT's adjusted view (bars_daily via DataStore.connect(stored_adjustment): splits,
# bonuses, rights, demergers + dividends, ISIN chains linked), exported read-only by
# /data/workspace/research/momentum/build_tr_panel.py to bars_tr.parquet (<= 2024-12-31).
tr = con.execute(f"""select instrument_id cid, isin, series, cast(date as date) d, cast(open as double) ao, cast(high as double) ah,
   cast(low as double) al, cast(close as double) ac, cast(volume as double) vadj
   from '/data/workspace/research/momentum/data/bars_tr.parquet' where date <= '{END}'""").df()
tr['d'] = pd.to_datetime(tr.d)
n0 = len(bars)
bars = bars.merge(tr, on=['isin', 'series', 'd'], how='inner')
print('rows with adjusted bars', len(bars), 'of', n0)
bars['r'] = 0
# membership flag
mem['f'] = pd.to_datetime(mem.f); mem['t'] = pd.to_datetime(mem.t).fillna(pd.Timestamp('2100-01-01'))
m = bars[['iid', 'd']].reset_index().merge(mem, on='iid')
m = m[(m.d >= m.f) & (m.d < m.t)]
bars['member'] = False; bars.loc[m['index'].unique(), 'member'] = True
# earnings: result public within [d-1 session 15:30 IST, d 09:15 IST] -> approximate with calendar
res['pa'] = pd.to_datetime(res.public_at, utc=True).dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
# map each result to the first session whose open (09:15) is after public_at
sess = np.sort(bars.d.unique())
openT = pd.to_datetime(sess) + pd.Timedelta(hours=9, minutes=15)
idx = np.searchsorted(openT.values, res.pa.values, side='left')
ok = idx < len(sess)
res = res[ok].copy(); res['first_sess'] = pd.to_datetime(sess[idx[ok]])
res = res.drop_duplicates(['iid', 'first_sess'])[['iid', 'first_sess']]
res['earn'] = True
bars = bars.merge(res.rename(columns={'first_sess': 'd'}), on=['iid', 'd'], how='left')
bars['earn'] = bars.earn.fillna(False).astype(bool)
# board-meeting results flag (scheduled meeting dates are public in advance; 2011+, all folds)
import glob
bm = pd.concat([pd.read_csv(f, usecols=['isin', 'meeting_date', 'purpose']) for f in glob.glob('/data/workspace/ca-data/board_meetings_*.csv')])
bm = bm[bm.purpose.str.contains('result', case=False, na=False)].copy()
bm['md'] = pd.to_datetime(bm.meeting_date, format='%d-%b-%Y', errors='coerce')
bm = bm[bm.md.notna() & (bm.md <= END)].drop_duplicates(['isin', 'md'])
si = np.searchsorted(sess, bm.md.values, side='left')          # meeting session (or next if holiday)
okb = si < len(sess) - 1
bm = bm[okb]; si = si[okb]
flag = pd.concat([pd.DataFrame({'isin': bm['isin'].values, 'd': pd.to_datetime(sess[si])}),
                  pd.DataFrame({'isin': bm['isin'].values, 'd': pd.to_datetime(sess[si + 1])})]).drop_duplicates()
flag['earn_bm'] = True
bars = bars.merge(flag, on=['isin', 'd'], how='left'); bars['earn_bm'] = bars.earn_bm.fillna(False).astype(bool)
print('board-meeting result flags on member days by year', bars[bars.member & bars.earn_bm].groupby(bars.d.dt.year).size().to_dict())
bars.drop(columns=['r']).to_parquet(f'{OUT}/panel.parquet')
idxd = con.execute(f"""select cast(date as date) d, cast(close as double) c from read_parquet('{D}/index_daily/date=*/*.parquet', hive_partitioning=1)
  where index_name='NIFTY 500' and cast(date as date) between '2014-01-01' and '{END}' order by 1""").df()
idxd.to_parquet(f'{OUT}/nifty500.parquet')
print(len(bars), bars.member.sum(), bars.earn.sum(), res.first_sess.min(), len(idxd))
