"""Cross-sectional momentum rotation on point-in-time NIFTY 500 members, 2016-01-01..2024-12-31.

Research only (not the HAT engine). Inputs from build_tr_panel.py / slim_panel.py:
  data/slim.parquet               total-return adjusted bars (HAT bars_daily view), EQ/BE, <= 2024-12-31
  data/nifty500_members.parquet   PIT NIFTY 500 intervals [from, to) by ISIN chain
  etf/indices.parquet             NIFTY 50 TRI / NIFTY 500 TRI;  etf/liquid_tr.parquet  cash proxy
Rules: decide on the close of the rebalance day with membership as of that day, trade at next
session's open; costs 0.22% per side; cash earns the liquid-fund TR proxy.
"""
from __future__ import annotations

import itertools
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data"
ETF = Path("/data/workspace/hat-data-isin/etf")
END = pd.Timestamp("2024-12-31")
START_DECISION = pd.Timestamp("2015-12-31")  # membership of 2016-01-01 (history start = members from before)
CAPITAL = 1_000_000.0
COST = 0.0012 + 0.0010  # per side: statutory + slippage
ADV_MIN = 10e7  # Rs 10 crore
PRICE_MIN = 50.0
FOLDS = [("2016-2018", "2016-01-01", "2018-12-31"), ("2019-2021", "2019-01-01", "2021-12-31"),
         ("2022-2024", "2022-01-01", "2024-12-31")]


# ----------------------------------------------------------------------------- data
def load():
    d = pd.read_parquet(DATA / "slim.parquet")
    d["date"] = pd.to_datetime(d.date)
    d = d[d.date <= END]
    C = d.pivot(index="date", columns="iid", values="c").sort_index()
    O = d.pivot(index="date", columns="iid", values="o").reindex(C.index)
    RC = d.pivot(index="date", columns="iid", values="rc").reindex(C.index)
    TV = d.pivot(index="date", columns="iid", values="tv").reindex(C.index)
    sym = d.sort_values("date").groupby("iid").symbol.last()
    m = pd.read_parquet(DATA / "nifty500_members.parquet")
    m["effective_from"] = pd.to_datetime(m.effective_from)
    m["effective_to"] = pd.to_datetime(m.effective_to)
    idx = pd.read_parquet(ETF / "indices.parquet")
    idx["date"] = pd.to_datetime(idx.date)
    idx = idx[idx.date <= END]
    idx["close"] = idx.close.astype(float)
    I = idx.pivot(index="date", columns="index", values="close")
    liq = pd.read_parquet(ETF / "liquid_tr.parquet")
    liq["date"] = pd.to_datetime(liq.date)
    liq = liq[liq.date <= END].set_index("date").tr_index.astype(float)
    return C, O, RC, TV, sym, m, I, liq


def membership_matrix(m, dates, cols):
    M = pd.DataFrame(False, index=dates, columns=cols)
    hist0 = m.effective_from.min()
    for r in m.itertuples():
        if r.chain_id not in M.columns:
            continue
        start = pd.Timestamp("1900-01-01") if r.effective_from == hist0 else r.effective_from
        end = r.effective_to if pd.notna(r.effective_to) else pd.Timestamp("2100-01-01")
        M.loc[(dates >= start) & (dates < end), r.chain_id] = True
    return M


# ----------------------------------------------------------------------------- signals
def signals(C, TV):
    Cf = C.ffill(limit=10)
    nobs = C.notna().rolling(252, min_periods=1).sum()
    ok = nobs >= 240
    lr = np.log(Cf).diff()
    vol = lr.rolling(252, min_periods=200).std() * np.sqrt(252)
    r12_1 = Cf.shift(21) / Cf.shift(252) - 1
    r6 = Cf / Cf.shift(126) - 1
    r12 = Cf / Cf.shift(252) - 1
    # many names sit at exactly 1.0 (at the high): round to 1% and break ties by 12-1 return
    hi52 = (Cf / Cf.rolling(252, min_periods=240).max()).round(2) + 1e-5 * (Cf.shift(21) / Cf.shift(252) - 1).clip(-1, 10)
    adv = TV.rolling(20, min_periods=15).mean()

    def z(x):
        mu = x.mean(axis=1)
        sd = x.std(axis=1)
        return x.sub(mu, axis=0).div(sd, axis=0)

    S = {"r12_1": r12_1.where(ok), "r6": r6.where(ok), "hi52": hi52.where(ok), "_r6v": (r6 / vol).where(ok),
         "_r12v": (r12 / vol).where(ok)}
    return S, adv, z


