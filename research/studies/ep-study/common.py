import numpy as np, pandas as pd
C = '/data/workspace/research/ep-study/cache'
COST = 0.003          # round trip, fraction of entry
HOLD_MAX = 60
import os
LIQ = float(os.environ.get('EP_LIQ', 1e8))   # Rs 10 cr ADV20 turnover (EP_LIQ=5e7 for Rs 5 cr)
RULES = ('sma10', 'sma20', 'hold60', 'time20', 'partial')
RISK_FLOOR = 0.01      # 1% minimum stop distance for R


def load_panel():
    p = pd.read_parquet(f'{C}/panel.parquet')
    assert p.d.max() <= pd.Timestamp('2024-12-31')
    ix = pd.read_parquet(f'{C}/nifty500.parquet'); ix['d'] = pd.to_datetime(ix.d)
    ix['sma200'] = ix.c.rolling(200).mean()
    ix['ixreg'] = (ix.c > ix.sma200).astype(float).where(ix.sma200.notna())
    ix['ixreg_prev'] = ix.ixreg.shift(1)
    # group by the HAT chain id (links ISIN changes); keep the raw instrument id for reference
    p['raw_iid'] = p.iid; p['iid'] = p.cid
    p = p.sort_values(['iid', 'd']).drop_duplicates(['iid', 'd'], keep='last').reset_index(drop=True)
    p = p.merge(ix[['d', 'c', 'ixreg_prev']].rename(columns={'c': 'ixc', 'ixreg_prev': 'regime'}), on='d', how='left')
    p['ixc'] = p.groupby('iid').ixc.transform(lambda s: s.ffill())
    g = p.groupby('iid', sort=False)
    p['tpos'] = g.cumcount()
    p['adv20'] = g.tv.transform(lambda s: s.shift(1).rolling(20, min_periods=15).mean())
    advv = g.vadj.transform(lambda s: s.shift(1).rolling(20, min_periods=15).mean())
    p['vr'] = p.vadj / advv                            # full-day volume / ADV20 (known at close)
    p['ret63'] = g.ac.shift(1) / g.ac.shift(64) - 1    # to previous close
    p.loc[p.tpos < 64, 'ret63'] = np.nan
    p['neg63'] = p.ret63.abs() <= 0.30
    p['sma10'] = g.ac.transform(lambda s: s.rolling(10).mean())
    p['sma20'] = g.ac.transform(lambda s: s.rolling(20).mean())
    p['gap'] = p.ao / g.ac.shift(1) - 1               # adjusted open / adjusted previous close
    p['gap_raw'] = p.o / p.pc - 1
    # corporate-action ex-date: NSE prev_close is the previous RAW close, so on an ex-date the raw day return
    # c/pc differs from the adjusted one ac/ac[-1] (splits, bonuses, rights, demergers, larger dividends)
    p['exdate'] = ((p.c / p.pc) / (p.ac / g.ac.shift(1)) - 1).abs() > 0.005
    p.loc[p.tpos == 0, 'gap'] = np.nan
    p['green'] = p.c > p.o
    p['locked'] = p.h == p.l                           # frozen all day (circuit): untradeable
    p['risk_open'] = 1 - p.l / p.o
    p['risk_close'] = 1 - p.l / p.c
    p['year'] = p.d.dt.year
    p['earn_cov'] = p.d >= pd.Timestamp('2020-04-16')   # result timestamps start here
    p['elig'] = p.member & (p.d >= '2016-01-01') & (p.adv20 >= LIQ) & p.ret63.notna() & p.pc.gt(0) & ~p.exdate & p.gap.notna()
    return p, ix


def simulate(arr, t, E, S, rule, start=1):
    """Exit after entry at E (adjusted) on session t, stop S. Checks from t+start.
    rule: 'sma10' (stop; close<SMA10 from day 3; 60d cap), 'sma20' (same with SMA20), 'hold60' (stop only; exit close t+60),
    'time20' (stop; exit close t+20),
    'partial' (1/3 at close t+3, stop->entry for the rest, close<SMA10 from day 3; 60d cap).
    Returns (gross return fraction, holding sessions, truncated, stopped)."""
    ao, al, ac = arr['ao'], arr['al'], arr['ac']
    s10 = arr['sma20'] if rule == 'sma20' else arr['sma10']
    n = len(ac); cap = 20 if rule == 'time20' else HOLD_MAX
    w, banked, stop = 1.0, 0.0, S
    for j in range(t + start, min(n, t + cap + 1)):
        if ao[j] <= stop:
            return banked + w * (ao[j] / E - 1), j - t, False, stop == S
        if al[j] <= stop:
            return banked + w * (stop / E - 1), j - t, False, stop == S
        k = j - t
        if rule == 'partial' and k == 3:
            banked += (1 / 3) * (ac[j] / E - 1); w = 2 / 3; stop = max(stop, E)
        if rule in ('sma10', 'sma20', 'partial') and k >= 3 and ac[j] < s10[j]:
            return banked + w * (ac[j] / E - 1), k, False, False
        if k == cap:
            return banked + w * (ac[j] / E - 1), k, False, False
    j = min(n, t + cap + 1) - 1
    return banked + w * (ac[j] / E - 1), j - t, True, False


def fwd_stats(arr, t, E, S, ent, start=1):
    ac, al, ixc = arr['ac'], arr['al'], arr['ixc']
    n = len(ac); out = {f'{ent}_E': E, f'{ent}_S': S}
    risk = (E - S) / E
    out[f'{ent}_risk'] = risk
    risk = max(risk, RISK_FLOOR)   # R denominator floor (open==low days give ~0 risk)
    for h in (5, 10, 20, 60):
        if t + h < n:
            out[f'{ent}_f{h}'] = ac[t + h] / E - 1 - COST
            out[f'{ent}_x{h}'] = out[f'{ent}_f{h}'] - (ixc[t + h] / ixc[t] - 1)   # excess vs NIFTY 500 (close-to-close index)
            out[f'{ent}_hit{h}'] = bool((al[t + start:t + h + 1] <= S).any())
    for rule in RULES:
        r, hold, trunc, stopped = simulate(arr, t, E, S, rule, start)
        out[f'{ent}_{rule}'] = r - COST
        out[f'{ent}_{rule}_R'] = (r - COST) / risk
        out[f'{ent}_{rule}_hold'] = hold; out[f'{ent}_{rule}_trunc'] = trunc; out[f'{ent}_{rule}_stop'] = stopped
    return out
