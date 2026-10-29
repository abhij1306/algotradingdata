"""Per-trade replay helpers on the engine's cap-adjusted daily bars (cache/adj.parquet).
Prices from run CSVs are raw; they are mapped to adjusted space with k = adj_close/raw_close on
the entry date, so a split during the trade is handled by the adjusted series."""
import numpy as np, pandas as pd
from common import bars

SLIP = 0.002  # 20 bps per side, as the runs

class Panel:
    def __init__(self):
        b = bars()
        self.b = b
        self.by_id = {i: g.reset_index(drop=True) for i, g in b.groupby('instrument_id', sort=False)}
        self.sym = b[['symbol', 'date', 'instrument_id']].drop_duplicates(['symbol', 'date'])
        for g in self.by_id.values():
            c = g['c']
            for n in (10, 20, 30, 50, 100, 150, 200):
                g[f'sma{n}'] = c.rolling(n).mean()
            tr = np.maximum(g['h'] - g['l'], np.maximum((g['h'] - c.shift()).abs(), (g['l'] - c.shift()).abs()))
            g['atr14'] = tr.rolling(14).mean()
            g['atr21'] = tr.rolling(21).mean()
            for n in (10, 20):
                g[f'swing{n}'] = g['l'].shift(1).rolling(n).min()  # lowest low of the n sessions before
            g['k'] = g['c'] / g['raw_c']

    def iid(self, symbol, date):
        m = self.sym[(self.sym.symbol == symbol) & (self.sym.date == date)]
        return None if m.empty else m.instrument_id.iloc[0]

    def series(self, iid):
        return self.by_id.get(iid)

    def locate(self, iid, date):
        g = self.by_id.get(iid)
        if g is None:
            return None, None
        pos = g.index[g.date == date]
        return g, (int(pos[0]) if len(pos) else None)


def fwd_r(g, i0, entry, stop, horizons=(20, 60)):
    """R at the close `h` sessions after entry day i0 (gross), -1 if a low reaches stop first
    (checked from the session after entry). Also max favourable R within 60 sessions and the
    session index of the stop hit."""
    risk = entry - stop
    out = {}
    lows = g['l'].values; closes = g['c'].values; highs = g['h'].values
    n = len(g)
    hit = None
    for j in range(i0 + 1, min(n, i0 + max(horizons) + 1)):
        if lows[j] <= stop:
            hit = j; break
    for h in horizons:
        j = i0 + h
        if j >= n:
            out[f'r{h}'] = np.nan
        elif hit is not None and hit <= j:
            out[f'r{h}'] = -1.0
        else:
            out[f'r{h}'] = (closes[j] - entry) / risk
    end = min(n, i0 + 61)
    out['mfe60'] = (highs[i0:end].max() - entry) / risk if end > i0 else np.nan
    out['stop_hit_idx'] = hit
    return out


def replay(g, i0, entry, stop, rule, end_date=None, max_hold=None):
    """Replay one exit rule from entry session i0 (adjusted prices). Returns (exit_idx, exit_px, reason).
    Hard stop (intraday, gap fills at the open) always on, from the session after entry.
    Close rules are decided on the close (entry day included, as the engine's days_held 0).
    rule: dict with keys
      sma: int | None           close < SMA(n) exit
      sma_grace_r: float        SMA exit only once peak close >= entry + x R (0 = always)
      sma_grace_days: int       SMA exit only after this many sessions
      swing: int | None         close < lowest low of the n prior sessions
      chand: (atr_n, mult)|None close < highest high since entry - mult*ATR
      pct_trail: float|None     close < (1-x) * highest close since entry
      be_at_r: float|None       stop -> entry once high >= entry + x R
      stop_mult: float          stop distance multiplier (wider stop)
      time: (days, min_r)|None  exit at close after `days` if close < entry + min_r*R
    """
    risk0 = entry - stop
    stop = entry - risk0 * rule.get('stop_mult', 1.0)
    risk = entry - stop
    cur_stop = stop
    o = g['o'].values; h = g['h'].values; l = g['l'].values; c = g['c'].values
    dates = g['date'].values
    n = len(g)
    peak_h = h[i0]; peak_c = c[i0]
    smacol = g[f"sma{rule['sma']}"].values if rule.get('sma') else None
    swcol = g[f"swing{rule['swing']}"].values if rule.get('swing') else None
    ch = rule.get('chand'); atr = g[f'atr{ch[0]}'].values if ch else None
    last = n - 1
    if end_date is not None:
        idx = np.searchsorted(dates, np.datetime64(end_date), side='right') - 1
        last = min(last, idx)
    for j in range(i0, last + 1):
        if j > i0:
            if l[j] <= cur_stop:
                px = min(o[j], cur_stop)
                return j, px * (1 - SLIP), 'stop', risk
        peak_h = max(peak_h, h[j]); peak_c = max(peak_c, c[j])
        held = j - i0
        why = None
        if smacol is not None and not np.isnan(smacol[j]) and c[j] < smacol[j]:
            ok_r = ('sma_grace_r' not in rule) or peak_c >= entry + rule['sma_grace_r'] * risk
            ok_d = held > rule.get('sma_grace_days', -1)
            if ok_r and ok_d:
                why = 'sma'
        if why is None and swcol is not None and not np.isnan(swcol[j]) and c[j] < swcol[j]:
            why = 'swing'
        if why is None and ch and not np.isnan(atr[j]) and c[j] < peak_h - ch[1] * atr[j]:
            why = 'chand'
        if why is None and rule.get('pct_trail') and c[j] < (1 - rule['pct_trail']) * peak_c:
            why = 'pct'
        if why is None and rule.get('time') and held >= rule['time'][0] and c[j] < entry + rule['time'][1] * risk and held == rule['time'][0]:
            why = 'time'
        if why is None and max_hold and held >= max_hold:
            why = 'max_hold'
        if why:
            return j, c[j] * (1 - SLIP), why, risk
        if rule.get('be_at_r') and h[j] >= entry + rule['be_at_r'] * risk:
            cur_stop = max(cur_stop, entry)
    return last, c[last] * (1 - SLIP), 'period_end', risk
