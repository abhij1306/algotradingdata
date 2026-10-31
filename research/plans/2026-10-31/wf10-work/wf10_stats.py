"""wf10: per-year and walk-forward stats from finished run folders (read-only, plain python3).
usage: wf10_stats.py RUNS_DIR LABEL=RUN_ID ...  -> JSON on stdout
Per run: run.json headline metrics; per calendar year (from equity.csv): return, NIFTY 500 TRI
return, excess, in-year max DD (strategy and TRI), avg invested %.
Walk-forward (criterion fixed before results): for each test year 2015..2021 pick the config with
the highest Calmar (CAGR / max DD) over the prior 3 calendar years; report its test-year excess.
"""
import csv, json, sys
from pathlib import Path

runs = Path(sys.argv[1]); out = {}
KEYS = ["invested_pct", "avg_open_positions", "avg_position_size_pct", "zero_position_days_pct",
        "cagr_pct", "benchmark_cagr_pct", "max_dd_pct", "avg_dd_pct", "longest_dd_sessions",
        "sharpe", "sortino", "mar", "cagr_per_invested_pct", "profit_factor", "win_pct",
        "avg_win_pct", "avg_loss_pct", "payoff_ratio_pct", "payoff_ratio_r", "expectancy_r",
        "mfe_capture", "cagr_ex_top5_trades_pct", "top5_trades_pnl_share_pct", "fees", "trades"]

def maxdd(xs):
    peak, dd = xs[0], 0.0
    for x in xs:
        peak = max(peak, x); dd = max(dd, 1 - x / peak)
    return dd * 100

for arg in sys.argv[2:]:
    label, rid = arg.split("=")
    d = next(runs.glob(rid + "*"))
    m = json.load(open(d / "run.json"))["metrics"]
    rows = list(csv.DictReader(open(d / "equity.csv")))
    years = {}
    prev_e = float(rows[0]["equity"]); prev_b = float(rows[0]["benchmark_tri"])
    by = {}
    for r in rows:
        by.setdefault(r["date"][:4], []).append(r)
    for y, rs in sorted(by.items()):
        e = [float(r["equity"]) for r in rs]; b = [float(r["benchmark_tri"]) for r in rs]
        ret = (e[-1] / prev_e - 1) * 100; bret = (b[-1] / prev_b - 1) * 100
        years[y] = {"ret": round(ret, 2), "tri": round(bret, 2), "excess": round(ret - bret, 2),
                    "dd": round(maxdd([prev_e] + e), 2), "tri_dd": round(maxdd([prev_b] + b), 2),
                    "inv": round(sum(float(r["invested_pct"]) for r in rs) / len(rs), 1)}
        prev_e, prev_b = e[-1], b[-1]
    out[label] = {"run_id": d.name, "metrics": {k: m.get(k) for k in KEYS}, "years": years}

def calmar(label, ys):
    g = 1.0; dd = 0.0
    for y in ys:
        g *= 1 + out[label]["years"][y]["ret"] / 100; dd = max(dd, out[label]["years"][y]["dd"])
    cagr = (g ** (1 / len(ys)) - 1) * 100
    return cagr / dd if dd else 0.0

cands = [l for l in out if l != "ref"]; wf = []
for t in range(2015, 2022):
    prior = [str(t - 3), str(t - 2), str(t - 1)]
    if not all(all(p in out[l]["years"] for p in prior) for l in cands):
        continue
    pick = max(cands, key=lambda l: calmar(l, prior))
    wf.append({"test": t, "pick": pick, **out[pick]["years"][str(t)],
               "base_excess": out["c0"]["years"][str(t)]["excess"] if "c0" in out else None})
out["_walk_forward"] = wf
print(json.dumps(out, indent=1))
