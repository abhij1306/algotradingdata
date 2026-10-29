"""Q2: stop distance vs noise, shakeouts (losers that later ran), and a simple re-entry rule.
Also MFE capture / give-back of winners (Q3, from trades.csv) and early SMA50 exits."""
import numpy as np, pandas as pd
from common import *
from sim import Panel, replay, SLIP
from scale import find_f
FEE = 0.00115
P = Panel()
pd.set_option('display.width', 250)
for run, label, end in ((R16, '2016-21', '2021-12-31'), (R22, '2022-24', '2024-12-31')):
    t = load(run, 'trades')
    rows = []
    for _, r in t.iterrows():
        g, i0 = P.locate(r.instrument_id, r.entry_date)
        F, _ = find_f(g, i0, r.entry_price / (1 + SLIP), r.initial_stop)
        e, s = r.entry_price / F, r.initial_stop / F
        risk = e - s
        h, l, c, o = g.h.values, g.l.values, g.c.values, g.o.values
        adr = np.mean(h[i0 - 20:i0] / l[i0 - 20:i0] - 1) * 100
        xi = g.index[g.date == r.exit_date]
        xi = int(xi[0]) if len(xi) else i0 + r.hold_sessions
        endi = min(len(g) - 1, i0 + 60)
        endi = min(endi, np.searchsorted(g.date.values, np.datetime64(end), side='right') - 1)
        post = (h[xi + 1:endi + 1].max() - e) / risk if xi < endi else np.nan
        post_close = (c[xi + 1:endi + 1].max() - e) / risk if xi < endi else np.nan
        # re-entry: first close back above the original entry within 20 sessions of a losing exit;
        # buy next open, stop 0.5% under the lowest low since the exit; exits: hard stop + close<SMA50.
        re = np.nan
        if r.r_net < 0:
            for j in range(xi + 1, min(xi + 21, len(g) - 1)):
                if c[j] > e:
                    ne = o[j + 1] * (1 + SLIP)
                    ns = l[xi:j + 1].min() * 0.995
                    if ns < ne * 0.9:
                        ns = ne * 0.9
                    jj, px, why, rk = replay(g, j + 1, ne, ns, dict(sma=50), end_date=end)
                    re = (px - ne) / rk - FEE * (ne + px) / rk
                    break
        rows.append(dict(trade_id=r.trade_id, r=r.r_net, reason=r.exit_reason, hold=r.hold_sessions, stop_pct=r.stop_pct,
                         adr=adr, stop_adr=r.stop_pct / adr, mfe=r.mfe_r, post_hi=post, post_close=post_close, reentry=re))
    d = pd.DataFrame(rows)
    print(f'===== {label}')
    print('stop_pct', d.stop_pct.describe(percentiles=[.1, .25, .5, .75, .9]).round(2).to_dict())
    print('stop in ADR multiples', d.stop_adr.describe(percentiles=[.1, .25, .5, .75, .9]).round(2).to_dict())
    d['stop_adr_q'] = pd.qcut(d.stop_adr, 4)
    print(d.groupby('stop_adr_q', observed=True).agg(n=('r', 'size'), exp=('r', 'mean'), stopped=('reason', lambda x: (x == 'initial_stop').mean())).round(2).to_string())
    los = d[d.r < 0]
    print('losers', len(los), 'by reason', los.reason.value_counts().to_dict(), 'avg loser R', los.r.mean().round(2))
    for nm, x in (('initial_stop losers', los[los.reason == 'initial_stop']), ('sma50_close losers', los[los.reason == 'sma50_close']), ('all losers', los)):
        print(f'  {nm}: n={len(x)} later high (within 60 sess of entry) >=+2R {(x.post_hi >= 2).mean():.0%} >=+5R {(x.post_hi >= 5).mean():.0%};'
              f' later CLOSE >=+2R {(x.post_close >= 2).mean():.0%}; avg hold {x.hold.mean():.1f}')
    rr = los.reentry.dropna()
    print(f'  re-entry rule: {len(rr)} re-entries of {len(los)} losers, exp {rr.mean():.2f}R, sum {rr.sum():.1f}R, win {(rr > 0).mean():.0%}, sum ex top-3 {rr.sort_values().iloc[:-3].sum():.1f}R')
    early = d[(d.reason == 'sma50_close') & (d.hold <= 5)]
    print(f'early SMA50 exits (<=5 sess): n={len(early)} avg R {early.r.mean():.2f}, sum {early.r.sum():.1f}R; later high >=+2R {(early.post_hi >= 2).mean():.0%}')
    w = d[d.r > 0]
    print(f'winners n={len(w)}: avg MFE {w.mfe.mean():.2f}R, avg realised {w.r.mean():.2f}R, capture {w.r.sum() / w.mfe.sum():.0%}, avg give-back {(w.mfe - w.r).mean():.2f}R, median give-back {(w.mfe - w.r).median():.2f}R')
    big = d[d.mfe >= 3]
    print(f'trades with MFE>=3R: n={len(big)}, realised avg {big.r.mean():.2f}R (MFE avg {big.mfe.mean():.2f}), ended as losers {(big.r < 0).sum()}, ended <1R {(big.r < 1).sum()}')
    m2 = d[(d.mfe >= 2)]
    print(f'trades with MFE>=2R that ended <=0R: {(m2.r <= 0).sum()} of {len(m2)}')
    print('MFE distribution all trades', d.mfe.describe(percentiles=[.25, .5, .75, .9]).round(2).to_dict())
