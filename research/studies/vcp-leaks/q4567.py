"""Q4 costs/turnover, Q5 exposure, Q6 regime/breadth, Q7 fill sanity checks."""
import json, numpy as np, pandas as pd
from common import *
from sim import Panel, SLIP
from scale import find_f
pd.set_option('display.width', 250)
P = Panel()
idx = pd.read_parquet(f'{CACHE}/index.parquet'); idx['date'] = pd.to_datetime(idx.date)
n5 = idx[idx.index_name == 'NIFTY 500'].sort_values('date').set_index('date').close
n5_sma50 = n5.rolling(50).mean(); n5_sma200 = n5.rolling(200).mean()
for run, label in ((R16, '2016-21'), (R22, '2022-24')):
    t = load(run, 'trades'); e = load(run, 'equity'); s = load(run, 'signals'); f = load(run, 'refusals')
    m = json.load(open(f'{RUNS}/{run}/run.json'))['metrics']
    print(f'===== {label}')
    # ---- Q4
    t['notional'] = t.entry_price * t.qty
    t['pos_pct'] = 100 * t.notional / np.interp(t.entry_date.astype('int64'), e.date.astype('int64'), e.equity)
    slip_rs = SLIP / (1 + SLIP) * t.notional + SLIP / (1 - SLIP) * t.exit_price * t.qty
    t['fee_R'] = t.fees / (t.risk_per_share * t.qty)
    t['slip_R'] = slip_rs / (t.risk_per_share * t.qty)
    gross = t.gross_pnl.sum(); fees = t.fees.sum(); slip = slip_rs.sum()
    yrs = (e.date.iloc[-1] - e.date.iloc[0]).days / 365.25
    turnover = (t.notional + t.exit_price * t.qty).sum() / e.equity.mean() / yrs
    print(f'Q4 position % of equity: median {t.pos_pct.median():.1f}% (p10 {t.pos_pct.quantile(.1):.1f}, p90 {t.pos_pct.quantile(.9):.1f}); '
          f'fee/trade median Rs {t.fees.median():.0f} = {100 * (t.fees / (t.notional + t.exit_price * t.qty)).median():.3f}% of each side')
    print(f'   fees {fees:,.0f}, slippage {slip:,.0f}, gross(after slip) {gross:,.0f}, net {t.net_pnl.sum():,.0f}; '
          f'fees/gross {fees / gross:.1%}; (fees+slip)/(gross+slip) {(fees + slip) / (gross + slip):.1%}')
    print(f'   friction per trade: fees {t.fee_R.mean():.3f}R + slippage {t.slip_R.mean():.3f}R = {(t.fee_R + t.slip_R).mean():.3f}R vs net expectancy {t.r_net.mean():.3f}R; '
          f'turnover {turnover:.1f}x equity/yr; trades/yr {len(t) / yrs:.0f}')
    t['stopq'] = pd.qcut(t.stop_pct, 4)
    print('   friction R by stop% quartile', t.groupby('stopq', observed=True).apply(lambda x: (x.fee_R + x.slip_R).mean()).round(3).to_dict())
    short = t[t.hold_sessions <= 5]
    print(f'   trades held <=5 sessions: {len(short)} ({len(short) / len(t):.0%}), their friction {(short.fee_R + short.slip_R).sum():.1f}R of total {(t.fee_R + t.slip_R).sum():.1f}R, their net R sum {short.r_net.sum():.1f}')
    # ---- Q5
    e['month'] = e.date.dt.to_period('M')
    sig = s.assign(month=s.date.dt.to_period('M')).groupby('month').size()
    mon = e.groupby('month').agg(inv=('invested_pct', 'mean'), pos=('open_positions', 'mean'), reg_on=('index_regime_on', lambda x: (x.astype(str).str.lower() == 'true').mean()))
    mon['signals'] = sig.reindex(mon.index).fillna(0)
    mon['taken'] = t.assign(month=t.entry_date.dt.to_period('M')).groupby('month').size().reindex(mon.index).fillna(0)
    print(f"Q5 sessions invested <10%: {(e.invested_pct < 10).mean():.0%}, >90%: {(e.invested_pct > 90).mean():.0%}; regime-on sessions {mon.reg_on.mean():.0%}")
    print('   months with 0 signals', (mon.signals == 0).sum(), 'of', len(mon), '; corr(monthly invested, regime_on)', mon[['inv', 'reg_on']].corr().iloc[0, 1].round(2))
    lo = mon[mon.inv < 25]; hi = mon[mon.inv >= 75]
    print(f'   low-invested months (<25%): {len(lo)}, avg regime-on {lo.reg_on.mean():.0%}, avg signals {lo.signals.mean():.1f}; high (>=75%): {len(hi)}, regime-on {hi.reg_on.mean():.0%}, signals {hi.signals.mean():.1f}')
    e['reg'] = e.index_regime_on.astype(str).str.lower() == 'true'
    print(f"   invested when regime on {e[e.reg].invested_pct.mean():.0f}% / off {e[~e.reg].invested_pct.mean():.0f}%")
    capref = f[f.reason.isin(['size_zero_cash', 'size_below_min', 'max_positions'])]
    print(f'   capacity refusals {len(capref)} on {capref.date.nunique()} days vs {len(t)} trades; refusals per month top:', capref.groupby(capref.date.dt.to_period("M")).size().sort_values().tail(4).to_dict())
    # ---- Q6
    t['n5_vs_sma50'] = [100 * (n5.asof(d - pd.Timedelta(days=1)) / n5_sma50.asof(d - pd.Timedelta(days=1)) - 1) for d in t.entry_date]
    t['n5_above200'] = [n5.asof(d - pd.Timedelta(days=1)) > n5_sma200.asof(d - pd.Timedelta(days=1)) for d in t.entry_date]
    t['brq'] = pd.cut(t.breadth_pct, [0, 40, 50, 60, 70, 101])
    print('Q6 by breadth:', t.groupby('brq', observed=True).agg(n=('r_net', 'size'), exp=('r_net', 'mean'), win=('r_net', lambda x: (x > 0).mean())).round(2).T.to_dict())
    t['n5q'] = pd.cut(t.n5_vs_sma50, [-50, 1, 2, 4, 50])
    print('   by NIFTY500 % above SMA50:', t.groupby('n5q', observed=True).agg(n=('r_net', 'size'), exp=('r_net', 'mean')).round(2).T.to_dict())
    print('   by NIFTY500 above SMA200:', t.groupby('n5_above200').agg(n=('r_net', 'size'), exp=('r_net', 'mean')).round(2).T.to_dict())
    # ---- Q7 fill sanity
    bad = []
    for _, r in t.iterrows():
        g, i0 = P.locate(r.instrument_id, r.entry_date)
        F, how = find_f(g, i0, r.entry_price / (1 + SLIP), r.initial_stop)
        px = r.price / F
        o, h, l = g.o[i0], g.h[i0], g.l[i0]
        bad.append(dict(trade_id=r.trade_id, how=how, outside=(px > h * 1.0005) or (px < l * 0.9995), gap_above=o > px * 1.0005,
                        open_over=(o / px - 1) * 100, sameday=r.hold_sessions == 0, prev_c=g.c[i0 - 1] / F, piv=px,
                        prev_above=g.c[i0 - 1] > px * 1.0005, r=r.r_net))
    b = pd.DataFrame(bad)
    print(f'Q7 fills outside the day range: {b.outside.sum()}; entries where the open was already above the fill (gap over pivot): {b.gap_above.sum()} '
          f'(avg open {b[b.gap_above].open_over.mean():.2f}% above fill; their R {b[b.gap_above].r.mean():.2f} vs others {b[~b.gap_above].r.mean():.2f}); '
          f'prior close already above the fill level: {b.prev_above.sum()}; exits on entry day: {b.sameday.sum()}; scale via stop-multi: {(b.how == "stop_multi").sum()}')
    print('   max_positions refusals by open_positions_at_entry', f[f.reason == 'max_positions'].open_positions_at_entry.value_counts().sort_index().to_dict())
    print('   by_regime from run.json', {k: v['trades'] for k, v in json.load(open(f'{RUNS}/{run}/run.json'))['breakdowns']['by_regime'].items()},
          'funnel regime_off_nights', json.load(open(f'{RUNS}/{run}/run.json'))['funnel'].get('regime_off_nights'))
# NIFTY 500 forward 60-session return by regime state, 2016-2024
d = pd.DataFrame({'c': n5, 'on': n5 > n5_sma50}).loc['2016':'2024']
d['f60'] = d.c.shift(-60) / d.c - 1
print('NIFTY500 fwd 60-session return when regime on/off (2016-24):', d.groupby('on').f60.agg(['mean', 'count']).round(3).to_dict())
