"""Q1: taken vs refused signals on the same forward metric (gross R at the close 20/60 sessions
after entry with the signal's stop, -1 if a low hits the stop first, stop checked from the session
after entry). Refusals' own fwd_r columns are compared with this recomputation."""
import numpy as np, pandas as pd
from common import *
from sim import Panel, fwd_r, SLIP
from scale import find_f
P = Panel()
out = []
for run, label in ((R16, '2016-21'), (R22, '2022-24')):
    t = load(run, 'trades'); f = load(run, 'refusals'); s = load(run, 'signals')
    rows = []
    for _, r in t.iterrows():
        g, i0 = P.locate(r.instrument_id, r.entry_date)
        F, _ = find_f(g, i0, r.entry_price / (1 + SLIP), r.initial_stop)
        d = fwd_r(g, i0, r.entry_price / F, r.initial_stop / F)
        rows.append(dict(run=label, date=r.entry_date, symbol=r.symbol, group='TAKEN', r_net=r.r_net,
                         rs_rank=r.rs_rank, setup_score=r.setup_score, stop_pct=r.stop_pct, **d))
    miss = 0
    for _, r in f.iterrows():
        iid = P.iid(r.symbol, r.date)
        g, i0 = P.locate(iid, r.date) if iid else (None, None)
        if i0 is None:
            miss += 1; continue
        F, _ = find_f(g, i0, r.would_be_entry, r.would_be_stop)
        d = fwd_r(g, i0, r.would_be_entry / F, r.would_be_stop / F)
        rows.append(dict(run=label, date=r.date, symbol=r.symbol, group=r.reason, eng_r20=r.fwd_r_20d_gross,
                         eng_r60=r.fwd_r_60d_gross, rs_rank=r.rs_rank, setup_score=r.setup_score, stop_pct=r.stop_pct,
                         open_pos=r.open_positions_at_entry, **d))
    print(label, 'refusals unmapped', miss)
    out.append(pd.DataFrame(rows))
df = pd.concat(out)
df.to_csv('q1_signals_fwd.csv', index=False)
ref = df[df.group != 'TAKEN']
print('my fwd vs engine fwd (refusals): |r20 diff| median', (ref.r20 - ref.eng_r20).abs().median().round(3),
      'corr r60', ref[['r60', 'eng_r60']].corr().iloc[0, 1].round(3))
# engine fwd for taken trades isn't available, so use mine for both
def summ(x):
    return pd.Series(dict(n=len(x), r20=x.r20.mean(), r60=x.r60.mean(), med_r60=x.r60.median(),
                          stop_hit60=(x.r60 == -1).mean(), ge2R=(x.r60 >= 2).mean(), mfe60=x.mfe60.mean(),
                          rs=x.rs_rank.mean(), stop_pct=x.stop_pct.mean()))
print(df.groupby(['run', 'group']).apply(summ).round(2).to_string())
df['bucket'] = np.where(df.group == 'TAKEN', 'TAKEN', np.where(df.group.isin(['size_zero_cash', 'size_below_min', 'max_positions']), 'capacity', 'other'))
print(df.groupby(['run', 'bucket']).apply(summ).round(2).to_string())
# RS / setup score as rankers across all signals
for col in ('rs_rank', 'setup_score', 'stop_pct'):
    for label, x in df.groupby('run'):
        x = x.dropna(subset=['r60', col])
        q = pd.qcut(x[col], 4, labels=False, duplicates='drop')
        print(col, label, 'spearman r60', x[[col, 'r60']].corr('spearman').iloc[0, 1].round(3),
              'r60 by quartile', x.groupby(q).r60.mean().round(2).tolist(), 'n', len(x))
# capacity-capped days: taken vs refused on the same day
cap = df[df.bucket.isin(['TAKEN', 'capacity'])]
days = cap.groupby(['run', 'date']).bucket.nunique()
both = days[days == 2].index
c2 = cap.set_index(['run', 'date']).loc[both].reset_index()
print('same-day taken vs capacity-refused', c2.groupby(['run', 'bucket']).agg(n=('r60', 'size'), r60=('r60', 'mean'), rs=('rs_rank', 'mean')).round(2).to_string())
