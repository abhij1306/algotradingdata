"""Cache raw daily bars 2015-01-01..2024-12-31 (hold-out excluded) as float parquet, with a
back-adjustment factor derived from NSE's prev_close (prev_close_t / close_{t-1} != 1 marks a
corporate action). adj_* = raw * cumulative factor (back-adjusted to the latest date <= 2024-12-31)."""
import duckdb, numpy as np, pandas as pd
ROOT = '/data/workspace/hat-data-isin'
OUT = '/data/workspace/research/vcp-leaks/cache'
c = duckdb.connect()
bars = c.sql(f"""
 select instrument_id, symbol, series, cast(date as date) as date,
  open::double as "open", high::double as high, low::double as low, close::double as "close",
  prev_close::double prev_close, volume::double volume, traded_value::double tv
 from read_parquet('{ROOT}/bars_daily_raw/**/*.parquet', hive_partitioning=1)
 where date between '2015-01-01' and '2024-12-31'
""").df()
bars = bars.sort_values(['instrument_id', 'date']).drop_duplicates(['instrument_id', 'date'], keep='last')
g = bars.groupby('instrument_id')
bars['prior_close'] = g['close'].shift(1)
ratio = bars['prev_close'] / bars['prior_close']
# event factor applies to all bars BEFORE the ex-date; only count clear CA (>1.5% gap between NSE prev_close and our prior close)
ev = np.where((ratio.notna()) & ((ratio - 1).abs() > 0.015), ratio, 1.0)
bars['ca_event'] = ev != 1.0
bars['ev'] = ev
# cumulative factor for bar t = product of ev over all later bars
bars['f'] = (bars.iloc[::-1].groupby('instrument_id')['ev'].cumprod().iloc[::-1]
             / bars['ev'])
for col in ['open', 'high', 'low', 'close']:
    bars['a' + col] = bars[col] * bars['f']
bars.drop(columns=['ev']).to_parquet(f'{OUT}/bars.parquet', index=False)
print(len(bars), bars.ca_event.sum())
idx = c.sql(f"""select index_name, cast(date as date) date, close::double as "close"
 from read_parquet('{ROOT}/index_daily/**/*.parquet', hive_partitioning=1)
 where date <= '2024-12-31' and index_name in ('NIFTY 500','NIFTY 500 TRI')""").df()
idx.to_parquet(f'{OUT}/index.parquet', index=False)
br = c.sql(f"""select cast(date as date) date, breadth_pct::double breadth_pct
 from read_parquet('{ROOT}/breadth_daily/**/*.parquet', hive_partitioning=1) where date <= '2024-12-31'""").df()
br.to_parquet(f'{OUT}/breadth.parquet', index=False)
