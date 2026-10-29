"""Tables for the 5m ORH study (2022-2024) and the 5m coverage bias."""
import numpy as np, pandas as pd
e = pd.read_parquet('cache/events_5m.parquet')
e['E'] = e.earn_bm | e.earn
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)


def row(d, ent, lab):
    k = f'{ent}_sma10'; d = d[d[k].notna()] if k in d else d.iloc[:0]
    if len(d) == 0: return None
    x = {'subset': lab, 'entry': ent, 'N': len(d), 'N/yr': len(d) / 3, 'f5%': 100 * d[f'{ent}_f5'].mean(), 'f20%': 100 * d[f'{ent}_f20'].mean(),
         'sma10%': 100 * d[k].mean(), 'sma10 med%': 100 * d[k].median(), 'win%': 100 * (d[k] > 0).mean(), 'sma10 R': d[f'{k}_R'].mean(),
         'sma20%': 100 * d[f'{ent}_sma20'].mean(), 'hold60%': 100 * d[f'{ent}_hold60'].mean(), 'time20%': 100 * d[f'{ent}_time20'].mean(), 'partial%': 100 * d[f'{ent}_partial'].mean(), 'risk%': 100 * d[f'{ent}_risk'].median()}
    for y in (2022, 2023, 2024): x[f'{y}%'] = 100 * d[d.year == y][k].mean()
    if ent.startswith('or'): x['stop day0%'] = 100 * d[f'{ent}_stop0'].mean()
    return x


out = []
cov = e[e.has5m]
for gmin in (.04, .06, .08):
    for earn in ('-', 'y', 'n'):
        for evol in (0, 0.5):
            m = cov.gap >= gmin
            if earn == 'y': m &= cov.E
            if earn == 'n': m &= ~cov.E
            d = cov[m]
            lab = f'gap>={int(gmin*100)} earn={earn}' + (' early-vol>=0.5' if evol else '')
            ents = ['or5', 'or15', 'or30'] if evol else ['open', 'close', 'or5', 'or15', 'or30']
            for ent in ents:
                dd = d
                if evol: dd = d[d[f'{ent}_ev'] >= evol]
                r = row(dd, ent, lab)
                if r: out.append(r)
t = pd.DataFrame(out)
t.to_csv('cache/orh.csv', index=False)
print(t.round(2).to_string(index=False))
# trigger rates
print('\nORH trigger rate on covered events:', {N: round(cov[f'or{N}_trig'].mean(), 3) for N in (5, 15, 30)})
# coverage bias: daily-entry outcomes, covered vs not
print('\ncoverage bias (2022-2024 events, daily entries):')
b = []
for gmin in (.04, .06, .08):
    for has in (True, False):
        d = e[(e.gap >= gmin) & (e.has5m == has)]
        b.append({'gap>=': gmin, 'has5m': has, 'N': len(d), 'earn share%': 100 * d.E.mean(), 'gap med%': 100 * d.gap.median(), 'adv20 med cr': d.adv20.median() / 1e7,
                  'open sma10%': 100 * d.open_sma10.mean(), 'close sma10%': 100 * d.close_sma10.mean(), 'open f20%': 100 * d.open_f20.mean()})
print(pd.DataFrame(b).round(2).to_string(index=False))
pd.DataFrame(b).to_csv('cache/coverage_bias.csv', index=False)
