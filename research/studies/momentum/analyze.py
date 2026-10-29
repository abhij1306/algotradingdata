"""Grid summary, robust pick, and sensitivity runs (tax, 2x costs, full reweight, lagged
membership) for the momentum study. Reads grid_results.csv / benchmarks.csv from momentum.py."""
import json
import sys

import numpy as np
import pandas as pd

import momentum as M

HERE = M.HERE
pd.set_option("display.width", 250)

df = pd.read_csv(HERE / "grid_results.csv")
bm = pd.read_csv(HERE / "benchmarks.csv").set_index("name")
folds = [f[0] for f in M.FOLDS]
for f in folds:
    df[f"x_{f}"] = df[f"cagr_{f}"] - bm.loc["NIFTY 500 TRI", f"cagr_{f}"]
df["min_fold_excess"] = df[[f"x_{f}" for f in folds]].min(axis=1)
df["folds_beaten"] = (df[[f"x_{f}" for f in folds]] > 0).sum(axis=1)

out = {}
cols = ["cagr", "maxdd", "mar", "sharpe", "worst_year", "turnover", "min_fold_excess", "folds_beaten"]
out["grid_median"] = df[cols].median().round(4).to_dict()
out["grid_best_cagr"] = df.sort_values("cagr").iloc[-1][["name"] + cols].to_dict()
out["share_beating_n500_all_folds"] = float((df.folds_beaten == 3).mean())
out["share_beating_n500_full"] = float((df.cagr > bm.loc["NIFTY 500 TRI", "cagr"]).mean())
by = {}
for k in ("rank", "n", "freq", "buffer", "mfilter"):
    by[k] = df.groupby(k)[cols].median().round(4)
print(json.dumps(out, indent=1, default=str))
for k, v in by.items():
    print(f"\n-- median by {k}\n{v.to_string()}")

# Neighbourhood score: a cell's median MAR / min fold excess over its one-step neighbours
# (same ranking + mfilter; N +-1 step, other freq, other buffer).
ns = [10, 20, 30]


def neighbours(r):
    m = df[(df["rank"] == r["rank"]) & (df.mfilter == r.mfilter)]
    a = m[(m.n == r.n) & ((m.freq != r.freq) ^ (m.buffer != r.buffer))]
    i = ns.index(r.n)
    b = m[m.n.isin([ns[j] for j in (i - 1, i + 1) if 0 <= j < 3]) & (m.freq == r.freq) & (m.buffer == r.buffer)]
    return pd.concat([a, b])


df["nb_med_mar"] = [neighbours(r).mar.median() for _, r in df.iterrows()]
df["nb_min_fold_excess"] = [neighbours(r).min_fold_excess.median() for _, r in df.iterrows()]
df["robust"] = df[["min_fold_excess", "nb_min_fold_excess"]].min(axis=1)
show = ["name", "cagr", "maxdd", "mar", "sharpe", "worst_year", "turnover", "cagr_2016-2018", "cagr_2019-2021",
        "cagr_2022-2024", "min_fold_excess", "nb_med_mar", "nb_min_fold_excess"]
print("\n-- top 12 by robustness (min of own and neighbourhood-median worst-fold excess vs NIFTY 500 TRI)")
print(df.sort_values("robust", ascending=False)[show].head(12).round(3).to_string())
df.to_csv(HERE / "grid_results_scored.csv", index=False)

if len(sys.argv) > 1:
    pick = M.Cfg(*json.loads(sys.argv[1]))
    ctx = M.Ctx()
    cr = pd.Series(ctx.cash_ret, index=ctx.dates)
    sens = {}

    def summ(res, label):
        m = M.metrics(res["equity"], cr)
        f = M.fold_metrics(res["equity"], cr)
        sens[label] = dict(cagr=m["cagr"], maxdd=m["maxdd"], mar=m["mar"], sharpe=m["sharpe"],
                           worst_year=m["worst_year"], turnover=M.turnover(res),
                           **{f"cagr_{k}": v["cagr"] for k, v in f.items()},
                           **{f"y{y}": v for y, v in m["years"].items()})
        return m

    base = M.run(ctx, pick, tax=True)
    summ(M.run(ctx, pick), "pre-tax")
    summ(base, "after tax (FY, STCG 20% / LTCG 12.5% >1.25L)")
    rl = base["realized"]
    lt_share = sum(r[1] for r in rl if r[2] and r[1] > 0) / max(1, sum(r[1] for r in rl if r[1] > 0))
    print("tax paid", round(base["tax_paid"]), "LT share of gross gains", round(lt_share, 3), base["tax_log"])
    M.COST = 2 * (0.0012 + 0.0010)
    summ(M.run(ctx, pick), "2x costs (0.44%/side)")
    M.COST = 0.0012 + 0.0010
    summ(M.run(ctx, M.Cfg(pick.rank, pick.n, pick.freq, pick.buffer, pick.mfilter, True)), "full equal-weight reweight")
    summ(M.run(ctx, M.Cfg(pick.rank, pick.n, pick.freq, pick.buffer, not pick.mfilter)), "market filter flipped")
    # execution lag check: trade at the open two sessions after the decision
    saved = ctx.rebal[pick.freq]
    idx = {d: i for i, d in enumerate(ctx.dates)}
    ctx.rebal[pick.freq] = [ctx.dates[idx[d] + 1] for d in saved if idx[d] + 2 < len(ctx.dates)]
    ctx.scores = {k: np.vstack([v[:1], v[:-1]]) for k, v in ctx.scores.items()}  # signal still from day d
    ctx.mkt_on = np.concatenate([ctx.mkt_on[:1], ctx.mkt_on[:-1]])
    summ(M.run(ctx, pick), "one extra session of execution delay")
    s = pd.DataFrame(sens).T
    print(s.round(4).to_string())
    s.to_csv(HERE / "sensitivity.csv")
    # trade sanity: biggest round trips
    tr = pd.DataFrame(rl, columns=["sold", "gain", "lt", "j", "bought", "cost"])
    tr["sym"] = [ctx.sym[ctx.cols[j]] for j in tr.j]
    tr["ret"] = tr.gain / tr.cost
    g = tr.groupby(["sym", "bought"]).agg(sold=("sold", "max"), gain=("gain", "sum"), cost=("cost", "sum"))
    g["ret"] = g.gain / g.cost
    g = g.sort_values("ret")
    print("\n-- worst / best round trips\n", pd.concat([g.head(8), g.tail(12)]).round(3).to_string())
    print("round trips", len(g), "win rate", round((g.ret > 0).mean(), 3), "median hold days",
          (g.sold - g.index.get_level_values(1)).dt.days.median())
    g.to_csv(HERE / "pick_round_trips.csv")
    eq = base["equity"]
    pd.DataFrame({"pick_after_tax": eq}).to_parquet(M.DATA / "pick_curve.parquet")
