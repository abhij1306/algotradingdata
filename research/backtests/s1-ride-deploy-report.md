# S1 ride variants — more capital, lower drawdown, more trades (2026-10-27)

In-sample 2016-01-01..2021-12-31, NIFTY500_PIT, policy v3, daily entry bars, ambiguous pessimistic.
Hold-out not used. Sweeps `sweeps/s1-ride-deploy.yaml` (11 single-knob variants vs ride_pess
01a17d5e) and `sweeps/s1-ride-deploy-2.yaml` (2 bundles); logs `s1-ride-deploy{,-2}.log`.
Reproduction check: ride_pess rerun on main 6cabfbd6 = run 01a17dda, identical 172-trade list.

| variant | run | trades | win% | expR | CAGR% | maxDD% | MAR | Sharpe | inv% | avg open | CAGR ex5% | top5% | DSR | PBO |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ride_pess | 01a17d5e | 172 | 31.4 | 0.588 | 15.76 | 24.12 | 0.65 | 1.11 | 51.7 | 2.93 | 4.62 | 77.9 | 0.385 | 0.614 |
| r075 | 01a17de6 | 201 | 33.3 | 0.609 | 13.93 | 20.57 | 0.68 | 1.14 | 46.6 | 3.48 | 4.82 | 72.5 | 0.405 | |
| r050 | 01a17df1 | 228 | 33.8 | 0.564 | 10.27 | 16.80 | 0.61 | 1.07 | 37.0 | 3.85 | 4.09 | 65.9 | 0.347 | |
| r050_pos15 | 01a17dfc | 245 | 33.9 | 0.561 | 10.86 | 16.77 | 0.65 | 1.09 | 38.6 | 4.14 | 4.86 | 61.5 | 0.363 | |
| pmax15 | 01a17e07 | 198 | 32.3 | 0.534 | 11.30 | 20.35 | 0.56 | 0.93 | 47.2 | 3.34 | 3.01 | 78.4 | 0.228 | |
| slot_rs | 01a17e12 | 175 | 33.7 | 0.665 | 17.91 | 24.80 | 0.72 | 1.21 | 52.1 | 3.09 | 6.82 | 71.2 | 0.462 | 0.429 |
| tstop | 01a17e21 | 206 | 42.7 | 0.458 | 13.94 | 24.87 | 0.56 | 1.03 | 43.1 | 2.30 | 3.02 | 83.6 | 0.302 | |
| regime_rising | 01a17e33 | 172 | 32.0 | 0.383 | 9.75 | 19.82 | 0.49 | 0.80 | 46.1 | 2.78 | 3.13 | 72.8 | 0.138 | |
| be2r | 01a17e3f | 178 | 27.5 | 0.531 | 15.22 | 24.61 | 0.62 | 1.08 | 51.1 | 2.90 | 3.77 | 81.5 | 0.343 | |
| sma30 | 01a17e4a | 229 | 29.3 | 0.270 | 9.59 | 27.19 | 0.35 | 0.79 | 41.1 | 2.32 | 3.05 | 73.0 | 0.129 | |
| fdepth15 | 01a17e55 | 172 | 31.4 | 0.586 | 15.68 | 24.12 | 0.65 | 1.11 | 51.7 | 2.93 | 4.51 | 78.3 | 0.362 | |
| ratio09 | 01a17e60 | 200 | 31.5 | 0.562 | 15.84 | 27.12 | 0.58 | 1.06 | 56.7 | 3.41 | 4.65 | 77.9 | 0.318 | |
| rs_r075 (bundle) | 01a17e6c | 202 | 33.7 | 0.619 | 14.51 | 20.97 | 0.69 | 1.16 | 46.6 | 3.53 | 5.49 | 69.9 | 0.410 | 0.443 |
| **rs_r075_ratio09 (bundle)** | 01a17e77 | 228 | 33.3 | 0.688 | 16.73 | 20.47 | 0.82 | 1.21 | 52.3 | 4.09 | 7.10 | 66.7 | 0.447 | 0.471 |

Not testable: per-industry cap below max positions (`backtest_industry_cap_without_industries`,
`app/hat/data/audit.py:694`, industries incomplete).

Findings
- Invested capital is bounded by signal supply, not cash: at 0.5% risk cash refusals fall 359 -> 41
  yet invested falls to 37%. Ride averages ~3 open positions.
- slot_rs is the only free improvement (every quality metric up).
- Risk per trade is the drawdown lever (24.1 -> 20.6 at 0.75%, 16.8 at 0.5%) at a CAGR cost.
- Exit/regime changes (time stop, breakeven 2R, SMA30, rising regime) all worse.
- Longest drawdown ~750 sessions (2018-2020) in every variant: structural.

Candidate: rs_r075_ratio09 — MAR 0.82 vs 0.65, max DD 20.5 vs 24.1, trades 228 vs 172, avg open
4.09 vs 2.93, invested 52.3 vs 51.7, CAGR 16.7 vs 15.8, CAGR ex top-5 7.1 vs 4.6. Caveats: chosen
after 13 trials on the same data (DSR 0.447 < 0.95, PBO 0.47); 2021 alone +63.5%; not hold-out tested.
