"""Daily event grid 2016-2024: every cell printed (no cherry-picking)."""
import numpy as np, pandas as pd, itertools, sys
ev = pd.read_parquet('cache/events.parquet'); bl = pd.read_parquet('cache/baseline.parquet')
FOLD = {2016: 'F1', 2017: 'F1', 2018: 'F1', 2019: 'F2', 2020: 'F2', 2021: 'F2', 2022: 'F3', 2023: 'F3', 2024: 'F3'}
for df in (ev, bl):
    df['fold'] = df.year.map(FOLD)
    df['E'] = df.earn_bm | df.earn   # results day or next session (board-meeting date 2016+, result timestamp 2020-04+)


def tstat(x):
    x = x.dropna(); return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 else np.nan


def stats(df, ent, years):
    k = f'{ent}_sma10'
    d = df[df[k].notna()]
    if len(d) == 0:
        return None
    r = {'N': len(d), 'N/yr': len(d) / years}
    for h in (5, 20, 60):
        r[f'f{h}%'] = 100 * d[f'{ent}_f{h}'].mean()
    r['x20%'] = 100 * d[f'{ent}_x20'].mean()
    r['stop20%'] = 100 * d[f'{ent}_hit20'].mean()
    r['sma10 mean%'] = 100 * d[k].mean()
    r['sma10 med%'] = 100 * d[k].median()
    r['win%'] = 100 * (d[k] > 0).mean()
    r['sma10 R'] = d[f'{k}_R'].mean()
    r['t'] = tstat(d[k])
    r['time20%'] = 100 * d[f'{ent}_time20'].mean()
    r['partial%'] = 100 * d[f'{ent}_partial'].mean()
    for f in ('F1', 'F2', 'F3'):
        r[f'{f}%'] = 100 * d[d.fold == f][k].mean()
    r['top5 share'] = d[k].nlargest(5).sum() / d[k].sum() if d[k].sum() > 0 else np.nan
    return r


def cells(df, earn_only_period=False):
    rows = []
    for ent, gmin, neg, vol, earn in itertools.product(('open', 'close'), (.04, .06, .08, .10), (False, True), (0, 2, 3), ('-', 'y', 'n')):
        if ent == 'open' and vol:      # full-day volume is unknown at the open: lookahead, skip
            continue
        m = df.gap >= gmin
        if neg: m &= df.neg63
        if vol: m &= df.vr >= vol
        yrs = 9
        if earn == 'y': m &= df.E
        if earn == 'n': m &= ~df.E
        s = stats(df[m], ent, yrs)
        if s:
            rows.append({'entry': ent, 'gap>=': int(gmin * 100), 'neglect': 'y' if neg else '-', 'vol>=': vol or '-', 'earn': earn, **s})
    return pd.DataFrame(rows)


pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40); pd.set_option('display.max_rows', 200)
g = cells(ev)
g.to_csv('cache/grid.csv', index=False)
gb = cells(bl.assign(gap=1.0))   # baseline: gap filter n/a; same other filters
fmt = lambda x: f'{x:.2f}' if isinstance(x, float) else str(x)
if __name__ == '__main__':
    print(g.round(2).to_string(index=False))
    print('\nbaseline (random |gap|<1% days of the same stocks, +-1y, same filters):')
    print(gb[gb['gap>='] == 4].drop(columns=['gap>=']).round(2).to_string(index=False))
    gb.to_csv('cache/grid_baseline.csv', index=False)
