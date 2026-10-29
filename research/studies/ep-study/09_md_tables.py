"""Print markdown tables (selected columns) from the cached CSVs for REPORT.md."""
import pandas as pd
def md(df, cols, r=2):
    d = df[cols].round(r)
    print('| ' + ' | '.join(cols) + ' |'); print('|' + '---|' * len(cols))
    for _, x in d.iterrows(): print('| ' + ' | '.join('' if pd.isna(v) else str(v) for v in x) + ' |')
    print()
g = pd.read_csv('cache/grid.csv', keep_default_na=False, na_values=[''])
g = g[g['vol>='].astype(str) == '-']
md(g, ['entry', 'gap>=', 'neglect', 'earn', 'N', 'N/yr', 'f5%', 'f20%', 'f60%', 'x20%', 'stop20%', 'sma10 mean%', 'win%', 'time20%', 'partial%', 'F1%', 'F2%', 'F3%'])
g = pd.read_csv('cache/grid.csv', keep_default_na=False, na_values=[''])
g = g[(g.entry == 'close') & (g['vol>='].astype(str) != '-') & (g.neglect == '-')]
md(g, ['gap>=', 'vol>=', 'earn', 'N', 'N/yr', 'f20%', 'f60%', 'sma10 mean%', 'F1%', 'F2%', 'F3%'])
b = pd.read_csv('cache/grid_baseline.csv', keep_default_na=False, na_values=[''])
md(b[(b['vol>='].astype(str) == '-') & (b.neglect == '-')], ['entry', 'earn', 'N', 'f5%', 'f20%', 'f60%', 'stop20%', 'sma10 mean%', 'time20%'])
s = pd.read_csv('cache/stability.csv')
md(s[s.cut.str.match('all|fold|reg|liq')], ['def', 'cut', 'N', 'stop20%', 'sma10%', 'sma20%', 'hold60%', 'hold60 R', 'hold60 base%', 'hold60 ev-base%', 'hold60 t(ev-base)', 'hold60 t(month)'])
md(s[s.cut.str.startswith('year') & s['def'].str.match('D2|D4|C1')], ['def', 'cut', 'N', 'sma10%', 'hold60%', 'hold60 ev-base%'])
md(pd.read_csv('cache/filters_wide_exit.csv', keep_default_na=False, na_values=['']), ['entry', 'gap>=', 'neglect', 'vol>=', 'N', 'N/yr', 'sma20%', 'hold60%', 'hold60 R', 'hold60 F1%', 'hold60 F2%', 'hold60 F3%'])
o = pd.read_csv('cache/orh.csv')
md(o[o.subset.str.contains('gap>=4|gap>=6') & ~o.subset.str.contains('early')], ['subset', 'entry', 'N', 'N/yr', 'risk%', 'f20%', 'sma10%', 'sma20%', 'hold60%', 'win%', 'stop day0%', '2022%', '2023%', '2024%'])
md(pd.read_csv('cache/orh_R.csv', keep_default_na=False, na_values=['']), ['gap>=', 'entry', 'early vol>=', 'N', 'N/yr', 'risk med%', 'hold60%', 'hold60 R', 'sma20%', 'hold60 ex top3%', 'hold60 2022%', 'hold60 2023%', 'hold60 2024%'])
md(pd.read_csv('cache/coverage_bias.csv'), list(pd.read_csv('cache/coverage_bias.csv').columns))
md(pd.read_csv('cache/extra.csv'), ['def', 'cut', 'N', 'N/yr', 'hold60%', 'hold60 med%', 'hold60 R', 'sma20%', 'hold60% ex top5', 'win%', 'avg hold'])
