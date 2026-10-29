"""Q2/Q3: replay alternative stops/exits on the same entries (taken trades, and separately all
capacity-refused signals as a second, larger sample of equal-quality entries). Gross R includes
20 bps slippage per side; net R also takes the runs' statutory fee rate (0.115% of notional per side)."""
import numpy as np, pandas as pd
from common import *
from sim import Panel, replay, SLIP
from scale import find_f
FEE = 0.00115
RULES = {
    'base sma50+swing20': dict(sma=50, swing=20),
    'sma50 only': dict(sma=50),
    'swing20 only': dict(swing=20),
    'sma20': dict(sma=20),
    'sma10': dict(sma=10),
    'sma100': dict(sma=100),
    'swing10': dict(swing=10),
    'sma50 after +1R peak, +swing20': dict(sma=50, sma_grace_r=1.0, swing=20),
    'sma50 after 10 sess, +swing20': dict(sma=50, sma_grace_days=10, swing=20),
    'sma50 after +2R, no swing': dict(sma=50, sma_grace_r=2.0),
    'chandelier 3xATR21': dict(chand=(21, 3.0)),
    'chandelier 4xATR21': dict(chand=(21, 4.0)),
    'chandelier 5xATR21': dict(chand=(21, 5.0)),
    'pct trail 15%': dict(pct_trail=0.15),
    'pct trail 20%': dict(pct_trail=0.20),
    'pct trail 25%': dict(pct_trail=0.25),
    'base + BE at 2R': dict(sma=50, swing=20, be_at_r=2.0),
    'base, stop x1.5': dict(sma=50, swing=20, stop_mult=1.5),
    'base, stop x2': dict(sma=50, swing=20, stop_mult=2.0),
    'sma50+swing20 after +1R, stop x1.5': dict(sma=50, sma_grace_r=1.0, swing=20, stop_mult=1.5),
    'stop only, 60-sess hold': dict(),
}
MAXHOLD = {'stop only, 60-sess hold': 60}
P = Panel()
entries = []
for run, label, end in ((R16, '2016-21', '2021-12-31'), (R22, '2022-24', '2024-12-31')):
    t = load(run, 'trades')
    for _, r in t.iterrows():
        g, i0 = P.locate(r.instrument_id, r.entry_date)
        F, _ = find_f(g, i0, r.entry_price / (1 + SLIP), r.initial_stop)
        entries.append(dict(run=label, sample='taken', key=(r.instrument_id, i0), e=r.entry_price / F, s=r.initial_stop / F, end=end, eng_r=r.r_net))
    f = load(run, 'refusals')
    f = f[f.reason.isin(['size_zero_cash', 'size_below_min', 'max_positions'])]
    for _, r in f.iterrows():
        iid = P.iid(r.symbol, r.date)
        g, i0 = P.locate(iid, r.date) if iid else (None, None)
        if i0 is None:
            continue
        F, _ = find_f(g, i0, r.would_be_entry, r.would_be_stop)
        entries.append(dict(run=label, sample='refused', key=(iid, i0), e=r.would_be_entry * (1 + SLIP) / F, s=r.would_be_stop / F, end=end, eng_r=np.nan))
rows = []
for k, en in enumerate(entries):
    g = P.series(en['key'][0]); i0 = en['key'][1]
    for name, rule in RULES.items():
        j, px, why, risk = replay(g, i0, en['e'], en['s'], rule, end_date=en['end'], max_hold=MAXHOLD.get(name))
        gross = (px - en['e']) / risk
        net = gross - FEE * (en['e'] + px) / risk
        rows.append(dict(i=k, run=en['run'], sample=en['sample'], rule=name, r_gross=gross, r_net=net, hold=j - i0, why=why, eng_r=en['eng_r']))
df = pd.DataFrame(rows)
df.to_parquet('q3_replay.parquet', index=False)
def summ(x):
    r = x.r_net.sort_values()
    return pd.Series(dict(n=len(x), exp_R=r.mean(), med=r.median(), win=(r > 0).mean(), sum_R=r.sum(),
                          sum_ex_top5=r.iloc[:-5].sum(), p95=r.quantile(.95), hold=x.hold.mean(),
                          R_per_100sess=100 * r.sum() / max(1, x.hold.clip(lower=1).sum())))
pd.set_option('display.width', 250)
for samp in ('taken', 'refused'):
    for run in ('2016-21', '2022-24'):
        x = df[(df['sample'] == samp) & (df.run == run)]
        print(f'== {samp} {run}')
        print(x.groupby('rule', sort=False).apply(summ).round(3).to_string())