def rebalance_dates(dates, freq):
    s = pd.Series(dates, index=dates)
    s = s[(s >= START_DECISION) & (s < END)]
    month_end = s.groupby([s.dt.year, s.dt.month]).max()
    out = set(month_end)
    if freq == "fortnightly":
        mid = s[s.dt.day <= 15].groupby([s[s.dt.day <= 15].dt.year, s[s.dt.day <= 15].dt.month]).max()
        out |= set(mid)
    out = sorted(d for d in out if d >= START_DECISION and d < dates[-1])
    return out


# ----------------------------------------------------------------------------- simulation
@dataclass(frozen=True)
class Cfg:
    rank: str
    n: int
    freq: str
    buffer: bool
    mfilter: bool
    reweight: bool = False  # True: reset all holdings to equal weight at each rebalance

    @property
    def name(self):
        return (f"{self.rank}|N{self.n}|{self.freq[0].upper()}|{'buf' if self.buffer else 'nobuf'}|"
                f"{'mf' if self.mfilter else 'nomf'}" + ("|rw" if self.reweight else ""))


class Ctx:
    """Everything shared across variants, as numpy arrays on one date x instrument grid."""

    def __init__(self):
        C, O, RC, TV, sym, m, I, liq = load()
        self.dates = C.index
        self.cols = C.columns
        self.sym = sym
        M = membership_matrix(m, self.dates, self.cols)
        S, adv, z = signals(C, TV)
        elig = M & (adv >= ADV_MIN) & (RC.ffill(limit=10) >= PRICE_MIN)
        self.elig = elig.values
        self.scores = {}
        for k in ("r12_1", "r6", "hi52"):
            self.scores[k] = S[k].where(elig).values
        # risk-adjusted (NSE Momentum-style): mean of z-scores of 6m/vol and 12m/vol within the eligible set
        ra = 0.5 * z(S["_r6v"].where(elig)) + 0.5 * z(S["_r12v"].where(elig))
        self.scores["riskadj"] = ra.values
        self.Cf = np.nan_to_num(C.ffill().values)  # mark-to-market (last close carried)
        self.O = O.values
        self.Ob = O.bfill(limit=20).values  # next available open within 20 sessions
        I = I.reindex(self.dates).ffill()
        n500 = I["NIFTY 500 TRI"]
        self.mkt_on = (n500 > n500.rolling(200, min_periods=200).mean()).values
        self.bench = I[["NIFTY 500 TRI", "NIFTY 50 TRI"]]
        liq = liq.reindex(self.dates).ffill()
        self.cash_ret = (liq / liq.shift(1)).fillna(1.0).values
        self.liq = liq
        self.pos = {d: i for i, d in enumerate(self.dates)}
        self.rebal = {f: rebalance_dates(self.dates, f) for f in ("monthly", "fortnightly")}
        self.i0 = self.pos[START_DECISION]


