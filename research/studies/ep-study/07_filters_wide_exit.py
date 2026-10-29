"""Do neglect / day-volume filters help the earnings-gap definitions under the wider exits (SMA20 trail, 60d hold)?"""
import itertools, pandas as pd
ev = pd.read_parquet('cache/events.parquet'); ev['E'] = ev.earn_bm | ev.earn
ev['fold'] = ev.year.map(lambda y: 'F1' if y <= 2018 else 'F2' if y <= 2021 else 'F3')
rows = []
for ent, g, neg, vol in itertools.product(('open', 'close'), (.04, .06, .08), (False, True), (0, 2)):
    if ent == 'open' and vol: continue
    d = ev[(ev.gap >= g) & ev.E]
    if neg: d = d[d.neg63]
    if vol: d = d[d.vr >= vol]
    d = d[d[f'{ent}_sma10'].notna()]
    r = {'entry': ent, 'gap>=': int(g * 100), 'neglect': 'y' if neg else '-', 'vol>=': vol or '-', 'N': len(d), 'N/yr': len(d) / 9}
    for rule in ('sma20', 'hold60'):
        k = f'{ent}_{rule}'
        r[f'{rule}%'] = 100 * d[k].mean(); r[f'{rule} R'] = d[f'{k}_R'].mean()
        for f in ('F1', 'F2', 'F3'): r[f'{rule} {f}%'] = 100 * d[d.fold == f][k].mean()
    rows.append(r)
t = pd.DataFrame(rows); t.to_csv('cache/filters_wide_exit.csv', index=False)
pd.set_option('display.width', 250); print(t.round(2).to_string(index=False))
