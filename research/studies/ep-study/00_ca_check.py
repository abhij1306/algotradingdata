"""How corporate-action ex-dates affect gap events (NSE prev_close is the raw previous close on ex-dates)."""
import numpy as np, pandas as pd
from common import load_panel, LIQ
p, _ = load_panel()
m = p[p.member & (p.d >= '2016-01-01') & (p.adv20 >= LIQ) & p.ret63.notna() & ~p.locked]
print('member liquid days', len(m), 'ex-dates', int(m.exdate.sum()))
for g in (.04, .06, .08, .10):
    raw, adj = m.gap_raw >= g, m.gap >= g
    print(f'gap>={g:.2f}: raw-gap events {raw.sum()}, adjusted-gap events {adj.sum()}, on ex-dates (dropped) {int((adj & m.exdate).sum())}, '
          f'raw-only artifacts {int((raw & ~adj).sum())}, adjusted-only {int((adj & ~raw).sum())}')
print(m[(m.gap_raw >= .04) & (m.gap < .04)][['d', 'symbol', 'o', 'pc', 'gap_raw', 'gap']].head(8).to_string())