def run(ctx: Ctx, cfg: Cfg, tax: bool = False):
    T, K = ctx.Cf.shape
    shares = np.zeros(K)
    cash = CAPITAL
    lots: dict[int, list] = {}  # col -> [[buy_date, qty, cost_per_share]]
    realized = []  # (date, gain, is_long)
    eq = np.full(T, np.nan)
    traded = np.zeros(T)
    nhold = np.zeros(T)
    invested = np.zeros(T)
    exec_days = {ctx.pos[d] + 1: ctx.pos[d] for d in ctx.rebal[cfg.freq]}
    tax_paid = 0.0
    tax_log = []
    fy_pending = None
    i0 = ctx.i0
    eq[i0] = CAPITAL
    for t in range(i0 + 1, T):
        cash *= ctx.cash_ret[t]
        if tax and ctx.dates[t].month == 4 and ctx.dates[t - 1].month == 3:
            fy_end = ctx.dates[t - 1]
            due, carry = fy_tax(realized, fy_end, fy_pending)
            fy_pending = carry
            cash -= due
            tax_paid += due
            tax_log.append((fy_end.date().isoformat(), round(due)))
        if t in exec_days:
            d = exec_days[t]
            px = np.where(np.isnan(ctx.O[t]), ctx.Ob[t], ctx.O[t])
            px = np.where(np.isnan(px), ctx.Cf[t - 1], px)
            px = np.where(px > 0, px, np.nan)  # never trades again: last close
            held = np.flatnonzero(shares > 0)
            score = ctx.scores[cfg.rank][d]
            target: list[int] = []
            if not cfg.mfilter or ctx.mkt_on[d]:
                valid = np.flatnonzero(~np.isnan(score))
                order = valid[np.argsort(-score[valid], kind="stable")]
                rank = np.full(K, 10**9)
                rank[order] = np.arange(len(order))
                keep_lim = 2 * cfg.n if cfg.buffer else cfg.n
                keep = [j for j in held if rank[j] < keep_lim]
                keep.sort(key=lambda j: rank[j])
                keep = keep[: cfg.n]
                target = list(keep)
                for j in order:
                    if len(target) >= cfg.n:
                        break
                    if j not in target and not np.isnan(ctx.O[t, j]):
                        target.append(j)
            tset = set(target)
            # sells
            for j in held:
                if j not in tset:
                    q = shares[j]
                    val = q * px[j]
                    cash += val * (1 - COST)
                    traded[t] += val
                    realized += close_lots(lots, j, q, px[j] * (1 - COST), ctx.dates[t])
                    shares[j] = 0
            equity = cash + (shares * np.nan_to_num(px)).sum()
            tw = equity / cfg.n if target else 0.0
            if cfg.reweight and target:
                for j in [j for j in held if j in tset]:  # trims first, raise cash
                    excess = shares[j] * px[j] - tw
                    if excess > 0.02 * tw:
                        q = excess / px[j]
                        cash += excess * (1 - COST)
                        traded[t] += excess
                        realized += close_lots(lots, j, q, px[j] * (1 - COST), ctx.dates[t])
                        shares[j] -= q
            buys = {}
            for j in target:
                need = tw - shares[j] * px[j]
                if need > 0.02 * tw and (shares[j] == 0 or cfg.reweight):
                    buys[j] = need
            tot = sum(buys.values()) * (1 + COST)
            scale = min(1.0, cash / tot) if tot > 0 else 0.0
            for j, v in buys.items():
                v *= scale
                q = v / px[j]
                shares[j] += q
                cash -= v * (1 + COST)
                traded[t] += v
                lots.setdefault(j, []).append([ctx.dates[t], q, px[j] * (1 + COST)])
        hv = (shares * ctx.Cf[t]).sum()
        eq[t] = cash + hv
        nhold[t] = (shares > 0).sum()
        invested[t] = hv / eq[t] if eq[t] > 0 else 0
    if tax:  # final FY (Apr-Dec 2024), realized gains only
        due, _ = fy_tax(realized, ctx.dates[-1], fy_pending)
        tax_paid += due
        tax_log.append((ctx.dates[-1].date().isoformat(), round(due)))
        eq[-1] -= due
    s = pd.Series(eq, index=ctx.dates).iloc[i0:]
    return dict(equity=s, traded=pd.Series(traded, index=ctx.dates).iloc[i0:],
                nhold=pd.Series(nhold, index=ctx.dates).iloc[i0:],
                invested=pd.Series(invested, index=ctx.dates).iloc[i0:], tax_paid=tax_paid, tax_log=tax_log,
                realized=realized)


def close_lots(lots, j, q, net_px, when):
    out = []
    book = lots.get(j, [])
    while q > 1e-12 and book:
        lot = book[0]
        take = min(q, lot[1])
        held_days = (when - lot[0]).days
        out.append((when, take * (net_px - lot[2]), held_days > 365, j, lot[0], take * lot[2]))
        lot[1] -= take
        q -= take
        if lot[1] <= 1e-12:
            book.pop(0)
    return out


def fy_tax(realized, fy_end, carry):
    """Indian FY tax on realized equity gains: STCG 20%, LTCG 12.5% above Rs 1.25L; ST losses set off
    against ST then LT gains, LT losses only against LT; net losses carried forward (8 years, ignored)."""
    fy_start = pd.Timestamp(year=fy_end.year - (1 if fy_end.month <= 3 else 0), month=4, day=1)
    st = sum(r[1] for r in realized if fy_start <= r[0] <= fy_end and not r[2])
    lt_ = sum(r[1] for r in realized if fy_start <= r[0] <= fy_end and r[2])
    cst, clt = carry or (0.0, 0.0)  # carried losses (positive numbers)
    if st < 0:
        lt_ += st
        st = 0.0
    # carried ST losses offset ST then LT; carried LT losses offset LT
    use = min(cst, st); st -= use; cst -= use
    use = min(cst, max(lt_, 0)); lt_ -= use; cst -= use
    use = min(clt, max(lt_, 0)); lt_ -= use; clt -= use
    if lt_ < 0:
        clt += -lt_
        lt_ = 0.0
    due = 0.20 * st + 0.125 * max(0.0, lt_ - 125_000)
    return due, (cst, clt)


