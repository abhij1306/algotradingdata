"""5m opening-range-high entries for gap events 2022-2024 (5m store from 2021-10-29).
Trigger: first 5m bar after the OR (5/15/30 min) whose CLOSE > ORH, before 15:00 IST; entry at that close;
stop = low of day through the trigger bar. Day 0 remainder checked for a stop hit, then the daily exits."""
import duckdb, numpy as np, pandas as pd
from common import load_panel, simulate, COST, RISK_FLOOR, RULES

p, _ = load_panel()
ev = pd.read_parquet('cache/events.parquet')
ev = ev[(ev.year >= 2022)].copy()
D = '/data/workspace/hat-data-isin/bars_5m'
con = duckdb.connect()
keys = ev[['raw_iid', 'd']].drop_duplicates().rename(columns={'raw_iid': 'iid'})   # 5m store is keyed by the raw instrument id
con.register('keys', keys.assign(d=keys.d.dt.date))
b5 = con.execute(f"""select b.instrument_id iid, cast(b.date as date) d, b.bar_start, cast(open as double) o, cast(high as double) h,
       cast(low as double) l, cast(close as double) c, volume v
  from read_parquet('{D}/date=*/*.parquet', hive_partitioning=1) b join keys k on b.instrument_id=k.iid and cast(b.date as date)=k.d
  where cast(b.date as date) between '2022-01-01' and '2024-12-31'""").df()
b5['d'] = pd.to_datetime(b5.d)
b5['mins'] = ((b5.bar_start.dt.tz_convert('Asia/Kolkata').dt.hour * 60 + b5.bar_start.dt.tz_convert('Asia/Kolkata').dt.minute) - 555)  # minutes after 09:15
b5 = b5.sort_values(['iid', 'd', 'bar_start'])
grp = dict(tuple(b5.groupby(['iid', 'd'])))
P = {iid: g.reset_index(drop=True) for iid, g in p.groupby('iid', sort=False) if iid in set(ev.iid)}
rows = []
for r in ev.itertuples():
    g = P[r.iid]; t = r.t
    arr = {k: g[k].to_numpy() for k in ['ao', 'ah', 'al', 'ac', 'sma10', 'sma20', 'ixc']}
    k = g.ac[t] / g.c[t]                # raw -> adjusted on the gap day
    x = grp.get((r.raw_iid, r.d))
    out = {'iid': r.iid, 't': t, 'has5m': x is not None and len(x) >= 60}
    if x is not None and len(x) >= 60:
        mins, h, l, c, v, o = x.mins.to_numpy(), x.h.to_numpy(), x.l.to_numpy(), x.c.to_numpy(), x.v.to_numpy(), x.o.to_numpy()
        f = g.l[t] / l.min()            # 5m store can carry later CA adjustments: rescale to the raw daily bar
        o, h, l, c = o * f, h * f, l * f, c * f
        out['scale_dev'] = abs(f - 1)
        tv = c * v
        out['open5_ok'] = abs(o[0] / g.o[t] - 1) < 0.01   # 5m first open matches daily open
        for N in (5, 15, 30):
            orm = mins < N
            if orm.sum() == 0:
                continue
            orh = h[orm].max()
            trig = np.flatnonzero(~orm & (c > orh) & (mins < 345))   # bar starting before 15:00
            if len(trig) == 0:
                out[f'or{N}_trig'] = False; continue
            i = trig[0]; E = c[i]; S = l[:i + 1].min()
            out[f'or{N}_trig'] = True
            out[f'or{N}_time'] = int(mins[i]) + 5
            out[f'or{N}_chase'] = E / orh - 1
            out[f'or{N}_risk'] = (E - S) / E
            out[f'or{N}_ev'] = tv[:i + 1].sum() / g.adv20[t]   # early turnover vs ADV20 turnover
            R = max((E - S) / E, RISK_FLOOR)
            after = l[i + 1:]
            if len(after) and after.min() <= S:
                ret = S / E - 1; stopped0 = True
                res = {rule: ret for rule in RULES}
            else:
                stopped0 = False
                res = {rule: simulate(arr, t, E * k, S * k, rule)[0] for rule in RULES}
            out[f'or{N}_stop0'] = stopped0
            for rule, ret in res.items():
                out[f'or{N}_{rule}'] = ret - COST
                out[f'or{N}_{rule}_R'] = (ret - COST) / R
            for hh in (5, 20, 60):
                if t + hh < len(g):
                    out[f'or{N}_f{hh}'] = g.ac[t + hh] / (E * k) - 1 - COST
    rows.append(out)
o = pd.DataFrame(rows)
ev = ev.merge(o, on=['iid', 't'])
ev.to_parquet('cache/events_5m.parquet')
print(len(ev), ev.has5m.mean(), ev.open5_ok.mean())
