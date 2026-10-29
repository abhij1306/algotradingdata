"""Check the replay reproduces the engine's exits (baseline: hard stop + close<SMA50 + close<20-day swing low)."""
import numpy as np, pandas as pd
from common import *
from sim import Panel, replay, SLIP
from scale import find_f
P = Panel()
for run, end in ((R16, '2021-12-31'), (R22, '2024-12-31')):
    t = load(run, 'trades')
    rows = []
    for _, r in t.iterrows():
        g, i0 = P.locate(r.instrument_id, r.entry_date)
        f, how = find_f(g, i0, r.entry_price / (1 + SLIP), r.initial_stop)
        e, s = r.entry_price / f, r.initial_stop / f
        j, px, why, risk = replay(g, i0, e, s, dict(sma=50, swing=20), end_date=end)
        rows.append(dict(trade_id=r.trade_id, how=how, f=f, my_exit=g.date[j], my_r=(px - e) / risk, why=why,
                         eng_exit=r.exit_date, eng_r=(r.exit_price - r.entry_price) / r.risk_per_share, eng_why=r.exit_reason))
    v = pd.DataFrame(rows)
    print('==', run, v.how.value_counts().to_dict())
    same = (v.my_exit == v.eng_exit)
    print('same exit date', same.mean().round(3), '|R diff| same date median/max', (v.my_r - v.eng_r)[same].abs().median().round(4), (v.my_r - v.eng_r)[same].abs().max().round(3),
          'sum R mine', v.my_r.sum().round(1), 'engine', v.eng_r.sum().round(1))
    print(v[~same][['trade_id', 'how', 'f', 'my_exit', 'eng_exit', 'my_r', 'eng_r', 'why', 'eng_why']].to_string())
