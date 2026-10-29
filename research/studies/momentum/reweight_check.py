"""Neighbourhood check of the full equal-weight reweight option (risk-adjusted ranking, no market filter)."""
import itertools
import pandas as pd
import momentum as M

ctx = M.Ctx()
cr = pd.Series(ctx.cash_ret, index=ctx.dates)
rows = []
for n, freq, buf, rw in itertools.product((10, 20, 30), ("monthly", "fortnightly"), (True, False), (True,)):
    cfg = M.Cfg("riskadj", n, freq, buf, False, rw)
    res = M.run(ctx, cfg)
    m = M.metrics(res["equity"], cr)
    f = M.fold_metrics(res["equity"], cr)
    rows.append(dict(name=cfg.name, cagr=m["cagr"], maxdd=m["maxdd"], mar=m["mar"], sharpe=m["sharpe"],
                     worst_year=m["worst_year"], turnover=M.turnover(res), **{k: v["cagr"] for k, v in f.items()}))
d = pd.DataFrame(rows)
d.to_csv(M.HERE / "reweight_check.csv", index=False)
print(d.round(3).to_string())