# ----------------------------------------------------------------------------- metrics
def metrics(eq: pd.Series, cash_ret: pd.Series | None = None):
    eq = eq.dropna()
    yrs = (eq.index[-1] - eq.index[0]).days / 365.25
    cagr = (eq.iloc[-1] / eq.iloc[0]) ** (1 / yrs) - 1
    dd = (eq / eq.cummax() - 1).min()
    r = eq.pct_change().dropna()
    ex = r - (cash_ret.reindex(r.index) - 1 if cash_ret is not None else 0)
    sharpe = ex.mean() / ex.std() * np.sqrt(252) if ex.std() > 0 else np.nan
    ye = eq.groupby(eq.index.year).last()
    ye = pd.concat([pd.Series([eq.iloc[0]], index=[eq.index[0].year - 1]), ye])
    yr = (ye / ye.shift(1) - 1).dropna()
    return dict(cagr=cagr, maxdd=dd, mar=cagr / -dd if dd < 0 else np.nan, sharpe=sharpe,
                worst_year=yr.min(), years=yr)


def fold_metrics(eq, cash_ret):
    out = {}
    for name, a, b in FOLDS:
        prior = eq[eq.index < pd.Timestamp(a)]
        seg = eq[(eq.index >= pd.Timestamp(a)) & (eq.index <= pd.Timestamp(b))]
        if len(prior):
            seg = pd.concat([prior.iloc[-1:], seg])
        out[name] = metrics(seg, cash_ret)
    return out


def turnover(res):
    eq = res["equity"]
    tr = res["traded"]
    yrs = (eq.index[-1] - eq.index[0]).days / 365.25
    return tr.sum() / 2 / eq.mean() / yrs  # one-way annual turnover (x of average equity)


def grid():
    for rank, n, freq, buf, mf in itertools.product(("r12_1", "r6", "riskadj", "hi52"), (10, 20, 30),
                                                    ("monthly", "fortnightly"), (False, True), (False, True)):
        yield Cfg(rank, n, freq, buf, mf)


def main():
    ctx = Ctx()
    cr = pd.Series(ctx.cash_ret, index=ctx.dates)
    rows = []
    curves = {}
    for cfg in grid():
        res = run(ctx, cfg)
        m = metrics(res["equity"], cr)
        f = fold_metrics(res["equity"], cr)
        row = dict(name=cfg.name, rank=cfg.rank, n=cfg.n, freq=cfg.freq, buffer=cfg.buffer, mfilter=cfg.mfilter,
                   cagr=m["cagr"], maxdd=m["maxdd"], mar=m["mar"], sharpe=m["sharpe"], worst_year=m["worst_year"],
                   turnover=turnover(res), avg_hold=res["nhold"].mean(), invested=res["invested"].mean())
        for k, fm in f.items():
            row[f"cagr_{k}"] = fm["cagr"]
            row[f"dd_{k}"] = fm["maxdd"]
        for y, v in m["years"].items():
            row[f"y{y}"] = v
        rows.append(row)
        curves[cfg.name] = res["equity"]
        print(cfg.name, f"{m['cagr']:.3f} {m['maxdd']:.3f}", file=sys.stderr)
    df = pd.DataFrame(rows)
    df.to_csv(HERE / "grid_results.csv", index=False)
    pd.DataFrame(curves).to_parquet(DATA / "grid_curves.parquet")
    # benchmarks
    b = ctx.bench.loc[START_DECISION:]
    brow = []
    for col in b.columns:
        m = metrics(b[col], cr)
        f = fold_metrics(b[col], cr)
        r = dict(name=col, cagr=m["cagr"], maxdd=m["maxdd"], mar=m["mar"], sharpe=m["sharpe"],
                 worst_year=m["worst_year"])
        for k, fm in f.items():
            r[f"cagr_{k}"] = fm["cagr"]
            r[f"dd_{k}"] = fm["maxdd"]
        for y, v in m["years"].items():
            r[f"y{y}"] = v
        brow.append(r)
    liq = ctx.liq.loc[START_DECISION:]
    m = metrics(liq)
    brow.append(dict(name="LIQUID proxy", cagr=m["cagr"], maxdd=m["maxdd"]))
    pd.DataFrame(brow).to_csv(HERE / "benchmarks.csv", index=False)
    print("variants:", len(df))


if __name__ == "__main__":
    main()
