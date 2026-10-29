"""Stability of pre-specified definitions on daily data 2016-2024: by year, fold, regime, liquidity, and
paired vs the matched baseline (same stock, +-250 sessions, |gap|<1% days, same entry and exit)."""
import numpy as np, pandas as pd
ev = pd.read_parquet('cache/events.parquet'); bl = pd.read_parquet('cache/baseline.parquet')
FOLD = {y: 'F1 16-18' if y <= 2018 else 'F2 19-21' if y <= 2021 else 'F3 22-24' for y in range(2016, 2025)}
ev['E'] = ev.earn_bm | ev.earn
ev['fold'] = ev.year.map(FOLD)
ev['reg'] = ev.regime.map({1.0: 'NIFTY500>SMA200', 0.0: 'NIFTY500<SMA200'})
ev['liq'] = pd.cut(ev.adv20 / 1e7, [10, 25, 100, 1e9], labels=['10-25cr', '25-100cr', '>100cr'], right=False)
pd.set_option('display.width', 250)
DEFS = {
    'D1 earn gap>=4 close': (lambda d: d[(d.gap >= .04) & d.E], 'close'),
    'D2 earn gap>=6 close': (lambda d: d[(d.gap >= .06) & d.E], 'close'),
    'D3 earn gap>=4 open': (lambda d: d[(d.gap >= .04) & d.E], 'open'),
    'D4 earn gap>=6 open': (lambda d: d[(d.gap >= .06) & d.E], 'open'),
    'C1 non-earn gap>=4 open': (lambda d: d[(d.gap >= .04) & ~d.E], 'open'),
    'C2 non-earn gap>=6 close': (lambda d: d[(d.gap >= .06) & ~d.E], 'close'),
}
bmean = {ent: bl.dropna(subset=[f'{ent}_sma10']).groupby(['iid', 'ev_t'])[[f'{ent}_{r}' for r in ('sma10', 'sma20', 'hold60')]].mean() for ent in ('open', 'close')}


def summ(d, ent):
    d = d[d[f'{ent}_sma10'].notna()]
    if len(d) < 3: return {'N': len(d)}
    b = bmean[ent].reindex(pd.MultiIndex.from_arrays([d.iid, d.t]))
    out = {'N': len(d), 'N/yr': len(d) / (d.year.nunique() if d.year.nunique() < 9 else 9), 'risk med%': 100 * d[f'{ent}_risk'].median(),
           'stop20%': 100 * d[f'{ent}_hit20'].mean(), 'f20%': 100 * d[f'{ent}_f20'].mean(), 'f60%': 100 * d[f'{ent}_f60'].mean()}
    for rule in ('sma10', 'sma20', 'hold60'):
        k = f'{ent}_{rule}'
        diff = (d[k].to_numpy() - b[k].to_numpy()); diff = diff[~np.isnan(diff)]
        mon = d.groupby(d.d.dt.to_period('M'))[k].mean()
        out.update({f'{rule}%': 100 * d[k].mean(), f'{rule} win%': 100 * (d[k] > 0).mean(), f'{rule} R': d[f'{k}_R'].mean(),
                    f'{rule} base%': 100 * np.nanmean(b[k].to_numpy()), f'{rule} ev-base%': 100 * diff.mean() if len(diff) else np.nan,
                    f'{rule} t(ev-base)': diff.mean() / diff.std() * np.sqrt(len(diff)) if len(diff) > 2 else np.nan,
                    f'{rule} t(month)': mon.mean() / mon.std() * np.sqrt(len(mon)) if len(mon) > 2 else np.nan})
    k = f'{ent}_hold60'
    out['hold60 top5 share'] = d[k].nlargest(5).sum() / d[k].sum() if d[k].sum() > 0 else np.nan
    return out


rows = []
for name, (f, ent) in DEFS.items():
    d = f(ev)
    rows.append({'def': name, 'cut': 'all', **summ(d, ent)})
    for col in ('fold', 'year', 'reg', 'liq'):
        for v, dd in d.groupby(col, observed=True):
            rows.append({'def': name, 'cut': f'{col}={v}', **summ(dd, ent)})
t = pd.DataFrame(rows)
t.to_csv('cache/stability.csv', index=False)
cols = ['def', 'cut', 'N', 'stop20%', 'sma10%', 'sma10 ev-base%', 'sma20%', 'sma20 ev-base%', 'hold60%', 'hold60 win%', 'hold60 R', 'hold60 base%', 'hold60 ev-base%', 'hold60 t(ev-base)', 'hold60 t(month)', 'hold60 top5 share']
print(t[cols].round(2).to_string(index=False))
