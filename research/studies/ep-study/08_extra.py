"""Extra checks for the two candidate definitions: Rs 5-10 cr liquidity bucket, the engine regime gate
(NIFTY 500 SMA10>SMA20, both rising over 3 sessions, on the previous session), R for the 5m ORH entries,
and outlier dependence."""
import numpy as np, pandas as pd
pd.set_option('display.width', 250)
ix = pd.read_parquet('cache/nifty500.parquet'); ix['d'] = pd.to_datetime(ix.d)
s10, s20 = ix.c.rolling(10).mean(), ix.c.rolling(20).mean()
ix['gate'] = ((s10 > s20) & (s10 > s10.shift(3)) & (s20 > s20.shift(3))).shift(1)
ev5 = pd.read_parquet('cache/events_liq5cr.parquet'); ev5['E'] = ev5.earn_bm | ev5.earn
ev5 = ev5.merge(ix[['d', 'gate']], on='d', how='left')
ev5['fold'] = ev5.year.map(lambda y: 'F1' if y <= 2018 else 'F2' if y <= 2021 else 'F3')
ev5['liq'] = pd.cut(ev5.adv20 / 1e7, [5, 10, 25, 100, 1e9], labels=['5-10cr', '10-25cr', '25-100cr', '>100cr'], right=False)
print('engine regime gate on share of sessions 2016-2024:', round(ix[ix.d >= '2016-01-01'].gate.mean(), 3))
rows = []
for name, gmin, ent in (('A earn gap>=6 close', .06, 'close'), ('A earn gap>=6 open', .06, 'open'), ('B earn gap>=4 close', .04, 'close')):
    d = ev5[(ev5.gap >= gmin) & ev5.E & ev5[f'{ent}_sma10'].notna()]
    for cut, dd in [('all >=5cr', d)] + [(f'liq {k}', v) for k, v in d.groupby('liq', observed=True)] + \
                   [(f'gate {k}', v) for k, v in d.groupby('gate')] + [(f'>=5cr {k}', v) for k, v in d.groupby('fold')]:
        k = f'{ent}_hold60'
        x = dd[k]
        rows.append({'def': name, 'cut': cut, 'N': len(dd), 'N/yr': len(dd) / 9, 'hold60%': 100 * x.mean(), 'hold60 med%': 100 * x.median(),
                     'hold60 R': dd[f'{k}_R'].mean(), 'sma20%': 100 * dd[f'{ent}_sma20'].mean(),
                     'hold60% ex top5': 100 * x.drop(x.nlargest(5).index).mean() if len(x) > 10 else np.nan,
                     'win%': 100 * (x > 0).mean(), 'avg hold': dd[f'{k}_hold'].mean()})
t = pd.DataFrame(rows); t.to_csv('cache/extra.csv', index=False)
print(t.round(2).to_string(index=False))
# R for the 5m ORH entries (2022-2024, Rs 10 cr universe, covered events)
e = pd.read_parquet('cache/events_5m.parquet'); e['E'] = e.earn_bm | e.earn
rows = []
for gmin in (.04, .06):
    for ent in ('open', 'close', 'or5', 'or15', 'or30'):
        for evol in ((0, 0.5) if ent.startswith('or') else (0,)):
            d = e[e.has5m & (e.gap >= gmin) & e.E & e[f'{ent}_sma10'].notna()]
            if evol: d = d[d[f'{ent}_ev'] >= evol]
            rows.append({'gap>=': gmin, 'entry': ent, 'early vol>=': evol or '-', 'N': len(d), 'N/yr': len(d) / 3,
                         'risk med%': 100 * d[f'{ent}_risk'].median(), 'hold60%': 100 * d[f'{ent}_hold60'].mean(), 'hold60 R': d[f'{ent}_hold60_R'].mean(),
                         'sma20%': 100 * d[f'{ent}_sma20'].mean(), 'sma20 R': d[f'{ent}_sma20_R'].mean(),
                         'hold60 ex top3%': 100 * d[f'{ent}_hold60'].drop(d[f'{ent}_hold60'].nlargest(3).index).mean(),
                         **{f'hold60 {y}%': 100 * d[d.year == y][f'{ent}_hold60'].mean() for y in (2022, 2023, 2024)}})
t = pd.DataFrame(rows); t.to_csv('cache/orh_R.csv', index=False)
print(t.round(2).to_string(index=False))
