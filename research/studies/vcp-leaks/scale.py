"""Engine run CSV prices are adjusted with every stored factor, including ones after 2024 that this
cache leaves out. Find the per-trade constant F (engine price = my adjusted price * F):
F must put the pre-slippage fill price inside the entry day's range, and the initial stop is 0.5%
below a low of the base (a prior low), which pins F exactly."""
import numpy as np

def find_f(g, i0, fill_px, stop, lookback=130):
    h, l = g['h'].values, g['l'].values
    lo, hi = fill_px / h[i0] * 0.999, fill_px / l[i0] * 1.001
    if lo <= 1 <= hi:
        # still prefer exact: check stop matches a prior low with F=1
        return 1.0, 'range'
    cands = []
    for j in range(max(0, i0 - lookback), i0 + 1):
        f = stop / (0.995 * l[j])
        if lo <= f <= hi:
            cands.append(f)
    if cands:
        f = float(np.median(cands))
        return f, 'stop' if (max(cands) - min(cands)) / f < 0.002 else 'stop_multi'
    return float(fill_px / ((h[i0] + l[i0]) / 2)), 'mid'
