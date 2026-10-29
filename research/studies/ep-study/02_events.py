"""Gap-up events (gap>=4%, NIFTY 500 PIT member, 2016-2024) + matched baseline days, with
daily-entry outcomes. Output cache/events.parquet, cache/baseline.parquet. Read-only."""
import numpy as np, pandas as pd
from common import load_panel, simulate, COST, fwd_stats, LIQ

p, ix = load_panel()
rng = np.random.default_rng(7)
ev_rows, bl_rows = [], []
for iid, g in p.groupby('iid', sort=False):
    g = g.reset_index(drop=True)
    arr = {k: g[k].to_numpy() for k in ['ao', 'ah', 'al', 'ac', 'sma10', 'sma20', 'ixc']}
    cand = np.flatnonzero(g.elig.to_numpy())
    if len(cand) == 0:
        continue
    gap = g.gap.to_numpy()
    evi = cand[(gap[cand] >= 0.04) & ~g.locked.to_numpy()[cand]]
    # baseline pool: eligible non-gap days (|gap| < 1%), same stock
    pool = cand[np.abs(gap[cand]) < 0.01]
    for kind, idxs in (('event', evi), ('base', None)):
        if kind == 'base':
            if len(evi) == 0 or len(pool) == 0:
                continue
            # 5 random pool days within +-250 sessions of each event
            sel, link = [], []
            for t in evi:
                near = pool[np.abs(pool - t) <= 250]
                if len(near):
                    ch = rng.choice(near, size=min(5, len(near)), replace=False)
                    sel.extend(ch); link.extend([t] * len(ch))
            idxs = np.array(sel, dtype=int)
            links = link
        for n, t in enumerate(idxs):
            row = {'iid': iid, 't': int(t), 'd': g.d[t], 'symbol': g.symbol[t], 'gap': gap[t]}
            if kind == 'base':
                row['ev_t'] = int(links[n])
            o, h, l, c = arr['ao'][t], arr['ah'][t], arr['al'][t], arr['ac'][t]
            for ent, E, ok in (('open', o, True), ('close', c, c > o)):
                if not ok:
                    continue
                row.update(fwd_stats(arr, t, E, l, ent))
            (ev_rows if kind == 'event' else bl_rows).append(row)
ev = pd.DataFrame(ev_rows); bl = pd.DataFrame(bl_rows)
cols = ['iid', 't', 'raw_iid', 'vr', 'neg63', 'ret63', 'adv20', 'earn', 'earn_bm', 'earn_cov', 'regime', 'locked', 'green', 'risk_open', 'risk_close', 'year']
key = p[['iid', 'tpos'] + cols[2:]].rename(columns={'tpos': 't'})
ev = ev.merge(key, on=['iid', 't'], how='left'); bl = bl.merge(key, on=['iid', 't'], how='left')
sfx = '' if LIQ == 1e8 else f'_liq{int(LIQ/1e7)}cr'
ev.to_parquet(f'cache/events{sfx}.parquet'); bl.to_parquet(f'cache/baseline{sfx}.parquet')
print(len(ev), len(bl))
