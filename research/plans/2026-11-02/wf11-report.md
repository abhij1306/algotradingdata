# wf11: c1 + point-in-time fundamentals screen, 2016-01..2021-12 (2026-11-02)

m1, main e76516e3 (#357), hat_live fundamentals from #352 (cache only). Configs `wf11-work/configs/`,
run ids `wf11-work/run_ids.txt`, stats `wf11-work/stats.json` (wf10_stats.py). In-sample only.

| run | screen | CAGR | max DD | Sharpe | MAR | PF | trades |
|---|---|---:|---:|---:|---:|---:|---:|
| f0 | none (c1) | 32.7 | 35.2 | 1.55 | 0.93 | 4.00 | 344 |
| f1 | ROCE>=12%, D/E<=1, CFO>0 | 29.8 | 32.2 | 1.44 | 0.92 | 4.37 | 321 |
| f2 | drop dearest 20% by earnings yield | 27.7 | 33.7 | 1.33 | 0.82 | 3.38 | 349 |
| f3 | drop dearest 20% by EBIT/EV | 35.3 | 32.9 | 1.65 | 1.07 | 4.84 | 333 |
| f4 | f1 + f2 | 28.3 | 29.0 | 1.41 | 0.98 | 3.95 | 323 |
| f5 | CFO>0 only | 30.3 | 34.2 | 1.46 | 0.88 | 3.88 | 336 |

NIFTY 500 TRI 15.7% CAGR. All ~99% invested.

Excess vs TRI per year (pp) / in-year DD (TRI DD: 13.8, 4.8, 15.6, 11.5, 38.1, 9.8):

| run | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | DD 2016 | DD 2018 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| f0 | -8.8 | +40.5 | -2.5 | +3.1 | +30.2 | +70.8 | 19.7 | 19.4 |
| f1 | -9.3 | +16.1 | +2.1 | +1.8 | +20.8 | +81.0 | 21.0 | 18.9 |
| f2 | -10.6 | +42.7 | +3.1 | +1.8 | +21.3 | +32.7 | 21.2 | 18.8 |
| f3 | -9.0 | +41.6 | -2.8 | +2.9 | +45.6 | +74.4 | 19.7 | 18.6 |
| f4 | -2.8 | +2.0 | +10.7 | -0.9 | +24.3 | +56.4 | 20.8 | 19.3 |
| f5 | -11.3 | +29.6 | -2.2 | +0.1 | +32.8 | +67.7 | 19.7 | 19.2 |

## Reading
- **No screen fixes the 2016/2018 in-year drawdown** (19-21% vs TRI 14-16%). The drawdown problem is not
  a quality/value problem.
- **f3 is not a real value test.** EBIT/EV needs TTM EBIT, which is mostly missing (24,690 name-nights
  kept as missing; zero non-financial value drops). Its gain is financials ranked apart on earnings
  yield (825 drops) and is concentrated in 2020 (+15 pp). Treat as noise until TTM coverage exists.
- **Earnings-yield value (f2) hurts** (-5 CAGR, mostly 2021: it drops expensive momentum winners).
- **Quality (f1) trades return for slightly lower DD**; Sharpe and MAR do not improve.
- **f4 has the lowest max DD (29.0) and best 2016/2018 excess**, but gives up 2017 (+2 vs +40) and
  4.4 CAGR. MAR 0.98 vs 0.93: marginal.
- Verdict: **no screen is promotable; c1 stays core.** Fundamentals don't add a robust edge on the data
  we hold. A fair EBIT/EV test needs TTM coverage (Tapetide or hand files), not available now.
