"""Per-fold CAGR, max DD, invested share and TRI for engine run folders. Usage: folds.py label=run_id ..."""
import sys, pandas as pd
R = "/data/workspace/hat-data-isin/backtests/runs"
FOLDS = [("2016-18", "2016", "2018"), ("2019-21", "2019", "2021"), ("2022-24", "2022", "2024"), ("all", "2016", "2024")]
def stats(s):
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    dd = (s / s.cummax() - 1).min()
    return cagr * 100, dd * 100
rows = []
for arg in sys.argv[1:]:
    label, rid = arg.split("=")
    e = pd.read_csv(f"{R}/{rid}/equity.csv", parse_dates=["date"]).set_index("date")
    for name, a, b in FOLDS:
        x = e.loc[a:b]
        c, d = stats(x.equity); tc, td = stats(x.benchmark_tri)
        rows.append(dict(run=label, fold=name, cagr=round(c, 1), dd=round(d, 1), mar=round(c / -d, 2) if d else None,
                         inv=round(x.invested_pct.mean(), 0), tri=round(tc, 1), excess=round(c - tc, 1)))
print(pd.DataFrame(rows).pivot(index="run", columns="fold", values=["cagr", "dd", "excess", "inv"]).round(1).to_string())
