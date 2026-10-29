"""Q3 robustness: per entry-year expectancy (net R) and R per 100 held sessions for the key exit
rules, on taken + capacity-refused entries pooled; 2016-21 entries are NOT truncated at 2021-12-31
here (bars to 2024-12-31 are in-sample), 2022-24 entries are marked at 2024-12-31."""
import numpy as np, pandas as pd
from common import *
from sim import Panel, replay, SLIP
from scale import find_f
FEE = 0.00115
RULES = {'base': dict(sma=50, swing=20), 'sma50 only': dict(sma=50), 'sma50 after 10 sess': dict(sma=50, sma_grace_days=10),
         'sma100': dict(sma=100), 'chand 5xATR21': dict(chand=(21, 5.0)), 'pct15': dict(pct_trail=0.15), 'pct20': dict(pct_trail=0.20),
         'sma50 after +2R': dict(sma=50, sma_grace_r=2.0)}
P = Panel()
rows = []
for run, label in ((R16, '2016-21'), (R22, '2022-24')):
    t = load(run, 'trades'); f = load(run, 'refusals')
    ents = []
    for _, r in t.iterrows():
        g, i0 = P.locate(r.instrument_id, r.entry_date)
        F, _ = find_f(g, i0, r.entry_price / (1 + SLIP), r.initial_stop)
        ents.append(('taken', r.instrument_id, i0, r.entry_price / F, r.initial_stop / F, r.entry_date))
    for _, r in f[f.reason.isin(['size_zero_cash', 'size_below_min', 'max_positions'])].iterrows():
        iid = P.iid(r.symbol, r.date)
        g, i0 = P.locate(iid, r.date) if iid else (None, None)
        if i0 is None: continue
        F, _ = find_f(g, i0, r.would_be_entry, r.would_be_stop)
        ents.append(('refused', iid, i0, r.would_be_entry * (1 + SLIP) / F, r.would_be_stop / F, r.date))
    for samp, iid, i0, e, s, d in ents:
        g = P.series(iid)
        for name, rule in RULES.items():
            j, px, why, risk = replay(g, i0, e, s, rule, end_date='2024-12-31')
            rows.append(dict(run=label, sample=samp, year=d.year, rule=name, r=(px - e) / risk - FEE * (e + px) / risk, hold=max(1, j - i0), open_end=why == 'period_end'))
df = pd.DataFrame(rows)
pd.set_option('display.width', 250)
piv = df.groupby(['year', 'rule']).r.mean().unstack()[list(RULES)]
piv['n'] = df[df.rule == 'base'].groupby('year').size()
print('expectancy net R by entry year (taken + capacity-refused pooled)'); print(piv.round(2).to_string())
eff = df.groupby(['year', 'rule']).apply(lambda x: 100 * x.r.sum() / x.hold.sum()).unstack()[list(RULES)]
print('R per 100 held sessions by year'); print(eff.round(2).to_string())
print('years where rule beats base on expectancy:', {k: int((piv[k] > piv['base']).sum()) for k in RULES if k != 'base'}, 'of', len(piv))
print('years where rule beats base on R/100 sessions:', {k: int((eff[k] > eff['base']).sum()) for k in RULES if k != 'base'})
tot = df.groupby(['run', 'rule']).agg(exp=('r', 'mean'), hold=('hold', 'mean'), open_end=('open_end', 'mean')).unstack(0)
print(tot.round(2).to_string())
